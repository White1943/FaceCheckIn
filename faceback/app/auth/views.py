from flask import request, Blueprint, current_app
from flask_login import login_required
from sqlalchemy.sql.functions import current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from app.auth import auth_bp
# from . import auth
from app.utils.response import Result
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from cryptography.hazmat.primitives import serialization, padding
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64

from app.models.user import User
import logging

# 生成密钥对
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)
public_key = private_key.public_key()

def decrypt_password(encrypted_password, private_key):
    try:
        # Base64解码
        encrypted_bytes = base64.b64decode(encrypted_password)

        # RSA解密
        decrypted_bytes = private_key.decrypt(
            encrypted_bytes,
            asym_padding.PKCS1v15()
        )

        # 转换为字符串
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        print(f"解密失败: {str(e)}")
        return None

@auth_bp.route('/public-key', methods=['GET'])
def get_public_key():
    try:
        # 获取公钥的PEM格式
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        # 转换为字符串并去除头尾
        pem_str = pem.decode('utf-8')
        key_str = pem_str.replace('-----BEGIN PUBLIC KEY-----\n', '')
        key_str = key_str.replace('\n-----END PUBLIC KEY-----\n', '')

        return Result.success(data={'publicKey': key_str})
    except Exception as e:
        print(f"获取公钥失败: {str(e)}")
        return Result.error("获取公钥失败")

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        # 解密密码
        if password:
            password = decrypt_password(password, private_key)

        if not username or not password:
            return Result.error("用户名和密码不能为空")

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            if user.status == 0:
                return Result.error("账号已被禁用")

            # 生成 JWT token
            access_token = create_access_token(identity=str(user.user_id))

            return Result.success(data={
                'token': access_token,
                'user': {
                    'username': user.username,
                    'role': user.role,
                    'realName': user.real_name,
                    'email': user.email,
                    'avatar': user.avatar  # 添加头像
                }
            }, message='登录成功')

        return Result.error("用户名或密码错误")

    except Exception as e:
        print("Login error:", str(e))
        return Result.error("登录失败")

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        print("Parsed JSON data:", data)

        # 数据验证
        required_fields = ['username', 'password', 'realName', 'role']
        for field in required_fields:
            if not data.get(field):
                return Result.error(f'请填写{field}', code=400)

        # 检查用户名是否已存在
        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user:
            return Result.error('用户名已存在', code=400)

        # 创建新用户
        try:
            user = User(
                username=data['username'],
                real_name=data['realName'],
                role=data['role'],
                email=data.get('email')
            )
            user.set_password(data['password'])

            db.session.add(user)
            db.session.commit()

            return Result.success(message="注册成功")

        except Exception as e:
            db.session.rollback()
            return Result.error(f"注册失败: {str(e)}", code=500)

    except Exception as e:
        return Result.error(f"注册失败: {str(e)}", code=500)

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return Result.error("用户不存在")
            
        return Result.success(data={
            'username': user.username,
            'role': user.role,
            'realName': user.real_name,
            'email': user.email,
            'avatar': user.avatar  # 添加头像
        }, message='获取成功')
        
    except Exception as e:
        print("Get profile error:", str(e))
        return Result.error("获取用户信息失败")

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        # JWT token 由前端删除即可
        return Result.success(message="退出成功")
    except Exception as e:
        print("Logout error:", str(e))
        return Result.error("退出失败")































# app\auth\views.py
