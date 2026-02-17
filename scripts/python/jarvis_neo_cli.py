#!/usr/bin/env python3
"""
JARVIS Neo Browser CLI

Command-line interface for JARVIS control over Neo Browser.
Provides easy access to all JARVIS Neo features.

Tags: #JARVIS #NEO #CLI #BROWSER @JARVIS @LUMINA
"""

import sys
import json
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

logger = get_logger("JARVISNeoCLI")

try:
    from jarvis_neo_full_control import JARVISNeoFullControl
except ImportError:
    logger.error("❌ JARVIS Neo Full Control not available")
    sys.exit(1)


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="JARVIS Neo Browser CLI - Full control over Neo Browser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export YouTube cookies automatically
  jarvis-neo export-cookies youtube.com

  # Navigate to URL
  jarvis-neo navigate https://youtube.com

  # Click element
  jarvis-neo click "button.submit"

  # Fill form field
  jarvis-neo fill "input.email" "user@example.com"

  # Take screenshot
  jarvis-neo screenshot screenshot.png

  # Get page info
  jarvis-neo info
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Export cookies command
    export_parser = subparsers.add_parser("export-cookies", help="Export cookies automatically")
    export_parser.add_argument("domain", nargs="?", default="youtube.com", help="Domain to export cookies for")

    # Navigate command
    nav_parser = subparsers.add_parser("navigate", help="Navigate to URL")
    nav_parser.add_argument("url", help="URL to navigate to")

    # Click command
    click_parser = subparsers.add_parser("click", help="Click element")
    click_parser.add_argument("selector", help="CSS selector of element to click")

    # Fill command
    fill_parser = subparsers.add_parser("fill", help="Fill input field")
    fill_parser.add_argument("selector", help="CSS selector of input field")
    fill_parser.add_argument("text", help="Text to fill")

    # Screenshot command
    screenshot_parser = subparsers.add_parser("screenshot", help="Take screenshot")
    screenshot_parser.add_argument("path", help="Path to save screenshot")

    # Info command
    info_parser = subparsers.add_parser("info", help="Get current page info")

    # Execute script command
    script_parser = subparsers.add_parser("execute", help="Execute JavaScript")
    script_parser.add_argument("script", help="JavaScript code to execute")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Initialize JARVIS control
    control = JARVISNeoFullControl()

    try:
        if args.command == "export-cookies":
            success = control.export_cookies_automatically(args.domain)
            if success:
                print(f"✅ Cookies exported for {args.domain}")
                return 0
            else:
                print(f"❌ Failed to export cookies for {args.domain}")
                return 1

        elif args.command == "navigate":
            success = control.navigate(args.url)
            if success:
                print(f"✅ Navigated to {args.url}")
                return 0
            else:
                print(f"❌ Failed to navigate to {args.url}")
                return 1

        elif args.command == "click":
            success = control.click(args.selector)
            if success:
                print(f"✅ Clicked {args.selector}")
                return 0
            else:
                print(f"❌ Failed to click {args.selector}")
                return 1

        elif args.command == "fill":
            success = control.fill(args.selector, args.text)
            if success:
                print(f"✅ Filled {args.selector} with {args.text}")
                return 0
            else:
                print(f"❌ Failed to fill {args.selector}")
                return 1

        elif args.command == "screenshot":
            success = control.screenshot(args.path)
            if success:
                print(f"✅ Screenshot saved to {args.path}")
                return 0
            else:
                print(f"❌ Failed to take screenshot")
                return 1

        elif args.command == "info":
            info = control.get_page_info()
            print(json.dumps(info, indent=2))
            return 0

        elif args.command == "execute":
            result = control.execute_script(args.script)
            if result is not None:
                print(json.dumps(result, indent=2, default=str))
            return 0

        else:
            parser.print_help()
            return 1

    finally:
        # Clean up
        control.close()


if __name__ == "__main__":


    sys.exit(main())