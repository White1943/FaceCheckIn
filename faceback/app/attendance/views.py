from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.attendance_task import AttendanceTask
from app.models.course import Course
from app.models.user import User
from app.models.attendance_record import AttendanceRecord
from app.utils.response import Result
from app import db
from datetime import datetime, time, timedelta
from app.attendance import teacher_attendance_bp
import os
import base64
import numpy as np
from io import BytesIO
from PIL import Image
import face_recognition
from app.models.course_students import CourseStudents
from sqlalchemy import func, case
import traceback


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
        current_time = datetime.now()
        
        # 首先更新所有已过期但未结束的任务
        expired_tasks = AttendanceTask.query.filter(
            AttendanceTask.end_time <= current_time,
            AttendanceTask.status == 'active'
        ).all()
        
        # 记录自动结束的任务数量
        auto_ended_count = len(expired_tasks)
        
        for task in expired_tasks:
            task.status = 'ended'
            
        if expired_tasks:
            db.session.commit()
            print(f"自动结束了 {auto_ended_count} 个过期任务")
        
        course_id = request.args.get('courseId')
        task_type = request.args.get('type', 'active')  # active 或 history
        
        # 构建查询
        query = AttendanceTask.query.filter_by(teacher_id=user_id)
        if course_id:
            query = query.filter_by(course_id=course_id)
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
            'items': result_items,
            'autoEndedCount': auto_ended_count
        })

    except Exception as e:
        print(f"Get attendance tasks error: {str(e)}")
        return Result.error("获取签到任务列表失败")

@teacher_attendance_bp.route('/tasks/<int:task_id>/end', methods=['PUT'])
@jwt_required()
def end_task(task_id):
    """Ends an active attendance task."""
    try:
        teacher_id = int(get_jwt_identity())
        task = AttendanceTask.query.get(task_id)

        if not task:
            return Result.error("签到任务不存在", code=404)

        # Verify teacher ownership
        if task.teacher_id != teacher_id:
            current_app.logger.warning(f"Teacher {teacher_id} attempted to end task {task_id} owned by {task.teacher_id}")
            return Result.error("无权操作此签到任务", code=403)

        if task.status != 'active':
            return Result.error(f"签到任务状态为 '{task.status}'，无法结束", code=400)

        # Update task status
        task.status = 'ended'
        # Optionally, set the actual end time if it wasn't set automatically
        # task.end_time = datetime.now()

        db.session.commit()
        current_app.logger.info(f"Teacher {teacher_id} ended attendance task {task_id}")
        return Result.success(message="签到已成功结束")

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error ending attendance task {task_id}: {e}")
        traceback.print_exc()
        return Result.error(f"结束签到失败: {str(e)}")

# 获取签到详情
@teacher_attendance_bp.route('/tasks/<int:task_id>/records', methods=['GET'])
@jwt_required()
def get_task_records(task_id):
    try:
        user_id = int(get_jwt_identity())
        task = AttendanceTask.query.get_or_404(task_id)

        # 验证权限
        if task.teacher_id != user_id:
            return Result.error("无权查看此签到任务详情", code=403)

        # 获取任务信息
        course = Course.query.get(task.course_id)
        task_info = {
            'taskId': task.task_id,
            'courseName': course.course_name,
            'startTime': task.start_time.strftime('%Y-%m-%d %H:%M'),
            'endTime': task.end_time.strftime('%Y-%m-%d %H:%M'),
            'status': task.status
        }

        # 获取课程所有学生
        students = course.students.all()

        # 获取已签到记录
        records = AttendanceRecord.query.filter_by(task_id=task_id).all()

        # 记录字典，便于后续查找
        record_dict = {record.student_id: record for record in records}

        result_records = []
        for student in students:
            if student.user_id in record_dict:
                record = record_dict[student.user_id]
                status = record.status
                check_in_time = record.check_in_time.strftime('%Y-%m-%d %H:%M:%S')

                # 处理照片路径 - 修改为相对路径
                face_image_url = None
                if record.face_image:
                    face_image_url = f'/uploads/attendance/{record.face_image}'

                result_records.append({
                    'recordId': record.id,
                    'studentId': student.user_id,
                    'studentName': student.real_name,
                    'status': status,
                    'checkInTime': check_in_time,
                    'faceImage': face_image_url  # URL路径形式
                })
            else:
                # 未签到的学生
                result_records.append({
                    'studentId': student.user_id,
                    'studentName': student.real_name,
                    'status': '缺课',
                    'checkInTime': None,
                    'faceImage': None
                })

        return Result.success(data={
            'taskInfo': task_info,
            'records': result_records
        })

    except Exception as e:
        print(f"Get task records error: {str(e)}")
        return Result.error("获取签到详情失败")

@teacher_attendance_bp.route('/sign', methods=['POST'])
@jwt_required()
def sign_attendance():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return Result.error(message='用户不存在', code=404)

        # 获取请求数据
        task_id = request.form.get('task_id')
        if not task_id:
            return Result.error(message='缺少签到任务ID', code=400)

        # 验证任务是否存在且在有效时间内
        task = AttendanceTask.query.get(task_id)
        if not task:
            return Result.error(message='签到任务不存在', code=404)

        # 检查任务是否已过期
        current_time = datetime.now()
        if current_time > task.end_time:
            return Result.error(message='签到已结束', code=400)

        # 检查是否已经签到
        existing_record = AttendanceRecord.query.filter_by(
            task_id=task_id,
            student_id=current_user_id
        ).first()

        if existing_record:
            return Result.error(message='您已经签到过了', code=400)

        # 处理人脸图像
        if 'face_image' not in request.files:
            return Result.error(message='缺少人脸图像', code=400)

        face_image_file = request.files['face_image']
        if not face_image_file:
            return Result.error(message='人脸图像无效', code=400)

        # 保存上传的图像
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'attendance')
        os.makedirs(upload_folder, exist_ok=True)
        filename = f"{current_user_id}_{task_id}_{int(datetime.now().timestamp())}.jpg"
        image_path = os.path.join(upload_folder, filename)
        face_image_file.save(image_path)
        print(f"保存签到图像: {image_path}")

        # 读取上传的人脸图像
        face_image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(face_image)

        # 检查是否检测到人脸
        if not face_locations:
            return Result.error(message='未检测到人脸，请确保光线充足且正面对准摄像头', code=400)

        # 如果检测到多个人脸，返回错误
        if len(face_locations) > 1:
            return Result.error(message='检测到多个人脸，请确保只有您自己的脸出现在画面中', code=400)

        # 获取人脸编码
        face_encoding = face_recognition.face_encodings(face_image, face_locations)[0]

        # 获取用户注册的头像
        avatar_path = os.path.join(current_app.root_path, 'static', user.avatar.lstrip('/'))

        # 检查头像文件是否存在
        if not os.path.exists(avatar_path):
            return Result.error(message='未找到您的头像信息，请先上传清晰的正面头像', code=400)

        # 加载头像并提取特征
        try:
            avatar_image = face_recognition.load_image_file(avatar_path)
            avatar_face_locations = face_recognition.face_locations(avatar_image)

            if not avatar_face_locations:
                return Result.error(message='您的头像中未检测到人脸，请重新上传清晰的正面头像', code=400)

            avatar_face_encoding = face_recognition.face_encodings(avatar_image, avatar_face_locations)[0]

            # 比较人脸
            match_results = face_recognition.compare_faces([avatar_face_encoding], face_encoding, tolerance=0.6)
            distance = face_recognition.face_distance([avatar_face_encoding], face_encoding)[0]

            print(f"人脸匹配结果: {match_results[0]} ")
            # print(f"人脸匹配结果: {match_results[0]}, 距离: {distance}")

            # 判断人脸识别是否通过
            is_face_valid = match_results[0] and distance <= 0.35

            # 如果人脸识别失败，检查今天失败的次数
            if not is_face_valid:
                # 获取今天的日期范围
                today = datetime.now().date()
                today_start = datetime.combine(today, datetime.min.time())
                today_end = datetime.combine(today, datetime.max.time())

                # 获取今天失败的次数
                failure_count = AttendanceRecord.query.filter(
                    AttendanceRecord.student_id == current_user_id,
                    AttendanceRecord.check_in_time.between(today_start, today_end),
                    AttendanceRecord.status == '异常'
                ).count()

                # 获取今天针对此任务的临时识别失败尝试记录
                temp_failures = AttendanceRecord.query.filter(
                    AttendanceRecord.student_id == current_user_id,
                    AttendanceRecord.task_id == task_id,
                    AttendanceRecord.check_in_time.between(today_start, today_end),
                    AttendanceRecord.status == '识别尝试'  # 使用特殊状态标记临时记录
                ).all()

                # 总共失败次数 = 已存在的异常记录 + 临时识别失败记录
                total_failures = failure_count + len(temp_failures)

                print(f"用户 {current_user_id} 今日已有 {total_failures} 次人脸识别失败尝试")

                # 如果总失败次数 < 2，创建一个临时识别失败记录
                if total_failures < 2:
                    temp_record = AttendanceRecord(
                        task_id=task_id,
                        student_id=current_user_id,
                        course_id=task.course_id,
                        check_in_time=current_time,
                        status='识别尝试',  # 使用特殊状态标记临时记录
                        location_lat=request.form.get('location_lat', 0),
                        location_lng=request.form.get('location_lng', 0),
                        face_image=filename,
                        review_status='临时记录',
                        appeal_reason="人脸识别距离过高：" + str(distance)
                    )

                    db.session.add(temp_record)
                    db.session.commit()

                    return Result.error(
                        message=f'人脸识别未通过，请重试。这是第 {total_failures} 次尝试，连续 3 次失败将记录为异常签到',
                        code=400
                    )
                else:
                    # 如果已经有2次失败，这次是第3次，创建一个异常签到记录
                    status = '异常'

                    # 收集今天所有临时失败记录的图片名
                    failure_images = [record.face_image for record in temp_failures if record.face_image]
                    # 添加当前失败的图片
                    failure_images.append(filename)

                    # 使用最后一次失败（当前）的图片
                    final_image = filename

                    # 删除所有临时记录
                    for record in temp_failures:
                        db.session.delete(record)
            else:
                # 人脸识别通过，设置签到状态
                status = '正常'

                # 检查是否迟到
                if current_time > task.start_time + (task.end_time - task.start_time) * 0.5:
                    status = '迟到'

                final_image = filename

            # 获取地理位置
            location_lat = request.form.get('location_lat', 0)
            location_lng = request.form.get('location_lng', 0)

            # 如果不是临时记录，创建正式签到记录
            if is_face_valid or (not is_face_valid and total_failures >= 2):
                record = AttendanceRecord(
                    task_id=task_id,
                    student_id=current_user_id,
                    course_id=task.course_id,
                    check_in_time=current_time,
                    status=status,
                    location_lat=location_lat,
                    location_lng=location_lng,
                    face_image=final_image,
                    review_status='未申诉' if status != '异常' else '待审核',
                    appeal_reason="系统自动申诉: 连续三次人脸识别失败" if status == '异常' else None
                )

                db.session.add(record)
                db.session.commit()

                response_data = {
                    'status': status,
                    'recordId': record.id if status == '异常' else None,
                    'message': '签到成功' if status != '异常' else '人脸识别异常，已自动提交申诉'
                }

                return Result.success(
                    data=response_data,
                    message='签到已记录，但人脸识别异常，已自动提交申诉' if status == '异常' else '签到成功'
                )

        except Exception as e:
            print(f"处理人脸识别失败: {str(e)}")
            return Result.error(message=f'人脸识别处理失败: {str(e)}', code=500)

    except Exception as e:
        print(f"签到失败: {str(e)}")
        db.session.rollback()
        return Result.error(message=f'签到失败: {str(e)}', code=500)


@teacher_attendance_bp.route('/active', methods=['GET'])
@jwt_required()
def get_active_attendance_tasks():
    """获取当前可签到的任务"""
    try:
        current_user_id = int(get_jwt_identity())
        current_time = time.time()

        # 获取学生的课程
        student_courses = db.session.query(Course.id).join(
            CourseStudent, Course.id == CourseStudent.course_id
        ).filter(CourseStudent.student_id == current_user_id).all()

        course_ids = [course.id for course in student_courses]

        # 获取活跃的签到任务
        active_tasks = AttendanceTask.query.filter(
            AttendanceTask.course_id.in_(course_ids),
            AttendanceTask.start_time <= current_time,
            AttendanceTask.end_time >= current_time
        ).all()

        # 排除已经签到的任务
        signed_task_ids = db.session.query(AttendanceRecord.task_id).filter(
            AttendanceRecord.student_id == current_user_id
        ).all()

        signed_task_ids = [record.task_id for record in signed_task_ids]

        # 过滤出未签到的活跃任务
        tasks = []
        for task in active_tasks:
            if task.id not in signed_task_ids:
                course = Course.query.get(task.course_id)
                teacher = User.query.get(course.teacher_id)

                tasks.append({
                    'taskId': task.id,
                    'courseName': course.name,
                    'teacherName': teacher.name,
                    'startTime': time.strftime('%Y-%m-%d %H:%M', time.localtime(task.start_time)),
                    'endTime': time.strftime('%Y-%m-%d %H:%M', time.localtime(task.end_time))
                })

        return Result.success(data={'items': tasks})

    except Exception as e:
        print(f"获取签到任务失败: {str(e)}")
        return Result.error(message=f'获取签到任务失败: {str(e)}', code=500)


@teacher_attendance_bp.route('/history', methods=['GET'])
@jwt_required()
def get_attendance_history():
    """获取签到历史记录"""
    try:
        current_user_id = get_jwt_identity()

        # 获取所有签到记录
        records = db.session.query(
            AttendanceRecord, AttendanceTask, Course, User
        ).join(
            AttendanceTask, AttendanceRecord.task_id == AttendanceTask.id
        ).join(
            Course, AttendanceTask.course_id == Course.id
        ).join(
            User, Course.teacher_id == User.id
        ).filter(
            AttendanceRecord.student_id == current_user_id
        ).order_by(
            AttendanceRecord.sign_time.desc()
        ).all()

        history = []
        for record, task, course, teacher in records:
            status_map = {
                'normal': '正常',
                'late': '迟到',
                'absent': '缺课'
            }

            history.append({
                'recordId': record.id,
                'courseName': course.name,
                'teacherName': teacher.name,
                'startTime': time.strftime('%Y-%m-%d %H:%M', time.localtime(task.start_time)),
                'endTime': time.strftime('%Y-%m-%d %H:%M', time.localtime(task.end_time)),
                'status': status_map.get(record.status, record.status),
                'checkInTime': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record.sign_time))
            })

        return Result.success(data={'items': history})

    except Exception as e:
        print(f"获取签到历史失败: {str(e)}")
        return Result.error(message=f'获取签到历史失败: {str(e)}', code=500)

@teacher_attendance_bp.route('/records/<int:record_id>/face', methods=['GET'])
@jwt_required()
def get_student_face_image(record_id):
    try:
        user_id = int(get_jwt_identity())
        record = AttendanceRecord.query.get_or_404(record_id)

        # 验证教师权限
        task = AttendanceTask.query.get(record.task_id)
        if task.teacher_id != user_id:
            return Result.error("无权查看此照片", code=403)

        if not record.face_image:
            return Result.error("该记录没有人脸照片", code=404)

        # 返回照片的完整URL
        image_url = f'/uploads/attendance/{record.face_image}'

        return Result.success(data={'imageUrl': image_url})

    except Exception as e:
        print(f"Get face image error: {str(e)}")
        return Result.error("获取照片失败")

@teacher_attendance_bp.route('/appeals', methods=['GET'])
@jwt_required()
def get_teacher_appeals():
    try:
        teacher_id = get_jwt_identity()

        # 打印调试信息
        print(f"Processing appeals request for teacher {teacher_id}")

        # 获取所有待审核的申诉记录
        appeals = db.session.query(
            AttendanceRecord, AttendanceTask, Course, User
        ).join(
            AttendanceTask, AttendanceRecord.task_id == AttendanceTask.task_id
        ).join(
            Course, AttendanceTask.course_id == Course.course_id
        ).join(
            User, AttendanceRecord.student_id == User.user_id
        ).filter(
            AttendanceTask.teacher_id == teacher_id,
            AttendanceRecord.review_status == '待审核'
        ).all()

        # 打印查询结果数量
        print(f"Found {len(appeals)} appeals")

        result = []
        for record, task, course, student in appeals:
            result.append({
                'recordId': record.id,
                'taskId': task.task_id,
                'courseName': course.course_name,
                'studentName': student.real_name,
                'checkInTime': record.check_in_time.strftime('%Y-%m-%d %H:%M:%S'),
                'status': record.status,
                'appealReason': record.appeal_reason,
                'faceImage': f'/uploads/attendance/{record.face_image}' if record.face_image else None
            })

        return Result.success(data={'items': result})

    except Exception as e:
        print(f"获取申诉记录失败: {str(e)}")
        import traceback
        traceback.print_exc()  # 打印详细错误堆栈
        return Result.error(f'获取申诉记录失败: {str(e)}', code=500)

@teacher_attendance_bp.route('/appeals/<int:record_id>/review', methods=['POST'])
@jwt_required()
def review_appeal(record_id):
    try:
        teacher_id = get_jwt_identity()
        data = request.json
        
        # 修复整数与字符串连接的问题
        print(f"教师id {teacher_id}")
        approved = data.get('approved', False)
        
        record = AttendanceRecord.query.get_or_404(record_id)
        
        # 验证权限
        task = AttendanceTask.query.get(record.task_id)
        
        # 使用 f-string 正确格式化字符串
        print(f"任务发布者，发布的教师id {task.teacher_id}")
        
        # 确保类型一致的比较
        if str(task.teacher_id) != str(teacher_id):
            return Result.error('无权审核此记录', code=403)
            
        # 验证记录状态
        if record.review_status != '待审核':
            return Result.error('该记录不在待审核状态', code=400)

        # 更新状态
        record.review_status = '已审核'
        if approved:
            record.status = '正常'  # 审核通过，修改为正常签到

        db.session.commit()

        return Result.success(message='审核完成')

    except Exception as e:
        db.session.rollback()
        print(f"审核申诉失败: {str(e)}")
        return Result.error(f'审核申诉失败: {str(e)}', code=500)

# --- New Statistics Endpoints ---

@teacher_attendance_bp.route('/stats/course-rates', methods=['GET'])
@jwt_required()
def get_course_attendance_rates():
    """
    获取教师授课课程的签到任务签到率统计
    Query Params:
        courseId (optional): 筛选特定课程的ID
    """
    try:
        teacher_id = get_jwt_identity()
        course_id_filter = request.args.get('courseId')

        # Base query for tasks created by the teacher
        query = db.session.query(
            AttendanceTask.task_id,
            AttendanceTask.start_time,
            Course.course_name
        ).join(Course, AttendanceTask.course_id == Course.course_id).filter(
            AttendanceTask.teacher_id == teacher_id
        )

        if course_id_filter:
            query = query.filter(AttendanceTask.course_id == course_id_filter)

        tasks = query.order_by(AttendanceTask.start_time.desc()).all()

        results = []
        for task_data in tasks:
            task_id, start_time, course_name = task_data

            # Get total students enrolled in the course for this task
            total_students = db.session.query(func.count(CourseStudents.student_id)).filter(
                CourseStudents.course_id == AttendanceTask.query.get(task_id).course_id
            ).scalar() or 0

            if total_students == 0:
                attendance_rate = 0.0
            else:
                # Count checked-in students (Normal, Late, Abnormal)
                checked_in_count = db.session.query(func.count(AttendanceRecord.id)).filter(
                    AttendanceRecord.task_id == task_id,
                    AttendanceRecord.status.in_(['正常', '迟到', '异常'])
                ).scalar() or 0
                attendance_rate = round((checked_in_count / total_students) * 100, 2) if total_students > 0 else 0

            results.append({
                'taskId': task_id,
                'courseName': course_name,
                'date': start_time.strftime('%Y-%m-%d %H:%M'),
                'attendanceRate': attendance_rate,
                'totalStudents': total_students,
                'checkedInCount': checked_in_count
            })

        return Result.success(data={'items': results})

    except Exception as e:
        print(f"获取课程签到率统计失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return Result.error("获取课程签到率统计失败")


@teacher_attendance_bp.route('/stats/task-details/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task_attendance_details(task_id):
    """
    获取指定签到任务下所有学生的签到详情
    """
    try:
        teacher_id = get_jwt_identity()

        # Verify task exists and teacher has permission
        task = db.session.query(AttendanceTask).filter(
            AttendanceTask.task_id == task_id,
            AttendanceTask.teacher_id == teacher_id
        ).first_or_404("签到任务不存在或无权限访问")

        # Get all students enrolled in the course
        enrolled_students = db.session.query(
            User.user_id, User.real_name
        ).join(CourseStudents, User.user_id == CourseStudents.student_id).filter(
            CourseStudents.course_id == task.course_id
        ).all()

        # Get attendance records for this task
        records = db.session.query(
            AttendanceRecord.student_id,
            AttendanceRecord.status,
            AttendanceRecord.check_in_time,
            AttendanceRecord.face_image # Include face image for potential display
        ).filter(
            AttendanceRecord.task_id == task_id
        ).all()

        # Create a dictionary for quick lookup of records
        records_dict = {record.student_id: record for record in records}

        results = []
        current_time = datetime.now()

        for student_id, student_name in enrolled_students:
            record = records_dict.get(student_id)
            status = '缺课' # Default status
            check_in_time_str = None
            face_image_url = None

            if record:
                status = record.status
                check_in_time_str = record.check_in_time.strftime('%Y-%m-%d %H:%M:%S') if record.check_in_time else None
                face_image_url = f'/uploads/attendance/{record.face_image}' if record.face_image else None
            elif task.status == 'active' and current_time < task.end_time:
                 # If task is still active and student hasn't checked in, mark as '未签到' instead of '缺课'
                 status = '未签到'


            results.append({
                'studentId': student_id,
                'studentName': student_name,
                'status': status,
                'checkInTime': check_in_time_str,
                'faceImageUrl': face_image_url
            })

        # Sort results by student name or ID if needed
        results.sort(key=lambda x: x['studentName'])

        return Result.success(data={'items': results, 'taskName': task.course.course_name + " - " + task.start_time.strftime('%Y-%m-%d %H:%M')})

    except Exception as e:
        print(f"获取任务签到详情失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return Result.error("获取任务签到详情失败")

# --- End of New Statistics Endpoints ---
