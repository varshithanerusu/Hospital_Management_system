import pandas as pd

from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt

from database import db
from models import Appointment, Patient, Doctor


# Create Blueprint
csv_bp = Blueprint("csv", __name__)


# ---------------------------------------------------------
# CSV UPLOAD PAGE
# ---------------------------------------------------------
@csv_bp.route("/csv-upload-page")
def csv_upload_page():
    return render_template("csv_upload.html")


# ---------------------------------------------------------
# UPLOAD CSV
# ---------------------------------------------------------
@csv_bp.route("/api/upload-csv", methods=["POST"])
@jwt_required()
def upload_csv():

    try:
        # ---------------------------------------------
        # Check user role
        # ---------------------------------------------
        claims = get_jwt()

        if claims.get("role") != "admin":
            return jsonify({
                "status": "error",
                "message": "Only admin can upload CSV files"
            }), 403

        # ---------------------------------------------
        # Check whether file exists
        # ---------------------------------------------
        if "file" not in request.files:
            return jsonify({
                "status": "error",
                "message": "No CSV file uploaded"
            }), 400

        file = request.files["file"]

        # ---------------------------------------------
        # Check filename
        # ---------------------------------------------
        if file.filename == "":
            return jsonify({
                "status": "error",
                "message": "Please select a CSV file"
            }), 400

        # ---------------------------------------------
        # Check file extension
        # ---------------------------------------------
        if not file.filename.lower().endswith(".csv"):
            return jsonify({
                "status": "error",
                "message": "Only CSV files are allowed"
            }), 400

        # ---------------------------------------------
        # Read CSV using Pandas
        # ---------------------------------------------
        df = pd.read_csv(file)

        print("\nCSV DATA:")
        print(df)

        # ---------------------------------------------
        # Required columns
        # ---------------------------------------------
        required_columns = [
            "patient_id",
            "doctor_id",
            "date",
            "diagnosis",
            "status"
        ]

        # ---------------------------------------------
        # Check missing columns
        # ---------------------------------------------
        missing_columns = [
            column
            for column in required_columns
            if column not in df.columns
        ]

        if missing_columns:
            return jsonify({
                "status": "error",
                "message": "Missing columns: "
                           + ", ".join(missing_columns)
            }), 400

        # ---------------------------------------------
        # Allowed statuses
        # ---------------------------------------------
        allowed_statuses = [
            "Recovered",
            "Under Treatment",
            "Critical"
        ]

        inserted = 0
        skipped = 0
        errors = []

        # ---------------------------------------------
        # Process every CSV row
        # ---------------------------------------------
        for index, row in df.iterrows():

            try:

                # Get patient ID
                patient_id = int(row["patient_id"])

                # Get doctor ID
                doctor_id = int(row["doctor_id"])

                # -----------------------------------------
                # Check patient
                # -----------------------------------------
                patient = Patient.query.get(patient_id)

                if not patient:
                    skipped += 1

                    errors.append(
                        f"Row {index + 2}: "
                        f"Patient ID {patient_id} not found"
                    )

                    continue

                # -----------------------------------------
                # Check doctor
                # -----------------------------------------
                doctor = Doctor.query.get(doctor_id)

                if not doctor:
                    skipped += 1

                    errors.append(
                        f"Row {index + 2}: "
                        f"Doctor ID {doctor_id} not found"
                    )

                    continue

                # -----------------------------------------
                # Check status
                # -----------------------------------------
                status = str(row["status"]).strip()

                if status not in allowed_statuses:

                    skipped += 1

                    errors.append(
                        f"Row {index + 2}: "
                        f"Invalid status '{status}'"
                    )

                    continue

                # -----------------------------------------
                # Convert date
                # -----------------------------------------
                appointment_date = pd.to_datetime(
                    row["date"],
                    errors="raise"
                )

                # -----------------------------------------
                # Get diagnosis
                # -----------------------------------------
                diagnosis = str(
                    row["diagnosis"]
                ).strip()

                if not diagnosis:

                    skipped += 1

                    errors.append(
                        f"Row {index + 2}: "
                        "Diagnosis cannot be empty"
                    )

                    continue

                # -----------------------------------------
                # Create appointment
                # -----------------------------------------
                appointment = Appointment(
                    patient_id=patient_id,
                    doctor_id=doctor_id,
                    date=appointment_date,
                    diagnosis=diagnosis,
                    status=status
                )

                db.session.add(appointment)

                inserted += 1

            except Exception as row_error:

                skipped += 1

                errors.append(
                    f"Row {index + 2}: {str(row_error)}"
                )

        # ---------------------------------------------
        # Save to MySQL
        # ---------------------------------------------
        db.session.commit()

        # ---------------------------------------------
        # Success response
        # ---------------------------------------------
        return jsonify({
            "status": "success",
            "message": "CSV uploaded successfully",
            "records_inserted": inserted,
            "records_skipped": skipped,
            "errors": errors
        }), 201

    except Exception as e:

        db.session.rollback()

        print("\nCSV ERROR:")
        print(str(e))

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500