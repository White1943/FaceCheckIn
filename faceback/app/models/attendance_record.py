from app import db
from datetime import datetime

class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, name='record_id')
    task_id = db.Column(db.Integer, db.ForeignKey('attendance_tasks.task_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False, name='student_id')
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'), nullable=False)
    check_in_time = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.Enum('正常', '迟到', '缺课', '异常'), name='check_in_type', nullable=False)
    location_lat = db.Column(db.Numeric(10, 7))
    location_lng = db.Column(db.Numeric(10, 7))
    created_at = db.Column(db.DateTime, default=datetime.now)
    face_image = db.Column(db.String(255))
    review_status = db.Column(db.Enum('未申诉', '待审核', '已审核'), default='未申诉', nullable=False)
    appeal_reason = db.Column(db.Text)

    task = db.relationship('AttendanceTask', backref='records')
    student = db.relationship('User', backref='attendance_records')
    course = db.relationship('Course', backref='attendance_records')
