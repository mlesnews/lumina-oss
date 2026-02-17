#!/usr/bin/env python3
"""
Restart Cursor IDE Properly

Properly restarts Cursor IDE by:
1. Saving all work
2. Gracefully closing Cursor
3. Waiting for complete shutdown
4. Restarting Cursor IDE
5. Restoring workspace

This ensures a proper restart, not just a shutdown.
"""

import sys
import time
import subprocess
from pathlib import Path
from typing import Optional

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
        get_logger = lambda name: logging.getLogger(name)

logger = get_logger("RestartCursor")


def find_cursor_executable() -> Path:
    """Find Cursor IDE executable"""
    possible_paths = [
        Path("C:/Users") / Path.home().name / "AppData/Local/Programs/cursor/Cursor.exe",
        Path("C:/Program Files/Cursor/Cursor.exe"),
        Path("C:/Program Files (x86)/Cursor/Cursor.exe"),
    ]

    for path in possible_paths:
        if path.exists():
            logger.info(f"✅ Found Cursor at: {path}")
            return path

    # Try to find in PATH
    try:
        result = subprocess.run(
            ["where", "cursor"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0 and result.stdout.strip():
            cursor_path = Path(result.stdout.strip().split('\n')[0])
            if cursor_path.exists():
                logger.info(f"✅ Found Cursor in PATH: {cursor_path}")
                return cursor_path
    except Exception:
        pass

    logger.warning("⚠️  Cursor executable not found in common locations")
    return None


def save_work():
    """Save all work in Cursor IDE"""
    try:
        import pyautogui
        import keyboard

        # Send Ctrl+S to save all
        keyboard.press_and_release('ctrl+s')
        time.sleep(0.5)
        logger.info("✅ Work saved")
        return True
    except ImportError:
        logger.warning("⚠️  pyautogui/keyboard not available - skipping save")
        return False
    except Exception as e:
        logger.warning(f"⚠️  Could not save work: {e}")
        return False


def close_cursor_gracefully():
    """Gracefully close Cursor IDE"""
    try:
        import psutil

        # Find Cursor processes
        cursor_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                if proc.info['name'] and 'cursor' in proc.info['name'].lower():
                    cursor_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if not cursor_processes:
            logger.info("✅ Cursor is not running")
            return True

        logger.info(f"📋 Found {len(cursor_processes)} Cursor process(es)")

        # Try graceful shutdown first
        try:
            import pyautogui
            import keyboard

            # Send Alt+F4 to close gracefully
            keyboard.press_and_release('alt+f4')
            time.sleep(2)

            # Check if still running
            still_running = [
                p for p in cursor_processes
                if p.is_running()
            ]

            if not still_running:
                logger.info("✅ Cursor closed gracefully")
                return True
        except Exception:
            pass

        # If graceful didn't work, terminate
        logger.info("⚠️  Graceful close failed, terminating processes...")
        for proc in cursor_processes:
            try:
                proc.terminate()
            except Exception as e:
                logger.warning(f"⚠️  Could not terminate {proc.pid}: {e}")

        # Wait for processes to end
        gone, alive = psutil.wait_procs(cursor_processes, timeout=5)
        for proc in alive:
            try:
                proc.kill()
                logger.warning(f"⚠️  Force killed {proc.pid}")
            except Exception:
                pass

        logger.info("✅ Cursor processes terminated")
        return True

    except ImportError:
        logger.warning("⚠️  psutil not available - using alternative method")
        # Alternative: Use taskkill
        try:
            subprocess.run(
                ["taskkill", "/F", "/IM", "Cursor.exe"],
                capture_output=True,
                check=False
            )
            time.sleep(2)
            logger.info("✅ Cursor terminated via taskkill")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to close Cursor: {e}")
            return False
    except Exception as e:
        logger.error(f"❌ Error closing Cursor: {e}")
        return False


def restart_cursor(workspace_path: Optional[Path] = None):
    """Restart Cursor IDE with workspace"""
    cursor_exe = find_cursor_executable()
    if not cursor_exe:
        logger.error("❌ Cursor executable not found")
        logger.info("💡 Please restart Cursor IDE manually")
        return False

    # Start Cursor with workspace
    try:
        # Always use workspace path - default to project root if not specified
        if workspace_path is None:
            workspace_path = project_root

        # Use --folder flag to open as workspace (not just file)
        cmd = [str(cursor_exe), "--folder", str(workspace_path)]

        logger.info(f"📂 Opening workspace: {workspace_path}")
        subprocess.Popen(cmd, shell=True)
        logger.info("✅ Cursor IDE restarted with workspace")
        time.sleep(3)  # Give it time to start
        return True
    except Exception as e:
        logger.error(f"❌ Failed to start Cursor: {e}")
        return False


def main():
    try:
        """Main restart process"""
        import argparse

        parser = argparse.ArgumentParser(description="Restart Cursor IDE Properly")
        parser.add_argument(
            "--workspace",
            type=str,
            help="Workspace path to open after restart"
        )
        parser.add_argument("--skip-save", action="store_true", help="Skip saving work")

        args = parser.parse_args()

        logger.info("=" * 70)
        logger.info("🔄 Restarting Cursor IDE")
        logger.info("=" * 70)

        # Step 1: Save work
        if not args.skip_save:
            logger.info("1️⃣  Saving work...")
            save_work()
            time.sleep(1)

        # Step 2: Close Cursor gracefully
        logger.info("2️⃣  Closing Cursor IDE...")
        if not close_cursor_gracefully():
            logger.error("❌ Failed to close Cursor")
            return 1

        # Step 3: Wait for complete shutdown
        logger.info("3️⃣  Waiting for shutdown...")
        time.sleep(3)

        # Step 4: Restart Cursor
        logger.info("4️⃣  Restarting Cursor IDE...")
        workspace = Path(args.workspace) if args.workspace else project_root
        if not restart_cursor(workspace):
            return 1

        logger.info("")
        logger.info("=" * 70)
        logger.info("✅ Cursor IDE restarted successfully!")
        logger.info("=" * 70)
        logger.info("")
        logger.info("📋 Next steps:")
        logger.info("   • Keybindings should now be active")
        logger.info("   • Use Ctrl+Alt+Enter for Keep All / Accept All")
        logger.info("")

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())