"""Task service for business logic."""

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.task import Task, TaskItem


def get_task_by_id(db: Session, task_id: UUID, user_id: int) -> Task | None:
    """Get task by ID (user-specific).

    Args:
        db: Database session.
        task_id: Task UUID to search for.
        user_id: User ID for ownership verification.

    Returns:
        Task object if found and owned by user, None otherwise.
    """
    return db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()


def get_user_tasks(
    db: Session, user_id: int, skip: int = 0, limit: int = 100, status: str | None = None
) -> list[Task]:
    """Get all tasks for a user with optional filters.

    Args:
        db: Database session.
        user_id: User ID to get tasks for.
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.
        status: Optional status filter.

    Returns:
        List of Task objects.
    """
    query = db.query(Task).filter(Task.user_id == user_id)

    if status:
        query = query.filter(Task.status == status)

    return query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()


def count_user_tasks(db: Session, user_id: int, status: str | None = None) -> int:
    """Count tasks for a user with optional filters.

    Args:
        db: Database session.
        user_id: User ID.
        status: Optional status filter.

    Returns:
        Total count of tasks matching the filters.
    """
    query = db.query(Task).filter(Task.user_id == user_id)

    if status:
        query = query.filter(Task.status == status)

    return query.count()


def create_task(
    db: Session,
    task_id: UUID,
    user_id: int,
    sb_setting_id: int,
    total_items: int,
    data_file_path: str,
    images_dir_path: str,
) -> Task:
    """Create a new task.

    Args:
        db: Database session.
        task_id: UUID for the task (should match Celery task ID).
        user_id: User ID who created this task.
        sb_setting_id: SALON BOARD setting ID to use.
        total_items: Total number of styles to process.
        data_file_path: Path to uploaded data file.
        images_dir_path: Path to uploaded images directory.

    Returns:
        Created Task object.
    """
    db_task = Task(
        id=task_id,
        user_id=user_id,
        sb_setting_id=sb_setting_id,
        status="PENDING",
        total_items=total_items,
        completed_items=0,
        data_file_path=data_file_path,
        images_dir_path=images_dir_path,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task_status(
    db: Session,
    task_id: UUID,
    status: str,
    completed_items: int | None = None,
    error_message: str | None = None,
    log_file_path: str | None = None,
    screenshot_path: str | None = None,
) -> Task | None:
    """Update task status and progress.

    Args:
        db: Database session.
        task_id: Task UUID to update.
        status: New status value.
        completed_items: Number of completed items (optional).
        error_message: Error message if failed (optional).
        log_file_path: Path to log file (optional).
        screenshot_path: Path to screenshot (optional).

    Returns:
        Updated Task object if found, None otherwise.
    """
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if not db_task:
        return None

    db_task.status = status

    if completed_items is not None:
        db_task.completed_items = completed_items

    if error_message is not None:
        db_task.error_message = error_message

    if log_file_path is not None:
        db_task.log_file_path = log_file_path

    if screenshot_path is not None:
        db_task.screenshot_path = screenshot_path

    if status in ["SUCCESS", "FAILURE"]:
        db_task.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(db_task)
    return db_task


def create_task_item(
    db: Session, task_id: UUID, item_index: int, style_name: str | None = None
) -> TaskItem:
    """Create a new task item.

    Args:
        db: Database session.
        task_id: Task UUID this item belongs to.
        item_index: Index of this item in the task.
        style_name: Name of the style (optional).

    Returns:
        Created TaskItem object.
    """
    db_item = TaskItem(
        task_id=task_id,
        item_index=item_index,
        status="PENDING",
        style_name=style_name,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_task_item_status(
    db: Session,
    item_id: int,
    status: str,
    error_message: str | None = None,
    screenshot_path: str | None = None,
) -> TaskItem | None:
    """Update task item status.

    Args:
        db: Database session.
        item_id: Task item ID to update.
        status: New status value.
        error_message: Error message if failed (optional).
        screenshot_path: Path to screenshot (optional).

    Returns:
        Updated TaskItem object if found, None otherwise.
    """
    db_item = db.query(TaskItem).filter(TaskItem.id == item_id).first()
    if not db_item:
        return None

    db_item.status = status

    if error_message is not None:
        db_item.error_message = error_message

    if screenshot_path is not None:
        db_item.screenshot_path = screenshot_path

    if status in ["SUCCESS", "FAILURE", "SKIPPED"]:
        db_item.processed_at = datetime.utcnow()

    db.commit()
    db.refresh(db_item)
    return db_item


def get_task_items(db: Session, task_id: UUID) -> list[TaskItem]:
    """Get all items for a task.

    Args:
        db: Database session.
        task_id: Task UUID to get items for.

    Returns:
        List of TaskItem objects.
    """
    return (
        db.query(TaskItem)
        .filter(TaskItem.task_id == task_id)
        .order_by(TaskItem.item_index)
        .all()
    )
