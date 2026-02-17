#!/usr/bin/env python3
"""
Microsoft Copilot Button → @JARVIS Remap
Hack the Copilot button to trigger JARVIS instead

Tags: #KEYBOARD #REMAP #COPILOT #JARVIS #HACK @JARVIS @LUMINA
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
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CopilotToJarvisRemap")

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    logger.error("❌ keyboard library not available - install: pip install keyboard")

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    logger.error("❌ pyautogui not available")


class CopilotToJarvisRemap:
    """
    Microsoft Copilot Button → @JARVIS Remap

    Hacks the Copilot button to trigger @JARVIS instead
    """

    def __init__(self):
        """Initialize Copilot to JARVIS remapping"""
        if not KEYBOARD_AVAILABLE:
            raise ImportError("keyboard library required")

        self.running = False
        self.hook_installed = False
        self.jarvis_text = "@JARVIS"

        # Prevent multiple triggers
        self.last_trigger_time = 0
        self.trigger_cooldown = 0.5  # 500ms cooldown

        logger.info("✅ Copilot → @JARVIS remapping initialized")

    def _on_copilot_press(self, event=None):
        """Handle Copilot button press"""
        try:
            current_time = time.time()

            # Cooldown check
            if current_time - self.last_trigger_time < self.trigger_cooldown:
                return

            self.last_trigger_time = current_time

            logger.info("⌨️  Copilot button pressed - typing '@JARVIS' + Enter")

            # Type @JARVIS + Enter
            if PYAUTOGUI_AVAILABLE:
                pyautogui.write(self.jarvis_text, interval=0.05)
                time.sleep(0.1)
                pyautogui.press('enter')
                logger.info(f"✅ Typed '{self.jarvis_text}' + Enter")
            else:
                keyboard.write(self.jarvis_text)
                time.sleep(0.1)
                keyboard.press_and_release('enter')
                logger.info(f"✅ Typed '{self.jarvis_text}' + Enter")
        except Exception as e:
            logger.error(f"❌ Error handling Copilot press: {e}")

    def _on_key_event(self, event):
        """Handle keyboard events - detect Copilot button"""
        try:
            # Check for Copilot button
            # Common scan codes: 0xE0 0x5D (Launch App 1), F23, etc.
            is_copilot = False

            if hasattr(event, 'scan_code'):
                # Launch App 1 scan code (common for Copilot)
                if event.scan_code == 0x5D or event.scan_code == 93:
                    is_copilot = True

            if hasattr(event, 'name'):
                # Check for Copilot-related key names
                copilot_names = ['launch app1', 'launch_app1', 'f23', 'right windows', 'rwin']
                if event.name.lower() in copilot_names:
                    is_copilot = True

            # Check for Right Windows + C (Copilot shortcut)
            if hasattr(event, 'name') and event.name == 'c':
                # Check if Right Windows is held
                if keyboard.is_pressed('right windows'):
                    is_copilot = True

            if is_copilot:
                if hasattr(event, 'event_type'):
                    if event.event_type == keyboard.KEY_DOWN:
                        self._on_copilot_press(event)
                else:
                    self._on_copilot_press(event)
        except Exception as e:
            logger.debug(f"Key event error: {e}")

    def start(self):
        """Start Copilot to JARVIS remapping"""
        if self.running:
            return

        if not KEYBOARD_AVAILABLE:
            logger.error("❌ keyboard library not available")
            return False

        try:
            # Hook multiple possible Copilot button mappings

            # Method 1: Launch App 1
            try:
                keyboard.on_press_key('launch app1', self._on_copilot_press, suppress=False)
                logger.info("✅ Copilot hook installed (Launch App 1)")
            except:
                pass

            # Method 2: F23
            try:
                keyboard.on_press_key('f23', self._on_copilot_press, suppress=False)
                logger.info("✅ Copilot hook installed (F23)")
            except:
                pass

            # Method 3: Right Windows + C
            try:
                keyboard.add_hotkey('right windows+c', self._on_copilot_press, suppress=False)
                logger.info("✅ Copilot hook installed (Right Windows + C)")
            except:
                pass

            # Method 4: Global hook to catch all keys
            try:
                keyboard.hook(self._on_key_event)
                logger.info("✅ Copilot hook installed (global hook)")
            except Exception as e:
                logger.debug(f"Global hook error: {e}")

            self.running = True
            self.hook_installed = True

            logger.info("=" * 80)
            logger.info("⌨️  COPILOT → @JARVIS REMAPPING ACTIVE")
            logger.info("=" * 80)
            logger.info("   Press Copilot button to type '@JARVIS' + Enter")
            logger.info("=" * 80)

            return True
        except Exception as e:
            logger.error(f"❌ Failed to start Copilot remapping: {e}")
            return False

    def stop(self):
        """Stop Copilot remapping"""
        if not self.running:
            return

        try:
            keyboard.unhook_all()
            self.running = False
            self.hook_installed = False
            logger.info("🛑 Copilot remapping stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping remapping: {e}")


def main():
    """Main entry point"""
    print("=" * 80)
    print("⌨️  COPILOT → @JARVIS REMAPPING")
    print("=" * 80)
    print()
    print("This will remap Microsoft Copilot button to type '@JARVIS' + Enter")
    print("Press Ctrl+C to stop")
    print()
    print("=" * 80)
    print()

    if not KEYBOARD_AVAILABLE:
        print("❌ keyboard library not available")
        print("   Install: pip install keyboard")
        return 1

    try:
        remap = CopilotToJarvisRemap()
        if remap.start():
            print("✅ Copilot → @JARVIS remapping active")
            print("   Press Copilot button to type '@JARVIS' + Enter")
            print()

            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 Stopping...")
                remap.stop()
                print("✅ Stopped")
        else:
            print("❌ Failed to start remapping")
            return 1
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":


    sys.exit(main() or 0)