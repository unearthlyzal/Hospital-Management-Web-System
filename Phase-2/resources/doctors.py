from flask_restful import Resource, reqparse, fields, marshal_with
from models import Doctor, Schedule, User, DoctorAvailability
from db import SessionLocal
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError
import json
from datetime import datetime, timedelta
from flask_restx import Namespace, request
from auth import admin_required, doctor_required, get_current_user

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

ns = Namespace('doctors', description='Doctor operations')

user_model = ns.model('User', {
    'id': fields.Integer(readonly=True),
    'username': fields.String(required=True),
    'email': fields.String(required=True),
    'role': fields.String(required=True)
})

availability_model = ns.model('Availability', {
    'id': fields.Integer(readonly=True),
    'doctor_id': fields.Integer(required=True),
    'day_of_week': fields.Integer(required=True, min=0, max=6),
    'start_time': fields.String(required=True),
    'end_time': fields.String(required=True),
    'is_available': fields.Boolean(default=True)
})

doctor_model = ns.model('Doctor', {
    'id': fields.Integer(readonly=True),
    'user_id': fields.Integer(required=True),
    'user': fields.Nested(user_model),
    'specialization': fields.String(required=True),
    'qualification': fields.String(required=True),
    'experience_years': fields.Integer(required=True),
    'availabilities': fields.List(fields.Nested(availability_model))
})

@ns.route('')
class DoctorList(Resource):
    @ns.marshal_list_with(doctor_model)
    def get(self):
        """Get all doctors"""
        session = SessionLocal()
        doctors = (
            session.query(Doctor)
                .join(User)
                .options(joinedload(Doctor.department_obj))
                .all()
        )
        session.close()
        return doctors

    @admin_required
    @ns.expect(doctor_model)
    @ns.marshal_with(doctor_model)
    def post(self):
        """Create a new doctor (Admin only)"""
        data = request.json
        session = SessionLocal()

        user = session.query(User).filter_by(id=data['user_id'], role="Doctor").first()
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
            user_id=data['user_id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            department_id=data['department_id'],
            availability={},
            phone=data['phone'],
            specialization=data['specialization'],
            qualification=data['qualification'],
            experience_years=data['experience_years']
        )
        session.add(doctor)
        session.commit()
        session.refresh(doctor)
        session.close()
        return doctor, 201

@ns.route('/<int:id>')
class DoctorResource(Resource):
    @ns.marshal_with(doctor_model)
    def get(self, id):
        """Get a doctor by ID"""
        session = SessionLocal()
        doctor = (
            session.query(Doctor)
                .join(User)
                .filter(Doctor.id == id)
                .first()
        )
        if not doctor:
            session.close()
            return {"message": "Doctor not found"}, 404
        session.close()
        return doctor

    @admin_required
    @ns.expect(doctor_model)
    @ns.marshal_with(doctor_model)
    def put(self, id):
        """Update a doctor (Admin only)"""
        session = SessionLocal()
        doctor = (
            session.query(Doctor)
                .join(User)
                .filter(Doctor.id == id)
                .first()
        )
        if not doctor:
            session.close()
            return {"message": "Doctor not found"}, 404

        data = request.json
        doctor.first_name = data.get('first_name', doctor.first_name)
        doctor.last_name = data.get('last_name', doctor.last_name)
        doctor.department_id = data.get('department_id', doctor.department_id)
        doctor.phone = data.get('phone', doctor.phone)
        doctor.specialization = data.get('specialization', doctor.specialization)
        doctor.qualification = data.get('qualification', doctor.qualification)
        doctor.experience_years = data.get('experience_years', doctor.experience_years)

        session.commit()
        session.refresh(doctor)
        session.close()
        return doctor

    @admin_required
    def delete(self, id):
        """Delete a doctor (Admin only)"""
        session = SessionLocal()
        doctor = (
            session.query(Doctor)
                .join(User)
                .filter(Doctor.id == id)
                .first()
        )
        if not doctor:
            session.close()
            return {"message": "Doctor not found"}, 404

        session.delete(doctor)
        session.commit()
        session.close()
        return {"message": f"Doctor {id} deleted"}, 200

@ns.route('/<int:id>/availabilities')
class DoctorAvailabilityList(Resource):
    @ns.marshal_list_with(availability_model)
    def get(self, id):
        """Get doctor's availabilities"""
        session = SessionLocal()
        doctor = (
            session.query(Doctor)
                .join(User)
                .filter(Doctor.id == id)
                .first()
        )
        if not doctor:
            session.close()
            return {"message": "Doctor not found"}, 404

        availabilities = doctor.availabilities
        session.close()
        return availabilities

    @doctor_required
    @ns.expect(availability_model)
    @ns.marshal_with(availability_model)
    def post(self, id):
        """Add doctor availability (Doctor only)"""
        current_user = get_current_user()
        session = SessionLocal()
        doctor = (
            session.query(Doctor)
                .join(User)
                .filter(Doctor.id == id)
                .first()
        )
        if not doctor:
            session.close()
            return {"message": "Doctor not found"}, 404

        # Verify the doctor is adding their own availability
        if current_user.role != 'admin' and doctor.user_id != current_user.id:
            session.close()
            return {'message': 'Unauthorized'}, 403

        data = request.json
        availability = DoctorAvailability(
            doctor_id=id,
            day_of_week=data['day_of_week'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            is_available=data.get('is_available', True)
        )
        
        session.add(availability)
        session.commit()
        session.close()
        return availability, 201

@ns.route('/<int:doctor_id>/availabilities/<int:id>')
class DoctorAvailabilityResource(Resource):
    @ns.marshal_with(availability_model)
    def get(self, doctor_id, id):
        """Get specific availability"""
        session = SessionLocal()
        doctor = (
            session.query(Doctor)
                .join(User)
                .filter(Doctor.id == doctor_id)
                .first()
        )
        if not doctor:
            session.close()
            return {"message": "Doctor not found"}, 404

        availability = session.query(DoctorAvailability).filter(DoctorAvailability.id == id).first()
        if not availability:
            session.close()
            return {"message": "Availability not found"}, 404

        session.close()
        return availability

    @doctor_required
    @ns.expect(availability_model)
    @ns.marshal_with(availability_model)
    def put(self, doctor_id, id):
        """Update availability (Doctor or Admin only)"""
        current_user = get_current_user()
        session = SessionLocal()
        doctor = (
            session.query(Doctor)
                .join(User)
                .filter(Doctor.id == doctor_id)
                .first()
        )
        if not doctor:
            session.close()
            return {"message": "Doctor not found"}, 404

        # Verify the doctor is updating their own availability
        if current_user.role != 'admin' and doctor.user_id != current_user.id:
            session.close()
            return {'message': 'Unauthorized'}, 403

        availability = session.query(DoctorAvailability).filter(DoctorAvailability.id == id).first()
        if not availability:
            session.close()
            return {"message": "Availability not found"}, 404

        data = request.json
        availability.day_of_week = data.get('day_of_week', availability.day_of_week)
        availability.start_time = data.get('start_time', availability.start_time)
        availability.end_time = data.get('end_time', availability.end_time)
        availability.is_available = data.get('is_available', availability.is_available)
        
        session.commit()
        session.close()
        return availability

    @doctor_required
    def delete(self, doctor_id, id):
        """Delete availability (Doctor or Admin only)"""
        current_user = get_current_user()
        session = SessionLocal()
        doctor = (
            session.query(Doctor)
                .join(User)
                .filter(Doctor.id == doctor_id)
                .first()
        )
        if not doctor:
            session.close()
            return {"message": "Doctor not found"}, 404

        # Verify the doctor is deleting their own availability
        if current_user.role != 'admin' and doctor.user_id != current_user.id:
            session.close()
            return {'message': 'Unauthorized'}, 403

        availability = session.query(DoctorAvailability).filter(DoctorAvailability.id == id).first()
        if not availability:
            session.close()
            return {"message": "Availability not found"}, 404

        session.delete(availability)
        session.commit()
        session.close()
        return '', 204

class DoctorAppointmentsAPI(Resource):
    @marshal_with(appointment_fields)
    def get(self, doctor_id):
        session = SessionLocal()
        doctor = (
            session.query(Doctor)
                .join(User)
                .filter(Doctor.id == doctor_id)
                .first()
        )
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
        doctor = (
            session.query(Doctor)
                .join(User)
                .filter(Doctor.id == doctor_id)
                .first()
        )
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
            doctor = session.query(Doctor).join(User).filter(Doctor.id == doctor_id).first()
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
            doctor = (
                session.query(Doctor)
                    .join(User)
                    .filter(Doctor.id == doctor_id)
                    .first()
            )
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


