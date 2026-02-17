#!/usr/bin/env python3
"""
Git Commit Retry Script

Handles git commits with Dropbox filesystem retry logic.
Monitors Dropbox sync status and retries commits when filesystem is stable.

Author: <COMPANY_NAME> LLC
Date: 2025-01-24
Issue: Dropbox filesystem limitations prevent git from writing to .git/logs/HEAD
"""

from __future__ import annotations

import subprocess
import time
import sys
from pathlib import Path
from typing import Optional
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
logger = get_logger("git_commit_retry")


try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class GitCommitRetry:
    """Retry git commits with Dropbox filesystem handling"""

    def __init__(self, repo_path: Path, max_retries: int = 10, retry_delay: int = 5) -> None:
        """
        Initialize retry handler.

        Args:
            repo_path: Path to git repository
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries (seconds)
        """
        self.repo_path = Path(repo_path)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = get_logger("GitCommitRetry")

    def check_dropbox_sync(self) -> bool:
        """
        Check if Dropbox sync appears to be active/stable.

        Returns:
            True if Dropbox appears synced, False otherwise
        """
        # Simple heuristic: check if .git directory is accessible and writable
        git_dir = self.repo_path / ".git"
        if not git_dir.exists():
            return False

        # Try to create a test file in .git to check filesystem
        test_file = git_dir / ".test_write"
        try:
            test_file.write_text("test")
            test_file.unlink()
            return True
        except (OSError, PermissionError, IOError) as e:
            self.logger.debug(f"Filesystem check failed: {e}")
            return False

    def commit(self, message: str, check_sync: bool = True) -> bool:
        """
        Attempt git commit with retry logic.

        Args:
            message: Commit message
            check_sync: Whether to check Dropbox sync before committing

        Returns:
            True if commit succeeded, False otherwise
        """
        if check_sync:
            if not self.check_dropbox_sync():
                self.logger.warning("Dropbox sync check failed, but proceeding with retry logic")

        for attempt in range(1, self.max_retries + 1):
            try:
                self.logger.info(f"Commit attempt {attempt}/{self.max_retries}...")

                result = subprocess.run(
                    ["git", "commit", "-m", message],
                    cwd=str(self.repo_path),
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    self.logger.info("✓ Commit successful!")
                    if result.stdout:
                        self.logger.info(result.stdout.strip())
                    return True
                else:
                    error_msg = result.stderr.strip()
                    self.logger.warning(f"Commit failed: {error_msg}")

                    # Check if it's the Dropbox filesystem issue
                    if "Function not implemented" in error_msg or "unable to append" in error_msg:
                        if attempt < self.max_retries:
                            self.logger.info(f"Dropbox filesystem issue detected. Waiting {self.retry_delay}s before retry...")
                            time.sleep(self.retry_delay)
                            continue
                    else:
                        # Different error, don't retry
                        self.logger.error(f"Non-retryable error: {error_msg}")
                        return False

            except subprocess.TimeoutExpired:
                self.logger.warning(f"Commit timed out on attempt {attempt}")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                    continue
            except Exception as e:
                self.logger.error(f"Unexpected error on attempt {attempt}: {e}")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                    continue

        self.logger.error(f"Failed to commit after {self.max_retries} attempts")
        return False

    def get_staged_files(self) -> list[str]:
        """Get list of staged files"""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
        except Exception as e:
            self.logger.error(f"Error getting staged files: {e}")
        return []


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Git commit with Dropbox retry logic")
        parser.add_argument("--repo", type=str, default=".", help="Repository path")
        parser.add_argument("--message", type=str, required=True, help="Commit message")
        parser.add_argument("--max-retries", type=int, default=10, help="Maximum retry attempts")
        parser.add_argument("--retry-delay", type=int, default=5, help="Delay between retries (seconds)")
        parser.add_argument("--no-sync-check", action="store_true", help="Skip Dropbox sync check")

        args = parser.parse_args()

        repo_path = Path(args.repo).resolve()

        retry = GitCommitRetry(
            repo_path=repo_path,
            max_retries=args.max_retries,
            retry_delay=args.retry_delay
        )

        # Show staged files
        staged = retry.get_staged_files()
        if staged:
            print(f"\nStaged files ({len(staged)}):")
            for f in staged[:10]:  # Show first 10
                print(f"  {f}")
            if len(staged) > 10:
                print(f"  ... and {len(staged) - 10} more")
        else:
            print("No files staged for commit")
            return 1

        # Attempt commit
        success = retry.commit(
            message=args.message,
            check_sync=not args.no_sync_check
        )

        return 0 if success else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    sys.exit(main())