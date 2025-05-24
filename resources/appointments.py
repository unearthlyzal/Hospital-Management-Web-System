from flask_restful import Resource, reqparse, fields, marshal_with
from sqlalchemy.orm import joinedload
from models import Appointment, Schedule
from db import SessionLocal
from datetime import timedelta

# Custom datetime formatter
def iso_datetime(value):
    return value.isoformat() if value else None

def get_date(obj):
    return obj.schedule.datetime.date().isoformat()

def get_start(obj):
    return obj.schedule.datetime.time().isoformat()

def get_end(obj):
    end_dt = obj.schedule.datetime + timedelta(minutes=obj.schedule.duration)
    return end_dt.time().isoformat()

def get_doc_name(appt):
    return appt.schedule.doctor.name if appt.schedule and appt.schedule.doctor else None

appointment_fields = {
    'id': fields.String,
    'patient_id': fields.String,
    'schedule_id': fields.String,
    'doctor_id': fields.String(attribute=get_doc_name),# fields.String (attribute=lambda x: x.schedule.doctor_id),

    'date':       fields.String(attribute=get_date),
    'start_time': fields.String(attribute=get_start),
    'end_time':   fields.String(attribute=get_end),
    # 'datetime': fields.String(attribute=lambda x: iso_datetime(x.schedule.datetime)),
    'status': fields.String
}

parser = reqparse.RequestParser()
parser.add_argument("patient_id", required=True)
parser.add_argument("schedule_id", required=True)
parser.add_argument("status", required=True)

class AppointmentListAPI(Resource):
    @marshal_with(appointment_fields)
    def get(self):
        session = SessionLocal()
        appointments = session.query(Appointment).options(
            joinedload(Appointment.schedule)
            .joinedload(Schedule.doctor)  # also pull in the doctor
        ).all()
        session.close()
        return appointments

    @marshal_with(appointment_fields)
    def post(self):
        args = parser.parse_args()
        session = SessionLocal()

        try:
            # Atomic transaction
            schedule = session.query(Schedule).filter(
                Schedule.id == args["schedule_id"],
                Schedule.is_available == True
            ).with_for_update().first()  # Lock the row

            if not schedule:
                return {"message": "Slot not available"}, 400

            # Generate appointment ID safely
            last_appointment = session.query(Appointment).order_by(Appointment.id.desc()).first()
            # Compute the next numeric suffix first
            if last_appointment:
                next_num = int(last_appointment.id[1:]) + 1
            else:
                next_num = 1

            # Then format it with leading zeros
            new_id = f"A{next_num:03}"
            
            # new_id = f"A{(int(last_appointment.id[1:]) + 1) if last_appointment else 1:03d}"

            new_appointment = Appointment(
                id=new_id,
                patient_id=args["patient_id"],
                schedule_id=args["schedule_id"],
                status=args["status"]
            )

            schedule.is_available = False
            session.add(new_appointment)
            session.commit()
            return new_appointment, 201

        except Exception as e:
            session.rollback()
            return {"message": str(e)}, 500
        finally:
            session.close()

class AppointmentAPI(Resource):
    @marshal_with(appointment_fields)
    def get(self, appointment_id):
        session = SessionLocal()
        appt = session.query(Appointment).get(appointment_id)
        session.close()
        if not appt:
            return {"message": "Appointment not found"}, 404
        return appt

    @marshal_with(appointment_fields)
    def put(self, appointment_id):
        args = parser.parse_args()
        session = SessionLocal()
        appt = session.query(Appointment).get(appointment_id)
        if not appt:
            session.close()
            return {"message": "Appointment not found"}, 404

        # Only allow updating status or rescheduling via schedule change
        if "schedule_id" in args:
            appt.schedule_id = args["schedule_id"]
        if "status" in args:
            appt.status = args["status"]

        session.commit()
        session.refresh(appt)
        session.close()
        return appt, 200

    def delete(self, appointment_id):
        session = SessionLocal()
        try:
            # Use transaction
            appointment = session.query(Appointment).filter(
                Appointment.id == appointment_id
            ).first()

            if not appointment:
                return {"message": "Appointment not found"}, 404

            # Free up the schedule slot
            schedule = session.query(Schedule).filter(
                Schedule.id == appointment.schedule_id
            ).first()
            
            if schedule:
                schedule.is_available = True

            session.delete(appointment)
            session.commit()
            return {"message": f"Appointment {appointment_id} deleted"}, 200

        except Exception as e:
            session.rollback()
            return {"message": str(e)}, 500
        finally:
            session.close()