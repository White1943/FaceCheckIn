from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    real_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.Enum('教师', '学生', '管理员'), nullable=False)
    email = db.Column(db.String(100))
    status = db.Column(db.Integer, default=1)  # 1: 正常, 0: 禁用
    avatar = db.Column(db.String(255), default='/avatar2.jpg')  # 添加默认头像

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        return {
            'username': self.username,
            'role': self.role,
            'realName': self.real_name,
            'email': self.email,
            'avatar': self.avatar
        }