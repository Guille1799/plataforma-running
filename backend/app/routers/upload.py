"""
File Upload Router
Handles manual workout file uploads (FIT, GPX, TCX)
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import tempfile
import os

from app.database import get_db
from app import models, crud
from app.security import verify_token
from app.core.config import settings
from app.services.file_upload_service import file_upload_service

router = APIRouter(prefix="/api/v1/upload", tags=["File Upload"])
security_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """Extract current user from JWT token."""
    token = credentials.credentials
    payload = verify_token(token, settings.secret_key, settings.algorithm)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id = int(payload.get("sub"))
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


@router.post("/workout")
async def upload_workout_file(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a workout file (FIT, GPX, or TCX).
    
    Parses the file and creates a workout entry.
    """
    # Check file format
    if not file_upload_service.is_supported(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format. Supported: {', '.join(file_upload_service.SUPPORTED_FORMATS)}"
        )
    
    # Save to temp file
    temp_path = None
    try:
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_path = temp_file.name
            content = await file.read()
            temp_file.write(content)
        
        # Parse and create workout
        workout = file_upload_service.create_workout_from_file(
            db, user_id, temp_path, file.filename
        )
        
        return {
            "message": "Workout uploaded successfully",
            "workout": {
                "id": workout.id,
                "sport_type": workout.sport_type,
                "start_time": workout.start_time.isoformat(),
                "distance_km": round(workout.distance_meters / 1000, 2),
                "duration_minutes": round(workout.duration_seconds / 60, 1)
            }
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse file: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )
    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


@router.get("/supported-formats")
def get_supported_formats():
    """Get list of supported file formats."""
    return {
        "formats": file_upload_service.SUPPORTED_FORMATS,
        "descriptions": {
            ".fit": "Garmin/Wahoo/Polar FIT files",
            ".gpx": "GPS Exchange Format (universal) - Auto-converts to FIT",
            ".tcx": "Training Center XML (Garmin)"
        },
        "auto_conversion": {
            "enabled": True,
            "feature": "GPX → FIT transparent conversion",
            "description": "GPX files are automatically converted to FIT format for advanced metric extraction"
        }
    }


@router.post("/test-gpx-conversion")
async def test_gpx_conversion(file: UploadFile = File(...)):
    """
    Test GPX to FIT conversion without creating workout.
    
    Returns conversion details and extracted metrics.
    Useful for validating Xiaomi/Amazfit GPX files.
    """
    from app.services.gpx_to_fit_converter import gpx_to_fit_converter
    import tempfile
    import os
    
    # Check if it's a GPX file
    if not file.filename.lower().endswith('.gpx'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only GPX files supported for this test endpoint"
        )
    
    temp_gpx = None
    temp_fit = None
    try:
        # Save GPX to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.gpx') as f:
            temp_gpx = f.name
            content = await file.read()
            f.write(content)
        
        # Read GPX content
        with open(temp_gpx, 'rb') as f:
            gpx_data = f.read()
        
        # Convert to FIT
        fit_data = gpx_to_fit_converter.convert_gpx_to_fit(gpx_data)
        
        # Save FIT to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.fit') as f:
            temp_fit = f.name
            f.write(fit_data)
        
        # Parse FIT to extract metrics
        workout_data = file_upload_service.parse_file(temp_fit, file.filename)
        
        return {
            "conversion_success": True,
            "input": {
                "format": "GPX",
                "size_bytes": len(gpx_data),
                "filename": file.filename
            },
            "output": {
                "format": "FIT",
                "size_bytes": len(fit_data),
                "header": fit_data[0:14].hex()
            },
            "extracted_metrics": {
                "sport_type": workout_data.get("sport_type"),
                "distance_km": round(workout_data.get("distance_meters", 0) / 1000, 2),
                "duration_minutes": round(workout_data.get("duration_seconds", 0) / 60, 1),
                "avg_heart_rate": workout_data.get("avg_heart_rate"),
                "max_heart_rate": workout_data.get("max_heart_rate"),
                "calories": workout_data.get("calories"),
                "elevation_gain": workout_data.get("elevation_gain"),
                "avg_speed_kmh": round(workout_data.get("avg_speed_ms", 0) * 3.6, 1) if workout_data.get("avg_speed_ms") else None
            },
            "message": "GPX successfully converted to FIT and parsed. Ready for workout creation."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Conversion test failed: {str(e)}"
        )
    finally:
        # Cleanup temp files
        if temp_gpx and os.path.exists(temp_gpx):
            os.unlink(temp_gpx)
        if temp_fit and os.path.exists(temp_fit):
            os.unlink(temp_fit)

