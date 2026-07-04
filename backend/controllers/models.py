from controllers.database import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'admin', 'company', 'student'
    is_active = db.Column(db.Boolean, default=True) # Used for blacklisting/deactivation

    # Relationships
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    company_profile = db.relationship('CompanyProfile', backref='user', uselist=False, cascade="all, delete-orphan")

class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    resume_path = db.Column(db.String(256), nullable=True)
    skills = db.Column(db.String(256), nullable=True)
    placement_status = db.Column(db.String(50), default="Unplaced") # Tracking historical overview

    applications = db.relationship('Application', backref='student', cascade="all, delete-orphan")

class CompanyProfile(db.Model):
    __tablename__ = 'company_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    hr_contact = db.Column(db.String(20), nullable=False) [cite: 19]
    website = db.Column(db.String(120), nullable=True) [cite: 19]
    approval_status = db.Column(db.String(20), default='Pending') # 'Pending', 'Approved', 'Rejected'

    drives = db.relationship('PlacementDrive', backref='company', cascade="all, delete-orphan")

class PlacementDrive(db.Model):
    __tablename__ = 'placement_drives'

    id = db.Column(db.Integer, primary_key=True) [cite: 15]
    company_id = db.Column(db.Integer, db.ForeignKey('company_profiles.id'), nullable=False) [cite: 15]
    title = db.Column(db.String(100), nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    approval_status = db.Column(db.String(20), default='Pending') # 'Pending', 'Approved', 'Rejected'

    applications = db.relationship('Application', backref='drive', cascade="all, delete-orphan")

class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True) [cite: 17]
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False) [cite: 17]
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drives.id'), nullable=False) [cite: 18]
    application_date = db.Column(db.DateTime, default=datetime.utcnow) [cite: 18]
    status = db.Column(db.String(20), default='Applied') # 'Applied', 'Shortlisted', 'Selected', 'Rejected' [cite: 18]

    # Constraint to prevent multiple applications by a single student to the same drive
    __table_args__ = (db.UniqueConstraint('student_id', drive_id, name='_student_drive_uc'),)
