import os
from flask import Flask
from flask_cors import Cors
from flask_jwt_extended import JWTManager
from controllers.config import Config
from controllers.database import db
from controllers.models import User
import bcrypt

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable Cross-Origin Requests for Vue frontend
    Cors(app)

    # Initialize DB & JWT
    db.init_app(app)
    jwt = JWTManager(app)

    # Register blueprints (APIs) here later
    # from controllers.authentication_apis import auth_bp
    # app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # Ensure instance folder exists and create tables programmatically
    with app.app_context():
        os.makedirs(app.instance_path, exist_ok=True)
        db.create_all()

        # Seed an admin user automatically if none exists
        admin_exists = User.query.filter_by(role='admin').first()
        if not admin_exists:
            hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            admin = User(email='admin@institute.edu', password_hash=hashed_password, role='admin')
            db.session.add(admin)
            db.session.commit()
            print("Database initialized and Superuser Admin seeded successfully.")

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
