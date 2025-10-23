"""Authentication endpoints."""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token
from app.models.user import User as UserModel
from app.schemas.user import Token, User
from app.services import user_service

router = APIRouter()


@router.post("/token", response_model=Token)
def login(
    db: Annotated[Session, Depends(get_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """Authenticate user and return JWT token.

    Args:
        db: Database session.
        form_data: OAuth2 password request form with username (email) and password.

    Returns:
        Token object with access_token and user information.

    Raises:
        HTTPException: If authentication fails.
    """
    user = user_service.authenticate_user(db, email=form_data.username, password=form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
        user=User.model_validate(user),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
) -> None:
    """Sign out current user.

    Note: JWT tokens are stateless, so this endpoint primarily serves to:
    1. Allow clients to perform logout actions (e.g., clearing local storage)
    2. Log the logout event for audit purposes

    The client should discard the token after calling this endpoint.

    Args:
        current_user: Current authenticated user.

    Returns:
        204 No Content
    """
    # JWT is stateless, so server-side invalidation is not implemented
    # Client should remove the token from storage
    # This endpoint can be extended to log logout events if needed
    pass


@router.post("/refresh", response_model=Token)
def refresh_token(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
) -> Token:
    """Refresh JWT token for authenticated user.

    Args:
        current_user: Current authenticated user (from existing valid token).

    Returns:
        New Token object with refreshed access_token.

    Raises:
        HTTPException: If user account is disabled.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.email}, expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
        user=User.model_validate(current_user),
    )
