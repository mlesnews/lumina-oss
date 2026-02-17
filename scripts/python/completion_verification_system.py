#!/usr/bin/env python3
"""
Completion Verification System

Prevents false completion claims:
- Verify actual completion (not just status)
- Track step progress (e.g., step 13 of 48)
- Investigate why work stopped
- Prevent incorrect "DONE" status
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from master_todo_tracker import MasterTodoTracker, TaskStatus
    TODO_TRACKER_AVAILABLE = True
except ImportError:
    TODO_TRACKER_AVAILABLE = False
    MasterTodoTracker = None


class CompletionStatus(Enum):
    """Actual completion status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PARTIALLY_DONE = "partially_done"  # Step 13 of 48, etc.
    COMPLETED = "completed"
    STOPPED_UNEXPECTEDLY = "stopped_unexpectedly"
    FALSE_COMPLETE = "false_complete"  # Claimed complete but not actually done


@dataclass
class StepProgress:
    """Step progress tracking"""
    step_number: int
    total_steps: int
    step_name: str
    status: str  # pending, in_progress, completed, skipped
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    stopped_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CompletionVerification:
    """Completion verification result"""
    item_id: str
    claimed_status: str  # What was claimed
    actual_status: CompletionStatus
    step_progress: Optional[StepProgress] = None
    completion_percentage: float = 0.0
    stopped_reason: Optional[str] = None
    investigation_notes: List[str] = field(default_factory=list)
    verified_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["actual_status"] = self.actual_status.value
        return data


class CompletionVerificationSystem:
    """
    Verifies actual completion vs. claimed completion

    Prevents false "DONE" claims
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("CompletionVerificationSystem")

        # Directories
        self.data_dir = self.project_root / "data" / "completion_verification"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Files
        self.verifications_file = self.data_dir / "verifications.jsonl"
        self.false_completes_file = self.data_dir / "false_completes.json"

        # Todo tracker  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
        self.todo_tracker = MasterTodoTracker(project_root) if TODO_TRACKER_AVAILABLE else None

        # State
        self.verifications: List[CompletionVerification] = []
        self.false_completes: List[Dict[str, Any]] = []

        # Load state
        self._load_state()

    def _load_state(self):
        """Load verification state"""
        # Load verifications
        if self.verifications_file.exists():
            try:
                with open(self.verifications_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            self.verifications.append(CompletionVerification(**data))
            except Exception as e:
                self.logger.error(f"Error loading verifications: {e}")

        # Load false completes
        if self.false_completes_file.exists():
            try:
                with open(self.false_completes_file, 'r', encoding='utf-8') as f:
                    self.false_completes = json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading false completes: {e}")

    def verify_completion(
        self,
        item_id: str,
        claimed_status: str,
        total_steps: Optional[int] = None,
        current_step: Optional[int] = None,
        step_name: Optional[str] = None
    ) -> CompletionVerification:
        """
        Verify actual completion vs. claimed completion

        Returns verification result
        """
        now = datetime.now().isoformat()

        # Determine actual status
        actual_status = CompletionStatus.NOT_STARTED
        completion_percentage = 0.0
        stopped_reason = None
        investigation_notes = []

        # Check if claimed complete
        if claimed_status.lower() in ["complete", "done", "completed", "finished"]:
            # Verify if actually complete
            if total_steps and current_step:
                if current_step < total_steps:
                    # Partially done (e.g., step 13 of 48)
                    actual_status = CompletionStatus.PARTIALLY_DONE
                    completion_percentage = (current_step / total_steps) * 100
                    investigation_notes.append(f"Only on step {current_step} of {total_steps} ({completion_percentage:.1f}% complete)")
                    stopped_reason = "Stopped before completion - no reason given"
                elif current_step == total_steps:
                    # Actually complete
                    actual_status = CompletionStatus.COMPLETED
                    completion_percentage = 100.0
                else:
                    # Beyond total steps (error)
                    actual_status = CompletionStatus.FALSE_COMPLETE
                    investigation_notes.append(f"Current step {current_step} exceeds total steps {total_steps}")
            else:
                # No step tracking - need to investigate
                actual_status = CompletionStatus.FALSE_COMPLETE
                investigation_notes.append("Claimed complete but no step tracking available")
                stopped_reason = "Cannot verify completion without step tracking"
        elif claimed_status.lower() in ["in_progress", "pending", "started"]:
            if total_steps and current_step:
                if current_step < total_steps:
                    actual_status = CompletionStatus.IN_PROGRESS
                    completion_percentage = (current_step / total_steps) * 100
                else:
                    actual_status = CompletionStatus.COMPLETED
                    completion_percentage = 100.0
            else:
                actual_status = CompletionStatus.IN_PROGRESS

        # Check if stopped unexpectedly
        if actual_status in [CompletionStatus.PARTIALLY_DONE, CompletionStatus.IN_PROGRESS]:
            if not stopped_reason:
                stopped_reason = "Work in progress - not completed"
                investigation_notes.append("Work stopped without completion - investigate why")

        # Create step progress if available
        step_progress = None
        if total_steps and current_step:
            step_progress = StepProgress(
                step_number=current_step,
                total_steps=total_steps,
                step_name=step_name or f"Step {current_step}",
                status="in_progress" if current_step < total_steps else "completed",
                stopped_reason=stopped_reason
            )

        # Create verification
        verification = CompletionVerification(
            item_id=item_id,
            claimed_status=claimed_status,
            actual_status=actual_status,
            step_progress=step_progress,
            completion_percentage=completion_percentage,
            stopped_reason=stopped_reason,
            investigation_notes=investigation_notes,
            verified_at=now
        )

        self.verifications.append(verification)

        # Save verification
        with open(self.verifications_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(verification.to_dict()) + '\n')

        # If false complete, record it
        if actual_status == CompletionStatus.FALSE_COMPLETE:
            self.false_completes.append({
                "item_id": item_id,
                "claimed_status": claimed_status,
                "actual_status": actual_status.value,
                "completion_percentage": completion_percentage,
                "stopped_reason": stopped_reason,
                "investigation_notes": investigation_notes,
                "detected_at": now
            })

            with open(self.false_completes_file, 'w', encoding='utf-8') as f:
                json.dump(self.false_completes, f, indent=2, ensure_ascii=False)

            self.logger.warning(f"⚠️ FALSE COMPLETE detected: {item_id} - {stopped_reason}")

        self.logger.info(f"✅ Verified completion: {item_id} - Actual: {actual_status.value} ({completion_percentage:.1f}%)")

        return verification

    def get_false_completes(self) -> List[Dict[str, Any]]:
        """Get all false complete detections"""
        return self.false_completes

    def get_incomplete_items(self) -> List[CompletionVerification]:
        """Get items that are incomplete (not actually done)"""
        return [
            v for v in self.verifications
            if v.actual_status in [
                CompletionStatus.PARTIALLY_DONE,
                CompletionStatus.IN_PROGRESS,
                CompletionStatus.STOPPED_UNEXPECTEDLY,
                CompletionStatus.FALSE_COMPLETE
            ]
        ]


def main():
    """Main execution for testing"""
    verifier = CompletionVerificationSystem()

    print("=" * 80)
    print("✅ COMPLETION VERIFICATION SYSTEM")
    print("=" * 80)

    # Test: False complete detection
    verification = verifier.verify_completion(
        item_id="test_item_123",
        claimed_status="complete",
        total_steps=48,
        current_step=13,
        step_name="Step 13: Processing items"
    )

    print(f"\n📊 Verification Result:")
    print(f"   Claimed: {verification.claimed_status}")
    print(f"   Actual: {verification.actual_status.value}")
    print(f"   Completion: {verification.completion_percentage:.1f}%")
    print(f"   Step: {verification.step_progress.step_number}/{verification.step_progress.total_steps}")
    print(f"   Stopped Reason: {verification.stopped_reason}")

    if verification.actual_status == CompletionStatus.FALSE_COMPLETE:
        print(f"\n⚠️ FALSE COMPLETE DETECTED!")
        print(f"   Investigation Notes:")
        for note in verification.investigation_notes:
            print(f"     - {note}")


if __name__ == "__main__":



    main()