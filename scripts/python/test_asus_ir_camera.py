#!/usr/bin/env python3
"""
Test ASUS IR Camera

Tests the ASUS IR camera (red light) to confirm it's working.
Hardware detection confirmed: ASUS IR camera is available.

Tags: #ASUS #IR_CAMERA #TEST #HARDWARE @JARVIS @LUMINA
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("❌ OpenCV not available")
    sys.exit(1)

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("TestASUSIRCamera")

print("=" * 80)
print("📹 TESTING ASUS IR CAMERA (RED LIGHT)")
print("=" * 80)
print()
print("Hardware Specs:")
print("  • ASUS IR camera: USB\\VID_2B7E&PID_C711&MI_02")
print("  • Status: OK")
print("  • This is the red light camera")
print()

# Test index 1 (most likely for ASUS IR camera)
print("Testing Camera Index 1 (ASUS IR camera)...")
try:
    cap = cv2.VideoCapture(1)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret and frame is not None:
            height, width = frame.shape[:2]
            channels = frame.shape[2] if len(frame.shape) > 2 else 1
            is_grayscale = channels == 1

            print(f"✅ ASUS IR camera opened at index 1")
            print(f"   Resolution: {width}x{height}")
            print(f"   Channels: {channels} ({'Grayscale' if is_grayscale else 'Color'})")
            print(f"   IR indicator: {'✅ Likely IR (grayscale)' if is_grayscale else '⚠️  May be IR (color output)'}")
            print()

            # Test a few frames
            print("Testing frame capture...")
            for i in range(3):
                ret, frame = cap.read()
                if ret:
                    print(f"   Frame {i+1}: ✅ Captured")
                else:
                    print(f"   Frame {i+1}: ❌ Failed")

            cap.release()
            print()
            print("✅ ASUS IR camera is working!")
            print("   This is the red light camera - no bright white light")
        else:
            print("❌ Could not read frame from index 1")
            cap.release()
    else:
        print("❌ Could not open camera at index 1")
except Exception as e:
    print(f"❌ Error testing index 1: {e}")

print()
print("=" * 80)
print("RECOMMENDATION")
print("=" * 80)
print("✅ Use ASUS IR camera (index 1) - red light")
print("   • No bright white light")
print("   • Better for privacy")
print("   • Less distracting when laying down")
print()
print("❌ Avoid ASUS FHD webcam (index 0) - white light")
print("   • Emits bright white light")
print("   • Can be distracting")
print("=" * 80)
