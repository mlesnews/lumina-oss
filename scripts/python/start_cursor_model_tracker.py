#!/usr/bin/env python3
"""
Start Cursor Active Model Tracker

Starts the model tracker in the background to monitor Cursor's active model.

@CURSOR @MODEL @TRACKING
"""

import subprocess
import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

tracker_script = script_dir / "cursor_active_model_tracker.py"

def main():
    """Start the tracker in monitor mode."""
    print("🚀 Starting Cursor Active Model Tracker...")
    print(f"   Script: {tracker_script}")
    print("   Mode: Continuous monitoring")
    print("   Status file: data/cursor_active_model_status.json")
    print("")
    print("   The tracker will run in the background.")
    print("   Press Ctrl+C to stop.")
    print("")

    try:
        subprocess.run([
            sys.executable,
            str(tracker_script),
            "--monitor",
            "--interval", "1.0"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Tracker stopped")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":


    main()