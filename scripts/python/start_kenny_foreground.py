#!/usr/bin/env python3
"""
Start Kenny in FOREGROUND - Window MUST be visible
Run this directly in terminal (not background) to see Kenny
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
print("🐢 STARTING KENNY - FOREGROUND MODE")
print("=" * 80)
print("⚠️  IMPORTANT: This must run in FOREGROUND to see the window!")
print("   The window will appear on your desktop")
print("   Press Ctrl+C to stop")
print("=" * 80)
print()

try:
    from kenny_imva_enhanced import KennyIMVAEnhanced

    # Detect Ace's size
    try:
        from acva_armoury_crate_integration import ACVAArmouryCrateIntegration
        ace = ACVAArmouryCrateIntegration()
        ace_info = ace.get_acva_window_info()
        if ace_info and ace_info.get('position'):
            ace_width = ace_info['position'].get('width', 60)
            ace_height = ace_info['position'].get('height', 60)
            ace_size = int((ace_width + ace_height) / 2) if ace_width > 0 and ace_height > 0 else 60
            print(f"✅ Detected Ace size: {ace_size}px")
        else:
            ace_size = 60
            print("⚠️  Ace not detected, using default size: 60px")
    except Exception as e:
        ace_size = 60
        print(f"⚠️  Could not detect Ace size: {e}, using default: 60px")

    print(f"\nCreating Kenny (size: {ace_size}px)...")
    kenny = KennyIMVAEnhanced(size=ace_size, load_ecosystem=False)
    print(f"✅ Kenny created")

    print("\nCreating window...")
    print("   Window should appear NOW on your desktop!")
    print("   Look for a window with orange Kenny sprite")
    print()

    # Start Kenny (this will create window and start mainloop)
    kenny.start()

except KeyboardInterrupt:
    print("\n✅ Kenny stopped")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
