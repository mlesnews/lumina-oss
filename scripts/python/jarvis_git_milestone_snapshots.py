#!/usr/bin/env python3
"""
JARVIS Git Milestone Snapshots

Automatically creates Git repository snapshots (commits) at each
major/minor milestone, following KILO CODE principles.
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISGitSnapshots")


class MilestoneType:
    """Milestone types"""
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    WORKFLOW = "workflow"
    FEATURE = "feature"
    SYSTEM = "system"


class JARVISGitMilestoneSnapshots:
    """
    Automatic Git snapshots at milestones

    Creates Git commits automatically at each major/minor milestone,
    following KILO CODE principles.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Milestone tracking
        self.milestones_dir = project_root / "data" / "milestones"
        self.milestones_dir.mkdir(parents=True, exist_ok=True)

        # Snapshot log
        self.snapshots_log = project_root / "data" / "git_snapshots_log.json"

        # Check if Git repo
        self.is_git_repo = (project_root / ".git").exists()

        if not self.is_git_repo:
            self.logger.warning("⚠️ Not a Git repository - snapshots disabled")

    def create_milestone_snapshot(self, milestone_type: str, description: str,
                                 changes: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a Git snapshot at a milestone

        Args:
            milestone_type: Type of milestone (major, minor, patch, workflow, feature, system)
            description: Description of the milestone
            changes: Optional list of changes made

        Returns:
            Snapshot result
        """
        if not self.is_git_repo:
            return {
                'success': False,
                'error': 'Not a Git repository'
            }

        timestamp = datetime.now()
        milestone_id = f"{milestone_type}_{timestamp.strftime('%Y%m%d_%H%M%S')}"

        self.logger.info("="*80)
        self.logger.info(f"CREATING MILESTONE SNAPSHOT: {milestone_type.upper()}")
        self.logger.info(f"Description: {description}")
        self.logger.info("="*80)

        try:
            # Stage all changes (ignore errors for files with long names)
            self.logger.info("Staging all changes...")
            stage_result = subprocess.run(
                ["git", "add", "-A"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )

            # Check if there are any stagged changes despite errors
            status_result = subprocess.run(
                ["git", "status", "--short"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )

            # If no changes to commit, return early
            if not status_result.stdout.strip():
                self.logger.info("No changes to commit")
                return {
                    'success': True,
                    'message': 'No changes to commit',
                    'milestone_id': milestone_id,
                    'warning': stage_result.stderr if stage_result.returncode != 0 else None
                }

            # If staging had errors but we have changes, log warning but continue
            if stage_result.returncode != 0:
                self.logger.warning(f"Some files could not be staged: {stage_result.stderr[:200]}")
                # Try to stage specific directories that are likely to work
                safe_dirs = ["scripts/", "docs/", "config/", "data/"]
                for safe_dir in safe_dirs:
                    safe_path = self.project_root / safe_dir
                    if safe_path.exists():
                        subprocess.run(
                            ["git", "add", safe_dir],
                            cwd=self.project_root,
                            capture_output=True,
                            text=True
                        )

            # Get status
            status_result = subprocess.run(
                ["git", "status", "--short"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )

            if not status_result.stdout.strip():
                self.logger.info("No changes to commit")
                return {
                    'success': True,
                    'message': 'No changes to commit',
                    'milestone_id': milestone_id
                }

            # Create commit message
            commit_message = self._create_commit_message(milestone_type, description, changes)

            # Create commit
            self.logger.info("Creating Git commit...")
            commit_result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )

            if commit_result.returncode != 0:
                return {
                    'success': False,
                    'error': f"Git commit failed: {commit_result.stderr}"
                }

            # Get commit hash
            hash_result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )

            commit_hash = hash_result.stdout.strip() if hash_result.returncode == 0 else "unknown"

            # Save milestone record
            milestone_record = {
                'milestone_id': milestone_id,
                'milestone_type': milestone_type,
                'description': description,
                'commit_hash': commit_hash,
                'timestamp': timestamp.isoformat(),
                'changes': changes or [],
                'status': 'committed'
            }

            self._save_milestone_record(milestone_record)
            self._log_snapshot(milestone_record)

            self.logger.info(f"✅ Milestone snapshot created: {commit_hash}")

            return {
                'success': True,
                'milestone_id': milestone_id,
                'commit_hash': commit_hash,
                'message': commit_message,
                'timestamp': timestamp.isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error creating milestone snapshot: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _create_commit_message(self, milestone_type: str, description: str,
                              changes: Optional[List[str]]) -> str:
        """Create commit message for milestone"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        message = f"[{milestone_type.upper()}] {description}\n\n"
        message += f"Milestone: {milestone_type}\n"
        message += f"Timestamp: {timestamp}\n"
        message += f"Generated by: JARVIS Git Milestone Snapshots\n"

        if changes:
            message += f"\nChanges:\n"
            for change in changes:
                message += f"  - {change}\n"

        return message

    def _save_milestone_record(self, record: Dict[str, Any]):
        """Save milestone record"""
        milestone_file = self.milestones_dir / f"{record['milestone_id']}.json"

        try:
            with open(milestone_file, 'w') as f:
                json.dump(record, f, indent=2)
            self.logger.info(f"✅ Milestone record saved: {milestone_file}")
        except Exception as e:
            self.logger.error(f"Failed to save milestone record: {e}")

    def _log_snapshot(self, record: Dict[str, Any]):
        """Log snapshot to snapshot log"""
        snapshots = []

        if self.snapshots_log.exists():
            try:
                with open(self.snapshots_log, 'r') as f:
                    snapshots = json.load(f)
            except:
                snapshots = []

        snapshots.append(record)

        try:
            with open(self.snapshots_log, 'w') as f:
                json.dump(snapshots, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to log snapshot: {e}")

    def auto_snapshot_on_milestone(self, milestone_type: str, description: str,
                                  context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Automatically create snapshot when milestone is reached

        Called automatically by workflow executor and other systems
        """
        # Extract changes from context if available
        changes = []
        if context:
            if 'steps_completed' in context:
                changes.append(f"Completed {context['steps_completed']} workflow steps")
            if 'systems_implemented' in context:
                changes.append(f"Implemented {len(context['systems_implemented'])} systems")
            if 'subagents_active' in context:
                changes.append(f"{context['subagents_active']} subagents active")

        return self.create_milestone_snapshot(milestone_type, description, changes)

    def list_milestones(self) -> List[Dict[str, Any]]:
        """List all milestones"""
        milestones = []

        for milestone_file in self.milestones_dir.glob("*.json"):
            try:
                with open(milestone_file, 'r') as f:
                    milestones.append(json.load(f))
            except Exception as e:
                self.logger.error(f"Failed to load {milestone_file}: {e}")

        return sorted(milestones, key=lambda x: x.get('timestamp', ''), reverse=True)

    def get_snapshot_summary(self) -> Dict[str, Any]:
        """Get summary of all snapshots"""
        milestones = self.list_milestones()

        by_type = {}
        for milestone in milestones:
            mtype = milestone.get('milestone_type', 'unknown')
            if mtype not in by_type:
                by_type[mtype] = 0
            by_type[mtype] += 1

        return {
            'total_milestones': len(milestones),
            'by_type': by_type,
            'latest_milestone': milestones[0] if milestones else None
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Git Milestone Snapshots")
        parser.add_argument("--snapshot", action="store_true", help="Create milestone snapshot")
        parser.add_argument("--type", type=str, choices=['major', 'minor', 'patch', 'workflow', 'feature', 'system'],
                           help="Milestone type")
        parser.add_argument("--description", type=str, help="Milestone description")
        parser.add_argument("--list", action="store_true", help="List all milestones")
        parser.add_argument("--summary", action="store_true", help="Get snapshot summary")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        snapshots = JARVISGitMilestoneSnapshots(project_root)

        if args.snapshot:
            if not args.type or not args.description:
                print("❌ Please provide --type and --description")
                return

            result = snapshots.create_milestone_snapshot(args.type, args.description)

            if result.get('success'):
                print(f"\n✅ Milestone snapshot created:")
                print(f"   Type: {args.type}")
                print(f"   Commit: {result.get('commit_hash', 'unknown')}")
                print(f"   ID: {result.get('milestone_id', 'unknown')}")
            else:
                print(f"❌ Error: {result.get('error', 'unknown error')}")

        elif args.list:
            milestones = snapshots.list_milestones()
            print(f"\n📋 Milestones: {len(milestones)}")
            for milestone in milestones[:10]:
                print(f"\n  {milestone['milestone_type'].upper()}: {milestone['description']}")
                print(f"    Commit: {milestone.get('commit_hash', 'unknown')}")
                print(f"    Time: {milestone.get('timestamp', 'unknown')}")

        elif args.summary:
            summary = snapshots.get_snapshot_summary()
            print(f"\n📊 Snapshot Summary:")
            print(f"   Total Milestones: {summary['total_milestones']}")
            print(f"   By Type:")
            for mtype, count in summary['by_type'].items():
                print(f"     {mtype}: {count}")
            if summary['latest_milestone']:
                latest = summary['latest_milestone']
                print(f"\n   Latest: {latest['milestone_type']} - {latest['description']}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()