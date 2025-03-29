# rom app import db
# import time
#
# class AttendanceTask(db.Model):
#     __tablename__ = 'attendance_tasks'
#
#     id = db.Column(db.Integer, primary_key=True)
#     course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
#     start_time = db.Column(db.Integer, nullable=False)  # Unix时间戳
#     end_time = db.Column(db.Integer, nullable=False)    # Unix时间戳
#     location = db.Column(db.String(100))
#     location_range = db.Column(db.Integer, default=100)  # 范围(米)
#     created_at = db.Column(db.Integer, default=lambda: int(time.time()))
#
#     # 关系
#     records = db.relationship('AttendanceRecord', backref='task', lazy=True)
#
# class AttendanceRecord(db.Model):
#     __tablename__ = 'attendance_records'
#
#     id = db.Column(db.Integer, primary_key=True)
#     task_id = db.Column(db.Integer, db.ForeignKey('attendance_tasks.id'), nullable=False)
#     student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#     status = db.Column(db.String(20), default='normal')  # normal, late, absent
#     sign_time = db.Column(db.Integer, nullable=False, default=lambda: int(time.time()))
#     location_lat = db.Column(db.Float)
#     location_lng = db.Column(db.Float)
#
#     # 联合唯一索引
#     __table_args__ = (db.UniqueConstraint('task_id', 'student_id', name='uix_task_student'),)
