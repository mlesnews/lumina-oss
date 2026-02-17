#!/usr/bin/env python3
"""
Cursor Chat Auto-Screenshot Helper
Quick helper to capture screenshot for Cursor chat
Can be triggered via keyboard shortcut or command
#JARVIS #CURSOR #CHAT #SCREENSHOT #QUICK-HELPER
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from cursor_chat_screenshot_integration import process_chat_message


def main():
    """Quick screenshot capture for Cursor chat"""
    import argparse

    parser = argparse.ArgumentParser(description="Quick screenshot capture for Cursor chat")
    parser.add_argument("message", nargs="?", help="Chat message (optional - will capture anyway)")
    parser.add_argument("--context", help="Context description for screenshot")
    args = parser.parse_args()

    message = args.message or args.context or "Cursor chat screenshot"

    print("📸 Capturing screenshot for Cursor chat...")
    print("")

    result = process_chat_message(message, auto_capture=True)

    if result["screenshot_path"]:
        print(f"✅ Screenshot ready: {result['screenshot_path']}")
        print("")
        print("💡 You can now attach this screenshot to your Cursor chat message")
        print(f"   Path: {result['screenshot_path']}")
    else:
        print(f"ℹ️  {result['message']}")

    return 0


if __name__ == "__main__":


    sys.exit(main())