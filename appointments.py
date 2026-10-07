from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import Appointment, Patient, Doctor, User
from database import db


appointments_bp = Blueprint("appointments", __name__)


# ---------------------------------------------------------
# HELPER FUNCTION
# ---------------------------------------------------------

def get_current_user():
    user_id = get_jwt_identity()

    if not user_id:
        return None

    return User.query.get(int(user_id))


# ---------------------------------------------------------
# GET ALL APPOINTMENTS
# ---------------------------------------------------------

@appointments_bp.route("/appointments", methods=["GET"])
@jwt_required()
def get_appointments():

    current_user = get_current_user()

    if not current_user:
        return jsonify({
            "status": "error",
            "message": "User not found"
        }), 404

    # Admin can see all appointments
    if current_user.role == "admin":

        appointments = Appointment.query.all()

    # Doctor can see only their appointments
    elif current_user.role == "doctor":

        if not current_user.doctor_id:
            return jsonify({
                "status": "error",
                "message": "Doctor account is not linked to a doctor"
            }), 400

        appointments = Appointment.query.filter_by(
            doctor_id=current_user.doctor_id
        ).all()

    else:

        return jsonify({
            "status": "error",
            "message": "Access denied"
        }), 403

    appointment_list = []

    for appointment in appointments:

        appointment_list.append({
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
        "data": appointment_list
    }), 200


# ---------------------------------------------------------
# CREATE APPOINTMENT
# ---------------------------------------------------------

@appointments_bp.route("/appointments", methods=["POST"])
@jwt_required()
def create_appointment():

    current_user = get_current_user()

    if not current_user:
        return jsonify({
            "status": "error",
            "message": "User not found"
        }), 404

    # Only admin can create appointments
    if current_user.role != "admin":
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

    patient_id = data.get("patient_id")
    doctor_id = data.get("doctor_id")
    diagnosis = data.get("diagnosis")
    status = data.get("status", "Under Treatment")
    date = data.get("date")

    # Validate required fields
    if not patient_id or not doctor_id or not diagnosis:
        return jsonify({
            "status": "error",
            "message": "Patient, doctor and diagnosis are required"
        }), 400

    # Check patient
    patient = Patient.query.get(patient_id)

    if not patient:
        return jsonify({
            "status": "error",
            "message": "Patient not found"
        }), 404

    # Check doctor
    doctor = Doctor.query.get(doctor_id)

    if not doctor:
        return jsonify({
            "status": "error",
            "message": "Doctor not found"
        }), 404

    # Validate status
    allowed_statuses = [
        "Recovered",
        "Under Treatment",
        "Critical"
    ]

    if status not in allowed_statuses:
        return jsonify({
            "status": "error",
            "message": "Invalid status. Use Recovered, Under Treatment or Critical"
        }), 400

    # Create appointment
    new_appointment = Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        diagnosis=diagnosis,
        status=status
    )

    # Handle date
    if date:

        from datetime import datetime

        try:

            new_appointment.date = datetime.strptime(
                date,
                "%Y-%m-%d %H:%M:%S"
            )

        except ValueError:

            return jsonify({
                "status": "error",
                "message": "Date must be YYYY-MM-DD HH:MM:SS"
            }), 400

    db.session.add(new_appointment)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Appointment created successfully",
        "data": {
            "id": new_appointment.id,
            "patient_id": new_appointment.patient_id,
            "doctor_id": new_appointment.doctor_id,
            "date": new_appointment.date.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "diagnosis": new_appointment.diagnosis,
            "status": new_appointment.status
        }
    }), 201


# ---------------------------------------------------------
# GET ONE APPOINTMENT
# ---------------------------------------------------------

@appointments_bp.route(
    "/appointments/<int:appointment_id>",
    methods=["GET"]
)
@jwt_required()
def get_appointment(appointment_id):

    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({
            "status": "error",
            "message": "Appointment not found"
        }), 404

    current_user = get_current_user()

    if not current_user:
        return jsonify({
            "status": "error",
            "message": "User not found"
        }), 404

    # Admin can access any appointment
    if current_user.role == "admin":
        pass

    # Doctor can access only their own appointment
    elif current_user.role == "doctor":

        if appointment.doctor_id != current_user.doctor_id:

            return jsonify({
                "status": "error",
                "message": "You can only access your own appointments"
            }), 403

    else:

        return jsonify({
            "status": "error",
            "message": "Access denied"
        }), 403

    return jsonify({
        "status": "success",
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


# ---------------------------------------------------------
# FULL UPDATE APPOINTMENT
# ---------------------------------------------------------

@appointments_bp.route(
    "/appointments/<int:appointment_id>",
    methods=["PUT"]
)
@jwt_required()
def update_appointment(appointment_id):

    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({
            "status": "error",
            "message": "Appointment not found"
        }), 404

    current_user = get_current_user()

    if not current_user:
        return jsonify({
            "status": "error",
            "message": "User not found"
        }), 404

    # Doctor can update only their own appointment
    if current_user.role == "doctor":

        if appointment.doctor_id != current_user.doctor_id:

            return jsonify({
                "status": "error",
                "message": "You can only edit your own appointments"
            }), 403

    elif current_user.role != "admin":

        return jsonify({
            "status": "error",
            "message": "Access denied"
        }), 403

    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "JSON data is required"
        }), 400

    patient_id = data.get("patient_id")
    doctor_id = data.get("doctor_id")
    diagnosis = data.get("diagnosis")
    status = data.get("status")
    date = data.get("date")

    # PUT requires all fields
    if not patient_id or not doctor_id or not diagnosis or not status:

        return jsonify({
            "status": "error",
            "message": "All fields are required for PUT"
        }), 400

    # Check patient
    patient = Patient.query.get(patient_id)

    if not patient:

        return jsonify({
            "status": "error",
            "message": "Patient not found"
        }), 404

    # Check doctor
    doctor = Doctor.query.get(doctor_id)

    if not doctor:

        return jsonify({
            "status": "error",
            "message": "Doctor not found"
        }), 404

    # Validate status
    allowed_statuses = [
        "Recovered",
        "Under Treatment",
        "Critical"
    ]

    if status not in allowed_statuses:

        return jsonify({
            "status": "error",
            "message": "Invalid status. Use Recovered, Under Treatment or Critical"
        }), 400

    # Doctor should not be able to move appointment
    # to another doctor's ID
    if current_user.role == "doctor":

        if doctor_id != current_user.doctor_id:

            return jsonify({
                "status": "error",
                "message": "Doctor cannot assign appointment to another doctor"
            }), 403

    appointment.patient_id = patient_id
    appointment.doctor_id = doctor_id
    appointment.diagnosis = diagnosis
    appointment.status = status

    # Handle date
    if date:

        from datetime import datetime

        try:

            appointment.date = datetime.strptime(
                date,
                "%Y-%m-%d %H:%M:%S"
            )

        except ValueError:

            return jsonify({
                "status": "error",
                "message": "Date must be YYYY-MM-DD HH:MM:SS"
            }), 400

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Appointment updated successfully",
        "data": {
            "id": appointment.id,
            "patient_id": appointment.patient_id,
            "doctor_id": appointment.doctor_id,
            "date": appointment.date.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "diagnosis": appointment.diagnosis,
            "status": appointment.status
        }
    }), 200


# ---------------------------------------------------------
# PARTIAL UPDATE APPOINTMENT
# ---------------------------------------------------------

@appointments_bp.route(
    "/appointments/<int:appointment_id>",
    methods=["PATCH"]
)
@jwt_required()
def patch_appointment(appointment_id):

    appointment = Appointment.query.get(appointment_id)

    if not appointment:

        return jsonify({
            "status": "error",
            "message": "Appointment not found"
        }), 404

    current_user = get_current_user()

    if not current_user:

        return jsonify({
            "status": "error",
            "message": "User not found"
        }), 404

    # Doctor can update only their own appointment
    if current_user.role == "doctor":

        if appointment.doctor_id != current_user.doctor_id:

            return jsonify({
                "status": "error",
                "message": "You can only edit your own appointments"
            }), 403

    elif current_user.role != "admin":

        return jsonify({
            "status": "error",
            "message": "Access denied"
        }), 403

    data = request.get_json()

    if not data:

        return jsonify({
            "status": "error",
            "message": "JSON data is required"
        }), 400

    # Update patient
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

    # Update doctor
    if "doctor_id" in data:

        doctor = Doctor.query.get(
            data["doctor_id"]
        )

        if not doctor:

            return jsonify({
                "status": "error",
                "message": "Doctor not found"
            }), 404

        # Doctor cannot assign to another doctor
        if current_user.role == "doctor":

            if data["doctor_id"] != current_user.doctor_id:

                return jsonify({
                    "status": "error",
                    "message": "Doctor cannot assign appointment to another doctor"
                }), 403

        appointment.doctor_id = data["doctor_id"]

    # Update diagnosis
    if "diagnosis" in data:

        if not data["diagnosis"]:

            return jsonify({
                "status": "error",
                "message": "Diagnosis cannot be empty"
            }), 400

        appointment.diagnosis = data["diagnosis"]

    # Update status
    if "status" in data:

        allowed_statuses = [
            "Recovered",
            "Under Treatment",
            "Critical"
        ]

        if data["status"] not in allowed_statuses:

            return jsonify({
                "status": "error",
                "message": "Invalid status. Use Recovered, Under Treatment or Critical"
            }), 400

        appointment.status = data["status"]

    # Update date
    if "date" in data:

        from datetime import datetime

        try:

            appointment.date = datetime.strptime(
                data["date"],
                "%Y-%m-%d %H:%M:%S"
            )

        except ValueError:

            return jsonify({
                "status": "error",
                "message": "Date must be YYYY-MM-DD HH:MM:SS"
            }), 400

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Appointment partially updated successfully",
        "data": {
            "id": appointment.id,
            "patient_id": appointment.patient_id,
            "doctor_id": appointment.doctor_id,
            "date": appointment.date.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "diagnosis": appointment.diagnosis,
            "status": appointment.status
        }
    }), 200


# ---------------------------------------------------------
# DELETE APPOINTMENT
# ---------------------------------------------------------

@appointments_bp.route(
    "/appointments/<int:appointment_id>",
    methods=["DELETE"]
)
@jwt_required()
def delete_appointment(appointment_id):

    current_user = get_current_user()

    if not current_user:

        return jsonify({
            "status": "error",
            "message": "User not found"
        }), 404

    # Only admin can delete appointments
    if current_user.role != "admin":

        return jsonify({
            "status": "error",
            "message": "Only admin can delete appointments"
        }), 403

    appointment = Appointment.query.get(appointment_id)

    if not appointment:

        return jsonify({
            "status": "error",
            "message": "Appointment not found"
        }), 404

    db.session.delete(appointment)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Appointment deleted successfully"
    }), 200