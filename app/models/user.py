"""
User Model

This module defines the User model for authentication and user management
in the Bitrix24 AI Assistant application.
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, String, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    """
    User model for storing user information and authentication data.
    
    This model represents users who can access the Bitrix24 AI Assistant
    and stores their profile information, preferences, and authentication details.
    """
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    
    # Basic user information
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=True)
    
    # Authentication
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Bitrix24 integration
    bitrix24_user_id = Column(String(100), unique=True, index=True, nullable=True)
    bitrix24_access_token = Column(Text, nullable=True)
    bitrix24_refresh_token = Column(Text, nullable=True)
    bitrix24_token_expires_at = Column(DateTime, nullable=True)
    
    # User preferences
    timezone = Column(String(50), default="UTC", nullable=False)
    language = Column(String(10), default="en", nullable=False)
    theme = Column(String(20), default="light", nullable=False)
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True, nullable=False)
    push_notifications = Column(Boolean, default=True, nullable=False)
    task_reminders = Column(Boolean, default=True, nullable=False)
    calendar_reminders = Column(Boolean, default=True, nullable=False)
    
    # AI preferences
    ai_suggestions_enabled = Column(Boolean, default=True, nullable=False)
    ai_auto_categorize = Column(Boolean, default=True, nullable=False)
    ai_sentiment_analysis = Column(Boolean, default=True, nullable=False)
    
    # Profile information
    avatar_url = Column(String(500), nullable=True)
    phone_number = Column(String(20), nullable=True)
    department = Column(String(100), nullable=True)
    position = Column(String(100), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    last_activity_at = Column(DateTime, nullable=True)
    
    # Login tracking
    login_count = Column(Integer, default=0, nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    account_locked_until = Column(DateTime, nullable=True)
    
    # API usage tracking
    api_calls_count = Column(Integer, default=0, nullable=False)
    api_calls_last_reset = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        """String representation of the User model."""
        return f"<User(id={self.id}, email={self.email}, full_name={self.full_name})>"
    
    def to_dict(self) -> dict:
        """
        Convert user model to dictionary.
        
        Returns:
            dict: User data as dictionary (excluding sensitive information)
        """
        return {
            "id": str(self.id),
            "email": self.email,
            "full_name": self.full_name,
            "username": self.username,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "bitrix24_user_id": self.bitrix24_user_id,
            "timezone": self.timezone,
            "language": self.language,
            "theme": self.theme,
            "email_notifications": self.email_notifications,
            "push_notifications": self.push_notifications,
            "task_reminders": self.task_reminders,
            "calendar_reminders": self.calendar_reminders,
            "ai_suggestions_enabled": self.ai_suggestions_enabled,
            "ai_auto_categorize": self.ai_auto_categorize,
            "ai_sentiment_analysis": self.ai_sentiment_analysis,
            "avatar_url": self.avatar_url,
            "phone_number": self.phone_number,
            "department": self.department,
            "position": self.position,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
            "last_activity_at": self.last_activity_at.isoformat() if self.last_activity_at else None,
            "login_count": self.login_count,
        }
    
    @property
    def is_bitrix24_connected(self) -> bool:
        """Check if user has active Bitrix24 connection."""
        return (
            self.bitrix24_user_id is not None
            and self.bitrix24_access_token is not None
            and (
                self.bitrix24_token_expires_at is None
                or self.bitrix24_token_expires_at > datetime.utcnow()
            )
        )
    
    @property
    def is_account_locked(self) -> bool:
        """Check if user account is locked."""
        return (
            self.account_locked_until is not None
            and self.account_locked_until > datetime.utcnow()
        )
    
    def update_last_activity(self) -> None:
        """Update the last activity timestamp."""
        self.last_activity_at = datetime.utcnow()
    
    def increment_login_count(self) -> None:
        """Increment login count and update last login timestamp."""
        self.login_count += 1
        self.last_login_at = datetime.utcnow()
        self.failed_login_attempts = 0  # Reset failed attempts on successful login
    
    def increment_failed_login(self) -> None:
        """Increment failed login attempts."""
        self.failed_login_attempts += 1
        
        # Lock account after 5 failed attempts for 30 minutes
        if self.failed_login_attempts >= 5:
            from datetime import timedelta
            self.account_locked_until = datetime.utcnow() + timedelta(minutes=30)
    
    def reset_failed_login_attempts(self) -> None:
        """Reset failed login attempts and unlock account."""
        self.failed_login_attempts = 0
        self.account_locked_until = None
    
    def update_bitrix24_tokens(
        self,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> None:
        """
        Update Bitrix24 authentication tokens.
        
        Args:
            access_token: New access token
            refresh_token: New refresh token (optional)
            expires_at: Token expiration time (optional)
        """
        self.bitrix24_access_token = access_token
        if refresh_token:
            self.bitrix24_refresh_token = refresh_token
        if expires_at:
            self.bitrix24_token_expires_at = expires_at
        self.updated_at = datetime.utcnow()
