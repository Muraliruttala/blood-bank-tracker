from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"

class RequestStatus(Enum):
    PENDING = "pending"
    SUCCESSFUL = "successful"
    REJECTED = "rejected"

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    # Admin uses ID (username), Users use email
    username = db.Column(db.String(100), unique=True, nullable=True)  # For admin login
    email = db.Column(db.String(120), unique=True, nullable=True)     # For user login
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)  # A+, B+, O-, etc.
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.USER)
    hospital = db.Column(db.String(200), nullable=True)  # For admin users
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    blood_requests = db.relationship('BloodRequest', backref='requester', lazy=True)
    donations = db.relationship('DonationSchedule', backref='donor', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'mobile': self.mobile,
            'blood_group': self.blood_group,
            'role': self.role.value,
            'hospital': self.hospital,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class BloodRequest(db.Model):
    __tablename__ = 'blood_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    hospital = db.Column(db.String(200), nullable=False)
    blood_type = db.Column(db.String(5), nullable=False)  # A+, B+, O-, etc.
    units = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(RequestStatus), nullable=False, default=RequestStatus.PENDING)
    urgency = db.Column(db.String(20), nullable=False, default='normal')  # urgent, normal
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'requester_name': self.requester.name if self.requester else None,
            'requester_mobile': self.requester.mobile if self.requester else None,
            'hospital': self.hospital,
            'blood_type': self.blood_type,
            'units': self.units,
            'status': self.status.value,
            'urgency': self.urgency,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class BloodInventory(db.Model):
    __tablename__ = 'blood_inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    hospital = db.Column(db.String(200), nullable=False)
    blood_type = db.Column(db.String(5), nullable=False)
    units_available = db.Column(db.Integer, nullable=False, default=0)
    expiry_date = db.Column(db.Date, nullable=True)
    last_updated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Composite unique constraint
    __table_args__ = (db.UniqueConstraint('hospital', 'blood_type', name='_hospital_blood_type_uc'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'hospital': self.hospital,
            'blood_type': self.blood_type,
            'units_available': self.units_available,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'last_updated_by': self.last_updated_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class DonationSchedule(db.Model):
    __tablename__ = 'donation_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    donor_name = db.Column(db.String(100), nullable=False)  # For non-registered donors
    donation_date = db.Column(db.Date, nullable=False)
    donation_time = db.Column(db.Time, nullable=False)
    blood_type = db.Column(db.String(5), nullable=False)
    contact_number = db.Column(db.String(15), nullable=False)
    hospital = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='scheduled')  # scheduled, completed, cancelled
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'donor_id': self.donor_id,
            'donor_name': self.donor_name,
            'donation_date': self.donation_date.isoformat() if self.donation_date else None,
            'donation_time': self.donation_time.isoformat() if self.donation_time else None,
            'blood_type': self.blood_type,
            'contact_number': self.contact_number,
            'hospital': self.hospital,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
