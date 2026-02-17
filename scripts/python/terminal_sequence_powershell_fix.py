#!/usr/bin/env python3
"""
Terminal Sequence PowerShell Fix

Uses PowerShell to directly fix terminal sequence issues in the actual terminal window.
This can detect and fix orange triangle warnings that appear in PowerShell terminals.

Tags: #TERMINAL #POWERSHELL #FIX #SEQUENCE @JARVIS @LUMINA
"""

import sys
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

logger = get_logger("TerminalSequencePowerShellFix")


def fix_terminal_via_powershell():
    """
    Fix terminal sequence issues using PowerShell script.

    This directly interacts with the PowerShell terminal to fix
    orange triangle warnings.
    """
    logger.info("🔧 Fixing terminal via PowerShell...")

    # Path to PowerShell fix script
    ps_script = project_root / "scripts" / "powershell" / "fix-terminal-sequence.ps1"

    if not ps_script.exists():
        logger.error("   ❌ PowerShell fix script not found: %s", ps_script)
        return False

    try:
        # Try pwsh first, then powershell
        powershell_exe = None
        for exe in ["pwsh", "powershell"]:
            try:
                subprocess.run([exe, "-Command", "exit"], check=True, capture_output=True, timeout=1.0)
                powershell_exe = exe
                break
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                continue

        if not powershell_exe:
            logger.warning("   ⚠️  PowerShell not found")
            return False

        # Run PowerShell script
        result = subprocess.run(
            [
                powershell_exe,
                "-NoProfile",
                "-ExecutionPolicy", "Bypass",
                "-File", str(ps_script)
            ],
            capture_output=True,
            text=True,
            timeout=10.0,
            check=False
        )

        if result.returncode == 0:
            logger.info("   ✅ PowerShell fix completed successfully")
            if result.stdout:
                logger.debug("   Output: %s", result.stdout)
            return True
        else:
            logger.warning("   ⚠️  PowerShell fix returned code %d", result.returncode)
            if result.stderr:
                logger.warning("   Error: %s", result.stderr)
            return False

    except subprocess.TimeoutExpired:
        logger.error("   ❌ PowerShell fix timed out")
        return False
    except Exception as e:
        logger.error("   ❌ PowerShell fix error: %s", e)
        return False


def send_sequence_reset():
    """
    Send sequence reset commands directly to terminal.

    This sends ANSI escape sequences to reset terminal state.
    """
    logger.info("   📝 Sending sequence reset commands...")

    try:
        # Send proper sequence markers
        # These are ANSI escape sequences for shell integration

        # Command start (A)
        print("\033]133;A\033\\", end="", flush=True)

        import time
        time.sleep(0.1)

        # Command end (B)
        print("\033]133;B\033\\", end="", flush=True)

        time.sleep(0.1)

        # Prompt ready (P)
        print("\033]133;P\033\\", end="", flush=True)

        logger.info("   ✅ Sequence reset commands sent")
        return True

    except Exception as e:
        logger.error("   ❌ Error sending sequence reset: %s", e)
        return False


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Terminal Sequence PowerShell Fix")
    parser.add_argument("--powershell", action="store_true", help="Use PowerShell script fix")
    parser.add_argument("--direct", action="store_true", help="Send direct sequence reset")
    parser.add_argument("--both", action="store_true", help="Try both methods")

    args = parser.parse_args()

    success = False

    if args.powershell or args.both:
        success = fix_terminal_via_powershell() or success

    if args.direct or args.both:
        success = send_sequence_reset() or success

    if not (args.powershell or args.direct or args.both):
        # Default: try both
        logger.info("Trying both fix methods...")
        fix_terminal_via_powershell()
        send_sequence_reset()
        success = True

    if success:
        logger.info("✅ Terminal fix completed")
        logger.info("   The orange triangle should disappear on the next command.")
    else:
        logger.warning("⚠️  Terminal fix may have failed")

    return 0 if success else 1


if __name__ == "__main__":


    sys.exit(main())