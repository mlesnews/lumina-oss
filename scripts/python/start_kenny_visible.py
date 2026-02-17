#!/usr/bin/env python3
"""
Start Kenny Visible - REQUIRED

Ensures Kenny is visible on screen and looks like Iron Man (not orange hoodie).
Fixes the issue where Kenny isn't showing up.

Tags: #KENNY #VISUAL #IRON_MAN #REQUIRED @JARVIS @LUMINA
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from kenny_imva_enhanced import KennyIMVAEnhanced
    KENNY_AVAILABLE = True
except ImportError as e:
    KENNY_AVAILABLE = False
    print(f"❌ Kenny not available: {e}")
    sys.exit(1)

print("=" * 80)
print("🤖 STARTING KENNY (IRON MAN VIRTUAL ASSISTANT) - REQUIRED")
print("=" * 80)
print()
print("This will:")
print("  - Show Kenny on screen (Iron Man design)")
print("  - Make sure it's visible (not hidden)")
print("  - Look like Iron Man (not orange hoodie)")
print()

try:
    # Create Kenny with default size (visible)
    kenny = KennyIMVAEnhanced(size=120)  # Larger size for visibility

    print(f"✅ Kenny created (size: {kenny.size}px)")
    print()
    print("Kenny should now be visible on screen")
    print("If you don't see Kenny:")
    print("  1. Check if window is off-screen")
    print("  2. Check if window is minimized")
    print("  3. Look for orange/red circle with helmet")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 80)
    print()

    # Start Kenny
    kenny.start()

except KeyboardInterrupt:
    print("\n👋 Stopping Kenny...")
    if 'kenny' in locals():
        kenny.stop()
except Exception as e:
    print(f"❌ Failed to start Kenny: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
