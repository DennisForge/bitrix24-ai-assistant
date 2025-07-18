"""
Task Model

This module defines the Task model for task management
in the Bitrix24 AI Assistant application.
"""

from datetime import datetime
from typing import Optional, List
from uuid import uuid4
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, String, Text, Integer, ForeignKey, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from app.core.database import Base


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class TaskPriority(str, Enum):
    """Task priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskCategory(str, Enum):
    """Task category enumeration."""
    GENERAL = "general"
    MEETING = "meeting"
    CALL = "call"
    EMAIL = "email"
    FOLLOW_UP = "follow_up"
    RESEARCH = "research"
    DOCUMENTATION = "documentation"
    DEVELOPMENT = "development"
    TESTING = "testing"
    REVIEW = "review"


class Task(Base):
    """
    Task model for storing task information and management data.
    
    This model represents tasks that can be created, assigned, and tracked
    within the Bitrix24 AI Assistant system.
    """
    
    __tablename__ = "tasks"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    
    # Basic task information
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(50), default=TaskCategory.GENERAL, nullable=False)
    priority = Column(String(20), default=TaskPriority.MEDIUM, nullable=False)
    status = Column(String(20), default=TaskStatus.PENDING, nullable=False)
    
    # Bitrix24 integration
    bitrix24_task_id = Column(String(100), unique=True, index=True, nullable=True)
    bitrix24_data = Column(JSON, nullable=True)
    
    # Assignment and ownership
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Task relationships
    created_by = relationship("User", foreign_keys=[created_by_id], backref="created_tasks")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], backref="assigned_tasks")
    
    # Time tracking
    estimated_hours = Column(Float, nullable=True)
    actual_hours = Column(Float, default=0.0, nullable=False)
    
    # Dates and deadlines
    start_date = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # AI-generated fields
    ai_generated = Column(Boolean, default=False, nullable=False)
    ai_category_confidence = Column(Float, nullable=True)
    ai_priority_confidence = Column(Float, nullable=True)
    ai_sentiment_score = Column(Float, nullable=True)
    ai_suggestions = Column(JSON, nullable=True)
    
    # Progress tracking
    progress_percentage = Column(Integer, default=0, nullable=False)
    last_activity_at = Column(DateTime, nullable=True)
    
    # Notification settings
    reminder_sent = Column(Boolean, default=False, nullable=False)
    reminder_date = Column(DateTime, nullable=True)
    
    # Tags and labels
    tags = Column(JSON, nullable=True)  # List of tags
    labels = Column(JSON, nullable=True)  # List of labels
    
    # Dependencies
    depends_on_tasks = Column(JSON, nullable=True)  # List of task IDs
    blocks_tasks = Column(JSON, nullable=True)  # List of task IDs
    
    # Comments and notes
    comments = Column(JSON, nullable=True)  # List of comments
    notes = Column(Text, nullable=True)
    
    # Attachments
    attachments = Column(JSON, nullable=True)  # List of attachment URLs
    
    # Recurrence
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurrence_pattern = Column(JSON, nullable=True)
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True)
    
    # Performance metrics
    completion_rate = Column(Float, nullable=True)
    average_completion_time = Column(Float, nullable=True)
    
    def __repr__(self) -> str:
        """String representation of the Task model."""
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"
    
    def to_dict(self) -> dict:
        """
        Convert task model to dictionary.
        
        Returns:
            dict: Task data as dictionary
        """
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "priority": self.priority,
            "status": self.status,
            "bitrix24_task_id": self.bitrix24_task_id,
            "created_by_id": str(self.created_by_id),
            "assigned_to_id": str(self.assigned_to_id) if self.assigned_to_id else None,
            "estimated_hours": self.estimated_hours,
            "actual_hours": self.actual_hours,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "ai_generated": self.ai_generated,
            "ai_category_confidence": self.ai_category_confidence,
            "ai_priority_confidence": self.ai_priority_confidence,
            "ai_sentiment_score": self.ai_sentiment_score,
            "ai_suggestions": self.ai_suggestions,
            "progress_percentage": self.progress_percentage,
            "last_activity_at": self.last_activity_at.isoformat() if self.last_activity_at else None,
            "reminder_sent": self.reminder_sent,
            "reminder_date": self.reminder_date.isoformat() if self.reminder_date else None,
            "tags": self.tags,
            "labels": self.labels,
            "depends_on_tasks": self.depends_on_tasks,
            "blocks_tasks": self.blocks_tasks,
            "comments": self.comments,
            "notes": self.notes,
            "attachments": self.attachments,
            "is_recurring": self.is_recurring,
            "recurrence_pattern": self.recurrence_pattern,
            "parent_task_id": str(self.parent_task_id) if self.parent_task_id else None,
            "completion_rate": self.completion_rate,
            "average_completion_time": self.average_completion_time,
        }
    
    @hybrid_property
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if not self.due_date or self.status == TaskStatus.COMPLETED:
            return False
        return datetime.utcnow() > self.due_date
    
    @hybrid_property
    def is_due_soon(self) -> bool:
        """Check if task is due within 24 hours."""
        if not self.due_date or self.status == TaskStatus.COMPLETED:
            return False
        from datetime import timedelta
        return datetime.utcnow() + timedelta(hours=24) >= self.due_date
    
    @hybrid_property
    def time_remaining(self) -> Optional[float]:
        """Get time remaining until due date (in hours)."""
        if not self.due_date or self.status == TaskStatus.COMPLETED:
            return None
        delta = self.due_date - datetime.utcnow()
        return delta.total_seconds() / 3600
    
    @hybrid_property
    def duration_days(self) -> Optional[int]:
        """Get task duration in days."""
        if not self.start_date or not self.due_date:
            return None
        delta = self.due_date - self.start_date
        return delta.days
    
    def mark_completed(self) -> None:
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.progress_percentage = 100
        self.updated_at = datetime.utcnow()
    
    def update_progress(self, percentage: int) -> None:
        """
        Update task progress percentage.
        
        Args:
            percentage: Progress percentage (0-100)
        """
        if not 0 <= percentage <= 100:
            raise ValueError("Progress percentage must be between 0 and 100")
        
        self.progress_percentage = percentage
        self.last_activity_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
        # Auto-complete if 100%
        if percentage == 100 and self.status != TaskStatus.COMPLETED:
            self.mark_completed()
    
    def add_comment(self, comment: str, user_id: str) -> None:
        """
        Add a comment to the task.
        
        Args:
            comment: Comment text
            user_id: ID of the user adding the comment
        """
        if not self.comments:
            self.comments = []
        
        self.comments.append({
            "id": str(uuid4()),
            "text": comment,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
        })
        
        self.last_activity_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def add_attachment(self, filename: str, url: str, user_id: str) -> None:
        """
        Add an attachment to the task.
        
        Args:
            filename: Name of the file
            url: URL to the file
            user_id: ID of the user adding the attachment
        """
        if not self.attachments:
            self.attachments = []
        
        self.attachments.append({
            "id": str(uuid4()),
            "filename": filename,
            "url": url,
            "user_id": user_id,
            "uploaded_at": datetime.utcnow().isoformat(),
        })
        
        self.updated_at = datetime.utcnow()
    
    def add_tag(self, tag: str) -> None:
        """
        Add a tag to the task.
        
        Args:
            tag: Tag to add
        """
        if not self.tags:
            self.tags = []
        
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()
    
    def remove_tag(self, tag: str) -> None:
        """
        Remove a tag from the task.
        
        Args:
            tag: Tag to remove
        """
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.utcnow()
    
    def set_reminder(self, reminder_date: datetime) -> None:
        """
        Set a reminder for the task.
        
        Args:
            reminder_date: When to send the reminder
        """
        self.reminder_date = reminder_date
        self.reminder_sent = False
        self.updated_at = datetime.utcnow()
    
    def calculate_completion_rate(self) -> float:
        """Calculate task completion rate based on historical data."""
        # This would be implemented based on user's historical task completion patterns
        # For now, return a simple calculation
        if self.status == TaskStatus.COMPLETED:
            return 1.0
        elif self.status == TaskStatus.CANCELLED:
            return 0.0
        else:
            return self.progress_percentage / 100.0
