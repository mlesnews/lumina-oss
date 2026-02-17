#!/usr/bin/env python3
"""
Cursor IDE Countdown Extension Helper

Helper script to integrate idle countdown into Cursor IDE footer.
Provides status bar integration and file watching for real-time updates.

@JARVIS #CURSOR #IDE #FOOTER #COUNTDOWN #EXTENSION
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CursorIDECountdown")

try:
    from jarvis_ide_idle_countdown import get_ide_countdown
    COUNTDOWN_AVAILABLE = True
except ImportError:
    COUNTDOWN_AVAILABLE = False
    get_ide_countdown = None
    logger.warning("⚠️  IDE countdown not available")


def get_cursor_status_bar_text() -> str:
    """Get text for Cursor IDE status bar"""
    if not COUNTDOWN_AVAILABLE:
        return "⚠️ Countdown unavailable"

    try:
        project_root = Path(__file__).parent.parent.parent
        countdown = get_ide_countdown(project_root)
        return countdown.get_footer_text_short()
    except Exception as e:
        logger.error(f"Failed to get countdown: {e}")
        return "⚠️ Countdown error"


def get_cursor_status_bar_full() -> str:
    """Get full text for Cursor IDE status bar (word-wrapping)"""
    if not COUNTDOWN_AVAILABLE:
        return "⚠️ Countdown unavailable"

    try:
        project_root = Path(__file__).parent.parent.parent
        countdown = get_ide_countdown(project_root)
        return countdown.get_footer_text_full()
    except Exception as e:
        logger.error(f"Failed to get countdown: {e}")
        return "⚠️ Countdown error"


def watch_countdown_file(callback=None):
    """Watch countdown status file for changes"""
    if not COUNTDOWN_AVAILABLE:
        return

    project_root = Path(__file__).parent.parent.parent
    status_file = project_root / "data" / "ide_countdown" / "countdown_status.json"

    last_modified = 0

    while True:
        try:
            if status_file.exists():
                current_modified = status_file.stat().st_mtime
                if current_modified > last_modified:
                    last_modified = current_modified

                    with open(status_file, 'r') as f:
                        status = json.load(f)

                    if callback:
                        callback(status)
                    else:
                        print(f"Countdown: {status.get('footer_display', 'N/A')}")

            time.sleep(1)
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Watch error: {e}")
            time.sleep(5)


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Cursor IDE Countdown Extension Helper")
    parser.add_argument("--text", action="store_true", help="Get status bar text")
    parser.add_argument("--full", action="store_true", help="Get full status bar text (word-wrapping)")
    parser.add_argument("--watch", action="store_true", help="Watch countdown file for changes")

    args = parser.parse_args()

    if args.text:
        print(get_cursor_status_bar_text())

    if args.full:
        print(get_cursor_status_bar_full())

    if args.watch:
        print("Watching countdown file (Ctrl+C to stop)...")
        watch_countdown_file()

    if not any([args.text, args.full, args.watch]):
        parser.print_help()


if __name__ == "__main__":


    main()