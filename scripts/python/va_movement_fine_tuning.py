#!/usr/bin/env python3
"""
VA Movement Fine-Tuning System

Captures VA movement events and uses them as eye tracking fine-tuning opportunities.
When a user moves a VA, they were looking at it - this is valuable learning data.

Tags: #EYE_TRACKING #FINE_TUNING #VA_MOVEMENT #LEARNING @JARVIS @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum

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

logger = get_logger("VAMovementFineTuning")


class MovementType(Enum):
    """Types of VA movements"""
    DRAG_START = "drag_start"
    DRAG_MOVE = "drag_move"
    DRAG_END = "drag_end"
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    POSITION_CHANGE = "position_change"


@dataclass
class VAMovementEvent:
    """A VA movement event for fine-tuning"""
    event_id: str
    va_id: str
    va_name: str
    movement_type: MovementType
    screen_position: Tuple[float, float]  # (x, y) where VA is/was
    window_size: Tuple[float, float]  # (width, height)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    operator_gaze_estimate: Optional[Tuple[float, float]] = None  # Estimated gaze position
    context: Dict[str, Any] = field(default_factory=dict)


class VAMovementFineTuning:
    """
    VA Movement Fine-Tuning System

    Captures VA movement events and provides them to eye tracking systems
    for fine-tuning. When a user moves a VA, they were looking at it.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize VA Movement Fine-Tuning System"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.logger = logger

        # Movement event storage
        self.movement_events: List[VAMovementEvent] = []
        self.max_events = 1000  # Keep last 1000 events

        # Subscribers (systems that want movement data)
        self.subscribers: List[Any] = []  # Will store JARVIS instance references

        # Data file
        self.data_file = self.project_root / "data" / "jarvis" / "va_movement_learning.json"
        self.data_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing data
        self._load_movement_data()

        self.logger.info("✅ VA Movement Fine-Tuning System initialized")
        self.logger.info(f"   Loaded {len(self.movement_events)} movement events")

    def register_subscriber(self, subscriber: Any):
        """Register a subscriber (e.g., JARVIS) to receive movement events"""
        if subscriber not in self.subscribers:
            self.subscribers.append(subscriber)
            self.logger.info(f"✅ Registered subscriber: {type(subscriber).__name__}")

    def record_movement(self, va_id: str, va_name: str, movement_type: MovementType,
                       screen_position: Tuple[float, float],
                       window_size: Tuple[float, float] = (0, 0),
                       context: Optional[Dict[str, Any]] = None) -> VAMovementEvent:
        """
        Record a VA movement event

        Args:
            va_id: VA identifier (e.g., "jarvis_va", "kenny")
            va_name: VA display name
            movement_type: Type of movement
            screen_position: Screen position (x, y)
            window_size: Window size (width, height)
            context: Additional context

        Returns:
            Created movement event
        """
        event_id = f"movement_{int(time.time() * 1000)}_{len(self.movement_events)}"

        event = VAMovementEvent(
            event_id=event_id,
            va_id=va_id,
            va_name=va_name,
            movement_type=movement_type,
            screen_position=screen_position,
            window_size=window_size,
            context=context or {}
        )

        # Estimate operator gaze - if user moved VA, they were looking at it
        # Gaze is estimated to be at the center of the VA window
        va_center_x = screen_position[0] + (window_size[0] / 2) if window_size[0] > 0 else screen_position[0]
        va_center_y = screen_position[1] + (window_size[1] / 2) if window_size[1] > 0 else screen_position[1]
        event.operator_gaze_estimate = (va_center_x, va_center_y)

        # Store event
        self.movement_events.append(event)

        # Keep only recent events
        if len(self.movement_events) > self.max_events:
            self.movement_events = self.movement_events[-self.max_events:]

        # Notify subscribers (e.g., JARVIS eye tracking fine-tuning)
        self._notify_subscribers(event)

        # Save periodically
        if len(self.movement_events) % 50 == 0:
            self._save_movement_data()

        self.logger.debug(f"📊 Recorded {movement_type.value} for {va_name} at {screen_position}")

        return event

    def _notify_subscribers(self, event: VAMovementEvent):
        """Notify subscribers about movement event"""
        for subscriber in self.subscribers:
            try:
                # Check if subscriber has method to receive movement events
                if hasattr(subscriber, 'on_va_movement'):
                    subscriber.on_va_movement(event)
                elif hasattr(subscriber, '_on_va_movement_fine_tuning'):
                    subscriber._on_va_movement_fine_tuning(event)
            except Exception as e:
                self.logger.debug(f"Subscriber notification error: {e}")

    def get_movement_events(self, va_id: Optional[str] = None,
                           movement_type: Optional[MovementType] = None,
                           limit: int = 100) -> List[VAMovementEvent]:
        """Get movement events, optionally filtered"""
        events = self.movement_events

        if va_id:
            events = [e for e in events if e.va_id == va_id]

        if movement_type:
            events = [e for e in events if e.movement_type == movement_type]

        # Return most recent
        return events[-limit:]

    def get_gaze_estimates_from_movements(self, limit: int = 100) -> List[Tuple[float, float]]:
        """Get gaze position estimates from movement events"""
        events = self.get_movement_events(limit=limit)
        estimates = []

        for event in events:
            if event.operator_gaze_estimate:
                estimates.append(event.operator_gaze_estimate)

        return estimates

    def _load_movement_data(self):
        """Load movement data from file"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    # Reconstruct events
                    events_data = data.get("movement_events", [])
                    self.movement_events = []

                    for event_data in events_data:
                        try:
                            event = VAMovementEvent(
                                event_id=event_data.get("event_id", ""),
                                va_id=event_data.get("va_id", ""),
                                va_name=event_data.get("va_name", ""),
                                movement_type=MovementType(event_data.get("movement_type", "drag_end")),
                                screen_position=tuple(event_data.get("screen_position", [0, 0])),
                                window_size=tuple(event_data.get("window_size", [0, 0])),
                                timestamp=event_data.get("timestamp", ""),
                                operator_gaze_estimate=tuple(event_data.get("operator_gaze_estimate", [0, 0])) if event_data.get("operator_gaze_estimate") else None,
                                context=event_data.get("context", {})
                            )
                            self.movement_events.append(event)
                        except Exception as e:
                            self.logger.debug(f"Error loading event: {e}")

                    self.logger.info(f"✅ Loaded {len(self.movement_events)} movement events")
        except Exception as e:
            self.logger.debug(f"Could not load movement data: {e}")
            self.movement_events = []

    def _save_movement_data(self):
        """Save movement data to file"""
        try:
            data = {
                "movement_events": [asdict(event) for event in self.movement_events[-500:]],  # Keep last 500
                "last_updated": datetime.now().isoformat(),
                "total_events": len(self.movement_events)
            }

            # Convert enums to strings
            for event_data in data["movement_events"]:
                if "movement_type" in event_data:
                    event_data["movement_type"] = event_data["movement_type"].value if isinstance(event_data["movement_type"], MovementType) else event_data["movement_type"]

            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.debug(f"💾 Saved {len(data['movement_events'])} movement events")
        except Exception as e:
            self.logger.debug(f"Could not save movement data: {e}")


# Global singleton instance
_global_instance: Optional[VAMovementFineTuning] = None


def get_va_movement_fine_tuning(project_root: Optional[Path] = None) -> VAMovementFineTuning:
    """Get global VA Movement Fine-Tuning instance"""
    global _global_instance

    if _global_instance is None:
        _global_instance = VAMovementFineTuning(project_root=project_root)

    return _global_instance


def record_va_movement(va_id: str, va_name: str, movement_type: MovementType,
                      screen_position: Tuple[float, float],
                      window_size: Tuple[float, float] = (0, 0),
                      context: Optional[Dict[str, Any]] = None) -> VAMovementEvent:
    """Convenience function to record VA movement"""
    system = get_va_movement_fine_tuning()
    return system.record_movement(va_id, va_name, movement_type, screen_position, window_size, context)
