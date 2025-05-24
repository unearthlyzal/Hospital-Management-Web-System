from sqlalchemy import or_
from models import Doctor, Patient, Appointment, MedicalRecord, Department
from db import SessionLocal

def search_doctors(query, department_id=None, limit=10):
    """Search doctors by name or department"""
    session = SessionLocal()
    try:
        search = f"%{query}%"
        doctors_query = session.query(Doctor).filter(
            or_(
                Doctor.first_name.ilike(search),
                Doctor.last_name.ilike(search)
            )
        )
        
        if department_id:
            doctors_query = doctors_query.filter(Doctor.department_id == department_id)
        
        return doctors_query.limit(limit).all()
    finally:
        session.close()

def search_patients(query, limit=10):
    """Search patients by name or email"""
    session = SessionLocal()
    try:
        search = f"%{query}%"
        return session.query(Patient).filter(
            or_(
                Patient.first_name.ilike(search),
                Patient.last_name.ilike(search),
                Patient.email.ilike(search)
            )
        ).limit(limit).all()
    finally:
        session.close()

def search_appointments(doctor_id=None, patient_id=None, status=None, start_date=None, end_date=None, limit=10):
    """Search appointments with various filters"""
    session = SessionLocal()
    try:
        query = session.query(Appointment)
        
        if doctor_id:
            query = query.filter(Appointment.doctor_id == doctor_id)
        if patient_id:
            query = query.filter(Appointment.patient_id == patient_id)
        if status:
            query = query.filter(Appointment.status == status)
        if start_date:
            query = query.filter(Appointment.schedule.has(datetime >= start_date))
        if end_date:
            query = query.filter(Appointment.schedule.has(datetime <= end_date))
        
        return query.limit(limit).all()
    finally:
        session.close()

def search_medical_records(patient_id=None, department_id=None, start_date=None, end_date=None, limit=10):
    """Search medical records with various filters"""
    session = SessionLocal()
    try:
        query = session.query(MedicalRecord)
        
        if patient_id:
            query = query.filter(MedicalRecord.patient_id == patient_id)
        if department_id:
            query = query.filter(MedicalRecord.department_id == department_id)
        if start_date:
            query = query.filter(MedicalRecord.visit_date >= start_date)
        if end_date:
            query = query.filter(MedicalRecord.visit_date <= end_date)
        
        return query.order_by(MedicalRecord.visit_date.desc()).limit(limit).all()
    finally:
        session.close()

def search_departments(query, limit=10):
    """Search departments by name"""
    session = SessionLocal()
    try:
        search = f"%{query}%"
        return session.query(Department).filter(
            Department.name.ilike(search)
        ).limit(limit).all()
    finally:
        session.close() 