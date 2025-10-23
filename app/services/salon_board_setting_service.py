"""SALON BOARD setting service for business logic."""

from sqlalchemy.orm import Session

from app.core.security import decrypt_password, encrypt_password
from app.models.salon_board_setting import SalonBoardSetting
from app.schemas.salon_board_setting import SalonBoardSettingCreate, SalonBoardSettingUpdate


def get_setting_by_id(db: Session, setting_id: int, user_id: int) -> SalonBoardSetting | None:
    """Get SALON BOARD setting by ID (user-specific).

    Args:
        db: Database session.
        setting_id: Setting ID to search for.
        user_id: User ID for ownership verification.

    Returns:
        SalonBoardSetting object if found and owned by user, None otherwise.
    """
    return (
        db.query(SalonBoardSetting)
        .filter(SalonBoardSetting.id == setting_id, SalonBoardSetting.user_id == user_id)
        .first()
    )


def get_user_settings(db: Session, user_id: int) -> list[SalonBoardSetting]:
    """Get all SALON BOARD settings for a user.

    Args:
        db: Database session.
        user_id: User ID to get settings for.

    Returns:
        List of SalonBoardSetting objects.
    """
    return db.query(SalonBoardSetting).filter(SalonBoardSetting.user_id == user_id).all()


def create_setting(db: Session, user_id: int, setting: SalonBoardSettingCreate) -> SalonBoardSetting:
    """Create a new SALON BOARD setting.

    Args:
        db: Database session.
        user_id: User ID who owns this setting.
        setting: Setting creation data.

    Returns:
        Created SalonBoardSetting object.
    """
    # Encrypt the SALON BOARD password
    encrypted_password = encrypt_password(setting.sb_password)

    db_setting = SalonBoardSetting(
        user_id=user_id,
        setting_name=setting.setting_name,
        sb_user_id=setting.sb_user_id,
        encrypted_sb_password=encrypted_password,
        salon_id=setting.salon_id,
        salon_name=setting.salon_name,
    )
    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)
    return db_setting


def update_setting(
    db: Session, setting_id: int, user_id: int, setting_update: SalonBoardSettingUpdate
) -> SalonBoardSetting | None:
    """Update an existing SALON BOARD setting.

    Args:
        db: Database session.
        setting_id: ID of setting to update.
        user_id: User ID for ownership verification.
        setting_update: Setting update data.

    Returns:
        Updated SalonBoardSetting object if found, None otherwise.
    """
    db_setting = get_setting_by_id(db, setting_id, user_id)
    if not db_setting:
        return None

    update_data = setting_update.model_dump(exclude_unset=True)

    # Encrypt password if provided
    if "sb_password" in update_data and update_data["sb_password"]:
        update_data["encrypted_sb_password"] = encrypt_password(update_data.pop("sb_password"))

    for key, value in update_data.items():
        setattr(db_setting, key, value)

    db.commit()
    db.refresh(db_setting)
    return db_setting


def delete_setting(db: Session, setting_id: int, user_id: int) -> bool:
    """Delete a SALON BOARD setting.

    Args:
        db: Database session.
        setting_id: ID of setting to delete.
        user_id: User ID for ownership verification.

    Returns:
        True if setting was deleted, False if not found.
    """
    db_setting = get_setting_by_id(db, setting_id, user_id)
    if not db_setting:
        return False

    db.delete(db_setting)
    db.commit()
    return True


def get_decrypted_password(db: Session, setting_id: int, user_id: int) -> str | None:
    """Get decrypted SALON BOARD password for a setting.

    Args:
        db: Database session.
        setting_id: Setting ID.
        user_id: User ID for ownership verification.

    Returns:
        Decrypted password string if found, None otherwise.

    Note:
        This function should only be called when actually needed for automation tasks.
        Never expose decrypted passwords in API responses.
    """
    db_setting = get_setting_by_id(db, setting_id, user_id)
    if not db_setting:
        return None

    try:
        return decrypt_password(db_setting.encrypted_sb_password)
    except Exception:
        return None
