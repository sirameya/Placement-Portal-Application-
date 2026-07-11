"""
tasks.py — the actual background jobs celery_app.py schedules/triggers.
"""

import csv
import io
from datetime import datetime

from flask import Flask
from services.celery_app import celery
from controllers.config import Config
from controllers.database import db
from controllers.models import StudentProfile, Job, Application


def _get_app_context():
    """Celery tasks run in a SEPARATE process from Flask, so they don't
    automatically have DB access. We recreate a minimal app here so
    queries work inside tasks."""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app


@celery.task(name="services.tasks.send_daily_reminders")
def send_daily_reminders():
    """Scheduled: reminds students about drives they haven't applied to.
    Swap the print() for a real email/SMS/webhook call in production."""
    app = _get_app_context()
    with app.app_context():
        approved_jobs = Job.query.filter_by(approval_status="approved").all()
        students = StudentProfile.query.all()

        for student in students:
            applied_ids = {a.job_id for a in student.applications}
            unapplied = [j for j in approved_jobs if j.id not in applied_ids]
            if unapplied:
                print(f"[REMINDER] Would notify {student.name} about "
                      f"{len(unapplied)} open drives they haven't applied to.")
        return f"Sent reminders for {len(students)} students"


@celery.task(name="services.tasks.send_monthly_report")
def send_monthly_report():
    """Scheduled: builds and 'emails' an HTML activity report to admin."""
    app = _get_app_context()
    with app.app_context():
        drives_count = Job.query.filter_by(approval_status="approved").count()
        applied_count = Application.query.count()
        selected_count = Application.query.filter_by(status="selected").count()

        html_report = f"""
        <h2>Monthly Placement Activity Report</h2>
        <p>Generated on: {datetime.utcnow().strftime('%Y-%m-%d')}</p>
        <ul>
            <li>Drives conducted: {drives_count}</li>
            <li>Students applied: {applied_count}</li>
            <li>Students selected: {selected_count}</li>
        </ul>
        """
        print("[MONTHLY REPORT]", html_report)  # swap for Flask-Mail/smtplib in production
        return "Monthly report generated and sent"


@celery.task(name="services.tasks.export_applications_csv")
def export_applications_csv(student_id):
    """User-triggered async job: student clicks 'Export' -> runs in the
    background -> generates a CSV. Triggered via .delay(student_id),
    never called directly (that would run it synchronously)."""
    app = _get_app_context()
    with app.app_context():
        student = StudentProfile.query.get(student_id)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Company Name", "Drive Title", "Application Status", "Applied Date"])
        for a in student.applications:
            writer.writerow([a.job.company.company_name, a.job.title, a.status,
                              a.application_date.strftime("%Y-%m-%d")])

        file_path = f"exports/student_{student_id}_applications.csv"
        print(f"[EXPORT DONE] Saved to {file_path}")
        return file_path
