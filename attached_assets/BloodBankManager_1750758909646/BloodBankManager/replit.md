# Blood Bank Management System

## Overview

This is a Flask-based Blood Bank Management System API that facilitates blood donation and request management. The system supports both regular users and administrators, providing authentication, blood inventory management, and donation scheduling capabilities.

## System Architecture

### Backend Framework
- **Flask**: Python web framework for REST API development
- **Flask-SQLAlchemy**: ORM for database operations
- **Flask-JWT-Extended**: JWT-based authentication system
- **Flask-CORS**: Cross-origin resource sharing support
- **Gunicorn**: WSGI HTTP server for production deployment

### Database Layer
- **PostgreSQL**: Primary database (configured via DATABASE_URL environment variable)
- **SQLAlchemy ORM**: Database abstraction layer with declarative models
- Connection pooling with automatic reconnection handling

### Authentication & Authorization
- **JWT (JSON Web Tokens)**: Stateless authentication mechanism
- **Role-based access control**: Admin and User roles
- **Password hashing**: Werkzeug security for secure password storage
- **Token-based API access**: No session management required

## Key Components

### User Management
- **Dual login system**: Email for users, username for admins
- **Role differentiation**: Admin users can manage hospitals, regular users for blood requests
- **Profile management**: Blood group, contact information, hospital affiliation

### Blood Management System
- **Blood inventory tracking**: Stock levels by blood type
- **Request management**: Status tracking (pending, successful, rejected)
- **Donation scheduling**: Appointment system for blood donations
- **Blood type validation**: Ensures valid blood group formats (A+, B-, etc.)

### File Upload System
- **Secure file handling**: Upload directory with size restrictions (16MB max)
- **File type validation**: Support for documents and images
- **Unique filename generation**: UUID-based naming to prevent conflicts

### API Structure
- **RESTful endpoints**: Standard HTTP methods for CRUD operations
- **JSON responses**: Consistent response format with success/error handling
- **Health check endpoint**: System status monitoring
- **CORS enabled**: Frontend integration support

## Data Flow

### User Registration Flow
1. Client submits registration data (name, email/username, mobile, blood group, password)
2. Server validates input data (blood type, mobile format, required fields)
3. Password is hashed using Werkzeug security
4. User record created with appropriate role (admin/user)
5. JWT token generated and returned for immediate authentication

### Authentication Flow
1. User submits credentials (email/username + password)
2. Server validates credentials against hashed password
3. JWT token created with user identity and role claims
4. Token used for subsequent API requests via Authorization header

### Blood Request Flow
1. Authenticated user submits blood request
2. System validates blood type compatibility
3. Request stored with pending status
4. Admin users can approve/reject requests
5. Status updates reflected in user dashboard

## External Dependencies

### Python Packages
- **Flask ecosystem**: Core web framework and extensions
- **Database**: psycopg2-binary for PostgreSQL connectivity
- **Authentication**: PyJWT for token handling
- **Email validation**: email-validator for input validation
- **OAuth**: flask-dance and oauthlib for potential social login integration

### System Dependencies
- **PostgreSQL**: Database server
- **OpenSSL**: Secure communications
- **Gunicorn**: Production WSGI server

### Development Tools
- **Python 3.11**: Runtime environment
- **Nix**: Package management and environment isolation

## Deployment Strategy

### Production Configuration
- **Gunicorn**: WSGI server with auto-scaling deployment target
- **Environment variables**: Configuration via DATABASE_URL, JWT_SECRET_KEY
- **Proxy handling**: ProxyFix middleware for proper URL generation behind reverse proxies
- **Connection pooling**: Database connection management with health checks

### File Structure
- **Modular design**: Separate files for models, routes, authentication, utilities
- **Upload handling**: Dedicated directory for user file uploads
- **Template support**: HTML templates for API testing interface

### Security Considerations
- **Password hashing**: No plain-text password storage
- **JWT secret management**: Environment-based secret configuration
- **File upload restrictions**: Size limits and type validation
- **Role-based access**: Admin-only endpoints protected with decorators

## Recent Changes
- June 24, 2025: Complete Blood Bank Management System implementation
  - DynamoDB integration with 4 tables (Users, Requests, Inventory, Donations)
  - AWS S3 bucket setup for document storage
  - Role-based authentication system (admin/user)
  - Full REST API with all requested endpoints
  - CORS enabled for React frontend compatibility
  - Successfully tested registration, login, blood requests, and inventory management
  - Enhanced React frontend with comprehensive homepage and improved dashboards
  - Added Admin ID field requirement for admin registration
  - Implemented detailed inventory system with 10+ blood bank entries
  - Enhanced role-based UI with proper admin vs user dashboard differentiation

## User Preferences

Preferred communication style: Simple, everyday language.