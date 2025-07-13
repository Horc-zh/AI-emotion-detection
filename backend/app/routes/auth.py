# app/routes/auth.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User

# 1. 定义 Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': '邮箱和密码为必填项'}), 400

    # 检查用户是否已存在
    if User.query.filter_by(email=email).first():
        return jsonify({'message': '用户已存在'}), 409

    # 创建并保存用户
    new_user = User(email=email)
    new_user.password_hash = generate_password_hash(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': '注册成功'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': '邮箱和密码为必填项'}), 400

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password_hash, password):
        # 生成访问令牌
        access_token = create_access_token(identity=user.id)
        return jsonify({'token': access_token}), 200

    return jsonify({'message': '邮箱或密码错误'}), 401

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    # 从令牌中获取用户 ID
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': '用户未找到'}), 404

    return jsonify({
        'id': user.id,
        'email': user.email
    }), 200
