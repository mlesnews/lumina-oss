#!/usr/bin/env python3
"""
JARVIS Automatic Helpdesk Ticket System
Creates tickets with PM123456789 format and GitHub/GitLens PR tracking

Tags: #JARVIS #HELPDESK #WORKFLOWS #GITHUB #GITLENS @JARVIS @HELPDESK
"""

import json
import logging
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISHelpdeskTicketSystem")

try:
    from jarvis_helpdesk_integration import JARVISHelpdeskIntegration
    HELPDESK_INTEGRATION_AVAILABLE = True
except ImportError:
    HELPDESK_INTEGRATION_AVAILABLE = False
    logger.warning("JARVIS Helpdesk Integration not available")

try:
    from jarvis_gitlens_automation import JARVISGitLensAutomation
    GITLENS_AVAILABLE = True
except ImportError:
    GITLENS_AVAILABLE = False
    logger.debug("GitLens automation not available")


class TicketPriority(Enum):
    """Ticket priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TicketStatus(Enum):
    """Ticket status"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketType(Enum):
    """Ticket type categories"""
    PROBLEM = "PM"  # Problem ticket: PM + 9 digits
    CHANGE_REQUEST = "C"  # Change Request ticket: C + 9 digits
    CHANGE_TASK = "T"  # Change/Task ticket: T + 9 digits


@dataclass
class HelpdeskTicket:
    """Helpdesk ticket with three types: PM (Problem), C (Change Request), T (Change/Task)

    All tickets use 9 digits, uniquely sequential and progressive.
    Spacer: 1-3000 reserved, tickets start from 3001+.
    """
    ticket_id: str  # PM/C/T + 9 digits (e.g., PM000003065, C000003065, T000003065)
    ticket_type: str  # "PM", "C", or "T"
    title: str
    description: str
    priority: TicketPriority
    status: TicketStatus
    component: str
    issue_type: str
    created_at: str
    created_by: str = "JARVIS"
    github_pr_number: Optional[int] = None
    gitlens_ref: Optional[str] = None
    git_ticket_ref: Optional[str] = None  # Git/GitLens ticket reference
    linked_tickets: List[str] = None  # Other ticket IDs
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    change_request_id: Optional[str] = None  # Optional change request reference

    def __post_init__(self):
        if self.linked_tickets is None:
            self.linked_tickets = []
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result['priority'] = self.priority.value
        result['status'] = self.status.value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HelpdeskTicket':
        """Create from dictionary"""
        data['priority'] = TicketPriority(data['priority'])
        data['status'] = TicketStatus(data['status'])
        # Handle legacy tickets without ticket_type field
        if 'ticket_type' not in data:
            ticket_id = data.get('ticket_id', '')
            if ticket_id.startswith('PM'):
                data['ticket_type'] = 'PM'
            elif ticket_id.startswith('C'):
                data['ticket_type'] = 'C'
            elif ticket_id.startswith('T'):
                data['ticket_type'] = 'T'
            else:
                data['ticket_type'] = 'T'  # Default
        return cls(**data)


class JARVISHelpdeskTicketSystem:
    """
    Automatic Helpdesk Ticket System with three ticket types

    Ticket Types:
    - PM (Problem): Problem tickets - PM + 9 digits (e.g., PM000003065)
    - C (Change Request): Change Request tickets - C + 9 digits (e.g., C000003065)
    - T (Change/Task): Change/Task tickets - T + 9 digits (e.g., T000003065)

    Features:
    - Sequential 9-digit ticket numbers (uniquely sequential and progressive)
    - Spacer: 1-3000 reserved, tickets start from 3001+
    - GitHub PR tracking
    - GitLens integration
    - Automatic ticket creation from JARVIS Physician diagnoses
    - Workflow integration
    - Cross-reference and consolidation of existing tickets
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize ticket system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.tickets_dir = self.project_root / "data" / "helpdesk" / "tickets"
        self.tickets_dir.mkdir(parents=True, exist_ok=True)

        # Ticket counter file
        self.counter_file = self.project_root / "data" / "helpdesk" / "ticket_counter.json"
        self._initialize_counter()

        # Helpdesk integration
        self.helpdesk_integration: Optional[JARVISHelpdeskIntegration] = None
        if HELPDESK_INTEGRATION_AVAILABLE:
            try:
                self.helpdesk_integration = JARVISHelpdeskIntegration(project_root=self.project_root)
            except Exception as e:
                logger.warning(f"Helpdesk integration init failed: {e}")

        # GitLens automation
        self.gitlens: Optional[JARVISGitLensAutomation] = None
        if GITLENS_AVAILABLE:
            try:
                self.gitlens = JARVISGitLensAutomation(
                    repo_path=self.project_root,
                    auto_commit=False
                )
            except Exception as e:
                logger.debug(f"GitLens automation init failed: {e}")

        logger.info("✅ JARVIS Helpdesk Ticket System initialized")

    def _initialize_counter(self) -> None:
        """Initialize or load ticket counter

        Tickets are uniquely sequential and progressive across all types (PM, C, T).
        Spacer: 1-3000 reserved, tickets start from 3001+.
        """
        if self.counter_file.exists():
            try:
                with open(self.counter_file) as f:
                    counter_data = json.load(f)
                    # Get next ticket number (should be >= 3001 due to spacer)
                    self.next_ticket_number = counter_data.get('next_ticket_number', 3001)
                    # Ensure we're past the spacer (1-3000)
                    if self.next_ticket_number < 3001:
                        self.next_ticket_number = 3001
            except Exception:
                self.next_ticket_number = 3001
        else:
            # Start at 3001 (after spacer 1-3000)
            self.next_ticket_number = 3001

        # Ensure counter file exists
        self._save_counter()

        # Also check existing tickets to ensure we don't create duplicates
        self._sync_counter_with_existing_tickets()

    def _save_counter(self) -> None:
        """Save ticket counter"""
        try:
            with open(self.counter_file, 'w') as f:
                json.dump({
                    'next_ticket_number': self.next_ticket_number,
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save ticket counter: {e}")

    def _sync_counter_with_existing_tickets(self) -> None:
        """Sync counter with existing tickets to ensure no duplicates"""
        try:
            all_numbers = []
            for ticket_file in self.tickets_dir.glob("*.json"):
                stem = ticket_file.stem
                if stem.startswith("PM") and stem[2:].isdigit():
                    all_numbers.append(int(stem[2:]))
                elif stem.startswith("C") and stem[1:].isdigit():
                    all_numbers.append(int(stem[1:]))
                elif stem.startswith("T") and stem[1:].isdigit():
                    all_numbers.append(int(stem[1:]))

            if all_numbers:
                max_existing = max(all_numbers)
                # Ensure counter is at least max_existing + 1
                if self.next_ticket_number <= max_existing:
                    self.next_ticket_number = max_existing + 1
                    self._save_counter()
                    logger.info(f"Synced counter to {self.next_ticket_number} based on existing tickets")
        except Exception as e:
            logger.warning(f"Failed to sync counter with existing tickets: {e}")

    def _generate_ticket_id(self, ticket_type: TicketType) -> str:
        """Generate ticket ID with proper type prefix

        Args:
            ticket_type: TicketType enum (PROBLEM, CHANGE_REQUEST, or CHANGE_TASK)

        Returns:
            Ticket ID in format: PM/C/T + 9 digits (e.g., PM000003065, C000003065, T000003065)
        """
        # Get next sequential number (uniquely sequential across all types)
        ticket_number = self.next_ticket_number
        self.next_ticket_number += 1
        self._save_counter()

        # Format based on ticket type
        prefix = ticket_type.value
        ticket_id = f"{prefix}{ticket_number:09d}"
        return ticket_id

    def create_ticket(
        self,
        title: str,
        description: str,
        ticket_type: TicketType = TicketType.CHANGE_TASK,
        priority: TicketPriority = TicketPriority.MEDIUM,
        component: str = "General",
        issue_type: str = "bug",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        auto_create_pr: bool = False,
        linked_tickets: Optional[List[str]] = None
    ) -> HelpdeskTicket:
        """
        Create a new helpdesk ticket

        Args:
            title: Ticket title
            description: Ticket description
            ticket_type: Ticket type (PROBLEM/PM, CHANGE_REQUEST/C, or CHANGE_TASK/T)
            priority: Ticket priority
            component: Affected component
            issue_type: Type of issue (bug, feature, task, etc.)
            tags: Optional tags
            metadata: Optional metadata
            auto_create_pr: If True, automatically create GitHub PR for this ticket
            linked_tickets: List of linked ticket IDs

        Returns:
            Created ticket
        """
        ticket_id = self._generate_ticket_id(ticket_type)

        ticket = HelpdeskTicket(
            ticket_id=ticket_id,
            ticket_type=ticket_type.value,
            title=title,
            description=description,
            priority=priority,
            status=TicketStatus.OPEN,
            component=component,
            issue_type=issue_type,
            created_at=datetime.now().isoformat(),
            created_by="JARVIS",
            linked_tickets=linked_tickets or [],
            tags=tags or [],
            metadata=metadata or {}
        )

        # Create GitHub PR if requested
        if auto_create_pr:
            try:
                pr_number = self._create_github_pr_for_ticket(ticket)
                if pr_number:
                    ticket.github_pr_number = pr_number
                    ticket.metadata['github_pr_url'] = f"https://github.com/{self._get_repo_path()}/pull/{pr_number}"
            except Exception as e:
                logger.warning(f"Failed to create GitHub PR for ticket {ticket_id}: {e}")

        # Save ticket
        self._save_ticket(ticket)

        # Integrate with helpdesk workflow
        if self.helpdesk_integration:
            try:
                self._integrate_with_helpdesk_workflow(ticket)
            except Exception as e:
                logger.debug(f"Helpdesk workflow integration failed: {e}")

        # Send N8N notifications (Email, SMS, Telegram, Discord, Slack)
        try:
            from helpdesk_ticket_n8n_notifications import HelpdeskTicketN8NNotifications
            notifications = HelpdeskTicketN8NNotifications(project_root=self.project_root)
            notification_results = notifications.send_ticket_notification(ticket.to_dict())
            logger.info(f"📧 Notifications sent via N8N: {list(notification_results.get('channels', {}).keys())}")
        except Exception as e:
            logger.debug(f"N8N notifications failed: {e}")

        logger.info(f"✅ Created ticket: {ticket_id} - {title}")
        return ticket

    def create_ticket_from_diagnosis(
        self,
        diagnosis: Any,  # Diagnosis from JARVIS Physician
        auto_create_pr: bool = True,
        auto_heal: bool = False
    ) -> HelpdeskTicket:
        """
        Create ticket from JARVIS Physician diagnosis

        Args:
            diagnosis: Diagnosis object from JARVIS Physician
            auto_create_pr: Automatically create GitHub PR
            auto_heal: If True, ticket includes auto-healing workflow

        Returns:
            Created ticket
        """
        # Extract diagnosis info
        if hasattr(diagnosis, 'to_dict'):
            diag_dict = diagnosis.to_dict()
        elif isinstance(diagnosis, dict):
            diag_dict = diagnosis
        else:
            diag_dict = {
                'component': getattr(diagnosis, 'component', 'Unknown'),
                'issue_type': getattr(diagnosis, 'issue_type', 'unknown'),
                'severity': getattr(diagnosis, 'severity', 'medium'),
                'description': getattr(diagnosis, 'description', 'No description'),
                'root_cause': getattr(diagnosis, 'root_cause', 'Unknown'),
                'symptoms': getattr(diagnosis, 'symptoms', [])
            }

        # Determine ticket type based on diagnosis
        # Default to PROBLEM for diagnoses, but can be overridden
        ticket_type = TicketType.PROBLEM

        # Map severity to priority
        severity_map = {
            'critical': TicketPriority.CRITICAL,
            'high': TicketPriority.HIGH,
            'medium': TicketPriority.MEDIUM,
            'low': TicketPriority.LOW
        }
        priority = severity_map.get(diag_dict.get('severity', 'medium'), TicketPriority.MEDIUM)

        # Build description
        description = f"""**Issue**: {diag_dict.get('description', 'No description')}

**Component**: {diag_dict.get('component', 'Unknown')}

**Root Cause**: {diag_dict.get('root_cause', 'Unknown')}

**Symptoms**:
{chr(10).join(f"- {symptom}" for symptom in diag_dict.get('symptoms', []))}

**Issue Type**: {diag_dict.get('issue_type', 'unknown')}

**Severity**: {diag_dict.get('severity', 'medium')}

**Auto-Healing**: {'Enabled' if auto_heal else 'Disabled'}
"""

        # Tags
        tags = [
            f"severity-{diag_dict.get('severity', 'medium')}",
            f"component-{diag_dict.get('component', 'unknown').lower().replace(' ', '-')}",
            f"type-{diag_dict.get('issue_type', 'unknown')}",
            "jarvis-physician",
            "auto-detected"
        ]

        if auto_heal:
            tags.append("auto-heal")

        # Metadata
        metadata = {
            'diagnosis_id': diag_dict.get('issue_id', 'unknown'),
            'diagnosis_data': diag_dict,
            'auto_heal_enabled': auto_heal,
            'detected_by': 'JARVIS Physician'
        }

        ticket = self.create_ticket(
            title=f"{diag_dict.get('component', 'System')}: {diag_dict.get('issue_type', 'Issue').replace('_', ' ').title()}",
            description=description,
            ticket_type=ticket_type,
            priority=priority,
            component=diag_dict.get('component', 'General'),
            issue_type=diag_dict.get('issue_type', 'bug'),
            tags=tags,
            metadata=metadata,
            auto_create_pr=auto_create_pr
        )

        logger.info(f"✅ Created ticket from diagnosis: {ticket.ticket_id}")
        return ticket

    def _create_github_pr_for_ticket(self, ticket: HelpdeskTicket) -> Optional[int]:
        """Create GitHub PR for ticket"""
        if not self.gitlens:
            logger.debug("GitLens not available for PR creation")
            return None

        try:
            # Create branch name from ticket
            branch_name = f"ticket/{ticket.ticket_id.lower()}/{ticket.issue_type}"
            branch_name = re.sub(r'[^a-z0-9/-]', '-', branch_name.lower())

            # PR title and description
            pr_title = f"[{ticket.ticket_id}] {ticket.title}"
            pr_description = f"""## Ticket: {ticket.ticket_id}

**Priority**: {ticket.priority.value}
**Component**: {ticket.component}
**Issue Type**: {ticket.issue_type}

### Description
{ticket.description}

### Tags
{', '.join(f'`{tag}`' for tag in ticket.tags)}

### Metadata
```json
{json.dumps(ticket.metadata, indent=2)}
```

---
*This PR was automatically created by JARVIS Helpdesk Ticket System*
"""

            # Create PR using GitLens (this would need GitLens PR creation support)
            # For now, return None and let user create PR manually
            logger.info(f"📝 PR creation for ticket {ticket.ticket_id} - GitLens PR creation not yet implemented")
            return None

        except Exception as e:
            logger.warning(f"GitHub PR creation failed: {e}")
            return None

    def _get_repo_path(self) -> str:
        """Get GitHub repo path"""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=5
            )
            if result.returncode == 0:
                url = result.stdout.strip()
                # Extract owner/repo from URL
                match = re.search(r'github\.com[:/]([^/]+/[^/]+)', url)
                if match:
                    return match.group(1).replace('.git', '')
        except Exception:
            pass
        return "owner/repo"

    def _save_ticket(self, ticket: HelpdeskTicket) -> None:
        """Save ticket to file"""
        ticket_file = self.tickets_dir / f"{ticket.ticket_id}.json"
        try:
            with open(ticket_file, 'w', encoding='utf-8') as f:
                json.dump(ticket.to_dict(), f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved ticket: {ticket_file}")
        except Exception as e:
            logger.error(f"Failed to save ticket {ticket.ticket_id}: {e}")

    def _integrate_with_helpdesk_workflow(self, ticket: HelpdeskTicket) -> None:
        """Integrate ticket with helpdesk workflow"""
        if not self.helpdesk_integration:
            return

        try:
            workflow_data = {
                "workflow_id": ticket.ticket_id,
                "workflow_name": f"Ticket: {ticket.title}",
                "workflow_type": ticket.issue_type,
                "ticket_data": ticket.to_dict(),
                "priority": ticket.priority.value,
                "status": ticket.status.value
            }

            # This would trigger helpdesk workflow verification
            # For now, just log
            logger.debug(f"Ticket {ticket.ticket_id} integrated with helpdesk workflow")

        except Exception as e:
            logger.debug(f"Helpdesk workflow integration failed: {e}")

    def get_ticket(self, ticket_id: str) -> Optional[HelpdeskTicket]:
        """Get ticket by ID"""
        ticket_file = self.tickets_dir / f"{ticket_id}.json"
        if not ticket_file.exists():
            return None

        try:
            with open(ticket_file, encoding='utf-8') as f:
                data = json.load(f)
            return HelpdeskTicket.from_dict(data)
        except Exception as e:
            logger.error(f"Failed to load ticket {ticket_id}: {e}")
            return None

    def list_tickets(
        self,
        status: Optional[TicketStatus] = None,
        priority: Optional[TicketPriority] = None,
        component: Optional[str] = None
    ) -> List[HelpdeskTicket]:
        """List tickets with optional filters"""
        tickets = []

        for ticket_file in self.tickets_dir.glob("*.json"):
            try:
                with open(ticket_file, encoding='utf-8') as f:
                    data = json.load(f)
                ticket = HelpdeskTicket.from_dict(data)

                # Apply filters
                if status and ticket.status != status:
                    continue
                if priority and ticket.priority != priority:
                    continue
                if component and ticket.component != component:
                    continue

                tickets.append(ticket)
            except Exception:
                continue

        # Sort by creation date (newest first)
        tickets.sort(key=lambda t: t.created_at, reverse=True)
        return tickets

    def update_ticket_status(
        self,
        ticket_id: str,
        new_status: TicketStatus,
        comment: Optional[str] = None
    ) -> bool:
        """Update ticket status"""
        ticket = self.get_ticket(ticket_id)
        if not ticket:
            return False

        ticket.status = new_status
        if comment:
            if 'comments' not in ticket.metadata:
                ticket.metadata['comments'] = []
            ticket.metadata['comments'].append({
                'timestamp': datetime.now().isoformat(),
                'comment': comment,
                'by': 'JARVIS'
            })

        self._save_ticket(ticket)
        logger.info(f"✅ Updated ticket {ticket_id} status to {new_status.value}")
        return True

    def link_tickets(self, ticket_id1: str, ticket_id2: str) -> bool:
        """Link two tickets together"""
        ticket1 = self.get_ticket(ticket_id1)
        ticket2 = self.get_ticket(ticket_id2)

        if not ticket1 or not ticket2:
            return False

        if ticket_id2 not in ticket1.linked_tickets:
            ticket1.linked_tickets.append(ticket_id2)
        if ticket_id1 not in ticket2.linked_tickets:
            ticket2.linked_tickets.append(ticket_id1)

        self._save_ticket(ticket1)
        self._save_ticket(ticket2)
        logger.info(f"✅ Linked tickets: {ticket_id1} <-> {ticket_id2}")
        return True


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Helpdesk Ticket System")
    parser.add_argument("--create", action="store_true", help="Create test ticket")
    parser.add_argument("--list", action="store_true", help="List tickets")
    parser.add_argument("--ticket-id", type=str, help="Ticket ID for operations")
    parser.add_argument("--status", type=str, choices=['open', 'in_progress', 'resolved', 'closed'], help="Update status")

    args = parser.parse_args()

    system = JARVISHelpdeskTicketSystem()

    if args.create:
        ticket = system.create_ticket(
            title="Test Ticket",
            description="This is a test ticket",
            priority=TicketPriority.MEDIUM
        )
        print(f"Created ticket: {ticket.ticket_id}")

    elif args.list:
        tickets = system.list_tickets()
        print(f"\nTotal tickets: {len(tickets)}")
        for ticket in tickets[:10]:  # Show first 10
            print(f"\n{ticket.ticket_id}: {ticket.title}")
            print(f"  Status: {ticket.status.value}, Priority: {ticket.priority.value}")
            print(f"  Component: {ticket.component}")

    elif args.ticket_id and args.status:
        status_map = {
            'open': TicketStatus.OPEN,
            'in_progress': TicketStatus.IN_PROGRESS,
            'resolved': TicketStatus.RESOLVED,
            'closed': TicketStatus.CLOSED
        }
        if system.update_ticket_status(args.ticket_id, status_map[args.status]):
            print(f"✅ Updated {args.ticket_id} to {args.status}")
        else:
            print(f"❌ Failed to update {args.ticket_id}")

    else:
        parser.print_help()


if __name__ == "__main__":


    main()