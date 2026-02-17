#!/usr/bin/env python3
"""
End-to-End Workflow Orchestrator
Complete one-shot workflow execution - eliminating "next steps"

Flow:
1. Request Analysis - Parse user request, identify all required actions
2. Dependency Resolution - Determine execution order
3. Approval Check - Identify critical actions requiring SMS approval
4. Pre-Approval Execution - Execute non-critical steps
5. Approval Request - Send SMS for critical actions
6. Post-Approval Execution - Execute approved critical actions
7. Verification - Verify all steps completed
8. Completion Report - Report final status

Tags: #WORKFLOW #ORCHESTRATOR #END_TO_END #ONE_SHOT #AUTOMATION
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("EndToEndWorkflow")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("EndToEndWorkflow")

try:
    from manus_cursor_ide_controller import MANUSCursorIDEController
    from dead_man_switch_sms_approval import DeadManSwitchSMSApproval
    COMPONENTS_AVAILABLE = True
except ImportError:
    COMPONENTS_AVAILABLE = False
    logger.warning("⚠️  Required components not available")


class EndToEndWorkflowOrchestrator:
    """End-to-End Workflow Orchestrator - One-Shot Execution"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "workflows"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        if COMPONENTS_AVAILABLE:
            self.manus = MANUSCursorIDEController(project_root)
            self.approval = DeadManSwitchSMSApproval(project_root)
        else:
            self.manus = None
            self.approval = None
            logger.warning("⚠️  MANUS and Approval systems not available")

        logger.info("✅ End-to-End Workflow Orchestrator initialized")

    def parse_request(self, user_request: str) -> Dict[str, Any]:
        """
        Parse user request into complete workflow

        Args:
            user_request: Natural language request

        Returns:
            Workflow definition with all steps
        """
        logger.info(f"📝 Parsing request: {user_request}")

        # This is a simplified parser - in production, use AI/NLP
        workflow = {
            "request": user_request,
            "steps": [],
            "requires_approval": [],
            "dependencies": {}
        }

        # Example: "Create a new file test.py with hello world"
        if "create" in user_request.lower() and "file" in user_request.lower():
            # Extract file path and content
            # Simplified - would use NLP in production
            workflow["steps"].append({
                "type": "file_create",
                "action": "create_file",
                "params": {
                    "path": "test.py",  # Would be extracted from request
                    "content": "# Hello World\nprint('Hello World')"
                },
                "requires_approval": False
            })

        return workflow

    def resolve_dependencies(self, workflow: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Resolve dependencies and determine execution order

        Args:
            workflow: Workflow definition

        Returns:
            Ordered list of steps
        """
        logger.info("🔗 Resolving dependencies...")

        # Simple dependency resolution - in production, use graph algorithm
        ordered_steps = []

        for step in workflow["steps"]:
            # Check if step has dependencies
            step_id = step.get("id", len(ordered_steps))
            dependencies = step.get("dependencies", [])

            # If no dependencies, can execute immediately
            if not dependencies:
                ordered_steps.append(step)
            else:
                # Insert after dependencies
                insert_index = len(ordered_steps)
                for dep_id in dependencies:
                    for i, existing_step in enumerate(ordered_steps):
                        if existing_step.get("id") == dep_id:
                            insert_index = max(insert_index, i + 1)
                            break
                ordered_steps.insert(insert_index, step)

        return ordered_steps

    def identify_critical_actions(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify actions requiring SMS approval

        Args:
            steps: List of workflow steps

        Returns:
            List of critical actions
        """
        critical_actions = []

        for step in steps:
            # Check if step requires approval
            if step.get("requires_approval", False):
                critical_actions.append(step)
            # Check action type
            elif step.get("type") in ["file_delete", "git_push"]:
                if step.get("params", {}).get("branch") in ["main", "master"]:
                    critical_actions.append(step)

        return critical_actions

    def execute_workflow(self, user_request: str) -> Dict[str, Any]:
        """
        Execute complete end-to-end workflow

        Args:
            user_request: Natural language request

        Returns:
            Execution results
        """
        logger.info("="*80)
        logger.info("🚀 EXECUTING END-TO-END WORKFLOW")
        logger.info("="*80)

        # Phase 1: Request Analysis
        workflow = self.parse_request(user_request)
        logger.info(f"✅ Parsed {len(workflow['steps'])} steps")

        # Phase 2: Dependency Resolution
        ordered_steps = self.resolve_dependencies(workflow)
        logger.info(f"✅ Resolved dependencies, {len(ordered_steps)} steps ordered")

        # Phase 3: Approval Check
        critical_actions = self.identify_critical_actions(ordered_steps)
        logger.info(f"⚠️  Identified {len(critical_actions)} critical actions requiring approval")

        # Phase 4: Pre-Approval Execution
        non_critical_steps = [s for s in ordered_steps if s not in critical_actions]
        pre_results = []
        if non_critical_steps and self.manus:
            logger.info(f"🔄 Executing {len(non_critical_steps)} non-critical steps...")
            for step in non_critical_steps:
                result = self._execute_step(step)
                pre_results.append(result)

        # Phase 5: Approval Request
        approval_results = []
        if critical_actions and self.approval:
            logger.info(f"📱 Requesting approval for {len(critical_actions)} critical actions...")
            for action in critical_actions:
                action_description = f"{action.get('type')} - {action.get('action')}"
                action_id = action.get("id", f"action-{len(approval_results)}")

                approved = self.approval.require_approval(
                    action_description=action_description,
                    action_id=action_id,
                    timeout_minutes=5
                )

                approval_results.append({
                    "action": action,
                    "approved": approved
                })

                if not approved:
                    logger.warning(f"❌ Action not approved: {action_description}")

        # Phase 6: Post-Approval Execution
        post_results = []
        if self.manus:
            approved_actions = [r["action"] for r in approval_results if r["approved"]]
            if approved_actions:
                logger.info(f"✅ Executing {len(approved_actions)} approved critical actions...")
                for action in approved_actions:
                    result = self._execute_step(action)
                    post_results.append(result)

        # Phase 7: Verification
        all_success = all(r.get("success", False) for r in pre_results + post_results)

        # Phase 8: Completion Report
        results = {
            "success": all_success,
            "workflow": workflow,
            "steps_executed": len(pre_results) + len(post_results),
            "steps_approved": len([r for r in approval_results if r["approved"]]),
            "steps_denied": len([r for r in approval_results if not r["approved"]]),
            "pre_approval_results": pre_results,
            "approval_results": approval_results,
            "post_approval_results": post_results,
            "completed_at": datetime.now().isoformat()
        }

        logger.info("="*80)
        if results["success"]:
            logger.info("✅ WORKFLOW COMPLETED SUCCESSFULLY")
        else:
            logger.warning("⚠️  WORKFLOW COMPLETED WITH ERRORS")
        logger.info("="*80)

        return results

    def _execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step"""
        if not self.manus:
            return {"success": False, "error": "MANUS not available"}

        step_type = step.get("type")
        params = step.get("params", {})

        if step_type == "file_create":
            result = self.manus.create_file(params.get("path", ""), params.get("content", ""))
            return {"success": result, "step": step}
        elif step_type == "file_update":
            result = self.manus.update_file(params.get("path", ""), params.get("content", ""))
            return {"success": result, "step": step}
        elif step_type == "command":
            result = self.manus.execute_command(params.get("command", ""))
            return {"success": result.get("success", False), "step": step, "result": result}
        else:
            return {"success": False, "error": f"Unknown step type: {step_type}", "step": step}


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="End-to-End Workflow Orchestrator")
        parser.add_argument("--request", type=str, help="User request to execute")
        parser.add_argument("--test", action="store_true", help="Test workflow orchestrator")

        args = parser.parse_args()

        orchestrator = EndToEndWorkflowOrchestrator(project_root)

        if args.test:
            # Test workflow
            test_request = "Create a new file test.py with hello world"
            results = orchestrator.execute_workflow(test_request)
            print(json.dumps(results, indent=2, default=str))

        if args.request:
            results = orchestrator.execute_workflow(args.request)
            print(json.dumps(results, indent=2, default=str))

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main() or 0)