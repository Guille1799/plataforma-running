from fastapi import FastAPI, Request
from fastapi.security import HTTPBearer
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
import json
import logging

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# Configure logging
logger = logging.getLogger(__name__)

from . import models
from .database import engine
from .routers import auth, workouts, garmin, profile, coach, strava, upload, training_plans, predictions, health, onboarding, integrations, events, overtraining, hrv, race_prediction_enhanced, training_recommendations
from .core.config import settings
from .middleware.cors import VercelCORSMiddleware
from .utils.rate_limiter import limiter

# Security validation: SECRET_KEY is validated in config.py during Settings initialization
# In production, SECRET_KEY must be explicitly set via environment variable (no defaults)
# If we reach here and environment is production, SECRET_KEY is guaranteed to be secure
# In development, a temporary key may be generated if not provided (with warning)

# Additional startup validation: Ensure SECRET_KEY is never None in production
if settings.environment == "production" and (not settings.secret_key or not settings.secret_key.strip()):
    raise RuntimeError(
        "CRITICAL SECURITY ERROR: Application cannot start without SECRET_KEY in production.\n"
        "Set SECRET_KEY environment variable before starting the application.\n"
        "Generate a secure key with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
    )

# Database table creation
# 
# IMPORTANT: Alembic migrations are the recommended way to manage database schema.
# 
# For NEW deployments:
#   1. Run migrations: `cd backend && alembic upgrade head`
#   2. This will create all tables from migrations
# 
# For EXISTING databases (already using create_all):
#   1. Mark current state as migrated: `cd backend && alembic stamp head`
#   2. Future changes: Generate new migrations with `alembic revision --autogenerate -m "Description"`
# 
# Development mode (convenience fallback):
#   - Auto-creates tables if they don't exist (for quick local setup)
#   - For production-like testing, use Alembic migrations instead
# 
# Production mode:
#   - ALWAYS use Alembic migrations: `cd backend && alembic upgrade head`
#   - Never use create_all() in production
#   - Run migrations BEFORE starting the server
if settings.environment == "development":
    # Only auto-create tables in development for convenience
    # For production-like testing, comment this out and use: `alembic upgrade head`
    logger.info("Development mode: Auto-creating database tables if they don't exist")
    logger.info("Note: For production-like setup, use 'alembic upgrade head' instead")
    models.Base.metadata.create_all(bind=engine)
else:
    logger.info("Production mode: Using Alembic migrations for database schema management")
    logger.info("Ensure migrations are applied: Run 'cd backend && alembic upgrade head'")


# Middleware to log request bodies for debugging
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: StarletteRequest, call_next):
        if request.url.path == "/api/v1/training-plans/generate":
            try:
                body = await request.body()
                logger.debug(
                    "Training plan generation request",
                    extra={
                        "path": request.url.path,
                        "content_length": len(body),
                        "content_type": request.headers.get("content-type"),
                    }
                )
                if body:
                    try:
                        parsed = json.loads(body)
                        logger.debug(f"Request body (parsed): {json.dumps(parsed, indent=2)}")
                    except Exception:
                        logger.debug(f"Request body (raw): {body}")
            except Exception as e:
                logger.error(f"Error logging request: {e}", exc_info=True)
        
        # Pass the request to the next middleware
        response = await call_next(request)
        return response

security = HTTPBearer()

# Create FastAPI app
app = FastAPI(
    title="RunCoach AI API",
    description="AI-powered sports coaching platform",
    version="0.1.0",
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
    }
)

# Attach rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add request logging middleware BEFORE CORS
app.add_middleware(RequestLoggingMiddleware)

# CORS configuration - MUST be added BEFORE any routes
# Custom middleware that validates Vercel preview URLs dynamically
allowed_origins = settings.get_allowed_origins()
app.add_middleware(
    VercelCORSMiddleware,
    allowed_origins=allowed_origins,
    allow_credentials=False,  # Can be True if needed for cookies, but requires specific origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    max_age=600,
)

# Include routers
app.include_router(auth.router, tags=["Authentication"])
app.include_router(onboarding.router, tags=["Onboarding"])
app.include_router(integrations.router, tags=["Device Integrations"])
app.include_router(workouts.router, tags=["Workouts"])
app.include_router(garmin.router, tags=["Garmin Connect"])
app.include_router(strava.router, tags=["Strava"])
app.include_router(upload.router, tags=["File Upload"])
app.include_router(profile.router, tags=["Athlete Profile"])
app.include_router(coach.router, tags=["AI Coach"])
app.include_router(training_plans.router, tags=["Training Plans"])
app.include_router(predictions.router, tags=["Race Predictions"])
app.include_router(health.router, tags=["Health Metrics"])
app.include_router(overtraining.router, tags=["Overtraining Detection"])
app.include_router(hrv.router, tags=["HRV Analysis"])
app.include_router(race_prediction_enhanced.router, tags=["Enhanced Race Predictions"])
app.include_router(training_recommendations.router, tags=["Training Recommendations"])
app.include_router(events.router, tags=["Events"])


@app.get("/", tags=["Health"])
def read_root() -> dict[str, str]:
    """Health check endpoint.
    
    Returns:
        Simple status message
    """
    return {
        "status": "ok",
        "message": "RunCoach AI API is running",
        "environment": settings.environment
    }


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Detailed health check endpoint.
    
    Returns:
        Health status with service information
    """
    return {
        "status": "healthy",
        "service": "RunCoach AI API",
        "version": "0.1.0"
    }


# Global exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Log validation errors in detail for debugging."""
    body = await request.body()
    logger.warning(
        "Validation error - 422 Unprocessable Entity",
        extra={
            "path": request.url.path,
            "method": request.method,
            "body": body.decode("utf-8") if body else None,
            "errors": exc.errors(),
        }
    )
    
    # Improve error messages for common issues
    errors = exc.errors()
    detail = []
    
    for error in errors:
        field = error.get('loc', ['unknown'])[-1]
        msg = error.get('msg', 'Invalid value')
        input_val = error.get('input', 'N/A')
        
        # Friendly messages for common validation errors
        if field == 'weeks' and 'less than or equal' in msg:
            detail.append(f"Maximum 24 weeks allowed (you sent: {input_val} weeks)")
        elif field == 'weeks' and 'greater than or equal' in msg:
            detail.append(f"Minimum 4 weeks required (you sent: {input_val} weeks)")
        else:
            detail.append(f"{field}: {msg}")
    
    return JSONResponse(
        status_code=422,
        content={"detail": detail if detail else [str(e) for e in errors]},
    )