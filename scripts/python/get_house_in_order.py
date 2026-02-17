#!/usr/bin/env python3
"""
Get House In Order - Comprehensive Repository and Version Management

Increments version, syncs all repos, updates company data, ensures everything is in order.
Handles public repo vs private company data separation.

Tags: #VERSION #REPO_SYNC #HOUSE_ORDER #PUBLIC_REPO @JARVIS @LUMINA
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    logger = get_logger("GetHouseInOrder")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("GetHouseInOrder")


class GetHouseInOrder:
    """
    Comprehensive house-ordering system

    - Version increment (7.0.0 → 7.1.0)
    - Public repo management
    - Private company data updates
    - Sub-repo synchronization
    - Complete house ordering
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.blueprint_file = self.project_root / "config" / "one_ring_blueprint.json"
        self.reports_dir = self.project_root / "data" / "house_order"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        logger.info("=" * 80)
        logger.info("🏠 GET HOUSE IN ORDER")
        logger.info("=" * 80)
        logger.info("   Version increment and repository sync")
        logger.info("   Public repo + private company data")
        logger.info("   All sub-repos in order")
        logger.info("")

    def get_version_info(self) -> Dict[str, Any]:
        """Get current and next version"""
        current_version = "7.0.0"
        previous_version = "6.0.0"

        if self.blueprint_file.exists():
            try:
                with open(self.blueprint_file, 'r', encoding='utf-8') as f:
                    blueprint = json.load(f)
                    metadata = blueprint.get("blueprint_metadata", {})
                    current_version = metadata.get("version", "7.0.0")
                    previous_version = metadata.get("previous_version", "6.0.0")
            except Exception as e:
                logger.warning(f"Could not load version: {e}")

        # Next version: 7.0.0 → 7.1.0 (minor bump for new features)
        parts = current_version.split('.')
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0
        next_version = f"{major}.{minor + 1}.0"

        return {
            "current": current_version,
            "previous": previous_version,
            "next": next_version,
            "type": "minor"
        }

    def check_all_repos(self) -> Dict[str, Any]:
        """Check status of all repositories"""
        logger.info("🔍 Checking all repositories...")
        logger.info("")

        repos = {
            "main": {
                "path": str(self.project_root),
                "status": "unknown",
                "branch": "unknown",
                "remote": "unknown",
                "changes": 0,
                "untracked": 0
            },
            "sub_repos": []
        }

        # Main repo
        try:
            # Get branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                repos["main"]["branch"] = result.stdout.strip()

            # Get remote
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                remote_url = result.stdout.strip()
                repos["main"]["remote"] = remote_url
                repos["main"]["is_public"] = "public" in remote_url.lower() or "github" in remote_url.lower()

            # Get status
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                changes = result.stdout.strip().split('\n') if result.stdout.strip() else []
                repos["main"]["changes"] = len([c for c in changes if not c.startswith('??')])
                repos["main"]["untracked"] = len([c for c in changes if c.startswith('??')])
                repos["main"]["status"] = "clean" if not changes else "dirty"

            logger.info(f"   Main Repo:")
            logger.info(f"      Branch: {repos['main']['branch']}")
            logger.info(f"      Remote: {repos['main']['remote']}")
            logger.info(f"      Status: {repos['main']['status']}")
            logger.info(f"      Changes: {repos['main']['changes']} modified, {repos['main']['untracked']} untracked")
        except Exception as e:
            logger.error(f"   Error checking main repo: {e}")
            repos["main"]["status"] = "error"

        # Sub-repos
        logger.info("")
        logger.info("   Sub-repositories:")
        for git_dir in self.project_root.rglob(".git"):
            if git_dir.is_dir() and git_dir.parent != self.project_root:
                sub_repo_path = git_dir.parent
                relative_path = sub_repo_path.relative_to(self.project_root)

                sub_repo = {
                    "path": str(relative_path),
                    "absolute_path": str(sub_repo_path),
                    "status": "unknown",
                    "branch": "unknown",
                    "changes": 0
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
                        sub_repo["changes"] = len(changes)
                        sub_repo["status"] = "clean" if not changes else "dirty"

                    result = subprocess.run(
                        ["git", "branch", "--show-current"],
                        cwd=sub_repo_path,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        sub_repo["branch"] = result.stdout.strip()

                    logger.info(f"      {relative_path}: {sub_repo['status']} ({sub_repo['changes']} changes)")
                except Exception as e:
                    logger.warning(f"      {relative_path}: Error - {e}")

                repos["sub_repos"].append(sub_repo)

        logger.info("")

        return repos

    def identify_company_data(self) -> Dict[str, Any]:
        try:
            """Identify private company data that needs updating"""
            logger.info("🔍 Identifying company data...")
            logger.info("")

            company_data = {
                "files": [],
                "directories": [],
                "needs_update": []
            }

            # Look for company-related files
            patterns = [
                "**/*<COMPANY>*",
                "**/*cfs*",
                "**/company/**",
                "**/private/**"
            ]

            company_dirs = [
                self.project_root / "data" / "company",
                self.project_root / "config" / "company",
                self.project_root / "data" / "private"
            ]

            for company_dir in company_dirs:
                if company_dir.exists():
                    company_data["directories"].append(str(company_dir.relative_to(self.project_root)))
                    for file in company_dir.rglob("*.json"):
                        company_data["files"].append(str(file.relative_to(self.project_root)))

            # Check if version needs updating in company data
            if company_data["files"]:
                company_data["needs_update"].append({
                    "action": "update_version_references",
                    "files": company_data["files"][:5]  # Sample
                })

            logger.info(f"   Company directories: {len(company_data['directories'])}")
            logger.info(f"   Company files: {len(company_data['files'])}")
            logger.info("")

            return company_data

        except Exception as e:
            self.logger.error(f"Error in identify_company_data: {e}", exc_info=True)
            raise
    def generate_order_plan(
        self,
        version_info: Dict[str, Any],
        repos: Dict[str, Any],
        company_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive order plan"""
        logger.info("📋 Generating house order plan...")
        logger.info("")

        plan = {
            "version": version_info,
            "repositories": repos,
            "company_data": company_data,
            "actions": [],
            "order": [],
            "warnings": [],
            "public_repo_concerns": []
        }

        # Version update
        plan["actions"].append({
            "step": 1,
            "action": "update_version",
            "description": f"Update version from {version_info['current']} to {version_info['next']}",
            "location": "config/one_ring_blueprint.json",
            "priority": "high"
        })
        plan["order"].append(f"1. Update version to {version_info['next']} in blueprint")

        # Public repo concerns
        if repos["main"].get("is_public", False):
            plan["public_repo_concerns"].append({
                "concern": "Public repository detected",
                "action": "Ensure no private company data is committed",
                "priority": "critical"
            })
            plan["warnings"].append("⚠️  PUBLIC REPO: Ensure .gitignore excludes company data")
            plan["order"].append("2. Verify .gitignore excludes private company data")

        # Company data update
        if company_data["files"]:
            plan["actions"].append({
                "step": 2,
                "action": "update_company_data",
                "description": "Update version references in company data files",
                "files": company_data["files"],
                "priority": "high"
            })
            plan["order"].append("3. Update version in private company data files")

        # Main repo sync
        if repos["main"]["status"] == "dirty":
            plan["actions"].append({
                "step": 3,
                "action": "commit_main_repo",
                "description": f"Commit changes in main repo (branch: {repos['main']['branch']})",
                "priority": "high",
                "warning": "Review changes before committing to public repo"
            })
            plan["order"].append(f"4. Commit main repo changes (review first - public repo)")

        # Sub-repo sync
        for sub_repo in repos["sub_repos"]:
            if sub_repo["status"] == "dirty":
                plan["actions"].append({
                    "step": 4 + len([a for a in plan["actions"] if a["action"].startswith("commit_sub")]),
                    "action": f"commit_sub_repo_{sub_repo['path'].replace('/', '_')}",
                    "description": f"Commit changes in {sub_repo['path']}",
                    "path": sub_repo["path"],
                    "priority": "medium"
                })
                plan["order"].append(f"5. Commit sub-repo: {sub_repo['path']}")

        # Version tag
        plan["actions"].append({
            "step": 999,
            "action": "create_version_tag",
            "description": f"Create git tag for version {version_info['next']}",
            "priority": "medium"
        })
        plan["order"].append(f"6. Create version tag: v{version_info['next']}")

        logger.info("✅ Order plan generated")
        logger.info(f"   Total actions: {len(plan['actions'])}")
        logger.info("")

        return plan

    def save_plan(self, plan: Dict[str, Any]) -> Path:
        try:
            """Save order plan"""
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plan_file = self.reports_dir / f"house_order_plan_{timestamp}.json"

            with open(plan_file, 'w', encoding='utf-8') as f:
                json.dump(plan, f, indent=2, ensure_ascii=False)

            logger.info(f"📁 Plan saved: {plan_file}")

            return plan_file

        except Exception as e:
            self.logger.error(f"Error in save_plan: {e}", exc_info=True)
            raise
    def print_summary(self, plan: Dict[str, Any]):
        """Print comprehensive summary"""
        version = plan["version"]
        repos = plan["repositories"]

        print("=" * 80)
        print("🏠 HOUSE ORDER SUMMARY")
        print("=" * 80)
        print("")
        print("VERSION:")
        print(f"   Current: {version['current']}")
        print(f"   Next: {version['next']} ({version['type']} bump)")
        print(f"   This work will bring us to: {version['next']}")
        print("")
        print("REPOSITORY STATUS:")
        print(f"   Main Repo: {repos['main']['status']}")
        print(f"   Branch: {repos['main']['branch']}")
        print(f"   Remote: {repos['main'].get('remote', 'unknown')}")
        if repos['main'].get('is_public'):
            print(f"   ⚠️  PUBLIC REPO - Be careful with commits")
        print(f"   Changes: {repos['main']['changes']} modified, {repos['main']['untracked']} untracked")
        print(f"   Sub-repos: {len(repos['sub_repos'])}")
        for sub_repo in repos["sub_repos"]:
            print(f"      - {sub_repo['path']}: {sub_repo['status']} ({sub_repo['changes']} changes)")
        print("")
        print("COMPANY DATA:")
        print(f"   Directories: {len(plan['company_data']['directories'])}")
        print(f"   Files: {len(plan['company_data']['files'])}")
        if plan['company_data']['files']:
            print(f"   ⚠️  Company data needs version update")
        print("")
        print("ORDER PLAN:")
        for item in plan["order"]:
            print(f"   {item}")
        print("")
        if plan["warnings"]:
            print("WARNINGS:")
            for warning in plan["warnings"]:
                print(f"   {warning}")
            print("")
        print("=" * 80)


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Get house in order")
    parser.add_argument("--save", action="store_true", help="Save plan")
    parser.add_argument("--execute", action="store_true", help="Execute plan (use with caution)")

    args = parser.parse_args()

    manager = GetHouseInOrder()

    # Get version info
    version_info = manager.get_version_info()

    # Check repos
    repos = manager.check_all_repos()

    # Identify company data
    company_data = manager.identify_company_data()

    # Generate plan
    plan = manager.generate_order_plan(version_info, repos, company_data)

    # Print summary
    manager.print_summary(plan)

    # Save if requested
    if args.save:
        manager.save_plan(plan)

    return plan


if __name__ == "__main__":

    main()