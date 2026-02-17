#!/usr/bin/env python3
"""
Start Auto-Accept Monitor - Background Service

Starts the auto-accept monitor in background mode.
This will automatically accept "Accept All Changes" dialogs without manual clicking.

Tags: #AUTO_ACCEPT #MONITOR #BACKGROUND #CURSOR_IDE @JARVIS @LUMINA
"""

import sys
import subprocess
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

# Start monitor in background
monitor_script = script_dir / "jarvis_auto_accept_monitor.py"

print("=" * 80)
print("🚀 STARTING AUTO-ACCEPT MONITOR")
print("=" * 80)
print()
print("This will automatically accept 'Accept All Changes' dialogs")
print("No manual clicking needed!")
print()

try:
    # Start in background mode
    process = subprocess.Popen(
        [sys.executable, str(monitor_script), "--background"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
    )

    print("✅ Auto-accept monitor started in background")
    print(f"   PID: {process.pid}")
    print()
    print("The monitor will:")
    print("  - Use VLM to detect 'Accept All' dialogs")
    print("  - Automatically click the button when detected")
    print("  - Run continuously in the background")
    print()
    print("To stop: Use emergency_stop_all_monitors.py")
    print("=" * 80)

except Exception as e:
    print(f"❌ Failed to start monitor: {e}")
    sys.exit(1)
