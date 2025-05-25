from flask_restful import Resource, reqparse, fields, marshal_with
from sqlalchemy.orm import joinedload
from models import Appointment, Schedule, Patient, Doctor
from db import SessionLocal
from datetime import timedelta, datetime
from sqlalchemy.exc import IntegrityError

VALID_STATUS = ["Scheduled", "Completed", "Cancelled", "No-Show"]

# Custom datetime formatter
def iso_datetime(value):
    return value.isoformat() if value else None

def get_date(obj):
    return obj.schedule.datetime.date().isoformat() if obj.schedule else None

def get_start(obj):
    return obj.schedule.datetime.time().isoformat() if obj.schedule else None

def get_end(obj):
    if not obj.schedule:
        return None
    end_dt = obj.schedule.datetime + timedelta(minutes=obj.schedule.duration)
    return end_dt.time().isoformat()

def get_doc_name(appt):
    if not (appt.schedule and appt.schedule.doctor):
        return None
    return f"{appt.schedule.doctor.first_name} {appt.schedule.doctor.last_name}"

appointment_fields = {
    'id': fields.String,
    'patient_id': fields.String,
    'doctor_id': fields.String,
    'schedule_id': fields.String,
    'status': fields.String,
}

parser = reqparse.RequestParser()
parser.add_argument("patient_id", required=True)
parser.add_argument("schedule_id", required=True)
parser.add_argument("status", required=True, choices=VALID_STATUS)

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
        try:
            appt = session.query(Appointment).get(appointment_id)
            if not appt:
                session.close()
                return {"message": "Appointment not found"}, 404

            # If changing schedule, verify new slot is available
            if "schedule_id" in args and args["schedule_id"] != appt.schedule_id:
                new_schedule = session.query(Schedule).filter(
                    Schedule.id == args["schedule_id"],
                    Schedule.is_available == True
                ).with_for_update().first()
                
                if not new_schedule:
                    session.close()
                    return {"message": "New schedule slot not available"}, 400
                
                # Free up old slot
                old_schedule = session.query(Schedule).filter(
                    Schedule.id == appt.schedule_id
                ).first()
                if old_schedule:
                    old_schedule.is_available = True
                
                # Take new slot
                new_schedule.is_available = False
                appt.schedule_id = args["schedule_id"]

            if "status" in args:
                appt.status = args["status"]

            session.commit()
            session.refresh(appt)
            return appt, 200

        except Exception as e:
            session.rollback()
            return {"message": str(e)}, 500
        finally:
            session.close()

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

class AppointmentCreateAPI(Resource):
    @marshal_with(appointment_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("patient_id", required=True)
        parser.add_argument("schedule_id", required=True)
        args = parser.parse_args()

        session = SessionLocal()
        try:
            # Verify patient exists
            patient = session.query(Patient).get(args["patient_id"])
            if not patient:
                return {"message": "Patient not found"}, 404

            # Get and verify schedule
            schedule = session.query(Schedule).get(args["schedule_id"])
            if not schedule:
                return {"message": "Schedule not found"}, 404
            
            if not schedule.is_available:
                return {"message": "This time slot is not available"}, 400

            if schedule.datetime < datetime.now():
                return {"message": "Cannot book past time slots"}, 400

            # Create new appointment
            last_appointment = session.query(Appointment).order_by(Appointment.id.desc()).first()
            new_id = f"A{(int(last_appointment.id[1:]) + 1) if last_appointment else 1:03}"
            
            appointment = Appointment(
                id=new_id,
                patient_id=args["patient_id"],
                doctor_id=schedule.doctor_id,
                schedule_id=schedule.id,
                status="Scheduled"
            )

            # Mark schedule as unavailable
            schedule.is_available = False

            session.add(appointment)
            session.commit()
            session.refresh(appointment)
            return appointment, 201
        except IntegrityError:
            session.rollback()
            return {"message": "Database error occurred"}, 500
        finally:
            session.close()

class AppointmentCancelAPI(Resource):
    @marshal_with(appointment_fields)
    def put(self, appointment_id):
        session = SessionLocal()
        try:
            appointment = session.query(Appointment).get(appointment_id)
            if not appointment:
                return {"message": "Appointment not found"}, 404

            if appointment.status == "Cancelled":
                return {"message": "Appointment is already cancelled"}, 400

            if appointment.status == "Completed":
                return {"message": "Cannot cancel completed appointment"}, 400

            if appointment.schedule.datetime < datetime.now():
                return {"message": "Cannot cancel past appointments"}, 400

            # Update appointment status
            appointment.status = "Cancelled"
            
            # Make the schedule available again
            schedule = session.query(Schedule).get(appointment.schedule_id)
            schedule.is_available = True

            session.commit()
            session.refresh(appointment)
            return appointment
        except IntegrityError:
            session.rollback()
            return {"message": "Database error occurred"}, 500
        finally:
            session.close()

class AppointmentRescheduleAPI(Resource):
    @marshal_with(appointment_fields)
    def put(self, appointment_id):
        parser = reqparse.RequestParser()
        parser.add_argument("new_schedule_id", required=True)
        args = parser.parse_args()

        session = SessionLocal()
        try:
            # Verify appointment exists
            appointment = session.query(Appointment).get(appointment_id)
            if not appointment:
                return {"message": "Appointment not found"}, 404

            if appointment.status != "Scheduled":
                return {"message": "Can only reschedule scheduled appointments"}, 400

            # Get and verify new schedule
            new_schedule = session.query(Schedule).get(args["new_schedule_id"])
            if not new_schedule:
                return {"message": "New schedule slot not found"}, 404

            if not new_schedule.is_available:
                return {"message": "New time slot is not available"}, 400

            if new_schedule.datetime < datetime.now():
                return {"message": "Cannot reschedule to past time slots"}, 400

            if new_schedule.doctor_id != appointment.doctor_id:
                return {"message": "Cannot reschedule to a different doctor"}, 400

            # Make old schedule available
            old_schedule = session.query(Schedule).get(appointment.schedule_id)
            old_schedule.is_available = True

            # Update appointment with new schedule
            appointment.schedule_id = new_schedule.id
            new_schedule.is_available = False

            session.commit()
            session.refresh(appointment)
            return appointment
        except IntegrityError:
            session.rollback()
            return {"message": "Database error occurred"}, 500
        finally:
            session.close()