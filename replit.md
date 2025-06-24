# Blood Bank Management System

## Overview

The Blood Bank Management System is a full-stack web application built with Python Flask that facilitates blood donation and request management. The system supports two types of users: regular users who can request blood and schedule donations, and administrators who can manage requests and blood inventory across multiple hospitals.

## System Architecture

### Backend Architecture
- **Framework**: Python Flask with Gunicorn WSGI server for production deployment
- **Authentication**: Session-based authentication with role-based access control
- **Security**: Werkzeug password hashing for secure password storage
- **Database**: AWS DynamoDB with fallback to in-memory mock data store
- **File Storage**: AWS S3 for optional document/image uploads

### Frontend Architecture
- **UI Framework**: Bootstrap 5 for responsive design and components
- **JavaScript**: Vanilla JavaScript for client-side interactions
- **Template Engine**: Flask's Jinja2 for server-side rendering
- **Styling**: Custom CSS with Bootstrap integration

### Application Structure
```
├── app.py                 # Main Flask application
├── main.py               # Application entry point
├── auth.py               # Authentication blueprint
├── user_routes.py        # User dashboard and functionality
├── admin_routes.py       # Admin dashboard and management
├── models.py             # Data models and database operations
├── aws_config.py         # AWS configuration and clients
├── templates/            # HTML templates
├── static/               # CSS, JavaScript, and assets
└── pyproject.toml       # Python dependencies
```

## Key Components

### Authentication System
- **Registration**: Dual-role registration (User/Admin) with form validation
- **Login**: Email/password authentication with session management
- **Role-based Access**: Decorator-based route protection for users and admins
- **Admin Verification**: Special admin ID validation for admin registration

### User Management
- **User Dashboard**: Profile display, statistics, and recent activity
- **Blood Requests**: Form to request blood units with hospital specification
- **Donation Scheduling**: Calendar-based donation appointment system
- **Activity History**: Personal blood request and donation tracking

### Admin Management
- **Admin Dashboard**: System-wide statistics and oversight
- **Request Management**: View and update status of all blood requests
- **Inventory Management**: Blood bank inventory across 10 hospitals
- **User Oversight**: Monitor all user activities and donations

### Data Models
- **Users**: Profile information, credentials, and role assignments
- **Blood Requests**: Hospital, blood group, units, and status tracking
- **Donations**: Scheduled donations with appointment details
- **Inventory**: Blood bank stock levels across multiple hospitals

## Data Flow

1. **User Registration/Login** → Session creation → Role-based dashboard redirect
2. **Blood Request** → Form submission → Database storage → Admin notification
3. **Donation Schedule** → Appointment booking → Inventory update → Confirmation
4. **Admin Actions** → Request status updates → User notifications → Inventory management

## External Dependencies

### AWS Services
- **DynamoDB**: Primary database for user data, requests, and donations
- **S3**: Optional file storage for documents and images
- **Boto3**: AWS SDK for Python integration

### Python Packages
- **Flask**: Web framework and routing
- **Werkzeug**: Security utilities and password hashing
- **Gunicorn**: Production WSGI server
- **Boto3**: AWS service integration
- **Email-validator**: Email format validation

### Frontend Libraries
- **Bootstrap 5**: UI components and responsive design
- **Font Awesome**: Icon library for enhanced UX
- **jQuery**: DOM manipulation and AJAX requests

## Deployment Strategy

### Development Environment
- **Local Development**: Flask development server with debug mode
- **Port Configuration**: Application runs on port 5000
- **Hot Reload**: Automatic restart on code changes

### Production Environment
- **WSGI Server**: Gunicorn with worker processes
- **Scaling**: Autoscale deployment target for load handling
- **Proxy Configuration**: ProxyFix middleware for proper header handling

### Database Fallback
- **Primary**: AWS DynamoDB for production data storage
- **Fallback**: In-memory mock data store when AWS credentials unavailable
- **Migration**: Seamless transition between mock and production data

### Environment Variables
- **AWS_ACCESS_KEY_ID**: AWS access credentials
- **AWS_SECRET_ACCESS_KEY**: AWS secret credentials
- **AWS_REGION**: AWS service region (default: us-east-1)
- **SESSION_SECRET**: Flask session encryption key

## Changelog

```
Changelog:
- June 24, 2025. Initial setup
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```