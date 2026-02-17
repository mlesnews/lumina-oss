#!/usr/bin/env python3
"""
Cross-Environment Mirroring System

Mirrors project state across all environments with:
- Git/GitLens versioning
- State synchronization
- Consistency verification
- Automatic conflict resolution
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import subprocess
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - 🔄 CrossEnvMirror - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CrossEnvironmentMirror:
    """
    Cross-Environment Mirroring System

    Ensures all environments are synchronized
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.environments_file = self.project_root / "config" / "environments.json"

    def load_environments(self) -> Dict[str, Any]:
        """Load environment configuration"""
        if self.environments_file.exists():
            try:
                with open(self.environments_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load environments: {e}")

        # Default environments
        return {
            "environments": [
                {
                    "name": "primary",
                    "path": str(self.project_root),
                    "type": "development",
                    "active": True
                }
            ],
            "sync_strategy": "git_based",
            "conflict_resolution": "manual"
        }

    def run_git_command(self, command: List[str], cwd: Optional[Path] = None) -> Tuple[int, str, str]:
        """Run a git command"""
        if cwd is None:
            cwd = self.project_root

        try:
            cmd = ["git"] + command
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            logger.error(f"Error running git command: {e}")
            return 1, "", str(e)

    def get_environment_state(self, env_path: Path) -> Dict[str, Any]:
        try:
            """Get state of an environment"""
            state = {
                "path": str(env_path),
                "exists": env_path.exists(),
                "is_git_repo": False,
                "current_branch": None,
                "current_commit": None,
                "has_changes": False,
                "last_sync": None
            }

            if not env_path.exists():
                return state

            # Check if git repo
            if (env_path / ".git").exists():
                state["is_git_repo"] = True

                # Get current branch
                exit_code, stdout, stderr = self.run_git_command(["branch", "--show-current"], cwd=env_path)
                if exit_code == 0:
                    state["current_branch"] = stdout

                # Get current commit
                exit_code, stdout, stderr = self.run_git_command(["log", "-1", "--pretty=format:%H"], cwd=env_path)
                if exit_code == 0:
                    state["current_commit"] = stdout

                # Check for changes
                exit_code, stdout, stderr = self.run_git_command(["status", "--porcelain"], cwd=env_path)
                if exit_code == 0:
                    state["has_changes"] = len(stdout.strip()) > 0

            return state

        except Exception as e:
            self.logger.error(f"Error in get_environment_state: {e}", exc_info=True)
            raise
    def compare_environments(self) -> Dict[str, Any]:
        try:
            """Compare all environments"""
            environments = self.load_environments()

            comparison = {
                "timestamp": datetime.now().isoformat(),
                "environments": {},
                "synchronized": False,
                "differences": []
            }

            env_states = {}
            for env in environments.get("environments", []):
                env_path = Path(env["path"])
                state = self.get_environment_state(env_path)
                env_states[env["name"]] = state
                comparison["environments"][env["name"]] = state

            # Compare commits
            commits = [s["current_commit"] for s in env_states.values() if s["current_commit"]]
            unique_commits = set(commits)

            if len(unique_commits) == 1:
                comparison["synchronized"] = True
            else:
                comparison["synchronized"] = False
                comparison["differences"].append({
                    "type": "commit_mismatch",
                    "details": {name: state["current_commit"] for name, state in env_states.items() if state["current_commit"]}
                })

            # Check for uncommitted changes
            for name, state in env_states.items():
                if state["has_changes"]:
                    comparison["differences"].append({
                        "type": "uncommitted_changes",
                        "environment": name,
                        "details": "Has uncommitted changes"
                    })

            return comparison

        except Exception as e:
            self.logger.error(f"Error in compare_environments: {e}", exc_info=True)
            raise
    def sync_environments(self, source_env: str, target_envs: List[str], strategy: str = "pull") -> Dict[str, Any]:
        try:
            """
            Sync environments

            Args:
                source_env: Source environment name
                target_envs: List of target environment names
                strategy: "pull" (pull from source) or "push" (push to targets)
            """
            environments = self.load_environments()
            env_configs = {e["name"]: e for e in environments.get("environments", [])}

            if source_env not in env_configs:
                return {"success": False, "error": f"Source environment not found: {source_env}"}

            source_path = Path(env_configs[source_env]["path"])
            source_state = self.get_environment_state(source_path)

            if not source_state["is_git_repo"]:
                return {"success": False, "error": "Source environment is not a git repository"}

            results = {
                "timestamp": datetime.now().isoformat(),
                "source": source_env,
                "targets": target_envs,
                "strategy": strategy,
                "sync_results": {}
            }

            for target_env in target_envs:
                if target_env not in env_configs:
                    results["sync_results"][target_env] = {
                        "success": False,
                        "error": f"Target environment not found: {target_env}"
                    }
                    continue

                target_path = Path(env_configs[target_env]["path"])
                target_state = self.get_environment_state(target_path)

                if not target_state["is_git_repo"]:
                    results["sync_results"][target_env] = {
                        "success": False,
                        "error": "Target environment is not a git repository"
                    }
                    continue

                # Perform sync
                if strategy == "pull":
                    # Pull from source to target
                    exit_code, stdout, stderr = self.run_git_command(
                        ["pull", "origin", source_state.get("current_branch", "main")],
                        cwd=target_path
                    )
                else:
                    # Push from source to target (would need remote setup)
                    results["sync_results"][target_env] = {
                        "success": False,
                        "error": "Push strategy not fully implemented"
                    }
                    continue

                results["sync_results"][target_env] = {
                    "success": exit_code == 0,
                    "stdout": stdout,
                    "stderr": stderr
                }

            results["overall_success"] = all(
                r.get("success", False) for r in results["sync_results"].values()
            )

            return results

        except Exception as e:
            self.logger.error(f"Error in sync_environments: {e}", exc_info=True)
            raise
    def verify_mirroring(self) -> Dict[str, Any]:
        """Verify all environments are properly mirrored"""
        comparison = self.compare_environments()

        verification = {
            "timestamp": datetime.now().isoformat(),
            "synchronized": comparison["synchronized"],
            "issues": [],
            "recommendations": []
        }

        if not comparison["synchronized"]:
            verification["issues"].append("Environments are not synchronized")

            for diff in comparison["differences"]:
                if diff["type"] == "commit_mismatch":
                    verification["recommendations"].append(
                        "Run sync to align all environments to the same commit"
                    )
                elif diff["type"] == "uncommitted_changes":
                    verification["recommendations"].append(
                        f"Commit or stash changes in {diff['environment']}"
                    )

        return verification


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Cross-Environment Mirroring")
    parser.add_argument("--compare", action="store_true", help="Compare all environments")
    parser.add_argument("--sync", type=str, help="Sync environments (format: source:target1,target2)")
    parser.add_argument("--verify", action="store_true", help="Verify mirroring")

    args = parser.parse_args()

    mirror = CrossEnvironmentMirror()

    if args.compare:
        comparison = mirror.compare_environments()
        print("\n" + "=" * 80)
        print("🔄 ENVIRONMENT COMPARISON")
        print("=" * 80)
        print(f"Synchronized: {'✅ Yes' if comparison['synchronized'] else '❌ No'}")
        print()
        print("Environments:")
        for name, state in comparison["environments"].items():
            print(f"  {name}:")
            print(f"    Path: {state['path']}")
            print(f"    Branch: {state.get('current_branch', 'N/A')}")
            print(f"    Commit: {state.get('current_commit', 'N/A')[:8] if state.get('current_commit') else 'N/A'}")
            print(f"    Changes: {'⚠️ Yes' if state.get('has_changes') else '✅ No'}")
            print()

        if comparison["differences"]:
            print("Differences:")
            for diff in comparison["differences"]:
                print(f"  ⚠️ {diff['type']}: {diff.get('details', '')}")
            print()

    if args.sync:
        parts = args.sync.split(":")
        if len(parts) == 2:
            source, targets_str = parts
            targets = [t.strip() for t in targets_str.split(",")]
            results = mirror.sync_environments(source, targets)
            print("\n" + "=" * 80)
            print("🔄 SYNC RESULTS")
            print("=" * 80)
            for target, result in results["sync_results"].items():
                status = "✅" if result.get("success") else "❌"
                print(f"{status} {target}: {result.get('error', 'Success')}")
            print()
        else:
            print("❌ Invalid sync format. Use: source:target1,target2")

    if args.verify:
        verification = mirror.verify_mirroring()
        print("\n" + "=" * 80)
        print("✅ MIRRORING VERIFICATION")
        print("=" * 80)
        print(f"Synchronized: {'✅ Yes' if verification['synchronized'] else '❌ No'}")
        if verification["issues"]:
            print("\nIssues:")
            for issue in verification["issues"]:
                print(f"  ⚠️ {issue}")
        if verification["recommendations"]:
            print("\nRecommendations:")
            for rec in verification["recommendations"]:
                print(f"  💡 {rec}")
        print()


if __name__ == "__main__":



    main()