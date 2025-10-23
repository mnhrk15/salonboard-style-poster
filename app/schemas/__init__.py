"""Pydantic schemas package."""

from app.schemas.salon_board_setting import (
    SalonBoardSetting,
    SalonBoardSettingCreate,
    SalonBoardSettingInDB,
    SalonBoardSettingUpdate,
)
from app.schemas.task import Task, TaskCreate, TaskInDB, TaskItem, TaskList, TaskOperation
from app.schemas.user import Token, TokenPayload, User, UserCreate, UserInDB, UserUpdate

__all__ = [
    # User schemas
    "User",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "Token",
    "TokenPayload",
    # SALON BOARD Setting schemas
    "SalonBoardSetting",
    "SalonBoardSettingCreate",
    "SalonBoardSettingUpdate",
    "SalonBoardSettingInDB",
    # Task schemas
    "Task",
    "TaskCreate",
    "TaskInDB",
    "TaskItem",
    "TaskList",
    "TaskOperation",
]
