from flask import Flask
from flask_restful import Api
from db import Base, engine
import models

# Create tables
Base.metadata.create_all(bind=engine)

app = Flask(__name__)
api = Api(app)

from resources.patients import PatientListAPI, PatientAPI, PatientAppointmentsAPI, PatientAppointmentsSortedAPI, PatientRegisterAPI
api.add_resource(PatientListAPI, "/api/patients")
api.add_resource(PatientAPI, "/api/patients/<string:patient_id>")
api.add_resource(PatientAppointmentsAPI, "/api/patients/<string:patient_id>/appointments")
api.add_resource(PatientAppointmentsSortedAPI, "/api/patients/<string:patient_id>/appointments/sorted")
api.add_resource(PatientRegisterAPI, "/api/patients/register")



from resources.doctors import DoctorListAPI, DoctorAPI, DoctorAppointmentsAPI, DoctorAppointmentsSortedAPI, DoctorRegisterAPI
api.add_resource(DoctorListAPI, "/api/doctors")
api.add_resource(DoctorAPI, "/api/doctors/<string:doctor_id>")
api.add_resource(DoctorAppointmentsAPI, "/api/doctors/<string:doctor_id>/appointments")
api.add_resource(DoctorAppointmentsSortedAPI, "/api/doctors/<string:doctor_id>/appointments/sorted")
api.add_resource(DoctorRegisterAPI, "/api/doctors/register")


from resources.appointments import AppointmentListAPI, AppointmentAPI
api.add_resource(AppointmentListAPI, "/api/appointments")
api.add_resource(AppointmentAPI, "/api/appointments/<appointment_id>")

from resources.medical_records import MedicalRecordListAPI, PatientMedicalRecordsAPI
api.add_resource(MedicalRecordListAPI, "/api/medical-records")
api.add_resource(PatientMedicalRecordsAPI, "/api/patients/<string:patient_id>/medical-records")

from resources.users import UserListAPI, AdminRegisterAPI
api.add_resource(UserListAPI, "/api/users")
api.add_resource(AdminRegisterAPI, "/api/admins/register")

from resources.schedules import DoctorSchedulesAPI, ScheduleListAPI
api.add_resource(DoctorSchedulesAPI, "/api/doctors/<string:doctor_id>/schedules")
api.add_resource(ScheduleListAPI, "/api/schedules")

from resources.schedules import ScheduleAPI
api.add_resource(ScheduleAPI, "/api/schedules/<string:schedule_id>")

from resources.departments import DepartmentListAPI, DepartmentAPI
api.add_resource(DepartmentListAPI, "/api/departments")
api.add_resource(DepartmentAPI,     "/api/departments/<string:department_id>")


if __name__ == "__main__":
    app.run(debug=True)
