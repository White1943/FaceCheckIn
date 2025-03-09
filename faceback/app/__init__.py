from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import Config


db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 配置CORS
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:8085"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })


    db.init_app(app)
    jwt.init_app(app)


        # 注册蓝图
    from  .auth import auth_bp
    from  .routes import  face_bp, course_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(face_bp, url_prefix='/api/face')
    app.register_blueprint(course_bp, url_prefix='/api/course')



    return app
