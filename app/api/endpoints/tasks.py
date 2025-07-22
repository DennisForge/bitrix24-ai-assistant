"""
Tasks endpoints
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def tasks_status():
    return {"tasks": "not implemented yet"}
