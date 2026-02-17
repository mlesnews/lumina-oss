#!/usr/bin/env python3
"""
JARVIS RAlt Doit Paste - Programmatic Version

Programmatically pastes "/🟢 PUBLIC: GitHub Open-Source (v2.0)/doit" + Enter
This is the Python equivalent of the AutoHotkey RAlt macro.

Tags: #JARVIS #RALT #DOIT #PASTE #WORKFLOW_CHAINING @JARVIS @LUMINA
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISRAltDoitPaste")

try:
    import pyautogui
    import pyperclip
    AUTOMATION_AVAILABLE = True
except ImportError:
    AUTOMATION_AVAILABLE = False
    logger.warning("⚠️  pyautogui/pyperclip not available - install: pip install pyautogui pyperclip")


class JARVISRAltDoitPaste:
    """
    JARVIS RAlt Doit Paste

    Programmatically pastes "/🟢 PUBLIC: GitHub Open-Source (v2.0)/doit" + Enter
    Equivalent to pressing Right Alt in the AutoHotkey script.
    """

    def __init__(self):
        """Initialize RAlt Doit Paste"""
        if AUTOMATION_AVAILABLE:
            pyautogui.PAUSE = 0.1
            pyautogui.FAILSAFE = False  # Disable failsafe for automation
            self.logger = logger
        else:
            self.logger = logger
            self.logger.error("Automation libraries not available")

        self.doit_command = "/🟢 PUBLIC: GitHub Open-Source (v2.0)/doit"

        self.logger.info("✅ JARVIS RAlt Doit Paste initialized")
        self.logger.info(f"   Command: {self.doit_command}")

    def paste_doit_command(self) -> Dict[str, Any]:
        """
        Paste the doit command and press Enter

        This is the programmatic equivalent of pressing Right Alt.

        Returns:
            Result dictionary
        """
        if not AUTOMATION_AVAILABLE:
            return {
                "success": False,
                "error": "Automation libraries not available",
                "message": "Cannot paste - install pyautogui and pyperclip"
            }

        self.logger.info("=" * 80)
        self.logger.info("🔘 PASTING DOIT COMMAND")
        self.logger.info("=" * 80)
        self.logger.info(f"   Command: {self.doit_command}")

        try:
            # Save current clipboard
            original_clipboard = pyperclip.paste()

            # Set clipboard to doit command
            pyperclip.copy(self.doit_command)
            time.sleep(0.05)  # Brief delay for clipboard

            # Paste (Ctrl+V)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.05)  # Brief delay for paste

            # Press Enter
            pyautogui.press('enter')
            time.sleep(0.1)  # Brief delay for Enter

            # Restore original clipboard
            try:
                pyperclip.copy(original_clipboard)
            except Exception:
                pass  # Ignore clipboard restore errors

            self.logger.info("✅ Doit command pasted and Enter pressed")
            return {
                "success": True,
                "command": self.doit_command,
                "message": "Doit command pasted and Enter pressed",
                "timestamp": time.time()
            }

        except Exception as e:
            self.logger.error(f"❌ Failed to paste doit command: {e}")
            return {
                "success": False,
                "error": str(e),
                "command": self.doit_command,
                "message": f"Failed to paste: {e}"
            }

    def trigger_ralt_equivalent(self) -> Dict[str, Any]:
        """
        Trigger the RAlt equivalent action

        This is what happens when you press Right Alt.
        """
        return self.paste_doit_command()


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS RAlt Doit Paste")
    parser.add_argument("--paste", action="store_true", help="Paste doit command")
    parser.add_argument("--test", action="store_true", help="Test paste (dry run)")

    args = parser.parse_args()

    paste_system = JARVISRAltDoitPaste()

    if args.test:
        print(f"Test mode - would paste: {paste_system.doit_command}")
        print("(Use --paste to actually paste)")
        return 0

    if args.paste or not any([args.test]):
        print("Pasting doit command...")
        result = paste_system.paste_doit_command()
        if result.get("success"):
            print("✅ Doit command pasted successfully")
            return 0
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
            return 1

    return 0


if __name__ == "__main__":


    sys.exit(main() or 0)