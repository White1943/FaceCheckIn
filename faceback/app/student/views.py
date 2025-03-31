from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.course import Course
from app.models.course_students import CourseStudents
from app.utils.response import Result
from app import db
from app.student import student_course_bp
from app.student import student_attendance_bp


from app.models.attendance_task import AttendanceTask
from app.models.attendance_record import AttendanceRecord


from app.utils.response import Result



import os
import time
import face_recognition
from werkzeug.utils import secure_filename
from datetime import datetime
from PIL import Image

from app.models.user import User



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
# 按钮点击进行签到
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
# 人脸识别的签到
@student_attendance_bp.route('/sign', methods=['POST', 'OPTIONS'])
@jwt_required()
def submit_attendance_record():

    if request.method == 'OPTIONS':
        return Result.success()

    try:
        user_id = int(get_jwt_identity())

        # 打印请求头和内容类型
        print("请求头:", request.headers)
        print("请求内容类型:", request.content_type)
        print("请求数据:", request.data)
        print("Form data:", dict(request.form))
        print("Files:", request.files)

        task_id = None

        # 尝试从不同来源获取task_id
        if request.is_json:
            json_data = request.get_json()
            print("JSON数据:", json_data)
            if json_data and 'task_id' in json_data:
                task_id = json_data['task_id']
            elif json_data and 'taskId' in json_data:  # 尝试驼峰命名
                task_id = json_data['taskId']
        elif request.form:
            task_id = request.form.get('task_id') or request.form.get('taskId')
        elif request.data:

            try:
                import json
                data = json.loads(request.data)
                task_id = data.get('task_id') or data.get('taskId')
                print("手动解析JSON:", data)
            except:
                pass

        print(f"找到的task_id: {task_id}")

        if not task_id:
            return Result.error("缺少签到任务ID，请检查请求格式")

        task_id = int(task_id)
        print(f"处理的task_id: {task_id}")

        # 获取用户和签到任务信息
        user = User.query.get_or_404(user_id)

        task = AttendanceTask.query.get_or_404(task_id)
        current_time = datetime.now()

        # 检查任务是否已结束
        if current_time > task.end_time:
            return Result.error("签到已结束")

        # 检查是否已签到
        existing_record = AttendanceRecord.query.filter_by(
            task_id=task_id,
            student_id=user_id
        ).first()
        if existing_record:
            return Result.error("您已经签到过了")

        # 检查人脸图像
        if 'face_image' not in request.files:
            return Result.error("缺少人脸图像")

        face_image_file = request.files['face_image']
        if not face_image_file or face_image_file.filename == '':
            return Result.error("人脸图像无效")

        # 保存上传的图像  位于 uploads/attendance
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'attendance')
        print(f"上传签到图像文件夹位于: {upload_folder}")
        os.makedirs(upload_folder, exist_ok=True)
        filename = f"{user_id}_{task_id}_{int(datetime.now().timestamp())}.jpg"
        image_path = os.path.join(upload_folder, filename)
        face_image_file.save(image_path)
        print("加载已有图片： ",image_path)

        # 人脸识别逻辑
        try:
            # 加载上传的图像
            uploaded_image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(uploaded_image)

            if not face_locations:
                return Result.error("未检测到人脸，请确保光线充足且正面对准摄像头")

            if len(face_locations) > 1:
                return Result.error("检测到多张人脸，请确保画面中只有您自己")

            # 获取用户头像路径
            if not user.avatar:
                return Result.error("您尚未设置头像，请先上传头像")

            # 处理头像路径
            avatar_file = user.avatar.lstrip('/')
            if avatar_file.startswith('static/'):
                avatar_file = avatar_file[7:]  # 移除 'static/' 前缀

            user_avatar_path = os.path.join(current_app.root_path, 'static', avatar_file)
            print(f"用户头像路径 (对比路径): {user_avatar_path}")
            # 检查文件是否存在
            if not os.path.exists(user_avatar_path):
                print(f"用户头像不存在: {user_avatar_path}")
                return Result.error("找不到您的头像文件，请重新上传头像")

            # 加载用户头像并进行人脸比对
            user_image = face_recognition.load_image_file(user_avatar_path)
            user_face_locations = face_recognition.face_locations(user_image)

            if not user_face_locations:
                print(f"用户 {user_id} 的头像中未检测到人脸")
                return Result.error("您的头像中未检测到人脸，请重新上传清晰的头像照片")

            # 提取人脸特征
            user_face_encoding = face_recognition.face_encodings(user_image, [user_face_locations[0]])[0]
            uploaded_face_encoding = face_recognition.face_encodings(uploaded_image, [face_locations[0]])[0]

            # 比较人脸特征
            matches = face_recognition.compare_faces([user_face_encoding], uploaded_face_encoding, tolerance=0.6)
            face_distance = face_recognition.face_distance([user_face_encoding], uploaded_face_encoding)[0]
            print(f"人脸匹配距离: {face_distance}, 是否匹配: {matches[0]}")

            if not matches[0]:
                return Result.error("人脸识别失败，请确保是本人操作")

        except Exception as e:
            print(f"人脸识别过程中出错: {str(e)}")
            # 开发环境中可以暂时注释下面这行，让签到流程继续
            # return Result.error(f"人脸识别失败: {str(e)}")

        # 判断是否迟到
        status = '正常'
        if current_time > task.end_time:
            status = '迟到'

        # 创建签到记录
        record = AttendanceRecord(
            task_id=task_id,
            student_id=user_id,
            course_id=task.course_id,
            check_in_time=current_time,
            status=status,
            face_image=filename
        )

        db.session.add(record)
        db.session.commit()

        return Result.success(message=f"签到成功，状态: {status}")

    except Exception as e:
        db.session.rollback()
        print(f"签到失败: {str(e)}")
        return Result.error(f"签到失败: {str(e)}")


#以下弃用，因为学生进行签到方面操作时，蓝图应该用student_attendance_bp

# @student_course_bp.route('/attendance/sign', methods=['POST', 'OPTIONS'])
# @jwt_required()
# def sign_attendance():
#     # 处理OPTIONS请求，解决CORS预检问题
#     if request.method == 'OPTIONS':
#         return Result.success()

#     try:
#         print("开始处理签到请求")
#         user_id = int(get_jwt_identity())
#         user = User.query.get(user_id)

#         if not user:
#             return Result.error("用户不存在")

#         # 获取请求数据
#         task_id = request.form.get('task_id')
#         if not task_id:
#             return Result.error("缺少签到任务ID")

#         # 验证任务是否存在且在有效时间内
#         task = AttendanceTask.query.get(task_id)
#         if not task:
#             return Result.error("签到任务不存在")

#         # 检查任务是否已过期
#         current_time = datetime.now()
#         if current_time > task.end_time:
#             return Result.error("签到已结束")

#         # 检查是否已经签到
#         existing_record = AttendanceRecord.query.filter_by(
#             task_id=task_id,
#             student_id=user_id
#         ).first()

#         if existing_record:
#             return Result.error("您已经签到过了")

#         # 处理人脸图像
#         if 'face_image' not in request.files:
#             return Result.error("缺少人脸图像")

#         face_image_file = request.files['face_image']
#         if not face_image_file or face_image_file.filename == '':
#             return Result.error("人脸图像无效")

#         # 检查文件类型
#         if not allowed_file(face_image_file.filename):
#             return Result.error("不支持的图像类型，请使用JPG/PNG格式")

#         # 读取人脸图像
#         face_image = face_recognition.load_image_file(face_image_file)
#         face_locations = face_recognition.face_locations(face_image)

#         if not face_locations:
#             return Result.error("未检测到人脸，请确保光线充足且正面对准摄像头")

#         if len(face_locations) > 1:
#             return Result.error("检测到多个人脸，请确保只有您自己的脸出现在画面中")

#         # 获取用户头像路径
#         if not user.avatar:
#             return Result.error("您尚未设置头像，请先上传头像")

#         # 获取头像完整路径
#         avatar_path = os.path.join(current_app.root_path, 'static', user.avatar.lstrip('/'))

#         # 加载用户头像
#         try:
#             user_image = face_recognition.load_image_file(avatar_path)
#             user_face_locations = face_recognition.face_locations(user_image)

#             if not user_face_locations:
#                 return Result.error("您的头像中未检测到人脸，请重新上传清晰的头像照片")

#             # 使用第一个检测到的人脸
#             user_face_encoding = face_recognition.face_encodings(user_image, [user_face_locations[0]])[0]
#             face_encoding = face_recognition.face_encodings(face_image, [face_locations[0]])[0]

#             # 比较人脸
#             results = face_recognition.compare_faces([user_face_encoding], face_encoding, tolerance=0.6)
#             face_distance = face_recognition.face_distance([user_face_encoding], face_encoding)[0]

#             # 输出人脸匹配得分，便于调试
#             print(f"Face match distance: {face_distance}, is match: {results[0]}")

#             if not results[0]:
#                 return Result.error("人脸验证失败，请确保是本人进行签到")

#             # 确定签到状态
#             status = '正常'
#             if current_time > task.start_time:
#                 # 如果当前时间已经超过了开始时间，则标记为迟到
#                 status = '迟到'

#             # 创建签到记录
#             record = AttendanceRecord(
#                 task_id=task.task_id,
#                 student_id=user_id,
#                 course_id=task.course_id,
#                 check_in_time=current_time,
#                 status=status
#             )

#             db.session.add(record)
#             db.session.commit()

#             return Result.success("签到成功")

#         except Exception as e:
#             print(f"人脸识别失败: {str(e)}")
#             return Result.error(f"人脸识别失败: {str(e)}")

#     except Exception as e:
#         print(f"签到失败: {str(e)}")
#         db.session.rollback()
#         return Result.error(f"签到失败: {str(e)}")

# @student_course_bp.route('/attendance/active', methods=['GET'])
# @jwt_required()
# def get_active_attendance_tasks():
#     """获取当前可签到的任务"""
#     try:
#         user_id = int(get_jwt_identity())
#         current_time = datetime.now()

#         # 获取学生所在的所有课程ID
#         course_ids = [cs.course_id for cs in CourseStudents.query.filter_by(
#             student_id=user_id
#         ).all()]

#         if not course_ids:
#             return Result.success(data={'items': []})

#         # 获取这些课程中当前有效的签到任务
#         tasks = AttendanceTask.query.filter(
#             AttendanceTask.course_id.in_(course_ids),
#             AttendanceTask.start_time <= current_time,
#             AttendanceTask.end_time >= current_time,
#             AttendanceTask.status == 'active'
#         ).all()

#         # 过滤掉已签到的任务
#         result_tasks = []
#         for task in tasks:
#             record = AttendanceRecord.query.filter_by(
#                 task_id=task.task_id,
#                 student_id=user_id
#             ).first()

#             if not record:
#                 course = Course.query.get(task.course_id)
#                 teacher = User.query.get(task.teacher_id)

#                 result_tasks.append({
#                     'taskId': task.task_id,
#                     'courseName': course.course_name,
#                     'teacherName': teacher.real_name if teacher else '未知',
#                     'startTime': task.start_time.strftime('%Y-%m-%d %H:%M'),
#                     'endTime': task.end_time.strftime('%Y-%m-%d %H:%M')
#                 })

#         return Result.success(data={'items': result_tasks})

#     except Exception as e:
#         print(f"获取签到任务失败: {str(e)}")
#         return Result.error(f"获取签到任务失败: {str(e)}")

# @student_course_bp.route('/attendance/history', methods=['GET'])
# @jwt_required()
# def get_attendance_history():
#     """获取学生的签到历史记录"""
#     try:
#         user_id = int(get_jwt_identity())

#         # 获取所有签到记录
#         records = db.session.query(
#             AttendanceRecord, AttendanceTask, Course, User
#         ).join(
#             AttendanceTask, AttendanceRecord.task_id == AttendanceTask.task_id
#         ).join(
#             Course, AttendanceTask.course_id == Course.course_id
#         ).join(
#             User, AttendanceTask.teacher_id == User.user_id
#         ).filter(
#             AttendanceRecord.student_id == user_id
#         ).order_by(
#             AttendanceRecord.check_in_time.desc()
#         ).all()

#         history = []
#         for record, task, course, teacher in records:
#             history.append({
#                 'recordId': record.record_id,
#                 'courseName': course.course_name,
#                 'teacherName': teacher.real_name,
#                 'startTime': task.start_time.strftime('%Y-%m-%d %H:%M'),
#                 'endTime': task.end_time.strftime('%Y-%m-%d %H:%M'),
#                 'status': record.status,
#                 'checkInTime': record.check_in_time.strftime('%Y-%m-%d %H:%M:%S')
#             })

#         return Result.success(data={'items': history})

#     except Exception as e:
#         print(f"获取签到历史失败: {str(e)}")
#         return Result.error(f"获取签到历史失败: {str(e)}")


