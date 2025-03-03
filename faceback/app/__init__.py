from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import  Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 配置CORS
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:8085"],
                     "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # 允许的方法
            "allow_headers": ["Content-Type", "Authorization"],  # 允许的请求头
            "supports_credentials": True  # 允许携带凭证
        }
    })

    db.init_app(app)
    jwt.init_app(app)

    from app.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    return app
