"""
app.py — the entry point that starts the Flask backend.
Run with: python app.py

Creates instance/placement_portal.db programmatically via db.create_all()
(no manual DB Browser creation, per the project statement).
"""

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash

from controllers.config import Config
from controllers.database import db
from controllers.models import User
from services.cache import cache

from controllers.auth import auth_bp
from controllers.students import students_bp
from controllers.companies import companies_bp
from controllers.drives import drives_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
CORS(app)                # lets the Vue frontend (different port) call this API
JWTManager(app)           # enables @role_required / get_jwt_identity() everywhere
cache.init_app(app)       # Redis-backed caching (see services/cache.py)

# "Plugs in" every blueprint's routes under their url_prefix
app.register_blueprint(auth_bp)
app.register_blueprint(students_bp)
app.register_blueprint(companies_bp)
app.register_blueprint(drives_bp)


def create_tables_and_seed_admin():
    """Creates all tables, then seeds ONE admin account if none exists —
    matching 'Admin is a pre-existing superuser, no admin registration'."""
    db.create_all()

    if not User.query.filter_by(role="admin").first():
        admin = User(
            email="admin@placementportal.com",
            password_hash=generate_password_hash("admin123"),  # CHANGE before submitting!
            role="admin",
        )
        db.session.add(admin)
        db.session.commit()
        print("Seeded default admin: admin@placementportal.com / admin123")


@app.route("/")
def health_check():
    return {"status": "Placement Portal API is running"}


if __name__ == "__main__":
    with app.app_context():
        create_tables_and_seed_admin()
    app.run(debug=True, port=5000)
