from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from models import Patient
from database import db


patients_bp = Blueprint("patients", __name__)


@patients_bp.route("/patients", methods=["GET"])
def get_patients():

    patients = Patient.query.all()

    patient_list = []

    for patient in patients:
        patient_list.append({
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "contact": patient.contact
        })

    return jsonify({
        "status": "success",
        "data": patient_list
    }), 200


@patients_bp.route("/patients", methods=["POST"])
def create_patient():

    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "JSON data is required"
        }), 400

    name = data.get("name")
    age = data.get("age")
    gender = data.get("gender")
    contact = data.get("contact")

    if not name or not age or not gender or not contact:
        return jsonify({
            "status": "error",
            "message": "All fields are required"
        }), 400

    existing_patient = Patient.query.filter_by(
        contact=contact
    ).first()

    if existing_patient:
        return jsonify({
            "status": "error",
            "message": "Contact number already exists"
        }), 409

    new_patient = Patient(
        name=name,
        age=age,
        gender=gender,
        contact=contact
    )

    db.session.add(new_patient)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Patient created successfully",
        "data": {
            "id": new_patient.id,
            "name": new_patient.name,
            "age": new_patient.age,
            "gender": new_patient.gender,
            "contact": new_patient.contact
        }
    }), 201
@patients_bp.route("/patients/<int:patient_id>", methods=["GET"])
def get_patient(patient_id):

    patient = Patient.query.get(patient_id)

    if not patient:
        return jsonify({
            "status": "error",
            "message": "Patient not found"
        }), 404

    return jsonify({
        "status": "success",
        "data": {
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "contact": patient.contact
        }
    }), 200
@patients_bp.route("/patients/<int:patient_id>", methods=["PUT"])
def update_patient(patient_id):

    patient = Patient.query.get(patient_id)

    if not patient:
        return jsonify({
            "status": "error",
            "message": "Patient not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "JSON data is required"
        }), 400

    name = data.get("name")
    age = data.get("age")
    gender = data.get("gender")
    contact = data.get("contact")

    if not name or not age or not gender or not contact:
        return jsonify({
            "status": "error",
            "message": "All fields are required for PUT"
        }), 400

    existing_patient = Patient.query.filter(
        Patient.contact == contact,
        Patient.id != patient_id
    ).first()

    if existing_patient:
        return jsonify({
            "status": "error",
            "message": "Contact number already belongs to another patient"
        }), 409

    patient.name = name
    patient.age = age
    patient.gender = gender
    patient.contact = contact

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Patient updated successfully",
        "data": {
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "contact": patient.contact
        }
    }), 200
@patients_bp.route("/patients/<int:patient_id>", methods=["PATCH"])
def patch_patient(patient_id):

    patient = Patient.query.get(patient_id)

    if not patient:
        return jsonify({
            "status": "error",
            "message": "Patient not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "JSON data is required"
        }), 400

    if "name" in data:
        patient.name = data["name"]

    if "age" in data:
        patient.age = data["age"]

    if "gender" in data:
        patient.gender = data["gender"]

    if "contact" in data:

        existing_patient = Patient.query.filter(
            Patient.contact == data["contact"],
            Patient.id != patient_id
        ).first()

        if existing_patient:
            return jsonify({
                "status": "error",
                "message": "Contact number already belongs to another patient"
            }), 409

        patient.contact = data["contact"]

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Patient partially updated successfully",
        "data": {
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "contact": patient.contact
        }
    }), 200
@patients_bp.route("/patients/<int:patient_id>", methods=["DELETE"])
def delete_patient(patient_id):
    patient = Patient.query.get(patient_id)

    if not patient:
        return jsonify({
            "status": "error",
            "message": "Patient not found"
        }), 404

    db.session.delete(patient)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Patient deleted successfully"
    }), 200