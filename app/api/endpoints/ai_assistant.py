"""
AI Assistant endpoints
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def ai_assistant_status():
    return {"ai_assistant": "not implemented yet"}
