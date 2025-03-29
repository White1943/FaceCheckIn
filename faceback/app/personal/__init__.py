from flask import Blueprint

personal_bp = Blueprint('api/personal', __name__)

from . import views
