from flask import Flask
from controllers.config import Config
from controllers.database import db
from controllers.models import CompanyProfile, User

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    comps = CompanyProfile.query.all()
    print('TOTAL_COMPANIES', len(comps))
    pend = CompanyProfile.query.filter_by(approval_status='pending').all()
    print('PENDING', len(pend))
    for c in pend:
        user = User.query.get(c.user_id)
        print(c.id, c.company_name, c.approval_status, user.email if user else None)
