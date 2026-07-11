"""
decorators.py — small reusable helpers shared across controllers.

role_required() wraps a route function and checks the JWT's role claim
BEFORE the route's own code runs. Without this, we'd copy-paste the same
role-check into every single admin/company/student route.
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def role_required(*allowed_roles):
    """
    Usage:
        @students_bp.route("/profile")
        @role_required("student")
        def profile():
            ...

    If the logged-in user's role isn't in allowed_roles, returns 403
    Forbidden BEFORE the route function ever runs.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("role") not in allowed_roles:
                return jsonify({"error": "You do not have permission to do this"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
