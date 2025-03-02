from flask import jsonify, request, Blueprint, current_app
from flask_login import login_required
from sqlalchemy.sql.functions import current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from app.auth import auth_bp
# from . import auth
from app.utils.response import Result
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app.models.user import User


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return Result.error("用户名和密码不能为空")
            
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if user.status == 0:
                return Result.error("账号已被禁用")
                
            access_token = create_access_token(identity=user.id)
            return Result.success(data={
                'token': access_token,
                'user': user.to_dict()
            })
        return Result.error("用户名或密码错误")
        
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return Result.error("登录失败")

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        phone = data.get('phone')
        real_name = data.get('realName')
        role = data.get('role', 'student')
        
        # 验证必填字段
        if not all([username, password, email, real_name, role]):
            return Result.error("请填写所有必填字段")
            
        # 检查用户名是否存在
        if User.query.filter_by(username=username).first():
            return Result.error("用户名已存在")
            
        # 检查邮箱是否存在
        if User.query.filter_by(email=email).first():
            return Result.error("邮箱已被注册")
            
        # 创建新用户
        user = User(
            username=username,
            real_name=real_name,
            email=email,
            phone=phone,
            role=role
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return Result.success(message="注册成功")
        
    except Exception as e:
        current_app.logger.error(f"Register error: {str(e)}")
        db.session.rollback()
        return Result.error("注册失败")

@auth_bp.route('/profile', methods=['GET'])
@jwt_required
def get_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return Result.error("用户不存在")
        return Result.success(data=user.to_dict())
    except Exception as e:
        current_app.logger.error(f"Get profile error: {str(e)}")
        return Result.error("获取用户信息失败")

@login_required
@auth_bp.route('/logout')
def logout():
    print(current_user.id)































# app\auth\views.py