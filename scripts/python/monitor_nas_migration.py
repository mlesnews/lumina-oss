#!/usr/bin/env python3
"""
Monitor NAS Migration Status
Real-time monitoring in terminal for NAS migration status
#JARVIS #NAS #MIGRATION #MONITORING
"""

import sys
import time
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "python"))

from nas_migration_status import NASMigrationStatus
import logging
logger = logging.getLogger("monitor_nas_migration")



def monitor_migration(refresh_interval: int = 5):
    """Monitor migration status with live updates"""
    monitor = NASMigrationStatus()

    print("=" * 80)
    print("  NAS MIGRATION STATUS MONITOR")
    print("=" * 80)
    print(f"Monitoring migration status (refresh every {refresh_interval}s)")
    print("Press Ctrl+C to stop")
    print("=" * 80)
    print()

    try:
        while True:
            # Clear screen (works on most terminals)
            import os
            os.system('cls' if os.name == 'nt' else 'clear')

            print("=" * 80)
            print("  NAS MIGRATION STATUS MONITOR")
            print(f"  Last Update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 80)
            print()

            status = monitor.get_status()

            # Display summary
            summary = monitor.get_status_summary()
            print(f"Status: {summary}")
            print()

            # Display details
            migration = status.get("migration", {})
            connectivity = status.get("connectivity", {})

            print("Migration Details:")
            print(f"  Running: {migration.get('running', False)}")
            print(f"  Current Attempt: {migration.get('current_attempt', 0)}/{migration.get('max_attempts', 10)}")
            print(f"  Method: {migration.get('method', 'N/A')}")
            print(f"  Source: {migration.get('source', 'N/A')}")
            print(f"  Destination: {migration.get('destination', 'N/A')}")

            if migration.get("last_success"):
                print(f"  Last Success: {migration.get('last_success')}")
            if migration.get("last_error"):
                print(f"  Last Error: {migration.get('last_error')}")

            print()
            print("Connectivity:")
            print(f"  Laptop Online: {connectivity.get('laptop_online', False)}")
            if connectivity.get("last_check"):
                print(f"  Last Check: {connectivity.get('last_check')}")

            print()
            print("=" * 80)
            print(f"Next refresh in {refresh_interval}s... (Ctrl+C to stop)")

            time.sleep(refresh_interval)

    except KeyboardInterrupt:
        print()
        print()
        print("=" * 80)
        print("Monitoring stopped")
        print("=" * 80)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Monitor NAS Migration Status")
        parser.add_argument("--interval", "-i", type=int, default=5,
                           help="Refresh interval in seconds (default: 5)")
        parser.add_argument("--once", action="store_true",
                           help="Show status once and exit")

        args = parser.parse_args()

        if args.once:
            monitor = NASMigrationStatus()
            status = monitor.get_status()
            print("=" * 80)
            print("  NAS MIGRATION STATUS")
            print("=" * 80)
            print()
            print(monitor.get_status_summary())
            print()
            print("Details:")
            import json
            print(json.dumps(status, indent=2))
            return 0
        else:
            monitor_migration(args.interval)
            return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())