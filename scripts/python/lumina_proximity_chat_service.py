#!/usr/bin/env python3
"""
Lumina Proximity Chat Service - Architectural Integration

A programmatic, service-oriented proximity chat system integrated into the Lumina ecosystem.
Provides local network awareness, chat bubbles, and architectural integration with existing
Lumina services.

Architectural Focus:
- Service-oriented architecture
- Programmatic API for ecosystem integration
- Proximity-based local network communication
- Chat bubble visualization
- Integration with Jarvis, workflows, and Lumina services

Tags: #LUMINA-ARCHITECTURE #PROXIMITY-CHAT #SERVICE-ORIENTED #ECOSYSTEM @LUMINA
"""

import sys
import json
import socket
import threading
import time
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LuminaProximityChat")


class ProximityLevel(Enum):
    """Proximity levels for local network awareness"""
    IMMEDIATE = "immediate"  # Same subnet, very close
    LOCAL = "local"  # Same network segment
    NEARBY = "nearby"  # Reachable on network
    DISTANT = "distant"  # Network reachable but far


class MessageScope(Enum):
    """Message scope/range"""
    IMMEDIATE = "immediate"  # Only immediate proximity
    LOCAL = "local"  # Local network segment
    NETWORK = "network"  # Full network
    PRIVATE = "private"  # Direct message


@dataclass
class ChatBubble:
    """Chat bubble representation for UI"""
    message_id: str
    user_id: str
    username: str
    content: str
    timestamp: datetime
    position: Optional[Tuple[int, int]] = None  # Screen position for bubble
    duration: float = 5.0  # How long bubble stays visible
    style: Dict[str, Any] = None  # Visual styling

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "user_id": self.user_id,
            "username": self.username,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "position": self.position,
            "duration": self.duration,
            "style": self.style or {}
        }


@dataclass
class ProximityMessage:
    """Proximity-aware message"""
    message_id: str
    sender_id: str
    sender_name: str
    content: str
    scope: MessageScope
    proximity: ProximityLevel
    timestamp: datetime
    metadata: Dict[str, Any] = None
    bubble: Optional[ChatBubble] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "sender_name": self.sender_name,
            "content": self.content,
            "scope": self.scope.value,
            "proximity": self.proximity.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata or {},
            "bubble": self.bubble.to_dict() if self.bubble else None
        }


class LuminaProximityChatService:
    """
    Lumina Proximity Chat Service

    Architectural integration point for proximity-based chat in the Lumina ecosystem.
    Provides programmatic API for services to send/receive proximity-aware messages.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = logger

        # Service state
        self.service_id = f"proximity_chat_{uuid.uuid4().hex[:8]}"
        self.running = False

        # Network awareness
        self.local_network = self._detect_local_network()
        self.proximity_map: Dict[str, ProximityLevel] = {}

        # Message handlers
        self.message_handlers: List[Callable[[ProximityMessage], None]] = []
        self.bubble_handlers: List[Callable[[ChatBubble], None]] = []

        # Integration points
        self.jarvis_integration = None
        self.workflow_integration = None

        # Data directory
        self.data_dir = self.project_root / "data" / "proximity_chat"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Message history
        self.message_history: List[ProximityMessage] = []
        self.max_history = 1000

        self.logger.info(f"✅ Lumina Proximity Chat Service initialized: {self.service_id}")
        self.logger.info(f"   Local network: {self.local_network}")

    def _detect_local_network(self) -> str:
        """Detect local network segment"""
        try:
            import socket
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            # Extract network segment (e.g., 192.168.1.x -> 192.168.1)
            network_segment = '.'.join(local_ip.split('.')[:-1])
            return network_segment
        except Exception as e:
            self.logger.warning(f"Could not detect local network: {e}")
            return "unknown"

    def calculate_proximity(self, target_ip: str) -> ProximityLevel:
        """Calculate proximity level to target"""
        try:
            # Extract network segments
            local_segment = self.local_network
            target_segment = '.'.join(target_ip.split('.')[:-1])

            if target_segment == local_segment:
                return ProximityLevel.IMMEDIATE
            elif target_segment.startswith(local_segment.split('.')[0]):
                return ProximityLevel.LOCAL
            else:
                return ProximityLevel.NEARBY
        except:
            return ProximityLevel.DISTANT

    def register_message_handler(self, handler: Callable[[ProximityMessage], None]):
        """Register handler for incoming messages"""
        self.message_handlers.append(handler)
        self.logger.info(f"Registered message handler: {handler.__name__}")

    def register_bubble_handler(self, handler: Callable[[ChatBubble], None]):
        """Register handler for chat bubble display"""
        self.bubble_handlers.append(handler)
        self.logger.info(f"Registered bubble handler: {handler.__name__}")

    def send_message(self, content: str, scope: MessageScope = MessageScope.LOCAL,
                    target_id: Optional[str] = None, metadata: Optional[Dict] = None) -> ProximityMessage:
        """
        Send proximity-aware message

        Args:
            content: Message content
            scope: Message scope (IMMEDIATE, LOCAL, NETWORK, PRIVATE)
            target_id: Target user/service ID (for PRIVATE scope)
            metadata: Additional metadata

        Returns:
            Created ProximityMessage
        """
        message = ProximityMessage(
            message_id=str(uuid.uuid4()),
            sender_id=self.service_id,
            sender_name="Lumina Service",
            content=content,
            scope=scope,
            proximity=ProximityLevel.LOCAL,  # Default, can be calculated
            timestamp=datetime.now(),
            metadata=metadata or {}
        )

        # Create chat bubble
        message.bubble = ChatBubble(
            message_id=message.message_id,
            user_id=message.sender_id,
            username=message.sender_name,
            content=message.content,
            timestamp=message.timestamp,
            duration=5.0,
            style={"color": "#00D9FF", "font_size": 14}
        )

        # Add to history
        self.message_history.append(message)
        if len(self.message_history) > self.max_history:
            self.message_history.pop(0)

        # Notify handlers
        for handler in self.message_handlers:
            try:
                handler(message)
            except Exception as e:
                self.logger.error(f"Error in message handler {handler.__name__}: {e}")

        # Notify bubble handlers
        if message.bubble:
            for handler in self.bubble_handlers:
                try:
                    handler(message.bubble)
                except Exception as e:
                    self.logger.error(f"Error in bubble handler {handler.__name__}: {e}")

        # Save to history
        self._save_message(message)

        self.logger.info(f"📤 Sent message: {content[:50]}... (scope: {scope.value})")
        return message

    def receive_message(self, message: ProximityMessage):
        """Receive and process incoming message"""
        # Check if message is in scope
        if not self._is_message_in_scope(message):
            return

        # Add to history
        self.message_history.append(message)
        if len(self.message_history) > self.max_history:
            self.message_history.pop(0)

        # Notify handlers
        for handler in self.message_handlers:
            try:
                handler(message)
            except Exception as e:
                self.logger.error(f"Error in message handler: {e}")

        # Display bubble if available
        if message.bubble:
            for handler in self.bubble_handlers:
                try:
                    handler(message.bubble)
                except Exception as e:
                    self.logger.error(f"Error in bubble handler: {e}")

        self.logger.info(f"📥 Received message from {message.sender_name}: {message.content[:50]}...")

    def _is_message_in_scope(self, message: ProximityMessage) -> bool:
        """Check if message is within scope"""
        if message.scope == MessageScope.PRIVATE:
            # Private messages need explicit target matching
            return message.metadata.get("target_id") == self.service_id

        if message.scope == MessageScope.IMMEDIATE:
            return message.proximity == ProximityLevel.IMMEDIATE

        if message.scope == MessageScope.LOCAL:
            return message.proximity in [ProximityLevel.IMMEDIATE, ProximityLevel.LOCAL]

        # NETWORK scope - always in scope
        return True

    def _save_message(self, message: ProximityMessage):
        """Save message to history file"""
        try:
            history_file = self.data_dir / "message_history.jsonl"
            with open(history_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(message.to_dict()) + '\n')
        except Exception as e:
            self.logger.error(f"Error saving message: {e}")

    def get_recent_messages(self, limit: int = 50, scope: Optional[MessageScope] = None) -> List[ProximityMessage]:
        """Get recent messages, optionally filtered by scope"""
        messages = self.message_history[-limit:]
        if scope:
            messages = [m for m in messages if m.scope == scope]
        return messages

    def integrate_with_jarvis(self, jarvis_service):
        """Integrate with Jarvis service"""
        self.jarvis_integration = jarvis_service

        # Register Jarvis message handler
        def jarvis_message_handler(message: ProximityMessage):
            # Jarvis can process proximity messages
            if self.jarvis_integration:
                # Forward to Jarvis for processing
                logger.info(f"Jarvis processing proximity message: {message.content[:50]}")

        self.register_message_handler(jarvis_message_handler)
        self.logger.info("✅ Integrated with Jarvis service")

    def integrate_with_workflows(self, workflow_service):
        """Integrate with workflow service"""
        self.workflow_integration = workflow_service

        def workflow_message_handler(message: ProximityMessage):
            # Workflows can react to proximity messages
            if self.workflow_integration:
                logger.info(f"Workflow processing proximity message: {message.content[:50]}")

        self.register_message_handler(workflow_message_handler)
        self.logger.info("✅ Integrated with workflow service")

    def get_service_info(self) -> Dict[str, Any]:
        """Get service information for ecosystem discovery"""
        return {
            "service_id": self.service_id,
            "service_type": "proximity_chat",
            "local_network": self.local_network,
            "message_count": len(self.message_history),
            "handlers": {
                "message_handlers": len(self.message_handlers),
                "bubble_handlers": len(self.bubble_handlers)
            },
            "integrations": {
                "jarvis": self.jarvis_integration is not None,
                "workflows": self.workflow_integration is not None
            }
        }


# Global service instance for ecosystem integration
_proximity_chat_service: Optional[LuminaProximityChatService] = None


def get_proximity_chat_service(project_root: Optional[Path] = None) -> LuminaProximityChatService:
    """Get or create global proximity chat service instance"""
    global _proximity_chat_service
    if _proximity_chat_service is None:
        _proximity_chat_service = LuminaProximityChatService(project_root)
    return _proximity_chat_service


def main():
    try:
        """Example usage"""
        service = get_proximity_chat_service()

        # Register bubble handler
        def display_bubble(bubble: ChatBubble):
            print(f"💬 [{bubble.username}]: {bubble.content}")

        service.register_bubble_handler(display_bubble)

        # Send test message
        service.send_message("Hello from Lumina proximity chat service!", scope=MessageScope.LOCAL)

        print(f"\n✅ Service running: {service.service_id}")
        print(f"   Network: {service.local_network}")
        print(f"   Info: {json.dumps(service.get_service_info(), indent=2)}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()