from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import (
    create_blood_request, create_donation_schedule, 
    get_user_blood_requests, get_user_donations,
    get_user_statistics
)
import logging

user_bp = Blueprint('user', __name__)

def login_required(f):
    """Decorator to require login"""
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('auth.login'))
        if session['user']['role'] != 'user':
            flash('Access denied', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@user_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with statistics and recent activity"""
    user_id = session['user']['id']
    
    # Get user statistics
    stats = get_user_statistics(user_id)
    
    # Get recent requests and donations
    recent_requests = get_user_blood_requests(user_id, limit=5)
    recent_donations = get_user_donations(user_id, limit=5)
    
    return render_template('user_dashboard.html', 
                         stats=stats, 
                         recent_requests=recent_requests,
                         recent_donations=recent_donations)

@user_bp.route('/blood-request', methods=['GET', 'POST'])
@login_required
def blood_request():
    """Handle blood request form"""
    if request.method == 'POST':
        hospital = request.form.get('hospital', '').strip()
        blood_group = request.form.get('blood_group', '')
        units = request.form.get('units', '')
        mobile = request.form.get('mobile', '').strip()
        
        # Validation
        if not all([hospital, blood_group, units, mobile]):
            flash('All fields are required', 'danger')
            return render_template('blood_request.html')
        
        try:
            units = int(units)
            if units <= 0:
                raise ValueError("Units must be positive")
        except ValueError:
            flash('Please enter a valid number of units', 'danger')
            return render_template('blood_request.html')
        
        # Create blood request
        request_data = {
            'user_id': session['user']['id'],
            'hospital': hospital,
            'blood_group': blood_group,
            'units': units,
            'mobile': mobile,
            'status': 'pending'
        }
        
        request_id = create_blood_request(request_data)
        if request_id:
            flash('Blood request submitted successfully!', 'success')
            return redirect(url_for('user.dashboard'))
        else:
            flash('Failed to submit blood request. Please try again.', 'danger')
    
    return render_template('blood_request.html')

@user_bp.route('/donation-schedule', methods=['GET', 'POST'])
@login_required
def donation_schedule():
    """Handle donation scheduling form"""
    if request.method == 'POST':
        hospital = request.form.get('hospital', '').strip()
        blood_group = request.form.get('blood_group', '')
        units = request.form.get('units', '')
        mobile = request.form.get('mobile', '').strip()
        
        # Validation
        if not all([hospital, blood_group, units, mobile]):
            flash('All fields are required', 'danger')
            return render_template('donation_schedule.html')
        
        try:
            units = int(units)
            if units <= 0:
                raise ValueError("Units must be positive")
        except ValueError:
            flash('Please enter a valid number of units', 'danger')
            return render_template('donation_schedule.html')
        
        # Create donation schedule
        donation_data = {
            'user_id': session['user']['id'],
            'hospital': hospital,
            'blood_group': blood_group,
            'units': units,
            'mobile': mobile,
            'status': 'scheduled'
        }
        
        donation_id = create_donation_schedule(donation_data)
        if donation_id:
            flash('Donation scheduled successfully!', 'success')
            return redirect(url_for('user.dashboard'))
        else:
            flash('Failed to schedule donation. Please try again.', 'danger')
    
    return render_template('donation_schedule.html')

@user_bp.route('/history')
@login_required
def history():
    """View complete history of requests and donations"""
    user_id = session['user']['id']
    
    all_requests = get_user_blood_requests(user_id)
    all_donations = get_user_donations(user_id)
    
    return render_template('user_dashboard.html', 
                         show_history=True,
                         all_requests=all_requests,
                         all_donations=all_donations)
