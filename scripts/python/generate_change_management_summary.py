#!/usr/bin/env python3
"""
Generate Change Management Summary Report

Creates comprehensive summary of all team feedback, responses, and final decision.

Tags: #CHANGE_MANAGEMENT #SUMMARY #DECISION @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    logger = get_logger("ChangeManagementSummary")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ChangeManagementSummary")


def main():
    try:
        """Generate comprehensive summary"""
        data_dir = project_root / "data" / "change_management"

        # Load decision report
        decision_reports = list(data_dir.glob("change_decision_*.json"))
        decision_report = None
        if decision_reports:
            with open(max(decision_reports, key=lambda p: p.stat().st_mtime), 'r') as f:
                decision_report = json.load(f)

        # Load team responses
        response_files = list((data_dir / "team_responses").glob("team_responses_*.json"))
        responses = None
        if response_files:
            with open(max(response_files, key=lambda p: p.stat().st_mtime), 'r') as f:
                responses = json.load(f)

        print("=" * 80)
        print("🔄 CHANGE MANAGEMENT - COMPREHENSIVE SUMMARY")
        print("=" * 80)
        print("")

        if decision_report:
            print("DECISION TREE ROUTING:")
            path = decision_report.get("decision_tree_result", {}).get("path", [])
            print(f"   {' → '.join(path)}")
            print("")

        if responses:
            rec = responses.get("final_recommendation", {})
            print("FINAL RECOMMENDATION:")
            print(f"   {rec.get('recommendation', 'UNKNOWN')}")
            print(f"   Ready to Proceed: {'✅ YES' if rec.get('ready') else '❌ NO'}")
            if rec.get("conditions"):
                print("   Conditions:")
                for condition in rec["conditions"]:
                    print(f"      - {condition}")
            print("")

        print("=" * 80)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":

    main()