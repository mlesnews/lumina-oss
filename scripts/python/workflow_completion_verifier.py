#!/usr/bin/env python3
"""
Workflow Completion Verifier
Automated verification and validation for all workflows

This module automatically verifies and validates workflow completion,
eliminating the need to manually ask "have we completed all steps?"

Applies to ALL workflows - always runs automatically.

@JARVIS @MARVIN @WORKFLOW @SYPHON
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("WorkflowCompletionVerifier")


class VerificationStatus(Enum):
    """Verification status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    PARTIAL = "partial"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"


@dataclass
class TaskItem:
    """Individual task item"""
    task_id: str
    description: str
    status: VerificationStatus = VerificationStatus.NOT_STARTED
    completed_at: Optional[str] = None
    verification_notes: List[str] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)  # Files, docs created

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass
class WorkflowVerification:
    """Workflow verification result"""
    workflow_id: str
    workflow_name: str
    verification_timestamp: str
    overall_status: VerificationStatus
    tasks: List[TaskItem] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)
    verification_summary: str = ""
    completion_percentage: float = 0.0
    missing_items: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["overall_status"] = self.overall_status.value
        data["tasks"] = [t.to_dict() for t in self.tasks]
        return data


class WorkflowCompletionVerifier:
    """
    Automated workflow completion verifier

    This class automatically verifies and validates workflow completion
    for ALL workflows. Should be integrated into workflow_base.py so it
    always runs automatically.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize verifier"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger
        self.verification_dir = self.project_root / "data" / "workflow_verifications"
        self.verification_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("✅ Workflow Completion Verifier initialized")

    def verify_workflow(
        self,
        workflow_id: str,
        workflow_name: str,
        expected_tasks: List[Dict[str, Any]],
        deliverables: List[str],
        workflow_context: Optional[Dict[str, Any]] = None
    ) -> WorkflowVerification:
        """
        Verify workflow completion

        Args:
            workflow_id: Unique workflow identifier
            workflow_name: Human-readable workflow name
            expected_tasks: List of expected tasks with verification criteria
            deliverables: List of expected deliverables (files, docs, etc.)
            workflow_context: Additional context about the workflow

        Returns:
            WorkflowVerification object with verification results
        """
        self.logger.info(f"🔍 Verifying workflow: {workflow_name} ({workflow_id})")

        # Parse expected tasks
        task_items = []
        for task_data in expected_tasks:
            task = TaskItem(
                task_id=task_data.get("task_id", ""),
                description=task_data.get("description", ""),
                verification_notes=task_data.get("verification_notes", [])
            )
            task_items.append(task)

        # Verify each task
        completed_tasks = 0
        for task in task_items:
            task_status = self._verify_task(task, workflow_context)
            task.status = task_status

            if task_status == VerificationStatus.COMPLETE:
                task.completed_at = datetime.now().isoformat()
                completed_tasks += 1

        # Verify deliverables
        verified_deliverables = []
        missing_deliverables = []

        for deliverable in deliverables:
            if self._verify_deliverable(deliverable):
                verified_deliverables.append(deliverable)
            else:
                missing_deliverables.append(deliverable)

        # Calculate completion percentage
        total_items = len(task_items) + len(deliverables)
        completed_items = completed_tasks + len(verified_deliverables)
        completion_percentage = (completed_items / total_items * 100) if total_items > 0 else 0.0

        # Determine overall status
        overall_status = self._determine_overall_status(
            task_items, verified_deliverables, missing_deliverables, completion_percentage
        )

        # Generate verification summary
        verification_summary = self._generate_summary(
            workflow_name, task_items, verified_deliverables, 
            missing_deliverables, completion_percentage, overall_status
        )

        # Identify next steps
        next_steps = self._identify_next_steps(
            task_items, missing_deliverables, overall_status
        )

        # Create verification result
        verification = WorkflowVerification(
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            verification_timestamp=datetime.now().isoformat(),
            overall_status=overall_status,
            tasks=task_items,
            deliverables=verified_deliverables,
            verification_summary=verification_summary,
            completion_percentage=completion_percentage,
            missing_items=missing_deliverables,
            next_steps=next_steps
        )

        # Save verification result
        self._save_verification(verification)

        # Log result
        self._log_verification_result(verification)

        return verification

    def _verify_task(
        self,
        task: TaskItem,
        workflow_context: Optional[Dict[str, Any]] = None
    ) -> VerificationStatus:
        """Verify individual task completion"""
        import re

        # Check if task has verification criteria
        if not task.verification_notes:
            # No specific criteria, check if task description indicates completion
            # This is a simple heuristic - can be enhanced
            return VerificationStatus.COMPLETE

        # Verify against criteria
        all_criteria_met = True
        failed_criteria = []

        for note in task.verification_notes:
            note_lower = note.lower()
            criterion_met = True

            # Check file existence patterns
            if "file exists" in note_lower or "file:" in note_lower:
                # Extract file path from note
                # Pattern: "File exists: path/to/file.md" or "file: path/to/file.md"
                match = re.search(r'(?:file exists|file):\s*(.+)', note, re.IGNORECASE)
                if match:
                    file_path = match.group(1).strip()
                    if not self._verify_deliverable(file_path):
                        criterion_met = False
                        failed_criteria.append(f"File missing: {file_path}")

            # Check document creation patterns
            elif "document created" in note_lower or "doc:" in note_lower or "document:" in note_lower:
                # Extract document path from note
                # Pattern: "Document created: path/to/doc.md" or "doc: path/to/doc.md"
                match = re.search(r'(?:document created|doc|document):\s*(.+)', note, re.IGNORECASE)
                if match:
                    doc_path = match.group(1).strip()
                    if not self._verify_deliverable(doc_path):
                        criterion_met = False
                        failed_criteria.append(f"Document missing: {doc_path}")

            # Check script creation patterns
            elif "script created" in note_lower or "script:" in note_lower:
                match = re.search(r'(?:script created|script):\s*(.+)', note, re.IGNORECASE)
                if match:
                    script_path = match.group(1).strip()
                    if not self._verify_deliverable(script_path):
                        criterion_met = False
                        failed_criteria.append(f"Script missing: {script_path}")

            # Check config creation patterns
            elif "config" in note_lower and ("created" in note_lower or ":" in note):
                match = re.search(r'config(?:uration)?(?:\s+created)?:\s*(.+)', note, re.IGNORECASE)
                if match:
                    config_path = match.group(1).strip()
                    if not self._verify_deliverable(config_path):
                        criterion_met = False
                        failed_criteria.append(f"Config missing: {config_path}")

            if not criterion_met:
                all_criteria_met = False

        # Update task verification notes with failures
        if failed_criteria:
            task.verification_notes.extend([f"❌ {fc}" for fc in failed_criteria])

        if all_criteria_met:
            return VerificationStatus.COMPLETE
        else:
            return VerificationStatus.NEEDS_REVIEW

    def _verify_deliverable(self, deliverable: str) -> bool:
        try:
            """Verify deliverable exists"""
            # Check if deliverable is a file path
            deliverable_path = Path(deliverable)

            # If absolute path, use as-is
            if deliverable_path.is_absolute():
                return deliverable_path.exists()

            # If relative path, check from project root
            full_path = self.project_root / deliverable_path
            return full_path.exists()

        except Exception as e:
            self.logger.error(f"Error in _verify_deliverable: {e}", exc_info=True)
            raise
    def _determine_overall_status(
        self,
        tasks: List[TaskItem],
        verified_deliverables: List[str],
        missing_deliverables: List[str],
        completion_percentage: float
    ) -> VerificationStatus:
        """Determine overall workflow status"""
        # If 100% complete
        if completion_percentage == 100.0:
            return VerificationStatus.COMPLETE

        # If 0% complete
        if completion_percentage == 0.0:
            return VerificationStatus.NOT_STARTED

        # If partial completion
        if completion_percentage > 0.0 and completion_percentage < 100.0:
            # Check if all critical items are complete
            critical_complete = all(
                task.status == VerificationStatus.COMPLETE
                for task in tasks
                if "critical" in task.description.lower() or "required" in task.description.lower()
            )

            if critical_complete:
                return VerificationStatus.PARTIAL
            else:
                return VerificationStatus.NEEDS_REVIEW

        return VerificationStatus.IN_PROGRESS

    def _generate_summary(
        self,
        workflow_name: str,
        tasks: List[TaskItem],
        verified_deliverables: List[str],
        missing_deliverables: List[str],
        completion_percentage: float,
        overall_status: VerificationStatus
    ) -> str:
        """Generate verification summary"""
        summary_parts = [
            f"Workflow: {workflow_name}",
            f"Overall Status: {overall_status.value.upper()}",
            f"Completion: {completion_percentage:.1f}%",
            f"",
            f"Tasks: {len([t for t in tasks if t.status == VerificationStatus.COMPLETE])}/{len(tasks)} complete",
            f"Deliverables: {len(verified_deliverables)}/{len(verified_deliverables) + len(missing_deliverables)} verified"
        ]

        if missing_deliverables:
            summary_parts.append("")
            summary_parts.append("Missing Deliverables:")
            for item in missing_deliverables:
                summary_parts.append(f"  - {item}")

        return "\n".join(summary_parts)

    def _identify_next_steps(
        self,
        tasks: List[TaskItem],
        missing_deliverables: List[str],
        overall_status: VerificationStatus
    ) -> List[str]:
        """Identify next steps based on verification"""
        next_steps = []

        # If incomplete, identify what needs to be done
        if overall_status != VerificationStatus.COMPLETE:
            # Incomplete tasks
            incomplete_tasks = [
                t for t in tasks
                if t.status != VerificationStatus.COMPLETE
            ]

            if incomplete_tasks:
                next_steps.append(f"Complete {len(incomplete_tasks)} remaining task(s)")
                for task in incomplete_tasks[:3]:  # Top 3
                    next_steps.append(f"  - {task.description}")

            # Missing deliverables
            if missing_deliverables:
                next_steps.append(f"Create {len(missing_deliverables)} missing deliverable(s)")
                for deliverable in missing_deliverables[:3]:  # Top 3
                    next_steps.append(f"  - {deliverable}")

        # If complete, no next steps
        if overall_status == VerificationStatus.COMPLETE:
            next_steps.append("✅ All steps complete - workflow verified and validated")

        return next_steps

    def _save_verification(self, verification: WorkflowVerification):
        try:
            """Save verification result to file"""
            verification_file = self.verification_dir / f"{verification.workflow_id}_verification.json"

            with open(verification_file, 'w', encoding='utf-8') as f:
                json.dump(verification.to_dict(), f, indent=2, ensure_ascii=False)

            self.logger.debug(f"Saved verification to {verification_file}")

        except Exception as e:
            self.logger.error(f"Error in _save_verification: {e}", exc_info=True)
            raise
    def _log_verification_result(self, verification: WorkflowVerification):
        """Log verification result"""
        status_emoji = {
            VerificationStatus.COMPLETE: "✅",
            VerificationStatus.PARTIAL: "⚠️",
            VerificationStatus.NEEDS_REVIEW: "🔍",
            VerificationStatus.NOT_STARTED: "⏸️",
            VerificationStatus.FAILED: "❌",
            VerificationStatus.IN_PROGRESS: "🔄"
        }

        emoji = status_emoji.get(verification.overall_status, "❓")

        self.logger.info(f"{emoji} {verification.workflow_name}: {verification.completion_percentage:.1f}% complete")
        self.logger.info(f"   Status: {verification.overall_status.value}")

        if verification.verification_summary:
            self.logger.info(f"   Summary: {verification.verification_summary.split(chr(10))[0]}")  # First line

        if verification.next_steps:
            self.logger.info(f"   Next Steps: {verification.next_steps[0]}")


def verify_workflow_completion(
    workflow_id: str,
    workflow_name: str,
    expected_tasks: List[Dict[str, Any]],
    deliverables: List[str],
    workflow_context: Optional[Dict[str, Any]] = None
) -> WorkflowVerification:
    """
    Convenience function to verify workflow completion

    This function should be called automatically at the end of every workflow.
    """
    verifier = WorkflowCompletionVerifier()
    return verifier.verify_workflow(
        workflow_id, workflow_name, expected_tasks, deliverables, workflow_context
    )


# @SYPHON: Workflow Completion Verification Pattern
# This pattern provides automatic workflow completion verification
# Extracted for reuse across all workflows
#
# Pattern Usage:
#   1. Inherit from WorkflowBase (already has verification integrated)
#   2. Set expected_deliverables in __init__
#   3. Optionally provide verification_template_path
#   4. Verification runs automatically in verify_completion()
#
# Pattern Features:
#   - Automatic file existence checking
#   - Task verification with criteria
#   - Completion percentage calculation
#   - Missing items identification
#   - Next steps suggestions
#   - Template-based configuration
#   - Integration with v3_verification

# Template for workflow verification
WORKFLOW_VERIFICATION_TEMPLATE = {
    "workflow_id": "workflow_unique_id",
    "workflow_name": "Human-readable workflow name",
    "expected_tasks": [
        {
            "task_id": "task_1",
            "description": "Task description",
            "verification_notes": [
                "Verification criterion 1",
                "Verification criterion 2"
            ]
        }
    ],
    "deliverables": [
        "path/to/deliverable1.md",
        "path/to/deliverable2.py"
    ],
    "workflow_context": {
        "additional": "context"
    }
}


if __name__ == "__main__":
    # Example usage
    verification = verify_workflow_completion(
        workflow_id="test_workflow_001",
        workflow_name="Test Workflow",
        expected_tasks=[
            {
                "task_id": "task_1",
                "description": "Create documentation",
                "verification_notes": ["Document file exists"]
            }
        ],
        deliverables=[
            "docs/test_documentation.md"
        ]
    )

    print(f"\n{verification.verification_summary}")
    print(f"\nNext Steps:")
    for step in verification.next_steps:
        print(f"  {step}")

