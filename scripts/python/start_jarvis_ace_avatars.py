#!/usr/bin/env python3
"""
Start JARVIS and ACE Avatar Windows

Starts the actual avatar windows for JARVIS and ACE so they're visible on desktop.

Tags: #VA #AVATAR #JARVIS #ACE #STARTUP @JARVIS @ACE @LUMINA
"""

import sys
import subprocess
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("StartJARVISACE")


def start_jarvis_avatar():
    """Start JARVIS narrator avatar"""
    print("🎭 Starting JARVIS Narrator Avatar...")

    jarvis_script = script_dir / "jarvis_narrator_avatar.py"
    if jarvis_script.exists():
        try:
            process = subprocess.Popen(
                [sys.executable, str(jarvis_script)],
                cwd=str(project_root)
                # No CREATE_NO_WINDOW - JARVIS needs to show its window
            )
            print(f"✅ JARVIS Narrator Avatar started (PID: {process.pid})")
            time.sleep(2)  # Give it time to initialize
            return True
        except Exception as e:
            print(f"❌ Failed to start JARVIS: {e}")
            return False
    else:
        print(f"❌ JARVIS script not found: {jarvis_script}")
        return False


def start_ace_avatar():
    """Start ACE (Iron Man) avatar"""
    print("🤖 Starting ACE (Iron Man) Avatar...")

    # Try ironman_animated_va.py first
    ace_script = script_dir / "ironman_animated_va.py"
    if not ace_script.exists():
        # Try other possible names
        ace_script = script_dir / "iron_man_va.py"
    if not ace_script.exists():
        ace_script = script_dir / "ace_avatar.py"

    if ace_script.exists():
        try:
            process = subprocess.Popen(
                [sys.executable, str(ace_script)],
                cwd=str(project_root)
                # No CREATE_NO_WINDOW - ACE needs to show its window
            )
            print(f"✅ ACE Avatar started (PID: {process.pid})")
            time.sleep(2)  # Give it time to initialize
            return True
        except Exception as e:
            print(f"❌ Failed to start ACE: {e}")
            return False
    else:
        print(f"⚠️  ACE avatar script not found")
        print(f"   Tried: ironman_animated_va.py, iron_man_va.py, ace_avatar.py")
        return False


def main():
    """Main function"""
    print("=" * 80)
    print("🚀 STARTING JARVIS AND ACE AVATARS")
    print("=" * 80)
    print()

    jarvis_started = start_jarvis_avatar()
    print()
    ace_started = start_ace_avatar()

    print()
    print("=" * 80)
    print("STATUS")
    print("=" * 80)
    print(f"JARVIS: {'✅ STARTED' if jarvis_started else '❌ NOT STARTED'}")
    print(f"ACE: {'✅ STARTED' if ace_started else '❌ NOT STARTED'}")
    print()
    print("💡 If avatars don't appear, check:")
    print("   1. Widget rendering is running (render_va_desktop_widgets.py)")
    print("   2. Avatar scripts exist and are executable")
    print("   3. No errors in avatar processes")
    print()
    print("=" * 80)


if __name__ == "__main__":


    main()