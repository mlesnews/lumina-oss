#!/usr/bin/env python3
"""
Capture Problems Panel Screenshot
Captures the IDE Problems panel to see the actual problem count.

Tags: #JARVIS #IDE #SCREENSHOT #PROBLEMS @helpdesk
"""

import sys
from pathlib import Path
from datetime import datetime

try:
    from PIL import ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

project_root = Path(__file__).parent.parent.parent
output_dir = project_root / "data" / "ide_problems" / "screenshots"
output_dir.mkdir(parents=True, exist_ok=True)

def capture_screen():
    """Capture current screen"""
    if not PIL_AVAILABLE:
        print("❌ PIL/Pillow not available - cannot capture screenshot")
        print("   Install: pip install Pillow")
        return None

    try:
        # Capture full screen
        screenshot = ImageGrab.grab()

        # Save with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f"problems_panel_{timestamp}.png"
        screenshot.save(output_file)

        print(f"✅ Screenshot captured: {output_file}")
        print(f"   Size: {screenshot.size[0]}x{screenshot.size[1]} pixels")
        print("")
        print("📋 Please ensure the Problems panel is visible in the screenshot")
        print("   The screenshot shows the current desktop state")

        return output_file
    except Exception as e:
        print(f"❌ Failed to capture screenshot: {e}")
        return None

if __name__ == "__main__":
    capture_screen()
