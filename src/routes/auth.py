import re
from datetime import timedelta
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_jwt_identity,
    jwt_required,
)

from src.extensions import db
from src.models.user import User

auth_bp = Blueprint("auth", __name__)

EMAIL_REGEX = re.compile(r"^[^@]+@[^@]+\.[^@]+$")


def _get_token_deltas():
    expires_cfg = current_app.config.get("JWT_ACCESS_TOKEN_EXPIRES", 86400)
    access_delta = expires_cfg if isinstance(expires_cfg, timedelta) else timedelta(seconds=int(expires_cfg))
    refresh_cfg = current_app.config.get("JWT_REFRESH_TOKEN_EXPIRES", 30 * 86400)
    refresh_delta = refresh_cfg if isinstance(refresh_cfg, timedelta) else timedelta(seconds=int(refresh_cfg))
    return access_delta, refresh_delta


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

    access_delta, refresh_delta = _get_token_deltas()
    access_token = create_access_token(identity=str(user.id), expires_delta=access_delta)
    refresh_token = create_refresh_token(identity=str(user.id), expires_delta=refresh_delta)

    return jsonify({
        "success": True,
        "message": "Registration successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
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

    access_delta, refresh_delta = _get_token_deltas()
    access_token = create_access_token(identity=str(user.id), expires_delta=access_delta)
    refresh_token = create_refresh_token(identity=str(user.id), expires_delta=refresh_delta)

    return jsonify({
        "success": True,
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user.to_dict(),
    }), 200


@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    auth_header = request.headers.get("Authorization", "")
    token = None
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
    if not token:
        data = request.get_json(silent=True) or {}
        token = data.get("refresh_token")

    if not token:
        return jsonify({"error": "Refresh token is required"}), 401

    try:
        decoded = decode_token(token)
        if decoded.get("type") != "refresh":
            return jsonify({"error": "Invalid token type; expected a refresh token"}), 401
        user_id = decoded.get("sub")
    except Exception as e:
        return jsonify({"error": f"Invalid or expired refresh token: {str(e)}"}), 401

    user = db.session.get(User, str(user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404

    access_delta, refresh_delta = _get_token_deltas()
    new_access_token = create_access_token(identity=str(user.id), expires_delta=access_delta)
    new_refresh_token = create_refresh_token(identity=str(user.id), expires_delta=refresh_delta)

    return jsonify({
        "success": True,
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "user": user.to_dict(),
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    user_id_str = get_jwt_identity()
    user = db.session.get(User, str(user_id_str))
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "success": True,
        "user": user.to_dict(),
    }), 200
