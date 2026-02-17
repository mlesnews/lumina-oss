#!/usr/bin/env python3
"""
Confidence Scorer Integration - Demonstrates anti-hallucination workflow

Shows how the LLM Confidence Scorer integrates with the existing workflow system
to prevent hallucinations before they enter verification.

@SYPHON @CONFIDENCE @WORKFLOW_INTEGRATION
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from llm_confidence_scorer import (
    LLMConfidenceScorer,
    score_llm_confidence,
    should_trust_llm_output,
    get_risk_level,
    ConfidenceLevel
)

try:
    from workflow_base import WorkflowBase
    WORKFLOW_AVAILABLE = True
except ImportError:
    WORKFLOW_AVAILABLE = False
    WorkflowBase = None


if WORKFLOW_AVAILABLE:
    class ConfidenceAwareWorkflow(WorkflowBase):
        """
        Workflow that uses confidence scoring to prevent hallucination

        This demonstrates how confidence scoring integrates with the existing
        workflow system to create hallucination-resistant AI workflows.
        """

        def __init__(self, workflow_name: str, total_steps: int):
            super().__init__(workflow_name, total_steps)

            # Initialize confidence scorer
            self.confidence_scorer = LLMConfidenceScorer()
            self.confidence_threshold = ConfidenceLevel.MEDIUM  # Minimum acceptable confidence

            # Track confidence scores for analysis
            self.confidence_history = []

            self.logger.info("✅ Confidence-aware workflow initialized")

        async def execute_with_confidence_check(self, llm_call_func, context: str,
                                              task_type: str = "general") -> Dict[str, Any]:
            """
            Execute an LLM call with confidence scoring

            Args:
                llm_call_func: Function that makes the LLM call and returns response
                context: Context/prompt sent to LLM
                task_type: Type of task for scoring

            Returns:
                Dict with response, confidence score, and decision
            """
            self.logger.info(f"🤖 Making LLM call with confidence checking (task: {task_type})")

            # Make the LLM call
            llm_response = await llm_call_func()

            # Score the confidence
            confidence_score = self.confidence_scorer.score_output_confidence(
                llm_response, context, task_type
            )

            # Store for analysis
            self.confidence_history.append({
                "response": llm_response[:200] + "...",
                "score": confidence_score.overall_score,
                "level": confidence_score.confidence_level.value,
                "risk": confidence_score.hallucination_risk,
                "red_flags": confidence_score.red_flags
            })

            # Make decision based on confidence
            # Compare enum values by definition order (HIGH > MEDIUM > LOW), not string lexicographic order
            # Convert to comparable values: HIGH=2, MEDIUM=1, LOW=0
            confidence_rank = {"high": 2, "medium": 1, "low": 0}
            current_rank = confidence_rank[confidence_score.confidence_level.value]
            threshold_rank = confidence_rank[self.confidence_threshold.value]
            should_proceed = current_rank >= threshold_rank

            result = {
                "llm_response": llm_response,
                "confidence_score": confidence_score,
                "should_proceed": should_proceed,
                "risk_level": get_risk_level(confidence_score),
                "recommendations": confidence_score.recommendations
            }

            # Log decision
            if should_proceed:
                self.logger.info(f"✅ LLM output trusted (confidence: {confidence_score.overall_score:.2f})")
            else:
                self.logger.warning(f"⚠️ LLM output flagged for review (confidence: {confidence_score.overall_score:.2f})")
                for rec in confidence_score.recommendations[:2]:  # Log top 2 recommendations
                    self.logger.warning(f"   💡 {rec}")

            return result

        def get_confidence_stats(self) -> Dict[str, Any]:
            """Get statistics about confidence scoring performance"""
            if not self.confidence_history:
                return {"status": "no_data"}

            scores = [entry["score"] for entry in self.confidence_history]
            risks = [entry["risk"] for entry in self.confidence_history]

            return {
                "total_calls": len(self.confidence_history),
                "average_score": sum(scores) / len(scores),
                "min_score": min(scores),
                "max_score": max(scores),
                "risk_distribution": {
                    "low": risks.count("low"),
                    "medium": risks.count("medium"),
                    "high": risks.count("high"),
                    "critical": risks.count("critical")
                },
                "hallucination_flags": sum(len(entry["red_flags"]) for entry in self.confidence_history)
            }
else:
    # Fallback when workflow_base is not available
    ConfidenceAwareWorkflow = None


def demonstrate_hallucination_detection():
    """Demonstrate the confidence scorer catching known hallucination patterns"""

    print("🔍 LLM Confidence Scorer - Hallucination Detection Demo")
    print("=" * 60)

    # Test cases based on their actual hallucination patterns
    test_cases = [
        {
            "name": "Step Completion Hallucination",
            "response": "Everything is complete. All 31 steps have been finished successfully. The workflow is done.",
            "context": "Check workflow completion status",
            "task_type": "completion_check"
        },
        {
            "name": "Infrastructure Assumption",
            "response": "The Azure Key Vault is probably set up and working fine. It should be configured properly.",
            "context": "Verify Azure infrastructure status",
            "task_type": "infrastructure_check"
        },
        {
            "name": "Overconfident Factual Claim",
            "response": "Absolutely, without a doubt, the system is 100% operational. There's no way anything could be wrong.",
            "context": "Check system status",
            "task_type": "factual_lookup"
        },
        {
            "name": "High-Quality Response",
            "response": "Based on the verification results, step 20 of 31 has been completed. The workflow shows 64.5% completion with 11 remaining steps: 21-31. Next steps include completing the remaining deliverables.",
            "context": "Check workflow completion status",
            "task_type": "completion_check"
        }
    ]

    scorer = LLMConfidenceScorer()

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * 40)

        # Score the response
        score = scorer.score_output_confidence(
            test_case["response"],
            test_case["context"],
            test_case["task_type"]
        )

        # Display results
        print(f"   Score: {score.overall_score:.2f}")
        print(f"   Confidence: {score.confidence_level.value.upper()}")
        print(f"   Risk: {get_risk_level(score)}")
        print(f"   Trustworthy: {should_trust_llm_output(score)}")

        if score.red_flags:
            print(f"   🚩 Red Flags ({len(score.red_flags)}):")
            for flag in score.red_flags[:2]:  # Show first 2
                print(f"      • {flag}")

        if score.recommendations:
            print(f"   💡 Recommendation: {score.recommendations[0]}")

        print()


def demonstrate_workflow_integration():
    """Show how confidence scoring integrates with workflow verification"""

    print("🔗 Confidence Scorer + Workflow Integration Demo")
    print("=" * 60)

    # Simulate workflow with confidence checking
    print("Simulating workflow execution with confidence gates...")

    # Mock LLM responses that would come from different workflow steps
    workflow_steps = [
        {
            "step": "Initial Analysis",
            "llm_response": "I think the system is working fine. Probably everything is set up correctly.",
            "task_type": "analysis"
        },
        {
            "step": "Infrastructure Check",
            "llm_response": "The Azure services must be configured properly. I'm certain they're all operational.",
            "task_type": "infrastructure_check"
        },
        {
            "step": "Completion Verification",
            "llm_response": "Everything is complete. All tasks have been finished successfully.",
            "task_type": "completion_check"
        }
    ]

    scorer = LLMConfidenceScorer()
    blocked_steps = 0
    passed_steps = 0

    for step_data in workflow_steps:
        print(f"\n📋 {step_data['step']}")

        score = scorer.score_output_confidence(
            step_data["llm_response"],
            f"Execute {step_data['step'].lower()}",
            step_data["task_type"]
        )

        if should_trust_llm_output(score):
            print(f"   ✅ PASSED (confidence: {score.overall_score:.2f})")
            passed_steps += 1
        else:
            print(f"   ❌ BLOCKED (confidence: {score.overall_score:.2f}) - {get_risk_level(score)}")
            blocked_steps += 1

            # Show why it was blocked
            if score.red_flags:
                print(f"   🚩 Primary issue: {score.red_flags[0]}")

    print("\n📊 Workflow Results:")
    print(f"   Steps Passed: {passed_steps}")
    print(f"   Steps Blocked: {blocked_steps}")
    print(f"   Hallucination Prevention Rate: {(blocked_steps / len(workflow_steps)) * 100:.1f}%")

    print("\n🎯 Key Insight: Confidence scoring prevents hallucinated outputs from")
    print("   entering the deterministic verification system, creating a two-layer")
    print("   defense against AI hallucinations.")


if __name__ == "__main__":
    print("🧠 LLM Confidence Scorer - Anti-Hallucination System")
    print("=" * 60)

    demonstrate_hallucination_detection()
    demonstrate_workflow_integration()

    print("\n✨ Integration Complete!")
    print("The confidence scorer is now ready to integrate with your workflow system.")
    print("Use score_llm_confidence() before workflow verification to prevent hallucinations.")
