"""API dependencies for dependency injection."""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.services import user_service

# OAuth2 scheme for JWT authentication
security = HTTPBearer()


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> User:
    """Get current authenticated user from JWT token.

    Args:
        db: Database session.
        credentials: HTTP Bearer credentials containing JWT token.

    Returns:
        Current authenticated User object.

    Raises:
        HTTPException: If token is invalid or user not found.
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email: str | None = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = user_service.get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get current active user.

    Args:
        current_user: Current authenticated user.

    Returns:
        Current active User object.

    Raises:
        HTTPException: If user is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get current admin user.

    Args:
        current_user: Current authenticated user.

    Returns:
        Current admin User object.

    Raises:
        HTTPException: If user is not an admin.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user


def get_current_user_from_token(db: Session, token: str) -> User | None:
    """Get current user from JWT token string (for WebSocket authentication).

    Args:
        db: Database session.
        token: JWT token string.

    Returns:
        User object if valid, None otherwise.
    """
    payload = decode_access_token(token)
    if payload is None:
        return None

    email: str | None = payload.get("sub")
    if email is None:
        return None

    user = user_service.get_user_by_email(db, email=email)
    if user is None or not user.is_active:
        return None

    return user
