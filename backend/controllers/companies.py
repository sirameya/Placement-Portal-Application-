"""
companies.py — routes about the Company entity: company's own dashboard
data, plus admin's approve/reject/search actions on companies.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from controllers.database import db
from controllers.models import CompanyProfile
from utils.decorators import role_required

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


# ─────────────────────────── Admin-on-company actions ───────────────────────────

@companies_bp.route("/all", methods=["GET"])
@role_required("admin")
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
    return jsonify({"message": f"{company.company_name} approved"})


@companies_bp.route("/<int:company_id>/reject", methods=["POST"])
@role_required("admin")
def reject(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    company.approval_status = "rejected"
    db.session.commit()
    return jsonify({"message": f"{company.company_name} rejected"})


@companies_bp.route("/search", methods=["GET"])
@role_required("admin")
def search_companies():
    q = request.args.get("q", "")
    matches = CompanyProfile.query.filter(CompanyProfile.company_name.ilike(f"%{q}%")).all()
    return jsonify([{"id": c.id, "company_name": c.company_name} for c in matches])


@companies_bp.route("/<int:company_id>/toggle-active", methods=["POST"])
@role_required("admin")
def toggle_company_active(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    company.user.is_active = not company.user.is_active
    db.session.commit()
    return jsonify({"message": f"Company account {'activated' if company.user.is_active else 'deactivated'}"})
