#!/usr/bin/env python3
"""
Start Kenny Simple - Minimal, Guaranteed Visible
Simplest possible start to ensure window is created and visible.

Tags: #KENNY #SIMPLE #VISIBLE @JARVIS @LUMINA
"""

import sys
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

print("=" * 80)
print("🚀 STARTING KENNY - SIMPLE MODE")
print("=" * 80)
print()

try:
    print("Step 1: Importing...")
    from kenny_imva_enhanced import KennyIMVAEnhanced
    print("✅ Import successful")
    print()

    print("Step 2: Creating instance...")
    kenny = KennyIMVAEnhanced(size=120, load_ecosystem=False)
    print(f"✅ Instance created (size: {kenny.size}px)")
    print()

    print("Step 3: Creating window...")
    kenny.create_window()
    print("✅ Window creation method called")
    print()

    # Wait a moment for window to be created
    time.sleep(1)

    # Check if window exists
    if kenny.root:
        print("Step 4: Verifying window...")
        print(f"   ✅ Window exists")
        print(f"   - Title: {kenny.root.title()}")
        print(f"   - Position: ({kenny.root.winfo_x()}, {kenny.root.winfo_y()})")
        print(f"   - Size: {kenny.root.winfo_width()}x{kenny.root.winfo_height()}")
        print(f"   - Viewable: {kenny.root.winfo_viewable()}")
        print()

        # Force visibility
        print("Step 5: Forcing visibility...")
        kenny.root.lift()
        kenny.root.focus_force()
        kenny.root.update()
        kenny.root.update_idletasks()

        # Windows API force visibility
        try:
            import ctypes
            hwnd = int(kenny.root.winfo_id())
            user32 = ctypes.windll.user32
            user32.ShowWindow(hwnd, 1)  # SW_SHOWNORMAL
            user32.ShowWindow(hwnd, 9)  # SW_RESTORE
            user32.SetForegroundWindow(hwnd)
            user32.BringWindowToTop(hwnd)
            print("   ✅ Windows API visibility forced")
        except Exception as e:
            print(f"   ⚠️  Windows API failed: {e}")

        print()
        print("=" * 80)
        print("✅ KENNY WINDOW SHOULD BE VISIBLE NOW!")
        print("=" * 80)
        print()
        print("Look for:")
        print("  - Window title: 'Kenny (@IMVA) - Enhanced Desktop Assistant'")
        print("  - Size: 120x120px")
        print("  - Hot Rod Red circle with hexagonal helmet")
        print("  - Position: Check desktop, especially top-right corner")
        print()
        print("If you still don't see it:")
        print("  1. Check if window is minimized")
        print("  2. Check desktop corners and edges")
        print("  3. Run: python scripts/python/find_and_show_kenny_window.py")
        print()
        print("=" * 80)
        print("   Starting animation loop...")
        print("   Press Ctrl+C to stop")
        print("=" * 80)
        print()
    else:
        print("❌ Window not created!")
        print("   Check logs for errors")
        sys.exit(1)

    # Start main loop
    kenny.start()

except KeyboardInterrupt:
    print("\n👋 Stopping...")
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
