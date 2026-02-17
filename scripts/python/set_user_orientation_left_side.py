#!/usr/bin/env python3
"""
Set User Orientation - Laying on Left Side

Sets the camera orientation handler to account for user laying on their left side.
When user is on left side, images need to be rotated 90° clockwise.

Tags: #CAMERA #ORIENTATION #USER_POSITION @JARVIS @LUMINA
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from camera_orientation_handler import get_camera_orientation_handler
    from lumina_logger import get_logger
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("SetUserOrientation")

print("=" * 80)
print("📹 SETTING USER ORIENTATION - LAYING ON LEFT SIDE")
print("=" * 80)
print()
print("User Position: Laying on left side")
print("Image Rotation: 90° clockwise (from camera's perspective)")
print("From user's perspective: Rotated to the left")
print()

handler = get_camera_orientation_handler()
handler.set_user_lying_left_side()

print("✅ Orientation set for user laying on left side")
print()
print("💡 All camera captures will now be rotated automatically")
print("   This ensures images appear correctly oriented")
print()
print("⚠️  Note: Regular camera is currently active (emits bright light)")
print("   IR camera is preferred to avoid bright light when laying down")
print()
print("=" * 80)
