#!/usr/bin/env python3
"""
Simple test to verify Kenny's window appears
Run this directly to see if the window shows up
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

print("=" * 80)
print("🧪 TESTING KENNY WINDOW")
print("=" * 80)
print()

try:
    from kenny_imva_enhanced import KennyIMVAEnhanced
    print("✅ Import successful")

    print("Creating Kenny instance...")
    kenny = KennyIMVAEnhanced(size=171)  # Match Ace's size
    print(f"✅ Kenny created: size={kenny.size}px")
    print(f"   Screen: {kenny.screen_width}x{kenny.screen_height}")

    print()
    print("Creating window...")
    kenny.create_window()
    print("✅ Window created")
    print(f"   Window should appear at center of screen")
    print(f"   Look for a white window with orange Kenny sprite")
    print()
    print("Starting main loop...")
    print("   (Window should be visible now)")
    print("   Press Ctrl+C to stop")
    print("=" * 80)

    kenny.root.mainloop()

except KeyboardInterrupt:
    print("\n✅ Test stopped")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
