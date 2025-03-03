from flask import Blueprint


auth_bp = Blueprint('api/auth', __name__)

from . import views