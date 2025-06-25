import os
import logging
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from werkzeug.middleware.proxy_fix import ProxyFix
from aws_config import initialize_aws_resources

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize extensions
jwt = JWTManager()

def create_app():
    # Create Flask app with static folder for React build
    app = Flask(__name__, static_folder='build', static_url_path='/')
    
    # Configuration
    app.secret_key = os.environ.get("SESSION_SECRET", "blood-bank-secret-key")
    app.config['JWT_SECRET_KEY'] = os.environ.get("JWT_SECRET_KEY", "jwt-secret-key")
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # Tokens don't expire for simplicity
    
    # File upload configuration
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['S3_BUCKET'] = 'bloodbank-documents'
    
    # Initialize extensions
    jwt.init_app(app)
    CORS(app, origins=["*"], supports_credentials=True)
    
    # Proxy fix for proper URL generation
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize AWS resources
    try:
        initialize_aws_resources()
        logging.info("AWS resources initialized")
    except Exception as e:
        logging.error(f"Failed to initialize AWS resources: {e}")
    
    return app

# Create app instance
app = create_app()

# Register routes after app creation
with app.app_context():
    import routes  # noqa: F401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
