"""Celery task for style posting automation."""

import logging
from pathlib import Path
from uuid import UUID

from celery import Task
from sqlalchemy.orm import Session

from app.automation.salon_board_poster import SalonBoardStylePoster, load_selectors
from app.core.config import settings
from app.core.database import SessionLocal
from app.services import salon_board_setting_service, task_service
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


class StylePostTask(Task):
    """Custom Celery task for style posting."""

    def __init__(self) -> None:
        """Initialize task."""
        super().__init__()
        self.db: Session | None = None

    def before_start(self, task_id: str, args: tuple, kwargs: dict) -> None:
        """Called before task execution starts."""
        self.db = SessionLocal()
        logger.info(f"Task {task_id} started")

    def after_return(
        self, status: str, retval: any, task_id: str, args: tuple, kwargs: dict, einfo: any
    ) -> None:
        """Called after task returns."""
        if self.db:
            self.db.close()
        logger.info(f"Task {task_id} completed with status: {status}")


@celery_app.task(base=StylePostTask, bind=True, name="style_post_task")
def execute_style_post(
    self: StylePostTask,
    task_id: str,
    user_id: int,
    sb_setting_id: int,
    data_file_path: str,
    images_dir_path: str,
) -> dict:
    """Execute style posting automation task.

    Args:
        self: Task instance.
        task_id: UUID of the task.
        user_id: User ID who created the task.
        sb_setting_id: SALON BOARD setting ID to use.
        data_file_path: Path to uploaded data file.
        images_dir_path: Path to uploaded images directory.

    Returns:
        Dictionary with execution results.
    """
    db = self.db
    if not db:
        raise RuntimeError("Database session not initialized")

    task_uuid = UUID(task_id)
    log_file_path = Path(settings.LOG_DIR) / f"task_{task_id}.log"
    screenshot_dir = Path(settings.SCREENSHOT_DIR) / task_id

    # Create log and screenshot directories
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    # Configure file logger for this task
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(file_handler)

    try:
        # Get initial task state
        task = task_service.get_task_by_id(db, task_uuid, user_id)
        if not task:
            raise ValueError("Task not found in database")

        start_from = task.completed_items
        logger.info(f"Task starting from item: {start_from}")

        # Update task status to PROCESSING
        task_service.update_task_status(
            db, task_uuid, "PROCESSING", log_file_path=str(log_file_path)
        )

        # Get SALON BOARD setting
        sb_setting = salon_board_setting_service.get_setting_by_id(db, sb_setting_id, user_id)
        if not sb_setting:
            raise ValueError(f"SALON BOARD setting not found: {sb_setting_id}")

        # Get decrypted password
        sb_password = salon_board_setting_service.get_decrypted_password(
            db, sb_setting_id, user_id
        )
        if not sb_password:
            raise ValueError("Failed to decrypt SALON BOARD password")

        # Prepare salon info
        salon_info = None
        if sb_setting.salon_id or sb_setting.salon_name:
            salon_info = {
                "id": sb_setting.salon_id,
                "name": sb_setting.salon_name,
            }

        # Load selectors
        selectors = load_selectors()

        # Progress callback that also checks for interruption
        def check_and_report_progress_callback(completed: int, total: int) -> bool:
            """Update task progress and check for interruption signal."""
            # Update progress in DB
            task_service.update_task_status(db, task_uuid, "PROCESSING", completed_items=completed)
            logger.info(f"Progress: {completed}/{total}")

            # Check for interruption
            task = task_service.get_task_by_id(db, task_uuid, user_id)
            if task and task.status == "INTERRUPTED":
                logger.warning("Interruption signal received, stopping task.")
                return False
            return True

        # Create and run poster
        poster = SalonBoardStylePoster(
            selectors=selectors,
            screenshot_dir=str(screenshot_dir),
            headless=settings.PLAYWRIGHT_HEADLESS,
            slow_mo=settings.PLAYWRIGHT_SLOW_MO,
            progress_callback=check_and_report_progress_callback,
        )

        results = poster.run(
            user_id=sb_setting.sb_user_id,
            password=sb_password,
            data_filepath=data_file_path,
            image_dir=images_dir_path,
            salon_info=salon_info,
            start_from_row=start_from,
        )

        # Check final status after run
        final_task_status = task_service.get_task_by_id(db, task_uuid, user_id)
        if final_task_status and final_task_status.status == "INTERRUPTED":
            logger.info("Task finished due to interruption.")
            # Status is already INTERRUPTED, no need to update again unless to add a message
            task_service.update_task_status(
                db,
                task_uuid,
                "INTERRUPTED",
                completed_items=results["completed"],
                error_message="Task was manually interrupted."
            )

        # Update task status based on results if not interrupted
        elif results["success"] and results["failed"] == 0:
            task_service.update_task_status(
                db,
                task_uuid,
                "SUCCESS",
                completed_items=results["completed"],
            )
        elif results["failed"] > 0:
            # Partial success (some items failed)
            error_summary = f"{results['failed']} out of {results['total']} styles failed"
            task_service.update_task_status(
                db,
                task_uuid,
                "SUCCESS",  # Or "PARTIAL_SUCCESS" if you add this status
                completed_items=results["completed"],
                error_message=error_summary,
            )
        else:
            task_service.update_task_status(
                db,
                task_uuid,
                "FAILURE",
                error_message="Task failed with unknown error",
            )

        logger.info(f"Task completed: {results}")
        return results

    except Exception as e:
        logger.error(f"Task failed with exception: {e}", exc_info=True)

        # Take screenshot if poster exists
        screenshot_path = None
        try:
            screenshot_path = str(screenshot_dir / "critical_error.png")
        except Exception:
            pass

        # Update task status to FAILURE
        task_service.update_task_status(
            db,
            task_uuid,
            "FAILURE",
            error_message=str(e),
            screenshot_path=screenshot_path,
        )

        raise

    finally:
        # Remove file handler
        logger.removeHandler(file_handler)
        file_handler.close()
