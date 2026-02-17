#!/usr/bin/env python3
"""
Version Increment and Repository Sync Manager

Increments version from current work, updates private company data,
ensures all sub-repos are in order, and gets the house in order.

Tags: #VERSION #REPO_SYNC #HOUSE_ORDER @JARVIS @LUMINA
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    logger = get_logger("VersionIncrementRepoSync")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("VersionIncrementRepoSync")


class VersionIncrementRepoSync:
    """
    Manages version increment and repository synchronization

    - Determines next version from current work
    - Updates private company data
    - Ensures all sub-repos are in order
    - Gets the house in order
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.blueprint_file = self.project_root / "config" / "one_ring_blueprint.json"

        logger.info("=" * 80)
        logger.info("🔄 VERSION INCREMENT & REPOSITORY SYNC MANAGER")
        logger.info("=" * 80)
        logger.info("   Getting the house in order")
        logger.info("   Syncing all repos")
        logger.info("   Updating version and company data")
        logger.info("")

    def get_current_version(self) -> Dict[str, Any]:
        """Get current version from blueprint"""
        version_info = {
            "current_version": "7.0.0",
            "previous_version": "6.0.0",
            "version_type": "major"  # major, minor, patch
        }

        if self.blueprint_file.exists():
            try:
                with open(self.blueprint_file, 'r', encoding='utf-8') as f:
                    blueprint = json.load(f)
                    metadata = blueprint.get("blueprint_metadata", {})
                    if "version" in metadata:
                        version_info["current_version"] = metadata["version"]
                    # Try to find previous version
                    if "previous_version" in metadata:
                        version_info["previous_version"] = metadata["previous_version"]
            except Exception as e:
                logger.warning(f"Could not load version from blueprint: {e}")

        return version_info

    def determine_next_version(self, version_type: Optional[str] = None) -> str:
        """
        Determine next version based on work done

        Based on the change report and work completed:
        - Major: Significant milestone, breaking changes, major new features
        - Minor: New features, enhancements
        - Patch: Bug fixes, small improvements
        """
        current = self.get_current_version()
        current_version = current["current_version"]

        # Parse version
        parts = current_version.split('.')
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0

        # Determine version type if not specified
        if version_type is None:
            # Based on change report: 7 features, major milestone
            # This suggests a minor version bump (new features)
            # But if it's a major milestone release, could be major
            version_type = "minor"  # Default to minor for new features

        # Increment based on type
        if version_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif version_type == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1

        next_version = f"{major}.{minor}.{patch}"

        logger.info(f"📌 Current Version: {current_version}")
        logger.info(f"📌 Next Version: {next_version} ({version_type} bump)")
        logger.info("")

        return next_version

    def check_repo_status(self) -> Dict[str, Any]:
        """Check status of main repo and sub-repos"""
        logger.info("🔍 Checking repository status...")
        logger.info("")

        repo_status = {
            "main_repo": {
                "path": str(self.project_root),
                "status": "unknown",
                "branch": "unknown",
                "uncommitted_changes": [],
                "untracked_files": []
            },
            "sub_repos": [],
            "issues": []
        }

        # Check main repo
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                changes = result.stdout.strip().split('\n') if result.stdout.strip() else []
                modified = [line for line in changes if line.startswith(' M')]
                untracked = [line for line in changes if line.startswith('??')]

                repo_status["main_repo"]["uncommitted_changes"] = modified[:20]  # Limit
                repo_status["main_repo"]["untracked_files"] = untracked[:20]  # Limit
                repo_status["main_repo"]["status"] = "ok" if not changes else "has_changes"

                # Get current branch
                branch_result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if branch_result.returncode == 0:
                    repo_status["main_repo"]["branch"] = branch_result.stdout.strip()

                logger.info(f"   Main Repo: {repo_status['main_repo']['status']}")
                logger.info(f"   Branch: {repo_status['main_repo']['branch']}")
                logger.info(f"   Uncommitted Changes: {len(modified)}")
                logger.info(f"   Untracked Files: {len(untracked)}")
            else:
                repo_status["main_repo"]["status"] = "not_git_repo"
                logger.warning("   Main repo is not a git repository")
        except Exception as e:
            logger.error(f"   Error checking main repo: {e}")
            repo_status["main_repo"]["status"] = "error"
            repo_status["issues"].append(f"Main repo check failed: {e}")

        # Find sub-repos (look for .git directories)
        logger.info("")
        logger.info("🔍 Checking for sub-repositories...")

        for git_dir in self.project_root.rglob(".git"):
            if git_dir.is_dir():
                sub_repo_path = git_dir.parent
                relative_path = sub_repo_path.relative_to(self.project_root)

                # Skip if it's the main repo
                if sub_repo_path == self.project_root:
                    continue

                sub_repo_info = {
                    "path": str(relative_path),
                    "absolute_path": str(sub_repo_path),
                    "status": "unknown",
                    "branch": "unknown",
                    "uncommitted_changes": []
                }

                try:
                    result = subprocess.run(
                        ["git", "status", "--porcelain"],
                        cwd=sub_repo_path,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )

                    if result.returncode == 0:
                        changes = result.stdout.strip().split('\n') if result.stdout.strip() else []
                        sub_repo_info["uncommitted_changes"] = changes[:10]
                        sub_repo_info["status"] = "ok" if not changes else "has_changes"

                        branch_result = subprocess.run(
                            ["git", "branch", "--show-current"],
                            cwd=sub_repo_path,
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        if branch_result.returncode == 0:
                            sub_repo_info["branch"] = branch_result.stdout.strip()

                        logger.info(f"   Sub-repo: {relative_path}")
                        logger.info(f"      Status: {sub_repo_info['status']}")
                        logger.info(f"      Branch: {sub_repo_info['branch']}")
                        logger.info(f"      Changes: {len(changes)}")
                except Exception as e:
                    sub_repo_info["status"] = "error"
                    logger.warning(f"   Sub-repo {relative_path}: Error - {e}")

                repo_status["sub_repos"].append(sub_repo_info)

        logger.info("")

        return repo_status

    def update_version_in_blueprint(self, new_version: str, version_type: str) -> bool:
        """Update version in One Ring Blueprint"""
        logger.info(f"📝 Updating version in blueprint to {new_version}...")

        if not self.blueprint_file.exists():
            logger.error("Blueprint file not found")
            return False

        try:
            with open(self.blueprint_file, 'r', encoding='utf-8') as f:
                blueprint = json.load(f)

            # Update metadata
            if "blueprint_metadata" not in blueprint:
                blueprint["blueprint_metadata"] = {}

            metadata = blueprint["blueprint_metadata"]
            old_version = metadata.get("version", "unknown")
            metadata["previous_version"] = old_version
            metadata["version"] = new_version
            metadata["last_updated"] = datetime.now().isoformat()
            metadata["version_type"] = version_type
            metadata["version_date"] = datetime.now().strftime("%Y-%m-%d")

            # Backup before saving
            backup_file = self.blueprint_file.with_suffix(f".backup_{int(datetime.now().timestamp())}.json")
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(blueprint, f, indent=2, ensure_ascii=False)
            logger.info(f"   💾 Backup saved: {backup_file.name}")

            # Save updated blueprint
            with open(self.blueprint_file, 'w', encoding='utf-8') as f:
                json.dump(blueprint, f, indent=2, ensure_ascii=False)

            logger.info(f"   ✅ Version updated: {old_version} → {new_version}")
            logger.info("")

            return True
        except Exception as e:
            logger.error(f"Failed to update version: {e}")
            return False

    def identify_company_data_files(self) -> List[Path]:
        try:
            """Identify private company data files that need updating"""
            logger.info("🔍 Identifying company data files...")

            company_data_patterns = [
                "**/company/**",
                "**/private/**",
                "**/confidential/**",
                "**/*company*.json",
                "**/*private*.json",
                "**/<COMPANY>*",
                "**/cfs*"
            ]

            company_files = []

            # Common company data locations
            company_dirs = [
                self.project_root / "data" / "company",
                self.project_root / "data" / "private",
                self.project_root / "config" / "company",
                self.project_root / "config" / "private"
            ]

            for company_dir in company_dirs:
                if company_dir.exists():
                    for file in company_dir.rglob("*.json"):
                        company_files.append(file)

            logger.info(f"   Found {len(company_files)} company data files")
            logger.info("")

            return company_files

        except Exception as e:
            self.logger.error(f"Error in identify_company_data_files: {e}", exc_info=True)
            raise
    def generate_sync_plan(
        self,
        next_version: str,
        repo_status: Dict[str, Any],
        company_files: List[Path]
    ) -> Dict[str, Any]:
        """Generate comprehensive sync plan to get house in order"""
        logger.info("📋 Generating sync plan...")
        logger.info("")

        plan = {
            "version": {
                "current": self.get_current_version()["current_version"],
                "next": next_version,
                "type": "minor"  # Based on change report
            },
            "repositories": {
                "main": {
                    "status": repo_status["main_repo"]["status"],
                    "actions": []
                },
                "sub_repos": []
            },
            "company_data": {
                "files_found": len(company_files),
                "actions": []
            },
            "sync_actions": [],
            "order": []
        }

        # Main repo actions
        if repo_status["main_repo"]["status"] == "has_changes":
            plan["repositories"]["main"]["actions"].append({
                "action": "commit_changes",
                "description": "Commit uncommitted changes",
                "priority": "high"
            })
            plan["sync_actions"].append("Commit main repo changes")

        # Sub-repo actions
        for sub_repo in repo_status["sub_repos"]:
            if sub_repo["status"] == "has_changes":
                plan["repositories"]["sub_repos"].append({
                    "path": sub_repo["path"],
                    "actions": [{
                        "action": "commit_changes",
                        "description": f"Commit changes in {sub_repo['path']}",
                        "priority": "medium"
                    }]
                })
                plan["sync_actions"].append(f"Commit changes in {sub_repo['path']}")

        # Company data actions
        if company_files:
            plan["company_data"]["actions"].append({
                "action": "update_version_references",
                "description": "Update version references in company data files",
                "priority": "high"
            })
            plan["sync_actions"].append("Update company data version references")

        # Version update
        plan["sync_actions"].append(f"Update version to {next_version}")
        plan["order"] = [
            "1. Update version in blueprint",
            "2. Update company data files",
            "3. Commit main repo changes",
            "4. Sync sub-repos",
            "5. Create version tag",
            "6. Generate release notes"
        ]

        logger.info("✅ Sync plan generated")
        logger.info(f"   Total actions: {len(plan['sync_actions'])}")
        logger.info("")

        return plan

    def print_summary(self, version_info: Dict, repo_status: Dict, plan: Dict):
        """Print summary"""
        print("=" * 80)
        print("🔄 VERSION INCREMENT & REPO SYNC SUMMARY")
        print("=" * 80)
        print("")
        print("VERSION:")
        print(f"   Current: {version_info['current_version']}")
        print(f"   Next: {plan['version']['next']}")
        print(f"   Type: {plan['version']['type']} bump")
        print("")
        print("REPOSITORY STATUS:")
        print(f"   Main Repo: {repo_status['main_repo']['status']}")
        print(f"   Branch: {repo_status['main_repo']['branch']}")
        print(f"   Sub-repos: {len(repo_status['sub_repos'])}")
        print("")
        print("SYNC PLAN:")
        for i, action in enumerate(plan['order'], 1):
            print(f"   {action}")
        print("")
        print("=" * 80)


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Version increment and repo sync")
    parser.add_argument("--version-type", choices=["major", "minor", "patch"],
                       help="Version increment type (default: auto-detect)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show plan without executing")
    parser.add_argument("--update-version", action="store_true",
                       help="Update version in blueprint")

    args = parser.parse_args()

    manager = VersionIncrementRepoSync()

    # Get current version
    version_info = manager.get_current_version()

    # Determine next version
    next_version = manager.determine_next_version(args.version_type)

    # Check repo status
    repo_status = manager.check_repo_status()

    # Identify company data
    company_files = manager.identify_company_data_files()

    # Generate plan
    plan = manager.generate_sync_plan(next_version, repo_status, company_files)

    # Print summary
    manager.print_summary(version_info, repo_status, plan)

    # Update version if requested
    if args.update_version and not args.dry_run:
        version_type = args.version_type or plan["version"]["type"]
        manager.update_version_in_blueprint(next_version, version_type)

    return {
        "version_info": version_info,
        "next_version": next_version,
        "repo_status": repo_status,
        "plan": plan
    }


if __name__ == "__main__":

    main()