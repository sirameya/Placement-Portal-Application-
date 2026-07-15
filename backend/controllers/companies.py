"""
companies.py — routes about the Company entity: company's own dashboard
data, plus admin's approve/reject/search actions on companies.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import or_
from controllers.database import db
from controllers.models import CompanyProfile
from utils.decorators import role_required
from services.cache import cache

companies_bp = Blueprint("companies", __name__, url_prefix="/api/companies")


def _get_company_profile():
    user_id = get_jwt_identity()
    return CompanyProfile.query.filter_by(user_id=int(user_id)).first_or_404()


# ─────────────────────────── Company self-service ───────────────────────────

@companies_bp.route("/me", methods=["GET"])
@role_required("company")
def my_profile():
    """Company dashboard header info."""
    company = _get_company_profile()
    return jsonify({
        "company_name": company.company_name,
        "hr_contact": company.hr_contact,
        "website": company.website,
        "industry": company.industry,
        "address": company.address,
        "contact_email": company.contact_email,
        "phone_number": company.phone_number,
        "description": company.description,
        "employee_count": company.employee_count,
        "approval_status": company.approval_status,
        "drives_created": len(company.jobs),
    })


@companies_bp.route("/me", methods=["PATCH"])
@role_required("company")
def update_my_profile():
    """Allow a company to update its own profile details."""
    company = _get_company_profile()
    data = request.get_json() or {}
    editable_fields = [
        "company_name",
        "hr_contact",
        "website",
        "industry",
        "address",
        "contact_email",
        "phone_number",
        "description",
        "employee_count",
    ]

    for field in editable_fields:
        if field in data:
            setattr(company, field, data[field])

    db.session.commit()
    cache.clear()
    return jsonify({
        "message": "Company profile updated",
        "company": {
            "company_name": company.company_name,
            "hr_contact": company.hr_contact,
            "website": company.website,
            "industry": company.industry,
            "address": company.address,
            "contact_email": company.contact_email,
            "phone_number": company.phone_number,
            "description": company.description,
            "employee_count": company.employee_count,
            "approval_status": company.approval_status,
            "drives_created": len(company.jobs),
        },
    })


# ─────────────────────────── Admin-on-company actions ───────────────────────────

@companies_bp.route("/all", methods=["GET"])
@role_required("admin")
@cache.cached(timeout=60)
def list_companies():
    companies = CompanyProfile.query.order_by(CompanyProfile.company_name).all()
    return jsonify([
        {
            "id": c.id,
            "company_name": c.company_name,
            "hr_contact": c.hr_contact,
            "website": c.website,
            "approval_status": c.approval_status,
            "industry": c.industry,
            "address": c.address,
            "contact_email": c.contact_email,
            "phone_number": c.phone_number,
            "description": c.description,
            "employee_count": c.employee_count,
            "is_active": c.user.is_active if c.user else True,
        }
        for c in companies
    ])


@companies_bp.route("/pending", methods=["GET"])
@role_required("admin")
@cache.cached(timeout=60)
def list_pending():
    companies = CompanyProfile.query.filter_by(approval_status="pending").all()
    return jsonify([
        {"id": c.id, "company_name": c.company_name, "hr_contact": c.hr_contact, "website": c.website}
        for c in companies
    ])


@companies_bp.route("/<int:company_id>/approve", methods=["POST"])
@role_required("admin")
def approve(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    company.approval_status = "approved"
    db.session.commit()
    cache.clear()
    return jsonify({"message": f"{company.company_name} approved"})


@companies_bp.route("/<int:company_id>/reject", methods=["POST"])
@role_required("admin")
def reject(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    company.approval_status = "rejected"
    db.session.commit()
    cache.clear()
    return jsonify({"message": f"{company.company_name} rejected"})


@companies_bp.route("/search", methods=["GET"])
@role_required("admin")
@cache.cached(timeout=60, query_string=True)
def search_companies():
    q = request.args.get("q", "")
    query = CompanyProfile.query
    if q:
        query = query.filter(
            or_(
                CompanyProfile.company_name.ilike(f"%{q}%"),
                CompanyProfile.industry.ilike(f"%{q}%"),
                CompanyProfile.hr_contact.ilike(f"%{q}%"),
            )
        )
    matches = query.order_by(CompanyProfile.company_name).all()
    return jsonify([
        {
            "id": c.id,
            "company_name": c.company_name,
            "hr_contact": c.hr_contact,
            "industry": c.industry,
            "approval_status": c.approval_status,
            "is_active": c.user.is_active if c.user else True,
        }
        for c in matches
    ])


@companies_bp.route("/<int:company_id>/toggle-active", methods=["POST"])
@role_required("admin")
def toggle_company_active(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    company.user.is_active = not company.user.is_active
    db.session.commit()
    cache.clear()
    return jsonify({"message": f"Company account {'activated' if company.user.is_active else 'deactivated'}"})
