"""
Smart Scheduler Service with AI-Powered Optimization

This module provides intelligent scheduling capabilities with AI-driven
optimization, conflict resolution, and team productivity analysis.
"""

import asyncio
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import json
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
import redis.asyncio as redis

from app.core.config import settings
from app.core.database import get_async_session
from app.core.logging_config import get_logger
from app.models.calendar import Event
from app.models.user import User
from app.models.task import Task

logger = get_logger(__name__)


class SchedulingPriority(str, Enum):
    """Scheduling priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class MeetingType(str, Enum):
    """Types of meetings for optimization."""
    STANDUP = "standup"
    BRAINSTORMING = "brainstorming"
    PRESENTATION = "presentation"
    DECISION_MAKING = "decision_making"
    ONE_ON_ONE = "one_on_one"
    TEAM_MEETING = "team_meeting"
    CLIENT_CALL = "client_call"


class OptimizationGoal(str, Enum):
    """Scheduling optimization goals."""
    PRODUCTIVITY = "productivity"
    WORK_LIFE_BALANCE = "work_life_balance"
    CREATIVITY = "creativity"
    FOCUS_TIME = "focus_time"
    COLLABORATION = "collaboration"


@dataclass
class TimeSlot:
    """Represents a time slot with availability info."""
    start_time: datetime
    end_time: datetime
    available_users: List[str]
    productivity_score: float
    conflict_score: float
    optimal_for: List[MeetingType]


@dataclass
class SchedulingConstraint:
    """Scheduling constraints for users or meetings."""
    working_hours: Tuple[time, time]  # (start, end)
    break_times: List[Tuple[time, time]]
    meeting_limit_per_day: int
    focus_time_blocks: List[Tuple[time, time]]
    preferred_meeting_duration: int  # minutes
    avoid_back_to_back: bool


@dataclass
class OptimizationResult:
    """Result of scheduling optimization."""
    recommended_time: datetime
    confidence_score: float
    alternative_times: List[datetime]
    reasoning: str
    productivity_impact: str
    conflict_warnings: List[str]


class SmartScheduler:
    """
    AI-powered smart scheduler with advanced optimization capabilities.
    
    Features:
    - Intelligent time slot analysis
    - Team availability optimization  
    - Productivity-based scheduling
    - Conflict detection and resolution
    - Meeting type optimization
    - Workload balancing
    - Serbian language support
    """
    
    def __init__(self):
        self.redis_client = None
        
        if settings.CACHE_ENABLED and settings.REDIS_URL:
            try:
                self.redis_client = redis.from_url(settings.REDIS_URL)
                logger.info("Smart Scheduler Redis client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Redis: {e}")
    
    async def find_optimal_meeting_time(
        self,
        participants: List[str],
        duration_minutes: int,
        meeting_type: MeetingType = MeetingType.TEAM_MEETING,
        priority: SchedulingPriority = SchedulingPriority.MEDIUM,
        preferred_date: Optional[datetime] = None,
        constraints: Optional[Dict[str, SchedulingConstraint]] = None,
        optimization_goal: OptimizationGoal = OptimizationGoal.PRODUCTIVITY
    ) -> OptimizationResult:
        """
        Find optimal meeting time using AI-powered analysis.
        
        Args:
            participants: List of participant user IDs
            duration_minutes: Meeting duration in minutes
            meeting_type: Type of meeting for optimization
            priority: Scheduling priority
            preferred_date: Preferred date (optional)
            constraints: Per-user scheduling constraints
            optimization_goal: Primary optimization goal
            
        Returns:
            OptimizationResult with recommendations
        """
        try:
            logger.info(f"Finding optimal time for {len(participants)} participants, {duration_minutes}min {meeting_type.value}")
            
            # Get search date range
            search_start = preferred_date or datetime.now()
            search_end = search_start + timedelta(days=14)  # 2 weeks ahead
            
            # Analyze participant availability
            availability_data = await self._analyze_team_availability(
                participants, search_start, search_end
            )
            
            # Generate potential time slots
            potential_slots = await self._generate_time_slots(
                participants,
                duration_minutes,
                search_start,
                search_end,
                constraints or {}
            )
            
            # Score and rank time slots
            scored_slots = await self._score_time_slots(
                potential_slots,
                participants,
                meeting_type,
                optimization_goal,
                availability_data
            )
            
            if not scored_slots:
                return OptimizationResult(
                    recommended_time=search_start + timedelta(days=1),
                    confidence_score=0.0,
                    alternative_times=[],
                    reasoning="Nema dostupnih termina za sve učesnike u traženom periodu.",
                    productivity_impact="Nepoznat",
                    conflict_warnings=["Nema slobodnih termina"]
                )
            
            # Select best option
            best_slot = scored_slots[0]
            alternatives = [slot.start_time for slot in scored_slots[1:6]]  # Top 5 alternatives
            
            # Generate reasoning in Serbian
            reasoning = await self._generate_scheduling_reasoning(
                best_slot, participants, meeting_type, optimization_goal
            )
            
            # Analyze productivity impact
            productivity_impact = await self._analyze_productivity_impact(
                best_slot, participants, availability_data
            )
            
            # Check for potential conflicts
            conflict_warnings = await self._check_scheduling_conflicts(
                best_slot, participants
            )
            
            result = OptimizationResult(
                recommended_time=best_slot.start_time,
                confidence_score=best_slot.productivity_score,
                alternative_times=alternatives,
                reasoning=reasoning,
                productivity_impact=productivity_impact,
                conflict_warnings=conflict_warnings
            )
            
            # Cache result for future reference
            await self._cache_scheduling_result(participants, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in optimal meeting scheduling: {e}")
            return OptimizationResult(
                recommended_time=datetime.now() + timedelta(hours=1),
                confidence_score=0.0,
                alternative_times=[],
                reasoning=f"Greška pri pronalaženju optimalnog vremena: {str(e)}",
                productivity_impact="Nepoznat",
                conflict_warnings=[]
            )
    
    async def _analyze_team_availability(
        self,
        participants: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Analyze team availability patterns and productivity data.
        """
        try:
            async with get_async_session() as db:
                availability_data = {}
                
                for user_id in participants:
                    # Get user's existing events
                    events_stmt = (
                        select(Event)
                        .where(Event.user_id == user_id)
                        .where(Event.start_time >= start_date)
                        .where(Event.start_time <= end_date)
                    )
                    events_result = await db.execute(events_stmt)
                    user_events = events_result.scalars().all()
                    
                    # Get user's tasks
                    tasks_stmt = (
                        select(Task)
                        .where(Task.assigned_to == user_id)
                        .where(Task.due_date >= start_date)
                        .where(Task.due_date <= end_date)
                    )
                    tasks_result = await db.execute(tasks_stmt)
                    user_tasks = tasks_result.scalars().all()
                    
                    # Calculate availability patterns
                    busy_slots = []
                    for event in user_events:
                        busy_slots.append({
                            'start': event.start_time,
                            'end': event.start_time + timedelta(minutes=event.duration),
                            'type': 'meeting'
                        })
                    
                    # Add task deadlines as busy periods
                    for task in user_tasks:
                        if task.due_date:
                            # Block 2 hours before deadline for task completion
                            busy_slots.append({
                                'start': task.due_date - timedelta(hours=2),
                                'end': task.due_date,
                                'type': 'deadline'
                            })
                    
                    # Calculate productivity patterns (mock implementation)
                    productivity_patterns = await self._calculate_productivity_patterns(user_id)
                    
                    availability_data[user_id] = {
                        'busy_slots': busy_slots,
                        'productivity_patterns': productivity_patterns,
                        'total_meetings': len([e for e in user_events]),
                        'total_tasks': len(user_tasks),
                        'workload_score': min(len(user_events) / 10.0, 1.0)  # 0-1 scale
                    }
                
                return availability_data
                
        except Exception as e:
            logger.error(f"Error analyzing team availability: {e}")
            return {}
    
    async def _calculate_productivity_patterns(self, user_id: str) -> Dict[str, float]:
        """
        Calculate user's productivity patterns throughout the day.
        
        Returns productivity scores (0-1) for different time periods.
        """
        # This is a simplified implementation
        # In reality, this would analyze historical data
        
        default_patterns = {
            'morning_early': 0.9,    # 8-10 AM
            'morning_late': 0.8,     # 10-12 PM  
            'afternoon_early': 0.6,  # 12-2 PM
            'afternoon_late': 0.7,   # 2-4 PM
            'evening': 0.5,          # 4-6 PM
            'late': 0.3              # After 6 PM
        }
        
        # Try to get cached patterns
        if self.redis_client:
            try:
                cache_key = f"productivity_patterns:{user_id}"
                cached = await self.redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception:
                pass
        
        return default_patterns
    
    async def _generate_time_slots(
        self,
        participants: List[str],
        duration_minutes: int,
        start_date: datetime,
        end_date: datetime,
        constraints: Dict[str, SchedulingConstraint]
    ) -> List[TimeSlot]:
        """
        Generate potential time slots based on constraints and availability.
        """
        time_slots = []
        
        # Default working hours if no constraints provided
        default_start = time(9, 0)  # 9:00 AM
        default_end = time(17, 0)   # 5:00 PM
        
        current_date = start_date.date()
        end_search_date = end_date.date()
        
        while current_date <= end_search_date:
            # Skip weekends for now (can be made configurable)
            if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                current_date += timedelta(days=1)
                continue
            
            # Generate slots for this day
            working_start = datetime.combine(current_date, default_start)
            working_end = datetime.combine(current_date, default_end)
            
            # Generate 30-minute intervals
            current_time = working_start
            while current_time + timedelta(minutes=duration_minutes) <= working_end:
                slot_end = current_time + timedelta(minutes=duration_minutes)
                
                # Check if all participants are potentially available
                available_users = await self._check_slot_availability(
                    current_time, slot_end, participants
                )
                
                if len(available_users) == len(participants):
                    time_slots.append(TimeSlot(
                        start_time=current_time,
                        end_time=slot_end,
                        available_users=available_users,
                        productivity_score=0.0,  # Will be calculated later
                        conflict_score=0.0,     # Will be calculated later
                        optimal_for=[]          # Will be determined later
                    ))
                
                # Move to next slot (30-minute intervals)
                current_time += timedelta(minutes=30)
            
            current_date += timedelta(days=1)
        
        return time_slots
    
    async def _check_slot_availability(
        self,
        start_time: datetime,
        end_time: datetime,
        participants: List[str]
    ) -> List[str]:
        """
        Check which participants are available for a time slot.
        """
        available_users = []
        
        try:
            async with get_async_session() as db:
                for user_id in participants:
                    # Check for conflicting events
                    conflict_stmt = (
                        select(Event)
                        .where(Event.user_id == user_id)
                        .where(
                            or_(
                                and_(Event.start_time <= start_time, 
                                     Event.start_time + timedelta(minutes=Event.duration) > start_time),
                                and_(Event.start_time < end_time,
                                     Event.start_time + timedelta(minutes=Event.duration) >= end_time),
                                and_(Event.start_time >= start_time,
                                     Event.start_time + timedelta(minutes=Event.duration) <= end_time)
                            )
                        )
                    )
                    
                    conflict_result = await db.execute(conflict_stmt)
                    conflicts = conflict_result.scalars().all()
                    
                    if not conflicts:
                        available_users.append(user_id)
                
                return available_users
                
        except Exception as e:
            logger.error(f"Error checking slot availability: {e}")
            return []
    
    async def _score_time_slots(
        self,
        time_slots: List[TimeSlot],
        participants: List[str],
        meeting_type: MeetingType,
        optimization_goal: OptimizationGoal,
        availability_data: Dict[str, Any]
    ) -> List[TimeSlot]:
        """
        Score and rank time slots based on various factors.
        """
        for slot in time_slots:
            score = 0.0
            
            # Base availability score
            score += 0.3  # Base score for being available
            
            # Time of day scoring based on meeting type
            hour = slot.start_time.hour
            
            if meeting_type == MeetingType.BRAINSTORMING:
                # Morning is better for creative work
                if 9 <= hour <= 11:
                    score += 0.4
                elif 14 <= hour <= 16:
                    score += 0.2
            elif meeting_type == MeetingType.STANDUP:
                # Early morning is ideal
                if 9 <= hour <= 10:
                    score += 0.5
                elif 10 <= hour <= 11:
                    score += 0.3
            elif meeting_type == MeetingType.DECISION_MAKING:
                # Mid-morning to early afternoon
                if 10 <= hour <= 14:
                    score += 0.4
            
            # Productivity patterns scoring
            for user_id in participants:
                if user_id in availability_data:
                    patterns = availability_data[user_id]['productivity_patterns']
                    
                    if 8 <= hour <= 10:
                        score += patterns.get('morning_early', 0.5) * 0.1
                    elif 10 <= hour <= 12:
                        score += patterns.get('morning_late', 0.5) * 0.1
                    elif 12 <= hour <= 14:
                        score += patterns.get('afternoon_early', 0.5) * 0.1
                    elif 14 <= hour <= 16:
                        score += patterns.get('afternoon_late', 0.5) * 0.1
                    elif 16 <= hour <= 18:
                        score += patterns.get('evening', 0.5) * 0.1
            
            # Workload balancing
            total_workload = sum(
                availability_data.get(user_id, {}).get('workload_score', 0.5)
                for user_id in participants
            )
            avg_workload = total_workload / len(participants)
            
            # Lower workload is better
            score += (1.0 - avg_workload) * 0.2
            
            # Day of week preferences
            weekday = slot.start_time.weekday()
            if weekday < 4:  # Monday to Thursday
                score += 0.1
            elif weekday == 4:  # Friday
                score += 0.05
            
            slot.productivity_score = min(score, 1.0)
        
        # Sort by score (highest first)
        return sorted(time_slots, key=lambda x: x.productivity_score, reverse=True)
    
    async def _generate_scheduling_reasoning(
        self,
        slot: TimeSlot,
        participants: List[str],
        meeting_type: MeetingType,
        optimization_goal: OptimizationGoal
    ) -> str:
        """
        Generate human-readable reasoning for the scheduling choice in Serbian.
        """
        time_str = slot.start_time.strftime("%d.%m.%Y u %H:%M")
        day_name = ["ponedeljak", "utorak", "sreda", "četvrtak", "petak", "subota", "nedelja"][slot.start_time.weekday()]
        hour = slot.start_time.hour
        
        reasons = [f"Preporučujem {time_str} ({day_name})"]
        
        # Time-based reasoning
        if 9 <= hour <= 11:
            reasons.append("jutarnji termin je idealan za produktivnost")
        elif 11 <= hour <= 13:
            reasons.append("pre-podnevni termin omogućava fokus")
        elif 14 <= hour <= 16:
            reasons.append("popodnevni termin je dobar za kolaboraciju")
        
        # Meeting type reasoning
        if meeting_type == MeetingType.BRAINSTORMING:
            reasons.append("vreme je optimalno za kreativni rad")
        elif meeting_type == MeetingType.STANDUP:
            reasons.append("idealno za kratak status update")
        elif meeting_type == MeetingType.DECISION_MAKING:
            reasons.append("omogućava kvalitetno donošenje odluka")
        
        # Participant availability
        reasons.append(f"svi {len(participants)} učesnika su dostupni")
        
        # Productivity score
        if slot.productivity_score > 0.8:
            reasons.append("visok score produktivnosti ({:.1f})".format(slot.productivity_score))
        elif slot.productivity_score > 0.6:
            reasons.append("dobar score produktivnosti ({:.1f})".format(slot.productivity_score))
        
        return ". ".join(reasons) + "."
    
    async def _analyze_productivity_impact(
        self,
        slot: TimeSlot,
        participants: List[str],
        availability_data: Dict[str, Any]
    ) -> str:
        """
        Analyze the productivity impact of the scheduled meeting.
        """
        if slot.productivity_score > 0.8:
            return "Visok pozitivan uticaj na produktivnost tima"
        elif slot.productivity_score > 0.6:
            return "Umeren pozitivan uticaj na produktivnost"
        elif slot.productivity_score > 0.4:
            return "Neutralan uticaj na produktivnost"
        else:
            return "Mogući negativan uticaj na produktivnost"
    
    async def _check_scheduling_conflicts(
        self,
        slot: TimeSlot,
        participants: List[str]
    ) -> List[str]:
        """
        Check for potential scheduling conflicts and warnings.
        """
        warnings = []
        
        # Check for back-to-back meetings
        for user_id in participants:
            # This would check for meetings immediately before/after
            # Simplified implementation
            pass
        
        # Check for lunch time conflicts
        if 12 <= slot.start_time.hour <= 13:
            warnings.append("Sastanak je zakazan tokom vremena za ručak")
        
        # Check for end-of-day conflicts
        if slot.start_time.hour >= 16:
            warnings.append("Kasni termin može uticati na work-life balance")
        
        # Check for Friday afternoon
        if slot.start_time.weekday() == 4 and slot.start_time.hour >= 15:
            warnings.append("Petak popodne može imati nižu angažovanost")
        
        return warnings
    
    async def _cache_scheduling_result(
        self,
        participants: List[str],
        result: OptimizationResult
    ) -> None:
        """
        Cache scheduling result for analytics and future optimization.
        """
        if not self.redis_client:
            return
        
        try:
            cache_key = f"scheduling_result:{':'.join(sorted(participants))}"
            cache_data = {
                'recommended_time': result.recommended_time.isoformat(),
                'confidence_score': result.confidence_score,
                'reasoning': result.reasoning,
                'timestamp': datetime.now().isoformat()
            }
            
            await self.redis_client.setex(
                cache_key,
                3600,  # 1 hour cache
                json.dumps(cache_data)
            )
        except Exception as e:
            logger.warning(f"Failed to cache scheduling result: {e}")
    
    async def analyze_team_workload(
        self,
        team_members: List[str],
        time_period: str = "week"
    ) -> Dict[str, Any]:
        """
        Analyze team workload and provide optimization recommendations.
        
        Args:
            team_members: List of team member user IDs
            time_period: Analysis period ('week', 'month', 'quarter')
            
        Returns:
            Workload analysis with recommendations
        """
        try:
            # Determine analysis period
            now = datetime.now()
            if time_period == "week":
                start_date = now - timedelta(days=7)
            elif time_period == "month":
                start_date = now - timedelta(days=30)
            else:  # quarter
                start_date = now - timedelta(days=90)
            
            workload_data = {}
            
            async with get_async_session() as db:
                for user_id in team_members:
                    # Get user's events
                    events_stmt = (
                        select(Event)
                        .where(Event.user_id == user_id)
                        .where(Event.start_time >= start_date)
                        .where(Event.start_time <= now)
                    )
                    events_result = await db.execute(events_stmt)
                    user_events = events_result.scalars().all()
                    
                    # Get user's tasks
                    tasks_stmt = (
                        select(Task)
                        .where(Task.assigned_to == user_id)
                        .where(Task.created_at >= start_date)
                    )
                    tasks_result = await db.execute(tasks_stmt)
                    user_tasks = tasks_result.scalars().all()
                    
                    # Calculate workload metrics
                    total_meeting_time = sum(event.duration for event in user_events)
                    meeting_count = len(user_events)
                    task_count = len(user_tasks)
                    
                    # Calculate workload score (0-1)
                    days_in_period = (now - start_date).days
                    avg_meetings_per_day = meeting_count / days_in_period if days_in_period > 0 else 0
                    avg_meeting_hours_per_day = (total_meeting_time / 60) / days_in_period if days_in_period > 0 else 0
                    
                    workload_score = min((avg_meetings_per_day / 5) + (avg_meeting_hours_per_day / 4), 1.0)
                    
                    workload_data[user_id] = {
                        'meeting_count': meeting_count,
                        'total_meeting_time': total_meeting_time,
                        'task_count': task_count,
                        'workload_score': workload_score,
                        'avg_meetings_per_day': round(avg_meetings_per_day, 1),
                        'avg_meeting_hours_per_day': round(avg_meeting_hours_per_day, 1),
                        'status': self._get_workload_status(workload_score)
                    }
            
            # Generate team recommendations
            recommendations = await self._generate_workload_recommendations(workload_data)
            
            return {
                'period': time_period,
                'analysis_date': now.isoformat(),
                'team_workload': workload_data,
                'team_average_score': sum(data['workload_score'] for data in workload_data.values()) / len(workload_data),
                'recommendations': recommendations,
                'summary': self._generate_workload_summary(workload_data)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing team workload: {e}")
            return {
                'error': f"Greška pri analizi opterećenja tima: {str(e)}",
                'team_workload': {},
                'recommendations': []
            }
    
    def _get_workload_status(self, score: float) -> str:
        """Get workload status in Serbian."""
        if score < 0.3:
            return "Nisko opterećenje"
        elif score < 0.6:
            return "Optimalno opterećenje"
        elif score < 0.8:
            return "Visoko opterećenje"
        else:
            return "Preopterećen"
    
    async def _generate_workload_recommendations(self, workload_data: Dict[str, Any]) -> List[str]:
        """Generate workload optimization recommendations in Serbian."""
        recommendations = []
        
        # Find overloaded team members
        overloaded = [uid for uid, data in workload_data.items() if data['workload_score'] > 0.8]
        underloaded = [uid for uid, data in workload_data.items() if data['workload_score'] < 0.3]
        
        if overloaded:
            recommendations.append(f"Preopterećeni članovi tima ({len(overloaded)}): potrebno je redistribuiranje zadataka")
        
        if underloaded:
            recommendations.append(f"Članovi sa niskim opterećenjem ({len(underloaded)}): mogu preuzeti dodatne zadatke")
        
        # Meeting recommendations
        high_meeting_users = [uid for uid, data in workload_data.items() if data['avg_meetings_per_day'] > 4]
        if high_meeting_users:
            recommendations.append("Previše sastanaka dnevno - razmotriti konsolidaciju ili ukidanje nepotrebnih")
        
        # Focus time recommendations
        recommendations.append("Planirati blokove vremena za fokusiran rad bez sastanaka")
        
        return recommendations
    
    def _generate_workload_summary(self, workload_data: Dict[str, Any]) -> str:
        """Generate workload summary in Serbian."""
        total_members = len(workload_data)
        avg_score = sum(data['workload_score'] for data in workload_data.values()) / total_members
        
        if avg_score < 0.4:
            return f"Tim od {total_members} članova ima nisko opterećenje (prosek: {avg_score:.1f})"
        elif avg_score < 0.7:
            return f"Tim od {total_members} članova ima optimalno opterećenje (prosek: {avg_score:.1f})"
        else:
            return f"Tim od {total_members} članova je preopterećen (prosek: {avg_score:.1f})"


# Global smart scheduler instance
smart_scheduler = SmartScheduler()