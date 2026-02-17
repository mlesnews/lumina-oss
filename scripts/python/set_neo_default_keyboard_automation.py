#!/usr/bin/env python3
"""
Set Neo Browser as Default - Keyboard Automation

Uses keyboard shortcuts and automation to navigate Windows Settings
and set Neo browser as default browser.

Tags: #NEO_BROWSER #KEYBOARD_AUTOMATION #WINDOWS_SETTINGS #MANUS @JARVIS @LUMINA
"""

import sys
import time
import subprocess
from pathlib import Path
from typing import Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("NeoKeyboardAuto")

# Keyboard automation
# Try MANUS first (preferred)
try:
    from manus_unified_control import MANUSUnifiedControl, ControlArea
    MANUS_AVAILABLE = True
except ImportError:
    MANUS_AVAILABLE = False
    logger.debug("MANUS not available")

# Fallback to pyautogui
try:
    import pyautogui
    KEYBOARD_AVAILABLE = True
    pyautogui.PAUSE = 0.5  # Small pause between actions
    pyautogui.FAILSAFE = True  # Move mouse to corner to abort
except ImportError:
    KEYBOARD_AVAILABLE = False
    logger.warning("pyautogui not available - install: pip install pyautogui")

try:
    import keyboard
    KEYBOARD_LIB_AVAILABLE = True
except ImportError:
    KEYBOARD_LIB_AVAILABLE = False
    logger.debug("keyboard library not available (optional)")


class NeoDefaultKeyboardAutomation:
    """
    Set Neo Browser as Default using Keyboard Automation

    Navigates Windows Settings using keyboard shortcuts.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize keyboard automation"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Initialize MANUS if available
        self.manus = None
        if MANUS_AVAILABLE:
            try:
                self.manus = MANUSUnifiedControl(self.project_root)
                logger.info("   ✅ MANUS available for keyboard control")
            except Exception as e:
                logger.debug(f"   MANUS init error: {e}")

        if not KEYBOARD_AVAILABLE and not MANUS_AVAILABLE:
            logger.error("   ❌ No keyboard automation available")

        logger.info("✅ Neo Default Keyboard Automation initialized")
        logger.info("   ⌨️  Ready to automate Windows Settings")

    def open_windows_settings(self):
        """Open Windows Settings"""
        logger.info("   🔧 Opening Windows Settings...")
        try:
            # Method 1: Use keyboard shortcut Win+I
            if KEYBOARD_AVAILABLE:
                pyautogui.hotkey('win', 'i')
                time.sleep(1.5)
                logger.info("   ✅ Opened Windows Settings (Win+I)")
                return True
            elif self.manus:
                # Try MANUS
                self._press_key_combination('win', 'i')
                time.sleep(1.5)
                logger.info("   ✅ Opened Windows Settings (Win+I via MANUS)")
                return True
        except Exception as e:
            logger.debug(f"   Keyboard method failed: {e}")

        try:
            # Method 2: Direct command
            subprocess.run(["start", "ms-settings:"], shell=True, timeout=2)
            time.sleep(1.5)
            logger.info("   ✅ Opened Windows Settings (direct)")
            return True
        except Exception as e2:
            logger.error(f"   ❌ Could not open Settings: {e2}")
            return False

    def _type_text(self, text: str, interval: float = 0.1):
        """Type text using MANUS or pyautogui"""
        if self.manus:
            try:
                # Try MANUS execute_operation for workstation control
                from manus_unified_control import ControlArea
                result = self.manus.execute_operation(
                    area=ControlArea.WORKSTATION_CONTROL,
                    operation="type_text",
                    parameters={"text": text, "interval": interval}
                )
                if result and result.success:
                    return True
            except Exception as e:
                logger.debug(f"   MANUS execute_operation failed: {e}")
                # Try direct methods
                try:
                    if hasattr(self.manus, 'type_text'):
                        self.manus.type_text(text)
                        return True
                    elif hasattr(self.manus, 'send_keys'):
                        self.manus.send_keys(text)
                        return True
                except Exception as e2:
                    logger.debug(f"   MANUS direct methods failed: {e2}")

        if KEYBOARD_AVAILABLE:
            pyautogui.write(text, interval=interval)
            return True

        return False

    def _press_key(self, key: str, presses: int = 1, interval: float = 0.1):
        """Press key using MANUS or pyautogui"""
        if self.manus:
            try:
                # Try MANUS execute_operation for workstation control
                from manus_unified_control import ControlArea
                for _ in range(presses):
                    result = self.manus.execute_operation(
                        area=ControlArea.WORKSTATION_CONTROL,
                        operation="press_key",
                        parameters={"key": key}
                    )
                    if result and not result.success:
                        return False
                    if presses > 1:
                        time.sleep(interval)
                return True
            except Exception as e:
                logger.debug(f"   MANUS execute_operation failed: {e}")
                # Try direct methods
                try:
                    if hasattr(self.manus, 'press_key'):
                        for _ in range(presses):
                            self.manus.press_key(key)
                            if presses > 1:
                                time.sleep(interval)
                        return True
                    elif hasattr(self.manus, 'send_key'):
                        for _ in range(presses):
                            self.manus.send_key(key)
                            if presses > 1:
                                time.sleep(interval)
                        return True
                except Exception as e2:
                    logger.debug(f"   MANUS direct methods failed: {e2}")

        if KEYBOARD_AVAILABLE:
            pyautogui.press(key, presses=presses, interval=interval)
            return True

        return False

    def _press_key_combination(self, *keys):
        """Press key combination (e.g., 'win', 'i')"""
        if KEYBOARD_AVAILABLE:
            try:
                pyautogui.hotkey(*keys)
                return True
            except Exception as e:
                logger.debug(f"   Hotkey failed: {e}")

        # Fallback: press keys sequentially
        for key in keys:
            self._press_key(key)
            time.sleep(0.1)
        return True

    def navigate_to_default_apps(self):
        """Navigate to Default Apps in Windows Settings using keyboard"""
        if not KEYBOARD_AVAILABLE and not MANUS_AVAILABLE:
            logger.error("   ❌ Keyboard automation not available")
            return False

        logger.info("   ⌨️  Navigating to Default Apps...")
        time.sleep(1.5)  # Wait for Settings to open

        try:
            # Type "default apps" to search
            self._type_text("default apps", interval=0.1)
            time.sleep(0.8)

            # Press Enter to select
            self._press_key('enter')
            time.sleep(1.5)

            logger.info("   ✅ Navigated to Default Apps")
            return True
        except Exception as e:
            logger.error(f"   ❌ Navigation error: {e}")
            return False

    def select_web_browser(self):
        """Select Web Browser option"""
        if not KEYBOARD_AVAILABLE and not MANUS_AVAILABLE:
            return False

        logger.info("   ⌨️  Selecting Web Browser...")
        time.sleep(0.8)

        try:
            # Method 1: Search for "web browser"
            self._type_text("web browser", interval=0.1)
            time.sleep(0.8)
            self._press_key('enter')
            time.sleep(1.2)

            logger.info("   ✅ Selected Web Browser")
            return True
        except Exception as e:
            logger.error(f"   ❌ Selection error: {e}")
            # Try alternative: Tab navigation
            try:
                logger.info("   ⌨️  Trying Tab navigation...")
                self._press_key('tab', presses=5, interval=0.2)
                time.sleep(0.5)
                self._press_key('enter')
                time.sleep(1)
                return True
            except Exception as e2:
                logger.error(f"   ❌ Tab navigation also failed: {e2}")
                return False

    def select_neo_browser(self):
        """Select Neo browser from the list"""
        if not KEYBOARD_AVAILABLE and not MANUS_AVAILABLE:
            return False

        logger.info("   ⌨️  Selecting Neo browser...")
        time.sleep(0.8)

        try:
            # Method 1: Type "neo" to find Neo browser
            self._type_text("neo", interval=0.1)
            time.sleep(0.8)

            # Press Enter to select
            self._press_key('enter')
            time.sleep(1)

            logger.info("   ✅ Selected Neo browser")
            return True
        except Exception as e:
            logger.error(f"   ❌ Selection error: {e}")
            # Try alternative: Arrow key navigation
            try:
                logger.info("   ⌨️  Trying Arrow key navigation...")
                # Press down arrow a few times to navigate
                self._press_key('down', presses=3, interval=0.3)
                time.sleep(0.5)
                self._press_key('enter')
                time.sleep(1)
                return True
            except Exception as e2:
                logger.error(f"   ❌ Arrow navigation also failed: {e2}")
                return False

    def set_neo_as_default_automated(self) -> bool:
        """
        Fully automated process to set Neo as default browser

        Returns:
            True if successful
        """
        logger.info("=" * 80)
        logger.info("🤖 AUTOMATED NEO BROWSER DEFAULT SETUP")
        logger.info("=" * 80)
        logger.info("   ⚠️  This will use keyboard automation")
        logger.info("   ⚠️  Please do NOT use your keyboard during this process")
        logger.info("   ⚠️  Move mouse to top-left corner to abort (if pyautogui)")
        logger.info("   ⚠️  Process will start in 5 seconds...")
        time.sleep(5)

        # Step 1: Open Windows Settings
        if not self.open_windows_settings():
            return False

        # Step 2: Navigate to Default Apps
        if not self.navigate_to_default_apps():
            logger.warning("   ⚠️  Could not navigate automatically - manual intervention may be needed")
            return False

        # Step 3: Select Web Browser
        if not self.select_web_browser():
            logger.warning("   ⚠️  Could not select Web Browser - manual intervention may be needed")
            return False

        # Step 4: Select Neo browser
        if not self.select_neo_browser():
            logger.warning("   ⚠️  Could not select Neo - manual intervention may be needed")
            return False

        logger.info("=" * 80)
        logger.info("✅ AUTOMATION COMPLETE")
        logger.info("=" * 80)
        logger.info("   Please verify that Neo browser is now selected as default")
        logger.info("   If not, you may need to manually complete the selection")

        return True

    def provide_keyboard_instructions(self):
        """Provide manual keyboard instructions"""
        instructions = """
================================================================================
⌨️  KEYBOARD SHORTCUTS TO SET NEO AS DEFAULT BROWSER
================================================================================

STEP 1: Open Windows Settings
   Press: Win + I

STEP 2: Navigate to Default Apps
   Type: "default apps"
   Press: Enter

STEP 3: Select Web Browser
   Press: Tab (multiple times until "Web browser" is highlighted)
   OR
   Type: "web browser"
   Press: Enter

STEP 4: Select Neo Browser
   Type: "neo"
   Press: Enter
   OR
   Use Arrow Keys to navigate to "Neo"
   Press: Enter

STEP 5: Verify
   Check that "Neo" is now shown as the default web browser

================================================================================
💡 TIPS:
   - Use Tab to navigate between options
   - Use Arrow Keys to navigate lists
   - Use Enter to select
   - Use Escape to go back
   - Type to search/filter options
================================================================================
"""
        print(instructions)


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Set Neo Browser as Default (Keyboard Automation)")
    parser.add_argument("--automate", action="store_true", help="Fully automated setup")
    parser.add_argument("--instructions", action="store_true", help="Show keyboard instructions")
    parser.add_argument("--open-settings", action="store_true", help="Open Windows Settings")

    args = parser.parse_args()

    automation = NeoDefaultKeyboardAutomation()

    if args.automate:
        if not KEYBOARD_AVAILABLE:
            logger.error("   ❌ pyautogui not available - cannot automate")
            logger.info("   📦 Install: pip install pyautogui")
            return

        success = automation.set_neo_as_default_automated()
        if success:
            print("✅ Automation completed")
        else:
            print("❌ Automation failed - manual intervention may be needed")

    elif args.open_settings:
        automation.open_windows_settings()
        print("✅ Windows Settings opened")
        print("   Use keyboard shortcuts to navigate:")
        print("   - Type 'default apps' and press Enter")
        print("   - Select 'Web browser'")
        print("   - Select 'Neo'")

    elif args.instructions or not any([args.automate, args.open_settings]):
        automation.provide_keyboard_instructions()

    else:
        parser.print_help()


if __name__ == "__main__":


    main()