from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash

from database import db
from models import User,Doctor


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/auth/register", methods=["POST"])
def register():

    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "JSON data is required"
        }), 400

    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "doctor")
    doctor_id = data.get("doctor_id")

    if not username or not password:
        return jsonify({
            "status": "error",
            "message": "Username and password are required"
        }), 400

    if role not in ["admin", "doctor"]:
        return jsonify({
            "status": "error",
            "message": "Role must be admin or doctor"
        }), 400

    existing_user = User.query.filter_by(
        username=username
    ).first()

    if existing_user:
        return jsonify({
            "status": "error",
            "message": "Username already exists"
        }), 409

    if role == "doctor":

        if not doctor_id:
            return jsonify({
                "status": "error",
                "message": "doctor_id is required for doctor account"
            }), 400

        doctor = Doctor.query.get(doctor_id)

        if not doctor:
            return jsonify({
                "status": "error",
                "message": "Doctor not found"
            }), 404

    else:
        doctor_id = None

    hashed_password = generate_password_hash(password)

    new_user = User(
        username=username,
        password_hash=hashed_password,
        role=role,
        doctor_id=doctor_id
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "User registered successfully"
    }), 201


@auth_bp.route("/auth/login", methods=["POST"])
def login():

    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(
        username=username
    ).first()

    if not user:
        return jsonify({
            "status": "error",
            "message": "Invalid username or password"
        }), 401

    if not check_password_hash(
        user.password_hash,
        password
    ):
        return jsonify({
            "status": "error",
            "message": "Invalid username or password"
        }), 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role
        }
    )

    return jsonify({
        "status": "success",
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
    }), 200


@auth_bp.route("/auth/profile", methods=["GET"])
@jwt_required()
def profile():

    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "status": "error",
            "message": "User not found"
        }), 404

    return jsonify({
        "status": "success",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
    })