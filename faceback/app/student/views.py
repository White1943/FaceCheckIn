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
from sqlalchemy import or_



# 允许的文件类型
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'PNG', 'JPG', 'JPEG'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].upper() in ALLOWED_EXTENSIONS

@student_course_bp.route('/courses', methods=['GET'])
@jwt_required()
def get_student_enrolled_courses():
    """Fetches courses the logged-in student is currently enrolled in."""
    try:
        student_id = int(get_jwt_identity())
        user = User.query.get(student_id)
        if not user or user.role != '学生':
            return Result.error("用户无效或非学生", code=403)
        search_term = request.args.get('search', None, type=str)
        query = user.enrolled_courses
        if search_term:
            search_pattern = f"%{search_term}%"
            query = query.filter(
                or_(
                    Course.course_name.like(search_pattern),
                    Course.description.like(search_pattern),
                   )
            )
        enrolled_courses = query.order_by(Course.course_name).all()
        return Result.success(data=[course.to_dict() for course in enrolled_courses])
    except Exception as e:
        current_app.logger.error(f"Error fetching enrolled courses for student {student_id}: {e}")
        traceback.print_exc()
        return Result.error("获取已选课程列表失败")

@student_course_bp.route('/available', methods=['GET'])
@jwt_required()
def get_available_courses_for_student():
    """Fetches courses available for the logged-in student to enroll in."""
    try:
        student_id = int(get_jwt_identity())
        user = User.query.get(student_id)
        if not user or user.role != '学生':
            return Result.error("用户无效或非学生", code=403)

        # --- Get search query ---
        search_term = request.args.get('search', None, type=str)
        # --- End Get search query ---

        enrolled_course_ids = [course.course_id for course in user.enrolled_courses]

        # Base query
        available_courses_query = Course.query.filter(
            Course.teacher_id != student_id,
            ~Course.course_id.in_(enrolled_course_ids)
        )

        # --- Apply search filter ---
        if search_term:
            search_pattern = f"%{search_term}%"
            available_courses_query = available_courses_query.filter(
                 or_(
                    Course.course_name.like(search_pattern),
                    Course.description.like(search_pattern),
                    )
            )
        # --- End Apply search filter ---

        available_courses = available_courses_query.order_by(Course.course_name).all()
        return Result.success(data=[course.to_dict() for course in available_courses])
    except Exception as e:
        current_app.logger.error(f"Error fetching available courses: {e}")
        traceback.print_exc()
        return Result.error("获取可选课程列表失败")

@student_course_bp.route('/select', methods=['POST'])
@jwt_required()
def select_course_for_student():
    try:
        student_id = int(get_jwt_identity())
        user = User.query.get(student_id)
        if not user or user.role != '学生':
            return Result.error("用户无效或非学生", code=403)
        data = request.get_json()
        if not data or 'courseId' not in data:
            return Result.error("请求体缺少 courseId", code=400)
        course_id = data['courseId']
        course = Course.query.get(course_id)
        if not course: return Result.error("课程不存在", code=404)
        if course in user.enrolled_courses: return Result.error("您已选修此课程", code=400)
        user.enrolled_courses.append(course)
        db.session.commit()
        return Result.success(message="选课成功")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error selecting course {data.get('courseId')} for student {student_id}: {e}")
        traceback.print_exc()
        return Result.error(f"选课失败: {str(e)}")

@student_course_bp.route('/join', methods=['POST'])
@jwt_required()
def join_course_route():
    # Implement specific join logic if needed, otherwise it might be the same as select
    return select_course_for_student() # Or custom logic

@student_course_bp.route('/<int:course_id>/leave', methods=['POST'])
@jwt_required()
def leave_course_route(course_id):
    """Allows the logged-in student to leave/unenroll from a course."""
    try:
        student_id = int(get_jwt_identity())
        user = User.query.get(student_id)
        if not user or user.role != '学生':
            return Result.error("用户无效或非学生", code=403)
        course = Course.query.get(course_id)
        if not course:
            return Result.error("课程不存在", code=404)
        if course not in user.enrolled_courses:
            return Result.error("您未选修此课程", code=400)
        user.enrolled_courses.remove(course)
        db.session.commit()
        return Result.success(message="退课成功")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error leaving course {course_id} for student {student_id}: {e}")
        traceback.print_exc()
        return Result.error(f"退课失败: {str(e)}")

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
                return Result.error('未检测到人脸，请确保人脸清晰可见以及确保已上传人脸照片', code=400)

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

            # 判断人脸识别是否通过
            is_face_valid = match_results[0] and distance <= 0.35

            # 如果人脸识别失败，检查今天失败的次数
            if not is_face_valid:
                # 获取今天的日期范围
                today = datetime.now().date()
                today_start = datetime.combine(today, datetime.min.time())
                today_end = datetime.combine(today, datetime.max.time())

                # 改用更可靠的方式来跟踪失败尝试 - 使用单独的临时表或使用文件缓存
                # 临时解决方案：使用缓存文件在服务器端存储失败尝试
                cache_dir = os.path.join(current_app.root_path, 'temp')
                os.makedirs(cache_dir, exist_ok=True)
                cache_file = os.path.join(cache_dir, f"face_attempts_{current_user_id}_{task_id}.txt")

                # 读取已有的失败尝试
                attempt_filenames = []
                if os.path.exists(cache_file):
                    try:
                        with open(cache_file, 'r') as f:
                            attempt_filenames = [line.strip() for line in f.readlines()]
                    except Exception as e:
                        print(f"读取缓存文件失败: {str(e)}")

                # 当前尝试添加到列表
                attempt_filenames.append(filename)

                # 获取真正的失败次数
                total_failures = len(attempt_filenames)
                print(f"用户 {current_user_id} 任务 {task_id} 已有 {total_failures} 次人脸识别失败尝试")

                # 如果总失败次数 < 3，保存这次尝试并返回错误提示
                if total_failures < 3:
                    # 保存最新的尝试列表
                    try:
                        with open(cache_file, 'w') as f:
                            for name in attempt_filenames:
                                f.write(f"{name}\n")
                    except Exception as e:
                        print(f"保存缓存文件失败: {str(e)}")

                    return Result.error(
                        message=f'人脸识别未通过，请重试。这是第 {total_failures} 次尝试，连续 3 次失败将记录为异常签到',
                        code=400
                    )
                else:
                    # 如果已经有2次失败，这次是第3次，创建一个异常签到记录
                    status = '异常'

                    # 使用最后一次失败（当前）的图片
                    final_image = filename

                    # 成功创建异常记录后，删除缓存文件
                    try:
                        os.remove(cache_file)
                    except Exception as e:
                        print(f"删除缓存文件失败: {str(e)}")
            else:
                # 人脸识别通过，设置签到状态
                status = '正常'

                # 检查是否迟到
                if current_time > task.start_time + (task.end_time - task.start_time) * 0.5:
                    status = '迟到'

                final_image = filename

                # 如果有缓存文件，删除它
                cache_file = os.path.join(current_app.root_path, 'temp', f"face_attempts_{current_user_id}_{task_id}.txt")
                if os.path.exists(cache_file):
                    try:
                        os.remove(cache_file)
                    except Exception as e:
                        print(f"删除缓存文件失败: {str(e)}")

            # 获取地理位置
            location_lat = request.form.get('location_lat', 0)
            location_lng = request.form.get('location_lng', 0)

            # 创建正式签到记录 - 注意这里不再使用check_in_type而是使用status
            if is_face_valid or total_failures >= 3:
                record = AttendanceRecord(
                    task_id=task_id,
                    student_id=current_user_id,
                    course_id=task.course_id,
                    check_in_time=current_time,
                    status=status,  # 使用'正常', '迟到', '异常'等值
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

            # 理论上代码不会执行到这里
            return Result.error("未知错误，请重试", code=500)

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


