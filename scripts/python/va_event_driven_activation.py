#!/usr/bin/env python3
"""
Event-Driven VA Activation System

Automatically activates Virtual Assistants based on system events.
Context-aware VA selection and priority-based activation.

Tags: #VIRTUAL_ASSISTANT #EVENT_DRIVEN #AUTOMATION #ACTIVATION @JARVIS @LUMINA
"""

import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from character_avatar_registry import (CharacterAvatarRegistry,
                                           CharacterType)
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    CharacterAvatarRegistry = None
    CharacterType = None

logger = get_logger("VAEventActivation")


class EventType(Enum):
    """System event types"""
    COMBAT = "combat"
    AUTOMATION = "automation"
    UI_INTERACTION = "ui_interaction"
    SYSTEM_EVENT = "system_event"
    CONCURRENT_BATTLE = "concurrent_battle"
    SECURITY = "security"
    WORKFLOW = "workflow"
    ERROR = "error"
    MILESTONE = "milestone"
    ENCOUNTER = "encounter"


class EventPriority(Enum):
    """Event priority"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class SystemEvent:
    """System event"""
    event_id: str
    event_type: EventType
    priority: EventPriority
    description: str
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    triggered_vas: List[str] = field(default_factory=list)


class VAEventActivationSystem:
    """
    Event-Driven VA Activation System

    Automatically activates VAs based on system events with:
    - Context-aware VA selection
    - Priority-based activation
    - Event routing
    - Automatic task assignment
    """

    def __init__(self, registry: Optional[CharacterAvatarRegistry] = None):
        """Initialize event-driven activation system"""
        if registry is None:
            if CharacterAvatarRegistry:
                registry = CharacterAvatarRegistry()
            else:
                raise ValueError("CharacterAvatarRegistry not available")

        self.registry = registry
        self.vas = self.registry.get_characters_by_type(CharacterType.VIRTUAL_ASSISTANT)

        # Event listeners
        self.event_listeners: Dict[EventType, List[str]] = {}  # event_type -> [va_ids]

        # Event history
        self.event_history: List[SystemEvent] = []

        # VA-event mapping
        self.va_event_mapping = self._initialize_va_event_mapping()

        # Event routing rules
        self.routing_rules = self._initialize_routing_rules()

        logger.info("=" * 80)
        logger.info("⚡ EVENT-DRIVEN VA ACTIVATION SYSTEM")
        logger.info("=" * 80)
        logger.info(f"   VAs Registered: {len(self.vas)}")
        logger.info("   Event listeners configured")
        logger.info("=" * 80)

    def _initialize_va_event_mapping(self) -> Dict[str, List[EventType]]:
        """Initialize VA-to-event mapping based on VA capabilities"""
        mapping = {}

        for va in self.vas:
            va_events = []

            # JARVIS_VA: Automation, system events
            if va.character_id == "jarvis_va":
                va_events.extend([EventType.AUTOMATION, EventType.SYSTEM_EVENT, EventType.WORKFLOW])

            # IMVA: UI interactions
            if va.character_id == "imva":
                va_events.extend([EventType.UI_INTERACTION, EventType.SYSTEM_EVENT])

            # ACE: Combat, security
            if va.character_id == "ace":
                va_events.extend([EventType.COMBAT, EventType.SECURITY, EventType.ENCOUNTER])

            # AVA: Concurrent battles, general
            if va.character_id == "ava":
                va_events.extend([EventType.CONCURRENT_BATTLE, EventType.SYSTEM_EVENT])

            # Combat mode enabled
            if va.combat_mode_enabled:
                if EventType.COMBAT not in va_events:
                    va_events.append(EventType.COMBAT)

            mapping[va.character_id] = va_events

        return mapping

    def _initialize_routing_rules(self) -> Dict[EventType, Dict[str, Any]]:
        """Initialize event routing rules"""
        return {
            EventType.COMBAT: {
                "primary_va": "ace",
                "secondary_vas": ["jarvis_va", "ava"],
                "auto_activate": True
            },
            EventType.AUTOMATION: {
                "primary_va": "jarvis_va",
                "secondary_vas": ["imva"],
                "auto_activate": True
            },
            EventType.UI_INTERACTION: {
                "primary_va": "imva",
                "secondary_vas": ["jarvis_va"],
                "auto_activate": True
            },
            EventType.CONCURRENT_BATTLE: {
                "primary_va": "ava",
                "secondary_vas": ["ace", "jarvis_va"],
                "auto_activate": True
            },
            EventType.SECURITY: {
                "primary_va": "ace",
                "secondary_vas": ["jarvis_va"],
                "auto_activate": True
            },
            EventType.WORKFLOW: {
                "primary_va": "jarvis_va",
                "secondary_vas": ["imva", "ace"],
                "auto_activate": True
            },
            EventType.ERROR: {
                "primary_va": "jarvis_va",
                "secondary_vas": ["ace", "imva"],
                "auto_activate": True
            },
            EventType.MILESTONE: {
                "primary_va": "jarvis_va",
                "secondary_vas": ["imva", "ace", "ava"],
                "auto_activate": True
            },
            EventType.ENCOUNTER: {
                "primary_va": "ace",
                "secondary_vas": ["ava", "jarvis_va"],
                "auto_activate": True
            }
        }

    def register_event_listener(self, event_type: EventType, va_id: str):
        """Register VA as listener for event type"""
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = []

        if va_id not in self.event_listeners[event_type]:
            self.event_listeners[event_type].append(va_id)
            logger.info(f"👂 Registered {va_id} for {event_type.value} events")

    def trigger_event(self, event_type: EventType, description: str,
                     priority: EventPriority = EventPriority.MEDIUM,
                     context: Optional[Dict[str, Any]] = None) -> SystemEvent:
        """Trigger a system event and activate appropriate VAs"""
        event_id = f"event_{datetime.now().timestamp()}"

        event = SystemEvent(
            event_id=event_id,
            event_type=event_type,
            priority=priority,
            description=description,
            context=context or {}
        )

        # Select VAs for this event
        activated_vas = self._select_vas_for_event(event)
        event.triggered_vas = activated_vas

        # Record event
        self.event_history.append(event)

        logger.info(f"⚡ Event triggered: {event_type.value} - {description}")
        logger.info(f"   Activated VAs: {', '.join(activated_vas)}")

        return event

    def _select_vas_for_event(self, event: SystemEvent) -> List[str]:
        """Select appropriate VAs for event"""
        selected_vas = []

        # Check routing rules
        if event.event_type in self.routing_rules:
            rule = self.routing_rules[event.event_type]

            # Primary VA
            primary_va = rule.get("primary_va")
            if primary_va:
                va = self.registry.get_character(primary_va)
                if va and va.character_type == CharacterType.VIRTUAL_ASSISTANT:
                    selected_vas.append(primary_va)

            # Secondary VAs (if priority is high/critical)
            if event.priority in [EventPriority.HIGH, EventPriority.CRITICAL]:
                secondary_vas = rule.get("secondary_vas", [])
                for va_id in secondary_vas[:2]:  # Limit to 2 secondary
                    va = self.registry.get_character(va_id)
                    if va and va.character_type == CharacterType.VIRTUAL_ASSISTANT:
                        if va_id not in selected_vas:
                            selected_vas.append(va_id)

        # Check event listeners
        if event.event_type in self.event_listeners:
            for va_id in self.event_listeners[event.event_type]:
                if va_id not in selected_vas:
                    selected_vas.append(va_id)

        # Fallback: Use VA-event mapping
        if not selected_vas:
            for va_id, va_events in self.va_event_mapping.items():
                if event.event_type in va_events:
                    selected_vas.append(va_id)
                    break

        return selected_vas

    def get_event_history(self, event_type: Optional[EventType] = None,
                         limit: int = 50) -> List[SystemEvent]:
        """Get event history"""
        history = self.event_history.copy()

        if event_type:
            history = [e for e in history if e.event_type == event_type]

        return history[-limit:]

    def get_va_activation_stats(self, va_id: str) -> Dict[str, Any]:
        """Get activation statistics for a VA"""
        stats = {
            "total_activations": 0,
            "by_event_type": {},
            "by_priority": {},
            "recent_activations": []
        }

        for event in self.event_history:
            if va_id in event.triggered_vas:
                stats["total_activations"] += 1

                event_type = event.event_type.value
                stats["by_event_type"][event_type] = stats["by_event_type"].get(event_type, 0) + 1

                priority = event.priority.value
                stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1

                stats["recent_activations"].append({
                    "event_id": event.event_id,
                    "event_type": event_type,
                    "priority": priority,
                    "timestamp": event.timestamp
                })

        # Keep only last 10
        stats["recent_activations"] = stats["recent_activations"][-10:]

        return stats


def main():
    """Main entry point for testing"""
    if not CharacterAvatarRegistry:
        print("❌ Character Avatar Registry not available")
        return

    registry = CharacterAvatarRegistry()
    activation_system = VAEventActivationSystem(registry)

    print("=" * 80)
    print("⚡ EVENT-DRIVEN VA ACTIVATION SYSTEM TEST")
    print("=" * 80)
    print()

    # Test: Combat event
    print("Triggering combat event...")
    event1 = activation_system.trigger_event(
        event_type=EventType.COMBAT,
        description="Combat encounter detected",
        priority=EventPriority.HIGH
    )
    print(f"✅ Event triggered: {event1.event_id}")
    print(f"   Activated VAs: {', '.join(event1.triggered_vas)}")
    print()

    # Test: Automation event
    print("Triggering automation event...")
    event2 = activation_system.trigger_event(
        event_type=EventType.AUTOMATION,
        description="Workflow automation required",
        priority=EventPriority.MEDIUM
    )
    print(f"✅ Event triggered: {event2.event_id}")
    print(f"   Activated VAs: {', '.join(event2.triggered_vas)}")
    print()

    # Test: UI interaction event
    print("Triggering UI interaction event...")
    event3 = activation_system.trigger_event(
        event_type=EventType.UI_INTERACTION,
        description="User interface interaction",
        priority=EventPriority.LOW
    )
    print(f"✅ Event triggered: {event3.event_id}")
    print(f"   Activated VAs: {', '.join(event3.triggered_vas)}")
    print()

    # Test: Get activation stats
    print("VA Activation Statistics:")
    for va in activation_system.vas:
        stats = activation_system.get_va_activation_stats(va.character_id)
        print(f"  • {va.name} ({va.character_id})")
        print(f"    Total Activations: {stats['total_activations']}")
        if stats['by_event_type']:
            print(f"    By Event Type: {stats['by_event_type']}")
        print()

    print("=" * 80)


if __name__ == "__main__":


    main()