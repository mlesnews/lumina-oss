#!/usr/bin/env python3
"""
VA Analytics and Reporting System

Tracks and reports on VA performance, usage, and metrics.

Tags: #VIRTUAL_ASSISTANT #ANALYTICS #REPORTING #METRICS @JARVIS @LUMINA
"""

import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
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

logger = get_logger("VAAnalytics")


@dataclass
class AnalyticsEvent:
    """Analytics event"""
    event_id: str
    va_id: str
    event_type: str
    timestamp: str
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class VAAnalytics:
    """
    VA Analytics and Reporting System

    Features:
    - Usage analytics
    - Performance reports
    - Task completion metrics
    - User interaction tracking
    - Trend analysis
    """

    def __init__(self, registry: Optional[CharacterAvatarRegistry] = None):
        """Initialize analytics system"""
        if registry is None:
            if CharacterAvatarRegistry:
                registry = CharacterAvatarRegistry()
            else:
                raise ValueError("CharacterAvatarRegistry not available")

        self.registry = registry
        self.vas = self.registry.get_characters_by_type(CharacterType.VIRTUAL_ASSISTANT)

        # Event tracking
        self.events: List[AnalyticsEvent] = []
        self.event_counter = 0

        # Metrics aggregation
        self.metrics: Dict[str, Dict[str, Any]] = {va.character_id: {} for va in self.vas}

        # Data persistence
        self.data_dir = project_root / "data" / "va_analytics"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        logger.info("=" * 80)
        logger.info("📊 VA ANALYTICS SYSTEM")
        logger.info("=" * 80)
        logger.info(f"   VAs Registered: {len(self.vas)}")
        logger.info("   Analytics tracking active")
        logger.info("=" * 80)

    def track_usage(self, va_id: str, metric: str, value: Any):
        """Track usage metric"""
        if va_id not in self.metrics:
            self.metrics[va_id] = {}

        if metric not in self.metrics[va_id]:
            self.metrics[va_id][metric] = []

        self.metrics[va_id][metric].append({
            "value": value,
            "timestamp": datetime.now().isoformat()
        })

        # Keep only last 1000 entries per metric
        if len(self.metrics[va_id][metric]) > 1000:
            self.metrics[va_id][metric] = self.metrics[va_id][metric][-1000:]

    def record_event(self, va_id: str, event_type: str, data: Optional[Dict[str, Any]] = None):
        """Record analytics event"""
        self.event_counter += 1
        event_id = f"analytics_event_{self.event_counter:06d}"

        event = AnalyticsEvent(
            event_id=event_id,
            va_id=va_id,
            event_type=event_type,
            timestamp=datetime.now().isoformat(),
            data=data or {}
        )

        self.events.append(event)

        # Keep only last 10000 events
        if len(self.events) > 10000:
            self.events = self.events[-10000:]

        logger.debug(f"📊 Event recorded: {event_type} for {va_id}")

    def generate_report(self, va_id: str, period: str = "24h") -> Dict[str, Any]:
        """Generate analytics report for a VA"""
        # Parse period
        if period.endswith("h"):
            hours = int(period[:-1])
            cutoff = datetime.now() - timedelta(hours=hours)
        elif period.endswith("d"):
            days = int(period[:-1])
            cutoff = datetime.now() - timedelta(days=days)
        else:
            cutoff = datetime.now() - timedelta(hours=24)

        # Filter events
        va_events = [
            e for e in self.events
            if e.va_id == va_id and datetime.fromisoformat(e.timestamp) >= cutoff
        ]

        # Aggregate metrics
        report = {
            "va_id": va_id,
            "period": period,
            "start_time": cutoff.isoformat(),
            "end_time": datetime.now().isoformat(),
            "total_events": len(va_events),
            "events_by_type": {},
            "metrics": {}
        }

        # Count events by type
        for event in va_events:
            event_type = event.event_type
            report["events_by_type"][event_type] = report["events_by_type"].get(event_type, 0) + 1

        # Aggregate metrics
        va_metrics = self.metrics.get(va_id, {})
        for metric, values in va_metrics.items():
            recent_values = [
                v for v in values
                if datetime.fromisoformat(v["timestamp"]) >= cutoff
            ]
            if recent_values:
                numeric_values = [v["value"] for v in recent_values if isinstance(v["value"], (int, float))]
                if numeric_values:
                    report["metrics"][metric] = {
                        "count": len(numeric_values),
                        "sum": sum(numeric_values),
                        "avg": sum(numeric_values) / len(numeric_values),
                        "min": min(numeric_values),
                        "max": max(numeric_values)
                    }

        return report

    def performance_analysis(self, va_id: str) -> Dict[str, Any]:
        """Analyze VA performance"""
        va_events = [e for e in self.events if e.va_id == va_id]

        analysis = {
            "va_id": va_id,
            "total_events": len(va_events),
            "event_types": {},
            "performance_indicators": {}
        }

        # Count event types
        for event in va_events:
            event_type = event.event_type
            analysis["event_types"][event_type] = analysis["event_types"].get(event_type, 0) + 1

        # Performance indicators (simplified)
        task_events = [e for e in va_events if "task" in e.event_type.lower()]
        completed_events = [e for e in task_events if "complete" in e.event_type.lower()]

        if task_events:
            analysis["performance_indicators"]["task_completion_rate"] = len(completed_events) / len(task_events)

        return analysis

    def user_interaction_tracking(self, va_id: str) -> Dict[str, Any]:
        """Track user interactions with a VA"""
        interaction_events = [
            e for e in self.events
            if e.va_id == va_id and "interaction" in e.event_type.lower()
        ]

        return {
            "va_id": va_id,
            "total_interactions": len(interaction_events),
            "interaction_types": {},
            "recent_interactions": [
                {
                    "event_type": e.event_type,
                    "timestamp": e.timestamp,
                    "data": e.data
                }
                for e in interaction_events[-10:]
            ]
        }

    def trend_analysis(self, all_vas: bool = True) -> Dict[str, Any]:
        """Analyze trends across all VAs"""
        if all_vas:
            va_ids = [va.character_id for va in self.vas]
        else:
            va_ids = list(self.metrics.keys())

        trends = {
            "period": "all_time",
            "vas": []
        }

        for va_id in va_ids:
            va_events = [e for e in self.events if e.va_id == va_id]

            # Calculate events per day
            if va_events:
                first_event_time = datetime.fromisoformat(va_events[0].timestamp)
                time_diff = datetime.now() - first_event_time
                days = max(1, time_diff.days + 1)
                events_per_day = len(va_events) / days
            else:
                events_per_day = 0.0

            trend = {
                "va_id": va_id,
                "total_events": len(va_events),
                "events_per_day": events_per_day,
                "most_common_event": max(set(e.event_type for e in va_events), key=lambda x: sum(1 for e in va_events if e.event_type == x)) if va_events else None
            }

            trends["vas"].append(trend)

        return trends

    def _save_state(self):
        try:
            """Save analytics state"""
            state_file = self.data_dir / "analytics_state.json"

            state = {
                "recent_events": [e.to_dict() for e in self.events[-1000:]],
                "metrics_summary": {
                    va_id: {
                        metric: len(values)
                        for metric, values in metrics.items()
                    }
                    for va_id, metrics in self.metrics.items()
                },
                "event_counter": self.event_counter,
                "timestamp": datetime.now().isoformat()
            }

            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)

            logger.info(f"💾 Saved analytics state to {state_file}")


        except Exception as e:
            self.logger.error(f"Error in _save_state: {e}", exc_info=True)
            raise
def main():
    """Main entry point for testing"""
    if not CharacterAvatarRegistry:
        print("❌ Character Avatar Registry not available")
        return

    registry = CharacterAvatarRegistry()
    analytics = VAAnalytics(registry)

    print("=" * 80)
    print("📊 VA ANALYTICS SYSTEM TEST")
    print("=" * 80)
    print()

    # Test: Record events
    print("Recording events...")
    analytics.record_event("jarvis_va", "task_started", {"task_id": "task_001"})
    analytics.record_event("jarvis_va", "task_completed", {"task_id": "task_001", "duration": 1.5})
    analytics.record_event("ace", "combat_activated", {"threat_level": "high"})
    analytics.record_event("imva", "ui_interaction", {"action": "display_update"})
    print("  ✅ Events recorded")
    print()

    # Test: Track usage
    print("Tracking usage metrics...")
    analytics.track_usage("jarvis_va", "response_time", 0.5)
    analytics.track_usage("jarvis_va", "response_time", 0.6)
    analytics.track_usage("ace", "combat_events", 1)
    print("  ✅ Metrics tracked")
    print()

    # Test: Generate report
    print("Generating reports...")
    report = analytics.generate_report("jarvis_va", "24h")
    print(f"  ✅ Report for jarvis_va: {report['total_events']} events")
    print(f"    Event types: {report['events_by_type']}")
    print()

    # Test: Performance analysis
    print("Performance Analysis:")
    for va in analytics.vas[:2]:
        perf = analytics.performance_analysis(va.character_id)
        print(f"  • {va.name}: {perf['total_events']} events")
    print()

    # Test: Trend analysis
    print("Trend Analysis:")
    trends = analytics.trend_analysis()
    for trend in trends["vas"][:2]:
        print(f"  • {trend['va_id']}: {trend['total_events']} events")
    print()

    # Save state
    analytics._save_state()

    print("=" * 80)


if __name__ == "__main__":


    main()