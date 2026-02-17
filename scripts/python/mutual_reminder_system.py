#!/usr/bin/env python3
"""
Mutual Reminder System - AI-Human Collaborative Reminders

Tracks partial completions, flags missing steps, prevents "forgot step 7" issues.
Both AI and human can remind each other of things we discussed/planned.

Tags: #REMINDERS #COLLABORATION #MUTUAL #STEP_TRACKING @JARVIS @LUMINA
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger

logger = get_logger("MutualReminderSystem")


class ReminderType(Enum):
    """Types of reminders"""
    PARTIAL_COMPLETION = "partial_completion"
    MISSING_STEP = "missing_step"
    FORGOTTEN_TASK = "forgotten_task"
    DISCUSSION_POINT = "discussion_point"
    PLANNED_ITEM = "planned_item"
    WORKFLOW_STEP = "workflow_step"


class ReminderSource(Enum):
    """Source of reminder"""
    AI = "ai"
    HUMAN = "human"
    SYSTEM = "system"


@dataclass
class Reminder:
    """Reminder item"""
    reminder_id: str
    reminder_type: ReminderType
    source: ReminderSource
    title: str
    description: str
    related_ask_id: Optional[str] = None
    related_todo_id: Optional[str] = None
    workflow_steps: List[str] = None
    missing_step: Optional[str] = None
    created_at: str = ""
    last_reminded: str = ""
    reminder_count: int = 0
    resolved: bool = False
    resolved_at: Optional[str] = None
    context: str = ""

    def __post_init__(self):
        if self.workflow_steps is None:
            self.workflow_steps = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class MutualReminderSystem:
    """
    Mutual Reminder System - AI-Human Collaborative Reminders

    Tracks what we discussed, what we planned, what we partially completed.
    Both AI and human can remind each other.
    Prevents "forgot step 7" issues by tracking workflow steps.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize mutual reminder system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.reminders_dir = self.data_dir / "mutual_reminders"
        self.reminders_dir.mkdir(parents=True, exist_ok=True)

        # Reminders storage
        self.reminders: List[Reminder] = []
        self.reminders_file = self.reminders_dir / "reminders.json"

        # Workflow tracking
        self.workflows: Dict[str, List[str]] = {}
        self.workflows_file = self.reminders_dir / "workflows.json"

        # Load existing data
        self._load_reminders()
        self._load_workflows()

        logger.info("=" * 80)
        logger.info("🔄 MUTUAL REMINDER SYSTEM INITIALIZED")
        logger.info(f"   Active reminders: {len([r for r in self.reminders if not r.resolved])}")
        logger.info("=" * 80)

    def _load_reminders(self):
        """Load reminders from file"""
        if self.reminders_file.exists():
            try:
                with open(self.reminders_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.reminders = [Reminder(**r) for r in data.get("reminders", [])]
                    logger.info(f"✅ Loaded {len(self.reminders)} reminders")
            except Exception as e:
                logger.warning(f"⚠️  Error loading reminders: {e}")

    def _save_reminders(self):
        """Save reminders to file"""
        try:
            with open(self.reminders_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "reminders": [asdict(r) for r in self.reminders],
                    "last_updated": datetime.now().isoformat(),
                    "total_reminders": len(self.reminders),
                    "active_reminders": len([r for r in self.reminders if not r.resolved])
                }, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            logger.warning(f"⚠️  Error saving reminders: {e}")

    def _load_workflows(self):
        """Load workflow definitions"""
        if self.workflows_file.exists():
            try:
                with open(self.workflows_file, 'r', encoding='utf-8') as f:
                    self.workflows = json.load(f)
                    logger.info(f"✅ Loaded {len(self.workflows)} workflows")
            except Exception as e:
                logger.warning(f"⚠️  Error loading workflows: {e}")

    def _save_workflows(self):
        """Save workflow definitions"""
        try:
            with open(self.workflows_file, 'w', encoding='utf-8') as f:
                json.dump(self.workflows, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"⚠️  Error saving workflows: {e}")

    def create_reminder(
        self,
        reminder_type: ReminderType,
        source: ReminderSource,
        title: str,
        description: str,
        related_ask_id: Optional[str] = None,
        related_todo_id: Optional[str] = None,
        missing_step: Optional[str] = None,
        context: str = ""
    ) -> Reminder:
        """
        Create a new reminder

        Args:
            reminder_type: Type of reminder
            source: Source (AI, human, or system)
            title: Reminder title
            description: Reminder description
            related_ask_id: Related ask ID if applicable
            related_todo_id: Related todo ID if applicable
            missing_step: Missing step if applicable
            context: Additional context

        Returns:
            Created reminder
        """
        reminder_id = f"reminder_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        reminder = Reminder(
            reminder_id=reminder_id,
            reminder_type=reminder_type,
            source=source,
            title=title,
            description=description,
            related_ask_id=related_ask_id,
            related_todo_id=related_todo_id,
            missing_step=missing_step,
            context=context
        )

        self.reminders.append(reminder)
        self._save_reminders()

        logger.info(f"📌 Reminder created: {title} ({source.value})")
        return reminder

    def remind_partial_completion(
        self,
        ask_id: str,
        ask_text: str,
        completed_steps: List[str],
        remaining_steps: List[str],
        source: ReminderSource = ReminderSource.SYSTEM
    ) -> Reminder:
        """Create reminder for partial completion"""
        title = f"Partial completion: {ask_text[:50]}..."
        description = (
            f"Ask '{ask_text}' is partially completed.\n"
            f"Completed: {', '.join(completed_steps)}\n"
            f"Remaining: {', '.join(remaining_steps)}"
        )

        reminder = self.create_reminder(
            reminder_type=ReminderType.PARTIAL_COMPLETION,
            source=source,
            title=title,
            description=description,
            related_ask_id=ask_id,
            workflow_steps=completed_steps + remaining_steps
        )

        return reminder

    def remind_missing_step(
        self,
        issue_description: str,
        missing_step: str,
        workflow_name: Optional[str] = None,
        source: ReminderSource = ReminderSource.SYSTEM
    ) -> Reminder:
        """Create reminder for missing step (e.g., 'forgot step 7')"""
        title = f"Missing step: {missing_step}"
        description = (
            f"Issue: {issue_description}\n"
            f"Missing step: {missing_step}\n"
            f"This is why we're hitting the same wall."
        )

        reminder = self.create_reminder(
            reminder_type=ReminderType.MISSING_STEP,
            source=source,
            title=title,
            description=description,
            missing_step=missing_step,
            context=workflow_name or ""
        )

        logger.warning(f"⚠️  Missing step detected: {missing_step}")
        return reminder

    def remind_discussion_point(
        self,
        topic: str,
        details: str,
        source: ReminderSource = ReminderSource.AI
    ) -> Reminder:
        """Create reminder for something we discussed"""
        reminder = self.create_reminder(
            reminder_type=ReminderType.DISCUSSION_POINT,
            source=source,
            title=f"Discussion: {topic}",
            description=details
        )
        return reminder

    def remind_planned_item(
        self,
        item: str,
        details: str,
        source: ReminderSource = ReminderSource.AI
    ) -> Reminder:
        """Create reminder for something we planned"""
        reminder = self.create_reminder(
            reminder_type=ReminderType.PLANNED_ITEM,
            source=source,
            title=f"Planned: {item}",
            description=details
        )
        return reminder

    def register_workflow(self, workflow_name: str, steps: List[str]):
        """Register a workflow with steps"""
        self.workflows[workflow_name] = steps
        self._save_workflows()
        logger.info(f"📋 Workflow registered: {workflow_name} ({len(steps)} steps)")

    def check_workflow_completion(
        self,
        workflow_name: str,
        completed_steps: List[str]
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if workflow is complete, return missing step if not

        Returns:
            (is_complete, missing_step)
        """
        if workflow_name not in self.workflows:
            return True, None

        workflow_steps = self.workflows[workflow_name]

        # Check if all steps are completed
        for step in workflow_steps:
            if step not in completed_steps:
                return False, step

        return True, None

    def get_active_reminders(
        self,
        reminder_type: Optional[ReminderType] = None,
        source: Optional[ReminderSource] = None,
        limit: int = 10
    ) -> List[Reminder]:
        """Get active (unresolved) reminders"""
        active = [r for r in self.reminders if not r.resolved]

        if reminder_type:
            active = [r for r in active if r.reminder_type == reminder_type]

        if source:
            active = [r for r in active if r.source == source]

        # Sort by creation date (oldest first)
        active.sort(key=lambda x: x.created_at)

        return active[:limit]

    def get_reminders_for_ask(self, ask_id: str) -> List[Reminder]:
        """Get all reminders related to a specific ask"""
        return [r for r in self.reminders if r.related_ask_id == ask_id]

    def resolve_reminder(self, reminder_id: str, resolved_by: str = "system"):
        """Mark reminder as resolved"""
        for reminder in self.reminders:
            if reminder.reminder_id == reminder_id:
                reminder.resolved = True
                reminder.resolved_at = datetime.now().isoformat()
                self._save_reminders()
                logger.info(f"✅ Reminder resolved: {reminder.title}")
                return

        logger.warning(f"⚠️  Reminder not found: {reminder_id}")

    def remind_me(self, message: str, source: ReminderSource = ReminderSource.HUMAN) -> Reminder:
        """
        Human can remind AI of something

        Args:
            message: Reminder message
            source: Source (default: human)

        Returns:
            Created reminder
        """
        reminder = self.create_reminder(
            reminder_type=ReminderType.DISCUSSION_POINT,
            source=source,
            title="Human reminder",
            description=message
        )
        logger.info(f"👤 Human reminder: {message[:50]}...")
        return reminder

    def remind_you(self, message: str, source: ReminderSource = ReminderSource.AI) -> Reminder:
        """
        AI can remind human of something

        Args:
            message: Reminder message
            source: Source (default: AI)

        Returns:
            Created reminder
        """
        reminder = self.create_reminder(
            reminder_type=ReminderType.DISCUSSION_POINT,
            source=source,
            title="AI reminder",
            description=message
        )
        logger.info(f"🤖 AI reminder: {message[:50]}...")
        return reminder

    def check_for_missing_steps(
        self,
        issue_description: str,
        workflow_name: Optional[str] = None
    ) -> Optional[Reminder]:
        """
        Check if we're hitting a wall due to missing steps

        Args:
            issue_description: Description of the issue
            workflow_name: Workflow name if applicable

        Returns:
            Reminder if missing step detected, None otherwise
        """
        # This would use pattern matching to detect "we forgot step X" patterns
        # For now, simple implementation

        if "forgot step" in issue_description.lower() or "missing step" in issue_description.lower():
            # Extract step number if possible
            import re
            step_match = re.search(r'step\s+(\d+)', issue_description.lower())
            missing_step = step_match.group(1) if step_match else "unknown"

            return self.remind_missing_step(
                issue_description=issue_description,
                missing_step=f"Step {missing_step}",
                workflow_name=workflow_name
            )

        return None


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Mutual Reminder System")
    parser.add_argument('--list', action='store_true', help='List active reminders')
    parser.add_argument('--type', type=str, help='Filter by reminder type')
    parser.add_argument('--source', type=str, help='Filter by source (ai, human, system)')
    parser.add_argument('--create', type=str, help='Create a reminder (message)')
    parser.add_argument('--resolve', type=str, help='Resolve a reminder (ID)')

    args = parser.parse_args()

    system = MutualReminderSystem()

    if args.list:
        reminder_type = ReminderType(args.type) if args.type else None
        source = ReminderSource(args.source) if args.source else None
        reminders = system.get_active_reminders(reminder_type, source)

        print("\n📋 ACTIVE REMINDERS:")
        print("=" * 80)
        for reminder in reminders:
            print(f"   [{reminder.reminder_id}] {reminder.title}")
            print(f"       Type: {reminder.reminder_type.value}, Source: {reminder.source.value}")
            print(f"       {reminder.description[:70]}...")
            print()

    elif args.create:
        system.remind_me(args.create)
        print(f"✅ Reminder created: {args.create}")

    elif args.resolve:
        system.resolve_reminder(args.resolve)
        print(f"✅ Reminder resolved: {args.resolve}")

    else:
        print("🔄 Mutual Reminder System")
        print("\nUsage:")
        print("  --list              List active reminders")
        print("  --create MESSAGE     Create a reminder")
        print("  --resolve ID        Resolve a reminder")


if __name__ == "__main__":


    main()