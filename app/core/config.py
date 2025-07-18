"""
Application Configuration

This module contains all configuration settings for the Bitrix24 AI Assistant application.
Settings are loaded from environment variables and .env files.
"""

import os
from typing import Optional, List
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings configuration."""
    
    # Application Settings
    APP_NAME: str = Field("Bitrix24 AI Assistant", env="APP_NAME")
    APP_VERSION: str = Field("1.0.0", env="APP_VERSION")
    APP_DESCRIPTION: str = Field("AI-powered assistant for Bitrix24 CRM", env="APP_DESCRIPTION")
    APP_HOST: str = Field("0.0.0.0", env="APP_HOST")
    APP_PORT: int = Field(8000, env="APP_PORT")
    APP_DEBUG: bool = Field(False, env="APP_DEBUG")
    APP_ENVIRONMENT: str = Field("production", env="APP_ENVIRONMENT")
    
    # Database Settings
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    DATABASE_ECHO: bool = Field(False, env="DATABASE_ECHO")
    DATABASE_POOL_SIZE: int = Field(10, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(20, env="DATABASE_MAX_OVERFLOW")
    
    # Redis Settings
    REDIS_URL: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    REDIS_PASSWORD: Optional[str] = Field(None, env="REDIS_PASSWORD")
    REDIS_DB: int = Field(0, env="REDIS_DB")
    
    # Bitrix24 API Settings
    BITRIX24_WEBHOOK_URL: str = Field(..., env="BITRIX24_WEBHOOK_URL")
    BITRIX24_CLIENT_ID: Optional[str] = Field(None, env="BITRIX24_CLIENT_ID")
    BITRIX24_CLIENT_SECRET: Optional[str] = Field(None, env="BITRIX24_CLIENT_SECRET")
    BITRIX24_SCOPE: str = Field("crm,calendar,tasks,user", env="BITRIX24_SCOPE")
    BITRIX24_DOMAIN: str = Field(..., env="BITRIX24_DOMAIN")
    
    # OpenAI Settings
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field("gpt-4", env="OPENAI_MODEL")
    OPENAI_MAX_TOKENS: int = Field(4000, env="OPENAI_MAX_TOKENS")
    OPENAI_TEMPERATURE: float = Field(0.7, env="OPENAI_TEMPERATURE")
    
    # Email Settings
    EMAIL_HOST: str = Field(..., env="EMAIL_HOST")
    EMAIL_PORT: int = Field(587, env="EMAIL_PORT")
    EMAIL_USERNAME: str = Field(..., env="EMAIL_USERNAME")
    EMAIL_PASSWORD: str = Field(..., env="EMAIL_PASSWORD")
    EMAIL_USE_TLS: bool = Field(True, env="EMAIL_USE_TLS")
    EMAIL_FROM: str = Field(..., env="EMAIL_FROM")
    
    # Security Settings
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field("HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Logging Settings
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FILE: str = Field("logs/app.log", env="LOG_FILE")
    LOG_FORMAT: str = Field("json", env="LOG_FORMAT")
    LOG_ROTATION: str = Field("1 day", env="LOG_ROTATION")
    LOG_RETENTION: str = Field("30 days", env="LOG_RETENTION")
    
    # Calendar Settings
    CALENDAR_SYNC_INTERVAL: int = Field(5, env="CALENDAR_SYNC_INTERVAL")
    CALENDAR_TIMEZONE: str = Field("UTC", env="CALENDAR_TIMEZONE")
    CALENDAR_DEFAULT_DURATION: int = Field(60, env="CALENDAR_DEFAULT_DURATION")
    
    # Task Settings
    TASK_AUTO_ASSIGN: bool = Field(True, env="TASK_AUTO_ASSIGN")
    TASK_DEFAULT_PRIORITY: str = Field("medium", env="TASK_DEFAULT_PRIORITY")
    TASK_REMINDER_ADVANCE: int = Field(1440, env="TASK_REMINDER_ADVANCE")
    
    # AI Settings
    AI_ENABLED: bool = Field(True, env="AI_ENABLED")
    AI_AUTO_CATEGORIZE: bool = Field(True, env="AI_AUTO_CATEGORIZE")
    AI_SENTIMENT_ANALYSIS: bool = Field(True, env="AI_SENTIMENT_ANALYSIS")
    AI_TASK_SUGGESTIONS: bool = Field(True, env="AI_TASK_SUGGESTIONS")
    
    # Scheduler Settings
    SCHEDULER_ENABLED: bool = Field(True, env="SCHEDULER_ENABLED")
    SCHEDULER_TIMEZONE: str = Field("UTC", env="SCHEDULER_TIMEZONE")
    SCHEDULER_MAX_WORKERS: int = Field(4, env="SCHEDULER_MAX_WORKERS")
    
    # File Upload Settings
    UPLOAD_MAX_SIZE: int = Field(10485760, env="UPLOAD_MAX_SIZE")  # 10MB
    UPLOAD_ALLOWED_EXTENSIONS: str = Field(
        "pdf,doc,docx,xls,xlsx,txt,csv,jpg,jpeg,png,gif",
        env="UPLOAD_ALLOWED_EXTENSIONS"
    )
    
    # API Settings
    API_V1_PREFIX: str = Field("/api/v1", env="API_V1_PREFIX")
    API_RATE_LIMIT: int = Field(100, env="API_RATE_LIMIT")
    API_RATE_LIMIT_WINDOW: int = Field(60, env="API_RATE_LIMIT_WINDOW")
    
    # Monitoring Settings
    SENTRY_DSN: Optional[str] = Field(None, env="SENTRY_DSN")
    METRICS_ENABLED: bool = Field(True, env="METRICS_ENABLED")
    HEALTH_CHECK_ENABLED: bool = Field(True, env="HEALTH_CHECK_ENABLED")
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """Validate log level."""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"Log level must be one of {allowed_levels}")
        return v.upper()
    
    @validator("TASK_DEFAULT_PRIORITY")
    def validate_task_priority(cls, v):
        """Validate task priority."""
        allowed_priorities = ["low", "medium", "high", "urgent"]
        if v.lower() not in allowed_priorities:
            raise ValueError(f"Task priority must be one of {allowed_priorities}")
        return v.lower()
    
    @validator("OPENAI_TEMPERATURE")
    def validate_temperature(cls, v):
        """Validate OpenAI temperature."""
        if not 0 <= v <= 2:
            raise ValueError("Temperature must be between 0 and 2")
        return v
    
    @property
    def allowed_upload_extensions(self) -> List[str]:
        """Get list of allowed upload file extensions."""
        return [ext.strip() for ext in self.UPLOAD_ALLOWED_EXTENSIONS.split(",")]
    
    @property
    def bitrix24_scopes(self) -> List[str]:
        """Get list of Bitrix24 API scopes."""
        return [scope.strip() for scope in self.BITRIX24_SCOPE.split(",")]
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
