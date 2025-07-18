"""
Bitrix24 Service

This module provides integration with Bitrix24 CRM API for synchronizing
tasks, calendar events, and user data.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_async_session
from app.core.logging_config import get_logger
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.calendar import Calendar, Event, EventStatus
from app.models.user import User

logger = get_logger(__name__)


class Bitrix24Service:
    """
    Service for integrating with Bitrix24 CRM API.
    
    This service handles:
    - Authentication with Bitrix24
    - Task synchronization
    - Calendar event synchronization
    - User data synchronization
    - Webhook handling
    """
    
    def __init__(self):
        """Initialize the Bitrix24 service."""
        self.base_url = settings.BITRIX24_WEBHOOK_URL
        self.domain = settings.BITRIX24_DOMAIN
        self.client_id = settings.BITRIX24_CLIENT_ID
        self.client_secret = settings.BITRIX24_CLIENT_SECRET
        self.timeout = httpx.Timeout(30.0)
        
        # Rate limiting
        self.rate_limit = asyncio.Semaphore(10)  # Max 10 concurrent requests
        self.last_request_time = None
        self.request_interval = 0.1  # 100ms between requests
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated request to Bitrix24 API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request data for POST/PUT requests
            params: Query parameters
            
        Returns:
            API response data
            
        Raises:
            Exception: If request fails
        """
        async with self.rate_limit:
            # Rate limiting
            if self.last_request_time:
                elapsed = datetime.now().timestamp() - self.last_request_time
                if elapsed < self.request_interval:
                    await asyncio.sleep(self.request_interval - elapsed)
            
            url = urljoin(self.base_url, endpoint)
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                try:
                    if method.upper() == "GET":
                        response = await client.get(url, params=params)
                    elif method.upper() == "POST":
                        response = await client.post(url, json=data, params=params)
                    elif method.upper() == "PUT":
                        response = await client.put(url, json=data, params=params)
                    elif method.upper() == "DELETE":
                        response = await client.delete(url, params=params)
                    else:
                        raise ValueError(f"Unsupported HTTP method: {method}")
                    
                    self.last_request_time = datetime.now().timestamp()
                    
                    response.raise_for_status()
                    result = response.json()
                    
                    if not result.get("result"):
                        error_msg = result.get("error_description", "Unknown error")
                        raise Exception(f"Bitrix24 API error: {error_msg}")
                    
                    return result
                
                except httpx.TimeoutException:
                    logger.error(f"Timeout making request to {url}")
                    raise Exception("Request timeout")
                except httpx.HTTPStatusError as e:
                    logger.error(f"HTTP error {e.response.status_code} for {url}")
                    raise Exception(f"HTTP error: {e.response.status_code}")
                except Exception as e:
                    logger.error(f"Error making request to {url}: {e}")
                    raise
    
    async def test_connection(self) -> bool:
        """
        Test connection to Bitrix24 API.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            result = await self._make_request("GET", "profile")
            return result.get("result") is not None
        except Exception as e:
            logger.error(f"Bitrix24 connection test failed: {e}")
            return False
    
    async def get_user_profile(self) -> Optional[Dict[str, Any]]:
        """
        Get current user profile from Bitrix24.
        
        Returns:
            User profile data or None if failed
        """
        try:
            result = await self._make_request("GET", "profile")
            return result.get("result")
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            return None
    
    async def sync_tasks(self, user_id: str) -> Dict[str, int]:
        """
        Synchronize tasks between local database and Bitrix24.
        
        Args:
            user_id: User ID to sync tasks for
            
        Returns:
            Dictionary with sync statistics
        """
        stats = {
            "pulled": 0,
            "pushed": 0,
            "updated": 0,
            "errors": 0
        }
        
        try:
            async with get_async_session() as session:
                # Pull tasks from Bitrix24
                await self._pull_tasks_from_bitrix24(session, user_id, stats)
                
                # Push local tasks to Bitrix24
                await self._push_tasks_to_bitrix24(session, user_id, stats)
                
                await session.commit()
                
            logger.info(f"Task sync completed for user {user_id}: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Task sync failed for user {user_id}: {e}")
            stats["errors"] += 1
            return stats
    
    async def _pull_tasks_from_bitrix24(
        self,
        session: AsyncSession,
        user_id: str,
        stats: Dict[str, int]
    ) -> None:
        """Pull tasks from Bitrix24 to local database."""
        try:
            # Get tasks from Bitrix24
            result = await self._make_request(
                "GET",
                "tasks.task.list",
                params={"filter": {"RESPONSIBLE_ID": user_id}}
            )
            
            bitrix24_tasks = result.get("result", {}).get("tasks", [])
            
            for b24_task in bitrix24_tasks:
                try:
                    # Check if task exists locally
                    existing_task = await session.execute(
                        session.query(Task).filter(
                            Task.bitrix24_task_id == str(b24_task["id"])
                        )
                    )
                    existing_task = existing_task.scalar_one_or_none()
                    
                    if existing_task:
                        # Update existing task
                        await self._update_task_from_bitrix24(existing_task, b24_task)
                        stats["updated"] += 1
                    else:
                        # Create new task
                        await self._create_task_from_bitrix24(session, b24_task, user_id)
                        stats["pulled"] += 1
                        
                except Exception as e:
                    logger.error(f"Error processing Bitrix24 task {b24_task.get('id')}: {e}")
                    stats["errors"] += 1
                    
        except Exception as e:
            logger.error(f"Error pulling tasks from Bitrix24: {e}")
            stats["errors"] += 1
    
    async def _push_tasks_to_bitrix24(
        self,
        session: AsyncSession,
        user_id: str,
        stats: Dict[str, int]
    ) -> None:
        """Push local tasks to Bitrix24."""
        try:
            # Get local tasks that need to be pushed
            local_tasks = await session.execute(
                session.query(Task).filter(
                    Task.created_by_id == user_id,
                    Task.bitrix24_task_id.is_(None)
                )
            )
            local_tasks = local_tasks.scalars().all()
            
            for task in local_tasks:
                try:
                    # Create task in Bitrix24
                    b24_task_data = self._convert_task_to_bitrix24(task)
                    result = await self._make_request(
                        "POST",
                        "tasks.task.add",
                        data={"fields": b24_task_data}
                    )
                    
                    if result.get("result", {}).get("task"):
                        b24_task_id = result["result"]["task"]["id"]
                        task.bitrix24_task_id = str(b24_task_id)
                        task.bitrix24_data = result["result"]["task"]
                        stats["pushed"] += 1
                        
                except Exception as e:
                    logger.error(f"Error pushing task {task.id} to Bitrix24: {e}")
                    stats["errors"] += 1
                    
        except Exception as e:
            logger.error(f"Error pushing tasks to Bitrix24: {e}")
            stats["errors"] += 1
    
    async def _create_task_from_bitrix24(
        self,
        session: AsyncSession,
        b24_task: Dict[str, Any],
        user_id: str
    ) -> Task:
        """Create a local task from Bitrix24 task data."""
        task = Task(
            title=b24_task.get("title", ""),
            description=b24_task.get("description", ""),
            priority=self._convert_bitrix24_priority(b24_task.get("priority", "1")),
            status=self._convert_bitrix24_status(b24_task.get("status", "2")),
            created_by_id=user_id,
            bitrix24_task_id=str(b24_task["id"]),
            bitrix24_data=b24_task
        )
        
        # Set dates
        if b24_task.get("deadline"):
            task.due_date = datetime.fromisoformat(b24_task["deadline"])
        
        if b24_task.get("createdDate"):
            task.created_at = datetime.fromisoformat(b24_task["createdDate"])
        
        session.add(task)
        return task
    
    async def _update_task_from_bitrix24(
        self,
        task: Task,
        b24_task: Dict[str, Any]
    ) -> None:
        """Update a local task from Bitrix24 task data."""
        task.title = b24_task.get("title", task.title)
        task.description = b24_task.get("description", task.description)
        task.priority = self._convert_bitrix24_priority(b24_task.get("priority", "1"))
        task.status = self._convert_bitrix24_status(b24_task.get("status", "2"))
        task.bitrix24_data = b24_task
        
        # Update dates
        if b24_task.get("deadline"):
            task.due_date = datetime.fromisoformat(b24_task["deadline"])
        
        task.updated_at = datetime.utcnow()
    
    def _convert_task_to_bitrix24(self, task: Task) -> Dict[str, Any]:
        """Convert local task to Bitrix24 task format."""
        return {
            "TITLE": task.title,
            "DESCRIPTION": task.description or "",
            "PRIORITY": self._convert_priority_to_bitrix24(task.priority),
            "STATUS": self._convert_status_to_bitrix24(task.status),
            "DEADLINE": task.due_date.isoformat() if task.due_date else None,
            "RESPONSIBLE_ID": task.assigned_to_id or task.created_by_id,
        }
    
    def _convert_bitrix24_priority(self, priority: str) -> TaskPriority:
        """Convert Bitrix24 priority to local priority."""
        priority_map = {
            "0": TaskPriority.LOW,
            "1": TaskPriority.MEDIUM,
            "2": TaskPriority.HIGH,
            "3": TaskPriority.URGENT,
        }
        return priority_map.get(priority, TaskPriority.MEDIUM)
    
    def _convert_priority_to_bitrix24(self, priority: TaskPriority) -> str:
        """Convert local priority to Bitrix24 priority."""
        priority_map = {
            TaskPriority.LOW: "0",
            TaskPriority.MEDIUM: "1",
            TaskPriority.HIGH: "2",
            TaskPriority.URGENT: "3",
        }
        return priority_map.get(priority, "1")
    
    def _convert_bitrix24_status(self, status: str) -> TaskStatus:
        """Convert Bitrix24 status to local status."""
        status_map = {
            "1": TaskStatus.PENDING,
            "2": TaskStatus.PENDING,
            "3": TaskStatus.IN_PROGRESS,
            "4": TaskStatus.COMPLETED,
            "5": TaskStatus.COMPLETED,
            "6": TaskStatus.CANCELLED,
            "7": TaskStatus.CANCELLED,
        }
        return status_map.get(status, TaskStatus.PENDING)
    
    def _convert_status_to_bitrix24(self, status: TaskStatus) -> str:
        """Convert local status to Bitrix24 status."""
        status_map = {
            TaskStatus.PENDING: "2",
            TaskStatus.IN_PROGRESS: "3",
            TaskStatus.COMPLETED: "5",
            TaskStatus.CANCELLED: "6",
            TaskStatus.ON_HOLD: "2",
        }
        return status_map.get(status, "2")
    
    async def sync_calendar_events(self, user_id: str) -> Dict[str, int]:
        """
        Synchronize calendar events between local database and Bitrix24.
        
        Args:
            user_id: User ID to sync events for
            
        Returns:
            Dictionary with sync statistics
        """
        stats = {
            "pulled": 0,
            "pushed": 0,
            "updated": 0,
            "errors": 0
        }
        
        try:
            async with get_async_session() as session:
                # Pull events from Bitrix24
                await self._pull_events_from_bitrix24(session, user_id, stats)
                
                # Push local events to Bitrix24
                await self._push_events_to_bitrix24(session, user_id, stats)
                
                await session.commit()
                
            logger.info(f"Calendar sync completed for user {user_id}: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Calendar sync failed for user {user_id}: {e}")
            stats["errors"] += 1
            return stats
    
    async def _pull_events_from_bitrix24(
        self,
        session: AsyncSession,
        user_id: str,
        stats: Dict[str, int]
    ) -> None:
        """Pull calendar events from Bitrix24."""
        try:
            # Get events from Bitrix24
            result = await self._make_request(
                "GET",
                "calendar.event.get",
                params={"filter": {"OWNER_ID": user_id}}
            )
            
            bitrix24_events = result.get("result", [])
            
            for b24_event in bitrix24_events:
                try:
                    # Check if event exists locally
                    existing_event = await session.execute(
                        session.query(Event).filter(
                            Event.bitrix24_event_id == str(b24_event["ID"])
                        )
                    )
                    existing_event = existing_event.scalar_one_or_none()
                    
                    if existing_event:
                        # Update existing event
                        await self._update_event_from_bitrix24(existing_event, b24_event)
                        stats["updated"] += 1
                    else:
                        # Create new event
                        await self._create_event_from_bitrix24(session, b24_event, user_id)
                        stats["pulled"] += 1
                        
                except Exception as e:
                    logger.error(f"Error processing Bitrix24 event {b24_event.get('ID')}: {e}")
                    stats["errors"] += 1
                    
        except Exception as e:
            logger.error(f"Error pulling events from Bitrix24: {e}")
            stats["errors"] += 1
    
    async def _push_events_to_bitrix24(
        self,
        session: AsyncSession,
        user_id: str,
        stats: Dict[str, int]
    ) -> None:
        """Push local events to Bitrix24."""
        try:
            # Get local events that need to be pushed
            local_events = await session.execute(
                session.query(Event).filter(
                    Event.created_by_id == user_id,
                    Event.bitrix24_event_id.is_(None)
                )
            )
            local_events = local_events.scalars().all()
            
            for event in local_events:
                try:
                    # Create event in Bitrix24
                    b24_event_data = self._convert_event_to_bitrix24(event)
                    result = await self._make_request(
                        "POST",
                        "calendar.event.add",
                        data=b24_event_data
                    )
                    
                    if result.get("result"):
                        b24_event_id = result["result"]
                        event.bitrix24_event_id = str(b24_event_id)
                        stats["pushed"] += 1
                        
                except Exception as e:
                    logger.error(f"Error pushing event {event.id} to Bitrix24: {e}")
                    stats["errors"] += 1
                    
        except Exception as e:
            logger.error(f"Error pushing events to Bitrix24: {e}")
            stats["errors"] += 1
    
    async def _create_event_from_bitrix24(
        self,
        session: AsyncSession,
        b24_event: Dict[str, Any],
        user_id: str
    ) -> Event:
        """Create a local event from Bitrix24 event data."""
        # First, get or create a default calendar
        calendar = await session.execute(
            session.query(Calendar).filter(
                Calendar.owner_id == user_id,
                Calendar.is_default == True
            )
        )
        calendar = calendar.scalar_one_or_none()
        
        if not calendar:
            calendar = Calendar(
                name="Default Calendar",
                owner_id=user_id,
                is_default=True
            )
            session.add(calendar)
            await session.flush()
        
        event = Event(
            title=b24_event.get("NAME", ""),
            description=b24_event.get("DESCRIPTION", ""),
            location=b24_event.get("LOCATION", ""),
            start_time=datetime.fromisoformat(b24_event.get("DATE_FROM", "")),
            end_time=datetime.fromisoformat(b24_event.get("DATE_TO", "")),
            calendar_id=calendar.id,
            created_by_id=user_id,
            bitrix24_event_id=str(b24_event["ID"]),
            bitrix24_data=b24_event
        )
        
        session.add(event)
        return event
    
    async def _update_event_from_bitrix24(
        self,
        event: Event,
        b24_event: Dict[str, Any]
    ) -> None:
        """Update a local event from Bitrix24 event data."""
        event.title = b24_event.get("NAME", event.title)
        event.description = b24_event.get("DESCRIPTION", event.description)
        event.location = b24_event.get("LOCATION", event.location)
        event.start_time = datetime.fromisoformat(b24_event.get("DATE_FROM", ""))
        event.end_time = datetime.fromisoformat(b24_event.get("DATE_TO", ""))
        event.bitrix24_data = b24_event
        event.updated_at = datetime.utcnow()
    
    def _convert_event_to_bitrix24(self, event: Event) -> Dict[str, Any]:
        """Convert local event to Bitrix24 event format."""
        return {
            "type": "user",
            "fields": {
                "NAME": event.title,
                "DESCRIPTION": event.description or "",
                "LOCATION": event.location or "",
                "DATE_FROM": event.start_time.isoformat(),
                "DATE_TO": event.end_time.isoformat(),
                "SKIP_TIME": "N" if not event.all_day else "Y",
            }
        }
    
    async def create_webhook_handler(self, event_type: str, handler_url: str) -> bool:
        """
        Create a webhook handler in Bitrix24.
        
        Args:
            event_type: Type of event to handle
            handler_url: URL to send webhook data to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = await self._make_request(
                "POST",
                "event.bind",
                data={
                    "event": event_type,
                    "handler": handler_url
                }
            )
            
            return result.get("result", False)
            
        except Exception as e:
            logger.error(f"Error creating webhook handler: {e}")
            return False
    
    async def handle_webhook(self, event_type: str, data: Dict[str, Any]) -> bool:
        """
        Handle incoming webhook from Bitrix24.
        
        Args:
            event_type: Type of event
            data: Webhook data
            
        Returns:
            True if handled successfully, False otherwise
        """
        try:
            if event_type.startswith("ONTASK"):
                await self._handle_task_webhook(event_type, data)
            elif event_type.startswith("ONCALENDAR"):
                await self._handle_calendar_webhook(event_type, data)
            else:
                logger.warning(f"Unknown webhook event type: {event_type}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling webhook {event_type}: {e}")
            return False
    
    async def _handle_task_webhook(self, event_type: str, data: Dict[str, Any]) -> None:
        """Handle task-related webhook events."""
        task_id = data.get("data", {}).get("FIELDS_AFTER", {}).get("ID")
        
        if not task_id:
            return
        
        async with get_async_session() as session:
            # Find local task
            local_task = await session.execute(
                session.query(Task).filter(
                    Task.bitrix24_task_id == str(task_id)
                )
            )
            local_task = local_task.scalar_one_or_none()
            
            if event_type == "ONTASKADD":
                if not local_task:
                    # Create new task
                    await self._create_task_from_bitrix24(
                        session, 
                        data["data"]["FIELDS_AFTER"], 
                        data["data"]["FIELDS_AFTER"]["RESPONSIBLE_ID"]
                    )
            elif event_type == "ONTASKUPDATE":
                if local_task:
                    # Update existing task
                    await self._update_task_from_bitrix24(
                        local_task,
                        data["data"]["FIELDS_AFTER"]
                    )
            elif event_type == "ONTASKDELETE":
                if local_task:
                    # Delete task
                    await session.delete(local_task)
            
            await session.commit()
    
    async def _handle_calendar_webhook(self, event_type: str, data: Dict[str, Any]) -> None:
        """Handle calendar-related webhook events."""
        event_id = data.get("data", {}).get("FIELDS_AFTER", {}).get("ID")
        
        if not event_id:
            return
        
        async with get_async_session() as session:
            # Find local event
            local_event = await session.execute(
                session.query(Event).filter(
                    Event.bitrix24_event_id == str(event_id)
                )
            )
            local_event = local_event.scalar_one_or_none()
            
            if event_type == "ONCALENDAREVENTADD":
                if not local_event:
                    # Create new event
                    await self._create_event_from_bitrix24(
                        session,
                        data["data"]["FIELDS_AFTER"],
                        data["data"]["FIELDS_AFTER"]["OWNER_ID"]
                    )
            elif event_type == "ONCALENDAREVENTUPDATE":
                if local_event:
                    # Update existing event
                    await self._update_event_from_bitrix24(
                        local_event,
                        data["data"]["FIELDS_AFTER"]
                    )
            elif event_type == "ONCALENDAREVENTDELETE":
                if local_event:
                    # Delete event
                    await session.delete(local_event)
            
            await session.commit()


# Global Bitrix24 service instance
bitrix24_service = Bitrix24Service()
