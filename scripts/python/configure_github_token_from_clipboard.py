#!/usr/bin/env python3
"""
Configure GitHub Token from Clipboard

Reads GitHub Personal Access Token from clipboard and provides
instructions for configuring it in Cursor IDE.

Tags: #GITHUB #PAT #CLIPBOARD #CURSOR_IDE @JARVIS @LUMINA
"""

import sys
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

logger = get_logger("GitHubTokenConfig")

# Clipboard access
try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False
    logger.warning("pyperclip not available - install: pip install pyperclip")


class GitHubTokenConfigurator:
    """
    Configure GitHub Token from Clipboard

    Reads token from clipboard and provides configuration instructions.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize token configurator"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        logger.info("✅ GitHub Token Configurator initialized")

    def get_token_from_clipboard(self) -> Optional[str]:
        """
        Get GitHub token from clipboard

        Returns:
            Token string or None
        """
        if not CLIPBOARD_AVAILABLE:
            logger.error("   ❌ Clipboard access not available")
            logger.info("   📦 Install: pip install pyperclip")
            return None

        try:
            token = pyperclip.paste()

            # Validate token format (GitHub tokens are typically 40+ characters, alphanumeric)
            if token and len(token.strip()) >= 40:
                # Check if it looks like a GitHub token (starts with ghp_ for fine-grained or is alphanumeric)
                token_clean = token.strip()
                if token_clean.startswith('ghp_') or token_clean.startswith('github_pat_') or (token_clean.isalnum() and len(token_clean) >= 40):
                    logger.info("   ✅ Token found in clipboard")
                    logger.info(f"   Token length: {len(token_clean)} characters")
                    logger.info(f"   Token preview: {token_clean[:10]}...{token_clean[-4:]}")
                    return token_clean
                else:
                    logger.warning("   ⚠️  Clipboard content doesn't look like a GitHub token")
                    logger.info(f"   Clipboard content: {token_clean[:50]}...")
                    return None
            else:
                logger.warning("   ⚠️  Clipboard content too short to be a GitHub token")
                return None

        except Exception as e:
            logger.error(f"   ❌ Error reading clipboard: {e}")
            return None

    def provide_configuration_instructions(self, token: Optional[str] = None):
        """Provide instructions for configuring token in Cursor IDE"""
        print("=" * 80)
        print("🔧 CONFIGURE GITHUB TOKEN IN CURSOR IDE")
        print("=" * 80)

        if token:
            print(f"\n✅ Token detected in clipboard")
            print(f"   Token preview: {token[:10]}...{token[-4:]}")
            print(f"   Token length: {len(token)} characters")
        else:
            print("\n⚠️  No token detected in clipboard")
            print("   Please copy your GitHub Personal Access Token to clipboard first")

        print("\n" + "=" * 80)
        print("📋 CONFIGURATION STEPS")
        print("=" * 80)

        print("\n1. Open Cursor IDE Settings")
        print("   • Press: Ctrl + , (comma)")
        print("   • OR: File > Preferences > Settings")

        print("\n2. Navigate to GitHub Access")
        print("   • Search for: 'GitHub Access'")
        print("   • OR: Look for 'GitHub' in settings")

        print("\n3. Add/Update Token")
        print("   • Click 'Connect GitHub' or 'Add Token'")
        print("   • Paste the token (Ctrl+V)")
        if token:
            print(f"   • Token is ready in clipboard: {token[:10]}...{token[-4:]}")

        print("\n4. Save and Verify")
        print("   • Click 'Save' or 'Connect'")
        print("   • Click 'Refresh' in GitHub Access section")
        print("   • Verify 'mlesnews/lumina-ai' shows green checkmark ✅")

        print("\n" + "=" * 80)
        print("💡 QUICK METHOD")
        print("=" * 80)
        print("1. Open Cursor IDE Settings (Ctrl+,)")
        print("2. Type 'GitHub' in search")
        print("3. Find 'GitHub Access' section")
        print("4. Click 'Connect GitHub' or 'Add Token'")
        print("5. Paste token (Ctrl+V)")
        print("6. Click 'Save'")
        print("7. Click 'Refresh' to verify")
        print("=" * 80)

        if token:
            print("\n✅ Token is ready in your clipboard - just paste it (Ctrl+V)")
        else:
            print("\n⚠️  Please copy your GitHub token to clipboard first")

    def open_cursor_settings(self):
        """Open Cursor IDE settings"""
        logger.info("   🔧 Opening Cursor IDE Settings...")
        try:
            # Try to open Cursor settings via keyboard
            try:
                import pyautogui
                # Press Ctrl+, to open settings
                pyautogui.hotkey('ctrl', ',')
                time.sleep(1)
                logger.info("   ✅ Opened Cursor IDE Settings (Ctrl+,)")
                return True
            except ImportError:
                logger.debug("   pyautogui not available")
        except Exception as e:
            logger.debug(f"   Keyboard method failed: {e}")

        logger.info("   📋 Please manually open Cursor IDE Settings:")
        logger.info("      Press: Ctrl + , (comma)")
        return False


def main():
    try:
        """CLI interface"""
        import argparse
        import time

        parser = argparse.ArgumentParser(description="Configure GitHub Token from Clipboard")
        parser.add_argument("--read-clipboard", action="store_true", help="Read token from clipboard")
        parser.add_argument("--instructions", action="store_true", help="Show configuration instructions")
        parser.add_argument("--open-settings", action="store_true", help="Open Cursor IDE settings")
        parser.add_argument("--json", action="store_true", help="JSON output")

        args = parser.parse_args()

        configurator = GitHubTokenConfigurator()

        if args.read_clipboard:
            token = configurator.get_token_from_clipboard()
            if args.json:
                import json
                print(json.dumps({
                    "token_found": token is not None,
                    "token_length": len(token) if token else 0,
                    "token_preview": f"{token[:10]}...{token[-4:]}" if token else None
                }, indent=2))
            else:
                if token:
                    print(f"✅ Token found: {token[:10]}...{token[-4:]}")
                    print(f"   Length: {len(token)} characters")
                    print(f"   Ready to paste in Cursor IDE Settings")
                else:
                    print("❌ No valid token found in clipboard")

        elif args.open_settings:
            configurator.open_cursor_settings()
            print("✅ Cursor IDE Settings should be open")
            print("   Search for 'GitHub Access' and paste your token")

        elif args.instructions or not any([args.read_clipboard, args.open_settings]):
            # Try to read token from clipboard
            token = configurator.get_token_from_clipboard()
            configurator.provide_configuration_instructions(token)

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()