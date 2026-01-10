"""
routers/integrations.py - Device integration management endpoints
Handles configuration and management of multiple connected devices
"""
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import logging

from ..database import get_db
from .. import models
from ..schemas import (
    DeviceIntegrationCreate,
    DeviceIntegrationUpdate,
    DeviceIntegrationList,
    DeviceSyncStatus,
    DeviceIntegration,
    DeviceSyncConfig,
)
from ..dependencies.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/profile/integrations", tags=["integrations"])

# Device type configuration defaults
DEVICE_DEFAULTS = {
    "garmin": {
        "sync_interval_hours": 1,
        "name_template": "Garmin {model}",
    },
    "xiaomi": {
        "sync_interval_hours": 2,
        "name_template": "Xiaomi {model}",
    },
    "strava": {
        "sync_interval_hours": 2,
        "name_template": "Strava",
    },
    "apple": {
        "sync_interval_hours": 1,
        "name_template": "Apple Health",
    },
    "manual": {
        "sync_interval_hours": 24,
        "name_template": "Manual Entry",
    },
}


def parse_devices_config(devices_json: Optional[str]) -> dict:
    """Parse devices_configured JSON from database."""
    if not devices_json:
        return {}
    try:
        return json.loads(devices_json) if isinstance(devices_json, str) else devices_json
    except json.JSONDecodeError:
        logger.error(f"Failed to parse devices_configured: {devices_json}")
        return {}


def parse_sync_config(sync_config_json: Optional[str]) -> dict:
    """Parse device_sync_config JSON from database."""
    if not sync_config_json:
        return {}
    try:
        return json.loads(sync_config_json) if isinstance(sync_config_json, str) else sync_config_json
    except json.JSONDecodeError:
        logger.error(f"Failed to parse device_sync_config: {sync_config_json}")
        return {}


def build_device_integration(device_id: str, device_type: str, sync_config: dict, is_primary: bool) -> DeviceIntegration:
    """Build DeviceIntegration from stored data."""
    config = sync_config.get(device_id, {})
    
    return DeviceIntegration(
        device_id=device_id,
        device_type=device_type,
        device_name=config.get("device_name", f"{device_type.capitalize()} Device"),
        sync_config=DeviceSyncConfig(
            sync_interval_hours=config.get("sync_interval_hours", DEVICE_DEFAULTS.get(device_type, {}).get("sync_interval_hours", 1)),
            auto_sync_enabled=config.get("auto_sync_enabled", True),
            last_sync=config.get("last_sync"),
            next_sync=config.get("next_sync"),
            sync_error=config.get("sync_error"),
        ),
        is_primary=is_primary,
        connected_at=datetime.fromisoformat(config.get("connected_at", datetime.utcnow().isoformat())),
    )


@router.get("", response_model=DeviceIntegrationList)
async def list_integrations(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all configured device integrations for the user.
    
    Returns:
        DeviceIntegrationList with devices_configured list and sync status
    """
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    devices_config = parse_devices_config(user.devices_configured)
    sync_config = parse_sync_config(user.device_sync_config)
    
    # Build list of DeviceIntegration objects
    devices = []
    for device_id, device_type in devices_config.items():
        device = build_device_integration(device_id, device_type, sync_config, device_id == user.primary_device)
        devices.append(device)
    
    return DeviceIntegrationList(
        primary_device=user.primary_device or "manual",
        devices_enabled=user.device_sync_enabled or False,
        devices=devices,
    )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=DeviceIntegration)
async def add_integration(
    request: DeviceIntegrationCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add a new device integration for the user.
    
    Args:
        request: DeviceIntegrationCreate with device_type and configuration
        
    Returns:
        The newly created DeviceIntegration
        
    Raises:
        400: Invalid device type
        409: Device already configured
    """
    # Validate device type
    if request.device_type not in DEVICE_DEFAULTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid device_type. Must be one of: {', '.join(DEVICE_DEFAULTS.keys())}"
        )
    
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    devices_config = parse_devices_config(user.devices_configured)
    sync_config = parse_sync_config(user.device_sync_config)
    
    # Generate unique device ID
    existing_count = sum(1 for dt in devices_config.values() if dt == request.device_type)
    device_id = f"{request.device_type}_{existing_count + 1}" if existing_count > 0 else request.device_type
    
    # Check if already exists
    if device_id in devices_config:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Device {device_id} already configured"
        )
    
    # Add device to config
    devices_config[device_id] = request.device_type
    sync_config[device_id] = {
        "device_name": request.device_name,
        "sync_interval_hours": request.sync_interval_hours,
        "auto_sync_enabled": request.auto_sync_enabled,
        "last_sync": None,
        "next_sync": None,
        "sync_error": None,
        "connected_at": datetime.utcnow().isoformat(),
    }
    
    # If first device or user marks as primary, set as primary
    if not user.primary_device or user.primary_device == "manual":
        user.primary_device = device_id
    
    # Update user
    user.devices_configured = json.dumps(devices_config)
    user.device_sync_config = json.dumps(sync_config)
    if not user.device_sync_enabled:
        user.device_sync_enabled = True
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"User {user.id} added device integration: {device_id}")
    
    return build_device_integration(device_id, request.device_type, sync_config, device_id == user.primary_device)


@router.put("/{device_id}", response_model=DeviceIntegration)
async def update_integration(
    device_id: str,
    request: DeviceIntegrationUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update device integration settings.
    
    Args:
        device_id: The device ID to update
        request: DeviceIntegrationUpdate with new settings
        
    Returns:
        The updated DeviceIntegration
        
    Raises:
        404: Device not found
    """
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    devices_config = parse_devices_config(user.devices_configured)
    sync_config = parse_sync_config(user.device_sync_config)
    
    if device_id not in devices_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device {device_id} not found"
        )
    
    device_type = devices_config[device_id]
    current_config = sync_config.get(device_id, {})
    
    # Update fields
    if request.device_name is not None:
        current_config["device_name"] = request.device_name
    
    if request.sync_interval_hours is not None:
        current_config["sync_interval_hours"] = request.sync_interval_hours
    
    if request.auto_sync_enabled is not None:
        current_config["auto_sync_enabled"] = request.auto_sync_enabled
    
    sync_config[device_id] = current_config
    
    # Save to database
    user.device_sync_config = json.dumps(sync_config)
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"User {user.id} updated device: {device_id}")
    
    return build_device_integration(device_id, device_type, sync_config, device_id == user.primary_device)


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_integration(
    device_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Remove a device integration.
    
    Args:
        device_id: The device ID to remove
        
    Raises:
        404: Device not found
        400: Cannot remove primary device
    """
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    devices_config = parse_devices_config(user.devices_configured)
    sync_config = parse_sync_config(user.device_sync_config)
    
    if device_id not in devices_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device {device_id} not found"
        )
    
    # Cannot remove primary device
    if device_id == user.primary_device and len(devices_config) == 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove the primary device when it's the only device"
        )
    
    # Remove from configs
    del devices_config[device_id]
    if device_id in sync_config:
        del sync_config[device_id]
    
    # If removed device was primary, select new primary
    if device_id == user.primary_device and devices_config:
        new_primary = next(iter(devices_config.keys()))
        user.primary_device = new_primary
        logger.info(f"User {user.id} primary device changed to: {new_primary}")
    
    # If no devices left, disable syncing
    if not devices_config:
        user.device_sync_enabled = False
        user.primary_device = "manual"
    
    user.devices_configured = json.dumps(devices_config) if devices_config else None
    user.device_sync_config = json.dumps(sync_config) if sync_config else None
    
    db.add(user)
    db.commit()
    
    logger.info(f"User {user.id} removed device: {device_id}")


@router.get("/{device_id}/sync-status", response_model=DeviceSyncStatus)
async def get_sync_status(
    device_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get sync status for a specific device.
    
    Args:
        device_id: The device ID to check
        
    Returns:
        DeviceSyncStatus with last sync time and status
        
    Raises:
        404: Device not found
    """
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    devices_config = parse_devices_config(user.devices_configured)
    sync_config = parse_sync_config(user.device_sync_config)
    
    if device_id not in devices_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device {device_id} not found"
        )
    
    config = sync_config.get(device_id, {})
    
    # Determine sync status
    if config.get("sync_error"):
        sync_status = "error"
    elif config.get("last_sync") and not config.get("next_sync"):
        sync_status = "success"
    else:
        sync_status = "idle"
    
    return DeviceSyncStatus(
        device_id=device_id,
        last_sync=config.get("last_sync"),
        next_sync=config.get("next_sync"),
        sync_status=sync_status,
        message=config.get("sync_error"),
    )


@router.post("/{device_id}/set-primary")
async def set_primary_device(
    device_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Set a device as the primary device for personalization.
    
    Args:
        device_id: The device ID to set as primary
        
    Returns:
        Updated user with new primary device
        
    Raises:
        404: Device not found
    """
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    devices_config = parse_devices_config(user.devices_configured)
    
    if device_id not in devices_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device {device_id} not found"
        )
    
    user.primary_device = device_id
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"User {user.id} set primary device to: {device_id}")
    
    return {
        "message": f"Primary device set to {device_id}",
        "primary_device": device_id,
    }


@router.post("/sync-all")
async def sync_all_devices(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Trigger synchronization for all user devices.
    
    This endpoint initiates sync jobs for all configured devices.
    Actual sync is performed asynchronously.
    
    Returns:
        Status of sync initiation for each device
    """
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if not user.device_sync_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device sync is disabled"
        )
    
    devices_config = parse_devices_config(user.devices_configured)
    sync_config = parse_sync_config(user.device_sync_config)
    
    if not devices_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No devices configured"
        )
    
    # Update next_sync for all devices (would trigger actual sync in background job)
    sync_results = {}
    for device_id in devices_config.keys():
        config = sync_config.get(device_id, {})
        if config.get("auto_sync_enabled", True):
            config["next_sync"] = datetime.utcnow().isoformat()
            sync_config[device_id] = config
            sync_results[device_id] = "queued"
        else:
            sync_results[device_id] = "skipped_disabled"
    
    user.device_sync_config = json.dumps(sync_config)
    db.add(user)
    db.commit()
    
    logger.info(f"User {user.id} initiated manual sync for all devices")
    
    return {
        "message": "Sync initiated for all devices",
        "results": sync_results,
    }
