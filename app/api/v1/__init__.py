"""API v1 router configuration."""

from fastapi import APIRouter

from app.api.v1 import auth, settings, tasks, users

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(settings.router, prefix="/sb-settings", tags=["SALON BOARD Settings"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
