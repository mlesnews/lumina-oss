#!/usr/bin/env python3
"""
Demonstration of The Shrink - Deep Cycle Introspection

This script demonstrates how The Shrink performs psychological analysis
on workflows, detecting patterns, assessing health, and generating insights.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from shrink_mental_health_verifier import (
    TheShrink,
    IntrospectionDepth,
    PsychologicalHealthLevel,
    CognitivePattern
)

def demonstrate_shrink_introspection():
    """Demonstrate The Shrink's deep cycle introspection capabilities"""

    print("="*70)
    print("🧠 THE SHRINK - DEEP CYCLE INTROSPECTION DEMONSTRATION")
    print("="*70)
    print()

    # Initialize The Shrink
    shrink = TheShrink()

    # Example 1: Healthy Workflow
    print("\n" + "="*70)
    print("EXAMPLE 1: HEALTHY WORKFLOW")
    print("="*70)

    healthy_workflow = {
        "type": "code_implementation",
        "steps": [
            {"id": 1, "type": "analysis", "completed": True},
            {"id": 2, "type": "design", "completed": True},
            {"id": 3, "type": "implementation", "completed": True},
            {"id": 4, "type": "testing", "completed": True},
            {"id": 5, "type": "verification", "completed": True}
        ],
        "decisions": [
            {"decision": "Use proven pattern", "confidence": 0.7, "evidence": ["past success", "documentation"]},
            {"decision": "Add comprehensive tests", "confidence": 0.8, "evidence": ["best practices"]}
        ],
        "outcomes": [
            {"step": 1, "success": True},
            {"step": 2, "success": True},
            {"step": 3, "success": True},
            {"step": 4, "success": True},
            {"step": 5, "success": True}
        ],
        "confidence_scores": [0.7, 0.8, 0.75, 0.8, 0.85],
        "errors": [],
        "verifications": [
            {"type": "pre_workflow", "passed": True},
            {"type": "post_workflow", "passed": True}
        ],
        "declared_complete": True,
        "pattern_references": ["pattern1"],
        "novel_approaches": ["optimization"],
        "evidence_considered": [
            {"evidence": "supports decision", "supports": True},
            {"evidence": "challenges decision", "supports": False}
        ],
        "well_documented": True,
        "uncertainty_acknowledged": True,
        "limitations_documented": True
    }

    profile1 = shrink.shrink_workflow(
        workflow_id="healthy_workflow_001",
        workflow_data=healthy_workflow,
        depth=IntrospectionDepth.DEEP
    )

    # Example 2: Problematic Workflow (Overconfident, Completion Bias)
    print("\n" + "="*70)
    print("EXAMPLE 2: PROBLEMATIC WORKFLOW (Overconfident, Completion Bias)")
    print("="*70)

    problematic_workflow = {
        "type": "feature_implementation",
        "steps": [
            {"id": 1, "type": "design", "completed": True},
            {"id": 2, "type": "implementation", "completed": True},
            {"id": 3, "type": "verification", "completed": False}  # Incomplete!
        ],
        "decisions": [
            {"decision": "Skip testing - looks good", "confidence": 0.95, "evidence": ["looks good"]},
            {"decision": "Declare complete early", "confidence": 0.98, "evidence": ["almost done"]}
        ],
        "outcomes": [
            {"step": 1, "success": True},
            {"step": 2, "success": True}
        ],
        "confidence_scores": [0.95, 0.98, 0.9],
        "errors": [
            {"type": "syntax_error", "recovered": True},
            {"type": "logic_error", "recovered": False}
        ],
        "verifications": [],  # No verifications!
        "declared_complete": True,  # Declared complete but step 3 incomplete!
        "pattern_references": ["pattern1", "pattern2", "pattern3"],
        "novel_approaches": [],
        "evidence_considered": [
            {"evidence": "supports decision", "supports": True},
            {"evidence": "supports decision", "supports": True}
        ],
        "well_documented": False,
        "uncertainty_acknowledged": False,
        "limitations_documented": False
    }

    profile2 = shrink.shrink_workflow(
        workflow_id="problematic_workflow_001",
        workflow_data=problematic_workflow,
        previous_workflows=[healthy_workflow],
        depth=IntrospectionDepth.DEEP
    )

    # Example 3: System-Wide Deep Cycle Introspection
    print("\n" + "="*70)
    print("EXAMPLE 3: SYSTEM-WIDE DEEP CYCLE INTROSPECTION")
    print("="*70)

    system_introspection = shrink.deep_cycle_introspection(
        workflow_ids=["healthy_workflow_001", "problematic_workflow_001"],
        depth=IntrospectionDepth.PROFOUND
    )

    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\n📊 Workflows Analyzed: {len(system_introspection.workflow_profiles)}")
    print(f"🏥 Overall System Health: {system_introspection.overall_health.value.upper()}")
    print(f"⚠️  Issues Detected: {len(system_introspection.detected_issues)}")
    print(f"💡 Recommendations: {len(system_introspection.recommendations)}")
    print(f"🚨 Intervention Needed: {system_introspection.intervention_needed}")

    if system_introspection.detected_issues:
        print("\n🔴 Detected Issues:")
        for issue in system_introspection.detected_issues:
            print(f"   - {issue}")

    if system_introspection.recommendations:
        print("\n💡 Recommendations:")
        for rec in system_introspection.recommendations[:5]:  # Top 5
            print(f"   - {rec}")

    print("\n" + "="*70)
    print("DEMONSTRATION COMPLETE")
    print("="*70)

if __name__ == "__main__":
    demonstrate_shrink_introspection()

