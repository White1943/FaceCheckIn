from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # 配置CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:8085"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    db.init_app(app)
    jwt.init_app(app)
    
    # 注册蓝图
    from app.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    return app