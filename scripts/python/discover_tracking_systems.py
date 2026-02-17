"""
PUBLIC: Discover All Development Tracking Systems
Location: scripts/python/discover_tracking_systems.py
License: MIT

Discovers and reports on all development/code tracking systems in LUMINA.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from collections import defaultdict


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TrackingSystemDiscovery:
    """Discover all development tracking systems."""

    def __init__(self, project_root: Path):
        """
        Initialize discovery.

        Args:
            project_root: Path to project root
        """
        self.project_root = project_root
        self.config_path = project_root / "config"
        self.data_path = project_root / "data"

    def discover_git_tracking(self) -> Dict[str, Any]:
        """
        Discover Git-based tracking statistics.

        Returns:
            Dictionary with Git statistics
        """
        stats = {
            "available": False,
            "system": "Git",
            "type": "Version Control Tracking"
        }

        try:
            # Check if git repo
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                return stats

            stats["available"] = True

            # Get commit count (all time)
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                stats["total_commits"] = int(result.stdout.strip())

            # Get commits in last year (memory-efficient counting)
            result = subprocess.run(
                ["git", "log", "--oneline", "--since=1 year ago"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=15
            )
            if result.returncode == 0:
                # Count without loading all into memory
                stats["commits_last_year"] = sum(1 for l in result.stdout.split('\n') if l.strip())

            # Get commits in last 30 days (memory-efficient)
            result = subprocess.run(
                ["git", "log", "--oneline", "--since=30 days ago"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=15
            )
            if result.returncode == 0:
                stats["commits_last_30_days"] = sum(1 for l in result.stdout.split('\n') if l.strip())

            # Get commits in last 7 days (memory-efficient)
            result = subprocess.run(
                ["git", "log", "--oneline", "--since=7 days ago"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                stats["commits_last_7_days"] = sum(1 for l in result.stdout.split('\n') if l.strip())

            # Get file count (with memory-efficient approach for large repos)
            try:
                result = subprocess.run(
                    ["git", "ls-files"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    # Count lines without loading all into memory
                    file_count = sum(1 for line in result.stdout.split('\n') if line.strip())
                    stats["tracked_files"] = file_count
                    stats["file_count_method"] = "efficient"
            except subprocess.TimeoutExpired:
                # Fallback: use git count-objects for large repos
                try:
                    result = subprocess.run(
                        ["git", "count-objects", "-v"],
                        cwd=self.project_root,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        stats["tracked_files"] = "large_repo_estimate"
                        stats["file_count_method"] = "estimate"
                        stats["note"] = "Repository too large for exact count"
                except Exception:
                    stats["tracked_files"] = None
                    stats["file_count_method"] = "failed"
                    stats["note"] = "Could not count files (resource limits)"

            # Get contributors
            result = subprocess.run(
                ["git", "shortlog", "-sn", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                contributors = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.strip().split('\t')
                        if len(parts) == 2:
                            contributors.append({
                                "commits": int(parts[0].strip()),
                                "name": parts[1].strip()
                            })
                stats["contributors"] = contributors[:10]  # Top 10

            # Get first and last commit dates
            result = subprocess.run(
                ["git", "log", "--reverse", "--format=%ai", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                first_commit = result.stdout.strip().split('\n')[0]
                stats["first_commit_date"] = first_commit

            result = subprocess.run(
                ["git", "log", "-1", "--format=%ai", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                stats["last_commit_date"] = result.stdout.strip()

        except subprocess.TimeoutExpired:
            logger.warning("Git operations timed out - repository may be too large")
            stats["error"] = "timeout"
            stats["note"] = "Repository size exceeded operation timeout"
        except MemoryError:
            logger.error("Out of memory during Git operations")
            stats["error"] = "memory_error"
            stats["note"] = "Insufficient memory for operation"
        except Exception as e:
            logger.error(f"Failed to get Git stats: {e}", exc_info=True)
            stats["error"] = str(e)
            stats["note"] = "Error during Git statistics collection"

        return stats

    def discover_request_tracking(self) -> Dict[str, Any]:
        """
        Discover request tracking analytics.

        Returns:
            Dictionary with request tracking stats
        """
        analytics_file = self.data_path / "request_tracking" / "analytics.json"

        if not analytics_file.exists():
            return {
                "available": False,
                "system": "Request Tracking Analytics",
                "type": "Request Analytics"
            }

        try:
            with open(analytics_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            return {
                "available": True,
                "system": "Request Tracking Analytics",
                "type": "Request Analytics",
                "generated_at": data.get("generated_at"),
                "total_requests": data.get("total_requests", 0),
                "by_status": data.get("by_status", {}),
                "by_escalation": data.get("by_escalation", {}),
                "by_management": data.get("by_management", {}),
                "raw_data": data
            }
        except Exception as e:
            logger.error(f"Failed to read request tracking: {e}", exc_info=True)
            return {
                "available": False,
                "error": str(e)
            }

    def discover_universal_measurement(self) -> Dict[str, Any]:
        """
        Discover universal measurement analytics.

        Returns:
            Dictionary with universal measurement stats
        """
        analytics_file = self.data_path / "universal_measurement" / "analytics.json"

        if not analytics_file.exists():
            return {
                "available": False,
                "system": "Universal Measurement",
                "type": "Universal Analytics"
            }

        try:
            with open(analytics_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            return {
                "available": True,
                "system": "Universal Measurement",
                "type": "Universal Analytics",
                "analytics_id": data.get("analytics_id"),
                "timestamp": data.get("timestamp"),
                "total_measurements": data.get("total_measurements", 0),
                "total_metrics": data.get("total_metrics", 0),
                "systems_measured": data.get("systems_measured", []),
                "principle": data.get("lumina_principle"),
                "raw_data": data
            }
        except Exception as e:
            logger.error(f"Failed to read universal measurement: {e}", exc_info=True)
            return {
                "available": False,
                "error": str(e)
            }

    def discover_lumina_metrics(self) -> Dict[str, Any]:
        """
        Discover Lumina metrics analytics.

        Returns:
            Dictionary with Lumina metrics stats
        """
        metrics_dir = self.data_path / "lumina_metrics" / "analytics"

        if not metrics_dir.exists():
            return {
                "available": False,
                "system": "Lumina Metrics Analytics",
                "type": "Metrics Analytics"
            }

        try:
            report_files = list(metrics_dir.glob("analytics_report_*.json"))

            if not report_files:
                return {
                    "available": False,
                    "system": "Lumina Metrics Analytics",
                    "type": "Metrics Analytics"
                }

            # Get most recent report
            latest_report = max(report_files, key=lambda p: p.stat().st_mtime)

            with open(latest_report, "r", encoding="utf-8") as f:
                data = json.load(f)

            return {
                "available": True,
                "system": "Lumina Metrics Analytics",
                "type": "Metrics Analytics",
                "report_count": len(report_files),
                "latest_report": latest_report.name,
                "latest_report_data": data,
                "raw_data": data
            }
        except Exception as e:
            logger.error(f"Failed to read Lumina metrics: {e}", exc_info=True)
            return {
                "available": False,
                "error": str(e)
            }

    def discover_all(self) -> Dict[str, Any]:
        """
        Discover all tracking systems.

        Returns:
            Comprehensive discovery dictionary
        """
        discovery = {
            "discovered_at": datetime.now().isoformat(),
            "project": "LUMINA",
            "systems": {}
        }

        logger.info("Discovering Git tracking...")
        discovery["systems"]["git"] = self.discover_git_tracking()

        logger.info("Discovering request tracking...")
        discovery["systems"]["request_tracking"] = self.discover_request_tracking()

        logger.info("Discovering universal measurement...")
        discovery["systems"]["universal_measurement"] = self.discover_universal_measurement()

        logger.info("Discovering Lumina metrics...")
        discovery["systems"]["lumina_metrics"] = self.discover_lumina_metrics()

        # Generate summary
        discovery["summary"] = {
            "total_systems": len(discovery["systems"]),
            "available_systems": sum(
                1 for s in discovery["systems"].values()
                if s.get("available", False)
            ),
            "system_types": list(set(
                s.get("type", "Unknown")
                for s in discovery["systems"].values()
            ))
        }

        return discovery

    def print_discovery(self, discovery: Dict[str, Any]):
        """Print formatted discovery results."""
        print("\n" + "=" * 80)
        print("DEVELOPMENT TRACKING SYSTEMS DISCOVERY - LUMINA")
        print("=" * 80)
        print(f"Discovered: {discovery['discovered_at']}")
        print()

        summary = discovery["summary"]
        print(f"Total Systems Found: {summary['total_systems']}")
        print(f"Available Systems: {summary['available_systems']}")
        print(f"System Types: {', '.join(summary['system_types'])}")
        print()

        systems = discovery["systems"]

        # Git
        print("-" * 80)
        print("1. GIT - Version Control Tracking")
        print("-" * 80)
        git = systems.get("git", {})
        if git.get("available", False):
            print(f"   Status: ✅ Available")
            print(f"   Total Commits: {git.get('total_commits', 0):,}")
            print(f"   Commits (Last Year): {git.get('commits_last_year', 0):,}")
            print(f"   Commits (Last 30 Days): {git.get('commits_last_30_days', 0):,}")
            print(f"   Commits (Last 7 Days): {git.get('commits_last_7_days', 0):,}")
            print(f"   Tracked Files: {git.get('tracked_files', 0):,}")
            if git.get("first_commit_date"):
                print(f"   First Commit: {git.get('first_commit_date')}")
            if git.get("last_commit_date"):
                print(f"   Last Commit: {git.get('last_commit_date')}")
            if git.get("contributors"):
                print(f"   Contributors: {len(git.get('contributors', []))}")
                for contrib in git.get("contributors", [])[:3]:
                    print(f"     - {contrib['name']}: {contrib['commits']} commits")
        else:
            print(f"   Status: ❌ Not available")
            if git.get("error"):
                print(f"   Error: {git.get('error')}")
        print()

        # Request Tracking
        print("-" * 80)
        print("2. REQUEST TRACKING ANALYTICS")
        print("-" * 80)
        req_track = systems.get("request_tracking", {})
        if req_track.get("available", False):
            print(f"   Status: ✅ Available")
            print(f"   Total Requests: {req_track.get('total_requests', 0):,}")
            print(f"   Generated: {req_track.get('generated_at', 'Unknown')}")
            by_status = req_track.get("by_status", {})
            if by_status:
                print(f"   By Status:")
                for status, count in by_status.items():
                    print(f"     - {status}: {count}")
        else:
            print(f"   Status: ❌ Not available")
        print()

        # Universal Measurement
        print("-" * 80)
        print("3. UNIVERSAL MEASUREMENT")
        print("-" * 80)
        univ = systems.get("universal_measurement", {})
        if univ.get("available", False):
            print(f"   Status: ✅ Available")
            print(f"   Total Measurements: {univ.get('total_measurements', 0):,}")
            print(f"   Total Metrics: {univ.get('total_metrics', 0):,}")
            print(f"   Systems Measured: {len(univ.get('systems_measured', []))}")
            print(f"   Principle: {univ.get('principle', 'Unknown')}")
        else:
            print(f"   Status: ❌ Not available")
        print()

        # Lumina Metrics
        print("-" * 80)
        print("4. LUMINA METRICS ANALYTICS")
        print("-" * 80)
        lumina = systems.get("lumina_metrics", {})
        if lumina.get("available", False):
            print(f"   Status: ✅ Available")
            print(f"   Report Count: {lumina.get('report_count', 0)}")
            print(f"   Latest Report: {lumina.get('latest_report', 'Unknown')}")
        else:
            print(f"   Status: ❌ Not available")
        print()

        print("=" * 80)
        print()


def main():
    try:
        """Main function to discover all tracking systems."""
        script_path = Path(__file__).resolve()
        project_root = script_path.parent.parent.parent

        print("🔍 Discovering all development tracking systems...")
        print()

        discovery_tool = TrackingSystemDiscovery(project_root)
        discovery = discovery_tool.discover_all()

        discovery_tool.print_discovery(discovery)

        # Save discovery
        output_path = project_root / "data" / "time_tracking" / f"discovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(discovery, f, indent=2, ensure_ascii=False)

        print(f"💾 Discovery saved to: {output_path}")
        print()

        return discovery


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()