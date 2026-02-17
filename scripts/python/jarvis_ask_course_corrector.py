#!/usr/bin/env python3
"""
JARVIS @ASK Course Corrector

Uses @REARVIEW_MIRROR to guide course correction.
Maintains vigilance as @JEDI @PATHFINDER.
Completes incomplete asks and validates completed asks.

Tags: #ASK_STACK #REARVIEW_MIRROR #JEDI #PATHFINDER #COURSE_CORRECTION @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger, setup_logging
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    setup_logging = lambda: None

logger = get_logger("JARVISAskCourseCorrector")


class AskCourseCorrector:
    """Course correct @ASK stack using @REARVIEW_MIRROR"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "ask_course_correction"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Import ask stack analyzer
        try:
            from jarvis_ask_stack_analyzer import AskStackDelver
            self.delver = AskStackDelver(project_root)
        except ImportError:
            logger.error("Could not import AskStackDelver")
            self.delver = None

    def load_ask_analysis(self) -> Dict[str, Any]:
        try:
            """Load latest ask stack analysis"""
            analysis_dir = project_root / "data" / "ask_stack_delver"
            if analysis_dir.exists():
                analysis_files = list(analysis_dir.glob("ask_stack_delve_*.json"))
                if analysis_files:
                    latest = max(analysis_files, key=lambda p: p.stat().st_mtime)
                    with open(latest, 'r', encoding='utf-8') as f:
                        return json.load(f)
            return {}

        except Exception as e:
            self.logger.error(f"Error in load_ask_analysis: {e}", exc_info=True)
            raise
    def prioritize_incomplete_asks(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prioritize incomplete asks for course correction"""
        incomplete_asks = analysis.get("completion_analysis", {}).get("incomplete_asks", [])

        # Prioritize by file/system importance
        prioritized = []

        for ask_status in incomplete_asks:
            ask = ask_status.get("ask", {})
            file_path = ask.get("file", "")

            # Determine priority
            priority = "LOW"
            if "jarvis" in file_path.lower() or "master" in file_path.lower():
                priority = "HIGH"
            elif "system" in file_path.lower() or "core" in file_path.lower():
                priority = "MEDIUM"

            prioritized.append({
                "ask": ask,
                "status": ask_status.get("status", "UNKNOWN"),
                "priority": priority,
                "file": file_path
            })

        # Sort by priority
        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        prioritized.sort(key=lambda x: priority_order.get(x["priority"], 3))

        return prioritized

    def create_course_correction_plan(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        try:
            """Create course correction plan"""
            logger.info("=" * 80)
            logger.info("⚔️ @JEDI @PATHFINDER - CREATING COURSE CORRECTION PLAN")
            logger.info("=" * 80)
            logger.info("")

            incomplete_asks = analysis.get("completion_analysis", {}).get("incomplete_asks", [])
            unvalidated_asks = analysis.get("completion_analysis", {}).get("unvalidated_asks", [])

            prioritized_incomplete = self.prioritize_incomplete_asks(analysis)

            plan = {
                "timestamp": datetime.now().isoformat(),
                "role": "@JEDI @PATHFINDER",
                "course_correction": {
                    "incomplete_asks": {
                        "total": len(incomplete_asks),
                        "prioritized": prioritized_incomplete[:50],  # Top 50
                        "action": "Review and complete incomplete asks"
                    },
                    "unvalidated_asks": {
                        "total": len(unvalidated_asks),
                        "action": "Validate completed asks"
                    }
                },
                "recommendations": [
                    "Always look to the past - @REARVIEW_MIRROR guides the rudder",
                    "Maintain course - course correct as needed",
                    "Remain vigilant - @JEDI @PATHFINDER role",
                    "Validate all completed asks",
                    "Complete all incomplete asks"
                ]
            }

            logger.info(f"📊 Course Correction Plan Created:")
            logger.info(f"   Incomplete asks: {len(incomplete_asks)}")
            logger.info(f"   Unvalidated asks: {len(unvalidated_asks)}")
            logger.info(f"   Prioritized: {len(prioritized_incomplete[:50])} top priority")
            logger.info("")

            # Save plan
            plan_file = self.data_dir / f"course_correction_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(plan_file, 'w', encoding='utf-8') as f:
                json.dump(plan, f, indent=2, default=str)

            logger.info(f"📄 Plan saved: {plan_file}")
            logger.info("")

            return plan


        except Exception as e:
            self.logger.error(f"Error in create_course_correction_plan: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS @ASK Course Corrector")
        parser.add_argument("--plan", action="store_true", help="Create course correction plan")
        parser.add_argument("--analyze", action="store_true", help="Run analysis first")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        corrector = AskCourseCorrector(project_root)

        if args.analyze or args.plan:
            # Run analysis first if needed
            if args.analyze and corrector.delver:
                logger.info("Running @ASK stack analysis...")
                analysis = corrector.delver.delve_ask_stack()
            else:
                analysis = corrector.load_ask_analysis()

            if args.plan:
                plan = corrector.create_course_correction_plan(analysis)
                print(json.dumps(plan, indent=2, default=str))
        else:
            # Default: create plan
            analysis = corrector.load_ask_analysis()
            if analysis:
                plan = corrector.create_course_correction_plan(analysis)
                print(json.dumps(plan, indent=2, default=str))
            else:
                logger.error("No analysis found. Run with --analyze first.")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()