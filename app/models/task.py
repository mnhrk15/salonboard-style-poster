"""Task model for SQLAlchemy."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Column, ForeignKey, Integer, String, Text, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Task(Base):
    """Style posting task model.

    Attributes:
        id: Primary key, UUID (shared with Celery task ID).
        user_id: Foreign key to users table.
        sb_setting_id: Foreign key to salon_board_settings table.
        status: Task status (PENDING, PROCESSING, SUCCESS, FAILURE, INTERRUPTED).
        total_items: Total number of styles to process.
        completed_items: Number of styles completed.
        data_file_path: Path to uploaded style data file (CSV/Excel).
        images_dir_path: Path to directory containing uploaded images.
        log_file_path: Path to task log file.
        screenshot_path: Path to error screenshot (if any).
        error_message: Error message (if any).
        created_at: Task creation timestamp.
        completed_at: Task completion timestamp.
        user: Relationship to User model.
        salon_board_setting: Relationship to SalonBoardSetting model.
        task_items: Relationship to TaskItem model.
    """

    __tablename__ = "tasks"

    id = Column(PG_UUID(as_uuid=True), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    sb_setting_id = Column(
        Integer, ForeignKey("salon_board_settings.id", ondelete="RESTRICT"), nullable=False
    )
    status = Column(String(50), nullable=False, default="PENDING", index=True)
    total_items = Column(Integer, nullable=False, default=0)
    completed_items = Column(Integer, nullable=False, default=0)
    data_file_path = Column(String(512), nullable=True)
    images_dir_path = Column(String(512), nullable=True)
    log_file_path = Column(String(512), nullable=True)
    screenshot_path = Column(String(512), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), index=True)
    completed_at = Column(TIMESTAMP, nullable=True)

    # Relationships
    user = relationship("User", back_populates="tasks")
    salon_board_setting = relationship("SalonBoardSetting", back_populates="tasks")
    task_items = relationship("TaskItem", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """String representation of Task."""
        return (
            f"<Task(id={self.id}, user_id={self.user_id}, status='{self.status}', "
            f"progress={self.completed_items}/{self.total_items})>"
        )


class TaskItem(Base):
    """Individual style item within a task.

    Attributes:
        id: Primary key, auto-incremented item ID.
        task_id: Foreign key to tasks table.
        item_index: Index of this item in the task (0-based).
        status: Item status (PENDING, PROCESSING, SUCCESS, FAILURE, SKIPPED).
        style_name: Name of the style.
        error_message: Error message (if any).
        screenshot_path: Path to error screenshot (if any).
        processed_at: Item processing completion timestamp.
        task: Relationship to Task model.
    """

    __tablename__ = "task_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    task_id = Column(PG_UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    item_index = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False, default="PENDING", index=True)
    style_name = Column(String(255), nullable=True)
    error_message = Column(Text, nullable=True)
    screenshot_path = Column(String(512), nullable=True)
    processed_at = Column(TIMESTAMP, nullable=True)

    # Relationships
    task = relationship("Task", back_populates="task_items")

    def __repr__(self) -> str:
        """String representation of TaskItem."""
        return (
            f"<TaskItem(id={self.id}, task_id={self.task_id}, "
            f"index={self.item_index}, status='{self.status}')>"
        )
