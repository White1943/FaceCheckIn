import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    # 从环境变量中获取数据库连接字符串和密钥
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SECRET_KEY = os.getenv('SECRET_KEY')  # 应用密钥
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 禁用 SQLAlchemy 对象修改追踪

    CORS_ORIGINS = os.getenv('CORS_ORIGINS')



    # 文件上传配置
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')

    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # 使用环境变量存储JWT密钥
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
    # 设置合理的过期时间
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)   


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


