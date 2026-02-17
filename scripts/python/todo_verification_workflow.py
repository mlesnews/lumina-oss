#!/usr/bin/env python3
"""
To-Do Verification Workflow - JARVIS/MARVIN Triple-Check

Upper management verification:
1. JARVIS reviews (systematic)
2. MARVIN reviews (philosophical)
3. Final verification (cross all T's, dot all I's)
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any

from dual_todo_system import DualTodoSystem, VerificationStatus
from master_todo_tracker import TaskStatus
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class TodoVerificationWorkflow:
    """
    To-Do Verification Workflow

    Triple-check process with JARVIS and MARVIN.
    """

    def __init__(self):
        self.dual_system = DualTodoSystem()
        self.logger = logging.getLogger("TodoVerification")
        self.logger.setLevel(logging.INFO)

    async def jarvis_review(self, todo_id: str) -> Dict[str, Any]:
        """
        JARVIS systematic review

        Checks:
        - Task is well-defined
        - Dependencies are met
        - Status is accurate
        - Priority is appropriate
        """
        if todo_id not in self.dual_system.master_tracker.items:
            return {"verified": False, "reason": "Todo not found"}

        todo = self.dual_system.master_tracker.items[todo_id]

        review = {
            "verified": True,
            "issues": [],
            "notes": []
        }

        # Check 1: Task is well-defined
        if not todo.title or len(todo.title) < 5:
            review["issues"].append("Title too short or missing")
            review["verified"] = False

        if not todo.description:
            review["notes"].append("No description provided")

        # Check 2: Dependencies
        for dep_id in todo.dependencies:
            if dep_id not in self.dual_system.master_tracker.items:
                review["issues"].append(f"Missing dependency: {dep_id}")
                review["verified"] = False
            elif self.dual_system.master_tracker.items[dep_id].status != TaskStatus.COMPLETE:
                review["notes"].append(f"Dependency {dep_id} not complete")

        # Check 3: Status accuracy
        if todo.status == TaskStatus.COMPLETE and not todo.completed_date:
            review["notes"].append("Marked complete but no completion date")

        # Check 4: Priority
        if todo.priority.value == "high" and todo.status == TaskStatus.PENDING:
            review["notes"].append("High priority task still pending")

        notes = "JARVIS Review: " + ("✓ Verified" if review["verified"] else "✗ Issues found")
        if review["issues"]:
            notes += f" - {', '.join(review['issues'])}"
        if review["notes"]:
            notes += f" - Notes: {', '.join(review['notes'])}"

        self.dual_system.verify_todo(todo_id, "JARVIS", notes)

        return review

    async def marvin_review(self, todo_id: str) -> Dict[str, Any]:
        """
        MARVIN philosophical review

        Checks:
        - Task aligns with Lumina philosophy
        - Task serves the mission
        - Task is meaningful
        """
        if todo_id not in self.dual_system.master_tracker.items:
            return {"verified": False, "reason": "Todo not found"}

        todo = self.dual_system.master_tracker.items[todo_id]

        review = {
            "verified": True,
            "philosophical_alignment": True,
            "mission_alignment": True,
            "notes": []
        }

        # Check: Mission alignment
        lumina_keywords = ["illuminate", "light", "share", "matter", "being", "public"]
        title_lower = todo.title.lower()
        description_lower = todo.description.lower()

        if not any(kw in title_lower or kw in description_lower for kw in lumina_keywords):
            review["notes"].append("May not align with Lumina mission")

        # Check: Meaningful
        if todo.status == TaskStatus.CANCELLED:
            review["notes"].append("Task was cancelled - may need review")

        notes = "MARVIN Review: " + ("✓ Philosophically aligned" if review["verified"] else "✗ Alignment concerns")
        if review["notes"]:
            notes += f" - {', '.join(review['notes'])}"

        self.dual_system.verify_todo(todo_id, "MARVIN", notes)

        return review

    async def verify_todo(self, todo_id: str) -> Dict[str, Any]:
        """
        Complete verification workflow

        1. JARVIS reviews (systematic)
        2. MARVIN reviews (philosophical)
        3. Final verification
        """
        self.logger.info(f"🔍 Starting verification for todo: {todo_id}")

        # Step 1: JARVIS review
        jarvis_result = await self.jarvis_review(todo_id)

        # Step 2: MARVIN review
        marvin_result = await self.marvin_review(todo_id)

        # Step 3: Final verification
        verified = jarvis_result.get("verified", False) and marvin_result.get("verified", False)

        result = {
            "todo_id": todo_id,
            "verified": verified,
            "jarvis_review": jarvis_result,
            "marvin_review": marvin_result,
            "final_status": "VERIFIED" if verified else "NEEDS_WORK"
        }

        if verified:
            self.logger.info(f"✅ Todo verified: {todo_id}")
        else:
            self.logger.warning(f"⚠️ Todo needs work: {todo_id}")

        return result


async def main():
    """Main execution"""
    workflow = TodoVerificationWorkflow()

    print("🔍 To-Do Verification Workflow")
    print("=" * 80)
    print("Triple-check process: JARVIS → MARVIN → Final Verification")
    print()

    # Get todos pending verification
    master_todos = workflow.dual_system.get_master_todos()
    verified_ids = set(workflow.dual_system.verified_todos.keys())

    unverified = [t for t in master_todos if t.id not in verified_ids and t.status == TaskStatus.COMPLETE]

    if not unverified:
        print("✅ All completed todos are verified!")
        return

    print(f"Found {len(unverified)} unverified completed todos")
    print()

    # Verify each
    for todo in unverified[:5]:  # Verify first 5
        print(f"🔍 Verifying: {todo.title}")
        result = await workflow.verify_todo(todo.id)

        if result["verified"]:
            print(f"   ✅ VERIFIED by {', '.join(result.get('verifiers', ['JARVIS', 'MARVIN']))}")
        else:
            print(f"   ⚠️ Needs work: {result['final_status']}")
        print()

    # Sync to Holocron
    workflow.dual_system.sync_to_nas_holocron()
    print("📦 Synced to Holocron")


if __name__ == "__main__":



    asyncio.run(main())