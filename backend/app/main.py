from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer

from . import models
from .database import engine
from .routers import auth, workouts, garmin, profile, coach, strava, upload, training_plans, predictions, health, onboarding, integrations, events
from .core.config import settings

# Create database tables
# TODO: Replace with Alembic migrations for production
models.Base.metadata.create_all(bind=engine)

security = HTTPBearer()

app = FastAPI(
    title="RunCoach AI API",
    description="AI-powered sports coaching platform",
    version="0.1.0",
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
    }
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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