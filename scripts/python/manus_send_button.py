#!/usr/bin/env python3
"""
MANUS Send Button Automation - REQUIRED

Actually clicks the Send button in Cursor IDE chat.
Fixes the issue where user still has to click Send manually.

Tags: #MANUS #AUTOMATION #SEND_BUTTON #REQUIRED @JARVIS @LUMINA
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

try:
    from vlm_integration import VLMIntegration
    from screen_capture_system import ScreenCaptureSystem
    VLM_AVAILABLE = True
except ImportError:
    VLM_AVAILABLE = False

logger = get_logger("MANUSSendButton")


class MANUSSendButton:
    """Finds and clicks the Send button in Cursor IDE"""

    def __init__(self):
        if not PYAUTOGUI_AVAILABLE:
            raise ImportError("pyautogui required")

        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.2

        logger.info("✅ MANUS Send Button automation initialized")

    def find_send_button(self):
        """Find Send button using VLM"""
        logger.info("🔍 Searching for Send button...")

        if VLM_AVAILABLE:
            try:
                capture = ScreenCaptureSystem()
                screenshot_path = capture.capture_screenshot()

                vlm = VLMIntegration()
                prompt = "Find the Send button in Cursor IDE chat interface. This button sends messages. It may have a send icon (arrow/paper plane) or say 'Send'. Return the exact pixel coordinates (x, y) of the center of the button. If found, return coordinates as 'X=123 Y=456'. If not found, return 'NOT_FOUND'."

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
                    logger.info(f"✅ Found Send button at ({x}, {y})")
                    return (x, y)
            except Exception as e:
                logger.warning(f"VLM search failed: {e}")

        # Fallback: Try common positions
        try:
            cursor_windows = gw.getWindowsWithTitle("Cursor")
            if cursor_windows:
                window = cursor_windows[0]
                # Common Send button positions (bottom-right of chat)
                send_x = window.left + window.width - 100
                send_y = window.top + window.height - 50
                logger.info(f"📍 Trying common Send position: ({send_x}, {send_y})")
                return (send_x, send_y)
        except Exception as e:
            logger.warning(f"Fallback search failed: {e}")

        return None

    def click_send(self):
        """Click the Send button"""
        coords = self.find_send_button()
        if not coords:
            logger.warning("⚠️  Send button not found")
            return False

        x, y = coords
        logger.info(f"🖱️  Clicking Send button at ({x}, {y})")
        pyautogui.click(x, y)
        time.sleep(0.3)
        logger.info("✅ Send button clicked")
        return True


def auto_send_after_transcription():
    """Auto-send after transcription - actually clicks Send button"""
    sender = MANUSSendButton()
    return sender.click_send()


if __name__ == "__main__":
    sender = MANUSSendButton()
    if sender.click_send():
        print("✅ Send button clicked")
    else:
        print("❌ Could not click Send button")
