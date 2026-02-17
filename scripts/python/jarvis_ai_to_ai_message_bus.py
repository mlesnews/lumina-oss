#!/usr/bin/env python3
"""
JARVIS AI-to-AI Message Bus

Central message bus for bidirectional (<=>) communication between ALL AI systems.
Handles routing, queuing, and delivery of messages between AI services.

Tags: #JARVIS #AI_TO_AI #MESSAGE_BUS #BIDIRECTIONAL #SIDER #ROAMWISE @JARVIS @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
from queue import Queue
import threading

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

logger = get_logger("JARVISAIToAIMessageBus")


@dataclass
class AIToAIMessage:
    """AI-to-AI message"""
    message_id: str
    from_service: str
    to_service: str
    message_type: str  # query, command, response, notification
    payload: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "pending"  # pending, delivered, failed
    response: Optional[Dict[str, Any]] = None


class JARVISAIToAIMessageBus:
    """
    JARVIS AI-to-AI Message Bus

    Central message bus for bidirectional (<=>) communication between ALL AI systems.
    Handles routing, queuing, and delivery.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize message bus"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "ai_to_ai_messages"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Message queues (one per service)
        self.message_queues: Dict[str, Queue] = {}

        # Message history
        self.message_history: List[AIToAIMessage] = []

        # Integration reference
        self.integration = None

        logger.info("✅ JARVIS AI-to-AI Message Bus initialized")
        logger.info("   🔄 Bidirectional (<=>) message routing")

    def initialize_integration(self):
        """Initialize AI-to-AI integration"""
        try:
            from ai_to_ai_bidirectional_integration import AIToAIBidirectionalIntegration
            self.integration = AIToAIBidirectionalIntegration(self.project_root)
            self.integration.discover_all_ai_services()
            self.integration.create_bidirectional_integration()

            # Initialize queues for each service
            for service_name in self.integration.ai_services.keys():
                self.message_queues[service_name] = Queue()

            logger.info(f"   ✅ Initialized queues for {len(self.message_queues)} services")
        except Exception as e:
            logger.error(f"   ❌ Error initializing integration: {e}")

    def send_message(self, from_service: str, to_service: str, message_type: str, payload: Dict[str, Any]) -> str:
        """
        Send message from one AI service to another

        Returns:
            Message ID
        """
        if not self.integration:
            self.initialize_integration()

        message_id = f"{from_service}_{to_service}_{int(time.time() * 1000)}"

        message = AIToAIMessage(
            message_id=message_id,
            from_service=from_service,
            to_service=to_service,
            message_type=message_type,
            payload=payload
        )

        # Add to queue
        if to_service in self.message_queues:
            self.message_queues[to_service].put(message)
        else:
            logger.warning(f"   ⚠️  Service {to_service} not found, creating queue")
            self.message_queues[to_service] = Queue()
            self.message_queues[to_service].put(message)

        # Send via integration
        result = self.integration.send_ai_to_ai_message(from_service, to_service, payload)

        message.status = "delivered" if "error" not in result else "failed"
        message.response = result

        # Save to history
        self.message_history.append(message)
        self._save_message(message)

        logger.info(f"   📤 Message {message_id}: {from_service} <=> {to_service}")

        return message_id

    def broadcast_message(self, from_service: str, message_type: str, payload: Dict[str, Any]) -> List[str]:
        """Broadcast message from one service to all other services"""
        if not self.integration:
            self.initialize_integration()

        message_ids = []
        for service_name in self.integration.ai_services.keys():
            if service_name != from_service:
                message_id = self.send_message(from_service, service_name, message_type, payload)
                message_ids.append(message_id)

        logger.info(f"   📢 Broadcast from {from_service} to {len(message_ids)} services")
        return message_ids

    def get_messages_for_service(self, service_name: str, limit: int = 10) -> List[AIToAIMessage]:
        """Get messages for a specific service"""
        service_messages = [
            msg for msg in self.message_history
            if msg.to_service == service_name or msg.from_service == service_name
        ]
        return sorted(service_messages, key=lambda x: x.timestamp, reverse=True)[:limit]

    def _save_message(self, message: AIToAIMessage):
        try:
            """Save message to disk"""
            message_file = self.data_dir / f"{message.message_id}.json"
            with open(message_file, 'w') as f:
                json.dump({
                    "message_id": message.message_id,
                    "from_service": message.from_service,
                    "to_service": message.to_service,
                    "message_type": message.message_type,
                    "payload": message.payload,
                    "timestamp": message.timestamp,
                    "status": message.status,
                    "response": message.response
                }, f, indent=2, default=str)

        except Exception as e:
            self.logger.error(f"Error in _save_message: {e}", exc_info=True)
            raise
    def get_message_bus_status(self) -> Dict[str, Any]:
        """Get message bus status"""
        return {
            "total_services": len(self.message_queues),
            "total_messages": len(self.message_history),
            "pending_messages": sum(q.qsize() for q in self.message_queues.values()),
            "services": list(self.message_queues.keys()),
            "recent_messages": [
                {
                    "id": msg.message_id,
                    "from": msg.from_service,
                    "to": msg.to_service,
                    "type": msg.message_type,
                    "status": msg.status,
                    "timestamp": msg.timestamp
                }
                for msg in sorted(self.message_history, key=lambda x: x.timestamp, reverse=True)[:10]
            ]
        }


def main():
    """Test message bus"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS AI-to-AI Message Bus")
    parser.add_argument("--send", nargs=4, metavar=("FROM", "TO", "TYPE", "PAYLOAD"),
                       help="Send message (payload as JSON string)")
    parser.add_argument("--broadcast", nargs=3, metavar=("FROM", "TYPE", "PAYLOAD"),
                       help="Broadcast message")
    parser.add_argument("--status", action="store_true", help="Show message bus status")

    args = parser.parse_args()

    bus = JARVISAIToAIMessageBus()

    if args.send:
        from_service, to_service, message_type, payload_json = args.send
        try:
            payload = json.loads(payload_json)
        except:
            payload = {"query": payload_json}

        message_id = bus.send_message(from_service, to_service, message_type, payload)
        print(f"✅ Message sent: {message_id}")

    elif args.broadcast:
        from_service, message_type, payload_json = args.broadcast
        try:
            payload = json.loads(payload_json)
        except:
            payload = {"query": payload_json}

        message_ids = bus.broadcast_message(from_service, message_type, payload)
        print(f"✅ Broadcast sent: {len(message_ids)} messages")

    elif args.status:
        bus.initialize_integration()
        status = bus.get_message_bus_status()
        print(json.dumps(status, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":


    main()