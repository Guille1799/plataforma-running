"""
permissions.py - Helper functions for resource ownership and permission validation
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import Any


def verify_resource_ownership(
    resource: Any,
    user_id: int,
    resource_name: str = "Resource"
) -> None:
    """Verify that a resource belongs to the specified user.
    
    Args:
        resource: Database model instance (must have user_id attribute)
        user_id: ID of the user who should own the resource
        resource_name: Name of the resource for error messages (default: "Resource")
        
    Raises:
        HTTPException: 404 if resource doesn't exist or doesn't belong to user
    """
    if resource is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource_name} not found"
        )
    
    if not hasattr(resource, 'user_id'):
        raise ValueError(f"Resource does not have 'user_id' attribute")
    
    if resource.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You don't have permission to access this {resource_name.lower()}"
        )
