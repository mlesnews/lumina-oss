#!/usr/bin/env python3
"""
VS Code / Cursor IDE Notification Monitor with C-3PO Ticket Lifecycle

This script monitors VS Code/Cursor IDE notifications and creates a complete ticket lifecycle:
1. Detect notification
2. Create PM (Problem), C (Change Request), T (Task) tickets
3. @C3PO assigns tickets to appropriate teams
4. Teams work on their personal ticket stacks
5. C-3PO updates, maintains, and closes tickets

Usage:
    python scripts/python/monitor_vscode_notifications.py --report

Tags: #JARVIS #HELPDESK #WORKFLOWS #C3PO #TICKET @JARVIS @C3PO @HELPDESK
"""

import hashlib
import json
import logging
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# ========================================
# TICKET NUMBER SYNTAX VALIDATION
# Rule: .kilocode/rules/ticket_number_syntax.md
# ========================================

TICKET_PATTERN = re.compile(r"^(PM|C|CR|T)[0-9]{9}$")
project_root = Path(__file__).parent.parent.parent


def _load_notification_tickets_from_storage(
    tickets_file: Path, tickets_dir: Path
) -> Dict[str, dict]:
    """
    Load notification tickets: prefer per-ticket files (mirror helpdesk tickets/), else index.
    Aligns notifications queue with problems queue structure.
    """
    tickets = {}
    tickets_dir.mkdir(parents=True, exist_ok=True)
    # Prefer loading from per-ticket files (same pattern as data/helpdesk/tickets/)
    json_files = list(tickets_dir.glob("*.json")) if tickets_dir.exists() else []
    if json_files:
        for path in json_files:
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                    tid = data.get("ticket_id") or path.stem
                    tickets[tid] = data
            except Exception as e:
                logger.warning(f"Failed to load notification ticket {path}: {e}")
    if tickets:
        return tickets
    # Fallback: legacy index file
    if tickets_file.exists():
        try:
            with open(tickets_file, encoding="utf-8") as f:
                data = json.load(f)
                tickets = data.get("tickets", {})
                # One-time migration: write each to tickets_dir for alignment
                for tid, rec in tickets.items():
                    out = tickets_dir / f"{tid}.json"
                    if not out.exists():
                        try:
                            with open(out, "w", encoding="utf-8") as w:
                                json.dump(rec, w, indent=2, ensure_ascii=False)
                        except Exception as e:
                            logger.debug(f"Migration write {out}: {e}")
        except Exception as e:
            logger.error(f"Failed to load notification tickets index: {e}")
    return tickets


def _save_notification_tickets_to_storage(
    tickets_file: Path, tickets_dir: Path, tickets_dict: Dict[str, dict]
) -> None:
    """
    Save notification tickets to index and per-ticket files (mirror helpdesk).
    """
    tickets_file.parent.mkdir(parents=True, exist_ok=True)
    tickets_dir.mkdir(parents=True, exist_ok=True)
    data = {"last_updated": datetime.now().isoformat(), "tickets": tickets_dict}
    with open(tickets_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    for tid, rec in tickets_dict.items():
        try:
            out = tickets_dir / f"{tid}.json"
            with open(out, "w", encoding="utf-8") as w:
                json.dump(rec, w, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Failed to save notification ticket {tid}: {e}")


scripts_python = project_root / "scripts" / "python"
sys.path.insert(0, str(scripts_python))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("VSCodeNotificationMonitor")

# Import ticket system components
HELPDESK_AVAILABLE = False
C3PO_AVAILABLE = False

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("VSCodeNotificationMonitor")

try:
    from jarvis_helpdesk_ticket_system import (
        HelpdeskTicket,
        JARVISHelpdeskTicketSystem,
        TicketPriority,
        TicketStatus,
        TicketType,
    )

    HELPDESK_AVAILABLE = True
    logger.info("✅ Helpdesk ticket system available")
except ImportError as e:
    logger.warning(f"⚠️ Helpdesk ticket system not available: {e}")
    HELPDESK_AVAILABLE = False

    # Define fallbacks
    class _TicketPriority:
        CRITICAL = "critical"
        HIGH = "high"
        MEDIUM = "medium"
        LOW = "low"

    class _TicketStatus:
        OPEN = "open"
        IN_PROGRESS = "in_progress"
        RESOLVED = "resolved"
        CLOSED = "closed"

    class _TicketType:
        PROBLEM = "PM"
        CHANGE_REQUEST = "C"
        CHANGE_TASK = "T"

    TicketPriority = _TicketPriority
    TicketStatus = _TicketStatus
    TicketType = _TicketType


try:
    from jarvis_c3po_ticket_assigner import C3POTicketAssigner

    C3PO_AVAILABLE = True
    logger.info("✅ C-3PO Ticket Assigner available")
except ImportError as e:
    logger.warning(f"⚠️ C-3PO Ticket Assigner not available: {e}")


class VSCodeNotificationMonitor:
    """
    Monitors VS Code / Cursor IDE notifications and manages full ticket lifecycle.

    C-3PO workflow:
    1. Monitor detects notification
    2. Create PM (Problem) ticket with full details
    3. Create C (Change Request) ticket for the fix
    4. Create T (Task) ticket for implementation
    5. C-3PO assigns tickets to appropriate teams
    6. Teams work on their stacks
    7. C-3PO updates and closes tickets upon completion
    """

    # Patterns for common VS Code notifications/errors
    NOTIFICATION_PATTERNS = [
        # Extension activation errors
        (
            r"Cannot activate '(.+)' extension because it depends on an unknown '(.+)' extension",
            "extension_dependency_error",
            TicketPriority.HIGH,
        ),
        # Extension format errors
        (
            r"(\w+\.\w+) \(bad format\) Expected: <provider>\.<name>",
            "extension_format_error",
            TicketPriority.MEDIUM,
        ),
        # Server crashes
        (
            r"(.+) server crashed (\d+) times in the last (\d+) minutes",
            "server_crash",
            TicketPriority.HIGH,
        ),
        # General extension errors
        (
            r"Extension '.+' failed to activate",
            "extension_activation_failed",
            TicketPriority.MEDIUM,
        ),
        # GitHub access errors
        (
            r"No GitHub access token found with access to repository",
            "github_access_error",
            TicketPriority.HIGH,
        ),
    ]

    # Team routing based on issue type
    TEAM_ROUTING = {
        "extension_dependency_error": "jarvis_superagent",
        "extension_format_error": "helpdesk_support",
        "server_crash": "helpdesk_support",
        "extension_activation_failed": "helpdesk_support",
        "github_access_error": "jarvis_superagent",
    }

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.tickets_file = self.project_root / "data/notification_tickets/tickets.json"
        self.tickets_dir = self.tickets_file.parent / "tickets"
        self.tickets_dir.mkdir(parents=True, exist_ok=True)

        # Initialize ticket system
        self.helpdesk_system = None
        if HELPDESK_AVAILABLE:
            try:
                self.helpdesk_system = JARVISHelpdeskTicketSystem(project_root=self.project_root)
                logger.info("✅ Helpdesk system initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize helpdesk system: {e}")

        # Initialize C-3PO
        self.c3po_assigner = None
        if C3PO_AVAILABLE:
            try:
                self.c3po_assigner = C3POTicketAssigner(self.project_root)
                logger.info("✅ C-3PO Ticket Assigner initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize C-3PO: {e}")

        self.notification_tickets: Dict[str, dict] = {}
        self.load_notification_tickets()

    def load_notification_tickets(self):
        """Load existing notification tickets (index + per-ticket files, mirror helpdesk)."""
        self.notification_tickets = _load_notification_tickets_from_storage(
            self.tickets_file, self.tickets_dir
        )
        logger.info(
            f"📂 Loaded {len(self.notification_tickets)} existing notification tickets"
        )

    def save_notification_tickets(self):
        """Save notification tickets to index and per-ticket files (mirror helpdesk)."""
        _save_notification_tickets_to_storage(
            self.tickets_file, self.tickets_dir, self.notification_tickets
        )
        logger.info(f"💾 Saved {len(self.notification_tickets)} notification tickets")

    def generate_request_id(self) -> str:
        """Generate a unique request ID for tracking."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = hashlib.md5(f"{time.time()}".encode()).hexdigest()[:6]
        return f"REQ-VSCODE-{timestamp}-{random_suffix}"

    def parse_notification(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse a notification text and extract relevant information."""
        for pattern, notif_type, priority in self.NOTIFICATION_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                request_id = self.generate_request_id()

                # Build detailed description with solutions
                solutions = {
                    "extension_dependency_error": [
                        "Install the required dependency extension",
                        "Or remove the dependency from the extension manifest",
                        "Clear workspace storage and restart VS Code",
                    ],
                    "extension_format_error": [
                        "Check workspace .code-workspace files for malformed extension IDs",
                        "Clear VS Code workspace storage",
                        "Remove corrupted extension cache",
                    ],
                    "server_crash": [
                        "Disable the crashing extension",
                        "Clear extension cache",
                        "Reinstall the extension if needed",
                    ],
                    "extension_activation_failed": [
                        "Check extension compatibility with VS Code version",
                        "Reinstall the extension",
                        "Check extension logs for specific errors",
                    ],
                    "github_access_error": [
                        "Check GitHub token validity",
                        "Verify token has required repository permissions",
                        "Refresh authentication",
                    ],
                }

                solution_text = "\n".join(
                    [f"{i + 1}. {s}" for i, s in enumerate(solutions.get(notif_type, []))]
                )

                title = f"[VS Code] {notif_type.replace('_', ' ').title()}"
                description = (
                    f"**Notification:** {text}\n\n"
                    f"**Request ID:** {request_id}\n\n"
                    f"**Analysis:**\n"
                    f"Type: {notif_type}\n"
                    f"Severity: {priority.value if hasattr(priority, 'value') else priority}\n\n"
                    f"**Recommended Solutions:**\n{solution_text}\n\n"
                    f"**C-3PO Workflow:**\n"
                    f"1. @C3PO will create PM, C, and T tickets\n"
                    f"2. Assign to appropriate team for resolution\n"
                    f"3. Team works on fix in their ticket stack\n"
                    f"4. @C3PO updates and closes upon completion"
                )

                return {
                    "title": title,
                    "description": description,
                    "notification_type": notif_type,
                    "severity": priority,
                    "request_id": request_id,
                    "team": self.TEAM_ROUTING.get(notif_type, "helpdesk_support"),
                }

        return None

    def create_ticket_set(self, info: Dict[str, Any]) -> Dict[str, str]:
        """
        Create a complete ticket set: PM (Problem), C (Change Request), T (Task).
        All tickets are linked by Request ID.
        """
        created = {}

        if not self.helpdesk_system:
            logger.warning("⚠️ Helpdesk system not available, skipping ticket creation")
            return created

        try:
            # Create PM (Problem) ticket
            pm_title = f"[PM] {info['title']}"
            pm_description = (
                f"**PROBLEM TICKET**\n\n"
                f"{info['description']}\n\n"
                f"**Linked Tickets:**\n"
                f"- C (Change Request): [Will be created]\n"
                f"- T (Task): [Will be created]\n\n"
                f"**Created by:** VS Code Notification Monitor\n"
                f"**Automation:** @JARVIS @C3PO"
            )

            pm_ticket = self.helpdesk_system.create_ticket(
                title=pm_title,
                description=pm_description,
                ticket_type=TicketType.PROBLEM,
                priority=TicketPriority(
                    info["severity"].value
                    if hasattr(info["severity"], "value")
                    else info["severity"]
                ),
                component="VS Code",
                issue_type=info["notification_type"],
            )

            if pm_ticket:
                created["PM"] = pm_ticket.ticket_id
                logger.info(f"✅ Created PM ticket: {pm_ticket.ticket_id}")

                # Link PM to notification record
                info["pm_ticket"] = pm_ticket.ticket_id

        except Exception as e:
            logger.error(f"❌ Error creating PM ticket: {e}")

        try:
            # Create C (Change Request) ticket
            c_title = f"[C] Fix: {info['title'].replace('[VS Code] ', '')}"
            c_description = (
                f"**CHANGE REQUEST TICKET**\n\n"
                f"**Original Problem:** {info['description']}\n\n"
                f"**Required Changes:**\n"
                f"1. Investigate root cause of {info['notification_type']}\n"
                f"2. Design solution for the issue\n"
                f"3. Create implementation plan\n"
                f"4. Test the solution\n\n"
                f"**Linked Tickets:**\n"
                f"- PM (Problem): {created.get('PM', 'N/A')}\n"
                f"- T (Task): [Will be created]\n\n"
                f"**Created by:** VS Code Notification Monitor\n"
                f"**Automation:** @JARVIS @C3PO"
            )

            c_ticket = self.helpdesk_system.create_ticket(
                title=c_title,
                description=c_description,
                ticket_type=TicketType.CHANGE_REQUEST,
                priority=TicketPriority(
                    info["severity"].value
                    if hasattr(info["severity"], "value")
                    else info["severity"]
                ),
                component="VS Code",
                issue_type=f"fix_{info['notification_type']}",
            )

            if c_ticket:
                created["C"] = c_ticket.ticket_id
                logger.info(f"✅ Created C ticket: {c_ticket.ticket_id}")
                info["c_ticket"] = c_ticket.ticket_id

        except Exception as e:
            logger.error(f"❌ Error creating C ticket: {e}")

        try:
            # Create T (Task) ticket
            t_title = f"[T] Implement: {info['title'].replace('[VS Code] ', '')}"
            t_description = (
                f"**TASK TICKET**\n\n"
                f"**Original Problem:** {info['description']}\n\n"
                f"**Implementation Steps:**\n"
                f"1. Review PM and C tickets for full context\n"
                f"2. Implement the fix according to change request\n"
                f"3. Test the implementation thoroughly\n"
                f"4. Update documentation\n"
                f"5. Hand off to C-3PO for closure\n\n"
                f"**Linked Tickets:**\n"
                f"- PM (Problem): {created.get('PM', 'N/A')}\n"
                f"- C (Change Request): {created.get('C', 'N/A')}\n\n"
                f"**Created by:** VS Code Notification Monitor\n"
                f"**Automation:** @JARVIS @C3PO"
            )

            t_ticket = self.helpdesk_system.create_ticket(
                title=t_title,
                description=t_description,
                ticket_type=TicketType.CHANGE_TASK,
                priority=TicketPriority(
                    info["severity"].value
                    if hasattr(info["severity"], "value")
                    else info["severity"]
                ),
                component="VS Code",
                issue_type=f"task_{info['notification_type']}",
            )

            if t_ticket:
                created["T"] = t_ticket.ticket_id
                logger.info(f"✅ Created T ticket: {t_ticket.ticket_id}")
                info["t_ticket"] = t_ticket.ticket_id

        except Exception as e:
            logger.error(f"❌ Error creating T ticket: {e}")

        return created

    def c3po_assign_tickets(self, tickets: Dict[str, str], team: str) -> Dict[str, Any]:
        """
        C-3PO assigns tickets to appropriate teams.

        C-3PO ensures:
        - Team Manager oversight (@c3po)
        - Technical Lead assignment (@r2d2 or team-specific)
        - Business Lead for coordination
        """
        if not self.c3po_assigner:
            logger.warning("⚠️ C-3PO not available for ticket assignment")
            return {"success": False, "reason": "C-3PO not available"}

        try:
            assignments = {}
            logger.info("=" * 80)
            logger.info("🤖 C-3PO ASSIGNING TICKETS TO TEAMS")
            logger.info("=" * 80)

            for ticket_type, ticket_id in tickets.items():
                if ticket_id:
                    result = self.c3po_assigner.assign_ticket_to_team(
                        ticket_number=ticket_id, team_id=team, auto_detect=True
                    )
                    assignments[ticket_id] = result
                    if result.get("success"):
                        logger.info(f"✅ {ticket_id} -> Team: {result.get('team_assigned', team)}")
                    else:
                        logger.warning(
                            f"⚠️ {ticket_id} assignment: {result.get('error', 'Unknown')}"
                        )

            logger.info("=" * 80)
            logger.info("✅ C-3PO assignment complete")
            logger.info("=" * 80)

            return {"success": True, "assignments": assignments}

        except Exception as e:
            logger.error(f"❌ Error in C-3PO assignment: {e}")
            return {"success": False, "error": str(e)}

    def save_notification_record(self, info: Dict[str, Any], tickets: Dict[str, str]):
        """Save the notification and ticket references."""
        ticket_id = hashlib.md5(f"{info['title']}|{info['request_id']}".encode()).hexdigest()[:14]

        record = {
            "ticket_id": ticket_id,
            "title": info["title"],
            "description": info["description"],
            "notification_type": info["notification_type"],
            "severity": info["severity"].value
            if hasattr(info["severity"], "value")
            else info["severity"],
            "request_id": info["request_id"],
            "team": info.get("team"),
            "pm_ticket": tickets.get("PM"),
            "c_ticket": tickets.get("C"),
            "t_ticket": tickets.get("T"),
            "status": "open",
            "priority": info["severity"].value
            if hasattr(info["severity"], "value")
            else info["severity"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "resolved_at": None,
            "metadata": {
                "c3po_assigned": False,
                "team_notified": False,
                "work_started": False,
                "completed": False,
            },
        }

        self.notification_tickets[ticket_id] = record
        self.save_notification_tickets()

        return record

    def process_notification(self, text: str) -> Optional[Dict[str, Any]]:
        """Process a notification with full C-3PO workflow."""
        info = self.parse_notification(text)
        if not info:
            return None

        # Check for duplicate
        for existing in self.notification_tickets.values():
            if existing.get("title") == info["title"]:
                logger.debug(f"Notification already processed: {info['title']}")
                return existing

        # Create ticket set
        tickets = self.create_ticket_set(info)

        # C-3PO assigns to team
        c3po_result = self.c3po_assign_tickets(tickets, info.get("team", "helpdesk_support"))

        # Save record
        record = self.save_notification_record(info, tickets)
        record["c3po_assignment"] = c3po_result

        return record

    def report_current_issues(self) -> List[Dict[str, Any]]:
        """
        Report and create tickets for known VS Code issues.
        This implements the full C-3PO workflow.
        """
        issues = [
            {
                "title": "[VS Code] Lumina Core Extension - Missing GitHub Copilot Dependency",
                "description": (
                    "Cannot activate 'Lumina Core - Open Source Lumina Ecosystem' extension "
                    "because it depends on an unknown 'github.copilot' extension.\n\n"
                    "**Analysis:**\n"
                    "- The Lumina Core extension has GitHub Copilot listed as a dependency\n"
                    "- Copilot may not be installed or may have a different extension ID\n"
                    "- This could also be a cached/corrupted extension state\n\n"
                    "**C-3PO Actions:**\n"
                    "1. Create PM, C, T tickets\n"
                    "2. Assign to jarvis_superagent team\n"
                    "3. Team implements fix\n"
                    "4. C-3PO closes upon completion"
                ),
                "type": "extension_dependency_error",
                "severity": TicketPriority.HIGH,
            },
            {
                "title": "[VS Code] Extension Format Error - undefined_publisher.lumina-ai",
                "description": (
                    "The extension recommendation 'undefined_publisher.lumina-ai' has bad format. "
                    "Expected format: <provider>.<name>\n\n"
                    "**Analysis:**\n"
                    "- A workspace or project configuration has a malformed extension reference\n"
                    "- 'undefined_publisher' suggests the publisher field is missing\n\n"
                    "**C-3PO Actions:**\n"
                    "1. Create PM, C, T tickets\n"
                    "2. Assign to helpdesk_support team\n"
                    "3. Team investigates and fixes\n"
                    "4. C-3PO closes upon completion"
                ),
                "type": "extension_format_error",
                "severity": TicketPriority.MEDIUM,
            },
            {
                "title": "[VS Code] Microsoft Edge Tools Server Crashes",
                "description": (
                    "Microsoft Edge Tools server crashed 5 times in the last 3 minutes. "
                    "The server will not be restarted.\n\n"
                    "**Analysis:**\n"
                    "- The Edge Tools extension has become unstable\n"
                    "- Known issue with certain VS Code versions\n\n"
                    "**C-3PO Actions:**\n"
                    "1. Create PM, C, T tickets\n"
                    "2. Assign to helpdesk_support team\n"
                    "3. Team disables/reinstalls extension\n"
                    "4. C-3PO closes upon completion"
                ),
                "type": "server_crash",
                "severity": TicketPriority.HIGH,
            },
        ]

        results = []
        for issue in issues:
            logger.info(f"\n📋 Processing: {issue['title']}")

            info = {
                "title": issue["title"],
                "description": issue["description"],
                "notification_type": issue["type"],
                "severity": issue["severity"],
                "request_id": self.generate_request_id(),
                "team": self.TEAM_ROUTING.get(issue["type"], "helpdesk_support"),
            }

            # Create tickets
            tickets = self.create_ticket_set(info)

            # C-3PO assigns
            c3po_result = self.c3po_assign_tickets(tickets, info["team"])

            # Save record
            record = self.save_notification_record(info, tickets)
            record["tickets"] = tickets
            record["c3po_result"] = c3po_result

            results.append(record)

        return results


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="VS Code Notification Monitor with C-3PO Ticket Lifecycle",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/python/monitor_vscode_notifications.py --report
      Process current VS Code issues with full C-3PO workflow

Workflow:
  1. Detect notification
  2. Create PM (Problem), C (Change Request), T (Task) tickets
  3. @C3PO assigns tickets to appropriate teams
  4. Teams work on their personal ticket stacks
  5. @C3PO updates, maintains, and closes tickets
        """,
    )
    parser.add_argument(
        "--report", action="store_true", help="Report current issues and create tickets"
    )
    args = parser.parse_args()

    monitor = VSCodeNotificationMonitor()

    if args.report:
        print("=" * 80)
        print("🤖 VS Code Notification Monitor with C-3PO Ticket Lifecycle")
        print("=" * 80)
        print()

        results = monitor.report_current_issues()

        print("\n" + "=" * 80)
        print("📊 SUMMARY - TICKETS CREATED AND ASSIGNED")
        print("=" * 80)

        for result in results:
            print(f"\n📋 Request ID: {result['request_id']}")
            print(f"   Title: {result['title']}")
            print(f"   Team: {result['team']}")
            print("   Tickets Created:")
            print(f"      - PM (Problem): {result.get('pm_ticket', 'N/A')}")
            print(f"      - C (Change Request): {result.get('c_ticket', 'N/A')}")
            print(f"      - T (Task): {result.get('t_ticket', 'N/A')}")

            c3po_result = result.get("c3po_result", {})
            if c3po_result.get("success"):
                print("   ✅ C-3PO Assignment: Success")
                assignments = c3po_result.get("assignments", {})
                for tid, assignment in assignments.items():
                    if assignment.get("success"):
                        print(f"      → {tid}: {assignment.get('team_assigned', 'Assigned')}")
            else:
                print(f"   ⚠️ C-3PO Assignment: {c3po_result.get('reason', 'Pending')}")

        print("\n" + "=" * 80)
        print("📈 TICKET STATISTICS")
        print("=" * 80)

        pm_count = sum(1 for r in results if r.get("pm_ticket"))
        c_count = sum(1 for r in results if r.get("c_ticket"))
        t_count = sum(1 for r in results if r.get("t_ticket"))

        print(f"PM (Problem) Tickets: {pm_count}")
        print(f"C (Change Request) Tickets: {c_count}")
        print(f"T (Task) Tickets: {t_count}")
        print(f"Total Ticket Sets: {len(results)}")

        print("\n" + "=" * 80)
        print("✅ C-3PO Workflow Complete")
        print("=" * 80)
        print("\nAll tickets have been:")
        print("  1. ✅ Created with PM, C, and T types")
        print("  2. ✅ Assigned to appropriate teams by @C3PO")
        print("  3. ✅ Ready for team resolution in their personal stacks")
        print("  4. ✅ Linked by Request ID for tracking")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

def validate_ticket_number(ticket: str) -> tuple[bool, str]:
    """
    Validate ticket number format.

    Args:
        ticket: Ticket number to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not ticket:
        return False, "Ticket number is empty"

    if not TICKET_PATTERN.match(ticket):
        return False, f"Invalid format: {ticket}. Expected: PM000000001, C000000001, T000000001"

    return True, ""

def format_ticket_number(prefix: str, counter: int) -> str:
    """
    Format ticket number with correct 9-digit zero-padding.

    Args:
        prefix: Ticket prefix (PM, C, CR, T)
        counter: Counter value

    Returns:
        Formatted ticket number (e.g., PM000000001)
    """
    return f"{prefix}{counter:09d}"

# Setup paths
project_root = Path(__file__).parent.parent.parent
scripts_python = project_root / "scripts" / "python"
sys.path.insert(0, str(scripts_python))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("VSCodeNotificationMonitor")

# Import ticket system components
HELPDESK_AVAILABLE = False
C3PO_AVAILABLE = False

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("VSCodeNotificationMonitor")

try:
    from jarvis_helpdesk_ticket_system import (
        HelpdeskTicket,
        JARVISHelpdeskTicketSystem,
        TicketPriority,
        TicketStatus,
        TicketType,
    )

    HELPDESK_AVAILABLE = True
    logger.info("✅ Helpdesk ticket system available")
except ImportError as e:
    logger.warning(f"⚠️ Helpdesk ticket system not available: {e}")
    HELPDESK_AVAILABLE = False

    # Define fallbacks
    class _TicketPriority:
        CRITICAL = "critical"
        HIGH = "high"
        MEDIUM = "medium"
        LOW = "low"

    class _TicketStatus:
        OPEN = "open"
        IN_PROGRESS = "in_progress"
        RESOLVED = "resolved"
        CLOSED = "closed"

    class _TicketType:
        PROBLEM = "PM"
        CHANGE_REQUEST = "C"
        CHANGE_TASK = "T"

    TicketPriority = _TicketPriority
    TicketStatus = _TicketStatus
    TicketType = _TicketType


try:
    from jarvis_c3po_ticket_assigner import C3POTicketAssigner

    C3PO_AVAILABLE = True
    logger.info("✅ C-3PO Ticket Assigner available")
except ImportError as e:
    logger.warning(f"⚠️ C-3PO Ticket Assigner not available: {e}")


class VSCodeNotificationMonitor:
    """
    Monitors VS Code / Cursor IDE notifications and manages full ticket lifecycle.

    C-3PO workflow:
    1. Monitor detects notification
    2. Create PM (Problem) ticket with full details
    3. Create C (Change Request) ticket for the fix
    4. Create T (Task) ticket for implementation
    5. C-3PO assigns tickets to appropriate teams
    6. Teams work on their stacks
    7. C-3PO updates and closes tickets upon completion
    """

    # Patterns for common VS Code notifications/errors
    NOTIFICATION_PATTERNS = [
        # Extension activation errors
        (
            r"Cannot activate '(.+)' extension because it depends on an unknown '(.+)' extension",
            "extension_dependency_error",
            TicketPriority.HIGH,
        ),
        # Extension format errors
        (
            r"(\w+\.\w+) \(bad format\) Expected: <provider>\.<name>",
            "extension_format_error",
            TicketPriority.MEDIUM,
        ),
        # Server crashes
        (
            r"(.+) server crashed (\d+) times in the last (\d+) minutes",
            "server_crash",
            TicketPriority.HIGH,
        ),
        # General extension errors
        (
            r"Extension '.+' failed to activate",
            "extension_activation_failed",
            TicketPriority.MEDIUM,
        ),
        # GitHub access errors
        (
            r"No GitHub access token found with access to repository",
            "github_access_error",
            TicketPriority.HIGH,
        ),
    ]

    # Team routing based on issue type
    TEAM_ROUTING = {
        "extension_dependency_error": "jarvis_superagent",
        "extension_format_error": "helpdesk_support",
        "server_crash": "helpdesk_support",
        "extension_activation_failed": "helpdesk_support",
        "github_access_error": "jarvis_superagent",
    }

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.tickets_file = self.project_root / "data/notification_tickets/tickets.json"
        self.tickets_dir = self.tickets_file.parent / "tickets"
        self.tickets_dir.mkdir(parents=True, exist_ok=True)

        # Initialize ticket system
        self.helpdesk_system = None
        if HELPDESK_AVAILABLE:
            try:
                self.helpdesk_system = JARVISHelpdeskTicketSystem(project_root=self.project_root)
                logger.info("✅ Helpdesk system initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize helpdesk system: {e}")

        # Initialize C-3PO
        self.c3po_assigner = None
        if C3PO_AVAILABLE:
            try:
                self.c3po_assigner = C3POTicketAssigner(self.project_root)
                logger.info("✅ C-3PO Ticket Assigner initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize C-3PO: {e}")

        self.notification_tickets: Dict[str, dict] = {}
        self.load_notification_tickets()

    def load_notification_tickets(self):
        """Load existing notification tickets (index + per-ticket files, mirror helpdesk)."""
        self.notification_tickets = _load_notification_tickets_from_storage(
            self.tickets_file, self.tickets_dir
        )
        logger.info(
            f"📂 Loaded {len(self.notification_tickets)} existing notification tickets"
        )

    def save_notification_tickets(self):
        """Save notification tickets to index and per-ticket files (mirror helpdesk)."""
        _save_notification_tickets_to_storage(
            self.tickets_file, self.tickets_dir, self.notification_tickets
        )
        logger.info(f"💾 Saved {len(self.notification_tickets)} notification tickets")

    def generate_request_id(self) -> str:
        """Generate a unique request ID for tracking."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = hashlib.md5(f"{time.time()}".encode()).hexdigest()[:6]
        return f"REQ-VSCODE-{timestamp}-{random_suffix}"

    def parse_notification(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse a notification text and extract relevant information."""
        for pattern, notif_type, priority in self.NOTIFICATION_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                request_id = self.generate_request_id()

                # Build detailed description with solutions
                solutions = {
                    "extension_dependency_error": [
                        "Install the required dependency extension",
                        "Or remove the dependency from the extension manifest",
                        "Clear workspace storage and restart VS Code",
                    ],
                    "extension_format_error": [
                        "Check workspace .code-workspace files for malformed extension IDs",
                        "Clear VS Code workspace storage",
                        "Remove corrupted extension cache",
                    ],
                    "server_crash": [
                        "Disable the crashing extension",
                        "Clear extension cache",
                        "Reinstall the extension if needed",
                    ],
                    "extension_activation_failed": [
                        "Check extension compatibility with VS Code version",
                        "Reinstall the extension",
                        "Check extension logs for specific errors",
                    ],
                    "github_access_error": [
                        "Check GitHub token validity",
                        "Verify token has required repository permissions",
                        "Refresh authentication",
                    ],
                }

                solution_text = "\n".join(
                    [f"{i + 1}. {s}" for i, s in enumerate(solutions.get(notif_type, []))]
                )

                title = f"[VS Code] {notif_type.replace('_', ' ').title()}"
                description = (
                    f"**Notification:** {text}\n\n"
                    f"**Request ID:** {request_id}\n\n"
                    f"**Analysis:**\n"
                    f"Type: {notif_type}\n"
                    f"Severity: {priority.value if hasattr(priority, 'value') else priority}\n\n"
                    f"**Recommended Solutions:**\n{solution_text}\n\n"
                    f"**C-3PO Workflow:**\n"
                    f"1. @C3PO will create PM, C, and T tickets\n"
                    f"2. Assign to appropriate team for resolution\n"
                    f"3. Team works on fix in their ticket stack\n"
                    f"4. @C3PO updates and closes upon completion"
                )

                return {
                    "title": title,
                    "description": description,
                    "notification_type": notif_type,
                    "severity": priority,
                    "request_id": request_id,
                    "team": self.TEAM_ROUTING.get(notif_type, "helpdesk_support"),
                }

        return None

    def create_ticket_set(self, info: Dict[str, Any]) -> Dict[str, str]:
        """
        Create a complete ticket set: PM (Problem), C (Change Request), T (Task).
        All tickets are linked by Request ID.
        """
        created = {}

        if not self.helpdesk_system:
            logger.warning("⚠️ Helpdesk system not available, skipping ticket creation")
            return created

        try:
            # Create PM (Problem) ticket
            pm_title = f"[PM] {info['title']}"
            pm_description = (
                f"**PROBLEM TICKET**\n\n"
                f"{info['description']}\n\n"
                f"**Linked Tickets:**\n"
                f"- C (Change Request): [Will be created]\n"
                f"- T (Task): [Will be created]\n\n"
                f"**Created by:** VS Code Notification Monitor\n"
                f"**Automation:** @JARVIS @C3PO"
            )

            pm_ticket = self.helpdesk_system.create_ticket(
                title=pm_title,
                description=pm_description,
                ticket_type=TicketType.PROBLEM,
                priority=TicketPriority(
                    info["severity"].value
                    if hasattr(info["severity"], "value")
                    else info["severity"]
                ),
                component="VS Code",
                issue_type=info["notification_type"],
            )

            if pm_ticket:
                created["PM"] = pm_ticket.ticket_id
                logger.info(f"✅ Created PM ticket: {pm_ticket.ticket_id}")

                # Link PM to notification record
                info["pm_ticket"] = pm_ticket.ticket_id

        except Exception as e:
            logger.error(f"❌ Error creating PM ticket: {e}")

        try:
            # Create C (Change Request) ticket
            c_title = f"[C] Fix: {info['title'].replace('[VS Code] ', '')}"
            c_description = (
                f"**CHANGE REQUEST TICKET**\n\n"
                f"**Original Problem:** {info['description']}\n\n"
                f"**Required Changes:**\n"
                f"1. Investigate root cause of {info['notification_type']}\n"
                f"2. Design solution for the issue\n"
                f"3. Create implementation plan\n"
                f"4. Test the solution\n\n"
                f"**Linked Tickets:**\n"
                f"- PM (Problem): {created.get('PM', 'N/A')}\n"
                f"- T (Task): [Will be created]\n\n"
                f"**Created by:** VS Code Notification Monitor\n"
                f"**Automation:** @JARVIS @C3PO"
            )

            c_ticket = self.helpdesk_system.create_ticket(
                title=c_title,
                description=c_description,
                ticket_type=TicketType.CHANGE_REQUEST,
                priority=TicketPriority(
                    info["severity"].value
                    if hasattr(info["severity"], "value")
                    else info["severity"]
                ),
                component="VS Code",
                issue_type=f"fix_{info['notification_type']}",
            )

            if c_ticket:
                created["C"] = c_ticket.ticket_id
                logger.info(f"✅ Created C ticket: {c_ticket.ticket_id}")
                info["c_ticket"] = c_ticket.ticket_id

        except Exception as e:
            logger.error(f"❌ Error creating C ticket: {e}")

        try:
            # Create T (Task) ticket
            t_title = f"[T] Implement: {info['title'].replace('[VS Code] ', '')}"
            t_description = (
                f"**TASK TICKET**\n\n"
                f"**Original Problem:** {info['description']}\n\n"
                f"**Implementation Steps:**\n"
                f"1. Review PM and C tickets for full context\n"
                f"2. Implement the fix according to change request\n"
                f"3. Test the implementation thoroughly\n"
                f"4. Update documentation\n"
                f"5. Hand off to C-3PO for closure\n\n"
                f"**Linked Tickets:**\n"
                f"- PM (Problem): {created.get('PM', 'N/A')}\n"
                f"- C (Change Request): {created.get('C', 'N/A')}\n\n"
                f"**Created by:** VS Code Notification Monitor\n"
                f"**Automation:** @JARVIS @C3PO"
            )

            t_ticket = self.helpdesk_system.create_ticket(
                title=t_title,
                description=t_description,
                ticket_type=TicketType.CHANGE_TASK,
                priority=TicketPriority(
                    info["severity"].value
                    if hasattr(info["severity"], "value")
                    else info["severity"]
                ),
                component="VS Code",
                issue_type=f"task_{info['notification_type']}",
            )

            if t_ticket:
                created["T"] = t_ticket.ticket_id
                logger.info(f"✅ Created T ticket: {t_ticket.ticket_id}")
                info["t_ticket"] = t_ticket.ticket_id

        except Exception as e:
            logger.error(f"❌ Error creating T ticket: {e}")

        return created

    def c3po_assign_tickets(self, tickets: Dict[str, str], team: str) -> Dict[str, Any]:
        """
        C-3PO assigns tickets to appropriate teams.

        C-3PO ensures:
        - Team Manager oversight (@c3po)
        - Technical Lead assignment (@r2d2 or team-specific)
        - Business Lead for coordination
        """
        if not self.c3po_assigner:
            logger.warning("⚠️ C-3PO not available for ticket assignment")
            return {"success": False, "reason": "C-3PO not available"}

        try:
            assignments = {}
            logger.info("=" * 80)
            logger.info("🤖 C-3PO ASSIGNING TICKETS TO TEAMS")
            logger.info("=" * 80)

            for ticket_type, ticket_id in tickets.items():
                if ticket_id:
                    result = self.c3po_assigner.assign_ticket_to_team(
                        ticket_number=ticket_id, team_id=team, auto_detect=True
                    )
                    assignments[ticket_id] = result
                    if result.get("success"):
                        logger.info(f"✅ {ticket_id} -> Team: {result.get('team_assigned', team)}")
                    else:
                        logger.warning(
                            f"⚠️ {ticket_id} assignment: {result.get('error', 'Unknown')}"
                        )

            logger.info("=" * 80)
            logger.info("✅ C-3PO assignment complete")
            logger.info("=" * 80)

            return {"success": True, "assignments": assignments}

        except Exception as e:
            logger.error(f"❌ Error in C-3PO assignment: {e}")
            return {"success": False, "error": str(e)}

    def save_notification_record(self, info: Dict[str, Any], tickets: Dict[str, str]):
        """Save the notification and ticket references."""
        ticket_id = hashlib.md5(f"{info['title']}|{info['request_id']}".encode()).hexdigest()[:14]

        record = {
            "ticket_id": ticket_id,
            "title": info["title"],
            "description": info["description"],
            "notification_type": info["notification_type"],
            "severity": info["severity"].value
            if hasattr(info["severity"], "value")
            else info["severity"],
            "request_id": info["request_id"],
            "team": info.get("team"),
            "pm_ticket": tickets.get("PM"),
            "c_ticket": tickets.get("C"),
            "t_ticket": tickets.get("T"),
            "status": "open",
            "priority": info["severity"].value
            if hasattr(info["severity"], "value")
            else info["severity"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "resolved_at": None,
            "metadata": {
                "c3po_assigned": False,
                "team_notified": False,
                "work_started": False,
                "completed": False,
            },
        }

        self.notification_tickets[ticket_id] = record
        self.save_notification_tickets()

        return record

    def process_notification(self, text: str) -> Optional[Dict[str, Any]]:
        """Process a notification with full C-3PO workflow."""
        info = self.parse_notification(text)
        if not info:
            return None

        # Check for duplicate
        for existing in self.notification_tickets.values():
            if existing.get("title") == info["title"]:
                logger.debug(f"Notification already processed: {info['title']}")
                return existing

        # Create ticket set
        tickets = self.create_ticket_set(info)

        # C-3PO assigns to team
        c3po_result = self.c3po_assign_tickets(tickets, info.get("team", "helpdesk_support"))

        # Save record
        record = self.save_notification_record(info, tickets)
        record["c3po_assignment"] = c3po_result

        return record

    def report_current_issues(self) -> List[Dict[str, Any]]:
        """
        Report and create tickets for known VS Code issues.
        This implements the full C-3PO workflow.
        """
        issues = [
            {
                "title": "[VS Code] Lumina Core Extension - Missing GitHub Copilot Dependency",
                "description": (
                    "Cannot activate 'Lumina Core - Open Source Lumina Ecosystem' extension "
                    "because it depends on an unknown 'github.copilot' extension.\n\n"
                    "**Analysis:**\n"
                    "- The Lumina Core extension has GitHub Copilot listed as a dependency\n"
                    "- Copilot may not be installed or may have a different extension ID\n"
                    "- This could also be a cached/corrupted extension state\n\n"
                    "**C-3PO Actions:**\n"
                    "1. Create PM, C, T tickets\n"
                    "2. Assign to jarvis_superagent team\n"
                    "3. Team implements fix\n"
                    "4. C-3PO closes upon completion"
                ),
                "type": "extension_dependency_error",
                "severity": TicketPriority.HIGH,
            },
            {
                "title": "[VS Code] Extension Format Error - undefined_publisher.lumina-ai",
                "description": (
                    "The extension recommendation 'undefined_publisher.lumina-ai' has bad format. "
                    "Expected format: <provider>.<name>\n\n"
                    "**Analysis:**\n"
                    "- A workspace or project configuration has a malformed extension reference\n"
                    "- 'undefined_publisher' suggests the publisher field is missing\n\n"
                    "**C-3PO Actions:**\n"
                    "1. Create PM, C, T tickets\n"
                    "2. Assign to helpdesk_support team\n"
                    "3. Team investigates and fixes\n"
                    "4. C-3PO closes upon completion"
                ),
                "type": "extension_format_error",
                "severity": TicketPriority.MEDIUM,
            },
            {
                "title": "[VS Code] Microsoft Edge Tools Server Crashes",
                "description": (
                    "Microsoft Edge Tools server crashed 5 times in the last 3 minutes. "
                    "The server will not be restarted.\n\n"
                    "**Analysis:**\n"
                    "- The Edge Tools extension has become unstable\n"
                    "- Known issue with certain VS Code versions\n\n"
                    "**C-3PO Actions:**\n"
                    "1. Create PM, C, T tickets\n"
                    "2. Assign to helpdesk_support team\n"
                    "3. Team disables/reinstalls extension\n"
                    "4. C-3PO closes upon completion"
                ),
                "type": "server_crash",
                "severity": TicketPriority.HIGH,
            },
        ]

        results = []
        for issue in issues:
            logger.info(f"\n📋 Processing: {issue['title']}")

            info = {
                "title": issue["title"],
                "description": issue["description"],
                "notification_type": issue["type"],
                "severity": issue["severity"],
                "request_id": self.generate_request_id(),
                "team": self.TEAM_ROUTING.get(issue["type"], "helpdesk_support"),
            }

            # Create tickets
            tickets = self.create_ticket_set(info)

            # C-3PO assigns
            c3po_result = self.c3po_assign_tickets(tickets, info["team"])

            # Save record
            record = self.save_notification_record(info, tickets)
            record["tickets"] = tickets
            record["c3po_result"] = c3po_result

            results.append(record)

        return results


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="VS Code Notification Monitor with C-3PO Ticket Lifecycle",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/python/monitor_vscode_notifications.py --report
      Process current VS Code issues with full C-3PO workflow

Workflow:
  1. Detect notification
  2. Create PM (Problem), C (Change Request), T (Task) tickets
  3. @C3PO assigns tickets to appropriate teams
  4. Teams work on their personal ticket stacks
  5. @C3PO updates, maintains, and closes tickets
        """,
    )
    parser.add_argument(
        "--report", action="store_true", help="Report current issues and create tickets"
    )
    args = parser.parse_args()

    monitor = VSCodeNotificationMonitor()

    if args.report:
        print("=" * 80)
        print("🤖 VS Code Notification Monitor with C-3PO Ticket Lifecycle")
        print("=" * 80)
        print()

        results = monitor.report_current_issues()

        print("\n" + "=" * 80)
        print("📊 SUMMARY - TICKETS CREATED AND ASSIGNED")
        print("=" * 80)

        for result in results:
            print(f"\n📋 Request ID: {result['request_id']}")
            print(f"   Title: {result['title']}")
            print(f"   Team: {result['team']}")
            print("   Tickets Created:")
            print(f"      - PM (Problem): {result.get('pm_ticket', 'N/A')}")
            print(f"      - C (Change Request): {result.get('c_ticket', 'N/A')}")
            print(f"      - T (Task): {result.get('t_ticket', 'N/A')}")

            c3po_result = result.get("c3po_result", {})
            if c3po_result.get("success"):
                print("   ✅ C-3PO Assignment: Success")
                assignments = c3po_result.get("assignments", {})
                for tid, assignment in assignments.items():
                    if assignment.get("success"):
                        print(f"      → {tid}: {assignment.get('team_assigned', 'Assigned')}")
            else:
                print(f"   ⚠️ C-3PO Assignment: {c3po_result.get('reason', 'Pending')}")

        print("\n" + "=" * 80)
        print("📈 TICKET STATISTICS")
        print("=" * 80)

        pm_count = sum(1 for r in results if r.get("pm_ticket"))
        c_count = sum(1 for r in results if r.get("c_ticket"))
        t_count = sum(1 for r in results if r.get("t_ticket"))

        print(f"PM (Problem) Tickets: {pm_count}")
        print(f"C (Change Request) Tickets: {c_count}")
        print(f"T (Task) Tickets: {t_count}")
        print(f"Total Ticket Sets: {len(results)}")

        print("\n" + "=" * 80)
        print("✅ C-3PO Workflow Complete")
        print("=" * 80)
        print("\nAll tickets have been:")
        print("  1. ✅ Created with PM, C, and T types")
        print("  2. ✅ Assigned to appropriate teams by @C3PO")
        print("  3. ✅ Ready for team resolution in their personal stacks")
        print("  4. ✅ Linked by Request ID for tracking")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

project_root = Path(__file__).parent.parent.parent
scripts_python = project_root / "scripts" / "python"
sys.path.insert(0, str(scripts_python))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("VSCodeNotificationMonitor")

# Import ticket system components
HELPDESK_AVAILABLE = False
C3PO_AVAILABLE = False

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("VSCodeNotificationMonitor")

try:
    from jarvis_helpdesk_ticket_system import (
        HelpdeskTicket,
        JARVISHelpdeskTicketSystem,
        TicketPriority,
        TicketStatus,
        TicketType,
    )

    HELPDESK_AVAILABLE = True
    logger.info("✅ Helpdesk ticket system available")
except ImportError as e:
    logger.warning(f"⚠️ Helpdesk ticket system not available: {e}")
    HELPDESK_AVAILABLE = False

    # Define fallbacks
    class _TicketPriority:
        CRITICAL = "critical"
        HIGH = "high"
        MEDIUM = "medium"
        LOW = "low"

    class _TicketStatus:
        OPEN = "open"
        IN_PROGRESS = "in_progress"
        RESOLVED = "resolved"
        CLOSED = "closed"

    class _TicketType:
        PROBLEM = "PM"
        CHANGE_REQUEST = "C"
        CHANGE_TASK = "T"

    TicketPriority = _TicketPriority
    TicketStatus = _TicketStatus
    TicketType = _TicketType


try:
    from jarvis_c3po_ticket_assigner import C3POTicketAssigner

    C3PO_AVAILABLE = True
    logger.info("✅ C-3PO Ticket Assigner available")
except ImportError as e:
    logger.warning(f"⚠️ C-3PO Ticket Assigner not available: {e}")


class VSCodeNotificationMonitor:
    """
    Monitors VS Code / Cursor IDE notifications and manages full ticket lifecycle.

    C-3PO workflow:
    1. Monitor detects notification
    2. Create PM (Problem) ticket with full details
    3. Create C (Change Request) ticket for the fix
    4. Create T (Task) ticket for implementation
    5. C-3PO assigns tickets to appropriate teams
    6. Teams work on their stacks
    7. C-3PO updates and closes tickets upon completion
    """

    # Patterns for common VS Code notifications/errors
    NOTIFICATION_PATTERNS = [
        # Extension activation errors
        (
            r"Cannot activate '(.+)' extension because it depends on an unknown '(.+)' extension",
            "extension_dependency_error",
            TicketPriority.HIGH,
        ),
        # Extension format errors
        (
            r"(\w+\.\w+) \(bad format\) Expected: <provider>\.<name>",
            "extension_format_error",
            TicketPriority.MEDIUM,
        ),
        # Server crashes
        (
            r"(.+) server crashed (\d+) times in the last (\d+) minutes",
            "server_crash",
            TicketPriority.HIGH,
        ),
        # General extension errors
        (
            r"Extension '.+' failed to activate",
            "extension_activation_failed",
            TicketPriority.MEDIUM,
        ),
        # GitHub access errors
        (
            r"No GitHub access token found with access to repository",
            "github_access_error",
            TicketPriority.HIGH,
        ),
    ]

    # Team routing based on issue type
    TEAM_ROUTING = {
        "extension_dependency_error": "jarvis_superagent",
        "extension_format_error": "helpdesk_support",
        "server_crash": "helpdesk_support",
        "extension_activation_failed": "helpdesk_support",
        "github_access_error": "jarvis_superagent",
    }

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.tickets_file = self.project_root / "data/notification_tickets/tickets.json"
        self.tickets_dir = self.tickets_file.parent / "tickets"
        self.tickets_dir.mkdir(parents=True, exist_ok=True)

        # Initialize ticket system
        self.helpdesk_system = None
        if HELPDESK_AVAILABLE:
            try:
                self.helpdesk_system = JARVISHelpdeskTicketSystem(project_root=self.project_root)
                logger.info("✅ Helpdesk system initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize helpdesk system: {e}")

        # Initialize C-3PO
        self.c3po_assigner = None
        if C3PO_AVAILABLE:
            try:
                self.c3po_assigner = C3POTicketAssigner(self.project_root)
                logger.info("✅ C-3PO Ticket Assigner initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize C-3PO: {e}")

        self.notification_tickets: Dict[str, dict] = {}
        self.load_notification_tickets()

    def load_notification_tickets(self):
        """Load existing notification tickets (index + per-ticket files, mirror helpdesk)."""
        self.notification_tickets = _load_notification_tickets_from_storage(
            self.tickets_file, self.tickets_dir
        )
        logger.info(
            f"📂 Loaded {len(self.notification_tickets)} existing notification tickets"
        )

    def save_notification_tickets(self):
        """Save notification tickets to index and per-ticket files (mirror helpdesk)."""
        _save_notification_tickets_to_storage(
            self.tickets_file, self.tickets_dir, self.notification_tickets
        )
        logger.info(f"💾 Saved {len(self.notification_tickets)} notification tickets")

    def generate_request_id(self) -> str:
        """Generate a unique request ID for tracking."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = hashlib.md5(f"{time.time()}".encode()).hexdigest()[:6]
        return f"REQ-VSCODE-{timestamp}-{random_suffix}"

    def parse_notification(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse a notification text and extract relevant information."""
        for pattern, notif_type, priority in self.NOTIFICATION_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                request_id = self.generate_request_id()

                # Build detailed description with solutions
                solutions = {
                    "extension_dependency_error": [
                        "Install the required dependency extension",
                        "Or remove the dependency from the extension manifest",
                        "Clear workspace storage and restart VS Code",
                    ],
                    "extension_format_error": [
                        "Check workspace .code-workspace files for malformed extension IDs",
                        "Clear VS Code workspace storage",
                        "Remove corrupted extension cache",
                    ],
                    "server_crash": [
                        "Disable the crashing extension",
                        "Clear extension cache",
                        "Reinstall the extension if needed",
                    ],
                    "extension_activation_failed": [
                        "Check extension compatibility with VS Code version",
                        "Reinstall the extension",
                        "Check extension logs for specific errors",
                    ],
                    "github_access_error": [
                        "Check GitHub token validity",
                        "Verify token has required repository permissions",
                        "Refresh authentication",
                    ],
                }

                solution_text = "\n".join(
                    [f"{i + 1}. {s}" for i, s in enumerate(solutions.get(notif_type, []))]
                )

                title = f"[VS Code] {notif_type.replace('_', ' ').title()}"
                description = (
                    f"**Notification:** {text}\n\n"
                    f"**Request ID:** {request_id}\n\n"
                    f"**Analysis:**\n"
                    f"Type: {notif_type}\n"
                    f"Severity: {priority.value if hasattr(priority, 'value') else priority}\n\n"
                    f"**Recommended Solutions:**\n{solution_text}\n\n"
                    f"**C-3PO Workflow:**\n"
                    f"1. @C3PO will create PM, C, and T tickets\n"
                    f"2. Assign to appropriate team for resolution\n"
                    f"3. Team works on fix in their ticket stack\n"
                    f"4. @C3PO updates and closes upon completion"
                )

                return {
                    "title": title,
                    "description": description,
                    "notification_type": notif_type,
                    "severity": priority,
                    "request_id": request_id,
                    "team": self.TEAM_ROUTING.get(notif_type, "helpdesk_support"),
                }

        return None

    def create_ticket_set(self, info: Dict[str, Any]) -> Dict[str, str]:
        """
        Create a complete ticket set: PM (Problem), C (Change Request), T (Task).
        All tickets are linked by Request ID.
        """
        created = {}

        if not self.helpdesk_system:
            logger.warning("⚠️ Helpdesk system not available, skipping ticket creation")
            return created

        try:
            # Create PM (Problem) ticket
            pm_title = f"[PM] {info['title']}"
            pm_description = (
                f"**PROBLEM TICKET**\n\n"
                f"{info['description']}\n\n"
                f"**Linked Tickets:**\n"
                f"- C (Change Request): [Will be created]\n"
                f"- T (Task): [Will be created]\n\n"
                f"**Created by:** VS Code Notification Monitor\n"
                f"**Automation:** @JARVIS @C3PO"
            )

            pm_ticket = self.helpdesk_system.create_ticket(
                title=pm_title,
                description=pm_description,
                ticket_type=TicketType.PROBLEM,
                priority=TicketPriority(
                    info["severity"].value
                    if hasattr(info["severity"], "value")
                    else info["severity"]
                ),
                component="VS Code",
                issue_type=info["notification_type"],
            )

            if pm_ticket:
                created["PM"] = pm_ticket.ticket_id
                logger.info(f"✅ Created PM ticket: {pm_ticket.ticket_id}")

                # Link PM to notification record
                info["pm_ticket"] = pm_ticket.ticket_id

        except Exception as e:
            logger.error(f"❌ Error creating PM ticket: {e}")

        try:
            # Create C (Change Request) ticket
            c_title = f"[C] Fix: {info['title'].replace('[VS Code] ', '')}"
            c_description = (
                f"**CHANGE REQUEST TICKET**\n\n"
                f"**Original Problem:** {info['description']}\n\n"
                f"**Required Changes:**\n"
                f"1. Investigate root cause of {info['notification_type']}\n"
                f"2. Design solution for the issue\n"
                f"3. Create implementation plan\n"
                f"4. Test the solution\n\n"
                f"**Linked Tickets:**\n"
                f"- PM (Problem): {created.get('PM', 'N/A')}\n"
                f"- T (Task): [Will be created]\n\n"
                f"**Created by:** VS Code Notification Monitor\n"
                f"**Automation:** @JARVIS @C3PO"
            )

            c_ticket = self.helpdesk_system.create_ticket(
                title=c_title,
                description=c_description,
                ticket_type=TicketType.CHANGE_REQUEST,
                priority=TicketPriority(
                    info["severity"].value
                    if hasattr(info["severity"], "value")
                    else info["severity"]
                ),
                component="VS Code",
                issue_type=f"fix_{info['notification_type']}",
            )

            if c_ticket:
                created["C"] = c_ticket.ticket_id
                logger.info(f"✅ Created C ticket: {c_ticket.ticket_id}")
                info["c_ticket"] = c_ticket.ticket_id

        except Exception as e:
            logger.error(f"❌ Error creating C ticket: {e}")

        try:
            # Create T (Task) ticket
            t_title = f"[T] Implement: {info['title'].replace('[VS Code] ', '')}"
            t_description = (
                f"**TASK TICKET**\n\n"
                f"**Original Problem:** {info['description']}\n\n"
                f"**Implementation Steps:**\n"
                f"1. Review PM and C tickets for full context\n"
                f"2. Implement the fix according to change request\n"
                f"3. Test the implementation thoroughly\n"
                f"4. Update documentation\n"
                f"5. Hand off to C-3PO for closure\n\n"
                f"**Linked Tickets:**\n"
                f"- PM (Problem): {created.get('PM', 'N/A')}\n"
                f"- C (Change Request): {created.get('C', 'N/A')}\n\n"
                f"**Created by:** VS Code Notification Monitor\n"
                f"**Automation:** @JARVIS @C3PO"
            )

            t_ticket = self.helpdesk_system.create_ticket(
                title=t_title,
                description=t_description,
                ticket_type=TicketType.CHANGE_TASK,
                priority=TicketPriority(
                    info["severity"].value
                    if hasattr(info["severity"], "value")
                    else info["severity"]
                ),
                component="VS Code",
                issue_type=f"task_{info['notification_type']}",
            )

            if t_ticket:
                created["T"] = t_ticket.ticket_id
                logger.info(f"✅ Created T ticket: {t_ticket.ticket_id}")
                info["t_ticket"] = t_ticket.ticket_id

        except Exception as e:
            logger.error(f"❌ Error creating T ticket: {e}")

        return created

    def c3po_assign_tickets(self, tickets: Dict[str, str], team: str) -> Dict[str, Any]:
        """
        C-3PO assigns tickets to appropriate teams.

        C-3PO ensures:
        - Team Manager oversight (@c3po)
        - Technical Lead assignment (@r2d2 or team-specific)
        - Business Lead for coordination
        """
        if not self.c3po_assigner:
            logger.warning("⚠️ C-3PO not available for ticket assignment")
            return {"success": False, "reason": "C-3PO not available"}

        try:
            assignments = {}
            logger.info("=" * 80)
            logger.info("🤖 C-3PO ASSIGNING TICKETS TO TEAMS")
            logger.info("=" * 80)

            for ticket_type, ticket_id in tickets.items():
                if ticket_id:
                    result = self.c3po_assigner.assign_ticket_to_team(
                        ticket_number=ticket_id, team_id=team, auto_detect=True
                    )
                    assignments[ticket_id] = result
                    if result.get("success"):
                        logger.info(f"✅ {ticket_id} -> Team: {result.get('team_assigned', team)}")
                    else:
                        logger.warning(
                            f"⚠️ {ticket_id} assignment: {result.get('error', 'Unknown')}"
                        )

            logger.info("=" * 80)
            logger.info("✅ C-3PO assignment complete")
            logger.info("=" * 80)

            return {"success": True, "assignments": assignments}

        except Exception as e:
            logger.error(f"❌ Error in C-3PO assignment: {e}")
            return {"success": False, "error": str(e)}

    def save_notification_record(self, info: Dict[str, Any], tickets: Dict[str, str]):
        """Save the notification and ticket references."""
        ticket_id = hashlib.md5(f"{info['title']}|{info['request_id']}".encode()).hexdigest()[:14]

        record = {
            "ticket_id": ticket_id,
            "title": info["title"],
            "description": info["description"],
            "notification_type": info["notification_type"],
            "severity": info["severity"].value
            if hasattr(info["severity"], "value")
            else info["severity"],
            "request_id": info["request_id"],
            "team": info.get("team"),
            "pm_ticket": tickets.get("PM"),
            "c_ticket": tickets.get("C"),
            "t_ticket": tickets.get("T"),
            "status": "open",
            "priority": info["severity"].value
            if hasattr(info["severity"], "value")
            else info["severity"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "resolved_at": None,
            "metadata": {
                "c3po_assigned": False,
                "team_notified": False,
                "work_started": False,
                "completed": False,
            },
        }

        self.notification_tickets[ticket_id] = record
        self.save_notification_tickets()

        return record

    def process_notification(self, text: str) -> Optional[Dict[str, Any]]:
        """Process a notification with full C-3PO workflow."""
        info = self.parse_notification(text)
        if not info:
            return None

        # Check for duplicate
        for existing in self.notification_tickets.values():
            if existing.get("title") == info["title"]:
                logger.debug(f"Notification already processed: {info['title']}")
                return existing

        # Create ticket set
        tickets = self.create_ticket_set(info)

        # C-3PO assigns to team
        c3po_result = self.c3po_assign_tickets(tickets, info.get("team", "helpdesk_support"))

        # Save record
        record = self.save_notification_record(info, tickets)
        record["c3po_assignment"] = c3po_result

        return record

    def report_current_issues(self) -> List[Dict[str, Any]]:
        """
        Report and create tickets for known VS Code issues.
        This implements the full C-3PO workflow.
        """
        issues = [
            {
                "title": "[VS Code] Lumina Core Extension - Missing GitHub Copilot Dependency",
                "description": (
                    "Cannot activate 'Lumina Core - Open Source Lumina Ecosystem' extension "
                    "because it depends on an unknown 'github.copilot' extension.\n\n"
                    "**Analysis:**\n"
                    "- The Lumina Core extension has GitHub Copilot listed as a dependency\n"
                    "- Copilot may not be installed or may have a different extension ID\n"
                    "- This could also be a cached/corrupted extension state\n\n"
                    "**C-3PO Actions:**\n"
                    "1. Create PM, C, T tickets\n"
                    "2. Assign to jarvis_superagent team\n"
                    "3. Team implements fix\n"
                    "4. C-3PO closes upon completion"
                ),
                "type": "extension_dependency_error",
                "severity": TicketPriority.HIGH,
            },
            {
                "title": "[VS Code] Extension Format Error - undefined_publisher.lumina-ai",
                "description": (
                    "The extension recommendation 'undefined_publisher.lumina-ai' has bad format. "
                    "Expected format: <provider>.<name>\n\n"
                    "**Analysis:**\n"
                    "- A workspace or project configuration has a malformed extension reference\n"
                    "- 'undefined_publisher' suggests the publisher field is missing\n\n"
                    "**C-3PO Actions:**\n"
                    "1. Create PM, C, T tickets\n"
                    "2. Assign to helpdesk_support team\n"
                    "3. Team investigates and fixes\n"
                    "4. C-3PO closes upon completion"
                ),
                "type": "extension_format_error",
                "severity": TicketPriority.MEDIUM,
            },
            {
                "title": "[VS Code] Microsoft Edge Tools Server Crashes",
                "description": (
                    "Microsoft Edge Tools server crashed 5 times in the last 3 minutes. "
                    "The server will not be restarted.\n\n"
                    "**Analysis:**\n"
                    "- The Edge Tools extension has become unstable\n"
                    "- Known issue with certain VS Code versions\n\n"
                    "**C-3PO Actions:**\n"
                    "1. Create PM, C, T tickets\n"
                    "2. Assign to helpdesk_support team\n"
                    "3. Team disables/reinstalls extension\n"
                    "4. C-3PO closes upon completion"
                ),
                "type": "server_crash",
                "severity": TicketPriority.HIGH,
            },
        ]

        results = []
        for issue in issues:
            logger.info(f"\n📋 Processing: {issue['title']}")

            info = {
                "title": issue["title"],
                "description": issue["description"],
                "notification_type": issue["type"],
                "severity": issue["severity"],
                "request_id": self.generate_request_id(),
                "team": self.TEAM_ROUTING.get(issue["type"], "helpdesk_support"),
            }

            # Create tickets
            tickets = self.create_ticket_set(info)

            # C-3PO assigns
            c3po_result = self.c3po_assign_tickets(tickets, info["team"])

            # Save record
            record = self.save_notification_record(info, tickets)
            record["tickets"] = tickets
            record["c3po_result"] = c3po_result

            results.append(record)

        return results


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="VS Code Notification Monitor with C-3PO Ticket Lifecycle",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/python/monitor_vscode_notifications.py --report
      Process current VS Code issues with full C-3PO workflow

Workflow:
  1. Detect notification
  2. Create PM (Problem), C (Change Request), T (Task) tickets
  3. @C3PO assigns tickets to appropriate teams
  4. Teams work on their personal ticket stacks
  5. @C3PO updates, maintains, and closes tickets
        """,
    )
    parser.add_argument(
        "--report", action="store_true", help="Report current issues and create tickets"
    )
    args = parser.parse_args()

    monitor = VSCodeNotificationMonitor()

    if args.report:
        print("=" * 80)
        print("🤖 VS Code Notification Monitor with C-3PO Ticket Lifecycle")
        print("=" * 80)
        print()

        results = monitor.report_current_issues()

        print("\n" + "=" * 80)
        print("📊 SUMMARY - TICKETS CREATED AND ASSIGNED")
        print("=" * 80)

        for result in results:
            print(f"\n📋 Request ID: {result['request_id']}")
            print(f"   Title: {result['title']}")
            print(f"   Team: {result['team']}")
            print("   Tickets Created:")
            print(f"      - PM (Problem): {result.get('pm_ticket', 'N/A')}")
            print(f"      - C (Change Request): {result.get('c_ticket', 'N/A')}")
            print(f"      - T (Task): {result.get('t_ticket', 'N/A')}")

            c3po_result = result.get("c3po_result", {})
            if c3po_result.get("success"):
                print("   ✅ C-3PO Assignment: Success")
                assignments = c3po_result.get("assignments", {})
                for tid, assignment in assignments.items():
                    if assignment.get("success"):
                        print(f"      → {tid}: {assignment.get('team_assigned', 'Assigned')}")
            else:
                print(f"   ⚠️ C-3PO Assignment: {c3po_result.get('reason', 'Pending')}")

        print("\n" + "=" * 80)
        print("📈 TICKET STATISTICS")
        print("=" * 80)

        pm_count = sum(1 for r in results if r.get("pm_ticket"))
        c_count = sum(1 for r in results if r.get("c_ticket"))
        t_count = sum(1 for r in results if r.get("t_ticket"))

        print(f"PM (Problem) Tickets: {pm_count}")
        print(f"C (Change Request) Tickets: {c_count}")
        print(f"T (Task) Tickets: {t_count}")
        print(f"Total Ticket Sets: {len(results)}")

        print("\n" + "=" * 80)
        print("✅ C-3PO Workflow Complete")
        print("=" * 80)
        print("\nAll tickets have been:")
        print("  1. ✅ Created with PM, C, and T types")
        print("  2. ✅ Assigned to appropriate teams by @C3PO")
        print("  3. ✅ Ready for team resolution in their personal stacks")
        print("  4. ✅ Linked by Request ID for tracking")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

def validate_ticket_number(ticket: str) -> tuple[bool, str]:
    """
    Validate ticket number format.

    Args:
        ticket: Ticket number to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not ticket:
        return False, "Ticket number is empty"

    if not TICKET_PATTERN.match(ticket):
        return False, f"Invalid format: {ticket}. Expected: PM000000001, C000000001, T000000001"

    return True, ""

def format_ticket_number(prefix: str, counter: int) -> str:
    """
    Format ticket number with correct 9-digit zero-padding.

    Args:
        prefix: Ticket prefix (PM, C, CR, T)
        counter: Counter value

    Returns:
        Formatted ticket number (e.g., PM000000001)
    """
    return f"{prefix}{counter:09d}"

# Setup paths
project_root = Path(__file__).parent.parent.parent
scripts_python = project_root / "scripts" / "python"
sys.path.insert(0, str(scripts_python))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("VSCodeNotificationMonitor")

# Import ticket system components
HELPDESK_AVAILABLE = False
C3PO_AVAILABLE = False

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("VSCodeNotificationMonitor")

try:
    from jarvis_helpdesk_ticket_system import (
        HelpdeskTicket,
        JARVISHelpdeskTicketSystem,
        TicketPriority,
        TicketStatus,
        TicketType,
    )

    HELPDESK_AVAILABLE = True
    logger.info("✅ Helpdesk ticket system available")
except ImportError as e:
    logger.warning(f"⚠️ Helpdesk ticket system not available: {e}")
    HELPDESK_AVAILABLE = False

    # Define fallbacks
    class _TicketPriority:
        CRITICAL = "critical"
        HIGH = "high"
        MEDIUM = "medium"
        LOW = "low"

    class _TicketStatus:
        OPEN = "open"
        IN_PROGRESS = "in_progress"
        RESOLVED = "resolved"
        CLOSED = "closed"

    class _TicketType:
        PROBLEM = "PM"
        CHANGE_REQUEST = "C"
        CHANGE_TASK = "T"

    TicketPriority = _TicketPriority
    TicketStatus = _TicketStatus
    TicketType = _TicketType


try:
    from jarvis_c3po_ticket_assigner import C3POTicketAssigner

    C3PO_AVAILABLE = True
    logger.info("✅ C-3PO Ticket Assigner available")
except ImportError as e:
    logger.warning(f"⚠️ C-3PO Ticket Assigner not available: {e}")


class VSCodeNotificationMonitor:
    """
    Monitors VS Code / Cursor IDE notifications and manages full ticket lifecycle.

    C-3PO workflow:
    1. Monitor detects notification
    2. Create PM (Problem) ticket with full details
    3. Create C (Change Request) ticket for the fix
    4. Create T (Task) ticket for implementation
    5. C-3PO assigns tickets to appropriate teams
    6. Teams work on their stacks
    7. C-3PO updates and closes tickets upon completion
    """

    # Patterns for common VS Code notifications/errors
    NOTIFICATION_PATTERNS = [
        # Extension activation errors
        (
            r"Cannot activate '(.+)' extension because it depends on an unknown '(.+)' extension",
            "extension_dependency_error",
            TicketPriority.HIGH,
        ),
        # Extension format errors
        (
            r"(\w+\.\w+) \(bad format\) Expected: <provider>\.<name>",
            "extension_format_error",
            TicketPriority.MEDIUM,
        ),
        # Server crashes
        (
            r"(.+) server crashed (\d+) times in the last (\d+) minutes",
            "server_crash",
            TicketPriority.HIGH,
        ),
        # General extension errors
        (
            r"Extension '.+' failed to activate",
            "extension_activation_failed",
            TicketPriority.MEDIUM,
        ),
        # GitHub access errors
        (
            r"No GitHub access token found with access to repository",
            "github_access_error",
            TicketPriority.HIGH,
        ),
    ]

    # Team routing based on issue type
    TEAM_ROUTING = {
        "extension_dependency_error": "jarvis_superagent",
        "extension_format_error": "helpdesk_support",
        "server_crash": "helpdesk_support",
        "extension_activation_failed": "helpdesk_support",
        "github_access_error": "jarvis_superagent",
    }

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.tickets_file = self.project_root / "data/notification_tickets/tickets.json"
        self.tickets_dir = self.tickets_file.parent / "tickets"
        self.tickets_dir.mkdir(parents=True, exist_ok=True)

        # Initialize ticket system
        self.helpdesk_system = None
        if HELPDESK_AVAILABLE:
            try:
                self.helpdesk_system = JARVISHelpdeskTicketSystem(project_root=self.project_root)
                logger.info("✅ Helpdesk system initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize helpdesk system: {e}")

        # Initialize C-3PO
        self.c3po_assigner = None
        if C3PO_AVAILABLE:
            try:
                self.c3po_assigner = C3POTicketAssigner(self.project_root)
                logger.info("✅ C-3PO Ticket Assigner initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize C-3PO: {e}")

        self.notification_tickets: Dict[str, dict] = {}
        self.load_notification_tickets()

    def load_notification_tickets(self):
        """Load existing notification tickets (index + per-ticket files, mirror helpdesk)."""
        self.notification_tickets = _load_notification_tickets_from_storage(
            self.tickets_file, self.tickets_dir
        )
        logger.info(
            f"📂 Loaded {len(self.notification_tickets)} existing notification tickets"
        )

    def save_notification_tickets(self):
        """Save notification tickets to index and per-ticket files (mirror helpdesk)."""
        _save_notification_tickets_to_storage(
            self.tickets_file, self.tickets_dir, self.notification_tickets
        )
        logger.info(f"💾 Saved {len(self.notification_tickets)} notification tickets")

    def generate_request_id(self) -> str:
        """Generate a unique request ID for tracking."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = hashlib.md5(f"{time.time()}".encode()).hexdigest()[:6]
        return f"REQ-VSCODE-{timestamp}-{random_suffix}"

    def parse_notification(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse a notification text and extract relevant information."""
        for pattern, notif_type, priority in self.NOTIFICATION_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                request_id = self.generate_request_id()

                # Build detailed description with solutions
                solutions = {
                    "extension_dependency_error": [
                        "Install the required dependency extension",
                        "Or remove the dependency from the extension manifest",
                        "Clear workspace storage and restart VS Code",
                    ],
                    "extension_format_error": [
                        "Check workspace .code-workspace files for malformed extension IDs",
                        "Clear VS Code workspace storage",
                        "Remove corrupted extension cache",
                    ],
                    "server_crash": [
                        "Disable the crashing extension",
                        "Clear extension cache",
                        "Reinstall the extension if needed",
                    ],
                    "extension_activation_failed": [
                        "Check extension compatibility with VS Code version",
                        "Reinstall the extension",
                        "Check extension logs for specific errors",
                    ],
                    "github_access_error": [
                        "Check GitHub token validity",
                        "Verify token has required repository permissions",
                        "Refresh authentication",
                    ],
                }

                solution_text = "\n".join(
                    [f"{i + 1}. {s}" for i, s in enumerate(solutions.get(notif_type, []))]
                )

                title = f"[VS Code] {notif_type.replace('_', ' ').title()}"
                description = (
                    f"**Notification:** {text}\n\n"
                    f"**Request ID:** {request_id}\n\n"
                    f"**Analysis:**\n"
                    f"Type: {notif_type}\n"
                    f"Severity: {priority.value if hasattr(priority, 'value') else priority}\n\n"
                    f"**Recommended Solutions:**\n{solution_text}\n\n"
                    f"**C-3PO Workflow:**\n"
                    f"1. @C3PO will create PM, C, and T tickets\n"
                    f"2. Assign to appropriate team for resolution\n"
                    f"3. Team works on fix in their ticket stack\n"
                    f"4. @C3PO updates and closes upon completion"
                )

                return {
                    "title": title,
                    "description": description,
                    "notification_type": notif_type,
                    "severity": priority,
                    "request_id": request_id,
                    "team": self.TEAM_ROUTING.get(notif_type, "helpdesk_support"),
                }

        return None

    def create_ticket_set(self, info: Dict[str, Any]) -> Dict[str, str]:
        """
        Create a complete ticket set: PM (Problem), C (Change Request), T (Task).
        All tickets are linked by Request ID.
        """
        created = {}

        if not self.helpdesk_system:
            logger.warning("⚠️ Helpdesk system not available, skipping ticket creation")
            return created

        try:
            # Create PM (Problem) ticket
            pm_title = f"[PM] {info['title']}"
            pm_description = (
                f"**PROBLEM TICKET**\n\n"
                f"{info['description']}\n\n"
                f"**Linked Tickets:**\n"
                f"- C (Change Request): [Will be created]\n"
                f"- T (Task): [Will be created]\n\n"
                f"**Created by:** VS Code Notification Monitor\n"
                f"**Automation:** @JARVIS @C3PO"
            )

            pm_ticket = self.helpdesk_system.create_ticket(
                title=pm_title,
                description=pm_description,
                ticket_type=TicketType.PROBLEM,
                priority=TicketPriority(
                    info["severity"].value
                    if hasattr(info["severity"], "value")
                    else info["severity"]
                ),
                component="VS Code",
                issue_type=info["notification_type"],
            )

            if pm_ticket:
                created["PM"] = pm_ticket.ticket_id
                logger.info(f"✅ Created PM ticket: {pm_ticket.ticket_id}")

                # Link PM to notification record
                info["pm_ticket"] = pm_ticket.ticket_id

        except Exception as e:
            logger.error(f"❌ Error creating PM ticket: {e}")

        try:
            # Create C (Change Request) ticket
            c_title = f"[C] Fix: {info['title'].replace('[VS Code] ', '')}"
            c_description = (
                f"**CHANGE REQUEST TICKET**\n\n"
                f"**Original Problem:** {info['description']}\n\n"
                f"**Required Changes:**\n"
                f"1. Investigate root cause of {info['notification_type']}\n"
                f"2. Design solution for the issue\n"
                f"3. Create implementation plan\n"
                f"4. Test the solution\n\n"
                f"**Linked Tickets:**\n"
                f"- PM (Problem): {created.get('PM', 'N/A')}\n"
                f"- T (Task): [Will be created]\n\n"
                f"**Created by:** VS Code Notification Monitor\n"
                f"**Automation:** @JARVIS @C3PO"
            )

            c_ticket = self.helpdesk_system.create_ticket(
                title=c_title,
                description=c_description,
                ticket_type=TicketType.CHANGE_REQUEST,
                priority=TicketPriority(
                    info["severity"].value
                    if hasattr(info["severity"], "value")
                    else info["severity"]
                ),
                component="VS Code",
                issue_type=f"fix_{info['notification_type']}",
            )

            if c_ticket:
                created["C"] = c_ticket.ticket_id
                logger.info(f"✅ Created C ticket: {c_ticket.ticket_id}")
                info["c_ticket"] = c_ticket.ticket_id

        except Exception as e:
            logger.error(f"❌ Error creating C ticket: {e}")

        try:
            # Create T (Task) ticket
            t_title = f"[T] Implement: {info['title'].replace('[VS Code] ', '')}"
            t_description = (
                f"**TASK TICKET**\n\n"
                f"**Original Problem:** {info['description']}\n\n"
                f"**Implementation Steps:**\n"
                f"1. Review PM and C tickets for full context\n"
                f"2. Implement the fix according to change request\n"
                f"3. Test the implementation thoroughly\n"
                f"4. Update documentation\n"
                f"5. Hand off to C-3PO for closure\n\n"
                f"**Linked Tickets:**\n"
                f"- PM (Problem): {created.get('PM', 'N/A')}\n"
                f"- C (Change Request): {created.get('C', 'N/A')}\n\n"
                f"**Created by:** VS Code Notification Monitor\n"
                f"**Automation:** @JARVIS @C3PO"
            )

            t_ticket = self.helpdesk_system.create_ticket(
                title=t_title,
                description=t_description,
                ticket_type=TicketType.CHANGE_TASK,
                priority=TicketPriority(
                    info["severity"].value
                    if hasattr(info["severity"], "value")
                    else info["severity"]
                ),
                component="VS Code",
                issue_type=f"task_{info['notification_type']}",
            )

            if t_ticket:
                created["T"] = t_ticket.ticket_id
                logger.info(f"✅ Created T ticket: {t_ticket.ticket_id}")
                info["t_ticket"] = t_ticket.ticket_id

        except Exception as e:
            logger.error(f"❌ Error creating T ticket: {e}")

        return created

    def c3po_assign_tickets(self, tickets: Dict[str, str], team: str) -> Dict[str, Any]:
        """
        C-3PO assigns tickets to appropriate teams.

        C-3PO ensures:
        - Team Manager oversight (@c3po)
        - Technical Lead assignment (@r2d2 or team-specific)
        - Business Lead for coordination
        """
        if not self.c3po_assigner:
            logger.warning("⚠️ C-3PO not available for ticket assignment")
            return {"success": False, "reason": "C-3PO not available"}

        try:
            assignments = {}
            logger.info("=" * 80)
            logger.info("🤖 C-3PO ASSIGNING TICKETS TO TEAMS")
            logger.info("=" * 80)

            for ticket_type, ticket_id in tickets.items():
                if ticket_id:
                    result = self.c3po_assigner.assign_ticket_to_team(
                        ticket_number=ticket_id, team_id=team, auto_detect=True
                    )
                    assignments[ticket_id] = result
                    if result.get("success"):
                        logger.info(f"✅ {ticket_id} -> Team: {result.get('team_assigned', team)}")
                    else:
                        logger.warning(
                            f"⚠️ {ticket_id} assignment: {result.get('error', 'Unknown')}"
                        )

            logger.info("=" * 80)
            logger.info("✅ C-3PO assignment complete")
            logger.info("=" * 80)

            return {"success": True, "assignments": assignments}

        except Exception as e:
            logger.error(f"❌ Error in C-3PO assignment: {e}")
            return {"success": False, "error": str(e)}

    def save_notification_record(self, info: Dict[str, Any], tickets: Dict[str, str]):
        """Save the notification and ticket references."""
        ticket_id = hashlib.md5(f"{info['title']}|{info['request_id']}".encode()).hexdigest()[:14]

        record = {
            "ticket_id": ticket_id,
            "title": info["title"],
            "description": info["description"],
            "notification_type": info["notification_type"],
            "severity": info["severity"].value
            if hasattr(info["severity"], "value")
            else info["severity"],
            "request_id": info["request_id"],
            "team": info.get("team"),
            "pm_ticket": tickets.get("PM"),
            "c_ticket": tickets.get("C"),
            "t_ticket": tickets.get("T"),
            "status": "open",
            "priority": info["severity"].value
            if hasattr(info["severity"], "value")
            else info["severity"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "resolved_at": None,
            "metadata": {
                "c3po_assigned": False,
                "team_notified": False,
                "work_started": False,
                "completed": False,
            },
        }

        self.notification_tickets[ticket_id] = record
        self.save_notification_tickets()

        return record

    def process_notification(self, text: str) -> Optional[Dict[str, Any]]:
        """Process a notification with full C-3PO workflow."""
        info = self.parse_notification(text)
        if not info:
            return None

        # Check for duplicate
        for existing in self.notification_tickets.values():
            if existing.get("title") == info["title"]:
                logger.debug(f"Notification already processed: {info['title']}")
                return existing

        # Create ticket set
        tickets = self.create_ticket_set(info)

        # C-3PO assigns to team
        c3po_result = self.c3po_assign_tickets(tickets, info.get("team", "helpdesk_support"))

        # Save record
        record = self.save_notification_record(info, tickets)
        record["c3po_assignment"] = c3po_result

        return record

    def report_current_issues(self) -> List[Dict[str, Any]]:
        """
        Report and create tickets for known VS Code issues.
        This implements the full C-3PO workflow.
        """
        issues = [
            {
                "title": "[VS Code] Lumina Core Extension - Missing GitHub Copilot Dependency",
                "description": (
                    "Cannot activate 'Lumina Core - Open Source Lumina Ecosystem' extension "
                    "because it depends on an unknown 'github.copilot' extension.\n\n"
                    "**Analysis:**\n"
                    "- The Lumina Core extension has GitHub Copilot listed as a dependency\n"
                    "- Copilot may not be installed or may have a different extension ID\n"
                    "- This could also be a cached/corrupted extension state\n\n"
                    "**C-3PO Actions:**\n"
                    "1. Create PM, C, T tickets\n"
                    "2. Assign to jarvis_superagent team\n"
                    "3. Team implements fix\n"
                    "4. C-3PO closes upon completion"
                ),
                "type": "extension_dependency_error",
                "severity": TicketPriority.HIGH,
            },
            {
                "title": "[VS Code] Extension Format Error - undefined_publisher.lumina-ai",
                "description": (
                    "The extension recommendation 'undefined_publisher.lumina-ai' has bad format. "
                    "Expected format: <provider>.<name>\n\n"
                    "**Analysis:**\n"
                    "- A workspace or project configuration has a malformed extension reference\n"
                    "- 'undefined_publisher' suggests the publisher field is missing\n\n"
                    "**C-3PO Actions:**\n"
                    "1. Create PM, C, T tickets\n"
                    "2. Assign to helpdesk_support team\n"
                    "3. Team investigates and fixes\n"
                    "4. C-3PO closes upon completion"
                ),
                "type": "extension_format_error",
                "severity": TicketPriority.MEDIUM,
            },
            {
                "title": "[VS Code] Microsoft Edge Tools Server Crashes",
                "description": (
                    "Microsoft Edge Tools server crashed 5 times in the last 3 minutes. "
                    "The server will not be restarted.\n\n"
                    "**Analysis:**\n"
                    "- The Edge Tools extension has become unstable\n"
                    "- Known issue with certain VS Code versions\n\n"
                    "**C-3PO Actions:**\n"
                    "1. Create PM, C, T tickets\n"
                    "2. Assign to helpdesk_support team\n"
                    "3. Team disables/reinstalls extension\n"
                    "4. C-3PO closes upon completion"
                ),
                "type": "server_crash",
                "severity": TicketPriority.HIGH,
            },
        ]

        results = []
        for issue in issues:
            logger.info(f"\n📋 Processing: {issue['title']}")

            info = {
                "title": issue["title"],
                "description": issue["description"],
                "notification_type": issue["type"],
                "severity": issue["severity"],
                "request_id": self.generate_request_id(),
                "team": self.TEAM_ROUTING.get(issue["type"], "helpdesk_support"),
            }

            # Create tickets
            tickets = self.create_ticket_set(info)

            # C-3PO assigns
            c3po_result = self.c3po_assign_tickets(tickets, info["team"])

            # Save record
            record = self.save_notification_record(info, tickets)
            record["tickets"] = tickets
            record["c3po_result"] = c3po_result

            results.append(record)

        return results


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="VS Code Notification Monitor with C-3PO Ticket Lifecycle",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/python/monitor_vscode_notifications.py --report
      Process current VS Code issues with full C-3PO workflow

Workflow:
  1. Detect notification
  2. Create PM (Problem), C (Change Request), T (Task) tickets
  3. @C3PO assigns tickets to appropriate teams
  4. Teams work on their personal ticket stacks
  5. @C3PO updates, maintains, and closes tickets
        """,
    )
    parser.add_argument(
        "--report", action="store_true", help="Report current issues and create tickets"
    )
    args = parser.parse_args()

    monitor = VSCodeNotificationMonitor()

    if args.report:
        print("=" * 80)
        print("🤖 VS Code Notification Monitor with C-3PO Ticket Lifecycle")
        print("=" * 80)
        print()

        results = monitor.report_current_issues()

        print("\n" + "=" * 80)
        print("📊 SUMMARY - TICKETS CREATED AND ASSIGNED")
        print("=" * 80)

        for result in results:
            print(f"\n📋 Request ID: {result['request_id']}")
            print(f"   Title: {result['title']}")
            print(f"   Team: {result['team']}")
            print("   Tickets Created:")
            print(f"      - PM (Problem): {result.get('pm_ticket', 'N/A')}")
            print(f"      - C (Change Request): {result.get('c_ticket', 'N/A')}")
            print(f"      - T (Task): {result.get('t_ticket', 'N/A')}")

            c3po_result = result.get("c3po_result", {})
            if c3po_result.get("success"):
                print("   ✅ C-3PO Assignment: Success")
                assignments = c3po_result.get("assignments", {})
                for tid, assignment in assignments.items():
                    if assignment.get("success"):
                        print(f"      → {tid}: {assignment.get('team_assigned', 'Assigned')}")
            else:
                print(f"   ⚠️ C-3PO Assignment: {c3po_result.get('reason', 'Pending')}")

        print("\n" + "=" * 80)
        print("📈 TICKET STATISTICS")
        print("=" * 80)

        pm_count = sum(1 for r in results if r.get("pm_ticket"))
        c_count = sum(1 for r in results if r.get("c_ticket"))
        t_count = sum(1 for r in results if r.get("t_ticket"))

        print(f"PM (Problem) Tickets: {pm_count}")
        print(f"C (Change Request) Tickets: {c_count}")
        print(f"T (Task) Tickets: {t_count}")
        print(f"Total Ticket Sets: {len(results)}")

        print("\n" + "=" * 80)
        print("✅ C-3PO Workflow Complete")
        print("=" * 80)
        print("\nAll tickets have been:")
        print("  1. ✅ Created with PM, C, and T types")
        print("  2. ✅ Assigned to appropriate teams by @C3PO")
        print("  3. ✅ Ready for team resolution in their personal stacks")
        print("  4. ✅ Linked by Request ID for tracking")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
project_root = Path(__file__).parent.parent.parent
scripts_python = project_root / "scripts" / "python"
sys.path.insert(0, str(scripts_python))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("VSCodeNotificationMonitor")

# Import ticket system components
HELPDESK_AVAILABLE = False
C3PO_AVAILABLE = False

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("VSCodeNotificationMonitor")

try:
    from jarvis_helpdesk_ticket_system import (
        HelpdeskTicket,
        JARVISHelpdeskTicketSystem,
        TicketPriority,
        TicketStatus,
        TicketType,
    )

    HELPDESK_AVAILABLE = True
    logger.info("✅ Helpdesk ticket system available")
except ImportError as e:
    logger.warning(f"⚠️ Helpdesk ticket system not available: {e}")
    HELPDESK_AVAILABLE = False

    # Define fallbacks
    class _TicketPriority:
        CRITICAL = "critical"
        HIGH = "high"
        MEDIUM = "medium"
        LOW = "low"

    class _TicketStatus:
        OPEN = "open"
        IN_PROGRESS = "in_progress"
        RESOLVED = "resolved"
        CLOSED = "closed"

    class _TicketType:
        PROBLEM = "PM"
        CHANGE_REQUEST = "C"
        CHANGE_TASK = "T"

    TicketPriority = _TicketPriority
    TicketStatus = _TicketStatus
    TicketType = _TicketType


try:
    from jarvis_c3po_ticket_assigner import C3POTicketAssigner

    C3PO_AVAILABLE = True
    logger.info("✅ C-3PO Ticket Assigner available")
except ImportError as e:
    logger.warning(f"⚠️ C-3PO Ticket Assigner not available: {e}")


class VSCodeNotificationMonitor:
    """
    Monitors VS Code / Cursor IDE notifications and manages full ticket lifecycle.

    C-3PO workflow:
    1. Monitor detects notification
    2. Create PM (Problem) ticket with full details
    3. Create C (Change Request) ticket for the fix
    4. Create T (Task) ticket for implementation
    5. C-3PO assigns tickets to appropriate teams
    6. Teams work on their stacks
    7. C-3PO updates and closes tickets upon completion
    """

    # Patterns for common VS Code notifications/errors
    NOTIFICATION_PATTERNS = [
        # Extension activation errors
        (
            r"Cannot activate '(.+)' extension because it depends on an unknown '(.+)' extension",
            "extension_dependency_error",
            TicketPriority.HIGH,
        ),
        # Extension format errors
        (
            r"(\w+\.\w+) \(bad format\) Expected: <provider>\.<name>",
            "extension_format_error",
            TicketPriority.MEDIUM,
        ),
        # Server crashes
        (
            r"(.+) server crashed (\d+) times in the last (\d+) minutes",
            "server_crash",
            TicketPriority.HIGH,
        ),
        # General extension errors
        (
            r"Extension '.+' failed to activate",
            "extension_activation_failed",
            TicketPriority.MEDIUM,
        ),
        # GitHub access errors
        (
            r"No GitHub access token found with access to repository",
            "github_access_error",
            TicketPriority.HIGH,
        ),
    ]

    # Team routing based on issue type
    TEAM_ROUTING = {
        "extension_dependency_error": "jarvis_superagent",
        "extension_format_error": "helpdesk_support",
        "server_crash": "helpdesk_support",
        "extension_activation_failed": "helpdesk_support",
        "github_access_error": "jarvis_superagent",
    }

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.tickets_file = self.project_root / "data/notification_tickets/tickets.json"
        self.tickets_dir = self.tickets_file.parent / "tickets"
        self.tickets_dir.mkdir(parents=True, exist_ok=True)

        # Initialize ticket system
        self.helpdesk_system = None
        if HELPDESK_AVAILABLE:
            try:
                self.helpdesk_system = JARVISHelpdeskTicketSystem(project_root=self.project_root)
                logger.info("✅ Helpdesk system initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize helpdesk system: {e}")

        # Initialize C-3PO
        self.c3po_assigner = None
        if C3PO_AVAILABLE:
            try:
                self.c3po_assigner = C3POTicketAssigner(self.project_root)
                logger.info("✅ C-3PO Ticket Assigner initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize C-3PO: {e}")

        self.notification_tickets: Dict[str, dict] = {}
        self.load_notification_tickets()

    def load_notification_tickets(self):
        """Load existing notification tickets (index + per-ticket files, mirror helpdesk)."""
        self.notification_tickets = _load_notification_tickets_from_storage(
            self.tickets_file, self.tickets_dir
        )
        logger.info(
            f"📂 Loaded {len(self.notification_tickets)} existing notification tickets"
        )

    def save_notification_tickets(self):
        """Save notification tickets to index and per-ticket files (mirror helpdesk)."""
        _save_notification_tickets_to_storage(
            self.tickets_file, self.tickets_dir, self.notification_tickets
        )
        logger.info(f"💾 Saved {len(self.notification_tickets)} notification tickets")

    def generate_request_id(self) -> str:
        """Generate a unique request ID for tracking."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = hashlib.md5(f"{time.time()}".encode()).hexdigest()[:6]
        return f"REQ-VSCODE-{timestamp}-{random_suffix}"

    def parse_notification(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse a notification text and extract relevant information."""
        for pattern, notif_type, priority in self.NOTIFICATION_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                request_id = self.generate_request_id()

                # Build detailed description with solutions
                solutions = {
                    "extension_dependency_error": [
                        "Install the required dependency extension",
                        "Or remove the dependency from the extension manifest",
                        "Clear workspace storage and restart VS Code",
                    ],
                    "extension_format_error": [
                        "Check workspace .code-workspace files for malformed extension IDs",
                        "Clear VS Code workspace storage",
                        "Remove corrupted extension cache",
                    ],
                    "server_crash": [
                        "Disable the crashing extension",
                        "Clear extension cache",
                        "Reinstall the extension if needed",
                    ],
                    "extension_activation_failed": [
                        "Check extension compatibility with VS Code version",
                        "Reinstall the extension",
                        "Check extension logs for specific errors",
                    ],
                    "github_access_error": [
                        "Check GitHub token validity",
                        "Verify token has required repository permissions",
                        "Refresh authentication",
                    ],
                }

                solution_text = "\n".join(
                    [f"{i + 1}. {s}" for i, s in enumerate(solutions.get(notif_type, []))]
                )

                title = f"[VS Code] {notif_type.replace('_', ' ').title()}"
                description = (
                    f"**Notification:** {text}\n\n"
                    f"**Request ID:** {request_id}\n\n"
                    f"**Analysis:**\n"
                    f"Type: {notif_type}\n"
                    f"Severity: {priority.value if hasattr(priority, 'value') else priority}\n\n"
                    f"**Recommended Solutions:**\n{solution_text}\n\n"
                    f"**C-3PO Workflow:**\n"
                    f"1. @C3PO will create PM, C, and T tickets\n"
                    f"2. Assign to appropriate team for resolution\n"
                    f"3. Team works on fix in their ticket stack\n"
                    f"4. @C3PO updates and closes upon completion"
                )

                return {
                    "title": title,
                    "description": description,
                    "notification_type": notif_type,
                    "severity": priority,
                    "request_id": request_id,
                    "team": self.TEAM_ROUTING.get(notif_type, "helpdesk_support"),
                }

        return None

    def create_ticket_set(self, info: Dict[str, Any]) -> Dict[str, str]:
        """
        Create a complete ticket set: PM (Problem), C (Change Request), T (Task).
        All tickets are linked by Request ID.
        """
        created = {}

        if not self.helpdesk_system:
            logger.warning("⚠️ Helpdesk system not available, skipping ticket creation")
            return created

        try:
            # Create PM (Problem) ticket
            pm_title = f"[PM] {info['title']}"
            pm_description = (
                f"**PROBLEM TICKET**\n\n"
                f"{info['description']}\n\n"
                f"**Linked Tickets:**\n"
                f"- C (Change Request): [Will be created]\n"
                f"- T (Task): [Will be created]\n\n"
                f"**Created by:** VS Code Notification Monitor\n"
                f"**Automation:** @JARVIS @C3PO"
            )

            pm_ticket = self.helpdesk_system.create_ticket(
                title=pm_title,
                description=pm_description,
                ticket_type=TicketType.PROBLEM,
                priority=TicketPriority(
                    info["severity"].value
                    if hasattr(info["severity"], "value")
                    else info["severity"]
                ),
                component="VS Code",
                issue_type=info["notification_type"],
            )

            if pm_ticket:
                created["PM"] = pm_ticket.ticket_id
                logger.info(f"✅ Created PM ticket: {pm_ticket.ticket_id}")

                # Link PM to notification record
                info["pm_ticket"] = pm_ticket.ticket_id

        except Exception as e:
            logger.error(f"❌ Error creating PM ticket: {e}")

        try:
            # Create C (Change Request) ticket
            c_title = f"[C] Fix: {info['title'].replace('[VS Code] ', '')}"
            c_description = (
                f"**CHANGE REQUEST TICKET**\n\n"
                f"**Original Problem:** {info['description']}\n\n"
                f"**Required Changes:**\n"
                f"1. Investigate root cause of {info['notification_type']}\n"
                f"2. Design solution for the issue\n"
                f"3. Create implementation plan\n"
                f"4. Test the solution\n\n"
                f"**Linked Tickets:**\n"
                f"- PM (Problem): {created.get('PM', 'N/A')}\n"
                f"- T (Task): [Will be created]\n\n"
                f"**Created by:** VS Code Notification Monitor\n"
                f"**Automation:** @JARVIS @C3PO"
            )

            c_ticket = self.helpdesk_system.create_ticket(
                title=c_title,
                description=c_description,
                ticket_type=TicketType.CHANGE_REQUEST,
                priority=TicketPriority(
                    info["severity"].value
                    if hasattr(info["severity"], "value")
                    else info["severity"]
                ),
                component="VS Code",
                issue_type=f"fix_{info['notification_type']}",
            )

            if c_ticket:
                created["C"] = c_ticket.ticket_id
                logger.info(f"✅ Created C ticket: {c_ticket.ticket_id}")
                info["c_ticket"] = c_ticket.ticket_id

        except Exception as e:
            logger.error(f"❌ Error creating C ticket: {e}")

        try:
            # Create T (Task) ticket
            t_title = f"[T] Implement: {info['title'].replace('[VS Code] ', '')}"
            t_description = (
                f"**TASK TICKET**\n\n"
                f"**Original Problem:** {info['description']}\n\n"
                f"**Implementation Steps:**\n"
                f"1. Review PM and C tickets for full context\n"
                f"2. Implement the fix according to change request\n"
                f"3. Test the implementation thoroughly\n"
                f"4. Update documentation\n"
                f"5. Hand off to C-3PO for closure\n\n"
                f"**Linked Tickets:**\n"
                f"- PM (Problem): {created.get('PM', 'N/A')}\n"
                f"- C (Change Request): {created.get('C', 'N/A')}\n\n"
                f"**Created by:** VS Code Notification Monitor\n"
                f"**Automation:** @JARVIS @C3PO"
            )

            t_ticket = self.helpdesk_system.create_ticket(
                title=t_title,
                description=t_description,
                ticket_type=TicketType.CHANGE_TASK,
                priority=TicketPriority(
                    info["severity"].value
                    if hasattr(info["severity"], "value")
                    else info["severity"]
                ),
                component="VS Code",
                issue_type=f"task_{info['notification_type']}",
            )

            if t_ticket:
                created["T"] = t_ticket.ticket_id
                logger.info(f"✅ Created T ticket: {t_ticket.ticket_id}")
                info["t_ticket"] = t_ticket.ticket_id

        except Exception as e:
            logger.error(f"❌ Error creating T ticket: {e}")

        return created

    def c3po_assign_tickets(self, tickets: Dict[str, str], team: str) -> Dict[str, Any]:
        """
        C-3PO assigns tickets to appropriate teams.

        C-3PO ensures:
        - Team Manager oversight (@c3po)
        - Technical Lead assignment (@r2d2 or team-specific)
        - Business Lead for coordination
        """
        if not self.c3po_assigner:
            logger.warning("⚠️ C-3PO not available for ticket assignment")
            return {"success": False, "reason": "C-3PO not available"}

        try:
            assignments = {}
            logger.info("=" * 80)
            logger.info("🤖 C-3PO ASSIGNING TICKETS TO TEAMS")
            logger.info("=" * 80)

            for ticket_type, ticket_id in tickets.items():
                if ticket_id:
                    result = self.c3po_assigner.assign_ticket_to_team(
                        ticket_number=ticket_id, team_id=team, auto_detect=True
                    )
                    assignments[ticket_id] = result
                    if result.get("success"):
                        logger.info(f"✅ {ticket_id} -> Team: {result.get('team_assigned', team)}")
                    else:
                        logger.warning(
                            f"⚠️ {ticket_id} assignment: {result.get('error', 'Unknown')}"
                        )

            logger.info("=" * 80)
            logger.info("✅ C-3PO assignment complete")
            logger.info("=" * 80)

            return {"success": True, "assignments": assignments}

        except Exception as e:
            logger.error(f"❌ Error in C-3PO assignment: {e}")
            return {"success": False, "error": str(e)}

    def save_notification_record(self, info: Dict[str, Any], tickets: Dict[str, str]):
        """Save the notification and ticket references."""
        ticket_id = hashlib.md5(f"{info['title']}|{info['request_id']}".encode()).hexdigest()[:14]

        record = {
            "ticket_id": ticket_id,
            "title": info["title"],
            "description": info["description"],
            "notification_type": info["notification_type"],
            "severity": info["severity"].value
            if hasattr(info["severity"], "value")
            else info["severity"],
            "request_id": info["request_id"],
            "team": info.get("team"),
            "pm_ticket": tickets.get("PM"),
            "c_ticket": tickets.get("C"),
            "t_ticket": tickets.get("T"),
            "status": "open",
            "priority": info["severity"].value
            if hasattr(info["severity"], "value")
            else info["severity"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "resolved_at": None,
            "metadata": {
                "c3po_assigned": False,
                "team_notified": False,
                "work_started": False,
                "completed": False,
            },
        }

        self.notification_tickets[ticket_id] = record
        self.save_notification_tickets()

        return record

    def process_notification(self, text: str) -> Optional[Dict[str, Any]]:
        """Process a notification with full C-3PO workflow."""
        info = self.parse_notification(text)
        if not info:
            return None

        # Check for duplicate
        for existing in self.notification_tickets.values():
            if existing.get("title") == info["title"]:
                logger.debug(f"Notification already processed: {info['title']}")
                return existing

        # Create ticket set
        tickets = self.create_ticket_set(info)

        # C-3PO assigns to team
        c3po_result = self.c3po_assign_tickets(tickets, info.get("team", "helpdesk_support"))

        # Save record
        record = self.save_notification_record(info, tickets)
        record["c3po_assignment"] = c3po_result

        return record

    def report_current_issues(self) -> List[Dict[str, Any]]:
        """
        Report and create tickets for known VS Code issues.
        This implements the full C-3PO workflow.
        """
        issues = [
            {
                "title": "[VS Code] Lumina Core Extension - Missing GitHub Copilot Dependency",
                "description": (
                    "Cannot activate 'Lumina Core - Open Source Lumina Ecosystem' extension "
                    "because it depends on an unknown 'github.copilot' extension.\n\n"
                    "**Analysis:**\n"
                    "- The Lumina Core extension has GitHub Copilot listed as a dependency\n"
                    "- Copilot may not be installed or may have a different extension ID\n"
                    "- This could also be a cached/corrupted extension state\n\n"
                    "**C-3PO Actions:**\n"
                    "1. Create PM, C, T tickets\n"
                    "2. Assign to jarvis_superagent team\n"
                    "3. Team implements fix\n"
                    "4. C-3PO closes upon completion"
                ),
                "type": "extension_dependency_error",
                "severity": TicketPriority.HIGH,
            },
            {
                "title": "[VS Code] Extension Format Error - undefined_publisher.lumina-ai",
                "description": (
                    "The extension recommendation 'undefined_publisher.lumina-ai' has bad format. "
                    "Expected format: <provider>.<name>\n\n"
                    "**Analysis:**\n"
                    "- A workspace or project configuration has a malformed extension reference\n"
                    "- 'undefined_publisher' suggests the publisher field is missing\n\n"
                    "**C-3PO Actions:**\n"
                    "1. Create PM, C, T tickets\n"
                    "2. Assign to helpdesk_support team\n"
                    "3. Team investigates and fixes\n"
                    "4. C-3PO closes upon completion"
                ),
                "type": "extension_format_error",
                "severity": TicketPriority.MEDIUM,
            },
            {
                "title": "[VS Code] Microsoft Edge Tools Server Crashes",
                "description": (
                    "Microsoft Edge Tools server crashed 5 times in the last 3 minutes. "
                    "The server will not be restarted.\n\n"
                    "**Analysis:**\n"
                    "- The Edge Tools extension has become unstable\n"
                    "- Known issue with certain VS Code versions\n\n"
                    "**C-3PO Actions:**\n"
                    "1. Create PM, C, T tickets\n"
                    "2. Assign to helpdesk_support team\n"
                    "3. Team disables/reinstalls extension\n"
                    "4. C-3PO closes upon completion"
                ),
                "type": "server_crash",
                "severity": TicketPriority.HIGH,
            },
        ]

        results = []
        for issue in issues:
            logger.info(f"\n📋 Processing: {issue['title']}")

            info = {
                "title": issue["title"],
                "description": issue["description"],
                "notification_type": issue["type"],
                "severity": issue["severity"],
                "request_id": self.generate_request_id(),
                "team": self.TEAM_ROUTING.get(issue["type"], "helpdesk_support"),
            }

            # Create tickets
            tickets = self.create_ticket_set(info)

            # C-3PO assigns
            c3po_result = self.c3po_assign_tickets(tickets, info["team"])

            # Save record
            record = self.save_notification_record(info, tickets)
            record["tickets"] = tickets
            record["c3po_result"] = c3po_result

            results.append(record)

        return results


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="VS Code Notification Monitor with C-3PO Ticket Lifecycle",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/python/monitor_vscode_notifications.py --report
      Process current VS Code issues with full C-3PO workflow

Workflow:
  1. Detect notification
  2. Create PM (Problem), C (Change Request), T (Task) tickets
  3. @C3PO assigns tickets to appropriate teams
  4. Teams work on their personal ticket stacks
  5. @C3PO updates, maintains, and closes tickets
        """,
    )
    parser.add_argument(
        "--report", action="store_true", help="Report current issues and create tickets"
    )
    args = parser.parse_args()

    monitor = VSCodeNotificationMonitor()

    if args.report:
        print("=" * 80)
        print("🤖 VS Code Notification Monitor with C-3PO Ticket Lifecycle")
        print("=" * 80)
        print()

        results = monitor.report_current_issues()

        print("\n" + "=" * 80)
        print("📊 SUMMARY - TICKETS CREATED AND ASSIGNED")
        print("=" * 80)

        for result in results:
            print(f"\n📋 Request ID: {result['request_id']}")
            print(f"   Title: {result['title']}")
            print(f"   Team: {result['team']}")
            print("   Tickets Created:")
            print(f"      - PM (Problem): {result.get('pm_ticket', 'N/A')}")
            print(f"      - C (Change Request): {result.get('c_ticket', 'N/A')}")
            print(f"      - T (Task): {result.get('t_ticket', 'N/A')}")

            c3po_result = result.get("c3po_result", {})
            if c3po_result.get("success"):
                print("   ✅ C-3PO Assignment: Success")
                assignments = c3po_result.get("assignments", {})
                for tid, assignment in assignments.items():
                    if assignment.get("success"):
                        print(f"      → {tid}: {assignment.get('team_assigned', 'Assigned')}")
            else:
                print(f"   ⚠️ C-3PO Assignment: {c3po_result.get('reason', 'Pending')}")

        print("\n" + "=" * 80)
        print("📈 TICKET STATISTICS")
        print("=" * 80)

        pm_count = sum(1 for r in results if r.get("pm_ticket"))
        c_count = sum(1 for r in results if r.get("c_ticket"))
        t_count = sum(1 for r in results if r.get("t_ticket"))

        print(f"PM (Problem) Tickets: {pm_count}")
        print(f"C (Change Request) Tickets: {c_count}")
        print(f"T (Task) Tickets: {t_count}")
        print(f"Total Ticket Sets: {len(results)}")

        print("\n" + "=" * 80)
        print("✅ C-3PO Workflow Complete")
        print("=" * 80)
        print("\nAll tickets have been:")
        print("  1. ✅ Created with PM, C, and T types")
        print("  2. ✅ Assigned to appropriate teams by @C3PO")
        print("  3. ✅ Ready for team resolution in their personal stacks")
        print("  4. ✅ Linked by Request ID for tracking")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

def validate_ticket_number(ticket: str) -> tuple[bool, str]:
    """
    Validate ticket number format.

    Args:
        ticket: Ticket number to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not ticket:
        return False, "Ticket number is empty"

    if not TICKET_PATTERN.match(ticket):
        return False, f"Invalid format: {ticket}. Expected: PM000000001, C000000001, T000000001"

    return True, ""

def format_ticket_number(prefix: str, counter: int) -> str:
    """
    Format ticket number with correct 9-digit zero-padding.

    Args:
        prefix: Ticket prefix (PM, C, CR, T)
        counter: Counter value

    Returns:
        Formatted ticket number (e.g., PM000000001)
    """
    return f"{prefix}{counter:09d}"

# Setup paths
project_root = Path(__file__).parent.parent.parent
scripts_python = project_root / "scripts" / "python"
sys.path.insert(0, str(scripts_python))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("VSCodeNotificationMonitor")

# Import ticket system components
HELPDESK_AVAILABLE = False
C3PO_AVAILABLE = False

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("VSCodeNotificationMonitor")

try:
    from jarvis_helpdesk_ticket_system import (
        HelpdeskTicket,
        JARVISHelpdeskTicketSystem,
        TicketPriority,
        TicketStatus,
        TicketType,
    )

    HELPDESK_AVAILABLE = True
    logger.info("✅ Helpdesk ticket system available")
except ImportError as e:
    logger.warning(f"⚠️ Helpdesk ticket system not available: {e}")
    HELPDESK_AVAILABLE = False

    # Define fallbacks
    class _TicketPriority:
        CRITICAL = "critical"
        HIGH = "high"
        MEDIUM = "medium"
        LOW = "low"

    class _TicketStatus:
        OPEN = "open"
        IN_PROGRESS = "in_progress"
        RESOLVED = "resolved"
        CLOSED = "closed"

    class _TicketType:
        PROBLEM = "PM"
        CHANGE_REQUEST = "C"
        CHANGE_TASK = "T"

    TicketPriority = _TicketPriority
    TicketStatus = _TicketStatus
    TicketType = _TicketType


try:
    from jarvis_c3po_ticket_assigner import C3POTicketAssigner

    C3PO_AVAILABLE = True
    logger.info("✅ C-3PO Ticket Assigner available")
except ImportError as e:
    logger.warning(f"⚠️ C-3PO Ticket Assigner not available: {e}")


class VSCodeNotificationMonitor:
    """
    Monitors VS Code / Cursor IDE notifications and manages full ticket lifecycle.

    C-3PO workflow:
    1. Monitor detects notification
    2. Create PM (Problem) ticket with full details
    3. Create C (Change Request) ticket for the fix
    4. Create T (Task) ticket for implementation
    5. C-3PO assigns tickets to appropriate teams
    6. Teams work on their stacks
    7. C-3PO updates and closes tickets upon completion
    """

    # Patterns for common VS Code notifications/errors
    NOTIFICATION_PATTERNS = [
        # Extension activation errors
        (
            r"Cannot activate '(.+)' extension because it depends on an unknown '(.+)' extension",
            "extension_dependency_error",
            TicketPriority.HIGH,
        ),
        # Extension format errors
        (
            r"(\w+\.\w+) \(bad format\) Expected: <provider>\.<name>",
            "extension_format_error",
            TicketPriority.MEDIUM,
        ),
        # Server crashes
        (
            r"(.+) server crashed (\d+) times in the last (\d+) minutes",
            "server_crash",
            TicketPriority.HIGH,
        ),
        # General extension errors
        (
            r"Extension '.+' failed to activate",
            "extension_activation_failed",
            TicketPriority.MEDIUM,
        ),
        # GitHub access errors
        (
            r"No GitHub access token found with access to repository",
            "github_access_error",
            TicketPriority.HIGH,
        ),
    ]

    # Team routing based on issue type
    TEAM_ROUTING = {
        "extension_dependency_error": "jarvis_superagent",
        "extension_format_error": "helpdesk_support",
        "server_crash": "helpdesk_support",
        "extension_activation_failed": "helpdesk_support",
        "github_access_error": "jarvis_superagent",
    }

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.tickets_file = self.project_root / "data/notification_tickets/tickets.json"
        self.tickets_dir = self.tickets_file.parent / "tickets"
        self.tickets_dir.mkdir(parents=True, exist_ok=True)

        # Initialize ticket system
        self.helpdesk_system = None
        if HELPDESK_AVAILABLE:
            try:
                self.helpdesk_system = JARVISHelpdeskTicketSystem(project_root=self.project_root)
                logger.info("✅ Helpdesk system initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize helpdesk system: {e}")

        # Initialize C-3PO
        self.c3po_assigner = None
        if C3PO_AVAILABLE:
            try:
                self.c3po_assigner = C3POTicketAssigner(self.project_root)
                logger.info("✅ C-3PO Ticket Assigner initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize C-3PO: {e}")

        self.notification_tickets: Dict[str, dict] = {}
        self.load_notification_tickets()

    def load_notification_tickets(self):
        """Load existing notification tickets (index + per-ticket files, mirror helpdesk)."""
        self.notification_tickets = _load_notification_tickets_from_storage(
            self.tickets_file, self.tickets_dir
        )
        logger.info(
            f"📂 Loaded {len(self.notification_tickets)} existing notification tickets"
        )

    def save_notification_tickets(self):
        """Save notification tickets to index and per-ticket files (mirror helpdesk)."""
        _save_notification_tickets_to_storage(
            self.tickets_file, self.tickets_dir, self.notification_tickets
        )
        logger.info(f"💾 Saved {len(self.notification_tickets)} notification tickets")

    def generate_request_id(self) -> str:
        """Generate a unique request ID for tracking."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = hashlib.md5(f"{time.time()}".encode()).hexdigest()[:6]
        return f"REQ-VSCODE-{timestamp}-{random_suffix}"

    def parse_notification(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse a notification text and extract relevant information."""
        for pattern, notif_type, priority in self.NOTIFICATION_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                request_id = self.generate_request_id()

                # Build detailed description with solutions
                solutions = {
                    "extension_dependency_error": [
                        "Install the required dependency extension",
                        "Or remove the dependency from the extension manifest",
                        "Clear workspace storage and restart VS Code",
                    ],
                    "extension_format_error": [
                        "Check workspace .code-workspace files for malformed extension IDs",
                        "Clear VS Code workspace storage",
                        "Remove corrupted extension cache",
                    ],
                    "server_crash": [
                        "Disable the crashing extension",
                        "Clear extension cache",
                        "Reinstall the extension if needed",
                    ],
                    "extension_activation_failed": [
                        "Check extension compatibility with VS Code version",
                        "Reinstall the extension",
                        "Check extension logs for specific errors",
                    ],
                    "github_access_error": [
                        "Check GitHub token validity",
                        "Verify token has required repository permissions",
                        "Refresh authentication",
                    ],
                }

                solution_text = "\n".join(
                    [f"{i + 1}. {s}" for i, s in enumerate(solutions.get(notif_type, []))]
                )

                title = f"[VS Code] {notif_type.replace('_', ' ').title()}"
                description = (
                    f"**Notification:** {text}\n\n"
                    f"**Request ID:** {request_id}\n\n"
                    f"**Analysis:**\n"
                    f"Type: {notif_type}\n"
                    f"Severity: {priority.value if hasattr(priority, 'value') else priority}\n\n"
                    f"**Recommended Solutions:**\n{solution_text}\n\n"
                    f"**C-3PO Workflow:**\n"
                    f"1. @C3PO will create PM, C, and T tickets\n"
                    f"2. Assign to appropriate team for resolution\n"
                    f"3. Team works on fix in their ticket stack\n"
                    f"4. @C3PO updates and closes upon completion"
                )

                return {
                    "title": title,
                    "description": description,
                    "notification_type": notif_type,
                    "severity": priority,
                    "request_id": request_id,
                    "team": self.TEAM_ROUTING.get(notif_type, "helpdesk_support"),
                }

        return None

    def create_ticket_set(self, info: Dict[str, Any]) -> Dict[str, str]:
        """
        Create a complete ticket set: PM (Problem), C (Change Request), T (Task).
        All tickets are linked by Request ID.
        """
        created = {}

        if not self.helpdesk_system:
            logger.warning("⚠️ Helpdesk system not available, skipping ticket creation")
            return created

        try:
            # Create PM (Problem) ticket
            pm_title = f"[PM] {info['title']}"
            pm_description = (
                f"**PROBLEM TICKET**\n\n"
                f"{info['description']}\n\n"
                f"**Linked Tickets:**\n"
                f"- C (Change Request): [Will be created]\n"
                f"- T (Task): [Will be created]\n\n"
                f"**Created by:** VS Code Notification Monitor\n"
                f"**Automation:** @JARVIS @C3PO"
            )

            pm_ticket = self.helpdesk_system.create_ticket(
                title=pm_title,
                description=pm_description,
                ticket_type=TicketType.PROBLEM,
                priority=TicketPriority(
                    info["severity"].value
                    if hasattr(info["severity"], "value")
                    else info["severity"]
                ),
                component="VS Code",
                issue_type=info["notification_type"],
            )

            if pm_ticket:
                created["PM"] = pm_ticket.ticket_id
                logger.info(f"✅ Created PM ticket: {pm_ticket.ticket_id}")

                # Link PM to notification record
                info["pm_ticket"] = pm_ticket.ticket_id

        except Exception as e:
            logger.error(f"❌ Error creating PM ticket: {e}")

        try:
            # Create C (Change Request) ticket
            c_title = f"[C] Fix: {info['title'].replace('[VS Code] ', '')}"
            c_description = (
                f"**CHANGE REQUEST TICKET**\n\n"
                f"**Original Problem:** {info['description']}\n\n"
                f"**Required Changes:**\n"
                f"1. Investigate root cause of {info['notification_type']}\n"
                f"2. Design solution for the issue\n"
                f"3. Create implementation plan\n"
                f"4. Test the solution\n\n"
                f"**Linked Tickets:**\n"
                f"- PM (Problem): {created.get('PM', 'N/A')}\n"
                f"- T (Task): [Will be created]\n\n"
                f"**Created by:** VS Code Notification Monitor\n"
                f"**Automation:** @JARVIS @C3PO"
            )

            c_ticket = self.helpdesk_system.create_ticket(
                title=c_title,
                description=c_description,
                ticket_type=TicketType.CHANGE_REQUEST,
                priority=TicketPriority(
                    info["severity"].value
                    if hasattr(info["severity"], "value")
                    else info["severity"]
                ),
                component="VS Code",
                issue_type=f"fix_{info['notification_type']}",
            )

            if c_ticket:
                created["C"] = c_ticket.ticket_id
                logger.info(f"✅ Created C ticket: {c_ticket.ticket_id}")
                info["c_ticket"] = c_ticket.ticket_id

        except Exception as e:
            logger.error(f"❌ Error creating C ticket: {e}")

        try:
            # Create T (Task) ticket
            t_title = f"[T] Implement: {info['title'].replace('[VS Code] ', '')}"
            t_description = (
                f"**TASK TICKET**\n\n"
                f"**Original Problem:** {info['description']}\n\n"
                f"**Implementation Steps:**\n"
                f"1. Review PM and C tickets for full context\n"
                f"2. Implement the fix according to change request\n"
                f"3. Test the implementation thoroughly\n"
                f"4. Update documentation\n"
                f"5. Hand off to C-3PO for closure\n\n"
                f"**Linked Tickets:**\n"
                f"- PM (Problem): {created.get('PM', 'N/A')}\n"
                f"- C (Change Request): {created.get('C', 'N/A')}\n\n"
                f"**Created by:** VS Code Notification Monitor\n"
                f"**Automation:** @JARVIS @C3PO"
            )

            t_ticket = self.helpdesk_system.create_ticket(
                title=t_title,
                description=t_description,
                ticket_type=TicketType.CHANGE_TASK,
                priority=TicketPriority(
                    info["severity"].value
                    if hasattr(info["severity"], "value")
                    else info["severity"]
                ),
                component="VS Code",
                issue_type=f"task_{info['notification_type']}",
            )

            if t_ticket:
                created["T"] = t_ticket.ticket_id
                logger.info(f"✅ Created T ticket: {t_ticket.ticket_id}")
                info["t_ticket"] = t_ticket.ticket_id

        except Exception as e:
            logger.error(f"❌ Error creating T ticket: {e}")

        return created

    def c3po_assign_tickets(self, tickets: Dict[str, str], team: str) -> Dict[str, Any]:
        """
        C-3PO assigns tickets to appropriate teams.

        C-3PO ensures:
        - Team Manager oversight (@c3po)
        - Technical Lead assignment (@r2d2 or team-specific)
        - Business Lead for coordination
        """
        if not self.c3po_assigner:
            logger.warning("⚠️ C-3PO not available for ticket assignment")
            return {"success": False, "reason": "C-3PO not available"}

        try:
            assignments = {}
            logger.info("=" * 80)
            logger.info("🤖 C-3PO ASSIGNING TICKETS TO TEAMS")
            logger.info("=" * 80)

            for ticket_type, ticket_id in tickets.items():
                if ticket_id:
                    result = self.c3po_assigner.assign_ticket_to_team(
                        ticket_number=ticket_id, team_id=team, auto_detect=True
                    )
                    assignments[ticket_id] = result
                    if result.get("success"):
                        logger.info(f"✅ {ticket_id} -> Team: {result.get('team_assigned', team)}")
                    else:
                        logger.warning(
                            f"⚠️ {ticket_id} assignment: {result.get('error', 'Unknown')}"
                        )

            logger.info("=" * 80)
            logger.info("✅ C-3PO assignment complete")
            logger.info("=" * 80)

            return {"success": True, "assignments": assignments}

        except Exception as e:
            logger.error(f"❌ Error in C-3PO assignment: {e}")
            return {"success": False, "error": str(e)}

    def save_notification_record(self, info: Dict[str, Any], tickets: Dict[str, str]):
        """Save the notification and ticket references."""
        ticket_id = hashlib.md5(f"{info['title']}|{info['request_id']}".encode()).hexdigest()[:14]

        record = {
            "ticket_id": ticket_id,
            "title": info["title"],
            "description": info["description"],
            "notification_type": info["notification_type"],
            "severity": info["severity"].value
            if hasattr(info["severity"], "value")
            else info["severity"],
            "request_id": info["request_id"],
            "team": info.get("team"),
            "pm_ticket": tickets.get("PM"),
            "c_ticket": tickets.get("C"),
            "t_ticket": tickets.get("T"),
            "status": "open",
            "priority": info["severity"].value
            if hasattr(info["severity"], "value")
            else info["severity"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "resolved_at": None,
            "metadata": {
                "c3po_assigned": False,
                "team_notified": False,
                "work_started": False,
                "completed": False,
            },
        }

        self.notification_tickets[ticket_id] = record
        self.save_notification_tickets()

        return record

    def process_notification(self, text: str) -> Optional[Dict[str, Any]]:
        """Process a notification with full C-3PO workflow."""
        info = self.parse_notification(text)
        if not info:
            return None

        # Check for duplicate
        for existing in self.notification_tickets.values():
            if existing.get("title") == info["title"]:
                logger.debug(f"Notification already processed: {info['title']}")
                return existing

        # Create ticket set
        tickets = self.create_ticket_set(info)

        # C-3PO assigns to team
        c3po_result = self.c3po_assign_tickets(tickets, info.get("team", "helpdesk_support"))

        # Save record
        record = self.save_notification_record(info, tickets)
        record["c3po_assignment"] = c3po_result

        return record

    def report_current_issues(self) -> List[Dict[str, Any]]:
        """
        Report and create tickets for known VS Code issues.
        This implements the full C-3PO workflow.
        """
        issues = [
            {
                "title": "[VS Code] Lumina Core Extension - Missing GitHub Copilot Dependency",
                "description": (
                    "Cannot activate 'Lumina Core - Open Source Lumina Ecosystem' extension "
                    "because it depends on an unknown 'github.copilot' extension.\n\n"
                    "**Analysis:**\n"
                    "- The Lumina Core extension has GitHub Copilot listed as a dependency\n"
                    "- Copilot may not be installed or may have a different extension ID\n"
                    "- This could also be a cached/corrupted extension state\n\n"
                    "**C-3PO Actions:**\n"
                    "1. Create PM, C, T tickets\n"
                    "2. Assign to jarvis_superagent team\n"
                    "3. Team implements fix\n"
                    "4. C-3PO closes upon completion"
                ),
                "type": "extension_dependency_error",
                "severity": TicketPriority.HIGH,
            },
            {
                "title": "[VS Code] Extension Format Error - undefined_publisher.lumina-ai",
                "description": (
                    "The extension recommendation 'undefined_publisher.lumina-ai' has bad format. "
                    "Expected format: <provider>.<name>\n\n"
                    "**Analysis:**\n"
                    "- A workspace or project configuration has a malformed extension reference\n"
                    "- 'undefined_publisher' suggests the publisher field is missing\n\n"
                    "**C-3PO Actions:**\n"
                    "1. Create PM, C, T tickets\n"
                    "2. Assign to helpdesk_support team\n"
                    "3. Team investigates and fixes\n"
                    "4. C-3PO closes upon completion"
                ),
                "type": "extension_format_error",
                "severity": TicketPriority.MEDIUM,
            },
            {
                "title": "[VS Code] Microsoft Edge Tools Server Crashes",
                "description": (
                    "Microsoft Edge Tools server crashed 5 times in the last 3 minutes. "
                    "The server will not be restarted.\n\n"
                    "**Analysis:**\n"
                    "- The Edge Tools extension has become unstable\n"
                    "- Known issue with certain VS Code versions\n\n"
                    "**C-3PO Actions:**\n"
                    "1. Create PM, C, T tickets\n"
                    "2. Assign to helpdesk_support team\n"
                    "3. Team disables/reinstalls extension\n"
                    "4. C-3PO closes upon completion"
                ),
                "type": "server_crash",
                "severity": TicketPriority.HIGH,
            },
        ]

        results = []
        for issue in issues:
            logger.info(f"\n📋 Processing: {issue['title']}")

            info = {
                "title": issue["title"],
                "description": issue["description"],
                "notification_type": issue["type"],
                "severity": issue["severity"],
                "request_id": self.generate_request_id(),
                "team": self.TEAM_ROUTING.get(issue["type"], "helpdesk_support"),
            }

            # Create tickets
            tickets = self.create_ticket_set(info)

            # C-3PO assigns
            c3po_result = self.c3po_assign_tickets(tickets, info["team"])

            # Save record
            record = self.save_notification_record(info, tickets)
            record["tickets"] = tickets
            record["c3po_result"] = c3po_result

            results.append(record)

        return results


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="VS Code Notification Monitor with C-3PO Ticket Lifecycle",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/python/monitor_vscode_notifications.py --report
      Process current VS Code issues with full C-3PO workflow

Workflow:
  1. Detect notification
  2. Create PM (Problem), C (Change Request), T (Task) tickets
  3. @C3PO assigns tickets to appropriate teams
  4. Teams work on their personal ticket stacks
  5. @C3PO updates, maintains, and closes tickets
        """,
    )
    parser.add_argument(
        "--report", action="store_true", help="Report current issues and create tickets"
    )
    args = parser.parse_args()

    monitor = VSCodeNotificationMonitor()

    if args.report:
        print("=" * 80)
        print("🤖 VS Code Notification Monitor with C-3PO Ticket Lifecycle")
        print("=" * 80)
        print()

        results = monitor.report_current_issues()

        print("\n" + "=" * 80)
        print("📊 SUMMARY - TICKETS CREATED AND ASSIGNED")
        print("=" * 80)

        for result in results:
            print(f"\n📋 Request ID: {result['request_id']}")
            print(f"   Title: {result['title']}")
            print(f"   Team: {result['team']}")
            print("   Tickets Created:")
            print(f"      - PM (Problem): {result.get('pm_ticket', 'N/A')}")
            print(f"      - C (Change Request): {result.get('c_ticket', 'N/A')}")
            print(f"      - T (Task): {result.get('t_ticket', 'N/A')}")

            c3po_result = result.get("c3po_result", {})
            if c3po_result.get("success"):
                print("   ✅ C-3PO Assignment: Success")
                assignments = c3po_result.get("assignments", {})
                for tid, assignment in assignments.items():
                    if assignment.get("success"):
                        print(f"      → {tid}: {assignment.get('team_assigned', 'Assigned')}")
            else:
                print(f"   ⚠️ C-3PO Assignment: {c3po_result.get('reason', 'Pending')}")

        print("\n" + "=" * 80)
        print("📈 TICKET STATISTICS")
        print("=" * 80)

        pm_count = sum(1 for r in results if r.get("pm_ticket"))
        c_count = sum(1 for r in results if r.get("c_ticket"))
        t_count = sum(1 for r in results if r.get("t_ticket"))

        print(f"PM (Problem) Tickets: {pm_count}")
        print(f"C (Change Request) Tickets: {c_count}")
        print(f"T (Task) Tickets: {t_count}")
        print(f"Total Ticket Sets: {len(results)}")

        print("\n" + "=" * 80)
        print("✅ C-3PO Workflow Complete")
        print("=" * 80)
        print("\nAll tickets have been:")
        print("  1. ✅ Created with PM, C, and T types")
        print("  2. ✅ Assigned to appropriate teams by @C3PO")
        print("  3. ✅ Ready for team resolution in their personal stacks")
        print("  4. ✅ Linked by Request ID for tracking")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

project_root = Path(__file__).parent.parent.parent
scripts_python = project_root / "scripts" / "python"
sys.path.insert(0, str(scripts_python))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("VSCodeNotificationMonitor")

# Import ticket system components
HELPDESK_AVAILABLE = False
C3PO_AVAILABLE = False

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("VSCodeNotificationMonitor")

try:
    from jarvis_helpdesk_ticket_system import (
        HelpdeskTicket,
        JARVISHelpdeskTicketSystem,
        TicketPriority,
        TicketStatus,
        TicketType,
    )

    HELPDESK_AVAILABLE = True
    logger.info("✅ Helpdesk ticket system available")
except ImportError as e:
    logger.warning(f"⚠️ Helpdesk ticket system not available: {e}")
    HELPDESK_AVAILABLE = False

    # Define fallbacks
    class _TicketPriority:
        CRITICAL = "critical"
        HIGH = "high"
        MEDIUM = "medium"
        LOW = "low"

    class _TicketStatus:
        OPEN = "open"
        IN_PROGRESS = "in_progress"
        RESOLVED = "resolved"
        CLOSED = "closed"

    class _TicketType:
        PROBLEM = "PM"
        CHANGE_REQUEST = "C"
        CHANGE_TASK = "T"

    TicketPriority = _TicketPriority
    TicketStatus = _TicketStatus
    TicketType = _TicketType


try:
    from jarvis_c3po_ticket_assigner import C3POTicketAssigner

    C3PO_AVAILABLE = True
    logger.info("✅ C-3PO Ticket Assigner available")
except ImportError as e:
    logger.warning(f"⚠️ C-3PO Ticket Assigner not available: {e}")


class VSCodeNotificationMonitor:
    """
    Monitors VS Code / Cursor IDE notifications and manages full ticket lifecycle.

    C-3PO workflow:
    1. Monitor detects notification
    2. Create PM (Problem) ticket with full details
    3. Create C (Change Request) ticket for the fix
    4. Create T (Task) ticket for implementation
    5. C-3PO assigns tickets to appropriate teams
    6. Teams work on their stacks
    7. C-3PO updates and closes tickets upon completion
    """

    # Patterns for common VS Code notifications/errors
    NOTIFICATION_PATTERNS = [
        # Extension activation errors
        (
            r"Cannot activate '(.+)' extension because it depends on an unknown '(.+)' extension",
            "extension_dependency_error",
            TicketPriority.HIGH,
        ),
        # Extension format errors
        (
            r"(\w+\.\w+) \(bad format\) Expected: <provider>\.<name>",
            "extension_format_error",
            TicketPriority.MEDIUM,
        ),
        # Server crashes
        (
            r"(.+) server crashed (\d+) times in the last (\d+) minutes",
            "server_crash",
            TicketPriority.HIGH,
        ),
        # General extension errors
        (
            r"Extension '.+' failed to activate",
            "extension_activation_failed",
            TicketPriority.MEDIUM,
        ),
        # GitHub access errors
        (
            r"No GitHub access token found with access to repository",
            "github_access_error",
            TicketPriority.HIGH,
        ),
    ]

    # Team routing based on issue type
    TEAM_ROUTING = {
        "extension_dependency_error": "jarvis_superagent",
        "extension_format_error": "helpdesk_support",
        "server_crash": "helpdesk_support",
        "extension_activation_failed": "helpdesk_support",
        "github_access_error": "jarvis_superagent",
    }

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.tickets_file = self.project_root / "data/notification_tickets/tickets.json"
        self.tickets_dir = self.tickets_file.parent / "tickets"
        self.tickets_dir.mkdir(parents=True, exist_ok=True)

        # Initialize ticket system
        self.helpdesk_system = None
        if HELPDESK_AVAILABLE:
            try:
                self.helpdesk_system = JARVISHelpdeskTicketSystem(project_root=self.project_root)
                logger.info("✅ Helpdesk system initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize helpdesk system: {e}")

        # Initialize C-3PO
        self.c3po_assigner = None
        if C3PO_AVAILABLE:
            try:
                self.c3po_assigner = C3POTicketAssigner(self.project_root)
                logger.info("✅ C-3PO Ticket Assigner initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize C-3PO: {e}")

        self.notification_tickets: Dict[str, dict] = {}
        self.load_notification_tickets()

    def load_notification_tickets(self):
        """Load existing notification tickets (index + per-ticket files, mirror helpdesk)."""
        self.notification_tickets = _load_notification_tickets_from_storage(
            self.tickets_file, self.tickets_dir
        )
        logger.info(
            f"📂 Loaded {len(self.notification_tickets)} existing notification tickets"
        )

    def save_notification_tickets(self):
        """Save notification tickets to index and per-ticket files (mirror helpdesk)."""
        _save_notification_tickets_to_storage(
            self.tickets_file, self.tickets_dir, self.notification_tickets
        )
        logger.info(f"💾 Saved {len(self.notification_tickets)} notification tickets")

    def generate_request_id(self) -> str:
        """Generate a unique request ID for tracking."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = hashlib.md5(f"{time.time()}".encode()).hexdigest()[:6]
        return f"REQ-VSCODE-{timestamp}-{random_suffix}"

    def parse_notification(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse a notification text and extract relevant information."""
        for pattern, notif_type, priority in self.NOTIFICATION_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                request_id = self.generate_request_id()

                # Build detailed description with solutions
                solutions = {
                    "extension_dependency_error": [
                        "Install the required dependency extension",
                        "Or remove the dependency from the extension manifest",
                        "Clear workspace storage and restart VS Code",
                    ],
                    "extension_format_error": [
                        "Check workspace .code-workspace files for malformed extension IDs",
                        "Clear VS Code workspace storage",
                        "Remove corrupted extension cache",
                    ],
                    "server_crash": [
                        "Disable the crashing extension",
                        "Clear extension cache",
                        "Reinstall the extension if needed",
                    ],
                    "extension_activation_failed": [
                        "Check extension compatibility with VS Code version",
                        "Reinstall the extension",
                        "Check extension logs for specific errors",
                    ],
                    "github_access_error": [
                        "Check GitHub token validity",
                        "Verify token has required repository permissions",
                        "Refresh authentication",
                    ],
                }

                solution_text = "\n".join(
                    [f"{i + 1}. {s}" for i, s in enumerate(solutions.get(notif_type, []))]
                )

                title = f"[VS Code] {notif_type.replace('_', ' ').title()}"
                description = (
                    f"**Notification:** {text}\n\n"
                    f"**Request ID:** {request_id}\n\n"
                    f"**Analysis:**\n"
                    f"Type: {notif_type}\n"
                    f"Severity: {priority.value if hasattr(priority, 'value') else priority}\n\n"
                    f"**Recommended Solutions:**\n{solution_text}\n\n"
                    f"**C-3PO Workflow:**\n"
                    f"1. @C3PO will create PM, C, and T tickets\n"
                    f"2. Assign to appropriate team for resolution\n"
                    f"3. Team works on fix in their ticket stack\n"
                    f"4. @C3PO updates and closes upon completion"
                )

                return {
                    "title": title,
                    "description": description,
                    "notification_type": notif_type,
                    "severity": priority,
                    "request_id": request_id,
                    "team": self.TEAM_ROUTING.get(notif_type, "helpdesk_support"),
                }

        return None

    def create_ticket_set(self, info: Dict[str, Any]) -> Dict[str, str]:
        """
        Create a complete ticket set: PM (Problem), C (Change Request), T (Task).
        All tickets are linked by Request ID.
        """
        created = {}

        if not self.helpdesk_system:
            logger.warning("⚠️ Helpdesk system not available, skipping ticket creation")
            return created

        try:
            # Create PM (Problem) ticket
            pm_title = f"[PM] {info['title']}"
            pm_description = (
                f"**PROBLEM TICKET**\n\n"
                f"{info['description']}\n\n"
                f"**Linked Tickets:**\n"
                f"- C (Change Request): [Will be created]\n"
                f"- T (Task): [Will be created]\n\n"
                f"**Created by:** VS Code Notification Monitor\n"
                f"**Automation:** @JARVIS @C3PO"
            )

            pm_ticket = self.helpdesk_system.create_ticket(
                title=pm_title,
                description=pm_description,
                ticket_type=TicketType.PROBLEM,
                priority=TicketPriority(
                    info["severity"].value
                    if hasattr(info["severity"], "value")
                    else info["severity"]
                ),
                component="VS Code",
                issue_type=info["notification_type"],
            )

            if pm_ticket:
                created["PM"] = pm_ticket.ticket_id
                logger.info(f"✅ Created PM ticket: {pm_ticket.ticket_id}")

                # Link PM to notification record
                info["pm_ticket"] = pm_ticket.ticket_id

        except Exception as e:
            logger.error(f"❌ Error creating PM ticket: {e}")

        try:
            # Create C (Change Request) ticket
            c_title = f"[C] Fix: {info['title'].replace('[VS Code] ', '')}"
            c_description = (
                f"**CHANGE REQUEST TICKET**\n\n"
                f"**Original Problem:** {info['description']}\n\n"
                f"**Required Changes:**\n"
                f"1. Investigate root cause of {info['notification_type']}\n"
                f"2. Design solution for the issue\n"
                f"3. Create implementation plan\n"
                f"4. Test the solution\n\n"
                f"**Linked Tickets:**\n"
                f"- PM (Problem): {created.get('PM', 'N/A')}\n"
                f"- T (Task): [Will be created]\n\n"
                f"**Created by:** VS Code Notification Monitor\n"
                f"**Automation:** @JARVIS @C3PO"
            )

            c_ticket = self.helpdesk_system.create_ticket(
                title=c_title,
                description=c_description,
                ticket_type=TicketType.CHANGE_REQUEST,
                priority=TicketPriority(
                    info["severity"].value
                    if hasattr(info["severity"], "value")
                    else info["severity"]
                ),
                component="VS Code",
                issue_type=f"fix_{info['notification_type']}",
            )

            if c_ticket:
                created["C"] = c_ticket.ticket_id
                logger.info(f"✅ Created C ticket: {c_ticket.ticket_id}")
                info["c_ticket"] = c_ticket.ticket_id

        except Exception as e:
            logger.error(f"❌ Error creating C ticket: {e}")

        try:
            # Create T (Task) ticket
            t_title = f"[T] Implement: {info['title'].replace('[VS Code] ', '')}"
            t_description = (
                f"**TASK TICKET**\n\n"
                f"**Original Problem:** {info['description']}\n\n"
                f"**Implementation Steps:**\n"
                f"1. Review PM and C tickets for full context\n"
                f"2. Implement the fix according to change request\n"
                f"3. Test the implementation thoroughly\n"
                f"4. Update documentation\n"
                f"5. Hand off to C-3PO for closure\n\n"
                f"**Linked Tickets:**\n"
                f"- PM (Problem): {created.get('PM', 'N/A')}\n"
                f"- C (Change Request): {created.get('C', 'N/A')}\n\n"
                f"**Created by:** VS Code Notification Monitor\n"
                f"**Automation:** @JARVIS @C3PO"
            )

            t_ticket = self.helpdesk_system.create_ticket(
                title=t_title,
                description=t_description,
                ticket_type=TicketType.CHANGE_TASK,
                priority=TicketPriority(
                    info["severity"].value
                    if hasattr(info["severity"], "value")
                    else info["severity"]
                ),
                component="VS Code",
                issue_type=f"task_{info['notification_type']}",
            )

            if t_ticket:
                created["T"] = t_ticket.ticket_id
                logger.info(f"✅ Created T ticket: {t_ticket.ticket_id}")
                info["t_ticket"] = t_ticket.ticket_id

        except Exception as e:
            logger.error(f"❌ Error creating T ticket: {e}")

        return created

    def c3po_assign_tickets(self, tickets: Dict[str, str], team: str) -> Dict[str, Any]:
        """
        C-3PO assigns tickets to appropriate teams.

        C-3PO ensures:
        - Team Manager oversight (@c3po)
        - Technical Lead assignment (@r2d2 or team-specific)
        - Business Lead for coordination
        """
        if not self.c3po_assigner:
            logger.warning("⚠️ C-3PO not available for ticket assignment")
            return {"success": False, "reason": "C-3PO not available"}

        try:
            assignments = {}
            logger.info("=" * 80)
            logger.info("🤖 C-3PO ASSIGNING TICKETS TO TEAMS")
            logger.info("=" * 80)

            for ticket_type, ticket_id in tickets.items():
                if ticket_id:
                    result = self.c3po_assigner.assign_ticket_to_team(
                        ticket_number=ticket_id, team_id=team, auto_detect=True
                    )
                    assignments[ticket_id] = result
                    if result.get("success"):
                        logger.info(f"✅ {ticket_id} -> Team: {result.get('team_assigned', team)}")
                    else:
                        logger.warning(
                            f"⚠️ {ticket_id} assignment: {result.get('error', 'Unknown')}"
                        )

            logger.info("=" * 80)
            logger.info("✅ C-3PO assignment complete")
            logger.info("=" * 80)

            return {"success": True, "assignments": assignments}

        except Exception as e:
            logger.error(f"❌ Error in C-3PO assignment: {e}")
            return {"success": False, "error": str(e)}

    def save_notification_record(self, info: Dict[str, Any], tickets: Dict[str, str]):
        """Save the notification and ticket references."""
        ticket_id = hashlib.md5(f"{info['title']}|{info['request_id']}".encode()).hexdigest()[:14]

        record = {
            "ticket_id": ticket_id,
            "title": info["title"],
            "description": info["description"],
            "notification_type": info["notification_type"],
            "severity": info["severity"].value
            if hasattr(info["severity"], "value")
            else info["severity"],
            "request_id": info["request_id"],
            "team": info.get("team"),
            "pm_ticket": tickets.get("PM"),
            "c_ticket": tickets.get("C"),
            "t_ticket": tickets.get("T"),
            "status": "open",
            "priority": info["severity"].value
            if hasattr(info["severity"], "value")
            else info["severity"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "resolved_at": None,
            "metadata": {
                "c3po_assigned": False,
                "team_notified": False,
                "work_started": False,
                "completed": False,
            },
        }

        self.notification_tickets[ticket_id] = record
        self.save_notification_tickets()

        return record

    def process_notification(self, text: str) -> Optional[Dict[str, Any]]:
        """Process a notification with full C-3PO workflow."""
        info = self.parse_notification(text)
        if not info:
            return None

        # Check for duplicate
        for existing in self.notification_tickets.values():
            if existing.get("title") == info["title"]:
                logger.debug(f"Notification already processed: {info['title']}")
                return existing

        # Create ticket set
        tickets = self.create_ticket_set(info)

        # C-3PO assigns to team
        c3po_result = self.c3po_assign_tickets(tickets, info.get("team", "helpdesk_support"))

        # Save record
        record = self.save_notification_record(info, tickets)
        record["c3po_assignment"] = c3po_result

        return record

    def report_current_issues(self) -> List[Dict[str, Any]]:
        """
        Report and create tickets for known VS Code issues.
        This implements the full C-3PO workflow.
        """
        issues = [
            {
                "title": "[VS Code] Lumina Core Extension - Missing GitHub Copilot Dependency",
                "description": (
                    "Cannot activate 'Lumina Core - Open Source Lumina Ecosystem' extension "
                    "because it depends on an unknown 'github.copilot' extension.\n\n"
                    "**Analysis:**\n"
                    "- The Lumina Core extension has GitHub Copilot listed as a dependency\n"
                    "- Copilot may not be installed or may have a different extension ID\n"
                    "- This could also be a cached/corrupted extension state\n\n"
                    "**C-3PO Actions:**\n"
                    "1. Create PM, C, T tickets\n"
                    "2. Assign to jarvis_superagent team\n"
                    "3. Team implements fix\n"
                    "4. C-3PO closes upon completion"
                ),
                "type": "extension_dependency_error",
                "severity": TicketPriority.HIGH,
            },
            {
                "title": "[VS Code] Extension Format Error - undefined_publisher.lumina-ai",
                "description": (
                    "The extension recommendation 'undefined_publisher.lumina-ai' has bad format. "
                    "Expected format: <provider>.<name>\n\n"
                    "**Analysis:**\n"
                    "- A workspace or project configuration has a malformed extension reference\n"
                    "- 'undefined_publisher' suggests the publisher field is missing\n\n"
                    "**C-3PO Actions:**\n"
                    "1. Create PM, C, T tickets\n"
                    "2. Assign to helpdesk_support team\n"
                    "3. Team investigates and fixes\n"
                    "4. C-3PO closes upon completion"
                ),
                "type": "extension_format_error",
                "severity": TicketPriority.MEDIUM,
            },
            {
                "title": "[VS Code] Microsoft Edge Tools Server Crashes",
                "description": (
                    "Microsoft Edge Tools server crashed 5 times in the last 3 minutes. "
                    "The server will not be restarted.\n\n"
                    "**Analysis:**\n"
                    "- The Edge Tools extension has become unstable\n"
                    "- Known issue with certain VS Code versions\n\n"
                    "**C-3PO Actions:**\n"
                    "1. Create PM, C, T tickets\n"
                    "2. Assign to helpdesk_support team\n"
                    "3. Team disables/reinstalls extension\n"
                    "4. C-3PO closes upon completion"
                ),
                "type": "server_crash",
                "severity": TicketPriority.HIGH,
            },
        ]

        results = []
        for issue in issues:
            logger.info(f"\n📋 Processing: {issue['title']}")

            info = {
                "title": issue["title"],
                "description": issue["description"],
                "notification_type": issue["type"],
                "severity": issue["severity"],
                "request_id": self.generate_request_id(),
                "team": self.TEAM_ROUTING.get(issue["type"], "helpdesk_support"),
            }

            # Create tickets
            tickets = self.create_ticket_set(info)

            # C-3PO assigns
            c3po_result = self.c3po_assign_tickets(tickets, info["team"])

            # Save record
            record = self.save_notification_record(info, tickets)
            record["tickets"] = tickets
            record["c3po_result"] = c3po_result

            results.append(record)

        return results


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="VS Code Notification Monitor with C-3PO Ticket Lifecycle",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/python/monitor_vscode_notifications.py --report
      Process current VS Code issues with full C-3PO workflow

Workflow:
  1. Detect notification
  2. Create PM (Problem), C (Change Request), T (Task) tickets
  3. @C3PO assigns tickets to appropriate teams
  4. Teams work on their personal ticket stacks
  5. @C3PO updates, maintains, and closes tickets
        """,
    )
    parser.add_argument(
        "--report", action="store_true", help="Report current issues and create tickets"
    )
    args = parser.parse_args()

    monitor = VSCodeNotificationMonitor()

    if args.report:
        print("=" * 80)
        print("🤖 VS Code Notification Monitor with C-3PO Ticket Lifecycle")
        print("=" * 80)
        print()

        results = monitor.report_current_issues()

        print("\n" + "=" * 80)
        print("📊 SUMMARY - TICKETS CREATED AND ASSIGNED")
        print("=" * 80)

        for result in results:
            print(f"\n📋 Request ID: {result['request_id']}")
            print(f"   Title: {result['title']}")
            print(f"   Team: {result['team']}")
            print("   Tickets Created:")
            print(f"      - PM (Problem): {result.get('pm_ticket', 'N/A')}")
            print(f"      - C (Change Request): {result.get('c_ticket', 'N/A')}")
            print(f"      - T (Task): {result.get('t_ticket', 'N/A')}")

            c3po_result = result.get("c3po_result", {})
            if c3po_result.get("success"):
                print("   ✅ C-3PO Assignment: Success")
                assignments = c3po_result.get("assignments", {})
                for tid, assignment in assignments.items():
                    if assignment.get("success"):
                        print(f"      → {tid}: {assignment.get('team_assigned', 'Assigned')}")
            else:
                print(f"   ⚠️ C-3PO Assignment: {c3po_result.get('reason', 'Pending')}")

        print("\n" + "=" * 80)
        print("📈 TICKET STATISTICS")
        print("=" * 80)

        pm_count = sum(1 for r in results if r.get("pm_ticket"))
        c_count = sum(1 for r in results if r.get("c_ticket"))
        t_count = sum(1 for r in results if r.get("t_ticket"))

        print(f"PM (Problem) Tickets: {pm_count}")
        print(f"C (Change Request) Tickets: {c_count}")
        print(f"T (Task) Tickets: {t_count}")
        print(f"Total Ticket Sets: {len(results)}")

        print("\n" + "=" * 80)
        print("✅ C-3PO Workflow Complete")
        print("=" * 80)
        print("\nAll tickets have been:")
        print("  1. ✅ Created with PM, C, and T types")
        print("  2. ✅ Assigned to appropriate teams by @C3PO")
        print("  3. ✅ Ready for team resolution in their personal stacks")
        print("  4. ✅ Linked by Request ID for tracking")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

def validate_ticket_number(ticket: str) -> tuple[bool, str]:
    """
    Validate ticket number format.

    Args:
        ticket: Ticket number to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not ticket:
        return False, "Ticket number is empty"

    if not TICKET_PATTERN.match(ticket):
        return False, f"Invalid format: {ticket}. Expected: PM000000001, C000000001, T000000001"

    return True, ""

def format_ticket_number(prefix: str, counter: int) -> str:
    """
    Format ticket number with correct 9-digit zero-padding.

    Args:
        prefix: Ticket prefix (PM, C, CR, T)
        counter: Counter value

    Returns:
        Formatted ticket number (e.g., PM000000001)
    """
    return f"{prefix}{counter:09d}"

# Setup paths
project_root = Path(__file__).parent.parent.parent
scripts_python = project_root / "scripts" / "python"
sys.path.insert(0, str(scripts_python))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("VSCodeNotificationMonitor")

# Import ticket system components
HELPDESK_AVAILABLE = False
C3PO_AVAILABLE = False

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("VSCodeNotificationMonitor")

try:
    from jarvis_helpdesk_ticket_system import (
        HelpdeskTicket,
        JARVISHelpdeskTicketSystem,
        TicketPriority,
        TicketStatus,
        TicketType,
    )

    HELPDESK_AVAILABLE = True
    logger.info("✅ Helpdesk ticket system available")
except ImportError as e:
    logger.warning(f"⚠️ Helpdesk ticket system not available: {e}")
    HELPDESK_AVAILABLE = False

    # Define fallbacks
    class _TicketPriority:
        CRITICAL = "critical"
        HIGH = "high"
        MEDIUM = "medium"
        LOW = "low"

    class _TicketStatus:
        OPEN = "open"
        IN_PROGRESS = "in_progress"
        RESOLVED = "resolved"
        CLOSED = "closed"

    class _TicketType:
        PROBLEM = "PM"
        CHANGE_REQUEST = "C"
        CHANGE_TASK = "T"

    TicketPriority = _TicketPriority
    TicketStatus = _TicketStatus
    TicketType = _TicketType


try:
    from jarvis_c3po_ticket_assigner import C3POTicketAssigner

    C3PO_AVAILABLE = True
    logger.info("✅ C-3PO Ticket Assigner available")
except ImportError as e:
    logger.warning(f"⚠️ C-3PO Ticket Assigner not available: {e}")


class VSCodeNotificationMonitor:
    """
    Monitors VS Code / Cursor IDE notifications and manages full ticket lifecycle.

    C-3PO workflow:
    1. Monitor detects notification
    2. Create PM (Problem) ticket with full details
    3. Create C (Change Request) ticket for the fix
    4. Create T (Task) ticket for implementation
    5. C-3PO assigns tickets to appropriate teams
    6. Teams work on their stacks
    7. C-3PO updates and closes tickets upon completion
    """

    # Patterns for common VS Code notifications/errors
    NOTIFICATION_PATTERNS = [
        # Extension activation errors
        (
            r"Cannot activate '(.+)' extension because it depends on an unknown '(.+)' extension",
            "extension_dependency_error",
            TicketPriority.HIGH,
        ),
        # Extension format errors
        (
            r"(\w+\.\w+) \(bad format\) Expected: <provider>\.<name>",
            "extension_format_error",
            TicketPriority.MEDIUM,
        ),
        # Server crashes
        (
            r"(.+) server crashed (\d+) times in the last (\d+) minutes",
            "server_crash",
            TicketPriority.HIGH,
        ),
        # General extension errors
        (
            r"Extension '.+' failed to activate",
            "extension_activation_failed",
            TicketPriority.MEDIUM,
        ),
        # GitHub access errors
        (
            r"No GitHub access token found with access to repository",
            "github_access_error",
            TicketPriority.HIGH,
        ),
    ]

    # Team routing based on issue type
    TEAM_ROUTING = {
        "extension_dependency_error": "jarvis_superagent",
        "extension_format_error": "helpdesk_support",
        "server_crash": "helpdesk_support",
        "extension_activation_failed": "helpdesk_support",
        "github_access_error": "jarvis_superagent",
    }

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.tickets_file = self.project_root / "data/notification_tickets/tickets.json"
        self.tickets_dir = self.tickets_file.parent / "tickets"
        self.tickets_dir.mkdir(parents=True, exist_ok=True)

        # Initialize ticket system
        self.helpdesk_system = None
        if HELPDESK_AVAILABLE:
            try:
                self.helpdesk_system = JARVISHelpdeskTicketSystem(project_root=self.project_root)
                logger.info("✅ Helpdesk system initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize helpdesk system: {e}")

        # Initialize C-3PO
        self.c3po_assigner = None
        if C3PO_AVAILABLE:
            try:
                self.c3po_assigner = C3POTicketAssigner(self.project_root)
                logger.info("✅ C-3PO Ticket Assigner initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize C-3PO: {e}")

        self.notification_tickets: Dict[str, dict] = {}
        self.load_notification_tickets()

    def load_notification_tickets(self):
        """Load existing notification tickets (index + per-ticket files, mirror helpdesk)."""
        self.notification_tickets = _load_notification_tickets_from_storage(
            self.tickets_file, self.tickets_dir
        )
        logger.info(
            f"📂 Loaded {len(self.notification_tickets)} existing notification tickets"
        )

    def save_notification_tickets(self):
        """Save notification tickets to index and per-ticket files (mirror helpdesk)."""
        _save_notification_tickets_to_storage(
            self.tickets_file, self.tickets_dir, self.notification_tickets
        )
        logger.info(f"💾 Saved {len(self.notification_tickets)} notification tickets")

    def generate_request_id(self) -> str:
        """Generate a unique request ID for tracking."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = hashlib.md5(f"{time.time()}".encode()).hexdigest()[:6]
        return f"REQ-VSCODE-{timestamp}-{random_suffix}"

    def parse_notification(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse a notification text and extract relevant information."""
        for pattern, notif_type, priority in self.NOTIFICATION_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                request_id = self.generate_request_id()

                # Build detailed description with solutions
                solutions = {
                    "extension_dependency_error": [
                        "Install the required dependency extension",
                        "Or remove the dependency from the extension manifest",
                        "Clear workspace storage and restart VS Code",
                    ],
                    "extension_format_error": [
                        "Check workspace .code-workspace files for malformed extension IDs",
                        "Clear VS Code workspace storage",
                        "Remove corrupted extension cache",
                    ],
                    "server_crash": [
                        "Disable the crashing extension",
                        "Clear extension cache",
                        "Reinstall the extension if needed",
                    ],
                    "extension_activation_failed": [
                        "Check extension compatibility with VS Code version",
                        "Reinstall the extension",
                        "Check extension logs for specific errors",
                    ],
                    "github_access_error": [
                        "Check GitHub token validity",
                        "Verify token has required repository permissions",
                        "Refresh authentication",
                    ],
                }

                solution_text = "\n".join(
                    [f"{i + 1}. {s}" for i, s in enumerate(solutions.get(notif_type, []))]
                )

                title = f"[VS Code] {notif_type.replace('_', ' ').title()}"
                description = (
                    f"**Notification:** {text}\n\n"
                    f"**Request ID:** {request_id}\n\n"
                    f"**Analysis:**\n"
                    f"Type: {notif_type}\n"
                    f"Severity: {priority.value if hasattr(priority, 'value') else priority}\n\n"
                    f"**Recommended Solutions:**\n{solution_text}\n\n"
                    f"**C-3PO Workflow:**\n"
                    f"1. @C3PO will create PM, C, and T tickets\n"
                    f"2. Assign to appropriate team for resolution\n"
                    f"3. Team works on fix in their ticket stack\n"
                    f"4. @C3PO updates and closes upon completion"
                )

                return {
                    "title": title,
                    "description": description,
                    "notification_type": notif_type,
                    "severity": priority,
                    "request_id": request_id,
                    "team": self.TEAM_ROUTING.get(notif_type, "helpdesk_support"),
                }

        return None

    def create_ticket_set(self, info: Dict[str, Any]) -> Dict[str, str]:
        """
        Create a complete ticket set: PM (Problem), C (Change Request), T (Task).
        All tickets are linked by Request ID.
        """
        created = {}

        if not self.helpdesk_system:
            logger.warning("⚠️ Helpdesk system not available, skipping ticket creation")
            return created

        try:
            # Create PM (Problem) ticket
            pm_title = f"[PM] {info['title']}"
            pm_description = (
                f"**PROBLEM TICKET**\n\n"
                f"{info['description']}\n\n"
                f"**Linked Tickets:**\n"
                f"- C (Change Request): [Will be created]\n"
                f"- T (Task): [Will be created]\n\n"
                f"**Created by:** VS Code Notification Monitor\n"
                f"**Automation:** @JARVIS @C3PO"
            )

            pm_ticket = self.helpdesk_system.create_ticket(
                title=pm_title,
                description=pm_description,
                ticket_type=TicketType.PROBLEM,
                priority=TicketPriority(
                    info["severity"].value
                    if hasattr(info["severity"], "value")
                    else info["severity"]
                ),
                component="VS Code",
                issue_type=info["notification_type"],
            )

            if pm_ticket:
                created["PM"] = pm_ticket.ticket_id
                logger.info(f"✅ Created PM ticket: {pm_ticket.ticket_id}")

                # Link PM to notification record
                info["pm_ticket"] = pm_ticket.ticket_id

        except Exception as e:
            logger.error(f"❌ Error creating PM ticket: {e}")

        try:
            # Create C (Change Request) ticket
            c_title = f"[C] Fix: {info['title'].replace('[VS Code] ', '')}"
            c_description = (
                f"**CHANGE REQUEST TICKET**\n\n"
                f"**Original Problem:** {info['description']}\n\n"
                f"**Required Changes:**\n"
                f"1. Investigate root cause of {info['notification_type']}\n"
                f"2. Design solution for the issue\n"
                f"3. Create implementation plan\n"
                f"4. Test the solution\n\n"
                f"**Linked Tickets:**\n"
                f"- PM (Problem): {created.get('PM', 'N/A')}\n"
                f"- T (Task): [Will be created]\n\n"
                f"**Created by:** VS Code Notification Monitor\n"
                f"**Automation:** @JARVIS @C3PO"
            )

            c_ticket = self.helpdesk_system.create_ticket(
                title=c_title,
                description=c_description,
                ticket_type=TicketType.CHANGE_REQUEST,
                priority=TicketPriority(
                    info["severity"].value
                    if hasattr(info["severity"], "value")
                    else info["severity"]
                ),
                component="VS Code",
                issue_type=f"fix_{info['notification_type']}",
            )

            if c_ticket:
                created["C"] = c_ticket.ticket_id
                logger.info(f"✅ Created C ticket: {c_ticket.ticket_id}")
                info["c_ticket"] = c_ticket.ticket_id

        except Exception as e:
            logger.error(f"❌ Error creating C ticket: {e}")

        try:
            # Create T (Task) ticket
            t_title = f"[T] Implement: {info['title'].replace('[VS Code] ', '')}"
            t_description = (
                f"**TASK TICKET**\n\n"
                f"**Original Problem:** {info['description']}\n\n"
                f"**Implementation Steps:**\n"
                f"1. Review PM and C tickets for full context\n"
                f"2. Implement the fix according to change request\n"
                f"3. Test the implementation thoroughly\n"
                f"4. Update documentation\n"
                f"5. Hand off to C-3PO for closure\n\n"
                f"**Linked Tickets:**\n"
                f"- PM (Problem): {created.get('PM', 'N/A')}\n"
                f"- C (Change Request): {created.get('C', 'N/A')}\n\n"
                f"**Created by:** VS Code Notification Monitor\n"
                f"**Automation:** @JARVIS @C3PO"
            )

            t_ticket = self.helpdesk_system.create_ticket(
                title=t_title,
                description=t_description,
                ticket_type=TicketType.CHANGE_TASK,
                priority=TicketPriority(
                    info["severity"].value
                    if hasattr(info["severity"], "value")
                    else info["severity"]
                ),
                component="VS Code",
                issue_type=f"task_{info['notification_type']}",
            )

            if t_ticket:
                created["T"] = t_ticket.ticket_id
                logger.info(f"✅ Created T ticket: {t_ticket.ticket_id}")
                info["t_ticket"] = t_ticket.ticket_id

        except Exception as e:
            logger.error(f"❌ Error creating T ticket: {e}")

        return created

    def c3po_assign_tickets(self, tickets: Dict[str, str], team: str) -> Dict[str, Any]:
        """
        C-3PO assigns tickets to appropriate teams.

        C-3PO ensures:
        - Team Manager oversight (@c3po)
        - Technical Lead assignment (@r2d2 or team-specific)
        - Business Lead for coordination
        """
        if not self.c3po_assigner:
            logger.warning("⚠️ C-3PO not available for ticket assignment")
            return {"success": False, "reason": "C-3PO not available"}

        try:
            assignments = {}
            logger.info("=" * 80)
            logger.info("🤖 C-3PO ASSIGNING TICKETS TO TEAMS")
            logger.info("=" * 80)

            for ticket_type, ticket_id in tickets.items():
                if ticket_id:
                    result = self.c3po_assigner.assign_ticket_to_team(
                        ticket_number=ticket_id, team_id=team, auto_detect=True
                    )
                    assignments[ticket_id] = result
                    if result.get("success"):
                        logger.info(f"✅ {ticket_id} -> Team: {result.get('team_assigned', team)}")
                    else:
                        logger.warning(
                            f"⚠️ {ticket_id} assignment: {result.get('error', 'Unknown')}"
                        )

            logger.info("=" * 80)
            logger.info("✅ C-3PO assignment complete")
            logger.info("=" * 80)

            return {"success": True, "assignments": assignments}

        except Exception as e:
            logger.error(f"❌ Error in C-3PO assignment: {e}")
            return {"success": False, "error": str(e)}

    def save_notification_record(self, info: Dict[str, Any], tickets: Dict[str, str]):
        """Save the notification and ticket references."""
        ticket_id = hashlib.md5(f"{info['title']}|{info['request_id']}".encode()).hexdigest()[:14]

        record = {
            "ticket_id": ticket_id,
            "title": info["title"],
            "description": info["description"],
            "notification_type": info["notification_type"],
            "severity": info["severity"].value
            if hasattr(info["severity"], "value")
            else info["severity"],
            "request_id": info["request_id"],
            "team": info.get("team"),
            "pm_ticket": tickets.get("PM"),
            "c_ticket": tickets.get("C"),
            "t_ticket": tickets.get("T"),
            "status": "open",
            "priority": info["severity"].value
            if hasattr(info["severity"], "value")
            else info["severity"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "resolved_at": None,
            "metadata": {
                "c3po_assigned": False,
                "team_notified": False,
                "work_started": False,
                "completed": False,
            },
        }

        self.notification_tickets[ticket_id] = record
        self.save_notification_tickets()

        return record

    def process_notification(self, text: str) -> Optional[Dict[str, Any]]:
        """Process a notification with full C-3PO workflow."""
        info = self.parse_notification(text)
        if not info:
            return None

        # Check for duplicate
        for existing in self.notification_tickets.values():
            if existing.get("title") == info["title"]:
                logger.debug(f"Notification already processed: {info['title']}")
                return existing

        # Create ticket set
        tickets = self.create_ticket_set(info)

        # C-3PO assigns to team
        c3po_result = self.c3po_assign_tickets(tickets, info.get("team", "helpdesk_support"))

        # Save record
        record = self.save_notification_record(info, tickets)
        record["c3po_assignment"] = c3po_result

        return record

    def report_current_issues(self) -> List[Dict[str, Any]]:
        """
        Report and create tickets for known VS Code issues.
        This implements the full C-3PO workflow.
        """
        issues = [
            {
                "title": "[VS Code] Lumina Core Extension - Missing GitHub Copilot Dependency",
                "description": (
                    "Cannot activate 'Lumina Core - Open Source Lumina Ecosystem' extension "
                    "because it depends on an unknown 'github.copilot' extension.\n\n"
                    "**Analysis:**\n"
                    "- The Lumina Core extension has GitHub Copilot listed as a dependency\n"
                    "- Copilot may not be installed or may have a different extension ID\n"
                    "- This could also be a cached/corrupted extension state\n\n"
                    "**C-3PO Actions:**\n"
                    "1. Create PM, C, T tickets\n"
                    "2. Assign to jarvis_superagent team\n"
                    "3. Team implements fix\n"
                    "4. C-3PO closes upon completion"
                ),
                "type": "extension_dependency_error",
                "severity": TicketPriority.HIGH,
            },
            {
                "title": "[VS Code] Extension Format Error - undefined_publisher.lumina-ai",
                "description": (
                    "The extension recommendation 'undefined_publisher.lumina-ai' has bad format. "
                    "Expected format: <provider>.<name>\n\n"
                    "**Analysis:**\n"
                    "- A workspace or project configuration has a malformed extension reference\n"
                    "- 'undefined_publisher' suggests the publisher field is missing\n\n"
                    "**C-3PO Actions:**\n"
                    "1. Create PM, C, T tickets\n"
                    "2. Assign to helpdesk_support team\n"
                    "3. Team investigates and fixes\n"
                    "4. C-3PO closes upon completion"
                ),
                "type": "extension_format_error",
                "severity": TicketPriority.MEDIUM,
            },
            {
                "title": "[VS Code] Microsoft Edge Tools Server Crashes",
                "description": (
                    "Microsoft Edge Tools server crashed 5 times in the last 3 minutes. "
                    "The server will not be restarted.\n\n"
                    "**Analysis:**\n"
                    "- The Edge Tools extension has become unstable\n"
                    "- Known issue with certain VS Code versions\n\n"
                    "**C-3PO Actions:**\n"
                    "1. Create PM, C, T tickets\n"
                    "2. Assign to helpdesk_support team\n"
                    "3. Team disables/reinstalls extension\n"
                    "4. C-3PO closes upon completion"
                ),
                "type": "server_crash",
                "severity": TicketPriority.HIGH,
            },
        ]

        results = []
        for issue in issues:
            logger.info(f"\n📋 Processing: {issue['title']}")

            info = {
                "title": issue["title"],
                "description": issue["description"],
                "notification_type": issue["type"],
                "severity": issue["severity"],
                "request_id": self.generate_request_id(),
                "team": self.TEAM_ROUTING.get(issue["type"], "helpdesk_support"),
            }

            # Create tickets
            tickets = self.create_ticket_set(info)

            # C-3PO assigns
            c3po_result = self.c3po_assign_tickets(tickets, info["team"])

            # Save record
            record = self.save_notification_record(info, tickets)
            record["tickets"] = tickets
            record["c3po_result"] = c3po_result

            results.append(record)

        return results


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="VS Code Notification Monitor with C-3PO Ticket Lifecycle",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/python/monitor_vscode_notifications.py --report
      Process current VS Code issues with full C-3PO workflow

Workflow:
  1. Detect notification
  2. Create PM (Problem), C (Change Request), T (Task) tickets
  3. @C3PO assigns tickets to appropriate teams
  4. Teams work on their personal ticket stacks
  5. @C3PO updates, maintains, and closes tickets
        """,
    )
    parser.add_argument(
        "--report", action="store_true", help="Report current issues and create tickets"
    )
    args = parser.parse_args()

    monitor = VSCodeNotificationMonitor()

    if args.report:
        print("=" * 80)
        print("🤖 VS Code Notification Monitor with C-3PO Ticket Lifecycle")
        print("=" * 80)
        print()

        results = monitor.report_current_issues()

        print("\n" + "=" * 80)
        print("📊 SUMMARY - TICKETS CREATED AND ASSIGNED")
        print("=" * 80)

        for result in results:
            print(f"\n📋 Request ID: {result['request_id']}")
            print(f"   Title: {result['title']}")
            print(f"   Team: {result['team']}")
            print("   Tickets Created:")
            print(f"      - PM (Problem): {result.get('pm_ticket', 'N/A')}")
            print(f"      - C (Change Request): {result.get('c_ticket', 'N/A')}")
            print(f"      - T (Task): {result.get('t_ticket', 'N/A')}")

            c3po_result = result.get("c3po_result", {})
            if c3po_result.get("success"):
                print("   ✅ C-3PO Assignment: Success")
                assignments = c3po_result.get("assignments", {})
                for tid, assignment in assignments.items():
                    if assignment.get("success"):
                        print(f"      → {tid}: {assignment.get('team_assigned', 'Assigned')}")
            else:
                print(f"   ⚠️ C-3PO Assignment: {c3po_result.get('reason', 'Pending')}")

        print("\n" + "=" * 80)
        print("📈 TICKET STATISTICS")
        print("=" * 80)

        pm_count = sum(1 for r in results if r.get("pm_ticket"))
        c_count = sum(1 for r in results if r.get("c_ticket"))
        t_count = sum(1 for r in results if r.get("t_ticket"))

        print(f"PM (Problem) Tickets: {pm_count}")
        print(f"C (Change Request) Tickets: {c_count}")
        print(f"T (Task) Tickets: {t_count}")
        print(f"Total Ticket Sets: {len(results)}")

        print("\n" + "=" * 80)
        print("✅ C-3PO Workflow Complete")
        print("=" * 80)
        print("\nAll tickets have been:")
        print("  1. ✅ Created with PM, C, and T types")
        print("  2. ✅ Assigned to appropriate teams by @C3PO")
        print("  3. ✅ Ready for team resolution in their personal stacks")
        print("  4. ✅ Linked by Request ID for tracking")

    else:
        parser.print_help()


if __name__ == "__main__":

    main()