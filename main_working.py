"""
Bitrix24 AI Assistant - Main Application (Working Version)

This is a simplified version of main.py that works with available components.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Try to import config, fallback to basic config if it fails
try:
    from app.core.config import settings
    use_config = True
except ImportError:
    use_config = False
    print("Warning: Could not import settings, using default configuration")

# Create FastAPI app
app = FastAPI(
    title="Bitrix24 AI Assistant",
    description="AI-powered assistant for Bitrix24 CRM",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic routes
@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "message": "Bitrix24 AI Assistant is running",
        "status": "ok",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Bitrix24 AI Assistant",
        "version": "1.0.0",
        "config_loaded": use_config
    }

@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_status": "operational",
        "endpoints": [
            "/",
            "/health", 
            "/api/v1/status",
            "/docs",
            "/redoc"
        ],
        "config_status": "loaded" if use_config else "default"
    }

@app.get("/api/v1/info")
async def app_info():
    """Application information"""
    info = {
        "name": "Bitrix24 AI Assistant",
        "version": "1.0.0",
        "description": "AI-powered assistant for Bitrix24 CRM",
        "status": "running"
    }
    
    if use_config:
        try:
            info.update({
                "app_name": settings.APP_NAME,
                "app_version": settings.APP_VERSION,
                "debug_mode": settings.APP_DEBUG,
                "environment": settings.APP_ENVIRONMENT
            })
        except Exception as e:
            info["config_error"] = str(e)
    
    return info

if __name__ == "__main__":
    # Get host and port
    host = "0.0.0.0"
    port = 8000
    
    if use_config:
        try:
            host = settings.APP_HOST
            port = settings.APP_PORT
        except:
            pass
    
    print(f"Starting Bitrix24 AI Assistant on {host}:{port}")
    uvicorn.run(
        "main_working:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
