from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import (
    get_all_blood_requests, get_all_donations, update_request_status,
    get_blood_inventory, get_admin_statistics, search_requests
)
import logging

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin login"""
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('auth.login'))
        if session['user']['role'] != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with overview"""
    # Get statistics
    stats = get_admin_statistics()
    
    # Get recent requests
    recent_requests = get_all_blood_requests(limit=10)
    
    # Get blood inventory
    inventory = get_blood_inventory()
    
    return render_template('admin_dashboard.html', 
                         stats=stats,
                         recent_requests=recent_requests,
                         inventory=inventory)

@admin_bp.route('/requests')
@admin_required
def view_requests():
    """View all blood requests with filtering"""
    status_filter = request.args.get('status', '')
    blood_group_filter = request.args.get('blood_group', '')
    search_query = request.args.get('search', '')
    
    # Get filtered requests
    if search_query:
        requests = search_requests(search_query, status_filter, blood_group_filter)
    else:
        requests = get_all_blood_requests(status_filter, blood_group_filter)
    
    return render_template('admin_dashboard.html', 
                         show_requests=True,
                         requests=requests,
                         status_filter=status_filter,
                         blood_group_filter=blood_group_filter,
                         search_query=search_query)

@admin_bp.route('/fulfill-request/<int:request_id>')
@admin_required
def fulfill_request(request_id):
    """Mark a blood request as fulfilled"""
    success = update_request_status(request_id, 'fulfilled')
    
    if success:
        flash('Blood request marked as fulfilled!', 'success')
    else:
        flash('Failed to update request status', 'danger')
    
    return redirect(url_for('admin.view_requests'))

@admin_bp.route('/donations')
@admin_required
def view_donations():
    """View all donation schedules"""
    donations = get_all_donations()
    
    return render_template('admin_dashboard.html', 
                         show_donations=True,
                         donations=donations)

@admin_bp.route('/inventory')
@admin_required
def view_inventory():
    """View blood inventory management"""
    inventory = get_blood_inventory()
    
    return render_template('admin_dashboard.html', 
                         show_inventory=True,
                         inventory=inventory)
