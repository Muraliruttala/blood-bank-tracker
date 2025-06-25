from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import app
from dynamodb_models import User, BloodRequest, BloodInventory, DonationSchedule, UserRole, RequestStatus
from auth import admin_required, create_user_token, get_current_user
from utils import validate_blood_type, validate_mobile, parse_date, parse_time, format_response
from s3_utils import upload_file_to_s3
from datetime import datetime

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify(format_response(message="Blood Bank API is running"))

# User Registration
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'mobile', 'blood_group', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify(format_response(
                    success=False, 
                    message=f"Field '{field}' is required"
                )), 400
        
        # Validate blood type
        if not validate_blood_type(data['blood_group']):
            return jsonify(format_response(
                success=False, 
                message="Invalid blood group"
            )), 400
        
        # Validate mobile
        if not validate_mobile(data['mobile']):
            return jsonify(format_response(
                success=False, 
                message="Invalid mobile number"
            )), 400
        
        # Determine if this is admin registration
        role = UserRole.ADMIN if data.get('role') == 'admin' else UserRole.USER
        
        # Check for existing user
        if role == UserRole.ADMIN:
            if not data.get('username'):
                return jsonify(format_response(
                    success=False, 
                    message="Username is required for admin registration"
                )), 400
            
            existing_user = User.get_by_username(data['username'])
            if existing_user:
                return jsonify(format_response(
                    success=False, 
                    message="Username already exists"
                )), 409
        else:
            if not data.get('email'):
                return jsonify(format_response(
                    success=False, 
                    message="Email is required for user registration"
                )), 400
            
            existing_user = User.get_by_email(data['email'])
            if existing_user:
                return jsonify(format_response(
                    success=False, 
                    message="Email already exists"
                )), 409
        
        # Create new user
        user = User(
            username=data.get('username') if role == UserRole.ADMIN else None,
            email=data.get('email') if role == UserRole.USER else None,
            name=data['name'],
            mobile=data['mobile'],
            blood_group=data['blood_group'],
            role=role,
            hospital=data.get('hospital')
        )
        user.set_password(data['password'])
        user.save()
        
        # Create token
        token = create_user_token(user)
        
        return jsonify(format_response(
            message="User registered successfully",
            data={
                'user': user.to_dict(),
                'token': token
            }
        )), 201
        
    except Exception as e:
        return jsonify(format_response(
            success=False, 
            message=f"Registration failed: {str(e)}"
        )), 500

# User Login
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data.get('password'):
            return jsonify(format_response(
                success=False, 
                message="Password is required"
            )), 400
        
        user = None
        
        # Admin login with username/ID
        if data.get('username'):
            user = User.get_by_username(data['username'])
            if user and user.role != UserRole.ADMIN:
                user = None
        
        # User login with email
        elif data.get('email'):
            user = User.get_by_email(data['email'])
            if user and user.role != UserRole.USER:
                user = None
        
        else:
            return jsonify(format_response(
                success=False, 
                message="Username (for admin) or email (for user) is required"
            )), 400
        
        if not user or not user.check_password(data['password']):
            return jsonify(format_response(
                success=False, 
                message="Invalid credentials"
            )), 401
        
        # Create token
        token = create_user_token(user)
        
        return jsonify(format_response(
            message="Login successful",
            data={
                'user': user.to_dict(),
                'token': token
            }
        ))
        
    except Exception as e:
        return jsonify(format_response(
            success=False, 
            message=f"Login failed: {str(e)}"
        )), 500

# Get current user profile
@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user = get_current_user()
        if not user:
            return jsonify(format_response(
                success=False, 
                message="User not found"
            )), 404
        
        return jsonify(format_response(
            message="Profile retrieved successfully",
            data=user.to_dict()
        ))
        
    except Exception as e:
        return jsonify(format_response(
            success=False, 
            message=f"Failed to get profile: {str(e)}"
        )), 500

# Blood Request Management
@app.route('/api/blood-requests', methods=['POST'])
@jwt_required()
def create_blood_request():
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        # Validate required fields
        required_fields = ['hospital', 'blood_type', 'units']
        for field in required_fields:
            if not data.get(field):
                return jsonify(format_response(
                    success=False, 
                    message=f"Field '{field}' is required"
                )), 400
        
        # Validate blood type
        if not validate_blood_type(data['blood_type']):
            return jsonify(format_response(
                success=False, 
                message="Invalid blood type"
            )), 400
        
        # Validate units
        try:
            units = int(data['units'])
            if units <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            return jsonify(format_response(
                success=False, 
                message="Units must be a positive integer"
            )), 400
        
        # Create blood request
        blood_request = BloodRequest(
            user_id=current_user_id,
            hospital=data['hospital'],
            blood_type=data['blood_type'],
            units=units,
            urgency=data.get('urgency', 'normal'),
            notes=data.get('notes')
        )
        
        blood_request.save()
        
        return jsonify(format_response(
            message="Blood request created successfully",
            data=blood_request.to_dict()
        )), 201
        
    except Exception as e:
        return jsonify(format_response(
            success=False, 
            message=f"Failed to create blood request: {str(e)}"
        )), 500

@app.route('/api/blood-requests', methods=['GET'])
@jwt_required()
def get_blood_requests():
    try:
        current_user_id = get_jwt_identity()
        user = User.get_by_id(current_user_id)
        
        if user.role == UserRole.ADMIN:
            # Admin can see all requests
            requests = BloodRequest.get_all()
        else:
            # Regular users can only see their own requests
            requests = BloodRequest.get_by_user(current_user_id)
        
        return jsonify(format_response(
            message="Blood requests retrieved successfully",
            data=[req.to_dict() for req in requests]
        ))
        
    except Exception as e:
        return jsonify(format_response(
            success=False, 
            message=f"Failed to get blood requests: {str(e)}"
        )), 500

@app.route('/api/blood-requests/<int:request_id>', methods=['PUT'])
@admin_required
def update_blood_request_status(request_id):
    try:
        data = request.get_json()
        
        if not data.get('status'):
            return jsonify(format_response(
                success=False, 
                message="Status is required"
            )), 400
        
        # Validate status
        if data['status'] not in [RequestStatus.PENDING, RequestStatus.SUCCESSFUL, RequestStatus.REJECTED]:
            return jsonify(format_response(
                success=False, 
                message="Invalid status value"
            )), 400
        
        blood_request = BloodRequest.get_by_id(request_id)
        if not blood_request:
            return jsonify(format_response(
                success=False, 
                message="Blood request not found"
            )), 404
        
        blood_request.status = data['status']
        blood_request.save()
        
        return jsonify(format_response(
            message="Blood request status updated successfully",
            data=blood_request.to_dict()
        ))
        
    except Exception as e:
        return jsonify(format_response(
            success=False, 
            message=f"Failed to update blood request: {str(e)}"
        )), 500

# Blood Inventory Management
@app.route('/api/inventory', methods=['GET'])
@jwt_required()
def get_inventory():
    try:
        hospital = request.args.get('hospital')
        blood_type = request.args.get('blood_type')
        
        if hospital and blood_type:
            inventory = [BloodInventory.get_by_hospital_and_type(hospital, blood_type)]
            inventory = [item for item in inventory if item is not None]
        elif hospital:
            inventory = BloodInventory.get_by_hospital(hospital)
        else:
            inventory = BloodInventory.get_all()
        
        return jsonify(format_response(
            message="Inventory retrieved successfully",
            data=[item.to_dict() for item in inventory]
        ))
        
    except Exception as e:
        return jsonify(format_response(
            success=False, 
            message=f"Failed to get inventory: {str(e)}"
        )), 500

@app.route('/api/inventory', methods=['PUT'])
@admin_required
def update_inventory():
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        # Validate required fields
        required_fields = ['hospital', 'blood_type', 'units_available']
        for field in required_fields:
            if field not in data:
                return jsonify(format_response(
                    success=False, 
                    message=f"Field '{field}' is required"
                )), 400
        
        # Validate blood type
        if not validate_blood_type(data['blood_type']):
            return jsonify(format_response(
                success=False, 
                message="Invalid blood type"
            )), 400
        
        # Validate units
        try:
            units = int(data['units_available'])
            if units < 0:
                raise ValueError()
        except (ValueError, TypeError):
            return jsonify(format_response(
                success=False, 
                message="Units available must be a non-negative integer"
            )), 400
        
        # Find or create inventory item
        inventory = BloodInventory.get_by_hospital_and_type(data['hospital'], data['blood_type'])
        
        if inventory:
            # Update existing
            inventory.units_available = units
            inventory.last_updated_by = current_user_id
            
            if data.get('expiry_date'):
                inventory.expiry_date = parse_date(data['expiry_date']).isoformat() if parse_date(data['expiry_date']) else None
        else:
            # Create new
            inventory = BloodInventory(
                hospital=data['hospital'],
                blood_type=data['blood_type'],
                units_available=units,
                last_updated_by=current_user_id,
                expiry_date=parse_date(data['expiry_date']).isoformat() if data.get('expiry_date') and parse_date(data['expiry_date']) else None
            )
        
        inventory.save()
        
        return jsonify(format_response(
            message="Inventory updated successfully",
            data=inventory.to_dict()
        ))
        
    except Exception as e:
        return jsonify(format_response(
            success=False, 
            message=f"Failed to update inventory: {str(e)}"
        )), 500

# Donation Scheduling
@app.route('/api/donations', methods=['POST'])
@jwt_required()
def schedule_donation():
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()
        
        # Validate required fields
        required_fields = ['donor_name', 'donation_date', 'donation_time', 'blood_type', 'contact_number', 'hospital']
        for field in required_fields:
            if not data.get(field):
                return jsonify(format_response(
                    success=False, 
                    message=f"Field '{field}' is required"
                )), 400
        
        # Validate blood type
        if not validate_blood_type(data['blood_type']):
            return jsonify(format_response(
                success=False, 
                message="Invalid blood type"
            )), 400
        
        # Validate mobile
        if not validate_mobile(data['contact_number']):
            return jsonify(format_response(
                success=False, 
                message="Invalid contact number"
            )), 400
        
        # Parse date and time
        donation_date = parse_date(data['donation_date'])
        donation_time = parse_time(data['donation_time'])
        
        if not donation_date:
            return jsonify(format_response(
                success=False, 
                message="Invalid donation date format (YYYY-MM-DD)"
            )), 400
        
        if not donation_time:
            return jsonify(format_response(
                success=False, 
                message="Invalid donation time format (HH:MM)"
            )), 400
        
        # Create donation schedule
        donation = DonationSchedule(
            donor_id=current_user_id,
            donor_name=data['donor_name'],
            donation_date=donation_date.isoformat(),
            donation_time=donation_time.isoformat(),
            blood_type=data['blood_type'],
            contact_number=data['contact_number'],
            hospital=data['hospital'],
            notes=data.get('notes')
        )
        
        donation.save()
        
        return jsonify(format_response(
            message="Donation scheduled successfully",
            data=donation.to_dict()
        )), 201
        
    except Exception as e:
        return jsonify(format_response(
            success=False, 
            message=f"Failed to schedule donation: {str(e)}"
        )), 500

@app.route('/api/donations', methods=['GET'])
@jwt_required()
def get_donations():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user.role == UserRole.ADMIN:
            # Admin can see all donations
            donations = DonationSchedule.query.order_by(DonationSchedule.donation_date.desc()).all()
        else:
            # Regular users can only see their own donations
            donations = DonationSchedule.query.filter_by(donor_id=current_user_id).order_by(DonationSchedule.donation_date.desc()).all()
        
        return jsonify(format_response(
            message="Donations retrieved successfully",
            data=[donation.to_dict() for donation in donations]
        ))
        
    except Exception as e:
        return jsonify(format_response(
            success=False, 
            message=f"Failed to get donations: {str(e)}"
        )), 500

@app.route('/api/donations/<int:donation_id>', methods=['PUT'])
@admin_required
def update_donation_status(donation_id):
    try:
        data = request.get_json()
        
        if not data.get('status'):
            return jsonify(format_response(
                success=False, 
                message="Status is required"
            )), 400
        
        donation = DonationSchedule.get_by_id(donation_id)
        if not donation:
            return jsonify(format_response(
                success=False, 
                message="Donation schedule not found"
            )), 404
        
        donation.status = data['status']
        
        if data.get('notes'):
            donation.notes = data['notes']
        
        donation.save()
        
        return jsonify(format_response(
            message="Donation status updated successfully",
            data=donation.to_dict()
        ))
        
    except Exception as e:
        return jsonify(format_response(
            success=False, 
            message=f"Failed to update donation: {str(e)}"
        )), 500

# Admin Dashboard Routes
@app.route('/api/admin/dashboard', methods=['GET'])
@admin_required
def admin_dashboard():
    try:
        # Get all data for statistics
        requests = BloodRequest.get_all()
        donations = DonationSchedule.get_all()
        inventory = BloodInventory.get_all()
        
        # Calculate statistics
        total_requests = len(requests)
        pending_requests = len([r for r in requests if r.status == RequestStatus.PENDING])
        total_donations = len(donations)
        scheduled_donations = len([d for d in donations if d.status == 'scheduled'])
        
        # Get recent requests (first 5)
        recent_requests = requests[:5]
        
        # Get recent donations
        recent_donations = DonationSchedule.query.order_by(DonationSchedule.created_at.desc()).limit(5).all()
        
        dashboard_data = {
            'statistics': {
                'total_requests': total_requests,
                'pending_requests': pending_requests,
                'total_donations': total_donations,
                'scheduled_donations': scheduled_donations,
                'total_users': total_users
            },
            'recent_requests': [req.to_dict() for req in recent_requests],
            'recent_donations': [donation.to_dict() for donation in recent_donations]
        }
        
        return jsonify(format_response(
            message="Dashboard data retrieved successfully",
            data=dashboard_data
        ))
        
    except Exception as e:
        return jsonify(format_response(
            success=False, 
            message=f"Failed to get dashboard data: {str(e)}"
        )), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify(format_response(
        success=False, 
        message="Endpoint not found"
    )), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify(format_response(
        success=False, 
        message="Internal server error"
    )), 500

@app.errorhandler(422)
def handle_unprocessable_entity(e):
    return jsonify(format_response(
        success=False, 
        message="Invalid JSON data"
    )), 422

# Health check for API
@app.route('/api/health')
def api_health_check():
    return jsonify(format_response(
        message="Blood Bank Management System API is running",
        data={
            "version": "1.0.0",
            "status": "healthy"
        }
    ))

# API testing route
@app.route('/test')
def api_test():
    from flask import render_template
    return render_template('api_test.html')

# Root route - serves React frontend
@app.route('/')
def index():
    """Serve React frontend"""
    try:
        return app.send_static_file('index.html')
    except:
        # Fallback if React build not available
        return jsonify(format_response(
            message="Blood Bank Management System API is running",
            data={
                "version": "1.0.0",
                "endpoints": {
                    "authentication": ["/api/register", "/api/login", "/api/profile"],
                    "blood_requests": ["/api/blood-requests"],
                    "donations": ["/api/donations"],
                    "inventory": ["/api/inventory"],
                    "admin": ["/api/admin/dashboard"],
                    "testing": ["/test"]
                }
            }
        ))

# Catch-all route for React Router (must be last)
@app.route('/<path:path>')
def catch_all(path):
    """Catch-all route to serve React frontend for any non-API routes"""
    # Don't interfere with API routes
    if path.startswith('api/'):
        return jsonify(format_response(
            success=False,
            message="API endpoint not found"
        )), 404
    
    try:
        return app.send_static_file('index.html')
    except:
        return jsonify(format_response(
            success=False,
            message="Frontend not available"
        )), 404
