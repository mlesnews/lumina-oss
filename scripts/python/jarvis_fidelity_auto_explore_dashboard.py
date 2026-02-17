#!/usr/bin/env python3
"""
JARVIS Fidelity Auto-Explore Dashboard
Automatically detects dashboard state and runs full exploration when logged in

This script:
- Monitors browser state
- Detects when logged into dashboard
- Automatically captures snapshot and network requests
- Runs complete @ff exploration with @MANUS control

Tags: #FIDELITY #@MANUS #@FF #AUTO_EXPLORE #JARVIS
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

logger = get_logger("JARVISFidelityAutoExplore")

# Import exploration modules
try:
    from jarvis_fidelity_full_exploration_manus import JARVISFidelityFullExplorationMANUS
    from jarvis_fidelity_complete_manus_workflow import JARVISFidelityCompleteMANUSWorkflow
except ImportError as e:
    logger.error(f"Failed to import modules: {e}")
    sys.exit(1)


class JARVISFidelityAutoExploreDashboard:
    """
    Auto-Explore Dashboard System

    Automatically detects dashboard state and runs exploration when ready
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize auto-explore system"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.output_dir = self.project_root / "data" / "fidelity_exploration"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.explorer = JARVISFidelityFullExplorationMANUS(self.project_root)
        self.workflow = JARVISFidelityCompleteMANUSWorkflow(self.project_root)

        logger.info("=" * 70)
        logger.info("🤖 JARVIS FIDELITY AUTO-EXPLORE DASHBOARD")
        logger.info("=" * 70)
        logger.info("   Auto-detection: ENABLED")
        logger.info("   Dashboard monitoring: ACTIVE")
        logger.info("")

    def detect_dashboard_state(self, snapshot_file: Path) -> Dict[str, Any]:
        """Detect if we're on login page or dashboard"""
        import yaml

        try:
            with open(snapshot_file, 'r', encoding='utf-8') as f:
                snapshot_content = f.read()

            snapshot_data = yaml.safe_load(snapshot_content)

            # Check for dashboard indicators
            dashboard_indicators = [
                "trader", "dashboard", "portfolio", "positions", "orders",
                "watchlist", "chart", "trade", "quote", "account summary"
            ]

            # Check for login indicators
            login_indicators = [
                "login", "sign in", "username", "password", "log in"
            ]

            snapshot_text = str(snapshot_data).lower()

            dashboard_score = sum(1 for indicator in dashboard_indicators if indicator in snapshot_text)
            login_score = sum(1 for indicator in login_indicators if indicator in snapshot_text)

            state = {
                "is_dashboard": dashboard_score > login_score and dashboard_score > 0,
                "is_login": login_score > dashboard_score or dashboard_score == 0,
                "dashboard_score": dashboard_score,
                "login_score": login_score,
                "confidence": "high" if abs(dashboard_score - login_score) > 2 else "medium"
            }

            return state

        except Exception as e:
            logger.error(f"Failed to detect dashboard state: {e}")
            return {"is_dashboard": False, "is_login": True, "confidence": "unknown"}

    async def auto_explore(self) -> Dict[str, Any]:
        """Auto-explore dashboard when ready"""
        logger.info("=" * 70)
        logger.info("🔍 AUTO-EXPLORING FIDELITY DASHBOARD")
        logger.info("=" * 70)
        logger.info("")

        # Find latest snapshot
        browser_logs = Path.home() / ".cursor" / "browser-logs"
        snapshot_files = sorted(browser_logs.glob("snapshot-*.log"), reverse=True)

        if not snapshot_files:
            logger.error("❌ No snapshot files found")
            logger.info("   Please navigate to Fidelity and capture a snapshot")
            return {"status": "error", "message": "No snapshot files found"}

        latest_snapshot = snapshot_files[0]
        logger.info(f"📄 Analyzing snapshot: {latest_snapshot.name}")

        # Detect state
        state = self.detect_dashboard_state(latest_snapshot)

        logger.info(f"   Dashboard detected: {state['is_dashboard']}")
        logger.info(f"   Login page detected: {state['is_login']}")
        logger.info(f"   Confidence: {state['confidence']}")
        logger.info("")

        if state["is_login"]:
            logger.warning("⚠️  Currently on LOGIN PAGE")
            logger.info("   Please log in to Fidelity dashboard")
            logger.info("   Then run this script again or navigate to dashboard")
            logger.info("")
            logger.info("   Expected URL: https://digital.fidelity.com/ftgw/digital/trader-dashboard")
            logger.info("")

            # Still run exploration on login page for completeness
            logger.info("   Running exploration on login page...")
            feature_map = self.explorer.process_snapshot_file(latest_snapshot)

            api_endpoints = {
                "trading": [],
                "market_data": [],
                "account": [],
                "positions": [],
                "orders": [],
                "watchlists": [],
                "charts": [],
                "other": []
            }

            manus_control = self.explorer.generate_manus_control_interface(feature_map, api_endpoints)
            report = self.explorer.create_comprehensive_report(feature_map, manus_control, api_endpoints)
            output_file = self.explorer.save_exploration(report)

            return {
                "status": "login_page",
                "message": "Explored login page - please log in for full dashboard exploration",
                "output_file": str(output_file),
                "summary": report["summary"]
            }

        else:
            logger.info("✅ DASHBOARD DETECTED - Running full exploration!")
            logger.info("")

            # Run complete workflow
            result = await self.workflow.execute_full_workflow()
            workflow_file = self.workflow.save_workflow_result(result)

            return {
                "status": "dashboard_explored",
                "message": "Full dashboard exploration complete",
                "workflow_file": str(workflow_file),
                "summary": result.get("summary", {})
            }


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Fidelity Auto-Explore Dashboard")
    parser.add_argument("--auto", action="store_true", help="Auto-explore dashboard")
    parser.add_argument("--check", action="store_true", help="Check current state only")

    args = parser.parse_args()

    auto_explore = JARVISFidelityAutoExploreDashboard()

    if args.check:
        # Just check state
        browser_logs = Path.home() / ".cursor" / "browser-logs"
        snapshot_files = sorted(browser_logs.glob("snapshot-*.log"), reverse=True)

        if snapshot_files:
            state = auto_explore.detect_dashboard_state(snapshot_files[0])
            print(f"\n📊 Dashboard State:")
            print(f"   Is Dashboard: {state['is_dashboard']}")
            print(f"   Is Login: {state['is_login']}")
            print(f"   Confidence: {state['confidence']}")
        else:
            print("\n❌ No snapshot files found")

    elif args.auto:
        result = await auto_explore.auto_explore()
        print(f"\n✅ Auto-explore complete!")
        print(f"   Status: {result.get('status')}")
        print(f"   Message: {result.get('message')}")
        if 'summary' in result:
            print(f"\n📊 Summary:")
            for key, value in result['summary'].items():
                print(f"   {key}: {value}")
    else:
        parser.print_help()


if __name__ == "__main__":


    asyncio.run(main())