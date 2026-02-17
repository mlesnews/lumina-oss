#!/usr/bin/env python3
"""
JARVIS Continuous Git Commit

Continuously commits changes to prevent unstaged changes.
Runs automatically in background or after operations.
"""

import sys
import subprocess
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from jarvis_auto_git_manager import JARVISAutoGitManager
    AUTO_GIT_AVAILABLE = True
except ImportError:
    AUTO_GIT_AVAILABLE = False
    JARVISAutoGitManager = None

logger = get_logger("JARVISContinuousGit")


class JARVISContinuousGitCommit:
    """
    Continuously commits changes to keep Git clean

    Prevents accumulation of unstaged changes
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        if AUTO_GIT_AVAILABLE:
            self.git_manager = JARVISAutoGitManager(project_root)
        else:
            self.git_manager = None

        self.running = False
        self.commit_thread = None
        self.commit_interval = 60  # Commit every 60 seconds if changes exist

    def start_continuous_commits(self, interval: int = 60):
        """Start continuous commit monitoring"""
        if not self.git_manager:
            self.logger.error("Auto Git Manager not available")
            return False

        self.commit_interval = interval
        self.running = True

        self.commit_thread = threading.Thread(
            target=self._continuous_commit_loop,
            daemon=True
        )
        self.commit_thread.start()

        self.logger.info(f"✅ Continuous Git commits started (interval: {interval}s)")
        return True

    def _continuous_commit_loop(self):
        """Continuous commit loop"""
        while self.running:
            try:
                changes = self.git_manager.get_unstaged_changes()

                if changes['count'] > 0:
                    self.logger.info(f"📦 Auto-committing {changes['count']} unstaged changes...")
                    result = self.git_manager.auto_stage_and_commit(
                        operation="continuous_auto_commit"
                    )

                    if result.get('success'):
                        self.logger.info(f"✅ Committed {result.get('changes_count', 0)} changes")
                    else:
                        self.logger.warning(f"⚠️ Commit failed: {result.get('error', 'unknown')[:100]}")

                time.sleep(self.commit_interval)

            except Exception as e:
                self.logger.error(f"Error in continuous commit loop: {e}")
                time.sleep(self.commit_interval)

    def stop_continuous_commits(self):
        """Stop continuous commits"""
        self.running = False
        if self.commit_thread:
            self.commit_thread.join(timeout=5)
        self.logger.info("✅ Continuous Git commits stopped")

    def commit_now(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """Commit changes immediately"""
        if not self.git_manager:
            return {
                'success': False,
                'error': 'Auto Git Manager not available'
            }

        return self.git_manager.auto_stage_and_commit(operation=operation)


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Continuous Git Commit")
    parser.add_argument("--start", action="store_true", help="Start continuous commits")
    parser.add_argument("--stop", action="store_true", help="Stop continuous commits")
    parser.add_argument("--commit-now", action="store_true", help="Commit changes now")
    parser.add_argument("--interval", type=int, default=60, help="Commit interval in seconds")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    continuous = JARVISContinuousGitCommit(project_root)

    if args.start:
        continuous.start_continuous_commits(args.interval)
        print(f"\n✅ Continuous Git commits started")
        print(f"   Interval: {args.interval} seconds")
        print("   Press Ctrl+C to stop")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            continuous.stop_continuous_commits()

    elif args.commit_now:
        result = continuous.commit_now("manual_commit")
        if result.get('success'):
            print(f"\n✅ Committed {result.get('changes_count', 0)} changes")
            print(f"   Commit: {result.get('commit_hash', 'unknown')}")
        else:
            print(f"❌ Error: {result.get('error', 'unknown')}")

    else:
        print("Usage:")
        print("  python jarvis_continuous_git_commit.py --start        # Start continuous commits")
        print("  python jarvis_continuous_git_commit.py --commit-now  # Commit now")


if __name__ == "__main__":


    main()