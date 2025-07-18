"""
Calendar Model

This module defines the Calendar and Event models for calendar management
in the Bitrix24 AI Assistant application.
"""

from datetime import datetime, timedelta
from typing import Optional, List
from uuid import uuid4
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, String, Text, Integer, ForeignKey, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from app.core.database import Base


class EventStatus(str, Enum):
    """Event status enumeration."""
    CONFIRMED = "confirmed"
    TENTATIVE = "tentative"
    CANCELLED = "cancelled"


class EventVisibility(str, Enum):
    """Event visibility enumeration."""
    PUBLIC = "public"
    PRIVATE = "private"
    CONFIDENTIAL = "confidential"


class EventType(str, Enum):
    """Event type enumeration."""
    MEETING = "meeting"
    APPOINTMENT = "appointment"
    CALL = "call"
    REMINDER = "reminder"
    DEADLINE = "deadline"
    PERSONAL = "personal"
    BUSINESS = "business"
    TRAVEL = "travel"
    HOLIDAY = "holiday"
    BREAK = "break"


class RecurrenceType(str, Enum):
    """Recurrence type enumeration."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class Calendar(Base):
    """
    Calendar model for storing calendar information.
    
    This model represents calendars that can contain events and be synced
    with Bitrix24 calendar system.
    """
    
    __tablename__ = "calendars"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    
    # Basic calendar information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(7), default="#3498db", nullable=False)  # Hex color code
    
    # Calendar settings
    timezone = Column(String(50), default="UTC", nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Bitrix24 integration
    bitrix24_calendar_id = Column(String(100), unique=True, index=True, nullable=True)
    bitrix24_data = Column(JSON, nullable=True)
    
    # Ownership
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    owner = relationship("User", backref="calendars")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Sync information
    last_sync_at = Column(DateTime, nullable=True)
    sync_enabled = Column(Boolean, default=True, nullable=False)
    sync_errors = Column(JSON, nullable=True)
    
    def __repr__(self) -> str:
        """String representation of the Calendar model."""
        return f"<Calendar(id={self.id}, name={self.name})>"
    
    def to_dict(self) -> dict:
        """
        Convert calendar model to dictionary.
        
        Returns:
            dict: Calendar data as dictionary
        """
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "timezone": self.timezone,
            "is_default": self.is_default,
            "is_active": self.is_active,
            "bitrix24_calendar_id": self.bitrix24_calendar_id,
            "owner_id": str(self.owner_id),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_sync_at": self.last_sync_at.isoformat() if self.last_sync_at else None,
            "sync_enabled": self.sync_enabled,
        }


class Event(Base):
    """
    Event model for storing calendar events.
    
    This model represents calendar events that can be created, scheduled,
    and synchronized with Bitrix24.
    """
    
    __tablename__ = "events"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    
    # Basic event information
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    
    # Event timing
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False, index=True)
    all_day = Column(Boolean, default=False, nullable=False)
    timezone = Column(String(50), default="UTC", nullable=False)
    
    # Event properties
    event_type = Column(String(50), default=EventType.MEETING, nullable=False)
    status = Column(String(20), default=EventStatus.CONFIRMED, nullable=False)
    visibility = Column(String(20), default=EventVisibility.PUBLIC, nullable=False)
    
    # Calendar relationship
    calendar_id = Column(UUID(as_uuid=True), ForeignKey("calendars.id"), nullable=False)
    calendar = relationship("Calendar", backref="events")
    
    # Bitrix24 integration
    bitrix24_event_id = Column(String(100), unique=True, index=True, nullable=True)
    bitrix24_data = Column(JSON, nullable=True)
    
    # Ownership and creation
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_by = relationship("User", backref="created_events")
    
    # Attendees (stored as JSON for flexibility)
    attendees = Column(JSON, nullable=True)  # List of attendee objects
    
    # Recurrence
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurrence_type = Column(String(20), nullable=True)
    recurrence_interval = Column(Integer, nullable=True)
    recurrence_end_date = Column(DateTime, nullable=True)
    recurrence_count = Column(Integer, nullable=True)
    master_event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=True)
    
    # Reminders
    reminders = Column(JSON, nullable=True)  # List of reminder objects
    
    # Meeting details
    meeting_url = Column(String(500), nullable=True)
    meeting_id = Column(String(100), nullable=True)
    meeting_password = Column(String(100), nullable=True)
    
    # AI-generated fields
    ai_generated = Column(Boolean, default=False, nullable=False)
    ai_category_confidence = Column(Float, nullable=True)
    ai_suggestions = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Sync information
    last_sync_at = Column(DateTime, nullable=True)
    sync_status = Column(String(20), default="pending", nullable=False)
    
    # Attendance tracking
    attendance_tracked = Column(Boolean, default=False, nullable=False)
    actual_start_time = Column(DateTime, nullable=True)
    actual_end_time = Column(DateTime, nullable=True)
    
    # Tags and categories
    tags = Column(JSON, nullable=True)
    categories = Column(JSON, nullable=True)
    
    # Priority and importance
    priority = Column(String(20), default="medium", nullable=False)
    importance = Column(String(20), default="normal", nullable=False)
    
    def __repr__(self) -> str:
        """String representation of the Event model."""
        return f"<Event(id={self.id}, title={self.title}, start_time={self.start_time})>"
    
    def to_dict(self) -> dict:
        """
        Convert event model to dictionary.
        
        Returns:
            dict: Event data as dictionary
        """
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "all_day": self.all_day,
            "timezone": self.timezone,
            "event_type": self.event_type,
            "status": self.status,
            "visibility": self.visibility,
            "calendar_id": str(self.calendar_id),
            "bitrix24_event_id": self.bitrix24_event_id,
            "created_by_id": str(self.created_by_id),
            "attendees": self.attendees,
            "is_recurring": self.is_recurring,
            "recurrence_type": self.recurrence_type,
            "recurrence_interval": self.recurrence_interval,
            "recurrence_end_date": self.recurrence_end_date.isoformat() if self.recurrence_end_date else None,
            "recurrence_count": self.recurrence_count,
            "master_event_id": str(self.master_event_id) if self.master_event_id else None,
            "reminders": self.reminders,
            "meeting_url": self.meeting_url,
            "meeting_id": self.meeting_id,
            "ai_generated": self.ai_generated,
            "ai_category_confidence": self.ai_category_confidence,
            "ai_suggestions": self.ai_suggestions,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_sync_at": self.last_sync_at.isoformat() if self.last_sync_at else None,
            "sync_status": self.sync_status,
            "attendance_tracked": self.attendance_tracked,
            "actual_start_time": self.actual_start_time.isoformat() if self.actual_start_time else None,
            "actual_end_time": self.actual_end_time.isoformat() if self.actual_end_time else None,
            "tags": self.tags,
            "categories": self.categories,
            "priority": self.priority,
            "importance": self.importance,
        }
    
    @hybrid_property
    def duration(self) -> timedelta:
        """Get event duration."""
        return self.end_time - self.start_time
    
    @hybrid_property
    def duration_minutes(self) -> int:
        """Get event duration in minutes."""
        return int(self.duration.total_seconds() / 60)
    
    @hybrid_property
    def is_today(self) -> bool:
        """Check if event is today."""
        today = datetime.utcnow().date()
        return self.start_time.date() == today
    
    @hybrid_property
    def is_upcoming(self) -> bool:
        """Check if event is upcoming (starts in the future)."""
        return self.start_time > datetime.utcnow()
    
    @hybrid_property
    def is_past(self) -> bool:
        """Check if event is in the past."""
        return self.end_time < datetime.utcnow()
    
    @hybrid_property
    def is_ongoing(self) -> bool:
        """Check if event is currently ongoing."""
        now = datetime.utcnow()
        return self.start_time <= now <= self.end_time
    
    @hybrid_property
    def time_until_start(self) -> Optional[timedelta]:
        """Get time until event starts."""
        if self.is_past or self.is_ongoing:
            return None
        return self.start_time - datetime.utcnow()
    
    def add_attendee(self, email: str, name: str, status: str = "pending") -> None:
        """
        Add an attendee to the event.
        
        Args:
            email: Attendee's email address
            name: Attendee's name
            status: Attendance status (pending, accepted, declined)
        """
        if not self.attendees:
            self.attendees = []
        
        # Check if attendee already exists
        for attendee in self.attendees:
            if attendee.get("email") == email:
                return
        
        self.attendees.append({
            "email": email,
            "name": name,
            "status": status,
            "added_at": datetime.utcnow().isoformat(),
        })
        
        self.updated_at = datetime.utcnow()
    
    def remove_attendee(self, email: str) -> None:
        """
        Remove an attendee from the event.
        
        Args:
            email: Attendee's email address
        """
        if not self.attendees:
            return
        
        self.attendees = [
            attendee for attendee in self.attendees
            if attendee.get("email") != email
        ]
        
        self.updated_at = datetime.utcnow()
    
    def update_attendee_status(self, email: str, status: str) -> None:
        """
        Update attendee's status.
        
        Args:
            email: Attendee's email address
            status: New status (accepted, declined, tentative)
        """
        if not self.attendees:
            return
        
        for attendee in self.attendees:
            if attendee.get("email") == email:
                attendee["status"] = status
                attendee["updated_at"] = datetime.utcnow().isoformat()
                break
        
        self.updated_at = datetime.utcnow()
    
    def add_reminder(self, minutes_before: int, method: str = "email") -> None:
        """
        Add a reminder to the event.
        
        Args:
            minutes_before: Minutes before event to send reminder
            method: Reminder method (email, push, sms)
        """
        if not self.reminders:
            self.reminders = []
        
        # Check if reminder already exists
        for reminder in self.reminders:
            if reminder.get("minutes_before") == minutes_before and reminder.get("method") == method:
                return
        
        self.reminders.append({
            "minutes_before": minutes_before,
            "method": method,
            "sent": False,
            "created_at": datetime.utcnow().isoformat(),
        })
        
        self.updated_at = datetime.utcnow()
    
    def mark_reminder_sent(self, minutes_before: int, method: str) -> None:
        """
        Mark a reminder as sent.
        
        Args:
            minutes_before: Minutes before event
            method: Reminder method
        """
        if not self.reminders:
            return
        
        for reminder in self.reminders:
            if reminder.get("minutes_before") == minutes_before and reminder.get("method") == method:
                reminder["sent"] = True
                reminder["sent_at"] = datetime.utcnow().isoformat()
                break
        
        self.updated_at = datetime.utcnow()
    
    def cancel_event(self) -> None:
        """Cancel the event."""
        self.status = EventStatus.CANCELLED
        self.updated_at = datetime.utcnow()
    
    def reschedule(self, new_start_time: datetime, new_end_time: datetime) -> None:
        """
        Reschedule the event.
        
        Args:
            new_start_time: New start time
            new_end_time: New end time
        """
        if new_start_time >= new_end_time:
            raise ValueError("Start time must be before end time")
        
        self.start_time = new_start_time
        self.end_time = new_end_time
        self.updated_at = datetime.utcnow()
        
        # Reset reminder sent status
        if self.reminders:
            for reminder in self.reminders:
                reminder["sent"] = False
    
    def get_conflicts(self, calendar_events: List['Event']) -> List['Event']:
        """
        Get conflicting events from a list of calendar events.
        
        Args:
            calendar_events: List of events to check for conflicts
            
        Returns:
            List of conflicting events
        """
        conflicts = []
        
        for event in calendar_events:
            if event.id == self.id:
                continue
            
            # Check for time overlap
            if (self.start_time < event.end_time and 
                self.end_time > event.start_time):
                conflicts.append(event)
        
        return conflicts
