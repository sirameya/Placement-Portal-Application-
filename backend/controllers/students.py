"""
students.py — routes about the Student entity.

Split into two sections:
  1. Student self-service (role: student)
  2. Admin actions targeting students (role: admin)
Grouped by WHO the data belongs to, not by WHO is logged in — that's
why admin's "search/blacklist student" also lives here rather than in
a separate admin file.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from controllers.database import db
from controllers.models import StudentProfile, Job, Application
from controllers.models import Interview
from utils.decorators import role_required
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
         "package": j.package, "salary_package": j.salary_package, "location": j.location,
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
    return jsonify([
        {"application_id": a.id, "drive_title": a.job.title,
         "company": a.job.company.company_name, "status": a.status,
         "applied_on": a.application_date.strftime("%Y-%m-%d"),
         "resume_path": a.resume_path, "cover_letter": a.cover_letter, "notes": a.notes}
        for a in student.applications
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
        "skills": student.skills,
        "resume_path": student.resume_path
    })


@students_bp.route("/profile", methods=["PATCH"])
@role_required("student")
def update_profile():
    student = _get_student_profile()
    data = request.get_json()
    for field in ("name", "cgpa", "branch", "year", "skills", "resume_path"):
        if field in data:
            setattr(student, field, data[field])
    db.session.commit()
    return jsonify({"message": "Profile updated"})


# ─────────────────────────── Admin-on-student actions ───────────────────────────

@students_bp.route("/search", methods=["GET"])
@role_required("admin")
def search_students():
    """GET /api/students/search?q=someterm"""
    q = request.args.get("q", "")
    matches = StudentProfile.query.filter(StudentProfile.name.ilike(f"%{q}%")).all()
    return jsonify([{"id": s.id, "name": s.name, "cgpa": s.cgpa} for s in matches])


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
    return jsonify({"message": f"Student account {'activated' if student.user.is_active else 'deactivated'}"})
