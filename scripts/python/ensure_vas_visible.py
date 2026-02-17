#!/usr/bin/env python3
"""
Ensure Virtual Assistants Are Visible
Quick script to start both Kenny and Ace, ensuring they're visible on screen.

Tags: #KENNY #ACE #VISIBILITY #STARTUP @JARVIS @LUMINA
"""

import sys
import time
import subprocess
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("EnsureVAsVisible")

def check_kenny_running():
    """Check if Kenny is already running"""
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and any('kenny' in str(arg).lower() for arg in cmdline):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except ImportError:
        # psutil not available - assume not running
        pass
    return False

def start_kenny():
    """Start Kenny if not already running"""
    if check_kenny_running():
        logger.info("✅ Kenny is already running")
        return True

    try:
        logger.info("🚀 Starting Kenny...")
        kenny_script = script_dir / "start_kenny_visible.py"
        subprocess.Popen(
            [sys.executable, str(kenny_script)],
            cwd=str(project_root),
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
        )
        time.sleep(2)  # Give it time to start
        logger.info("✅ Kenny startup command sent")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to start Kenny: {e}")
        return False

def start_ace():
    """Check/start Ace (ACVA)"""
    try:
        from acva_armoury_crate_integration import ACVAArmouryCrateIntegration
        logger.info("🔍 Checking for Ace (ACVA)...")

        ace = ACVAArmouryCrateIntegration(project_root)
        hwnd = ace.find_armoury_crate_va()

        if hwnd:
            logger.info("✅ Ace (ACVA) window found")
            # Try to make it visible
            try:
                import ctypes
                user32 = ctypes.windll.user32
                user32.ShowWindow(hwnd, 1)  # SW_SHOWNORMAL
                user32.SetForegroundWindow(hwnd)
                logger.info("✅ Attempted to make Ace visible")
            except Exception as e:
                logger.warning(f"Could not make Ace visible: {e}")
            return True
        else:
            logger.warning("⚠️  Ace (ACVA) window not found")
            logger.info("   Is Armoury Crate running? Ace may not be available.")
            return False
    except ImportError:
        logger.warning("⚠️  Ace integration not available")
        return False
    except Exception as e:
        logger.warning(f"⚠️  Could not check Ace: {e}")
        return False

def main():
    """Main function"""
    print("=" * 80)
    print("🤖 ENSURING VIRTUAL ASSISTANTS ARE VISIBLE")
    print("=" * 80)
    print()

    # Start Kenny
    kenny_started = start_kenny()
    time.sleep(1)

    # Check/Start Ace
    ace_found = start_ace()
    time.sleep(1)

    print()
    print("=" * 80)
    print("📊 STATUS")
    print("=" * 80)
    print()

    if kenny_started:
        print("✅ Kenny: Startup command sent")
        print("   Look for a red circle with hexagonal helmet on your desktop")
        print("   Window size: 120x120px")
    else:
        print("❌ Kenny: Failed to start")

    if ace_found:
        print("✅ Ace: Window found and made visible")
        print("   Should be visible if Armoury Crate is running")
    else:
        print("⚠️  Ace: Not found or not available")
        print("   Make sure Armoury Crate is running")

    print()
    print("=" * 80)
    print()
    print("If you still don't see the VAs:")
    print("  1. Check Task Manager for Python processes")
    print("  2. Look for windows that might be off-screen")
    print("  3. Try running: python scripts/python/start_kenny_visible.py")
    print("  4. Check logs for errors")
    print()
    print("=" * 80)

if __name__ == "__main__":


    main()