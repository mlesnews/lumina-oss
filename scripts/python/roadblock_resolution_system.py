#!/usr/bin/env python3
"""
Roadblock Resolution System

Systematically addresses all identified roadblocks in master and sub to-do lists.
Works in coordination with Autonomous AI Agent.

Tags: #ROADBLOCKS #RESOLUTION #SYSTEMATIC #TODOS @JARVIS @LUMINA  # [ADDRESSED]  # [ADDRESSED]
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("RoadblockResolutionSystem")


class RoadblockResolutionSystem:
    """
    Roadblock Resolution System

    Systematically addresses all roadblocks identified in todos.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize roadblock resolution system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "roadblock_resolution"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Import autonomous agent for roadblock identification
        try:
            from autonomous_ai_agent import AutonomousAIAgent
            self.autonomous_agent = AutonomousAIAgent(project_root)
        except ImportError:
            self.autonomous_agent = None
            logger.warning("   ⚠️  Autonomous AI Agent not available")

        logger.info("✅ Roadblock Resolution System initialized")

    def load_roadblock_report(self, report_file: Optional[Path] = None) -> Dict[str, Any]:
        """
        Load roadblock report

        Args:
            report_file: Path to report file (if None, loads most recent)

        Returns:
            Roadblock report data
        """
        if report_file is None:
            # Find most recent report
            reports = list(self.data_dir.glob("roadblocks_report_*.json"))
            if not reports:
                # Check autonomous_ai directory
                autonomous_dir = self.project_root / "data" / "autonomous_ai"
                if autonomous_dir.exists():
                    reports = list(autonomous_dir.glob("roadblocks_report_*.json"))

            if reports:
                report_file = max(reports, key=lambda p: p.stat().st_mtime)
            else:
                logger.warning("   ⚠️  No roadblock report found")
                return {}

        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"   ❌ Error loading report: {e}")
            return {}

    def resolve_roadblocks_systematically(
        self,
        roadblock_report: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Resolve roadblocks systematically

        Args:
            roadblock_report: Roadblock report (if None, loads most recent)

        Returns:
            Resolution results
        """
        logger.info("=" * 80)
        logger.info("🔧 SYSTEMATIC ROADBLOCK RESOLUTION")
        logger.info("=" * 80)
        logger.info("")

        if roadblock_report is None:
            roadblock_report = self.load_roadblock_report()

        if not roadblock_report:
            logger.warning("   ⚠️  No roadblock report available")
            return {"success": False, "error": "No roadblock report"}

        roadblocks = roadblock_report.get("roadblocks", [])

        if not roadblocks:
            logger.info("   ✅ No roadblocks to resolve")
            return {"success": True, "resolved": 0}

        logger.info(f"   📊 Found {len(roadblocks)} todos with roadblocks")
        logger.info("")

        # Group roadblocks by type
        by_type = {}
        for todo_data in roadblocks:
            for roadblock in todo_data.get("roadblocks", []):
                rb_type = roadblock.get("type")
                if rb_type not in by_type:
                    by_type[rb_type] = []
                by_type[rb_type].append({
                    "todo_id": todo_data.get("todo_id"),
                    "todo_title": todo_data.get("todo_title"),
                    "roadblock": roadblock
                })

        logger.info("   📋 Roadblocks by type:")
        for rb_type, items in sorted(by_type.items()):
            logger.info(f"      {rb_type}: {len(items)}")
        logger.info("")

        # Resolve by priority (high severity first)
        resolution_results = []
        resolved_count = 0

        # Sort by severity
        severity_order = {"high": 0, "medium": 1, "low": 2}

        all_roadblock_items = []
        for todo_data in roadblocks:
            for roadblock in todo_data.get("roadblocks", []):
                all_roadblock_items.append({
                    "todo_id": todo_data.get("todo_id"),
                    "todo_title": todo_data.get("todo_title"),
                    "roadblock": roadblock,
                    "severity": roadblock.get("severity", "medium")
                })

        all_roadblock_items.sort(key=lambda x: severity_order.get(x["severity"], 1))

        logger.info("=" * 80)
        logger.info("🔧 RESOLVING ROADBLOCKS")
        logger.info("=" * 80)
        logger.info("")

        for item in all_roadblock_items:
            todo_id = item["todo_id"]
            todo_title = item["todo_title"]
            roadblock = item["roadblock"]

            logger.info(f"   🔧 Resolving: {todo_title}")
            logger.info(f"      Type: {roadblock.get('type')}")
            logger.info(f"      Description: {roadblock.get('description')}")

            # Address roadblock
            if self.autonomous_agent:
                # Get todo item
                if self.autonomous_agent.master_todo_tracker:
                    todo_item = self.autonomous_agent.master_todo_tracker.items.get(todo_id)
                    if todo_item:
                        address_result = self.autonomous_agent.address_roadblock(
                            roadblock,
                            todo_item.to_dict()
                        )

                        if address_result.get("addressed"):
                            resolved_count += 1
                            logger.info(f"      ✅ Addressed: {address_result.get('action_taken')}")

                            # Update todo status if needed
                            if roadblock.get("type") == "stalled":
                                # Re-evaluate stalled task
                                self.autonomous_agent.master_todo_tracker.update_status(
                                    todo_id,
                                    self.autonomous_agent.TaskStatus.IN_PROGRESS
                                )
                                logger.info(f"      ✅ Updated status: IN_PROGRESS")
                        else:
                            logger.warning(f"      ⚠️  Could not address: {roadblock.get('type')}")

                        resolution_results.append({
                            "todo_id": todo_id,
                            "todo_title": todo_title,
                            "roadblock": roadblock,
                            "resolution": address_result
                        })

            logger.info("")

        # Save resolution results
        resolution_file = self.data_dir / f"resolution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(resolution_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_roadblocks": len(all_roadblock_items),
                "resolved": resolved_count,
                "resolution_results": resolution_results
            }, f, indent=2, ensure_ascii=False, default=str)

        logger.info("=" * 80)
        logger.info("✅ ROADBLOCK RESOLUTION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"   Total roadblocks: {len(all_roadblock_items)}")
        logger.info(f"   Resolved: {resolved_count}")
        logger.info(f"   Results saved: {resolution_file.name}")
        logger.info("")

        return {
            "success": True,
            "total_roadblocks": len(all_roadblock_items),
            "resolved": resolved_count,
            "resolution_results": resolution_results
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Roadblock Resolution System")
        parser.add_argument("--resolve", action="store_true", help="Resolve all roadblocks systematically")
        parser.add_argument("--report", help="Roadblock report file to use")

        args = parser.parse_args()

        system = RoadblockResolutionSystem()

        if args.resolve:
            report = None
            if args.report:
                report = Path(args.report)
            system.resolve_roadblocks_systematically(roadblock_report=report)
        else:
            parser.print_help()

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())