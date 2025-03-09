from app import db
from datetime import datetime

class Course(db.Model):
    __tablename__ = 'courses'

    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    semester = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)

    location = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.now)

    # 关系
    teacher = db.relationship('User', back_populates='teaching_courses')
    students = db.relationship(
        'User',
        secondary='course_students',
        back_populates='enrolled_courses',
        lazy='dynamic',
        overlaps="student,course"
    )

    @staticmethod
    def get_end_time(start_time_str):
        """根据上课时间获取下课时间"""
        time_mapping = {
            '08:15': '09:45',
            '10:05': '11:35',
            '13:00': '14:30',
            '15:00': '16:30',
            '18:00': '19:30',
            '20:00': '21:30'
        }
        return time_mapping.get(start_time_str)
