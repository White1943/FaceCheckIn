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
    # 处理 OPTIONS 请求
    if request.method == 'OPTIONS':
        return Result.success()

    try:
        # 打印详细的请求信息
        print(f"请求方法: {request.method}")
        print(f"Content-Type: {request.content_type}")
        print(f"表单数据: {request.form}")
        print(f"JSON数据: {request.json if request.is_json else None}")
        print(f"文件: {request.files}")

        current_user_id = get_jwt_identity()
        student = User.query.get(current_user_id)

        # 尝试从不同来源获取task_id和位置信息
        if request.is_json:
            json_data = request.get_json()
            print("JSON数据:", json_data)
            if json_data:
                task_id = json_data.get('task_id') or json_data.get('taskId')
                lat = json_data.get('location_lat') or json_data.get('locationLat') or 0
                lng = json_data.get('location_lng') or json_data.get('locationLng') or 0
        elif request.form:
            task_id = request.form.get('task_id') or request.form.get('taskId')
            lat = request.form.get('location_lat') or request.form.get('locationLat') or 0
            lng = request.form.get('location_lng') or request.form.get('locationLng') or 0
        elif request.data:
            try:
                import json
                data = json.loads(request.data)
                task_id = data.get('task_id') or data.get('taskId')
                lat = data.get('location_lat') or data.get('locationLat') or 0
                lng = data.get('location_lng') or data.get('locationLng') or 0
                print("手动解析JSON:", data)
            except:
                # 如果解析失败，设置默认值
                task_id = None
                lat = 0
                lng = 0

        # 如果没有获取到位置信息，设置为默认值
        if 'lat' not in locals() or lat is None:
            lat = 0
        if 'lng' not in locals() or lng is None:
            lng = 0

        print(f"找到的task_id: {task_id}, 位置: lat={lat}, lng={lng}")

        if not task_id:
            return Result.error("缺少签到任务ID，请检查请求格式")

        task_id = int(task_id)
        print(f"处理的task_id: {task_id}")


        # 检查任务是否存在
        task = AttendanceTask.query.get(task_id)
        if not task:
            return Result.error('签到任务不存在', code=404)

        # 检查是否已签到
        existing_record = AttendanceRecord.query.filter_by(
            task_id=task_id,
            student_id=current_user_id
        ).first()

        if existing_record:
            return Result.error('您已经签到过了', code=400)

        # 检查时间是否在有效范围内
        current_time = datetime.now()
        if current_time > task.end_time:
            return Result.error('签到已结束', code=400)

        # 获取人脸图像
        if 'image' not in request.files and 'face_image' not in request.files:
            return Result.error('缺少人脸图像', code=400)

        # 同时兼容两种键名
        if 'face_image' in request.files:
            image_file = request.files['face_image']
        else:
            image_file = request.files['image']
        
        if not image_file:
            return Result.error('人脸图像无效', code=400)

        # 保存图像
        filename = f"{current_user_id}_{task_id}_{int(time.time())}.jpg"
        uploads_dir = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), 'attendance')
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir, exist_ok=True)

        image_path = os.path.join(uploads_dir, filename)
        image_file.save(image_path)

        # 人脸识别处理
        try:
            # 加载上传的图像
            upload_image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(upload_image)

            if not face_locations:
                # 未检测到人脸，可以删除已上传的图片
                os.remove(image_path)
                return Result.error('未检测到人脸，请确保人脸清晰可见', code=400)

            if len(face_locations) > 1:
                # 检测到多个人脸，可以删除已上传的图片
                os.remove(image_path)
                return Result.error('检测到多个人脸，请确保只有您自己的脸出现在画面中', code=400)

            # 获取上传图像的人脸编码
            face_encoding = face_recognition.face_encodings(upload_image, face_locations)[0]

            # 加载学生头像进行对比
            if student.avatar:
                # 处理头像路径
                avatar_file = student.avatar.lstrip('/')
                if avatar_file.startswith('static/'):
                    avatar_file = avatar_file[7:]  # 移除 'static/' 前缀

                user_avatar_path = os.path.join(current_app.root_path, 'static', avatar_file)
                print(f"用户头像路径 (对比路径): {user_avatar_path}")
            else:
                # 默认头像路径
                user_avatar_path = os.path.join(current_app.root_path, 'static', 'images', 'avatars', 'default.jpg')
                print(f"使用默认头像路径: {user_avatar_path}")

            # 检查文件是否存在
            if not os.path.exists(user_avatar_path):
                print(f"用户头像不存在: {user_avatar_path}")
                return Result.error("找不到您的头像文件，请重新上传头像", code=400)

            # 加载用户头像并进行人脸比对
            user_image = face_recognition.load_image_file(user_avatar_path)
            user_face_locations = face_recognition.face_locations(user_image)

            if not user_face_locations:
                print(f"用户 {current_user_id} 的头像中未检测到人脸")
                return Result.error("您的头像中未检测到人脸，请重新上传清晰的头像照片", code=400)

            # 提取人脸特征
            user_face_encoding = face_recognition.face_encodings(user_image, [user_face_locations[0]])[0]

            # 比较人脸
            match_results = face_recognition.compare_faces([user_face_encoding], face_encoding, tolerance=0.6)
            distance = face_recognition.face_distance([user_face_encoding], face_encoding)[0]

            print(f"人脸匹配结果: {match_results[0]}, 距离: {distance}")

            # 判断签到状态
            status = '正常'  # 默认正常

            # 检查是否为异常签到 - 距离大于0.35认为是不匹配的
            if distance > 0.35:
                # 获取今天该学生之前的异常签到次数
                today = datetime.now().date()
                today_start = datetime.combine(today, datetime.min.time())
                today_end = datetime.combine(today, datetime.max.time())

                failure_count = AttendanceRecord.query.filter(
                    AttendanceRecord.student_id == current_user_id,
                    AttendanceRecord.created_at.between(today_start, today_end),
                    AttendanceRecord.status == '异常'
                ).count()

                # 如果已经有2次或以上异常记录，这次将标记为异常
                if failure_count >= 2:
                    status = '异常'
                    print(f"用户 {current_user_id} 今日已有 {failure_count} 次人脸识别失败，标记为异常")
                else:
                    # 仍然允许签到，但检查是否迟到
                    if current_time > task.start_time + (task.end_time - task.start_time) * 0.5:
                        status = '迟到'
            else:
                # 人脸匹配成功，检查是否迟到
                if current_time > task.start_time + (task.end_time - task.start_time) * 0.5:
                    status = '迟到'

            # 创建签到记录前确保所有需要的变量都已定义
            if 'lat' not in locals():
                lat = 0
            if 'lng' not in locals():
                lng = 0

            # 创建签到记录
            record = AttendanceRecord(
                task_id=task_id,
                student_id=current_user_id,
                course_id=task.course_id,
                check_in_time=current_time,
                status=status,
                location_lat=lat,
                location_lng=lng,
                face_image=filename,
                review_status='未申诉'
            )

            db.session.add(record)
            db.session.commit()

            response_data = {
                'status': status,
                'time': current_time.strftime('%Y-%m-%d %H:%M:%S')
            }

            # 如果是异常签到，告知用户可以申诉
            if status == '异常':
                response_data['recordId'] = record.id
                return Result.success(
                    data=response_data,
                    message='签到已记录，但人脸识别异常，您可以提交申诉'
                )
            else:
                return Result.success(
                    data=response_data,
                    message='签到成功'
                )

        except Exception as e:
            print(f"人脸识别处理失败: {str(e)}")
            return Result.error(f'人脸识别处理失败: {str(e)}', code=500)

    except Exception as e:
        db.session.rollback()
        print(f"签到失败: {str(e)}")
        import traceback
        traceback.print_exc()  # 打印详细错误堆栈
        return Result.error(f'签到失败: {str(e)}', code=500)

# 添加申诉相关路由
@student_attendance_bp.route('/appeal', methods=['POST'])
@jwt_required()
def submit_appeal():
    try:
        student_id = get_jwt_identity()
        data = request.json

        record_id = data.get('recordId')
        reason = data.get('reason')

        if not record_id or not reason:
            return Result.error('缺少必要参数', code=400)

        # 获取记录
        record = AttendanceRecord.query.get(record_id)
        if not record:
            return Result.error('签到记录不存在', code=404)

        # 验证是否是本人的记录
        if record.student_id != student_id:
            return Result.error('无权限操作此记录', code=403)

        # 验证是否是异常记录且未申诉
        if record.status != '异常' or record.review_status != '未申诉':
            return Result.error('只能申诉异常签到记录，且不能重复申诉', code=400)

        # 更新申诉状态
        record.review_status = '待审核'
        record.appeal_reason = reason

        db.session.commit()

        return Result.success(message='申诉提交成功，请等待教师审核')

    except Exception as e:
        db.session.rollback()
        print(f"提交申诉失败: {str(e)}")
        return Result.error(f'提交申诉失败: {str(e)}', code=500)

@student_attendance_bp.route('/appeals', methods=['GET'])
@jwt_required()
def get_appeals():
    try:
        student_id = get_jwt_identity()

        # 获取所有申诉记录
        appeals = db.session.query(
            AttendanceRecord, AttendanceTask, Course
        ).join(
            AttendanceTask, AttendanceRecord.task_id == AttendanceTask.task_id
        ).join(
            Course, AttendanceTask.course_id == Course.course_id
        ).filter(
            AttendanceRecord.student_id == student_id,
            AttendanceRecord.review_status.in_(['待审核', '已审核'])
        ).order_by(
            AttendanceRecord.created_at.desc()
        ).all()

        result = []
        for record, task, course in appeals:
            result.append({
                'recordId': record.id,
                'taskId': task.task_id,
                'courseName': course.course_name,
                'checkInTime': record.check_in_time.strftime('%Y-%m-%d %H:%M:%S'),
                'status': record.status,
                'reviewStatus': record.review_status,
                'appealReason': record.appeal_reason
            })

        return Result.success(data={'items': result})

    except Exception as e:
        print(f"获取申诉记录失败: {str(e)}")
        return Result.error(f'获取申诉记录失败: {str(e)}', code=500)


