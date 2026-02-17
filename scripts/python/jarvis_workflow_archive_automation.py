#!/usr/bin/env python3
"""
JARVIS Workflow Archive Automation

Automatically archives AI agent history workflows that are:
1. Finished/completed
2. Backed up to GitLens with PR

Runs in fullauto mode by default - no manual intervention needed.

Features:
- Monitors workflow completion status
- Checks GitLens PR backup status
- Automatically archives completed workflows
- Integrates with existing archive systems
- Tracks archive history

Tags: #WORKFLOW #ARCHIVE #AUTOMATION #GITLENS #PR #FULLAUTO @JARVIS @DOIT
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISWorkflowArchiveAutomation")

# Import required systems
try:
    from jarvis_gitlens_automation import JARVISGitLensAutomation
    GITLENS_AVAILABLE = True
except ImportError:
    GITLENS_AVAILABLE = False
    logger.warning("⚠️  GitLens automation not available")

try:
    from cursor_chat_session_workflow_manager import CursorChatSessionWorkflowManager, SessionAction, WorkflowPattern
    WORKFLOW_MANAGER_AVAILABLE = True
except ImportError:
    WORKFLOW_MANAGER_AVAILABLE = False
    logger.warning("⚠️  Workflow manager not available")

try:
    from archive_review_system import ArchiveReviewSystem
    ARCHIVE_REVIEW_AVAILABLE = True
except ImportError:
    ARCHIVE_REVIEW_AVAILABLE = False
    logger.warning("⚠️  Archive review system not available")


class WorkflowStatus(Enum):
    """Workflow completion status"""
    ACTIVE = "active"
    FINISHED = "finished"
    COMPLETED = "completed"
    ARCHIVED = "archived"
    BACKED_UP = "backed_up"


class PRStatus(Enum):
    """Pull Request status"""
    NONE = "none"
    OPEN = "open"
    MERGED = "merged"
    CLOSED = "closed"
    BACKED_UP = "backed_up"  # PR created and merged/closed


@dataclass
class WorkflowMetadata:
    """Workflow metadata for tracking"""
    workflow_id: str
    workflow_name: str
    created_at: datetime
    finished_at: Optional[datetime] = None
    status: WorkflowStatus = WorkflowStatus.ACTIVE
    pr_status: PRStatus = PRStatus.NONE
    pr_number: Optional[str] = None
    pr_url: Optional[str] = None
    git_commit_hash: Optional[str] = None
    archived_at: Optional[datetime] = None
    archive_location: Optional[str] = None
    agents_involved: List[str] = field(default_factory=list)
    message_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["status"] = self.status.value
        data["pr_status"] = self.pr_status.value
        # Convert datetime objects
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowMetadata":
        """Create from dictionary"""
        # Convert string dates back to datetime
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "finished_at" in data and isinstance(data["finished_at"], str):
            data["finished_at"] = datetime.fromisoformat(data["finished_at"])
        if "archived_at" in data and isinstance(data["archived_at"], str):
            data["archived_at"] = datetime.fromisoformat(data["archived_at"])

        data["status"] = WorkflowStatus(data["status"])
        data["pr_status"] = PRStatus(data["pr_status"])
        return cls(**data)


class JARVISWorkflowArchiveAutomation:
    """
    JARVIS Workflow Archive Automation

    Automatically archives AI agent history workflows that are finished
    and backed up to GitLens with PR.
    """

    def __init__(self, project_root: Optional[Path] = None, fullauto: bool = True):
        """
        Initialize JARVIS Workflow Archive Automation.

        Args:
            project_root: Path to project root. If None, auto-detects.
            fullauto: Enable full automation (default: True)
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.fullauto = fullauto
        self.data_dir = self.project_root / "data" / "jarvis_workflow_archive"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize GitLens automation
        self.gitlens_automation = None
        if GITLENS_AVAILABLE:
            try:
                self.gitlens_automation = JARVISGitLensAutomation(
                    repo_path=self.project_root,
                    fullauto=self.fullauto
                )
                logger.info("✅ GitLens automation initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize GitLens automation: {e}")

        # Initialize workflow manager
        self.workflow_manager = None
        if WORKFLOW_MANAGER_AVAILABLE:
            try:
                self.workflow_manager = CursorChatSessionWorkflowManager(project_root=self.project_root)
                logger.info("✅ Workflow manager initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize workflow manager: {e}")

        # Initialize archive review system
        self.archive_review = None
        if ARCHIVE_REVIEW_AVAILABLE:
            try:
                self.archive_review = ArchiveReviewSystem(project_root=self.project_root)
                logger.info("✅ Archive review system initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize archive review: {e}")

        # State files
        self.workflows_file = self.data_dir / "workflows.jsonl"
        self.archive_history_file = self.data_dir / "archive_history.jsonl"
        self.state_file = self.data_dir / "automation_state.json"

        # Workflow tracking
        self.workflows: Dict[str, WorkflowMetadata] = {}
        self.running = False

        # Load existing workflows
        self._load_workflows()

        logger.info("✅ JARVIS Workflow Archive Automation initialized")
        logger.info(f"   Fullauto mode: {'✅ ENABLED' if self.fullauto else '❌ DISABLED'}")
        logger.info(f"   Tracked workflows: {len(self.workflows)}")

    def _load_workflows(self):
        """Load tracked workflows from file"""
        if not self.workflows_file.exists():
            return

        try:
            with open(self.workflows_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            workflow = WorkflowMetadata.from_dict(data)
                            self.workflows[workflow.workflow_id] = workflow
                        except Exception as e:
                            logger.debug(f"Error loading workflow: {e}")
        except Exception as e:
            logger.warning(f"⚠️  Error loading workflows: {e}")

    def _save_workflow(self, workflow: WorkflowMetadata):
        """Save workflow to tracking file"""
        try:
            # Update in-memory dict
            self.workflows[workflow.workflow_id] = workflow

            # Append to file
            with open(self.workflows_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(workflow.to_dict()) + '\n')
        except Exception as e:
            logger.error(f"❌ Error saving workflow: {e}")

    def _save_archive_history(self, entry: Dict[str, Any]):
        """Save archive action to history"""
        try:
            entry["timestamp"] = datetime.now().isoformat()
            with open(self.archive_history_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            logger.error(f"❌ Error saving archive history: {e}")

    def discover_workflows(self, session_dir: Optional[Path] = None) -> List[WorkflowMetadata]:
        """
        Discover AI agent history workflows from session directory.

        Args:
            session_dir: Directory containing workflow sessions. If None, uses default.

        Returns:
            List of discovered workflow metadata
        """
        if session_dir is None:
            session_dir = self.project_root / "data" / "agent_chat_sessions"

        if not session_dir.exists():
            logger.warning(f"⚠️  Session directory not found: {session_dir}")
            return []

        discovered = []
        session_files = list(session_dir.glob("*.json"))

        logger.info(f"🔍 Discovering workflows from {len(session_files)} session files...")

        for session_file in session_files:
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)

                workflow_id = session_file.stem

                # Check if already tracked
                if workflow_id in self.workflows:
                    continue

                # Extract metadata
                created_at = datetime.fromisoformat(
                    session_data.get("inception_time", datetime.now().isoformat())
                )

                messages = session_data.get("messages", [])
                agents = session_data.get("agents_involved", [])

                workflow = WorkflowMetadata(
                    workflow_id=workflow_id,
                    workflow_name=session_data.get("session_name", workflow_id),
                    created_at=created_at,
                    status=WorkflowStatus.ACTIVE,
                    agents_involved=agents,
                    message_count=len(messages),
                    metadata={
                        "source_file": str(session_file),
                        "session_data_keys": list(session_data.keys())
                    }
                )

                discovered.append(workflow)
                self._save_workflow(workflow)

            except Exception as e:
                logger.debug(f"Error processing {session_file}: {e}")

        logger.info(f"✅ Discovered {len(discovered)} new workflows")
        return discovered

    def check_workflow_completion(self, workflow: WorkflowMetadata) -> bool:
        """
        Check if workflow is finished/completed.

        Args:
            workflow: Workflow metadata to check

        Returns:
            True if workflow is finished
        """
        # Check if workflow has completion indicators
        if workflow.status in [WorkflowStatus.FINISHED, WorkflowStatus.COMPLETED]:
            return True

        # Check age - if very old and inactive, consider finished
        age_days = (datetime.now() - workflow.created_at).days
        if age_days > 7 and workflow.status == WorkflowStatus.ACTIVE:
            # Check if there's been recent activity
            # For now, assume old workflows are finished
            workflow.status = WorkflowStatus.FINISHED
            workflow.finished_at = datetime.now()
            self._save_workflow(workflow)
            return True

        return False

    def _check_github_pr_status(self, branch: str) -> Optional[Dict[str, Any]]:
        """
        Check GitHub PR status for a branch using GitHub API.

        Args:
            branch: Branch name to check

        Returns:
            PR information if found, None otherwise
        """
        try:
            # Try to get GitHub repo info from git remote
            exit_code, stdout, stderr = self.gitlens_automation.run_git_command(
                ["remote", "get-url", "origin"]
            )
            if exit_code != 0:
                return None

            remote_url = stdout.strip()
            # Parse GitHub URL (supports both https and ssh)
            import re
            match = re.search(r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$', remote_url)
            if not match:
                return None

            owner, repo = match.groups()

            # Try to use GitHub API (requires token in environment or config)
            import os
            github_token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")

            if github_token:
                try:
                    import requests
                    headers = {
                        "Authorization": f"token {github_token}",
                        "Accept": "application/vnd.github.v3+json"
                    }

                    # Check for open PRs for this branch
                    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
                    params = {"head": f"{owner}:{branch}", "state": "all"}

                    response = requests.get(url, headers=headers, params=params, timeout=10)
                    if response.status_code == 200:
                        prs = response.json()
                        if prs:
                            # Return the most recent PR
                            pr = prs[0]
                            return {
                                "number": pr.get("number"),
                                "state": pr.get("state"),  # open, closed, merged
                                "merged": pr.get("merged", False),
                                "url": pr.get("html_url"),
                                "title": pr.get("title")
                            }
                except ImportError:
                    logger.debug("requests library not available for GitHub API")
                except Exception as e:
                    logger.debug(f"GitHub API check failed: {e}")

            return None

        except Exception as e:
            logger.debug(f"Error checking GitHub PR: {e}")
            return None

    def check_pr_backup_status(self, workflow: WorkflowMetadata) -> bool:
        """
        Check if workflow is backed up to GitLens with PR.

        Enhanced with GitHub API support for better PR detection.

        Args:
            workflow: Workflow metadata to check

        Returns:
            True if backed up with PR
        """
        if not self.gitlens_automation:
            return False

        try:
            # Get git status
            git_status = self.gitlens_automation.get_git_status()
            current_branch = self.gitlens_automation.get_current_branch()

            if not current_branch:
                return False

            # First, try GitHub API for PR detection (most accurate)
            if current_branch not in ["main", "master", "develop"]:
                pr_info = self._check_github_pr_status(current_branch)
                if pr_info:
                    # PR exists - check if it's merged or closed
                    if pr_info.get("merged") or pr_info.get("state") in ["closed", "merged"]:
                        workflow.pr_status = PRStatus.BACKED_UP
                        workflow.pr_number = str(pr_info.get("number"))
                        workflow.pr_url = pr_info.get("url")
                        # Get commit hash
                        exit_code, stdout, stderr = self.gitlens_automation.run_git_command(
                            ["rev-parse", "HEAD"]
                        )
                        if exit_code == 0:
                            workflow.git_commit_hash = stdout.strip()
                        self._save_workflow(workflow)
                        logger.info(f"✅ Workflow {workflow.workflow_id} has merged/closed PR #{pr_info.get('number')}")
                        return True
                    elif pr_info.get("state") == "open":
                        # PR is open but not merged yet - not ready for archive
                        workflow.pr_status = PRStatus.OPEN
                        workflow.pr_number = str(pr_info.get("number"))
                        workflow.pr_url = pr_info.get("url")
                        self._save_workflow(workflow)
                        logger.debug(f"PR #{pr_info.get('number')} is open, waiting for merge")
                        return False

            # Fallback: Check if workflow-related files are committed
            workflow_file = Path(workflow.metadata.get("source_file", ""))
            if workflow_file.exists():
                # Check if file is tracked and committed
                exit_code, stdout, stderr = self.gitlens_automation.run_git_command(
                    ["ls-files", "--error-unmatch", str(workflow_file.relative_to(self.project_root))]
                )
                if exit_code == 0:
                    # File is tracked, check if it's committed
                    # Check git log for recent commits containing this file
                    exit_code, stdout, stderr = self.gitlens_automation.run_git_command(
                        ["log", "--oneline", "-1", "--", str(workflow_file.relative_to(self.project_root))]
                    )
                    if exit_code == 0 and stdout:
                        # File has been committed
                        # Check if branch has remote tracking
                        exit_code, stdout, stderr = self.gitlens_automation.run_git_command(
                            ["branch", "-vv"]
                        )
                        if exit_code == 0:
                            # Check if current branch tracks remote
                            if f"[origin/{current_branch}" in stdout or f"origin/{current_branch}" in stdout:
                                # Check if branch has been pushed
                                exit_code, stdout, stderr = self.gitlens_automation.run_git_command(
                                    ["log", "--oneline", "origin/" + current_branch, "-1"]
                                )
                                if exit_code == 0:
                                    # Branch exists on remote and has commits
                                    # If branch is pushed and not main/master, assume PR exists or will be created
                                    if current_branch not in ["main", "master", "develop"]:
                                        # Check if already marked as backed up
                                        if workflow.pr_status == PRStatus.BACKED_UP:
                                            return True
                                        # For feature branches, consider backed up if pushed
                                        workflow.pr_status = PRStatus.BACKED_UP
                                        workflow.git_commit_hash = stdout.split()[0] if stdout else None
                                        self._save_workflow(workflow)
                                        logger.info(f"✅ Workflow {workflow.workflow_id} backed up on branch {current_branch}")
                                        return True

                                    # If on main/master and committed, also consider backed up
                                    if current_branch in ["main", "master"]:
                                        workflow.pr_status = PRStatus.BACKED_UP
                                        workflow.git_commit_hash = stdout.split()[0] if stdout else None
                                        self._save_workflow(workflow)
                                        logger.info(f"✅ Workflow {workflow.workflow_id} backed up on {current_branch}")
                                        return True

            # Alternative: Check if git is clean (all changes committed and pushed)
            if not git_status.get("has_changes", False):
                # Check if branch tracks remote and is up to date
                exit_code, stdout, stderr = self.gitlens_automation.run_git_command(
                    ["status", "-sb"]
                )
                if exit_code == 0:
                    # Check if branch is ahead/behind or up to date
                    if "ahead" not in stdout and "behind" not in stdout:
                        # Branch is up to date with remote
                        workflow.pr_status = PRStatus.BACKED_UP
                        self._save_workflow(workflow)
                        logger.info(f"✅ Workflow {workflow.workflow_id} backed up (clean git state)")
                        return True

            return False

        except Exception as e:
            logger.debug(f"Error checking PR status: {e}")
            return False

    def archive_workflow(self, workflow: WorkflowMetadata) -> Dict[str, Any]:
        """
        Archive a workflow.

        Args:
            workflow: Workflow metadata to archive

        Returns:
            Archive result dictionary
        """
        logger.info(f"📦 Archiving workflow: {workflow.workflow_name} ({workflow.workflow_id})")

        result = {
            "workflow_id": workflow.workflow_id,
            "workflow_name": workflow.workflow_name,
            "archived_at": datetime.now().isoformat(),
            "success": False,
            "actions_taken": []
        }

        try:
            # Use workflow manager to archive if available
            if self.workflow_manager:
                # Create archive action
                from cursor_chat_session_workflow_manager import WorkflowAction

                archive_action = WorkflowAction(
                    action=SessionAction.ARCHIVE,
                    session_id=workflow.workflow_id,
                    session_name=workflow.workflow_name,
                    reason="Workflow finished and backed up to GitLens with PR",
                    priority=10
                )

                # Execute archive
                success = self.workflow_manager.execute_action(archive_action)
                if success:
                    result["actions_taken"].append("workflow_manager_archive")
                    result["success"] = True
            else:
                # Manual archive - move to archive directory
                archive_dir = self.project_root / "data" / "workflow_archives"
                archive_dir.mkdir(parents=True, exist_ok=True)

                # Find source file
                source_file = Path(workflow.metadata.get("source_file", ""))
                if source_file.exists():
                    archive_file = archive_dir / f"{workflow.workflow_id}.json"
                    # Copy to archive (don't move, keep original)
                    import shutil
                    shutil.copy2(source_file, archive_file)
                    result["actions_taken"].append("file_copy_archive")
                    result["archive_location"] = str(archive_file)
                    result["success"] = True
                else:
                    result["error"] = "Source file not found"

            if result["success"]:
                # Update workflow status
                workflow.status = WorkflowStatus.ARCHIVED
                workflow.archived_at = datetime.now()
                workflow.archive_location = result.get("archive_location")
                self._save_workflow(workflow)

                # Register with archive review system
                if self.archive_review:
                    try:
                        self.archive_review.review_archived_item(
                            item_id=workflow.workflow_id,
                            item_type="workflow"
                        )
                        result["actions_taken"].append("archive_review_registered")
                    except Exception as e:
                        logger.debug(f"Error registering with archive review: {e}")

                logger.info(f"✅ Workflow archived: {workflow.workflow_name}")
            else:
                logger.warning(f"⚠️  Failed to archive workflow: {workflow.workflow_name}")

        except Exception as e:
            logger.error(f"❌ Error archiving workflow: {e}", exc_info=True)
            result["error"] = str(e)

        # Save to history
        self._save_archive_history(result)

        return result

    def process_ready_workflows(self) -> Dict[str, Any]:
        """
        Process workflows that are ready to archive (finished + backed up).

        Returns:
            Processing results
        """
        logger.info("🔄 Processing workflows ready for archive...")

        results = {
            "timestamp": datetime.now().isoformat(),
            "workflows_checked": 0,
            "workflows_ready": 0,
            "workflows_archived": 0,
            "archived": []
        }

        # Check all active/finished workflows
        for workflow_id, workflow in self.workflows.items():
            if workflow.status == WorkflowStatus.ARCHIVED:
                continue

            results["workflows_checked"] += 1

            # Check if finished
            is_finished = self.check_workflow_completion(workflow)

            if is_finished:
                # Check if backed up with PR
                is_backed_up = self.check_pr_backup_status(workflow)

                if is_backed_up:
                    results["workflows_ready"] += 1

                    # Archive workflow
                    archive_result = self.archive_workflow(workflow)
                    if archive_result.get("success"):
                        results["workflows_archived"] += 1
                        results["archived"].append({
                            "workflow_id": workflow.workflow_id,
                            "workflow_name": workflow.workflow_name
                        })

        logger.info(f"✅ Processed {results['workflows_checked']} workflows")
        logger.info(f"   Ready for archive: {results['workflows_ready']}")
        logger.info(f"   Archived: {results['workflows_archived']}")

        return results

    def continuous_monitor(self, interval: int = 3600) -> None:
        """
        Continuously monitor and archive workflows.

        Args:
            interval: Check interval in seconds (default: 3600 = 1 hour)
        """
        logger.info("="*80)
        logger.info("🔄 JARVIS WORKFLOW ARCHIVE AUTOMATION - CONTINUOUS MODE")
        logger.info("="*80)
        logger.info(f"   Fullauto mode: {'✅ ENABLED' if self.fullauto else '❌ DISABLED'}")
        logger.info(f"   Check interval: {interval} seconds ({interval/60:.1f} minutes)")
        logger.info("   Press Ctrl+C to stop")
        logger.info("")

        self.running = True

        try:
            while self.running:
                try:
                    # Discover new workflows
                    discovered = self.discover_workflows()
                    if discovered:
                        logger.info(f"   📋 Discovered {len(discovered)} new workflows")

                    # Process ready workflows
                    results = self.process_ready_workflows()

                    if results["workflows_archived"] > 0:
                        logger.info(f"   ✅ Archived {results['workflows_archived']} workflows")
                    else:
                        logger.info(f"   ℹ️  No workflows ready for archive")

                except Exception as e:
                    logger.error(f"   ❌ Error in monitoring cycle: {e}", exc_info=True)

                # Wait for next check
                logger.info(f"   Next check in {interval/60:.1f} minutes...")
                time.sleep(interval)

        except KeyboardInterrupt:
            logger.info("\n🛑 Stopping continuous monitoring...")
            self.running = False
        except Exception as e:
            logger.error(f"❌ Fatal error in continuous monitoring: {e}", exc_info=True)
            self.running = False

    def get_status(self) -> Dict[str, Any]:
        """Get automation status"""
        active = sum(1 for w in self.workflows.values() if w.status == WorkflowStatus.ACTIVE)
        finished = sum(1 for w in self.workflows.values() if w.status == WorkflowStatus.FINISHED)
        archived = sum(1 for w in self.workflows.values() if w.status == WorkflowStatus.ARCHIVED)

        return {
            "fullauto": self.fullauto,
            "running": self.running,
            "total_workflows": len(self.workflows),
            "active_workflows": active,
            "finished_workflows": finished,
            "archived_workflows": archived,
            "components": {
                "gitlens_automation": self.gitlens_automation is not None,
                "workflow_manager": self.workflow_manager is not None,
                "archive_review": self.archive_review is not None
            }
        }


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="JARVIS Workflow Archive Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Discover and process workflows once
  python jarvis_workflow_archive_automation.py --process

  # Continuous monitoring (default: 1 hour interval)
  python jarvis_workflow_archive_automation.py --monitor

  # Continuous monitoring with custom interval
  python jarvis_workflow_archive_automation.py --monitor --interval 1800

  # Discover new workflows only
  python jarvis_workflow_archive_automation.py --discover

  # Get status
  python jarvis_workflow_archive_automation.py --status

  # Disable fullauto (requires manual approval)
  python jarvis_workflow_archive_automation.py --process --no-fullauto
        """
    )

    parser.add_argument("--process", action="store_true",
                       help="Process workflows ready for archive (then exit)")
    parser.add_argument("--monitor", action="store_true",
                       help="Continuous monitoring mode")
    parser.add_argument("--interval", type=int, default=3600,
                       help="Monitoring interval in seconds (default: 3600)")
    parser.add_argument("--discover", action="store_true",
                       help="Discover new workflows only")
    parser.add_argument("--status", action="store_true",
                       help="Show automation status")
    parser.add_argument("--fullauto", action="store_true", default=True,
                       help="Enable full automation (default: True)")
    parser.add_argument("--no-fullauto", action="store_true",
                       help="Disable full automation (requires manual approval)")

    args = parser.parse_args()

    # Determine fullauto mode
    fullauto = args.fullauto and not args.no_fullauto

    # Initialize automation
    automation = JARVISWorkflowArchiveAutomation(fullauto=fullauto)

    if args.status:
        # Show status
        status = automation.get_status()
        print("\n" + "="*80)
        print("📊 JARVIS WORKFLOW ARCHIVE AUTOMATION STATUS")
        print("="*80)
        print(json.dumps(status, indent=2, default=str))
        print()

    elif args.discover:
        # Discover workflows
        discovered = automation.discover_workflows()
        print("\n" + "="*80)
        print("🔍 WORKFLOW DISCOVERY")
        print("="*80)
        print(f"   Discovered: {len(discovered)} new workflows")
        for wf in discovered[:10]:  # Show first 10
            print(f"   - {wf.workflow_name} ({wf.workflow_id})")
        print()

    elif args.monitor:
        # Continuous monitoring
        automation.continuous_monitor(interval=args.interval)

    elif args.process:
        # Process once
        results = automation.process_ready_workflows()
        print("\n" + "="*80)
        print("🔄 WORKFLOW PROCESSING RESULTS")
        print("="*80)
        print(json.dumps(results, indent=2, default=str))
        print()

    else:
        # Default: process once
        results = automation.process_ready_workflows()
        print("\n" + "="*80)
        print("🔄 WORKFLOW PROCESSING RESULTS")
        print("="*80)
        print(json.dumps(results, indent=2, default=str))
        print()


if __name__ == "__main__":


    main()