from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
import pandas as pd
import numpy as np

from models import Patient, Doctor, Appointment


analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/analytics", methods=["GET"])
@jwt_required()
def analytics():

    try:

        # -----------------------------------------
        # Get data from database
        # -----------------------------------------

        patients = Patient.query.all()
        doctors = Doctor.query.all()
        appointments = Appointment.query.all()


        # -----------------------------------------
        # Basic totals
        # -----------------------------------------

        total_patients = len(patients)

        total_doctors = len(doctors)

        total_appointments = len(appointments)


        # -----------------------------------------
        # Create appointment data
        # -----------------------------------------

        appointment_data = []

        for appointment in appointments:

            appointment_data.append({
                "id": appointment.id,
                "patient_id": appointment.patient_id,
                "doctor_id": appointment.doctor_id,
                "doctor_name": appointment.doctor.name,
                "date": appointment.date,
                "diagnosis": appointment.diagnosis,
                "status": appointment.status
            })


        # -----------------------------------------
        # Create Pandas DataFrame
        # -----------------------------------------

        if appointment_data:

            df = pd.DataFrame(
                appointment_data
            )

        else:

            df = pd.DataFrame(
                columns=[
                    "id",
                    "patient_id",
                    "doctor_id",
                    "doctor_name",
                    "date",
                    "diagnosis",
                    "status"
                ]
            )


        # -----------------------------------------
        # Convert date
        # -----------------------------------------

        if not df.empty:

            df["date"] = pd.to_datetime(
                df["date"]
            )


        # =========================================
        # STATUS DISTRIBUTION
        # =========================================

        if not df.empty:

            status_distribution = (
                df["status"]
                .value_counts()
                .to_dict()
            )

        else:

            status_distribution = {}


        # =========================================
        # COMMON DIAGNOSES
        # =========================================

        if not df.empty:

            common_diagnoses = (
                df["diagnosis"]
                .value_counts()
                .to_dict()
            )

        else:

            common_diagnoses = {}


        # =========================================
        # DOCTOR PERFORMANCE
        # =========================================

        if not df.empty:

            doctor_performance = (
                df["doctor_name"]
                .value_counts()
                .to_dict()
            )

        else:

            doctor_performance = {}


        # =========================================
        # AVERAGE APPOINTMENTS PER DOCTOR
        # =========================================

        appointment_counts = np.array(
            list(doctor_performance.values())
        )


        if len(appointment_counts) > 0:

            average_appointments = float(
                np.mean(appointment_counts)
            )

        else:

            average_appointments = 0


        # =========================================
        # AVERAGE RECOVERY TIME
        # =========================================
        #
        # We calculate:
        #
        # First appointment date
        #          ↓
        # Recovered appointment date
        #          ↓
        # Difference in days
        #
        # This is calculated for patients
        # who have a "Recovered" appointment.
        # =========================================

        recovery_times = []

        if not df.empty:

            for patient_id in df["patient_id"].unique():

                patient_records = df[
                    df["patient_id"] == patient_id
                ].sort_values("date")


                recovered_records = patient_records[
                    patient_records["status"] == "Recovered"
                ]


                if not recovered_records.empty:

                    first_date = (
                        patient_records.iloc[0]["date"]
                    )

                    recovered_date = (
                        recovered_records.iloc[0]["date"]
                    )


                    recovery_days = (
                        recovered_date - first_date
                    ).total_seconds() / 86400


                    # Make sure the value isn't negative
                    if recovery_days >= 0:

                        recovery_times.append(
                            recovery_days
                        )


        if recovery_times:

            average_recovery_time = float(
                np.mean(recovery_times)
            )

        else:

            average_recovery_time = 0


        # =========================================
        # TIME-SERIES TRENDS
        # =========================================

        if not df.empty:

            df["date_only"] = (
                df["date"]
                .dt.strftime("%Y-%m-%d")
            )


            time_series = (
                df.groupby("date_only")
                .size()
                .to_dict()
            )

        else:

            time_series = {}


        # =========================================
        # RETURN RESPONSE
        # =========================================

        return jsonify({

            "status": "success",

            "data": {

                "total_patients":
                    total_patients,

                "total_doctors":
                    total_doctors,

                "total_appointments":
                    total_appointments,

                "average_appointments_per_doctor":
                    round(
                        average_appointments,
                        2
                    ),

                "average_recovery_time_days":
                    round(
                        average_recovery_time,
                        2
                    ),

                "status_distribution":
                    status_distribution,

                "common_diagnoses":
                    common_diagnoses,

                "doctor_performance":
                    doctor_performance,

                "time_series":
                    time_series
            }

        }), 200


    except Exception as e:

        print(
            "ANALYTICS ERROR:",
            str(e)
        )

        return jsonify({

            "status": "error",

            "message": str(e)

        }), 500