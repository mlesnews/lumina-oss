#!/usr/bin/env python3
"""
API Chat Service
Handles chat conversations and messages

Integrates with database and Azure Service Bus.
"""

import sys
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("APIChatService")

try:
    from database_connection_manager import get_db_manager
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

try:
    from azure_service_bus_integration import (
        ServiceBusMessage,
        MessageType,
        get_service_bus_client,
        get_key_vault_client
    )
    SERVICE_BUS_AVAILABLE = True
except ImportError:
    SERVICE_BUS_AVAILABLE = False


class ChatService:
    """Handles chat operations"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent

        if DB_AVAILABLE:
            self.db_manager = get_db_manager(project_root)
        else:
            self.db_manager = None

        self.service_bus_client = None
        if SERVICE_BUS_AVAILABLE:
            try:
                kv_client = get_key_vault_client()
                self.service_bus_client = get_service_bus_client(
                    namespace="jarvis-lumina-bus.servicebus.windows.net",
                    key_vault_client=kv_client
                )
            except Exception as e:
                logger.warning(f"Service Bus not available: {e}")

    def create_conversation(self, user_id: str, title: Optional[str] = None) -> Dict[str, Any]:
        """Create a new conversation"""
        if not self.db_manager:
            raise RuntimeError("Database manager not available")

        conversation_id = str(uuid.uuid4())

        query = """
        INSERT INTO conversations (id, user_id, title, created_at, updated_at, last_message_at, message_count)
        VALUES (%s, %s, %s, NOW(), NOW(), NOW(), 0)
        RETURNING id, user_id, title, created_at, updated_at, message_count
        """

        try:
            results = self.db_manager.execute_query(query, (conversation_id, user_id, title))
            if results:
                conv = results[0]
                return {
                    "id": str(conv["id"]),
                    "user_id": str(conv["user_id"]),
                    "title": conv.get("title"),
                    "created_at": conv["created_at"].isoformat() if hasattr(conv["created_at"], 'isoformat') else str(conv["created_at"]),
                    "updated_at": conv["updated_at"].isoformat() if hasattr(conv["updated_at"], 'isoformat') else str(conv["updated_at"]),
                    "message_count": conv.get("message_count", 0)
                }
            raise Exception("Conversation creation failed")
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            raise

    def send_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send a chat message"""
        if not self.db_manager:
            raise RuntimeError("Database manager not available")

        message_id = str(uuid.uuid4())

        # Insert message
        query = """
        INSERT INTO chat_messages (id, conversation_id, role, content, metadata, timestamp)
        VALUES (%s, %s, %s, %s, %s, NOW())
        RETURNING id, conversation_id, role, content, timestamp, metadata
        """

        try:
            results = self.db_manager.execute_query(
                query,
                (message_id, conversation_id, role, content, json.dumps(metadata or {}))
            )

            if not results:
                raise Exception("Message creation failed")

            # Update conversation
            update_query = """
            UPDATE conversations
            SET updated_at = NOW(), last_message_at = NOW(), message_count = message_count + 1
            WHERE id = %s
            """
            self.db_manager.execute_update(update_query, (conversation_id,))

            message = results[0]

            # Publish to Service Bus
            if self.service_bus_client:
                sb_message = ServiceBusMessage(
                    message_id=message_id,
                    message_type=MessageType.RESPONSE,
                    timestamp=datetime.now(),
                    source="api-chat",
                    destination="chat-processor",
                    payload={
                        "conversation_id": conversation_id,
                        "message_id": message_id,
                        "role": role,
                        "content": content,
                        "metadata": metadata
                    }
                )
                self.service_bus_client.publish_to_topic("jarvis.responses", sb_message)

            return {
                "id": str(message["id"]),
                "conversation_id": str(message["conversation_id"]),
                "role": message["role"],
                "content": message["content"],
                "timestamp": message["timestamp"].isoformat() if hasattr(message["timestamp"], 'isoformat') else str(message["timestamp"]),
                "metadata": message.get("metadata")
            }
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise

    def get_messages(
        self,
        conversation_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get messages from a conversation"""
        if not self.db_manager:
            return {"messages": [], "total": 0, "limit": limit, "offset": offset}

        # Get total count
        count_query = "SELECT COUNT(*) as total FROM chat_messages WHERE conversation_id = %s"
        count_results = self.db_manager.execute_query(count_query, (conversation_id,))
        total = count_results[0]['total'] if count_results else 0

        # Get messages
        query = """
        SELECT id, conversation_id, role, content, timestamp, metadata, parent_message_id
        FROM chat_messages
        WHERE conversation_id = %s
        ORDER BY timestamp ASC
        LIMIT %s OFFSET %s
        """

        try:
            results = self.db_manager.execute_query(query, (conversation_id, limit, offset))
            messages = [
                {
                    "id": str(m["id"]),
                    "conversation_id": str(m["conversation_id"]),
                    "role": m["role"],
                    "content": m["content"],
                    "timestamp": m["timestamp"].isoformat() if hasattr(m["timestamp"], 'isoformat') else str(m["timestamp"]),
                    "metadata": m.get("metadata"),
                    "parent_message_id": str(m["parent_message_id"]) if m.get("parent_message_id") else None
                }
                for m in results
            ]

            return {
                "messages": messages,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return {"messages": [], "total": 0, "limit": limit, "offset": offset}

    def list_conversations(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        is_archived: bool = False
    ) -> Dict[str, Any]:
        """List conversations for a user"""
        if not self.db_manager:
            return {"conversations": [], "total": 0, "limit": limit, "offset": offset}

        # Get total count
        count_query = "SELECT COUNT(*) as total FROM conversations WHERE user_id = %s AND is_archived = %s"
        count_results = self.db_manager.execute_query(count_query, (user_id, is_archived))
        total = count_results[0]['total'] if count_results else 0

        # Get conversations
        query = """
        SELECT id, user_id, title, created_at, updated_at, last_message_at, message_count
        FROM conversations
        WHERE user_id = %s AND is_archived = %s
        ORDER BY last_message_at DESC NULLS LAST, updated_at DESC
        LIMIT %s OFFSET %s
        """

        try:
            results = self.db_manager.execute_query(query, (user_id, is_archived, limit, offset))
            conversations = [
                {
                    "id": str(c["id"]),
                    "user_id": str(c["user_id"]),
                    "title": c.get("title"),
                    "created_at": c["created_at"].isoformat() if hasattr(c["created_at"], 'isoformat') else str(c["created_at"]),
                    "updated_at": c["updated_at"].isoformat() if hasattr(c["updated_at"], 'isoformat') else str(c["updated_at"]),
                    "last_message_at": c["last_message_at"].isoformat() if c.get("last_message_at") and hasattr(c["last_message_at"], 'isoformat') else (str(c["last_message_at"]) if c.get("last_message_at") else None),
                    "message_count": c.get("message_count", 0)
                }
                for c in results
            ]

            return {
                "conversations": conversations,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            logger.error(f"Error listing conversations: {e}")
            return {"conversations": [], "total": 0, "limit": limit, "offset": offset}


def get_chat_service(project_root: Optional[Path] = None) -> ChatService:
    """Get global chat service"""
    return ChatService(project_root)
