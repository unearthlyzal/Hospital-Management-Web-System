from flask_restful import Resource, reqparse, fields, marshal_with
from models import Schedule, Doctor
from resources.doctors import doctor_fields
from db import SessionLocal
from sqlalchemy.orm import joinedload
import datetime
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta

def get_day(obj):
    # obj.datetime is a Python datetime
    return obj.datetime.strftime("%A")

schedule_fields = {
    'id': fields.String,
    'doctor_id': fields.String,
    'doctor': fields.Nested(doctor_fields),
    'datetime': fields.DateTime(dt_format='iso8601'),
    'day': fields.String(attribute=get_day),
    'duration': fields.Integer,
    'is_available': fields.Boolean,
}

parser = reqparse.RequestParser()
parser.add_argument("doctor_id", required=True)
parser.add_argument("datetime", required=True)  # ISO format
parser.add_argument("duration", type=int, required=True)

class ScheduleListAPI(Resource):
    @marshal_with(schedule_fields)
    def get(self, doctor_id):
        session = SessionLocal()
        schedules = session.query(Schedule).all()
        session.close()
        return schedules

    @marshal_with(schedule_fields)
    def post(self):
        args = parser.parse_args()
        session = SessionLocal()
        # Generate schedule ID (e.g., SC001)
        last = session.query(Schedule).order_by(Schedule.id.desc()).first()
        new_id = f"SC{(int(last.id[2:]) + 1) if last else 1:03}"

        session.add(Schedule(id=new_id, **args))
        session.commit()

        # Now re-query with doctor eagerly loaded
        sched = (
            session.query(Schedule)
            .options(joinedload(Schedule.doctor))
            .filter(Schedule.id == new_id)
            .one()
        )

        # new_schedule = Schedule(id=new_id, **args)
        # session.add(new_schedule)
        # session.commit()
        # session.refresh(new_schedule)
        session.close()
        return sched, 201

class DoctorSchedulesAPI(Resource):
    @marshal_with(schedule_fields)
    def get(self, doctor_id):
        session = SessionLocal()
        schedules = session.query(Schedule).filter(
            Schedule.doctor_id == doctor_id
        ).all()
        session.close()
        return schedules

class ScheduleAPI(Resource):
    @marshal_with(schedule_fields)
    def get(self, schedule_id):
        session = SessionLocal()
        sched = session.query(Schedule).get(schedule_id)
        session.close()
        if not sched:
            return {"message": "Schedule not found"}, 404
        return sched

    @marshal_with(schedule_fields)
    def put(self, schedule_id):
        args = parser.parse_args()
        session = SessionLocal()
        sched = session.query(Schedule).get(schedule_id)
        if not sched:
            session.close()
            return {"message": "Schedule not found"}, 404

        # Update mutable fields
        sched.datetime     = args["datetime"]
        sched.duration     = args["duration"]
        sched.is_available = args.get("is_available", sched.is_available)
        session.commit()
        session.refresh(sched)
        session.close()
        return sched, 200

    def delete(self, schedule_id):
        session = SessionLocal()
        sched = session.query(Schedule).get(schedule_id)
        if not sched:
            session.close()
            return {"message": "Schedule not found"}, 404
        session.delete(sched)
        session.commit()
        session.close()
        return {"message": f"Schedule {schedule_id} deleted"}, 200

class ScheduleCheckAvailabilityAPI(Resource):
    @marshal_with(schedule_fields)
    def get(self, doctor_id):
        parser = reqparse.RequestParser()
        parser.add_argument("start_date", type=str, required=True, help="Start date in YYYY-MM-DD format")
        parser.add_argument("end_date", type=str, required=True, help="End date in YYYY-MM-DD format")
        args = parser.parse_args()

        session = SessionLocal()
        try:
            # Verify doctor exists
            doctor = session.query(Doctor).get(doctor_id)
            if not doctor:
                return {"message": "Doctor not found"}, 404

            # Convert string dates to datetime
            try:
                start_date = datetime.strptime(args["start_date"], "%Y-%m-%d")
                end_date = datetime.strptime(args["end_date"], "%Y-%m-%d") + timedelta(days=1)  # Include end date
            except ValueError:
                return {"message": "Invalid date format. Use YYYY-MM-DD"}, 400

            # Get available schedules
            available_schedules = session.query(Schedule)\
                .filter(
                    Schedule.doctor_id == doctor_id,
                    Schedule.datetime >= start_date,
                    Schedule.datetime < end_date,
                    Schedule.is_available == True
                )\
                .order_by(Schedule.datetime)\
                .all()

            return available_schedules
        finally:
            session.close()
