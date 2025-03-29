from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.course import Course
from app.models.course_students import CourseStudents
from app.utils.response import Result
from app import db
from app.student import student_course_bp

import os
import time
import face_recognition
from werkzeug.utils import secure_filename
from datetime import datetime
from PIL import Image

from app.models.user import User
from app.models.attendance_task import AttendanceTask
from app.models.attendance_record import AttendanceRecord

# 允许的文件类型
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'PNG', 'JPG', 'JPEG'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].upper() in ALLOWED_EXTENSIONS

@student_course_bp.route('/list', methods=['GET'])
@jwt_required()
def get_student_courses():
    try:
        user_id = int(get_jwt_identity())

        # 获取学生已选课程
        courses = Course.query.join(CourseStudents).filter(
            CourseStudents.student_id == user_id
        ).all()

        return Result.success(data={
            'items': [{
                'courseId': course.course_id,
                'courseName': course.course_name,
                'teacherName': course.teacher.real_name,
                'semester': course.semester,
                'classTime': f"{course.start_time.strftime('%H:%M')}-{course.end_time.strftime('%H:%M')}",
                'location': course.location
            } for course in courses]
        })

    except Exception as e:
        print(f"Get student courses error: {str(e)}")
        return Result.error("获取课程列表失败")

@student_course_bp.route('/available', methods=['GET'])
@jwt_required()
def get_available_courses():
    try:
        user_id = int(get_jwt_identity())

        # 获取所有课程
        all_courses = Course.query.all()
        # 获取学生已选课程ID
        selected_course_ids = set(
            cs.course_id for cs in CourseStudents.query.filter_by(student_id=user_id).all()
        )

        return Result.success(data={
            'items': [{
                'courseId': course.course_id,
                'courseName': course.course_name,
                'teacherName': course.teacher.real_name,
                'semester': course.semester,
                'classTime': f"{course.start_time.strftime('%H:%M')}-{course.end_time.strftime('%H:%M')}",
                'location': course.location,
                'selected': course.course_id in selected_course_ids
            } for course in all_courses]
        })

    except Exception as e:
        print(f"Get available courses error: {str(e)}")
        return Result.error("获取可选课程失败")

@student_course_bp.route('/select', methods=['POST'])
@jwt_required()
def select_course():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        course_id = data.get('courseId')

        if not course_id:
            return Result.error("缺少课程ID")

        # 检查课程是否存在
        course = Course.query.get_or_404(course_id)

        # 检查是否已选
        if CourseStudents.query.filter_by(
            student_id=user_id,
            course_id=course_id
        ).first():
            return Result.error("已经选择了该课程")

        # 创建选课记录
        course_student = CourseStudents(
            student_id=user_id,
            course_id=course_id
        )
        db.session.add(course_student)
        db.session.commit()

        return Result.success(message="选课成功")

    except Exception as e:
        print(f"Select course error: {str(e)}")
        return Result.error("选课失败")

@student_course_bp.route('/attendance/sign', methods=['POST', 'OPTIONS'])
@jwt_required()
def sign_attendance():
    # 处理OPTIONS请求，解决CORS预检问题
    if request.method == 'OPTIONS':
        return Result.success()
        
    try:
        print("开始处理签到请求")
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return Result.error("用户不存在")

        # 获取请求数据
        task_id = request.form.get('task_id')
        if not task_id:
            return Result.error("缺少签到任务ID")
            
        # 验证任务是否存在且在有效时间内
        task = AttendanceTask.query.get(task_id)
        if not task:
            return Result.error("签到任务不存在")
            
        # 检查任务是否已过期
        current_time = datetime.now()
        if current_time > task.end_time:
            return Result.error("签到已结束")
            
        # 检查是否已经签到
        existing_record = AttendanceRecord.query.filter_by(
            task_id=task_id,
            student_id=user_id
        ).first()
        
        if existing_record:
            return Result.error("您已经签到过了")
        
        # 处理人脸图像
        if 'face_image' not in request.files:
            return Result.error("缺少人脸图像")
            
        face_image_file = request.files['face_image']
        if not face_image_file or face_image_file.filename == '':
            return Result.error("人脸图像无效")
            
        # 检查文件类型
        if not allowed_file(face_image_file.filename):
            return Result.error("不支持的图像类型，请使用JPG/PNG格式")
            
        # 读取人脸图像
        face_image = face_recognition.load_image_file(face_image_file)
        face_locations = face_recognition.face_locations(face_image)
        
        if not face_locations:
            return Result.error("未检测到人脸，请确保光线充足且正面对准摄像头")
            
        if len(face_locations) > 1:
            return Result.error("检测到多个人脸，请确保只有您自己的脸出现在画面中")
            
        # 获取用户头像路径
        if not user.avatar:
            return Result.error("您尚未设置头像，请先上传头像")
            
        # 获取头像完整路径
        avatar_path = os.path.join(current_app.root_path, 'static', user.avatar.lstrip('/'))
        
        # 加载用户头像
        try:
            user_image = face_recognition.load_image_file(avatar_path)
            user_face_locations = face_recognition.face_locations(user_image)
            
            if not user_face_locations:
                return Result.error("您的头像中未检测到人脸，请重新上传清晰的头像照片")
                
            # 使用第一个检测到的人脸
            user_face_encoding = face_recognition.face_encodings(user_image, [user_face_locations[0]])[0]
            face_encoding = face_recognition.face_encodings(face_image, [face_locations[0]])[0]
            
            # 比较人脸
            results = face_recognition.compare_faces([user_face_encoding], face_encoding, tolerance=0.6)
            face_distance = face_recognition.face_distance([user_face_encoding], face_encoding)[0]
            
            # 输出人脸匹配得分，便于调试
            print(f"Face match distance: {face_distance}, is match: {results[0]}")
            
            if not results[0]:
                return Result.error("人脸验证失败，请确保是本人进行签到")
                
            # 确定签到状态
            status = '正常'
            if current_time > task.start_time:
                # 如果当前时间已经超过了开始时间，则标记为迟到
                status = '迟到'
                
            # 创建签到记录
            record = AttendanceRecord(
                task_id=task.task_id,
                student_id=user_id,
                course_id=task.course_id,
                check_in_time=current_time,
                status=status
            )
                
            db.session.add(record)
            db.session.commit()
            
            return Result.success("签到成功")
            
        except Exception as e:
            print(f"人脸识别失败: {str(e)}")
            return Result.error(f"人脸识别失败: {str(e)}")
            
    except Exception as e:
        print(f"签到失败: {str(e)}")
        db.session.rollback()
        return Result.error(f"签到失败: {str(e)}")

@student_course_bp.route('/attendance/active', methods=['GET'])
@jwt_required()
def get_active_attendance_tasks():
    """获取当前可签到的任务"""
    try:
        user_id = int(get_jwt_identity())
        current_time = datetime.now()
        
        # 获取学生所在的所有课程ID
        course_ids = [cs.course_id for cs in CourseStudents.query.filter_by(
            student_id=user_id
        ).all()]
        
        if not course_ids:
            return Result.success(data={'items': []})
        
        # 获取这些课程中当前有效的签到任务
        tasks = AttendanceTask.query.filter(
            AttendanceTask.course_id.in_(course_ids),
            AttendanceTask.start_time <= current_time,
            AttendanceTask.end_time >= current_time,
            AttendanceTask.status == 'active'
        ).all()
        
        # 过滤掉已签到的任务
        result_tasks = []
        for task in tasks:
            record = AttendanceRecord.query.filter_by(
                task_id=task.task_id,
                student_id=user_id
            ).first()
            
            if not record:
                course = Course.query.get(task.course_id)
                teacher = User.query.get(task.teacher_id)
                
                result_tasks.append({
                    'taskId': task.task_id,
                    'courseName': course.course_name,
                    'teacherName': teacher.real_name if teacher else '未知',
                    'startTime': task.start_time.strftime('%Y-%m-%d %H:%M'),
                    'endTime': task.end_time.strftime('%Y-%m-%d %H:%M')
                })
        
        return Result.success(data={'items': result_tasks})
        
    except Exception as e:
        print(f"获取签到任务失败: {str(e)}")
        return Result.error(f"获取签到任务失败: {str(e)}")

@student_course_bp.route('/attendance/history', methods=['GET'])
@jwt_required()
def get_attendance_history():
    """获取学生的签到历史记录"""
    try:
        user_id = int(get_jwt_identity())
        
        # 获取所有签到记录
        records = db.session.query(
            AttendanceRecord, AttendanceTask, Course, User
        ).join(
            AttendanceTask, AttendanceRecord.task_id == AttendanceTask.task_id
        ).join(
            Course, AttendanceTask.course_id == Course.course_id
        ).join(
            User, AttendanceTask.teacher_id == User.user_id
        ).filter(
            AttendanceRecord.student_id == user_id
        ).order_by(
            AttendanceRecord.check_in_time.desc()
        ).all()
        
        history = []
        for record, task, course, teacher in records:
            history.append({
                'recordId': record.record_id,
                'courseName': course.course_name,
                'teacherName': teacher.real_name,
                'startTime': task.start_time.strftime('%Y-%m-%d %H:%M'),
                'endTime': task.end_time.strftime('%Y-%m-%d %H:%M'),
                'status': record.status,
                'checkInTime': record.check_in_time.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return Result.success(data={'items': history})
        
    except Exception as e:
        print(f"获取签到历史失败: {str(e)}")
        return Result.error(f"获取签到历史失败: {str(e)}")


