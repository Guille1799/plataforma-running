"""
rate_limiter.py - Centralized rate limiter configuration

Note: The limiter instance must be attached to app.state.limiter in main.py
for the decorators to work correctly.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Global limiter instance - will be attached to app.state in main.py
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/hour"],  # Default rate limit for all endpoints
    storage_uri="memory://"  # Use in-memory storage (no Redis required)
)
