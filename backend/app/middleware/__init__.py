"""
middleware package - Custom middleware for the application
"""

from .cors import VercelCORSMiddleware

__all__ = ["VercelCORSMiddleware"]
