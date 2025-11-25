from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import json

from . import models
from .database import engine
from .routers import auth, workouts, garmin, profile, coach, strava, upload, training_plans, predictions, health, onboarding, integrations, events, overtraining, hrv, race_prediction_enhanced, training_recommendations
from .core.config import settings

# Create database tables
# TODO: Replace with Alembic migrations for production
models.Base.metadata.create_all(bind=engine)


# Middleware to log request bodies for debugging
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/api/v1/training-plans/generate":
            try:
                body = await request.body()
                print(f"\n{'='*60}")
                print(f"🟡 MIDDLEWARE CAPTURE - Raw POST body to /api/v1/training-plans/generate:")
                print(f"Content-Length: {len(body)} bytes")
                print(f"Content-Type: {request.headers.get('content-type')}")
                if body:
                    try:
                        parsed = json.loads(body)
                        print(f"Parsed JSON: {json.dumps(parsed, indent=2)}")
                    except:
                        print(f"Raw: {body}")
                print(f"{'='*60}\n")
            except Exception as e:
                print(f"Error logging request: {e}")
        
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

# Add request logging middleware BEFORE CORS
app.add_middleware(RequestLoggingMiddleware)

# CORS configuration - MUST be added BEFORE any routes
# Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Cannot be True with wildcard origins
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=600,
    expose_headers=["*"],
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
    print(f"\n{'='*60}")
    print(f"🔴 VALIDATION ERROR - 422 UNPROCESSABLE ENTITY")
    print(f"Path: {request.url.path}")
    print(f"Method: {request.method}")
    print(f"Raw body: {await request.body()}")
    print(f"Errors: {exc.errors()}")
    print(f"{'='*60}\n")
    
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