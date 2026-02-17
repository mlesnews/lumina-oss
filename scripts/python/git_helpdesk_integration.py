#!/usr/bin/env python3
"""
Git/GitLens + Help Desk Integration

Git/GitLens and internal help desk need to be one complete unit of:
- Problem documentation
- Tracking
"""

import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)


class ProblemStatus(Enum):
    """Problem status"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"


@dataclass
class ProblemDocumentation:
    """Problem documentation entry"""
    problem_id: str
    title: str
    description: str
    status: ProblemStatus
    git_commit_hash: Optional[str] = None
    git_branch: Optional[str] = None
    gitlens_issue_id: Optional[str] = None
    helpdesk_ticket_id: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    resolved_at: Optional[str] = None
    related_files: List[str] = field(default_factory=list)
    related_commits: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


class GitHelpdeskIntegration:
    """
    Git/GitLens + Help Desk Integration

    One complete unit for problem documentation and tracking.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("GitHelpdeskIntegration")

        # Directories
        self.data_dir = self.project_root / "data" / "git_helpdesk"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Files
        self.problems_file = self.data_dir / "problems.json"
        self.git_mapping_file = self.data_dir / "git_mapping.json"
        self.helpdesk_mapping_file = self.data_dir / "helpdesk_mapping.json"

        # Help desk config
        self.helpdesk_config = self.project_root / "config" / "helpdesk" / "helpdesk_structure.json"

        # State
        self.problems: Dict[str, ProblemDocumentation] = {}
        self.git_to_problem: Dict[str, str] = {}  # commit_hash -> problem_id
        self.helpdesk_to_problem: Dict[str, str] = {}  # ticket_id -> problem_id

        # Load state
        self._load_state()

    def _load_state(self):
        """Load state"""
        # Load problems
        if self.problems_file.exists():
            try:
                with open(self.problems_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for problem_id, problem_data in data.items():
                        problem = ProblemDocumentation(**problem_data)
                        problem.status = ProblemStatus(problem_data["status"])
                        self.problems[problem_id] = problem
            except Exception as e:
                self.logger.error(f"Error loading problems: {e}")

        # Load git mapping
        if self.git_mapping_file.exists():
            try:
                with open(self.git_mapping_file, 'r', encoding='utf-8') as f:
                    self.git_to_problem = json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading git mapping: {e}")

        # Load helpdesk mapping
        if self.helpdesk_mapping_file.exists():
            try:
                with open(self.helpdesk_mapping_file, 'r', encoding='utf-8') as f:
                    self.helpdesk_to_problem = json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading helpdesk mapping: {e}")

    def _save_state(self):
        try:
            """Save state"""
            # Save problems
            problems_data = {
                problem_id: problem.to_dict()
                for problem_id, problem in self.problems.items()
            }
            with open(self.problems_file, 'w', encoding='utf-8') as f:
                json.dump(problems_data, f, indent=2, ensure_ascii=False)

            # Save git mapping
            with open(self.git_mapping_file, 'w', encoding='utf-8') as f:
                json.dump(self.git_to_problem, f, indent=2, ensure_ascii=False)

            # Save helpdesk mapping
            with open(self.helpdesk_mapping_file, 'w', encoding='utf-8') as f:
                json.dump(self.helpdesk_to_problem, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in _save_state: {e}", exc_info=True)
            raise
    def create_problem(
        self,
        title: str,
        description: str,
        git_commit_hash: Optional[str] = None,
        git_branch: Optional[str] = None,
        gitlens_issue_id: Optional[str] = None,
        helpdesk_ticket_id: Optional[str] = None,
        related_files: Optional[List[str]] = None
    ) -> ProblemDocumentation:
        """
        Create problem documentation

        Links Git/GitLens with help desk
        """
        problem_id = f"problem_{int(datetime.now().timestamp() * 1000)}"
        now = datetime.now().isoformat()

        # Get current git info if not provided
        if not git_commit_hash:
            git_commit_hash = self._get_current_commit_hash()
        if not git_branch:
            git_branch = self._get_current_branch()

        problem = ProblemDocumentation(
            problem_id=problem_id,
            title=title,
            description=description,
            status=ProblemStatus.OPEN,
            git_commit_hash=git_commit_hash,
            git_branch=git_branch,
            gitlens_issue_id=gitlens_issue_id,
            helpdesk_ticket_id=helpdesk_ticket_id,
            created_at=now,
            updated_at=now,
            related_files=related_files or []
        )

        self.problems[problem_id] = problem

        # Map git to problem
        if git_commit_hash:
            self.git_to_problem[git_commit_hash] = problem_id

        # Map helpdesk to problem
        if helpdesk_ticket_id:
            self.helpdesk_to_problem[helpdesk_ticket_id] = problem_id

        # Get related commits
        if related_files:
            problem.related_commits = self._get_commits_for_files(related_files)

        self._save_state()

        self.logger.info(f"📝 Created problem: {problem_id} - {title}")

        return problem

    def _get_current_commit_hash(self) -> Optional[str]:
        """Get current git commit hash"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            self.logger.debug(f"Could not get commit hash: {e}")
        return None

    def _get_current_branch(self) -> Optional[str]:
        """Get current git branch"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            self.logger.debug(f"Could not get branch: {e}")
        return None

    def _get_commits_for_files(self, files: List[str]) -> List[str]:
        """Get commits related to files"""
        commits = []
        try:
            for file_path in files:
                result = subprocess.run(
                    ['git', 'log', '--oneline', '--', file_path],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    file_commits = [line.split()[0] for line in result.stdout.strip().split('\n') if line]
                    commits.extend(file_commits[:10])  # Last 10 commits per file
        except Exception as e:
            self.logger.debug(f"Could not get commits for files: {e}")
        return list(set(commits))  # Remove duplicates

    def link_git_commit(self, problem_id: str, commit_hash: str) -> bool:
        """Link git commit to problem"""
        if problem_id not in self.problems:
            return False

        problem = self.problems[problem_id]
        problem.git_commit_hash = commit_hash
        problem.updated_at = datetime.now().isoformat()

        self.git_to_problem[commit_hash] = problem_id

        # Get related files from commit
        related_files = self._get_files_from_commit(commit_hash)
        problem.related_files.extend(related_files)
        problem.related_files = list(set(problem.related_files))  # Remove duplicates

        # Get related commits
        problem.related_commits = self._get_commits_for_files(problem.related_files)

        self._save_state()

        self.logger.info(f"🔗 Linked git commit {commit_hash} to problem {problem_id}")

        return True

    def _get_files_from_commit(self, commit_hash: str) -> List[str]:
        """Get files changed in commit"""
        try:
            result = subprocess.run(
                ['git', 'show', '--name-only', '--pretty=format:', commit_hash],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
        except Exception as e:
            self.logger.debug(f"Could not get files from commit: {e}")
        return []

    def link_helpdesk_ticket(self, problem_id: str, ticket_id: str) -> bool:
        """Link helpdesk ticket to problem"""
        if problem_id not in self.problems:
            return False

        problem = self.problems[problem_id]
        problem.helpdesk_ticket_id = ticket_id
        problem.updated_at = datetime.now().isoformat()

        self.helpdesk_to_problem[ticket_id] = problem_id

        self._save_state()

        self.logger.info(f"🔗 Linked helpdesk ticket {ticket_id} to problem {problem_id}")

        return True

    def update_problem_status(
        self,
        problem_id: str,
        status: ProblemStatus
    ) -> bool:
        """Update problem status"""
        if problem_id not in self.problems:
            return False

        problem = self.problems[problem_id]
        problem.status = status
        problem.updated_at = datetime.now().isoformat()

        if status == ProblemStatus.RESOLVED:
            problem.resolved_at = datetime.now().isoformat()

        self._save_state()

        self.logger.info(f"✅ Updated problem {problem_id} status: {status.value}")

        return True

    def get_problem_by_git_commit(self, commit_hash: str) -> Optional[ProblemDocumentation]:
        """Get problem by git commit"""
        problem_id = self.git_to_problem.get(commit_hash)
        if problem_id:
            return self.problems.get(problem_id)
        return None

    def get_problem_by_helpdesk_ticket(self, ticket_id: str) -> Optional[ProblemDocumentation]:
        """Get problem by helpdesk ticket"""
        problem_id = self.helpdesk_to_problem.get(ticket_id)
        if problem_id:
            return self.problems.get(problem_id)
        return None

    def create_problem_from_marvin_fault(
        self,
        fault_id: str,
        fault_description: str,
        fault_specific: str,
        comprehensive_description: Optional[str] = None
    ) -> ProblemDocumentation:
        """Create problem from MARVIN fault with comprehensive description"""
        title = f"MARVIN Fault: {fault_specific}"
        description = comprehensive_description or f"{fault_description}\n\nSpecific Fault: {fault_specific}"

        problem = self.create_problem(
            title=title,
            description=description,
            related_files=[]  # Will be populated from git
        )

        problem.metadata["fault_id"] = fault_id
        problem.metadata["source"] = "marvin_roast"

        self._save_state()

        return problem

    def create_comprehensive_commit_message(
        self,
        problem: ProblemDocumentation,
        action_taken: str,
        files_changed: List[str]
    ) -> str:
        """
        Create comprehensive, robust descriptive commit message

        Format:
        - Problem summary
        - Action taken
        - Files changed
        - Helpdesk ticket reference
        """
        commit_message = f"""Fix: {problem.title}

{problem.description}

## Action Taken
{action_taken}

## Files Changed
{chr(10).join(f'- {f}' for f in files_changed)}

## Related
- Helpdesk Ticket: {problem.helpdesk_ticket_id or 'N/A'}
- Problem ID: {problem.problem_id}
- Git Commit: {problem.git_commit_hash or 'N/A'}

## Status
- Fixed: {datetime.now().isoformat()}
- Verified: Pending
"""
        return commit_message.strip()


def main():
    """Main execution for testing"""
    integration = GitHelpdeskIntegration()

    print("=" * 80)
    print("🔗 GIT/HELPDESK INTEGRATION")
    print("=" * 80)

    # Create problem
    problem = integration.create_problem(
        title="Test Problem",
        description="Test problem documentation",
        related_files=["scripts/python/test.py"]
    )

    print(f"\n📝 Created Problem:")
    print(f"   ID: {problem.problem_id}")
    print(f"   Title: {problem.title}")
    print(f"   Git Commit: {problem.git_commit_hash}")
    print(f"   Git Branch: {problem.git_branch}")
    print(f"   Related Commits: {len(problem.related_commits)}")


if __name__ == "__main__":



    main()