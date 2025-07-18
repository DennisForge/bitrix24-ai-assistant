"""
Bitrix24 AI Assistant - Main Application Entry Point

This module serves as the main entry point for the Bitrix24 AI Assistant application.
It initializes the FastAPI application, configures middleware, sets up routes,
and starts the server.
"""

import argparse
import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.logging_config import setup_logging
from app.api.routes import api_router
from app.services.scheduler import scheduler_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    
    Args:
        app: FastAPI application instance
    """
    # Startup
    logging.info("Starting Bitrix24 AI Assistant...")
    
    # Initialize database
    await init_db()
    
    # Start scheduler
    if settings.SCHEDULER_ENABLED:
        await scheduler_service.start()
    
    logging.info("Application started successfully!")
    
    yield
    
    # Shutdown
    logging.info("Shutting down Bitrix24 AI Assistant...")
    
    # Stop scheduler
    if settings.SCHEDULER_ENABLED:
        await scheduler_service.stop()
    
    # Close database connections
    await close_db()
    
    logging.info("Application shutdown complete!")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        debug=settings.APP_DEBUG,
        lifespan=lifespan,
        docs_url="/docs" if settings.APP_DEBUG else None,
        redoc_url="/redoc" if settings.APP_DEBUG else None,
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Add exception handlers
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler for unhandled exceptions."""
        logging.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred. Please try again later."
            }
        )
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENVIRONMENT
        }
    
    # Include API routes
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    
    # Mount static files
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    return app


def init_database():
    """Initialize the database schema."""
    import asyncio
    from app.core.database import init_db
    
    async def _init():
        await init_db()
        print("Database initialized successfully!")
    
    asyncio.run(_init())


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="Bitrix24 AI Assistant")
    parser.add_argument(
        "--init-db",
        action="store_true",
        help="Initialize the database schema"
    )
    parser.add_argument(
        "--host",
        default=settings.APP_HOST,
        help="Host to bind the server to"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=settings.APP_PORT,
        help="Port to bind the server to"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    
    if args.init_db:
        init_database()
        return
    
    # Create and run the application
    app = create_app()
    
    logging.info(f"Starting server on {args.host}:{args.port}")
    
    uvicorn.run(
        "main:create_app",
        factory=True,
        host=args.host,
        port=args.port,
        reload=args.reload or settings.APP_DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
    )


if __name__ == "__main__":
    main()
