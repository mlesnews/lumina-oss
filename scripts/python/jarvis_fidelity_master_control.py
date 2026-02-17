#!/usr/bin/env python3
"""
JARVIS Fidelity Master Control System
@TRIAD protocol - Complete @ff exploration and full JARVIS control

Coordinates:
- ProtonPass credential retrieval
- Automated login
- @ff feature exploration
- JARVIS control interface generation
- Full automated control of all features

Tags: #FIDELITY #@TRIAD #@FF #JARVIS #MASTER_CONTROL
"""

import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
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

logger = get_logger("JARVISFidelityMasterControl")

# Import exploration and control modules
try:
    from jarvis_fidelity_protonpass_login import JARVISFidelityProtonPassLogin, ProtonPassCLI
    from jarvis_fidelity_complete_exploration import JARVISFidelityCompleteExploration
    from jarvis_fidelity_automated_control import JARVISFidelityAutomatedControl
except ImportError as e:
    logger.warning(f"Some modules not available: {e}")


class JARVISFidelityMasterControl:
    """
    Master Control System for Fidelity Dashboard

    @TRIAD Protocol:
    - @TRIAGE: Identify and map all features
    - @BAU: Standardized exploration and control
    - @DOIT: Autonomous execution and control
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize master control system"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.output_dir = self.project_root / "data" / "fidelity_exploration"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize subsystems
        self.login_system = JARVISFidelityProtonPassLogin(self.project_root)
        self.explorer = JARVISFidelityCompleteExploration(self.project_root)
        self.controller = JARVISFidelityAutomatedControl(self.project_root)

        logger.info("=" * 70)
        logger.info("🎮 JARVIS FIDELITY MASTER CONTROL SYSTEM")
        logger.info("=" * 70)
        logger.info("   @TRIAD Protocol: ACTIVE")
        logger.info("   @ff Exploration: ENABLED")
        logger.info("   Full Control: READY")
        logger.info("")

    async def execute_full_workflow(self) -> Dict[str, Any]:
        """
        Execute complete @TRIAD workflow:
        1. @TRIAGE: Get credentials and identify dashboard state
        2. @BAU: Perform @ff exploration and mapping
        3. @DOIT: Generate control interface and enable automation
        """
        logger.info("=" * 70)
        logger.info("🚀 EXECUTING @TRIAD WORKFLOW")
        logger.info("=" * 70)
        logger.info("")

        workflow_result = {
            "started_at": datetime.now().isoformat(),
            "triad_phases": {},
            "final_status": "in_progress"
        }

        # Phase 1: @TRIAGE - Identify and prepare
        logger.info("PHASE 1: @TRIAGE - Identification and Preparation")
        logger.info("-" * 70)

        triage_result = await self._triad_triage()
        workflow_result["triad_phases"]["triage"] = triage_result

        logger.info("")

        # Phase 2: @BAU - Standardized exploration
        logger.info("PHASE 2: @BAU - Standardized @ff Exploration")
        logger.info("-" * 70)

        bau_result = await self._triad_bau()
        workflow_result["triad_phases"]["bau"] = bau_result

        logger.info("")

        # Phase 3: @DOIT - Autonomous execution
        logger.info("PHASE 3: @DOIT - Autonomous Control Generation")
        logger.info("-" * 70)

        doit_result = await self._triad_doit()
        workflow_result["triad_phases"]["doit"] = doit_result

        logger.info("")
        logger.info("=" * 70)
        logger.info("✅ @TRIAD WORKFLOW COMPLETE")
        logger.info("=" * 70)

        workflow_result["final_status"] = "completed"
        workflow_result["completed_at"] = datetime.now().isoformat()

        return workflow_result

    async def _triad_triage(self) -> Dict[str, Any]:
        """@TRIAGE: Identify dashboard state and prepare"""
        logger.info("📋 @TRIAGE: Identifying dashboard state...")

        triage_result = {
            "phase": "triage",
            "credentials_available": False,
            "dashboard_state": "unknown",
            "actions_required": []
        }

        # Check for credentials
        logger.info("   Checking ProtonPass credentials...")
        credentials = self.login_system.get_fidelity_credentials("Fidelity")

        if credentials.get("password"):
            triage_result["credentials_available"] = True
            logger.info("   ✅ Credentials available")
        else:
            logger.warning("   ⚠️  Credentials not found in ProtonPass")
            triage_result["actions_required"].append("Store Fidelity credentials in ProtonPass")

        # Check dashboard state (would use browser MCP)
        logger.info("   Checking dashboard state...")
        # This would use browser_snapshot() to check current state
        triage_result["dashboard_state"] = "login_page"  # Detected from earlier snapshot

        if triage_result["dashboard_state"] == "login_page":
            triage_result["actions_required"].append("Login to Fidelity dashboard")

        logger.info(f"   Actions required: {len(triage_result['actions_required'])}")

        return triage_result

    async def _triad_bau(self) -> Dict[str, Any]:
        """@BAU: Standardized @ff exploration"""
        logger.info("🔍 @BAU: Performing @ff exploration...")

        bau_result = {
            "phase": "bau",
            "exploration_complete": False,
            "elements_mapped": 0,
            "features_identified": 0
        }

        # Find latest snapshot or capture new one
        browser_logs = Path.home() / ".cursor" / "browser-logs"
        snapshot_files = sorted(browser_logs.glob("snapshot-*.log"), reverse=True)

        if snapshot_files:
            logger.info(f"   Processing snapshot: {snapshot_files[0].name}")
            feature_map = self.explorer.process_snapshot_file(snapshot_files[0])

            bau_result["elements_mapped"] = len(feature_map.get("elements", []))
            bau_result["features_identified"] = len(feature_map.get("trading_features", []))
            bau_result["exploration_complete"] = True

            logger.info(f"   ✅ Mapped {bau_result['elements_mapped']} elements")
            logger.info(f"   ✅ Identified {bau_result['features_identified']} trading features")
        else:
            logger.warning("   ⚠️  No snapshot available - capture one with browser_snapshot()")
            bau_result["actions_required"] = ["Capture browser snapshot"]

        return bau_result

    async def _triad_doit(self) -> Dict[str, Any]:
        """@DOIT: Generate control interface and enable automation"""
        logger.info("⚡ @DOIT: Generating control interface...")

        doit_result = {
            "phase": "doit",
            "control_interface_generated": False,
            "control_methods": 0
        }

        # Load or generate control interface
        if self.controller.load_control_interface():
            doit_result["control_interface_generated"] = True
            doit_result["control_methods"] = len(
                self.controller.control_interface.get("feature_controls", {})
            )

            logger.info(f"   ✅ Control interface ready")
            logger.info(f"   ✅ {doit_result['control_methods']} control methods available")
        else:
            logger.warning("   ⚠️  Control interface not available")
            doit_result["actions_required"] = ["Run complete exploration first"]

        return doit_result

    def save_workflow_result(self, result: Dict[str, Any]) -> Path:
        try:
            """Save workflow result"""
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"triad_workflow_{timestamp}.json"

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

    parser = argparse.ArgumentParser(description="JARVIS Fidelity Master Control")
    parser.add_argument("--workflow", action="store_true", help="Execute full @TRIAD workflow")
    parser.add_argument("--triage", action="store_true", help="Run @TRIAGE phase only")
    parser.add_argument("--bau", action="store_true", help="Run @BAU phase only")
    parser.add_argument("--doit", action="store_true", help="Run @DOIT phase only")

    args = parser.parse_args()

    master = JARVISFidelityMasterControl()

    if args.workflow:
        result = await master.execute_full_workflow()
        output_file = master.save_workflow_result(result)
        print(f"\n✅ @TRIAD workflow complete!")
        print(f"   Result saved to: {output_file}")
    elif args.triage:
        result = await master._triad_triage()
        print(json.dumps(result, indent=2))
    elif args.bau:
        result = await master._triad_bau()
        print(json.dumps(result, indent=2))
    elif args.doit:
        result = await master._triad_doit()
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":


    asyncio.run(main())