#!/usr/bin/env python3
"""
Terminal Restart Manager

Actually restarts terminals that are in a bad state (orange triangle warning).
This closes and reopens terminals or forces reinitialization.

Tags: #TERMINAL #RESTART #FIX #ORANGE_TRIANGLE @JARVIS @LUMINA
"""

import sys
import time
import subprocess
import os
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        def get_logger(name):
            return logging.getLogger(name)

logger = get_logger("TerminalRestartManager")


def restart_terminal_via_keyboard():
    """
    Restart terminal by sending keyboard shortcuts to Cursor IDE.

    This uses keyboard automation to:
    1. Close the current terminal
    2. Open a new terminal
    """
    try:
        import keyboard

        logger.info("   🔄 Restarting terminal via keyboard shortcuts...")

        # Method 1: Kill terminal (Ctrl+Shift+` toggles terminal)
        keyboard.press_and_release('ctrl+shift+`')
        time.sleep(0.3)

        # Kill terminal explicitly (Ctrl+W closes terminal)
        keyboard.press_and_release('ctrl+w')
        time.sleep(0.3)

        # Open new terminal (Ctrl+Shift+` again)
        keyboard.press_and_release('ctrl+shift+`')
        time.sleep(0.5)

        # Alternative: Use command palette to kill and create terminal
        # Ctrl+Shift+P opens command palette
        keyboard.press_and_release('ctrl+shift+p')
        time.sleep(0.3)

        # Type "Terminal: Kill Active Terminal Instance"
        keyboard.write("Terminal: Kill Active Terminal Instance", delay=0.05)
        time.sleep(0.3)
        keyboard.press_and_release('enter')
        time.sleep(0.5)

        # Create new terminal
        keyboard.press_and_release('ctrl+shift+`')
        time.sleep(0.5)

        logger.info("   ✅ Terminal restarted via keyboard")
        return True

    except ImportError:
        logger.warning("   ⚠️  keyboard library not available")
        return False
    except Exception as e:
        logger.error("   ❌ Keyboard restart error: %s", e)
        return False


def restart_terminal_via_command():
    """
    Restart terminal by sending commands to the terminal itself.

    This sends commands that force terminal reinitialization.
    """
    try:
        logger.info("   🔄 Restarting terminal via command...")

        # Send clear and reinitialize commands
        print("\033[2J\033[H", end="", flush=True)  # Clear screen
        time.sleep(0.1)

        # Force shell integration reload
        if sys.platform == "win32":
            # PowerShell: Reload shell integration
            reload_cmd = """
            try {
                $script = "$env:CURSOR_PATH\\resources\\app\\out\\vs\\workbench\\contrib\\terminal\\common\\scripts\\shellIntegration.ps1"
                if (Test-Path $script) {
                    . $script
                }
            } catch {}
            """
            subprocess.run(["pwsh", "-NoProfile", "-Command", reload_cmd], 
                         timeout=2.0, check=False, capture_output=True)
        else:
            # Unix: Source shell integration
            subprocess.run(["bash", "-c", "source ~/.bashrc 2>/dev/null || true"], 
                         timeout=2.0, check=False, capture_output=True)

        logger.info("   ✅ Terminal reinitialized via command")
        return True

    except Exception as e:
        logger.error("   ❌ Command restart error: %s", e)
        return False


def force_terminal_reinit():
    """
    Force terminal reinitialization by sending proper sequences.

    This is more aggressive than just resetting sequences.
    """
    try:
        logger.info("   🔄 Forcing terminal reinitialization...")

        # Clear terminal completely
        print("\033[2J\033[H", end="", flush=True)  # Clear screen and move to home
        time.sleep(0.2)

        # Send reset sequences multiple times to ensure they're processed
        for _ in range(3):
            # Command start (A)
            print("\033]133;A\033\\", end="", flush=True)
            time.sleep(0.1)

            # Command end (B)
            print("\033]133;B\033\\", end="", flush=True)
            time.sleep(0.1)

            # Prompt ready (P)
            print("\033]133;P\033\\", end="", flush=True)
            time.sleep(0.1)

        # Send a harmless command to establish proper state
        print("echo Terminal reinitialized", flush=True)
        time.sleep(0.2)

        logger.info("   ✅ Terminal forced reinitialization complete")
        return True

    except Exception as e:
        logger.error("   ❌ Force reinit error: %s", e)
        return False


def restart_terminal_aggressive():
    """
    Aggressively restart terminal using all available methods.

    This tries multiple approaches to ensure terminal is restarted.
    """
    logger.info("🔄 Aggressively restarting terminal...")

    success = False

    # Method 1: Keyboard shortcuts (most reliable - actually closes/reopens terminal)
    try:
        if restart_terminal_via_keyboard():
            success = True
            # Give terminal time to restart
            time.sleep(1.0)
    except Exception as e:
        logger.debug("   Keyboard restart failed: %s", e)

    # Method 2: Force reinitialization (if keyboard didn't work)
    if not success:
        try:
            if force_terminal_reinit():
                success = True
        except Exception as e:
            logger.debug("   Force reinit failed: %s", e)

    # Method 3: Command-based restart (fallback)
    if not success:
        try:
            if restart_terminal_via_command():
                success = True
        except Exception as e:
            logger.debug("   Command restart failed: %s", e)

    if success:
        logger.info("   ✅ Terminal restart completed")
    else:
        logger.warning("   ⚠️  Terminal restart may have failed")

    return success


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Terminal Restart Manager")
    parser.add_argument("--keyboard", action="store_true", help="Use keyboard shortcuts")
    parser.add_argument("--command", action="store_true", help="Use command-based restart")
    parser.add_argument("--force", action="store_true", help="Force reinitialization")
    parser.add_argument("--aggressive", action="store_true", help="Try all methods")

    args = parser.parse_args()

    if args.keyboard:
        restart_terminal_via_keyboard()
    elif args.command:
        restart_terminal_via_command()
    elif args.force:
        force_terminal_reinit()
    else:
        # Default: aggressive restart
        restart_terminal_aggressive()

    return 0


if __name__ == "__main__":


    sys.exit(main())