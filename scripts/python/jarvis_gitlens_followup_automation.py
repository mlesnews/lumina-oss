#!/usr/bin/env python3
"""
JARVIS GitLens Follow-up Automation

Automatically monitors and handles all GitLens follow-up requirements.
Runs in fullauto mode by default - no manual intervention needed.

Features:
- Continuous monitoring of GitLens alerts
- Automatic PR/Issue follow-up handling
- Auto-commit, auto-push, auto-pull
- Conflict resolution
- Integration with PR/Ticket coordination

Tags: #GITLENS #AUTOMATION #FULLAUTO #FOLLOWUP @JARVIS @DOIT
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISGitLensFollowupAutomation")

# Import GitLens automation components
try:
    from jarvis_gitlens_automation import JARVISGitLensAutomation
    GITLENS_AUTOMATION_AVAILABLE = True
except ImportError:
    GITLENS_AUTOMATION_AVAILABLE = False
    logger.warning("⚠️  GitLens automation not available")

try:
    from gitlens_ide_footer_alert_handler import GitLensIDEFooterAlertHandler
    ALERT_HANDLER_AVAILABLE = True
except ImportError:
    ALERT_HANDLER_AVAILABLE = False
    logger.warning("⚠️  GitLens alert handler not available")


class JARVISGitLensFollowupAutomation:
    """
    Automated GitLens Follow-up Handler

    Monitors and automatically handles all GitLens follow-up requirements.
    Runs in fullauto mode - no manual intervention needed.
    """

    def __init__(self, project_root: Optional[Path] = None, fullauto: bool = True):
        """
        Initialize GitLens follow-up automation.

        Args:
            project_root: Path to project root. If None, auto-detects.
            fullauto: Enable full automation (default: True)
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.fullauto = fullauto
        self.data_dir = self.project_root / "data" / "gitlens_followup_automation"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize GitLens automation (fullauto mode)
        self.gitlens_automation = None
        if GITLENS_AUTOMATION_AVAILABLE:
            try:
                self.gitlens_automation = JARVISGitLensAutomation(
                    repo_path=self.project_root,
                    fullauto=self.fullauto
                )
                logger.info("✅ GitLens automation initialized (fullauto mode)")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize GitLens automation: {e}")

        # Initialize alert handler
        self.alert_handler = None
        if ALERT_HANDLER_AVAILABLE:
            try:
                self.alert_handler = GitLensIDEFooterAlertHandler(project_root=self.project_root)
                logger.info("✅ GitLens alert handler initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize alert handler: {e}")

        # State tracking
        self.state_file = self.data_dir / "automation_state.json"
        self.history_file = self.data_dir / "followup_history.jsonl"
        self.running = False

        logger.info("✅ JARVIS GitLens Follow-up Automation initialized")
        logger.info(f"   Fullauto mode: {'✅ ENABLED' if self.fullauto else '❌ DISABLED'}")

    def _load_state(self) -> Dict[str, Any]:
        """Load automation state"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️  Error loading state: {e}")
        return {
            "last_check": None,
            "total_handled": 0,
            "last_handled_at": None
        }

    def _save_state(self, state: Dict[str, Any]):
        """Save automation state"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"❌ Error saving state: {e}")

    def _save_to_history(self, result: Dict[str, Any]):
        """Save follow-up handling result to history"""
        try:
            history_entry = {
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
            with open(self.history_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(history_entry) + '\n')
        except Exception as e:
            logger.error(f"❌ Error saving to history: {e}")

    def check_git_status(self) -> Dict[str, Any]:
        """Check current git status for follow-up requirements"""
        if not self.gitlens_automation:
            return {"error": "GitLens automation not available"}

        try:
            status = self.gitlens_automation.get_git_status()
            branch = self.gitlens_automation.get_current_branch()

            return {
                "status": "ok",
                "has_changes": status.get("has_changes", False),
                "branch": branch,
                "details": status
            }
        except Exception as e:
            logger.error(f"❌ Error checking git status: {e}")
            return {"error": str(e)}

    def handle_follow_ups(self) -> Dict[str, Any]:
        """
        Handle all GitLens follow-ups automatically.

        This is the main entry point for automated follow-up handling.
        """
        logger.info("🔄 Handling GitLens follow-ups automatically...")

        result = {
            "timestamp": datetime.now().isoformat(),
            "fullauto": self.fullauto,
            "actions_taken": [],
            "success": False
        }

        # Check git status and handle follow-ups
        if self.gitlens_automation:
            try:
                # Use GitLens automation to handle follow-ups
                followup_result = self.gitlens_automation.handle_follow_ups()
                result["actions_taken"] = followup_result.get("actions_taken", [])
                result["success"] = any(
                    action.get("success", False) 
                    for action in result["actions_taken"]
                )
                result["details"] = followup_result

                if result["success"]:
                    logger.info(f"✅ Handled {len(result['actions_taken'])} follow-up actions")
                else:
                    logger.info("ℹ️  No follow-up actions needed")

            except Exception as e:
                logger.error(f"❌ Error handling follow-ups: {e}", exc_info=True)
                result["error"] = str(e)
        else:
            result["error"] = "GitLens automation not available"
            logger.warning("⚠️  GitLens automation not available")

        # Save to history
        self._save_to_history(result)

        # Update state
        state = self._load_state()
        state["last_check"] = datetime.now().isoformat()
        if result["success"]:
            state["total_handled"] = state.get("total_handled", 0) + len(result["actions_taken"])
            state["last_handled_at"] = datetime.now().isoformat()
        self._save_state(state)

        return result

    def process_alert(self, alert_text: str) -> Dict[str, Any]:
        """
        Process a specific GitLens alert.

        Args:
            alert_text: Alert text from GitLens IDE-footer
        """
        logger.info(f"🔔 Processing alert: {alert_text}")

        result = {
            "timestamp": datetime.now().isoformat(),
            "alert_text": alert_text,
            "handled": False
        }

        if self.alert_handler:
            try:
                # Parse and handle alert
                alert_result = self.alert_handler.process_alert_text(alert_text)
                result["handled"] = alert_result.get("handled", False)
                result["action_taken"] = alert_result.get("action_taken")
                result["details"] = alert_result.get("details", {})

                if result["handled"]:
                    logger.info(f"✅ Alert handled: {result.get('action_taken')}")
                else:
                    logger.warning(f"⚠️  Alert not fully handled: {result.get('action_taken')}")

            except Exception as e:
                logger.error(f"❌ Error processing alert: {e}", exc_info=True)
                result["error"] = str(e)
        else:
            result["error"] = "Alert handler not available"
            logger.warning("⚠️  Alert handler not available")

        # Save to history
        self._save_to_history(result)

        return result

    def handle_all_active_alerts(self) -> Dict[str, Any]:
        """Handle all active GitLens alerts"""
        logger.info("🔄 Handling all active GitLens alerts...")

        result = {
            "timestamp": datetime.now().isoformat(),
            "alerts_handled": 0,
            "alerts": []
        }

        if self.alert_handler:
            try:
                # Get active alerts
                active_alerts = self.alert_handler.active_alerts

                if not active_alerts:
                    logger.info("ℹ️  No active alerts")
                    return result

                logger.info(f"📋 Found {len(active_alerts)} active alerts")

                # Handle each alert
                for alert_id, alert in active_alerts.items():
                    alert_result = self.alert_handler.handle_alert(alert)
                    result["alerts"].append({
                        "alert_id": alert_id,
                        "alert_text": alert.alert_text,
                        "handled": alert_result.get("handled", False),
                        "action_taken": alert_result.get("action_taken")
                    })

                    if alert_result.get("handled"):
                        result["alerts_handled"] += 1

                logger.info(f"✅ Handled {result['alerts_handled']}/{len(active_alerts)} alerts")

            except Exception as e:
                logger.error(f"❌ Error handling active alerts: {e}", exc_info=True)
                result["error"] = str(e)
        else:
            result["error"] = "Alert handler not available"

        # Save to history
        self._save_to_history(result)

        return result

    def continuous_monitor(self, interval: int = 60) -> None:
        """
        Continuously monitor and handle GitLens follow-ups.

        Args:
            interval: Check interval in seconds (default: 60)
        """
        logger.info("="*80)
        logger.info("🔄 JARVIS GITLENS FOLLOW-UP AUTOMATION - CONTINUOUS MODE")
        logger.info("="*80)
        logger.info(f"   Fullauto mode: {'✅ ENABLED' if self.fullauto else '❌ DISABLED'}")
        logger.info(f"   Check interval: {interval} seconds")
        logger.info("   Press Ctrl+C to stop")
        logger.info("")

        self.running = True

        try:
            while self.running:
                try:
                    # Handle follow-ups
                    result = self.handle_follow_ups()

                    # Handle active alerts
                    if self.alert_handler:
                        alert_result = self.handle_all_active_alerts()
                        if alert_result.get("alerts_handled", 0) > 0:
                            logger.info(f"   ✅ Handled {alert_result['alerts_handled']} alerts")

                    # Log summary
                    if result.get("success"):
                        actions = result.get("actions_taken", [])
                        successful = sum(1 for a in actions if a.get("success", False))
                        logger.info(f"   [{datetime.now().strftime('%H:%M:%S')}] ✅ {successful}/{len(actions)} actions successful")
                    else:
                        logger.info(f"   [{datetime.now().strftime('%H:%M:%S')}] ℹ️  No actions needed")

                except Exception as e:
                    logger.error(f"   ❌ Error in monitoring cycle: {e}", exc_info=True)

                # Wait for next check
                logger.info(f"   Next check in {interval} seconds...")
                time.sleep(interval)

        except KeyboardInterrupt:
            logger.info("\n🛑 Stopping continuous monitoring...")
            self.running = False
        except Exception as e:
            logger.error(f"❌ Fatal error in continuous monitoring: {e}", exc_info=True)
            self.running = False

    def get_status(self) -> Dict[str, Any]:
        """Get automation status"""
        state = self._load_state()
        git_status = self.check_git_status()

        return {
            "fullauto": self.fullauto,
            "running": self.running,
            "state": state,
            "git_status": git_status,
            "components": {
                "gitlens_automation": self.gitlens_automation is not None,
                "alert_handler": self.alert_handler is not None
            }
        }


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="JARVIS GitLens Follow-up Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Handle follow-ups once
  python jarvis_gitlens_followup_automation.py --handle

  # Continuous monitoring (default: 60s interval)
  python jarvis_gitlens_followup_automation.py --monitor

  # Continuous monitoring with custom interval
  python jarvis_gitlens_followup_automation.py --monitor --interval 30

  # Process specific alert
  python jarvis_gitlens_followup_automation.py --alert "REPO#123 REQUIRES FOLLOW-UP"

  # Get status
  python jarvis_gitlens_followup_automation.py --status

  # Disable fullauto (requires manual approval)
  python jarvis_gitlens_followup_automation.py --handle --no-fullauto
        """
    )

    parser.add_argument("--handle", action="store_true", 
                       help="Handle follow-ups once (then exit)")
    parser.add_argument("--monitor", action="store_true",
                       help="Continuous monitoring mode")
    parser.add_argument("--interval", type=int, default=60,
                       help="Monitoring interval in seconds (default: 60)")
    parser.add_argument("--alert", type=str,
                       help="Process specific alert text")
    parser.add_argument("--status", action="store_true",
                       help="Show automation status")
    parser.add_argument("--fullauto", action="store_true", default=True,
                       help="Enable full automation (default: True)")
    parser.add_argument("--no-fullauto", action="store_true",
                       help="Disable full automation (requires manual approval)")

    args = parser.parse_args()

    # Determine fullauto mode
    fullauto = args.fullauto and not args.no_fullauto

    # Initialize automation
    automation = JARVISGitLensFollowupAutomation(fullauto=fullauto)

    if args.status:
        # Show status
        status = automation.get_status()
        print("\n" + "="*80)
        print("📊 JARVIS GITLENS FOLLOW-UP AUTOMATION STATUS")
        print("="*80)
        print(json.dumps(status, indent=2, default=str))
        print()

    elif args.alert:
        # Process specific alert
        result = automation.process_alert(args.alert)
        print("\n" + "="*80)
        print("🔔 ALERT PROCESSING RESULT")
        print("="*80)
        print(json.dumps(result, indent=2, default=str))
        print()

    elif args.monitor:
        # Continuous monitoring
        automation.continuous_monitor(interval=args.interval)

    elif args.handle:
        # Handle once
        result = automation.handle_follow_ups()
        print("\n" + "="*80)
        print("🔄 FOLLOW-UP HANDLING RESULT")
        print("="*80)
        print(json.dumps(result, indent=2, default=str))
        print()

    else:
        # Default: handle once
        result = automation.handle_follow_ups()
        print("\n" + "="*80)
        print("🔄 FOLLOW-UP HANDLING RESULT")
        print("="*80)
        print(json.dumps(result, indent=2, default=str))
        print()


if __name__ == "__main__":


    main()