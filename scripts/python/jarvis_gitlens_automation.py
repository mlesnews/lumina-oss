#!/usr/bin/env python3
"""
JARVIS GitLens Automation
Automatically handles all GitLens follow-ups and git operations.
Part of JARVIS automated workflow system.

Features:
- Automatic commit message generation
- Auto-commit on save (configurable)
- Automatic push/pull coordination
- Branch management
- Conflict resolution prompts
- Git status monitoring
- Integration with R5 for commit intelligence
"""

import sys
import json
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import re
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(project_root / "data" / "logs" / "jarvis_gitlens.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

try:
    from r5_living_context_matrix import R5LivingContextMatrix
    R5_AVAILABLE = True
except ImportError:
    R5_AVAILABLE = False
    logger.warning("R5 Living Context Matrix not available")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class JARVISGitLensAutomation:
    """Automated GitLens follow-up handler integrated with JARVIS"""

    def __init__(self, repo_path: Optional[Path] = None, auto_commit: bool = False, fullauto: bool = False):
        """
        Initialize GitLens automation.

        Args:
            repo_path: Path to git repository. If None, uses current directory or project root.
            auto_commit: If True, automatically commits changes. Default: False (prompts user).
            fullauto: If True, enables full automation (auto-commit, auto-push, auto-pull, conflict resolution).
                      Overrides auto_commit to True.
        """
        if repo_path is None:
            repo_path = Path.cwd()
            # Try to find git repo
            for path in [repo_path, project_root]:
                if (path / ".git").exists():
                    repo_path = path
                    break

        self.repo_path = Path(repo_path)
        self.fullauto = fullauto
        self.auto_commit = auto_commit or fullauto  # Fullauto enables auto-commit
        self.auto_push_enabled = fullauto  # Fullauto enables auto-push
        self.auto_pull_enabled = fullauto  # Fullauto enables auto-pull
        self.r5 = None

        if R5_AVAILABLE:
            try:
                self.r5 = R5LivingContextMatrix(project_root)
            except Exception as e:
                logger.warning(f"Could not initialize R5: {e}")

    def run_git_command(self, command: List[str], capture_output: bool = True) -> Tuple[int, str, str]:
        """Run a git command and return exit code, stdout, stderr"""
        try:
            cmd = ["git"] + command
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=capture_output,
                text=True,
                timeout=30
            )
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            logger.error(f"Git command timed out: {' '.join(command)}")
            return 1, "", "Command timed out"
        except Exception as e:
            logger.error(f"Error running git command: {e}")
            return 1, "", str(e)

    def get_git_status(self) -> Dict[str, Any]:
        """Get current git status"""
        exit_code, stdout, stderr = self.run_git_command(["status", "--porcelain"])

        if exit_code != 0:
            return {"error": stderr, "has_changes": False}

        lines = stdout.split('\n') if stdout else []
        staged = [l for l in lines if l.startswith('M ') or l.startswith('A ') or l.startswith('D ')]
        modified = [l for l in lines if l.startswith(' M') or l.startswith(' A') or l.startswith(' D')]
        untracked = [l for l in lines if l.startswith('??')]

        return {
            "has_changes": len(lines) > 0,
            "staged": len(staged),
            "modified": len(modified),
            "untracked": len(untracked),
            "files": {
                "staged": [l[3:] for l in staged],
                "modified": [l[3:] for l in modified],
                "untracked": [l[3:] for l in untracked]
            }
        }

    def get_current_branch(self) -> Optional[str]:
        """Get current git branch"""
        exit_code, stdout, stderr = self.run_git_command(["branch", "--show-current"])
        if exit_code == 0 and stdout:
            return stdout.strip()
        return None

    def generate_commit_message(self, files: List[str], use_r5: bool = True) -> str:
        """Generate intelligent commit message based on changed files and R5 context"""
        message_parts = []

        # Analyze file changes
        file_types = {}
        for file in files:
            ext = Path(file).suffix.lower()
            file_types[ext] = file_types.get(ext, 0) + 1

        # Generate prefix based on file types
        if file_types.get('.py', 0) > 0:
            prefix = "[JARVIS] Python"
        elif file_types.get('.ps1', 0) > 0:
            prefix = "[JARVIS] PowerShell"
        elif file_types.get('.md', 0) > 0:
            prefix = "[JARVIS] Documentation"
        elif file_types.get('.json', 0) > 0:
            prefix = "[JARVIS] Configuration"
        elif file_types.get('.yml', 0) > 0 or file_types.get('.yaml', 0) > 0:
            prefix = "[JARVIS] Configuration"
        else:
            prefix = "[JARVIS]"

        # Try to get context from R5
        if use_r5 and self.r5:
            try:
                # Get recent R5 intelligence that might relate to these files
                r5_data = self.r5.get_living_context()
                if r5_data and "recent_intelligence" in r5_data:
                    # Use R5 context to inform commit message
                    message_parts.append(prefix)
                    message_parts.append("- Auto-commit via JARVIS GitLens automation")
                else:
                    message_parts.append(prefix)
                    message_parts.append("- Automated commit")
            except Exception as e:
                logger.debug(f"Could not get R5 context: {e}")
                message_parts.append(prefix)
                message_parts.append("- Automated commit")
        else:
            message_parts.append(prefix)
            message_parts.append("- Automated commit")

        # Add file summary
        if len(files) <= 5:
            message_parts.append(f"\n\nFiles: {', '.join([Path(f).name for f in files[:5]])}")
        else:
            message_parts.append(f"\n\nFiles: {len(files)} files changed")

        message_parts.append(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return "\n".join(message_parts)

    def auto_commit_changes(self, message: Optional[str] = None) -> Tuple[bool, str]:
        """
        Automatically commit all changes.

        Returns:
            (success, message)
        """
        status = self.get_git_status()

        if not status.get("has_changes"):
            return True, "No changes to commit"

        if status.get("error"):
            return False, f"Error getting status: {status['error']}"

        # Stage all changes
        exit_code, stdout, stderr = self.run_git_command(["add", "-A"])
        if exit_code != 0:
            return False, f"Error staging files: {stderr}"

        # Generate commit message if not provided
        if not message:
            all_files = (
                status["files"]["staged"] +
                status["files"]["modified"] +
                status["files"]["untracked"]
            )
            message = self.generate_commit_message(all_files)

        # Commit
        exit_code, stdout, stderr = self.run_git_command(["commit", "-m", message])
        if exit_code != 0:
            # Check if it's a Dropbox filesystem issue
            if "Function not implemented" in stderr or "cannot update the ref" in stderr:
                logger.warning("Dropbox filesystem issue detected - may need retry")
                return False, f"Dropbox sync issue: {stderr}. Try again after sync completes."
            return False, f"Error committing: {stderr}"

        logger.info(f"✅ Committed changes: {stdout}")
        return True, stdout

    def auto_push(self, retry_on_dropbox_error: bool = True, max_retries: int = 3) -> Tuple[bool, str]:
        """Automatically push changes to remote"""
        branch = self.get_current_branch()
        if not branch:
            return False, "Not on a branch"

        for attempt in range(max_retries):
            exit_code, stdout, stderr = self.run_git_command(["push", "origin", branch])

            if exit_code == 0:
                logger.info(f"✅ Pushed to origin/{branch}")
                return True, stdout

            # Check for Dropbox issues
            if retry_on_dropbox_error and "Function not implemented" in stderr:
                if attempt < max_retries - 1:
                    logger.warning(f"Dropbox issue detected, retrying ({attempt + 1}/{max_retries})...")
                    import time
                    time.sleep(5)
                    continue

            return False, f"Error pushing: {stderr}"

        return False, f"Failed after {max_retries} attempts"

    def auto_pull(self) -> Tuple[bool, str]:
        """Automatically pull latest changes"""
        branch = self.get_current_branch()
        if not branch:
            return False, "Not on a branch"

        exit_code, stdout, stderr = self.run_git_command(["pull", "origin", branch])

        if exit_code == 0:
            logger.info(f"✅ Pulled from origin/{branch}")
            return True, stdout

        # Check for conflicts
        if "CONFLICT" in stderr.upper() or "merge conflict" in stderr.lower():
            return False, f"Merge conflicts detected: {stderr}"

        return False, f"Error pulling: {stderr}"

    def handle_follow_ups(self) -> Dict[str, Any]:
        """
        Main handler for GitLens follow-ups.
        Checks status and performs appropriate actions.
        In fullauto mode, handles all operations automatically including conflict resolution.
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "actions_taken": [],
            "status": self.get_git_status(),
            "branch": self.get_current_branch(),
            "fullauto": self.fullauto
        }

        status = results["status"]

        # In fullauto mode, always pull first to sync with remote
        if self.fullauto and self.auto_pull_enabled:
            pull_success, pull_msg = self.auto_pull()
            results["actions_taken"].append({
                "action": "auto_pull",
                "success": pull_success,
                "message": pull_msg
            })

            # If pull had conflicts, try to resolve automatically
            if not pull_success and "conflict" in pull_msg.lower():
                conflict_resolution = self._auto_resolve_conflicts()
                results["actions_taken"].append({
                    "action": "auto_resolve_conflicts",
                    "success": conflict_resolution["success"],
                    "message": conflict_resolution["message"]
                })

        if not status.get("has_changes"):
            results["message"] = "No changes detected"
            return results

        # Auto-commit if enabled
        if self.auto_commit:
            success, message = self.auto_commit_changes()
            results["actions_taken"].append({
                "action": "auto_commit",
                "success": success,
                "message": message
            })

            if success and self.auto_push_enabled:
                # Try to push
                push_success, push_msg = self.auto_push()
                results["actions_taken"].append({
                    "action": "auto_push",
                    "success": push_success,
                    "message": push_msg
                })
        else:
            # Just report status
            results["message"] = "Changes detected (auto-commit disabled)"
            results["recommended_actions"] = [
                "Review changes",
                "Stage files: git add -A",
                "Commit: git commit -m 'message'",
                "Push: git push"
            ]

        return results

    def _auto_resolve_conflicts(self) -> Dict[str, Any]:
        """
        Automatically resolve merge conflicts.
        In fullauto mode, uses strategy to resolve conflicts.
        """
        try:
            # Get conflicted files
            exit_code, stdout, stderr = self.run_git_command(["diff", "--name-only", "--diff-filter=U"])
            if exit_code != 0 or not stdout:
                return {"success": True, "message": "No conflicts detected"}

            conflicted_files = [f.strip() for f in stdout.split('\n') if f.strip()]

            if not conflicted_files:
                return {"success": True, "message": "No conflicts to resolve"}

            # Strategy: Use local changes (ours) for most conflicts
            # This is a simple strategy - can be enhanced with more sophisticated logic
            logger.info(f"Auto-resolving conflicts in {len(conflicted_files)} files using 'ours' strategy")

            for file in conflicted_files:
                # Use 'ours' strategy (keep local changes)
                exit_code, stdout, stderr = self.run_git_command(["checkout", "--ours", file])
                if exit_code == 0:
                    # Stage the resolved file
                    self.run_git_command(["add", file])

            # Complete the merge
            exit_code, stdout, stderr = self.run_git_command(["commit", "--no-edit"])
            if exit_code == 0:
                return {"success": True, "message": f"Resolved conflicts in {len(conflicted_files)} files using 'ours' strategy"}
            else:
                return {"success": False, "message": f"Could not complete merge: {stderr}"}

        except Exception as e:
            logger.error(f"Error auto-resolving conflicts: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}


def main():
    try:
        """CLI entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS GitLens Automation")
        parser.add_argument("--repo", type=str, help="Path to git repository")
        parser.add_argument("--auto-commit", action="store_true", help="Automatically commit changes")
        parser.add_argument("--auto-push", action="store_true", help="Automatically push after commit")
        parser.add_argument("--fullauto", action="store_true", help="Full automation mode: auto-commit, auto-push, auto-pull, auto-resolve conflicts")
        parser.add_argument("--status", action="store_true", help="Show git status only")
        parser.add_argument("--commit", action="store_true", help="Commit changes")
        parser.add_argument("--push", action="store_true", help="Push changes")
        parser.add_argument("--pull", action="store_true", help="Pull latest changes")

        args = parser.parse_args()

        repo_path = Path(args.repo) if args.repo else None
        automation = JARVISGitLensAutomation(
            repo_path=repo_path, 
            auto_commit=args.auto_commit,
            fullauto=args.fullauto
        )

        if args.status:
            status = automation.get_git_status()
            print(json.dumps(status, indent=2))
            return

        if args.commit:
            success, message = automation.auto_commit_changes()
            print(f"Commit: {'✅ Success' if success else '❌ Failed'}")
            print(message)
            if success and args.push:
                push_success, push_msg = automation.auto_push()
                print(f"Push: {'✅ Success' if push_success else '❌ Failed'}")
                print(push_msg)
            return

        if args.push:
            success, message = automation.auto_push()
            print(f"Push: {'✅ Success' if success else '❌ Failed'}")
            print(message)
            return

        if args.pull:
            success, message = automation.auto_pull()
            print(f"Pull: {'✅ Success' if success else '❌ Failed'}")
            print(message)
            return

        # Default: handle follow-ups
        results = automation.handle_follow_ups()
        print(json.dumps(results, indent=2))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()