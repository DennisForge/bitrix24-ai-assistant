"""
AI Assistant Service

This module provides AI-powered assistance using OpenAI's GPT models
for task analysis, suggestions, and automated responses.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

import openai
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_async_session
from app.core.logging_config import get_logger
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.calendar import Event
from app.models.user import User

logger = get_logger(__name__)


class SuggestionType(str, Enum):
    """Types of AI suggestions."""
    TASK_CREATION = "task_creation"
    TASK_PRIORITIZATION = "task_prioritization"
    SCHEDULE_OPTIMIZATION = "schedule_optimization"
    PRODUCTIVITY_INSIGHT = "productivity_insight"
    MEETING_SCHEDULING = "meeting_scheduling"
    DEADLINE_WARNING = "deadline_warning"
    WORKLOAD_BALANCING = "workload_balancing"


class AIAssistantService:
    """
    Service for AI-powered assistance and automation.
    
    This service provides:
    - Task analysis and suggestions
    - Automated task categorization
    - Intelligent scheduling recommendations
    - Productivity insights
    - Natural language processing for task creation
    - Sentiment analysis for task descriptions
    """
    
    def __init__(self):
        """Initialize the AI Assistant service."""
        self.client = None
        self.enabled = settings.AI_ENABLED
        
        if self.enabled and settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.OPENAI_MODEL
            self.max_tokens = settings.OPENAI_MAX_TOKENS
            self.temperature = settings.OPENAI_TEMPERATURE
        else:
            logger.warning("AI features disabled: missing OpenAI API key")
    
    async def chat_with_assistant(
        self,
        message: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Chat with the AI assistant.
        
        Args:
            message: User message
            user_id: User ID for context
            context: Additional context for the conversation
            
        Returns:
            AI response with suggestions and actions
        """
        if not self.enabled or not self.client:
            return {
                "response": "AI assistant is currently disabled. Please enable it in settings.",
                "suggestions": [],
                "actions": []
            }
        
        try:
            # Get user context
            user_context = await self._get_user_context(user_id)
            
            # Build conversation context
            system_prompt = self._build_system_prompt(user_context, context)
            
            # Make request to OpenAI
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                functions=[
                    {
                        "name": "create_task",
                        "description": "Create a new task based on user input",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "description": {"type": "string"},
                                "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
                                "due_date": {"type": "string", "format": "date-time"},
                                "category": {"type": "string"}
                            },
                            "required": ["title"]
                        }
                    },
                    {
                        "name": "schedule_meeting",
                        "description": "Schedule a meeting or event",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "description": {"type": "string"},
                                "start_time": {"type": "string", "format": "date-time"},
                                "duration": {"type": "integer"},
                                "attendees": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["title", "start_time"]
                        }
                    }
                ],
                function_call="auto"
            )
            
            # Process response
            result = await self._process_ai_response(response, user_id)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in AI chat: {e}")
            return {
                "response": "I apologize, but I encountered an error. Please try again.",
                "suggestions": [],
                "actions": []
            }
    
    async def analyze_task(self, task: Task) -> Dict[str, Any]:
        """
        Analyze a task and provide AI insights.
        
        Args:
            task: Task to analyze
            
        Returns:
            Analysis results with suggestions
        """
        if not self.enabled or not self.client:
            return {"analysis": "AI analysis disabled", "suggestions": []}
        
        try:
            prompt = f"""
            Analyze the following task and provide insights:
            
            Title: {task.title}
            Description: {task.description or 'No description'}
            Priority: {task.priority}
            Status: {task.status}
            Due Date: {task.due_date.isoformat() if task.due_date else 'No due date'}
            
            Please provide:
            1. Task complexity assessment
            2. Estimated time to complete
            3. Suggested priority level
            4. Potential blockers or dependencies
            5. Optimization recommendations
            """
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3
            )
            
            analysis = response.choices[0].message.content
            
            # Extract priority and time estimates
            priority_confidence = await self._extract_priority_confidence(analysis)
            time_estimate = await self._extract_time_estimate(analysis)
            
            return {
                "analysis": analysis,
                "priority_confidence": priority_confidence,
                "time_estimate": time_estimate,
                "suggestions": await self._extract_suggestions(analysis)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing task {task.id}: {e}")
            return {"analysis": "Analysis failed", "suggestions": []}
    
    async def categorize_task(self, task_title: str, task_description: str = "") -> Dict[str, Any]:
        """
        Automatically categorize a task using AI.
        
        Args:
            task_title: Task title
            task_description: Task description
            
        Returns:
            Categorization results
        """
        if not self.enabled or not self.client:
            return {"category": "general", "confidence": 0.0}
        
        try:
            prompt = f"""
            Categorize the following task into one of these categories:
            - meeting
            - call  
            - email
            - follow_up
            - research
            - documentation
            - development
            - testing
            - review
            - general
            
            Task: {task_title}
            Description: {task_description}
            
            Respond with just the category name and confidence level (0-1).
            Format: category:confidence
            """
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            
            if ":" in result:
                category, confidence = result.split(":", 1)
                return {
                    "category": category.strip(),
                    "confidence": float(confidence.strip())
                }
            else:
                return {"category": "general", "confidence": 0.5}
                
        except Exception as e:
            logger.error(f"Error categorizing task: {e}")
            return {"category": "general", "confidence": 0.0}
    
    async def suggest_task_priority(self, task: Task) -> Dict[str, Any]:
        """
        Suggest task priority based on AI analysis.
        
        Args:
            task: Task to analyze
            
        Returns:
            Priority suggestion with confidence
        """
        if not self.enabled or not self.client:
            return {"priority": task.priority, "confidence": 0.0}
        
        try:
            prompt = f"""
            Suggest the priority level for this task:
            
            Title: {task.title}
            Description: {task.description or 'No description'}
            Due Date: {task.due_date.isoformat() if task.due_date else 'No due date'}
            Current Priority: {task.priority}
            
            Consider:
            - Urgency (time sensitivity)
            - Importance (impact on goals)
            - Dependencies
            - Effort required
            
            Respond with: priority:confidence
            Priorities: low, medium, high, urgent
            """
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            
            if ":" in result:
                priority, confidence = result.split(":", 1)
                return {
                    "priority": priority.strip(),
                    "confidence": float(confidence.strip())
                }
            else:
                return {"priority": task.priority, "confidence": 0.5}
                
        except Exception as e:
            logger.error(f"Error suggesting priority for task {task.id}: {e}")
            return {"priority": task.priority, "confidence": 0.0}
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text (task description, comments, etc.).
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment analysis results
        """
        if not self.enabled or not self.client:
            return {"sentiment": "neutral", "score": 0.0}
        
        try:
            prompt = f"""
            Analyze the sentiment of this text:
            
            "{text}"
            
            Respond with: sentiment:score
            Sentiment: positive, negative, neutral
            Score: -1.0 to 1.0 (negative to positive)
            """
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            
            if ":" in result:
                sentiment, score = result.split(":", 1)
                return {
                    "sentiment": sentiment.strip(),
                    "score": float(score.strip())
                }
            else:
                return {"sentiment": "neutral", "score": 0.0}
                
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {"sentiment": "neutral", "score": 0.0}
    
    async def generate_task_suggestions(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Generate AI-powered task suggestions for a user.
        
        Args:
            user_id: User ID to generate suggestions for
            
        Returns:
            List of task suggestions
        """
        if not self.enabled or not self.client:
            return []
        
        try:
            # Get user context
            user_context = await self._get_user_context(user_id)
            
            prompt = f"""
            Based on the user's current tasks and schedule, suggest 3-5 new tasks or improvements:
            
            Current Context:
            - Active tasks: {len(user_context.get('active_tasks', []))}
            - Overdue tasks: {len(user_context.get('overdue_tasks', []))}
            - Upcoming events: {len(user_context.get('upcoming_events', []))}
            
            Recent tasks:
            {self._format_tasks_for_ai(user_context.get('recent_tasks', []))}
            
            Provide suggestions for:
            1. Task optimization
            2. Time management
            3. Productivity improvements
            4. Missing or forgotten tasks
            5. Schedule optimization
            
            Format each suggestion as:
            Type: suggestion_type
            Title: suggestion_title
            Description: suggestion_description
            Priority: low/medium/high
            """
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.7
            )
            
            suggestions_text = response.choices[0].message.content
            suggestions = await self._parse_suggestions(suggestions_text)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating task suggestions: {e}")
            return []
    
    async def optimize_schedule(self, user_id: str, date: datetime) -> Dict[str, Any]:
        """
        Provide schedule optimization suggestions.
        
        Args:
            user_id: User ID
            date: Date to optimize
            
        Returns:
            Schedule optimization suggestions
        """
        if not self.enabled or not self.client:
            return {"suggestions": [], "optimization_score": 0.0}
        
        try:
            async with get_async_session() as session:
                # Get user's events and tasks for the date
                start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = start_date + timedelta(days=1)
                
                events = await session.execute(
                    session.query(Event).filter(
                        Event.created_by_id == user_id,
                        Event.start_time >= start_date,
                        Event.start_time < end_date
                    )
                )
                events = events.scalars().all()
                
                tasks = await session.execute(
                    session.query(Task).filter(
                        Task.created_by_id == user_id,
                        Task.due_date >= start_date,
                        Task.due_date < end_date,
                        Task.status != TaskStatus.COMPLETED
                    )
                )
                tasks = tasks.scalars().all()
            
            # Analyze schedule
            schedule_analysis = await self._analyze_schedule(events, tasks, date)
            
            return schedule_analysis
            
        except Exception as e:
            logger.error(f"Error optimizing schedule: {e}")
            return {"suggestions": [], "optimization_score": 0.0}
    
    async def _get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get user context for AI analysis."""
        try:
            async with get_async_session() as session:
                # Get user
                user = await session.get(User, user_id)
                
                # Get recent tasks
                recent_tasks = await session.execute(
                    session.query(Task).filter(
                        Task.created_by_id == user_id
                    ).order_by(Task.updated_at.desc()).limit(10)
                )
                recent_tasks = recent_tasks.scalars().all()
                
                # Get active tasks
                active_tasks = await session.execute(
                    session.query(Task).filter(
                        Task.created_by_id == user_id,
                        Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS])
                    )
                )
                active_tasks = active_tasks.scalars().all()
                
                # Get overdue tasks
                overdue_tasks = await session.execute(
                    session.query(Task).filter(
                        Task.created_by_id == user_id,
                        Task.due_date < datetime.utcnow(),
                        Task.status != TaskStatus.COMPLETED
                    )
                )
                overdue_tasks = overdue_tasks.scalars().all()
                
                # Get upcoming events
                upcoming_events = await session.execute(
                    session.query(Event).filter(
                        Event.created_by_id == user_id,
                        Event.start_time > datetime.utcnow(),
                        Event.start_time < datetime.utcnow() + timedelta(days=7)
                    )
                )
                upcoming_events = upcoming_events.scalars().all()
                
                return {
                    "user": user,
                    "recent_tasks": recent_tasks,
                    "active_tasks": active_tasks,
                    "overdue_tasks": overdue_tasks,
                    "upcoming_events": upcoming_events
                }
                
        except Exception as e:
            logger.error(f"Error getting user context: {e}")
            return {}
    
    def _build_system_prompt(
        self,
        user_context: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build system prompt for AI assistant."""
        user = user_context.get("user")
        
        prompt = f"""
        You are an AI assistant for Bitrix24 CRM integration. You help users manage tasks, 
        schedule meetings, and optimize their productivity.
        
        Current user: {user.full_name if user else 'Unknown'}
        Active tasks: {len(user_context.get('active_tasks', []))}
        Overdue tasks: {len(user_context.get('overdue_tasks', []))}
        Upcoming events: {len(user_context.get('upcoming_events', []))}
        
        You can:
        1. Create tasks and schedule meetings using function calls
        2. Analyze tasks and provide productivity insights
        3. Suggest optimizations for workflow
        4. Answer questions about the user's schedule and tasks
        
        Be helpful, concise, and proactive in suggesting improvements.
        """
        
        if context:
            prompt += f"\n\nAdditional context: {json.dumps(context, indent=2)}"
        
        return prompt
    
    def _format_tasks_for_ai(self, tasks: List[Task]) -> str:
        """Format tasks for AI analysis."""
        if not tasks:
            return "No tasks"
        
        formatted = []
        for task in tasks[:5]:  # Limit to 5 tasks
            formatted.append(
                f"- {task.title} ({task.priority}, {task.status})"
            )
        
        return "\n".join(formatted)
    
    async def _process_ai_response(
        self,
        response: Any,
        user_id: str
    ) -> Dict[str, Any]:
        """Process AI response and extract actions."""
        choice = response.choices[0]
        message = choice.message
        
        result = {
            "response": message.content or "",
            "suggestions": [],
            "actions": []
        }
        
        # Check for function calls
        if message.function_call:
            function_name = message.function_call.name
            function_args = json.loads(message.function_call.arguments)
            
            if function_name == "create_task":
                result["actions"].append({
                    "type": "create_task",
                    "data": function_args
                })
            elif function_name == "schedule_meeting":
                result["actions"].append({
                    "type": "schedule_meeting",
                    "data": function_args
                })
        
        return result
    
    async def _extract_priority_confidence(self, analysis: str) -> float:
        """Extract priority confidence from analysis text."""
        # Simple keyword-based confidence extraction
        high_confidence_keywords = ["urgent", "critical", "important", "deadline"]
        medium_confidence_keywords = ["should", "consider", "might", "could"]
        
        analysis_lower = analysis.lower()
        
        high_count = sum(1 for word in high_confidence_keywords if word in analysis_lower)
        medium_count = sum(1 for word in medium_confidence_keywords if word in analysis_lower)
        
        if high_count > 0:
            return min(0.8 + (high_count * 0.1), 1.0)
        elif medium_count > 0:
            return 0.5 + (medium_count * 0.1)
        else:
            return 0.3
    
    async def _extract_time_estimate(self, analysis: str) -> Optional[float]:
        """Extract time estimate from analysis text."""
        # Simple pattern matching for time estimates
        import re
        
        time_patterns = [
            r'(\d+)\s*hour[s]?',
            r'(\d+)\s*minute[s]?',
            r'(\d+)\s*day[s]?'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, analysis.lower())
            if match:
                value = int(match.group(1))
                if 'hour' in pattern:
                    return value
                elif 'minute' in pattern:
                    return value / 60
                elif 'day' in pattern:
                    return value * 8  # 8 hours per day
        
        return None
    
    async def _extract_suggestions(self, analysis: str) -> List[str]:
        """Extract suggestions from analysis text."""
        # Simple extraction of suggestions
        suggestions = []
        
        lines = analysis.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(('•', '-', '*', '1.', '2.', '3.', '4.', '5.')):
                suggestion = line.lstrip('•-* 123456789.')
                if suggestion:
                    suggestions.append(suggestion)
        
        return suggestions
    
    async def _parse_suggestions(self, suggestions_text: str) -> List[Dict[str, Any]]:
        """Parse AI-generated suggestions."""
        suggestions = []
        
        # Simple parsing of suggestion format
        current_suggestion = {}
        
        for line in suggestions_text.split('\n'):
            line = line.strip()
            if line.startswith('Type:'):
                if current_suggestion:
                    suggestions.append(current_suggestion)
                current_suggestion = {"type": line.split(':', 1)[1].strip()}
            elif line.startswith('Title:'):
                current_suggestion["title"] = line.split(':', 1)[1].strip()
            elif line.startswith('Description:'):
                current_suggestion["description"] = line.split(':', 1)[1].strip()
            elif line.startswith('Priority:'):
                current_suggestion["priority"] = line.split(':', 1)[1].strip()
        
        if current_suggestion:
            suggestions.append(current_suggestion)
        
        return suggestions
    
    async def _analyze_schedule(
        self,
        events: List[Event],
        tasks: List[Task],
        date: datetime
    ) -> Dict[str, Any]:
        """Analyze schedule and provide optimization suggestions."""
        # Calculate schedule metrics
        total_event_time = sum(
            (event.end_time - event.start_time).total_seconds() / 3600
            for event in events
        )
        
        total_task_time = sum(
            task.estimated_hours or 2  # Default 2 hours per task
            for task in tasks
        )
        
        # Calculate optimization score
        working_hours = 8  # Standard working day
        utilization = (total_event_time + total_task_time) / working_hours
        
        optimization_score = max(0, min(1, 1 - abs(utilization - 0.8)))
        
        # Generate suggestions
        suggestions = []
        
        if utilization > 1.2:
            suggestions.append({
                "type": "overbooked",
                "message": "Your schedule is overbooked. Consider rescheduling some tasks.",
                "priority": "high"
            })
        elif utilization < 0.5:
            suggestions.append({
                "type": "underutilized",
                "message": "You have free time. Consider tackling pending tasks.",
                "priority": "medium"
            })
        
        # Check for conflicts
        events_sorted = sorted(events, key=lambda e: e.start_time)
        for i in range(len(events_sorted) - 1):
            if events_sorted[i].end_time > events_sorted[i + 1].start_time:
                suggestions.append({
                    "type": "conflict",
                    "message": f"Time conflict between '{events_sorted[i].title}' and '{events_sorted[i + 1].title}'",
                    "priority": "high"
                })
        
        return {
            "suggestions": suggestions,
            "optimization_score": optimization_score,
            "utilization": utilization,
            "total_event_time": total_event_time,
            "total_task_time": total_task_time
        }


# Global AI Assistant service instance
ai_assistant_service = AIAssistantService()
