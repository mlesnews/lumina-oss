#!/usr/bin/env python3
"""
Initialize Centralized Logging

1. Mounts L: drive to NAS logs share
2. Syncs local logs to NAS
3. Creates directory junctions for real-time redirection
4. Configures centralized logging environment

Tags: #LOGGING #NAS #SETUP #JUNCTIONS @JARVIS @LUMINA
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from nas_logging_watchdog import NASLoggingWatchdog

def initialize():
    print("📋 INITIALIZING CENTRALIZED LOGGING SYSTEM")
    print("=" * 60)

    watchdog = NASLoggingWatchdog()

    print("\n1. Checking L: drive mount...")
    if watchdog.check_and_ensure_mount():
        print("✅ L: drive is mounted and redirected.")
    else:
        print("❌ Failed to mount L: drive. System will fallback to local logging.")
        print("   Logs will be synced back once L: is available.")

    print("\n2. Status Summary:")
    is_mounted = watchdog.is_l_drive_mounted()
    print(f"   NAS Connected: {'YES' if is_mounted else 'NO'}")
    print(f"   Log Location:  {'L:\\logs (Centralized)' if is_mounted else 'data\\logs (Local Fallback)'}")

    if is_mounted:
        print("\n3. Junction Redirections:")
        mappings = watchdog._get_junction_mappings()
        for local, nas in mappings.items():
            status = "ACTIVE" if watchdog._is_junction(local) else "INACTIVE"
            print(f"   {local.name:15} -> {nas} [{status}]")

    print("\n" + "=" * 60)
    print("🎉 Initialization process complete.")

if __name__ == "__main__":
    initialize()
