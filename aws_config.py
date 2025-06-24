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
