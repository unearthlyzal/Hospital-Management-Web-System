from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Date, DateTime, Text
from sqlalchemy.orm import relationship
from db import Base
from datetime import datetime

# from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Boolean

class User(Base):
    __tablename__ = "users"

    id = Column(String(10), primary_key=True)  # We'll use U001, U002, etc.
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)  # Plain text for now; hash later
    email = Column(String(100), unique=True, nullable=False)
    role = Column(String(20))  # "Admin", "Doctor", "Patient"
    is_active = Column(Boolean, default=True)

    patients = relationship("Patient", back_populates="user")
    doctors  = relationship("Doctor", back_populates="user")
    admins   = relationship("Admin",   back_populates="user")

class Patient(Base):
    __tablename__ = "patients"

    id = Column(String(10), primary_key=True)
    user_id = Column(String(10), ForeignKey("users.id"))
    first_name = Column(String(50))
    last_name = Column(String(50))
    birth_date = Column(Date, nullable=True)
    gender     = Column(String(1), nullable=True)   # 'M' or 'F'
    address    = Column(String(200), nullable=True)
    email = Column(String(100), unique=True)
    phone = Column(String(20))

    user = relationship("User", back_populates="patients")
    appointments = relationship("Appointment", back_populates="patient")


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(String(10), primary_key=True)
    user_id     = Column(String(10), ForeignKey("users.id"))
    #name = Column(String(100))
    first_name    = Column(String(50), nullable=False)
    last_name     = Column(String(50), nullable=False)
    department_id= Column(String(10), ForeignKey("departments.id"))
     
    availability = Column(JSON)  # e.g., {"Monday": "9-5", "Tuesday": "9-1"}
    phone = Column(String(20))
    appointments = relationship("Appointment", back_populates="doctor")

    user         = relationship("User", back_populates="doctors")
    appointments = relationship("Appointment", back_populates="doctor")
    schedules    = relationship("Schedule", back_populates="doctor")
    department_obj = relationship("Department", back_populates="doctors")

class Admin(Base):
    __tablename__ = "admins"

    id = Column(String(10), primary_key=True)
    user_id = Column(String(10), ForeignKey("users.id"))
    user = relationship("User", back_populates="admins")

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(String(10), primary_key=True)
    doctor_id = Column(String(10), ForeignKey("doctors.id"))
    datetime = Column(DateTime)  # Start time of the slot
    duration = Column(Integer)  # Duration in minutes (e.g., 30, 60)
    is_available = Column(Boolean, default=True)

    # Relationships (one Schedule can have many Appointments)
    doctor = relationship("Doctor", back_populates="schedules")
    appointments = relationship("Appointment", back_populates="schedule")


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(String(10), primary_key=True)
    patient_id = Column(String(10), ForeignKey("patients.id"))
    doctor_id = Column(String(10), ForeignKey("doctors.id"))
    schedule_id = Column(String(10), ForeignKey("schedules.id"))  # Foreign key to Schedule
    status = Column(String(20))  # e.g., "Scheduled", "Cancelled"

    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    schedule = relationship("Schedule", back_populates="appointments")

from sqlalchemy import Text
from datetime import datetime
class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(String(10), primary_key=True)
    patient_id = Column(String(10), ForeignKey("patients.id"))
    appointment_id = Column(String(10), ForeignKey("appointments.id"), nullable=True)
    department_id   = Column(String(10), ForeignKey("departments.id"), nullable=True)
    diagnosis = Column(Text)
    prescription = Column(Text)
    notes = Column(Text, nullable=True)
    visit_date      = Column(Date, nullable=False)
    date_created = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    patient = relationship("Patient")
    appointment = relationship("Appointment")
    department = relationship("Department", back_populates="medical_records")

class Department(Base):
    __tablename__ = "departments"
    id          = Column(String(10), primary_key=True)
    name        = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    doctors     = relationship("Doctor", back_populates="department_obj")
    records     = relationship("MedicalRecord", back_populates="department")