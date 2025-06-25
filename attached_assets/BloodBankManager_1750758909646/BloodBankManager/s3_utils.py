import os
import uuid
from werkzeug.utils import secure_filename
from aws_config import get_s3_client
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_file_to_s3(file, bucket_name='bloodbank-documents'):
    """Upload file to S3 and return the key"""
    if not file or not allowed_file(file.filename):
        return None
    
    try:
        s3_client = get_s3_client()
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{uuid.uuid4().hex}{ext}"
        
        # Upload to S3
        s3_client.upload_fileobj(
            file,
            bucket_name,
            unique_filename,
            ExtraArgs={'ContentType': file.content_type}
        )
        
        logger.info(f"File uploaded to S3: {unique_filename}")
        return unique_filename
        
    except ClientError as e:
        logger.error(f"Error uploading file to S3: {e}")
        return None

def get_file_url(file_key, bucket_name='bloodbank-documents'):
    """Generate presigned URL for file access"""
    try:
        s3_client = get_s3_client()
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': file_key},
            ExpiresIn=3600  # 1 hour
        )
        return url
    except ClientError as e:
        logger.error(f"Error generating presigned URL: {e}")
        return None

def delete_file_from_s3(file_key, bucket_name='bloodbank-documents'):
    """Delete file from S3"""
    try:
        s3_client = get_s3_client()
        s3_client.delete_object(Bucket=bucket_name, Key=file_key)
        logger.info(f"File deleted from S3: {file_key}")
        return True
    except ClientError as e:
        logger.error(f"Error deleting file from S3: {e}")
        return False