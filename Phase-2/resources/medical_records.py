from flask_restful import Resource, reqparse, fields, marshal_with
from sqlalchemy import desc
from models import MedicalRecord, Patient, Appointment
from db import SessionLocal
from sqlalchemy.exc import IntegrityError
from datetime import datetime

def get_dept_name(rec):
    return rec.department.name if rec.department else None

def validate_date(date_str):
    try:
        date = datetime.fromisoformat(date_str).date()
        if date > datetime.now().date():
            raise ValueError("Visit date cannot be in the future")
        return date
    except ValueError as e:
        raise ValueError(f"Invalid date format or {str(e)}")

medical_record_fields = {
    'id': fields.String,
    'patient_id': fields.String,
    'appointment_id': fields.String,
    'department_id': fields.String,
    'diagnosis': fields.String,
    'prescription': fields.String,
    'notes': fields.String,
    'visit_date': fields.DateTime,
    'date_created': fields.DateTime,
    'updated_at': fields.DateTime
}

parser = reqparse.RequestParser()
parser.add_argument("patient_id", required=True)
parser.add_argument("appointment_id")  # Optional
parser.add_argument("diagnosis", required=True)
parser.add_argument("prescription", required=True)
parser.add_argument("notes") # Optional
parser.add_argument("department_id")       # optional
parser.add_argument("visit_date",   required=True)  # "YYYY-MM-DD"

class MedicalRecordListAPI(Resource):
    @marshal_with(medical_record_fields)
    def get(self):
        session = SessionLocal()
        try:
            records = session.query(MedicalRecord).all()
            return records
        finally:
            session.close()

    @marshal_with(medical_record_fields)
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("patient_id", required=True)
        parser.add_argument("appointment_id", required=True)
        parser.add_argument("department_id", required=True)
        parser.add_argument("diagnosis", required=True)
        parser.add_argument("prescription", required=True)
        parser.add_argument("notes")
        args = parser.parse_args()

        session = SessionLocal()
        try:
            # Verify patient exists
            patient = session.query(Patient).get(args["patient_id"])
            if not patient:
                return {"message": "Patient not found"}, 404

            # Get last record to generate new ID
            last_record = session.query(MedicalRecord).order_by(MedicalRecord.id.desc()).first()
            new_id = f"M{(int(last_record.id[1:]) + 1) if last_record else 1:03}"

            record = MedicalRecord(
                id=new_id,
                patient_id=args["patient_id"],
                appointment_id=args["appointment_id"],
                department_id=args["department_id"],
                diagnosis=args["diagnosis"],
                prescription=args["prescription"],
                notes=args.get("notes"),
                visit_date=datetime.now().date(),
                date_created=datetime.now(),
                updated_at=datetime.now()
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return record, 201
        except IntegrityError:
            session.rollback()
            return {"message": "Database error occurred"}, 500
        finally:
            session.close()

class PatientMedicalRecordsAPI(Resource):
    @marshal_with(medical_record_fields)
    def get(self, patient_id):
        session = SessionLocal()
        try:
            # Verify patient exists
            patient = session.query(Patient).get(patient_id)
            if not patient:
                return {"message": "Patient not found"}, 404

            # Get all medical records for the patient
            records = session.query(MedicalRecord)\
                .filter(MedicalRecord.patient_id == patient_id)\
                .order_by(MedicalRecord.visit_date.desc())\
                .all()
            return records
        finally:
            session.close()

class MedicalRecordAPI(Resource):
    @marshal_with(medical_record_fields)
    def get(self, record_id):
        session = SessionLocal()
        try:
            record = session.query(MedicalRecord).get(record_id)
            if not record:
                return {"message": "Medical record not found"}, 404
            return record
        finally:
            session.close()

    @marshal_with(medical_record_fields)
    def put(self, record_id):
        parser = reqparse.RequestParser()
        parser.add_argument("diagnosis")
        parser.add_argument("prescription")
        parser.add_argument("notes")
        args = parser.parse_args()

        session = SessionLocal()
        try:
            record = session.query(MedicalRecord).get(record_id)
            if not record:
                return {"message": "Medical record not found"}, 404

            if args.get("diagnosis"):
                record.diagnosis = args["diagnosis"]
            if args.get("prescription"):
                record.prescription = args["prescription"]
            if args.get("notes"):
                record.notes = args["notes"]
            
            record.updated_at = datetime.now()
            session.commit()
            session.refresh(record)
            return record
        except IntegrityError:
            session.rollback()
            return {"message": "Database error occurred"}, 500
        finally:
            session.close()

    def delete(self, record_id):
        session = SessionLocal()
        record = session.query(MedicalRecord).get(record_id)
        if not record:
            session.close()
            return {"message": "Medical record not found"}, 404
        session.delete(record)
        session.commit()
        session.close()
        return {"message": f"Medical record {record_id} deleted"}, 200
