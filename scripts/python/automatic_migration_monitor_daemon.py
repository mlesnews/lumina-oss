#!/usr/bin/env python3
"""
Automatic Migration Monitor Daemon

REAL AUTOMATION: Automatically detects and resumes interrupted migrations.
No manual intervention required - runs in background, monitors, detects, resumes.

Tags: #AUTOMATION #MIGRATION #DAEMON #AUTO-RESUME #REAL-AUTOMATION @JARVIS @TEAM
"""

import sys
import time
import threading
from pathlib import Path
from typing import List, Optional
from datetime import datetime

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from cloud_nas_migration_tracker import CloudNASMigrationTracker
    from resume_interrupted_migration import resume_migration
    from lumina_logger import get_logger
    from standardized_timestamp_logging import get_timestamp_logger
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

logger = get_logger("AutomaticMigrationMonitor")
ts_logger = get_timestamp_logger()


class AutomaticMigrationMonitor:
    """
    Automatic Migration Monitor Daemon

    REAL AUTOMATION:
    - Runs in background
    - Automatically detects interrupted migrations
    - Automatically resumes interrupted migrations
    - No manual intervention required
    """

    def __init__(self, project_root: Optional[Path] = None, check_interval: int = 300):
        """
        Initialize automatic migration monitor

        Args:
            project_root: Project root directory
            check_interval: How often to check for interrupted migrations (seconds)
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.check_interval = check_interval
        self.tracker = CloudNASMigrationTracker(project_root=project_root)
        self.running = False
        self.monitor_thread = None
        self.resumed_migrations = []

        logger.info("🤖 Automatic Migration Monitor initialized")
        logger.info(f"   Check interval: {check_interval} seconds")

    def start(self):
        """Start automatic monitoring"""
        if self.running:
            logger.warning("⚠️  Monitor already running")
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

        logger.info("🚀 Automatic Migration Monitor started")
        logger.info("   Monitoring for interrupted migrations...")
        logger.info("   Will automatically resume when detected")

    def stop(self):
        """Stop automatic monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("🛑 Automatic Migration Monitor stopped")

    def _monitor_loop(self):
        """Background monitoring loop - AUTOMATIC"""
        logger.info("🔄 Monitoring loop started (AUTOMATIC)")

        while self.running:
            try:
                # AUTOMATIC: Check for interrupted migrations
                interrupted = self._detect_interrupted_migrations()

                if interrupted:
                    logger.info(f"🚨 Detected {len(interrupted)} interrupted migration(s)")

                    # AUTOMATIC: Resume each interrupted migration
                    for status in interrupted:
                        if status.can_resume:
                            logger.info(f"🔄 AUTOMATIC RESUME: {status.source_path}")
                            self._auto_resume(status)
                else:
                    logger.debug("✅ No interrupted migrations detected")

                # Wait before next check
                time.sleep(self.check_interval)

            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                time.sleep(60)  # Wait 1 minute on error

    def _detect_interrupted_migrations(self) -> List:
        """Automatically detect interrupted migrations"""
        interrupted = []

        try:
            # Analyze storage to find all migrations
            analysis = self.tracker.analyze_storage()

            # Check each migration status
            for status in analysis.migration_statuses:
                if status.migration_status in ["interrupted", "partial"]:
                    if status.can_resume:
                        interrupted.append(status)

            # Also check known paths
            known_paths = [
                Path("C:/Users/mlesn/Dropbox/my_projects/.lumina"),
                Path("C:/Users/mlesn/Dropbox/my_projects"),
            ]

            for path in known_paths:
                if path.exists():
                    status = self.tracker.check_migration_status(path)
                    if status.migration_status in ["interrupted", "partial"]:
                        if status.can_resume and status not in interrupted:
                            interrupted.append(status)

        except Exception as e:
            logger.error(f"❌ Error detecting interrupted migrations: {e}")

        return interrupted

    def _auto_resume(self, status):
        """Automatically resume interrupted migration"""
        try:
            logger.info(f"🚀 AUTOMATIC RESUME: {status.source_path}")
            logger.info(f"   Progress: {status.size_migrated_gb:.2f} GB / {status.size_total_gb:.2f} GB")

            # Check if already resumed (prevent duplicate resumes)
            if str(status.source_path) in self.resumed_migrations:
                logger.debug(f"   Already resumed - skipping")
                return

            # AUTOMATIC: Resume migration (dry_run=False for actual migration)
            success = resume_migration(str(status.source_path), dry_run=False)

            if success:
                self.resumed_migrations.append(str(status.source_path))
                logger.info(f"✅ AUTOMATIC RESUME COMPLETE: {status.source_path}")
            else:
                logger.warning(f"⚠️  Automatic resume failed: {status.source_path}")

        except Exception as e:
            logger.error(f"❌ Error in automatic resume: {e}")

    def get_status(self) -> dict:
        """Get monitor status"""
        return {
            "running": self.running,
            "check_interval": self.check_interval,
            "resumed_count": len(self.resumed_migrations),
            "resumed_migrations": self.resumed_migrations,
        }


def main():
    """Main function - run as daemon"""
    import argparse

    parser = argparse.ArgumentParser(description="Automatic Migration Monitor Daemon")
    parser.add_argument("--interval", type=int, default=300, help="Check interval in seconds (default: 300)")
    parser.add_argument("--once", action="store_true", help="Run once and exit (for testing)")

    args = parser.parse_args()

    print("="*80)
    print("🤖 AUTOMATIC MIGRATION MONITOR DAEMON")
    print("="*80)
    print()
    print("REAL AUTOMATION:")
    print("  - Automatically detects interrupted migrations")
    print("  - Automatically resumes interrupted migrations")
    print("  - No manual intervention required")
    print()

    monitor = AutomaticMigrationMonitor(check_interval=args.interval)

    if args.once:
        # Run once for testing
        print("🔍 Running one-time check...")
        interrupted = monitor._detect_interrupted_migrations()
        if interrupted:
            print(f"🚨 Found {len(interrupted)} interrupted migration(s)")
            for status in interrupted:
                print(f"   {status.source_path} - {status.migration_status}")
                if status.can_resume:
                    print(f"   ✅ Can resume - Progress: {status.size_migrated_gb:.2f} GB / {status.size_total_gb:.2f} GB")
        else:
            print("✅ No interrupted migrations found")
    else:
        # Run as daemon
        try:
            monitor.start()
            print("🚀 Monitor started - running in background")
            print("   Press Ctrl+C to stop")
            print()

            # Keep running
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n🛑 Stopping monitor...")
            monitor.stop()
            print("✅ Monitor stopped")


if __name__ == "__main__":


    main()