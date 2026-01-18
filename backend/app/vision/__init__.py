from flask import Blueprint

vision_bp = Blueprint('vision', __name__)

from backend.app.vision import routes
