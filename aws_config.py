import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import logging

# AWS Configuration
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')

def get_dynamodb_client():
    """Get DynamoDB client with proper configuration"""
    try:
        if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
            # Real AWS credentials provided
            client = boto3.client(
                'dynamodb',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=AWS_REGION
            )
            logging.info("Connected to AWS DynamoDB")
            return client
        else:
            # No credentials - return None to use mock data
            logging.warning("No AWS credentials found - using mock data store")
            return None
    except (NoCredentialsError, ClientError) as e:
        logging.error(f"AWS connection failed: {e}")
        return None

def get_dynamodb_resource():
    """Get DynamoDB resource with proper configuration"""
    try:
        if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
            # Real AWS credentials provided
            resource = boto3.resource(
                'dynamodb',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=AWS_REGION
            )
            logging.info("Connected to AWS DynamoDB Resource")
            return resource
        else:
            # No credentials - return None to use mock data
            logging.warning("No AWS credentials found - using mock data store")
            return None
    except (NoCredentialsError, ClientError) as e:
        logging.error(f"AWS DynamoDB Resource connection failed: {e}")
        return None

def create_tables_if_not_exist():
    """Create DynamoDB tables if they don't exist"""
    dynamodb = get_dynamodb_resource()
    if not dynamodb:
        return False
    
    try:
        # Users table
        try:
            users_table = dynamodb.Table(USERS_TABLE)
            users_table.load()
            logging.info(f"Table {USERS_TABLE} already exists")
        except dynamodb.meta.client.exceptions.ResourceNotFoundException:
            users_table = dynamodb.create_table(
                TableName=USERS_TABLE,
                KeySchema=[
                    {'AttributeName': 'id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'id', 'AttributeType': 'S'},
                    {'AttributeName': 'email', 'AttributeType': 'S'}
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'email-index',
                        'KeySchema': [
                            {'AttributeName': 'email', 'KeyType': 'HASH'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            users_table.wait_until_exists()
            logging.info(f"Created table {USERS_TABLE}")

        # Blood requests table
        try:
            requests_table = dynamodb.Table(REQUESTS_TABLE)
            requests_table.load()
            logging.info(f"Table {REQUESTS_TABLE} already exists")
        except dynamodb.meta.client.exceptions.ResourceNotFoundException:
            requests_table = dynamodb.create_table(
                TableName=REQUESTS_TABLE,
                KeySchema=[
                    {'AttributeName': 'id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'id', 'AttributeType': 'S'},
                    {'AttributeName': 'user_id', 'AttributeType': 'S'}
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'user_id-index',
                        'KeySchema': [
                            {'AttributeName': 'user_id', 'KeyType': 'HASH'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            requests_table.wait_until_exists()
            logging.info(f"Created table {REQUESTS_TABLE}")

        # Donations table
        try:
            donations_table = dynamodb.Table(DONATIONS_TABLE)
            donations_table.load()
            logging.info(f"Table {DONATIONS_TABLE} already exists")
        except dynamodb.meta.client.exceptions.ResourceNotFoundException:
            donations_table = dynamodb.create_table(
                TableName=DONATIONS_TABLE,
                KeySchema=[
                    {'AttributeName': 'id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'id', 'AttributeType': 'S'},
                    {'AttributeName': 'user_id', 'AttributeType': 'S'}
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'user_id-index',
                        'KeySchema': [
                            {'AttributeName': 'user_id', 'KeyType': 'HASH'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            donations_table.wait_until_exists()
            logging.info(f"Created table {DONATIONS_TABLE}")

        # Inventory table
        try:
            inventory_table = dynamodb.Table(INVENTORY_TABLE)
            inventory_table.load()
            logging.info(f"Table {INVENTORY_TABLE} already exists")
        except dynamodb.meta.client.exceptions.ResourceNotFoundException:
            inventory_table = dynamodb.create_table(
                TableName=INVENTORY_TABLE,
                KeySchema=[
                    {'AttributeName': 'id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'id', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            inventory_table.wait_until_exists()
            logging.info(f"Created table {INVENTORY_TABLE}")
            
        return True
    except Exception as e:
        logging.error(f"Error creating tables: {e}")
        return False

def get_s3_client():
    """Get S3 client with proper configuration"""
    try:
        if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
            # Real AWS credentials provided
            client = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=AWS_REGION
            )
            logging.info("Connected to AWS S3")
            return client
        else:
            # No credentials - return None
            logging.warning("No AWS credentials found - S3 functionality disabled")
            return None
    except (NoCredentialsError, ClientError) as e:
        logging.error(f"AWS S3 connection failed: {e}")
        return None

# Table names
USERS_TABLE = 'blood_bank_users'
REQUESTS_TABLE = 'blood_requests'
DONATIONS_TABLE = 'donations'
INVENTORY_TABLE = 'blood_inventory'

# S3 bucket for document uploads
S3_BUCKET = os.environ.get('S3_BUCKET_NAME', 'blood-bank-documents')
