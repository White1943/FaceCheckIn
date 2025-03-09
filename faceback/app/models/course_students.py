from app import db
from datetime import datetime

class CourseStudents(db.Model):
    __tablename__ = 'course_students'

    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    join_date = db.Column(db.DateTime, default=datetime.now)

    # 简单的关系定义，不需要 backref
    course = db.relationship('Course')
    student = db.relationship('User')