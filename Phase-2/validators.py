from datetime import datetime
import re
from error_handlers import ValidationError

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError('Invalid email format')
    return email

def validate_phone(phone):
    """Validate phone number format"""
    pattern = r'^\+?1?\d{9,15}$'
    if not re.match(pattern, phone):
        raise ValidationError('Invalid phone number format')
    return phone

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long')
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter')
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain at least one lowercase letter')
    if not re.search(r'\d', password):
        raise ValidationError('Password must contain at least one number')
    return password

def validate_date(date_str, allow_future=False, allow_past=True):
    """Validate date string format and value"""
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        today = datetime.now().date()
        
        if not allow_future and date > today:
            raise ValidationError('Date cannot be in the future')
        if not allow_past and date < today:
            raise ValidationError('Date cannot be in the past')
        return date
    except ValueError:
        raise ValidationError('Invalid date format. Use YYYY-MM-DD')

def validate_time(time_str):
    """Validate time string format"""
    try:
        datetime.strptime(time_str, '%H:%M')
        return time_str
    except ValueError:
        raise ValidationError('Invalid time format. Use HH:MM')

def validate_name(name):
    """Validate person name"""
    if not name or len(name) < 2:
        raise ValidationError('Name must be at least 2 characters long')
    if not re.match(r'^[a-zA-Z\s\'-]+$', name):
        raise ValidationError('Name contains invalid characters')
    return name

def validate_gender(gender):
    """Validate gender value"""
    valid_genders = ['M', 'F']
    if gender not in valid_genders:
        raise ValidationError('Invalid gender. Use M or F')
    return gender

def validate_role(role):
    """Validate user role"""
    valid_roles = ['Admin', 'Doctor', 'Patient']
    if role not in valid_roles:
        raise ValidationError('Invalid role')
    return role

def validate_appointment_status(status):
    """Validate appointment status"""
    valid_statuses = ['Scheduled', 'Completed', 'Cancelled', 'No-Show']
    if status not in valid_statuses:
        raise ValidationError('Invalid appointment status')
    return status

def validate_schedule_time(start_time, end_time):
    """Validate schedule time range"""
    try:
        start = datetime.strptime(start_time, '%H:%M').time()
        end = datetime.strptime(end_time, '%H:%M').time()
        if start >= end:
            raise ValidationError('End time must be after start time')
        return start_time, end_time
    except ValueError:
        raise ValidationError('Invalid time format. Use HH:MM')

def validate_user_data(data):
    """Validate user registration/update data"""
    errors = {}
    
    try:
        if 'email' in data:
            validate_email(data['email'])
    except ValidationError as e:
        errors['email'] = str(e)
        
    try:
        if 'password' in data:
            validate_password(data['password'])
    except ValidationError as e:
        errors['password'] = str(e)
        
    try:
        if 'role' in data:
            validate_role(data['role'])
    except ValidationError as e:
        errors['role'] = str(e)
        
    if errors:
        raise ValidationError(errors)
    
    return data 