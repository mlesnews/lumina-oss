#!/usr/bin/env python3
"""
Completion Verification Checkpoint System

Prevents premature completion claims by forcing introspection and verification
before reporting task status. Addresses the "Communication Breakdown Cycle"
pattern where specialists claim completion without verification.

Based on: HOLOCRON-COMM-001 (Communication Breakdown Pattern)
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class VerificationStatus(Enum):
    """Verification status levels"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    PARTIAL = "partial"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class VerificationCriterion:
    """A single verification criterion"""
    criterion_id: str
    description: str
    required: bool = True
    verified: bool = False
    verification_method: Optional[str] = None
    verification_result: Optional[str] = None
    notes: str = ""


@dataclass
class CompletionVerification:
    """Completion verification checkpoint"""
    task_id: str
    task_name: str
    timestamp: datetime = field(default_factory=datetime.now)

    # What was implemented
    implemented_items: List[str] = field(default_factory=list)

    # Verification criteria
    criteria: List[VerificationCriterion] = field(default_factory=list)

    # Status
    implementation_status: str = "unknown"
    verification_status: VerificationStatus = VerificationStatus.NOT_STARTED
    overall_status: str = "unknown"

    # Gaps
    identified_gaps: List[str] = field(default_factory=list)

    # Honest reporting
    what_was_tested: List[str] = field(default_factory=list)
    what_was_not_tested: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['verification_status'] = self.verification_status.value
        data['criteria'] = [asdict(c) for c in self.criteria]
        return data


class CompletionVerificationCheckpoint:
    """
    Completion Verification Checkpoint System

    Forces introspection before claiming completion:
    1. Pause and introspect: What does completion mean?
    2. List verification criteria: What needs to be tested?
    3. Check each criterion: Have I verified this?
    4. Identify gaps: What's missing?
    5. Report honestly: Implemented X, Verified Y, Gaps Z
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)
        self.verification_dir = self.project_root / "data" / "completion_verifications"
        self.verification_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Completion Verification Checkpoint System initialized")

    def create_verification(self, task_id: str, task_name: str,
                           implemented_items: List[str],
                           criteria: List[Dict[str, Any]]) -> CompletionVerification:
        """
        Create a completion verification checkpoint

        Args:
            task_id: Unique task identifier
            task_name: Human-readable task name
            implemented_items: List of what was implemented
            criteria: List of verification criteria (dicts with criterion_id, description, required)
        """
        verification = CompletionVerification(
            task_id=task_id,
            task_name=task_name,
            implemented_items=implemented_items
        )

        # Convert criteria dicts to VerificationCriterion objects
        for crit_dict in criteria:
            criterion = VerificationCriterion(
                criterion_id=crit_dict.get("criterion_id", ""),
                description=crit_dict.get("description", ""),
                required=crit_dict.get("required", True),
                verification_method=crit_dict.get("verification_method")
            )
            verification.criteria.append(criterion)

        return verification

    def verify_criterion(self, verification: CompletionVerification,
                        criterion_id: str, verified: bool,
                        result: Optional[str] = None,
                        notes: Optional[str] = None) -> bool:
        """
        Mark a criterion as verified or not verified

        Returns:
            True if criterion was found and updated
        """
        for criterion in verification.criteria:
            if criterion.criterion_id == criterion_id:
                criterion.verified = verified
                if result:
                    criterion.verification_result = result
                if notes:
                    criterion.notes = notes
                return True
        return False

    def evaluate_verification(self, verification: CompletionVerification) -> CompletionVerification:
        """
        Evaluate verification status based on criteria

        Updates verification_status and overall_status
        """
        if not verification.criteria:
            verification.verification_status = VerificationStatus.NOT_STARTED
            verification.overall_status = "no_criteria_defined"
            return verification

        required_criteria = [c for c in verification.criteria if c.required]
        verified_required = [c for c in required_criteria if c.verified]

        total_criteria = len(verification.criteria)
        verified_total = sum(1 for c in verification.criteria if c.verified)

        # Determine status
        if verified_total == 0:
            verification.verification_status = VerificationStatus.NOT_STARTED
        elif verified_total < len(required_criteria):
            verification.verification_status = VerificationStatus.IN_PROGRESS
        elif verified_total == total_criteria:
            verification.verification_status = VerificationStatus.COMPLETE
        elif len(verified_required) == len(required_criteria):
            verification.verification_status = VerificationStatus.PARTIAL
        else:
            verification.verification_status = VerificationStatus.IN_PROGRESS

        # Identify gaps
        unverified_required = [c for c in required_criteria if not c.verified]
        verification.identified_gaps = [
            f"{c.criterion_id}: {c.description}" for c in unverified_required
        ]

        # Determine overall status
        if verification.verification_status == VerificationStatus.COMPLETE:
            verification.overall_status = "complete_and_verified"
        elif verification.verification_status == VerificationStatus.PARTIAL:
            verification.overall_status = "implemented_partially_verified"
        elif verification.verification_status == VerificationStatus.IN_PROGRESS:
            verification.overall_status = "implemented_verification_in_progress"
        else:
            verification.overall_status = "implemented_not_verified"

        return verification

    def generate_honest_report(self, verification: CompletionVerification) -> str:
        """
        Generate honest status report

        Format: "Implemented: X, Verified: Y, Gaps: Z"
        Never claims 100% unless 100% verified
        """
        self.evaluate_verification(verification)

        lines = [
            f"=== Completion Verification: {verification.task_name} ===",
            f"Task ID: {verification.task_id}",
            f"Timestamp: {verification.timestamp.isoformat()}",
            "",
            "IMPLEMENTED:",
        ]

        if verification.implemented_items:
            for item in verification.implemented_items:
                lines.append(f"  ✓ {item}")
        else:
            lines.append("  (no items listed)")

        lines.extend([
            "",
            "VERIFICATION STATUS:",
            f"  Status: {verification.verification_status.value}",
            f"  Overall: {verification.overall_status}",
            "",
            "VERIFICATION CRITERIA:",
        ])

        for criterion in verification.criteria:
            status = "✓" if criterion.verified else "✗"
            required = "[REQUIRED]" if criterion.required else "[OPTIONAL]"
            lines.append(f"  {status} {required} {criterion.criterion_id}: {criterion.description}")
            if criterion.verification_result:
                lines.append(f"      Result: {criterion.verification_result}")
            if criterion.notes:
                lines.append(f"      Notes: {criterion.notes}")

        if verification.identified_gaps:
            lines.extend([
                "",
                "IDENTIFIED GAPS:",
            ])
            for gap in verification.identified_gaps:
                lines.append(f"  ⚠ {gap}")

        if verification.what_was_tested:
            lines.extend([
                "",
                "WHAT WAS TESTED:",
            ])
            for test in verification.what_was_tested:
                lines.append(f"  ✓ {test}")

        if verification.what_was_not_tested:
            lines.extend([
                "",
                "WHAT WAS NOT TESTED:",
            ])
            for test in verification.what_was_not_tested:
                lines.append(f"  ✗ {test}")

        lines.extend([
            "",
            "HONEST STATUS:",
            f"  {verification.overall_status.replace('_', ' ').title()}",
        ])

        # Forbidden claims check
        if verification.verification_status != VerificationStatus.COMPLETE:
            lines.append("  ⚠️  DO NOT claim '100% complete' or 'all done'")
            lines.append("  ⚠️  DO NOT claim 'finished' without full verification")

        return "\n".join(lines)

    def save_verification(self, verification: CompletionVerification) -> Path:
        try:
            """Save verification to file"""
            filename = f"verification_{verification.task_id}_{verification.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.verification_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(verification.to_dict(), f, indent=2, ensure_ascii=False)

            logger.info(f"Verification saved to {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"Error in save_verification: {e}", exc_info=True)
            raise
    def should_claim_completion(self, verification: CompletionVerification) -> tuple[bool, str]:
        """
        Determine if completion can be claimed

        Returns:
            (can_claim: bool, reason: str)
        """
        self.evaluate_verification(verification)

        if verification.verification_status == VerificationStatus.COMPLETE:
            return True, "All criteria verified"

        required_criteria = [c for c in verification.criteria if c.required]
        verified_required = [c for c in required_criteria if c.verified]

        if len(verified_required) == len(required_criteria) and len(required_criteria) > 0:
            return True, "All required criteria verified (some optional criteria pending)"

        return False, f"Only {len(verified_required)}/{len(required_criteria)} required criteria verified"


def main():
    """Example usage"""
    checkpoint = CompletionVerificationCheckpoint()

    # Example: Phase 3 verification
    verification = checkpoint.create_verification(
        task_id="manus_phase3",
        task_name="MANUS Phase 3 Implementation",
        implemented_items=[
            "complete_ide_control.py created",
            "data_lifecycle_manager.py created",
            "security_scanning_automation.py created",
            "Integration into unified control interface"
        ],
        criteria=[
            {
                "criterion_id": "files_created",
                "description": "Phase 3 files created and run without errors",
                "required": True,
                "verification_method": "run_scripts"
            },
            {
                "criterion_id": "integration_complete",
                "description": "Modules integrated into unified control interface",
                "required": True,
                "verification_method": "check_unified_control"
            },
            {
                "criterion_id": "end_to_end_testing",
                "description": "End-to-end testing of all Phase 3 features",
                "required": True,
                "verification_method": "run_tests"
            },
            {
                "criterion_id": "ide_state_detection",
                "description": "Complete IDE state management detects windows/tabs correctly",
                "required": False,
                "verification_method": "test_ide_detection"
            }
        ]
    )

    # Mark some as verified
    checkpoint.verify_criterion(verification, "files_created", True, "All files run without errors")
    checkpoint.verify_criterion(verification, "integration_complete", True, "Health check shows operational")
    checkpoint.verify_criterion(verification, "end_to_end_testing", False, "Not yet performed")

    # Evaluate and generate report
    checkpoint.evaluate_verification(verification)
    report = checkpoint.generate_honest_report(verification)
    print(report)

    # Check if completion can be claimed
    can_claim, reason = checkpoint.should_claim_completion(verification)
    print(f"\nCan claim completion: {can_claim}")
    print(f"Reason: {reason}")

    # Save verification
    checkpoint.save_verification(verification)


if __name__ == "__main__":



    main()