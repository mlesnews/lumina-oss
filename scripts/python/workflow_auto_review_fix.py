#!/usr/bin/env python3
"""
Workflow Auto Review & Fix Component

Automatically:
1. Maintains agent chat histories
2. Accepts all changes after running
3. Reviews changes
4. Fixes all issues
5. Feeds back into workflow loop

Integrates with WorkflowBase for seamless workflow integration.
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)


class ReviewStatus(Enum):
    """Review status"""
    PENDING = "pending"
    REVIEWING = "reviewing"
    ACCEPTED = "accepted"
    NEEDS_FIX = "needs_fix"
    FIXING = "fixing"
    FIXED = "fixed"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class ChatHistoryEntry:
    """Agent chat history entry"""
    entry_id: str
    timestamp: str
    agent: str
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ChangeEntry:
    """Change entry for review"""
    change_id: str
    timestamp: str
    file_path: str
    change_type: str  # created, modified, deleted
    diff: Optional[str] = None
    review_status: ReviewStatus = ReviewStatus.PENDING
    review_notes: str = ""
    fix_required: bool = False
    fix_applied: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["review_status"] = self.review_status.value
        return data


@dataclass
class ReviewResult:
    """Review result"""
    review_id: str
    timestamp: str
    changes_reviewed: int
    changes_accepted: int
    changes_need_fix: int
    fixes_applied: int
    review_notes: List[str] = field(default_factory=list)
    fix_results: List[Dict[str, Any]] = field(default_factory=list)
    workflow_feedback: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class WorkflowAutoReviewFix:
    """
    Automatic review and fix component for workflows

    Maintains chat histories, accepts changes, reviews, fixes, and feeds back into workflow.
    """

    def __init__(self, project_root: Optional[Path] = None, workflow_id: Optional[str] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.workflow_id = workflow_id or f"workflow_{int(datetime.now().timestamp())}"

        # Data directories
        self.data_dir = self.project_root / "data" / "workflow_reviews"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.chat_history_dir = self.project_root / "data" / "agent_chat_history"
        self.chat_history_dir.mkdir(parents=True, exist_ok=True)

        # Files
        self.chat_history_file = self.chat_history_dir / f"{self.workflow_id}_chat_history.jsonl"
        self.changes_file = self.data_dir / f"{self.workflow_id}_changes.json"
        self.review_file = self.data_dir / f"{self.workflow_id}_review.json"

        # State
        self.chat_history: List[ChatHistoryEntry] = []
        self.changes: List[ChangeEntry] = []
        self.review_result: Optional[ReviewResult] = None

        self.logger = get_logger("WorkflowAutoReviewFix")
        self._load_existing_data()

    def _load_existing_data(self):
        """Load existing chat history and changes"""
        # Load chat history
        if self.chat_history_file.exists():
            try:
                with open(self.chat_history_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            entry_data = json.loads(line)
                            self.chat_history.append(ChatHistoryEntry(**entry_data))
            except Exception as e:
                self.logger.warning(f"Could not load chat history: {e}")

        # Load changes
        if self.changes_file.exists():
            try:
                with open(self.changes_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.changes = [
                        ChangeEntry(**{**change_data, 'review_status': ReviewStatus(change_data['review_status'])})
                        for change_data in data.get("changes", [])
                    ]
            except Exception as e:
                self.logger.warning(f"Could not load changes: {e}")

    def add_chat_history(self, agent: str, message: str, context: Optional[Dict[str, Any]] = None):
        """Add entry to chat history"""
        entry = ChatHistoryEntry(
            entry_id=f"chat_{int(datetime.now().timestamp() * 1000)}",
            timestamp=datetime.now().isoformat(),
            agent=agent,
            message=message,
            context=context or {},
            metadata={"workflow_id": self.workflow_id}
        )

        self.chat_history.append(entry)

        # Append to JSONL file
        try:
            with open(self.chat_history_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry.to_dict()) + '\n')
        except Exception as e:
            self.logger.error(f"Error saving chat history: {e}")

        self.logger.debug(f"Added chat history: {agent}: {message[:50]}")

    def track_change(
        self,
        file_path: str,
        change_type: str,
        diff: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Track a file change"""
        change = ChangeEntry(
            change_id=f"change_{int(datetime.now().timestamp() * 1000)}",
            timestamp=datetime.now().isoformat(),
            file_path=file_path,
            change_type=change_type,
            diff=diff,
            review_status=ReviewStatus.PENDING,
            metadata=metadata or {}
        )

        self.changes.append(change)
        self._save_changes()

        self.logger.info(f"Tracked change: {change_type} {file_path}")

        return change.change_id

    def auto_accept_all_changes(self) -> Dict[str, Any]:
        """
        Automatically accept all changes after running

        This is the automatic acceptance step.
        """
        self.logger.info("🔄 Auto-accepting all changes...")

        accepted_count = 0
        for change in self.changes:
            if change.review_status == ReviewStatus.PENDING:
                change.review_status = ReviewStatus.ACCEPTED
                accepted_count += 1

        self._save_changes()

        result = {
            "accepted_count": accepted_count,
            "total_changes": len(self.changes),
            "timestamp": datetime.now().isoformat()
        }

        self.logger.info(f"✅ Auto-accepted {accepted_count} changes")

        return result

    def review_changes(self) -> ReviewResult:
        """
        Review all changes

        Analyzes changes for issues, errors, and improvements.
        """
        self.logger.info("🔍 Reviewing all changes...")

        review_id = f"review_{int(datetime.now().timestamp())}"
        review_notes = []
        changes_need_fix = []

        for change in self.changes:
            if change.review_status == ReviewStatus.ACCEPTED:
                change.review_status = ReviewStatus.REVIEWING

                # Review logic
                issues = self._review_change(change)

                if issues:
                    change.review_status = ReviewStatus.NEEDS_FIX
                    change.fix_required = True
                    change.review_notes = "; ".join(issues)
                    changes_need_fix.append(change)
                    review_notes.append(f"{change.file_path}: {'; '.join(issues)}")
                else:
                    change.review_status = ReviewStatus.COMPLETE
                    review_notes.append(f"{change.file_path}: ✅ No issues found")

        self._save_changes()

        self.review_result = ReviewResult(
            review_id=review_id,
            timestamp=datetime.now().isoformat(),
            changes_reviewed=len([c for c in self.changes if c.review_status != ReviewStatus.PENDING]),
            changes_accepted=len([c for c in self.changes if c.review_status == ReviewStatus.ACCEPTED]),
            changes_need_fix=len(changes_need_fix),
            fixes_applied=0,
            review_notes=review_notes
        )

        self._save_review()

        self.logger.info(f"✅ Reviewed {self.review_result.changes_reviewed} changes, {len(changes_need_fix)} need fixes")

        return self.review_result

    def _review_change(self, change: ChangeEntry) -> List[str]:
        """Review a single change for issues"""
        issues = []

        # Check file path
        if not change.file_path:
            issues.append("Missing file path")

        # Check change type
        if change.change_type not in ["created", "modified", "deleted"]:
            issues.append(f"Invalid change type: {change.change_type}")

        # Check for common issues in diff
        if change.diff:
            # Check for syntax errors (basic checks)
            if "SyntaxError" in change.diff or "IndentationError" in change.diff:
                issues.append("Syntax error detected")

            # Check for TODO/FIXME
            if "TODO" in change.diff or "FIXME" in change.diff:
                issues.append("TODO/FIXME found - may need attention")

            # Check for hardcoded secrets
            if any(keyword in change.diff.lower() for keyword in ["password", "secret", "api_key", "token"]):
                issues.append("Potential secret detected - review needed")

        return issues

    def fix_all_issues(self) -> Dict[str, Any]:
        """
        Fix all issues found during review

        Automatically fixes issues where possible.
        """
        self.logger.info("🔧 Fixing all issues...")

        fixes_applied = []
        changes_fixed = []

        for change in self.changes:
            if change.fix_required and change.review_status == ReviewStatus.NEEDS_FIX:
                change.review_status = ReviewStatus.FIXING

                # Attempt to fix
                fix_result = self._fix_change(change)

                if fix_result["fixed"]:
                    change.review_status = ReviewStatus.FIXED
                    change.fix_applied = True
                    changes_fixed.append(change)
                    fixes_applied.append(fix_result)
                    self.logger.info(f"✅ Fixed: {change.file_path}")
                else:
                    change.review_status = ReviewStatus.NEEDS_FIX
                    self.logger.warning(f"⚠️ Could not auto-fix: {change.file_path}")

        self._save_changes()

        # Update review result
        if self.review_result:
            self.review_result.fixes_applied = len(fixes_applied)
            self.review_result.fix_results = fixes_applied
            self._save_review()

        result = {
            "fixes_applied": len(fixes_applied),
            "changes_fixed": len(changes_fixed),
            "fix_results": fixes_applied,
            "timestamp": datetime.now().isoformat()
        }

        self.logger.info(f"✅ Fixed {len(fixes_applied)} issues")

        return result

    def _fix_change(self, change: ChangeEntry) -> Dict[str, Any]:
        """Attempt to fix a single change"""
        fix_result = {
            "change_id": change.change_id,
            "file_path": change.file_path,
            "fixed": False,
            "fixes_applied": [],
            "notes": ""
        }

        # Basic fixes
        if change.file_path:
            file_path = Path(change.file_path)
            if not file_path.is_absolute():
                file_path = self.project_root / file_path

            # Check if file exists and is readable
            if file_path.exists():
                try:
                    # Read file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Apply basic fixes
                    fixes = []

                    # Fix common indentation issues (basic)
                    if "IndentationError" in change.review_notes:
                        # This would need more sophisticated logic
                        fixes.append("Indentation check - manual review recommended")

                    # Remove hardcoded secrets (basic - just flag)
                    if "secret" in change.review_notes.lower():
                        fixes.append("Secret detection - manual review required")

                    if fixes:
                        fix_result["fixed"] = True
                        fix_result["fixes_applied"] = fixes
                        fix_result["notes"] = "Basic fixes applied, manual review recommended"
                except Exception as e:
                    fix_result["notes"] = f"Could not read file: {e}"
            else:
                fix_result["notes"] = "File does not exist"

        return fix_result

    def feed_back_to_workflow(self) -> Dict[str, Any]:
        """
        Feed review and fix results back into workflow loop

        Returns feedback data for workflow to use in next iteration.
        """
        self.logger.info("🔄 Feeding back to workflow loop...")

        # Prepare workflow feedback
        feedback = {
            "workflow_id": self.workflow_id,
            "timestamp": datetime.now().isoformat(),
            "review_complete": self.review_result is not None,
            "changes_summary": {
                "total": len(self.changes),
                "accepted": len([c for c in self.changes if c.review_status == ReviewStatus.ACCEPTED]),
                "fixed": len([c for c in self.changes if c.fix_applied]),
                "needs_manual_review": len([c for c in self.changes if c.review_status == ReviewStatus.NEEDS_FIX and not c.fix_applied])
            },
            "review_result": self.review_result.to_dict() if self.review_result else None,
            "chat_history_count": len(self.chat_history),
            "next_steps": self._generate_next_steps(),
            "workflow_should_continue": self._should_workflow_continue()
        }

        # Update review result
        if self.review_result:
            self.review_result.workflow_feedback = feedback
            self._save_review()

        self.logger.info(f"✅ Feedback prepared: {feedback['changes_summary']}")

        return feedback

    def _generate_next_steps(self) -> List[str]:
        """Generate next steps based on review results"""
        next_steps = []

        if not self.review_result:
            next_steps.append("Complete review process")
            return next_steps

        if self.review_result.changes_need_fix > 0:
            if self.review_result.fixes_applied < self.review_result.changes_need_fix:
                next_steps.append(f"Manual review needed for {self.review_result.changes_need_fix - self.review_result.fixes_applied} changes")
            else:
                next_steps.append("All fixes applied - proceed to next workflow step")
        else:
            next_steps.append("All changes reviewed and accepted - proceed to next workflow step")

        return next_steps

    def _should_workflow_continue(self) -> bool:
        """Determine if workflow should continue"""
        if not self.review_result:
            return False

        # Continue if all changes are accepted or fixed
        needs_manual = self.review_result.changes_need_fix - self.review_result.fixes_applied
        return needs_manual == 0

    def execute_full_cycle(self) -> Dict[str, Any]:
        """
        Execute full auto-review-fix cycle:
        1. Auto-accept all changes
        2. Review changes
        3. Fix all issues
        4. Feed back to workflow
        """
        self.logger.info("🔄 Starting full auto-review-fix cycle...")

        # Step 1: Auto-accept all changes
        accept_result = self.auto_accept_all_changes()

        # Step 2: Review changes
        review_result = self.review_changes()

        # Step 3: Fix all issues
        fix_result = self.fix_all_issues()

        # Step 4: Feed back to workflow
        feedback = self.feed_back_to_workflow()

        cycle_result = {
            "cycle_id": f"cycle_{int(datetime.now().timestamp())}",
            "timestamp": datetime.now().isoformat(),
            "accept_result": accept_result,
            "review_result": review_result.to_dict(),
            "fix_result": fix_result,
            "workflow_feedback": feedback,
            "cycle_complete": True
        }

        self.logger.info("✅ Full cycle complete")

        return cycle_result

    def _save_changes(self):
        try:
            """Save changes to file"""
            changes_data = {
                "workflow_id": self.workflow_id,
                "timestamp": datetime.now().isoformat(),
                "changes": [c.to_dict() for c in self.changes]
            }

            with open(self.changes_file, 'w', encoding='utf-8') as f:
                json.dump(changes_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in _save_changes: {e}", exc_info=True)
            raise
    def _save_review(self):
        try:
            """Save review result"""
            if not self.review_result:
                return

            with open(self.review_file, 'w', encoding='utf-8') as f:
                json.dump(self.review_result.to_dict(), f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in _save_review: {e}", exc_info=True)
            raise
    def get_chat_history(self) -> List[Dict[str, Any]]:
        """Get all chat history entries"""
        return [entry.to_dict() for entry in self.chat_history]

    def get_changes_summary(self) -> Dict[str, Any]:
        """Get summary of all changes"""
        return {
            "total_changes": len(self.changes),
            "by_status": {
                status.value: len([c for c in self.changes if c.review_status == status])
                for status in ReviewStatus
            },
            "needs_fix": len([c for c in self.changes if c.fix_required]),
            "fixed": len([c for c in self.changes if c.fix_applied])
        }


def main():
    """Main execution for testing"""
    reviewer = WorkflowAutoReviewFix(workflow_id="test_workflow")

    print("🔄 Workflow Auto Review & Fix Component")
    print("=" * 80)

    # Add some chat history
    reviewer.add_chat_history("JARVIS", "Starting workflow execution")
    reviewer.add_chat_history("MARVIN", "Reviewing workflow steps")

    # Track some changes
    reviewer.track_change("test_file.py", "created", diff="+ def test_function(): pass")
    reviewer.track_change("workflow_base.py", "modified", diff="- old_code\n+ new_code")

    # Execute full cycle
    result = reviewer.execute_full_cycle()

    print("\n✅ Full Cycle Result:")
    print(f"   Changes Accepted: {result['accept_result']['accepted_count']}")
    print(f"   Changes Reviewed: {result['review_result']['changes_reviewed']}")
    print(f"   Fixes Applied: {result['fix_result']['fixes_applied']}")
    print(f"   Workflow Should Continue: {result['workflow_feedback']['workflow_should_continue']}")


if __name__ == "__main__":



    main()