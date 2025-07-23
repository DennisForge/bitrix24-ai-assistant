"""
AI Assistant Service - Enhanced Edition

This module provides advanced AI-powered assistance using OpenAI's GPT-4o model
with agentic workflows, Serbian language optimization, and smart scheduling capabilities.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from enum import Enum
import hashlib

import openai
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import redis.asyncio as redis

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
    SMART_SCHEDULING = "smart_scheduling"
    CONTEXT_AWARE_RESPONSE = "context_aware_response"


class AgenticWorkflowType(str, Enum):
    """Types of agentic workflows for GPT-4o."""
    PLANNING = "planning"
    EXECUTION = "execution"
    REFLECTION = "reflection"
    TOOL_USE = "tool_use"
    PERSISTENCE = "persistence"


class EnhancedAIAssistantService:
    """
    Enhanced AI Assistant Service with GPT-4o and Agentic Workflows.
    
    Features:
    - GPT-4o with 128k context window
    - Agentic workflow patterns (planning, persistence, tool use)
    - Serbian language optimization
    - Smart scheduling with predictive analytics
    - Context-aware responses
    - Real-time caching with Redis
    - Workload optimization algorithms
    """
    
    def __init__(self):
        """Initialize the Enhanced AI Assistant service."""
        self.client = None
        self.redis_client = None
        self.enabled = settings.AI_ENABLED
        
        if self.enabled and settings.OPENAI_API_KEY:
            self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.OPENAI_MODEL  # GPT-4o
            self.max_tokens = settings.OPENAI_MAX_TOKENS
            self.temperature = settings.OPENAI_TEMPERATURE
            self.context_window = settings.OPENAI_CONTEXT_WINDOW
            self.agentic_mode = settings.OPENAI_AGENTIC_MODE
            self.serbian_optimized = settings.OPENAI_SERBIAN_OPTIMIZED
        else:
            logger.warning("AI features disabled: missing OpenAI API key")
        
        # Initialize Redis for caching
        if settings.CACHE_ENABLED:
            try:
                self.redis_client = redis.from_url(settings.REDIS_URL)
                logger.info("Redis cache initialized for AI assistant")
            except Exception as e:
                logger.warning(f"Failed to initialize Redis cache: {e}")
                self.redis_client = None
    
    async def _get_cache_key(self, message: str, user_id: str, context: Optional[Dict] = None) -> str:
        """Generate cache key for AI responses."""
        cache_data = f"{message}:{user_id}:{json.dumps(context, sort_keys=True) if context else ''}"
        return f"ai_response:{hashlib.md5(cache_data.encode()).hexdigest()}"
    
    async def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached AI response."""
        if not self.redis_client:
            return None
        
        try:
            cached = await self.redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache retrieval error: {e}")
        
        return None
    
    async def _cache_response(self, cache_key: str, response: Dict[str, Any]) -> None:
        """Cache AI response."""
        if not self.redis_client:
            return
        
        try:
            await self.redis_client.setex(
                cache_key,
                settings.CACHE_TTL,
                json.dumps(response, default=str)
            )
        except Exception as e:
            logger.warning(f"Cache storage error: {e}")
    
    def _get_serbian_system_prompt(self, user_context: Dict[str, Any], context: Optional[Dict] = None) -> str:
        """
        Build Serbian-optimized system prompt for GPT-4o.
        
        This prompt is specifically designed for Serbian language processing
        with context awareness and agentic workflow patterns.
        """
        base_prompt = """Ti si napredni AI asistent za Bitrix24 CRM sistem, specijalizovan za srpski jezik.

TVOJA ULOGA:
- Pomažeš korisnicima da upravljaju kalendarom, zadacima i projektima
- Koristiš prirodni srpski jezik sa razumevanjem lokalnog konteksta
- Primenjuješ agentic workflow pattern: planiranje → izvršavanje → refleksija
- Daješ kontekstualne odgovore na osnovu korisničke istorije

MOGUĆNOSTI:
1. PAMETNO ZAKAZIVANJE: Analiziraj dostupnost tima i predloži optimalna vremena
2. UPRAVLJANJE ZADACIMA: Kreiraj, prioritizuj i kategoriši zadatke
3. PRODUKTIVNOST: Analiziraj radne navike i daj personalizovane savete
4. TIMSKA SARADNJA: Optimizuj raspored rada i balansiranje opterećenja

AGENTIC WORKFLOW:
- PLANIRANJE: Razloži složene zahteve na korake
- ALATI: Koristi dostupne funkcije za kreiranje zadataka/događaja
- PERZISTENTNOST: Nastavi rad dok se zadatak ne završi
- REFLEKSIJA: Proveri rezultate i predloži poboljšanja

KONTEKST KORISNIKA:"""
        
        if user_context:
            base_prompt += f"""
- Korisnik: {user_context.get('name', 'Nepoznat')}
- Uloga: {user_context.get('role', 'Korisnik')}
- Timezone: {user_context.get('timezone', 'UTC')}
- Radni sati: {user_context.get('working_hours', '09:00-17:00')}
- Aktivni projekti: {len(user_context.get('projects', []))}
- Nedavni zadaci: {len(user_context.get('recent_tasks', []))}"""
        
        if context and settings.AI_CONTEXT_AWARE:
            base_prompt += f"\n\nTRENUTNI KONTEKST:\n{json.dumps(context, indent=2, ensure_ascii=False)}"
        
        base_prompt += """

INSTRUKCIJE:
1. Odgovori UVEK na srpskom jeziku
2. Budi konkretan i akciono orijentisan
3. Koristi dostupne alate kada je potrebno
4. Predloži sledeće korake
5. Pitaj za pojašnjenja ako nešto nije jasno

Započni razgovor sa korisnim predlozima na osnovu konteksta."""
        
        return base_prompt
    
    def _get_enhanced_tools(self) -> List[Dict[str, Any]]:
        """
        Define enhanced tools for GPT-4o with Serbian language support.
        
        These tools are optimized for agentic workflows and include
        advanced scheduling and analytics capabilities.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "create_smart_task",
                    "description": "Kreiraj pametan zadatak sa AI analizom prioriteta i konteksta",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Naslov zadatka na srpskom"
                            },
                            "description": {
                                "type": "string",
                                "description": "Detaljan opis zadatka"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["nizak", "srednji", "visok", "hitan"],
                                "description": "Prioritet zadatka"
                            },
                            "estimated_duration": {
                                "type": "integer",
                                "description": "Procenjeno vreme izvršavanja u minutima"
                            },
                            "due_date": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Krajnji rok za zadatak"
                            },
                            "category": {
                                "type": "string",
                                "description": "Kategorija zadatka"
                            },
                            "dependencies": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "ID-jevi zadataka od kojih zavisi"
                            }
                        },
                        "required": ["title", "priority"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "schedule_smart_meeting",
                    "description": "Zakaži pametan sastanak sa AI optimizacijom vremena",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Naslov sastanka"
                            },
                            "description": {
                                "type": "string",
                                "description": "Opis i agenda sastanka"
                            },
                            "participants": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Lista učesnika (email adrese)"
                            },
                            "duration": {
                                "type": "integer",
                                "description": "Trajanje sastanka u minutima"
                            },
                            "preferred_time": {
                                "type": "string",
                                "format": "date-time",
                                "description": "Željeno vreme sastanka"
                            },
                            "meeting_type": {
                                "type": "string",
                                "enum": ["prezentacija", "brainstorming", "status_update", "decision_making"],
                                "description": "Tip sastanka"
                            },
                            "location": {
                                "type": "string",
                                "description": "Lokacija ili link za online sastanak"
                            }
                        },
                        "required": ["title", "participants", "duration"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_workload",
                    "description": "Analiziraj trenutno opterećenje tima i predloži optimizacije",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "team_members": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Lista članova tima za analizu"
                            },
                            "time_period": {
                                "type": "string",
                                "enum": ["nedelja", "mesec", "kvartal"],
                                "description": "Period za analizu"
                            },
                            "include_predictions": {
                                "type": "boolean",
                                "description": "Da li uključiti predviđanja buduće produktivnosti"
                            }
                        },
                        "required": ["team_members"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "optimize_schedule",
                    "description": "Optimizuj raspored za maksimalnu produktivnost",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "ID korisnika"
                            },
                            "optimization_goal": {
                                "type": "string",
                                "enum": ["produktivnost", "work_life_balance", "kreativnost", "fokus"],
                                "description": "Cilj optimizacije"
                            },
                            "constraints": {
                                "type": "object",
                                "properties": {
                                    "working_hours": {"type": "string"},
                                    "break_preferences": {"type": "string"},
                                    "meeting_limits": {"type": "integer"}
                                }
                            }
                        },
                        "required": ["user_id", "optimization_goal"]
                    }
                }
            }
        ]
    
    async def chat_with_assistant(
        self,
        message: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Enhanced chat with AI assistant using GPT-4o agentic workflows.
        
        Features:
        - Agentic workflow patterns (planning, execution, reflection)
        - Serbian language optimization
        - Context-aware responses
        - Redis caching for performance
        - Smart tool usage
        
        Args:
            message: User message in Serbian or English
            user_id: User ID for personalization
            context: Additional context (calendar events, tasks, etc.)
            
        Returns:
            Enhanced AI response with actions and insights
        """
        if not self.enabled or not self.client:
            return {
                "response": "AI asistent je trenutno onemogućen. Molimo omogućite ga u podešavanjima.",
                "suggestions": [],
                "actions": [],
                "workflow_type": "disabled"
            }
        
        try:
            # Check cache first
            cache_key = await self._get_cache_key(message, user_id, context)
            cached_response = await self._get_cached_response(cache_key)
            
            if cached_response and not settings.APP_DEBUG:
                logger.info(f"Returning cached response for user {user_id}")
                return cached_response
            
            # Get enhanced user context
            user_context = await self._get_enhanced_user_context(user_id)
            
            # Build Serbian-optimized system prompt
            system_prompt = self._get_serbian_system_prompt(user_context, context)
            
            # Prepare messages for agentic workflow
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
            
            # Add conversation history if available
            if context and "conversation_history" in context:
                for hist_msg in context["conversation_history"][-5:]:  # Last 5 messages
                    messages.append(hist_msg)
                messages.append({"role": "user", "content": message})
            
            # Enhanced GPT-4o request with agentic tools
            response = await self.client.chat.completions.create(
                model=self.model,  # GPT-4o
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                tools=self._get_enhanced_tools() if self.agentic_mode else None,
                tool_choice="auto" if self.agentic_mode else None,
                response_format={"type": "text"}
            )
            
            # Process agentic response
            result = await self._process_agentic_response(response, user_id, context)
            
            # Cache the response
            await self._cache_response(cache_key, result)
            
            # Log interaction for analytics
            await self._log_interaction(user_id, message, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in enhanced AI chat: {e}")
            return {
                "response": "Izvinjavam se, došlo je do greške. Molimo pokušajte ponovo.",
                "suggestions": [],
                "actions": [],
                "error": str(e) if settings.APP_DEBUG else None,
                "workflow_type": "error"
            }
    
    async def _get_enhanced_user_context(self, user_id: str) -> Dict[str, Any]:
        """
        Get enhanced user context with recent activity and preferences.
        """
        try:
            async with get_async_session() as db:
                # Get user info
                user_stmt = select(User).where(User.id == user_id)
                user_result = await db.execute(user_stmt)
                user = user_result.scalars().first()
                
                # Get recent tasks
                tasks_stmt = (
                    select(Task)
                    .where(Task.assigned_to == user_id)
                    .where(Task.created_at >= datetime.now() - timedelta(days=7))
                    .limit(10)
                )
                tasks_result = await db.execute(tasks_stmt)
                recent_tasks = tasks_result.scalars().all()
                
                # Get upcoming events
                events_stmt = (
                    select(Event)
                    .where(Event.user_id == user_id)
                    .where(Event.start_time >= datetime.now())
                    .where(Event.start_time <= datetime.now() + timedelta(days=7))
                    .limit(10)
                )
                events_result = await db.execute(events_stmt)
                upcoming_events = events_result.scalars().all()
                
                return {
                    "name": user.full_name if user else "Korisnik",
                    "email": user.email if user else "",
                    "role": user.role if user else "korisnik",
                    "timezone": user.timezone if user else "UTC",
                    "working_hours": "09:00-17:00",  # Can be made configurable
                    "recent_tasks": [
                        {
                            "id": task.id,
                            "title": task.title,
                            "priority": task.priority.value,
                            "status": task.status.value
                        } for task in recent_tasks
                    ],
                    "upcoming_events": [
                        {
                            "id": event.id,
                            "title": event.title,
                            "start_time": event.start_time.isoformat(),
                            "duration": event.duration
                        } for event in upcoming_events
                    ],
                    "projects": [],  # Can be expanded
                    "productivity_score": await self._calculate_productivity_score(user_id),
                    "preferred_language": "srpski"
                }
                
        except Exception as e:
            logger.error(f"Error getting user context: {e}")
            return {
                "name": "Korisnik",
                "role": "korisnik",
                "timezone": "UTC",
                "working_hours": "09:00-17:00",
                "recent_tasks": [],
                "upcoming_events": [],
                "projects": [],
                "productivity_score": 0.5,
                "preferred_language": "srpski"
            }
    
    async def _process_agentic_response(
        self,
        response: Any,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process GPT-4o response with agentic workflow patterns.
        
        This method handles tool calls, persistence, and reflection
        according to the agentic workflow paradigm.
        """
        result = {
            "response": "",
            "suggestions": [],
            "actions": [],
            "workflow_type": "standard",
            "tool_calls": [],
            "reflection": None,
            "next_steps": []
        }
        
        choice = response.choices[0]
        
        # Handle tool calls (agentic execution phase)
        if choice.message.tool_calls:
            result["workflow_type"] = "agentic_execution"
            result["tool_calls"] = []
            
            for tool_call in choice.message.tool_calls:
                tool_result = await self._execute_tool_call(tool_call, user_id, context)
                result["tool_calls"].append(tool_result)
                
                # Add tool results to actions
                if tool_result["success"]:
                    result["actions"].append({
                        "type": tool_call.function.name,
                        "data": tool_result["data"],
                        "message": tool_result["message"]
                    })
        
        # Get the main response
        result["response"] = choice.message.content or "Zadatak je uspešno izvršen."
        
        # Add intelligent suggestions based on context
        if settings.AI_CONTEXT_AWARE and context:
            suggestions = await self._generate_contextual_suggestions(user_id, context, result)
            result["suggestions"].extend(suggestions)
        
        # Agentic reflection phase
        if self.agentic_mode and result["tool_calls"]:
            reflection = await self._perform_reflection(result, user_id)
            result["reflection"] = reflection
            result["next_steps"] = reflection.get("next_steps", [])
        
        return result
    
    async def _execute_tool_call(
        self,
        tool_call: Any,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute tool calls with proper error handling and validation.
        """
        try:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            
            logger.info(f"Executing tool: {function_name} for user {user_id}")
            
            if function_name == "create_smart_task":
                return await self._create_smart_task(arguments, user_id)
            elif function_name == "schedule_smart_meeting":
                return await self._schedule_smart_meeting(arguments, user_id)
            elif function_name == "analyze_workload":
                return await self._analyze_workload(arguments, user_id)
            elif function_name == "optimize_schedule":
                return await self._optimize_schedule(arguments, user_id)
            else:
                return {
                    "success": False,
                    "message": f"Nepoznata funkcija: {function_name}",
                    "data": None
                }
                
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {
                "success": False,
                "message": f"Greška pri izvršavanju: {str(e)}",
                "data": None
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
ai_assistant_service = EnhancedAIAssistantService()
