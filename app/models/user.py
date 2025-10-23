"""User model for SQLAlchemy."""

from datetime import datetime

from sqlalchemy import Boolean, Column, Integer, String, TIMESTAMP, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    """User account model.

    Attributes:
        id: Primary key, auto-incremented user ID.
        email: Unique email address for login.
        hashed_password: Bcrypt-hashed password.
        role: User role ('admin' or 'user').
        is_active: Account active status.
        created_at: Account creation timestamp.
        salon_board_settings: Relationship to SalonBoardSetting model.
        tasks: Relationship to Task model.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="user", index=True)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    # Relationships
    salon_board_settings = relationship(
        "SalonBoardSetting", back_populates="user", cascade="all, delete-orphan"
    )
    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
