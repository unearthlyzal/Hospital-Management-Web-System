from flask_restful import Resource, reqparse, fields, marshal_with
from sqlalchemy import desc
from models import MedicalRecord
from db import SessionLocal
from datetime import datetime

def get_dept_name(rec):
    return rec.department.name if rec.department else None

medical_record_fields = {
    'id': fields.String,
    'patient_id': fields.String,
    'appointment_id': fields.String,
    'diagnosis': fields.String,
    'prescription': fields.String,
    'notes': fields.String,
    'department_id': fields.String,
    'department': fields.String(attribute=get_dept_name),
    'visit_date':    fields.String,   # iso date
    'date_created': fields.DateTime, # (dt_format='iso8601')
    'updated_at':    fields.DateTime(dt_format='iso8601'),
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
        records = session.query(MedicalRecord).all()
        session.close()
        return records

    @marshal_with(medical_record_fields)
    def post(self):
        args = parser.parse_args()
        session = SessionLocal()

        last = session.query(MedicalRecord).order_by(MedicalRecord.id.desc()).first()
        if last:
            last_num = int(last.id[1:])
        else:
            last_num = 0
        new_id = f"M{last_num + 1:03}"

        new_record = MedicalRecord(
            id=new_id,
            patient_id=args['patient_id'],
            appointment_id=args.get('appointment_id'),
            diagnosis=args['diagnosis'],
            prescription=args['prescription'],
            notes=args.get('notes'),
            department_id=args.get("department_id"),
            visit_date=datetime.fromisoformat(args["visit_date"]).date()
        )

        session.add(new_record)
        session.commit()
        session.refresh(new_record)
        session.close()
        return new_record, 201

class PatientMedicalRecordsAPI(Resource):
    @marshal_with(medical_record_fields)
    def get(self, patient_id):
        session = SessionLocal()
        # Fetch only this patient’s records, most recent first
        records = (
            session.query(MedicalRecord)
                   .filter(MedicalRecord.patient_id == patient_id)
                   .order_by(desc(MedicalRecord.visit_date))
                   .all()
        )
        session.close()
        return records
