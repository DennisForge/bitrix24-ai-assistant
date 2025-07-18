"""
Simple test application for basic functionality testing
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(
    title="Bitrix24 AI Assistant",
    description="AI-powered assistant for Bitrix24 CRM",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {"message": "Bitrix24 AI Assistant is running", "status": "ok"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Bitrix24 AI Assistant",
        "version": "1.0.0"
    }

@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_status": "operational",
        "endpoints": [
            "/",
            "/health",
            "/api/v1/status"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "test_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
