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
from utils.decorators import role_required

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
    """Only approved drives are visible to students."""
    jobs = Job.query.filter_by(approval_status="approved").all()
    return jsonify([
        {"id": j.id, "title": j.title, "company": j.company.company_name,
         "package": j.package, "min_cgpa": j.min_cgpa}
        for j in jobs
    ])


@students_bp.route("/drives/<int:job_id>/apply", methods=["POST"])
@role_required("student")
def apply_to_drive(job_id):
    student = _get_student_profile()
    job = Job.query.get_or_404(job_id)

    if job.approval_status != "approved":
        return jsonify({"error": "This drive is not open for applications"}), 400

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
         "applied_on": a.application_date.strftime("%Y-%m-%d")}
        for a in student.applications
    ])


@students_bp.route("/profile", methods=["PATCH"])
@role_required("student")
def update_profile():
    student = _get_student_profile()
    data = request.get_json()
    for field in ("name", "cgpa", "skills", "resume_path"):
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
    """Locks the student out by invalidating their password hash.
    A cleaner future version would add an `is_active` boolean to User."""
    student = StudentProfile.query.get_or_404(student_id)
    student.user.password_hash = "!blacklisted!"
    db.session.commit()
    return jsonify({"message": f"{student.name} has been blacklisted"})
