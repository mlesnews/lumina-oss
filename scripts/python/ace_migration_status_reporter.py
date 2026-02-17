#!/usr/bin/env python3
"""
ACE NAS Migration Status Reporter

ACE (Anakin Combat Virtual Assistant) reports NAS migration status periodically.
Integrates with ACE voice interface and display system.

Tags: #ACE #NAS #MIGRATION #STATUS #VOICE @JARVIS @LUMINA
"""

import json
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from imva_nas_migration_monitor import IMVANASMigrationMonitor
    from lumina_logger import get_logger
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

logger = get_logger("ACEMigrationStatusReporter")


class ACEMigrationStatusReporter:
    """
    ACE NAS Migration Status Reporter

    Provides periodic status updates via ACE voice interface and display.
    """

    def __init__(self, project_root: Path, update_interval: int = 60):
        """
        Initialize ACE Migration Status Reporter.

        Args:
            project_root: Path to project root
            update_interval: Update interval in seconds (default: 60)
        """
        self.project_root = project_root
        self.update_interval = update_interval
        self.monitor = IMVANASMigrationMonitor(project_root, update_interval=30)
        self.running = False
        self.reporter_thread = None

        # ACE status file
        self.ace_status_file = project_root / "data" / "ace" / "migration_status.json"
        self.ace_status_file.parent.mkdir(parents=True, exist_ok=True)

        # ACE voice/display integration
        self.ace_voice_file = project_root / "data" / "ace" / "voice_messages.jsonl"
        self.ace_voice_file.parent.mkdir(parents=True, exist_ok=True)

        logger.info("✅ ACE Migration Status Reporter initialized")
        logger.info(f"   Update interval: {update_interval} seconds")
        logger.info(f"   Status file: {self.ace_status_file}")
        logger.info(f"   Voice file: {self.ace_voice_file}")

    def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status from monitor."""
        return self.monitor.get_migration_status()

    def generate_ace_message(self, status: Dict[str, Any]) -> str:
        """
        Generate ACE-style status message.

        Args:
            status: Migration status dictionary

        Returns:
            ACE-formatted message string
        """
        migration_status = status.get("migration_status", "unknown")
        progress_percent = status.get("progress_percent", 0.0)
        files_migrated = status.get("files_migrated", 0)
        total_files = status.get("total_files", 0)
        size_migrated = status.get("size_migrated_gb", 0.0)
        total_size = status.get("total_size_gb", 3.73)
        time_remaining = status.get("estimated_time_remaining", "calculating...")

        if migration_status == "complete":
            return (
                "Master, NAS migration is complete. All files have been successfully "
                f"migrated to the network storage. Total size: {total_size:.2f} gigabytes. "
                "The Force is strong with this migration."
            )

        if migration_status == "in_progress":
            return (
                f"Master, NAS migration is in progress. Current status: {progress_percent:.1f} percent complete. "
                f"Files migrated: {files_migrated:,} of {total_files:,}. "
                f"Data transferred: {size_migrated:.2f} gigabytes of {total_size:.2f} gigabytes. "
                f"Estimated time remaining: {time_remaining}. "
                "The migration proceeds as planned."
            )

        if migration_status == "error":
            return (
                "Master, I've detected an issue with the NAS migration. "
                "Please check the migration logs for details. "
                "I recommend investigating the network connection and NAS accessibility."
            )

        nas_accessible = status.get("nas_accessible", False)
        creds_available = status.get("credentials_available", False)

        if nas_accessible and creds_available:
            return (
                "Master, the NAS migration system is ready. "
                "Network storage is accessible and credentials are available. "
                "We are prepared to begin the migration when you give the command."
            )
        elif not nas_accessible:
            return (
                "Master, I cannot access the network storage. "
                "Please verify the network connection to the NAS. "
                "The migration cannot proceed until connectivity is restored."
            )
        elif not creds_available:
            return (
                "Master, NAS credentials are not available. "
                "Please check the Azure Key Vault or TRIAD system. "
                "The migration requires authentication credentials to proceed."
            )
        else:
            return (
                "Master, I am checking the NAS migration status. "
                "Please stand by while I gather the current information."
            )

    def generate_ace_short_status(self, status: Dict[str, Any]) -> str:
        """
        Generate short ACE status message for quick updates.

        Args:
            status: Migration status dictionary

        Returns:
            Short ACE message
        """
        migration_status = status.get("migration_status", "unknown")
        progress_percent = status.get("progress_percent", 0.0)

        if migration_status == "complete":
            return "NAS migration complete, Master."

        if migration_status == "in_progress":
            return f"Migration in progress: {progress_percent:.1f}% complete, Master."

        if migration_status == "error":
            return "Migration error detected, Master."

        return "Migration status: ready, Master."

    def report_status(self):
        """Report current migration status via ACE."""
        try:
            status = self.get_migration_status()

            # Generate ACE messages
            full_message = self.generate_ace_message(status)
            short_message = self.generate_ace_short_status(status)

            # Save to ACE status file
            ace_status = {
                "timestamp": datetime.now().isoformat(),
                "status": status,
                "ace_message_full": full_message,
                "ace_message_short": short_message,
                "reported_by": "ACE"
            }

            with open(self.ace_status_file, "w", encoding="utf-8") as f:
                json.dump(ace_status, f, indent=2, ensure_ascii=False)

            # Append to ACE voice messages file
            voice_entry = {
                "timestamp": datetime.now().isoformat(),
                "message": full_message,
                "short_message": short_message,
                "type": "migration_status",
                "priority": "normal"
            }

            with open(self.ace_voice_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(voice_entry, ensure_ascii=False) + "\n")

            # Log the report
            logger.info("📢 ACE Migration Status Report:")
            logger.info(f"   {short_message}")
            logger.info(f"   Full: {full_message[:100]}...")

            # Print for immediate visibility
            print("\n" + "=" * 80)
            print("📢 ACE MIGRATION STATUS REPORT")
            print("=" * 80)
            print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"\n{full_message}\n")
            print("=" * 80)
            print()

        except Exception as e:
            logger.error(f"Error reporting status via ACE: {e}", exc_info=True)

    def start_reporting(self):
        """Start periodic status reporting."""
        if self.running:
            logger.warning("Reporter already running")
            return

        self.running = True
        self.reporter_thread = threading.Thread(target=self._reporting_loop, daemon=True)
        self.reporter_thread.start()
        logger.info("✅ ACE Migration Status Reporter started")

    def stop_reporting(self):
        """Stop periodic reporting."""
        self.running = False
        if self.reporter_thread:
            self.reporter_thread.join(timeout=5)
        logger.info("⏸️ ACE Migration Status Reporter stopped")

    def _reporting_loop(self):
        """Main reporting loop."""
        logger.info("🔄 Starting ACE migration status reporting loop...")

        # Report immediately
        self.report_status()

        while self.running:
            try:
                time.sleep(self.update_interval)
                if self.running:
                    self.report_status()
            except Exception as e:
                logger.error(f"Error in reporting loop: {e}", exc_info=True)
                time.sleep(self.update_interval)


def main():
    """Main function for testing/standalone execution."""
    import argparse

    parser = argparse.ArgumentParser(description="ACE NAS Migration Status Reporter")
    parser.add_argument("--interval", type=int, default=60, help="Update interval in seconds (default: 60)")
    parser.add_argument("--once", action="store_true", help="Report once and exit")
    parser.add_argument("--start", action="store_true", help="Start continuous reporting")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    reporter = ACEMigrationStatusReporter(project_root, update_interval=args.interval)

    if args.once:
        # Report once
        reporter.report_status()
        print(f"\n✅ Status saved to: {reporter.ace_status_file}")
        print(f"✅ Voice message saved to: {reporter.ace_voice_file}")

    elif args.start:
        # Start continuous reporting
        print("🚀 Starting ACE Migration Status Reporter...")
        print(f"   Update interval: {args.interval} seconds")
        print(f"   Status file: {reporter.ace_status_file}")
        print(f"   Voice file: {reporter.ace_voice_file}")
        print("\nPress Ctrl+C to stop...\n")

        reporter.start_reporting()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏸️ Stopping reporter...")
            reporter.stop_reporting()
            print("✅ Reporter stopped")
    else:
        # Default: report once
        reporter.report_status()


if __name__ == "__main__":


    main()