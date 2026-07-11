"""
models.py — our database tables, defined as Python classes.
Each class = one table. Each attribute = one column.
"""

from datetime import datetime
from controllers.database import db


class User(db.Model):
    """
    The single 'login' table for EVERYONE — admin, company, and student.
    One table works because login logic (check email+password) is
    IDENTICAL for all roles. The 'role' column tells us who they are.
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin' | 'company' | 'student'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student_profile = db.relationship("StudentProfile", backref="user", uselist=False)
    company_profile = db.relationship("CompanyProfile", backref="user", uselist=False)


class StudentProfile(db.Model):
    """Extra details specific to students."""
    __tablename__ = "student_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    name = db.Column(db.String(120), nullable=False)
    cgpa = db.Column(db.Float)
    skills = db.Column(db.String(500))
    resume_path = db.Column(db.String(255))

    applications = db.relationship("Application", backref="student", lazy=True)


class CompanyProfile(db.Model):
    """Extra details specific to companies."""
    __tablename__ = "company_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    company_name = db.Column(db.String(120), nullable=False)
    hr_contact = db.Column(db.String(120))
    website = db.Column(db.String(255))
    approval_status = db.Column(db.String(20), default="pending")  # pending | approved | rejected

    jobs = db.relationship("Job", backref="company", lazy=True)


class Job(db.Model):
    """A placement drive created by a company. (Called 'Job' in code,
    'Drive' in the UI/routes — same table, matches project terminology.)"""
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company_profiles.id"), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    package = db.Column(db.String(50))
    min_cgpa = db.Column(db.Float, default=0.0)
    approval_status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship("Application", backref="job", lazy=True)


class Application(db.Model):
    """Join table connecting a Student to a Drive they applied for,
    with extra data (status, date) attached."""
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student_profiles.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="applied")  # applied | shortlisted | selected | rejected

    __table_args__ = (
        db.UniqueConstraint("student_id", "job_id", name="unique_student_job_application"),
    )
