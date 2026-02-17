#!/usr/bin/env python3
"""
NAS Migration VA Integration
Provides migration status integration for Iron Man Virtual Assistant
#JARVIS #NAS #MIGRATION #IRONMAN #VA
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "python"))

from nas_migration_status import NASMigrationStatus


def get_migration_status_for_va() -> Dict[str, Any]:
    """
    Get migration status formatted for VA display

    Returns:
        Dict with status information formatted for VA
    """
    monitor = NASMigrationStatus()
    status = monitor.get_status()

    migration = status.get("migration", {})
    connectivity = status.get("connectivity", {})

    # Format for VA display
    va_status = {
        "system": "NAS Migration",
        "status": status.get("status", "unknown"),
        "is_running": migration.get("running", False),
        "message": monitor.get_status_summary(),
        "details": {
            "laptop_online": connectivity.get("laptop_online", False),
            "current_attempt": migration.get("current_attempt", 0),
            "max_attempts": migration.get("max_attempts", 10),
            "method": migration.get("method", "unknown"),
            "last_success": migration.get("last_success"),
            "last_error": migration.get("last_error")
        },
        "last_updated": status.get("last_updated")
    }

    return va_status


def get_migration_status_message() -> str:
    """Get human-readable status message for VA"""
    monitor = NASMigrationStatus()
    return monitor.get_status_summary()


if __name__ == "__main__":
    # Test/example usage
    status = get_migration_status_for_va()
    print("Migration Status for VA:")
    print(f"  System: {status['system']}")
    print(f"  Status: {status['status']}")
    print(f"  Running: {status['is_running']}")
    print(f"  Message: {status['message']}")
    print(f"  Details: {status['details']}")
