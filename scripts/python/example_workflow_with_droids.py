"""
Example Workflow Using Droid Actor System
Demonstrates how to use droid actors for workflow verification.
"""

import sys
from pathlib import Path
from typing import Dict, Any
import json
from datetime import datetime

# Add scripts/python to path for imports
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from droid_actor_system import verify_workflow_with_droid_actor
from jarvis_helpdesk_integration import execute_jarvis_workflow_with_helpdesk
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
import logging
logger = logging.getLogger("example_workflow_with_droids")




# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def example_technical_workflow(workflow_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Example technical workflow executor.
    This would be replaced with actual JARVIS workflow execution.
    """
    print(f"Executing technical workflow: {workflow_data.get('workflow_name')}")

    # Simulate workflow execution
    return {
        "success": True,
        "result": "Workflow completed successfully",
        "execution_time": 1.5,
        "output": "System diagnostics complete"
    }


def example_security_workflow(workflow_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Example security workflow executor.
    """
    print(f"Executing security workflow: {workflow_data.get('workflow_name')}")

    return {
        "success": True,
        "result": "Security scan complete",
        "threats_found": 0,
        "recommendations": ["All systems secure"]
    }


def example_knowledge_workflow(workflow_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Example knowledge aggregation workflow executor.
    """
    print(f"Executing knowledge workflow: {workflow_data.get('workflow_name')}")

    return {
        "success": True,
        "result": "Knowledge aggregated",
        "patterns_extracted": 5,
        "matrix_updated": True
    }


def main():
    try:
        """Run example workflows with droid actor verification."""
        project_root = Path("D:/Dropbox/my_projects")

        print("=" * 60)
        print("Example Workflows with Droid Actor System")
        print("=" * 60)

        # Example 1: Technical workflow (should route to R2-D2)
        print("\n" + "=" * 60)
        print("Example 1: Technical Workflow")
        print("=" * 60)

        technical_workflow = {
            "workflow_id": "tech_001",
            "workflow_name": "System Diagnostics",
            "workflow_type": "technical",
            "description": "Run system diagnostics and repair",
            "steps": [
                {"step": 1, "action": "scan_system"},
                {"step": 2, "action": "identify_issues"},
                {"step": 3, "action": "apply_fixes"}
            ]
        }

        success, results = execute_jarvis_workflow_with_helpdesk(
            technical_workflow,
            example_technical_workflow,
            project_root=project_root,
            require_verification=True,
            ingest_to_r5=True
        )

        print(f"\nWorkflow Status: {'SUCCESS' if success else 'FAILED'}")
        if results.get("verification", {}).get("droid_assignment"):
            droid = results["verification"]["droid_assignment"]
            print(f"Assigned Droid: {droid.get('droid_name', 'Unknown')}")
            print(f"Droid Response: {droid.get('persona_response', 'N/A')}")

        # Example 2: Security workflow (should route to K-2SO)
        print("\n" + "=" * 60)
        print("Example 2: Security Workflow")
        print("=" * 60)

        security_workflow = {
            "workflow_id": "sec_001",
            "workflow_name": "Threat Analysis",
            "workflow_type": "security",
            "description": "Analyze security threats",
            "steps": [
                {"step": 1, "action": "scan_threats"},
                {"step": 2, "action": "assess_risk"},
                {"step": 3, "action": "recommend_actions"}
            ]
        }

        success, results = execute_jarvis_workflow_with_helpdesk(
            security_workflow,
            example_security_workflow,
            project_root=project_root,
            require_verification=True,
            ingest_to_r5=True
        )

        print(f"\nWorkflow Status: {'SUCCESS' if success else 'FAILED'}")
        if results.get("verification", {}).get("droid_assignment"):
            droid = results["verification"]["droid_assignment"]
            print(f"Assigned Droid: {droid.get('droid_name', 'Unknown')}")
            print(f"Droid Response: {droid.get('persona_response', 'N/A')}")

        # Example 3: Knowledge workflow (should route to R5-D4)
        print("\n" + "=" * 60)
        print("Example 3: Knowledge Workflow")
        print("=" * 60)

        knowledge_workflow = {
            "workflow_id": "know_001",
            "workflow_name": "Knowledge Aggregation",
            "workflow_type": "knowledge",
            "description": "Aggregate and extract patterns",
            "steps": [
                {"step": 1, "action": "aggregate_sessions"},
                {"step": 2, "action": "extract_patterns"},
                {"step": 3, "action": "update_matrix"}
            ]
        }

        success, results = execute_jarvis_workflow_with_helpdesk(
            knowledge_workflow,
            example_knowledge_workflow,
            project_root=project_root,
            require_verification=True,
            ingest_to_r5=True
        )

        print(f"\nWorkflow Status: {'SUCCESS' if success else 'FAILED'}")
        if results.get("verification", {}).get("droid_assignment"):
            droid = results["verification"]["droid_assignment"]
            print(f"Assigned Droid: {droid.get('droid_name', 'Unknown')}")
            print(f"Droid Response: {droid.get('persona_response', 'N/A')}")

        print("\n" + "=" * 60)
        print("All Examples Complete")
        print("=" * 60)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()