"""Task management endpoints."""

import shutil
from pathlib import Path
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.task import Task, TaskCreate, TaskList, TaskOperation
from app.services import salon_board_setting_service, task_service
from app.tasks.style_post_task import execute_style_post

router = APIRouter()


@router.get("/", response_model=dict)
def read_tasks(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    status: str | None = Query(
        None,
        pattern="^(PENDING|PROCESSING|SUCCESS|FAILURE|INTERRUPTED)$",
        description="Filter by status",
    ),
) -> dict:
    """Get list of tasks for current user.

    Args:
        db: Database session.
        current_user: Current authenticated user.
        page: Page number (1-indexed).
        per_page: Number of items per page.
        status: Optional status filter.

    Returns:
        Dictionary with tasks list and pagination info.
    """
    skip = (page - 1) * per_page
    tasks = task_service.get_user_tasks(
        db, current_user.id, skip=skip, limit=per_page, status=status
    )
    total = task_service.count_user_tasks(db, current_user.id, status=status)
    total_pages = (total + per_page - 1) // per_page

    # Calculate progress percentage for each task
    tasks_with_progress = []
    for task in tasks:
        task_dict = Task.model_validate(task).model_dump()
        if task.total_items > 0:
            task_dict["progress_percentage"] = round(
                (task.completed_items / task.total_items) * 100, 2
            )
        else:
            task_dict["progress_percentage"] = 0.0
        tasks_with_progress.append(task_dict)

    return {
        "success": True,
        "data": {
            "tasks": tasks_with_progress,
            "pagination": {
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": total_pages,
            },
        },
    }


@router.get("/{task_id}", response_model=dict)
def read_task(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    task_id: UUID,
) -> dict:
    """Get a specific task.

    Args:
        db: Database session.
        current_user: Current authenticated user.
        task_id: UUID of task to retrieve.

    Returns:
        Task information.

    Raises:
        HTTPException: If task not found.
    """
    task = task_service.get_task_by_id(db, task_id, current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    task_dict = Task.model_validate(task).model_dump()
    if task.total_items > 0:
        task_dict["progress_percentage"] = round(
            (task.completed_items / task.total_items) * 100, 2
        )
    else:
        task_dict["progress_percentage"] = 0.0

    return {
        "success": True,
        "data": task_dict,
    }


@router.post("/{task_id}/interrupt", response_model=dict)
def interrupt_task(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    task_id: UUID,
) -> dict:
    """Interrupt a running task.

    Args:
        db: Database session.
        current_user: Current authenticated user.
        task_id: UUID of task to interrupt.

    Returns:
        Task operation response.

    Raises:
        HTTPException: If task not found or cannot be interrupted.
    """
    task = task_service.get_task_by_id(db, task_id, current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task.status not in ["PENDING", "PROCESSING"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot interrupt task with status: {task.status}",
        )

    # Update task status to INTERRUPTED
    updated_task = task_service.update_task_status(db, task_id, "INTERRUPTED")

    # TODO: Signal Celery task to stop (implement in Celery task)

    return {
        "success": True,
        "data": {
            "task_id": str(task_id),
            "status": "INTERRUPTED",
            "message": "Task has been interrupted",
        },
    }


@router.post("/{task_id}/resume", response_model=dict)
def resume_task(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    task_id: UUID,
) -> dict:
    """Resume an interrupted task.

    Args:
        db: Database session.
        current_user: Current authenticated user.
        task_id: UUID of task to resume.

    Returns:
        Task operation response.

    Raises:
        HTTPException: If task not found or cannot be resumed.
    """
    task = task_service.get_task_by_id(db, task_id, current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if task.status != "INTERRUPTED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot resume task with status: {task.status}",
        )

    # Update task status to PENDING (will be picked up by Celery)
    updated_task = task_service.update_task_status(db, task_id, "PENDING")

    # TODO: Re-queue Celery task (implement in Celery task)

    return {
        "success": True,
        "data": {
            "task_id": str(task_id),
            "status": "PROCESSING",
            "message": "Task has been resumed",
        },
    }


@router.post("/style-post", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_style_post_task(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    sb_setting_id: Annotated[int, Form()],
    data_file: Annotated[UploadFile, File()],
    images: Annotated[list[UploadFile], File()],
) -> dict:
    """Create a new style posting task.

    Args:
        db: Database session.
        current_user: Current authenticated user.
        sb_setting_id: SALON BOARD setting ID to use.
        data_file: Style data file (CSV/Excel).
        images: List of image files.

    Returns:
        Task creation response.

    Raises:
        HTTPException: If validation fails or setting not found.
    """
    # Verify SALON BOARD setting exists and belongs to user
    sb_setting = salon_board_setting_service.get_setting_by_id(db, sb_setting_id, current_user.id)
    if not sb_setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SALON BOARD setting not found",
        )

    # Validate file types
    if not data_file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data file is required",
        )

    if not data_file.filename.endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data file must be CSV or Excel format",
        )

    if not images:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one image file is required",
        )

    # Generate task ID
    task_id = uuid4()

    # Create upload directories
    upload_dir = Path(settings.UPLOAD_DIR) / str(task_id)
    data_dir = upload_dir / "data"
    images_dir = upload_dir / "images"

    data_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Save data file
        data_file_path = data_dir / data_file.filename
        with data_file_path.open("wb") as buffer:
            shutil.copyfileobj(data_file.file, buffer)

        # Save image files
        image_filenames = []
        for image in images:
            if not image.filename:
                continue

            image_path = images_dir / image.filename
            with image_path.open("wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            image_filenames.append(image.filename)

        # Load and validate data file
        if data_file.filename.endswith(".csv"):
            import pandas as pd

            df = pd.read_csv(data_file_path)
        else:
            import pandas as pd

            df = pd.read_excel(data_file_path)

        total_items = len(df)

        # Validate file consistency (FR-03-03: ファイル間整合性検証)
        if "image_filename" not in df.columns:
            raise ValueError("Data file must contain 'image_filename' column")

        # Get all image filenames from data file
        required_images = set(df["image_filename"].dropna().astype(str).tolist())
        uploaded_images = set(image_filenames)

        # Check for missing images
        missing_images = required_images - uploaded_images
        if missing_images:
            missing_list = ", ".join(sorted(list(missing_images)[:10]))  # Show first 10
            if len(missing_images) > 10:
                missing_list += f" and {len(missing_images) - 10} more"
            raise ValueError(
                f"Missing image files referenced in data file: {missing_list}"
            )

        # Create task record in database
        db_task = task_service.create_task(
            db=db,
            task_id=task_id,
            user_id=current_user.id,
            sb_setting_id=sb_setting_id,
            total_items=total_items,
            data_file_path=str(data_file_path),
            images_dir_path=str(images_dir),
        )

        # Queue Celery task
        execute_style_post.apply_async(
            args=[
                str(task_id),
                current_user.id,
                sb_setting_id,
                str(data_file_path),
                str(images_dir),
            ],
            task_id=str(task_id),
        )

        return {
            "success": True,
            "data": {
                "task_id": str(task_id),
                "status": "PENDING",
                "message": "Task created successfully and queued for processing",
            },
        }

    except Exception as e:
        # Clean up uploaded files on error
        if upload_dir.exists():
            shutil.rmtree(upload_dir)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}",
        )


@router.get("/{task_id}/logs", response_class=FileResponse)
def download_task_logs(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    task_id: UUID,
) -> FileResponse:
    """Download task execution log file.

    Args:
        db: Database session.
        current_user: Current authenticated user.
        task_id: UUID of task.

    Returns:
        Log file as download.

    Raises:
        HTTPException: If task not found or log file not available.
    """
    task = task_service.get_task_by_id(db, task_id, current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if not task.log_file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log file not available for this task",
        )

    log_file = Path(task.log_file_path)
    if not log_file.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log file not found on server",
        )

    return FileResponse(
        path=str(log_file),
        filename=f"task_{task_id}_log.txt",
        media_type="text/plain",
    )


@router.get("/{task_id}/screenshots", response_class=FileResponse)
def download_task_screenshot(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    task_id: UUID,
) -> FileResponse:
    """Download task error screenshot.

    Args:
        db: Database session.
        current_user: Current authenticated user.
        task_id: UUID of task.

    Returns:
        Screenshot image as download.

    Raises:
        HTTPException: If task not found or screenshot not available.
    """
    task = task_service.get_task_by_id(db, task_id, current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    if not task.screenshot_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Screenshot not available for this task",
        )

    screenshot_file = Path(task.screenshot_path)
    if not screenshot_file.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Screenshot file not found on server",
        )

    return FileResponse(
        path=str(screenshot_file),
        filename=f"task_{task_id}_screenshot.png",
        media_type="image/png",
    )
