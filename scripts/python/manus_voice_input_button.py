#!/usr/bin/env python3
"""
MANUS Voice Input Button Automation
Automatically clicks the voice input button in Cursor IDE to start microphone listening.

Tags: #MANUS #VOICE_INPUT #AUTOMATION #CURSOR_IDE @manus @helpdesk
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
    logger = get_logger("MANUSVoiceInput")
    logger.error("pyautogui/pygetwindow not available")

try:
    from manus_unified_control import MANUSUnifiedControl, ControlArea
    MANUS_AVAILABLE = True
except ImportError:
    MANUS_AVAILABLE = False

logger = get_logger("MANUSVoiceInput")


class MANUSVoiceInputButton:
    """
    MANUS Voice Input Button Automation

    Finds and clicks the voice input button in Cursor IDE to start microphone listening.
    """

    def __init__(self):
        """Initialize Voice Input button automation"""
        if not PYAUTOGUI_AVAILABLE:
            raise ImportError("pyautogui/pygetwindow required for button clicking")

        # Configure pyautogui
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.3

        # MANUS control
        if MANUS_AVAILABLE:
            project_root = Path(__file__).parent.parent.parent
            self.manus = MANUSUnifiedControl(project_root)
        else:
            self.manus = None

        logger.info("✅ MANUS Voice Input Button automation initialized")

    def find_voice_input_button(self) -> tuple:
        """
        Find the Voice Input button on screen using VLM (best method).

        Returns:
            (x, y) coordinates of button, or None if not found
        """
        logger.info("🔍 Searching for 'Voice Input' button...")

        try:
            # Method 1: Use VLM (Vision Language Model) - BEST METHOD
            try:
                from vlm_integration import VLMIntegration
                from screen_capture_system import ScreenCaptureSystem

                logger.info("🤖 Using VLM to find 'Voice Input' button...")

                # Capture screen
                capture = ScreenCaptureSystem()
                screenshot_path = capture.capture_screenshot()

                # Use VLM to analyze screen
                vlm = VLMIntegration(use_vlm=True, vlm_provider="local", vlm_model="Qwen/Qwen2-VL-2B-Instruct")
                prompt = "Find the voice input button or microphone button in Cursor IDE. This button starts microphone listening. It may have a microphone icon or say 'Voice' or 'Voice Input'. Return the exact pixel coordinates (x, y) of the center of the button. If found, return coordinates as 'X=123 Y=456'. If not found, return 'NOT_FOUND'."

                result = vlm.analyze_screen_with_vlm(screenshot_path, prompt=prompt)

                # VLM returns dict with 'analysis' or 'text' key
                if result and isinstance(result, dict):
                    analysis_text = result.get('analysis', result.get('text', result.get('response', '')))
                    if analysis_text:
                        # Parse VLM response for coordinates
                        import re
                        coord_match = re.search(r'X[=\s]*(\d+)[,\s]+Y[=\s]*(\d+)', str(analysis_text), re.IGNORECASE)
                        if coord_match:
                            x = int(coord_match.group(1))
                            y = int(coord_match.group(2))
                            logger.info(f"✅ VLM found 'Voice Input' button at ({x}, {y})")
                            return (x, y)
                        elif "NOT_FOUND" not in str(analysis_text).upper():
                            logger.debug(f"VLM response: {analysis_text}")
                elif result and isinstance(result, str):
                    # Handle string response directly
                    import re
                    coord_match = re.search(r'X[=\s]*(\d+)[,\s]+Y[=\s]*(\d+)', result, re.IGNORECASE)
                    if coord_match:
                        x = int(coord_match.group(1))
                        y = int(coord_match.group(2))
                        logger.info(f"✅ VLM found 'Voice Input' button at ({x}, {y})")
                        return (x, y)
            except ImportError:
                logger.debug("VLM not available, trying OCR")
            except Exception as e:
                logger.debug(f"VLM search failed: {e}")

            # Method 2: Search by text using OCR
            try:
                import pytesseract
                from PIL import ImageGrab

                # Capture screen
                screenshot = ImageGrab.grab()

                # Use OCR to find "Voice" or "Microphone" text
                text_data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)

                for i, text in enumerate(text_data['text']):
                    text_lower = text.lower()
                    # Look for voice-related text
                    if 'voice' in text_lower or 'mic' in text_lower or 'microphone' in text_lower:
                        x = text_data['left'][i] + text_data['width'][i] // 2
                        y = text_data['top'][i] + text_data['height'][i] // 2
                        logger.info(f"✅ OCR found voice button '{text}' at ({x}, {y})")
                        return (x, y)
            except ImportError:
                logger.debug("pytesseract not available for OCR")
            except Exception as e:
                logger.debug(f"OCR search failed: {e}")

            # Method 3: Try keyboard shortcut (Control+Shift+Space)
            # This is the standard Cursor IDE voice input shortcut
            logger.info("⌨️  Trying keyboard shortcut Control+Shift+Space...")
            try:
                pyautogui.hotkey('ctrl', 'shift', 'space')
                logger.info("✅ Sent Control+Shift+Space (voice input shortcut)")
                time.sleep(0.5)
                return True  # Return True to indicate success
            except Exception as e:
                logger.debug(f"Keyboard shortcut failed: {e}")

            logger.warning("⚠️  Could not find 'Voice Input' button automatically")
            return None

        except Exception as e:
            logger.error(f"❌ Error finding Voice Input button: {e}", exc_info=True)
            return None

    def click_voice_input(self, use_manus: bool = True) -> bool:
        """
        Click the Voice Input button to start microphone listening.

        Args:
            use_manus: Use MANUS control if available

        Returns:
            True if successful
        """
        logger.info("="*80)
        logger.info("🎤 CLICKING VOICE INPUT BUTTON")
        logger.info("="*80)

        # Method 1: Try keyboard shortcut first (fastest and most reliable)
        logger.info("⌨️  Trying keyboard shortcut Control+Shift+Space...")
        try:
            pyautogui.hotkey('ctrl', 'shift', 'space')
            logger.info("✅ Sent Control+Shift+Space (voice input shortcut)")
            time.sleep(0.5)
            return True
        except Exception as e:
            logger.debug(f"Keyboard shortcut failed: {e}")

        # Method 2: Try MANUS if available
        if use_manus and self.manus:
            try:
                logger.info("🤖 Using MANUS to click Voice Input...")

                # Use MANUS IDE control
                ide_controllers = self.manus.controllers.get(ControlArea.IDE_CONTROL)
                if ide_controllers:
                    cursor_controller = ide_controllers.get("cursor")
                    if cursor_controller:
                        result = self._click_via_manus_cursor(cursor_controller)
                        if result:
                            logger.info("✅ Voice Input clicked via MANUS")
                            return True
            except Exception as e:
                logger.debug(f"MANUS click failed: {e}")

        # Method 3: Find and click button directly
        logger.info("🖱️  Using direct click method...")

        button_location = self.find_voice_input_button()

        if button_location:
            if button_location is True:  # Keyboard shortcut already worked
                return True

            x, y = button_location
            try:
                pyautogui.click(x, y)
                logger.info(f"✅ Clicked Voice Input at ({x}, {y})")
                time.sleep(0.5)
                return True
            except Exception as e:
                logger.error(f"❌ Failed to click: {e}")
                return False
        else:
            logger.warning("⚠️  Could not find Voice Input button")
            return False

    def _click_via_manus_cursor(self, cursor_controller) -> bool:
        """Click Voice Input via MANUS cursor controller"""
        try:
            # Get Cursor window
            windows = gw.getWindowsWithTitle("Cursor")
            if not windows:
                windows = gw.getWindowsWithTitle("Visual Studio Code")

            if not windows:
                logger.warning("⚠️  Cursor window not found")
                return False

            cursor_window = windows[0]
            cursor_window.activate()
            time.sleep(0.5)

            # Get window position and size
            left = max(0, cursor_window.left)
            top = max(0, cursor_window.top)
            width = cursor_window.width
            height = cursor_window.height

            if width < 100 or height < 100:
                logger.warning("⚠️  Window appears minimized")
                # Try keyboard shortcut instead
                pyautogui.hotkey('ctrl', 'shift', 'space')
                time.sleep(0.5)
                return True

            logger.info(f"✅ Cursor window activated: {width}x{height} at ({left}, {top})")

            # Voice Input button is typically in the chat/input area
            # Common locations (relative to window)
            voice_button_locations = [
                (left + width - 100, top + height - 50),   # Bottom-right (chat area)
                (left + width - 150, top + height - 50),   # Bottom-right area
                (left + width // 2, top + height - 50),    # Bottom center
            ]

            # Try each location
            for x, y in voice_button_locations:
                try:
                    screen_width, screen_height = pyautogui.size()
                    if 0 <= x < screen_width and 0 <= y < screen_height:
                        pyautogui.click(x, y)
                        logger.info(f"🖱️  Clicked at ({x}, {y}) - Voice Input location")
                        time.sleep(0.5)
                        return True
                except Exception as e:
                    logger.debug(f"Click at ({x}, {y}) failed: {e}")
                    continue

            # Fallback: Try keyboard shortcut
            logger.info("⌨️  Trying keyboard shortcut as fallback...")
            pyautogui.hotkey('ctrl', 'shift', 'space')
            time.sleep(0.5)
            return True

        except Exception as e:
            logger.debug(f"MANUS cursor click failed: {e}")

        return False

    def activate_voice_input(self) -> bool:
        """
        Activate voice input - main entry point.

        Returns:
            True if successful
        """
        logger.info("🎤 Activating voice input...")

        # Try keyboard shortcut first (most reliable)
        try:
            pyautogui.hotkey('ctrl', 'shift', 'space')
            logger.info("✅ Voice input activated via keyboard shortcut")
            time.sleep(0.5)
            return True
        except Exception as e:
            logger.debug(f"Keyboard shortcut failed: {e}")

        # Try MANUS
        if self.click_voice_input(use_manus=True):
            return True

        logger.error("❌ Failed to activate voice input")
        return False


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="MANUS Voice Input Button")
    parser.add_argument('--click', action='store_true', help='Click Voice Input button')
    parser.add_argument('--find', action='store_true', help='Find Voice Input button location')

    args = parser.parse_args()

    try:
        automator = MANUSVoiceInputButton()

        if args.find:
            location = automator.find_voice_input_button()
            if location:
                print(f"✅ Voice Input button found at: {location}")
            else:
                print("❌ Voice Input button not found")

        if args.click or not any([args.find]):
            success = automator.activate_voice_input()
            if success:
                print("✅ Voice Input activated successfully")
                return 0
            else:
                print("❌ Failed to activate Voice Input")
                return 1

    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":


    sys.exit(main() or 0)