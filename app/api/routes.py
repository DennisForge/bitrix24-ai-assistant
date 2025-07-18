"""
API Routes Configuration

This module configures all API routes for the Bitrix24 AI Assistant application.
"""

from fastapi import APIRouter

from app.api.endpoints import auth, tasks, calendar, users, ai_assistant

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

api_router.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["Tasks"]
)

api_router.include_router(
    calendar.router,
    prefix="/calendar",
    tags=["Calendar"]
)

api_router.include_router(
    ai_assistant.router,
    prefix="/ai",
    tags=["AI Assistant"]
)
