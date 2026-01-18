from flask import Blueprint, jsonify, request

api_bp = Blueprint('api', __name__)

@api_bp.route('/', methods=['GET'])
def health_check():
    return jsonify({"health": "ok"}), 200

