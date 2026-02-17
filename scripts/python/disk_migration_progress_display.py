#!/usr/bin/env python3
"""
Disk Migration Progress Display - Visual Progress Bar

Shows visual progress bar with:
- Migration progress percentage
- Estimated time to complete
- Details on which directories/files have been migrated
- Real-time updates

Tags: #PROGRESS-BAR #VISUALIZATION #MIGRATION @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import os

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("MigrationProgress")


class MigrationProgressDisplay:
    """
    Visual progress bar for disk migration

    Shows:
    - Progress bar with percentage
    - Estimated time to complete
    - Migrated directories/files
    - Current operation
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "disk_migration"
        self.state_file = self.data_dir / "migration_state.json"
        self.log_file = self.data_dir / "migration_log.jsonl"
        self.resume_state_file = self.data_dir / "resume_state.json"

    def get_migration_progress(self) -> Dict[str, Any]:
        """Get current migration progress"""
        # Load state
        state = {}
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
            except:
                pass

        # Get disk status
        try:
            import psutil
            usage = psutil.disk_usage("C:")
            total_gb = usage.total / (1024 ** 3)
            used_gb = usage.used / (1024 ** 3)
            percent_used = (used_gb / total_gb) * 100
            target_percent = 50.0
            space_to_free_gb = max(0, used_gb - (total_gb * target_percent / 100))
        except:
            return {"error": "Could not get disk status"}

        # Calculate progress
        total_migrated_gb = state.get("total_migrated_gb", 0.0)
        if space_to_free_gb > 0:
            progress_percent = min(100, (total_migrated_gb / space_to_free_gb) * 100)
        else:
            progress_percent = 100.0

        # Get migrated items from log
        migrated_items = self._get_migrated_items()

        # Calculate time estimate
        time_estimate = self._calculate_time_estimate(total_migrated_gb, space_to_free_gb, state)

        return {
            "progress_percent": round(progress_percent, 2),
            "total_migrated_gb": round(total_migrated_gb, 2),
            "space_to_free_gb": round(space_to_free_gb, 2),
            "remaining_gb": round(max(0, space_to_free_gb - total_migrated_gb), 2),
            "current_usage_percent": round(percent_used, 2),
            "target_percent": target_percent,
            "migrated_items": migrated_items,
            "time_estimate": time_estimate,
            "migrations_count": state.get("migrations_count", 0),
            "last_migration": state.get("last_migration"),
            "timestamp": datetime.now().isoformat()
        }

    def _get_migrated_items(self) -> List[Dict[str, Any]]:
        """Get list of migrated items from log with detailed info"""
        migrated = []
        if not self.log_file.exists():
            return migrated

        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            entry = json.loads(line)
                            if entry.get("success"):
                                item = entry.get("item", {})
                                details = entry.get("migration_details", {})

                                migrated.append({
                                    "source": item.get("source_path", details.get("source_directory", "unknown")),
                                    "target": item.get("target_path", details.get("target_directory", "unknown")),
                                    "size_gb": item.get("size_gb", 0),
                                    "file_count": item.get("file_count", details.get("file_count", 0)),
                                    "directory_name": details.get("directory_name", Path(item.get("source_path", "")).name),
                                    "migration_type": details.get("migration_type", item.get("migration_type", "move")),
                                    "timestamp": entry.get("timestamp", "unknown"),
                                    "status": "✅ Migrated"
                                })
                        except Exception as e:
                            logger.debug(f"Error parsing log entry: {e}")
                            continue
        except Exception as e:
            logger.error(f"Error reading migration log: {e}")

        # Return most recent first
        return list(reversed(migrated[-30:]))  # Last 30 items for better history

    def _calculate_time_estimate(self, migrated_gb: float, remaining_gb: float, state: Dict) -> Dict[str, Any]:
        """Calculate estimated time to complete"""
        if remaining_gb <= 0:
            return {
                "status": "complete",
                "estimated_seconds": 0,
                "estimated_formatted": "Complete!"
            }

        # Calculate average speed from recent migrations
        migrations_count = state.get("migrations_count", 0)
        last_migration = state.get("last_migration")

        if migrations_count > 0 and last_migration:
            try:
                last_time = datetime.fromisoformat(last_migration)
                elapsed = (datetime.now() - last_time).total_seconds()
                # Estimate based on recent rate (rough estimate)
                if elapsed > 0 and migrated_gb > 0:
                    rate_gb_per_hour = (migrated_gb / elapsed) * 3600
                    if rate_gb_per_hour > 0:
                        estimated_seconds = (remaining_gb / rate_gb_per_hour) * 3600
                        estimated_timedelta = timedelta(seconds=int(estimated_seconds))

                        # Format time
                        hours = int(estimated_seconds // 3600)
                        minutes = int((estimated_seconds % 3600) // 60)

                        if hours > 0:
                            formatted = f"{hours}h {minutes}m"
                        else:
                            formatted = f"{minutes}m"

                        return {
                            "status": "in_progress",
                            "estimated_seconds": int(estimated_seconds),
                            "estimated_formatted": formatted,
                            "rate_gb_per_hour": round(rate_gb_per_hour, 2)
                        }
            except:
                pass

        # Default estimate (conservative)
        estimated_hours = remaining_gb / 10.0  # Assume ~10 GB/hour
        hours = int(estimated_hours)
        minutes = int((estimated_hours - hours) * 60)

        return {
            "status": "estimating",
            "estimated_seconds": int(estimated_hours * 3600),
            "estimated_formatted": f"{hours}h {minutes}m (estimate)",
            "rate_gb_per_hour": 10.0
        }

    def display_progress_bar(self, width: int = 60):
        """Display visual progress bar"""
        progress = self.get_migration_progress()

        if "error" in progress:
            print(f"❌ Error: {progress['error']}")
            return

        # Clear screen (optional)
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
        except:
            pass  # Ignore clear errors

        print("=" * 80)
        print("📊 DISK MIGRATION PROGRESS - Visual Progress Bar")
        print("=" * 80)
        print()

        # Show current operation status for transparency
        operation_status_file = self.data_dir / "operation_status.json"
        if operation_status_file.exists():
            try:
                with open(operation_status_file, 'r', encoding='utf-8') as f:
                    op_status = json.load(f)
                    status = op_status.get("status", "unknown")
                    message = op_status.get("message", "")

                    status_emoji = {
                        "initializing": "🔄",
                        "checking_disk": "🔍",
                        "scanning": "🔎",
                        "migrating": "📦",
                        "no_candidates": "⏸️",
                        "error": "❌",
                        "idle": "⏸️"
                    }.get(status, "⚪")

                    print(f"**Current Operation:** {status_emoji} {message}")
                    print()
            except:
                pass

        # Overall progress
        progress_percent = progress["progress_percent"]
        remaining_gb = progress["remaining_gb"]
        total_migrated = progress["total_migrated_gb"]
        space_to_free = progress["space_to_free_gb"]

        # Progress bar
        filled = int(width * progress_percent / 100)
        bar = "█" * filled + "░" * (width - filled)

        print(f"Overall Progress: {progress_percent:.1f}%")
        print(f"[{bar}]")
        print()

        # Statistics
        print("📈 Statistics:")
        print(f"   Migrated: {total_migrated:.2f} GB")
        print(f"   Remaining: {remaining_gb:.2f} GB")
        print(f"   Total to Free: {space_to_free:.2f} GB")
        print(f"   Migrations Completed: {progress['migrations_count']}")
        print()

        # Current disk status
        current_usage = progress["current_usage_percent"]
        target_usage = progress["target_percent"]
        usage_filled = int(width * current_usage / 100)
        usage_bar = "█" * usage_filled + "░" * (width - usage_filled)

        print(f"Current Disk Usage: {current_usage:.1f}% (Target: {target_usage}%)")
        print(f"[{usage_bar}]")
        print()

        # Time estimate
        time_est = progress["time_estimate"]
        print("⏱️  Time Estimate:")
        print(f"   Estimated Time Remaining: {time_est['estimated_formatted']}")
        if "rate_gb_per_hour" in time_est:
            print(f"   Migration Rate: {time_est['rate_gb_per_hour']:.2f} GB/hour")
        print()

        # Migrated items with detailed info
        migrated_items = progress["migrated_items"]
        if migrated_items:
            print("📁 Recently Migrated Directories/Files:")
            print()
            print(f"{'Directory/File':<45} {'Size':>12} {'Files':>10} {'Time':>10} {'Status':<15}")
            print("-" * 95)

            for item in migrated_items[:15]:  # Show last 15
                source = Path(item.get("source", "")).name
                if not source:
                    source = item.get("source", "unknown")[:44]
                size = item.get("size_gb", 0)

                # Get file count if available
                file_count = item.get("file_count", 0)
                file_count_str = f"{file_count:,}" if file_count > 0 else "N/A"

                timestamp = item.get("timestamp", "unknown")
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_str = dt.strftime("%H:%M:%S")
                except:
                    time_str = timestamp[:8] if len(timestamp) > 8 else timestamp[:8]

                status = item.get("status", "✅ Migrated")

                print(f"{source[:44]:<45} {size:>11.2f} GB {file_count_str:>10} {time_str:>10} {status:<15}")

            if len(migrated_items) > 15:
                print(f"   ... and {len(migrated_items) - 15} more items")
            print()

        # Last update
        if progress.get("last_migration"):
            try:
                last_dt = datetime.fromisoformat(progress["last_migration"].replace('Z', '+00:00'))
                last_str = last_dt.strftime("%Y-%m-%d %H:%M:%S")
                print(f"Last Migration: {last_str}")
            except:
                print(f"Last Migration: {progress.get('last_migration', 'unknown')}")

        print()
        # Show what's actually happening - TRANSPARENCY
        print("=" * 80)
        print("**🔍 CURRENT OPERATION STATUS - TRANSPARENCY:**")
        print()

        # Check if migration is actually running
        try:
            from background_disk_space_migration import BackgroundDiskSpaceMigration
            temp_mgr = BackgroundDiskSpaceMigration(self.project_root)
            mgr_status = temp_mgr.get_status()
            is_running = mgr_status.get("running", False)

            if not is_running:
                print("   ⚠️  **MIGRATION IS NOT RUNNING**")
                print("   💡 Start migration with: python background_disk_space_migration.py --start")
                print()
            else:
                print("   ✅ Migration is RUNNING")
                print()
        except:
            pass

        # Check operation status file
        operation_status_file = self.data_dir / "operation_status.json"
        if operation_status_file.exists():
            try:
                with open(operation_status_file, 'r', encoding='utf-8') as f:
                    op_status = json.load(f)
                    status = op_status.get("status", "unknown")
                    message = op_status.get("message", "No status available")
                    timestamp = op_status.get("timestamp", "")

                    status_display = {
                        "initializing": ("🔄", "Initializing migration system..."),
                        "checking_disk": ("🔍", "Checking disk space status..."),
                        "scanning": ("🔎", "Scanning directories for candidates (this can take time)..."),
                        "migrating": ("📦", "Migrating files..."),
                        "no_candidates": ("⏸️", "No migration candidates found"),
                        "error": ("❌", "Error occurred"),
                        "idle": ("⏸️", "Waiting for next check cycle"),
                        "waiting": ("⏳", "Waiting for next check cycle")
                    }.get(status, ("⚪", message))

                    emoji, desc = status_display
                    print(f"   {emoji} **{desc}**")

                    if timestamp:
                        try:
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            time_str = dt.strftime("%H:%M:%S")
                            print(f"   Last update: {time_str}")
                        except:
                            pass

                    # Add helpful context
                    if status == "scanning":
                        print("   ⏱️  Scanning can take several minutes for large directories")
                        print("   💡 This is normal - the system is evaluating what to migrate")
                    elif status == "checking_disk":
                        print("   ⏱️  Checking disk space...")
            except Exception as e:
                print(f"   ⚠️  Could not read operation status: {e}")
        else:
            print("   ⏳ Status: Not initialized or migration not started")
            print("   💡 Start migration to see operation status")

        print()
        print("=" * 80)
        print("💡 Press Ctrl+C to exit. Progress updates automatically.")
        print("   (Migration continues in background even if you exit)")
        print("=" * 80)

    def display_live_progress(self, update_interval: int = 5):
        """Display live updating progress bar - VISIBLE TO OPERATOR"""
        import signal
        import sys

        # Set up signal handler for clean exit
        def signal_handler(sig, frame):
            print("\n\n👋 Progress display stopped (Ctrl+C received).")
            print("💡 Migration continues in background. Use --status to check.")
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        try:
            iteration = 0
            while True:
                # Clear screen for better visibility (optional)
                if iteration > 0:  # Don't clear on first display
                    try:
                        os.system('cls' if os.name == 'nt' else 'clear')
                    except:
                        pass  # Ignore clear errors

                self.display_progress_bar()
                iteration += 1

                # Use interruptible sleep
                try:
                    time.sleep(update_interval)
                except KeyboardInterrupt:
                    raise
        except KeyboardInterrupt:
            print("\n\n👋 Progress display stopped.")
            print("💡 Migration continues in background. Use --status to check.")
            sys.exit(0)
        except Exception as e:
            print(f"\n\n❌ Error in progress display: {e}")
            sys.exit(1)


def main():
    try:
        """Main function"""
        import argparse

        parser = argparse.ArgumentParser(description="Disk Migration Progress Display")
        parser.add_argument("--live", action="store_true", help="Show live updating progress")
        parser.add_argument("--interval", type=int, default=5, help="Update interval in seconds (default: 5)")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        display = MigrationProgressDisplay()

        if args.json:
            progress = display.get_migration_progress()
            print(json.dumps(progress, indent=2))
        elif args.live:
            display.display_live_progress(update_interval=args.interval)
        else:
            display.display_progress_bar()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()