#!/usr/bin/env python3
"""
JARVIS Follow-Up on MARVIN Roasts

JARVIS follows up on each and every MARVIN roast item:
1. Match them with workflows
2. Validate them
3. Cross them off as done (sub-flows/sub-agent chats)
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from marvin_granular_roast import MarvinGranularRoast, GranularFault
    MARVIN_GRANULAR_AVAILABLE = True
except ImportError:
    MARVIN_GRANULAR_AVAILABLE = False
    MarvinGranularRoast = None
    GranularFault = None

try:
    from master_workflow_orchestrator import MasterWorkflowOrchestrator
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False
    MasterWorkflowOrchestrator = None

try:
    from sub_ask_todo_manager import SubAskTodoManager
    SUB_ASK_AVAILABLE = True
except ImportError:
    SUB_ASK_AVAILABLE = False
    SubAskTodoManager = None


class FollowUpStatus(Enum):
    """Follow-up status"""
    PENDING = "pending"
    MATCHED = "matched"  # Matched with workflow
    VALIDATED = "validated"  # Validated
    IN_PROGRESS = "in_progress"  # Being worked on
    COMPLETED = "completed"  # Completed
    ARCHIVED = "archived"  # Archived


@dataclass
class FollowUpItem:
    """Follow-up item from MARVIN roast"""
    followup_id: str
    fault_id: str
    fault: GranularFault
    workflow_id: Optional[str] = None
    workflow_name: Optional[str] = None
    sub_agent_chat_id: Optional[str] = None
    status: FollowUpStatus = FollowUpStatus.PENDING
    matched_at: Optional[str] = None
    validated_at: Optional[str] = None
    completed_at: Optional[str] = None
    archived_at: Optional[str] = None
    validation_notes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        data["fault"] = self.fault.to_dict()
        return data


class JarvisMarvinFollowUp:
    """
    JARVIS Follow-Up on MARVIN Roasts

    For each and every MARVIN roast item:
    1. Match with workflows
    2. Validate
    3. Cross off as done (sub-flows/sub-agent chats)
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("JarvisMarvinFollowUp")

        # Directories
        self.data_dir = self.project_root / "data" / "jarvis_marvin_followup"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Files
        self.followups_file = self.data_dir / "followups.json"

        # MARVIN granular roaster
        self.marvin_roaster = None
        if MARVIN_GRANULAR_AVAILABLE and MarvinGranularRoast:
            try:
                self.marvin_roaster = MarvinGranularRoast(project_root=self.project_root)
            except Exception as e:
                self.logger.warning(f"MARVIN granular roaster not available: {e}")

        # Orchestrator
        self.orchestrator = None
        if ORCHESTRATOR_AVAILABLE and MasterWorkflowOrchestrator:
            try:
                self.orchestrator = MasterWorkflowOrchestrator(project_root=self.project_root)
            except Exception as e:
                self.logger.warning(f"Orchestrator not available: {e}")

        # Sub-ask manager
        self.sub_ask_manager = None
        if SUB_ASK_AVAILABLE and SubAskTodoManager:
            try:
                self.sub_ask_manager = SubAskTodoManager(project_root=self.project_root)
            except Exception as e:
                self.logger.warning(f"Sub-ask manager not available: {e}")

        # State
        self.followups: Dict[str, FollowUpItem] = {}

        # Load state
        self._load_state()

    def _load_state(self):
        """Load follow-ups"""
        if self.followups_file.exists():
            try:
                with open(self.followups_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for followup_id, followup_data in data.items():
                        fault_data = followup_data["fault"]
                        fault = GranularFault(**fault_data)
                        fault.granularity_level = type(fault.granularity_level)(fault_data["granularity_level"])
                        fault.category = type(fault.category)(fault_data["category"])

                        followup = FollowUpItem(**followup_data)
                        followup.fault = fault
                        followup.status = FollowUpStatus(followup_data["status"])
                        self.followups[followup_id] = followup
            except Exception as e:
                self.logger.error(f"Error loading follow-ups: {e}")

    def _save_state(self):
        try:
            """Save follow-ups"""
            followups_data = {
                followup_id: followup.to_dict()
                for followup_id, followup in self.followups.items()
            }
            with open(self.followups_file, 'w', encoding='utf-8') as f:
                json.dump(followups_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in _save_state: {e}", exc_info=True)
            raise
    def process_marvin_roast(self, roast_id: Optional[str] = None) -> List[FollowUpItem]:
        """
        Process MARVIN roast - create follow-up items for each fault

        Returns list of follow-up items created
        """
        if not self.marvin_roaster:
            self.logger.error("MARVIN roaster not available")
            return []

        # Get latest roast or specific roast
        if roast_id:
            roasts = [r for r in self.marvin_roaster.roasts if r.roast_id == roast_id]
        else:
            roasts = self.marvin_roaster.roasts[-1:] if self.marvin_roaster.roasts else []

        if not roasts:
            self.logger.warning("No roasts found")
            return []

        roast = roasts[0]
        followups = []

        self.logger.info(f"🔧 JARVIS processing MARVIN roast: {roast.roast_id} ({len(roast.faults)} faults)")

        # Create follow-up item for each fault
        for fault in roast.faults:
            followup_id = f"followup_{int(datetime.now().timestamp() * 1000)}_{len(followups)}"

            followup = FollowUpItem(
                followup_id=followup_id,
                fault_id=fault.fault_id,
                fault=fault,
                status=FollowUpStatus.PENDING
            )

            self.followups[followup_id] = followup
            followups.append(followup)

            self.logger.info(f"📋 Created follow-up: {followup_id} for fault {fault.fault_id}")

        self._save_state()

        return followups

    def match_with_workflows(self, followup_id: str) -> bool:
        """
        Match follow-up item with workflow

        Returns True if matched, False otherwise
        """
        if followup_id not in self.followups:
            return False

        followup = self.followups[followup_id]

        if not self.orchestrator:
            self.logger.error("Orchestrator not available")
            return False

        # Create ask from fault
        ask_text = f"Fix: {followup.fault.specific_fault} - {followup.fault.description}"

        # Match to workflows
        ask_id = self.orchestrator.receive_user_ask(ask_text)
        matches = self.orchestrator.get_workflow_matches_for_ask(ask_id)

        if matches:
            # Use best match
            best_match = matches[0]
            followup.workflow_id = best_match.workflow_id
            followup.workflow_name = best_match.workflow_name
            followup.status = FollowUpStatus.MATCHED
            followup.matched_at = datetime.now().isoformat()
            followup.metadata["ask_id"] = ask_id
            followup.metadata["match_confidence"] = best_match.confidence

            self.logger.info(f"✅ Matched follow-up {followup_id} with workflow {best_match.workflow_name}")

            # Automatically spawn sub-session (creates sub-agent chat)
            try:
                sub_session_id = self.orchestrator.spawn_sub_session(ask_id, best_match)
                followup.sub_agent_chat_id = self.orchestrator.sub_sessions.get(sub_session_id, {}).get("metadata", {}).get("chat_session_id")
                followup.status = FollowUpStatus.IN_PROGRESS
                self.logger.info(f"✅ Spawned sub-session {sub_session_id} for follow-up {followup_id}")
            except Exception as e:
                self.logger.warning(f"Could not spawn sub-session: {e}")

            self._save_state()
            return True
        else:
            self.logger.warning(f"⚠️ No workflow match for follow-up {followup_id}")
            return False

    def validate_followup(self, followup_id: str, validation_notes: List[str]) -> bool:
        """
        Validate follow-up item

        Returns True if validated, False otherwise
        """
        if followup_id not in self.followups:
            return False

        followup = self.followups[followup_id]

        followup.status = FollowUpStatus.VALIDATED
        followup.validated_at = datetime.now().isoformat()
        followup.validation_notes = validation_notes

        self.logger.info(f"✅ Validated follow-up {followup_id}")

        self._save_state()

        return True

    def complete_followup(self, followup_id: str) -> bool:
        """
        Mark follow-up as completed

        Returns True if completed, False otherwise
        """
        if followup_id not in self.followups:
            return False

        followup = self.followups[followup_id]

        followup.status = FollowUpStatus.COMPLETED
        followup.completed_at = datetime.now().isoformat()

        self.logger.info(f"✅ Completed follow-up {followup_id}")

        self._save_state()

        return True

    def archive_followup(self, followup_id: str) -> bool:
        """
        Archive follow-up (cross off list as done)

        Returns True if archived, False otherwise
        """
        if followup_id not in self.followups:
            return False

        followup = self.followups[followup_id]

        followup.status = FollowUpStatus.ARCHIVED
        followup.archived_at = datetime.now().isoformat()

        self.logger.info(f"📦 Archived follow-up {followup_id}")

        self._save_state()

        return True

    def process_all_marvin_faults(self) -> Dict[str, Any]:
        """
        Process all MARVIN faults:
        1. Match with workflows
        2. Validate
        3. Complete
        4. Archive
        """
        if not self.marvin_roaster:
            return {"error": "MARVIN roaster not available"}

        # Get all faults
        all_faults = self.marvin_roaster.get_all_faults()

        # Process each fault
        processed = 0
        matched = 0
        validated = 0
        completed = 0
        archived = 0

        for fault in all_faults:
            # Create follow-up if not exists
            existing = [f for f in self.followups.values() if f.fault_id == fault.fault_id]
            if not existing:
                followup_id = f"followup_{int(datetime.now().timestamp() * 1000)}_{processed}"
                followup = FollowUpItem(
                    followup_id=followup_id,
                    fault_id=fault.fault_id,
                    fault=fault,
                    status=FollowUpStatus.PENDING
                )
                self.followups[followup_id] = followup
                processed += 1

            # Match with workflows
            followup = existing[0] if existing else followup
            if followup.status == FollowUpStatus.PENDING:
                if self.match_with_workflows(followup.followup_id):
                    matched += 1

            # Auto-validate if matched
            if followup.status == FollowUpStatus.MATCHED:
                self.validate_followup(followup.followup_id, ["Auto-validated after workflow match"])
                validated += 1

        self._save_state()

        return {
            "processed": processed,
            "matched": matched,
            "validated": validated,
            "completed": completed,
            "archived": archived,
            "total_faults": len(all_faults)
        }

    def get_pending_followups(self) -> List[FollowUpItem]:
        """Get pending follow-ups"""
        return [f for f in self.followups.values() if f.status == FollowUpStatus.PENDING]

    def get_completed_followups(self) -> List[FollowUpItem]:
        """Get completed follow-ups"""
        return [f for f in self.followups.values() if f.status == FollowUpStatus.COMPLETED]

    def get_archived_followups(self) -> List[FollowUpItem]:
        """Get archived follow-ups"""
        return [f for f in self.followups.values() if f.status == FollowUpStatus.ARCHIVED]


def main():
    """Main execution for testing"""
    followup = JarvisMarvinFollowUp()

    print("=" * 80)
    print("🔧 JARVIS MARVIN FOLLOW-UP")
    print("=" * 80)

    # Process MARVIN roast
    followups = followup.process_marvin_roast()

    print(f"\n📋 Created {len(followups)} follow-up items")

    # Process all faults
    result = followup.process_all_marvin_faults()

    print(f"\n✅ Processed:")
    print(f"   Processed: {result.get('processed', 0)}")
    print(f"   Matched: {result.get('matched', 0)}")
    print(f"   Validated: {result.get('validated', 0)}")
    print(f"   Total Faults: {result.get('total_faults', 0)}")


if __name__ == "__main__":



    main()