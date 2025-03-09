from flask import Blueprint


course_bp = Blueprint('api/course', __name__)

from . import views
