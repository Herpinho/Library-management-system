from flask import Blueprint, request, jsonify
from model import User

user_blueprint = Blueprint('user', __name__)

utilizadores = {}

@user_blueprint.route('/<int:id>', methods=['GET'])
def get_user(id):
    user = utilizadores.get(id)
    if user:
        return jsonify(user.to_json())
    return jsonify({"error": "User not found"}), 404

@user_blueprint.route('/', methods=['POST'])
def create_user():
    user_data = request.json
    user = User(id=user_data['id'], name=user_data['name'], email=user_data['email'])
    utilizadores[user.id] = user
    return jsonify(user.to_json()), 201