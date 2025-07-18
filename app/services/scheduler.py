"""
Scheduler Service

This module provides task scheduling and background job management
for the Bitrix24 AI Assistant application.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, Callable, Dict, Any, List
from uuid import uuid4

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class SchedulerService:
    """
    Service for managing scheduled tasks and background jobs.
    
    This service handles:
    - Task scheduling and execution
    - Background job management
    - Recurring task management
    - Calendar event reminders
    - Data synchronization jobs
    """
    
    def __init__(self):
        """Initialize the scheduler service."""
        self.scheduler = None
        self.is_running = False
        self.jobs: Dict[str, Dict[str, Any]] = {}
        
        # Configure job stores and executors
        jobstores = {
            'default': MemoryJobStore()
        }
        
        executors = {
            'default': AsyncIOExecutor()
        }
        
        job_defaults = {
            'coalesce': False,
            'max_instances': 3,
            'misfire_grace_time': 30
        }
        
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=settings.SCHEDULER_TIMEZONE
        )
        
        # Add event listeners
        self.scheduler.add_listener(self._job_listener, mask=None)
    
    async def start(self) -> None:
        """Start the scheduler service."""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        logger.info("Starting scheduler service...")
        
        try:
            self.scheduler.start()
            self.is_running = True
            
            # Schedule default jobs
            await self._schedule_default_jobs()
            
            logger.info("Scheduler service started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler service: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the scheduler service."""
        if not self.is_running:
            logger.warning("Scheduler is not running")
            return
        
        logger.info("Stopping scheduler service...")
        
        try:
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            
            logger.info("Scheduler service stopped successfully")
            
        except Exception as e:
            logger.error(f"Failed to stop scheduler service: {e}")
            raise
    
    def schedule_job(
        self,
        func: Callable,
        trigger_type: str,
        job_id: Optional[str] = None,
        name: Optional[str] = None,
        **trigger_kwargs
    ) -> str:
        """
        Schedule a job.
        
        Args:
            func: Function to execute
            trigger_type: Type of trigger (date, interval, cron)
            job_id: Unique job identifier
            name: Human-readable job name
            **trigger_kwargs: Trigger-specific arguments
            
        Returns:
            str: Job ID
        """
        if not self.is_running:
            raise RuntimeError("Scheduler is not running")
        
        job_id = job_id or str(uuid4())
        
        # Create trigger based on type
        if trigger_type == "date":
            trigger = DateTrigger(**trigger_kwargs)
        elif trigger_type == "interval":
            trigger = IntervalTrigger(**trigger_kwargs)
        elif trigger_type == "cron":
            trigger = CronTrigger(**trigger_kwargs)
        else:
            raise ValueError(f"Unknown trigger type: {trigger_type}")
        
        # Schedule the job
        job = self.scheduler.add_job(
            func,
            trigger=trigger,
            id=job_id,
            name=name or f"Job {job_id}",
            replace_existing=True
        )
        
        # Store job info
        self.jobs[job_id] = {
            "id": job_id,
            "name": name or f"Job {job_id}",
            "function": func.__name__,
            "trigger_type": trigger_type,
            "trigger_kwargs": trigger_kwargs,
            "created_at": datetime.utcnow(),
            "status": "scheduled"
        }
        
        logger.info(f"Job scheduled: {job_id} - {name}")
        
        return job_id
    
    def schedule_once(
        self,
        func: Callable,
        run_date: datetime,
        job_id: Optional[str] = None,
        name: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Schedule a one-time job.
        
        Args:
            func: Function to execute
            run_date: When to run the job
            job_id: Unique job identifier
            name: Human-readable job name
            **kwargs: Additional arguments for the function
            
        Returns:
            str: Job ID
        """
        return self.schedule_job(
            func,
            "date",
            job_id=job_id,
            name=name,
            run_date=run_date,
            kwargs=kwargs
        )
    
    def schedule_recurring(
        self,
        func: Callable,
        interval_type: str,
        interval_value: int,
        job_id: Optional[str] = None,
        name: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        **kwargs
    ) -> str:
        """
        Schedule a recurring job.
        
        Args:
            func: Function to execute
            interval_type: Type of interval (seconds, minutes, hours, days, weeks)
            interval_value: Interval value
            job_id: Unique job identifier
            name: Human-readable job name
            start_date: When to start the recurring job
            end_date: When to end the recurring job
            **kwargs: Additional arguments for the function
            
        Returns:
            str: Job ID
        """
        trigger_kwargs = {
            interval_type: interval_value,
            "start_date": start_date,
            "end_date": end_date,
            "kwargs": kwargs
        }
        
        return self.schedule_job(
            func,
            "interval",
            job_id=job_id,
            name=name,
            **trigger_kwargs
        )
    
    def schedule_cron(
        self,
        func: Callable,
        cron_expression: str,
        job_id: Optional[str] = None,
        name: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Schedule a cron job.
        
        Args:
            func: Function to execute
            cron_expression: Cron expression (e.g., "0 9 * * *")
            job_id: Unique job identifier
            name: Human-readable job name
            **kwargs: Additional arguments for the function
            
        Returns:
            str: Job ID
        """
        # Parse cron expression
        parts = cron_expression.split()
        if len(parts) != 5:
            raise ValueError("Invalid cron expression")
        
        minute, hour, day, month, day_of_week = parts
        
        trigger_kwargs = {
            "minute": minute,
            "hour": hour,
            "day": day,
            "month": month,
            "day_of_week": day_of_week,
            "kwargs": kwargs
        }
        
        return self.schedule_job(
            func,
            "cron",
            job_id=job_id,
            name=name,
            **trigger_kwargs
        )
    
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a scheduled job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            bool: True if job was cancelled, False if not found
        """
        try:
            self.scheduler.remove_job(job_id)
            
            if job_id in self.jobs:
                self.jobs[job_id]["status"] = "cancelled"
                self.jobs[job_id]["cancelled_at"] = datetime.utcnow()
            
            logger.info(f"Job cancelled: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel job {job_id}: {e}")
            return False
    
    def get_job_info(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job information.
        
        Args:
            job_id: Job identifier
            
        Returns:
            dict: Job information or None if not found
        """
        return self.jobs.get(job_id)
    
    def list_jobs(self) -> List[Dict[str, Any]]:
        """
        List all scheduled jobs.
        
        Returns:
            List of job information dictionaries
        """
        return list(self.jobs.values())
    
    def _job_listener(self, event):
        """Handle job events."""
        job_id = event.job_id
        
        if job_id in self.jobs:
            if event.exception:
                self.jobs[job_id]["status"] = "failed"
                self.jobs[job_id]["error"] = str(event.exception)
                self.jobs[job_id]["failed_at"] = datetime.utcnow()
                logger.error(f"Job failed: {job_id} - {event.exception}")
            else:
                self.jobs[job_id]["status"] = "completed"
                self.jobs[job_id]["completed_at"] = datetime.utcnow()
                logger.info(f"Job completed: {job_id}")
    
    async def _schedule_default_jobs(self) -> None:
        """Schedule default system jobs."""
        logger.info("Scheduling default system jobs...")
        
        # Calendar sync job - every 5 minutes
        self.schedule_recurring(
            self._sync_calendars,
            "minutes",
            settings.CALENDAR_SYNC_INTERVAL,
            job_id="calendar_sync",
            name="Calendar Synchronization"
        )
        
        # Task reminder job - every minute
        self.schedule_recurring(
            self._send_task_reminders,
            "minutes",
            1,
            job_id="task_reminders",
            name="Task Reminders"
        )
        
        # Event reminder job - every minute
        self.schedule_recurring(
            self._send_event_reminders,
            "minutes",
            1,
            job_id="event_reminders",
            name="Event Reminders"
        )
        
        # Data cleanup job - daily at 2 AM
        self.schedule_cron(
            self._cleanup_old_data,
            "0 2 * * *",
            job_id="data_cleanup",
            name="Data Cleanup"
        )
        
        # Health check job - every 30 minutes
        self.schedule_recurring(
            self._health_check,
            "minutes",
            30,
            job_id="health_check",
            name="System Health Check"
        )
        
        logger.info("Default system jobs scheduled successfully")
    
    async def _sync_calendars(self) -> None:
        """Synchronize calendars with Bitrix24."""
        logger.debug("Running calendar synchronization...")
        
        try:
            # Import here to avoid circular imports
            from app.services.calendar_service import calendar_service
            await calendar_service.sync_all_calendars()
            
        except Exception as e:
            logger.error(f"Calendar sync failed: {e}")
    
    async def _send_task_reminders(self) -> None:
        """Send task reminders."""
        logger.debug("Checking for task reminders...")
        
        try:
            # Import here to avoid circular imports
            from app.services.task_service import task_service
            await task_service.send_due_task_reminders()
            
        except Exception as e:
            logger.error(f"Task reminder job failed: {e}")
    
    async def _send_event_reminders(self) -> None:
        """Send event reminders."""
        logger.debug("Checking for event reminders...")
        
        try:
            # Import here to avoid circular imports
            from app.services.calendar_service import calendar_service
            await calendar_service.send_event_reminders()
            
        except Exception as e:
            logger.error(f"Event reminder job failed: {e}")
    
    async def _cleanup_old_data(self) -> None:
        """Clean up old data."""
        logger.info("Running data cleanup...")
        
        try:
            # Clean up old logs, temporary files, etc.
            # Implementation would depend on specific cleanup requirements
            pass
            
        except Exception as e:
            logger.error(f"Data cleanup failed: {e}")
    
    async def _health_check(self) -> None:
        """Perform system health check."""
        logger.debug("Running system health check...")
        
        try:
            # Check database connectivity
            from app.core.database import check_db_health
            db_healthy = await check_db_health()
            
            if not db_healthy:
                logger.warning("Database health check failed")
            
            # Check external services
            # Implementation would depend on specific health check requirements
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")


# Global scheduler service instance
scheduler_service = SchedulerService()
