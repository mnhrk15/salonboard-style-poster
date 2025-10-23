"""FastAPI main application."""

import asyncio
from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_from_token
from app.api.v1 import api_router
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.services import task_service

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="SALON BOARD style automatic posting web application",
    debug=settings.DEBUG,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health_check() -> dict:
    """Health check endpoint.

    Returns:
        Dictionary with health status information.
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/")
def root() -> dict:
    """Root endpoint.

    Returns:
        Dictionary with API information.
    """
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


@app.websocket("/ws/tasks/{task_id}")
async def websocket_task_progress(websocket: WebSocket, task_id: UUID, token: str | None = None) -> None:
    """WebSocket endpoint for real-time task progress updates.

    Clients should connect with: ws://host/ws/tasks/{task_id}?token=JWT_TOKEN

    Args:
        websocket: WebSocket connection.
        task_id: Task UUID to monitor.
        token: JWT authentication token (query parameter).

    Sends JSON updates:
        {
            "task_id": "uuid",
            "status": "PROCESSING",
            "total_items": 10,
            "completed_items": 3,
            "progress_percentage": 30.0
        }
    """
    # Authenticate user
    db = next(get_db())
    try:
        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        user = get_current_user_from_token(db, token)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Verify task belongs to user
        task = task_service.get_task_by_id(db, task_id, user.id)
        if not task:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        await websocket.accept()

        # Send updates every 2 seconds until task is complete or connection closes
        try:
            while True:
                # Fetch latest task status
                task = task_service.get_task_by_id(db, task_id, user.id)
                if not task:
                    break

                # Calculate progress
                progress_percentage = 0.0
                if task.total_items > 0:
                    progress_percentage = round((task.completed_items / task.total_items) * 100, 2)

                # Send update
                await websocket.send_json({
                    "task_id": str(task_id),
                    "status": task.status,
                    "total_items": task.total_items,
                    "completed_items": task.completed_items,
                    "progress_percentage": progress_percentage,
                })

                # Stop sending if task is finished
                if task.status in ["SUCCESS", "FAILURE", "INTERRUPTED"]:
                    break

                # Wait before next update
                await asyncio.sleep(2)

        except WebSocketDisconnect:
            pass

    finally:
        db.close()
