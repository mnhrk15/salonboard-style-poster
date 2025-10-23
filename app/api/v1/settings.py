"""SALON BOARD settings endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.salon_board_setting import (
    SalonBoardSetting,
    SalonBoardSettingCreate,
    SalonBoardSettingUpdate,
)
from app.services import salon_board_setting_service

router = APIRouter()


@router.get("/", response_model=dict)
def read_settings(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> dict:
    """Get all SALON BOARD settings for current user.

    Args:
        db: Database session.
        current_user: Current authenticated user.

    Returns:
        Dictionary with settings list.
    """
    settings = salon_board_setting_service.get_user_settings(db, current_user.id)

    return {
        "success": True,
        "data": {
            "settings": [SalonBoardSetting.model_validate(setting) for setting in settings],
        },
    }


@router.get("/{setting_id}", response_model=dict)
def read_setting(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    setting_id: int,
) -> dict:
    """Get a specific SALON BOARD setting.

    Args:
        db: Database session.
        current_user: Current authenticated user.
        setting_id: ID of setting to retrieve.

    Returns:
        Setting information.

    Raises:
        HTTPException: If setting not found.
    """
    setting = salon_board_setting_service.get_setting_by_id(db, setting_id, current_user.id)
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setting not found",
        )

    return {
        "success": True,
        "data": SalonBoardSetting.model_validate(setting),
    }


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_setting(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    setting: SalonBoardSettingCreate,
) -> dict:
    """Create a new SALON BOARD setting.

    Args:
        db: Database session.
        current_user: Current authenticated user.
        setting: Setting creation data.

    Returns:
        Created setting information.
    """
    db_setting = salon_board_setting_service.create_setting(db, current_user.id, setting)

    return {
        "success": True,
        "data": SalonBoardSetting.model_validate(db_setting),
    }


@router.put("/{setting_id}", response_model=dict)
def update_setting(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    setting_id: int,
    setting: SalonBoardSettingUpdate,
) -> dict:
    """Update a SALON BOARD setting.

    Args:
        db: Database session.
        current_user: Current authenticated user.
        setting_id: ID of setting to update.
        setting: Setting update data.

    Returns:
        Updated setting information.

    Raises:
        HTTPException: If setting not found.
    """
    db_setting = salon_board_setting_service.update_setting(
        db, setting_id, current_user.id, setting
    )
    if not db_setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setting not found",
        )

    return {
        "success": True,
        "data": SalonBoardSetting.model_validate(db_setting),
    }


@router.delete("/{setting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_setting(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    setting_id: int,
) -> None:
    """Delete a SALON BOARD setting.

    Args:
        db: Database session.
        current_user: Current authenticated user.
        setting_id: ID of setting to delete.

    Raises:
        HTTPException: If setting not found.
    """
    success = salon_board_setting_service.delete_setting(db, setting_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setting not found",
        )
