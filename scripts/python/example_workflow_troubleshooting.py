#!/usr/bin/env python3
"""
Example: Universal Workflow Troubleshooting Usage

Demonstrates how to inject troubleshooting into workflows.

@ai @jarvis @marvin @rr[#roast + #repair] @decide[#decisioning + @aiq + @jc[#jedicouncil + #jedihighcouncil]]

Tags: #TROUBLESHOOTING #EXAMPLE #WORKFLOW @JARVIS @TEAM
"""

from universal_workflow_troubleshooting import (
    UniversalWorkflowTroubleshooting,
    TroubleshootingMode,
    EvaluationLevel,
    troubleshoot
)


# Example 1: Using the decorator
@troubleshoot(
    mode=TroubleshootingMode.PRE_WORKFLOW,
    level=EvaluationLevel.STANDARD,
    auto_repair=False,
    require_approval=False
)
def example_workflow(workflow_data: dict):
    """Example workflow with troubleshooting injected"""
    print(f"Executing workflow: {workflow_data.get('workflow_name', 'Unknown')}")
    # Your workflow logic here
    return {"status": "success", "result": "Workflow completed"}


# Example 2: Direct evaluation
def example_direct_evaluation():
    """Example of direct workflow evaluation"""
    troubleshooting = UniversalWorkflowTroubleshooting()

    workflow_data = {
        "workflow_id": "example_001",
        "workflow_name": "Example Workflow",
        "steps": ["step1", "step2", "step3"],
        "urgency": "medium",
        "complexity": "medium"
    }

    # Evaluate workflow
    evaluation = troubleshooting.evaluate_workflow(
        workflow_data,
        mode=TroubleshootingMode.PRE_WORKFLOW,
        level=EvaluationLevel.STANDARD,
        auto_repair=False,
        require_approval=False
    )

    print(f"\n{'='*70}")
    print(f"Workflow Evaluation: {evaluation.workflow_name}")
    print(f"{'='*70}")
    print(f"Should proceed: {evaluation.should_proceed}")
    print(f"Roast score: {evaluation.roast_score:.2f}")
    print(f"Findings: {len(evaluation.roast_findings)}")
    print(f"Repair needed: {evaluation.repair_needed}")
    print(f"Decision: {evaluation.decision_outcome}")
    print(f"Decision confidence: {evaluation.decision_confidence:.2f}")

    if evaluation.jedi_council_approval:
        print(f"Jedi Council: {'APPROVED' if evaluation.jedi_council_approval.get('approved') else 'REJECTED'}")

    return evaluation


# Example 3: Deep evaluation with Jedi Council approval
def example_deep_evaluation():
    """Example of deep evaluation requiring Jedi Council approval"""
    troubleshooting = UniversalWorkflowTroubleshooting()

    workflow_data = {
        "workflow_id": "critical_001",
        "workflow_name": "Critical Production Workflow",
        "steps": ["critical_step1", "critical_step2"],
        "urgency": "high",
        "complexity": "high"
    }

    evaluation = troubleshooting.evaluate_workflow(
        workflow_data,
        mode=TroubleshootingMode.PRE_WORKFLOW,
        level=EvaluationLevel.JEDI_COUNCIL,
        auto_repair=False,
        require_approval=True
    )

    print(f"\n{'='*70}")
    print(f"Deep Evaluation: {evaluation.workflow_name}")
    print(f"{'='*70}")
    print(f"Should proceed: {evaluation.should_proceed}")
    print(f"Requires approval: {evaluation.requires_approval}")

    if evaluation.jedi_council_approval:
        approval = evaluation.jedi_council_approval
        print(f"Jedi Council: {'APPROVED' if approval.get('approved') else 'REJECTED'}")
        if approval.get('votes'):
            print(f"Votes: {len(approval.get('votes', []))}")

    return evaluation


if __name__ == "__main__":
    print("=" * 70)
    print("🔍 Universal Workflow Troubleshooting - Examples")
    print("=" * 70)

    # Example 1: Decorator usage
    print("\n1. Decorator Usage:")
    print("-" * 70)
    try:
        result = example_workflow({
            "workflow_id": "decorator_001",
            "workflow_name": "Decorator Example Workflow"
        })
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")

    # Example 2: Direct evaluation
    print("\n2. Direct Evaluation:")
    print("-" * 70)
    try:
        evaluation = example_direct_evaluation()
        print(f"   ✅ Evaluation complete")
    except Exception as e:
        print(f"   Error: {e}")

    # Example 3: Deep evaluation (commented out to avoid long execution)
    # print("\n3. Deep Evaluation with Jedi Council:")
    # print("-" * 70)
    # try:
    #     evaluation = example_deep_evaluation()
    #     print(f"   ✅ Deep evaluation complete")
    # except Exception as e:
    #     print(f"   Error: {e}")

    print("\n" + "=" * 70)
    print("✅ Examples complete!")
    print("=" * 70)
