"""
WebSocket Service for Real-time Collaboration

This module provides WebSocket functionality for real-time calendar updates,
team collaboration, and instant notifications.
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Set, Optional, Any
from enum import Enum

from fastapi import WebSocket, WebSocketDisconnect
import redis.asyncio as redis

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class MessageType(str, Enum):
    """WebSocket message types."""
    CALENDAR_UPDATE = "calendar_update"
    TASK_UPDATE = "task_update"
    TEAM_NOTIFICATION = "team_notification"
    USER_STATUS = "user_status"
    MEETING_REMINDER = "meeting_reminder"
    AI_SUGGESTION = "ai_suggestion"
    SYSTEM_MESSAGE = "system_message"
    HEARTBEAT = "heartbeat"


class UserStatus(str, Enum):
    """User online status."""
    ONLINE = "online"
    AWAY = "away"
    BUSY = "busy"
    OFFLINE = "offline"


class WebSocketManager:
    """
    WebSocket connection manager for real-time features.
    
    Features:
    - Connection management per user
    - Room-based broadcasting (teams, projects)
    - Message queuing with Redis
    - Automatic reconnection handling
    - Heartbeat monitoring
    """
    
    def __init__(self):
        # Active connections: {user_id: {connection_id: websocket}}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        
        # User rooms: {user_id: [room_ids]}
        self.user_rooms: Dict[str, Set[str]] = {}
        
        # Room members: {room_id: {user_ids}}
        self.room_members: Dict[str, Set[str]] = {}
        
        # User status tracking
        self.user_status: Dict[str, UserStatus] = {}
        
        # Redis for message persistence
        self.redis_client = None
        
        if settings.WEBSOCKET_ENABLED and settings.REDIS_URL:
            try:
                self.redis_client = redis.from_url(settings.REDIS_URL)
                logger.info("WebSocket Redis client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize WebSocket Redis: {e}")
    
    async def connect(self, websocket: WebSocket, user_id: str, connection_id: str = None) -> str:
        """
        Accept WebSocket connection and register user.
        
        Args:
            websocket: WebSocket connection
            user_id: User identifier
            connection_id: Optional connection identifier
            
        Returns:
            Connection ID for this session
        """
        await websocket.accept()
        
        # Generate connection ID if not provided
        if not connection_id:
            connection_id = f"{user_id}_{datetime.now().timestamp()}"
        
        # Add to active connections
        if user_id not in self.active_connections:
            self.active_connections[user_id] = {}
        
        self.active_connections[user_id][connection_id] = websocket
        
        # Set user status to online
        self.user_status[user_id] = UserStatus.ONLINE
        
        # Join default user room
        await self.join_room(user_id, f"user_{user_id}")
        
        # Notify about user coming online
        await self.broadcast_user_status(user_id, UserStatus.ONLINE)
        
        logger.info(f"WebSocket connected: user={user_id}, connection={connection_id}")
        
        # Send welcome message
        await self.send_personal_message(user_id, {
            "type": MessageType.SYSTEM_MESSAGE,
            "message": "Uspešno povezano. Real-time funkcionalnosti su aktivne.",
            "timestamp": datetime.now().isoformat()
        })
        
        return connection_id
    
    async def disconnect(self, user_id: str, connection_id: str):
        """
        Handle WebSocket disconnection.
        
        Args:
            user_id: User identifier
            connection_id: Connection identifier
        """
        # Remove from active connections
        if user_id in self.active_connections:
            if connection_id in self.active_connections[user_id]:
                del self.active_connections[user_id][connection_id]
            
            # If no more connections, mark as offline
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                self.user_status[user_id] = UserStatus.OFFLINE
                
                # Leave all rooms
                if user_id in self.user_rooms:
                    for room_id in list(self.user_rooms[user_id]):
                        await self.leave_room(user_id, room_id)
                
                # Notify about user going offline
                await self.broadcast_user_status(user_id, UserStatus.OFFLINE)
        
        logger.info(f"WebSocket disconnected: user={user_id}, connection={connection_id}")
    
    async def join_room(self, user_id: str, room_id: str):
        """
        Add user to a room for group messaging.
        
        Args:
            user_id: User identifier
            room_id: Room identifier (e.g., 'team_123', 'project_456')
        """
        # Add user to room
        if room_id not in self.room_members:
            self.room_members[room_id] = set()
        
        self.room_members[room_id].add(user_id)
        
        # Add room to user's rooms
        if user_id not in self.user_rooms:
            self.user_rooms[user_id] = set()
        
        self.user_rooms[user_id].add(room_id)
        
        logger.debug(f"User {user_id} joined room {room_id}")
    
    async def leave_room(self, user_id: str, room_id: str):
        """
        Remove user from a room.
        
        Args:
            user_id: User identifier
            room_id: Room identifier
        """
        # Remove user from room
        if room_id in self.room_members:
            self.room_members[room_id].discard(user_id)
            
            # Clean up empty room
            if not self.room_members[room_id]:
                del self.room_members[room_id]
        
        # Remove room from user's rooms
        if user_id in self.user_rooms:
            self.user_rooms[user_id].discard(room_id)
        
        logger.debug(f"User {user_id} left room {room_id}")
    
    async def send_personal_message(self, user_id: str, message: Dict[str, Any]):
        """
        Send message to specific user across all their connections.
        
        Args:
            user_id: Target user identifier
            message: Message data
        """
        if user_id in self.active_connections:
            # Add timestamp if not present
            if "timestamp" not in message:
                message["timestamp"] = datetime.now().isoformat()
            
            message_json = json.dumps(message, ensure_ascii=False)
            
            # Send to all user's connections
            disconnected_connections = []
            
            for connection_id, websocket in self.active_connections[user_id].items():
                try:
                    await websocket.send_text(message_json)
                except Exception as e:
                    logger.warning(f"Failed to send message to {user_id}:{connection_id}: {e}")
                    disconnected_connections.append(connection_id)
            
            # Clean up disconnected connections
            for connection_id in disconnected_connections:
                await self.disconnect(user_id, connection_id)
    
    async def broadcast_to_room(self, room_id: str, message: Dict[str, Any], exclude_user: str = None):
        """
        Broadcast message to all users in a room.
        
        Args:
            room_id: Room identifier
            message: Message data
            exclude_user: Optional user ID to exclude from broadcast
        """
        if room_id in self.room_members:
            for user_id in self.room_members[room_id]:
                if exclude_user and user_id == exclude_user:
                    continue
                
                await self.send_personal_message(user_id, message)
    
    async def broadcast_calendar_update(
        self,
        event_data: Dict[str, Any],
        affected_users: List[str],
        update_type: str = "update"
    ):
        """
        Broadcast calendar event updates to affected users.
        
        Args:
            event_data: Calendar event data
            affected_users: List of user IDs to notify
            update_type: Type of update (create, update, delete)
        """
        message = {
            "type": MessageType.CALENDAR_UPDATE,
            "update_type": update_type,
            "event": event_data,
            "timestamp": datetime.now().isoformat()
        }
        
        for user_id in affected_users:
            await self.send_personal_message(user_id, message)
        
        # Store in Redis for offline users
        if self.redis_client:
            try:
                for user_id in affected_users:
                    queue_key = f"offline_messages:{user_id}"
                    await self.redis_client.lpush(queue_key, json.dumps(message))
                    await self.redis_client.expire(queue_key, 86400)  # 24 hours
            except Exception as e:
                logger.warning(f"Failed to queue offline messages: {e}")
    
    async def broadcast_task_update(
        self,
        task_data: Dict[str, Any],
        affected_users: List[str],
        update_type: str = "update"
    ):
        """
        Broadcast task updates to affected users.
        
        Args:
            task_data: Task data
            affected_users: List of user IDs to notify
            update_type: Type of update (create, update, delete, assign)
        """
        message = {
            "type": MessageType.TASK_UPDATE,
            "update_type": update_type,
            "task": task_data,
            "timestamp": datetime.now().isoformat()
        }
        
        for user_id in affected_users:
            await self.send_personal_message(user_id, message)
    
    async def send_ai_suggestion(self, user_id: str, suggestion: Dict[str, Any]):
        """
        Send AI-generated suggestion to user.
        
        Args:
            user_id: Target user ID
            suggestion: AI suggestion data
        """
        message = {
            "type": MessageType.AI_SUGGESTION,
            "suggestion": suggestion,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.send_personal_message(user_id, message)
    
    async def broadcast_user_status(self, user_id: str, status: UserStatus):
        """
        Broadcast user status change to relevant users.
        
        Args:
            user_id: User whose status changed
            status: New status
        """
        message = {
            "type": MessageType.USER_STATUS,
            "user_id": user_id,
            "status": status.value,
            "timestamp": datetime.now().isoformat()
        }
        
        # Broadcast to all rooms the user is in
        if user_id in self.user_rooms:
            for room_id in self.user_rooms[user_id]:
                await self.broadcast_to_room(room_id, message, exclude_user=user_id)
    
    async def send_meeting_reminder(
        self,
        user_ids: List[str],
        meeting_data: Dict[str, Any],
        minutes_before: int
    ):
        """
        Send meeting reminder to participants.
        
        Args:
            user_ids: List of participant user IDs
            meeting_data: Meeting information
            minutes_before: Minutes before meeting starts
        """
        message = {
            "type": MessageType.MEETING_REMINDER,
            "meeting": meeting_data,
            "minutes_before": minutes_before,
            "timestamp": datetime.now().isoformat()
        }
        
        for user_id in user_ids:
            await self.send_personal_message(user_id, message)
    
    async def get_online_users(self, room_id: str = None) -> List[str]:
        """
        Get list of online users, optionally filtered by room.
        
        Args:
            room_id: Optional room ID to filter by
            
        Returns:
            List of online user IDs
        """
        if room_id:
            # Get online users in specific room
            if room_id in self.room_members:
                return [
                    user_id for user_id in self.room_members[room_id]
                    if user_id in self.active_connections
                ]
            return []
        else:
            # Get all online users
            return list(self.active_connections.keys())
    
    async def get_offline_messages(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve queued messages for user who was offline.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of queued messages
        """
        if not self.redis_client:
            return []
        
        try:
            queue_key = f"offline_messages:{user_id}"
            messages = await self.redis_client.lrange(queue_key, 0, -1)
            
            # Clear the queue
            await self.redis_client.delete(queue_key)
            
            return [json.loads(msg) for msg in messages]
        
        except Exception as e:
            logger.error(f"Failed to retrieve offline messages: {e}")
            return []
    
    async def start_heartbeat_monitor(self):
        """
        Start heartbeat monitoring for connection health.
        """
        async def heartbeat_loop():
            while True:
                try:
                    await asyncio.sleep(settings.WEBSOCKET_HEARTBEAT)
                    
                    # Send heartbeat to all connections
                    heartbeat_message = {
                        "type": MessageType.HEARTBEAT,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    for user_id in list(self.active_connections.keys()):
                        await self.send_personal_message(user_id, heartbeat_message)
                
                except Exception as e:
                    logger.error(f"Heartbeat monitor error: {e}")
        
        if settings.WEBSOCKET_ENABLED:
            asyncio.create_task(heartbeat_loop())
            logger.info("WebSocket heartbeat monitor started")


# Global WebSocket manager instance
websocket_manager = WebSocketManager()