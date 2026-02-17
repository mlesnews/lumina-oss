#!/usr/bin/env python3
"""
Start Kenny Direct - Simple Direct Start
Starts Kenny with minimal setup, ensures window is visible.

Tags: #KENNY #DIRECT_START #VISIBILITY @JARVIS @LUMINA
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
print("🚀 STARTING KENNY - DIRECT MODE")
print("=" * 80)
print()

try:
    from kenny_imva_enhanced import KennyIMVAEnhanced

    print("✅ Creating Kenny...")
    kenny = KennyIMVAEnhanced(size=120, load_ecosystem=False)

    print(f"✅ Kenny created (size: {kenny.size}px)")
    print()
    print("   Creating window...")

    # Create window
    kenny.create_window()

    print("✅ Window created")
    print()
    print("   Window should be visible at:")
    print(f"   - Position: ({kenny.x}, {kenny.y})")
    print(f"   - Size: 120x120px")
    print()
    print("   Look for:")
    print("   - Hot Rod Red circle")
    print("   - Hexagonal helmet")
    print("   - Wandering movement")
    print()
    print("=" * 80)
    print("   Kenny is running!")
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
