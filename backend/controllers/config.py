"""
config.py — every setting the app needs, in ONE place, instead of
scattered across files. Other files import `Config` and read from it.
"""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # .../backend/controllers
INSTANCE_DIR = os.path.join(BASE_DIR, "..", "instance")


class Config:
    # --- Database ---
    # Lives in backend/instance/ — Flask's conventional folder for files
    # that shouldn't be committed to git (databases, secrets, uploads).
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(INSTANCE_DIR, 'placement_portal.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- JWT (login tokens) ---
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret-change-this")
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 8  # 8 hours, in seconds

    # --- Celery (background jobs) + Redis (broker + cache) ---
    CELERY_BROKER_URL = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = "redis://localhost:6379/1"
    CACHE_DEFAULT_TIMEOUT = 300

    # --- Mail (for reminders / reports) ---
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")

    # Public base URL used in notifications (change in production)
    APP_BASE_URL = os.environ.get("APP_BASE_URL", "http://localhost:5000")

    # Optional webhook to POST notifications to (JSON payload)
    NOTIFICATION_WEBHOOK_URL = os.environ.get("NOTIFICATION_WEBHOOK_URL", "")

    # Local storage paths (inside instance/)
    EXPORTS_DIR = os.path.join(INSTANCE_DIR, "exports")
    UPLOADS_DIR = os.path.join(INSTANCE_DIR, "uploads")
