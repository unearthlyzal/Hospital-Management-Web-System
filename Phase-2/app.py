from flask import Flask
from flask_restx import Api
from db import Base, engine
import models
from error_handlers import register_error_handlers
from api_docs import api
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize API documentation
api.init_app(app)

# Register error handlers
register_error_handlers(app)

# Import and register resources
from resources.users import ns as users_ns
from resources.doctors import ns as doctors_ns
from resources.patients import ns as patients_ns
from resources.appointments import ns as appointments_ns
from resources.medical_records import ns as medical_records_ns
from resources.departments import ns as departments_ns
from resources.schedules import ns as schedules_ns

api.add_namespace(users_ns)
api.add_namespace(doctors_ns)
api.add_namespace(patients_ns)
api.add_namespace(appointments_ns)
api.add_namespace(medical_records_ns)
api.add_namespace(departments_ns)
api.add_namespace(schedules_ns)

if __name__ == '__main__':
    app.run(debug=True)
