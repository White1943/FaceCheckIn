from app import db
from datetime import datetime

class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, name='record_id')
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False, name='student_id')
    task_id = db.Column(db.Integer, db.ForeignKey('attendance_tasks.task_id'), nullable=False)
    check_in_time = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.Enum('正常', '迟到', '缺课'), name='check_in_type', nullable=False)
    location_lat = db.Column(db.Numeric(10, 7))
    location_lng = db.Column(db.Numeric(10, 7))
    created_at = db.Column(db.DateTime, default=datetime.now)
    face_image = db.Column(db.String(255))
