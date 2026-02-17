#!/usr/bin/env python3
"""
One-Shot Orchestrator V2
Complete end-to-end workflow execution - following The One Ring Blueprint

This orchestrator integrates:
- MANUS Cursor IDE Controller (Execution)
- Dead Man Switch SMS Approval (Security/Human-in-the-loop)
- Unified Secrets Manager (Authentication)
- Master Feedback Loop (Orchestration)

Flow:
1. Plan - Generate complete workflow steps
2. Risk Assessment - Identify critical actions requiring SMS approval
3. Pre-Approval Execution - Execute non-critical preparatory steps
4. Human-in-the-loop - Batch SMS approval for critical actions
5. Final Execution - Execute approved critical actions
6. Verification & Reporting - Final status and cleanup

Tags: #ONE_SHOT #ORCHESTRATOR #MANUS #DMS #AUTOMATION #BLUEPRINT @JARVIS @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("OneShotOrchestratorV2")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("OneShotOrchestratorV2")

try:
    from scripts.python.manus_cursor_ide_controller import MANUSCursorIDEController
    from scripts.python.dead_man_switch_sms_approval import DeadManSwitchSMSApproval
    from scripts.python.unified_secrets_manager import UnifiedSecretsManager
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    COMPONENTS_AVAILABLE = False
    logger.warning(f"⚠️  Required components not available: {e}")


class OneShotOrchestratorV2:
    """One-Shot Orchestrator - The ultimate automation enabler"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "workflows" / "one_shot"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        if COMPONENTS_AVAILABLE:
            self.manus = MANUSCursorIDEController(self.project_root)
            self.approval = DeadManSwitchSMSApproval(self.project_root)
            self.secrets = UnifiedSecretsManager(self.project_root)
        else:
            self.manus = None
            self.approval = None
            self.secrets = None

        logger.info("✅ One-Shot Orchestrator V2 initialized")

    def execute_one_shot(self, request_name: str, workflow_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute a complete one-shot workflow

        Args:
            request_name: Name of the request
            workflow_steps: Pre-defined steps for the workflow

        Returns:
            Execution results
        """
        logger.info("="*80)
        logger.info(f"🚀 STARTING ONE-SHOT: {request_name}")
        logger.info("="*80)

        execution_id = f"oneshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        results = {
            "execution_id": execution_id,
            "request_name": request_name,
            "start_time": datetime.now().isoformat(),
            "success": False,
            "steps_total": len(workflow_steps),
            "steps_executed": 0,
            "approvals": [],
            "errors": []
        }

        # Step 1: Risk Assessment & Step Categorization
        critical_steps = []
        non_critical_steps = []

        for step in workflow_steps:
            if self._is_critical(step):
                critical_steps.append(step)
            else:
                non_critical_steps.append(step)

        logger.info(f"📊 Assessment: {len(non_critical_steps)} pre-approval, {len(critical_steps)} requiring approval")

        # Step 2: Pre-Approval Execution
        if non_critical_steps:
            logger.info("🔄 Executing pre-approval steps...")
            pre_results = self.manus.execute_workflow(non_critical_steps)
            results["steps_executed"] += len(pre_results.get("steps_completed", []))

            if not pre_results.get("success"):
                results["errors"].extend(pre_results.get("errors", []))
                results["success"] = False
                self._save_results(results)
                return results

        # Step 3: Human-in-the-loop (Batch Approval)
        approved_steps = []
        if critical_steps:
            logger.info("📱 Batch requesting approval for critical steps...")

            # Combine all critical actions into one description for the SMS
            combined_desc = " | ".join([s.get('action') for s in critical_steps])
            if len(combined_desc) > 100:
                combined_desc = f"{len(critical_steps)} critical actions: {critical_steps[0].get('action')}..."

            # Request one approval for the entire batch of critical steps
            # In a more granular system, we'd do one by one, but batch is faster for "one-shot"
            approved = self.approval.require_approval(
                action_description=f"BATCH: {combined_desc}",
                action_id=execution_id,
                timeout_minutes=10
            )

            results["approvals"].append({
                "batch": True,
                "approved": approved,
                "steps": [s.get('action') for s in critical_steps]
            })

            if approved:
                approved_steps = critical_steps
            else:
                results["errors"].append("Batch approval denied or timed out")
                results["success"] = False
                self._save_results(results)
                return results

        # Step 4: Post-Approval (Critical) Execution
        if approved_steps:
            logger.info("🔥 Executing approved critical steps...")
            post_results = self.manus.execute_workflow(approved_steps)
            results["steps_executed"] += len(post_results.get("steps_completed", []))

            if not post_results.get("success"):
                results["errors"].extend(post_results.get("errors", []))
                results["success"] = False
                self._save_results(results)
                return results

        # Final Verification
        results["success"] = results["steps_executed"] == results["steps_total"]
        results["end_time"] = datetime.now().isoformat()

        self._save_results(results)

        logger.info("="*80)
        if results["success"]:
            logger.info(f"✅ ONE-SHOT COMPLETED: {request_name}")
        else:
            logger.warning(f"⚠️  ONE-SHOT FAILED: {request_name}")
        logger.info("="*80)

        return results

    def _is_critical(self, step: Dict[str, Any]) -> bool:
        """Determine if a step is critical based on type and parameters"""
        if step.get("requires_approval", False):
            return True

        step_type = step.get("type")
        params = step.get("params", {})

        critical_types = ["file_delete", "git_push", "git_commit", "pip_install", "npm_install"]

        if step_type in critical_types:
            # git_push/commit to main/master is always critical
            if step_type in ["git_push", "git_commit"]:
                if params.get("branch") in ["main", "master", None]:
                    return True
            # file_delete is always critical unless in a temp dir
            if step_type == "file_delete":
                path = params.get("path", "")
                if "temp" not in path.lower() and "cache" not in path.lower():
                    return True
            # Package installs are critical in production
            if step_type in ["pip_install", "npm_install"]:
                return True

        return False

    def _save_results(self, results: Dict[str, Any]):
        try:
            """Save execution results to data directory"""
            file_path = self.data_dir / f"{results['execution_id']}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"💾 Execution log saved: {file_path}")


        except Exception as e:
            self.logger.error(f"Error in _save_results: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="One-Shot Orchestrator V2")
        parser.add_argument("--request", type=str, help="Name of the request")
        parser.add_argument("--steps", type=str, help="Path to JSON file with workflow steps")

        args = parser.parse_args()

        if args.request and args.steps:
            orchestrator = OneShotOrchestratorV2(project_root)

            with open(args.steps, 'r') as f:
                steps = json.load(f)

            results = orchestrator.execute_one_shot(args.request, steps)
            print(json.dumps(results, indent=2))

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":

    main()