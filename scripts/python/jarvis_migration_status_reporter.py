#!/usr/bin/env python3
"""
JARVIS Migration Status Reporter

Provides ETA calculations and scheduled status updates for NAS migration.
Can send updates hourly or every 2-3 hours as requested.

Tags: #MIGRATION #STATUS #ETA #JARVIS #NOTIFICATIONS @LUMINA
"""

import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISMigrationReporter")


class JARVISMigrationStatusReporter:
    """JARVIS status reporter for migration progress and ETA"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "disk_migration"
        self.state_file = self.data_dir / "migration_state.json"
        self.log_file = self.data_dir / "migration_log.jsonl"
        self.operation_status_file = self.data_dir / "operation_status.json"

    def get_current_status(self) -> Dict[str, Any]:
        """Get current migration status with ETA"""
        try:
            import psutil
            usage = psutil.disk_usage("C:")
            total_gb = usage.total / (1024 ** 3)
            used_gb = usage.used / (1024 ** 3)
            free_gb = usage.free / (1024 ** 3)
            percent_used = (used_gb / total_gb) * 100
        except Exception as e:
            logger.error(f"Error getting disk status: {e}")
            return {"error": str(e)}

        # Load migration state
        state = {}
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
            except Exception as e:
                logger.debug(f"Could not load state: {e}")

        # Load operation status
        operation_status = {}
        if self.operation_status_file.exists():
            try:
                with open(self.operation_status_file, 'r', encoding='utf-8') as f:
                    operation_status = json.load(f)
            except Exception:
                pass

        # Calculate progress
        target_percent = 50.0
        target_used_gb = total_gb * (target_percent / 100)
        space_to_free_gb = max(0, used_gb - target_used_gb)
        total_migrated_gb = state.get("total_migrated_gb", 0.0)
        remaining_gb = max(0, space_to_free_gb - total_migrated_gb)

        if space_to_free_gb > 0:
            progress_percent = min(100, (total_migrated_gb / space_to_free_gb) * 100)
        else:
            progress_percent = 100.0

        # Calculate ETA
        eta_info = self._calculate_eta(total_migrated_gb, remaining_gb, state)

        # Get recent migration activity
        recent_activity = self._get_recent_activity()

        return {
            "timestamp": datetime.now().isoformat(),
            "disk_status": {
                "total_gb": round(total_gb, 2),
                "used_gb": round(used_gb, 2),
                "free_gb": round(free_gb, 2),
                "percent_used": round(percent_used, 2),
                "target_percent": target_percent,
                "space_to_free_gb": round(space_to_free_gb, 2),
            },
            "migration_progress": {
                "total_migrated_gb": round(total_migrated_gb, 2),
                "remaining_gb": round(remaining_gb, 2),
                "progress_percent": round(progress_percent, 2),
                "migrations_count": state.get("migrations_count", 0),
                "last_migration": state.get("last_migration"),
            },
            "eta": eta_info,
            "current_operation": operation_status.get("status", "unknown"),
            "operation_message": operation_status.get("message", ""),
            "recent_activity": recent_activity,
        }

    def _calculate_eta(self, migrated_gb: float, remaining_gb: float, state: Dict) -> Dict[str, Any]:
        """Calculate ETA based on transfer rate"""
        if remaining_gb <= 0:
            return {
                "status": "complete",
                "estimated_completion": None,
                "estimated_hours": 0,
                "estimated_days": 0,
            }

        # Get transfer rate from recent migrations
        transfer_rate_gb_per_hour = self._calculate_transfer_rate(state)

        if transfer_rate_gb_per_hour <= 0:
            # No data yet, use conservative estimate
            # Network speed varies, but for large file transfers over 1Gbps:
            # Real-world: ~100-200 MB/s = ~360-720 GB/hour
            # Account for overhead, small files, network fluctuations: ~200-300 GB/hour
            # Use 250 GB/hour as conservative estimate
            transfer_rate_gb_per_hour = 250.0
            estimated_hours = remaining_gb / transfer_rate_gb_per_hour
            confidence = "low"
        elif transfer_rate_gb_per_hour > 1000:
            # Unrealistically high rate (likely from small sample or calculation error)
            # Cap at reasonable maximum and use conservative estimate
            transfer_rate_gb_per_hour = 500.0  # Max reasonable for 1Gbps network
            estimated_hours = remaining_gb / transfer_rate_gb_per_hour
            confidence = "low"
        else:
            estimated_hours = remaining_gb / transfer_rate_gb_per_hour
            confidence = "high" if state.get("migrations_count", 0) >= 3 else "medium"

        estimated_days = estimated_hours / 24
        estimated_completion = datetime.now() + timedelta(hours=estimated_hours)

        return {
            "status": "in_progress",
            "estimated_completion": estimated_completion.isoformat(),
            "estimated_hours": round(estimated_hours, 2),
            "estimated_days": round(estimated_days, 2),
            "transfer_rate_gb_per_hour": round(transfer_rate_gb_per_hour, 2),
            "confidence": confidence,
        }

    def _calculate_transfer_rate(self, state: Dict) -> float:
        """Calculate transfer rate from migration log"""
        if not self.log_file.exists():
            return 0.0

        try:
            successful_migrations = []
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        if entry.get("success") and entry.get("space_freed_gb", 0) > 0:
                            timestamp_str = entry.get("timestamp")
                            if timestamp_str:
                                timestamp = datetime.fromisoformat(timestamp_str)
                                successful_migrations.append({
                                    "timestamp": timestamp,
                                    "gb": entry.get("space_freed_gb", 0),
                                })
                    except (json.JSONDecodeError, ValueError):
                        continue

            if len(successful_migrations) < 2:
                return 0.0

            # Sort by timestamp
            successful_migrations.sort(key=lambda x: x["timestamp"])

            # Calculate rate from most recent migrations
            recent = successful_migrations[-10:]  # Last 10 successful migrations
            if len(recent) < 2:
                return 0.0

            total_gb = sum(m["gb"] for m in recent)
            time_span = (recent[-1]["timestamp"] - recent[0]["timestamp"]).total_seconds() / 3600

            if time_span <= 0:
                return 0.0

            return total_gb / time_span

        except Exception as e:
            logger.debug(f"Error calculating transfer rate: {e}")
            return 0.0

    def _get_recent_activity(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent migration activity"""
        if not self.log_file.exists():
            return []

        activities = []
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    try:
                        entry = json.loads(line.strip())
                        if entry.get("success"):
                            activities.append({
                                "item": entry.get("item", {}).get("source_path", "unknown"),
                                "size_gb": entry.get("space_freed_gb", 0),
                                "timestamp": entry.get("timestamp"),
                            })
                    except (json.JSONDecodeError, ValueError):
                        continue
        except Exception:
            pass

        return activities

    def generate_status_report(self) -> str:
        try:
            """Generate human-readable status report"""
            status = self.get_current_status()

            if "error" in status:
                return f"❌ Error getting status: {status['error']}"

            disk = status["disk_status"]
            progress = status["migration_progress"]
            eta = status["eta"]

            report = []
            report.append("=" * 80)
            report.append("📊 JARVIS MIGRATION STATUS REPORT")
            report.append("=" * 80)
            report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append("")

            # Disk Status
            report.append("💾 DISK STATUS (C:):")
            report.append(f"   Used: {disk['used_gb']:.2f} GB ({disk['percent_used']:.1f}%)")
            report.append(f"   Free: {disk['free_gb']:.2f} GB ({100 - disk['percent_used']:.1f}%)")
            report.append(f"   Target: {disk['target_percent']}% usage")
            report.append(f"   Space to Free: {disk['space_to_free_gb']:.2f} GB")
            report.append("")

            # Migration Progress
            report.append("🚀 MIGRATION PROGRESS:")
            report.append(f"   Migrated: {progress['total_migrated_gb']:.2f} GB")
            report.append(f"   Remaining: {progress['remaining_gb']:.2f} GB")
            report.append(f"   Progress: {progress['progress_percent']:.1f}%")
            report.append(f"   Migrations Completed: {progress['migrations_count']}")
            if progress.get("last_migration"):
                report.append(f"   Last Migration: {progress['last_migration']}")
            report.append("")

            # ETA
            report.append("⏱️  ESTIMATED TIME TO COMPLETION:")
            if eta["status"] == "complete":
                report.append("   ✅ Migration Complete!")
            else:
                report.append(f"   Estimated Hours: {eta['estimated_hours']:.1f} hours")
                report.append(f"   Estimated Days: {eta['estimated_days']:.2f} days")
                if eta.get("estimated_completion"):
                    completion_time = datetime.fromisoformat(eta["estimated_completion"])
                    report.append(f"   Estimated Completion: {completion_time.strftime('%Y-%m-%d %H:%M:%S')}")
                report.append(f"   Transfer Rate: {eta['transfer_rate_gb_per_hour']:.2f} GB/hour")
                report.append(f"   Confidence: {eta['confidence'].upper()}")
            report.append("")

            # Current Operation
            if status.get("current_operation") != "unknown":
                report.append(f"🔄 CURRENT OPERATION: {status['current_operation'].upper()}")
                if status.get("operation_message"):
                    report.append(f"   {status['operation_message']}")
                report.append("")

            # Recent Activity
            if status.get("recent_activity"):
                report.append("📁 RECENT ACTIVITY:")
                for activity in status["recent_activity"][:3]:
                    item_name = Path(activity["item"]).name if activity.get("item") else "unknown"
                    report.append(f"   ✅ {item_name}: {activity['size_gb']:.2f} GB")
                report.append("")

            report.append("=" * 80)

            return "\n".join(report)

        except Exception as e:
            self.logger.error(f"Error in generate_status_report: {e}", exc_info=True)
            raise
    def print_status_report(self):
        """Print status report to console"""
        report = self.generate_status_report()
        print(report)
        logger.info("Status report generated")


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Migration Status Reporter")
        parser.add_argument("--report", action="store_true", help="Generate and print status report")
        parser.add_argument("--json", action="store_true", help="Output as JSON")
        parser.add_argument("--eta-only", action="store_true", help="Show only ETA information")

        args = parser.parse_args()

        reporter = JARVISMigrationStatusReporter(project_root)

        if args.json:
            status = reporter.get_current_status()
            print(json.dumps(status, indent=2))
        elif args.eta_only:
            status = reporter.get_current_status()
            eta = status.get("eta", {})
            if eta.get("status") == "complete":
                print("✅ Migration Complete!")
            else:
                print(f"⏱️  ETA: {eta.get('estimated_hours', 0):.1f} hours ({eta.get('estimated_days', 0):.2f} days)")
                if eta.get("estimated_completion"):
                    completion = datetime.fromisoformat(eta["estimated_completion"])
                    print(f"   Completion: {completion.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            reporter.print_status_report()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":

    main()