from flask_restx import Api, Resource, fields

# Create API documentation instance
api = Api(
    title='Hospital Management System API',
    version='1.0',
    description='A comprehensive API for managing hospital operations',
    doc='/api/docs'
)

# Define namespaces
ns_auth = api.namespace('auth', description='Authentication operations')
ns_users = api.namespace('users', description='User operations')
ns_doctors = api.namespace('doctors', description='Doctor operations')
ns_patients = api.namespace('patients', description='Patient operations')
ns_appointments = api.namespace('appointments', description='Appointment operations')
ns_medical_records = api.namespace('medical-records', description='Medical record operations')
ns_departments = api.namespace('departments', description='Department operations')
ns_schedules = api.namespace('schedules', description='Schedule operations')

# Define models for documentation
login_model = api.model('Login', {
    'username': fields.String(required=True, description='User username'),
    'password': fields.String(required=True, description='User password')
})

user_model = api.model('User', {
    'id': fields.String(description='User ID'),
    'username': fields.String(required=True, description='Username'),
    'email': fields.String(required=True, description='Email address'),
    'role': fields.String(required=True, description='User role'),
    'is_active': fields.Boolean(description='Account status')
})

doctor_model = api.model('Doctor', {
    'id': fields.String(description='Doctor ID'),
    'first_name': fields.String(required=True, description='First name'),
    'last_name': fields.String(required=True, description='Last name'),
    'department_id': fields.String(required=True, description='Department ID'),
    'phone': fields.String(required=True, description='Contact number'),
    'availability': fields.Raw(description='Availability schedule')
})

patient_model = api.model('Patient', {
    'id': fields.String(description='Patient ID'),
    'first_name': fields.String(required=True, description='First name'),
    'last_name': fields.String(required=True, description='Last name'),
    'email': fields.String(required=True, description='Email address'),
    'phone': fields.String(required=True, description='Contact number'),
    'birth_date': fields.Date(description='Date of birth'),
    'gender': fields.String(description='Gender (M/F)'),
    'address': fields.String(description='Residential address')
})

appointment_model = api.model('Appointment', {
    'id': fields.String(description='Appointment ID'),
    'patient_id': fields.String(required=True, description='Patient ID'),
    'doctor_id': fields.String(required=True, description='Doctor ID'),
    'schedule_id': fields.String(required=True, description='Schedule ID'),
    'status': fields.String(description='Appointment status')
})

medical_record_model = api.model('MedicalRecord', {
    'id': fields.String(description='Record ID'),
    'patient_id': fields.String(required=True, description='Patient ID'),
    'appointment_id': fields.String(description='Appointment ID'),
    'department_id': fields.String(required=True, description='Department ID'),
    'diagnosis': fields.String(required=True, description='Diagnosis'),
    'prescription': fields.String(required=True, description='Prescription'),
    'notes': fields.String(description='Additional notes'),
    'visit_date': fields.DateTime(description='Visit date'),
    'date_created': fields.DateTime(description='Record creation date'),
    'updated_at': fields.DateTime(description='Last update date')
})

department_model = api.model('Department', {
    'id': fields.String(description='Department ID'),
    'name': fields.String(required=True, description='Department name'),
    'description': fields.String(description='Department description')
})

schedule_model = api.model('Schedule', {
    'id': fields.String(description='Schedule ID'),
    'doctor_id': fields.String(required=True, description='Doctor ID'),
    'datetime': fields.DateTime(required=True, description='Appointment datetime'),
    'duration': fields.Integer(required=True, description='Duration in minutes'),
    'is_available': fields.Boolean(description='Availability status')
})

# Response models
token_response = api.model('TokenResponse', {
    'token': fields.String(description='JWT token'),
    'user_id': fields.String(description='User ID'),
    'role': fields.String(description='User role')
})

error_response = api.model('ErrorResponse', {
    'message': fields.String(description='Error message'),
    'status': fields.String(description='Error status')
})

# Example documentation for an endpoint
@ns_auth.route('/login')
class Login(Resource):
    @api.doc('user_login')
    @api.expect(login_model)
    @api.response(200, 'Success', token_response)
    @api.response(401, 'Authentication failed', error_response)
    def post(self):
        """User login endpoint"""
        pass  # Implementation in users.py 