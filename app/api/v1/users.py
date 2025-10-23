"""User management endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_current_admin_user
from app.core.database import get_db
from app.models.user import User as UserModel
from app.schemas.user import User, UserCreate, UserUpdate
from app.services import user_service

router = APIRouter()


@router.get("/me", response_model=User)
def read_current_user(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
) -> User:
    """Get current user information.

    Args:
        current_user: Current authenticated user.

    Returns:
        Current user information.
    """
    return User.model_validate(current_user)


@router.get("/", response_model=dict)
def read_users(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_admin_user)],
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    role: str | None = Query(None, pattern="^(admin|user)$", description="Filter by role"),
    is_active: bool | None = Query(None, description="Filter by active status"),
) -> dict:
    """Get list of users (admin only).

    Args:
        db: Database session.
        current_user: Current admin user.
        page: Page number (1-indexed).
        per_page: Number of items per page.
        role: Optional role filter.
        is_active: Optional active status filter.

    Returns:
        Dictionary with users list and pagination info.
    """
    skip = (page - 1) * per_page
    users = user_service.get_users(db, skip=skip, limit=per_page, role=role, is_active=is_active)
    total = user_service.count_users(db, role=role, is_active=is_active)
    total_pages = (total + per_page - 1) // per_page

    return {
        "success": True,
        "data": {
            "users": [User.model_validate(user) for user in users],
            "pagination": {
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages,
            },
        },
    }


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_user(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_admin_user)],
    user: UserCreate,
) -> dict:
    """Create a new user (admin only).

    Args:
        db: Database session.
        current_user: Current admin user.
        user: User creation data.

    Returns:
        Created user information.

    Raises:
        HTTPException: If email already exists.
    """
    # Check if email already exists
    existing_user = user_service.get_user_by_email(db, email=user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    db_user = user_service.create_user(db, user)
    return {
        "success": True,
        "data": User.model_validate(db_user),
    }


@router.put("/{user_id}", response_model=dict)
def update_user(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_admin_user)],
    user_id: int,
    user: UserUpdate,
) -> dict:
    """Update a user (admin only).

    Args:
        db: Database session.
        current_user: Current admin user.
        user_id: ID of user to update.
        user: User update data.

    Returns:
        Updated user information.

    Raises:
        HTTPException: If user not found or email already exists.
    """
    # Check if email already exists (if email is being updated)
    if user.email:
        existing_user = user_service.get_user_by_email(db, email=user.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

    db_user = user_service.update_user(db, user_id, user)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return {
        "success": True,
        "data": User.model_validate(db_user),
    }


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_admin_user)],
    user_id: int,
) -> None:
    """Delete a user (admin only).

    Args:
        db: Database session.
        current_user: Current admin user.
        user_id: ID of user to delete.

    Raises:
        HTTPException: If user not found or trying to delete self.
    """
    # Prevent deleting self
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete your own account",
        )

    success = user_service.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
