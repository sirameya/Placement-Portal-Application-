"""
tasks.py — the actual background jobs celery_app.py schedules/triggers.
"""

import csv
import io
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
import json

from flask import Flask
from services.celery_app import celery
from controllers.config import Config, INSTANCE_DIR
from controllers.database import db
from controllers.models import StudentProfile, Job, Application
import urllib.request
import urllib.error


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
                subject = "Reminder: Open placement drives"
                body = f"Hi {student.name},\n\nThere are {len(unapplied)} open drives you haven't applied to yet. Please check your dashboard.\n\nRegards,\nPlacement Portal"
                # Try to notify by email or webhook; fall back to log
                _notify_user(email=getattr(student, 'user', None) and getattr(student.user, 'email', None),
                             subject=subject, body=body,
                             webhook_payload={"student_id": student.id, "unapplied_count": len(unapplied)})
        return f"Processed reminders for {len(students)} students"


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

        # Send to configured admin email (MAIL_USERNAME) if present
        admin_email = Config.MAIL_USERNAME or None
        if admin_email:
            _send_email(to_addr=admin_email, subject="Monthly Placement Report", body=html_report, html=True)

        # Also POST to webhook if configured
        if getattr(Config, 'NOTIFICATION_WEBHOOK_URL', None):
            _post_webhook(Config.NOTIFICATION_WEBHOOK_URL, {"type": "monthly_report", "html": html_report})

        print("[MONTHLY REPORT] Generated and delivered (attempted)")
        return "Monthly report generated and delivered"


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

        # Ensure exports directory exists
        exports_dir = Config.EXPORTS_DIR if hasattr(Config, 'EXPORTS_DIR') else os.path.join(INSTANCE_DIR, 'exports')
        os.makedirs(exports_dir, exist_ok=True)
        filename = f"student_{student_id}_applications_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
        full_path = os.path.join(exports_dir, filename)
        with open(full_path, 'w', newline='', encoding='utf-8') as f:
            f.write(output.getvalue())

        # Notify student with download link if possible
        download_url = f"{Config.APP_BASE_URL}/api/students/exports/{filename}"
        student_email = getattr(student.user, 'email', None) if student and getattr(student, 'user', None) else None
        if student_email:
            subject = "Your application export is ready"
            body = f"Hi {student.name},\n\nYour applications export is ready: {download_url}\n\nRegards,\nPlacement Portal"
            _send_email(to_addr=student_email, subject=subject, body=body)

        if getattr(Config, 'NOTIFICATION_WEBHOOK_URL', None):
            _post_webhook(Config.NOTIFICATION_WEBHOOK_URL, {"type": "export_ready", "student_id": student_id, "file": filename, "url": download_url})

        print(f"[EXPORT DONE] Saved to {full_path}")
        return full_path


def _send_email(to_addr, subject, body, html=False):
    if not to_addr:
        return False
    if not getattr(Config, 'MAIL_USERNAME', None) or not getattr(Config, 'MAIL_PASSWORD', None):
        # Mail not configured; skip
        print(f"[EMAIL SKIP] Mail not configured, would send to {to_addr}")
        return False

    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = Config.MAIL_USERNAME
        msg['To'] = to_addr
        if html:
            msg.set_content('Please view this message in HTML-capable client')
            msg.add_alternative(body, subtype='html')
        else:
            msg.set_content(body)

        with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
            if Config.MAIL_USE_TLS:
                server.starttls()
            server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
            server.send_message(msg)
        print(f"[EMAIL SENT] to {to_addr}")
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False


def _post_webhook(url, payload: dict):
    if not url:
        return False
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.getcode()
        print(f"[WEBHOOK] Posted to {url} status={status}")
        return True
    except urllib.error.URLError as e:
        print(f"[WEBHOOK ERROR] {e}")
        return False


def _notify_user(email=None, subject=None, body=None, webhook_payload=None):
    sent = False
    if email:
        sent = _send_email(to_addr=email, subject=subject, body=body)
    if not sent and webhook_payload and getattr(Config, 'NOTIFICATION_WEBHOOK_URL', None):
        _post_webhook(Config.NOTIFICATION_WEBHOOK_URL, webhook_payload)
