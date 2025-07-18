"""
Logging Configuration

This module sets up structured logging for the Bitrix24 AI Assistant application.
It configures log formatting, rotation, and output destinations.
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Dict, Any

import structlog
from structlog.stdlib import LoggerFactory

from app.core.config import settings


def setup_logging() -> None:
    """
    Set up structured logging configuration.
    
    This function configures the logging system with:
    - Structured logging using structlog
    - JSON formatting for production
    - Console output for development
    - File rotation for persistent logging
    - Proper log levels based on environment
    """
    
    # Create logs directory if it doesn't exist
    log_file_path = Path(settings.LOG_FILE)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.LOG_FORMAT == "json" else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL),
    )
    
    # Configure file handler with rotation
    if settings.LOG_FILE:
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=settings.LOG_FILE,
            when="midnight",
            interval=1,
            backupCount=30,
            encoding="utf-8",
        )
        file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
        
        # Add file handler to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
    
    # Configure specific loggers
    _configure_external_loggers()
    
    # Log startup message
    logger = structlog.get_logger(__name__)
    logger.info(
        "Logging configured successfully",
        log_level=settings.LOG_LEVEL,
        log_format=settings.LOG_FORMAT,
        log_file=settings.LOG_FILE,
    )


def _configure_external_loggers() -> None:
    """Configure logging levels for external libraries."""
    
    # Reduce verbosity of external libraries
    external_loggers = {
        "uvicorn": logging.INFO,
        "uvicorn.access": logging.INFO,
        "uvicorn.error": logging.INFO,
        "fastapi": logging.INFO,
        "sqlalchemy": logging.WARNING,
        "sqlalchemy.engine": logging.WARNING,
        "httpx": logging.WARNING,
        "requests": logging.WARNING,
        "asyncio": logging.WARNING,
        "celery": logging.INFO,
        "redis": logging.WARNING,
        "openai": logging.WARNING,
    }
    
    for logger_name, level in external_loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Name of the logger (usually __name__)
        
    Returns:
        Configured structlog logger instance
    """
    return structlog.get_logger(name)


class LoggerMixin:
    """
    Mixin class to add logging capabilities to other classes.
    
    Usage:
        class MyClass(LoggerMixin):
            def my_method(self):
                self.logger.info("This is a log message")
    """
    
    @property
    def logger(self) -> structlog.stdlib.BoundLogger:
        """Get logger instance for this class."""
        return get_logger(self.__class__.__module__ + "." + self.__class__.__name__)


def log_function_call(func_name: str, **kwargs: Any) -> None:
    """
    Log a function call with its parameters.
    
    Args:
        func_name: Name of the function being called
        **kwargs: Function parameters to log
    """
    logger = get_logger(__name__)
    logger.debug(
        "Function called",
        function=func_name,
        parameters=kwargs,
    )


def log_api_request(method: str, url: str, status_code: int, duration: float, **kwargs: Any) -> None:
    """
    Log an API request.
    
    Args:
        method: HTTP method
        url: Request URL
        status_code: Response status code
        duration: Request duration in seconds
        **kwargs: Additional request details
    """
    logger = get_logger(__name__)
    logger.info(
        "API request",
        method=method,
        url=url,
        status_code=status_code,
        duration=duration,
        **kwargs,
    )


def log_error(error: Exception, context: Dict[str, Any] = None) -> None:
    """
    Log an error with context.
    
    Args:
        error: Exception that occurred
        context: Additional context information
    """
    logger = get_logger(__name__)
    logger.error(
        "Error occurred",
        error=str(error),
        error_type=type(error).__name__,
        context=context or {},
        exc_info=True,
    )
