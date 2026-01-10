from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field

from .. import crud, models, security
from ..database import get_db
from ..core.config import settings
from ..utils.rate_limiter import limiter
from ..dependencies.auth import get_current_user


class UserCreate(BaseModel):
    """Schema for user registration request.
    
    Attributes:
        name: User's full name
        email: Valid email address
        password: Password (min 8 characters)
    """
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class UserOut(BaseModel):
    """Schema for user response (excludes sensitive data).
    
    Attributes:
        id: User's unique identifier
        name: User's full name
        email: User's email address
    """
    id: int
    name: str
    email: EmailStr
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """JWT token response.
    
    Attributes:
        access_token: JWT access token
        refresh_token: JWT refresh token
        token_type: Token type (bearer)
        user: User information
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut


class LoginRequest(BaseModel):
    """Login request schema.
    
    Attributes:
        email: User email
        password: User password
    """
    email: EmailStr
    password: str


router = APIRouter()


@router.post("/api/v1/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/15minutes")
def register_user(
    request: Request,
    user: UserCreate,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """Register a new user and return JWT tokens.
    
    Args:
        user: User registration data
        db: Database session (injected)
        
    Returns:
        JWT tokens and user information
        
    Raises:
        HTTPException: 400 if email already registered
    """
    # Check if user already exists
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = crud.create_user(db=db, user_data=user.model_dump())
    
    # Generate tokens
    access_token = security.create_access_token(
        data={"sub": str(new_user.id)},
        secret_key=settings.secret_key,
        algorithm=settings.algorithm,
        expire_minutes=settings.access_token_expire_minutes
    )
    refresh_token = security.create_refresh_token(
        data={"sub": str(new_user.id)},
        secret_key=settings.secret_key,
        algorithm=settings.algorithm,
        expire_days=settings.refresh_token_expire_days
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserOut.model_validate(new_user)
    )


@router.post("/api/v1/auth/login", response_model=TokenResponse)
@limiter.limit("5/15minutes")
def login_user(
    request: Request,
    credentials: LoginRequest,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """Login user and return JWT tokens.
    
    Args:
        credentials: Email and password
        db: Database session (injected)
        
    Returns:
        JWT tokens and user information
        
    Raises:
        HTTPException: 401 if credentials invalid
    """
    # Find user by email
    db_user = crud.get_user_by_email(db, email=credentials.email)
    
    # Verify user exists and password is correct
    if not db_user or not security.verify_password(credentials.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate tokens
    access_token = security.create_access_token(
        data={"sub": str(db_user.id)},
        secret_key=settings.secret_key,
        algorithm=settings.algorithm,
        expire_minutes=settings.access_token_expire_minutes
    )
    refresh_token = security.create_refresh_token(
        data={"sub": str(db_user.id)},
        secret_key=settings.secret_key,
        algorithm=settings.algorithm,
        expire_days=settings.refresh_token_expire_days
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserOut.model_validate(db_user)
    )
class RefreshTokenRequest(BaseModel):
    """Schema for token refresh request.
    
    Attributes:
        refresh_token: Valid refresh token
    """
    refresh_token: str = Field(..., min_length=10)


@router.post("/api/v1/auth/refresh", response_model=TokenResponse)
def refresh_token_endpoint(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
) -> TokenResponse:
    """Refresh access token using refresh token.
    
    Args:
        request: Request body with refresh_token
        db: Database session (injected)
        
    Returns:
        New JWT tokens and user information
        
    Raises:
        HTTPException: 401 if refresh token invalid
    """
    refresh_token = request.refresh_token
    
    # Verify refresh token
    payload = security.verify_token(
        refresh_token,
        secret_key=settings.secret_key,
        algorithm=settings.algorithm
    )
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = int(payload.get("sub"))
    
    # Get user from database
    db_user = crud.get_user_by_id(db, user_id=user_id)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    # Generate new tokens
    access_token = security.create_access_token(
        data={"sub": str(db_user.id)},
        secret_key=settings.secret_key,
        algorithm=settings.algorithm,
        expire_minutes=settings.access_token_expire_minutes
    )
    new_refresh_token = security.create_refresh_token(
        data={"sub": str(db_user.id)},
        secret_key=settings.secret_key,
        algorithm=settings.algorithm,
        expire_days=settings.refresh_token_expire_days
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user=UserOut.model_validate(db_user)
    )


@router.get("/api/v1/auth/me", response_model=UserOut)
def get_current_user_info(
    current_user: models.User = Depends(get_current_user),
) -> UserOut:
    """Get current authenticated user information.
    
    Uses the centralized get_current_user dependency for consistency.
    
    Args:
        current_user: Current authenticated user (injected by dependency)
        
    Returns:
        Current user information
    """
    return UserOut.model_validate(current_user)