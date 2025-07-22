"""
Users endpoints
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def users_status():
    return {"users": "not implemented yet"}
