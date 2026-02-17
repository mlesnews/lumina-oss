#!/usr/bin/env python3
"""
Auto-Save Terminal Fix Integration

Monitors file saves (including auto-save) and automatically fixes terminal
sequence issues when files are saved. This ensures terminal stays healthy
during active development.

Tags: #AUTOSAVE #TERMINAL #FIX #FILE_WATCHER @JARVIS @LUMINA
"""

import sys
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    # Create dummy classes for fallback
    class Observer:
        pass
    class FileSystemEventHandler:
        pass

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from terminal_sequence_powershell_fix import send_sequence_reset
    from terminal_sequence_manager import get_terminal_manager
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from terminal_sequence_powershell_fix import send_sequence_reset
        from terminal_sequence_manager import get_terminal_manager
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        def get_logger(name):
            return logging.getLogger(name)
        send_sequence_reset = None
        get_terminal_manager = None

logger = get_logger("AutoSaveTerminalFix")


class AutoSaveTerminalFixHandler(FileSystemEventHandler):
    """
    File system event handler that fixes terminal on file saves.

    Triggers terminal sequence fix whenever a file is saved (including auto-save).
    """

    def __init__(self):
        """Initialize handler"""
        self.last_fix_time = None
        self.min_fix_interval = 1.0  # Don't fix more than once per second
        self.fix_count = 0
        self.ignored_extensions = {'.tmp', '.swp', '.bak', '.log', '.jsonl'}
        self.project_paths = set()

        # Track project root
        self.project_root = project_root

        logger.info("✅ Auto-Save Terminal Fix handler initialized")

    def _should_process_file(self, file_path: Path) -> bool:
        """
        Check if file should trigger terminal fix.

        Args:
            file_path: Path to file that was saved

        Returns:
            True if file should trigger fix
        """
        # Ignore temporary files
        if file_path.suffix.lower() in self.ignored_extensions:
            return False

        # Only process files in project
        try:
            file_path.resolve().relative_to(self.project_root)
            return True
        except ValueError:
            # File not in project
            return False

    def _can_fix_now(self) -> bool:
        """Check if we can fix now (rate limiting)"""
        if self.last_fix_time is None:
            return True

        time_since_last = (datetime.now() - self.last_fix_time).total_seconds()
        return time_since_last >= self.min_fix_interval

    def _fix_terminal(self):
        """Fix terminal sequence issues"""
        try:
            # Try aggressive restart first (actually restarts terminal)
            try:
                from terminal_restart_manager import force_terminal_reinit
                if force_terminal_reinit():
                    logger.debug("   ✅ Terminal restarted (auto-save trigger)")
                    self.fix_count += 1
                    self.last_fix_time = datetime.now()
                    return
            except ImportError:
                pass
            except Exception as e:
                logger.debug("   Restart error: %s", e)

            # Fallback: Send direct sequence reset
            if send_sequence_reset:
                send_sequence_reset()
                logger.debug("   ✅ Terminal fix sent (auto-save trigger)")
            else:
                # Fallback: use terminal manager
                if get_terminal_manager:
                    manager = get_terminal_manager()
                    manager.reinitialize_terminal()
                    logger.debug("   ✅ Terminal re-initialized (auto-save trigger)")

            self.fix_count += 1
            self.last_fix_time = datetime.now()

        except Exception as e:
            logger.debug("   ⚠️  Terminal fix error: %s", e)

    def on_modified(self, event):
        try:
            """Handle file modification events"""
            if event.is_directory:
                return

            file_path = Path(event.src_path)

            # Check if we should process this file
            if not self._should_process_file(file_path):
                return

            # Rate limiting
            if not self._can_fix_now():
                return

            # Fix terminal on file save
            logger.debug("   📝 File saved: %s - fixing terminal...", file_path.name)
            self._fix_terminal()

        except Exception as e:
            self.logger.error(f"Error in on_modified: {e}", exc_info=True)
            raise
    def on_created(self, event):
        try:
            """Handle file creation events (sometimes auto-save creates new files)"""
            if event.is_directory:
                return

            file_path = Path(event.src_path)

            # Only process if it's a save-like operation (not temp files)
            if not self._should_process_file(file_path):
                return

            # Rate limiting
            if not self._can_fix_now():
                return

            # Fix terminal
            logger.debug("   📝 File created: %s - fixing terminal...", file_path.name)
            self._fix_terminal()


        except Exception as e:
            self.logger.error(f"Error in on_created: {e}", exc_info=True)
            raise
class AutoSaveTerminalFix:
    """
    Auto-save terminal fix monitor.

    Watches for file saves and automatically fixes terminal sequences.
    """

    def __init__(self, watch_path: Path = None):
        """
        Initialize auto-save terminal fix.

        Args:
            watch_path: Path to watch (default: project root)
        """
        if watch_path is None:
            watch_path = project_root

        self.watch_path = Path(watch_path)
        self.observer = None
        self.handler = AutoSaveTerminalFixHandler()
        self.running = False

        logger.info("✅ Auto-Save Terminal Fix initialized")
        logger.info("   Watching: %s", self.watch_path)

    def start(self):
        """Start watching for file saves"""
        if not WATCHDOG_AVAILABLE:
            logger.warning("   ⚠️  watchdog not installed - auto-save fix unavailable")
            logger.info("   Install with: pip install watchdog")
            return

        if self.running:
            logger.warning("   Already watching for file saves")
            return

        try:
            self.observer = Observer()
            self.observer.schedule(
                self.handler,
                str(self.watch_path),
                recursive=True
            )
            self.observer.start()
            self.running = True
            logger.info("🚀 Auto-Save Terminal Fix started")
            logger.info("   Terminal will be fixed automatically on file saves")
        except Exception as e:
            logger.error("   ❌ Failed to start file watcher: %s", e)
            self.running = False

    def stop(self):
        """Stop watching for file saves"""
        if not self.running:
            return

        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=2.0)

        self.running = False
        logger.info("⏹️  Auto-Save Terminal Fix stopped")

    def get_stats(self) -> dict:
        """Get monitoring statistics"""
        return {
            "running": self.running,
            "watch_path": str(self.watch_path),
            "fix_count": self.handler.fix_count,
            "last_fix_time": self.handler.last_fix_time.isoformat() if self.handler.last_fix_time else None
        }


# Global instance
_autosave_fix_instance = None
_autosave_fix_lock = threading.Lock()


def get_autosave_terminal_fix() -> AutoSaveTerminalFix:
    """Get or create global auto-save terminal fix instance"""
    global _autosave_fix_instance  # pylint: disable=global-statement

    with _autosave_fix_lock:
        if _autosave_fix_instance is None:
            _autosave_fix_instance = AutoSaveTerminalFix()
            # Auto-start
            _autosave_fix_instance.start()
            logger.info("✅ Auto-Save Terminal Fix initialized and started")
        elif not _autosave_fix_instance.running:
            # Restart if stopped
            _autosave_fix_instance.start()
        return _autosave_fix_instance


def start_autosave_fix():
    """Start auto-save terminal fix"""
    monitor = get_autosave_terminal_fix()
    monitor.start()
    return monitor


def stop_autosave_fix():
    """Stop auto-save terminal fix"""
    global _autosave_fix_instance  # pylint: disable=global-statement

    if _autosave_fix_instance:
        _autosave_fix_instance.stop()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Auto-Save Terminal Fix")
    parser.add_argument("--start", action="store_true", help="Start watching")
    parser.add_argument("--stop", action="store_true", help="Stop watching")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--watch-path", type=Path, help="Path to watch (default: project root)")

    args = parser.parse_args()

    if args.stop:
        stop_autosave_fix()
        logger.info("✅ Auto-Save Terminal Fix stopped")
        return

    if args.stats:
        monitor = get_autosave_terminal_fix()
        stats = monitor.get_stats()
        print("\n📊 Auto-Save Terminal Fix Statistics:")
        print(f"   Running: {stats['running']}")
        print(f"   Watch path: {stats['watch_path']}")
        print(f"   Fix count: {stats['fix_count']}")
        print(f"   Last fix: {stats['last_fix_time']}")
        return

    # Default: start and keep running
    watch_path = args.watch_path if args.watch_path else None
    monitor = AutoSaveTerminalFix(watch_path=watch_path)
    monitor.start()

    logger.info("✅ Auto-Save Terminal Fix running")
    logger.info("   Terminal will be fixed automatically whenever files are saved")
    logger.info("   Use --stats to check status")
    logger.info("   Use --stop to stop")

    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        logger.info("\n⏹️  Stopping...")
        monitor.stop()


if __name__ == "__main__":


    main()