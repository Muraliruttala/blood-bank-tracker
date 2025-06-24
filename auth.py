from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import get_user_by_email, create_user, validate_admin_id
import logging

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Email and password are required', 'danger')
            return render_template('login.html')
        
        user = get_user_by_email(email)
        if user and check_password_hash(user['password_hash'], password):
            # Store user info in session
            session['user'] = {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'role': user['role'],
                'blood_group': user['blood_group'],
                'mobile': user['mobile'],
                'hospital': user.get('hospital', ''),
                'admin_id': user.get('admin_id', '')
            }
            
            # Redirect based on role
            if user['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('user.dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', '')
        blood_group = request.form.get('blood_group', '')
        mobile = request.form.get('mobile', '').strip()
        hospital = request.form.get('hospital', '').strip()
        admin_id = request.form.get('admin_id', '').strip()
        
        # Validation
        if not all([name, email, password, confirm_password, role, blood_group, mobile]):
            flash('All fields are required', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'danger')
            return render_template('register.html')
        
        # Check if admin fields are provided for admin role
        if role == 'admin' and (not hospital or not admin_id):
            flash('Hospital and Admin ID are required for admin registration', 'danger')
            return render_template('register.html')
        
        # Check if admin ID is valid (for admin role)
        if role == 'admin' and not validate_admin_id(admin_id):
            flash('Invalid Admin ID', 'danger')
            return render_template('register.html')
        
        # Check if user already exists
        if get_user_by_email(email):
            flash('User with this email already exists', 'danger')
            return render_template('register.html')
        
        # Create user
        user_data = {
            'name': name,
            'email': email,
            'password_hash': generate_password_hash(password),
            'role': role,
            'blood_group': blood_group,
            'mobile': mobile,
            'hospital': hospital if role == 'admin' else '',
            'admin_id': admin_id if role == 'admin' else ''
        }
        
        user_id = create_user(user_data)
        if user_id:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Registration failed. Please try again.', 'danger')
    
    return render_template('register.html')
