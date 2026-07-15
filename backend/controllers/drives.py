"""
drives.py — routes about placement Drives (Job postings): company
creates/manages them, admin approves them, admin views overall stats.
"""

import os
from flask import Blueprint, jsonify, request, send_from_directory
from datetime import datetime
from flask_jwt_extended import get_jwt_identity, get_jwt
from sqlalchemy import or_
from controllers.database import db
from controllers.models import CompanyProfile, StudentProfile, Job, Application, Interview
from controllers.config import Config
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
    if company.approval_status != "approved":
        return jsonify({"error": "Your company account must be approved before creating drives."}), 403

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

    # Validate that drive_date is strictly after application_deadline
    if deadline and drive_date and deadline >= drive_date:
        return jsonify({"error": "Drive date must be strictly after the application deadline"}), 400

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
         "description": j.description,
         "package": j.package,
         "salary_package": j.salary_package,
         "location": j.location,
         "job_type": j.job_type,
         "employment_type": j.employment_type,
         "placement_mode": j.placement_mode,
         "skills_required": j.skills_required,
         "eligible_branches": j.eligible_branches,
         "eligible_years": j.eligible_years,
         "application_deadline": j.application_deadline.isoformat() if j.application_deadline else None,
         "drive_date": j.drive_date.isoformat() if j.drive_date else None,
         "applicant_count": len(j.applications)}
        for j in company.jobs
    ])


@drives_bp.route("/<int:job_id>", methods=["PATCH"])
@role_required("company")
def update_drive(job_id):
    company = _get_company_profile()
    job = Job.query.get_or_404(job_id)
    if job.company_id != company.id:
        return jsonify({"error": "This drive does not belong to your company"}), 403
    if job.approval_status == "closed":
        return jsonify({"error": "Closed drives cannot be edited"}), 400

    data = request.get_json() or {}
    editable_fields = [
        "title",
        "description",
        "package",
        "salary_package",
        "location",
        "job_type",
        "employment_type",
        "placement_mode",
        "skills_required",
        "eligible_branches",
        "eligible_years",
    ]

    deadline_raw = data.get("application_deadline")
    drive_date_raw = data.get("drive_date")
    deadline = job.application_deadline
    drive_date = job.drive_date

    if deadline_raw is not None:
        if deadline_raw == "":
            deadline = None
        else:
            try:
                deadline = datetime.fromisoformat(deadline_raw)
            except Exception:
                return jsonify({"error": "application_deadline must be ISO datetime string"}), 400

    if drive_date_raw is not None:
        if drive_date_raw == "":
            drive_date = None
        else:
            try:
                drive_date = datetime.fromisoformat(drive_date_raw)
            except Exception:
                return jsonify({"error": "drive_date must be ISO datetime string"}), 400

    if deadline and drive_date and deadline >= drive_date:
        return jsonify({"error": "Drive date must be strictly after the application deadline"}), 400

    for field in editable_fields:
        if field in data:
            setattr(job, field, data[field])

    job.application_deadline = deadline
    job.drive_date = drive_date

    db.session.commit()
    return jsonify({"message": "Drive updated successfully", "drive_id": job.id})


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
@cache.cached(timeout=60)
def list_active_drives():
    jobs = Job.query.filter_by(approval_status="approved").all()
    return jsonify([
        {
            "id": j.id,
            "title": j.title,
            "company": j.company.company_name,
            "package": j.salary_package,
            "location": j.location,
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
@cache.cached(timeout=60)
def list_past_drives():
    jobs = Job.query.filter_by(approval_status="rejected").all()
    return jsonify([
        {
            "id": j.id,
            "title": j.title,
            "company": j.company.company_name,
            "package": j.salary_package,
            "location": j.location,
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
@cache.cached(timeout=60)
def list_pending_drives():
    jobs = Job.query.filter_by(approval_status="pending").all()
    return jsonify([
        {"id": j.id, "title": j.title, "company": j.company.company_name, "package": j.salary_package, "location": j.location, "job_type": j.job_type, "employment_type": j.employment_type, "application_deadline": j.application_deadline.isoformat() if j.application_deadline else None}
        for j in jobs
    ])


@drives_bp.route("/<int:job_id>/approve", methods=["POST"])
@role_required("admin")
def approve_drive(job_id):
    job = Job.query.get_or_404(job_id)
    job.approval_status = "approved"
    db.session.commit()
    cache.delete_memoized(list_active_drives)
    cache.delete_memoized(list_pending_drives)
    cache.delete_memoized(list_past_drives)
    return jsonify({"message": f"Drive '{job.title}' approved"})


@drives_bp.route("/<int:job_id>/reject", methods=["POST"])
@role_required("admin")
def reject_drive(job_id):
    job = Job.query.get_or_404(job_id)
    job.approval_status = "rejected"
    db.session.commit()
    cache.delete_memoized(list_active_drives)
    cache.delete_memoized(list_pending_drives)
    cache.delete_memoized(list_past_drives)
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


@drives_bp.route("/search", methods=["GET"])
@role_required("admin", "student", "company")
def search_drives():
    q = request.args.get("q", "").strip()
    query = Job.query
    role = get_jwt().get("role")
    if role != "admin":
        query = query.filter_by(approval_status="approved")
    if q:
        query = query.filter(
            or_(
                Job.title.ilike(f"%{q}%"),
                Job.location.ilike(f"%{q}%"),
                Job.skills_required.ilike(f"%{q}%"),
                Job.description.ilike(f"%{q}%"),
                Job.company.has(CompanyProfile.company_name.ilike(f"%{q}%")),
            )
        )
    jobs = query.order_by(Job.created_at.desc()).all()
    return jsonify([
        {
            "id": j.id,
            "title": j.title,
            "company": j.company.company_name,
            "package": j.salary_package,
            "location": j.location,
            "min_cgpa": j.min_cgpa,
            "status": j.approval_status,
            "application_deadline": j.application_deadline.isoformat() if j.application_deadline else None,
            "created_at": j.created_at.strftime("%Y-%m-%d"),
        }
        for j in jobs
    ])


@drives_bp.route("/reports", methods=["GET"])
@role_required("admin")
def list_reports():
    reports_dir = getattr(Config, 'REPORTS_DIR', None)
    if not reports_dir:
        return jsonify({"reports": []})

    os.makedirs(reports_dir, exist_ok=True)
    files = [
        {"name": f, "url": f"/api/drives/reports/{f}"}
        for f in sorted(os.listdir(reports_dir), reverse=True)
        if os.path.isfile(os.path.join(reports_dir, f))
    ]
    return jsonify({"reports": files})


@drives_bp.route("/reports/<path:filename>", methods=["GET"])
@role_required("admin")
def download_report(filename):
    reports_dir = getattr(Config, 'REPORTS_DIR', None)
    if not reports_dir:
        return jsonify({"error": "Reports directory not configured"}), 500
    return send_from_directory(reports_dir, filename, as_attachment=True)


@drives_bp.route("/notifications/status", methods=["GET"])
@role_required("admin")
def notification_status():
    mail_ready = bool(getattr(Config, 'MAIL_USERNAME', None) and getattr(Config, 'MAIL_PASSWORD', None))
    webhook_ready = bool(getattr(Config, 'NOTIFICATION_WEBHOOK_URL', None))
    return jsonify({
        "mail_ready": mail_ready,
        "webhook_ready": webhook_ready,
        "admin_email": getattr(Config, 'ADMIN_EMAIL', None),
        "notifications_ready": mail_ready or webhook_ready,
    })


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
        "application_status_counts": {
            "applied": Application.query.filter_by(status="applied").count(),
            "shortlisted": Application.query.filter_by(status="shortlisted").count(),
            "selected": Application.query.filter_by(status="selected").count(),
            "rejected": Application.query.filter_by(status="rejected").count(),
        },
    })
