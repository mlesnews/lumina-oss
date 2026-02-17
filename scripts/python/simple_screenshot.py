#!/usr/bin/env python3
"""
Simple Screenshot Capture
Captures a screenshot using MANUS RDP and saves it locally.
"""

import sys
from pathlib import Path
import logging
logger = logging.getLogger("simple_screenshot")


script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from manus_rdp_screenshot_capture import MANUSRDPScreenshotCapture
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def main():
    try:
        print("📸 Capturing desktop view...")
        capture = MANUSRDPScreenshotCapture()
        screenshot_path = capture.capture_screenshot(filename="kenny_visibility_check.png")

        if screenshot_path and screenshot_path.exists():
            print(f"✅ Screenshot saved: {screenshot_path}")
        else:
            print("❌ Failed to capture screenshot")

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()