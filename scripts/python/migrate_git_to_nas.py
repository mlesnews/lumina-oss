#!/usr/bin/env python3
"""
Git Repository Migration to NAS

Long-term solution for Dropbox Git Dilemma:
- Moves .git directories from Dropbox to NAS
- Creates gitdir pointer files to link working directories to NAS .git
- Enables git operations without Dropbox filesystem limitations

Author: <COMPANY_NAME> LLC
Date: 2025-01-24
Issue: Dropbox filesystem limitations prevent git from writing to .git/logs/HEAD
Solution: Store .git on NAS, keep working directory in Dropbox
"""

from __future__ import annotations

import subprocess
import shutil
import sys
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
import json

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)


class GitToNASMigrator:
    """Migrate git repositories from Dropbox to NAS storage"""

    # NAS Configuration
    NAS_IP = "<NAS_PRIMARY_IP>"
    NAS_BASE_PATH = f"\\\\{NAS_IP}\\backups\\MATT_Backups"
    NAS_GIT_REPOS_PATH = f"{NAS_BASE_PATH}\\git_repos"

    def __init__(self, dry_run: bool = False):
        """
        Initialize migrator.

        Args:
            dry_run: If True, show what would be done without making changes
        """
        self.dry_run = dry_run
        self.logger = get_logger("GitToNASMigrator")
        self.nas_git_path = Path(self.NAS_GIT_REPOS_PATH)
        self.migration_log: List[Dict[str, any]] = []

    def check_nas_accessible(self) -> bool:
        """Check if NAS path is accessible"""
        try:
            if not self.nas_git_path.exists():
                if not self.dry_run:
                    self.nas_git_path.mkdir(parents=True, exist_ok=True)
                else:
                    self.logger.info(f"[DRY RUN] Would create: {self.nas_git_path}")
                return True

            # Test write access
            test_file = self.nas_git_path / ".test_write"
            if not self.dry_run:
                test_file.write_text("test")
                test_file.unlink()
            else:
                self.logger.info(f"[DRY RUN] Would test write access: {test_file}")

            return True
        except Exception as e:
            self.logger.error(f"NAS not accessible: {e}")
            return False

    def find_git_repos(self, search_path: Path) -> List[Path]:
        try:
            """
            Find all git repositories in a directory tree.

            Args:
                search_path: Root directory to search

            Returns:
                List of paths containing .git directories
            """
            git_repos = []

            # Check if search_path itself is a git repo
            if (search_path / ".git").exists():
                git_repos.append(search_path)

            # Search subdirectories (but not inside .git directories)
            for item in search_path.iterdir():
                if item.name == ".git":
                    continue
                if item.is_dir() and not item.name.startswith("."):
                    git_repos.extend(self.find_git_repos(item))

            return git_repos

        except Exception as e:
            self.logger.error(f"Error in find_git_repos: {e}", exc_info=True)
            raise
    def get_repo_name(self, repo_path: Path) -> str:
        """Get repository name for NAS storage"""
        # Use the directory name as repo name
        return repo_path.name

    def migrate_repo(self, repo_path: Path) -> bool:
        """
        Migrate a single git repository to NAS.

        Args:
            repo_path: Path to git repository (working directory)

        Returns:
            True if migration succeeded, False otherwise
        """
        repo_path = Path(repo_path).resolve()
        git_dir = repo_path / ".git"

        if not git_dir.exists():
            self.logger.warning(f"No .git directory found in {repo_path}")
            return False

        # Check if already migrated (has gitdir pointer)
        gitdir_file = repo_path / ".git"
        if gitdir_file.is_file():
            existing_gitdir = gitdir_file.read_text().strip()
            if "git_repos" in existing_gitdir:
                self.logger.info(f"Repository {repo_path} already migrated to NAS")
                return True

        repo_name = self.get_repo_name(repo_path)
        nas_git_dir = self.nas_git_path / repo_name / ".git"

        self.logger.info(f"\n{'[DRY RUN] ' if self.dry_run else ''}Migrating: {repo_path}")
        self.logger.info(f"  From: {git_dir}")
        self.logger.info(f"  To:   {nas_git_dir}")

        try:
            # Step 1: Ensure NAS directory exists
            nas_repo_dir = nas_git_dir.parent
            if not self.dry_run:
                nas_repo_dir.mkdir(parents=True, exist_ok=True)
            else:
                self.logger.info(f"[DRY RUN] Would create: {nas_repo_dir}")

            # Step 2: Move .git directory to NAS
            if not self.dry_run:
                if nas_git_dir.exists():
                    # Backup existing if any
                    backup_name = f".git.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    shutil.move(str(nas_git_dir), str(nas_repo_dir / backup_name))
                    self.logger.info(f"  Backed up existing: {backup_name}")

                # Move .git to NAS
                shutil.move(str(git_dir), str(nas_git_dir))
                self.logger.info(f"  ✓ Moved .git to NAS")
            else:
                self.logger.info(f"[DRY RUN] Would move: {git_dir} -> {nas_git_dir}")

            # Step 3: Create gitdir pointer file
            gitdir_content = str(nas_git_dir.resolve())
            if not self.dry_run:
                gitdir_file.write_text(f"gitdir: {gitdir_content}\n")
                self.logger.info(f"  ✓ Created gitdir pointer: {gitdir_file}")
            else:
                self.logger.info(f"[DRY RUN] Would create gitdir pointer: {gitdir_file}")
                self.logger.info(f"  Content: gitdir: {gitdir_content}")

            # Step 4: Verify migration
            if not self.dry_run:
                result = subprocess.run(
                    ["git", "status"],
                    cwd=str(repo_path),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    self.logger.info(f"  ✓ Git repository verified - migration successful!")
                else:
                    self.logger.warning(f"  ⚠ Git verification failed: {result.stderr}")
                    return False

            # Log migration
            self.migration_log.append({
                "repo_path": str(repo_path),
                "repo_name": repo_name,
                "nas_git_dir": str(nas_git_dir),
                "migrated_at": datetime.now().isoformat(),
                "status": "success" if not self.dry_run else "dry_run"
            })

            return True

        except Exception as e:
            self.logger.error(f"  ✗ Migration failed: {e}", exc_info=True)
            self.migration_log.append({
                "repo_path": str(repo_path),
                "repo_name": repo_name,
                "error": str(e),
                "migrated_at": datetime.now().isoformat(),
                "status": "failed"
            })
            return False

    def migrate_all_repos(self, search_paths: List[Path]) -> Dict[str, any]:
        try:
            """
            Migrate all git repositories found in search paths.

            Args:
                search_paths: List of directories to search for git repos

            Returns:
                Migration summary
            """
            if not self.check_nas_accessible():
                return {
                    "success": False,
                    "error": "NAS not accessible",
                    "migrated": 0,
                    "failed": 0
                }

            all_repos = []
            for search_path in search_paths:
                search_path = Path(search_path).resolve()
                if not search_path.exists():
                    self.logger.warning(f"Search path does not exist: {search_path}")
                    continue

                repos = self.find_git_repos(search_path)
                all_repos.extend(repos)
                self.logger.info(f"Found {len(repos)} git repositories in {search_path}")

            if not all_repos:
                self.logger.warning("No git repositories found")
                return {
                    "success": True,
                    "migrated": 0,
                    "failed": 0,
                    "repos_found": 0
                }

            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Found {len(all_repos)} git repositories to migrate")
            self.logger.info(f"{'='*60}\n")

            migrated = 0
            failed = 0

            for repo in all_repos:
                if self.migrate_repo(repo):
                    migrated += 1
                else:
                    failed += 1

            summary = {
                "success": failed == 0,
                "migrated": migrated,
                "failed": failed,
                "repos_found": len(all_repos),
                "nas_path": str(self.nas_git_path),
                "migration_log": self.migration_log
            }

            return summary

        except Exception as e:
            self.logger.error(f"Error in migrate_all_repos: {e}", exc_info=True)
            raise
    def save_migration_log(self, log_path: Optional[Path] = None):
        try:
            """Save migration log to file"""
            if log_path is None:
                log_path = Path("git_migration_log.json")

            log_data = {
                "migration_date": datetime.now().isoformat(),
                "nas_path": str(self.nas_git_path),
                "dry_run": self.dry_run,
                "migrations": self.migration_log
            }

            if not self.dry_run:
                with open(log_path, 'w', encoding='utf-8') as f:
                    json.dump(log_data, f, indent=2)
                self.logger.info(f"Migration log saved: {log_path}")
            else:
                self.logger.info(f"[DRY RUN] Would save migration log: {log_path}")


        except Exception as e:
            self.logger.error(f"Error in save_migration_log: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrate git repositories from Dropbox to NAS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run to see what would be migrated
  python migrate_git_to_nas.py --dry-run

  # Migrate all repos in Dropbox my_projects
  python migrate_git_to_nas.py --path "C:\\Users\\mlesn\\Dropbox\\my_projects"

  # Migrate specific repository
  python migrate_git_to_nas.py --path "C:\\Users\\mlesn\\Dropbox\\my_projects\\.lumina"
        """
    )
    parser.add_argument(
        "--path",
        type=str,
        nargs="+",
        default=["C:\\Users\\mlesn\\Dropbox\\my_projects"],
        help="Path(s) to search for git repositories (default: Dropbox my_projects)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--log",
        type=str,
        help="Path to save migration log (default: git_migration_log.json)"
    )

    args = parser.parse_args()

    migrator = GitToNASMigrator(dry_run=args.dry_run)

    if args.dry_run:
        print("\n" + "="*60)
        print("DRY RUN MODE - No changes will be made")
        print("="*60 + "\n")

    search_paths = [Path(p) for p in args.path]
    summary = migrator.migrate_all_repos(search_paths)

    # Save log
    log_path = Path(args.log) if args.log else None
    migrator.save_migration_log(log_path)

    # Print summary
    print("\n" + "="*60)
    print("MIGRATION SUMMARY")
    print("="*60)
    print(f"Repositories found: {summary['repos_found']}")
    print(f"Successfully migrated: {summary['migrated']}")
    print(f"Failed: {summary['failed']}")
    print(f"NAS path: {summary['nas_path']}")
    print("="*60)

    if summary['failed'] > 0:
        return 1

    return 0


if __name__ == "__main__":



    sys.exit(main())