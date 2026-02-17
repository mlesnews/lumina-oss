#!/usr/bin/env python3
"""
Force Start Kenny Visible - FIXED
Ensures Kenny window is created and visible on screen.

Tags: #KENNY #VISIBILITY #FORCE_START @JARVIS @LUMINA
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

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ForceStartKenny")

print("=" * 80)
print("🚀 FORCE STARTING KENNY - ENSURING VISIBILITY")
print("=" * 80)
print()

try:
    from kenny_imva_enhanced import KennyIMVAEnhanced

    print("✅ Kenny module loaded")
    print("   Creating Kenny instance...")

    # Create Kenny with explicit size and visibility settings
    kenny = KennyIMVAEnhanced(
        size=120,  # Explicit size
        load_ecosystem=False  # Don't load heavy integrations
    )

    print(f"✅ Kenny instance created (size: {kenny.size}px)")
    print()
    print("   Window settings:")
    print(f"   - Size: {kenny.size}x{kenny.size}px")
    print(f"   - Screen: {kenny.screen_width}x{kenny.screen_height}")
    print()

    print("   Creating window...")

    # Create window explicitly
    kenny.create_window()

    print("✅ Window created")
    print()
    print("   Window should now be visible!")
    print("   Look for:")
    print("   - 120x120px window")
    print("   - Hot Rod Red circle")
    print("   - Hexagonal helmet")
    print("   - Wandering around desktop")
    print()
    print("   If you don't see it:")
    print("   1. Check desktop corners and edges")
    print("   2. Check if window is minimized")
    print("   3. Look for red/orange circle")
    print()
    print("=" * 80)
    print("   Kenny is running - window should be visible")
    print("   Press Ctrl+C to stop")
    print("=" * 80)
    print()

    # Start main loop
    kenny.start()

except KeyboardInterrupt:
    print("\n👋 Stopping Kenny...")
    if 'kenny' in locals():
        try:
            kenny.stop()
        except:
            pass
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
