#!/usr/bin/env python3
"""
Test script to verify DynamoDB connection and table operations
"""
import logging
from models import create_user, get_user_by_email, create_blood_request, create_donation_schedule
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_user_creation():
    """Test user creation and retrieval"""
    print("Testing user creation...")
    
    test_user = {
        'name': 'Test User',
        'email': 'test@example.com',
        'password_hash': 'test_hash',
        'role': 'user',
        'blood_group': 'O+',
        'mobile': '123-456-7890',
        'hospital': '',
        'admin_id': ''
    }
    
    # Create user
    user_id = create_user(test_user)
    print(f"Created user with ID: {user_id}")
    
    # Retrieve user
    retrieved_user = get_user_by_email('test@example.com')
    if retrieved_user:
        print(f"Successfully retrieved user: {retrieved_user['name']}")
        return retrieved_user['id']
    else:
        print("Failed to retrieve user")
        return None

def test_blood_request_creation(user_id):
    """Test blood request creation"""
    if not user_id:
        print("No user ID available for blood request test")
        return
        
    print("Testing blood request creation...")
    
    request_data = {
        'user_id': user_id,
        'hospital': 'Test Hospital',
        'blood_group': 'O+',
        'units': 2,
        'mobile': '123-456-7890',
        'status': 'pending'
    }
    
    request_id = create_blood_request(request_data)
    print(f"Created blood request with ID: {request_id}")

def test_donation_creation(user_id):
    """Test donation schedule creation"""
    if not user_id:
        print("No user ID available for donation test")
        return
        
    print("Testing donation creation...")
    
    donation_data = {
        'user_id': user_id,
        'hospital': 'Test Hospital',
        'blood_group': 'O+',
        'units': 1,
        'mobile': '123-456-7890',
        'status': 'scheduled'
    }
    
    donation_id = create_donation_schedule(donation_data)
    print(f"Created donation with ID: {donation_id}")

if __name__ == "__main__":
    print("Starting DynamoDB connection test...")
    
    # Test user operations
    user_id = test_user_creation()
    
    # Test blood request
    test_blood_request_creation(user_id)
    
    # Test donation
    test_donation_creation(user_id)
    
    print("DynamoDB test completed!")