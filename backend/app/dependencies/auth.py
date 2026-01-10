"""
dependencies/auth.py - Common authentication dependency for FastAPI routers

This module provides a centralized get_current_user dependency that can be used
across all routers to eliminate code duplication.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .. import crud, models, security
from ..database import get_db
from ..core.config import settings

security_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    """Get current authenticated user from JWT token.
    
    This is a common dependency that should be used in all routers that require
    authentication. It validates the JWT token and returns the User object.
    
    Args:
        credentials: HTTP Bearer token credentials from Authorization header
        db: Database session (injected by FastAPI)
        
    Returns:
        Current authenticated User object
        
    Raises:
        HTTPException: 401 if token is invalid or expired, or user not found
    """
    token = credentials.credentials
    payload = security.verify_token(
        token,
        secret_key=settings.secret_key,
        algorithm=settings.algorithm
    )
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = int(payload.get("sub"))
    user = crud.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user
