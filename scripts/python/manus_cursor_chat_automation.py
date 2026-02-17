#!/usr/bin/env python3
"""
MANUS Cursor IDE Chat Automation

Automates sending messages to Cursor IDE chat using MANUS control.
Eliminates need to manually click "Send" button.
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    import pyautogui
    import keyboard
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    pyautogui = None
    keyboard = None

logger = get_logger("MANUSCursorChat")


class MANUSCursorChatAutomation:
    """
    MANUS control for Cursor IDE chat automation

    Automates sending messages to Cursor IDE chat
    """

    def __init__(self, project_root: Path, auto_capture_screenshots: bool = True):
        self.project_root = project_root
        self.logger = logger
        self.auto_capture_screenshots = auto_capture_screenshots

        # Initialize screenshot integration
        self.screenshot_integration = None
        if auto_capture_screenshots:
            try:
                from cursor_chat_screenshot_integration import CursorChatScreenshotIntegration
                self.screenshot_integration = CursorChatScreenshotIntegration(auto_capture=True)
                self.logger.info("✅ Screenshot capture integration enabled")
            except ImportError:
                self.logger.warning("Screenshot integration not available")

        if not PYAUTOGUI_AVAILABLE:
            self.logger.warning("⚠️ pyautogui/keyboard not available - install: pip install pyautogui keyboard")

    def send_chat_message(self, message: str, use_shortcut: bool = True, auto_capture: bool = True) -> Dict[str, Any]:
        """
        Send a message to Cursor IDE chat with automatic screenshot capture on errors

        Args:
            message: Message to send
            use_shortcut: Use keyboard shortcut (Ctrl+Enter) instead of clicking
            auto_capture: Automatically capture screenshot if error detected
        """
        if not PYAUTOGUI_AVAILABLE:
            return {
                'success': False,
                'error': 'pyautogui/keyboard not available'
            }

        self.logger.info(f"📤 Sending chat message via MANUS: {message[:50]}...")

        # Check if screenshot should be captured (before sending)
        screenshot_path = None
        if auto_capture and self.screenshot_integration:
            analysis = self.screenshot_integration.analyze_message(message)
            if analysis["should_capture"]:
                self.logger.info(f"📸 Auto-capturing screenshot: {analysis['capture_reason']}")
                screenshot_info = self.screenshot_integration.capture_for_chat(
                    f"Cursor chat: {analysis['capture_reason']}"
                )
                if screenshot_info:
                    screenshot_path = screenshot_info.get("screenshot_path")
                    self.logger.info(f"✅ Screenshot captured: {screenshot_path}")

        try:
            # Method 1: Use keyboard shortcut (Ctrl+Enter or Cmd+Enter)
            if use_shortcut:
                # Type the message (assuming chat input is focused)
                keyboard.write(message)
                time.sleep(0.2)

                # Send using Ctrl+Enter (Windows/Linux) or Cmd+Enter (Mac)
                keyboard.press_and_release('ctrl+enter')

                self.logger.info("✅ Message sent via keyboard shortcut")

                result = {
                    'success': True,
                    'method': 'keyboard_shortcut',
                    'message': message
                }

                # Add screenshot info if captured
                if screenshot_path:
                    result['screenshot_captured'] = True
                    result['screenshot_path'] = screenshot_path
                    result['message'] = f"{message}\n\n📸 Screenshot captured: {screenshot_path}"

                return result

            # Method 2: Click Send button (fallback)
            else:
                # Find and click Send button
                # This is more complex and less reliable
                send_button = pyautogui.locateOnScreen('send_button.png')  # Would need screenshot

                if send_button:
                    pyautogui.click(send_button)
                    return {
                        'success': True,
                        'method': 'button_click',
                        'message': message
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Send button not found'
                    }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def automate_chat_workflow(self, messages: list[str]) -> Dict[str, Any]:
        """Automate sending multiple chat messages"""
        results = []

        for message in messages:
            result = self.send_chat_message(message)
            results.append(result)
            time.sleep(0.5)  # Small delay between messages

        return {
            'success': all(r.get('success') for r in results),
            'results': results,
            'total': len(messages),
            'succeeded': sum(1 for r in results if r.get('success'))
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="MANUS Cursor IDE Chat Automation")
        parser.add_argument("--send", type=str, help="Send a chat message")
        parser.add_argument("--test", action="store_true", help="Test chat automation")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        automation = MANUSCursorChatAutomation(project_root)

        if args.send:
            result = automation.send_chat_message(args.send)
            if result.get('success'):
                print(f"✅ Message sent: {result.get('method')}")
            else:
                print(f"❌ Error: {result.get('error')}")

        elif args.test:
            print("Testing chat automation...")
            print("Make sure Cursor IDE chat input is focused")
            result = automation.send_chat_message("Test message from MANUS")
            if result.get('success'):
                print("✅ Test successful")
            else:
                print(f"❌ Test failed: {result.get('error')}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()