# database_setup.py
from sqlalchemy import text
from db import Base, engine
from models import *

def reset_database():
    with engine.connect() as conn:
        # Disable foreign key constraints (SQL Server specific)
        conn.execute(text("EXEC sp_MSforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT ALL'"))
        
        # Drop tables in dependency order
        tables = [
            "medical_records",  # Depends on appointments
            "appointments",     # Depends on schedules/patients/doctors
            "schedules",        # Depends on doctors
            "patients",         # Depends on users
            "doctors",          # Depends on users
            "admins",           # Depends on users
            "users"             # Base table
        ]
        
        for table in tables:
            conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
        
        # Recreate tables
        Base.metadata.create_all(bind=conn)
        
        # Re-enable constraints
        conn.execute(text("EXEC sp_MSforeachtable 'ALTER TABLE ? WITH CHECK CHECK CONSTRAINT ALL'"))
    
    print("Database reset successfully!")

if __name__ == "__main__":
    reset_database()