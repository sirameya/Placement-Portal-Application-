"""
database.py — defines the single shared `db` object used everywhere.

Why is this its own file instead of living in models.py or app.py?
Because BOTH of those files need to import `db`, and if `db` lived
inside either one of them, we'd risk a circular import (A imports B,
B imports A). Keeping it in its own tiny neutral file avoids that.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
