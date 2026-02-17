#!/usr/bin/env python3
"""
MANUS People Button Automation - REQUIRED

Finds and clicks the "People" button in Cursor IDE.
User shouldn't have to click this manually.

Tags: #MANUS #PEOPLE_BUTTON #AUTOMATION #REQUIRED @JARVIS @LUMINA
"""

import sys
import time
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

try:
    import pyautogui
    import pygetwindow as gw
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

logger = get_logger("MANUSPeopleButton")


class MANUSPeopleButton:
    """Finds and clicks the People button in Cursor IDE"""

    def __init__(self):
        if not PYAUTOGUI_AVAILABLE:
            raise ImportError("pyautogui required")

        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.2

        logger.info("✅ MANUS People Button automation initialized")

    def find_people_button(self):
        """Find People button using VLM or common positions"""
        logger.info("🔍 Searching for People button...")

        try:
            # Try VLM first
            from vlm_integration import VLMIntegration
            from screen_capture_system import ScreenCaptureSystem

            capture = ScreenCaptureSystem()
            screenshot_path = capture.capture_screenshot()

            vlm = VLMIntegration()
            prompt = "Find the 'People' button in Cursor IDE. This button may be in a sidebar or toolbar. Return the exact pixel coordinates (x, y) of the center of the button. If found, return coordinates as 'X=123 Y=456'. If not found, return 'NOT_FOUND'."

            result = vlm.analyze_image(str(screenshot_path), prompt)

            # Parse result
            import re
            if isinstance(result, dict):
                text = result.get('analysis', result.get('text', str(result)))
            else:
                text = str(result)

            coord_match = re.search(r'X[=\s]*(\d+)[,\s]+Y[=\s]*(\d+)', text, re.IGNORECASE)
            if coord_match:
                x = int(coord_match.group(1))
                y = int(coord_match.group(2))
                logger.info(f"✅ Found People button at ({x}, {y})")
                return (x, y)
        except Exception as e:
            logger.debug(f"VLM search failed: {e}")

        # Fallback: Try common positions (usually in left sidebar)
        try:
            cursor_windows = gw.getWindowsWithTitle("Cursor")
            if cursor_windows:
                window = cursor_windows[0]
                # Common People button position (left sidebar, near top)
                people_x = window.left + 50  # Left sidebar
                people_y = window.top + 150  # Below top menu
                logger.info(f"📍 Trying common People position: ({people_x}, {people_y})")
                return (people_x, people_y)
        except Exception as e:
            logger.debug(f"Fallback search failed: {e}")

        return None

    def click_people(self):
        """Click the People button"""
        coords = self.find_people_button()
        if not coords:
            logger.warning("⚠️  People button not found")
            return False

        x, y = coords
        logger.info(f"🖱️  Clicking People button at ({x}, {y})")
        pyautogui.click(x, y)
        time.sleep(0.3)
        logger.info("✅ People button clicked")
        return True


if __name__ == "__main__":
    button = MANUSPeopleButton()
    if button.click_people():
        print("✅ People button clicked")
    else:
        print("❌ Could not click People button")
