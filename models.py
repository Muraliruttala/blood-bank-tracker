import uuid
from datetime import datetime
import logging
import boto3
import boto3.dynamodb.conditions
from aws_config import get_dynamodb_client, get_dynamodb_resource, create_tables_if_not_exist, USERS_TABLE, REQUESTS_TABLE, DONATIONS_TABLE, INVENTORY_TABLE
from botocore.exceptions import ClientError

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
    dynamodb = get_dynamodb_resource()
    
    if dynamodb:
        try:
            table = dynamodb.Table(USERS_TABLE)
            
            # First check if table exists
            table.load()
            
            response = table.query(
                IndexName='email-index',
                KeyConditionExpression=boto3.dynamodb.conditions.Key('email').eq(email)
            )
            
            if response['Items']:
                user = response['Items'][0]
                logging.info(f"Found user by email: {email} in DynamoDB")
                return user
            else:
                logging.info(f"No user found with email: {email} in DynamoDB")
                return None
                
        except Exception as e:
            logging.error(f"DynamoDB error getting user by email: {e}")
            # Fall back to mock data on error
            for user in mock_data['users'].values():
                if user['email'] == email:
                    logging.info(f"Found user by email: {email} in mock data")
                    return user
            return None
    else:
        # Use mock data
        for user in mock_data['users'].values():
            if user['email'] == email:
                logging.info(f"Found user by email: {email} in mock data")
                return user
    
    return None

def create_user(user_data):
    """Create a new user"""
    dynamodb = get_dynamodb_resource()
    
    if dynamodb:
        try:
            table = dynamodb.Table(USERS_TABLE)
            
            # Ensure table exists first
            table.load()
            
            # Generate unique user ID
            user_id = str(uuid.uuid4())
            user_data['id'] = user_id
            user_data['created_at'] = datetime.now().isoformat()
            
            # Put item in DynamoDB
            response = table.put_item(Item=user_data)
            
            logging.info(f"Successfully created user in DynamoDB: {user_id}, Response: {response}")
            return user_id
            
        except Exception as e:
            logging.error(f"DynamoDB error creating user: {e}")
            # Fall back to mock data on error
            user_id = id_counter['users']
            id_counter['users'] += 1
            
            user_data['id'] = str(user_id)
            user_data['created_at'] = datetime.now().isoformat()
            mock_data['users'][user_id] = user_data
            
            logging.info(f"Created user in mock data: {user_id}")
            return str(user_id)
    else:
        # Use mock data
        user_id = id_counter['users']
        id_counter['users'] += 1
        
        user_data['id'] = str(user_id)
        user_data['created_at'] = datetime.now().isoformat()
        mock_data['users'][user_id] = user_data
        
        logging.info(f"Created user in mock data: {user_id}")
        return str(user_id)

def create_blood_request(request_data):
    """Create a blood request"""
    dynamodb = get_dynamodb_resource()
    
    if dynamodb:
        try:
            table = dynamodb.Table(REQUESTS_TABLE)
            table.load()  # Check if table exists
            
            # Generate unique request ID
            request_id = str(uuid.uuid4())
            request_data['id'] = request_id
            request_data['created_at'] = datetime.now().isoformat()
            
            # Convert user_id to string for consistency
            request_data['user_id'] = str(request_data['user_id'])
            
            # Put item in DynamoDB
            response = table.put_item(Item=request_data)
            
            logging.info(f"Successfully created blood request in DynamoDB: {request_id}, Response: {response}")
            return request_id
            
        except Exception as e:
            logging.error(f"DynamoDB error creating blood request: {e}")
            # Fall back to mock data on error
            request_id = id_counter['requests']
            id_counter['requests'] += 1
            
            request_data['id'] = str(request_id)
            request_data['created_at'] = datetime.now().isoformat()
            mock_data['blood_requests'][request_id] = request_data
            
            logging.info(f"Created blood request in mock data: {request_id}")
            return str(request_id)
    else:
        # Use mock data
        request_id = id_counter['requests']
        id_counter['requests'] += 1
        
        request_data['id'] = str(request_id)
        request_data['created_at'] = datetime.now().isoformat()
        mock_data['blood_requests'][request_id] = request_data
        
        logging.info(f"Created blood request in mock data: {request_id}")
        return str(request_id)

def create_donation_schedule(donation_data):
    """Create a donation schedule"""
    dynamodb = get_dynamodb_resource()
    
    if dynamodb:
        try:
            table = dynamodb.Table(DONATIONS_TABLE)
            table.load()  # Check if table exists
            
            # Generate unique donation ID
            donation_id = str(uuid.uuid4())
            donation_data['id'] = donation_id
            donation_data['created_at'] = datetime.now().isoformat()
            
            # Convert user_id to string for consistency
            donation_data['user_id'] = str(donation_data['user_id'])
            
            # Put item in DynamoDB
            response = table.put_item(Item=donation_data)
            
            logging.info(f"Successfully created donation schedule in DynamoDB: {donation_id}, Response: {response}")
            return donation_id
            
        except Exception as e:
            logging.error(f"DynamoDB error creating donation: {e}")
            # Fall back to mock data on error
            donation_id = id_counter['donations']
            id_counter['donations'] += 1
            
            donation_data['id'] = str(donation_id)
            donation_data['created_at'] = datetime.now().isoformat()
            mock_data['donations'][donation_id] = donation_data
            
            logging.info(f"Created donation in mock data: {donation_id}")
            return str(donation_id)
    else:
        # Use mock data
        donation_id = id_counter['donations']
        id_counter['donations'] += 1
        
        donation_data['id'] = str(donation_id)
        donation_data['created_at'] = datetime.now().isoformat()
        mock_data['donations'][donation_id] = donation_data
        
        logging.info(f"Created donation in mock data: {donation_id}")
        return str(donation_id)

def get_user_blood_requests(user_id, limit=None):
    """Get blood requests for a user"""
    dynamodb = get_dynamodb_resource()
    user_id = str(user_id)  # Ensure user_id is string
    
    if dynamodb:
        try:
            table = dynamodb.Table(REQUESTS_TABLE)
            table.load()  # Check if table exists
            
            response = table.query(
                IndexName='user_id-index',
                KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(user_id),
                ScanIndexForward=False  # Sort by newest first
            )
            
            requests = response['Items']
            logging.info(f"Found {len(requests)} blood requests for user {user_id} in DynamoDB")
            
            if limit:
                requests = requests[:limit]
            
            return requests
            
        except Exception as e:
            logging.error(f"DynamoDB error getting user blood requests: {e}")
            # Fall back to mock data
            pass
    
    # Use mock data fallback
    requests = []
    for request in mock_data['blood_requests'].values():
        if str(request['user_id']) == user_id:
            requests.append(request)
    
    # Sort by creation date (newest first)
    requests.sort(key=lambda x: x['created_at'], reverse=True)
    
    if limit:
        requests = requests[:limit]
    
    logging.info(f"Found {len(requests)} blood requests for user {user_id} in mock data")
    return requests

def get_user_donations(user_id, limit=None):
    """Get donations for a user"""
    dynamodb = get_dynamodb_resource()
    user_id = str(user_id)  # Ensure user_id is string
    
    if dynamodb:
        try:
            table = dynamodb.Table(DONATIONS_TABLE)
            response = table.query(
                IndexName='user_id-index',
                KeyConditionExpression='user_id = :user_id',
                ExpressionAttributeValues={':user_id': user_id},
                ScanIndexForward=False  # Sort by newest first
            )
            
            donations = response['Items']
            logging.info(f"Found {len(donations)} donations for user {user_id}")
            
            if limit:
                donations = donations[:limit]
            
            return donations
            
        except ClientError as e:
            logging.error(f"DynamoDB error getting user donations: {e}")
            # Fall back to mock data
            pass
    
    # Use mock data fallback
    donations = []
    for donation in mock_data['donations'].values():
        if str(donation['user_id']) == user_id:
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
    dynamodb = get_dynamodb_resource()
    
    if dynamodb:
        try:
            table = dynamodb.Table(REQUESTS_TABLE)
            
            # Scan all requests (for admin view)
            response = table.scan()
            requests = response['Items']
            
            # Apply filters
            if status_filter:
                requests = [r for r in requests if r.get('status') == status_filter]
            
            if blood_group_filter:
                requests = [r for r in requests if r.get('blood_group') == blood_group_filter]
            
            # Add user names to requests
            users_table = dynamodb.Table(USERS_TABLE)
            for request in requests:
                try:
                    user_response = users_table.get_item(Key={'id': request['user_id']})
                    if 'Item' in user_response:
                        request['user_name'] = user_response['Item'].get('name', 'Unknown User')
                    else:
                        request['user_name'] = 'Unknown User'
                except:
                    request['user_name'] = 'Unknown User'
            
            # Sort by creation date (newest first)
            requests.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            if limit:
                requests = requests[:limit]
            
            logging.info(f"Retrieved {len(requests)} blood requests from DynamoDB")
            return requests
            
        except ClientError as e:
            logging.error(f"DynamoDB error getting all blood requests: {e}")
            # Fall back to mock data
            pass
    
    # Use mock data fallback
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
    dynamodb = get_dynamodb_resource()
    
    if dynamodb:
        try:
            table = dynamodb.Table(DONATIONS_TABLE)
            
            # Scan all donations (for admin view)
            response = table.scan()
            donations = response['Items']
            
            # Add user names to donations
            users_table = dynamodb.Table(USERS_TABLE)
            for donation in donations:
                try:
                    user_response = users_table.get_item(Key={'id': donation['user_id']})
                    if 'Item' in user_response:
                        donation['user_name'] = user_response['Item'].get('name', 'Unknown User')
                    else:
                        donation['user_name'] = 'Unknown User'
                except:
                    donation['user_name'] = 'Unknown User'
            
            # Sort by creation date (newest first)
            donations.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            logging.info(f"Retrieved {len(donations)} donations from DynamoDB")
            return donations
            
        except ClientError as e:
            logging.error(f"DynamoDB error getting all donations: {e}")
            # Fall back to mock data
            pass
    
    # Use mock data fallback
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
    dynamodb = get_dynamodb_resource()
    request_id = str(request_id)  # Ensure request_id is string
    
    if dynamodb:
        try:
            table = dynamodb.Table(REQUESTS_TABLE)
            
            response = table.update_item(
                Key={'id': request_id},
                UpdateExpression='SET #status = :status, updated_at = :updated_at',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': status,
                    ':updated_at': datetime.now().isoformat()
                },
                ReturnValues='UPDATED_NEW'
            )
            
            logging.info(f"Updated blood request {request_id} status to {status}")
            return True
            
        except ClientError as e:
            logging.error(f"DynamoDB error updating request status: {e}")
            # Fall back to mock data
            pass
    
    # Use mock data fallback
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
    dynamodb = get_dynamodb_resource()
    
    if dynamodb:
        try:
            requests_table = dynamodb.Table(REQUESTS_TABLE)
            donations_table = dynamodb.Table(DONATIONS_TABLE)
            
            # Get all requests and donations for statistics
            requests_response = requests_table.scan()
            donations_response = donations_table.scan()
            
            requests = requests_response['Items']
            donations = donations_response['Items']
            
            total_requests = len(requests)
            total_donations = len(donations)
            pending_requests = len([r for r in requests if r.get('status') == 'pending'])
            fulfilled_requests = len([r for r in requests if r.get('status') == 'fulfilled'])
            
            logging.info(f"Admin statistics from DynamoDB: {total_requests} requests, {total_donations} donations")
            
            return {
                'total_requests': total_requests,
                'total_donations': total_donations,
                'pending_requests': pending_requests,
                'fulfilled_requests': fulfilled_requests
            }
            
        except ClientError as e:
            logging.error(f"DynamoDB error getting admin statistics: {e}")
            # Fall back to mock data
            pass
    
    # Use mock data fallback
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
