#!/usr/bin/env python3
"""
Lumina Proximity Chat Integration Example

Demonstrates how to integrate proximity chat into Lumina services programmatically.
Shows architectural integration patterns for ecosystem services.

Tags: #INTEGRATION-EXAMPLE #LUMINA-ARCHITECTURE #ECOSYSTEM @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, Any

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_proximity_chat_service import (
    get_proximity_chat_service,
    MessageScope,
    ProximityMessage
)
from lumina_chat_bubble_renderer import LuminaChatBubbleManager


def example_jarvis_integration():
    """Example: Integrate with Jarvis service"""
    print("=" * 80)
    print("Example: Jarvis Integration")
    print("=" * 80)

    # Get proximity chat service
    chat_service = get_proximity_chat_service()

    # Register handler for Jarvis to process messages
    def jarvis_message_handler(message: ProximityMessage):
        print(f"🤖 Jarvis received: {message.content}")
        # Jarvis can respond, process, or forward messages
        if "help" in message.content.lower():
            chat_service.send_message(
                "Jarvis here! How can I assist?",
                scope=MessageScope.LOCAL,
                metadata={"source": "jarvis", "response_to": message.message_id}
            )

    chat_service.register_message_handler(jarvis_message_handler)

    # Send test message
    chat_service.send_message("Hello Jarvis, I need help", scope=MessageScope.LOCAL)

    print("✅ Jarvis integration example complete\n")


def example_workflow_integration():
    """Example: Integrate with workflow service"""
    print("=" * 80)
    print("Example: Workflow Integration")
    print("=" * 80)

    chat_service = get_proximity_chat_service()

    def workflow_message_handler(message: ProximityMessage):
        print(f"⚙️  Workflow processing: {message.content}")
        # Workflows can trigger based on proximity messages
        if "deploy" in message.content.lower():
            print("   → Triggering deployment workflow...")
            chat_service.send_message(
                "Deployment workflow triggered",
                scope=MessageScope.LOCAL,
                metadata={"workflow": "deploy", "triggered_by": message.sender_id}
            )

    chat_service.register_message_handler(workflow_message_handler)

    # Send test message
    chat_service.send_message("Please deploy the latest version", scope=MessageScope.LOCAL)

    print("✅ Workflow integration example complete\n")


def example_bubble_display():
    """Example: Display chat bubbles"""
    print("=" * 80)
    print("Example: Chat Bubble Display")
    print("=" * 80)

    # Create bubble manager
    bubble_manager = LuminaChatBubbleManager()

    # Send messages that will display as bubbles
    chat_service = get_proximity_chat_service()

    chat_service.send_message(
        "System status: All services operational",
        scope=MessageScope.LOCAL,
        metadata={"type": "status", "show_bubble": True}
    )

    chat_service.send_message(
        "New workflow completed successfully",
        scope=MessageScope.LOCAL,
        metadata={"type": "notification", "show_bubble": True}
    )

    print("✅ Bubble display example complete\n")


def example_programmatic_api():
    """Example: Programmatic API usage"""
    print("=" * 80)
    print("Example: Programmatic API")
    print("=" * 80)

    chat_service = get_proximity_chat_service()

    # Get service info
    info = chat_service.get_service_info()
    print(f"Service ID: {info['service_id']}")
    print(f"Local Network: {info['local_network']}")
    print(f"Message Count: {info['message_count']}")
    print()

    # Send messages programmatically
    message1 = chat_service.send_message(
        "Service initialization complete",
        scope=MessageScope.LOCAL,
        metadata={"service": "example", "status": "ready"}
    )
    print(f"Sent message: {message1.message_id}")

    # Get recent messages
    recent = chat_service.get_recent_messages(limit=5)
    print(f"Recent messages: {len(recent)}")
    for msg in recent:
        print(f"  - {msg.sender_name}: {msg.content[:50]}")

    print("\n✅ Programmatic API example complete\n")


def example_ecosystem_integration():
    """Example: Full ecosystem integration"""
    print("=" * 80)
    print("Example: Ecosystem Integration")
    print("=" * 80)

    chat_service = get_proximity_chat_service()

    # Simulate multiple services communicating
    services = {
        "jarvis": "Jarvis Service",
        "workflow": "Workflow Engine",
        "monitor": "System Monitor",
        "scheduler": "Task Scheduler"
    }

    # Each service can send/receive messages
    for service_id, service_name in services.items():
        def create_handler(name):
            def handler(message: ProximityMessage):
                print(f"  [{name}] Received: {message.content[:40]}...")
            return handler

        chat_service.register_message_handler(create_handler(service_name))

    # Services communicate
    chat_service.send_message(
        "System check initiated",
        scope=MessageScope.LOCAL,
        metadata={"source": "monitor"}
    )

    chat_service.send_message(
        "All checks passed",
        scope=MessageScope.LOCAL,
        metadata={"source": "jarvis", "response": True}
    )

    print("✅ Ecosystem integration example complete\n")


def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("LUMINA PROXIMITY CHAT - INTEGRATION EXAMPLES")
    print("=" * 80)
    print()

    example_programmatic_api()
    example_jarvis_integration()
    example_workflow_integration()
    example_bubble_display()
    example_ecosystem_integration()

    print("=" * 80)
    print("All examples complete!")
    print("=" * 80)
    print()
    print("Key Points:")
    print("  - Service-oriented architecture")
    print("  - Programmatic API for integration")
    print("  - Proximity-aware messaging")
    print("  - Chat bubble visualization")
    print("  - Ecosystem-wide integration")
    print()


if __name__ == "__main__":


    main()