import uuid
import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from aws_config import get_dynamodb_resource
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

class UserRole:
    ADMIN = "admin"
    USER = "user"

class RequestStatus:
    PENDING = "pending"
    SUCCESSFUL = "successful"
    REJECTED = "rejected"

class DynamoDBModel:
    """Base class for DynamoDB models"""
    
    @classmethod
    def get_table(cls):
        dynamodb = get_dynamodb_resource()
        return dynamodb.Table(cls.table_name)

class User(DynamoDBModel):
    table_name = 'BloodBank_Users'
    
    def __init__(self, user_id=None, username=None, email=None, name=None, 
                 mobile=None, blood_group=None, role=UserRole.USER, 
                 hospital=None, password_hash=None):
        self.user_id = user_id or str(uuid.uuid4())
        self.username = username
        self.email = email
        self.name = name
        self.mobile = mobile
        self.blood_group = blood_group
        self.role = role
        self.hospital = hospital
        self.password_hash = password_hash
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def save(self):
        table = self.get_table()
        self.updated_at = datetime.utcnow().isoformat()
        
        item = {
            'user_id': self.user_id,
            'name': self.name,
            'mobile': self.mobile,
            'blood_group': self.blood_group,
            'role': self.role,
            'password_hash': self.password_hash,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        if self.username:
            item['username'] = self.username
        if self.email:
            item['email'] = self.email
        if self.hospital:
            item['hospital'] = self.hospital
            
        table.put_item(Item=item)
        return self
    
    @classmethod
    def get_by_id(cls, user_id):
        table = cls.get_table()
        try:
            response = table.get_item(Key={'user_id': user_id})
            if 'Item' in response:
                return cls.from_dict(response['Item'])
        except ClientError as e:
            logger.error(f"Error getting user by ID: {e}")
        return None
    
    @classmethod
    def get_by_email(cls, email):
        table = cls.get_table()
        try:
            response = table.query(
                IndexName='email-index',
                KeyConditionExpression='email = :email',
                ExpressionAttributeValues={':email': email}
            )
            if response['Items']:
                return cls.from_dict(response['Items'][0])
        except ClientError as e:
            logger.error(f"Error getting user by email: {e}")
        return None
    
    @classmethod
    def get_by_username(cls, username):
        table = cls.get_table()
        try:
            response = table.query(
                IndexName='username-index',
                KeyConditionExpression='username = :username',
                ExpressionAttributeValues={':username': username}
            )
            if response['Items']:
                return cls.from_dict(response['Items'][0])
        except ClientError as e:
            logger.error(f"Error getting user by username: {e}")
        return None
    
    @classmethod
    def from_dict(cls, data):
        user = cls()
        user.user_id = data.get('user_id')
        user.username = data.get('username')
        user.email = data.get('email')
        user.name = data.get('name')
        user.mobile = data.get('mobile')
        user.blood_group = data.get('blood_group')
        user.role = data.get('role', UserRole.USER)
        user.hospital = data.get('hospital')
        user.password_hash = data.get('password_hash')
        user.created_at = data.get('created_at')
        user.updated_at = data.get('updated_at')
        return user
    
    def to_dict(self):
        return {
            'id': self.user_id,
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'mobile': self.mobile,
            'blood_group': self.blood_group,
            'role': self.role,
            'hospital': self.hospital,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class BloodRequest(DynamoDBModel):
    table_name = 'BloodBank_Requests'
    
    def __init__(self, request_id=None, user_id=None, hospital=None, 
                 blood_type=None, units=None, status=RequestStatus.PENDING,
                 urgency='normal', notes=None):
        self.request_id = request_id or str(uuid.uuid4())
        self.user_id = user_id
        self.hospital = hospital
        self.blood_type = blood_type
        self.units = units
        self.status = status
        self.urgency = urgency
        self.notes = notes
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
    
    def save(self):
        table = self.get_table()
        self.updated_at = datetime.utcnow().isoformat()
        
        item = {
            'request_id': self.request_id,
            'user_id': self.user_id,
            'hospital': self.hospital,
            'blood_type': self.blood_type,
            'units': self.units,
            'status': self.status,
            'urgency': self.urgency,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        if self.notes:
            item['notes'] = self.notes
            
        table.put_item(Item=item)
        return self
    
    @classmethod
    def get_by_id(cls, request_id):
        table = cls.get_table()
        try:
            response = table.get_item(Key={'request_id': request_id})
            if 'Item' in response:
                return cls.from_dict(response['Item'])
        except ClientError as e:
            logger.error(f"Error getting request by ID: {e}")
        return None
    
    @classmethod
    def get_by_user(cls, user_id):
        table = cls.get_table()
        try:
            response = table.query(
                IndexName='user-index',
                KeyConditionExpression='user_id = :user_id',
                ExpressionAttributeValues={':user_id': user_id}
            )
            return [cls.from_dict(item) for item in response['Items']]
        except ClientError as e:
            logger.error(f"Error getting requests by user: {e}")
        return []
    
    @classmethod
    def get_all(cls):
        table = cls.get_table()
        try:
            response = table.scan()
            return [cls.from_dict(item) for item in response['Items']]
        except ClientError as e:
            logger.error(f"Error getting all requests: {e}")
        return []
    
    @classmethod
    def from_dict(cls, data):
        request = cls()
        request.request_id = data.get('request_id')
        request.user_id = data.get('user_id')
        request.hospital = data.get('hospital')
        request.blood_type = data.get('blood_type')
        request.units = data.get('units')
        request.status = data.get('status', RequestStatus.PENDING)
        request.urgency = data.get('urgency', 'normal')
        request.notes = data.get('notes')
        request.created_at = data.get('created_at')
        request.updated_at = data.get('updated_at')
        return request
    
    def to_dict(self):
        user = User.get_by_id(self.user_id) if self.user_id else None
        return {
            'id': self.request_id,
            'user_id': self.user_id,
            'requester_name': user.name if user else None,
            'requester_mobile': user.mobile if user else None,
            'hospital': self.hospital,
            'blood_type': self.blood_type,
            'units': self.units,
            'status': self.status,
            'urgency': self.urgency,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class BloodInventory(DynamoDBModel):
    table_name = 'BloodBank_Inventory'
    
    def __init__(self, inventory_id=None, hospital=None, blood_type=None,
                 units_available=0, expiry_date=None, last_updated_by=None):
        self.inventory_id = inventory_id or f"{hospital}#{blood_type}"
        self.hospital = hospital
        self.blood_type = blood_type
        self.units_available = units_available
        self.expiry_date = expiry_date
        self.last_updated_by = last_updated_by
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
    
    def save(self):
        table = self.get_table()
        self.updated_at = datetime.utcnow().isoformat()
        
        item = {
            'inventory_id': self.inventory_id,
            'hospital': self.hospital,
            'blood_type': self.blood_type,
            'units_available': self.units_available,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        if self.expiry_date:
            item['expiry_date'] = self.expiry_date
        if self.last_updated_by:
            item['last_updated_by'] = self.last_updated_by
            
        table.put_item(Item=item)
        return self
    
    @classmethod
    def get_by_hospital_and_type(cls, hospital, blood_type):
        table = cls.get_table()
        inventory_id = f"{hospital}#{blood_type}"
        try:
            response = table.get_item(Key={'inventory_id': inventory_id})
            if 'Item' in response:
                return cls.from_dict(response['Item'])
        except ClientError as e:
            logger.error(f"Error getting inventory: {e}")
        return None
    
    @classmethod
    def get_by_hospital(cls, hospital):
        table = cls.get_table()
        try:
            response = table.query(
                IndexName='hospital-index',
                KeyConditionExpression='hospital = :hospital',
                ExpressionAttributeValues={':hospital': hospital}
            )
            return [cls.from_dict(item) for item in response['Items']]
        except ClientError as e:
            logger.error(f"Error getting inventory by hospital: {e}")
        return []
    
    @classmethod
    def get_all(cls):
        table = cls.get_table()
        try:
            response = table.scan()
            return [cls.from_dict(item) for item in response['Items']]
        except ClientError as e:
            logger.error(f"Error getting all inventory: {e}")
        return []
    
    @classmethod
    def from_dict(cls, data):
        inventory = cls()
        inventory.inventory_id = data.get('inventory_id')
        inventory.hospital = data.get('hospital')
        inventory.blood_type = data.get('blood_type')
        inventory.units_available = data.get('units_available', 0)
        inventory.expiry_date = data.get('expiry_date')
        inventory.last_updated_by = data.get('last_updated_by')
        inventory.created_at = data.get('created_at')
        inventory.updated_at = data.get('updated_at')
        return inventory
    
    def to_dict(self):
        return {
            'id': self.inventory_id,
            'hospital': self.hospital,
            'blood_type': self.blood_type,
            'units_available': self.units_available,
            'expiry_date': self.expiry_date,
            'last_updated_by': self.last_updated_by,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class DonationSchedule(DynamoDBModel):
    table_name = 'BloodBank_Donations'
    
    def __init__(self, donation_id=None, donor_id=None, donor_name=None,
                 donation_date=None, donation_time=None, blood_type=None,
                 contact_number=None, hospital=None, status='scheduled', notes=None):
        self.donation_id = donation_id or str(uuid.uuid4())
        self.donor_id = donor_id
        self.donor_name = donor_name
        self.donation_date = donation_date
        self.donation_time = donation_time
        self.blood_type = blood_type
        self.contact_number = contact_number
        self.hospital = hospital
        self.status = status
        self.notes = notes
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()
    
    def save(self):
        table = self.get_table()
        self.updated_at = datetime.utcnow().isoformat()
        
        item = {
            'donation_id': self.donation_id,
            'donor_id': self.donor_id,
            'donor_name': self.donor_name,
            'donation_date': self.donation_date,
            'donation_time': self.donation_time,
            'blood_type': self.blood_type,
            'contact_number': self.contact_number,
            'hospital': self.hospital,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        if self.notes:
            item['notes'] = self.notes
            
        table.put_item(Item=item)
        return self
    
    @classmethod
    def get_by_id(cls, donation_id):
        table = cls.get_table()
        try:
            response = table.get_item(Key={'donation_id': donation_id})
            if 'Item' in response:
                return cls.from_dict(response['Item'])
        except ClientError as e:
            logger.error(f"Error getting donation by ID: {e}")
        return None
    
    @classmethod
    def get_by_donor(cls, donor_id):
        table = cls.get_table()
        try:
            response = table.query(
                IndexName='donor-index',
                KeyConditionExpression='donor_id = :donor_id',
                ExpressionAttributeValues={':donor_id': donor_id}
            )
            return [cls.from_dict(item) for item in response['Items']]
        except ClientError as e:
            logger.error(f"Error getting donations by donor: {e}")
        return []
    
    @classmethod
    def get_all(cls):
        table = cls.get_table()
        try:
            response = table.scan()
            return [cls.from_dict(item) for item in response['Items']]
        except ClientError as e:
            logger.error(f"Error getting all donations: {e}")
        return []
    
    @classmethod
    def from_dict(cls, data):
        donation = cls()
        donation.donation_id = data.get('donation_id')
        donation.donor_id = data.get('donor_id')
        donation.donor_name = data.get('donor_name')
        donation.donation_date = data.get('donation_date')
        donation.donation_time = data.get('donation_time')
        donation.blood_type = data.get('blood_type')
        donation.contact_number = data.get('contact_number')
        donation.hospital = data.get('hospital')
        donation.status = data.get('status', 'scheduled')
        donation.notes = data.get('notes')
        donation.created_at = data.get('created_at')
        donation.updated_at = data.get('updated_at')
        return donation
    
    def to_dict(self):
        return {
            'id': self.donation_id,
            'donor_id': self.donor_id,
            'donor_name': self.donor_name,
            'donation_date': self.donation_date,
            'donation_time': self.donation_time,
            'blood_type': self.blood_type,
            'contact_number': self.contact_number,
            'hospital': self.hospital,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }