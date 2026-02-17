#!/usr/bin/env python3
"""
Test Kenny Window Creation
Simple test to see if Kenny window is created and visible.

Tags: #KENNY #TEST #WINDOW @JARVIS @LUMINA
"""

import sys
import time
import tkinter as tk
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

print("=" * 80)
print("🧪 TESTING KENNY WINDOW CREATION")
print("=" * 80)
print()

try:
    from kenny_imva_enhanced import KennyIMVAEnhanced

    print("✅ Import successful")
    print("   Creating Kenny instance...")

    kenny = KennyIMVAEnhanced(size=120, load_ecosystem=False)

    print(f"✅ Instance created (size: {kenny.size}px)")
    print()
    print("   Creating window...")

    # Create window
    kenny.create_window()

    print("✅ Window created")
    print()

    # Check window properties
    if kenny.root:
        print("   Window properties:")
        print(f"   - Title: {kenny.root.title()}")
        print(f"   - Position: ({kenny.root.winfo_x()}, {kenny.root.winfo_y()})")
        print(f"   - Size: {kenny.root.winfo_width()}x{kenny.root.winfo_height()}")
        print(f"   - Visible: {kenny.root.winfo_viewable()}")
        print()

        # Force visibility
        kenny.root.lift()
        kenny.root.focus_force()
        kenny.root.update()

        print("   ✅ Window should be visible now!")
        print()
        print("   Look for:")
        print("   - Window title: 'Kenny (@IMVA) - Enhanced Desktop Assistant'")
        print("   - Size: 120x120px")
        print("   - Hot Rod Red circle with hexagonal helmet")
        print()
    else:
        print("   ❌ Window not created!")

    print("=" * 80)
    print("   Window created - should be visible")
    print("   Press Ctrl+C to stop")
    print("=" * 80)
    print()

    # Start main loop
    kenny.start()

except KeyboardInterrupt:
    print("\n👋 Stopping...")
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
