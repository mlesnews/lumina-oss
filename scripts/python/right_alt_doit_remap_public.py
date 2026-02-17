#!/usr/bin/env python3
"""
Right Alt Key Remapping to @DOIT - PUBLIC VERSION
🟢 PUBLIC: GitHub Open-Source (v2.0)

Remaps the Right Alt key to automatically type "@DOIT" + Enter when pressed.
This enables quick execution trigger without typing.

This is a public version suitable for GitHub Open-Source release.
Removed internal references and dependencies.

Tags: #KEYBOARD #REMAP #RIGHT_ALT #DOIT #PUBLIC #OPEN_SOURCE
"""

import sys
import time
from pathlib import Path

# Public version - minimal dependencies
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("❌ keyboard library not available - install: pip install keyboard")

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    print("❌ pyautogui not available - install: pip install pyautogui")


class RightAltDoitRemap:
    """
    Right Alt Key Remapping to @DOIT - PUBLIC VERSION

    When Right Alt is pressed, automatically types "@DOIT" + Enter
    """

    def __init__(self, doit_text="@DOIT"):
        """Initialize Right Alt remapping"""
        if not KEYBOARD_AVAILABLE:
            raise ImportError("keyboard library required - install: pip install keyboard")

        self.running = False
        self.hook_installed = False
        self.doit_text = doit_text

        # Prevent multiple triggers
        self.last_trigger_time = 0
        self.trigger_cooldown = 0.5  # 500ms cooldown

        print("✅ Right Alt → @DOIT + Enter remapping initialized")

    def _on_right_alt_press(self, event=None):
        """Handle Right Alt key press"""
        try:
            # If event provided, check if it's Right Alt
            if event:
                # Check if it's Right Alt (not Left Alt)
                # Check for both scan codes (54 and 56) as different systems use different codes
                is_right_alt = (
                    (hasattr(event, 'name') and event.name == 'right alt') or
                    (hasattr(event, 'scan_code') and event.scan_code in [54, 56]) or
                    (hasattr(event, 'name') and event.name in ['right menu', 'alt gr', 'altgr'])
                )
                if not is_right_alt:
                    return  # Not Right Alt, ignore

            current_time = time.time()

            # Cooldown check
            if current_time - self.last_trigger_time < self.trigger_cooldown:
                return

            self.last_trigger_time = current_time

            print("⌨️  Right Alt pressed - typing '@DOIT' + Enter")

            # Type @DOIT + Enter (Return/Send button)
            # CRITICAL: Use raw string to avoid double backslash issues
            doit_text_to_type = self.doit_text  # "@DOIT" - no escaping needed

            if PYAUTOGUI_AVAILABLE:
                # Use pyautogui to type (more reliable)
                pyautogui.write(doit_text_to_type, interval=0.05)
                time.sleep(0.1)  # Small delay before Enter
                pyautogui.press('enter')
                print(f"✅ Typed '{doit_text_to_type}' + Enter")
            else:
                # Fallback: use keyboard library
                # CRITICAL: Use write() which handles special characters correctly
                keyboard.write(doit_text_to_type)
                time.sleep(0.1)  # Small delay before Enter
                keyboard.press_and_release('enter')
                print(f"✅ Typed '{doit_text_to_type}' + Enter")
        except Exception as e:
            print(f"❌ Error handling Right Alt press: {e}")

    def start(self):
        """Start Right Alt remapping"""
        if self.running:
            return

        if not KEYBOARD_AVAILABLE:
            print("❌ keyboard library not available")
            return False

        try:
            # Hook Right Alt key - try multiple methods for compatibility
            # Method 1: Hook by key name
            try:
                keyboard.on_press_key('right alt', self._on_right_alt_press, suppress=False)
                print("✅ Right Alt hook installed (by name)")
            except Exception as e:
                pass

            # Method 2: Hook all keys and filter (more reliable)
            try:
                keyboard.hook(self._on_key_event)
                print("✅ Right Alt hook installed (global hook)")
            except Exception as e:
                pass

            # Method 3: Try alternative key names
            try:
                alt_names = ['right menu', 'alt gr', 'altgr']
                for alt_name in alt_names:
                    try:
                        keyboard.on_press_key(alt_name, self._on_right_alt_press, suppress=False)
                        print(f"✅ Right Alt hook installed (as '{alt_name}')")
                        break
                    except:
                        continue
            except:
                pass

            self.running = True
            self.hook_installed = True

            print("=" * 80)
            print("⌨️  RIGHT ALT → @DOIT + ENTER REMAPPING ACTIVE")
            print("=" * 80)
            print("   Press Right Alt to automatically type '@DOIT' + Enter (Return/Send)")
            print("=" * 80)

            return True
        except Exception as e:
            print(f"❌ Failed to start Right Alt remapping: {e}")
            return False

    def _on_key_event(self, event):
        """Handle keyboard events (alternative method)"""
        try:
            # Check for Right Alt (scan code 54 or by name)
            is_right_alt = False

            if hasattr(event, 'scan_code'):
                is_right_alt = (event.scan_code in [54, 56])  # Right Alt scan codes (54 or 56)

            if hasattr(event, 'name'):
                is_right_alt = is_right_alt or (event.name in ['right alt', 'right menu', 'alt gr', 'altgr'])

            if is_right_alt:
                # Check if it's a key down event
                if hasattr(event, 'event_type'):
                    if event.event_type == keyboard.KEY_DOWN:
                        self._on_right_alt_press(event)
                elif hasattr(event, 'event_type') and event.event_type == 'down':
                    self._on_right_alt_press(event)
                else:
                    # Assume it's a key press
                    self._on_right_alt_press(event)
        except Exception as e:
            pass

    def stop(self):
        """Stop Right Alt remapping"""
        if not self.running:
            return

        try:
            keyboard.unhook_all()
            self.running = False
            self.hook_installed = False
            print("🛑 Right Alt remapping stopped")
        except Exception as e:
            print(f"❌ Error stopping remapping: {e}")


def main():
    """Main entry point"""
    print("=" * 80)
    print("⌨️  RIGHT ALT → @DOIT + ENTER REMAPPING")
    print("🟢 PUBLIC VERSION - GitHub Open-Source (v2.0)")
    print("=" * 80)
    print()
    print("This will remap Right Alt key to automatically type '@DOIT' + Enter")
    print("(Acts as Return/Send button)")
    print("Press Ctrl+C to stop")
    print()
    print("=" * 80)
    print()

    if not KEYBOARD_AVAILABLE:
        print("❌ keyboard library not available")
        print("   Install: pip install keyboard")
        return 1

    try:
        remap = RightAltDoitRemap()
        if remap.start():
            print("✅ Right Alt remapping active")
            print("   Press Right Alt to type '@DOIT' + Enter (Return/Send)")
            print()

            # Keep running
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
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":


    sys.exit(main() or 0)