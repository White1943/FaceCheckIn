from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import Config
import os


db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 配置CORS
    CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]}})

    #  uploads目录是放在与app同级的位置
    base_dir = os.path.dirname(app.root_path)  # 获取app的父目录，faceback/
    uploads_dir = os.path.join(base_dir, 'uploads')
    app.config['UPLOADED_PHOTOS_DEST'] = uploads_dir

    # 确保上传目录存在
    attendance_dir = os.path.join(uploads_dir, 'attendance')
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)
    if not os.path.exists(attendance_dir):
        os.makedirs(attendance_dir)

    db.init_app(app)
    jwt.init_app(app)

    # 注册蓝图
    from .auth import auth_bp
    from .routes import face_bp
    from .courses import course_bp
    from app.attendance import teacher_attendance_bp
    from app.student import student_course_bp, student_attendance_bp
    from app.personal import personal_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(face_bp, url_prefix='/api/face')
    app.register_blueprint(course_bp, url_prefix='/api/course')
    app.register_blueprint(teacher_attendance_bp, url_prefix='/api/teacher/attendance')
    app.register_blueprint(student_course_bp, url_prefix='/api/stu/course')
    app.register_blueprint(student_attendance_bp, url_prefix='/api/stu/attendance')
    app.register_blueprint(personal_bp, url_prefix='/api/personal')

    # 修改：更新静态文件路由
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        # 直接传递uploads_dir作为目录
        return send_from_directory(uploads_dir, filename)

    return app
