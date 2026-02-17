#!/usr/bin/env python3
"""
Force Show All Virtual Assistants

Forces JARVIS, ACE, and all VAs to be visible on desktop.
Checks for hidden windows and brings them to front.

Tags: #VA #VISIBILITY #JARVIS #ACE #FORCE_SHOW @JARVIS @ACE @LUMINA
"""

import sys
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    import tkinter as tk
    from lumina_logger import get_logger
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("ForceShowVAs")


def force_show_jarvis():
    """Force JARVIS to be visible"""
    print("🎭 Forcing JARVIS to be visible...")
    try:
        from jarvis_narrator_avatar import JARVISNarratorAvatar

        # Create new instance
        jarvis = JARVISNarratorAvatar()

        # Create window
        jarvis.create_avatar_window()

        # Ensure window is on top and visible
        if jarvis.avatar_window:
            jarvis.avatar_window.lift()
            jarvis.avatar_window.focus_force()
            jarvis.avatar_window.attributes('-topmost', True)
            jarvis.avatar_visible = True
            print("✅ JARVIS window created and brought to front")

            # Start in background thread
            import threading
            def run_jarvis():
                jarvis.run()

            thread = threading.Thread(target=run_jarvis, daemon=True)
            thread.start()
            return True
    except Exception as e:
        print(f"❌ Error showing JARVIS: {e}")
        import traceback
        traceback.print_exc()
        return False


def force_show_ace():
    """Force ACE to be visible"""
    print("🤖 Forcing ACE to be visible...")
    try:
        from ironman_animated_va import IronManAnimatedVA

        # Create new instance
        ace = IronManAnimatedVA()

        # Start
        import threading
        def run_ace():
            ace.run()

        thread = threading.Thread(target=run_ace, daemon=True)
        thread.start()
        print("✅ ACE started")
        return True
    except Exception as e:
        print(f"❌ Error showing ACE: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function"""
    print("=" * 80)
    print("👁️  FORCING ALL VAs TO BE VISIBLE")
    print("=" * 80)
    print()

    jarvis_ok = force_show_jarvis()
    time.sleep(1)
    ace_ok = force_show_ace()

    print()
    print("=" * 80)
    print("STATUS")
    print("=" * 80)
    print(f"JARVIS: {'✅ VISIBLE' if jarvis_ok else '❌ FAILED'}")
    print(f"ACE: {'✅ VISIBLE' if ace_ok else '❌ FAILED'}")
    print()
    print("💡 If VAs still don't appear:")
    print("   1. Check Task Manager for running processes")
    print("   2. Check if windows are behind other windows")
    print("   3. Try Alt+Tab to find hidden windows")
    print("   4. Restart the VA processes")
    print()
    print("=" * 80)

    # Keep script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Exiting...")


if __name__ == "__main__":


    main()