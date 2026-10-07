from flask import Flask, render_template, redirect
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from patients import patients_bp
from doctors import doctors_bp
from appointments import appointments_bp
from analytics import analytics_bp
from csv_upload import csv_bp
from export import export_bp
from csv_upload import csv_bp
from export import export_bp
from api_v1 import api_v1_bp
import os

from database import db
import models
from auth import auth_bp


load_dotenv()

app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["JWT_SECRET_KEY"] = os.getenv(
    "JWT_SECRET_KEY"
)


db.init_app(app)

jwt = JWTManager(app)

app.register_blueprint(auth_bp)
app.register_blueprint(patients_bp)
app.register_blueprint(doctors_bp)
app.register_blueprint(appointments_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(csv_bp)
app.register_blueprint(export_bp)
app.register_blueprint(api_v1_bp)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return "Hospital Management System is Running!"

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/patients-page")
def patients_page():
    return render_template("patients.html")

@app.route("/patients/new")
def new_patient_page():
    return render_template("patient_form.html")

@app.route("/patients/<int:patient_id>/view")
def view_patient_page(patient_id):
    return render_template(
        "patient_view.html"
    )
@app.route("/patients/<int:patient_id>/edit")
def edit_patient_page(patient_id):
    return render_template(
        "patient_edit.html"
    )
@app.route("/doctors-page")
def doctors_page():
    return render_template("doctors.html")
@app.route("/doctors/new")
def new_doctor_page():
    return render_template("doctor_form.html")

@app.route("/doctors/<int:doctor_id>/view")
def view_doctor_page(doctor_id):
    return render_template("doctor_view.html")

@app.route("/doctors/<int:doctor_id>/edit")
def edit_doctor_page(doctor_id):
    return render_template("doctor_edit.html")

@app.route("/appointments-page")
def appointments_page():
    return render_template("appointments.html")

@app.route("/appointments/new")
def new_appointment_page():
    return render_template("appointment_form.html")

@app.route("/appointments/<int:appointment_id>/view")
def view_appointment_page(appointment_id):
    return render_template(
        "appointment_view.html",
        appointment_id=appointment_id
    )
@app.route("/appointments/<int:appointment_id>/edit")
def edit_appointment_page(appointment_id):
    return render_template(
        "appointment_edit.html",
        appointment_id=appointment_id
    )
@app.route("/analytics-page")
def analytics_page():
    return render_template("analytics.html")

if __name__ == "__main__":
    app.run(debug=True)