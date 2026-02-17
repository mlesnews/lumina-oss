"""
PUBLIC: Time Tracking Systems Comparison
Location: scripts/python/time_tracking_comparison.py
License: MIT

Compares statistics across all time tracking systems:
- WakaTime (coding time)
- Cursor IDE (session/usage tracking)
- AI Token Request Tracker (AI interaction time)
- Other tracking systems
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from collections import defaultdict

# Try to import WakaTime integration
try:
    from wakatime_integration import WakaTimeAPI
    WAKATIME_AVAILABLE = True
except ImportError:
    WAKATIME_AVAILABLE = False
    logging.warning("WakaTime integration not available")


# Initialize logger
logger = logging.getLogger(__name__)


class TimeTrackingComparison:
    """Compare statistics across all time tracking systems."""

    def __init__(self, project_root: Path):
        """
        Initialize time tracking comparison.

        Args:
            project_root: Path to project root
        """
        self.project_root = project_root
        self.config_path = project_root / "config"
        self.data_path = project_root / "data"
        self.cursor_path = project_root / ".cursor"

    def get_wakatime_stats(
        self,
        api_key: Optional[str] = None,
        range_type: str = "all_time"
    ) -> Dict[str, Any]:
        """
        Get WakaTime statistics.

        Args:
            api_key: WakaTime API key (optional, from env if not provided)
            range_type: Time range (last_7_days, last_30_days, last_year, all_time)

        Returns:
            Dictionary with WakaTime statistics
        """
        if not WAKATIME_AVAILABLE:
            return {
                "available": False,
                "error": "WakaTime integration not available"
            }

        if not api_key:
            api_key = os.getenv("WAKATIME_API_KEY")

        if not api_key:
            return {
                "available": False,
                "error": "WakaTime API key not found. Set WAKATIME_API_KEY environment variable."
            }

        try:
            client = WakaTimeAPI(api_key)
            stats = client.get_stats(range_type)

            data = stats.get("data", {})
            total_seconds = data.get("total_seconds", 0)

            return {
                "available": True,
                "system": "WakaTime",
                "range": range_type,
                "total_seconds": total_seconds,
                "total_hours": round(total_seconds / 3600, 2),
                "total_days": round(total_seconds / 86400, 2),
                "languages": data.get("languages", [])[:10],  # Top 10
                "projects": data.get("projects", [])[:10],  # Top 10
                "editors": data.get("editors", [])[:5],  # Top 5
                "operating_systems": data.get("operating_systems", [])[:5],  # Top 5
                "best_day": data.get("best_day", {}),
                "daily_average": data.get("daily_average", 0) / 3600 if data.get("daily_average") else 0,
                "raw_data": stats
            }
        except Exception as e:
            logger.error(f"Failed to fetch WakaTime stats: {e}", exc_info=True)
            return {
                "available": False,
                "error": str(e)
            }

    def get_cursor_stats(self) -> Dict[str, Any]:
        """
        Get Cursor IDE usage statistics.

        Note: Cursor may store usage data in various locations.
        This attempts to find and parse available data.
        Uses memory-efficient methods for large directories.

        Returns:
            Dictionary with Cursor statistics
        """
        stats = {
            "available": False,
            "system": "Cursor IDE",
            "data_sources": [],
            "resource_limits": {}
        }

        # Check for Cursor workspace data
        workspace_file = self.cursor_path / "workspace.json"
        if workspace_file.exists():
            try:
                with open(workspace_file, "r", encoding="utf-8") as f:
                    workspace_data = json.load(f)
                    stats["data_sources"].append("workspace.json")
                    stats["workspace_data"] = workspace_data
            except Exception as e:
                logger.warning(f"Failed to read workspace.json: {e}")

        # Check for session data (memory-efficient for large directories)
        try:
            session_files = list(self.data_path.glob("**/session*.json"))
            if session_files:
                stats["data_sources"].append(f"{len(session_files)} session files")
                stats["session_count"] = len(session_files)
        except MemoryError:
            logger.warning("Out of memory counting session files - using estimate")
            stats["session_count"] = "large"
            stats["resource_limits"]["session_count"] = "memory_limit"
        except Exception as e:
            logger.warning(f"Error counting session files: {e}")
            stats["resource_limits"]["session_count"] = str(e)

        # Check for agent chat sessions (chunked for large directories)
        agent_sessions = self.data_path / "agent_chat_sessions"
        if agent_sessions.exists():
            try:
                # Use iterator to avoid loading all into memory
                session_count = sum(1 for _ in agent_sessions.glob("*.json"))
                if session_count > 0:
                    stats["data_sources"].append(f"{session_count} agent chat sessions")
                    stats["agent_session_count"] = session_count
            except MemoryError:
                logger.warning("Out of memory counting agent sessions")
                stats["agent_session_count"] = "large"
                stats["resource_limits"]["agent_sessions"] = "memory_limit"
            except Exception as e:
                logger.warning(f"Error counting agent sessions: {e}")

        # Check for AI chat summaries (chunked)
        chat_summaries = self.data_path / "ai_chat_summaries"
        if chat_summaries.exists():
            try:
                summary_files = list(chat_summaries.glob("*.json"))
                if summary_files:
                    stats["data_sources"].append(f"{len(summary_files)} chat summaries")
                    stats["chat_summary_count"] = len(summary_files)
            except MemoryError:
                logger.warning("Out of memory counting chat summaries")
                stats["chat_summary_count"] = "large"
                stats["resource_limits"]["chat_summaries"] = "memory_limit"
            except Exception as e:
                logger.warning(f"Error counting chat summaries: {e}")

        if stats["data_sources"]:
            stats["available"] = True

        return stats

    def get_ai_token_tracker_stats(self) -> Dict[str, Any]:
        """
        Get AI Token Request Tracker statistics.

        Returns:
            Dictionary with AI token tracker statistics
        """
        tracker_file = self.config_path / "ai_token_request_tracker.json"

        if not tracker_file.exists():
            return {
                "available": False,
                "error": "AI Token Request Tracker config not found"
            }

        try:
            with open(tracker_file, "r", encoding="utf-8") as f:
                tracker_data = json.load(f)

            # Extract relevant statistics
            stats = {
                "available": True,
                "system": "AI Token Request Tracker",
                "version": tracker_data.get("version", "unknown"),
                "last_updated": tracker_data.get("last_updated", "unknown"),
                "lookback_windows": tracker_data.get("lookback_configuration", {}).get("lookback_windows", {}),
                "token_budgets": tracker_data.get("token_budgets", {}),
                "raw_data": tracker_data
            }

            # Calculate total token budgets
            total_daily = sum(
                budget.get("daily_limit", 0)
                for budget in tracker_data.get("token_budgets", {}).values()
            )
            total_monthly = sum(
                budget.get("monthly_limit", 0)
                for budget in tracker_data.get("token_budgets", {}).values()
            )

            stats["total_daily_budget"] = total_daily
            stats["total_monthly_budget"] = total_monthly

            return stats
        except Exception as e:
            logger.error(f"Failed to read AI token tracker: {e}", exc_info=True)
            return {
                "available": False,
                "error": str(e)
            }

    def get_gitlens_stats(self) -> Dict[str, Any]:
        """
        Get GitLens followup automation statistics.

        Returns:
            Dictionary with GitLens statistics
        """
        gitlens_file = self.data_path / "gitlens_followup_automation" / "followup_history.jsonl"

        if not gitlens_file.exists():
            return {
                "available": False,
                "error": "GitLens followup history not found"
            }

        try:
            # Count lines in JSONL file
            with open(gitlens_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            return {
                "available": True,
                "system": "GitLens Followup Automation",
                "followup_count": len(lines),
                "data_file": str(gitlens_file)
            }
        except Exception as e:
            logger.error(f"Failed to read GitLens stats: {e}", exc_info=True)
            return {
                "available": False,
                "error": str(e)
            }

    def compare_all_systems(
        self,
        wakatime_api_key: Optional[str] = None,
        wakatime_range: str = "all_time"
    ) -> Dict[str, Any]:
        """
        Compare statistics across all tracking systems.

        Args:
            wakatime_api_key: Optional WakaTime API key
            wakatime_range: WakaTime time range

        Returns:
            Comprehensive comparison dictionary
        """
        comparison = {
            "generated_at": datetime.now().isoformat(),
            "project": "LUMINA",
            "systems": {}
        }

        # Get WakaTime stats
        logger.info("Fetching WakaTime statistics...")
        comparison["systems"]["wakatime"] = self.get_wakatime_stats(
            wakatime_api_key,
            wakatime_range
        )

        # Get Cursor stats
        logger.info("Fetching Cursor IDE statistics...")
        comparison["systems"]["cursor"] = self.get_cursor_stats()

        # Get AI Token Tracker stats
        logger.info("Fetching AI Token Tracker statistics...")
        comparison["systems"]["ai_token_tracker"] = self.get_ai_token_tracker_stats()

        # Get GitLens stats
        logger.info("Fetching GitLens statistics...")
        comparison["systems"]["gitlens"] = self.get_gitlens_stats()

        # Get Git tracking stats (if discover script available)
        try:
            from discover_tracking_systems import TrackingSystemDiscovery
            logger.info("Discovering additional tracking systems...")
            discovery_tool = TrackingSystemDiscovery(self.project_root)
            git_stats = discovery_tool.discover_git_tracking()
            if git_stats.get("available", False):
                comparison["systems"]["git"] = git_stats
        except ImportError:
            logger.warning("discover_tracking_systems not available")
        except Exception as e:
            logger.warning(f"Could not discover additional systems: {e}")

        # Generate summary
        comparison["summary"] = self._generate_summary(comparison["systems"])

        return comparison

    def _generate_summary(self, systems: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate summary of all systems.

        Args:
            systems: Dictionary of system statistics

        Returns:
            Summary dictionary
        """
        summary = {
            "total_systems": len(systems),
            "available_systems": sum(1 for s in systems.values() if s.get("available", False)),
            "system_details": {}
        }

        # Extract key metrics
        for system_name, system_data in systems.items():
            if system_data.get("available", False):
                summary["system_details"][system_name] = {
                    "status": "available",
                    "key_metrics": self._extract_key_metrics(system_name, system_data)
                }
            else:
                summary["system_details"][system_name] = {
                    "status": "unavailable",
                    "error": system_data.get("error", "Unknown error")
                }

        return summary

    def _extract_key_metrics(self, system_name: str, system_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key metrics from system data.

        Args:
            system_name: Name of the system
            system_data: System statistics data

        Returns:
            Key metrics dictionary
        """
        metrics = {}

        if system_name == "wakatime":
            metrics["total_hours"] = system_data.get("total_hours", 0)
            metrics["total_days"] = system_data.get("total_days", 0)
            metrics["daily_average_hours"] = round(system_data.get("daily_average", 0), 2)
            metrics["top_languages"] = [
                lang.get("name", "Unknown")
                for lang in system_data.get("languages", [])[:5]
            ]
            metrics["top_projects"] = [
                proj.get("name", "Unknown")
                for proj in system_data.get("projects", [])[:5]
            ]

        elif system_name == "cursor":
            metrics["session_count"] = system_data.get("session_count", 0)
            metrics["agent_session_count"] = system_data.get("agent_session_count", 0)
            metrics["chat_summary_count"] = system_data.get("chat_summary_count", 0)
            metrics["data_sources"] = system_data.get("data_sources", [])

        elif system_name == "ai_token_tracker":
            metrics["total_daily_budget"] = system_data.get("total_daily_budget", 0)
            metrics["total_monthly_budget"] = system_data.get("total_monthly_budget", 0)
            metrics["token_budget_count"] = len(system_data.get("token_budgets", {}))

        elif system_name == "gitlens":
            metrics["followup_count"] = system_data.get("followup_count", 0)

        return metrics

    def save_comparison(self, comparison: Dict[str, Any], output_path: Optional[Path] = None) -> Path:
        try:
            """
            Save comparison to JSON file.

            Args:
                comparison: Comparison dictionary
                output_path: Optional output path

            Returns:
                Path to saved file
            """
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = self.data_path / "time_tracking" / f"comparison_{timestamp}.json"

            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(comparison, f, indent=2, ensure_ascii=False)

            logger.info(f"Comparison saved to {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Error in save_comparison: {e}", exc_info=True)
            raise
    def print_comparison(self, comparison: Dict[str, Any]):
        """
        Print formatted comparison to console.

        Args:
            comparison: Comparison dictionary
        """
        print("\n" + "=" * 80)
        print("TIME TRACKING SYSTEMS COMPARISON - LUMINA PROJECT")
        print("=" * 80)
        print(f"Generated: {comparison['generated_at']}")
        print()

        systems = comparison["systems"]
        summary = comparison["summary"]

        print(f"Total Systems: {summary['total_systems']}")
        print(f"Available Systems: {summary['available_systems']}")
        print()

        # WakaTime
        print("-" * 80)
        print("1. WAKATIME (Coding Time Tracking)")
        print("-" * 80)
        wakatime = systems.get("wakatime", {})
        if wakatime.get("available", False):
            print(f"   Status: ✅ Available")
            print(f"   Total Time: {wakatime.get('total_hours', 0):.2f} hours ({wakatime.get('total_days', 0):.2f} days)")
            print(f"   Daily Average: {wakatime.get('daily_average', 0):.2f} hours/day")
            print(f"   Time Range: {wakatime.get('range', 'unknown')}")

            languages = wakatime.get("languages", [])[:5]
            if languages:
                print(f"   Top Languages:")
                for lang in languages:
                    name = lang.get("name", "Unknown")
                    hours = lang.get("total_seconds", 0) / 3600
                    percent = lang.get("percent", 0)
                    print(f"     - {name}: {hours:.2f} hours ({percent:.1f}%)")
        else:
            print(f"   Status: ❌ Unavailable")
            print(f"   Error: {wakatime.get('error', 'Unknown error')}")
        print()

        # Cursor
        print("-" * 80)
        print("2. CURSOR IDE (Session Tracking)")
        print("-" * 80)
        cursor = systems.get("cursor", {})
        if cursor.get("available", False):
            print(f"   Status: ✅ Available")
            print(f"   Data Sources: {', '.join(cursor.get('data_sources', []))}")
            if cursor.get("session_count"):
                print(f"   Session Files: {cursor.get('session_count')}")
            if cursor.get("agent_session_count"):
                print(f"   Agent Chat Sessions: {cursor.get('agent_session_count')}")
            if cursor.get("chat_summary_count"):
                print(f"   Chat Summaries: {cursor.get('chat_summary_count')}")
        else:
            print(f"   Status: ⚠️  Limited Data")
            print(f"   Note: Cursor IDE may track usage internally, but data not accessible via API")
        print()

        # AI Token Tracker
        print("-" * 80)
        print("3. AI TOKEN REQUEST TRACKER")
        print("-" * 80)
        ai_tracker = systems.get("ai_token_tracker", {})
        if ai_tracker.get("available", False):
            print(f"   Status: ✅ Available")
            print(f"   Version: {ai_tracker.get('version', 'unknown')}")
            print(f"   Last Updated: {ai_tracker.get('last_updated', 'unknown')}")
            print(f"   Total Daily Budget: {ai_tracker.get('total_daily_budget', 0):,} tokens")
            print(f"   Total Monthly Budget: {ai_tracker.get('total_monthly_budget', 0):,} tokens")
            print(f"   Token Budgets Configured: {len(ai_tracker.get('token_budgets', {}))}")
        else:
            print(f"   Status: ❌ Unavailable")
            print(f"   Error: {ai_tracker.get('error', 'Unknown error')}")
        print()

        # GitLens
        print("-" * 80)
        print("4. GITLENS FOLLOWUP AUTOMATION")
        print("-" * 80)
        gitlens = systems.get("gitlens", {})
        if gitlens.get("available", False):
            print(f"   Status: ✅ Available")
            print(f"   Followup Count: {gitlens.get('followup_count', 0)}")
        else:
            print(f"   Status: ❌ Unavailable")
            print(f"   Error: {gitlens.get('error', 'Unknown error')}")
        print()

        # Git Tracking
        git = systems.get("git", {})
        if git.get("available", False):
            print("-" * 80)
            print("5. GIT - Version Control Tracking")
            print("-" * 80)
            print(f"   Status: ✅ Available")
            print(f"   Total Commits: {git.get('total_commits', 0):,}")
            print(f"   Commits (Last 30 Days): {git.get('commits_last_30_days', 0):,}")
            print(f"   Commits (Last 7 Days): {git.get('commits_last_7_days', 0):,}")
            print(f"   Tracked Files: {git.get('tracked_files', 0):,}")
            if git.get("contributors"):
                print(f"   Contributors: {len(git.get('contributors', []))}")
            print()

        print("=" * 80)
        print()

        # Recommendations
        print("RECOMMENDATIONS:")
        print("-" * 80)
        if not wakatime.get("available", False):
            print("  • Set up WAKATIME_API_KEY environment variable for coding time tracking")
        if not cursor.get("available", False):
            print("  • Cursor IDE usage data may be available in Cursor settings or logs")
        print("  • Consider integrating all systems for comprehensive time tracking")
        print()


def main():
    try:
        """Main function to run time tracking comparison."""
        import sys

        # Get project root
        script_path = Path(__file__).resolve()
        project_root = script_path.parent.parent.parent

        # Get WakaTime API key from environment
        wakatime_api_key = os.getenv("WAKATIME_API_KEY")

        # Parse arguments
        wakatime_range = "all_time"
        save_output = True

        if len(sys.argv) > 1:
            wakatime_range = sys.argv[1]
        if len(sys.argv) > 2 and sys.argv[2].lower() == "no-save":
            save_output = False

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # Create comparison instance
        comparison_tool = TimeTrackingComparison(project_root)

        # Run comparison
        print("🔄 Comparing time tracking systems...")
        comparison = comparison_tool.compare_all_systems(
            wakatime_api_key=wakatime_api_key,
            wakatime_range=wakatime_range
        )

        # Print results
        comparison_tool.print_comparison(comparison)

        # Save if requested
        if save_output:
            output_path = comparison_tool.save_comparison(comparison)
            print(f"💾 Comparison saved to: {output_path}")

        return comparison


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()