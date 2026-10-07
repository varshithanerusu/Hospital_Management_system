from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from datetime import datetime

from database import db
from models import Patient, Doctor, Appointment, User


api_v1_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")


# =========================================================
# HELPER - GET CURRENT USER
# =========================================================

def get_current_user():

    user_id = get_jwt_identity()

    return User.query.get(int(user_id))


# =========================================================
# PATIENTS - GET ALL
# =========================================================

@api_v1_bp.route("/patients", methods=["GET"])
@jwt_required()
def get_patients_v1():

    patients = Patient.query.all()

    data = []

    for patient in patients:

        data.append({
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "contact": patient.contact
        })

    return jsonify({
        "status": "success",
        "version": "v1",
        "data": data
    }), 200


# =========================================================
# PATIENTS - GET ONE
# =========================================================

@api_v1_bp.route("/patients/<int:patient_id>", methods=["GET"])
@jwt_required()
def get_patient_v1(patient_id):

    patient = Patient.query.get(patient_id)

    if not patient:

        return jsonify({
            "status": "error",
            "message": "Patient not found"
        }), 404

    return jsonify({
        "status": "success",
        "version": "v1",
        "data": {
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "contact": patient.contact
        }
    }), 200


# =========================================================
# PATIENTS - CREATE
# =========================================================

@api_v1_bp.route("/patients", methods=["POST"])
@jwt_required()
def create_patient_v1():

    claims = get_jwt()

    if claims.get("role") != "admin":

        return jsonify({
            "status": "error",
            "message": "Admin access required"
        }), 403

    data = request.get_json()

    if not data:

        return jsonify({
            "status": "error",
            "message": "JSON data is required"
        }), 400

    required_fields = [
        "name",
        "age",
        "gender",
        "contact"
    ]

    for field in required_fields:

        if field not in data:

            return jsonify({
                "status": "error",
                "message": f"Missing field: {field}"
            }), 400

    existing_patient = Patient.query.filter_by(
        contact=data["contact"]
    ).first()

    if existing_patient:

        return jsonify({
            "status": "error",
            "message": "Contact already exists"
        }), 400

    patient = Patient(
        name=data["name"],
        age=data["age"],
        gender=data["gender"],
        contact=data["contact"]
    )

    db.session.add(patient)
    db.session.commit()

    return jsonify({
        "status": "success",
        "version": "v1",
        "message": "Patient created successfully",
        "data": {
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender,
            "contact": patient.contact
        }
    }), 201


# =========================================================
# PATIENTS - UPDATE
# =========================================================

@api_v1_bp.route("/patients/<int:patient_id>", methods=["PUT"])
@jwt_required()
def update_patient_v1(patient_id):

    claims = get_jwt()

    if claims.get("role") != "admin":

        return jsonify({
            "status": "error",
            "message": "Admin access required"
        }), 403

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

    patient.name = data.get(
        "name",
        patient.name
    )

    patient.age = data.get(
        "age",
        patient.age
    )

    patient.gender = data.get(
        "gender",
        patient.gender
    )

    patient.contact = data.get(
        "contact",
        patient.contact
    )

    db.session.commit()

    return jsonify({
        "status": "success",
        "version": "v1",
        "message": "Patient updated successfully"
    }), 200


# =========================================================
# PATIENTS - DELETE
# =========================================================

@api_v1_bp.route("/patients/<int:patient_id>", methods=["DELETE"])
@jwt_required()
def delete_patient_v1(patient_id):

    claims = get_jwt()

    if claims.get("role") != "admin":

        return jsonify({
            "status": "error",
            "message": "Admin access required"
        }), 403

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
        "version": "v1",
        "message": "Patient deleted successfully"
    }), 200


# =========================================================
# DOCTORS - GET ALL
# =========================================================

@api_v1_bp.route("/doctors", methods=["GET"])
@jwt_required()
def get_doctors_v1():

    doctors = Doctor.query.all()

    data = []

    for doctor in doctors:

        data.append({
            "id": doctor.id,
            "name": doctor.name,
            "specialization": doctor.specialization
        })

    return jsonify({
        "status": "success",
        "version": "v1",
        "data": data
    }), 200


# =========================================================
# DOCTORS - GET ONE
# =========================================================

@api_v1_bp.route("/doctors/<int:doctor_id>", methods=["GET"])
@jwt_required()
def get_doctor_v1(doctor_id):

    doctor = Doctor.query.get(doctor_id)

    if not doctor:

        return jsonify({
            "status": "error",
            "message": "Doctor not found"
        }), 404

    return jsonify({
        "status": "success",
        "version": "v1",
        "data": {
            "id": doctor.id,
            "name": doctor.name,
            "specialization": doctor.specialization
        }
    }), 200


# =========================================================
# DOCTORS - CREATE
# =========================================================

@api_v1_bp.route("/doctors", methods=["POST"])
@jwt_required()
def create_doctor_v1():

    claims = get_jwt()

    if claims.get("role") != "admin":

        return jsonify({
            "status": "error",
            "message": "Admin access required"
        }), 403

    data = request.get_json()

    if not data:

        return jsonify({
            "status": "error",
            "message": "JSON data is required"
        }), 400

    if "name" not in data or "specialization" not in data:

        return jsonify({
            "status": "error",
            "message": "Name and specialization are required"
        }), 400

    doctor = Doctor(
        name=data["name"],
        specialization=data["specialization"]
    )

    db.session.add(doctor)
    db.session.commit()

    return jsonify({
        "status": "success",
        "version": "v1",
        "message": "Doctor created successfully",
        "data": {
            "id": doctor.id,
            "name": doctor.name,
            "specialization": doctor.specialization
        }
    }), 201


# =========================================================
# DOCTORS - UPDATE
# =========================================================

@api_v1_bp.route("/doctors/<int:doctor_id>", methods=["PUT"])
@jwt_required()
def update_doctor_v1(doctor_id):

    claims = get_jwt()

    if claims.get("role") != "admin":

        return jsonify({
            "status": "error",
            "message": "Admin access required"
        }), 403

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

    doctor.name = data.get(
        "name",
        doctor.name
    )

    doctor.specialization = data.get(
        "specialization",
        doctor.specialization
    )

    db.session.commit()

    return jsonify({
        "status": "success",
        "version": "v1",
        "message": "Doctor updated successfully"
    }), 200


# =========================================================
# DOCTORS - DELETE
# =========================================================

@api_v1_bp.route("/doctors/<int:doctor_id>", methods=["DELETE"])
@jwt_required()
def delete_doctor_v1(doctor_id):

    claims = get_jwt()

    if claims.get("role") != "admin":

        return jsonify({
            "status": "error",
            "message": "Admin access required"
        }), 403

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
        "version": "v1",
        "message": "Doctor deleted successfully"
    }), 200


# =========================================================
# APPOINTMENTS - GET ALL
# =========================================================

@api_v1_bp.route("/appointments", methods=["GET"])
@jwt_required()
def get_appointments_v1():

    user = get_current_user()

    if not user:

        return jsonify({
            "status": "error",
            "message": "User not found"
        }), 401

    if user.role == "admin":

        appointments = Appointment.query.all()

    else:

        appointments = Appointment.query.filter_by(
            doctor_id=user.doctor_id
        ).all()

    data = []

    for appointment in appointments:

        data.append({
            "id": appointment.id,
            "patient_id": appointment.patient_id,
            "patient_name": appointment.patient.name,
            "doctor_id": appointment.doctor_id,
            "doctor_name": appointment.doctor.name,
            "date": appointment.date.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "diagnosis": appointment.diagnosis,
            "status": appointment.status
        })

    return jsonify({
        "status": "success",
        "version": "v1",
        "data": data
    }), 200


# =========================================================
# APPOINTMENTS - GET ONE
# =========================================================

@api_v1_bp.route(
    "/appointments/<int:appointment_id>",
    methods=["GET"]
)
@jwt_required()
def get_appointment_v1(appointment_id):

    user = get_current_user()

    if not user:

        return jsonify({
            "status": "error",
            "message": "User not found"
        }), 401

    appointment = Appointment.query.get(
        appointment_id
    )

    if not appointment:

        return jsonify({
            "status": "error",
            "message": "Appointment not found"
        }), 404

    if (
        user.role == "doctor"
        and appointment.doctor_id != user.doctor_id
    ):

        return jsonify({
            "status": "error",
            "message": "You can only view your own appointments"
        }), 403

    return jsonify({
        "status": "success",
        "version": "v1",
        "data": {
            "id": appointment.id,
            "patient_id": appointment.patient_id,
            "patient_name": appointment.patient.name,
            "doctor_id": appointment.doctor_id,
            "doctor_name": appointment.doctor.name,
            "date": appointment.date.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "diagnosis": appointment.diagnosis,
            "status": appointment.status
        }
    }), 200


# =========================================================
# APPOINTMENTS - CREATE
# =========================================================

@api_v1_bp.route("/appointments", methods=["POST"])
@jwt_required()
def create_appointment_v1():

    user = get_current_user()

    if not user:

        return jsonify({
            "status": "error",
            "message": "User not found"
        }), 401

    if user.role != "admin":

        return jsonify({
            "status": "error",
            "message": "Only admin can create appointments"
        }), 403

    data = request.get_json()

    if not data:

        return jsonify({
            "status": "error",
            "message": "JSON data is required"
        }), 400

    required_fields = [
        "patient_id",
        "doctor_id",
        "date",
        "diagnosis",
        "status"
    ]

    for field in required_fields:

        if field not in data:

            return jsonify({
                "status": "error",
                "message": f"Missing field: {field}"
            }), 400

    patient = Patient.query.get(
        data["patient_id"]
    )

    if not patient:

        return jsonify({
            "status": "error",
            "message": "Patient not found"
        }), 404

    doctor = Doctor.query.get(
        data["doctor_id"]
    )

    if not doctor:

        return jsonify({
            "status": "error",
            "message": "Doctor not found"
        }), 404

    allowed_statuses = [
        "Recovered",
        "Under Treatment",
        "Critical"
    ]

    if data["status"] not in allowed_statuses:

        return jsonify({
            "status": "error",
            "message": "Invalid status"
        }), 400

    try:

        appointment_date = datetime.strptime(
            data["date"],
            "%Y-%m-%d %H:%M:%S"
        )

    except ValueError:

        return jsonify({
            "status": "error",
            "message":
                "Date must be YYYY-MM-DD HH:MM:SS"
        }), 400

    appointment = Appointment(
        patient_id=data["patient_id"],
        doctor_id=data["doctor_id"],
        date=appointment_date,
        diagnosis=data["diagnosis"],
        status=data["status"]
    )

    db.session.add(appointment)
    db.session.commit()

    return jsonify({
        "status": "success",
        "version": "v1",
        "message": "Appointment created successfully",
        "data": {
            "id": appointment.id
        }
    }), 201


# =========================================================
# APPOINTMENTS - UPDATE
# =========================================================

@api_v1_bp.route(
    "/appointments/<int:appointment_id>",
    methods=["PUT", "PATCH"]
)
@jwt_required()
def update_appointment_v1(appointment_id):

    user = get_current_user()

    if not user:

        return jsonify({
            "status": "error",
            "message": "User not found"
        }), 401

    appointment = Appointment.query.get(
        appointment_id
    )

    if not appointment:

        return jsonify({
            "status": "error",
            "message": "Appointment not found"
        }), 404

    # Doctor can only edit own appointment
    if (
        user.role == "doctor"
        and appointment.doctor_id != user.doctor_id
    ):

        return jsonify({
            "status": "error",
            "message":
                "You can only edit your own appointments"
        }), 403

    data = request.get_json()

    if not data:

        return jsonify({
            "status": "error",
            "message": "JSON data is required"
        }), 400

    # -----------------------------------------
    # Patient
    # -----------------------------------------

    if "patient_id" in data:

        patient = Patient.query.get(
            data["patient_id"]
        )

        if not patient:

            return jsonify({
                "status": "error",
                "message": "Patient not found"
            }), 404

        appointment.patient_id = data["patient_id"]


    # -----------------------------------------
    # Doctor
    # -----------------------------------------

    if "doctor_id" in data:

        # Doctor cannot assign appointment
        # to another doctor
        if (
            user.role == "doctor"
            and data["doctor_id"] != user.doctor_id
        ):

            return jsonify({
                "status": "error",
                "message":
                    "Doctor cannot assign another doctor"
            }), 403

        doctor = Doctor.query.get(
            data["doctor_id"]
        )

        if not doctor:

            return jsonify({
                "status": "error",
                "message": "Doctor not found"
            }), 404

        appointment.doctor_id = data["doctor_id"]


    # -----------------------------------------
    # Date
    # -----------------------------------------

    if "date" in data:

        try:

            appointment.date = datetime.strptime(
                data["date"],
                "%Y-%m-%d %H:%M:%S"
            )

        except ValueError:

            return jsonify({
                "status": "error",
                "message":
                    "Date must be YYYY-MM-DD HH:MM:SS"
            }), 400


    # -----------------------------------------
    # Diagnosis
    # -----------------------------------------

    if "diagnosis" in data:

        appointment.diagnosis = data[
            "diagnosis"
        ]


    # -----------------------------------------
    # Status
    # -----------------------------------------

    if "status" in data:

        allowed_statuses = [
            "Recovered",
            "Under Treatment",
            "Critical"
        ]

        if data["status"] not in allowed_statuses:

            return jsonify({
                "status": "error",
                "message": "Invalid status"
            }), 400

        appointment.status = data["status"]


    db.session.commit()

    return jsonify({
        "status": "success",
        "version": "v1",
        "message":
            "Appointment updated successfully"
    }), 200


# =========================================================
# APPOINTMENTS - DELETE
# =========================================================

@api_v1_bp.route(
    "/appointments/<int:appointment_id>",
    methods=["DELETE"]
)
@jwt_required()
def delete_appointment_v1(appointment_id):

    claims = get_jwt()

    if claims.get("role") != "admin":

        return jsonify({
            "status": "error",
            "message": "Only admin can delete appointments"
        }), 403

    appointment = Appointment.query.get(
        appointment_id
    )

    if not appointment:

        return jsonify({
            "status": "error",
            "message": "Appointment not found"
        }), 404

    db.session.delete(appointment)
    db.session.commit()

    return jsonify({
        "status": "success",
        "version": "v1",
        "message":
            "Appointment deleted successfully"
    }), 200