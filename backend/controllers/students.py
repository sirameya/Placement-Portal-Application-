"""
students.py — routes about the Student entity.

Split into two sections:
  1. Student self-service (role: student)
  2. Admin actions targeting students (role: admin)
Grouped by WHO the data belongs to, not by WHO is logged in — that's
why admin's "search/blacklist student" also lives here rather than in
a separate admin file.
"""

from flask import Blueprint, jsonify, request, current_app, send_from_directory
from flask_jwt_extended import get_jwt_identity
from controllers.database import db
from controllers.models import StudentProfile, Job, Application
from controllers.models import Interview
from controllers.config import Config, INSTANCE_DIR
from services.tasks import export_applications_csv
from services.celery_app import celery
import os
from werkzeug.utils import secure_filename
from utils.decorators import role_required
from services.cache import cache
from sqlalchemy import or_
from datetime import datetime

students_bp = Blueprint("students", __name__, url_prefix="/api/students")


def _get_student_profile():
    """Every student route derives 'which student is this?' from the JWT
    identity — NEVER from a value the client sends, or a student could
    act as another student."""
    user_id = get_jwt_identity()
    return StudentProfile.query.filter_by(user_id=int(user_id)).first_or_404()


# ─────────────────────────── Student self-service ───────────────────────────

@students_bp.route("/drives", methods=["GET"])
@role_required("student")
@cache.cached(timeout=60, query_string=True)
def browse_drives():
    """Students can filter by active or past drives.
    active = approved drives
    past = rejected drives
    """
    filter_type = request.args.get("filter", "active")
    if filter_type == "past":
        jobs = Job.query.filter_by(approval_status="rejected").all()
    else:
        jobs = Job.query.filter_by(approval_status="approved").all()

    return jsonify([
        {"id": j.id, "title": j.title, "company": j.company.company_name,
         "package": j.salary_package, "location": j.location,
         "job_type": j.job_type, "employment_type": j.employment_type, "skills_required": j.skills_required,
         "placement_mode": j.placement_mode, "min_cgpa": j.min_cgpa, "status": j.approval_status,
         "application_deadline": j.application_deadline.isoformat() if j.application_deadline else None,
         "drive_date": j.drive_date.isoformat() if j.drive_date else None}
        for j in jobs
    ])


@students_bp.route("/drives/<int:job_id>/apply", methods=["POST"])
@role_required("student")
def apply_to_drive(job_id):
    student = _get_student_profile()
    job = Job.query.get_or_404(job_id)

    if job.approval_status != "approved":
        return jsonify({"error": "This drive is not open for applications"}), 400

    # Check application deadline
    if job.application_deadline and datetime.utcnow() > job.application_deadline:
        return jsonify({"error": "The application deadline for this drive has passed"}), 400

    # Check branch eligibility if provided
    if job.eligible_branches:
        allowed = [b.strip().lower() for b in job.eligible_branches.split(",") if b.strip()]
        if not student.branch or student.branch.strip().lower() not in allowed:
            return jsonify({"error": "You are not eligible for this drive based on branch"}), 400

    # Check year eligibility if provided
    if job.eligible_years:
        allowed_years = [y.strip() for y in job.eligible_years.split(",") if y.strip()]
        if not student.year or str(student.year) not in allowed_years:
            return jsonify({"error": "You are not eligible for this drive based on year"}), 400

    if student.cgpa is not None and student.cgpa < job.min_cgpa:
        return jsonify({"error": f"Minimum CGPA required is {job.min_cgpa}"}), 400

    if Application.query.filter_by(student_id=student.id, job_id=job.id).first():
        return jsonify({"error": "You have already applied to this drive"}), 409

    application = Application(student_id=student.id, job_id=job.id, status="applied")
    db.session.add(application)
    db.session.commit()
    return jsonify({"message": "Application submitted successfully"}), 201


@students_bp.route("/applications", methods=["GET"])
@role_required("student")
def my_applications():
    """Full placement history for the logged-in student."""
    student = _get_student_profile()
    applications = Application.query.filter_by(student_id=student.id).order_by(Application.application_date.desc()).all()
    return jsonify([
        {"application_id": a.id, "drive_title": a.job.title,
         "company": a.job.company.company_name, "status": a.status,
         "applied_on": a.application_date.strftime("%Y-%m-%d"),
         "resume_path": a.resume_path, "cover_letter": a.cover_letter, "notes": a.notes}
        for a in applications
    ])


@students_bp.route("/interviews", methods=["GET"])
@role_required("student")
def my_interviews():
    student = _get_student_profile()
    interviews = []
    for app in student.applications:
        for iv in app.interviews:
            interviews.append({
                "interview_id": iv.id,
                "drive_title": app.job.title,
                "company": app.job.company.company_name,
                "scheduled_at": iv.scheduled_at.isoformat() if iv.scheduled_at else None,
                "location": iv.location,
                "status": iv.status,
            })
    return jsonify(interviews)


@students_bp.route("/profile", methods=["GET"])
@role_required("student")
def get_profile():
    """Retrieve the logged-in student's profile including CGPA."""
    student = _get_student_profile()
    return jsonify({
        "id": student.id,
        "name": student.name,
        "cgpa": student.cgpa,
        "branch": student.branch,
        "year": student.year,
        "skills": student.skills,
        "phone": student.phone,
        "address": student.address,
        "portfolio_url": student.portfolio_url,
        "linkedin_url": student.linkedin_url,
        "resume_path": student.resume_path
    })


@students_bp.route("/profile", methods=["PATCH"])
@role_required("student")
def update_profile():
    student = _get_student_profile()
    data = request.get_json() or {}
    for field in ("name", "cgpa", "branch", "year", "skills", "resume_path", "phone", "address", "portfolio_url", "linkedin_url"):
        if field in data:
            setattr(student, field, data[field])
    db.session.commit()
    return jsonify({"message": "Profile updated"})


@students_bp.route("/profile/upload_resume", methods=["POST"])
@role_required("student")
def upload_resume():
    """Accepts multipart/form-data file under 'resume' key and stores it in instance/uploads."""
    student = _get_student_profile()
    if 'resume' not in request.files:
        return jsonify({"error": "No resume file provided"}), 400
    f = request.files['resume']
    if f.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(f.filename)
    uploads_dir = Config.UPLOADS_DIR if hasattr(Config, 'UPLOADS_DIR') else os.path.join(INSTANCE_DIR, 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    out_name = f"student_{student.id}_resume_{int(datetime.utcnow().timestamp())}_{filename}"
    full_path = os.path.join(uploads_dir, out_name)
    f.save(full_path)
    # Persist path relative to instance for portability
    student.resume_path = f"uploads/{out_name}"
    db.session.commit()
    return jsonify({"message": "Resume uploaded", "resume_path": student.resume_path})


@students_bp.route("/applications/export", methods=["POST"])
@role_required("student")
def trigger_export():
    """Starts async export job and returns Celery task id."""
    student = _get_student_profile()
    task = export_applications_csv.delay(student.id)
    return jsonify({"message": "Export started", "task_id": task.id}), 202


@students_bp.route('/exports/status/<task_id>', methods=['GET'])
@role_required('student')
def export_status(task_id):
    res = celery.AsyncResult(task_id)
    data = {"state": res.state}
    if res.ready():
        data.update({"result": res.result})
    return jsonify(data)


@students_bp.route('/exports/<path:filename>', methods=['GET'])
def download_export(filename):
    exports_dir = Config.EXPORTS_DIR if hasattr(Config, 'EXPORTS_DIR') else os.path.join(INSTANCE_DIR, 'exports')
    return send_from_directory(exports_dir, filename, as_attachment=True)


# ─────────────────────────── Admin-on-student actions ───────────────────────────

@students_bp.route("/search", methods=["GET"])
@role_required("admin")
@cache.cached(timeout=60, query_string=True)
def search_students():
    """GET /api/students/search?q=someterm"""
    q = request.args.get("q", "")
    query = StudentProfile.query
    if q:
        query = query.filter(StudentProfile.name.ilike(f"%{q}%"))
    matches = query.order_by(StudentProfile.name).all()
    return jsonify([
        {
            "id": s.id,
            "name": s.name,
            "branch": s.branch,
            "year": s.year,
            "cgpa": s.cgpa,
            "skills": s.skills,
            "is_active": s.user.is_active if s.user else True,
        }
        for s in matches
    ])


@students_bp.route("/applications/all", methods=["GET"])
@role_required("admin")
def admin_all_applications():
    applications = Application.query.order_by(Application.application_date.desc()).all()
    return jsonify([
        {
            "id": a.id,
            "student_name": a.student.name if a.student else None,
            "drive_title": a.job.title if a.job else None,
            "company": a.job.company.company_name if a.job and a.job.company else None,
            "status": a.status,
            "applied_on": a.application_date.strftime("%Y-%m-%d") if a.application_date else None,
        }
        for a in applications
    ])


@students_bp.route("/<int:student_id>/blacklist", methods=["POST"])
@role_required("admin")
def blacklist_student(student_id):
    student = StudentProfile.query.get_or_404(student_id)
    student.user.is_active = False
    db.session.commit()
    return jsonify({"message": f"{student.name} has been deactivated"})


@students_bp.route("/<int:student_id>/toggle-active", methods=["POST"])
@role_required("admin")
def toggle_student_active(student_id):
    student = StudentProfile.query.get_or_404(student_id)
    student.user.is_active = not student.user.is_active
    db.session.commit()
    cache.clear()
    return jsonify({"message": f"Student account {'activated' if student.user.is_active else 'deactivated'}"})
