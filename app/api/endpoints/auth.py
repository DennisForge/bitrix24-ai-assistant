"""
Authentication endpoints
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def auth_status():
    return {"auth": "not implemented yet"}
