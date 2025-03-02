from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(32), primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    real_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.Enum('teacher', 'student'), nullable=False)
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Integer, default=1)

    # 关联关系
    courses_teaching = db.relationship('Course', backref='teacher', lazy='dynamic')
    courses_enrolled = db.relationship('CourseStudent', backref='student', lazy='dynamic')
    attendance_records = db.relationship('AttendanceRecord', backref='student', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.id is None:
            self.id = generate_uuid()  # 需要实现generate_uuid函数

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'real_name': self.real_name,
            'role': self.role,
            'email': self.email,
            'phone': self.phone
        }












































    # \app\models\user.py