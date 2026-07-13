"""
drives.py — routes about placement Drives (Job postings): company
creates/manages them, admin approves them, admin views overall stats.
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
from flask_jwt_extended import get_jwt_identity
from controllers.database import db
from controllers.models import CompanyProfile, StudentProfile, Job, Application, Interview
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

    # parse optional eligibility fields
    eligible_branches = data.get("eligible_branches")  # expected comma-separated string
    eligible_years = data.get("eligible_years")
    deadline_raw = data.get("application_deadline")
    deadline = None
    if deadline_raw:
        try:
            deadline = datetime.fromisoformat(deadline_raw)
        except Exception:
            return jsonify({"error": "application_deadline must be ISO datetime string"}), 400

    drive_date_raw = data.get("drive_date")
    drive_date = None
    if drive_date_raw:
        try:
            drive_date = datetime.fromisoformat(drive_date_raw)
        except Exception:
            return jsonify({"error": "drive_date must be ISO datetime string"}), 400

    job = Job(
        company_id=company.id,
        title=data["title"],
        description=data.get("description", ""),
        package=data.get("package"),
        salary_package=data.get("salary_package"),
        location=data.get("location"),
        job_type=data.get("job_type"),
        employment_type=data.get("employment_type"),
        skills_required=data.get("skills_required"),
        placement_mode=data.get("placement_mode"),
        min_cgpa=data.get("min_cgpa", 0.0),
        eligible_branches=eligible_branches,
        eligible_years=eligible_years,
        application_deadline=deadline,
        drive_date=drive_date,
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
         "company_name": j.company.company_name,
         "location": j.location,
         "job_type": j.job_type,
         "employment_type": j.employment_type,
         "salary_package": j.salary_package,
         "skills_required": j.skills_required,
         "application_deadline": j.application_deadline.isoformat() if j.application_deadline else None,
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


@drives_bp.route("/applications/<int:application_id>/interview", methods=["POST"])
@role_required("company")
def schedule_interview(application_id):
    company = _get_company_profile()
    application = Application.query.get_or_404(application_id)
    if application.job.company_id != company.id:
        return jsonify({"error": "This application is not for your company"}), 403

    data = request.get_json()
    scheduled_raw = data.get("scheduled_at")
    location = data.get("location")
    if not scheduled_raw:
        return jsonify({"error": "scheduled_at is required (ISO datetime)"}), 400
    try:
        scheduled_at = datetime.fromisoformat(scheduled_raw)
    except Exception:
        return jsonify({"error": "scheduled_at must be ISO datetime string"}), 400

    interview = Interview(application_id=application.id, scheduled_at=scheduled_at, location=location)
    db.session.add(interview)
    db.session.commit()
    return jsonify({"message": "Interview scheduled", "interview_id": interview.id}), 201


@drives_bp.route("/applications/<int:application_id>/interview", methods=["GET"])
@role_required("company")
def get_application_interviews(application_id):
    company = _get_company_profile()
    application = Application.query.get_or_404(application_id)
    if application.job.company_id != company.id:
        return jsonify({"error": "This application is not for your company"}), 403

    return jsonify([
        {"id": i.id, "scheduled_at": i.scheduled_at.isoformat() if i.scheduled_at else None, "location": i.location, "status": i.status}
        for i in application.interviews
    ])


# ─────────────────────────── Admin: approve drives + stats ───────────────────────────

@drives_bp.route("/active", methods=["GET"])
@role_required("admin")
def list_active_drives():
    jobs = Job.query.filter_by(approval_status="approved").all()
    return jsonify([
        {
            "id": j.id,
            "title": j.title,
            "company": j.company.company_name,
            "package": j.package,
            "min_cgpa": j.min_cgpa,
            "eligible_branches": j.eligible_branches,
            "eligible_years": j.eligible_years,
            "application_deadline": j.application_deadline.isoformat() if j.application_deadline else None,
            "created_at": j.created_at.strftime("%Y-%m-%d"),
        }
        for j in jobs
    ])


@drives_bp.route("/past", methods=["GET"])
@role_required("admin")
def list_past_drives():
    jobs = Job.query.filter_by(approval_status="rejected").all()
    return jsonify([
        {
            "id": j.id,
            "title": j.title,
            "company": j.company.company_name,
            "package": j.package,
            "min_cgpa": j.min_cgpa,
            "eligible_branches": j.eligible_branches,
            "eligible_years": j.eligible_years,
            "application_deadline": j.application_deadline.isoformat() if j.application_deadline else None,
            "created_at": j.created_at.strftime("%Y-%m-%d"),
        }
        for j in jobs
    ])


@drives_bp.route("/pending", methods=["GET"])
@role_required("admin")
def list_pending_drives():
    jobs = Job.query.filter_by(approval_status="pending").all()
    return jsonify([
        {"id": j.id, "title": j.title, "company": j.company.company_name, "package": j.package, "location": j.location, "job_type": j.job_type, "employment_type": j.employment_type, "salary_package": j.salary_package, "application_deadline": j.application_deadline.isoformat() if j.application_deadline else None}
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


@drives_bp.route("/<int:job_id>/close", methods=["POST"])
@role_required("company")
def close_drive(job_id):
    company = _get_company_profile()
    job = Job.query.get_or_404(job_id)
    if job.company_id != company.id:
        return jsonify({"error": "This drive does not belong to your company"}), 403
    job.approval_status = "closed"
    db.session.commit()
    return jsonify({"message": f"Drive '{job.title}' closed"})


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
