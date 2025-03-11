from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.attendance_task import AttendanceTask
from app.models.attendance_record import AttendanceRecord
from app.models.course import Course
from app.models.course_students import CourseStudents
from app.utils.response import Result
from app import db
from datetime import datetime
from app.student import student_attendance_bp


@student_attendance_bp.route('/active', methods=['GET'])
@jwt_required()
def get_active_attendance_tasks():
    try:
        user_id = int(get_jwt_identity())
        now = datetime.now()

        # 获取学生已选课程的当前有效签到任务
        tasks = AttendanceTask.query.join(Course).join(CourseStudents).filter(
            CourseStudents.student_id == user_id,
            AttendanceTask.status == 'active',
            AttendanceTask.end_time > now
        ).all()

        # 排除已签到的任务
        signed_task_ids = set(
            record.task_id for record in AttendanceRecord.query.filter_by(
                student_id=user_id
            ).all()
        )

        return Result.success(data={
            'items': [{
                'taskId': task.task_id,
                'courseId': task.course_id,
                'courseName': task.course.course_name,
                'teacherName': task.course.teacher.real_name,
                'startTime': task.start_time.strftime('%H:%M'),
                'endTime': task.end_time.strftime('%H:%M')
            } for task in tasks if task.task_id not in signed_task_ids]
        })

    except Exception as e:
        print(f"Get active attendance tasks error: {str(e)}")
        return Result.error("获取签到任务失败")

@student_attendance_bp.route('/history', methods=['GET'])
@jwt_required()
def get_attendance_history():
    try:
        user_id = int(get_jwt_identity())

        # 获取学生选课的所有已结束的签到任务
        ended_tasks = AttendanceTask.query.join(Course).join(CourseStudents).filter(
            CourseStudents.student_id == user_id,
            AttendanceTask.status != 'active'
        ).order_by(AttendanceTask.created_at.desc()).all()

        result_items = []
        for task in ended_tasks:
            # 查找该任务的签到记录
            record = AttendanceRecord.query.filter_by(
                student_id=user_id,
                task_id=task.task_id
            ).first()

            # 如果没有签到记录且任务已结束，创建一个缺课记录
            if not record and task.status == 'ended':
                record = AttendanceRecord(
                    task_id=task.task_id,
                    student_id=user_id,
                    course_id=task.course_id,
                    check_in_time=task.end_time,
                    status='缺课'
                )
                db.session.add(record)
                db.session.flush()  # 获取新记录的 ID

            # 只有当有记录时才添加到结果中
            if record:
                result_items.append({
                    'recordId': record.id,
                    'taskId': task.task_id,
                    'courseName': task.course.course_name,
                    'teacherName': task.course.teacher.real_name,
                    'date': task.start_time.strftime('%Y-%m-%d'),
                    'startTime': task.start_time.strftime('%H:%M'),
                    'endTime': task.end_time.strftime('%H:%M'),
                    'status': record.status,
                    'checkInTime': record.check_in_time.strftime('%Y-%m-%d %H:%M:%S') if record.check_in_time else None
                })

        db.session.commit()  # 提交所有新创建的缺课记录

        return Result.success(data={
            'items': result_items
        })

    except Exception as e:
        print(f"Get attendance history error: {str(e)}")
        return Result.error("获取签到记录失败")

@student_attendance_bp.route('/checkin', methods=['POST'])
@jwt_required()
def submit_attendance():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        task_id = data.get('taskId')
        location_lat = data.get('locationLat')
        location_lng = data.get('locationLng')
        face_image = data.get('faceImage')

        if not task_id:
            return Result.error("缺少签到任务ID")

        # 获取签到任务
        task = AttendanceTask.query.get_or_404(task_id)
        now = datetime.now()

        # 检查是否已签到
        if AttendanceRecord.query.filter_by(
            student_id=user_id,
            task_id=task_id
        ).first():
            return Result.error("已经签到过了")

        # 判断签到状态
        if now > task.end_time:  # 超过结束时间
            status = '缺课'
        elif now >= task.start_time:  # 在开始时间和结束时间之间
            status = '正常'
        else:  # 在开始时间之前
            status = '正常'  # 或者可以设置为"提前"

        # 创建签到记录
        record = AttendanceRecord(
            task_id=task_id,
            student_id=user_id,
            course_id=task.course_id,
            check_in_time=now,
            status=status,
            location_lat=location_lat,
            location_lng=location_lng,
            face_image=face_image
        )

        db.session.add(record)
        db.session.commit()

        return Result.success(message="签到成功")

    except Exception as e:
        print(f"Submit attendance error: {str(e)}")
        return Result.error("签到失败")