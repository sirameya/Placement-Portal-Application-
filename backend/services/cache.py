"""
cache.py — a single shared Flask-Caching instance (backed by Redis).
This module provides a SafeCache wrapper that falls back to an in-memory
SimpleCache when Redis is not available (useful for development on
machines without Redis). Controllers import `cache` and use it the
same way as a normal Flask-Caching `Cache` instance.
"""

import logging
from flask_caching import Cache

log = logging.getLogger(__name__)


class SafeCache:
	"""Wrapper around Flask-Caching that falls back to SimpleCache when
	the configured Redis cache cannot be reached. This prevents connection
	refused errors when Redis isn't running locally.
	"""

	def __init__(self):
		self._cache = Cache()

	def init_app(self, app):
		# Initialize with the app config first; if Redis backend later
		# raises connection errors when used, attempt to reconfigure.
		try:
			self._cache.init_app(app)
			# Probe the cache to force a connection attempt (some backends
			# only connect on first use). Use a harmless set operation.
			try:
				self._cache.set('_cache_probe', '1', timeout=1)
			except Exception as e:
				log.warning('Redis cache unavailable, falling back to SimpleCache: %s', e)
				app.config['CACHE_TYPE'] = 'SimpleCache'
				self._cache.init_app(app)
		except Exception as e:
			log.warning('Cache initialization failed, using SimpleCache: %s', e)
			app.config['CACHE_TYPE'] = 'SimpleCache'
			self._cache.init_app(app)

	def cached(self, *args, **kwargs):
		"""Delegate cached decorator to the currently active cache backend."""
		return getattr(self._cache, 'cached')(*args, **kwargs)

	def __getattr__(self, name):
		return getattr(self._cache, name)


cache = SafeCache()
