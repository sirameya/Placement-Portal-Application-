"""
celery_app.py — sets up Celery, which runs jobs OUTSIDE the normal
request/response cycle (e.g. emailing 500 students shouldn't make a
user wait for a page to load). Redis is the "to-do list" workers check
for pending jobs.

To run background jobs, alongside `python app.py` you also need:
    1. redis-server
    2. celery -A services.celery_app worker --loglevel=info
    3. celery -A services.celery_app beat --loglevel=info   (for scheduled jobs)
"""

from celery import Celery
from celery.schedules import crontab
from controllers.config import Config

celery = Celery(
    "placement_portal",
    broker=Config.CELERY_BROKER_URL,
    backend=Config.CELERY_RESULT_BACKEND,
    include=["services.tasks"],
)

celery.conf.beat_schedule = {
    "daily-application-reminders": {
        "task": "services.tasks.send_daily_reminders",
        "schedule": crontab(hour=18, minute=0),  # every day at 6 PM
    },
    "monthly-activity-report": {
        "task": "services.tasks.send_monthly_report",
        "schedule": crontab(day_of_month=1, hour=6, minute=0),  # 1st of every month
    },
}
celery.conf.timezone = "Asia/Kolkata"
