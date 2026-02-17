#!/usr/bin/env python3
"""
Silent Workflow Executor - No Explanations, Just Execute
Auto-digests to Holocrons/DB/YouTube with importance scoring
"""

import json
import sys
from pathlib import Path
from auto_workflow_processor import AutoWorkflowProcessor
from ai_overmind_analytics import AIOvermindAnalytics
from httw_wopr_integration import AIOvermindHTTWIntegration

class SilentWorkflowExecutor:
    """Execute workflows silently - auto-process to Holocrons/DB/YouTube"""

    def __init__(self):
        self.processor = AutoWorkflowProcessor()
        self.analytics = AIOvermindAnalytics()
        self.integration = AIOvermindHTTWIntegration()

    def execute(self, workflow_type: str, data: Dict = None) -> Dict:
        """
        Execute workflow silently - no explanations

        Returns:
            Result dict (minimal output)
        """
        workflow_data = data or {}
        workflow_data["workflow_type"] = workflow_type

        # Process workflow
        result = self.processor.process_workflow(workflow_data)

        # Integrate with HTTW/WOPR
        integration_result = self.integration.process_workflow_with_analytics(
            workflow_type,
            workflow_data.get("employee_id"),
            workflow_data
        )

        # Combine results
        final_result = {
            "executed": True,
            "importance": result.get("importance_symbol", "+"),
            "holocron_id": result.get("holocron_id"),
            "workflow_id": integration_result.get("workflow_id"),
            "timestamp": result.get("timestamp")
        }

        return final_result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(0)

    workflow_type = sys.argv[1]
    data = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}

    executor = SilentWorkflowExecutor()
    result = executor.execute(workflow_type, data)

    # Minimal output - just result
    print(json.dumps(result))
