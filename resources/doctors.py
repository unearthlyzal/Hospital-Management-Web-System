from flask_restful import Resource, reqparse, fields, marshal_with
from models import Doctor
from models import User
from db import SessionLocal
from sqlalchemy.orm import joinedload

def get_dept_name(doc):
    return doc.department_obj.name if doc.department_obj else None

doctor_fields = {
    'id': fields.String,
    'first_name': fields.String,
    'last_name': fields.String,
    'department': fields.String(attribute=get_dept_name),
    'availability': fields.Raw,  # For JSON field
    'phone': fields.String   
}

appointment_fields = {
    'id': fields.String,
    'patient_id': fields.String,
    'doctor_id': fields.String,
    'datetime': fields.DateTime(dt_format='iso8601'),
    'status': fields.String,
}

parser = reqparse.RequestParser()
# parser.add_argument("name", required=True)
parser.add_argument("first_name", required=True)
parser.add_argument("last_name", required=True)
parser.add_argument("department_id", required=True)
parser.add_argument("phone", required=True)
parser.add_argument("availability", type=dict, required=True)
parser.add_argument("user_id", required=True)


class DoctorListAPI(Resource):
    @marshal_with(doctor_fields)
    def get(self):
        session = SessionLocal()
        doctors = (
            session.query(Doctor)
                .options(joinedload(Doctor.department_obj))
                .all()
        )
        session.close()
        return doctors

    @marshal_with(doctor_fields)
    def post(self):
        args = parser.parse_args()
        session = SessionLocal()

        user = session.query(User).filter_by(id=args["user_id"], role="Doctor").first()
        if not user:
            session.close()
            return {"message": "Invalid user_id or role"}, 400

        last = session.query(Doctor).order_by(Doctor.id.desc()).first()
        if last:
            last_num = int(last.id[1:])
        else:
            last_num = 0
        doctor_id = f"D{last_num + 1:03}"

        doctor = Doctor(
            id=doctor_id,
            user_id=args["user_id"],
            first_name=args["first_name"],
            last_name=args["last_name"],
            department_id=args["department_id"],
            availability={},
            phone=args["phone"]
            )
        session.add(doctor)
        session.commit()
        session.refresh(doctor)
        session.close()
        return doctor, 201

class DoctorRegisterAPI(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("username", required=True)
        parser.add_argument("password", required=True)
        parser.add_argument("email", required=True)
        parser.add_argument("first_name", required=True)
        parser.add_argument("last_name", required=True)
        parser.add_argument("department_id", required=True)
        parser.add_argument("phone", required=True)
        args = parser.parse_args()

        session = SessionLocal()

        # Create new user
        last_user = session.query(User).order_by(User.id.desc()).first()
        new_user_id = f"U{(int(last_user.id[1:]) + 1) if last_user else 1:03}"
        user = User(
            id=new_user_id,
            username=args["username"],
            password=args["password"],
            email=args["email"],
            role="Doctor"
        )
        session.add(user)

        # Create new doctor
        last_doctor = session.query(Doctor).order_by(Doctor.id.desc()).first()

        if last_doctor and last_doctor.id.startswith('D') and last_doctor.id[1:].isdigit():
            last_id_num = int(last_doctor.id[1:])
        else:
            last_id_num = 0

        new_doctor_id = f"D{last_id_num + 1:03}"

        new_doctor = Doctor(
            id=new_doctor_id,
            user_id=new_user_id,
            first_name=args["first_name"],
            last_name=args["last_name"],
            department_id=args["department_id"],
            availability={},
            phone=args["phone"]
            )
        session.add(new_doctor)

        session.commit()
        session.close()
        return {"message": f"Doctor {new_doctor.id} created and linked to user {user.id}"}, 201


class DoctorAPI(Resource):
    @marshal_with(doctor_fields)
    def get(self, doctor_id):
        session = SessionLocal()
        doctor = session.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor:
            session.close()
            return {"message": "Doctor not found"}, 404
        session.close()
        return doctor

    @marshal_with(doctor_fields)
    def put(self, doctor_id):
        args = parser.parse_args()
        session = SessionLocal()
        doctor = session.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor:
            session.close()
            return {"message": "Doctor not found"}, 404

        doctor.first_name = args["first_name"]
        doctor.last_name = args["last_name"]
        doctor.department_id = args["department_id"]
        doctor.phone = args["phone"]
        doctor.availability = args["availability"]

        session.commit()
        session.refresh(doctor)
        session.close()
        return doctor

    def delete(self, doctor_id):
        session = SessionLocal()
        doctor = session.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor:
            session.close()
            return {"message": "Doctor not found"}, 404

        session.delete(doctor)
        session.commit()
        session.close()
        return {"message": f"Doctor {doctor_id} deleted"}, 200


class DoctorAppointmentsAPI(Resource):
    @marshal_with(appointment_fields)
    def get(self, doctor_id):
        session = SessionLocal()
        doctor = session.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor:
            session.close()
            return {"message": "Doctor not found"}, 404

        appointments = doctor.appointments
        session.close()
        return appointments

from datetime import datetime

class DoctorAppointmentsSortedAPI(Resource):
    @marshal_with(appointment_fields)
    def get(self, doctor_id):
        session = SessionLocal()
        doctor = session.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not doctor:
            session.close()
            return {"message": "Doctor not found"}, 404

        now = datetime.utcnow()

        upcoming = sorted(
            [a for a in doctor.appointments if a.schedule and a.schedule.datetime > now],
            key=lambda a: a.datetime
        )
        history = sorted(
            [a for a in doctor.appointments if a.schedule and a.schedule.datetime <= now],
            key=lambda a: a.datetime,
            reverse=True
        )

        session.close()
        return {
            "upcoming": upcoming,
            "history": history
        }


