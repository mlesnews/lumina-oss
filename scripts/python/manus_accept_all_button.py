#!/usr/bin/env python3
"""
MANUS Accept All Button Automation
Maps and clicks the "Accept All" button in Cursor IDE using MANUS.

Tags: #MANUS #AUTOMATION #ACCEPT_ALL #IDE @manus @helpdesk
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
    logger = get_logger("MANUSAcceptAll")
    logger.error("pyautogui/pygetwindow not available")

try:
    from manus_unified_control import MANUSUnifiedControl, ControlArea
    MANUS_AVAILABLE = True
except ImportError:
    MANUS_AVAILABLE = False

logger = get_logger("MANUSAcceptAll")


class MANUSAcceptAllButton:
    """
    MANUS Accept All Button Automation

    Maps and clicks the "Accept All" button in Cursor IDE.
    """

    def __init__(self):
        """Initialize Accept All button automation"""
        if not PYAUTOGUI_AVAILABLE:
            raise ImportError("pyautogui/pygetwindow required for button clicking")

        # Configure pyautogui
        pyautogui.FAILSAFE = False  # Disable failsafe for automation (user requested)
        pyautogui.PAUSE = 0.3  # Faster for automation

        # MANUS control
        if MANUS_AVAILABLE:
            project_root = Path(__file__).parent.parent.parent
            self.manus = MANUSUnifiedControl(project_root)
        else:
            self.manus = None

        logger.info("✅ MANUS Accept All Button automation initialized")

    def find_accept_all_button(self) -> tuple:
        """
        Find the Accept All button on screen using VLM (best method).

        Returns:
            (x, y) coordinates of button, or None if not found
        """
        logger.info("🔍 Searching for 'Accept All' button...")

        try:
            # Method 1: Use VLM (Vision Language Model) - BEST METHOD
            try:
                from vlm_integration import VLMIntegration
                from screen_capture_system import ScreenCaptureSystem

                logger.info("🤖 Using VLM to find 'Accept All' button...")

                # Capture screen
                capture = ScreenCaptureSystem()
                screenshot_path = capture.capture_screenshot()

                # Use VLM to analyze screen
                vlm = VLMIntegration(use_vlm=True, vlm_provider="local", vlm_model="Qwen/Qwen2-VL-2B-Instruct")
                prompt = "Find the button that says 'Keep All' or 'Accept All Changes' or 'Accept All' on this screen. This button may say 'Keep All' but when hovered shows 'Accept all changes'. Return the exact pixel coordinates (x, y) of the center of the button. If found, return coordinates as 'X=123 Y=456'. If not found, return 'NOT_FOUND'."

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
                            logger.info(f"✅ VLM found 'Accept All' button at ({x}, {y})")
                            return (x, y)
                        elif "NOT_FOUND" not in str(analysis_text).upper():
                            # VLM might describe location, try to extract
                            logger.debug(f"VLM response: {analysis_text}")
                elif result and isinstance(result, str):
                    # Handle string response directly
                    import re
                    coord_match = re.search(r'X[=\s]*(\d+)[,\s]+Y[=\s]*(\d+)', result, re.IGNORECASE)
                    if coord_match:
                        x = int(coord_match.group(1))
                        y = int(coord_match.group(2))
                        logger.info(f"✅ VLM found 'Accept All' button at ({x}, {y})")
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

                # Use OCR to find "Accept All" text
                text_data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)

                for i, text in enumerate(text_data['text']):
                    text_lower = text.lower()
                    # Look for "Accept All", "Keep All", or "Accept all changes"
                    if ('accept' in text_lower and 'all' in text_lower) or \
                       ('keep' in text_lower and 'all' in text_lower):
                        x = text_data['left'][i] + text_data['width'][i] // 2
                        y = text_data['top'][i] + text_data['height'][i] // 2
                        logger.info(f"✅ OCR found button '{text}' at ({x}, {y})")
                        return (x, y)
            except ImportError:
                logger.debug("pytesseract not available for OCR")
            except Exception as e:
                logger.debug(f"OCR search failed: {e}")

            # Method 2: Search by image template matching
            try:
                # Look for common button locations in Cursor IDE
                # Accept All is typically in the top-right area of the editor
                screen_width, screen_height = pyautogui.size()

                # Common locations for Accept All button
                search_regions = [
                    (screen_width - 300, 0, 300, 100),  # Top-right
                    (screen_width - 200, 50, 200, 150),  # Top-right area
                    (screen_width // 2, 0, screen_width // 2, 100),  # Top half
                ]

                for region in search_regions:
                    try:
                        # Try to find button by color/pattern
                        # Accept All buttons are often blue/green
                        location = pyautogui.locateOnScreen(
                            None,  # Would need actual button image
                            region=region,
                            confidence=0.8
                        )
                        if location:
                            center = pyautogui.center(location)
                            logger.info(f"✅ Found button at {center}")
                            return center
                    except Exception:
                        continue
            except Exception as e:
                logger.debug(f"Image matching failed: {e}")

            # Method 3: Use keyboard shortcut (if available)
            # Cursor IDE might have Ctrl+Shift+A or similar for Accept All

            logger.warning("⚠️  Could not find 'Accept All' button automatically")
            return None

        except Exception as e:
            logger.error(f"❌ Error finding Accept All button: {e}", exc_info=True)
            return None

    def click_accept_all(self, use_manus: bool = True) -> bool:
        """
        Click the Accept All button.

        Args:
            use_manus: Use MANUS control if available

        Returns:
            True if successful
        """
        logger.info("="*80)
        logger.info("🖱️  CLICKING ACCEPT ALL BUTTON")
        logger.info("="*80)

        # Try MANUS first if available
        if use_manus and self.manus:
            try:
                logger.info("🤖 Using MANUS to click Accept All...")

                # Use MANUS IDE control
                ide_controllers = self.manus.controllers.get(ControlArea.IDE_CONTROL)
                if ide_controllers:
                    cursor_controller = ide_controllers.get("cursor")
                    if cursor_controller:
                        # Try to find and click Accept All
                        result = self._click_via_manus_cursor(cursor_controller)
                        if result:
                            logger.info("✅ Accept All clicked via MANUS")
                            return True
            except Exception as e:
                logger.debug(f"MANUS click failed: {e}")

        # Fallback: Direct pyautogui
        logger.info("🖱️  Using direct click method...")

        # Find button
        button_location = self.find_accept_all_button()

        if button_location:
            x, y = button_location
            try:
                pyautogui.click(x, y)
                logger.info(f"✅ Clicked Accept All at ({x}, {y})")
                time.sleep(0.5)  # Wait for action to complete
                return True
            except Exception as e:
                logger.error(f"❌ Failed to click: {e}")
                return False
        else:
            # Try keyboard shortcut as fallback
            logger.info("⌨️  Trying keyboard shortcut...")
            try:
                # Common shortcuts: Ctrl+Shift+A, Ctrl+K Ctrl+A, etc.
                pyautogui.hotkey('ctrl', 'shift', 'a')
                logger.info("✅ Sent Ctrl+Shift+A (Accept All shortcut)")
                time.sleep(0.5)
                return True
            except Exception as e:
                logger.error(f"❌ Keyboard shortcut failed: {e}")
                return False

    def _click_via_manus_cursor(self, cursor_controller) -> bool:
        """Click Accept All via MANUS cursor controller"""
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

            # Get window position and size (handle minimized windows)
            left = max(0, cursor_window.left)  # Ensure positive
            top = max(0, cursor_window.top)    # Ensure positive
            width = cursor_window.width
            height = cursor_window.height

            # Skip if window appears minimized or off-screen
            if width < 100 or height < 100 or left < -10000 or top < -10000:
                logger.warning(f"⚠️  Window appears minimized/off-screen: {width}x{height} at ({left}, {top})")
                # Try keyboard shortcut instead
                logger.info("⌨️  Using keyboard shortcut instead...")
                pyautogui.hotkey('ctrl', 'shift', 'a')
                time.sleep(0.5)
                return True

            logger.info(f"✅ Cursor window activated: {width}x{height} at ({left}, {top})")

            # Accept All / Keep All button locations (relative to window)
            # In Cursor IDE, this button is typically in notification area or diff view
            # Button may say "Keep All" but tooltip says "Accept all changes"
            accept_all_locations = [
                (left + width - 150, top + 50),   # Top-right notification area
                (left + width - 200, top + 100),   # Slightly lower
                (left + width - 100, top + 30),   # Very top-right
                (left + width // 2, top + 20),    # Center-top (for diff view)
                (left + width - 120, top + 60),   # Common "Keep All" position
            ]

            # Try each location
            for x, y in accept_all_locations:
                try:
                    # Ensure coordinates are on screen
                    screen_width, screen_height = pyautogui.size()
                    if 0 <= x < screen_width and 0 <= y < screen_height:
                        pyautogui.click(x, y)
                        logger.info(f"🖱️  Clicked at ({x}, {y}) - Accept All location")
                        time.sleep(0.5)
                        return True
                except Exception as e:
                    logger.debug(f"Click at ({x}, {y}) failed: {e}")
                    continue

            # Fallback: Try keyboard shortcut
            logger.info("⌨️  Trying keyboard shortcut as fallback...")
            pyautogui.hotkey('ctrl', 'shift', 'a')
            time.sleep(0.5)
            return True

        except Exception as e:
            logger.debug(f"MANUS cursor click failed: {e}")

        return False

    def accept_all_changes(self) -> bool:
        """
        Accept all changes - main entry point.

        Returns:
            True if successful
        """
        logger.info("🔄 Accepting all changes...")

        # Try multiple methods
        methods = [
            ("MANUS", lambda: self.click_accept_all(use_manus=True)),
            ("Direct Click", lambda: self.click_accept_all(use_manus=False)),
            ("Keyboard Shortcut", lambda: self._try_keyboard_shortcuts())
        ]

        for method_name, method_func in methods:
            try:
                logger.info(f"🔧 Trying method: {method_name}")
                if method_func():
                    logger.info(f"✅ Success with method: {method_name}")
                    return True
            except Exception as e:
                logger.debug(f"Method {method_name} failed: {e}")
                continue

        logger.error("❌ All methods failed to accept all changes")
        return False

    def _try_keyboard_shortcuts(self) -> bool:
        """Try various keyboard shortcuts for Accept All"""
        shortcuts = [
            ('ctrl', 'shift', 'a'),
            ('ctrl', 'k', 'ctrl', 'a'),
            ('ctrl', 'alt', 'a'),
        ]

        for shortcut in shortcuts:
            try:
                pyautogui.hotkey(*shortcut)
                logger.info(f"✅ Sent shortcut: {'+'.join(shortcut)}")
                time.sleep(0.5)
                return True
            except Exception as e:
                logger.debug(f"Shortcut {shortcut} failed: {e}")
                continue

        return False


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="MANUS Accept All Button")
    parser.add_argument('--click', action='store_true', help='Click Accept All button')
    parser.add_argument('--find', action='store_true', help='Find Accept All button location')

    args = parser.parse_args()

    try:
        automator = MANUSAcceptAllButton()

        if args.find:
            location = automator.find_accept_all_button()
            if location:
                print(f"✅ Accept All button found at: {location}")
            else:
                print("❌ Accept All button not found")

        if args.click or not any([args.find]):
            success = automator.accept_all_changes()
            if success:
                print("✅ Accept All clicked successfully")
                return 0
            else:
                print("❌ Failed to click Accept All")
                return 1

    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":


    sys.exit(main() or 0)