#!/usr/bin/env python3
"""
Mustafar Mode - Burn-In Testing for Disk Migration

"Burn-in" testing mode - pushes migration to maximum limits.
Like Mustafar's lava flows - maximum heat, maximum stress, maximum performance.

Features:
- Maximum throughput
- Extended runtime
- Stress testing
- Performance monitoring
- Error resilience testing
- "The system will be pushed to its limits" - Mustafar Mode

Tags: #MUSTAFAR-MODE #BURN-IN #STRESS-TEST #MAX-PERFORMANCE @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from background_disk_space_migration import BackgroundDiskSpaceMigration
    from disk_migration_progress_display import MigrationProgressDisplay
    from lumina_logger import get_logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("MustafarMode")


class MustafarModeMigration:
    """
    Mustafar Mode - Burn-In Testing

    "You were the chosen one! It was said you would destroy the Sith, not join them!"
    - Maximum stress testing mode
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Mustafar Mode Configuration - MAXIMUM STRESS
        self.mustafar_config = {
            "mode": "mustafar_burn_in",
            "max_workers": 8,  # Maximum workers (was 4)
            "batch_size_gb": 50.0,  # Maximum batch size (was 25GB)
            "check_interval": 10,  # Ultra-fast checks (was 30s)
            "stress_level": "maximum",
            "error_tolerance": "high",  # Keep going despite errors
            "performance_monitoring": True,
            "extended_runtime": True
        }

        # Initialize migration with mustafar config
        self.migration = BackgroundDiskSpaceMigration(project_root)

        # Override with mustafar settings
        self.migration.max_workers = self.mustafar_config["max_workers"]
        self.migration.migration_batch_size_gb = self.mustafar_config["batch_size_gb"]
        self.migration.check_interval_seconds = self.mustafar_config["check_interval"]

        self.logger.info("🔥 MUSTAFAR MODE ACTIVATED - Burn-In Testing")
        self.logger.info("   'The system will be pushed to its limits'")
        self.logger.info(f"   Workers: {self.mustafar_config['max_workers']}")
        self.logger.info(f"   Batch Size: {self.mustafar_config['batch_size_gb']} GB")
        self.logger.info(f"   Check Interval: {self.mustafar_config['check_interval']}s")

    def start_burn_in(self):
        """Start Mustafar Mode burn-in testing"""
        print("\n" + "=" * 80)
        print("🔥 MUSTAFAR MODE - BURN-IN TESTING")
        print("=" * 80)
        print()
        print("'You were the chosen one! It was said you would destroy the Sith...'")
        print("'...not join them!'")
        print()
        print("⚡ MAXIMUM STRESS MODE ACTIVATED")
        print(f"   Workers: {self.mustafar_config['max_workers']}")
        print(f"   Batch Size: {self.mustafar_config['batch_size_gb']} GB")
        print(f"   Check Interval: {self.mustafar_config['check_interval']}s")
        print(f"   Stress Level: {self.mustafar_config['stress_level']}")
        print()
        print("🔥 The system will be pushed to its limits!")
        print("=" * 80)
        print()

        # Start migration with mustafar config - WITH VISIBLE PROGRESS BAR
        self.migration.start(show_progress=True, foreground_progress=True)

        # Start performance monitoring
        if self.mustafar_config["performance_monitoring"]:
            self._start_performance_monitoring()

        # Keep running
        try:
            start_time = time.time()
            while True:
                time.sleep(60)  # Update every minute

                elapsed = time.time() - start_time
                elapsed_hours = elapsed / 3600

                # Show status
                status = self.migration.get_status()
                if status["disk_status"]:
                    ds = status["disk_status"]
                    state = status.get("state", {})
                    migrated = state.get("total_migrated_gb", 0)

                    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                          f"🔥 MUSTAFAR MODE - {elapsed_hours:.1f}h elapsed | "
                          f"Disk: {ds['percent_used']:.1f}% | "
                          f"Migrated: {migrated:.2f} GB | "
                          f"Status: {'🔥 BURNING' if self.migration.running else 'COOLED'}")
        except KeyboardInterrupt:
            print("\n\n🔥 Mustafar Mode: 'I have the high ground!'")
            print("   Stopping burn-in test...")
            self.migration.stop()

    def _start_performance_monitoring(self):
        """Start performance monitoring thread"""
        def monitor():
            while self.migration.running:
                try:
                    import psutil
                    cpu = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory().percent
                    disk_io = psutil.disk_io_counters()

                    perf_data = {
                        "timestamp": datetime.now().isoformat(),
                        "cpu_percent": cpu,
                        "memory_percent": memory,
                        "disk_read_mb": disk_io.read_bytes / (1024**2) if disk_io else 0,
                        "disk_write_mb": disk_io.write_bytes / (1024**2) if disk_io else 0
                    }

                    # Log performance
                    perf_file = self.project_root / "data" / "disk_migration" / "mustafar_performance.jsonl"
                    with open(perf_file, 'a', encoding='utf-8') as f:
                        f.write(json.dumps(perf_data) + '\n')

                    time.sleep(30)  # Monitor every 30 seconds
                except Exception as e:
                    logger.debug(f"Performance monitoring error: {e}")
                    time.sleep(30)

        import threading
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        self.logger.info("   📊 Performance monitoring started")


def main():
    try:
        """Main function - Mustafar Mode"""
        import argparse

        parser = argparse.ArgumentParser(description="Mustafar Mode - Burn-In Testing")
        parser.add_argument("--start", action="store_true", help="Start Mustafar Mode burn-in")
        parser.add_argument("--status", action="store_true", help="Show Mustafar Mode status")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        mustafar = MustafarModeMigration(project_root)

        if args.start:
            mustafar.start_burn_in()
        elif args.status:
            status = mustafar.migration.get_status()
            print("\n" + "=" * 80)
            print("🔥 MUSTAFAR MODE STATUS")
            print("=" * 80)
            print(f"Mode: {mustafar.mustafar_config['mode']}")
            print(f"Workers: {mustafar.mustafar_config['max_workers']}")
            print(f"Batch Size: {mustafar.mustafar_config['batch_size_gb']} GB")
            print(f"Check Interval: {mustafar.mustafar_config['check_interval']}s")
            print(f"Running: {mustafar.migration.running}")
            print("=" * 80)
        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()