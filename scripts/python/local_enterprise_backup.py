#!/usr/bin/env python3
"""
Local Enterprise Backup System

Automated backups to local GitHub Enterprise repository before pushing
to remote GitHub repositories. Ensures data safety and version control.

Tags: #BACKUP #LOCAL_ENTERPRISE #GIT #VERSION_CONTROL @JARVIS @LUMINA
"""

import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)

    def get_logger(name: str):
        return logging.getLogger(name)

logger = get_logger("LocalEnterpriseBackup")


class LocalEnterpriseBackup:
    """Local GitHub Enterprise backup system"""

    def __init__(self, base_path: Path):
        self.project_root = base_path
        self.config_file = base_path / "config" / "local_enterprise_backup.json"
        self.config = self._load_config()

        # Local enterprise repository path
        default_path = "B:\\git\\repositories\\lumina-backup"
        nas_path = self.config.get("local_repository", {}).get("path", default_path)
        self.local_repo_path = Path(nas_path)

        # Check if NAS path is accessible, fallback to local if not
        if not self._is_path_accessible(self.local_repo_path):
            # Fallback to local backup directory
            self.local_repo_path = self.project_root / "data" / "local_backup"
            logger.warning(
                "NAS path not accessible, using local fallback: %s", self.local_repo_path
            )

        self.local_repo_path.mkdir(parents=True, exist_ok=True)

        # Remote repositories
        self.remote_repos = self.config.get("remote_repositories", {})

    def _is_path_accessible(self, path: Path) -> bool:
        """Check if path is accessible (NAS drive mounted, etc.)"""
        try:
            # Check if parent directory exists
            parent = path.parent
            if parent.exists():
                return True
            # Try to access the root
            root = Path(path.parts[0] + "\\")
            return root.exists()
        except OSError:
            return False

    def _load_config(self) -> Dict[str, Any]:
        """Load backup configuration"""
        try:
            if self.config_file.exists():
                with open(self.config_file, encoding="utf-8") as f:
                    return json.load(f)
            return self._default_config()
        except Exception as e:
            logger.error("Error in _load_config: %s", e, exc_info=True)
            raise
    def _default_config(self) -> Dict[str, Any]:
        """Default backup configuration"""
        return {
            "version": "1.0.0",
            "local_repository": {
                "path": "B:\\git\\repositories\\lumina-backup",
                "name": "lumina-backup",
                "description": "Local enterprise backup repository"
            },
            "remote_repositories": {
                "public": {
                    "url": "https://github.com/mlesnews/lumina-ai",
                    "enabled": True,
                    "push_after_local": True
                },
                "private": {
                    "url": "https://github.com/mlesnews/lumina-enterprise",
                    "enabled": True,
                    "push_after_local": True
                }
            },
            "backup": {
                "enabled": True,
                "schedule": {
                    "frequency": "daily",
                    "time": "02:00"
                },
                "content": {
                    "include": [
                        "config/",
                        "scripts/",
                        "docs/",
                        "data/"
                    ],
        "exclude": [
        "node_modules/",
        "__pycache__/",
        "*.pyc",
        ".git/",
        "*.log",
        "*.tmp",
        "data/local_backup",
        "local_backup",
        "data/nas_cron",
        "personaplex/.cache/"
      ]
                }
            }
        }

    def initialize_local_repo(self) -> bool:
        """Initialize local GitHub Enterprise repository"""
        if not self.local_repo_path.exists():
            self.local_repo_path.mkdir(parents=True, exist_ok=True)

        # Check if already a git repository
        git_dir = self.local_repo_path / ".git"
        if git_dir.exists():
            logger.info("Local repository already initialized")
            return True

        try:
            # Initialize git repository
            subprocess.run(["git", "init"], cwd=self.local_repo_path, check=True)
            logger.info("✅ Initialized local repository: %s", self.local_repo_path)

            # Create initial commit
            self._create_readme()
            subprocess.run(["git", "add", "README.md"], cwd=self.local_repo_path, check=True)
            subprocess.run(
                ["git", "commit", "-m", "Initial backup repository"],
                cwd=self.local_repo_path,
                check=True,
            )

            return True
        except subprocess.CalledProcessError as e:
            logger.error("Failed to initialize local repository: %s", e)
            return False

    def _create_readme(self):
        """Create README for local repository"""
        readme_content = f"""# Lumina Backup Repository

Local Enterprise Backup Repository

**Created**: {datetime.now().isoformat()}
**Purpose**: Automated backups before pushing to remote repositories

## Backup Strategy

1. Backup to local repository (this repo)
2. Verify backup integrity
3. Push to remote repositories (if enabled)

## Repository Structure

- `config/` - Configuration files
- `scripts/` - Python scripts
- `docs/` - Documentation
- `data/` - Data files

## Remote Repositories

- Public: {self.remote_repos.get('public', {}).get('url', 'N/A')}
- Private: {self.remote_repos.get('private', {}).get('url', 'N/A')}
"""

        readme_file = self.local_repo_path / "README.md"
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(readme_content)

    def backup_to_local(self) -> bool:
        """Backup current project to local repository"""
        logger.info("Starting backup to local enterprise repository...")

        # Ensure local repo is initialized
        if not self.initialize_local_repo():
            return False

        # Get files to backup
        files_to_backup = self._get_files_to_backup()

        if not files_to_backup:
            logger.warning("No files to backup")
            return False

        try:
            # Copy files to local repository
            backup_count = 0
            skipped_count = 0

            for file_path in files_to_backup:
                try:
                    relative_path = file_path.relative_to(self.project_root)
                    target_path = self.local_repo_path / relative_path

                    # Check target path length (Windows limit)
                    if len(str(target_path)) > 260:
                        skipped_count += 1
                        continue

                    # Create directory if needed
                    target_path.parent.mkdir(parents=True, exist_ok=True)

                    # Copy file
                    shutil.copy2(file_path, target_path)
                    backup_count += 1
                except Exception as e:
                    logger.debug("Skipped %s: %s", file_path, e)
                    skipped_count += 1
                    continue

            if skipped_count > 0:
                logger.warning(
                    "Skipped %s files (path too long or other issues)", skipped_count
                )

            logger.info(f"✅ Backed up {backup_count} files to local repository")

            # Stage and commit
            subprocess.run(["git", "add", "-A"], cwd=self.local_repo_path, check=True)

            commit_message = f"Backup: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.local_repo_path,
                check=True,
            )

            logger.info("✅ Committed backup to local repository")
            return True

        except Exception as e:
            logger.error("Backup failed: %s", e)
            return False

    def _get_files_to_backup(self) -> List[Path]:
        """Get list of files to backup"""
        try:
            backup_cfg = self.config.get("backup", {}).get("content", {})
            include_patterns = backup_cfg.get("include", [])
            exclude_patterns = backup_cfg.get("exclude", [])

            files_to_backup = []

            # Collect files based on include patterns
            for pattern in include_patterns:
                if pattern.endswith("/"):
                    # Directory pattern
                    dir_path = self.project_root / pattern.rstrip("/")
                    if dir_path.exists():
                        for file_path in dir_path.rglob("*"):
                            try:
                                if file_path.is_file() and self._should_include(
                                    file_path, exclude_patterns
                                ):
                                    files_to_backup.append(file_path)
                            except (OSError, PermissionError):
                                logger.debug(
                                    "Access denied to %s, skipping.", file_path
                                )
                                continue
                else:
                    # File pattern
                    for file_path in self.project_root.rglob(pattern):
                        try:
                            if file_path.is_file() and self._should_include(
                                file_path, exclude_patterns
                            ):
                                files_to_backup.append(file_path)
                        except (OSError, PermissionError):
                            logger.debug(
                                "Access denied to %s, skipping.", file_path
                            )
                            continue

            # Remove duplicates
            return list(set(files_to_backup))

        except Exception as e:
            logger.error(
                "Error in _get_files_to_backup: %s", e, exc_info=True
            )
            raise
    def _should_include(self, file_path: Path, exclude_patterns: List[str]) -> bool:
        """Check if file should be included"""
        path_str = str(file_path)
        try:
            relative_path = file_path.relative_to(self.project_root)
        except ValueError:
            return False

        # Windows path length limit (260 characters)
        if len(path_str) > 260:
            return False

        # CRITICAL: Always exclude the target local repository path itself
        # This prevents the "Hall of Mirrors" recursion effect
        if str(self.local_repo_path).lower() in path_str.lower():
            return False

        # Always exclude generic backup patterns to prevent recursive backups
        forbidden_patterns = ["local_backup", "lumina-backup", "backup_repo"]
        if any(p in path_str.lower() for p in forbidden_patterns):
            return False

        # Check exclude patterns from config
        for pattern in exclude_patterns:
            if pattern.endswith("/"):
                # Directory pattern - check if path contains this directory
                pattern_dir = pattern.rstrip("/")
                if pattern_dir.lower() in str(relative_path).lower().replace("\\", "/"):
                    return False
            else:
                # File pattern - use glob matching
                if file_path.match(pattern) or relative_path.match(pattern):
                    return False

        return True

    def verify_backup(self) -> Dict[str, Any]:
        """Verify backup integrity"""
        verification = {
            "timestamp": datetime.now().isoformat(),
            "local_repo_exists": self.local_repo_path.exists(),
            "is_git_repo": (self.local_repo_path / ".git").exists(),
            "file_count": 0,
            "last_commit": None,
            "status": "unknown"
        }

        if not verification["local_repo_exists"]:
            verification["status"] = "failed"
            return verification

        try:
            # Get file count
            files = list(self.local_repo_path.rglob("*"))
            verification["file_count"] = len([f for f in files if f.is_file()])

            # Get last commit
            result = subprocess.run(
                ["git", "log", "-1", "--format=%H|%s|%cd", "--date=iso"],
                cwd=self.local_repo_path,
                capture_output=True,
                text=True,
                check=True
            )

            if result.stdout:
                commit_info = result.stdout.strip().split("|")
                verification["last_commit"] = {
                    "hash": commit_info[0],
                    "message": commit_info[1],
                    "date": commit_info[2] if len(commit_info) > 2 else None
                }

            verification["status"] = "success"

        except Exception as e:
            verification["status"] = "error"
            verification["error"] = str(e)

        return verification

    def push_to_remote(self, remote_name: str = "public") -> bool:
        """Push local backup to remote repository"""
        remote_config = self.remote_repos.get(remote_name, {})

        if not remote_config.get("enabled", False):
            logger.info("Remote %s is disabled", remote_name)
            return False

        remote_url = remote_config.get("url")
        if not remote_url:
            logger.error("No URL configured for remote %s", remote_name)
            return False

        try:
            # Check if remote exists
            result = subprocess.run(
                ["git", "remote", "get-url", remote_name],
                cwd=self.local_repo_path,
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                # Add remote
                subprocess.run(
                    ["git", "remote", "add", remote_name, remote_url],
                    cwd=self.local_repo_path,
                    check=True
                )
                logger.info("✅ Added remote: %s", remote_name)

            # Push to remote
            branch = "main" if remote_name == "public" else "main"
            subprocess.run(
                ["git", "push", remote_name, branch],
                cwd=self.local_repo_path,
                check=True
            )

            logger.info("✅ Pushed to remote: %s", remote_name)
            return True

        except subprocess.CalledProcessError as e:
            logger.error("Failed to push to %s: %s", remote_name, e)
            return False

    def backup_and_push(self, push_to_remote: bool = True) -> Dict[str, Any]:
        """Complete backup workflow: local → verify → remote"""
        results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "local_backup": False,
            "verification": None,
            "remote_push": {},
            "success": False,
        }

        # Step 1: Backup to local
        results["local_backup"] = self.backup_to_local()

        if not results["local_backup"]:
            return results

        # Step 2: Verify backup
        results["verification"] = self.verify_backup()

        if results["verification"]["status"] != "success":
            logger.warning("Backup verification failed")
            return results

        # Step 3: Push to remote (if enabled)
        if push_to_remote:
            for remote_name in self.remote_repos.keys():
                remote_config = self.remote_repos[remote_name]
                if remote_config.get("push_after_local", False):
                    results["remote_push"][remote_name] = self.push_to_remote(remote_name)

        results["success"] = True
        return results


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Local Enterprise Backup System")
    parser.add_argument("--backup", action="store_true", help="Backup to local repository")
    parser.add_argument("--verify", action="store_true", help="Verify backup integrity")
    parser.add_argument("--push", type=str, help="Push to remote (public/private)")
    parser.add_argument("--full", action="store_true", help="Full workflow: backup → verify → push")
    parser.add_argument("--init", action="store_true", help="Initialize local repository")

    args = parser.parse_args()

    backup_system = LocalEnterpriseBackup(project_root)

    if args.init:
        if backup_system.initialize_local_repo():
            print("✅ Local repository initialized")
        else:
            print("❌ Failed to initialize local repository")

    if args.backup:
        if backup_system.backup_to_local():
            print("✅ Backup to local repository completed")
        else:
            print("❌ Backup failed")

    if args.verify:
        verification = backup_system.verify_backup()
        print("=" * 80)
        print("📊 BACKUP VERIFICATION")
        print("=" * 80)
        print(f"Status: {verification['status']}")
        print(f"File Count: {verification['file_count']}")
        last_commit = verification.get("last_commit")
        if last_commit and isinstance(last_commit, dict):
            print(f"Last Commit: {last_commit.get('message', 'N/A')}")
        print()

    if args.push:
        if backup_system.push_to_remote(args.push):
            print(f"✅ Pushed to {args.push} repository")
        else:
            print(f"❌ Failed to push to {args.push}")

    if args.full:
        results = backup_system.backup_and_push()
        print("=" * 80)
        print("🔄 FULL BACKUP WORKFLOW")
        print("=" * 80)
        print(f"Local Backup: {'✅' if results['local_backup'] else '❌'}")
        ver = results.get("verification") or {}
        print(f"Verification: {ver.get('status', 'N/A')}")
        print("Remote Push:")
        for remote, success in results['remote_push'].items():
            print(f"  {remote}: {'✅' if success else '❌'}")
        print(f"Overall: {'✅ Success' if results['success'] else '❌ Failed'}")
        print()


if __name__ == "__main__":
    main()
