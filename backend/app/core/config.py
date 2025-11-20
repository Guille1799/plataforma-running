"""
Pydantic settings for application configuration.

Loads environment variables and validates them on startup.
"""
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""
    
    # Database
    database_url: str = "sqlite:///./runcoach.db"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Application
    debug: bool = False
    environment: str = "development"
    
    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000,http://127.0.0.1:8000,https://plataforma-running.vercel.app,https://plataforma-running-c0wt0v6c3-guilledummies-projects.vercel.app"
    
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
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env
    
    def get_allowed_origins(self) -> list[str]:
        """Parse allowed origins from comma-separated string and add wildcard for Vercel."""
        origins = [origin.strip() for origin in self.allowed_origins.split(",")]
        # Allow all Vercel preview URLs by adding a broad pattern
        # Note: This is a workaround - CORSMiddleware doesn't support regex patterns
        # So we need to add the wildcard pattern manually
        print(f"DEBUG: CORS allowed origins (configured): {origins}")
        return origins


settings = Settings()
