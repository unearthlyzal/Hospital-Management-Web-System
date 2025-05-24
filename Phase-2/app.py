from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException
import os

from db import SessionLocal, engine, Base
from error_handlers import register_error_handlers
from resources.users import UserList, UserResource, UserLoginAPI, UserLogoutAPI, CurrentUser
from resources.patients import PatientList, PatientResource, PatientRegisterAPI, PatientAppointmentsAPI, PatientAppointmentsSortedAPI, PatientBookAppointmentAPI
from resources.doctors import DoctorList, DoctorResource, DoctorAvailabilityList, DoctorAvailabilityResource, DoctorAppointmentsAPI, DoctorAppointmentsSortedAPI, DoctorSetAvailabilityAPI, DoctorViewScheduleAPI
from resources.appointments import AppointmentListAPI, AppointmentAPI, AppointmentCreateAPI, AppointmentCancelAPI, AppointmentRescheduleAPI
from resources.medical_records import MedicalRecordListAPI, MedicalRecordAPI, PatientMedicalRecordsAPI
from resources.departments import DepartmentListAPI, DepartmentAPI

# Load environment variables
load_dotenv()

def create_app(config_object=None):
    app = Flask(__name__)
    
    # Configuration
    if config_object:
        app.config.from_object(config_object)
    else:
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-this')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLSERVER_CONN', "mssql+pyodbc://@localhost/HospitalDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes")
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-key-change-this')

    # Initialize extensions
    CORS(app, resources={
        r"/*": {
            "origins": os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(','),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Initialize API
    api = Api(app)

    # Register error handlers
    register_error_handlers(app)

    # Create database tables
    Base.metadata.create_all(bind=engine)

    # Register routes
    api.add_resource(UserList, '/api/users')
    api.add_resource(UserResource, '/api/users/<string:id>')
    api.add_resource(UserLoginAPI, '/api/auth/login')
    api.add_resource(UserLogoutAPI, '/api/auth/logout')
    api.add_resource(CurrentUser, '/api/users/me')
    
    api.add_resource(PatientList, '/api/patients')
    api.add_resource(PatientResource, '/api/patients/<string:patient_id>')
    api.add_resource(PatientRegisterAPI, '/api/patients/register')
    api.add_resource(PatientAppointmentsAPI, '/api/patients/<string:patient_id>/appointments')
    api.add_resource(PatientAppointmentsSortedAPI, '/api/patients/<string:patient_id>/appointments/sorted')
    api.add_resource(PatientBookAppointmentAPI, '/api/patients/<string:patient_id>/appointments/book')
    
    api.add_resource(DoctorList, '/api/doctors')
    api.add_resource(DoctorResource, '/api/doctors/<string:doctor_id>')
    api.add_resource(DoctorAvailabilityList, '/api/doctors/<string:doctor_id>/availabilities')
    api.add_resource(DoctorAvailabilityResource, '/api/doctors/<string:doctor_id>/availabilities/<int:id>')
    api.add_resource(DoctorAppointmentsAPI, '/api/doctors/<string:doctor_id>/appointments')
    api.add_resource(DoctorAppointmentsSortedAPI, '/api/doctors/<string:doctor_id>/appointments/sorted')
    api.add_resource(DoctorSetAvailabilityAPI, '/api/doctors/<string:doctor_id>/set-availability')
    api.add_resource(DoctorViewScheduleAPI, '/api/doctors/<string:doctor_id>/schedule')
    
    api.add_resource(AppointmentListAPI, '/api/appointments')
    api.add_resource(AppointmentAPI, '/api/appointments/<string:appointment_id>')
    api.add_resource(AppointmentCreateAPI, '/api/appointments/create')
    api.add_resource(AppointmentCancelAPI, '/api/appointments/<string:appointment_id>/cancel')
    api.add_resource(AppointmentRescheduleAPI, '/api/appointments/<string:appointment_id>/reschedule')
    
    api.add_resource(MedicalRecordListAPI, '/api/medical-records')
    api.add_resource(MedicalRecordAPI, '/api/medical-records/<string:record_id>')
    api.add_resource(PatientMedicalRecordsAPI, '/api/patients/<string:patient_id>/medical-records')
    
    api.add_resource(DepartmentListAPI, '/api/departments')
    api.add_resource(DepartmentAPI, '/api/departments/<string:department_id>')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=os.getenv('DEBUG', 'True') == 'True')
