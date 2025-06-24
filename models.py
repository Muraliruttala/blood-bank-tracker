import uuid
from datetime import datetime
import logging
from aws_config import get_dynamodb_client

# Mock data store when AWS is not available
mock_data = {
    'users': {},
    'blood_requests': {},
    'donations': {},
    'inventory': {}
}

# Counter for generating IDs in mock mode
id_counter = {'users': 1, 'requests': 1, 'donations': 1, 'inventory': 1}

# Initialize blood inventory data
def initialize_inventory():
    """Initialize blood inventory with 10 blood banks"""
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    hospitals = [
        'City General Hospital',
        'Metropolitan Medical Center',
        'St. Mary\'s Hospital',
        'Regional Blood Bank',
        'University Hospital',
        'Central Blood Center',
        'Community Health Hospital',
        'Emergency Medical Center',
        'District Hospital',
        'Primary Care Blood Bank'
    ]
    
    if not mock_data['inventory']:
        for i, hospital in enumerate(hospitals, 1):
            for bg in blood_groups:
                inventory_id = f"inv_{i}_{bg.replace('+', 'pos').replace('-', 'neg')}"
                mock_data['inventory'][inventory_id] = {
                    'id': inventory_id,
                    'hospital': hospital,
                    'blood_group': bg,
                    'units_available': 0,  # Start with 0 - real data will come from donations
                    'last_updated': datetime.now().isoformat()
                }

# Initialize inventory on module load
initialize_inventory()

# Valid admin IDs for registration
VALID_ADMIN_IDS = [
    'ADMIN001', 'ADMIN002', 'ADMIN003', 'ADMIN004', 'ADMIN005',
    'ADMIN006', 'ADMIN007', 'ADMIN008', 'ADMIN009', 'ADMIN010'
]

def validate_admin_id(admin_id):
    """Validate admin ID"""
    return admin_id in VALID_ADMIN_IDS

def get_user_by_email(email):
    """Get user by email"""
    dynamodb = get_dynamodb_client()
    
    if dynamodb:
        # Use real DynamoDB
        try:
            # Real DynamoDB implementation would go here
            pass
        except Exception as e:
            logging.error(f"DynamoDB error: {e}")
            return None
    else:
        # Use mock data
        for user in mock_data['users'].values():
            if user['email'] == email:
                return user
    
    return None

def create_user(user_data):
    """Create a new user"""
    dynamodb = get_dynamodb_client()
    
    if dynamodb:
        # Use real DynamoDB
        try:
            # Real DynamoDB implementation would go here
            pass
        except Exception as e:
            logging.error(f"DynamoDB error: {e}")
            return None
    else:
        # Use mock data
        user_id = id_counter['users']
        id_counter['users'] += 1
        
        user_data['id'] = user_id
        user_data['created_at'] = datetime.now().isoformat()
        mock_data['users'][user_id] = user_data
        
        return user_id

def create_blood_request(request_data):
    """Create a blood request"""
    dynamodb = get_dynamodb_client()
    
    if dynamodb:
        # Use real DynamoDB
        try:
            # Real DynamoDB implementation would go here
            pass
        except Exception as e:
            logging.error(f"DynamoDB error: {e}")
            return None
    else:
        # Use mock data
        request_id = id_counter['requests']
        id_counter['requests'] += 1
        
        request_data['id'] = request_id
        request_data['created_at'] = datetime.now().isoformat()
        mock_data['blood_requests'][request_id] = request_data
        
        return request_id

def create_donation_schedule(donation_data):
    """Create a donation schedule"""
    dynamodb = get_dynamodb_client()
    
    if dynamodb:
        # Use real DynamoDB
        try:
            # Real DynamoDB implementation would go here
            pass
        except Exception as e:
            logging.error(f"DynamoDB error: {e}")
            return None
    else:
        # Use mock data
        donation_id = id_counter['donations']
        id_counter['donations'] += 1
        
        donation_data['id'] = donation_id
        donation_data['created_at'] = datetime.now().isoformat()
        mock_data['donations'][donation_id] = donation_data
        
        return donation_id

def get_user_blood_requests(user_id, limit=None):
    """Get blood requests for a user"""
    requests = []
    
    for request in mock_data['blood_requests'].values():
        if request['user_id'] == user_id:
            requests.append(request)
    
    # Sort by creation date (newest first)
    requests.sort(key=lambda x: x['created_at'], reverse=True)
    
    if limit:
        requests = requests[:limit]
    
    return requests

def get_user_donations(user_id, limit=None):
    """Get donations for a user"""
    donations = []
    
    for donation in mock_data['donations'].values():
        if donation['user_id'] == user_id:
            donations.append(donation)
    
    # Sort by creation date (newest first)
    donations.sort(key=lambda x: x['created_at'], reverse=True)
    
    if limit:
        donations = donations[:limit]
    
    return donations

def get_user_statistics(user_id):
    """Get statistics for a user"""
    requests = get_user_blood_requests(user_id)
    donations = get_user_donations(user_id)
    
    pending_requests = len([r for r in requests if r['status'] == 'pending'])
    
    return {
        'total_requests': len(requests),
        'total_donations': len(donations),
        'pending_requests': pending_requests
    }

def get_all_blood_requests(status_filter=None, blood_group_filter=None, limit=None):
    """Get all blood requests with optional filtering"""
    requests = list(mock_data['blood_requests'].values())
    
    # Apply filters
    if status_filter:
        requests = [r for r in requests if r['status'] == status_filter]
    
    if blood_group_filter:
        requests = [r for r in requests if r['blood_group'] == blood_group_filter]
    
    # Add user names to requests
    for request in requests:
        user = mock_data['users'].get(request['user_id'], {})
        request['user_name'] = user.get('name', 'Unknown User')
    
    # Sort by creation date (newest first)
    requests.sort(key=lambda x: x['created_at'], reverse=True)
    
    if limit:
        requests = requests[:limit]
    
    return requests

def get_all_donations():
    """Get all donation schedules"""
    donations = list(mock_data['donations'].values())
    
    # Add user names to donations
    for donation in donations:
        user = mock_data['users'].get(donation['user_id'], {})
        donation['user_name'] = user.get('name', 'Unknown User')
    
    # Sort by creation date (newest first)
    donations.sort(key=lambda x: x['created_at'], reverse=True)
    
    return donations

def update_request_status(request_id, status):
    """Update the status of a blood request"""
    if request_id in mock_data['blood_requests']:
        mock_data['blood_requests'][request_id]['status'] = status
        mock_data['blood_requests'][request_id]['updated_at'] = datetime.now().isoformat()
        return True
    return False

def get_blood_inventory():
    """Get blood inventory from all blood banks"""
    return list(mock_data['inventory'].values())

def get_admin_statistics():
    """Get statistics for admin dashboard"""
    total_requests = len(mock_data['blood_requests'])
    total_donations = len(mock_data['donations'])
    pending_requests = len([r for r in mock_data['blood_requests'].values() if r['status'] == 'pending'])
    fulfilled_requests = len([r for r in mock_data['blood_requests'].values() if r['status'] == 'fulfilled'])
    
    return {
        'total_requests': total_requests,
        'total_donations': total_donations,
        'pending_requests': pending_requests,
        'fulfilled_requests': fulfilled_requests
    }

def search_requests(query, status_filter=None, blood_group_filter=None):
    """Search blood requests by user name or hospital"""
    all_requests = get_all_blood_requests(status_filter, blood_group_filter)
    
    # Filter by search query
    filtered_requests = []
    query_lower = query.lower()
    
    for request in all_requests:
        if (query_lower in request.get('user_name', '').lower() or 
            query_lower in request.get('hospital', '').lower()):
            filtered_requests.append(request)
    
    return filtered_requests
