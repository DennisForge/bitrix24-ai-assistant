"""
Calendar endpoints
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def calendar_status():
    return {"calendar": "not implemented yet"}
