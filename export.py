import io
import pandas as pd

from flask import Blueprint, send_file, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from models import Appointment


# Create Blueprint
export_bp = Blueprint("export", __name__)


# ---------------------------------------------------------
# GET APPOINTMENT DATA
# ---------------------------------------------------------
def get_appointment_data():

    appointments = Appointment.query.all()

    data = []

    for appointment in appointments:

        data.append({
            "Appointment ID": appointment.id,
            "Patient ID": appointment.patient_id,
            "Patient Name": appointment.patient.name,
            "Doctor ID": appointment.doctor_id,
            "Doctor Name": appointment.doctor.name,
            "Date": appointment.date.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "Diagnosis": appointment.diagnosis,
            "Status": appointment.status
        })

    return data


# ---------------------------------------------------------
# EXPORT CSV
# ---------------------------------------------------------
@export_bp.route("/api/export-csv", methods=["GET"])
@jwt_required()
def export_csv():

    try:

        # Check user role
        claims = get_jwt()

        if claims.get("role") != "admin":
            return jsonify({
                "status": "error",
                "message": "Only admin can export data"
            }), 403

        # Get appointment data
        data = get_appointment_data()

        # Convert to Pandas DataFrame
        df = pd.DataFrame(data)

        # Create memory file
        output = io.StringIO()

        # Convert DataFrame to CSV
        df.to_csv(
            output,
            index=False
        )

        # Move to beginning
        output.seek(0)

        # Send CSV file
        return send_file(
            io.BytesIO(
                output.getvalue().encode("utf-8")
            ),
            mimetype="text/csv",
            as_attachment=True,
            download_name="hospital_appointments.csv"
        )

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ---------------------------------------------------------
# EXPORT EXCEL
# ---------------------------------------------------------
@export_bp.route("/api/export-excel", methods=["GET"])
@jwt_required()
def export_excel():

    try:

        # Check user role
        claims = get_jwt()

        if claims.get("role") != "admin":
            return jsonify({
                "status": "error",
                "message": "Only admin can export data"
            }), 403

        # Get appointment data
        data = get_appointment_data()

        # Convert to DataFrame
        df = pd.DataFrame(data)

        # Create memory file
        output = io.BytesIO()

        # Create Excel file
        with pd.ExcelWriter(
            output,
            engine="openpyxl"
        ) as writer:

            df.to_excel(
                writer,
                sheet_name="Appointments",
                index=False
            )

        # Move to beginning
        output.seek(0)

        # Send Excel file
        return send_file(
            output,
            mimetype=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            as_attachment=True,
            download_name="hospital_appointments.xlsx"
        )

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500