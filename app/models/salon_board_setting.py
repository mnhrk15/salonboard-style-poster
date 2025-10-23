"""SALON BOARD settings model for SQLAlchemy."""

from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class SalonBoardSetting(Base):
    """SALON BOARD connection settings model.

    Attributes:
        id: Primary key, auto-incremented setting ID.
        user_id: Foreign key to users table.
        setting_name: User-defined name for this setting (e.g., "A店", "B店").
        sb_user_id: SALON BOARD login ID.
        encrypted_sb_password: AES-256 encrypted SALON BOARD password.
        salon_id: Target salon ID (for multi-store accounts).
        salon_name: Target salon name (for multi-store accounts).
        created_at: Setting creation timestamp.
        updated_at: Setting last update timestamp.
        user: Relationship to User model.
        tasks: Relationship to Task model.
    """

    __tablename__ = "salon_board_settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    setting_name = Column(String(100), nullable=False)
    sb_user_id = Column(String(255), nullable=False)
    encrypted_sb_password = Column(String(512), nullable=False)
    salon_id = Column(String(100), nullable=True)
    salon_name = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="salon_board_settings")
    tasks = relationship("Task", back_populates="salon_board_setting")

    def __repr__(self) -> str:
        """String representation of SalonBoardSetting."""
        return (
            f"<SalonBoardSetting(id={self.id}, user_id={self.user_id}, "
            f"setting_name='{self.setting_name}')>"
        )
