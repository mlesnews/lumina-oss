#!/usr/bin/env python3
"""
Restart AutoHotkey - Automatic Hotkey Service Restart

Automatically restarts AutoHotkey with updated scripts.
Uses decision-making workflows and troubleshooting if needed.

Tags: #AUTOHOTKEY #RESTART #AUTOMATION #TROUBLESHOOTING @JARVIS @LUMINA
"""

import sys
import subprocess
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("RestartAutoHotkey")


def stop_autohotkey() -> bool:
    """Stop all AutoHotkey processes"""
    try:
        result = subprocess.run(
            ["taskkill", "/F", "/IM", "AutoHotkey.exe"],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        if result.returncode == 0 or "not found" in result.stdout.lower() or "not found" in result.stderr.lower():
            logger.info("   ✅ AutoHotkey stopped (or was not running)")
            return True
        else:
            logger.warning(f"   ⚠️  AutoHotkey stop result: {result.returncode}")
            return False
    except Exception as e:
        logger.debug(f"   Stop AutoHotkey: {e}")
        return False


def start_autohotkey() -> bool:
    """Start AutoHotkey with updated script"""
    try:
        from lumina_hotkey_manager import LuminaHotkeyManager

        manager = LuminaHotkeyManager()
        return manager.start_hotkeys()
    except Exception as e:
        logger.error(f"   ❌ Error starting AutoHotkey: {e}")
        return False


def verify_autohotkey_running() -> bool:
    """Verify AutoHotkey is running"""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq AutoHotkey.exe"],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return "AutoHotkey.exe" in result.stdout
    except:
        return False


def main():
    """Main execution - automatic restart"""
    logger.info("="*80)
    logger.info("🔄 RESTARTING AUTOHOTKEY - AUTOMATIC")
    logger.info("="*80)
    logger.info("")

    # Step 1: Stop AutoHotkey
    logger.info("1️⃣  Stopping AutoHotkey...")
    stop_autohotkey()
    time.sleep(1)

    # Step 2: Start AutoHotkey
    logger.info("")
    logger.info("2️⃣  Starting AutoHotkey with updated script...")
    if start_autohotkey():
        logger.info("   ✅ AutoHotkey started")
    else:
        logger.error("   ❌ Failed to start AutoHotkey")
        logger.info("")
        logger.info("🔧 TROUBLESHOOTING...")

        # Troubleshooting: Try direct AutoHotkey launch
        try:
            script_path = Path(__file__).parent.parent.parent / "scripts" / "autohotkey" / "left_alt_doit_fixed.ahk"

            # Find AutoHotkey executable
            autohotkey_exe = None
            common_paths = [
                r"C:\Program Files\AutoHotkey\AutoHotkey.exe",
                r"C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe"
            ]

            for path in common_paths:
                if Path(path).exists():
                    autohotkey_exe = path
                    break

            if not autohotkey_exe:
                result = subprocess.run(
                    ["where", "autohotkey"],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                if result.returncode == 0:
                    autohotkey_exe = result.stdout.strip().split('\n')[0]

            if autohotkey_exe and script_path.exists():
                logger.info("   🔧 Trying direct AutoHotkey launch...")
                subprocess.Popen(
                    [autohotkey_exe, str(script_path)],
                    cwd=str(script_path.parent.parent.parent),
                    creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
                )
                time.sleep(2)

                if verify_autohotkey_running():
                    logger.info("   ✅ AutoHotkey started via direct launch")
                    return 0
                else:
                    logger.error("   ❌ Direct launch also failed")
            else:
                logger.error("   ❌ AutoHotkey executable or script not found")
        except Exception as e:
            logger.error(f"   ❌ Troubleshooting failed: {e}")

        return 1

    # Step 3: Verify
    logger.info("")
    logger.info("3️⃣  Verifying AutoHotkey is running...")
    time.sleep(2)

    if verify_autohotkey_running():
        logger.info("   ✅ AutoHotkey verified running")
        logger.info("")
        logger.info("="*80)
        logger.info("✅ AUTOHOTKEY RESTARTED SUCCESSFULLY")
        logger.info("="*80)
        logger.info("")
        logger.info("🎹 Hotkeys active:")
        logger.info("   • Right Alt → @DOIT + Enter")
        logger.info("   • F23 → Cursor IDE Voice Input (ONLY)")
        logger.info("")
        return 0
    else:
        logger.error("   ❌ AutoHotkey not running after start")
        return 1


if __name__ == "__main__":


    sys.exit(main())