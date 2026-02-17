#!/usr/bin/env python3
"""
IMVA NAS Migration Status Monitor

Provides periodic status updates to IMVA regarding NAS migration progress.
Integrates with IMVA display system to show real-time migration status.

Tags: #IMVA #NAS #MIGRATION #STATUS #MONITORING @JARVIS @LUMINA
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import threading

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from nas_migration_status import NASMigrationStatus
    from lumina_logger import get_logger
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

logger = get_logger("IMVANASMigrationMonitor")


class IMVANASMigrationMonitor:
    """
    IMVA NAS Migration Status Monitor

    Provides periodic status updates to IMVA display system.
    """

    def __init__(self, project_root: Path, update_interval: int = 30):
        """
        Initialize IMVA NAS Migration Monitor.

        Args:
            project_root: Path to project root
            update_interval: Update interval in seconds (default: 30)
        """
        self.project_root = project_root
        self.update_interval = update_interval
        self.status_checker = NASMigrationStatus(project_root)
        self.running = False
        self.monitor_thread = None

        # IMVA integration paths
        self.imva_status_file = project_root / "data" / "imva" / "nas_migration_status.json"
        self.imva_status_file.parent.mkdir(parents=True, exist_ok=True)

        logger.info("✅ IMVA NAS Migration Monitor initialized")
        logger.info(f"   Update interval: {update_interval} seconds")
        logger.info(f"   Status file: {self.imva_status_file}")

    def get_migration_status(self) -> Dict[str, Any]:
        """
        Get current migration status.

        Returns:
            Migration status dictionary
        """
        try:
            status = self.status_checker.get_comprehensive_status()

            # Extract key metrics for IMVA display
            nas_access = status.get("nas_accessibility", {})
            vault_creds = status.get("azure_vault_credentials", {})
            doit_exec = status.get("doit_execution", {})

            # Check for migration progress files
            migration_progress = self._check_migration_progress()

            return {
                "timestamp": datetime.now().isoformat(),
                "nas_accessible": nas_access.get("accessible", False),
                "credentials_available": vault_creds.get("available", False),
                "migration_status": migration_progress.get("status", "unknown"),
                "files_migrated": migration_progress.get("files_migrated", 0),
                "total_files": migration_progress.get("total_files", 0),
                "size_migrated_gb": migration_progress.get("size_migrated_gb", 0.0),
                "total_size_gb": migration_progress.get("total_size_gb", 0.0),
                "progress_percent": migration_progress.get("progress_percent", 0.0),
                "estimated_time_remaining": migration_progress.get("estimated_time_remaining", "calculating..."),
                "current_speed_mbps": migration_progress.get("current_speed_mbps", 0.0),
                "status_message": self._generate_status_message(status, migration_progress),
                "ready_to_migrate": nas_access.get("accessible", False) and vault_creds.get("available", False),
                "migration_in_progress": migration_progress.get("status") == "in_progress"
            }
        except Exception as e:
            logger.error(f"Error getting migration status: {e}", exc_info=True)
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status_message": f"Error checking migration status: {e}"
            }

    def _check_migration_progress(self) -> Dict[str, Any]:
        """
        Check actual migration progress from logs/files.

        Returns:
            Migration progress dictionary
        """
        progress = {
            "status": "unknown",
            "files_migrated": 0,
            "total_files": 0,
            "size_migrated_gb": 0.0,
            "total_size_gb": 3.73,  # From migration plan
            "progress_percent": 0.0,
            "estimated_time_remaining": "calculating...",
            "current_speed_mbps": 0.0
        }

        try:
            # Check migration tracker status
            tracker_file = self.project_root / "data" / "cloud_nas_migration_tracker.json"
            if tracker_file.exists():
                with open(tracker_file, "r", encoding="utf-8") as f:
                    tracker_data = json.load(f)

                    # Find LUMINA project migration status
                    source_path = str(self.project_root).lower()
                    for path_data in tracker_data.get("migration_status", {}).values():
                        if source_path in path_data.get("source_path", "").lower():
                            status = path_data.get("status", "unknown")
                            progress["status"] = status

                            if status == "in_progress" or status == "partial":
                                # Try to get progress info
                                progress_info = path_data.get("progress", {})
                                progress["files_migrated"] = progress_info.get("files_migrated", 0)
                                progress["total_files"] = progress_info.get("total_files", 24226)
                                progress["size_migrated_gb"] = progress_info.get("size_migrated_gb", 0.0)
                                progress["total_size_gb"] = progress_info.get("total_size_gb", 3.73)

                                if progress["total_size_gb"] > 0:
                                    progress["progress_percent"] = (
                                        progress["size_migrated_gb"] / progress["total_size_gb"]
                                    ) * 100

                            break

            # Check for migration log files
            log_files = list(self.project_root.glob("migration_log_*.txt"))
            if log_files:
                # Most recent log
                latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
                if latest_log.exists():
                    # Try to parse progress from log
                    try:
                        with open(latest_log, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            if "complete" in content.lower() or "finished" in content.lower():
                                progress["status"] = "complete"
                                progress["progress_percent"] = 100.0
                            elif "error" in content.lower() or "failed" in content.lower():
                                progress["status"] = "error"
                    except Exception:
                        pass

            # Calculate estimated time remaining
            if progress["status"] == "in_progress" and progress["progress_percent"] > 0:
                # Estimate based on WiFi speed (50-100 Mbps)
                remaining_gb = progress["total_size_gb"] - progress["size_migrated_gb"]
                if remaining_gb > 0:
                    # Assume average 75 Mbps (9.375 MB/s)
                    estimated_seconds = (remaining_gb * 1024) / 9.375
                    if estimated_seconds < 60:
                        progress["estimated_time_remaining"] = f"{int(estimated_seconds)} seconds"
                    elif estimated_seconds < 3600:
                        progress["estimated_time_remaining"] = f"{int(estimated_seconds / 60)} minutes"
                    else:
                        progress["estimated_time_remaining"] = f"{int(estimated_seconds / 3600)} hours"

        except Exception as e:
            logger.debug(f"Error checking migration progress: {e}")

        return progress

    def _generate_status_message(self, status: Dict[str, Any], progress: Dict[str, Any]) -> str:
        """
        Generate human-readable status message for IMVA.

        Args:
            status: Full status dictionary
            progress: Migration progress dictionary

        Returns:
            Status message string
        """
        if progress.get("status") == "complete":
            return "✅ NAS Migration Complete! All files migrated successfully."

        if progress.get("status") == "in_progress":
            percent = progress.get("progress_percent", 0.0)
            files = progress.get("files_migrated", 0)
            total = progress.get("total_files", 0)
            size = progress.get("size_migrated_gb", 0.0)
            total_size = progress.get("total_size_gb", 3.73)
            time_remaining = progress.get("estimated_time_remaining", "calculating...")

            return (
                f"🔄 NAS Migration In Progress: {percent:.1f}% complete\n"
                f"   Files: {files:,} / {total:,}\n"
                f"   Size: {size:.2f} GB / {total_size:.2f} GB\n"
                f"   Estimated time remaining: {time_remaining}"
            )

        if progress.get("status") == "error":
            return "❌ NAS Migration Error - Check logs for details"

        nas_accessible = status.get("nas_accessibility", {}).get("accessible", False)
        creds_available = status.get("azure_vault_credentials", {}).get("available", False)

        if nas_accessible and creds_available:
            return "✅ Ready to migrate - NAS accessible and credentials available"
        elif not nas_accessible:
            return "⚠️ NAS not accessible - Check network connection"
        elif not creds_available:
            return "⚠️ Credentials not available - Check Azure Vault/TRIAD"
        else:
            return "⏸️ Migration status unknown - Checking..."

    def update_imva_status(self):
        """Update IMVA status file with current migration status."""
        try:
            status = self.get_migration_status()

            # Write to IMVA status file
            with open(self.imva_status_file, "w", encoding="utf-8") as f:
                json.dump(status, f, indent=2, ensure_ascii=False)

            logger.debug(f"✅ Updated IMVA status file: {self.imva_status_file}")

            # Also log status message
            status_msg = status.get("status_message", "Status unknown")
            logger.info(f"📊 Migration Status: {status_msg}")

        except Exception as e:
            logger.error(f"Error updating IMVA status: {e}", exc_info=True)

    def start_monitoring(self):
        """Start periodic monitoring thread."""
        if self.running:
            logger.warning("Monitor already running")
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("✅ IMVA NAS Migration Monitor started")

    def stop_monitoring(self):
        """Stop periodic monitoring."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("⏸️ IMVA NAS Migration Monitor stopped")

    def _monitor_loop(self):
        """Main monitoring loop."""
        logger.info("🔄 Starting IMVA migration status monitoring loop...")

        while self.running:
            try:
                self.update_imva_status()
                time.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}", exc_info=True)
                time.sleep(self.update_interval)

    def get_status_for_imva_display(self) -> str:
        """
        Get formatted status string for IMVA display.

        Returns:
            Formatted status string
        """
        status = self.get_migration_status()
        return status.get("status_message", "Status unknown")


def main():
    """Main function for testing/standalone execution."""
    import argparse

    parser = argparse.ArgumentParser(description="IMVA NAS Migration Status Monitor")
    parser.add_argument("--interval", type=int, default=30, help="Update interval in seconds (default: 30)")
    parser.add_argument("--once", action="store_true", help="Update once and exit")
    parser.add_argument("--start", action="store_true", help="Start continuous monitoring")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    monitor = IMVANASMigrationMonitor(project_root, update_interval=args.interval)

    if args.once:
        # Update once and display
        status = monitor.get_migration_status()
        print("\n" + "=" * 80)
        print("IMVA NAS MIGRATION STATUS")
        print("=" * 80)
        print(status.get("status_message", "Status unknown"))
        print()
        print(f"NAS Accessible: {status.get('nas_accessible', False)}")
        print(f"Credentials Available: {status.get('credentials_available', False)}")
        print(f"Migration Status: {status.get('migration_status', 'unknown')}")
        print(f"Progress: {status.get('progress_percent', 0.0):.1f}%")
        print(f"Files: {status.get('files_migrated', 0):,} / {status.get('total_files', 0):,}")
        print(f"Size: {status.get('size_migrated_gb', 0.0):.2f} GB / {status.get('total_size_gb', 0.0):.2f} GB")
        print("=" * 80)

        # Update IMVA status file
        monitor.update_imva_status()
        print(f"\n✅ Status saved to: {monitor.imva_status_file}")

    elif args.start:
        # Start continuous monitoring
        print("🚀 Starting IMVA NAS Migration Monitor...")
        print(f"   Update interval: {args.interval} seconds")
        print(f"   Status file: {monitor.imva_status_file}")
        print("\nPress Ctrl+C to stop...\n")

        monitor.start_monitoring()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏸️ Stopping monitor...")
            monitor.stop_monitoring()
            print("✅ Monitor stopped")
    else:
        # Default: update once
        monitor.update_imva_status()
        print(f"✅ Status updated: {monitor.imva_status_file}")
        print(f"   Status: {monitor.get_status_for_imva_display()}")


if __name__ == "__main__":


    main()