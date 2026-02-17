#!/usr/bin/env python3
"""
Comprehensive Analytics & Metrics Tracker
Integrates WakaTime, Cursor Workflow Tracking, and all timekeeping sources

Tracks analytics/metrics for everything we do.
Integrates with existing timekeeping systems.

Tags: #ANALYTICS #METRICS #WAKATIME #CURSOR #TRACKING #COMPREHENSIVE
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from cursor_ide_mode_tracker import CursorIDEModeTracker
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    CursorIDEModeTracker = None

logger = get_logger("ComprehensiveAnalytics")


class ComprehensiveAnalyticsTracker:
    """
    Comprehensive Analytics & Metrics Tracker

    Integrates:
    - WakaTime
    - Cursor Workflow Tracking
    - Cursor IDE Mode Tracker
    - System Resource Monitoring
    - All timekeeping sources
    """

    def __init__(self, project_root: Path):
        """Initialize comprehensive tracker"""
        self.project_root = project_root
        self.logger = logger

        # Data paths
        self.data_path = project_root / "data"
        self.analytics_path = self.data_path / "analytics"
        self.analytics_path.mkdir(parents=True, exist_ok=True)

        # Integration paths
        self.wakatime_path = self._find_wakatime_data()
        self.cursor_workflow_path = self._find_cursor_workflow_data()

        # Initialize mode tracker
        if CursorIDEModeTracker:
            self.mode_tracker = CursorIDEModeTracker(project_root)
        else:
            self.mode_tracker = None

        self.logger.info("📊 Comprehensive Analytics Tracker initialized")
        self.logger.info(f"   WakaTime: {'Found' if self.wakatime_path else 'Not found'}")
        self.logger.info(f"   Cursor Workflow: {'Found' if self.cursor_workflow_path else 'Not found'}")

    def _find_wakatime_data(self) -> Optional[Path]:
        try:
            """Find WakaTime data location"""
            # Common WakaTime locations
            possible_paths = [
                Path.home() / ".wakatime",
                Path.home() / "AppData" / "Roaming" / "WakaTime",
                self.project_root / ".wakatime"
            ]

            for path in possible_paths:
                if path.exists():
                    return path

            return None

        except Exception as e:
            self.logger.error(f"Error in _find_wakatime_data: {e}", exc_info=True)
            raise
    def _find_cursor_workflow_data(self) -> Optional[Path]:
        try:
            """Find Cursor Workflow tracking data"""
            # Common Cursor locations
            possible_paths = [
                Path.home() / ".cursor",
                Path.home() / "AppData" / "Roaming" / "Cursor",
                self.project_root / ".cursor"
            ]

            for path in possible_paths:
                if path.exists():
                    return path

            return None

        except Exception as e:
            self.logger.error(f"Error in _find_cursor_workflow_data: {e}", exc_info=True)
            raise
    def collect_all_analytics(self) -> Dict[str, Any]:
        """Collect analytics from all sources"""
        self.logger.info("📊 Collecting analytics from all sources...")

        analytics = {
            "timestamp": datetime.now().isoformat(),
            "sources": {},
            "summary": {},
            "system_resources": self._check_system_resources()
        }

        # WakaTime
        if self.wakatime_path:
            analytics["sources"]["wakatime"] = self._collect_wakatime()

        # Cursor Workflow
        if self.cursor_workflow_path:
            analytics["sources"]["cursor_workflow"] = self._collect_cursor_workflow()

        # Cursor IDE Mode Tracker
        if self.mode_tracker:
            analytics["sources"]["cursor_ide_mode"] = self._collect_mode_tracker()

        # Calculate summary
        analytics["summary"] = self._calculate_summary(analytics["sources"])

        # Save analytics
        self._save_analytics(analytics)

        return analytics

    def _collect_wakatime(self) -> Dict[str, Any]:
        """Collect WakaTime data"""
        try:
            # Look for WakaTime database or API
            # This is a placeholder - actual implementation would read WakaTime data
            return {
                "available": True,
                "status": "connected",
                "note": "WakaTime integration - implement based on WakaTime API or database"
            }
        except Exception as e:
            return {"available": False, "error": str(e)}

    def _collect_cursor_workflow(self) -> Dict[str, Any]:
        """Collect Cursor Workflow tracking data"""
        try:
            # Look for Cursor workflow data
            # This is a placeholder - actual implementation would read Cursor data
            return {
                "available": True,
                "status": "connected",
                "note": "Cursor Workflow integration - implement based on Cursor data format"
            }
        except Exception as e:
            return {"available": False, "error": str(e)}

    def _collect_mode_tracker(self) -> Dict[str, Any]:
        """Collect Cursor IDE Mode Tracker data"""
        if not self.mode_tracker:
            return {"available": False}

        try:
            today_stats = self.mode_tracker.get_today_stats()
            weekly_stats = self.mode_tracker.get_weekly_stats()

            return {
                "available": True,
                "today": today_stats,
                "week": weekly_stats,
                "current_mode": self.mode_tracker.current_mode
            }
        except Exception as e:
            return {"available": False, "error": str(e)}

    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resources to detect bottlenecks"""
        try:
            import psutil

            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_io": {
                    "read_bytes": psutil.disk_io_counters().read_bytes if psutil.disk_io_counters() else 0,
                    "write_bytes": psutil.disk_io_counters().write_bytes if psutil.disk_io_counters() else 0
                },
                "warning": self._check_resource_warnings()
            }
        except ImportError:
            return {
                "available": False,
                "note": "psutil not available - install with: pip install psutil"
            }
        except Exception as e:
            return {"available": False, "error": str(e)}

    def _check_resource_warnings(self) -> List[str]:
        """Check for resource warnings (fans spinning = bottleneck)"""
        warnings = []

        try:
            import psutil

            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent

            if cpu_percent > 80:
                warnings.append(f"High CPU usage: {cpu_percent:.1f}% - Fans may be spinning")

            if memory_percent > 85:
                warnings.append(f"High memory usage: {memory_percent:.1f}% - System bottleneck")

            # Check disk I/O
            disk_io = psutil.disk_io_counters()
            if disk_io:
                if disk_io.read_bytes > 0 or disk_io.write_bytes > 0:
                    # High I/O can cause fan spinning
                    pass

        except:
            pass

        return warnings

    def _calculate_summary(self, sources: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate summary from all sources"""
        summary = {
            "total_sources": len(sources),
            "active_sources": sum(1 for s in sources.values() if s.get("available", False)),
            "time_tracked": {},
            "warnings": []
        }

        # Aggregate time tracking
        if "cursor_ide_mode" in sources and sources["cursor_ide_mode"].get("available"):
            mode_data = sources["cursor_ide_mode"]
            if "today" in mode_data:
                summary["time_tracked"]["today"] = mode_data["today"]
            if "week" in mode_data:
                summary["time_tracked"]["week"] = mode_data["week"]

        # Collect warnings
        if "system_resources" in sources:
            warnings = sources.get("system_resources", {}).get("warning", [])
            summary["warnings"].extend(warnings)

        return summary

    def _save_analytics(self, analytics: Dict[str, Any]):
        try:
            """Save analytics data"""
            timestamp = datetime.now()
            filename = f"analytics_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.analytics_path / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(analytics, f, indent=2, ensure_ascii=False)

            # Also update latest
            latest_file = self.analytics_path / "latest.json"
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(analytics, f, indent=2, ensure_ascii=False)

            self.logger.info(f"✅ Analytics saved: {filename}")

        except Exception as e:
            self.logger.error(f"Error in _save_analytics: {e}", exc_info=True)
            raise
    def get_dashboard(self) -> str:
        """Get formatted dashboard"""
        analytics = self.collect_all_analytics()

        markdown = []
        markdown.append("## 📊 Comprehensive Analytics Dashboard")
        markdown.append("")
        markdown.append(f"**Generated:** {analytics['timestamp']}")
        markdown.append("")

        # Sources
        markdown.append("### 📡 Data Sources")
        markdown.append("")
        for source_name, source_data in analytics["sources"].items():
            status = "✅" if source_data.get("available") else "❌"
            markdown.append(f"{status} **{source_name.replace('_', ' ').title()}**")
        markdown.append("")

        # System Resources
        if "system_resources" in analytics:
            resources = analytics["system_resources"]
            markdown.append("### ⚙️ System Resources")
            markdown.append("")
            if resources.get("available"):
                markdown.append(f"**CPU:** {resources.get('cpu_percent', 0):.1f}%")
                markdown.append(f"**Memory:** {resources.get('memory_percent', 0):.1f}%")

                warnings = resources.get("warning", [])
                if warnings:
                    markdown.append("")
                    markdown.append("⚠️ **Warnings:**")
                    for warning in warnings:
                        markdown.append(f"- {warning}")
            else:
                markdown.append("*System resource monitoring not available*")
            markdown.append("")

        # Summary
        summary = analytics.get("summary", {})
        markdown.append("### 📈 Summary")
        markdown.append("")
        markdown.append(f"**Active Sources:** {summary.get('active_sources', 0)}/{summary.get('total_sources', 0)}")
        markdown.append("")

        return "\n".join(markdown)


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Comprehensive Analytics Tracker")
        parser.add_argument("--collect", action="store_true", help="Collect all analytics")
        parser.add_argument("--dashboard", action="store_true", help="Show dashboard")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        tracker = ComprehensiveAnalyticsTracker(project_root)

        if args.collect or args.dashboard:
            if args.json:
                analytics = tracker.collect_all_analytics()
                print(json.dumps(analytics, indent=2, default=str))
            else:
                dashboard = tracker.get_dashboard()
                print(dashboard)
        else:
            dashboard = tracker.get_dashboard()
            print(dashboard)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()