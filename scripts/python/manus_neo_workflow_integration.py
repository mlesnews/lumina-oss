#!/usr/bin/env python3
"""
MANUS-NEO Browser Workflow Integration

Integrates Neo AI browser into MANUS workflow control system.
Enables MANUS to orchestrate browser automation tasks as part of workflows.

@MANUS @NEO @WORKFLOW @AUTOMATION
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from manus_neo_browser_control import MANUSNEOBrowserControl
    from manus_neo_integration import MANUSNEOIntegration
    NEO_AVAILABLE = True
except ImportError:
    NEO_AVAILABLE = False
    logging.warning("MANUS-NEO browser control not available")

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("MANUS-NEO-Workflow")


class MANUSNEOWorkflowController:
    """
    MANUS-NEO Browser Workflow Controller

    Integrates Neo browser automation into MANUS workflow orchestration.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger

        if not NEO_AVAILABLE:
            self.logger.error("❌ MANUS-NEO browser control not available")
            self.browser = None
            self.integration = None
        else:
            self.browser = MANUSNEOBrowserControl(headless=False)
            self.integration = MANUSNEOIntegration()
            self.logger.info("✅ MANUS-NEO Workflow Controller initialized")

        # Workflow state
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.workflow_history: List[Dict[str, Any]] = []

    def execute_workflow_step(self, workflow_id: str, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single workflow step using Neo browser

        Args:
            workflow_id: Unique workflow identifier
            step: Step definition with action and parameters

        Returns:
            Step execution result
        """
        if not self.browser:
            return {"success": False, "error": "Neo browser not available"}

        action = step.get("action", "").lower()
        params = step.get("parameters", {})

        self.logger.info(f"🔄 Executing workflow step: {action}")

        try:
            result = None

            # Browser launch
            if action == "launch" or action == "open":
                url = params.get("url")
                result = self.browser.launch(url=url)

            # Navigate
            elif action == "navigate" or action == "goto":
                url = params.get("url")
                if not self.browser.is_running():
                    self.browser.launch()
                result = self.browser.navigate(url)

            # Execute script
            elif action == "execute_script" or action == "script":
                script = params.get("script")
                result = self.browser.execute_script(script)

            # Get cookies
            elif action == "get_cookies":
                domain = params.get("domain")
                cookies = self.browser.get_cookies(domain=domain)
                result = {"cookies": cookies, "count": len(cookies)}

            # Get page info
            elif action == "get_page_info" or action == "page_info":
                info = self.browser.get_page_info()
                result = info

            # Fill form
            elif action == "fill_form":
                form_data = params.get("form_data", {})
                url = params.get("url")
                if url:
                    if not self.browser.is_running():
                        self.browser.launch(url)
                    else:
                        self.browser.navigate(url)
                    time.sleep(2)

                # Fill each field
                for field_name, value in form_data.items():
                    script = f"""
                    (function() {{
                        var field = document.querySelector('input[name="{field_name}"], input[id="{field_name}"], #{field_name}');
                        if (field) {{
                            field.value = {json.dumps(value)};
                            field.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            field.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            return true;
                        }}
                        return false;
                    }})();
                    """
                    self.browser.execute_script(script)
                    time.sleep(0.5)

                result = {"success": True, "fields_filled": len(form_data)}

            # Click element
            elif action == "click":
                selector = params.get("selector")
                script = f"""
                (function() {{
                    var element = document.querySelector('{selector}');
                    if (element) {{
                        element.click();
                        return true;
                    }}
                    return false;
                }})();
                """
                result = self.browser.execute_script(script)

            # Wait
            elif action == "wait":
                seconds = params.get("seconds", 1)
                time.sleep(seconds)
                result = {"success": True, "waited": seconds}

            # Close browser
            elif action == "close":
                self.browser.close()
                result = {"success": True}

            # Unknown action
            else:
                result = {"success": False, "error": f"Unknown action: {action}"}

            # Record step result
            step_result = {
                "workflow_id": workflow_id,
                "step": step,
                "result": result,
                "timestamp": datetime.now().isoformat(),
                "success": result.get("success", True) if isinstance(result, dict) else result is not None
            }

            self.workflow_history.append(step_result)

            return step_result

        except Exception as e:
            self.logger.error(f"❌ Workflow step failed: {e}")
            return {
                "workflow_id": workflow_id,
                "step": step,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def execute_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a complete workflow

        Args:
            workflow: Workflow definition with steps

        Returns:
            Workflow execution result
        """
        workflow_id = workflow.get("id", f"workflow_{int(time.time())}")
        steps = workflow.get("steps", [])
        name = workflow.get("name", "Unnamed Workflow")

        self.logger.info(f"🚀 Starting workflow: {name} ({workflow_id})")
        self.logger.info(f"   Steps: {len(steps)}")

        self.active_workflows[workflow_id] = {
            "workflow": workflow,
            "started_at": datetime.now().isoformat(),
            "status": "running",
            "steps_completed": 0,
            "steps_total": len(steps)
        }

        results = []

        try:
            for i, step in enumerate(steps, 1):
                self.logger.info(f"   Step {i}/{len(steps)}: {step.get('action', 'unknown')}")

                step_result = self.execute_workflow_step(workflow_id, step)
                results.append(step_result)

                if not step_result.get("success", True):
                    self.logger.warning(f"   ⚠️  Step {i} failed: {step_result.get('error', 'Unknown error')}")
                    # Continue or stop based on workflow config
                    if workflow.get("stop_on_error", True):
                        break

                self.active_workflows[workflow_id]["steps_completed"] = i

            # Complete workflow
            self.active_workflows[workflow_id]["status"] = "completed"
            self.active_workflows[workflow_id]["completed_at"] = datetime.now().isoformat()

            success_count = sum(1 for r in results if r.get("success", False))

            self.logger.info(f"✅ Workflow completed: {success_count}/{len(steps)} steps successful")

            return {
                "workflow_id": workflow_id,
                "success": success_count == len(steps),
                "steps_completed": success_count,
                "steps_total": len(steps),
                "results": results,
                "completed_at": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"❌ Workflow execution failed: {e}")
            self.active_workflows[workflow_id]["status"] = "failed"
            self.active_workflows[workflow_id]["error"] = str(e)

            return {
                "workflow_id": workflow_id,
                "success": False,
                "error": str(e),
                "steps_completed": len(results),
                "steps_total": len(steps),
                "results": results
            }

    def create_elevenlabs_setup_workflow(self) -> Dict[str, Any]:
        """Create workflow for ElevenLabs API key setup"""
        return {
            "id": "elevenlabs_setup",
            "name": "ElevenLabs API Key Setup",
            "description": "Automate ElevenLabs account setup and API key retrieval",
            "stop_on_error": True,
            "steps": [
                {
                    "action": "launch",
                    "parameters": {"url": "https://elevenlabs.io"}
                },
                {
                    "action": "wait",
                    "parameters": {"seconds": 3}
                },
                {
                    "action": "navigate",
                    "parameters": {"url": "https://elevenlabs.io/app/settings/api-keys"}
                },
                {
                    "action": "wait",
                    "parameters": {"seconds": 3}
                },
                {
                    "action": "get_page_info",
                    "parameters": {}
                },
                {
                    "action": "execute_script",
                    "parameters": {
                        "script": """
                        (function() {
                            // Try to find API key on page
                            var bodyText = document.body.innerText;
                            var patterns = [
                                /api[_-]?key["\\s:]+([a-zA-Z0-9_-]{20,})/i,
                                /sk[-_][a-zA-Z0-9_-]{20,}/i
                            ];

                            for (var p of patterns) {
                                var match = bodyText.match(p);
                                if (match && match[1] && match[1].length > 20) {
                                    return match[1];
                                }
                            }

                            // Try input fields
                            var inputs = document.querySelectorAll('input[readonly], input[type="text"], code, pre');
                            for (var inp of inputs) {
                                var val = inp.value || inp.innerText;
                                if (val && val.length > 20 && /[a-zA-Z0-9]/.test(val)) {
                                    return val.trim();
                                }
                            }

                            return null;
                        })();
                        """
                    }
                }
            ]
        }

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get status of active workflow"""
        return self.active_workflows.get(workflow_id)

    def list_active_workflows(self) -> List[str]:
        """List all active workflow IDs"""
        return list(self.active_workflows.keys())

    def cleanup(self):
        """Cleanup resources"""
        if self.browser:
            self.browser.close()


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="MANUS-NEO Browser Workflow Integration")
    parser.add_argument("--workflow", type=str, help="Workflow JSON file")
    parser.add_argument("--elevenlabs", action="store_true", help="Run ElevenLabs setup workflow")
    parser.add_argument("--status", type=str, help="Get workflow status")
    parser.add_argument("--list", action="store_true", help="List active workflows")

    args = parser.parse_args()

    controller = MANUSNEOWorkflowController()

    try:
        if args.workflow:
            # Load workflow from file
            with open(args.workflow, 'r') as f:
                workflow = json.load(f)

            result = controller.execute_workflow(workflow)
            print("\n" + "="*70)
            print(f"Workflow: {workflow.get('name', 'Unknown')}")
            print(f"Success: {result.get('success')}")
            print(f"Steps: {result.get('steps_completed')}/{result.get('steps_total')}")
            print("="*70)

        elif args.elevenlabs:
            # Run ElevenLabs setup workflow
            workflow = controller.create_elevenlabs_setup_workflow()
            result = controller.execute_workflow(workflow)
            print("\n" + "="*70)
            print("ElevenLabs Setup Workflow")
            print(f"Success: {result.get('success')}")
            if result.get("results"):
                last_result = result["results"][-1]
                if last_result.get("result"):
                    api_key = last_result["result"]
                    print(f"API Key Found: {api_key[:30]}..." if api_key else "API Key: Not found")
            print("="*70)

        elif args.status:
            status = controller.get_workflow_status(args.status)
            if status:
                print(json.dumps(status, indent=2))
            else:
                print(f"Workflow {args.status} not found")

        elif args.list:
            workflows = controller.list_active_workflows()
            print(f"Active workflows: {len(workflows)}")
            for wf_id in workflows:
                print(f"  - {wf_id}")

        else:
            parser.print_help()

    finally:
        controller.cleanup()


if __name__ == "__main__":

# TODO: Add error handling to functions identified by roast system:  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]


    main()