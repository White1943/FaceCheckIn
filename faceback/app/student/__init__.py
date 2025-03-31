from flask import Blueprint

student_course_bp = Blueprint('api/stu/course', __name__)
student_attendance_bp = Blueprint('api/stu/attendance', __name__)

from . import views

