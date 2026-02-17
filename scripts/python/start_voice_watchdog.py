#!/usr/bin/env python3
"""
Start Voice Systems Watchdog
Quick launcher for the voice systems watchdog
"""
import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from voice_systems_watchdog import VoiceSystemsWatchdog

if __name__ == "__main__":
    print("🚀 Starting Voice Systems Watchdog...")
    watchdog = VoiceSystemsWatchdog()
    watchdog.start()

    print("✅ Watchdog started. Press Ctrl+C to stop.")
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping watchdog...")
        watchdog.stop()
        print("✅ Watchdog stopped")
