from flask import jsonify, request, current_app, make_response, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from datetime import datetime
import os
from app.personal import personal_bp
from app.utils.response import Result
import time
from werkzeug.utils import secure_filename

# 允许的文件类型
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'PNG', 'JPG', 'JPEG'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].upper() in ALLOWED_EXTENSIONS


def generate_unique_filename(original_filename, user_id):
    """生成唯一的文件名"""
    # 获取文件扩展名
    ext = original_filename.rsplit('.', 1)[1].lower()
    # 生成文件名：avatar_用户ID_时间戳.扩展名
    return f'avatar_{user_id}_{int(time.time())}.{ext}'


@personal_bp.route('/info', methods=['GET'])
@jwt_required()
def get_personal_info():
  current_user_id = get_jwt_identity()
  user = User.query.get(current_user_id)
  if user:
    return jsonify({
      'code': 200,
      'data': {
        'username': user.username,
        'role': user.role,
        'name': user.real_name,
        'email': user.email,
        'avatar': user.avatar
      }
    })
  return jsonify({'code': 404, 'message': '用户不存在'})


@personal_bp.route('/info', methods=['PUT'])
@jwt_required()
def update_personal_info():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'code': 404, 'message': '用户不存在'})

        # 只处理个人信息更新
        data = request.get_json()
        user.real_name = data.get('name', user.real_name)
        user.email = data.get('email', user.email)

        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': {
                'username': user.username,
                'role': user.role,
                'name': user.real_name,
                'email': user.email,
                'avatar': user.avatar
            }
        })

    except Exception as e:
        db.session.rollback()
        print(f"更新个人信息失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'更新失败: {str(e)}'})


@personal_bp.route('/avatar', methods=['POST'])
@jwt_required()
def update_avatar():
    try:
        print("开始处理头像上传请求")
        print("请求方法:", request.method)
        print("请求头:", request.headers)
        print("请求文件:", request.files)
        print("请求表单:", request.form)
        
        # 检查文件是否存在于请求中
        if 'avatar' not in request.files:
            print("请求中没有avatar文件，尝试获取所有文件：", list(request.files.keys()))
            # 尝试从请求的第一个文件开始处理
            if request.files:
                file_key = list(request.files.keys())[0]
                file = request.files[file_key]
                print(f"使用第一个可用文件: {file_key} -> {file.filename}")
            else:
                return Result.error(message='没有上传文件', code=400)
        else:
            file = request.files['avatar']
            
        print(f"获取到的文件: {file.filename}")

        # 检查文件名是否为空
        if file.filename == '':
            return Result.error(message='文件名为空', code=400)

        # 获取安全的文件名
        filename = secure_filename(file.filename)

        # 检查文件类型
        if not allowed_file(filename):
            return Result.error(message='不支持的文件类型，仅支持 JPG/PNG 格式', code=400)

        # 获取当前用户
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return Result.error(message='用户不存在', code=404)

        # 确保上传目录存在
        avatar_dir = os.path.join(current_app.root_path, 'static', 'images', 'avatars')
        os.makedirs(avatar_dir, exist_ok=True)

        # 生成新文件名
        ext = filename.rsplit('.', 1)[1].lower()
        new_filename = f'avatar_{current_user_id}_{int(time.time())}.{ext}'
        file_path = os.path.join(avatar_dir, new_filename)

        # 删除旧头像
        if user.avatar:
            old_avatar_path = os.path.join(current_app.root_path, 'static', user.avatar.lstrip('/'))
            try:
                if os.path.exists(old_avatar_path):
                    os.remove(old_avatar_path)
            except Exception as e:
                print(f"删除旧头像失败: {str(e)}")

        # 保存新文件
        try:
            file.save(file_path)
            print(f"文件已保存到: {file_path}")
        except Exception as e:
            print(f"保存文件失败: {str(e)}")
            return Result.error(message=f'保存文件失败: {str(e)}', code=500)

        # 更新数据库
        try:
            user.avatar = f'/static/images/avatars/{new_filename}'
            db.session.commit()
            print(f"用户头像已更新: {user.avatar}")
        except Exception as e:
            print(f"更新数据库失败: {str(e)}")
            if os.path.exists(file_path):
                os.remove(file_path)
            return Result.error(message=f'更新数据库失败: {str(e)}', code=500)

        return Result.success(
            message='头像上传成功',
            data={'avatar': user.avatar}
        )

    except Exception as e:
        print(f"处理上传请求失败: {str(e)}")
        db.session.rollback()
        return Result.error(message=f'上传失败: {str(e)}', code=500)


@personal_bp.route('/avatar/<path:filename>', methods=['GET'])
def get_avatar(filename):
    """获取头像图片"""
    try:
        avatar_dir = os.path.join(current_app.root_path, 'static', 'images', 'avatars')
        file_path = os.path.join(avatar_dir, filename)

        if not os.path.exists(file_path):
            return jsonify({'code': 404, 'message': '头像不存在'})

        # 读取图片文件并返回
        with open(file_path, 'rb') as f:
            image_data = f.read()

        response = make_response(image_data)
        # 根据文件扩展名设置正确的 Content-Type
        ext = filename.rsplit('.', 1)[1].lower()
        content_type = 'image/jpeg' if ext in ['jpg', 'jpeg'] else 'image/png'
        response.headers['Content-Type'] = content_type
        return response

    except Exception as e:
        print(f"获取头像失败: {str(e)}")
        return jsonify({'code': 500, 'message': f'获取头像失败: {str(e)}'})


@personal_bp.route('/password', methods=['PUT'])
@jwt_required()
def change_password():
  current_user_id = get_jwt_identity()
  user = User.query.get(current_user_id)
  if not user:
    return jsonify({'code': 404, 'message': '用户不存在'})

  data = request.get_json()
  old_password = data.get('oldPassword')
  new_password = data.get('newPassword')

  if not user.check_password(old_password):
    return jsonify({'code': 400, 'message': '原密码错误'})

  user.set_password(new_password)
  try:
    db.session.commit()
    return jsonify({'code': 200, 'message': '密码修改成功'})
  except Exception as e:
    db.session.rollback()
    return jsonify({'code': 500, 'message': '密码修改失败'})
