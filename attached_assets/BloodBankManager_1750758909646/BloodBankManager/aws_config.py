import boto3
import os
from botocore.exceptions import ClientError
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# AWS Configuration
AWS_REGION = 'us-east-1'  # Default region

def get_aws_session():
    """Get AWS session with credentials"""
    return boto3.Session(
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name=AWS_REGION
    )

def get_dynamodb_client():
    """Get DynamoDB client"""
    session = get_aws_session()
    return session.client('dynamodb')

def get_dynamodb_resource():
    """Get DynamoDB resource"""
    session = get_aws_session()
    return session.resource('dynamodb')

def get_s3_client():
    """Get S3 client"""
    session = get_aws_session()
    return session.client('s3')

def create_dynamodb_tables():
    """Create DynamoDB tables if they don't exist"""
    dynamodb = get_dynamodb_resource()
    
    tables_config = [
        {
            'TableName': 'BloodBank_Users',
            'KeySchema': [
                {'AttributeName': 'user_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'email', 'AttributeType': 'S'},
                {'AttributeName': 'username', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'email-index',
                    'KeySchema': [{'AttributeName': 'email', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'},
                    'OnDemandThroughput': {
                        'MaxReadRequestUnits': 40000,
                        'MaxWriteRequestUnits': 40000
                    }
                },
                {
                    'IndexName': 'username-index',
                    'KeySchema': [{'AttributeName': 'username', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'},
                    'OnDemandThroughput': {
                        'MaxReadRequestUnits': 40000,
                        'MaxWriteRequestUnits': 40000
                    }
                }
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        },
        {
            'TableName': 'BloodBank_Requests',
            'KeySchema': [
                {'AttributeName': 'request_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'request_id', 'AttributeType': 'S'},
                {'AttributeName': 'user_id', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'user-index',
                    'KeySchema': [{'AttributeName': 'user_id', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'},
                    'OnDemandThroughput': {
                        'MaxReadRequestUnits': 40000,
                        'MaxWriteRequestUnits': 40000
                    }
                }
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        },
        {
            'TableName': 'BloodBank_Inventory',
            'KeySchema': [
                {'AttributeName': 'inventory_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'inventory_id', 'AttributeType': 'S'},
                {'AttributeName': 'hospital', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'hospital-index',
                    'KeySchema': [{'AttributeName': 'hospital', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'},
                    'OnDemandThroughput': {
                        'MaxReadRequestUnits': 40000,
                        'MaxWriteRequestUnits': 40000
                    }
                }
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        },
        {
            'TableName': 'BloodBank_Donations',
            'KeySchema': [
                {'AttributeName': 'donation_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'donation_id', 'AttributeType': 'S'},
                {'AttributeName': 'donor_id', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'donor-index',
                    'KeySchema': [{'AttributeName': 'donor_id', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'},
                    'OnDemandThroughput': {
                        'MaxReadRequestUnits': 40000,
                        'MaxWriteRequestUnits': 40000
                    }
                }
            ],
            'BillingMode': 'PAY_PER_REQUEST'
        }
    ]
    
    for table_config in tables_config:
        table_name = table_config['TableName']
        try:
            # Check if table exists
            table = dynamodb.Table(table_name)
            table.load()
            logger.info(f"Table {table_name} already exists")
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                # Create table
                logger.info(f"Creating table {table_name}")
                table = dynamodb.create_table(**table_config)
                table.wait_until_exists()
                logger.info(f"Table {table_name} created successfully")
            else:
                logger.error(f"Error checking table {table_name}: {e}")
                raise

def create_s3_bucket(bucket_name='bloodbank-documents'):
    """Create S3 bucket if it doesn't exist"""
    s3_client = get_s3_client()
    
    try:
        # Check if bucket exists
        s3_client.head_bucket(Bucket=bucket_name)
        logger.info(f"Bucket {bucket_name} already exists")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            # Create bucket
            try:
                if AWS_REGION == 'us-east-1':
                    s3_client.create_bucket(Bucket=bucket_name)
                else:
                    s3_client.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': AWS_REGION}
                    )
                logger.info(f"Bucket {bucket_name} created successfully")
            except ClientError as create_error:
                logger.error(f"Error creating bucket {bucket_name}: {create_error}")
                raise
        else:
            logger.error(f"Error checking bucket {bucket_name}: {e}")
            raise

def initialize_aws_resources():
    """Initialize all AWS resources"""
    try:
        create_dynamodb_tables()
        create_s3_bucket()
        logger.info("AWS resources initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing AWS resources: {e}")
        raise