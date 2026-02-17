#!/usr/bin/env python3
"""
JARVIS Breadcrumbs System

Tracks activities, leaves markers, follows trails.
Breadcrumb navigation and evidence tracking.

Tags: #BREADCRUMBS #TRAIL #MARKERS #EVIDENCE #TRACKING @JARVIS @LUMINA
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
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("JARVISBreadcrumbs")
except ImportError:
    try:
        from lumina_logger import get_logger
        logger = get_logger("JARVISBreadcrumbs")
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("JARVISBreadcrumbs")


class BreadcrumbTracker:
    """Track breadcrumbs - leave markers, follow trails"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "breadcrumbs"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.breadcrumbs_file = self.data_dir / "breadcrumbs.jsonl"
        self.trail_file = self.data_dir / "trail.json"
        self.markers_file = self.data_dir / "markers.json"

        self.current_trail = []

    def drop_breadcrumb(
        self,
        action: str,
        location: str = None,
        context: Dict[str, Any] = None,
        marker_type: str = "info"
    ) -> Dict[str, Any]:
        """Drop a breadcrumb - leave a marker"""
        breadcrumb = {
            "breadcrumb_id": f"crumb_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "location": location or str(self.project_root),
            "context": context or {},
            "marker_type": marker_type,  # info, warning, error, milestone, gap
            "trail_position": len(self.current_trail)
        }

        # Add to current trail
        self.current_trail.append(breadcrumb)

        # Save breadcrumb
        try:
            with open(self.breadcrumbs_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(breadcrumb) + '\n')
        except Exception as e:
            logger.error(f"Error saving breadcrumb: {e}")

        # Update trail
        self._update_trail()

        logger.info(f"🍞 Breadcrumb dropped: {action}")
        logger.info(f"   Location: {location or 'default'}")
        logger.info(f"   Marker type: {marker_type}")

        return breadcrumb

    def mark_milestone(self, milestone: str, description: str = None) -> Dict[str, Any]:
        """Mark a milestone - important breadcrumb"""
        return self.drop_breadcrumb(
            action=f"MILESTONE: {milestone}",
            context={"description": description, "milestone": True},
            marker_type="milestone"
        )

    def mark_gap(self, gap_type: str, gap_description: str, location: str = None) -> Dict[str, Any]:
        """Mark a gap found - strategic gap analysis marker"""
        return self.drop_breadcrumb(
            action=f"GAP FOUND: {gap_type}",
            location=location,
            context={"gap_type": gap_type, "description": gap_description, "gap": True},
            marker_type="gap"
        )

    def mark_integration(self, system: str, integrated_with: str) -> Dict[str, Any]:
        """Mark an integration - system connection"""
        return self.drop_breadcrumb(
            action=f"INTEGRATION: {system} ↔ {integrated_with}",
            context={"system": system, "integrated_with": integrated_with, "integration": True},
            marker_type="milestone"
        )

    def follow_trail(self, from_breadcrumb: str = None, to_breadcrumb: str = None) -> List[Dict[str, Any]]:
        """Follow the breadcrumb trail"""
        trail = []

        try:
            if self.breadcrumbs_file.exists():
                with open(self.breadcrumbs_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            breadcrumb = json.loads(line)
                            trail.append(breadcrumb)
        except Exception as e:
            logger.error(f"Error reading trail: {e}")

        # Filter trail if needed
        if from_breadcrumb:
            start_idx = next((i for i, crumb in enumerate(trail) if crumb.get("breadcrumb_id") == from_breadcrumb), 0)
            trail = trail[start_idx:]

        if to_breadcrumb:
            end_idx = next((i for i, crumb in enumerate(trail) if crumb.get("breadcrumb_id") == to_breadcrumb), len(trail))
            trail = trail[:end_idx + 1]

        logger.info(f"🛤️ Trail followed: {len(trail)} breadcrumbs")

        return trail

    def get_trail_summary(self) -> Dict[str, Any]:
        """Get trail summary"""
        trail = self.follow_trail()

        summary = {
            "total_breadcrumbs": len(trail),
            "by_type": {},
            "milestones": [],
            "gaps": [],
            "integrations": [],
            "recent": trail[-10:] if trail else [],
            "oldest": trail[0] if trail else None,
            "newest": trail[-1] if trail else None
        }

        # Count by type
        for crumb in trail:
            marker_type = crumb.get("marker_type", "info")
            summary["by_type"][marker_type] = summary["by_type"].get(marker_type, 0) + 1

            # Collect milestones
            if crumb.get("context", {}).get("milestone"):
                summary["milestones"].append(crumb)

            # Collect gaps
            if crumb.get("context", {}).get("gap"):
                summary["gaps"].append(crumb)

            # Collect integrations
            if crumb.get("context", {}).get("integration"):
                summary["integrations"].append(crumb)

        return summary

    def find_breadcrumbs_by_action(self, action_pattern: str) -> List[Dict[str, Any]]:
        """Find breadcrumbs by action pattern"""
        trail = self.follow_trail()
        matching = [crumb for crumb in trail if action_pattern.lower() in crumb.get("action", "").lower()]

        logger.info(f"🔍 Found {len(matching)} breadcrumbs matching '{action_pattern}'")

        return matching

    def find_breadcrumbs_by_location(self, location_pattern: str) -> List[Dict[str, Any]]:
        """Find breadcrumbs by location pattern"""
        trail = self.follow_trail()
        matching = [crumb for crumb in trail if location_pattern.lower() in crumb.get("location", "").lower()]

        logger.info(f"🔍 Found {len(matching)} breadcrumbs at location matching '{location_pattern}'")

        return matching

    def _update_trail(self):
        """Update trail file"""
        try:
            trail_data = {
                "last_updated": datetime.now().isoformat(),
                "trail_length": len(self.current_trail),
                "recent_breadcrumbs": self.current_trail[-10:] if self.current_trail else []
            }

            with open(self.trail_file, 'w', encoding='utf-8') as f:
                json.dump(trail_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error updating trail: {e}")


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Breadcrumbs")
        parser.add_argument("--drop", type=str, metavar="ACTION", help="Drop a breadcrumb")
        parser.add_argument("--milestone", type=str, metavar="MILESTONE", help="Mark a milestone")
        parser.add_argument("--gap", type=str, nargs=2, metavar=("TYPE", "DESCRIPTION"), help="Mark a gap")
        parser.add_argument("--integration", type=str, nargs=2, metavar=("SYSTEM", "INTEGRATED_WITH"), help="Mark an integration")
        parser.add_argument("--follow", action="store_true", help="Follow the trail")
        parser.add_argument("--summary", action="store_true", help="Get trail summary")
        parser.add_argument("--find-action", type=str, metavar="PATTERN", help="Find breadcrumbs by action pattern")
        parser.add_argument("--find-location", type=str, metavar="PATTERN", help="Find breadcrumbs by location pattern")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        tracker = BreadcrumbTracker(project_root)

        if args.drop:
            crumb = tracker.drop_breadcrumb(args.drop)
            print(f"🍞 Breadcrumb dropped: {crumb['breadcrumb_id']}")
            print(json.dumps(crumb, indent=2, default=str))

        elif args.milestone:
            crumb = tracker.mark_milestone(args.milestone)
            print(f"🏁 Milestone marked: {crumb['breadcrumb_id']}")
            print(json.dumps(crumb, indent=2, default=str))

        elif args.gap:
            crumb = tracker.mark_gap(args.gap[0], args.gap[1])
            print(f"🔍 Gap marked: {crumb['breadcrumb_id']}")
            print(json.dumps(crumb, indent=2, default=str))

        elif args.integration:
            crumb = tracker.mark_integration(args.integration[0], args.integration[1])
            print(f"🔗 Integration marked: {crumb['breadcrumb_id']}")
            print(json.dumps(crumb, indent=2, default=str))

        elif args.follow:
            trail = tracker.follow_trail()
            print("=" * 80)
            print("🛤️ BREADCRUMB TRAIL")
            print("=" * 80)
            print(f"\nTotal breadcrumbs: {len(trail)}")
            print("\nRecent trail:")
            for crumb in trail[-20:]:  # Show last 20
                print(f"  [{crumb['timestamp']}] {crumb['action']}")
                if crumb.get('location'):
                    print(f"    Location: {crumb['location']}")
            print("=" * 80)

        elif args.summary:
            summary = tracker.get_trail_summary()
            print("=" * 80)
            print("🍞 BREADCRUMB SUMMARY")
            print("=" * 80)
            print(f"\nTotal breadcrumbs: {summary['total_breadcrumbs']}")
            print(f"\nBy type:")
            for marker_type, count in summary['by_type'].items():
                print(f"  {marker_type}: {count}")
            print(f"\nMilestones: {len(summary['milestones'])}")
            print(f"Gaps found: {len(summary['gaps'])}")
            print(f"Integrations: {len(summary['integrations'])}")
            print("=" * 80)
            print(json.dumps(summary, indent=2, default=str))

        elif args.find_action:
            matching = tracker.find_breadcrumbs_by_action(args.find_action)
            print(f"Found {len(matching)} breadcrumbs matching '{args.find_action}'")
            for crumb in matching:
                print(f"  [{crumb['timestamp']}] {crumb['action']}")

        elif args.find_location:
            matching = tracker.find_breadcrumbs_by_location(args.find_location)
            print(f"Found {len(matching)} breadcrumbs at location matching '{args.find_location}'")
            for crumb in matching:
                print(f"  [{crumb['timestamp']}] {crumb['action']} @ {crumb.get('location', 'unknown')}")

        else:
            # Default: show summary
            summary = tracker.get_trail_summary()
            print("=" * 80)
            print("🍞 BREADCRUMBS")
            print("=" * 80)
            print(f"\nTotal breadcrumbs: {summary['total_breadcrumbs']}")
            print(f"Milestones: {len(summary['milestones'])}")
            print(f"Gaps found: {len(summary['gaps'])}")
            print(f"Integrations: {len(summary['integrations'])}")
            print("\nRecent breadcrumbs:")
            for crumb in summary['recent']:
                print(f"  [{crumb['timestamp']}] {crumb['action']}")
            print("=" * 80)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()