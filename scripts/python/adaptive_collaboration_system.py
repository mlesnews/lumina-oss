#!/usr/bin/env python3
"""
Adaptive Collaboration System - Unified AI-Human Collaboration

Integrates adaptive ask processing, mutual reminders, and learning.
Provides unified interface for context-aware collaboration.

Tags: #ADAPTIVE #COLLABORATION #LEARNING #SWARM @JARVIS @LUMINA @AIQ
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger
from adaptive_ask_processor import AdaptiveAskProcessor, CollaborationContext, ProcessingMode
from mutual_reminder_system import MutualReminderSystem, ReminderSource, ReminderType

logger = get_logger("AdaptiveCollaborationSystem")


@dataclass
class CollaborationSession:
    """Collaboration session data"""
    session_id: str
    started_at: str
    context: CollaborationContext
    mode: ProcessingMode
    asks_processed: int = 0
    reminders_created: int = 0
    patterns_learned: int = 0
    performance_score: float = 0.0


class AdaptiveCollaborationSystem:
    """
    Adaptive Collaboration System - Unified Interface

    Integrates:
    - Adaptive ask processing (context-aware)
    - Mutual reminder system
    - Learning and pattern matching
    - Performance tracking
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize adaptive collaboration system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.collab_dir = self.data_dir / "adaptive_collaboration"
        self.collab_dir.mkdir(parents=True, exist_ok=True)

        # Initialize subsystems
        self.ask_processor = AdaptiveAskProcessor(project_root)
        self.reminder_system = MutualReminderSystem(project_root)

        # Current session
        self.current_session: Optional[CollaborationSession] = None

        logger.info("=" * 80)
        logger.info("🔄 ADAPTIVE COLLABORATION SYSTEM INITIALIZED")
        logger.info("   Integrated: Ask Processor + Reminder System")
        logger.info("=" * 80)

    def start_session(
        self,
        context: Optional[CollaborationContext] = None,
        activity: Optional[str] = None
    ) -> CollaborationSession:
        """Start a new collaboration session"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Detect context if not provided
        if context is None:
            context = self.ask_processor.detect_context(activity)

        mode = self.ask_processor.select_mode(context)

        session = CollaborationSession(
            session_id=session_id,
            started_at=datetime.now().isoformat(),
            context=context,
            mode=mode
        )

        self.current_session = session

        logger.info(f"🚀 Session started: {session_id}")
        logger.info(f"   Context: {context.value}, Mode: {mode.value}")

        return session

    def process_asks_with_context(
        self,
        asks: List[Dict[str, Any]],
        activity: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Process asks with adaptive context awareness

        Args:
            asks: List of asks to process
            activity: Current activity description

        Returns:
            Processed asks in appropriate order
        """
        # Update context based on activity
        context = self.ask_processor.detect_context(activity)

        # Process asks adaptively
        processed = self.ask_processor.process_asks_adaptively(
            asks=asks,
            context=context,
            activity=activity
        )

        # Check for reminders
        reminders = self.reminder_system.get_active_reminders(limit=5)
        if reminders:
            logger.info(f"📌 {len(reminders)} active reminders")
            for reminder in reminders:
                logger.info(f"   • {reminder.title}")

        if self.current_session:
            self.current_session.asks_processed += len(processed)

        return processed

    def check_reminders(self) -> List[Dict[str, Any]]:
        """Check for active reminders"""
        reminders = self.reminder_system.get_active_reminders(limit=10)

        if reminders:
            logger.info(f"\n📋 ACTIVE REMINDERS ({len(reminders)}):")
            logger.info("=" * 80)
            for reminder in reminders:
                logger.info(f"   [{reminder.source.value.upper()}] {reminder.title}")
                logger.info(f"       {reminder.description[:70]}...")
                logger.info()

        return [{
            'id': r.reminder_id,
            'type': r.reminder_type.value,
            'source': r.source.value,
            'title': r.title,
            'description': r.description
        } for r in reminders]

    def create_reminder(
        self,
        message: str,
        source: ReminderSource = ReminderSource.AI,
        reminder_type: ReminderType = ReminderType.DISCUSSION_POINT
    ):
        """Create a reminder"""
        if source == ReminderSource.AI:
            reminder = self.reminder_system.remind_you(message, source)
        else:
            reminder = self.reminder_system.remind_me(message, source)

        if self.current_session:
            self.current_session.reminders_created += 1

        return reminder

    def learn_from_interaction(
        self,
        ask_text: str,
        success: bool,
        context: str = ""
    ):
        """Learn from an interaction"""
        self.ask_processor.learn_pattern(ask_text, success, context)

        if self.current_session:
            self.current_session.patterns_learned += 1

    def update_performance(
        self,
        ai_performance: Optional[float] = None,
        human_performance: Optional[float] = None,
        collaborative_performance: Optional[float] = None
    ):
        """Update performance metrics"""
        self.ask_processor.update_performance(
            ai_performance=ai_performance,
            human_performance=human_performance,
            collaborative_performance=collaborative_performance
        )

        if self.current_session and collaborative_performance:
            self.current_session.performance_score = collaborative_performance

    def get_session_summary(self) -> Dict[str, Any]:
        """Get current session summary"""
        if not self.current_session:
            return {"status": "no_active_session"}

        return {
            "session_id": self.current_session.session_id,
            "started_at": self.current_session.started_at,
            "context": self.current_session.context.value,
            "mode": self.current_session.mode.value,
            "asks_processed": self.current_session.asks_processed,
            "reminders_created": self.current_session.reminders_created,
            "patterns_learned": self.current_session.patterns_learned,
            "performance_score": self.current_session.performance_score
        }

    def detect_missing_step(
        self,
        issue_description: str,
        workflow_name: Optional[str] = None
    ):
        """Detect and create reminder for missing step"""
        reminder = self.reminder_system.check_for_missing_steps(
            issue_description=issue_description,
            workflow_name=workflow_name
        )

        if reminder:
            logger.warning(f"⚠️  Missing step detected: {reminder.missing_step}")
            if self.current_session:
                self.current_session.reminders_created += 1

        return reminder


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Adaptive Collaboration System")
    parser.add_argument('--start', action='store_true', help='Start a new session')
    parser.add_argument('--context', type=str, help='Set context (review, execution, planning, discovery)')
    parser.add_argument('--activity', type=str, help='Describe current activity')
    parser.add_argument('--reminders', action='store_true', help='Check reminders')
    parser.add_argument('--summary', action='store_true', help='Show session summary')

    args = parser.parse_args()

    system = AdaptiveCollaborationSystem()

    if args.start:
        context = None
        if args.context:
            context_map = {
                'review': CollaborationContext.REVIEW,
                'execution': CollaborationContext.EXECUTION,
                'planning': CollaborationContext.PLANNING,
                'discovery': CollaborationContext.DISCOVERY
            }
            context = context_map.get(args.context.lower())

        session = system.start_session(context=context, activity=args.activity)
        print(f"✅ Session started: {session.session_id}")

    elif args.reminders:
        reminders = system.check_reminders()
        print(f"\n📋 Found {len(reminders)} active reminders")

    elif args.summary:
        summary = system.get_session_summary()
        print("\n📊 SESSION SUMMARY:")
        print("=" * 80)
        for key, value in summary.items():
            print(f"   {key}: {value}")

    else:
        print("🔄 Adaptive Collaboration System")
        print("\nUsage:")
        print("  --start              Start a new session")
        print("  --context CONTEXT    Set context")
        print("  --activity ACTIVITY  Describe activity")
        print("  --reminders          Check reminders")
        print("  --summary            Show session summary")


if __name__ == "__main__":


    main()