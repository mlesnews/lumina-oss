#!/usr/bin/env python3
"""
Git/GitLens Enterprise Services

Runs all applicable Git and GitLens related services for local cloud Enterprise version.
Integrates with NAS cron scheduler for routine scheduled tasks.

Tags: #GIT #GITLENS #ENTERPRISE #NAS #CRON @JARVIS @LUMINA
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

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
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("GitGitLensEnterpriseServices")


class GitGitLensEnterpriseServices:
    """Git/GitLens enterprise services for local cloud"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_file = project_root / "config" / "git_gitlens_enterprise.json"
        self.config = self._load_config()

        # Service endpoints
        self.services = {
            "git_status": self._run_git_status,
            "git_sync": self._run_git_sync,
            "gitlens_followup": self._run_gitlens_followup,
            "git_backup": self._run_git_backup,
            "git_cleanup": self._run_git_cleanup,
            "git_health_check": self._run_git_health_check
        }

    def _load_config(self) -> Dict[str, Any]:
        try:
            """Load Git/GitLens enterprise configuration"""
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            return self._default_config()

        except Exception as e:
            self.logger.error(f"Error in _load_config: {e}", exc_info=True)
            raise
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration"""
        return {
            "version": "1.0.0",
            "git": {
                "enabled": True,
                "auto_commit": True,
                "auto_push": False,
                "commit_message_template": "Automated backup: {timestamp}"
            },
            "gitlens": {
                "enabled": True,
                "automatic_followup": True,
                "pr_integration": True,
                "workflow_automation": True
            },
            "local_enterprise": {
                "enabled": True,
                "repository_path": "N:\\git\\repositories\\lumina-enterprise",
                "backup_path": "N:\\git\\repositories\\lumina-backup"
            },
            "nas_cron": {
                "enabled": True,
                "schedule_file": "N:\\git\\cron\\lumina_tasks.cron",
                "tasks": []
            }
        }

    def _run_git_status(self) -> Dict[str, Any]:
        """Run git status check"""
        logger.info("Running git status check...")

        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )

            changes = result.stdout.strip().split('\n') if result.stdout.strip() else []

            # Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )

            return {
                "status": "success",
                "branch": branch_result.stdout.strip(),
                "has_changes": len(changes) > 0,
                "changes": changes,
                "change_count": len(changes)
            }
        except subprocess.CalledProcessError as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def _run_git_sync(self) -> Dict[str, Any]:
        """Run git sync (fetch, pull, push)"""
        logger.info("Running git sync...")

        results = {
            "fetch": False,
            "pull": False,
            "push": False
        }

        try:
            # Fetch
            subprocess.run(["git", "fetch"], cwd=self.project_root, check=True, capture_output=True)
            results["fetch"] = True
            logger.info("✅ Fetched from remote")

            # Pull (if behind)
            subprocess.run(["git", "pull"], cwd=self.project_root, check=True, capture_output=True)
            results["pull"] = True
            logger.info("✅ Pulled from remote")

            # Push (if auto_push enabled)
            if self.config.get("git", {}).get("auto_push", False):
                subprocess.run(["git", "push"], cwd=self.project_root, check=True, capture_output=True)
                results["push"] = True
                logger.info("✅ Pushed to remote")

            return {
                "status": "success",
                "results": results
            }
        except subprocess.CalledProcessError as e:
            return {
                "status": "error",
                "error": str(e),
                "results": results
            }

    def _run_gitlens_followup(self) -> Dict[str, Any]:
        """Run GitLens automatic followup"""
        logger.info("Running GitLens automatic followup...")

        try:
            from jarvis_gitlens_followup_automation import GitLensFollowupAutomation

            automation = GitLensFollowupAutomation(self.project_root)
            result = automation.run_automatic_followup()

            return {
                "status": "success",
                "result": result
            }
        except ImportError:
            logger.warning("GitLens followup automation not available")
            return {
                "status": "not_available",
                "message": "GitLens followup automation module not found"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def _run_git_backup(self) -> Dict[str, Any]:
        """Run git backup to local enterprise repository"""
        logger.info("Running git backup...")

        try:
            from local_enterprise_backup import LocalEnterpriseBackup

            backup_system = LocalEnterpriseBackup(self.project_root)
            result = backup_system.backup_to_local()

            return {
                "status": "success" if result else "failed",
                "backed_up": result
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def _run_git_cleanup(self) -> Dict[str, Any]:
        """Run git cleanup (prune, gc)"""
        logger.info("Running git cleanup...")

        results = {
            "prune": False,
            "gc": False
        }

        try:
            # Prune remote tracking branches
            subprocess.run(["git", "remote", "prune", "origin"], cwd=self.project_root, check=True, capture_output=True)
            results["prune"] = True
            logger.info("✅ Pruned remote tracking branches")

            # Garbage collection
            subprocess.run(["git", "gc", "--auto"], cwd=self.project_root, check=True, capture_output=True)
            results["gc"] = True
            logger.info("✅ Ran garbage collection")

            return {
                "status": "success",
                "results": results
            }
        except subprocess.CalledProcessError as e:
            return {
                "status": "error",
                "error": str(e),
                "results": results
            }

    def _run_git_health_check(self) -> Dict[str, Any]:
        """Run git health check"""
        logger.info("Running git health check...")

        health = {
            "is_git_repo": (self.project_root / ".git").exists(),
            "has_remote": False,
            "branch_exists": False,
            "status": "unknown"
        }

        if not health["is_git_repo"]:
            health["status"] = "not_a_git_repo"
            return health

        try:
            # Check remotes
            result = subprocess.run(
                ["git", "remote", "-v"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            health["has_remote"] = len(result.stdout.strip()) > 0

            # Check branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            health["branch_exists"] = len(branch_result.stdout.strip()) > 0
            health["current_branch"] = branch_result.stdout.strip()

            health["status"] = "healthy" if health["has_remote"] and health["branch_exists"] else "unhealthy"

        except Exception as e:
            health["status"] = "error"
            health["error"] = str(e)

        return health

    def run_all_services(self) -> Dict[str, Any]:
        """Run all Git/GitLens services"""
        logger.info("Running all Git/GitLens enterprise services...")

        results = {
            "timestamp": datetime.now().isoformat(),
            "services": {}
        }

        for service_name, service_func in self.services.items():
            try:
                result = service_func()
                results["services"][service_name] = result
                logger.info(f"✅ {service_name}: {result.get('status', 'completed')}")
            except Exception as e:
                results["services"][service_name] = {
                    "status": "error",
                    "error": str(e)
                }
                logger.error(f"❌ {service_name}: {e}")

        return results


class NASCronScheduler:
    """NAS cron scheduler integration"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.nas_cron_path = Path("N:\\git\\cron\\lumina_tasks.cron")
        self.local_cron_path = project_root / "data" / "nas_cron" / "lumina_tasks.cron"
        self.local_cron_path.parent.mkdir(parents=True, exist_ok=True)

    def create_cron_tasks(self) -> List[Dict[str, Any]]:
        """Create cron tasks for Git/GitLens services"""
        tasks = [
            {
                "schedule": "0 2 * * *",  # Daily at 2 AM
                "command": f"python {self.project_root}/scripts/python/local_enterprise_backup.py --full",
                "description": "Daily backup to local enterprise repository"
            },
            {
                "schedule": "0 */6 * * *",  # Every 6 hours
                "command": f"python {self.project_root}/scripts/python/git_gitlens_enterprise_services.py --sync",
                "description": "Git sync every 6 hours"
            },
            {
                "schedule": "0 3 * * *",  # Daily at 3 AM
                "command": f"python {self.project_root}/scripts/python/git_gitlens_enterprise_services.py --cleanup",
                "description": "Daily git cleanup"
            },
            {
                "schedule": "0 */12 * * *",  # Every 12 hours
                "command": f"python {self.project_root}/scripts/python/git_gitlens_enterprise_services.py --gitlens",
                "description": "GitLens followup every 12 hours"
            },
            {
                "schedule": "0 * * * *",  # Every hour
                "command": f"python {self.project_root}/scripts/python/git_gitlens_enterprise_services.py --health",
                "description": "Git health check every hour"
            }
        ]

        return tasks

    def generate_cron_file(self) -> str:
        """Generate cron file content"""
        tasks = self.create_cron_tasks()

        cron_content = "# Lumina Git/GitLens Enterprise Services - Cron Schedule\n"
        cron_content += f"# Generated: {datetime.now().isoformat()}\n"
        cron_content += "# NAS Cron Scheduler Integration\n\n"

        for task in tasks:
            cron_content += f"# {task['description']}\n"
            cron_content += f"{task['schedule']} {task['command']}\n\n"

        return cron_content

    def save_cron_file(self) -> bool:
        """Save cron file to NAS and local"""
        cron_content = self.generate_cron_file()

        # Save to local
        try:
            with open(self.local_cron_path, 'w') as f:
                f.write(cron_content)
            logger.info(f"✅ Saved cron file locally: {self.local_cron_path}")
        except Exception as e:
            logger.error(f"Failed to save local cron file: {e}")
            return False

        # Try to save to NAS
        try:
            if self._is_path_accessible(self.nas_cron_path):
                self.nas_cron_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.nas_cron_path, 'w') as f:
                    f.write(cron_content)
                logger.info(f"✅ Saved cron file to NAS: {self.nas_cron_path}")
            else:
                logger.warning(f"NAS path not accessible, using local only: {self.local_cron_path}")
        except Exception as e:
            logger.warning(f"Could not save to NAS: {e}")

        return True

    def _is_path_accessible(self, path: Path) -> bool:
        """Check if path is accessible"""
        try:
            root = Path(path.parts[0] + "\\")
            return root.exists()
        except:
            return False


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Git/GitLens Enterprise Services")
    parser.add_argument("--status", action="store_true", help="Run git status")
    parser.add_argument("--sync", action="store_true", help="Run git sync")
    parser.add_argument("--gitlens", action="store_true", help="Run GitLens followup")
    parser.add_argument("--backup", action="store_true", help="Run git backup")
    parser.add_argument("--cleanup", action="store_true", help="Run git cleanup")
    parser.add_argument("--health", action="store_true", help="Run git health check")
    parser.add_argument("--all", action="store_true", help="Run all services")
    parser.add_argument("--setup-cron", action="store_true", help="Setup NAS cron scheduler")

    args = parser.parse_args()

    services = GitGitLensEnterpriseServices(project_root)

    if args.status:
        result = services._run_git_status()
        print(f"Git Status: {result.get('status')}")
        print(f"Branch: {result.get('branch', 'N/A')}")
        print(f"Changes: {result.get('change_count', 0)}")

    if args.sync:
        result = services._run_git_sync()
        print(f"Git Sync: {result.get('status')}")

    if args.gitlens:
        result = services._run_gitlens_followup()
        print(f"GitLens Followup: {result.get('status')}")

    if args.backup:
        result = services._run_git_backup()
        print(f"Git Backup: {result.get('status')}")

    if args.cleanup:
        result = services._run_git_cleanup()
        print(f"Git Cleanup: {result.get('status')}")

    if args.health:
        result = services._run_git_health_check()
        print(f"Git Health: {result.get('status')}")
        print(f"Is Git Repo: {result.get('is_git_repo')}")
        print(f"Has Remote: {result.get('has_remote')}")

    if args.all:
        results = services.run_all_services()
        print("=" * 80)
        print("🔄 ALL GIT/GITLENS SERVICES")
        print("=" * 80)
        for service, result in results["services"].items():
            status = result.get("status", "unknown")
            icon = "✅" if status == "success" else "❌"
            print(f"{icon} {service}: {status}")
        print()

    if args.setup_cron:
        scheduler = NASCronScheduler(project_root)
        if scheduler.save_cron_file():
            print("✅ NAS cron scheduler configured")
            print(f"   Local cron file: {scheduler.local_cron_path}")
            print(f"   NAS cron file: {scheduler.nas_cron_path}")
        else:
            print("❌ Failed to setup cron scheduler")


if __name__ == "__main__":


    main()