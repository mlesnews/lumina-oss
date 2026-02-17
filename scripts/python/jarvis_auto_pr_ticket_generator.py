#!/usr/bin/env python3
"""
JARVIS Auto PR & Ticket Generator
Automatically detects major/minor issues and changes, then generates PRs and tickets.

Tags: #AUTOMATION #PR #TICKET #MONITORING @AUTO
"""

import sys
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
    from jarvis_pr_ticket_coordinator import PRTicketCoordinator, ChangeType, IssueSeverity
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    PRTicketCoordinator = None
    ChangeType = None
    IssueSeverity = None

logger = get_logger("JARVISAutoPRTicket")


class AutoPRTicketGenerator:
    """
    Automatically detects issues and changes, then generates PRs and tickets.

    Monitors:
    - Git changes (commits, branches)
    - Linter errors
    - Test failures
    - System issues
    - Configuration changes
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        if PRTicketCoordinator:
            self.coordinator = PRTicketCoordinator(project_root)
        else:
            self.coordinator = None
            self.logger.warning("⚠️  PRTicketCoordinator not available")

        self.logger.info("✅ Auto PR & Ticket Generator initialized")

    def detect_git_changes(self) -> List[Dict[str, Any]]:
        """Detect uncommitted or recent git changes"""
        changes = []

        try:
            # Check for uncommitted changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 and result.stdout.strip():
                files_changed = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        status, filepath = line.split(maxsplit=1)
                        files_changed.append(filepath)

                if files_changed:
                    changes.append({
                        "type": "uncommitted",
                        "files": files_changed,
                        "count": len(files_changed)
                    })

            # Check recent commits (last 5)
            result = subprocess.run(
                ["git", "log", "-5", "--oneline", "--no-merges"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 and result.stdout.strip():
                commits = []
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        commit_hash, *message_parts = line.split()
                        message = ' '.join(message_parts)
                        commits.append({
                            "hash": commit_hash,
                            "message": message
                        })

                if commits:
                    changes.append({
                        "type": "recent_commits",
                        "commits": commits,
                        "count": len(commits)
                    })

        except Exception as e:
            self.logger.debug(f"Git detection error: {e}")

        return changes

    def detect_linter_errors(self) -> List[Dict[str, Any]]:
        """Detect linter errors"""
        errors = []

        # This would integrate with your linter system
        # For now, placeholder
        return errors

    def analyze_changes_for_issues(self, changes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze changes to determine if they need PRs/tickets"""
        issues = []

        for change in changes:
            if change["type"] == "uncommitted":
                # Analyze file changes
                files = change.get("files", [])

                # Check for critical files
                critical_patterns = [
                    "config/", ".cursor/", "scripts/python/jarvis_",
                    "security", "auth", "credential", "password", "key"
                ]

                has_critical = any(
                    any(pattern in file for pattern in critical_patterns)
                    for file in files
                )

                if has_critical or len(files) >= 5:
                    issues.append({
                        "type": "major_change",
                        "files": files,
                        "severity": "major" if has_critical else "minor",
                        "reason": "Critical files changed" if has_critical else "Multiple files changed"
                    })

            elif change["type"] == "recent_commits":
                # Analyze commit messages
                commits = change.get("commits", [])

                for commit in commits:
                    message = commit.get("message", "").lower()

                    # Check for issue indicators
                    if any(keyword in message for keyword in [
                        "fix", "bug", "error", "issue", "problem", "security"
                    ]):
                        issues.append({
                            "type": "bug_fix",
                            "commit": commit,
                            "severity": "major" if "security" in message or "critical" in message else "minor"
                        })

        return issues

    def generate_prs_and_tickets(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate PRs and tickets for detected issues"""
        results = []

        if not self.coordinator:
            self.logger.error("❌ Coordinator not available")
            return results

        for issue in issues:
            issue_type = issue.get("type", "change")
            severity_str = issue.get("severity", "minor")

            # Map to ChangeType
            change_type_map = {
                "bug_fix": ChangeType.BUG_FIX,
                "major_change": ChangeType.ENHANCEMENT,
                "config_change": ChangeType.CONFIG,
                "security": ChangeType.SECURITY
            }
            change_type = change_type_map.get(issue_type, ChangeType.ENHANCEMENT)

            # Map to IssueSeverity
            severity_map = {
                "critical": IssueSeverity.CRITICAL,
                "major": IssueSeverity.MAJOR,
                "minor": IssueSeverity.MINOR,
                "trivial": IssueSeverity.TRIVIAL
            }
            severity = severity_map.get(severity_str, IssueSeverity.MINOR)

            # Generate title and description
            if issue_type == "bug_fix":
                commit = issue.get("commit", {})
                title = f"Fix: {commit.get('message', 'Bug fix')}"
                description = f"Bug fix from commit {commit.get('hash', 'unknown')}: {commit.get('message', '')}"
            else:
                files = issue.get("files", [])
                title = f"Change: {issue_type.replace('_', ' ').title()}"
                description = f"{issue.get('reason', 'Change detected')}\n\nFiles changed: {len(files)}"

            # Create PR and ticket
            result = self.coordinator.create_pr_and_ticket(
                title=title,
                description=description,
                change_type=change_type,
                severity=severity,
                files_changed=issue.get("files", [])
            )

            results.append(result)

        return results

    def auto_detect_and_generate(self) -> Dict[str, Any]:
        """Main auto-detection and generation workflow"""
        self.logger.info("="*80)
        self.logger.info("AUTO-DETECTING ISSUES AND CHANGES")
        self.logger.info("="*80)

        # Detect changes
        self.logger.info("1. Detecting git changes...")
        changes = self.detect_git_changes()
        self.logger.info(f"   Found {len(changes)} change groups")

        # Analyze for issues
        self.logger.info("2. Analyzing changes for issues...")
        issues = self.analyze_changes_for_issues(changes)
        self.logger.info(f"   Found {len(issues)} issues requiring PRs/tickets")

        # Generate PRs and tickets
        if issues:
            self.logger.info("3. Generating PRs and tickets...")
            results = self.generate_prs_and_tickets(issues)
            self.logger.info(f"   Generated {len(results)} PR/ticket pairs")
        else:
            results = []
            self.logger.info("   No issues requiring PRs/tickets")

        return {
            "changes_detected": len(changes),
            "issues_found": len(issues),
            "prs_tickets_generated": len(results),
            "results": results
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Auto PR & Ticket Generator")
        parser.add_argument("--auto", action="store_true", help="Auto-detect and generate")
        parser.add_argument("--detect", action="store_true", help="Only detect, don't generate")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        generator = AutoPRTicketGenerator(project_root)

        if args.auto:
            result = generator.auto_detect_and_generate()
            import json
            print(json.dumps(result, indent=2, default=str))
        elif args.detect:
            changes = generator.detect_git_changes()
            issues = generator.analyze_changes_for_issues(changes)
            import json
            print(json.dumps({
                "changes": changes,
                "issues": issues
            }, indent=2, default=str))
        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()