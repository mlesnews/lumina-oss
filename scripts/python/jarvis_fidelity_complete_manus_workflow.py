#!/usr/bin/env python3
"""
JARVIS Fidelity Complete @MANUS Workflow
Orchestrates complete exploration, keyboard shortcuts, and @MANUS control generation

This script:
1. Captures dashboard snapshot
2. Captures network requests
3. Performs full @ff exploration
4. Extracts keyboard shortcuts
5. Generates complete @MANUS control interface

Tags: #FIDELITY #@MANUS #@FF #WORKFLOW #JARVIS
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

logger = get_logger("JARVISFidelityCompleteMANUSWorkflow")

# Import exploration module
try:
    from jarvis_fidelity_full_exploration_manus import JARVISFidelityFullExplorationMANUS
except ImportError as e:
    logger.error(f"Failed to import exploration module: {e}")
    sys.exit(1)


class JARVISFidelityCompleteMANUSWorkflow:
    """
    Complete @MANUS Workflow Orchestrator

    Coordinates full exploration and @MANUS control generation
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize workflow orchestrator"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.output_dir = self.project_root / "data" / "fidelity_exploration"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.explorer = JARVISFidelityFullExplorationMANUS(self.project_root)

        logger.info("=" * 70)
        logger.info("🚀 JARVIS FIDELITY COMPLETE @MANUS WORKFLOW")
        logger.info("=" * 70)
        logger.info("")

    async def execute_full_workflow(self) -> Dict[str, Any]:
        """Execute complete workflow"""
        logger.info("=" * 70)
        logger.info("📋 EXECUTING COMPLETE @MANUS WORKFLOW")
        logger.info("=" * 70)
        logger.info("")

        workflow_result = {
            "started_at": datetime.now().isoformat(),
            "steps": {},
            "final_status": "in_progress"
        }

        # Step 1: Capture snapshot (via MCP Browser - user should run browser_snapshot())
        logger.info("STEP 1: Dashboard Snapshot")
        logger.info("-" * 70)
        logger.info("   ⚠️  Please ensure you're logged into Fidelity dashboard")
        logger.info("   ⚠️  Run: browser_snapshot() in MCP Browser")
        logger.info("   ⚠️  Snapshot will be auto-detected from browser logs")
        logger.info("")

        # Step 2: Capture network requests (via MCP Browser)
        logger.info("STEP 2: Network Requests")
        logger.info("-" * 70)
        logger.info("   ⚠️  Run: browser_network_requests() in MCP Browser")
        logger.info("   ⚠️  Network data will be processed for API endpoints")
        logger.info("")

        # Step 3: Process snapshot
        logger.info("STEP 3: Processing Snapshot")
        logger.info("-" * 70)
        browser_logs = Path.home() / ".cursor" / "browser-logs"
        snapshot_files = sorted(browser_logs.glob("snapshot-*.log"), reverse=True)

        if not snapshot_files:
            logger.error("   ❌ No snapshot files found")
            logger.info("   Please capture snapshot first using browser_snapshot()")
            workflow_result["final_status"] = "failed"
            workflow_result["error"] = "No snapshot files found"
            return workflow_result

        latest_snapshot = snapshot_files[0]
        logger.info(f"   📄 Using snapshot: {latest_snapshot.name}")
        feature_map = self.explorer.process_snapshot_file(latest_snapshot)
        workflow_result["steps"]["snapshot_processing"] = {
            "file": latest_snapshot.name,
            "elements_found": len(feature_map.get("elements", []))
        }
        logger.info("")

        # Step 4: Process network requests (if available)
        logger.info("STEP 4: Processing Network Requests")
        logger.info("-" * 70)
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

        # Note: Network requests would come from browser_network_requests() MCP call
        # For now, we'll use empty structure
        logger.info("   ⚠️  Network requests should be captured via browser_network_requests()")
        logger.info("   ⚠️  API endpoints will be discovered from network data")
        workflow_result["steps"]["network_processing"] = {
            "endpoints_found": 0,
            "note": "Network requests should be captured separately"
        }
        logger.info("")

        # Step 5: Generate @MANUS control interface
        logger.info("STEP 5: Generating @MANUS Control Interface")
        logger.info("-" * 70)
        manus_control = self.explorer.generate_manus_control_interface(feature_map, api_endpoints)
        workflow_result["steps"]["manus_generation"] = {
            "control_methods": len(manus_control.get("control_methods", {})),
            "trading_controls": len(manus_control.get("control_areas", {}).get("trading", {})),
            "chart_controls": len(manus_control.get("control_areas", {}).get("charts", {})),
            "keyboard_shortcuts": len(manus_control.get("control_areas", {}).get("keyboard_shortcuts", {}))
        }
        logger.info("")

        # Step 6: Create comprehensive report
        logger.info("STEP 6: Creating Comprehensive Report")
        logger.info("-" * 70)
        report = self.explorer.create_comprehensive_report(feature_map, manus_control, api_endpoints)
        workflow_result["steps"]["report_creation"] = {
            "total_elements": report["summary"]["total_elements"],
            "control_methods": report["summary"]["manus_control_methods"],
            "keyboard_shortcuts": report["summary"]["keyboard_shortcuts"]
        }
        logger.info("")

        # Step 7: Save exploration
        logger.info("STEP 7: Saving Exploration Results")
        logger.info("-" * 70)
        output_file = self.explorer.save_exploration(report)
        workflow_result["steps"]["saving"] = {
            "output_file": str(output_file)
        }
        logger.info("")

        # Complete
        logger.info("=" * 70)
        logger.info("✅ COMPLETE @MANUS WORKFLOW FINISHED")
        logger.info("=" * 70)
        logger.info("")
        logger.info(f"📊 Summary:")
        logger.info(f"   Total Elements: {report['summary']['total_elements']}")
        logger.info(f"   @MANUS Control Methods: {report['summary']['manus_control_methods']}")
        logger.info(f"   Keyboard Shortcuts: {report['summary']['keyboard_shortcuts']}")
        logger.info(f"   Trading Features: {report['summary']['trading_features']}")
        logger.info(f"   Charts: {report['summary']['charts']}")
        logger.info(f"   API Endpoints: {report['summary']['api_endpoints']}")
        logger.info("")
        logger.info(f"📁 Output File: {output_file}")
        logger.info("")

        workflow_result["final_status"] = "completed"
        workflow_result["completed_at"] = datetime.now().isoformat()
        workflow_result["output_file"] = str(output_file)
        workflow_result["summary"] = report["summary"]

        return workflow_result

    def save_workflow_result(self, result: Dict[str, Any]) -> Path:
        try:
            """Save workflow result"""
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"manus_workflow_{timestamp}.json"

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

    parser = argparse.ArgumentParser(description="JARVIS Fidelity Complete @MANUS Workflow")
    parser.add_argument("--workflow", action="store_true", help="Execute complete workflow")

    args = parser.parse_args()

    if args.workflow:
        workflow = JARVISFidelityCompleteMANUSWorkflow()
        result = await workflow.execute_full_workflow()
        output_file = workflow.save_workflow_result(result)
        print(f"\n✅ Complete @MANUS workflow finished!")
        print(f"   Result saved to: {output_file}")
    else:
        parser.print_help()


if __name__ == "__main__":


    asyncio.run(main())