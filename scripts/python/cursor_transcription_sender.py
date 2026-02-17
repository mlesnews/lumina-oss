#!/usr/bin/env python3
"""
Cursor Transcription Sender with Retry Manager

Sends transcribed text to Cursor IDE chat with automatic retry on failure.
Integrates with cursor_chat_retry_manager for resilient message sending.

Tags: #CURSOR #TRANSCRIPTION #RETRY #RESILIENCE @JARVIS @LUMINA
"""

import sys
import time
import logging
from pathlib import Path
from typing import Optional, Callable, Any

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from cursor_chat_retry_manager import retry_chat_operation, RetryStrategy
    RETRY_MANAGER_AVAILABLE = True
except ImportError:
    RETRY_MANAGER_AVAILABLE = False
    logger = get_logger("CursorTranscriptionSender")
    logger.warning("⚠️  Retry manager not available - install cursor_chat_retry_manager")

logger = get_logger("CursorTranscriptionSender")

# Try keyboard automation
try:
    import pyautogui
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    logger.warning("⚠️  Keyboard automation not available - install: pip install pyautogui keyboard")

try:
    from pynput.keyboard import Key, Controller as KeyboardController
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False


class CursorTranscriptionSender:
    """
    Sends transcribed text to Cursor IDE chat with retry logic.

    Handles:
    - Text input to Cursor chat
    - Automatic retry on failure
    - Timeout/disconnect recovery
    """

    def __init__(self, use_retry: bool = True):
        """
        Initialize transcription sender.

        Args:
            use_retry: Use retry manager for resilient sending
        """
        self.use_retry = use_retry and RETRY_MANAGER_AVAILABLE
        self.keyboard_controller = KeyboardController() if PYNPUT_AVAILABLE else None

    def send_text_to_cursor(self, text: str, max_retries: int = 3) -> bool:
        """
        Send text to Cursor IDE chat with retry logic.

        Args:
            text: Text to send
            max_retries: Maximum retry attempts

        Returns:
            True if sent successfully, False otherwise
        """
        if not text or not text.strip():
            logger.warning("⚠️  Empty text - nothing to send")
            return False

        def _send_operation():
            """Internal send operation (wrapped for retry)"""
            return self._do_send_text(text)

        if self.use_retry:
            try:
                logger.info(f"📤 Sending transcription to Cursor ({len(text)} chars) with retry protection...")
                result = retry_chat_operation(
                    _send_operation,
                    max_retries=max_retries,
                    initial_delay=1.0,
                    max_delay=10.0,
                    strategy=RetryStrategy.EXPONENTIAL
                )
                if result:
                    logger.info(f"✅ Transcription sent successfully to Cursor")
                return result
            except Exception as e:
                logger.error(f"❌ Failed to send text after {max_retries} retries: {type(e).__name__}: {e}")
                logger.error(f"   Connection error - transcription NOT sent to Cursor")
                return False
        else:
            # No retry - just try once
            try:
                return self._do_send_text(text)
            except Exception as e:
                logger.error(f"❌ Failed to send text: {e}")
                return False

    def _do_send_text(self, text: str) -> bool:
        """
        Actually send text to Cursor (internal method).

        Args:
            text: Text to send

        Returns:
            True if successful, False otherwise
        """
        try:
            # Method 1: Try pynput (more reliable)
            if PYNPUT_AVAILABLE and self.keyboard_controller:
                return self._send_with_pynput(text)

            # Method 2: Try pyautogui
            elif KEYBOARD_AVAILABLE:
                return self._send_with_pyautogui(text)

            # Method 3: Try keyboard library
            elif KEYBOARD_AVAILABLE:
                return self._send_with_keyboard_lib(text)

            else:
                logger.error("❌ No keyboard automation available")
                return False

        except Exception as e:
            logger.error(f"❌ Error sending text: {e}", exc_info=True)
            raise  # Re-raise for retry manager

    def _send_with_pynput(self, text: str) -> bool:
        """Send text using pynput"""
        try:
            # Focus Cursor window (assume it's already focused)
            # Type text
            self.keyboard_controller.type(text)

            # CRITICAL FIX: Try Enter key first, but if that doesn't work, click Send button
            time.sleep(0.1)  # Small delay
            self.keyboard_controller.press(Key.enter)
            self.keyboard_controller.release(Key.enter)
            time.sleep(0.3)  # Wait to see if it sent

            # FALLBACK: If Enter didn't work, actually click Send button
            try:
                from manus_send_button import MANUSSendButton
                send_button = MANUSSendButton()
                # Check if message was sent by looking for Send button (if still visible, message didn't send)
                # For now, always try clicking Send button as backup
                logger.info("🔄 Trying Send button click as backup...")
                send_button.click_send()
            except Exception as e:
                logger.debug(f"Send button click fallback failed: {e}")

            logger.info(f"✅ Sent text to Cursor ({len(text)} chars)")
            return True
        except Exception as e:
            logger.error(f"❌ pynput send failed: {e}")
            raise

    def _send_with_pyautogui(self, text: str) -> bool:
        """Send text using pyautogui"""
        try:
            # Type text
            pyautogui.write(text, interval=0.01)

            # CRITICAL FIX: Try Enter key first, but also click Send button as backup
            time.sleep(0.1)
            pyautogui.press('enter')
            time.sleep(0.3)  # Wait to see if it sent

            # FALLBACK: Click Send button
            try:
                from manus_send_button import MANUSSendButton
                send_button = MANUSSendButton()
                logger.info("🔄 Trying Send button click as backup...")
                send_button.click_send()
            except Exception as e:
                logger.debug(f"Send button click fallback failed: {e}")

            logger.info(f"✅ Sent text to Cursor ({len(text)} chars)")
            return True
        except Exception as e:
            logger.error(f"❌ pyautogui send failed: {e}")
            raise

    def _send_with_keyboard_lib(self, text: str) -> bool:
        """Send text using keyboard library"""
        try:
            # Type text
            keyboard.write(text)

            # Press Enter
            time.sleep(0.1)
            keyboard.press_and_release('enter')

            logger.info(f"✅ Sent text to Cursor ({len(text)} chars)")
            return True
        except Exception as e:
            logger.error(f"❌ keyboard lib send failed: {e}")
            raise


# Global sender instance
_default_sender = CursorTranscriptionSender(use_retry=True)


def send_transcription_to_cursor(text: str, max_retries: int = 3) -> bool:
    """
    Convenience function to send transcription to Cursor with retry.

    Args:
        text: Transcribed text to send
        max_retries: Maximum retry attempts

    Returns:
        True if sent successfully, False otherwise
    """
    return _default_sender.send_text_to_cursor(text, max_retries=max_retries)


def send_to_cursor(text: str, max_retries: int = 3) -> bool:
    """
    Alias for send_transcription_to_cursor - convenience function.

    Args:
        text: Text to send to Cursor
        max_retries: Maximum retry attempts

    Returns:
        True if sent successfully, False otherwise
    """
    return send_transcription_to_cursor(text, max_retries=max_retries)


if __name__ == "__main__":
    # Test
    test_text = "Test transcription message"
    result = send_transcription_to_cursor(test_text)
    print(f"✅ Send result: {result}")
