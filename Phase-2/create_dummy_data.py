from models import Base, User, Patient, Doctor, Admin, Schedule, Appointment, MedicalRecord, Department
from db import engine, SessionLocal
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import random

# First, create all tables
Base.metadata.create_all(engine)

# Create a session
session = SessionLocal()

try:
    # Create departments
    departments = [
        Department(
            id=f"DEPT{i:03}",
            name=name,
            description=desc
        ) for i, (name, desc) in enumerate([
            ("Cardiology", "Heart and cardiovascular system specialists"),
            ("Neurology", "Brain, spine, and nervous system specialists"),
            ("Pediatrics", "Medical care for children and adolescents"),
            ("Orthopedics", "Bone and joint specialists"),
            ("Dermatology", "Skin care and treatment"),
        ], 1)
    ]
    session.add_all(departments)
    session.commit()

    # Create some users with different roles
    users = []
    # Admin users
    for i in range(1, 3):
        users.append(User(
            id=f"U{len(users)+1:03}",
            username=f"admin{i}",
            password=generate_password_hash(f"admin{i}pass"),
            email=f"admin{i}@hospital.com",
            role="Admin"
        ))
    
    # Doctor users
    doctor_specialties = {
        "DEPT001": ["John Smith", "Sarah Johnson"],
        "DEPT002": ["Michael Brown", "Emily Davis"],
        "DEPT003": ["David Wilson", "Lisa Anderson"],
        "DEPT004": ["Robert Taylor", "Jennifer Martin"],
        "DEPT005": ["William Lee", "Jessica White"]
    }

    for dept_id, names in doctor_specialties.items():
        for name in names:
            first_name, last_name = name.split()
            username = f"{first_name.lower()}{last_name.lower()}"
            users.append(User(
                id=f"U{len(users)+1:03}",
                username=username,
                password=generate_password_hash(f"{username}pass"),
                email=f"{username}@hospital.com",
                role="Doctor"
            ))

    # Patient users
    patient_names = [
        "James Wilson", "Mary Johnson", "Robert Brown", "Patricia Davis",
        "John Miller", "Linda Garcia", "Michael Martinez", "Barbara Robinson",
        "William Anderson", "Elizabeth Thomas", "David Jackson", "Margaret White",
        "Richard Harris", "Susan Martin", "Joseph Thompson", "Dorothy Lee"
    ]

    for name in patient_names:
        first_name, last_name = name.split()
        username = f"{first_name.lower()}{last_name.lower()}"
        users.append(User(
            id=f"U{len(users)+1:03}",
            username=username,
            password=generate_password_hash(f"{username}pass"),
            email=f"{username}@example.com",
            role="Patient"
        ))

    session.add_all(users)
    session.commit()

    # Create admins
    admins = [
        Admin(id=f"A{i:03}", user_id=f"U{i:03}")
        for i in range(1, 3)
    ]
    session.add_all(admins)
    session.commit()

    # Create doctors
    doctors = []
    doctor_user_start = 3  # After admin users
    for dept_id, names in doctor_specialties.items():
        for name in names:
            first_name, last_name = name.split()
            doctors.append(Doctor(
                id=f"D{len(doctors)+1:03}",
                user_id=f"U{doctor_user_start + len(doctors):03}",
                first_name=first_name,
                last_name=last_name,
                department_id=dept_id,
                availability={
                    "Monday": "9:00-17:00",
                    "Tuesday": "9:00-17:00",
                    "Wednesday": "9:00-17:00",
                    "Thursday": "9:00-17:00",
                    "Friday": "9:00-15:00"
                },
                phone=f"+1-555-{random.randint(1000000,9999999)}"
            ))
    session.add_all(doctors)
    session.commit()

    # Create patients
    patients = []
    patient_user_start = doctor_user_start + len(doctors)
    for i, name in enumerate(patient_names):
        first_name, last_name = name.split()
        patients.append(Patient(
            id=f"P{i+1:03}",
            user_id=f"U{patient_user_start + i:03}",
            first_name=first_name,
            last_name=last_name,
            birth_date=datetime.now() - timedelta(days=random.randint(6570, 29200)),  # 18-80 years
            gender=random.choice(['M', 'F']),
            address=f"{random.randint(100,999)} Main St, City",
            email=f"{first_name.lower()}{last_name.lower()}@example.com",
            phone=f"+1-555-{random.randint(1000000,9999999)}"
        ))
    session.add_all(patients)
    session.commit()

    # Create schedules (next 30 days)
    schedules = []
    for doctor in doctors:
        # Create slots for next 30 days
        for day in range(30):
            if day % 7 not in [5, 6]:  # Skip weekends
                base_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=day)
                # Create 8 slots per day
                for hour in range(9, 17):
                    schedules.append(Schedule(
                        id=f"SC{len(schedules)+1:03}",
                        doctor_id=doctor.id,
                        datetime=base_date.replace(hour=hour),
                        duration=60,
                        is_available=True
                    ))
    session.add_all(schedules)
    session.commit()

    # Create some appointments
    appointments = []
    statuses = ["Scheduled", "Completed", "Cancelled", "No-Show"]
    
    # Past appointments (completed or no-show)
    past_schedules = [s for s in schedules if s.datetime < datetime.now()]
    for i, schedule in enumerate(random.sample(past_schedules, min(20, len(past_schedules)))):
        appointments.append(Appointment(
            id=f"A{len(appointments)+1:03}",
            patient_id=random.choice(patients).id,
            doctor_id=schedule.doctor_id,
            schedule_id=schedule.id,
            status=random.choice(["Completed", "No-Show"])
        ))
        schedule.is_available = False

    # Future appointments (scheduled or cancelled)
    future_schedules = [s for s in schedules if s.datetime > datetime.now()]
    for i, schedule in enumerate(random.sample(future_schedules, min(15, len(future_schedules)))):
        appointments.append(Appointment(
            id=f"A{len(appointments)+1:03}",
            patient_id=random.choice(patients).id,
            doctor_id=schedule.doctor_id,
            schedule_id=schedule.id,
            status=random.choice(["Scheduled", "Cancelled"])
        ))
        schedule.is_available = False

    session.add_all(appointments)
    session.commit()

    # Create medical records for completed appointments
    medical_records = []
    completed_appointments = [a for a in appointments if a.status == "Completed"]
    
    diagnoses = [
        "Hypertension", "Type 2 Diabetes", "Upper Respiratory Infection",
        "Anxiety Disorder", "Osteoarthritis", "Migraine", "Allergic Rhinitis"
    ]
    
    prescriptions = [
        "Lisinopril 10mg daily", "Metformin 500mg twice daily",
        "Amoxicillin 500mg three times daily", "Sertraline 50mg daily",
        "Ibuprofen 400mg as needed", "Sumatriptan 50mg as needed"
    ]

    for appointment in completed_appointments:
        medical_records.append(MedicalRecord(
            id=f"M{len(medical_records)+1:03}",
            patient_id=appointment.patient_id,
            appointment_id=appointment.id,
            department_id=random.choice(departments).id,
            diagnosis=random.choice(diagnoses),
            prescription=random.choice(prescriptions),
            notes="Patient showing improvement with current treatment plan.",
            visit_date=appointment.schedule.datetime.date(),
            date_created=appointment.schedule.datetime,
            updated_at=appointment.schedule.datetime
        ))

    session.add_all(medical_records)
    session.commit()

    print("Successfully created dummy data!")
    print(f"Created:")
    print(f"- {len(departments)} departments")
    print(f"- {len(users)} users")
    print(f"- {len(doctors)} doctors")
    print(f"- {len(patients)} patients")
    print(f"- {len(schedules)} schedules")
    print(f"- {len(appointments)} appointments")
    print(f"- {len(medical_records)} medical records")

except Exception as e:
    print(f"An error occurred: {e}")
    session.rollback()
finally:
    session.close() 