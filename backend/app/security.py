from datetime import datetime, timedelta, timezone
from typing import Any

from passlib.context import CryptContext
from jose import JWTError, jwt

# Use bcrypt for password hashing (most stable)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plain text password using argon2.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a hashed password.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict[str, Any], secret_key: str, expires_delta: timedelta | None = None, algorithm: str = "HS256", expire_minutes: int = 30) -> str:
    """Create JWT access token.
    
    Args:
        data: Payload data to encode
        secret_key: Secret key for encoding (REQUIRED)
        expires_delta: Optional custom expiration time
        algorithm: JWT algorithm
        expire_minutes: Minutes until expiration
        
    Returns:
        Encoded JWT token string
        
    Raises:
        ValueError: If secret_key is not provided or is empty
    """
    if not secret_key or not secret_key.strip():
        raise ValueError("secret_key is required and cannot be empty")
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        secret_key,
        algorithm=algorithm
    )
    return encoded_jwt


def create_refresh_token(data: dict[str, Any], secret_key: str, algorithm: str = "HS256", expire_days: int = 7) -> str:
    """Create JWT refresh token.
    
    Args:
        data: Payload data to encode
        secret_key: Secret key for encoding (REQUIRED)
        algorithm: JWT algorithm
        expire_days: Days until expiration
        
    Returns:
        Encoded JWT refresh token string
        
    Raises:
        ValueError: If secret_key is not provided or is empty
    """
    if not secret_key or not secret_key.strip():
        raise ValueError("secret_key is required and cannot be empty")
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        secret_key,
        algorithm=algorithm
    )
    return encoded_jwt


def verify_token(token: str, secret_key: str, algorithm: str = "HS256") -> dict[str, Any] | None:
    """Verify and decode JWT token.
    
    Args:
        token: JWT token string to verify
        secret_key: Secret key for decoding (REQUIRED)
        algorithm: JWT algorithm
        
    Returns:
        Decoded token payload or None if invalid
        
    Raises:
        ValueError: If secret_key is not provided or is empty
    """
    if not secret_key or not secret_key.strip():
        raise ValueError("secret_key is required and cannot be empty")
    try:
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[algorithm]
        )
        return payload
    except JWTError:
        return None


def require_admin(current_user) -> None:
    """Require that the current user has admin role.
    
    Args:
        current_user: User object from database
        
    Raises:
        HTTPException: 403 if user is not admin
    """
    from fastapi import HTTPException, status
    from app.schemas import UserRole
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authentication required"
        )
    
    # Check role using Enum value for type safety
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )