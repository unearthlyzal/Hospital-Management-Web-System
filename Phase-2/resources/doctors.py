from flask_restful import Resource, reqparse, fields, marshal_with
from models import Doctor, Schedule, User
from db import SessionLocal
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
import json
from datetime import datetime, timedelta

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

class DoctorSetAvailabilityAPI(Resource):
    def post(self, doctor_id):
        parser = reqparse.RequestParser()
        parser.add_argument("availability", type=dict, required=True, 
            help="Availability should be a dictionary with days as keys and time ranges as values")
        args = parser.parse_args()

        session = SessionLocal()
        try:
            doctor = session.query(Doctor).get(doctor_id)
            if not doctor:
                return {"message": "Doctor not found"}, 404

            # Update the availability JSON
            doctor.availability = args["availability"]
            session.commit()

            # Now create/update schedule entries for the next 30 days based on availability
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=30)
            current_date = start_date

            # Delete existing future schedules
            session.query(Schedule).filter(
                Schedule.doctor_id == doctor_id,
                Schedule.datetime >= start_date
            ).delete()

            # Create new schedules
            new_schedules = []
            while current_date < end_date:
                day_name = current_date.strftime("%A")
                if day_name in args["availability"]:
                    time_ranges = args["availability"][day_name].split(",")
                    for time_range in time_ranges:
                        start_time, end_time = time_range.split("-")
                        start_hour = int(start_time.strip())
                        end_hour = int(end_time.strip())
                        
                        for hour in range(start_hour, end_hour):
                            schedule_time = current_date.replace(hour=hour)
                            new_schedules.append(Schedule(
                                id=f"SC{len(new_schedules)+1:04}",
                                doctor_id=doctor_id,
                                datetime=schedule_time,
                                duration=60,
                                is_available=True
                            ))
                current_date += timedelta(days=1)

            session.bulk_save_objects(new_schedules)
            session.commit()
            return {"message": "Availability updated successfully"}, 200
        except Exception as e:
            session.rollback()
            return {"message": f"Error occurred: {str(e)}"}, 500
        finally:
            session.close()

schedule_fields = {
    'id': fields.String,
    'datetime': fields.DateTime,
    'duration': fields.Integer,
    'is_available': fields.Boolean
}

class DoctorViewScheduleAPI(Resource):
    @marshal_with(schedule_fields)
    def get(self, doctor_id):
        parser = reqparse.RequestParser()
        parser.add_argument("start_date", type=str, required=False)
        parser.add_argument("end_date", type=str, required=False)
        args = parser.parse_args()

        session = SessionLocal()
        try:
            # Verify doctor exists
            doctor = session.query(Doctor).get(doctor_id)
            if not doctor:
                return {"message": "Doctor not found"}, 404

            query = session.query(Schedule).filter(Schedule.doctor_id == doctor_id)

            # Add date filters if provided
            if args["start_date"]:
                start_date = datetime.strptime(args["start_date"], "%Y-%m-%d")
                query = query.filter(Schedule.datetime >= start_date)
            if args["end_date"]:
                end_date = datetime.strptime(args["end_date"], "%Y-%m-%d")
                query = query.filter(Schedule.datetime <= end_date)

            # Order by datetime
            schedules = query.order_by(Schedule.datetime).all()
            return schedules
        finally:
            session.close()


