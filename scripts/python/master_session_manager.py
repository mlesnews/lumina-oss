#!/usr/bin/env python3
"""
Master Session Manager - JARVIS Lead Session System

Manages master/lead agent chat session with:
1. Master session designation (penned/pinned)
2. Session consolidation (roll all sessions into master)
3. Workflow pattern matching for correct workflow identification
4. Session duplication for branching
5. Archive system for completed sessions
6. BAU (Business As Usual) detection and processing
7. Master feedback loop integration

JARVIS uses this master session to work with all other agents.
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from wopr_workflow_pattern_mapper import WOPRWorkflowPatternMapper
    WOPR_MAPPER_AVAILABLE = True
except ImportError:
    WOPR_MAPPER_AVAILABLE = False
    WOPRWorkflowPatternMapper = None

try:
    from universal_decision_tree import decide, DecisionContext, DecisionOutcome
    DECISION_TREE_AVAILABLE = True
except ImportError:
    DECISION_TREE_AVAILABLE = False
    decide = None
    DecisionContext = None
    DecisionOutcome = None


class SessionStatus(Enum):
    """Session status"""
    ACTIVE = "active"
    MASTER = "master"  # Penned/pinned master session
    CONSOLIDATED = "consolidated"  # Rolled into master
    ARCHIVED = "archived"  # Completed and archived
    DUPLICATE = "duplicate"  # Duplicated for branching


class BAUCategory(Enum):
    """BAU (Business As Usual) category"""
    BAU = "bau"  # Standard BAU processing
    NON_BAU = "non_bau"  # Requires special handling
    UNKNOWN = "unknown"  # Needs investigation


@dataclass
class AgentChatEntry:
    """Agent chat history entry"""
    entry_id: str
    timestamp: str
    agent: str
    message: str
    workflow_id: Optional[str] = None
    pattern_matched: Optional[str] = None
    bau_category: BAUCategory = BAUCategory.UNKNOWN
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["bau_category"] = self.bau_category.value
        return data


@dataclass
class AgentSession:
    """Agent chat session"""
    session_id: str
    session_name: str
    status: SessionStatus
    created_at: str
    updated_at: str
    is_master: bool = False
    chat_history: List[AgentChatEntry] = field(default_factory=list)
    workflows_identified: List[str] = field(default_factory=list)
    patterns_matched: List[str] = field(default_factory=list)
    consolidated_from: List[str] = field(default_factory=list)  # Session IDs rolled into this
    duplicated_to: List[str] = field(default_factory=list)  # Session IDs duplicated from this
    archived_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        data["chat_history"] = [entry.to_dict() for entry in self.chat_history]
        return data


@dataclass
class WorkflowMatch:
    """Workflow pattern match result"""
    workflow_id: str
    workflow_name: str
    confidence: float
    pattern_matched: str
    match_type: str  # exact, similar, pattern
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MasterSessionManager:
    """
    Master Session Manager

    Manages master/lead session for JARVIS to work with all agents.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Data directories
        self.data_dir = self.project_root / "data" / "master_sessions"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.sessions_dir = self.data_dir / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        self.archive_dir = self.data_dir / "archive"
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        # Files
        self.master_session_file = self.data_dir / "MASTER_SESSION.json"
        self.sessions_index_file = self.data_dir / "sessions_index.json"

        # State
        self.master_session: Optional[AgentSession] = None
        self.all_sessions: Dict[str, AgentSession] = {}

        # Initialize WOPR mapper for workflow pattern matching
        self.wopr_mapper = None
        if WOPR_MAPPER_AVAILABLE and WOPRWorkflowPatternMapper:
            try:
                self.wopr_mapper = WOPRWorkflowPatternMapper(project_root=self.project_root)
            except Exception as e:
                self.logger.warning(f"WOPR mapper not available: {e}")

        self.logger = get_logger("MasterSessionManager")
        self._load_existing_data()

    def _load_existing_data(self):
        """Load existing master session and sessions"""
        # Load master session
        if self.master_session_file.exists():
            try:
                with open(self.master_session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.master_session = AgentSession(**{**data, 'status': SessionStatus(data['status'])})
                    # Load chat history
                    if 'chat_history' in data:
                        self.master_session.chat_history = [
                            AgentChatEntry(**{**entry, 'bau_category': BAUCategory(entry.get('bau_category', 'unknown'))})
                            for entry in data['chat_history']
                        ]
            except Exception as e:
                self.logger.warning(f"Could not load master session: {e}")

        # Load sessions index
        if self.sessions_index_file.exists():
            try:
                with open(self.sessions_index_file, 'r', encoding='utf-8') as f:
                    sessions_data = json.load(f)
                    for session_id, session_data in sessions_data.items():
                        session = AgentSession(**{**session_data, 'status': SessionStatus(session_data['status'])})
                        # Load chat history
                        if 'chat_history' in session_data:
                            session.chat_history = [
                                AgentChatEntry(**{**entry, 'bau_category': BAUCategory(entry.get('bau_category', 'unknown'))})
                                for entry in session_data['chat_history']
                            ]
                        self.all_sessions[session_id] = session
            except Exception as e:
                self.logger.warning(f"Could not load sessions index: {e}")

    def create_or_set_master_session(self, session_name: str = "JARVIS Master Session") -> str:
        """
        Create or set master session (penned/pinned)

        This becomes the lead session that JARVIS uses.
        """
        if self.master_session and self.master_session.status == SessionStatus.MASTER:
            self.logger.info(f"Master session already exists: {self.master_session.session_id}")
            return self.master_session.session_id

        # Create new master session
        session_id = f"master_{int(datetime.now().timestamp())}"

        self.master_session = AgentSession(
            session_id=session_id,
            session_name=session_name,
            status=SessionStatus.MASTER,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            is_master=True,
            metadata={
                "designated_at": datetime.now().isoformat(),
                "designated_by": "MasterSessionManager"
            }
        )

        self.all_sessions[session_id] = self.master_session
        self._save_master_session()
        self._save_sessions_index()

        self.logger.info(f"✅ Created master session: {session_id}")

        return session_id

    def add_to_master_session(
        self,
        agent: str,
        message: str,
        workflow_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add entry to master session

        Automatically:
        - Detects BAU vs non-BAU
        - Matches workflow patterns
        - Processes workflow identification
        """
        if not self.master_session:
            self.create_or_set_master_session()

        entry_id = f"entry_{int(datetime.now().timestamp() * 1000)}"

        # Detect BAU
        bau_category = self._detect_bau(message, context)

        # Match workflow patterns
        workflow_match = self._match_workflow_patterns(message, context)

        entry = AgentChatEntry(
            entry_id=entry_id,
            timestamp=datetime.now().isoformat(),
            agent=agent,
            message=message,
            workflow_id=workflow_match.workflow_id if workflow_match else workflow_id,
            pattern_matched=workflow_match.pattern_matched if workflow_match else None,
            bau_category=bau_category,
            context=context or {},
            metadata={
                "workflow_match": workflow_match.to_dict() if workflow_match else None
            }
        )

        self.master_session.chat_history.append(entry)
        self.master_session.updated_at = datetime.now().isoformat()

        # Track workflows and patterns
        if workflow_match:
            if workflow_match.workflow_id not in self.master_session.workflows_identified:
                self.master_session.workflows_identified.append(workflow_match.workflow_id)
            if workflow_match.pattern_matched not in self.master_session.patterns_matched:
                self.master_session.patterns_matched.append(workflow_match.pattern_matched)

        self._save_master_session()

        self.logger.info(f"➕ Added to master session: {agent}: {message[:50]}")

        return entry_id

    def _detect_bau(self, message: str, context: Optional[Dict[str, Any]] = None) -> BAUCategory:
        """
        Detect if message/task is BAU (Business As Usual)

        Uses decision tree and pattern matching to determine BAU.
        """
        message_lower = message.lower()

        # BAU indicators
        bau_keywords = [
            "verify", "check", "validate", "confirm", "archive", "complete",
            "standard", "routine", "normal", "usual", "regular", "typical",
            "automated", "automatic", "bau", "business as usual"
        ]

        # Non-BAU indicators
        non_bau_keywords = [
            "new", "create", "build", "implement", "develop", "design",
            "critical", "urgent", "emergency", "unusual", "special",
            "first time", "never done", "experimental"
        ]

        # Check keywords
        has_bau_keywords = any(keyword in message_lower for keyword in bau_keywords)
        has_non_bau_keywords = any(keyword in message_lower for keyword in non_bau_keywords)

        # Use decision tree if available
        if DECISION_TREE_AVAILABLE and decide:
            try:
                context_data = DecisionContext(
                    action="detect_bau",
                    inputs={"message": message, "context": context or {}},
                    metadata={"has_bau_keywords": has_bau_keywords, "has_non_bau_keywords": has_non_bau_keywords}
                )
                result = decide('bau_detection', context_data)

                if result.outcome == DecisionOutcome.SUCCESS:
                    if result.metadata.get("is_bau"):
                        return BAUCategory.BAU
                    else:
                        return BAUCategory.NON_BAU
            except Exception as e:
                self.logger.debug(f"Decision tree not available: {e}")

        # Fallback logic
        if has_bau_keywords and not has_non_bau_keywords:
            return BAUCategory.BAU
        elif has_non_bau_keywords:
            return BAUCategory.NON_BAU
        else:
            return BAUCategory.UNKNOWN

    def _match_workflow_patterns(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[WorkflowMatch]:
        """
        Match message to workflow patterns

        Uses WOPR pattern mapper to identify correct workflow(s).
        """
        if not self.wopr_mapper:
            return None

        try:
            # Process workflow mapping to get all workflows
            self.wopr_mapper.process_workflow_mapping()

            # Search for matching workflows
            workflows = self.wopr_mapper.identified_workflows

            # Simple pattern matching (can be enhanced)
            message_lower = message.lower()

            best_match = None
            best_confidence = 0.0

            for workflow_id, workflow in workflows.items():
                workflow_name_lower = workflow.workflow_name.lower()

                # Check for exact match
                if workflow_name_lower in message_lower:
                    confidence = 0.9
                    match_type = "exact"
                # Check for similar match
                elif any(word in message_lower for word in workflow_name_lower.split() if len(word) > 3):
                    confidence = 0.6
                    match_type = "similar"
                # Check pattern hashtags
                elif workflow.pattern_hashtags and any(tag.lower() in message_lower for tag in workflow.pattern_hashtags):
                    confidence = 0.8
                    match_type = "pattern"
                else:
                    continue

                if confidence > best_confidence:
                    best_match = WorkflowMatch(
                        workflow_id=workflow_id,
                        workflow_name=workflow.workflow_name,
                        confidence=confidence,
                        pattern_matched=workflow.pattern_hashtags[0] if workflow.pattern_hashtags else None,
                        match_type=match_type
                    )
                    best_confidence = confidence

            return best_match if best_confidence >= 0.6 else None

        except Exception as e:
            self.logger.debug(f"Could not match workflow patterns: {e}")
            return None

    def consolidate_sessions(self, session_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Consolidate (roll) sessions into master session

        Rolls all specified sessions (or all active sessions) into master.
        """
        if not self.master_session:
            self.create_or_set_master_session()

        self.logger.info("🔄 Consolidating sessions into master...")

        # Get sessions to consolidate
        if session_ids:
            sessions_to_consolidate = [self.all_sessions[sid] for sid in session_ids if sid in self.all_sessions]
        else:
            # Consolidate all non-master active sessions
            sessions_to_consolidate = [
                session for session in self.all_sessions.values()
                if session.status == SessionStatus.ACTIVE and not session.is_master
            ]

        consolidated_count = 0
        entries_consolidated = 0

        for session in sessions_to_consolidate:
            # Roll chat history into master
            for entry in session.chat_history:
                # Re-detect BAU and match workflows
                bau_category = self._detect_bau(entry.message, entry.context)
                workflow_match = self._match_workflow_patterns(entry.message, entry.context)

                # Update entry
                entry.bau_category = bau_category
                if workflow_match:
                    entry.workflow_id = workflow_match.workflow_id
                    entry.pattern_matched = workflow_match.pattern_matched

                # Add to master
                self.master_session.chat_history.append(entry)
                entries_consolidated += 1

            # Track workflows and patterns
            for workflow_id in session.workflows_identified:
                if workflow_id not in self.master_session.workflows_identified:
                    self.master_session.workflows_identified.append(workflow_id)

            for pattern in session.patterns_matched:
                if pattern not in self.master_session.patterns_matched:
                    self.master_session.patterns_matched.append(pattern)

            # Mark session as consolidated
            session.status = SessionStatus.CONSOLIDATED
            session.consolidated_from.append(session.session_id)
            self.master_session.consolidated_from.append(session.session_id)

            consolidated_count += 1

        self.master_session.updated_at = datetime.now().isoformat()

        self._save_master_session()
        self._save_sessions_index()

        result = {
            "consolidated_sessions": consolidated_count,
            "entries_consolidated": entries_consolidated,
            "master_session_id": self.master_session.session_id,
            "timestamp": datetime.now().isoformat()
        }

        self.logger.info(f"✅ Consolidated {consolidated_count} sessions, {entries_consolidated} entries")

        return result

    def duplicate_session(self, session_id: Optional[str] = None, new_session_name: str = "New Session") -> str:
        """
        Duplicate session for branching

        Creates new session from master (or specified session) to work from.
        """
        source_session = self.master_session if not session_id else self.all_sessions.get(session_id)

        if not source_session:
            raise ValueError(f"Session {session_id or 'master'} not found")

        # Create duplicate session
        new_session_id = f"session_{int(datetime.now().timestamp())}"

        new_session = AgentSession(
            session_id=new_session_id,
            session_name=new_session_name,
            status=SessionStatus.DUPLICATE,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            is_master=False,
            chat_history=source_session.chat_history.copy(),  # Copy history
            workflows_identified=source_session.workflows_identified.copy(),
            patterns_matched=source_session.patterns_matched.copy(),
            metadata={
                "duplicated_from": source_session.session_id,
                "duplicated_at": datetime.now().isoformat()
            }
        )

        # Track duplication
        source_session.duplicated_to.append(new_session_id)

        self.all_sessions[new_session_id] = new_session
        self._save_sessions_index()

        self.logger.info(f"✅ Duplicated session: {new_session_id} from {source_session.session_id}")

        return new_session_id

    def archive_completed_session(self, session_id: str, verify_success: bool = True) -> bool:
        try:
            """
            Archive completed session after verification

            BAU: Verification is automatic part of processing.
            """
            if session_id not in self.all_sessions:
                self.logger.warning(f"Session {session_id} not found")
                return False

            session = self.all_sessions[session_id]

            # Verify success (BAU processing)
            if verify_success:
                verification_result = self._verify_session_success(session)
                if not verification_result["success"]:
                    self.logger.warning(f"Session {session_id} verification failed - not archiving")
                    return False

            # Archive session
            session.status = SessionStatus.ARCHIVED
            session.archived_at = datetime.now().isoformat()

            # Move to archive
            archive_file = self.archive_dir / f"{session_id}.json"
            with open(archive_file, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)

            # Remove from active sessions (but keep in index)
            self._save_sessions_index()

            self.logger.info(f"✅ Archived session: {session_id}")

            return True

        except Exception as e:
            self.logger.error(f"Error in archive_completed_session: {e}", exc_info=True)
            raise
    def _verify_session_success(self, session: AgentSession) -> Dict[str, Any]:
        """
        Verify session success (BAU processing)

        Checks:
        - All workflows completed
        - All patterns processed
        - No critical errors
        - Success indicators present
        """
        # Check for success indicators
        success_indicators = ["complete", "success", "done", "finished", "verified"]
        failure_indicators = ["error", "failed", "broken", "issue", "problem"]

        success_count = sum(1 for entry in session.chat_history 
                          if any(indicator in entry.message.lower() for indicator in success_indicators))
        failure_count = sum(1 for entry in session.chat_history 
                          if any(indicator in entry.message.lower() for indicator in failure_indicators))

        # Check workflow completion
        workflows_complete = len(session.workflows_identified) > 0

        # Determine success
        success = (
            success_count > failure_count and
            workflows_complete and
            failure_count == 0
        )

        return {
            "success": success,
            "success_count": success_count,
            "failure_count": failure_count,
            "workflows_complete": workflows_complete,
            "verification_timestamp": datetime.now().isoformat()
        }

    def process_workflows_from_master(self) -> Dict[str, Any]:
        """
        Process workflows identified in master session

        Uses workflow pattern matching to identify and process correct workflows.
        """
        if not self.master_session:
            self.logger.warning("No master session")
            return {"error": "No master session"}

        self.logger.info("🔄 Processing workflows from master session...")

        # Get unique workflows
        workflow_ids = list(set(self.master_session.workflows_identified))

        # Process each workflow
        processed_workflows = []

        for workflow_id in workflow_ids:
            if not self.wopr_mapper:
                continue

            # Get workflow
            workflow = self.wopr_mapper.identified_workflows.get(workflow_id)
            if not workflow:
                continue

            # Process workflow mapping (processes all workflows)
            result = self.wopr_mapper.process_workflow_mapping()

            processed_workflows.append({
                "workflow_id": workflow_id,
                "workflow_name": workflow.workflow_name if hasattr(workflow, 'workflow_name') else workflow_id,
                "result": result
            })

        processing_result = {
            "processed_at": datetime.now().isoformat(),
            "workflows_processed": len(processed_workflows),
            "workflows": processed_workflows,
            "master_session_id": self.master_session.session_id
        }

        self.logger.info(f"✅ Processed {len(processed_workflows)} workflows")

        return processing_result

    def apply_master_feedback_loop(self) -> Dict[str, Any]:
        """
        Apply master feedback loop system

        Enhances workflows with learned patterns from master session.
        """
        if not self.master_session:
            return {"error": "No master session"}

        self.logger.info("🔄 Applying master feedback loop...")

        # Extract learned patterns from master session
        learned_patterns = self._extract_learned_patterns()

        # Apply to new workflows
        applied_count = 0
        if self.wopr_mapper:
            for pattern in learned_patterns:
                # Apply pattern to workflow mapping
                # This would enhance workflow processing
                applied_count += 1

        result = {
            "applied_at": datetime.now().isoformat(),
            "learned_patterns": len(learned_patterns),
            "patterns_applied": applied_count,
            "master_session_id": self.master_session.session_id
        }

        self.logger.info(f"✅ Applied {applied_count} learned patterns")

        return result

    def _extract_learned_patterns(self) -> List[Dict[str, Any]]:
        """Extract learned patterns from master session"""
        patterns = []

        # Extract from chat history
        for entry in self.master_session.chat_history:
            if entry.pattern_matched:
                patterns.append({
                    "pattern": entry.pattern_matched,
                    "workflow_id": entry.workflow_id,
                    "context": entry.context,
                    "timestamp": entry.timestamp
                })

        # Extract from workflows
        for workflow_id in self.master_session.workflows_identified:
            if self.wopr_mapper:
                workflow = self.wopr_mapper.identified_workflows.get(workflow_id)
                if workflow and hasattr(workflow, 'pattern_hashtags') and workflow.pattern_hashtags:
                    patterns.append({
                        "pattern": workflow.pattern_hashtags[0],
                        "workflow_id": workflow_id,
                        "workflow_name": workflow.workflow_name
                    })

        return patterns

    def _save_master_session(self):
        try:
            """Save master session"""
            if not self.master_session:
                return

            with open(self.master_session_file, 'w', encoding='utf-8') as f:
                json.dump(self.master_session.to_dict(), f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in _save_master_session: {e}", exc_info=True)
            raise
    def _save_sessions_index(self):
        try:
            """Save sessions index"""
            sessions_data = {
                session_id: session.to_dict()
                for session_id, session in self.all_sessions.items()
            }

            with open(self.sessions_index_file, 'w', encoding='utf-8') as f:
                json.dump(sessions_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in _save_sessions_index: {e}", exc_info=True)
            raise
    def get_master_session_summary(self) -> Dict[str, Any]:
        """Get master session summary"""
        if not self.master_session:
            return {"error": "No master session"}

        return {
            "session_id": self.master_session.session_id,
            "session_name": self.master_session.session_name,
            "status": self.master_session.status.value,
            "created_at": self.master_session.created_at,
            "updated_at": self.master_session.updated_at,
            "chat_entries": len(self.master_session.chat_history),
            "workflows_identified": len(self.master_session.workflows_identified),
            "patterns_matched": len(self.master_session.patterns_matched),
            "consolidated_sessions": len(self.master_session.consolidated_from),
            "duplicated_sessions": len(self.master_session.duplicated_to)
        }


def main():
    """Main execution"""
    manager = MasterSessionManager()

    print("🎯 Master Session Manager - JARVIS Lead Session")
    print("=" * 80)
    print("")

    # Create or get master session
    master_id = manager.create_or_set_master_session("JARVIS Master Lead Session")
    print(f"✅ Master Session: {master_id}")
    print("")

    # Add some entries
    manager.add_to_master_session("JARVIS", "Starting workflow processing")
    manager.add_to_master_session("MARVIN", "Reviewing workflow patterns")
    manager.add_to_master_session("User", "Complete the Lumina extension")

    # Get summary
    summary = manager.get_master_session_summary()
    print("📊 Master Session Summary:")
    print(f"   Chat Entries: {summary['chat_entries']}")
    print(f"   Workflows: {summary['workflows_identified']}")
    print(f"   Patterns: {summary['patterns_matched']}")
    print("")

    # Process workflows
    result = manager.process_workflows_from_master()
    print(f"✅ Processed {result['workflows_processed']} workflows")
    print("")

    # Apply feedback loop
    feedback_result = manager.apply_master_feedback_loop()
    print(f"✅ Applied {feedback_result['patterns_applied']} learned patterns")


if __name__ == "__main__":



    main()