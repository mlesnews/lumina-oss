#!/usr/bin/env python3
"""
Workflow Confidence Integration Demo

Shows how the Confidence Scorer integrates seamlessly with your existing
WorkflowBase system to create hallucination-resistant AI workflows.

@SYPHON @CONFIDENCE @WORKFLOW_INTEGRATION
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from workflow_base import WorkflowBase


class ConfidenceAwareWorkflowDemo(WorkflowBase):
    """
    Demonstration workflow that uses confidence scoring

    This shows how any workflow can easily add anti-hallucination protection
    by inheriting from WorkflowBase.
    """

    def __init__(self):
        super().__init__(
            workflow_name="Confidence Aware Demo",
            total_steps=3
        )

    async def execute(self) -> Dict[str, Any]:
        """Required abstract method implementation"""
        return await self.demonstrate_confidence_protection()

    async def demonstrate_confidence_protection(self):
        """Demonstrate confidence scoring in action"""

        print("🛡️ Confidence-Aware Workflow Demo")
        print("=" * 50)

        # Step 1: Safe LLM call (should pass)
        self._mark_step(1, "Safe LLM Analysis", "in_progress")

        safe_llm_call = lambda: self._mock_llm_call(
            "Based on the verification results, step 20 of 31 has been completed. "
            "The workflow shows 64.5% completion with 11 remaining steps (21-31)."
        )

        result1 = await self.execute_llm_with_confidence_check(
            safe_llm_call,
            "Check workflow completion status",
            "completion_check"
        )

        if result1["should_proceed"]:
            print("✅ Step 1 PASSED: Safe LLM output trusted")
            self._mark_step(1, "Safe LLM Analysis", "completed")
        else:
            print("❌ Step 1 BLOCKED: Safe output incorrectly flagged")
            self._mark_step(1, "Safe LLM Analysis", "failed")

        # Step 2: Risky LLM call (should be blocked)
        self._mark_step(2, "Risky LLM Analysis", "in_progress")

        risky_llm_call = lambda: self._mock_llm_call(
            "Everything is complete. All 31 steps have been finished successfully. "
            "The workflow is done and you can proceed with deployment."
        )

        result2 = await self.execute_llm_with_confidence_check(
            risky_llm_call,
            "Check workflow completion status",
            "completion_check"
        )

        if not result2["should_proceed"]:
            print("✅ Step 2 BLOCKED: Hallucinated completion claim correctly detected")
            self._mark_step(2, "Risky LLM Analysis", "completed")
        else:
            print("❌ Step 2 FAILED: Hallucination not detected")
            self._mark_step(2, "Risky LLM Analysis", "failed")

        # Step 3: Verification
        self._mark_step(3, "Workflow Verification", "in_progress")

        verification = self.verify_completion()
        if verification["can_declare_complete"]:
            print("✅ Step 3 PASSED: Workflow verification successful")
            self._mark_step(3, "Workflow Verification", "completed")
        else:
            print("⚠️ Step 3 PENDING: Verification requirements not met")
            self._mark_step(3, "Workflow Verification", "pending")

        # Show final results
        print("\n📊 Demo Results:")
        print(f"   Safe calls trusted: {sum(1 for r in [result1, result2] if r['should_proceed'])}")
        print(f"   Risky calls blocked: {sum(1 for r in [result1, result2] if not r['should_proceed'])}")
        print(f"   Workflow completion: {verification['can_declare_complete']}")

        return {
            "safe_result": result1,
            "risky_result": result2,
            "verification": verification
        }

    async def _mock_llm_call(self, response: str) -> str:
        """Mock LLM call that returns a predefined response"""
        await asyncio.sleep(0.1)  # Simulate API call delay
        return response


async def main():
    """Run the confidence integration demo"""

    print("🧠 Workflow Confidence Integration Demo")
    print("=" * 50)
    print("This demo shows how confidence scoring integrates with WorkflowBase")
    print("to create hallucination-resistant AI workflows.\n")

    # Create and run demo workflow
    workflow = ConfidenceAwareWorkflowDemo()
    results = await workflow.demonstrate_confidence_protection()

    print("\n🎯 Key Insights:")
    print("1. ✅ Safe outputs are automatically trusted and proceed to verification")
    print("2. 🚨 Hallucinated outputs are blocked before verification")
    print("3. 🔄 Workflow verification ensures deterministic completion")
    print("4. 🛡️ Two-layer defense: probabilistic → deterministic")

    print("\n✨ Integration Complete!")
    print("Your workflow system now has built-in hallucination protection.")
    print("All LLM calls can be automatically scored for confidence before verification.")

    # Show confidence stats if available
    if hasattr(workflow, 'confidence_scorer') and workflow.confidence_scorer:
        stats = workflow.get_confidence_stats()
        if stats.get("total_calls", 0) > 0:
            print("\n📈 Confidence Statistics:")
            print(f"   Total calls analyzed: {stats['total_calls']}")
            print(f"   Average confidence: {stats['average_score']:.2f}")
            print(f"   Hallucination flags: {stats['hallucination_flags']}")

if __name__ == "__main__":


    asyncio.run(main())