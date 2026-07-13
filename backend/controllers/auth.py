"""
auth.py — registration and login for students and companies.

Uses a Flask "Blueprint": a mini-app grouping related routes, which we
plug into the main app in app.py. Keeps app.py clean instead of cramming
every route into one file.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from controllers.database import db
from controllers.models import User, StudentProfile, CompanyProfile

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Handles registration for BOTH students and companies — 'role' in the
    request body decides which.

    Student body:  { "email", "password", "role": "student", "name" }
    Company body:  { "email", "password", "role": "company", "company_name", ... }
    """
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    if not email or not password or role not in ("student", "company"):
        return jsonify({"error": "email, password, and a valid role are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "An account with this email already exists"}), 409

    user = User(email=email, password_hash=generate_password_hash(password), role=role, is_active=True)
    db.session.add(user)
    db.session.flush()  # gives us user.id before committing, to link the profile

    if role == "student":
        if not data.get("name"):
            return jsonify({"error": "name is required for student registration"}), 400
        profile = StudentProfile(
            user_id=user.id,
            name=data["name"],
            cgpa=data.get("cgpa"),  # CGPA is optional during registration
            branch=data.get("branch"),
            year=data.get("year"),
            phone=data.get("phone"),
            address=data.get("address"),
            portfolio_url=data.get("portfolio_url"),
            linkedin_url=data.get("linkedin_url"),
        )
    else:  # company
        if not data.get("company_name"):
            return jsonify({"error": "company_name is required for company registration"}), 400
        profile = CompanyProfile(
            user_id=user.id,
            company_name=data["company_name"],
            hr_contact=data.get("hr_contact"),
            website=data.get("website"),
            industry=data.get("industry"),
            address=data.get("address"),
            contact_email=data.get("contact_email"),
            phone_number=data.get("phone_number"),
            description=data.get("description"),
            employee_count=data.get("employee_count"),
            approval_status="pending",
        )

    db.session.add(profile)
    db.session.commit()
    return jsonify({"message": "Registered successfully. You can now log in."}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Every role logs in through this SAME endpoint. We check the password,
    then issue a JWT encoding the user's id and role — every future
    request carries this token so we know who's calling.
    """
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    if not user.is_active:
        return jsonify({"error": "This account has been deactivated"}), 403

    if user.role == "company" and user.company_profile.approval_status != "approved":
        return jsonify({"error": f"Company account is {user.company_profile.approval_status} by admin"}), 403

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role},
    )
    return jsonify({"access_token": access_token, "role": user.role, "user_id": user.id}), 200
