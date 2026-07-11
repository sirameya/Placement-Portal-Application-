"""
drives.py — routes about placement Drives (Job postings): company
creates/manages them, admin approves them, admin views overall stats.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from controllers.database import db
from controllers.models import CompanyProfile, StudentProfile, Job, Application
from utils.decorators import role_required
from services.cache import cache

drives_bp = Blueprint("drives", __name__, url_prefix="/api/drives")


def _get_company_profile():
    user_id = get_jwt_identity()
    return CompanyProfile.query.filter_by(user_id=int(user_id)).first_or_404()


# ─────────────────────────── Company: manage own drives ───────────────────────────

@drives_bp.route("", methods=["POST"])
@role_required("company")
def create_drive():
    """Company creates a drive. Starts 'pending' — invisible to students
    until admin approves it."""
    company = _get_company_profile()
    data = request.get_json()

    if not data.get("title"):
        return jsonify({"error": "title is required"}), 400

    job = Job(
        company_id=company.id,
        title=data["title"],
        description=data.get("description", ""),
        package=data.get("package"),
        min_cgpa=data.get("min_cgpa", 0.0),
        approval_status="pending",
    )
    db.session.add(job)
    db.session.commit()
    return jsonify({"message": "Drive created, awaiting admin approval", "drive_id": job.id}), 201


@drives_bp.route("/mine", methods=["GET"])
@role_required("company")
def my_drives():
    company = _get_company_profile()
    return jsonify([
        {"id": j.id, "title": j.title, "status": j.approval_status,
         "applicant_count": len(j.applications)}
        for j in company.jobs
    ])


@drives_bp.route("/<int:job_id>/applicants", methods=["GET"])
@role_required("company")
def view_applicants(job_id):
    company = _get_company_profile()
    job = Job.query.get_or_404(job_id)
    if job.company_id != company.id:
        return jsonify({"error": "This drive does not belong to your company"}), 403

    return jsonify([
        {"application_id": a.id, "student_name": a.student.name,
         "cgpa": a.student.cgpa, "status": a.status}
        for a in job.applications
    ])


@drives_bp.route("/applications/<int:application_id>/status", methods=["PATCH"])
@role_required("company")
def update_application_status(application_id):
    """Body: { "status": "shortlisted" }  (or 'selected' / 'rejected')"""
    company = _get_company_profile()
    application = Application.query.get_or_404(application_id)
    if application.job.company_id != company.id:
        return jsonify({"error": "This application is not for your company"}), 403

    new_status = request.get_json().get("status")
    if new_status not in ("shortlisted", "selected", "rejected"):
        return jsonify({"error": "status must be shortlisted, selected, or rejected"}), 400

    application.status = new_status
    db.session.commit()
    return jsonify({"message": f"Application status updated to {new_status}"})


# ─────────────────────────── Admin: approve drives + stats ───────────────────────────

@drives_bp.route("/pending", methods=["GET"])
@role_required("admin")
def list_pending_drives():
    jobs = Job.query.filter_by(approval_status="pending").all()
    return jsonify([
        {"id": j.id, "title": j.title, "company": j.company.company_name, "package": j.package}
        for j in jobs
    ])


@drives_bp.route("/<int:job_id>/approve", methods=["POST"])
@role_required("admin")
def approve_drive(job_id):
    job = Job.query.get_or_404(job_id)
    job.approval_status = "approved"
    db.session.commit()
    return jsonify({"message": f"Drive '{job.title}' approved"})


@drives_bp.route("/<int:job_id>/reject", methods=["POST"])
@role_required("admin")
def reject_drive(job_id):
    job = Job.query.get_or_404(job_id)
    job.approval_status = "rejected"
    db.session.commit()
    return jsonify({"message": f"Drive '{job.title}' rejected"})


@drives_bp.route("/stats", methods=["GET"])
@role_required("admin")
@cache.cached(timeout=60)  # recompute at most once per 60s
def stats():
    """Dashboard numbers. Cached since 4 COUNT queries on every
    dashboard refresh is wasteful and this data doesn't need to be
    perfectly real-time."""
    return jsonify({
        "total_students": StudentProfile.query.count(),
        "total_companies": CompanyProfile.query.filter_by(approval_status="approved").count(),
        "total_drives": Job.query.filter_by(approval_status="approved").count(),
        "total_selected": Application.query.filter_by(status="selected").count(),
    })
