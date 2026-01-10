"""
Pydantic settings for application configuration.

Loads environment variables and validates them on startup.
"""

import secrets
import warnings
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Database
    database_url: str = "sqlite:///./runcoach.db"

    # Security
    secret_key: Optional[str] = Field(
        default=None,
        description="Secret key for JWT token signing. REQUIRED in production via SECRET_KEY environment variable."
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Application
    debug: bool = False
    environment: str = "development"

    # CORS
    allowed_origins: str = (
        "http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000,https://plataforma-running.vercel.app,https://plataforma-running-c0wt0v6c3-guilledummies-projects.vercel.app"
    )

    # API Keys
    anthropic_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None  # Groq AI for coaching

    # Strava Integration
    strava_client_id: Optional[str] = None
    strava_client_secret: Optional[str] = None
    strava_redirect_uri: str = "http://localhost:3000/auth/strava/callback"

    # Google Fit Integration
    google_fit_client_id: Optional[str] = None
    google_fit_client_secret: Optional[str] = None
    google_fit_redirect_uri: str = "http://localhost:3000/auth/google-fit/callback"

    # Supabase (legacy - optional)
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None

    # Redis (for Celery)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_url: Optional[str] = None

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    @field_validator("secret_key", mode="before")
    @classmethod
    def validate_secret_key(cls, v: Optional[str], info) -> str:
        """Validate and generate secret key if needed.
        
        In development: Generate a random key if not provided (with warning).
        In production: Require SECRET_KEY to be explicitly set via environment variable.
        
        Args:
            v: Secret key value from environment or None
            info: Validation info containing environment settings
            
        Returns:
            Validated secret key string
            
        Raises:
            ValueError: If SECRET_KEY is not set or is insecure in production
        """
        environment = info.data.get("environment", "development")
        
        # Common insecure secret key values to reject
        INSECURE_SECRET_KEYS = [
            "your-secret-key-change-in-production",
            "secret",
            "password",
            "admin",
            "12345678",
            "changeme",
            "default",
            "test",
            "",
        ]
        
        # In production, SECRET_KEY is REQUIRED and must be secure
        if environment == "production":
            if not v or v.strip() == "":
                raise ValueError(
                    "CRITICAL SECURITY ERROR: SECRET_KEY is required in production environment.\n"
                    "Set SECRET_KEY environment variable before starting the application.\n"
                    "Generate a secure key with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
                )
            
            # Check for insecure values
            if v.strip().lower() in [key.lower() for key in INSECURE_SECRET_KEYS]:
                raise ValueError(
                    "CRITICAL SECURITY ERROR: SECRET_KEY is set to an insecure value.\n"
                    "Generate a secure key and set SECRET_KEY environment variable:\n"
                    "python -c \"import secrets; print(secrets.token_urlsafe(32))\""
                )
            
            # Require minimum length in production (at least 32 characters)
            if len(v.strip()) < 32:
                raise ValueError(
                    f"CRITICAL SECURITY ERROR: SECRET_KEY is too short ({len(v.strip())} chars). "
                    "Minimum length is 32 characters for production.\n"
                    "Generate a secure key with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
                )
            
            return v
        
        # In development, generate a random key if not provided
        if not v or v.strip() == "":
            generated_key = secrets.token_urlsafe(32)
            warnings.warn(
                f"SECRET_KEY not set in development. Generated temporary key: {generated_key[:20]}...\n"
                "This key will change on each restart. Set SECRET_KEY environment variable for consistency.",
                UserWarning,
                stacklevel=2
            )
            return generated_key
        
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env

    def get_allowed_origins(self) -> list[str]:
        """Parse allowed origins from comma-separated string.
        
        Returns list of explicitly allowed origins. Vercel preview URLs (*.vercel.app)
        are validated dynamically by VercelCORSMiddleware.
        """
        origins = [origin.strip() for origin in self.allowed_origins.split(",")]
        
        # Filter out localhost in production
        if self.environment == "production":
            origins = [origin for origin in origins if not origin.startswith("http://localhost") and not origin.startswith("http://127.0.0.1")]
        
        return origins


# Validate settings on import (Pydantic will call validators)
settings = Settings()

# Post-initialization validation: Ensure SECRET_KEY is never None or empty in production
if settings.environment == "production":
    if not settings.secret_key or not settings.secret_key.strip():
        raise RuntimeError(
            "CRITICAL SECURITY ERROR: SECRET_KEY must be explicitly set in production environment.\n"
            "The application cannot start without a secure SECRET_KEY.\n"
            "Set SECRET_KEY environment variable before starting the application.\n"
            "Generate a secure key with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
        )
    
    # Additional validation: Ensure SECRET_KEY meets minimum security requirements
    if len(settings.secret_key.strip()) < 32:
        raise RuntimeError(
            f"CRITICAL SECURITY ERROR: SECRET_KEY is too short ({len(settings.secret_key.strip())} chars). "
            "Minimum length is 32 characters for production.\n"
            "Generate a secure key with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
        )
