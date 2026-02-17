#!/usr/bin/env python3
"""
GitLens IDE-Footer Alert/Notification Handler

Handles GitLens IDE-footer alerts and notifications, including:
- PR/Issue follow-up requirements
- Automatic follow-up processing
- Integration with PR/Ticket coordination
- Notification management

Tags: #GITLENS #IDE #FOOTER #ALERT #NOTIFICATION #PR #FOLLOWUP @JARVIS @TEAM
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
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

logger = get_logger("GitLensIDEFooterAlertHandler")

# PR/Ticket Coordination
try:
    from jarvis_pr_ticket_coordinator import PRTicketCoordinator
    PR_TICKET_COORDINATOR_AVAILABLE = True
except ImportError:
    PR_TICKET_COORDINATOR_AVAILABLE = False
    PRTicketCoordinator = None

# GitLens Automation
try:
    from jarvis_gitlens_automation import JARVISGitLensAutomation
    GITLENS_AUTOMATION_AVAILABLE = True
except ImportError:
    GITLENS_AUTOMATION_AVAILABLE = False
    JARVISGitLensAutomation = None

# IDE Notification Service
try:
    from jarvis_ide_notification_service import JARVISIDENotificationService
    IDE_NOTIFICATION_AVAILABLE = True
except ImportError:
    IDE_NOTIFICATION_AVAILABLE = False
    JARVISIDENotificationService = None


class AlertType(Enum):
    """Types of GitLens IDE-footer alerts"""
    PR_FOLLOW_UP = "pr_follow_up"
    ISSUE_FOLLOW_UP = "issue_follow_up"
    MERGE_CONFLICT = "merge_conflict"
    BRANCH_AHEAD = "branch_ahead"
    BRANCH_BEHIND = "branch_behind"
    UNCOMMITTED_CHANGES = "uncommitted_changes"
    UNPUSHED_COMMITS = "unpushed_commits"
    UNKNOWN = "unknown"


class FollowUpPriority(Enum):
    """Follow-up priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class GitLensAlert:
    """GitLens IDE-footer alert"""
    alert_id: str
    alert_text: str
    alert_type: AlertType
    repository: str
    pr_or_issue_number: Optional[int] = None
    priority: FollowUpPriority = FollowUpPriority.MEDIUM
    detected_at: datetime = field(default_factory=datetime.now)
    handled: bool = False
    handled_at: Optional[datetime] = None
    action_taken: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class GitLensIDEFooterAlertHandler:
    """
    GitLens IDE-Footer Alert Handler

    Handles GitLens IDE-footer alerts and notifications automatically.
    Processes follow-up requirements and takes appropriate actions.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize GitLens IDE-Footer Alert Handler"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "gitlens_alerts"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # PR/Ticket Coordinator
        self.pr_ticket_coordinator = None
        if PR_TICKET_COORDINATOR_AVAILABLE:
            try:
                self.pr_ticket_coordinator = PRTicketCoordinator(project_root=project_root)
                logger.info("✅ PR/Ticket Coordinator initialized")
            except Exception as e:
                logger.warning(f"⚠️  PR/Ticket Coordinator not available: {e}")

        # GitLens Automation
        self.gitlens_automation = None
        if GITLENS_AUTOMATION_AVAILABLE:
            try:
                self.gitlens_automation = JARVISGitLensAutomation(repo_path=project_root)
                logger.info("✅ GitLens Automation initialized")
            except Exception as e:
                logger.warning(f"⚠️  GitLens Automation not available: {e}")

        # Alert history
        self.alert_history_file = self.data_dir / "alert_history.jsonl"
        self.active_alerts_file = self.data_dir / "active_alerts.json"

        # Load active alerts
        self.active_alerts: Dict[str, GitLensAlert] = {}
        self._load_active_alerts()

        logger.info("✅ GitLens IDE-Footer Alert Handler initialized")

    def _load_active_alerts(self):
        """Load active alerts from file"""
        if self.active_alerts_file.exists():
            try:
                with open(self.active_alerts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for alert_id, alert_data in data.get("alerts", {}).items():
                        # Convert datetime strings back to datetime
                        if "detected_at" in alert_data:
                            alert_data["detected_at"] = datetime.fromisoformat(alert_data["detected_at"])
                        if "handled_at" in alert_data and alert_data["handled_at"]:
                            alert_data["handled_at"] = datetime.fromisoformat(alert_data["handled_at"])
                        # Convert enums
                        alert_data["alert_type"] = AlertType(alert_data["alert_type"])
                        alert_data["priority"] = FollowUpPriority(alert_data["priority"])
                        self.active_alerts[alert_id] = GitLensAlert(**alert_data)
                logger.info(f"✅ Loaded {len(self.active_alerts)} active alerts")
            except Exception as e:
                logger.warning(f"⚠️  Error loading active alerts: {e}")

    def _save_active_alerts(self):
        """Save active alerts to file"""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "alerts": {}
            }
            for alert_id, alert in self.active_alerts.items():
                alert_dict = {
                    "alert_id": alert.alert_id,
                    "alert_text": alert.alert_text,
                    "alert_type": alert.alert_type.value,
                    "repository": alert.repository,
                    "pr_or_issue_number": alert.pr_or_issue_number,
                    "priority": alert.priority.value,
                    "detected_at": alert.detected_at.isoformat(),
                    "handled": alert.handled,
                    "handled_at": alert.handled_at.isoformat() if alert.handled_at else None,
                    "action_taken": alert.action_taken,
                    "metadata": alert.metadata
                }
                data["alerts"][alert_id] = alert_dict

            with open(self.active_alerts_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"❌ Error saving active alerts: {e}")

    def parse_alert(self, alert_text: str) -> GitLensAlert:
        """Parse GitLens IDE-footer alert text"""
        alert_id = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        # Parse repository and PR/issue number
        # Format: "REPO#NUMBER REQUIRES FOLLOW-UP"
        # Example: "MLESNEWSS/<COMPANY>-FINANCIAL-SERVICES_LLC-ENV#1 REQUIRES FOLLOW-UP"

        repository = None
        pr_or_issue_number = None
        alert_type = AlertType.UNKNOWN
        priority = FollowUpPriority.MEDIUM

        # Extract repository and number
        match = re.search(r'([A-Z0-9_/-]+)#(\d+)', alert_text, re.IGNORECASE)
        if match:
            repository = match.group(1)
            pr_or_issue_number = int(match.group(2))

        # Determine alert type
        if "REQUIRES FOLLOW-UP" in alert_text.upper():
            if pr_or_issue_number:
                # Check if it's a PR or issue (could be either)
                # Default to PR_FOLLOW_UP, can be refined
                alert_type = AlertType.PR_FOLLOW_UP
                priority = FollowUpPriority.HIGH
        elif "CONFLICT" in alert_text.upper():
            alert_type = AlertType.MERGE_CONFLICT
            priority = FollowUpPriority.CRITICAL
        elif "AHEAD" in alert_text.upper():
            alert_type = AlertType.BRANCH_AHEAD
            priority = FollowUpPriority.MEDIUM
        elif "BEHIND" in alert_text.upper():
            alert_type = AlertType.BRANCH_BEHIND
            priority = FollowUpPriority.MEDIUM
        elif "UNCOMMITTED" in alert_text.upper():
            alert_type = AlertType.UNCOMMITTED_CHANGES
            priority = FollowUpPriority.LOW
        elif "UNPUSHED" in alert_text.upper():
            alert_type = AlertType.UNPUSHED_COMMITS
            priority = FollowUpPriority.MEDIUM

        alert = GitLensAlert(
            alert_id=alert_id,
            alert_text=alert_text,
            alert_type=alert_type,
            repository=repository or "unknown",
            pr_or_issue_number=pr_or_issue_number,
            priority=priority,
            metadata={
                "parsed_at": datetime.now().isoformat(),
                "original_text": alert_text
            }
        )

        return alert

    def handle_alert(self, alert: GitLensAlert) -> Dict[str, Any]:
        """Handle a GitLens alert"""
        logger.info(f"🔔 Handling alert: {alert.alert_text}")
        logger.info(f"   Type: {alert.alert_type.value}")
        logger.info(f"   Priority: {alert.priority.value}")

        result = {
            "alert_id": alert.alert_id,
            "handled": False,
            "action_taken": None,
            "details": {}
        }

        try:
            if alert.alert_type == AlertType.PR_FOLLOW_UP:
                result = self._handle_pr_follow_up(alert)
            elif alert.alert_type == AlertType.ISSUE_FOLLOW_UP:
                result = self._handle_issue_follow_up(alert)
            elif alert.alert_type == AlertType.MERGE_CONFLICT:
                result = self._handle_merge_conflict(alert)
            elif alert.alert_type == AlertType.BRANCH_AHEAD:
                result = self._handle_branch_ahead(alert)
            elif alert.alert_type == AlertType.BRANCH_BEHIND:
                result = self._handle_branch_behind(alert)
            elif alert.alert_type == AlertType.UNCOMMITTED_CHANGES:
                result = self._handle_uncommitted_changes(alert)
            elif alert.alert_type == AlertType.UNPUSHED_COMMITS:
                result = self._handle_unpushed_commits(alert)
            else:
                result["action_taken"] = "Unknown alert type - manual review needed"
                logger.warning(f"   ⚠️  Unknown alert type: {alert.alert_type}")

            # Mark as handled
            alert.handled = result.get("handled", False)
            alert.handled_at = datetime.now() if alert.handled else None
            alert.action_taken = result.get("action_taken")

            # Save to history
            self._save_alert_to_history(alert)

            # Update active alerts
            if alert.handled:
                if alert.alert_id in self.active_alerts:
                    del self.active_alerts[alert.alert_id]
            else:
                self.active_alerts[alert.alert_id] = alert

            self._save_active_alerts()

        except Exception as e:
            logger.error(f"❌ Error handling alert: {e}", exc_info=True)
            result["error"] = str(e)

        return result

    def _handle_pr_follow_up(self, alert: GitLensAlert) -> Dict[str, Any]:
        """Handle PR follow-up requirement"""
        logger.info(f"   📋 PR Follow-up: {alert.repository}#{alert.pr_or_issue_number}")

        result = {
            "handled": False,
            "action_taken": None,
            "details": {}
        }

        # Get PR information
        pr_number = alert.pr_or_issue_number
        repository = alert.repository

        # Check if PR exists in our tracking
        pr_info = None
        if self.pr_ticket_coordinator:
            # Look up PR in PR-Ticket map
            pr_key = f"PR-{pr_number}"
            pr_ticket_map = self.pr_ticket_coordinator.pr_ticket_map

            # Check if PR exists in map
            if pr_key in pr_ticket_map.get("pr_to_ticket", {}):
                ticket_id = pr_ticket_map["pr_to_ticket"][pr_key]
                pr_info = {
                    "pr_id": pr_key,
                    "ticket_id": ticket_id,
                    "repository": repository,
                    "pr_number": pr_number
                }
                result["details"]["pr_info"] = pr_info
                result["details"]["ticket_linked"] = ticket_id
            else:
                # PR not in our tracking - create entry
                logger.info(f"   📝 PR {pr_key} not in tracking - will create entry")
                pr_info = {
                    "pr_id": pr_key,
                    "repository": repository,
                    "pr_number": pr_number,
                    "status": "unknown",
                    "needs_follow_up": True
                }

        # Generate follow-up action plan
        follow_up_actions = self._generate_pr_follow_up_actions(alert, pr_info)
        result["details"]["follow_up_actions"] = follow_up_actions

        # Execute follow-up actions
        if follow_up_actions:
            executed = self._execute_follow_up_actions(follow_up_actions)
            result["handled"] = executed.get("success", False)
            result["action_taken"] = executed.get("action_taken")
            result["details"]["executed_actions"] = executed.get("actions", [])

        if not self.pr_ticket_coordinator:
            result["action_taken"] = "PR/Ticket Coordinator not available - manual review needed"
            logger.warning("   ⚠️  PR/Ticket Coordinator not available")

        return result

    def _handle_issue_follow_up(self, alert: GitLensAlert) -> Dict[str, Any]:
        """Handle issue follow-up requirement"""
        logger.info(f"   📋 Issue Follow-up: {alert.repository}#{alert.pr_or_issue_number}")

        # Similar to PR follow-up
        return self._handle_pr_follow_up(alert)

    def _handle_merge_conflict(self, alert: GitLensAlert) -> Dict[str, Any]:
        """Handle merge conflict"""
        logger.info("   ⚠️  Merge conflict detected")

        result = {
            "handled": False,
            "action_taken": None,
            "details": {}
        }

        if self.gitlens_automation:
            # Use GitLens automation to resolve conflicts
            conflict_resolution = self.gitlens_automation._auto_resolve_conflicts()
            result["handled"] = conflict_resolution.get("success", False)
            result["action_taken"] = conflict_resolution.get("message", "Conflict resolution attempted")
            result["details"]["conflict_resolution"] = conflict_resolution
        else:
            result["action_taken"] = "GitLens Automation not available - manual conflict resolution needed"
            logger.warning("   ⚠️  GitLens Automation not available")

        return result

    def _handle_branch_ahead(self, alert: GitLensAlert) -> Dict[str, Any]:
        """Handle branch ahead (unpushed commits)"""
        logger.info("   📤 Branch ahead - unpushed commits detected")

        result = {
            "handled": False,
            "action_taken": None,
            "details": {}
        }

        if self.gitlens_automation:
            # Auto-push if enabled
            push_success, push_msg = self.gitlens_automation.auto_push()
            result["handled"] = push_success
            result["action_taken"] = push_msg
            result["details"]["push_result"] = {"success": push_success, "message": push_msg}
        else:
            result["action_taken"] = "GitLens Automation not available - manual push needed"

        return result

    def _handle_branch_behind(self, alert: GitLensAlert) -> Dict[str, Any]:
        """Handle branch behind (need to pull)"""
        logger.info("   📥 Branch behind - need to pull")

        result = {
            "handled": False,
            "action_taken": None,
            "details": {}
        }

        if self.gitlens_automation:
            # Auto-pull
            pull_success, pull_msg = self.gitlens_automation.auto_pull()
            result["handled"] = pull_success
            result["action_taken"] = pull_msg
            result["details"]["pull_result"] = {"success": pull_success, "message": pull_msg}
        else:
            result["action_taken"] = "GitLens Automation not available - manual pull needed"

        return result

    def _handle_uncommitted_changes(self, alert: GitLensAlert) -> Dict[str, Any]:
        """Handle uncommitted changes"""
        logger.info("   📝 Uncommitted changes detected")

        result = {
            "handled": False,
            "action_taken": None,
            "details": {}
        }

        if self.gitlens_automation:
            # Check git status
            status = self.gitlens_automation.get_git_status()
            result["details"]["git_status"] = status

            if status.get("has_changes"):
                # Auto-commit if enabled
                if self.gitlens_automation.auto_commit:
                    commit_success, commit_msg = self.gitlens_automation.auto_commit_changes()
                    result["handled"] = commit_success
                    result["action_taken"] = commit_msg
                    result["details"]["commit_result"] = {"success": commit_success, "message": commit_msg}
                else:
                    result["action_taken"] = "Auto-commit disabled - manual commit needed"
            else:
                result["action_taken"] = "No changes detected"
        else:
            result["action_taken"] = "GitLens Automation not available - manual commit needed"

        return result

    def _handle_unpushed_commits(self, alert: GitLensAlert) -> Dict[str, Any]:
        """Handle unpushed commits"""
        logger.info("   📤 Unpushed commits detected")

        # Same as branch ahead
        return self._handle_branch_ahead(alert)

    def _generate_pr_follow_up_actions(self, alert: GitLensAlert, pr_info: Optional[Dict[str, Any]]) -> List[str]:
        """Generate follow-up actions for PR"""
        actions = []

        # Standard PR follow-up actions
        actions.append("Review PR status")
        actions.append("Check for merge conflicts")
        actions.append("Verify tests pass")
        actions.append("Check for required approvals")

        if pr_info:
            if pr_info.get("status") == "draft":
                actions.append("Mark PR as ready for review")
            if pr_info.get("has_conflicts"):
                actions.append("Resolve merge conflicts")
            if pr_info.get("needs_review"):
                actions.append("Request code review")

        # Check git status
        if self.gitlens_automation:
            status = self.gitlens_automation.get_git_status()
            if status.get("has_changes"):
                actions.append("Commit pending changes")
            if status.get("branch") != "main" and status.get("branch") != "master":
                actions.append("Ensure branch is up to date")

        return actions

    def _execute_follow_up_actions(self, actions: List[str]) -> Dict[str, Any]:
        """Execute follow-up actions"""
        executed = []
        success_count = 0

        for action in actions:
            try:
                if "Commit pending changes" in action:
                    if self.gitlens_automation:
                        success, msg = self.gitlens_automation.auto_commit_changes()
                        executed.append({"action": action, "success": success, "message": msg})
                        if success:
                            success_count += 1

                elif "Resolve merge conflicts" in action:
                    if self.gitlens_automation:
                        resolution = self.gitlens_automation._auto_resolve_conflicts()
                        executed.append({"action": action, "success": resolution.get("success", False), "message": resolution.get("message")})
                        if resolution.get("success"):
                            success_count += 1

                elif "Ensure branch is up to date" in action:
                    if self.gitlens_automation:
                        pull_success, pull_msg = self.gitlens_automation.auto_pull()
                        executed.append({"action": action, "success": pull_success, "message": pull_msg})
                        if pull_success:
                            success_count += 1

                else:
                    # Manual action required
                    executed.append({"action": action, "success": False, "message": "Manual action required"})

            except Exception as e:
                logger.error(f"   ❌ Error executing action '{action}': {e}")
                executed.append({"action": action, "success": False, "error": str(e)})

        return {
            "success": success_count > 0,
            "actions": executed,
            "action_taken": f"Executed {success_count}/{len(actions)} actions"
        }

    def _save_alert_to_history(self, alert: GitLensAlert):
        """Save alert to history"""
        try:
            alert_data = {
                "alert_id": alert.alert_id,
                "alert_text": alert.alert_text,
                "alert_type": alert.alert_type.value,
                "repository": alert.repository,
                "pr_or_issue_number": alert.pr_or_issue_number,
                "priority": alert.priority.value,
                "detected_at": alert.detected_at.isoformat(),
                "handled": alert.handled,
                "handled_at": alert.handled_at.isoformat() if alert.handled_at else None,
                "action_taken": alert.action_taken,
                "metadata": alert.metadata
            }

            with open(self.alert_history_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(alert_data) + '\n')
        except Exception as e:
            logger.error(f"❌ Error saving alert to history: {e}")

    def process_alert_text(self, alert_text: str) -> Dict[str, Any]:
        """Process alert text from GitLens IDE-footer"""
        # Parse alert
        alert = self.parse_alert(alert_text)

        # Handle alert
        result = self.handle_alert(alert)

        return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="GitLens IDE-Footer Alert Handler")
    parser.add_argument("--alert", type=str, help="Alert text to process")
    parser.add_argument("--list-active", action="store_true", help="List active alerts")
    parser.add_argument("--handle-all", action="store_true", help="Handle all active alerts")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("🔔 GitLens IDE-Footer Alert Handler")
    print("="*80 + "\n")

    handler = GitLensIDEFooterAlertHandler()

    if args.alert:
        # Process specific alert
        result = handler.process_alert_text(args.alert)
        print(f"\n📊 ALERT PROCESSING RESULT:")
        print(f"   Handled: {'✅' if result.get('handled') else '❌'}")
        print(f"   Action: {result.get('action_taken', 'N/A')}")
        if result.get('details'):
            print(f"   Details: {json.dumps(result['details'], indent=2)}")
        print()

    elif args.list_active:
        # List active alerts
        print(f"\n📋 ACTIVE ALERTS: {len(handler.active_alerts)}")
        for alert_id, alert in handler.active_alerts.items():
            print(f"\n   Alert: {alert.alert_text}")
            print(f"   Type: {alert.alert_type.value}")
            print(f"   Priority: {alert.priority.value}")
            print(f"   Detected: {alert.detected_at.isoformat()}")
        print()

    elif args.handle_all:
        # Handle all active alerts
        print(f"\n🔄 Handling {len(handler.active_alerts)} active alerts...\n")
        for alert_id, alert in list(handler.active_alerts.items()):
            result = handler.handle_alert(alert)
            print(f"   {alert.alert_text}: {'✅' if result.get('handled') else '❌'}")
        print()

    else:
        # Process the specific alert from user
        alert_text = "MLESNEWSS/<COMPANY>-FINANCIAL-SERVICES_LLC-ENV#1 REQUIRES FOLLOW-UP"
        print(f"📋 Processing alert: {alert_text}\n")
        result = handler.process_alert_text(alert_text)
        print(f"\n📊 RESULT:")
        print(f"   Handled: {'✅' if result.get('handled') else '❌'}")
        print(f"   Action: {result.get('action_taken', 'N/A')}")
        if result.get('details'):
            print(f"   Details: {json.dumps(result['details'], indent=2)}")
        print()
        print("="*80 + "\n")
