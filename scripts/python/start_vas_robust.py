#!/usr/bin/env python3
"""
Robust VA Starter - Handles errors and ensures VAs start properly

Tags: #ROBUST_STARTUP #ERROR_HANDLING @JARVIS @LUMINA
"""

import sys
import time
import traceback
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

# Wait for system to initialize
print("Waiting for system to initialize...")
time.sleep(5)

try:
    from replika_inspired_va_renderer import render_replika_inspired
    print("✅ Replika renderer loaded")
except ImportError as e:
    print(f"❌ Could not import Replika renderer: {e}")
    print("Falling back to standard renderer...")
    try:
        from render_va_desktop_widgets import render_with_tkinter
        from va_visibility_system import VAVisibilitySystem

        visibility = VAVisibilitySystem()
        visibility.show_all_vas()
        render_with_tkinter(visibility)
    except Exception as e2:
        print(f"❌ Standard renderer also failed: {e2}")
        traceback.print_exc()
        sys.exit(1)

try:
    print("=" * 80)
    print("🚀 STARTING VIRTUAL ASSISTANTS")
    print("=" * 80)
    print()

    render_replika_inspired()

except KeyboardInterrupt:
    print("\n⏹️  Interrupted by user")
except Exception as e:
    print(f"❌ Error starting VAs: {e}")
    traceback.print_exc()

    # Try to notify about the error
    try:
        from notify_papa_palpatine import notify_papa_palpatine
        notify_papa_palpatine(
            f"Failed to start Virtual Assistants: {str(e)}\n\nTraceback:\n{traceback.format_exc()}",
            "startup_error"
        )
    except:
        pass

    sys.exit(1)
