"""Task Pydantic schemas for request/response validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# Task status enum values
TASK_STATUS_PENDING = "PENDING"
TASK_STATUS_PROCESSING = "PROCESSING"
TASK_STATUS_SUCCESS = "SUCCESS"
TASK_STATUS_FAILURE = "FAILURE"
TASK_STATUS_INTERRUPTED = "INTERRUPTED"


# Task item status enum values
ITEM_STATUS_PENDING = "PENDING"
ITEM_STATUS_PROCESSING = "PROCESSING"
ITEM_STATUS_SUCCESS = "SUCCESS"
ITEM_STATUS_FAILURE = "FAILURE"
ITEM_STATUS_SKIPPED = "SKIPPED"


# Base schema for task
class TaskBase(BaseModel):
    """Base task schema with common attributes."""

    pass


# Schema for task creation response
class TaskCreate(BaseModel):
    """Schema for task creation response."""

    task_id: UUID
    status: str
    message: str


# Schema for task in database (response)
class TaskInDB(TaskBase):
    """Schema for task stored in database."""

    id: UUID
    user_id: int
    sb_setting_id: int
    status: str
    total_items: int
    completed_items: int
    data_file_path: str | None
    images_dir_path: str | None
    log_file_path: str | None
    screenshot_path: str | None
    error_message: str | None
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


# Schema for task response (public)
class Task(TaskInDB):
    """Schema for task response."""

    progress_percentage: float | None = None

    @property
    def calculate_progress(self) -> float:
        """Calculate progress percentage."""
        if self.total_items == 0:
            return 0.0
        return round((self.completed_items / self.total_items) * 100, 2)


# Schema for task list response
class TaskList(BaseModel):
    """Schema for paginated task list response."""

    tasks: list[Task]
    pagination: dict[str, int]


# Schema for task item
class TaskItem(BaseModel):
    """Schema for individual task item."""

    id: int
    task_id: UUID
    item_index: int
    status: str
    style_name: str | None
    error_message: str | None
    screenshot_path: str | None
    processed_at: datetime | None

    model_config = {"from_attributes": True}


# Schema for task operation response
class TaskOperation(BaseModel):
    """Schema for task operation response (interrupt/resume)."""

    task_id: UUID
    status: str
    message: str
