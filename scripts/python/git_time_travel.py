#!/usr/bin/env python3
"""
Git Time Travel System

Navigate to any point in project lifetime using Git/GitLens versioning.
Supports:
- Major/minor milestone tagging
- Time travel to any commit
- State restoration
- Cross-environment synchronization
- Project history navigation
"""

import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - ⏰ GitTimeTravel - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GitTimeTravel:
    """
    Git Time Travel System

    Navigate project history using Git/GitLens
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.milestones_file = self.project_root / "data" / "git_milestones.json"

    def run_git_command(self, command: List[str], capture_output: bool = True) -> Tuple[int, str, str]:
        """Run a git command"""
        try:
            cmd = ["git"] + command
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
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

    def get_current_commit(self) -> Optional[Dict[str, Any]]:
        """Get current commit information"""
        exit_code, stdout, stderr = self.run_git_command(["log", "-1", "--pretty=format:%H|%an|%ae|%ad|%s", "--date=iso"])

        if exit_code != 0:
            return None

        parts = stdout.split("|")
        if len(parts) >= 5:
            return {
                "hash": parts[0],
                "author": parts[1],
                "email": parts[2],
                "date": parts[3],
                "message": parts[4]
            }

        return None

    def get_commit_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get commit history"""
        exit_code, stdout, stderr = self.run_git_command([
            "log",
            f"-{limit}",
            "--pretty=format:%H|%an|%ae|%ad|%s",
            "--date=iso"
        ])

        if exit_code != 0:
            return []

        commits = []
        for line in stdout.split("\n"):
            if not line.strip():
                continue
            parts = line.split("|")
            if len(parts) >= 5:
                commits.append({
                    "hash": parts[0],
                    "author": parts[1],
                    "email": parts[2],
                    "date": parts[3],
                    "message": parts[4]
                })

        return commits

    def get_tags(self) -> List[Dict[str, Any]]:
        """Get all git tags"""
        exit_code, stdout, stderr = self.run_git_command(["tag", "-l", "--sort=-version:refname"])

        if exit_code != 0:
            return []

        tags = []
        for tag in stdout.split("\n"):
            if not tag.strip():
                continue

            # Get tag info
            exit_code2, stdout2, stderr2 = self.run_git_command([
                "log", "-1", f"{tag}", "--pretty=format:%H|%an|%ae|%ad|%s", "--date=iso"
            ])

            if exit_code2 == 0:
                parts = stdout2.split("|")
                if len(parts) >= 5:
                    tags.append({
                        "tag": tag,
                        "hash": parts[0],
                        "author": parts[1],
                        "email": parts[2],
                        "date": parts[3],
                        "message": parts[4]
                    })

        return tags

    def create_milestone_tag(self, version: str, milestone_type: str = "minor", message: Optional[str] = None) -> Tuple[bool, str]:
        """
        Create a milestone tag (major or minor)

        Args:
            version: Version string (e.g., "1.0.0", "2.1.0")
            milestone_type: "major" or "minor"
            message: Optional tag message
        """
        tag_name = f"v{version}"

        if message is None:
            message = f"{milestone_type.upper()} milestone: {version}"

        # Create annotated tag
        exit_code, stdout, stderr = self.run_git_command([
            "tag", "-a", tag_name, "-m", message
        ])

        if exit_code != 0:
            return False, f"Failed to create tag: {stderr}"

        # Save milestone info
        self._save_milestone(tag_name, version, milestone_type, message)

        logger.info(f"✅ Created {milestone_type} milestone tag: {tag_name}")
        return True, f"Created tag: {tag_name}"

    def _save_milestone(self, tag: str, version: str, milestone_type: str, message: str):
        try:
            """Save milestone information"""
            milestones = self._load_milestones()

            current_commit = self.get_current_commit()

            milestone = {
                "tag": tag,
                "version": version,
                "type": milestone_type,
                "message": message,
                "commit_hash": current_commit["hash"] if current_commit else "unknown",
                "date": datetime.now().isoformat(),
                "author": current_commit["author"] if current_commit else "unknown"
            }

            milestones["milestones"].append(milestone)
            milestones["last_updated"] = datetime.now().isoformat()

            # Save to file
            self.milestones_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.milestones_file, 'w', encoding='utf-8') as f:
                json.dump(milestones, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_milestone: {e}", exc_info=True)
            raise
    def _load_milestones(self) -> Dict[str, Any]:
        """Load milestone information"""
        if self.milestones_file.exists():
            try:
                with open(self.milestones_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "milestones": [],
            "last_updated": datetime.now().isoformat()
        }

    def travel_to_commit(self, commit_hash: str, create_branch: bool = False) -> Tuple[bool, str]:
        """
        Travel to a specific commit (checkout)

        Args:
            commit_hash: Commit hash or tag
            create_branch: If True, create a new branch at this commit
        """
        if create_branch:
            branch_name = f"time-travel-{commit_hash[:8]}"
            exit_code, stdout, stderr = self.run_git_command([
                "checkout", "-b", branch_name, commit_hash
            ])
        else:
            exit_code, stdout, stderr = self.run_git_command([
                "checkout", commit_hash
            ])

        if exit_code != 0:
            return False, f"Failed to checkout: {stderr}"

        logger.info(f"✅ Traveled to commit: {commit_hash[:8]}")
        return True, f"Checked out: {commit_hash[:8]}"

    def travel_to_milestone(self, milestone_tag: str, create_branch: bool = False) -> Tuple[bool, str]:
        """Travel to a milestone tag"""
        return self.travel_to_commit(milestone_tag, create_branch)

    def get_project_timeline(self) -> Dict[str, Any]:
        """Get complete project timeline"""
        commits = self.get_commit_history(limit=1000)
        tags = self.get_tags()
        milestones = self._load_milestones()

        # Combine and sort by date
        timeline_items = []

        for commit in commits:
            timeline_items.append({
                "type": "commit",
                "hash": commit["hash"],
                "date": commit["date"],
                "message": commit["message"],
                "author": commit["author"]
            })

        for tag in tags:
            timeline_items.append({
                "type": "tag",
                "tag": tag["tag"],
                "hash": tag["hash"],
                "date": tag["date"],
                "message": tag["message"],
                "author": tag["author"]
            })

        # Sort by date
        timeline_items.sort(key=lambda x: x["date"], reverse=True)

        return {
            "total_commits": len(commits),
            "total_tags": len(tags),
            "total_milestones": len(milestones.get("milestones", [])),
            "timeline": timeline_items[:100]  # Last 100 items
        }

    def restore_state(self, commit_hash: str, target_path: Optional[Path] = None) -> Tuple[bool, str]:
        """
        Restore project state from a commit

        Args:
            commit_hash: Commit hash or tag to restore from
            target_path: Optional path to restore to (creates a copy)
        """
        if target_path:
            # Create a copy at target path
            exit_code, stdout, stderr = self.run_git_command([
                "archive", "--format=tar", commit_hash
            ])
            # This would need additional handling for extraction
            return False, "Archive restoration not fully implemented"
        else:
            # Restore in place
            return self.travel_to_commit(commit_hash, create_branch=False)

    def compare_environments(self, env1_commit: str, env2_commit: str) -> Dict[str, Any]:
        """Compare two environment states"""
        exit_code, stdout, stderr = self.run_git_command([
            "diff", "--stat", env1_commit, env2_commit
        ])

        if exit_code != 0:
            return {"error": stderr}

        # Parse diff stats
        changes = {
            "files_changed": 0,
            "insertions": 0,
            "deletions": 0,
            "files": []
        }

        for line in stdout.split("\n"):
            if "|" in line:
                parts = line.split("|")
                if len(parts) >= 2:
                    file_info = parts[0].strip()
                    change_info = parts[1].strip()

                    changes["files"].append({
                        "file": file_info,
                        "changes": change_info
                    })
                    changes["files_changed"] += 1

        return changes


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Git Time Travel System")
    parser.add_argument("--timeline", action="store_true", help="Show project timeline")
    parser.add_argument("--milestone", type=str, help="Create milestone tag (format: version:type, e.g., 1.0.0:major)")
    parser.add_argument("--travel", type=str, help="Travel to commit hash or tag")
    parser.add_argument("--branch", action="store_true", help="Create branch when traveling")
    parser.add_argument("--current", action="store_true", help="Show current commit")
    parser.add_argument("--history", type=int, default=20, help="Show commit history (default: 20)")
    parser.add_argument("--tags", action="store_true", help="Show all tags")

    args = parser.parse_args()

    time_travel = GitTimeTravel()

    if args.current:
        commit = time_travel.get_current_commit()
        if commit:
            print("\n" + "=" * 80)
            print("📍 CURRENT COMMIT")
            print("=" * 80)
            print(f"Hash: {commit['hash']}")
            print(f"Author: {commit['author']} ({commit['email']})")
            print(f"Date: {commit['date']}")
            print(f"Message: {commit['message']}")
            print()
        else:
            print("❌ Could not get current commit")

    if args.history:
        commits = time_travel.get_commit_history(limit=args.history)
        print("\n" + "=" * 80)
        print(f"📜 COMMIT HISTORY (Last {len(commits)} commits)")
        print("=" * 80)
        for i, commit in enumerate(commits, 1):
            print(f"{i}. {commit['hash'][:8]} - {commit['date']}")
            print(f"   {commit['message']}")
            print(f"   {commit['author']}")
            print()

    if args.tags:
        tags = time_travel.get_tags()
        print("\n" + "=" * 80)
        print(f"🏷️  TAGS ({len(tags)} total)")
        print("=" * 80)
        for tag in tags:
            print(f"  {tag['tag']} - {tag['date']}")
            print(f"    {tag['message']}")
            print()

    if args.timeline:
        timeline = time_travel.get_project_timeline()
        print("\n" + "=" * 80)
        print("⏰ PROJECT TIMELINE")
        print("=" * 80)
        print(f"Total Commits: {timeline['total_commits']}")
        print(f"Total Tags: {timeline['total_tags']}")
        print(f"Total Milestones: {timeline['total_milestones']}")
        print()
        print("Recent Timeline:")
        for item in timeline['timeline'][:20]:
            icon = "🏷️" if item['type'] == 'tag' else "📝"
            print(f"  {icon} {item.get('tag', item.get('hash', ''))[:8]} - {item['date']}")
            print(f"     {item['message']}")
            print()

    if args.milestone:
        parts = args.milestone.split(":")
        if len(parts) == 2:
            version, milestone_type = parts
            success, message = time_travel.create_milestone_tag(version, milestone_type)
            print(f"{'✅' if success else '❌'} {message}")
        else:
            print("❌ Invalid milestone format. Use: version:type (e.g., 1.0.0:major)")

    if args.travel:
        success, message = time_travel.travel_to_commit(args.travel, create_branch=args.branch)
        print(f"{'✅' if success else '❌'} {message}")


if __name__ == "__main__":



    main()