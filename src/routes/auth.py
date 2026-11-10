import re
from datetime import timedelta
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
)

from src.extensions import db
from src.models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

EMAIL_REGEX = re.compile(r"^[^@]+@[^@]+\.[^@]+$")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    if not EMAIL_REGEX.match(email):
        return jsonify({"error": "Invalid email address format"}), 400

    if not password:
        return jsonify({"error": "Password is required"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters long"}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "User with this email already exists"}), 409

    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    expires_cfg = current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES", 86400)
    token_expires = expires_cfg if isinstance(expires_cfg, timedelta) else timedelta(seconds=int(expires_cfg))
    token = create_access_token(identity=str(user.id), expires_delta=token_expires)

    return jsonify({
        "success": True,
        "message": "Registration successful",
        "access_token": token,
        "user": user.to_dict(),
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    expires_cfg = current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES", 86400)
    token_expires = expires_cfg if isinstance(expires_cfg, timedelta) else timedelta(seconds=int(expires_cfg))
    token = create_access_token(identity=str(user.id), expires_delta=token_expires)

    return jsonify({
        "success": True,
        "message": "Login successful",
        "access_token": token,
        "user": user.to_dict(),
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    user_id_str = get_jwt_identity()
    user = db.session.get(User, int(user_id_str))
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "success": True,
        "user": user.to_dict(),
    }), 200
