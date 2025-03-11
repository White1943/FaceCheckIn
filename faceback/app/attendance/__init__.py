from flask import Blueprint


teacher_attendance_bp = Blueprint('api/teacher/attendance', __name__)

from . import views
