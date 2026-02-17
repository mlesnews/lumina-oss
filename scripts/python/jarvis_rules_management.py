#!/usr/bin/env python3
"""
JARVIS Rules Management System

Automatically manages .cursorrules and other rule files:
- Checks if rules exist
- Detects when rules need updating
- Creates helpdesk tickets for rule changes
- Integrates with change management
- Ensures harmony across all systems

Tags: #RULES #CHANGE_MANAGEMENT #HELPDESK #HARMONY @JARVIS @LUMINA
"""

import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("JARVISRulesManagement")
except ImportError:
    try:
        from lumina_logger import get_logger
        logger = get_logger("JARVISRulesManagement")
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("JARVISRulesManagement")


class RulesManagement:
    """Rules management system integrated with helpdesk and change management"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "rules_management"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.rules_file = project_root / ".cursorrules"
        self.rules_history_file = self.data_dir / "rules_history.json"
        self.rules_checksum_file = self.data_dir / "rules_checksum.json"

        self.helpdesk_tickets_file = project_root / "data" / "notification_tickets" / "tickets.json"
        self.change_management_config = self._load_change_management_config()

        self.rules_history = self._load_rules_history()
        self.rules_checksum = self._load_rules_checksum()

    def _load_change_management_config(self) -> Dict[str, Any]:
        """Load change management team configuration"""
        config_file = self.project_root / "config" / "helpdesk" / "change_management_team.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _load_rules_history(self) -> List[Dict[str, Any]]:
        """Load rules change history"""
        if self.rules_history_file.exists():
            try:
                with open(self.rules_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def _load_rules_checksum(self) -> Dict[str, Any]:
        """Load rules checksum"""
        if self.rules_checksum_file.exists():
            try:
                with open(self.rules_checksum_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_rules_history(self):
        """Save rules change history"""
        try:
            with open(self.rules_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.rules_history, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving rules history: {e}")

    def _save_rules_checksum(self, checksum: str):
        """Save rules checksum"""
        try:
            checksum_data = {
                "checksum": checksum,
                "last_checked": datetime.now().isoformat(),
                "rules_file": str(self.rules_file)
            }
            with open(self.rules_checksum_file, 'w', encoding='utf-8') as f:
                json.dump(checksum_data, f, indent=2, default=str)
            self.rules_checksum = checksum_data
        except Exception as e:
            logger.error(f"Error saving rules checksum: {e}")

    def _calculate_checksum(self, content: str) -> str:
        """Calculate SHA256 checksum of rules content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def check_rules_exist(self) -> Dict[str, Any]:
        """Check if rules file exists"""
        exists = self.rules_file.exists()

        result = {
            "rules_file": str(self.rules_file),
            "exists": exists,
            "checked_at": datetime.now().isoformat()
        }

        if exists:
            try:
                stat = self.rules_file.stat()
                result["size"] = stat.st_size
                result["modified_at"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
                result["created_at"] = datetime.fromtimestamp(stat.st_ctime).isoformat()
            except Exception as e:
                result["error"] = str(e)
        else:
            # Rules file missing - create helpdesk ticket
            self._create_missing_rules_ticket()

        return result

    def check_rules_changed(self) -> Dict[str, Any]:
        """Check if rules file has changed"""
        if not self.rules_file.exists():
            return {
                "changed": False,
                "error": "Rules file does not exist"
            }

        try:
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                content = f.read()

            current_checksum = self._calculate_checksum(content)
            previous_checksum = self.rules_checksum.get("checksum")

            if previous_checksum and current_checksum != previous_checksum:
                # Rules changed - record in history and create ticket
                change_record = {
                    "timestamp": datetime.now().isoformat(),
                    "previous_checksum": previous_checksum,
                    "current_checksum": current_checksum,
                    "size": len(content),
                    "lines": content.count('\n') + 1
                }
                self.rules_history.append(change_record)
                self._save_rules_history()
                self._save_rules_checksum(current_checksum)

                # Create change management ticket
                self._create_rules_update_ticket(change_record)

                return {
                    "changed": True,
                    "previous_checksum": previous_checksum,
                    "current_checksum": current_checksum,
                    "change_record": change_record
                }
            else:
                # No change
                if not previous_checksum:
                    # First time checking - save checksum
                    self._save_rules_checksum(current_checksum)

                return {
                    "changed": False,
                    "checksum": current_checksum
                }
        except Exception as e:
            return {
                "changed": False,
                "error": str(e)
            }

    def check_rules_need_updating(self, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Check if rules need updating based on context (change management tasks, etc.)"""
        result = {
            "needs_updating": False,
            "reasons": [],
            "checked_at": datetime.now().isoformat()
        }

        # Check for change management tasks that might require rule updates
        if context and context.get("change_management_task"):
            task = context["change_management_task"]

            # Check if task mentions rules
            task_description = str(task.get("description", "")).lower()
            task_title = str(task.get("title", "")).lower()

            rules_keywords = ["rule", "rules", ".cursorrules", "cursor rules", "workspace rules"]
            if any(keyword in task_description or keyword in task_title for keyword in rules_keywords):
                result["needs_updating"] = True
                result["reasons"].append("Change management task requires rule updates")
                result["task_id"] = task.get("id")

        # Check if rules file is missing
        if not self.rules_file.exists():
            result["needs_updating"] = True
            result["reasons"].append("Rules file does not exist")

        # Check if rules are outdated (older than 30 days without update)
        if self.rules_file.exists():
            try:
                stat = self.rules_file.stat()
                age_days = (datetime.now().timestamp() - stat.st_mtime) / 86400
                if age_days > 30:
                    result["needs_updating"] = True
                    result["reasons"].append(f"Rules file is {age_days:.0f} days old")
            except Exception:
                pass

        if result["needs_updating"]:
            self._create_rules_update_required_ticket(result)

        return result

    def _create_missing_rules_ticket(self):
        """Create helpdesk ticket for missing rules file"""
        ticket = {
            "ticket_id": f"rules-missing-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "type": "rules_missing",
            "title": "Rules File Missing",
            "description": f"Rules file (.cursorrules) is missing at {self.rules_file}",
            "priority": "high",
            "status": "open",
            "assigned_to": "change_management_team",
            "created_at": datetime.now().isoformat(),
            "tags": ["#RULES", "#CHANGE_MANAGEMENT", "#CRITICAL"],
            "context": {
                "rules_file": str(self.rules_file),
                "action_required": "Create or restore .cursorrules file"
            }
        }

        self._save_ticket(ticket)
        logger.warning(f"📋 Created ticket for missing rules: {ticket['ticket_id']}")

    def _create_rules_update_ticket(self, change_record: Dict[str, Any]):
        """Create helpdesk ticket for rules update"""
        ticket = {
            "ticket_id": f"rules-update-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "type": "rules_update",
            "title": "Rules File Updated",
            "description": f"Rules file (.cursorrules) has been updated",
            "priority": "medium",
            "status": "open",
            "assigned_to": "change_management_team",
            "created_at": datetime.now().isoformat(),
            "tags": ["#RULES", "#CHANGE_MANAGEMENT", "#UPDATE"],
            "context": {
                "rules_file": str(self.rules_file),
                "change_record": change_record,
                "action_required": "Review rule changes and update documentation if needed"
            }
        }

        self._save_ticket(ticket)
        logger.info(f"📋 Created ticket for rules update: {ticket['ticket_id']}")

    def _create_rules_update_required_ticket(self, check_result: Dict[str, Any]):
        """Create helpdesk ticket when rules update is required"""
        ticket = {
            "ticket_id": f"rules-update-required-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "type": "rules_update_required",
            "title": "Rules Update Required",
            "description": f"Rules file may need updating: {', '.join(check_result.get('reasons', []))}",
            "priority": "medium",
            "status": "open",
            "assigned_to": "change_management_team",
            "created_at": datetime.now().isoformat(),
            "tags": ["#RULES", "#CHANGE_MANAGEMENT", "#UPDATE_REQUIRED"],
            "context": {
                "rules_file": str(self.rules_file),
                "reasons": check_result.get("reasons", []),
                "action_required": "Review and update rules file as needed"
            }
        }

        self._save_ticket(ticket)
        logger.info(f"📋 Created ticket for required rules update: {ticket['ticket_id']}")

    def _save_ticket(self, ticket: Dict[str, Any]):
        """Save ticket to helpdesk tickets file"""
        try:
            tickets_file = self.helpdesk_tickets_file
            tickets_file.parent.mkdir(parents=True, exist_ok=True)

            tickets = []
            if tickets_file.exists():
                try:
                    with open(tickets_file, 'r', encoding='utf-8') as f:
                        tickets = json.load(f)
                except Exception:
                    pass

            tickets.append(ticket)

            with open(tickets_file, 'w', encoding='utf-8') as f:
                json.dump(tickets, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving ticket: {e}")

    def get_rules_status(self) -> Dict[str, Any]:
        """Get comprehensive rules status"""
        exists_check = self.check_rules_exist()
        changed_check = self.check_rules_changed() if exists_check["exists"] else {"changed": False}

        return {
            "rules_file": str(self.rules_file),
            "exists": exists_check["exists"],
            "changed": changed_check.get("changed", False),
            "checksum": changed_check.get("current_checksum") or self.rules_checksum.get("checksum"),
            "last_checked": self.rules_checksum.get("last_checked"),
            "history_count": len(self.rules_history),
            "status": "ok" if exists_check["exists"] else "missing"
        }


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Rules Management")
        parser.add_argument("--check", action="store_true", help="Check rules status")
        parser.add_argument("--check-changed", action="store_true", help="Check if rules changed")
        parser.add_argument("--status", action="store_true", help="Show comprehensive status")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        rules_mgmt = RulesManagement(project_root)

        if args.check:
            result = rules_mgmt.check_rules_exist()
            print(json.dumps(result, indent=2, default=str))

        elif args.check_changed:
            result = rules_mgmt.check_rules_changed()
            print(json.dumps(result, indent=2, default=str))

        elif args.status:
            status = rules_mgmt.get_rules_status()
            print(json.dumps(status, indent=2, default=str))

        else:
            # Default: show status
            status = rules_mgmt.get_rules_status()
            print(json.dumps(status, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()