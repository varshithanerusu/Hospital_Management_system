from flask import Blueprint, jsonify, request
from models import Doctor
from database import db

doctors_bp = Blueprint("doctors", __name__)


# GET ALL DOCTORS
@doctors_bp.route("/doctors", methods=["GET"])
def get_doctors():
    doctors = Doctor.query.all()

    doctor_list = []

    for doctor in doctors:
        doctor_list.append({
            "id": doctor.id,
            "name": doctor.name,
            "specialization": doctor.specialization
        })

    return jsonify({
        "status": "success",
        "data": doctor_list
    }), 200


# CREATE DOCTOR
@doctors_bp.route("/doctors", methods=["POST"])
def create_doctor():
    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "JSON data is required"
        }), 400

    name = data.get("name")
    specialization = data.get("specialization")

    if not name or not specialization:
        return jsonify({
            "status": "error",
            "message": "Name and specialization are required"
        }), 400

    new_doctor = Doctor(
        name=name,
        specialization=specialization
    )

    db.session.add(new_doctor)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Doctor created successfully",
        "data": {
            "id": new_doctor.id,
            "name": new_doctor.name,
            "specialization": new_doctor.specialization
        }
    }), 201


# GET ONE DOCTOR
@doctors_bp.route("/doctors/<int:doctor_id>", methods=["GET"])
def get_doctor(doctor_id):
    doctor = Doctor.query.get(doctor_id)

    if not doctor:
        return jsonify({
            "status": "error",
            "message": "Doctor not found"
        }), 404

    return jsonify({
        "status": "success",
        "data": {
            "id": doctor.id,
            "name": doctor.name,
            "specialization": doctor.specialization
        }
    }), 200


# FULL UPDATE DOCTOR
@doctors_bp.route("/doctors/<int:doctor_id>", methods=["PUT"])
def update_doctor(doctor_id):
    doctor = Doctor.query.get(doctor_id)

    if not doctor:
        return jsonify({
            "status": "error",
            "message": "Doctor not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "JSON data is required"
        }), 400

    name = data.get("name")
    specialization = data.get("specialization")

    if not name or not specialization:
        return jsonify({
            "status": "error",
            "message": "Name and specialization are required for PUT"
        }), 400

    doctor.name = name
    doctor.specialization = specialization

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Doctor updated successfully",
        "data": {
            "id": doctor.id,
            "name": doctor.name,
            "specialization": doctor.specialization
        }
    }), 200


# PARTIAL UPDATE DOCTOR
@doctors_bp.route("/doctors/<int:doctor_id>", methods=["PATCH"])
def patch_doctor(doctor_id):
    doctor = Doctor.query.get(doctor_id)

    if not doctor:
        return jsonify({
            "status": "error",
            "message": "Doctor not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "JSON data is required"
        }), 400

    if "name" in data:
        doctor.name = data["name"]

    if "specialization" in data:
        doctor.specialization = data["specialization"]

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Doctor partially updated successfully",
        "data": {
            "id": doctor.id,
            "name": doctor.name,
            "specialization": doctor.specialization
        }
    }), 200


# DELETE DOCTOR
@doctors_bp.route("/doctors/<int:doctor_id>", methods=["DELETE"])
def delete_doctor(doctor_id):
    doctor = Doctor.query.get(doctor_id)

    if not doctor:
        return jsonify({
            "status": "error",
            "message": "Doctor not found"
        }), 404

    db.session.delete(doctor)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Doctor deleted successfully"
    }), 200