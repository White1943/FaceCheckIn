from app import db
from datetime import datetime

class AttendanceTask(db.Model):
    __tablename__ = 'attendance_tasks'

    task_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    location_lat = db.Column(db.Numeric(10, 7))
    location_lng = db.Column(db.Numeric(10, 7))
    status = db.Column(db.Enum('active', 'ended', 'cancelled'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 关系
    course = db.relationship('Course', backref='attendance_tasks')
    teacher = db.relationship('User', backref='created_tasks')
