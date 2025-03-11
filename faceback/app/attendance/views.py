from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.attendance_task import AttendanceTask
from app.models.course import Course
from app.utils.response import Result
from app import db
from datetime import datetime, time, timedelta
from app.attendance import teacher_attendance_bp
from app.models.attendance_record import AttendanceRecord


@teacher_attendance_bp.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        # 验证必填字段
        required_fields = ['courseId', 'startTime', 'endTime']
        for field in required_fields:
            if field not in data:
                return Result.error(f"缺少必填字段: {field}")

        # 验证课程权限
        course = Course.query.get_or_404(data['courseId'])
        if course.teacher_id != user_id:
            return Result.error("无权在此课程发起签到", code=403)

     
        current_date = datetime.now().date()
 
        start_time = datetime.combine(
            current_date,
            datetime.strptime(data['startTime'], '%H:%M').time()
        )
        end_time = datetime.combine(
            current_date,
            datetime.strptime(data['endTime'], '%H:%M').time()
        )

        # 如果结束时间早于开始时间，说明跨天，需要加一天
        if end_time < start_time:
            end_time = datetime.combine(
                current_date + timedelta(days=1),
                datetime.strptime(data['endTime'], '%H:%M').time()
            )
 
        task = AttendanceTask(
            course_id=data['courseId'],
            teacher_id=user_id,
            start_time=start_time,
            end_time=end_time,
            status='active'
        )

        db.session.add(task)
        db.session.commit()

        return Result.success(message="签到任务创建成功")

    except Exception as e:
        print(f"Create attendance task error: {str(e)}")
        return Result.error("创建签到任务失败")

@teacher_attendance_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    try:
        user_id = int(get_jwt_identity())
        course_id = request.args.get('courseId')
        task_type = request.args.get('type', 'active')  # active 或 history

        # 构建查询
        query = AttendanceTask.query.filter_by(teacher_id=user_id)
        if course_id:
            query = query.filter_by(course_id=course_id)
        
        # 根据类型筛选
        if task_type == 'active':
            query = query.filter_by(status='active')
        else:
            query = query.filter(AttendanceTask.status != 'active')

        tasks = query.order_by(AttendanceTask.created_at.desc()).all()

        # 获取每个任务的签到统计
        result_items = []
        for task in tasks:
            # 获取该课程的总学生数
            total_students = task.course.students.count()
            # 获取已签到学生数
            checked_in = AttendanceRecord.query.filter_by(
                task_id=task.task_id
            ).filter(
                AttendanceRecord.status != '缺课'
            ).count()
            
            result_items.append({
                'taskId': task.task_id,
                'courseId': task.course_id,
                'courseName': task.course.course_name,
                'startTime': task.start_time.strftime('%H:%M'),
                'endTime': task.end_time.strftime('%H:%M'),
                'date': task.start_time.strftime('%Y-%m-%d'),
                'status': task.status,
                'attendanceRate': f'{checked_in}/{total_students}',
                'createdAt': task.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })

        return Result.success(data={
            'items': result_items
        })

    except Exception as e:
        print(f"Get attendance tasks error: {str(e)}")
        return Result.error("获取签到任务列表失败")

@teacher_attendance_bp.route('/tasks/<int:task_id>/end', methods=['PUT'])
@jwt_required()
def end_task(task_id):
    try:
        user_id = int(get_jwt_identity())
        task = AttendanceTask.query.get_or_404(task_id)

        # 验证权限
        if task.teacher_id != user_id:
            return Result.error("无权结束此签到任务", code=403)

        # 更新状态
        task.status = 'ended'
        db.session.commit()

        return Result.success(message="签到任务已结束")

    except Exception as e:
        print(f"End attendance task error: {str(e)}")
        return Result.error("结束签到任务失败")

# 获取签到详情
@teacher_attendance_bp.route('/tasks/<int:task_id>/records', methods=['GET'])
@jwt_required()
def get_task_records(task_id):
    try:
        user_id = int(get_jwt_identity())
        task = AttendanceTask.query.get_or_404(task_id)

        # 验证权限
        if task.teacher_id != user_id:
            return Result.error("无权查看此签到记录", code=403)

        records = task.records
        return Result.success(data={
            'taskInfo': {
                'courseName': task.course.course_name,
                'startTime': task.start_time.strftime('%Y-%m-%d %H:%M'),
                'endTime': task.end_time.strftime('%Y-%m-%d %H:%M'),
                'status': task.status
            },
            'records': [{
                'studentId': record.student.user_id,
                'studentName': record.student.real_name,
                'checkInTime': record.check_in_time.strftime('%Y-%m-%d %H:%M:%S'),
                'status': record.status
            } for record in records]
        })

    except Exception as e:
        print(f"Get task records error: {str(e)}")
        return Result.error("获取签到记录失败")
