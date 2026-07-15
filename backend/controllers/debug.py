"""
debug.py — small diagnostic endpoints for backend health and SMTP testing.
"""

from flask import Blueprint, jsonify
from services.tasks import _send_email, send_daily_reminders, send_monthly_report
from controllers.config import Config

debug_bp = Blueprint("debug", __name__, url_prefix="/api/debug")


@debug_bp.route("/mail-status", methods=["GET"])
def mail_status():
    return jsonify({
        "mail_server": Config.MAIL_SERVER,
        "mail_port": Config.MAIL_PORT,
        "mail_username": bool(Config.MAIL_USERNAME),
        "mail_password": bool(Config.MAIL_PASSWORD),
        "admin_email": Config.ADMIN_EMAIL,
        "mail_ready": bool(Config.MAIL_USERNAME and Config.MAIL_PASSWORD),
    })


@debug_bp.route("/mail-test", methods=["POST"])
def mail_test():
    if not Config.MAIL_USERNAME or not Config.MAIL_PASSWORD:
        return jsonify({"error": "Mail credentials are not configured."}), 400

    to_addr = Config.ADMIN_EMAIL or Config.MAIL_USERNAME
    success = _send_email(
        to_addr=to_addr,
        subject="Placement Portal SMTP test",
        body="This is a test email from Placement Portal.",
    )
    if success:
        return jsonify({"message": "SMTP test email sent.", "to": to_addr}), 200
    return jsonify({"error": "Failed to send SMTP test email. Check backend logs."}), 500


@debug_bp.route("/daily-reminder", methods=["POST"])
def trigger_daily_reminder():
    if not Config.MAIL_USERNAME or not Config.MAIL_PASSWORD:
        return jsonify({"error": "Mail credentials are not configured."}), 400

    result = send_daily_reminders.delay()
    return jsonify({"message": "Daily reminder task queued.", "task_id": result.id}), 202


@debug_bp.route("/monthly-report", methods=["POST"])
def trigger_monthly_report():
    if not Config.MAIL_USERNAME or not Config.MAIL_PASSWORD:
        return jsonify({"error": "Mail credentials are not configured."}), 400

    result = send_monthly_report.delay()
    return jsonify({"message": "Monthly report task queued.", "task_id": result.id}), 202
