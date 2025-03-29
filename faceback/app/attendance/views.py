from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.attendance_task import AttendanceTask
from app.models.course import Course
from app.utils.response import Result
from app import db
from datetime import datetime, time, timedelta
from app.attendance import teacher_attendance_bp
from app.models.attendance_record import AttendanceRecord
import os
import base64
import numpy as np
from io import BytesIO
from PIL import Image
import face_recognition


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
        current_time = time.time()
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
            
        # 读取上传的人脸图像
        face_image = face_recognition.load_image_file(face_image_file)
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
            match = face_recognition.compare_faces([avatar_face_encoding], face_encoding, tolerance=0.6)
            distance = face_recognition.face_distance([avatar_face_encoding], face_encoding)[0]
            
            print(f"人脸匹配结果: {match}, 距离: {distance}")
            
            if not match[0]:
                return Result.error(message='人脸验证失败，与注册头像不匹配', code=403)
                
            # 如果距离太大，即使匹配也可能不是同一个人
            if distance > 0.5:
                return Result.error(message='人脸相似度过低，请尝试在更好的光线条件下重新签到', code=403)
                
            # 确定签到状态
            status = 'normal'  # 正常
            if current_time > task.start_time + (task.end_time - task.start_time) * 0.5:
                status = 'late'  # 迟到
                
            # 获取地理位置（如果提供）
            location_lat = request.form.get('location_lat', 0)
            location_lng = request.form.get('location_lng', 0)
            
            # 记录签到
            record = AttendanceRecord(
                task_id=task_id,
                student_id=current_user_id,
                status=status,
                sign_time=int(current_time),
                location_lat=location_lat,
                location_lng=location_lng
            )
            
            db.session.add(record)
            db.session.commit()
            
            return Result.success(message='签到成功')
            
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
        current_user_id = get_jwt_identity()
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
