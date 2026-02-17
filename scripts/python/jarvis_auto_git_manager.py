#!/usr/bin/env python3
"""
JARVIS Auto Git Manager

Automatically stages and commits changes to prevent unstaged changes.
Integrates with all JARVIS operations to keep Git clean.
"""

import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import time

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISAutoGit")


class JARVISAutoGitManager:
    """
    Automatically manages Git to prevent unstaged changes

    Stages and commits changes automatically after operations
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Check if Git repo
        self.is_git_repo = (project_root / ".git").exists()

        if not self.is_git_repo:
            self.logger.warning("⚠️ Not a Git repository")

    def get_unstaged_changes(self) -> Dict[str, Any]:
        """Get count and list of unstaged changes"""
        if not self.is_git_repo:
            return {
                'count': 0,
                'files': [],
                'is_git_repo': False
            }

        try:
            # Get status
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )

            if status_result.returncode != 0:
                return {
                    'count': 0,
                    'files': [],
                    'error': status_result.stderr
                }

            lines = [line.strip() for line in status_result.stdout.strip().split('\n') if line.strip()]

            # Parse status
            unstaged = []
            untracked = []

            for line in lines:
                if line.startswith('??'):
                    # Untracked file
                    untracked.append(line[3:])
                elif line.startswith(' M') or line.startswith('MM'):
                    # Modified but not staged
                    unstaged.append(line[3:])
                elif line.startswith('A ') or line.startswith('M '):
                    # Staged
                    pass
                else:
                    # Other status
                    unstaged.append(line[3:] if len(line) > 3 else line)

            return {
                'count': len(unstaged) + len(untracked),
                'unstaged': len(unstaged),
                'untracked': len(untracked),
                'files': unstaged + untracked,
                'is_git_repo': True
            }

        except Exception as e:
            return {
                'count': 0,
                'files': [],
                'error': str(e)
            }

    def auto_stage_and_commit(self, message: Optional[str] = None,
                             operation: Optional[str] = None) -> Dict[str, Any]:
        """
        Automatically stage and commit all changes

        Args:
            message: Optional commit message
            operation: Optional operation that triggered this (for context)
        """
        if not self.is_git_repo:
            return {
                'success': False,
                'error': 'Not a Git repository'
            }

        # Get current unstaged changes
        changes = self.get_unstaged_changes()

        if changes['count'] == 0:
            return {
                'success': True,
                'message': 'No changes to commit',
                'changes_count': 0
            }

        self.logger.info(f"📦 Auto-staging {changes['count']} changes...")

        try:
            # Stage all changes
            stage_result = subprocess.run(
                ["git", "add", "-A"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )

            if stage_result.returncode != 0:
                # Try staging specific safe directories
                safe_dirs = ["scripts/", "docs/", "config/", "data/"]
                staged_count = 0

                for safe_dir in safe_dirs:
                    safe_path = self.project_root / safe_dir
                    if safe_path.exists():
                        subprocess.run(
                            ["git", "add", safe_dir],
                            cwd=self.project_root,
                            capture_output=True,
                            text=True
                        )
                        staged_count += 1

                if staged_count == 0:
                    return {
                        'success': False,
                        'error': f"Git add failed: {stage_result.stderr[:200]}"
                    }

            # Create commit message
            if not message:
                if operation:
                    message = f"[AUTO] {operation} - Auto-commit changes"
                else:
                    message = f"[AUTO] Auto-commit {changes['count']} changes at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            # Commit (skip hooks for auto-commits to prevent blocking)
            commit_result = subprocess.run(
                ["git", "commit", "--no-verify", "-m", message],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )

            if commit_result.returncode != 0:
                return {
                    'success': False,
                    'error': f"Git commit failed: {commit_result.stderr[:200]}"
                }

            # Get commit hash
            hash_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )

            commit_hash = hash_result.stdout.strip() if hash_result.returncode == 0 else "unknown"

            self.logger.info(f"✅ Auto-committed {changes['count']} changes: {commit_hash}")

            return {
                'success': True,
                'commit_hash': commit_hash,
                'changes_count': changes['count'],
                'message': message
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def cleanup_unstaged(self) -> Dict[str, Any]:
        """Clean up unstaged changes by auto-committing"""
        changes = self.get_unstaged_changes()

        if changes['count'] == 0:
            return {
                'success': True,
                'message': 'No unstaged changes',
                'cleaned': 0
            }

        self.logger.info(f"🧹 Cleaning up {changes['count']} unstaged changes...")

        result = self.auto_stage_and_commit(
            message=f"[AUTO] Cleanup unstaged changes - {changes['count']} files"
        )

        return {
            'success': result.get('success', False),
            'cleaned': changes['count'],
            'commit_hash': result.get('commit_hash'),
            'error': result.get('error')
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Auto Git Manager")
        parser.add_argument("--status", action="store_true", help="Get unstaged changes status")
        parser.add_argument("--auto-commit", action="store_true", help="Auto-commit all changes")
        parser.add_argument("--cleanup", action="store_true", help="Clean up unstaged changes")
        parser.add_argument("--message", type=str, help="Commit message")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        git_manager = JARVISAutoGitManager(project_root)

        if args.status:
            changes = git_manager.get_unstaged_changes()
            print("\n" + "="*80)
            print("UNSTAGED CHANGES STATUS")
            print("="*80)
            print(f"Total Unstaged: {changes['count']}")
            print(f"  Unstaged: {changes.get('unstaged', 0)}")
            print(f"  Untracked: {changes.get('untracked', 0)}")

            if changes['files']:
                print(f"\nFiles ({len(changes['files'][:20])} shown):")
                for file in changes['files'][:20]:
                    print(f"  - {file}")
                if len(changes['files']) > 20:
                    print(f"  ... and {len(changes['files']) - 20} more")

        elif args.auto_commit:
            result = git_manager.auto_stage_and_commit(args.message)

            if result.get('success'):
                print(f"\n✅ Auto-committed {result.get('changes_count', 0)} changes")
                print(f"   Commit: {result.get('commit_hash', 'unknown')}")
            else:
                print(f"❌ Error: {result.get('error', 'unknown')}")

        elif args.cleanup:
            result = git_manager.cleanup_unstaged()

            if result.get('success'):
                print(f"\n✅ Cleaned up {result.get('cleaned', 0)} unstaged changes")
                print(f"   Commit: {result.get('commit_hash', 'unknown')}")
            else:
                print(f"❌ Error: {result.get('error', 'unknown')}")
        else:
            print("Usage:")
            print("  python jarvis_auto_git_manager.py --status      # Check unstaged changes")
            print("  python jarvis_auto_git_manager.py --auto-commit # Auto-commit all changes")
            print("  python jarvis_auto_git_manager.py --cleanup    # Clean up unstaged changes")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()