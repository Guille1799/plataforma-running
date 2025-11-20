from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from . import models
from .database import engine
from .routers import auth, workouts, garmin, profile, coach, strava, upload, training_plans, predictions, health, onboarding, integrations, events, overtraining, hrv, race_prediction_enhanced, training_recommendations
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

# Enhanced CORS configuration - allow Vercel and localhost
class CORSMiddlewareEnhanced(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        origin = request.headers.get("origin")
        
        # Check if origin is allowed
        allowed = False
        if origin:
            # Allow localhost
            if origin.startswith("http://localhost") or origin.startswith("http://127.0.0.1"):
                allowed = True
            # Allow Vercel (production and preview)
            elif origin.endswith(".vercel.app") or "vercel.app" in origin:
                allowed = True
        
        # Handle preflight requests
        if request.method == "OPTIONS":
            if allowed:
                return Response(
                    status_code=200,
                    headers={
                        "Access-Control-Allow-Origin": origin,
                        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
                        "Access-Control-Allow-Credentials": "true",
                    }
                )
            else:
                return Response(status_code=400)
        
        # Process the request
        response = await call_next(request)
        
        # Add CORS headers to response
        if allowed:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response

# Add the enhanced CORS middleware
app.add_middleware(CORSMiddlewareEnhanced)

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