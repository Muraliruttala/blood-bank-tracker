import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
from datetime import datetime, date, time

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file):
    """Save uploaded file and return filename"""
    if file and allowed_file(file.filename):
        # Generate unique filename
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{uuid.uuid4().hex}{ext}"
        
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        return unique_filename
    return None

def validate_blood_type(blood_type):
    """Validate blood type format"""
    valid_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    return blood_type in valid_types

def validate_mobile(mobile):
    """Basic mobile number validation"""
    # Remove any non-digit characters
    digits_only = ''.join(filter(str.isdigit, mobile))
    # Check if it's 10 digits (Indian format) or other valid formats
    return len(digits_only) >= 10 and len(digits_only) <= 15

def parse_date(date_string):
    """Parse date string to date object"""
    try:
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except ValueError:
        return None

def parse_time(time_string):
    """Parse time string to time object"""
    try:
        return datetime.strptime(time_string, '%H:%M').time()
    except ValueError:
        return None

def format_response(success=True, message="", data=None):
    """Standard API response format"""
    response = {
        'success': success,
        'message': message
    }
    if data is not None:
        response['data'] = data
    return response
