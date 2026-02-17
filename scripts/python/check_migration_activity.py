#!/usr/bin/env python3
"""
Check Migration Activity - Transparency Tool

Shows what the migration is actually doing right now.
Helps operator understand if it's scanning, migrating, or waiting.

Tags: #TRANSPARENCY #STATUS #OPERATOR @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from background_disk_space_migration import BackgroundDiskSpaceMigration

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🔍 MIGRATION ACTIVITY CHECK - TRANSPARENCY")
    print("=" * 80)
    print()

    manager = BackgroundDiskSpaceMigration(project_root)
    status = manager.get_status()
    op_status = manager.get_operation_status()

    print("**MIGRATION STATUS:**")
    print(f"   Running: {'✅ YES' if status.get('running') else '❌ NO'}")
    print()

    if status.get('running'):
        print("**CURRENT OPERATION:**")
        current_status = op_status.get("status", "unknown")
        message = op_status.get("message", "")

        status_info = {
            "initializing": "🔄 Initializing - Setting up migration system",
            "checking_disk": "🔍 Checking Disk - Evaluating disk space",
            "scanning": "🔎 Scanning - Finding migration candidates (this takes time!)",
            "migrating": "📦 Migrating - Actually moving files now",
            "no_candidates": "⏸️ No Candidates - No items found to migrate",
            "error": "❌ Error - Something went wrong",
            "idle": "⏸️ Idle - Waiting for next check cycle",
            "waiting": "⏳ Waiting - Between check cycles"
        }

        print(f"   {status_info.get(current_status, f'⚪ {current_status}')}")
        if message:
            print(f"   Details: {message}")
        print()

        if current_status == "scanning":
            print("💡 **TRANSPARENCY:**")
            print("   The system is currently SCANNING directories to find what to migrate.")
            print("   This can take several minutes for large directories.")
            print("   Progress will update once scanning completes and migration begins.")
            print()
        elif current_status == "checking_disk":
            print("💡 **TRANSPARENCY:**")
            print("   The system is checking disk space status.")
            print("   This happens every 30 seconds (or 10s in Mustafar mode).")
            print()
        elif current_status == "migrating":
            print("💡 **TRANSPARENCY:**")
            print("   The system is actively migrating files!")
            print("   Progress should be incrementing now.")
            print()
    else:
        print("⚠️  **MIGRATION IS NOT RUNNING**")
        print()
        print("To start migration:")
        print("   python scripts/python/background_disk_space_migration.py --start")
        print()
        print("Or for Mustafar mode:")
        print("   python scripts/python/mustafar_mode_migration.py --start")
        print()

    # Show disk status
    if status.get("disk_status"):
        ds = status["disk_status"]
        print("**DISK STATUS:**")
        print(f"   Usage: {ds['percent_used']:.1f}%")
        print(f"   Needs Migration: {'✅ YES' if ds.get('needs_migration') else '❌ NO'}")
        if ds.get('needs_migration'):
            print(f"   Space to Free: {ds.get('space_to_free_gb', 0):.2f} GB")
        print()

    print("=" * 80)
