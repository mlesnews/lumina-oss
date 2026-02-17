#!/usr/bin/env python3
"""
Collaborative Workflow Tracker - Learning OUR Workflow Patterns

Every focus change, alt-tab, or interruption is a RED FLAG indicating
productivity degradation. We're learning how WE work together to become
ONE API interface instead of two opposing interfaces struggling to communicate.

This is the hard way - pieces face down, no pattern matching shortcuts.
We're building the puzzle from scratch, learning every granular detail.

Tags: #WORKFLOW #COLLABORATION #PRODUCTIVITY #LEARNING #API_INTEGRATION @JARVIS @LUMINA
"""

import sys
import json
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
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

logger = get_logger("CollaborativeWorkflowTracker")


class FocusChangeType(Enum):
    """Types of focus changes that indicate productivity degradation"""
    ALT_TAB = "alt_tab"  # Alt+Tab away from conversation
    WINDOW_SWITCH = "window_switch"  # Window focus change
    APP_SWITCH = "app_switch"  # Application switch
    MANUAL_FOCUS = "manual_focus"  # Manual focus change
    INTERRUPTION = "interruption"  # External interruption
    UNKNOWN = "unknown"  # Unknown focus change


class ProductivityImpact(Enum):
    """Impact level of focus change on productivity"""
    CRITICAL = "critical"  # Complete workflow break
    HIGH = "high"  # Significant degradation
    MEDIUM = "medium"  # Moderate impact
    LOW = "low"  # Minor impact
    NONE = "none"  # No impact


@dataclass
class FocusChangeEvent:
    """Record of a focus change event (productivity red flag)"""
    event_id: str
    timestamp: datetime
    change_type: FocusChangeType
    from_window: str
    to_window: str
    from_app: str
    to_app: str
    duration_away: float = 0.0  # Seconds away from conversation
    productivity_impact: ProductivityImpact = ProductivityImpact.MEDIUM
    context: Dict[str, Any] = field(default_factory=dict)
    recovered: bool = False  # Did we recover back to conversation?
    recovery_time: Optional[float] = None  # Time to recover (seconds)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["change_type"] = self.change_type.value
        data["productivity_impact"] = self.productivity_impact.value
        return data


@dataclass
class WorkflowPattern:
    """Learned pattern of how WE work together"""
    pattern_id: str
    name: str
    description: str
    trigger_conditions: List[str] = field(default_factory=list)
    typical_duration: float = 0.0
    frequency: int = 0
    productivity_impact: ProductivityImpact = ProductivityImpact.MEDIUM
    compensation_strategy: str = ""  # How we compensate for this pattern
    learned_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["learned_at"] = self.learned_at.isoformat()
        data["productivity_impact"] = self.productivity_impact.value
        return data


class CollaborativeWorkflowTracker:
    """
    Collaborative Workflow Tracker

    Tracks every focus change as a productivity red flag.
    Learns how WE work together to become ONE API interface.

    Goal: Minimize interruptions, maximize seamless collaboration.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Use centralized storage (not local) - preserve local disk space
        try:
            from centralized_holocron_storage import CentralizedHolocronStorage
            self.storage = CentralizedHolocronStorage(project_root=project_root)
            # Use holocron base for workflow data (centralized storage)
            self.data_dir = self.storage.holocron_base / "collaborative_workflow"
            self.use_centralized = True
            logger.info("✅ Using centralized storage (preserves local disk space)")
        except ImportError:
            # Fallback to local (shouldn't happen, but graceful degradation)
            self.data_dir = self.project_root / "data" / "collaborative_workflow"
            self.storage = None
            self.use_centralized = False
            logger.warning("⚠️  Centralized storage not available, using local")

        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Data files
        self.events_file = self.data_dir / "focus_events.jsonl"
        self.patterns_file = self.data_dir / "workflow_patterns.json"
        self.stats_file = self.data_dir / "workflow_stats.json"

        # Current state
        self.current_window = ""
        self.current_app = ""
        self.conversation_window = ""  # Window where our conversation is
        self.conversation_app = ""  # App where our conversation is (Cursor IDE)
        self.is_in_conversation = True
        self.last_focus_time = datetime.now()
        self.focus_change_events: List[FocusChangeEvent] = []

        # Learned patterns
        self.workflow_patterns: Dict[str, WorkflowPattern] = {}

        # Statistics
        self.stats = {
            "total_focus_changes": 0,
            "total_time_away": 0.0,
            "critical_interruptions": 0,
            "high_impact_changes": 0,
            "recovered_events": 0,
            "unrecovered_events": 0,
            "average_recovery_time": 0.0,
            "productivity_score": 100.0  # 100 = perfect, decreases with interruptions
        }

        # Monitoring thread
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None

        # Load existing data
        self._load_patterns()
        self._load_stats()

        # Integrate with Jedi training holocron (centralized storage)
        try:
            from jedi_training_holocron_integration import JediTrainingHolocron
            self.jedi_holocron = JediTrainingHolocron(project_root=project_root)
            # Auto-integrate analytics periodically
            self._schedule_jedi_integration()
        except ImportError:
            self.jedi_holocron = None
            logger.debug("Jedi training holocron not available")

        logger.info("=" * 80)
        logger.info("🤝 COLLABORATIVE WORKFLOW TRACKER")
        logger.info("=" * 80)
        logger.info("   Goal: Become ONE API interface")
        logger.info("   Method: Learn every granular detail of OUR workflow")
        logger.info("   Red Flag: Every focus change = productivity degradation")
        logger.info(f"   Patterns Learned: {len(self.workflow_patterns)}")
        logger.info(f"   Focus Changes Tracked: {self.stats['total_focus_changes']}")
        logger.info(f"   Productivity Score: {self.stats['productivity_score']:.1f}/100")
        logger.info("=" * 80)

    def _load_patterns(self):
        """Load learned workflow patterns"""
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for pattern_data in data.get("patterns", []):
                        pattern = WorkflowPattern(
                            pattern_id=pattern_data["pattern_id"],
                            name=pattern_data["name"],
                            description=pattern_data["description"],
                            trigger_conditions=pattern_data.get("trigger_conditions", []),
                            typical_duration=pattern_data.get("typical_duration", 0.0),
                            frequency=pattern_data.get("frequency", 0),
                            productivity_impact=ProductivityImpact(pattern_data.get("productivity_impact", "medium")),
                            compensation_strategy=pattern_data.get("compensation_strategy", ""),
                            learned_at=datetime.fromisoformat(pattern_data.get("learned_at", datetime.now().isoformat()))
                        )
                        self.workflow_patterns[pattern.pattern_id] = pattern
                logger.info(f"✅ Loaded {len(self.workflow_patterns)} workflow patterns")
            except Exception as e:
                logger.error(f"❌ Error loading patterns: {e}")

    def _save_patterns(self):
        """Save learned workflow patterns"""
        try:
            data = {
                "version": "1.0.0",
                "last_updated": datetime.now().isoformat(),
                "patterns": [pattern.to_dict() for pattern in self.workflow_patterns.values()]
            }
            with open(self.patterns_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Error saving patterns: {e}")

    def _load_stats(self):
        """Load workflow statistics"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    self.stats.update(json.load(f))
            except Exception as e:
                logger.error(f"❌ Error loading stats: {e}")

    def _save_stats(self):
        """Save workflow statistics"""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Error saving stats: {e}")

    def register_conversation_window(self, window_title: str, app_name: str = "Cursor IDE"):
        """
        Register the conversation window (where WE are working)

        This is our primary workspace - leaving it is a red flag.
        """
        self.conversation_window = window_title
        self.conversation_app = app_name
        self.current_window = window_title
        self.current_app = app_name
        self.is_in_conversation = True
        logger.info(f"📌 Registered conversation window: {window_title} ({app_name})")

    def track_focus_change(
        self,
        to_window: str,
        to_app: str,
        change_type: FocusChangeType = FocusChangeType.UNKNOWN
    ) -> FocusChangeEvent:
        """
        Track a focus change - RED FLAG for productivity degradation

        Every focus change away from our conversation is tracked and analyzed.
        """
        from_window = self.current_window
        from_app = self.current_app

        # Determine if we're leaving conversation
        leaving_conversation = (
            self.is_in_conversation and
            (to_app != self.conversation_app or to_window != self.conversation_window)
        )

        # Determine if we're returning to conversation
        returning_to_conversation = (
            not self.is_in_conversation and
            (to_app == self.conversation_app or to_window == self.conversation_window)
        )

        # Calculate time away if returning
        duration_away = 0.0
        if returning_to_conversation and self.last_focus_time:
            duration_away = (datetime.now() - self.last_focus_time).total_seconds()

        # Determine productivity impact
        if leaving_conversation:
            if change_type == FocusChangeType.ALT_TAB:
                impact = ProductivityImpact.CRITICAL
            elif change_type == FocusChangeType.APP_SWITCH:
                impact = ProductivityImpact.HIGH
            else:
                impact = ProductivityImpact.MEDIUM
        else:
            impact = ProductivityImpact.LOW

        # Create event
        event = FocusChangeEvent(
            event_id=f"focus_{int(time.time())}_{len(self.focus_change_events)}",
            timestamp=datetime.now(),
            change_type=change_type,
            from_window=from_window,
            to_window=to_window,
            from_app=from_app,
            to_app=to_app,
            duration_away=duration_away if returning_to_conversation else 0.0,
            productivity_impact=impact,
            context={
                "leaving_conversation": leaving_conversation,
                "returning_to_conversation": returning_to_conversation,
                "conversation_window": self.conversation_window,
                "conversation_app": self.conversation_app
            },
            recovered=returning_to_conversation,
            recovery_time=duration_away if returning_to_conversation else None
        )

        # Update state
        self.current_window = to_window
        self.current_app = to_app
        self.is_in_conversation = not leaving_conversation if leaving_conversation else returning_to_conversation

        if leaving_conversation:
            self.last_focus_time = datetime.now()
        elif returning_to_conversation:
            # We recovered - log recovery time
            if event.recovery_time:
                self.stats["recovered_events"] += 1
                # Update average recovery time
                total_recovered = self.stats["recovered_events"]
                current_avg = self.stats["average_recovery_time"]
                self.stats["average_recovery_time"] = (
                    (current_avg * (total_recovered - 1) + event.recovery_time) / total_recovered
                )

        # Update statistics
        self.stats["total_focus_changes"] += 1
        if event.productivity_impact == ProductivityImpact.CRITICAL:
            self.stats["critical_interruptions"] += 1
        elif event.productivity_impact == ProductivityImpact.HIGH:
            self.stats["high_impact_changes"] += 1

        if not event.recovered:
            self.stats["unrecovered_events"] += 1

        # Calculate productivity score (decreases with interruptions)
        self._update_productivity_score()

        # Save event
        self._save_event(event)

        # Learn from this event
        self._learn_from_event(event)

        # Log red flag
        if leaving_conversation:
            logger.warning(f"🚩 RED FLAG: Focus change away from conversation")
            logger.warning(f"   From: {from_app} ({from_window})")
            logger.warning(f"   To: {to_app} ({to_window})")
            logger.warning(f"   Impact: {impact.value.upper()}")
        elif returning_to_conversation:
            logger.info(f"✅ Recovered to conversation (away for {duration_away:.1f}s)")

        return event

    def _update_productivity_score(self):
        """Update productivity score based on interruptions"""
        # Base score: 100
        # Deduct points for interruptions
        score = 100.0

        # Critical interruptions: -5 points each
        score -= self.stats["critical_interruptions"] * 5.0

        # High impact changes: -2 points each
        score -= self.stats["high_impact_changes"] * 2.0

        # Unrecovered events: -3 points each
        score -= self.stats["unrecovered_events"] * 3.0

        # Time away penalty: -0.1 points per second
        score -= min(self.stats["total_time_away"] * 0.1, 20.0)  # Max 20 point penalty

        # Ensure score doesn't go below 0
        self.stats["productivity_score"] = max(0.0, score)

    def _save_event(self, event: FocusChangeEvent):
        """Save focus change event to log"""
        try:
            with open(self.events_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event.to_dict(), ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"❌ Error saving event: {e}")

    def _learn_from_event(self, event: FocusChangeEvent):
        """
        Learn from focus change event

        This is the hard way - building the puzzle piece by piece,
        learning every granular detail of how WE work together.
        """
        # Look for patterns in the event
        # This is where we learn compensation strategies

        # Example: If we frequently alt-tab to check something,
        # learn to provide that information proactively

        # For now, just track the event
        # In future, we'll build pattern recognition

        pass

    def get_workflow_insights(self) -> Dict[str, Any]:
        """Get insights about our collaborative workflow"""
        insights = {
            "productivity_score": self.stats["productivity_score"],
            "total_interruptions": self.stats["total_focus_changes"],
            "critical_interruptions": self.stats["critical_interruptions"],
            "average_recovery_time": self.stats["average_recovery_time"],
            "recovery_rate": (
                self.stats["recovered_events"] / max(self.stats["total_focus_changes"], 1) * 100
            ),
            "patterns_learned": len(self.workflow_patterns),
            "is_in_conversation": self.is_in_conversation,
            "current_window": self.current_window,
            "current_app": self.current_app
        }

        # Auto-integrate with Jedi training holocron
        if self.jedi_holocron:
            try:
                self.jedi_holocron.integrate_workflow_tracker_analytics(self)
            except Exception as e:
                logger.debug(f"Could not integrate with Jedi holocron: {e}")

        return insights

    def _schedule_jedi_integration(self):
        """Schedule periodic integration with Jedi training holocron"""
        # Integration happens automatically in get_workflow_insights()
        # This is a placeholder for future scheduled integration
        pass

    def start_monitoring(self):
        """Start monitoring focus changes"""
        if self.monitoring_active:
            logger.warning("⚠️  Monitoring already active")
            return

        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("🔄 Started focus change monitoring")

    def stop_monitoring(self):
        """Stop monitoring focus changes"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
        logger.info("⏹️  Stopped focus change monitoring")

    def _monitoring_loop(self):
        """Monitor focus changes (Windows-specific)"""
        try:
            import win32gui
            import win32process
            import psutil

            last_window = None

            while self.monitoring_active:
                try:
                    # Get current foreground window
                    hwnd = win32gui.GetForegroundWindow()
                    window_title = win32gui.GetWindowText(hwnd)

                    # Get process name
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    process = psutil.Process(pid)
                    app_name = process.name()

                    # Check if window changed
                    if window_title != last_window:
                        if last_window is not None:
                            # Focus changed
                            change_type = FocusChangeType.WINDOW_SWITCH
                            if app_name != self.current_app:
                                change_type = FocusChangeType.APP_SWITCH

                            self.track_focus_change(
                                to_window=window_title,
                                to_app=app_name,
                                change_type=change_type
                            )

                        last_window = window_title

                    time.sleep(0.5)  # Check every 500ms

                except Exception as e:
                    logger.debug(f"Error in monitoring loop: {e}")
                    time.sleep(1.0)

        except ImportError:
            logger.warning("⚠️  Windows monitoring requires pywin32 and psutil")
            logger.warning("   Install: pip install pywin32 psutil")
        except Exception as e:
            logger.error(f"❌ Monitoring error: {e}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Collaborative Workflow Tracker")
    parser.add_argument("--register", type=str, help="Register conversation window title")
    parser.add_argument("--start", action="store_true", help="Start monitoring")
    parser.add_argument("--stop", action="store_true", help="Stop monitoring")
    parser.add_argument("--insights", action="store_true", help="Show workflow insights")

    args = parser.parse_args()

    tracker = CollaborativeWorkflowTracker()

    if args.register:
        tracker.register_conversation_window(args.register)

    if args.start:
        tracker.start_monitoring()
        print("✅ Monitoring started")
        print("   Press Ctrl+C to stop")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            tracker.stop_monitoring()

    if args.stop:
        tracker.stop_monitoring()
        print("✅ Monitoring stopped")

    if args.insights:
        insights = tracker.get_workflow_insights()
        print("\n" + "=" * 80)
        print("🤝 COLLABORATIVE WORKFLOW INSIGHTS")
        print("=" * 80)
        print(f"Productivity Score: {insights['productivity_score']:.1f}/100")
        print(f"Total Interruptions: {insights['total_interruptions']}")
        print(f"Critical Interruptions: {insights['critical_interruptions']}")
        print(f"Average Recovery Time: {insights['average_recovery_time']:.1f}s")
        print(f"Recovery Rate: {insights['recovery_rate']:.1f}%")
        print(f"Patterns Learned: {insights['patterns_learned']}")
        print(f"In Conversation: {insights['is_in_conversation']}")
        print(f"Current: {insights['current_app']} - {insights['current_window']}")
        print("=" * 80)


if __name__ == "__main__":


    main()