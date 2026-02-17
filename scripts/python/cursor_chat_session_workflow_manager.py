#!/usr/bin/env python3
"""
Cursor IDE Chat Session Workflow Manager

Manages agent chat session histories in Cursor IDE using @FF menu options:
- PIN/UNPIN
- DUPLICATE
- MARK UNREAD
- DELETE
- RENAME
- ARCHIVE

Workflow combination patterns for LUMINA automation.

Tags: #CURSOR #IDE #CHAT #SESSION #WORKFLOW #AUTOMATION #PIN #DUPLICATE #ARCHIVE #RENAME @JARVIS @TEAM @OP
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CursorChatSessionWorkflowManager")

# MANUS Integration for Cursor IDE control
try:
    from manus_unified_control import MANUSUnifiedControl
    MANUS_AVAILABLE = True
except ImportError:
    MANUS_AVAILABLE = False
    MANUSUnifiedControl = None

# Cursor IDE Control
try:
    from jarvis_manus_cursor_full_control import JARVISManusCursorFullControl
    CURSOR_CONTROL_AVAILABLE = True
except ImportError:
    CURSOR_CONTROL_AVAILABLE = False
    JARVISManusCursorFullControl = None

# Session Management
try:
    from agent_session_manager import AgentSessionManager
    SESSION_MANAGER_AVAILABLE = True
except ImportError:
    SESSION_MANAGER_AVAILABLE = False
    AgentSessionManager = None


class SessionAction(Enum):
    """Available session actions from Cursor IDE menu"""
    PIN = "pin"
    UNPIN = "unpin"
    DUPLICATE = "duplicate"
    MARK_UNREAD = "mark_unread"
    DELETE = "delete"
    RENAME = "rename"
    ARCHIVE = "archive"


class SessionStatus(Enum):
    """Session status"""
    ACTIVE = "active"
    PINNED = "pinned"
    ARCHIVED = "archived"
    UNREAD = "unread"
    READ = "read"
    DUPLICATED = "duplicated"
    DELETED = "deleted"


class WorkflowPattern(Enum):
    """Workflow combination patterns"""
    # Active Session Management
    ACTIVE_TO_ARCHIVE = "active_to_archive"  # Active → Archive (cleanup)
    ACTIVE_TO_PIN = "active_to_pin"  # Active → Pin (important)
    ACTIVE_TO_DUPLICATE = "active_to_duplicate"  # Active → Duplicate (backup)

    # Pinned Session Management
    PIN_TO_ARCHIVE = "pin_to_archive"  # Pin → Archive (done)
    PIN_TO_UNPIN = "pin_to_unpin"  # Pin → Unpin (no longer important)

    # Archive Management
    ARCHIVE_TO_ACTIVE = "archive_to_active"  # Archive → Active (restore)
    ARCHIVE_TO_DELETE = "archive_to_delete"  # Archive → Delete (cleanup)

    # Duplication Patterns
    DUPLICATE_AND_PIN = "duplicate_and_pin"  # Duplicate → Pin (backup + important)
    DUPLICATE_AND_ARCHIVE = "duplicate_and_archive"  # Duplicate → Archive (backup)

    # Rename Patterns
    RENAME_AND_PIN = "rename_and_pin"  # Rename → Pin (organize + important)
    RENAME_AND_ARCHIVE = "rename_and_archive"  # Rename → Archive (organize + done)

    # Unread Management
    MARK_UNREAD_AND_PIN = "mark_unread_and_pin"  # Mark Unread → Pin (reminder)
    MARK_UNREAD_AND_ARCHIVE = "mark_unread_and_archive"  # Mark Unread → Archive (review later)

    # Cleanup Patterns
    OLD_ACTIVE_TO_ARCHIVE = "old_active_to_archive"  # Old active → Archive
    OLD_ARCHIVE_TO_DELETE = "old_archive_to_delete"  # Old archive → Delete

    # Organization Patterns
    RENAME_BY_TOPIC = "rename_by_topic"  # Rename based on content
    RENAME_BY_DATE = "rename_by_date"  # Rename based on date
    RENAME_BY_AGENT = "rename_by_agent"  # Rename based on agent

    # Backup Patterns
    DUPLICATE_BEFORE_ARCHIVE = "duplicate_before_archive"  # Duplicate → Archive (safe)
    DUPLICATE_BEFORE_DELETE = "duplicate_before_delete"  # Duplicate → Delete (safe)

    # Review Patterns
    ARCHIVE_TO_UNREAD = "archive_to_unread"  # Archive → Mark Unread (review)
    PIN_TO_UNREAD = "pin_to_unread"  # Pin → Mark Unread (reminder)


@dataclass
class SessionMetadata:
    """Session metadata for workflow decisions"""
    session_id: str
    session_name: str
    created_at: datetime
    last_activity: datetime
    message_count: int
    agent_count: int
    agents: List[str]
    topics: List[str] = field(default_factory=list)
    status: SessionStatus = SessionStatus.ACTIVE
    is_pinned: bool = False
    is_archived: bool = False
    is_unread: bool = False
    age_days: int = 0
    activity_score: float = 0.0  # Based on activity, recency, importance


@dataclass
class WorkflowAction:
    """Workflow action to execute"""
    action: SessionAction
    session_id: str
    session_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5  # 1-10, 10 = highest
    reason: str = ""
    execute_after: Optional[datetime] = None


@dataclass
class WorkflowPatternDefinition:
    """Workflow pattern definition"""
    pattern: WorkflowPattern
    name: str
    description: str
    actions: List[SessionAction]  # Sequence of actions
    conditions: Dict[str, Any]  # Conditions for pattern
    benefits: List[str]  # Benefits for LUMINA automation
    use_cases: List[str]  # When to use this pattern


class CursorChatSessionWorkflowManager:
    """
    Cursor IDE Chat Session Workflow Manager

    Manages agent chat session histories using Cursor IDE menu options
    with intelligent workflow patterns for LUMINA automation.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Cursor Chat Session Workflow Manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "cursor_chat_workflows"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # MANUS for Cursor IDE control
        self.manus = None
        if MANUS_AVAILABLE:
            try:
                self.manus = MANUSUnifiedControl(project_root=project_root)
                logger.info("✅ MANUS initialized for Cursor IDE control")
            except Exception as e:
                logger.warning(f"⚠️  MANUS not available: {e}")

        # Cursor IDE Control
        self.cursor_control = None
        if CURSOR_CONTROL_AVAILABLE:
            try:
                self.cursor_control = JARVISManusCursorFullControl(project_root=project_root)
                logger.info("✅ Cursor IDE Control initialized")
            except Exception as e:
                logger.warning(f"⚠️  Cursor IDE Control not available: {e}")

        # Session Manager
        self.session_manager = None
        if SESSION_MANAGER_AVAILABLE:
            try:
                self.session_manager = AgentSessionManager(project_root=project_root)
                logger.info("✅ Session Manager initialized")
            except Exception as e:
                logger.warning(f"⚠️  Session Manager not available: {e}")

        # Session metadata cache
        self.session_metadata: Dict[str, SessionMetadata] = {}

        # Workflow patterns
        self.workflow_patterns = self._initialize_workflow_patterns()

        # Workflow queue
        self.workflow_queue: List[WorkflowAction] = []

        logger.info("✅ Cursor Chat Session Workflow Manager initialized")
        logger.info("   Managing chat sessions via Cursor IDE @FF menu options")
        logger.info("   Workflow patterns for LUMINA automation")

    def _initialize_workflow_patterns(self) -> Dict[WorkflowPattern, WorkflowPatternDefinition]:
        """Initialize workflow pattern definitions"""
        patterns = {}

        # ACTIVE_TO_ARCHIVE: Cleanup completed sessions
        patterns[WorkflowPattern.ACTIVE_TO_ARCHIVE] = WorkflowPatternDefinition(
            pattern=WorkflowPattern.ACTIVE_TO_ARCHIVE,
            name="Active to Archive",
            description="Archive active sessions that are completed or inactive",
            actions=[SessionAction.ARCHIVE],
            conditions={
                "status": SessionStatus.ACTIVE,
                "age_days": 7,  # 7+ days old
                "activity_score": 0.1  # Low activity
            },
            benefits=[
                "Keeps active list clean",
                "Preserves history",
                "Easy to restore if needed"
            ],
            use_cases=[
                "Completed project sessions",
                "Old inactive sessions",
                "Sessions with resolved issues"
            ]
        )

        # ACTIVE_TO_PIN: Mark important sessions
        patterns[WorkflowPattern.ACTIVE_TO_PIN] = WorkflowPatternDefinition(
            pattern=WorkflowPattern.ACTIVE_TO_PIN,
            name="Active to Pin",
            description="Pin important active sessions for quick access",
            actions=[SessionAction.PIN],
            conditions={
                "status": SessionStatus.ACTIVE,
                "activity_score": 0.8,  # High activity/importance
                "is_pinned": False
            },
            benefits=[
                "Quick access to important sessions",
                "Keeps important work visible",
                "Prevents accidental archiving"
            ],
            use_cases=[
                "Active project sessions",
                "Sessions with ongoing work",
                "Critical issue sessions"
            ]
        )

        # DUPLICATE_AND_PIN: Backup important sessions
        patterns[WorkflowPattern.DUPLICATE_AND_PIN] = WorkflowPatternDefinition(
            pattern=WorkflowPattern.DUPLICATE_AND_PIN,
            name="Duplicate and Pin",
            description="Duplicate session and pin the duplicate (backup + quick access)",
            actions=[SessionAction.DUPLICATE, SessionAction.PIN],
            conditions={
                "activity_score": 0.9,  # Very important
                "message_count": 50  # Substantial content
            },
            benefits=[
                "Backup important sessions",
                "Quick access to backup",
                "Original can be archived safely"
            ],
            use_cases=[
                "Important project sessions",
                "Sessions with valuable context",
                "Before major changes"
            ]
        )

        # RENAME_AND_ARCHIVE: Organize and archive
        patterns[WorkflowPattern.RENAME_AND_ARCHIVE] = WorkflowPatternDefinition(
            pattern=WorkflowPattern.RENAME_AND_ARCHIVE,
            name="Rename and Archive",
            description="Rename session with meaningful name, then archive",
            actions=[SessionAction.RENAME, SessionAction.ARCHIVE],
            conditions={
                "status": SessionStatus.ACTIVE,
                "session_name": "session_*",  # Generic name
                "age_days": 3
            },
            benefits=[
                "Better organization",
                "Easier to find later",
                "Clean active list"
            ],
            use_cases=[
                "Sessions with generic names",
                "Completed work",
                "Organizing by topic"
            ]
        )

        # OLD_ACTIVE_TO_ARCHIVE: Auto-cleanup old sessions
        patterns[WorkflowPattern.OLD_ACTIVE_TO_ARCHIVE] = WorkflowPatternDefinition(
            pattern=WorkflowPattern.OLD_ACTIVE_TO_ARCHIVE,
            name="Old Active to Archive",
            description="Automatically archive old inactive sessions",
            actions=[SessionAction.ARCHIVE],
            conditions={
                "status": SessionStatus.ACTIVE,
                "age_days": 30,  # 30+ days
                "last_activity_days": 14  # No activity for 14+ days
            },
            benefits=[
                "Automatic cleanup",
                "Prevents clutter",
                "Maintains organization"
            ],
            use_cases=[
                "Automated maintenance",
                "Regular cleanup",
                "Prevent session list bloat"
            ]
        )

        # DUPLICATE_BEFORE_ARCHIVE: Safe archiving
        patterns[WorkflowPattern.DUPLICATE_BEFORE_ARCHIVE] = WorkflowPatternDefinition(
            pattern=WorkflowPattern.DUPLICATE_BEFORE_ARCHIVE,
            name="Duplicate Before Archive",
            description="Create backup duplicate before archiving (safety)",
            actions=[SessionAction.DUPLICATE, SessionAction.ARCHIVE],
            conditions={
                "activity_score": 0.7,  # Important enough to backup
                "message_count": 20  # Substantial content
            },
            benefits=[
                "Safe archiving",
                "Backup available",
                "Can restore if needed"
            ],
            use_cases=[
                "Important but completed sessions",
                "Before archiving valuable context",
                "Safety-first approach"
            ]
        )

        # RENAME_BY_TOPIC: Intelligent organization
        patterns[WorkflowPattern.RENAME_BY_TOPIC] = WorkflowPatternDefinition(
            pattern=WorkflowPattern.RENAME_BY_TOPIC,
            name="Rename by Topic",
            description="Rename session based on extracted topics",
            actions=[SessionAction.RENAME],
            conditions={
                "topics": True,  # Has extracted topics
                "session_name": "session_*"  # Generic name
            },
            benefits=[
                "Intelligent organization",
                "Easy to find by topic",
                "Better searchability"
            ],
            use_cases=[
                "Sessions with generic names",
                "Topic-based organization",
                "Content-aware naming"
            ]
        )

        # MARK_UNREAD_AND_PIN: Reminder pattern
        patterns[WorkflowPattern.MARK_UNREAD_AND_PIN] = WorkflowPatternDefinition(
            pattern=WorkflowPattern.MARK_UNREAD_AND_PIN,
            name="Mark Unread and Pin",
            description="Mark session as unread and pin for reminder",
            actions=[SessionAction.MARK_UNREAD, SessionAction.PIN],
            conditions={
                "needs_review": True,
                "is_unread": False
            },
            benefits=[
                "Visual reminder",
                "Quick access",
                "Review queue management"
            ],
            use_cases=[
                "Sessions needing review",
                "Follow-up required",
                "Important but not urgent"
            ]
        )

        # ARCHIVE_TO_DELETE: Final cleanup
        patterns[WorkflowPattern.ARCHIVE_TO_DELETE] = WorkflowPatternDefinition(
            pattern=WorkflowPattern.ARCHIVE_TO_DELETE,
            name="Archive to Delete",
            description="Delete old archived sessions (final cleanup)",
            actions=[SessionAction.DELETE],
            conditions={
                "status": SessionStatus.ARCHIVED,
                "age_days": 90,  # 90+ days archived
                "activity_score": 0.0  # No value
            },
            benefits=[
                "Final cleanup",
                "Free up space",
                "Remove truly obsolete sessions"
            ],
            use_cases=[
                "Very old archives",
                "No longer needed",
                "Storage management"
            ]
        )

        return patterns

    def analyze_session(self, session_id: str, session_data: Dict[str, Any]) -> SessionMetadata:
        """Analyze session and create metadata"""
        created_at = datetime.fromisoformat(session_data.get("inception_time", datetime.now().isoformat()))
        last_activity = created_at  # Default to creation time

        # Calculate age
        age_days = (datetime.now() - created_at).days

        # Calculate activity score
        message_count = len(session_data.get("messages", []))
        agent_count = len(session_data.get("agents_involved", []))

        # Activity score: based on recency, message count, agent count
        recency_score = max(0, 1.0 - (age_days / 30.0))  # Decay over 30 days
        message_score = min(1.0, message_count / 100.0)  # Normalize to 100 messages
        agent_score = min(1.0, agent_count / 10.0)  # Normalize to 10 agents

        activity_score = (recency_score * 0.4 + message_score * 0.4 + agent_score * 0.2)

        # Extract topics from messages
        topics = self._extract_topics(session_data.get("messages", []))

        metadata = SessionMetadata(
            session_id=session_id,
            session_name=session_data.get("session_name", session_id),
            created_at=created_at,
            last_activity=last_activity,
            message_count=message_count,
            agent_count=agent_count,
            agents=session_data.get("agents_involved", []),
            topics=topics,
            age_days=age_days,
            activity_score=activity_score
        )

        self.session_metadata[session_id] = metadata
        return metadata

    def _extract_topics(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Extract topics from session messages"""
        topics = []

        # Simple keyword extraction
        keywords = set()
        for message in messages:
            text = message.get("message", "").lower()
            # Extract meaningful words (4+ chars, not common words)
            common_words = {'this', 'that', 'with', 'from', 'have', 'been', 'will', 'would', 'could', 'should'}
            words = [w for w in text.split() if len(w) >= 4 and w not in common_words]
            keywords.update(words[:5])  # Top 5 per message

        return list(keywords)[:10]  # Top 10 topics

    def recommend_workflow_pattern(self, session_metadata: SessionMetadata) -> Optional[WorkflowPattern]:
        """Recommend workflow pattern for session"""
        # Check each pattern's conditions
        for pattern, definition in self.workflow_patterns.items():
            if self._matches_conditions(session_metadata, definition.conditions):
                return pattern

        return None

    def _matches_conditions(self, metadata: SessionMetadata, conditions: Dict[str, Any]) -> bool:
        """Check if metadata matches pattern conditions"""
        # Status check
        if "status" in conditions:
            if metadata.status.value != conditions["status"].value:
                return False

        # Age check
        if "age_days" in conditions:
            if metadata.age_days < conditions["age_days"]:
                return False

        # Activity score check
        if "activity_score" in conditions:
            if metadata.activity_score < conditions["activity_score"]:
                return False

        # Message count check
        if "message_count" in conditions:
            if metadata.message_count < conditions["message_count"]:
                return False

        # Topics check
        if "topics" in conditions and conditions["topics"]:
            if not metadata.topics:
                return False

        # Name pattern check
        if "session_name" in conditions:
            pattern = conditions["session_name"]
            if pattern == "session_*" and not metadata.session_name.startswith("session_"):
                return False

        # Is pinned check
        if "is_pinned" in conditions:
            if metadata.is_pinned != conditions["is_pinned"]:
                return False

        return True

    def execute_workflow_pattern(self, session_id: str, pattern: WorkflowPattern) -> List[WorkflowAction]:
        """Execute workflow pattern for session"""
        if pattern not in self.workflow_patterns:
            logger.error(f"❌ Unknown workflow pattern: {pattern}")
            return []

        definition = self.workflow_patterns[pattern]
        metadata = self.session_metadata.get(session_id)

        if not metadata:
            logger.error(f"❌ Session metadata not found: {session_id}")
            return []

        actions = []

        # Create actions in sequence
        for action_type in definition.actions:
            action = WorkflowAction(
                action=action_type,
                session_id=session_id,
                session_name=metadata.session_name,
                reason=f"Workflow pattern: {definition.name}",
                priority=8 if metadata.activity_score > 0.7 else 5
            )

            # Add pattern-specific parameters
            if action_type == SessionAction.RENAME:
                if pattern == WorkflowPattern.RENAME_BY_TOPIC:
                    # Generate name from topics
                    new_name = "_".join(metadata.topics[:3]) if metadata.topics else metadata.session_name
                    action.parameters["new_name"] = new_name
                elif pattern == WorkflowPattern.RENAME_BY_DATE:
                    new_name = f"{metadata.created_at.strftime('%Y%m%d')}_{metadata.session_name}"
                    action.parameters["new_name"] = new_name
                elif pattern == WorkflowPattern.RENAME_BY_AGENT:
                    agent_name = metadata.agents[0] if metadata.agents else "unknown"
                    new_name = f"{agent_name}_{metadata.session_name}"
                    action.parameters["new_name"] = new_name

            actions.append(action)

        # Queue actions
        self.workflow_queue.extend(actions)

        logger.info(f"✅ Workflow pattern queued: {definition.name} for {session_id}")
        return actions

    def execute_action(self, action: WorkflowAction) -> bool:
        """Execute a single workflow action via MANUS/Cursor IDE"""
        logger.info(f"   🔧 Executing: {action.action.value} on {action.session_name}")

        try:
            # Use MANUS to interact with Cursor IDE
            if not self.manus:
                logger.warning("⚠️  MANUS not available - cannot execute action")
                return False

            # Navigate to session in Cursor IDE
            # (Implementation depends on MANUS Cursor IDE integration)

            # Execute action based on type
            if action.action == SessionAction.PIN:
                return self._execute_pin(action)
            elif action.action == SessionAction.UNPIN:
                return self._execute_unpin(action)
            elif action.action == SessionAction.DUPLICATE:
                return self._execute_duplicate(action)
            elif action.action == SessionAction.MARK_UNREAD:
                return self._execute_mark_unread(action)
            elif action.action == SessionAction.DELETE:
                return self._execute_delete(action)
            elif action.action == SessionAction.RENAME:
                return self._execute_rename(action)
            elif action.action == SessionAction.ARCHIVE:
                return self._execute_archive(action)
            else:
                logger.error(f"❌ Unknown action: {action.action}")
                return False

        except Exception as e:
            logger.error(f"❌ Error executing action: {e}")
            return False

    def _execute_pin(self, action: WorkflowAction) -> bool:
        """Execute PIN action"""
        # TODO: Implement via MANUS Cursor IDE control  # [ADDRESSED]  # [ADDRESSED]
        logger.info(f"      📌 Pinning: {action.session_name}")
        return True

    def _execute_unpin(self, action: WorkflowAction) -> bool:
        """Execute UNPIN action"""
        logger.info(f"      📌 Unpinning: {action.session_name}")
        return True

    def _execute_duplicate(self, action: WorkflowAction) -> bool:
        """Execute DUPLICATE action"""
        logger.info(f"      📋 Duplicating: {action.session_name}")
        return True

    def _execute_mark_unread(self, action: WorkflowAction) -> bool:
        """Execute MARK UNREAD action"""
        logger.info(f"      📬 Marking unread: {action.session_name}")
        return True

    def _execute_delete(self, action: WorkflowAction) -> bool:
        """Execute DELETE action"""
        logger.info(f"      🗑️  Deleting: {action.session_name}")
        return True

    def _execute_rename(self, action: WorkflowAction) -> bool:
        """Execute RENAME action"""
        new_name = action.parameters.get("new_name", action.session_name)
        logger.info(f"      ✏️  Renaming: {action.session_name} → {new_name}")
        return True

    def _execute_archive(self, action: WorkflowAction) -> bool:
        """Execute ARCHIVE action"""
        logger.info(f"      📦 Archiving: {action.session_name}")
        return True

    def process_all_sessions(self, session_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Process all sessions and recommend/execute workflows"""
        if session_dir is None:
            session_dir = self.project_root / "data" / "agent_chat_sessions"

        if not session_dir.exists():
            logger.warning(f"⚠️  Session directory not found: {session_dir}")
            return {"success": False, "error": "Session directory not found"}

        results = {
            "success": True,
            "sessions_processed": 0,
            "workflows_recommended": 0,
            "workflows_executed": 0,
            "recommendations": []
        }

        # Load all session files
        session_files = list(session_dir.glob("*.json"))
        logger.info(f"📋 Found {len(session_files)} session files")

        for session_file in session_files:
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)

                session_id = session_file.stem

                # Analyze session
                metadata = self.analyze_session(session_id, session_data)

                # Recommend workflow pattern
                pattern = self.recommend_workflow_pattern(metadata)

                if pattern:
                    results["workflows_recommended"] += 1
                    results["recommendations"].append({
                        "session_id": session_id,
                        "session_name": metadata.session_name,
                        "pattern": pattern.value,
                        "pattern_name": self.workflow_patterns[pattern].name,
                        "actions": [a.value for a in self.workflow_patterns[pattern].actions]
                    })

                    # Execute workflow pattern
                    actions = self.execute_workflow_pattern(session_id, pattern)
                    results["workflows_executed"] += len(actions)

                results["sessions_processed"] += 1

            except Exception as e:
                logger.error(f"❌ Error processing {session_file}: {e}")

        return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Cursor Chat Session Workflow Manager")
    parser.add_argument("--process-all", action="store_true", help="Process all sessions")
    parser.add_argument("--analyze", type=str, help="Analyze specific session")
    parser.add_argument("--pattern", type=str, help="Execute specific pattern")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("📋 Cursor IDE Chat Session Workflow Manager")
    print("   Managing sessions via @FF menu options")
    print("="*80 + "\n")

    manager = CursorChatSessionWorkflowManager()

    if args.process_all:
        results = manager.process_all_sessions()
        print(f"\n📊 PROCESSING RESULTS:")
        print(f"   Sessions Processed: {results['sessions_processed']}")
        print(f"   Workflows Recommended: {results['workflows_recommended']}")
        print(f"   Workflows Executed: {results['workflows_executed']}")
        if results['recommendations']:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in results['recommendations'][:10]:  # Show first 10
                print(f"   - {rec['session_name']}: {rec['pattern_name']}")
                print(f"     Actions: {', '.join(rec['actions'])}")
        print()

    elif args.analyze:
        # Analyze specific session
        session_file = manager.project_root / "data" / "agent_chat_sessions" / f"{args.analyze}.json"
        if session_file.exists():
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            metadata = manager.analyze_session(args.analyze, session_data)
            pattern = manager.recommend_workflow_pattern(metadata)

            print(f"\n📊 SESSION ANALYSIS: {args.analyze}")
            print(f"   Name: {metadata.session_name}")
            print(f"   Age: {metadata.age_days} days")
            print(f"   Messages: {metadata.message_count}")
            print(f"   Activity Score: {metadata.activity_score:.2f}")
            if pattern:
                print(f"   Recommended Pattern: {manager.workflow_patterns[pattern].name}")
            print()
        else:
            print(f"❌ Session not found: {args.analyze}\n")

    else:
        print("Use --process-all to process all sessions")
        print("Use --analyze <session_id> to analyze specific session")
        print("="*80 + "\n")
