# 这次进行统一管理路由
import face_recognition
from flask import Flask, jsonify, request, redirect, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.attendance_task import AttendanceTask
from app.models.user import User
from app.utils.face_utils import FaceUtils
from app.utils.response import Result
from app.models.attendance_record import AttendanceRecord
from app.models.course_students import CourseStudents
from app.models.course import Course


from app import db
from datetime import datetime
import os



ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
face_bp = Blueprint('api/face', __name__)
face_utils = FaceUtils()



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_image():
    # 检测图片是否上传成功
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # 图片上传成功，检测图片中的人脸
            return detect_faces_in_image(file)

    # 图片上传失败，输出以下html代码
    return '''
    <!doctype html>
    <title>Is this a picture of Obama?</title>
    <h1>Upload a picture and see if it's a picture of Obama!</h1>
    <form method="POST" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit" value="Upload">
    </form>
    '''


def detect_faces_in_image(file_stream):
    # 用face_recognition.face_encodings(img)接口提前把奥巴马人脸的编码录入
    known_face_encoding = [-0.09634063,  0.12095481, -0.00436332, -0.07643753,  0.0080383,
                            0.01902981, -0.07184699, -0.09383309,  0.18518871, -0.09588896,
                            0.23951106,  0.0986533 , -0.22114635, -0.1363683 ,  0.04405268,
                            0.11574756, -0.19899382, -0.09597053, -0.11969153, -0.12277931,
                            0.03416885, -0.00267565,  0.09203379,  0.04713435, -0.12731361,
                           -0.35371891, -0.0503444 , -0.17841317, -0.00310897, -0.09844551,
                           -0.06910533, -0.00503746, -0.18466514, -0.09851682,  0.02903969,
                           -0.02174894,  0.02261871,  0.0032102 ,  0.20312519,  0.02999607,
                           -0.11646006,  0.09432904,  0.02774341,  0.22102901,  0.26725179,
                            0.06896867, -0.00490024, -0.09441824,  0.11115381, -0.22592428,
                            0.06230862,  0.16559327,  0.06232892,  0.03458837,  0.09459756,
                           -0.18777156,  0.00654241,  0.08582542, -0.13578284,  0.0150229 ,
                            0.00670836, -0.08195844, -0.04346499,  0.03347827,  0.20310158,
                            0.09987706, -0.12370517, -0.06683611,  0.12704916, -0.02160804,
                            0.00984683,  0.00766284, -0.18980607, -0.19641446, -0.22800779,
                            0.09010898,  0.39178532,  0.18818057, -0.20875394,  0.03097027,
                           -0.21300618,  0.02532415,  0.07938635,  0.01000703, -0.07719778,
                           -0.12651891, -0.04318593,  0.06219772,  0.09163868,  0.05039065,
                           -0.04922386,  0.21839413, -0.02394437,  0.06173781,  0.0292527 ,
                            0.06160797, -0.15553983, -0.02440624, -0.17509389, -0.0630486 ,
                            0.01428208, -0.03637431,  0.03971229,  0.13983178, -0.23006812,
                            0.04999552,  0.0108454 , -0.03970895,  0.02501768,  0.08157793,
                           -0.03224047, -0.04502571,  0.0556995 , -0.24374914,  0.25514284,
                            0.24795187,  0.04060191,  0.17597422,  0.07966681,  0.01920104,
                           -0.01194376, -0.02300822, -0.17204897, -0.0596558 ,  0.05307484,
                            0.07417042,  0.07126575,  0.00209804]

    # 载入用户上传的图片
    img = face_recognition.load_image_file(file_stream)
    # 为用户上传的图片中的人脸编码
    unknown_face_encodings = face_recognition.face_encodings(img)

    face_found = False
    is_obama = False

    if len(unknown_face_encodings) > 0:
        face_found = True
        # 看看图片中的第一张脸是不是奥巴马
        match_results = face_recognition.compare_faces([known_face_encoding], unknown_face_encodings[0])
        if match_results[0]:
            is_obama = True

    # 讲识别结果以json键值对的数据结构输出
    result = {
        "face_found_in_image": face_found,
        "is_picture_of_obama": is_obama
    }
    return jsonify(result)


@face_bp.route('/check-in', methods=['POST'])
@jwt_required()
def check_in():
    try:
        # 获取当前用户
        user_id = get_jwt_identity()
        task_id = request.form.get('task_id')

        # 检查签到任务是否存在且在有效时间内
        task = AttendanceTask.query.get(task_id)
        if not task:
            return Result.error("签到任务不存在")

        if task.status != '进行中':
            return Result.error("签到任务已结束")

        # 获取上传的图片
        if 'file' not in request.files:
            return Result.error("未上传图片")

        file = request.files['file']
        if file.filename == '':
            return Result.error("未选择图片")

        # 保存上传的图片
        upload_path = face_utils.save_upload_file(file)

        # 获取用户注册时的人脸图片
        user = User.query.get(user_id)
        registered_face = user.face_image  # 假设用户模型中有face_image字段

        # 比对人脸
        if face_utils.compare_faces(registered_face, upload_path):
            # 创建签到记录
            now = datetime.now()
            status = '正常' if now <= task.end_time else '迟到'

            attendance_record = AttendanceRecord(
                user_id=user_id,
                task_id=task_id,
                check_in_time=now,
                status=status,
                face_image=upload_path
            )

            db.session.add(attendance_record)
            db.session.commit()

            return Result.success(message="签到成功")
        else:
            return Result.error("人脸识别失败，请重试")

    except Exception as e:
        print(f"Check-in error: {str(e)}")
        return Result.error("签到失败")

@face_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    """获取当前可签到的任务"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if user.role == '学生':
            # 获取学生的课程对应的签到任务
            tasks = AttendanceTask.query.join(Course).filter(
                Course.id.in_([c.id for c in user.courses]),
                AttendanceTask.status == '进行中'
            ).all()
        else:
            # 获取教师创建的签到任务
            tasks = AttendanceTask.query.filter_by(
                teacher_id=user_id,
                status='进行中'
            ).all()

        return Result.success(data=[{
            'id': task.id,
            'course_name': task.course.name,
            'start_time': task.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': task.end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': task.status
        } for task in tasks])

    except Exception as e:
        print(f"Get tasks error: {str(e)}")
        return Result.error("获取签到任务失败")
