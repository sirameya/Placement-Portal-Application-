"""
cache.py — a single shared Flask-Caching instance (backed by Redis).
Lives in services/ since caching is an infrastructure concern, not a
route or a model. Defined here (not in app.py) so any controller can
import it without circular imports.
"""

from flask_caching import Cache

cache = Cache()
