#!/usr/bin/env python3
"""
JARVIS Fidelity Manual Login & Full Exploration
Manual login workflow with complete @ff exploration and @MANUS control

This script:
1. Provides login instructions (manual or via ProtonPass if available)
2. Waits for user to log in manually
3. Detects when dashboard is loaded
4. Performs complete @ff exploration
5. Generates full @MANUS control interface
6. Creates JARVIS reporting

Tags: #FIDELITY #@MANUS #@FF #JARVIS #MANUAL_LOGIN #AUTOMATION
"""

import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISFidelityManualLoginExplore")

# Import modules
try:
    from jarvis_fidelity_protonpass_login import JARVISFidelityProtonPassLogin
    from jarvis_fidelity_full_exploration_manus import JARVISFidelityFullExplorationMANUS
    from jarvis_fidelity_complete_manus_workflow import JARVISFidelityCompleteMANUSWorkflow
    from jarvis_fidelity_auto_explore_dashboard import JARVISFidelityAutoExploreDashboard
except ImportError as e:
    logger.error(f"Failed to import modules: {e}")
    sys.exit(1)


class JARVISFidelityManualLoginExplore:
    """
    Manual Login & Full Exploration Workflow

    Supports manual login, then automatically explores and maps everything
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize workflow"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.output_dir = self.project_root / "data" / "fidelity_exploration"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.login_system = JARVISFidelityProtonPassLogin(self.project_root)
        self.explorer = JARVISFidelityFullExplorationMANUS(self.project_root)
        self.workflow = JARVISFidelityCompleteMANUSWorkflow(self.project_root)
        self.auto_explore = JARVISFidelityAutoExploreDashboard(self.project_root)

        logger.info("=" * 70)
        logger.info("🎮 JARVIS FIDELITY MANUAL LOGIN & EXPLORATION")
        logger.info("=" * 70)
        logger.info("   Manual Login: SUPPORTED")
        logger.info("   ProtonPass: OPTIONAL")
        logger.info("   @ff Exploration: ENABLED")
        logger.info("   @MANUS Control: ENABLED")
        logger.info("   JARVIS Reporting: ENABLED")
        logger.info("")

    def try_protonpass_credentials(self) -> Optional[Dict[str, Any]]:
        """Try to get credentials from ProtonPass"""
        logger.info("🔐 Attempting to retrieve credentials from ProtonPass...")

        try:
            credentials = self.login_system.get_fidelity_credentials("Fidelity")
            if credentials.get("password"):
                logger.info("✅ Credentials found in ProtonPass!")
                return credentials
            else:
                logger.info("⚠️  No credentials found in ProtonPass")
                return None
        except Exception as e:
            logger.debug(f"ProtonPass check failed: {e}")
            return None

    def provide_login_instructions(self, credentials: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Provide login instructions"""
        logger.info("=" * 70)
        logger.info("📋 LOGIN INSTRUCTIONS")
        logger.info("=" * 70)
        logger.info("")

        instructions = {
            "login_url": "https://digital.fidelity.com/ftgw/digital/login",
            "dashboard_url": "https://digital.fidelity.com/ftgw/digital/trader-dashboard",
            "has_credentials": credentials is not None and credentials.get("password") is not None,
            "steps": []
        }

        if credentials and credentials.get("password"):
            logger.info("✅ Credentials available from ProtonPass")
            logger.info("   You can:")
            logger.info("   1. Use MCP Browser to automate login")
            logger.info("   2. Or log in manually in the browser")
            logger.info("")
            instructions["steps"].append({
                "step": 1,
                "action": "automated_login_available",
                "description": "Credentials found - can automate login"
            })
        else:
            logger.info("⚠️  No credentials in ProtonPass")
            logger.info("   Please log in manually:")
            logger.info("")
            logger.info("   1. Navigate to: https://digital.fidelity.com/ftgw/digital/login")
            logger.info("   2. Enter your username and password")
            logger.info("   3. Complete 2FA if required")
            logger.info("   4. Navigate to: https://digital.fidelity.com/ftgw/digital/trader-dashboard")
            logger.info("   5. Once logged in, this script will automatically detect and explore")
            logger.info("")
            instructions["steps"].append({
                "step": 1,
                "action": "manual_login_required",
                "description": "Please log in manually in the browser"
            })

        logger.info("=" * 70)
        logger.info("⏳ WAITING FOR LOGIN...")
        logger.info("=" * 70)
        logger.info("")
        logger.info("   The script will monitor for dashboard state")
        logger.info("   Once dashboard is detected, full exploration will begin")
        logger.info("")

        return instructions

    async def wait_for_dashboard(self, max_attempts: int = 10, wait_seconds: int = 5) -> bool:
        """Wait for dashboard to be loaded"""
        logger.info("🔍 Monitoring for dashboard state...")

        for attempt in range(1, max_attempts + 1):
            logger.info(f"   Attempt {attempt}/{max_attempts}...")

            # Check latest snapshot
            browser_logs = Path.home() / ".cursor" / "browser-logs"
            snapshot_files = sorted(browser_logs.glob("snapshot-*.log"), reverse=True)

            if snapshot_files:
                state = self.auto_explore.detect_dashboard_state(snapshot_files[0])

                if state["is_dashboard"]:
                    logger.info("✅ DASHBOARD DETECTED!")
                    logger.info("")
                    return True
                elif state["is_login"]:
                    logger.info("   Still on login page...")
                else:
                    logger.info(f"   State: {state.get('confidence', 'unknown')}")

            if attempt < max_attempts:
                await asyncio.sleep(wait_seconds)

        logger.warning("⚠️  Dashboard not detected after waiting")
        logger.info("   You may need to manually navigate to the dashboard")
        return False

    async def execute_full_exploration(self) -> Dict[str, Any]:
        """Execute complete exploration workflow"""
        logger.info("=" * 70)
        logger.info("🚀 EXECUTING FULL EXPLORATION")
        logger.info("=" * 70)
        logger.info("")

        # Run complete workflow
        result = await self.workflow.execute_full_workflow()
        workflow_file = self.workflow.save_workflow_result(result)

        return {
            "exploration_complete": True,
            "workflow_file": str(workflow_file),
            "summary": result.get("summary", {})
        }

    def generate_jarvis_report(self, exploration_result: Dict[str, Any]) -> Dict[str, Any]:
        try:
            """Generate comprehensive JARVIS report"""
            logger.info("=" * 70)
            logger.info("📊 GENERATING JARVIS REPORT")
            logger.info("=" * 70)
            logger.info("")

            report = {
                "generated_at": datetime.now().isoformat(),
                "report_type": "fidelity_full_exploration_jarvis",
                "exploration": exploration_result,
                "manus_control": {
                    "status": "ready",
                    "control_methods": exploration_result.get("summary", {}).get("manus_control_methods", 0),
                    "trading_features": exploration_result.get("summary", {}).get("trading_features", 0),
                    "keyboard_shortcuts": exploration_result.get("summary", {}).get("keyboard_shortcuts", 0),
                    "charts": exploration_result.get("summary", {}).get("charts", 0),
                    "watchlists": exploration_result.get("summary", {}).get("watchlists", 0)
                },
                "jarvis_integration": {
                    "status": "ready",
                    "control_interface": "available",
                    "reporting": "active",
                    "automation": "enabled"
                },
                "capabilities": [
                    "Full @MANUS control of all Fidelity dashboard features",
                    "Keyboard shortcut automation",
                    "Trading workflow automation",
                    "Chart control and analysis",
                    "Watchlist management",
                    "Account monitoring and reporting"
                ]
            }

            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.output_dir / f"jarvis_report_{timestamp}.json"

            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ JARVIS report saved to: {report_file}")
            logger.info("")

            return report

        except Exception as e:
            self.logger.error(f"Error in generate_jarvis_report: {e}", exc_info=True)
            raise
    async def execute_workflow(self) -> Dict[str, Any]:
        """Execute complete workflow"""
        logger.info("=" * 70)
        logger.info("🚀 JARVIS FIDELITY MANUAL LOGIN & EXPLORATION WORKFLOW")
        logger.info("=" * 70)
        logger.info("")

        workflow_result = {
            "started_at": datetime.now().isoformat(),
            "steps": {},
            "final_status": "in_progress"
        }

        # Step 1: Try ProtonPass credentials
        credentials = self.try_protonpass_credentials()
        workflow_result["steps"]["credentials"] = {
            "found": credentials is not None and credentials.get("password") is not None
        }

        # Step 2: Provide login instructions
        instructions = self.provide_login_instructions(credentials)
        workflow_result["steps"]["login_instructions"] = instructions

        # Step 3: Wait for dashboard
        logger.info("")
        dashboard_ready = await self.wait_for_dashboard()
        workflow_result["steps"]["dashboard_ready"] = dashboard_ready

        if not dashboard_ready:
            logger.warning("⚠️  Dashboard not detected")
            logger.info("   Please ensure you're logged in and on the trader dashboard")
            logger.info("   URL: https://digital.fidelity.com/ftgw/digital/trader-dashboard")
            logger.info("")
            logger.info("   Then run this script again or capture a snapshot manually")
            workflow_result["final_status"] = "waiting_for_dashboard"
            return workflow_result

        # Step 4: Execute full exploration
        exploration_result = await self.execute_full_exploration()
        workflow_result["steps"]["exploration"] = exploration_result

        # Step 5: Generate JARVIS report
        jarvis_report = self.generate_jarvis_report(exploration_result)
        workflow_result["steps"]["jarvis_report"] = {
            "generated": True,
            "report_file": jarvis_report.get("generated_at", "")
        }

        # Complete
        workflow_result["final_status"] = "completed"
        workflow_result["completed_at"] = datetime.now().isoformat()

        logger.info("=" * 70)
        logger.info("✅ COMPLETE WORKFLOW FINISHED")
        logger.info("=" * 70)
        logger.info("")
        logger.info("📊 Summary:")
        logger.info(f"   Dashboard: ✅ Detected")
        logger.info(f"   Exploration: ✅ Complete")
        logger.info(f"   @MANUS Control: ✅ Ready")
        logger.info(f"   JARVIS Report: ✅ Generated")
        logger.info("")

        return workflow_result

    def save_workflow_result(self, result: Dict[str, Any]) -> Path:
        try:
            """Save workflow result"""
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"manual_login_workflow_{timestamp}.json"

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Workflow result saved to: {output_file}")
            return output_file


        except Exception as e:
            self.logger.error(f"Error in save_workflow_result: {e}", exc_info=True)
            raise
async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Fidelity Manual Login & Exploration")
    parser.add_argument("--workflow", "-w", action="store_true", help="Execute full workflow")
    parser.add_argument("--wait", action="store_true", help="Wait for dashboard and explore")

    args = parser.parse_args()

    workflow = JARVISFidelityManualLoginExplore()

    if args.workflow or args.wait:
        result = await workflow.execute_workflow()
        output_file = workflow.save_workflow_result(result)
        print(f"\n✅ Workflow complete!")
        print(f"   Result saved to: {output_file}")
    else:
        parser.print_help()


if __name__ == "__main__":


    asyncio.run(main())