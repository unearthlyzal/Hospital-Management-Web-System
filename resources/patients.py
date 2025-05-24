from flask_restful import Resource, reqparse, fields, marshal_with
from models import Patient, User
from db import SessionLocal
from sqlalchemy.orm import joinedload
from datetime import datetime

# Define how the output should look
patient_fields = {
    'id': fields.String,
    'first_name': fields.String,
    'last_name': fields.String,
    'email': fields.String,
    'phone': fields.String,
    'birth_date': fields.String,  # iso date
    'gender':     fields.String,
    'address':    fields.String,
}

appointment_fields = {
    'id': fields.String,
    'patient_id': fields.String,
    'doctor_id': fields.String,
    'datetime': fields.DateTime(dt_format='iso8601'),
    'status': fields.String,
}

# Define what inputs are allowed
parser = reqparse.RequestParser()
parser.add_argument("first_name", required=True)
parser.add_argument("last_name", required=True)
parser.add_argument("email", required=True)
parser.add_argument("phone", required=True)
parser.add_argument("birth_date")   # "YYYY-MM-DD"
parser.add_argument("gender")       # "M" or "F"
parser.add_argument("address")      # optional
parser.add_argument("user_id")      # required in manual create

class PatientListAPI(Resource):
    @marshal_with(patient_fields)
    def get(self):
        session = SessionLocal()
        patients = session.query(Patient).all()
        session.close()
        return patients

    @marshal_with(patient_fields)
    def post(self):
        args = parser.parse_args()
        session = SessionLocal()

        last = session.query(Patient).order_by(Patient.id.desc()).first()
        new_id = f"P{(int(last.id[1:]) + 1) if last else 1:03}"

        new_patient = Patient(
            id=new_id,
            first_name=args["first_name"],
            last_name=args["last_name"],
            email=args["email"],
            phone=args["phone"],
            birth_date=args.get("birth_date"),
            gender=args.get("gender"),
            address=args.get("address"),
            user_id=args.get("user_id")
        )
        session.add(new_patient)
        session.commit()
        session.refresh(new_patient)
        session.close()
        return new_patient, 201

class PatientAPI(Resource):
    @marshal_with(patient_fields)
    def get(self, patient_id):
        session = SessionLocal()
        patient = session.query(Patient).filter(Patient.id == patient_id).first()
        session.close()
        if not patient:
            return {"message": "Patient not found"}, 404
        return patient

    @marshal_with(patient_fields)
    def put(self, patient_id):
        args = parser.parse_args()
        session = SessionLocal()
        patient = session.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            session.close()
            return {"message": "Patient not found"}, 404

        for key, value in args.items():
            if value is not None:
                setattr(patient, key, value)

        session.commit()
        session.refresh(patient)
        session.close()
        return patient, 200

    def delete(self, patient_id):
        session = SessionLocal()
        patient = session.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            session.close()
            return {"message": "Patient not found"}, 404

        session.delete(patient)
        session.commit()
        session.close()
        return {"message": f"Patient {patient_id} deleted"}, 200

class PatientRegisterAPI(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("username", required=True)
        parser.add_argument("password", required=True)
        parser.add_argument("email", required=True)
        parser.add_argument("first_name", required=True)
        parser.add_argument("last_name", required=True)
        parser.add_argument("phone", required=True)
        args = parser.parse_args()

        session = SessionLocal()

        last_user = session.query(User).order_by(User.id.desc()).first()
        new_user_id = f"U{(int(last_user.id[1:]) + 1) if last_user else 1:03}"

        user = User(
            id=new_user_id,
            username=args["username"],
            password=args["password"],
            email=args["email"],
            role="Patient"
        )
        session.add(user)

        # Create patient
        last_patient = session.query(Patient).order_by(Patient.id.desc()).first()
        new_patient_id = f"P{(int(last_patient.id[1:]) + 1) if last_patient else 1:03}"
        patient = Patient(
            id=new_patient_id,
            user_id=new_user_id,
            first_name=args["first_name"],
            last_name=args["last_name"],
            phone=args["phone"]
        )
        session.add(patient)

        session.commit()
        session.close()
        return {"message": f"Patient {patient.id} created and linked to user {user.id}"}, 201


# class PatientAPI(Resource):
#     def delete(self, patient_id):
#         session = SessionLocal()
#         patient = session.query(Patient).filter(Patient.id == patient_id).first()
#         if not patient:
#             session.close()
#             return {"message": "Patient not found"}, 404

#         session.delete(patient)
#         session.commit()
#         session.close()
#         return {"message": f"Patient {patient_id} deleted"}, 200

class PatientAppointmentsAPI(Resource):
    @marshal_with(appointment_fields)
    def get(self, patient_id):
        session = SessionLocal()
        patient = session.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            session.close()
            return {"message": "Patient not found"}, 404

        appointments = patient.appointments
        session.close()
        return appointments

from datetime import datetime

class PatientAppointmentsSortedAPI(Resource):
    @marshal_with(appointment_fields)
    def get(self, patient_id):
        session = SessionLocal()
        patient = session.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            session.close()
            return {"message": "Patient not found"}, 404

        now = datetime.utcnow()

        upcoming = sorted(
            [a for a in patient.appointments if a.schedule.datetime > now],
            key=lambda a: a.datetime
        )
        history = sorted(
            [a for a in patient.appointments if a.datetime <= now],
            key=lambda a: a.datetime,
            reverse=True
        )

        session.close()
        return {
            "upcoming": upcoming,
            "history": history
        }
