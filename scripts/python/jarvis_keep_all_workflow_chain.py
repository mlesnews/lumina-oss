#!/usr/bin/env python3
"""
JARVIS Keep All - Workflow Chaining Integration

The "Keep All" button (mouseover: "Accept all changes") is CRITICAL for chaining
workflows and agent sessions together. This system ensures it's always available
and can be triggered automatically to continue workflows.

Tags: #JARVIS #KEEP_ALL #WORKFLOW_CHAINING #AGENT_SESSION @JARVIS @LUMINA
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISKeepAllWorkflowChain")


class JARVISKeepAllWorkflowChain:
    """
    JARVIS Keep All - Workflow Chaining Integration

    The "Keep All" button is critical for:
    - Chaining workflows together
    - Continuing agent sessions
    - Accepting all changes automatically
    - Enabling uninterrupted workflow execution

    Button Details:
    - Button Text: "Keep All"
    - Mouseover Text: "Accept all changes"
    - Keyboard Shortcut: Ctrl+Alt+Enter (or Ctrl+Shift+A)
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root

        # Import Keep All automation
        self.keep_all_automator = None
        try:
            from manus_accept_all_button import MANUSAcceptAllButton
            self.keep_all_automator = MANUSAcceptAllButton()
            logger.info("✅ Keep All automator initialized")
        except ImportError as e:
            logger.warning(f"⚠️  Keep All automator not available: {e}")

        # Import RAlt Doit Paste (for workflow chaining)
        self.ralt_doit_paste = None
        try:
            from jarvis_ralt_doit_paste import JARVISRAltDoitPaste
            self.ralt_doit_paste = JARVISRAltDoitPaste()
            logger.info("✅ RAlt Doit Paste initialized")
        except ImportError as e:
            logger.debug(f"RAlt Doit Paste not available: {e}")

        # Import auto-accept monitor
        self.auto_accept_monitor = None
        try:
            from jarvis_auto_accept_monitor import JARVISAutoAcceptMonitor
            self.auto_accept_monitor = JARVISAutoAcceptMonitor()
            logger.info("✅ Auto-accept monitor available")
        except ImportError as e:
            logger.debug(f"Auto-accept monitor not available: {e}")

        logger.info("=" * 80)
        logger.info("🔗 JARVIS KEEP ALL - WORKFLOW CHAINING")
        logger.info("=" * 80)
        logger.info("   Button: 'Keep All'")
        logger.info("   Mouseover: 'Accept all changes'")
        logger.info("   Purpose: Chain workflows & agent sessions")
        logger.info("=" * 80)

    def trigger_keep_all(self) -> Dict[str, Any]:
        """
        Trigger Keep All button to accept all changes

        This is critical for workflow chaining - when AI makes changes,
        they must be accepted to continue the workflow.

        Returns:
            Result dictionary
        """
        logger.info("🔗 Triggering Keep All for workflow chaining...")

        if not self.keep_all_automator:
            return {
                "success": False,
                "error": "Keep All automator not available",
                "message": "Cannot trigger Keep All - automator not initialized"
            }

        try:
            # Use MANUS to click Keep All button
            success = self.keep_all_automator.accept_all_changes()

            if success:
                logger.info("✅ Keep All triggered successfully - workflow can continue")
                return {
                    "success": True,
                    "message": "Keep All triggered - all changes accepted",
                    "workflow_chain": "continued",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.warning("⚠️  Keep All trigger failed - workflow may be blocked")
                return {
                    "success": False,
                    "error": "Failed to trigger Keep All",
                    "message": "Workflow may be blocked - manual intervention may be needed",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"❌ Error triggering Keep All: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Error occurred while triggering Keep All",
                "timestamp": datetime.now().isoformat()
            }

    def ensure_keep_all_available(self) -> Dict[str, Any]:
        """
        Ensure Keep All functionality is available and ready

        This checks that:
        - Keep All automator is initialized
        - Auto-accept monitor is running (if available)
        - System is ready for workflow chaining

        Returns:
            Status dictionary
        """
        status = {
            "keep_all_available": self.keep_all_automator is not None,
            "auto_accept_monitor_available": self.auto_accept_monitor is not None,
            "workflow_chaining_ready": False,
            "timestamp": datetime.now().isoformat()
        }

        # Check if auto-accept monitor is running
        if self.auto_accept_monitor:
            status["auto_accept_monitor_running"] = getattr(self.auto_accept_monitor, 'running', False)
        else:
            status["auto_accept_monitor_running"] = False

        # Workflow chaining is ready if Keep All automator is available
        status["workflow_chaining_ready"] = status["keep_all_available"]

        if status["workflow_chaining_ready"]:
            logger.info("✅ Keep All ready for workflow chaining")
        else:
            logger.warning("⚠️  Keep All not ready - workflow chaining may be blocked")

        return status

    def start_auto_accept_monitor(self) -> Dict[str, Any]:
        """
        Start auto-accept monitor for continuous workflow chaining

        This ensures Keep All is automatically triggered when needed,
        enabling uninterrupted workflow execution.

        Returns:
            Result dictionary
        """
        if not self.auto_accept_monitor:
            return {
                "success": False,
                "error": "Auto-accept monitor not available",
                "message": "Cannot start auto-accept monitor"
            }

        try:
            if self.auto_accept_monitor.start():
                logger.info("✅ Auto-accept monitor started - workflow chaining enabled")
                return {
                    "success": True,
                    "message": "Auto-accept monitor started",
                    "workflow_chaining": "enabled",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to start auto-accept monitor",
                    "message": "Monitor may already be running or failed to start"
                }
        except Exception as e:
            logger.error(f"❌ Error starting auto-accept monitor: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Error occurred while starting monitor"
            }

    def chain_workflow(self, workflow_step: str, use_ralt_doit: bool = True) -> Dict[str, Any]:
        """
        Chain a workflow step by ensuring Keep All is triggered

        This is the main function for workflow chaining:
        1. Check if Keep All is needed
        2. Trigger Keep All if needed
        3. Optionally trigger RAlt Doit command
        4. Continue workflow

        Args:
            workflow_step: Description of current workflow step
            use_ralt_doit: If True, also paste RAlt Doit command

        Returns:
            Result dictionary
        """
        logger.info(f"🔗 Chaining workflow step: {workflow_step}")

        # Ensure Keep All is available
        status = self.ensure_keep_all_available()
        if not status["workflow_chaining_ready"]:
            return {
                "success": False,
                "error": "Keep All not ready",
                "workflow_step": workflow_step,
                "message": "Cannot chain workflow - Keep All not available"
            }

        # Trigger Keep All to accept any pending changes
        keep_all_result = self.trigger_keep_all()

        # Optionally trigger RAlt Doit command
        ralt_doit_result = None
        if use_ralt_doit and self.ralt_doit_paste:
            logger.info("🔘 Triggering RAlt Doit command...")
            ralt_doit_result = self.ralt_doit_paste.paste_doit_command()
            if ralt_doit_result.get("success"):
                logger.info("✅ RAlt Doit command pasted")
            else:
                logger.warning(f"⚠️  RAlt Doit paste failed: {ralt_doit_result.get('error')}")

        if keep_all_result["success"]:
            logger.info(f"✅ Workflow step chained: {workflow_step}")
            return {
                "success": True,
                "workflow_step": workflow_step,
                "keep_all_triggered": True,
                "ralt_doit_triggered": ralt_doit_result.get("success") if ralt_doit_result else False,
                "workflow_chain": "continued",
                "message": f"Workflow step '{workflow_step}' chained successfully",
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.warning(f"⚠️  Workflow step may be blocked: {workflow_step}")
            return {
                "success": False,
                "workflow_step": workflow_step,
                "keep_all_triggered": False,
                "workflow_chain": "blocked",
                "error": keep_all_result.get("error", "Unknown error"),
                "message": f"Workflow step '{workflow_step}' may be blocked",
                "timestamp": datetime.now().isoformat()
            }


def main():
    """Test Keep All workflow chaining"""
    chainer = JARVISKeepAllWorkflowChain()

    print("\n" + "=" * 80)
    print("🔗 JARVIS KEEP ALL - WORKFLOW CHAINING TEST")
    print("=" * 80 + "\n")

    # Check availability
    print("1. Checking Keep All availability:")
    status = chainer.ensure_keep_all_available()
    print(f"   Keep All Available: {'✅ Yes' if status['keep_all_available'] else '❌ No'}")
    print(f"   Workflow Chaining Ready: {'✅ Yes' if status['workflow_chaining_ready'] else '❌ No'}")
    print()

    # Test workflow chaining
    print("2. Testing workflow chaining:")
    result = chainer.chain_workflow("Test workflow step")
    if result["success"]:
        print(f"   ✅ Workflow chained successfully")
        print(f"   Keep All Triggered: {result.get('keep_all_triggered', False)}")
    else:
        print(f"   ❌ Workflow chaining failed: {result.get('error', 'Unknown')}")
    print()

    print("=" * 80)
    print("✅ TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":


    main()