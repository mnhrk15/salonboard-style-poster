"""HTML page endpoints for web UI."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_current_admin_user
from app.core.database import get_db
from app.models.user import User
from app.services import salon_board_setting_service, task_service

router = APIRouter()

# Import templates from main.py
# This will be accessed via dependency injection
def get_templates():
    """Get Jinja2Templates instance from main app."""
    from app.main import templates
    return templates


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def login_page(request: Request):
    """Render login page.

    Args:
        request: FastAPI request object.

    Returns:
        Rendered login HTML page.
    """
    templates = get_templates()
    return templates.TemplateResponse("auth/login.html", {
        "request": request,
        "title": "サインイン"
    })


@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
async def dashboard(request: Request):
    """Render dashboard page with task list.

    Args:
        request: FastAPI request object.

    Returns:
        Rendered dashboard HTML page.
    """
    templates = get_templates()

    # Note: Authentication and data loading are handled client-side via JavaScript
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "title": "ダッシュボード"
    })


@router.get("/tasks/new", response_class=HTMLResponse, include_in_schema=False)
async def new_task_page(request: Request):
    """Render new task creation page.

    Args:
        request: FastAPI request object.

    Returns:
        Rendered task creation HTML page.
    """
    templates = get_templates()

    # Note: Authentication and data loading are handled client-side via JavaScript
    return templates.TemplateResponse("tasks/create.html", {
        "request": request,
        "title": "新規スタイル投稿"
    })


@router.get("/settings", response_class=HTMLResponse, include_in_schema=False)
async def settings_page(request: Request):
    """Render SALON BOARD settings page.

    Args:
        request: FastAPI request object.

    Returns:
        Rendered settings HTML page.
    """
    templates = get_templates()

    # Note: Authentication and data loading are handled client-side via JavaScript
    return templates.TemplateResponse("settings/index.html", {
        "request": request,
        "title": "SALON BOARD設定"
    })


@router.get("/tasks/{task_id}", response_class=HTMLResponse, include_in_schema=False)
async def task_detail_page(
    task_id: str,
    request: Request,
):
    """Render task detail page.

    Args:
        task_id: Task ID (UUID).
        request: FastAPI request object.

    Returns:
        Rendered task detail HTML page.
    """
    templates = get_templates()

    # Note: Authentication and data loading are handled client-side via JavaScript
    return templates.TemplateResponse("tasks/detail.html", {
        "request": request,
        "title": f"タスク詳細 - {task_id}",
        "task_id": task_id
    })


@router.get("/admin/users", response_class=HTMLResponse, include_in_schema=False)
async def admin_users_page(request: Request):
    """Render user management page (admin only).

    Args:
        request: FastAPI request object.

    Returns:
        Rendered user management HTML page.
    """
    templates = get_templates()

    # Note: Authentication and data loading are handled client-side via JavaScript
    return templates.TemplateResponse("admin/users.html", {
        "request": request,
        "title": "ユーザー管理"
    })
