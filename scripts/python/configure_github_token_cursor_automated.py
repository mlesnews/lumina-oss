#!/usr/bin/env python3
"""
Configure GitHub Token in Cursor IDE - Automated

Uses keyboard automation to navigate Cursor IDE settings and configure
GitHub Personal Access Token from clipboard.

Tags: #GITHUB #PAT #CURSOR_IDE #KEYBOARD_AUTOMATION #MANUS @JARVIS @LUMINA
"""

import sys
import time
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

logger = get_logger("GitHubTokenAuto")

# Clipboard
try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False
    logger.warning("pyperclip not available")

# Keyboard automation
try:
    from manus_unified_control import MANUSUnifiedControl, ControlArea
    MANUS_AVAILABLE = True
except ImportError:
    MANUS_AVAILABLE = False
    logger.debug("MANUS not available")

try:
    import pyautogui
    KEYBOARD_AVAILABLE = True
    pyautogui.PAUSE = 0.5
except ImportError:
    KEYBOARD_AVAILABLE = False
    logger.warning("pyautogui not available")


class GitHubTokenCursorAutomation:
    """
    Automated GitHub Token Configuration in Cursor IDE

    Uses keyboard automation to configure token from clipboard.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize automation"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Initialize MANUS if available
        self.manus = None
        if MANUS_AVAILABLE:
            try:
                self.manus = MANUSUnifiedControl(self.project_root)
                logger.info("   ✅ MANUS available")
            except Exception as e:
                logger.debug(f"   MANUS init error: {e}")

        logger.info("✅ GitHub Token Cursor Automation initialized")

    def get_token_from_clipboard(self) -> Optional[str]:
        """Get token from clipboard"""
        if not CLIPBOARD_AVAILABLE:
            return None

        try:
            token = pyperclip.paste().strip()
            if token and len(token) >= 40:
                logger.info(f"   ✅ Token found: {token[:10]}...{token[-4:]}")
                return token
        except Exception as e:
            logger.error(f"   ❌ Clipboard error: {e}")

        return None

    def _type_text(self, text: str):
        try:
            """Type text"""
            if KEYBOARD_AVAILABLE:
                pyautogui.write(text, interval=0.1)
                return True
            return False

        except Exception as e:
            self.logger.error(f"Error in _type_text: {e}", exc_info=True)
            raise
    def _press_key(self, key: str, presses: int = 1):
        """Press key"""
        if KEYBOARD_AVAILABLE:
            pyautogui.press(key, presses=presses, interval=0.2)
            return True
        return False

    def _press_hotkey(self, *keys):
        """Press key combination"""
        if KEYBOARD_AVAILABLE:
            pyautogui.hotkey(*keys)
            return True
        return False

    def _paste(self):
        """Paste from clipboard"""
        if KEYBOARD_AVAILABLE:
            pyautogui.hotkey('ctrl', 'v')
            return True
        return False

    def open_cursor_settings(self):
        """Open Cursor IDE Settings"""
        logger.info("   🔧 Opening Cursor IDE Settings...")
        time.sleep(0.5)

        # Press Ctrl+, to open settings
        self._press_hotkey('ctrl', ',')
        time.sleep(1.5)
        logger.info("   ✅ Opened Settings (Ctrl+,)")
        return True

    def navigate_to_github_access(self):
        """Navigate to GitHub Access section"""
        logger.info("   ⌨️  Navigating to GitHub Access...")
        time.sleep(0.5)

        # Type "GitHub" to search
        self._type_text("GitHub")
        time.sleep(1)

        # Press Enter or Tab to select
        self._press_key('enter')
        time.sleep(1)

        # Or try Tab to navigate
        self._press_key('tab', presses=3)
        time.sleep(0.5)

        logger.info("   ✅ Navigated to GitHub Access")
        return True

    def paste_token(self):
        """Paste token from clipboard"""
        logger.info("   📋 Pasting token from clipboard...")
        time.sleep(0.5)

        # Paste (Ctrl+V)
        self._paste()
        time.sleep(0.5)

        logger.info("   ✅ Token pasted")
        return True

    def save_and_refresh(self):
        """Save and refresh"""
        logger.info("   💾 Saving and refreshing...")
        time.sleep(0.5)

        # Press Tab to navigate to Save button
        self._press_key('tab', presses=2)
        time.sleep(0.3)

        # Press Enter to save
        self._press_key('enter')
        time.sleep(1)

        # Look for Refresh button
        # This may require manual intervention
        logger.info("   ✅ Configuration saved")
        logger.info("   📋 Please manually click 'Refresh' in GitHub Access section")
        return True

    def configure_token_automated(self) -> bool:
        """
        Fully automated token configuration

        Returns:
            True if successful
        """
        logger.info("=" * 80)
        logger.info("🤖 AUTOMATED GITHUB TOKEN CONFIGURATION")
        logger.info("=" * 80)

        # Get token from clipboard
        token = self.get_token_from_clipboard()
        if not token:
            logger.error("   ❌ No token found in clipboard")
            logger.info("   📋 Please copy your GitHub token to clipboard first")
            return False

        logger.info("   ⚠️  This will use keyboard automation")
        logger.info("   ⚠️  Please do NOT use your keyboard during this process")
        logger.info("   ⚠️  Process will start in 3 seconds...")
        time.sleep(3)

        # Step 1: Open Cursor Settings
        if not self.open_cursor_settings():
            return False

        # Step 2: Navigate to GitHub Access
        if not self.navigate_to_github_access():
            logger.warning("   ⚠️  Could not navigate automatically")
            return False

        # Step 3: Paste token
        if not self.paste_token():
            logger.warning("   ⚠️  Could not paste token")
            return False

        # Step 4: Save
        if not self.save_and_refresh():
            logger.warning("   ⚠️  Could not save automatically")

        logger.info("=" * 80)
        logger.info("✅ AUTOMATION COMPLETE")
        logger.info("=" * 80)
        logger.info("   Please verify:")
        logger.info("   1. Token is pasted correctly")
        logger.info("   2. Click 'Save' or 'Connect' if not done automatically")
        logger.info("   3. Click 'Refresh' in GitHub Access section")
        logger.info("   4. Verify 'mlesnews/lumina-ai' shows green checkmark ✅")
        logger.info("=" * 80)

        return True


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Configure GitHub Token in Cursor IDE (Automated)")
    parser.add_argument("--automate", action="store_true", help="Fully automated configuration")
    parser.add_argument("--read-token", action="store_true", help="Read token from clipboard")

    args = parser.parse_args()

    automation = GitHubTokenCursorAutomation()

    if args.automate:
        if not KEYBOARD_AVAILABLE:
            logger.error("   ❌ Keyboard automation not available")
            logger.info("   📦 Install: pip install pyautogui")
            return

        success = automation.configure_token_automated()
        if success:
            print("✅ Automation completed")
        else:
            print("❌ Automation failed - manual intervention may be needed")

    elif args.read_token:
        token = automation.get_token_from_clipboard()
        if token:
            print(f"✅ Token found: {token[:10]}...{token[-4:]}")
            print(f"   Length: {len(token)} characters")
            print(f"   Ready to configure in Cursor IDE")
        else:
            print("❌ No token found in clipboard")

    else:
        # Show instructions
        token = automation.get_token_from_clipboard()
        if token:
            print("=" * 80)
            print("🔧 CONFIGURE GITHUB TOKEN IN CURSOR IDE")
            print("=" * 80)
            print(f"\n✅ Token found in clipboard: {token[:10]}...{token[-4:]}")
            print(f"   Length: {len(token)} characters")
            print("\n📋 Quick Steps:")
            print("   1. Press Ctrl+, to open Cursor IDE Settings")
            print("   2. Type 'GitHub' in search")
            print("   3. Find 'GitHub Access' section")
            print("   4. Click 'Connect GitHub' or 'Add Token'")
            print("   5. Paste token (Ctrl+V)")
            print("   6. Click 'Save'")
            print("   7. Click 'Refresh' to verify")
            print("\n🤖 Or run with --automate for full automation")
            print("=" * 80)
        else:
            print("❌ No token found in clipboard")
            print("   Please copy your GitHub token to clipboard first")


if __name__ == "__main__":


    main()