#!/usr/bin/env python3
"""
End-to-End Ticket Tracking System
Tracks tickets from origin (@ask Request ID) to completion with full lifecycle monitoring

Tags: #TRACKING #E2E #TICKETS #HELPDESK #PM #MONITORING @JARVIS @LUMINA
"""

import sys
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict, field
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_core.logging import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("TicketE2ETracker")


class TicketStage(Enum):
    """Ticket lifecycle stages"""
    ORIGIN = "origin"  # @ask Request ID created
    COLLATED = "collated"  # Linked to helpdesk ticket
    ASSIGNED = "assigned"  # Assigned to team/individual
    IN_PROGRESS = "in_progress"  # Work started
    REVIEW = "review"  # Under review
    TESTING = "testing"  # In testing
    RESOLVED = "resolved"  # Issue resolved
    CLOSED = "closed"  # Ticket closed
    COMPLETED = "completed"  # Fully completed


class TrackingEvent(Enum):
    """Types of tracking events"""
    CREATED = "created"
    STATUS_CHANGED = "status_changed"
    ASSIGNED = "assigned"
    UPDATED = "updated"
    COMMENTED = "commented"
    LINKED = "linked"
    MILESTONE = "milestone"
    COMPLETED = "completed"


@dataclass
class TrackingEventRecord:
    """Record of a tracking event"""
    event_id: str
    ticket_id: str
    event_type: str
    stage: str
    timestamp: str
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    user: Optional[str] = None
    system: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class E2ETicketTracking:
    """End-to-end ticket tracking record"""
    # Origin identifiers
    request_id: str  # @ask Request ID
    helpdesk_ticket: str  # PM ticket number
    change_request: Optional[str] = None  # CR number

    # Current state
    current_stage: str = TicketStage.ORIGIN.value
    status: str = "open"
    priority: str = "medium"

    # Assignment
    assigned_team: Optional[str] = None
    assigned_individual: Optional[str] = None

    # Timestamps
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    assigned_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    # Progress tracking
    progress_percentage: int = 0
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)

    # Links
    gitlens_ticket: Optional[str] = None
    gitlens_pr: Optional[str] = None
    related_tickets: List[str] = field(default_factory=list)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TicketE2ETracker:
    """
    End-to-End Ticket Tracking System

    Tracks tickets from origin (@ask Request ID) through all stages to completion.
    Provides full lifecycle monitoring, progress tracking, and status updates.
    """

    def __init__(self, project_root: Optional[Path] = None, db_path: Optional[Path] = None):
        """Initialize E2E tracking system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "ticket_e2e_tracking"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Database path
        if db_path is None:
            db_path = self.data_dir / "e2e_tracking.db"
        self.db_path = Path(db_path)

        # Initialize database
        self._init_database()

        logger.info("✅ End-to-End Ticket Tracking System initialized")
        logger.info(f"   Database: {self.db_path}")

    def _init_database(self):
        try:
            """Initialize SQLite database with schema"""
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Main tracking table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS e2e_tracking (
                    request_id TEXT PRIMARY KEY,
                    helpdesk_ticket TEXT NOT NULL,
                    change_request TEXT,
                    current_stage TEXT NOT NULL,
                    status TEXT NOT NULL,
                    priority TEXT,
                    assigned_team TEXT,
                    assigned_individual TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    assigned_at TEXT,
                    started_at TEXT,
                    completed_at TEXT,
                    progress_percentage INTEGER DEFAULT 0,
                    milestones TEXT,  -- JSON array
                    events TEXT,  -- JSON array
                    gitlens_ticket TEXT,
                    gitlens_pr TEXT,
                    related_tickets TEXT,  -- JSON array
                    metadata TEXT  -- JSON object
                )
            """)

            # Events table for detailed event tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tracking_events (
                    event_id TEXT PRIMARY KEY,
                    ticket_id TEXT NOT NULL,
                    request_id TEXT,
                    event_type TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    description TEXT,
                    metadata TEXT,  -- JSON object
                    user TEXT,
                    system TEXT,
                    FOREIGN KEY (request_id) REFERENCES e2e_tracking(request_id)
                )
            """)

            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_helpdesk_ticket ON e2e_tracking(helpdesk_ticket)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON e2e_tracking(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_stage ON e2e_tracking(current_stage)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ticket_id ON tracking_events(ticket_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_request_id ON tracking_events(request_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON tracking_events(timestamp)")

            conn.commit()
            conn.close()

            logger.info("✅ Database initialized with schema and indexes")

        except Exception as e:
            self.logger.error(f"Error in _init_database: {e}", exc_info=True)
            raise
    def create_tracking(
        self,
        request_id: str,
        helpdesk_ticket: str,
        change_request: Optional[str] = None,
        priority: str = "medium"
    ) -> E2ETicketTracking:
        """
        Create new E2E tracking record

        Args:
            request_id: @ask Request ID (origin)
            helpdesk_ticket: PM ticket number
            change_request: Change request number (optional)
            priority: Ticket priority

        Returns:
            Created tracking record
        """
        tracking = E2ETicketTracking(
            request_id=request_id,
            helpdesk_ticket=helpdesk_ticket,
            change_request=change_request,
            current_stage=TicketStage.ORIGIN.value,
            status="open",
            priority=priority
        )

        # Record origin event
        self._record_event(
            ticket_id=helpdesk_ticket,
            request_id=request_id,
            event_type=TrackingEvent.CREATED.value,
            stage=TicketStage.ORIGIN.value,
            description=f"Ticket created from @ask Request ID: {request_id}",
            metadata={"origin": "ask_request", "change_request": change_request}
        )

        # Save to database
        self._save_tracking(tracking)

        logger.info(f"✅ Created E2E tracking: {request_id} -> {helpdesk_ticket}")
        return tracking

    def update_stage(
        self,
        request_id: str,
        new_stage: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update ticket stage and record event

        Args:
            request_id: @ask Request ID
            new_stage: New stage (from TicketStage enum)
            description: Optional description
            metadata: Optional metadata

        Returns:
            True if successful
        """
        tracking = self.get_tracking(request_id)
        if not tracking:
            logger.error(f"Tracking not found for request_id: {request_id}")
            return False

        old_stage = tracking.current_stage
        tracking.current_stage = new_stage
        tracking.updated_at = datetime.now().isoformat()

        # Update timestamps based on stage
        if new_stage == TicketStage.IN_PROGRESS.value and not tracking.started_at:
            tracking.started_at = datetime.now().isoformat()
        elif new_stage == TicketStage.COMPLETED.value and not tracking.completed_at:
            tracking.completed_at = datetime.now().isoformat()

        # Record event
        event_desc = description or f"Stage changed: {old_stage} -> {new_stage}"
        event_metadata = metadata or {}
        event_metadata.update({"old_stage": old_stage, "new_stage": new_stage})
        self._record_event(
            ticket_id=tracking.helpdesk_ticket,
            request_id=request_id,
            event_type=TrackingEvent.STATUS_CHANGED.value,
            stage=new_stage,
            description=event_desc,
            metadata=event_metadata
        )

        # Update progress percentage based on stage
        tracking.progress_percentage = self._calculate_progress(new_stage)

        self._save_tracking(tracking)

        logger.info(f"✅ Updated stage: {request_id} -> {new_stage} ({tracking.progress_percentage}%)")
        return True

    def add_milestone(
        self,
        request_id: str,
        milestone_name: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add milestone to tracking

        Args:
            request_id: @ask Request ID
            milestone_name: Name of milestone
            description: Description
            metadata: Optional metadata

        Returns:
            True if successful
        """
        tracking = self.get_tracking(request_id)
        if not tracking:
            return False

        milestone = {
            "name": milestone_name,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }

        tracking.milestones.append(milestone)
        tracking.updated_at = datetime.now().isoformat()

        # Record event
        self._record_event(
            ticket_id=tracking.helpdesk_ticket,
            request_id=request_id,
            event_type=TrackingEvent.MILESTONE.value,
            stage=tracking.current_stage,
            description=f"Milestone: {milestone_name}",
            metadata={"milestone": milestone}
        )

        self._save_tracking(tracking)

        logger.info(f"✅ Added milestone: {request_id} -> {milestone_name}")
        return True

    def link_ticket(
        self,
        request_id: str,
        link_type: str,
        link_id: str,
        description: Optional[str] = None
    ) -> bool:
        """
        Link related ticket (GitLens, PR, etc.)

        Args:
            request_id: @ask Request ID
            link_type: Type of link (gitlens_ticket, gitlens_pr, related_ticket)
            link_id: ID of linked item
            description: Optional description

        Returns:
            True if successful
        """
        tracking = self.get_tracking(request_id)
        if not tracking:
            return False

        if link_type == "gitlens_ticket":
            tracking.gitlens_ticket = link_id
        elif link_type == "gitlens_pr":
            tracking.gitlens_pr = link_id
        elif link_type == "related_ticket":
            if link_id not in tracking.related_tickets:
                tracking.related_tickets.append(link_id)

        tracking.updated_at = datetime.now().isoformat()

        # Record event
        self._record_event(
            ticket_id=tracking.helpdesk_ticket,
            request_id=request_id,
            event_type=TrackingEvent.LINKED.value,
            stage=tracking.current_stage,
            description=description or f"Linked {link_type}: {link_id}",
            metadata={"link_type": link_type, "link_id": link_id}
        )

        self._save_tracking(tracking)

        logger.info(f"✅ Linked {link_type}: {request_id} -> {link_id}")
        return True

    def get_tracking(self, request_id: str) -> Optional[E2ETicketTracking]:
        try:
            """Get tracking record by request_id"""
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM e2e_tracking WHERE request_id = ?
            """, (request_id,))

            row = cursor.fetchone()
            conn.close()

            if not row:
                return None

            # Reconstruct from database row
            return self._row_to_tracking(row)

        except Exception as e:
            self.logger.error(f"Error in get_tracking: {e}", exc_info=True)
            raise
    def get_tracking_by_ticket(self, helpdesk_ticket: str) -> Optional[E2ETicketTracking]:
        try:
            """Get tracking record by helpdesk ticket number"""
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM e2e_tracking WHERE helpdesk_ticket = ?
            """, (helpdesk_ticket,))

            row = cursor.fetchone()
            conn.close()

            if not row:
                return None

            return self._row_to_tracking(row)

        except Exception as e:
            self.logger.error(f"Error in get_tracking_by_ticket: {e}", exc_info=True)
            raise
    def get_events(self, request_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        try:
            """Get all events for a ticket"""
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM tracking_events 
                WHERE request_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (request_id, limit))

            rows = cursor.fetchall()
            conn.close()

            columns = [desc[0] for desc in cursor.description]
            events = []
            for row in rows:
                event = dict(zip(columns, row))
                if event.get("metadata"):
                    event["metadata"] = json.loads(event["metadata"])
                events.append(event)

            return events

        except Exception as e:
            self.logger.error(f"Error in get_events: {e}", exc_info=True)
            raise
    def get_progress_report(self, request_id: str) -> Dict[str, Any]:
        """Get comprehensive progress report"""
        tracking = self.get_tracking(request_id)
        if not tracking:
            return {"error": "Tracking not found"}

        events = self.get_events(request_id)

        return {
            "request_id": tracking.request_id,
            "helpdesk_ticket": tracking.helpdesk_ticket,
            "change_request": tracking.change_request,
            "current_stage": tracking.current_stage,
            "status": tracking.status,
            "progress_percentage": tracking.progress_percentage,
            "milestones": tracking.milestones,
            "events_count": len(events),
            "recent_events": events[:10],
            "timeline": {
                "created_at": tracking.created_at,
                "assigned_at": tracking.assigned_at,
                "started_at": tracking.started_at,
                "completed_at": tracking.completed_at,
                "updated_at": tracking.updated_at
            },
            "links": {
                "gitlens_ticket": tracking.gitlens_ticket,
                "gitlens_pr": tracking.gitlens_pr,
                "related_tickets": tracking.related_tickets
            }
        }

    def _record_event(
        self,
        ticket_id: str,
        request_id: str,
        event_type: str,
        stage: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
        user: Optional[str] = None,
        system: Optional[str] = None
    ):
        """Record tracking event"""
        import uuid

        event = TrackingEventRecord(
            event_id=str(uuid.uuid4()),
            ticket_id=ticket_id,
            event_type=event_type,
            stage=stage,
            timestamp=datetime.now().isoformat(),
            description=description,
            metadata=metadata or {},
            user=user,
            system=system or "JARVIS"
        )

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO tracking_events (
                event_id, ticket_id, request_id, event_type, stage,
                timestamp, description, metadata, user, system
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event.event_id,
            event.ticket_id,
            request_id,
            event.event_type,
            event.stage,
            event.timestamp,
            event.description,
            json.dumps(event.metadata),
            event.user,
            event.system
        ))

        conn.commit()
        conn.close()

    def _save_tracking(self, tracking: E2ETicketTracking):
        """Save tracking record to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        data = tracking.to_dict()

        # Convert to JSON strings
        data["milestones"] = json.dumps(data["milestones"])
        data["events"] = json.dumps(data["events"])
        data["related_tickets"] = json.dumps(data["related_tickets"])
        data["metadata"] = json.dumps(data["metadata"])

        cursor.execute("""
            INSERT OR REPLACE INTO e2e_tracking (
                request_id, helpdesk_ticket, change_request, current_stage, status, priority,
                assigned_team, assigned_individual, created_at, updated_at, assigned_at,
                started_at, completed_at, progress_percentage, milestones, events,
                gitlens_ticket, gitlens_pr, related_tickets, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["request_id"],
            data["helpdesk_ticket"],
            data["change_request"],
            data["current_stage"],
            data["status"],
            data["priority"],
            data["assigned_team"],
            data["assigned_individual"],
            data["created_at"],
            data["updated_at"],
            data["assigned_at"],
            data["started_at"],
            data["completed_at"],
            data["progress_percentage"],
            data["milestones"],
            data["events"],
            data["gitlens_ticket"],
            data["gitlens_pr"],
            data["related_tickets"],
            data["metadata"]
        ))

        conn.commit()
        conn.close()

    def _row_to_tracking(self, row: tuple) -> E2ETicketTracking:
        """Convert database row to E2ETicketTracking object"""
        return E2ETicketTracking(
            request_id=row[0],
            helpdesk_ticket=row[1],
            change_request=row[2],
            current_stage=row[3],
            status=row[4],
            priority=row[5] or "medium",
            assigned_team=row[6],
            assigned_individual=row[7],
            created_at=row[8],
            updated_at=row[9],
            assigned_at=row[10],
            started_at=row[11],
            completed_at=row[12],
            progress_percentage=row[13] or 0,
            milestones=json.loads(row[14]) if row[14] else [],
            events=json.loads(row[15]) if row[15] else [],
            gitlens_ticket=row[16],
            gitlens_pr=row[17],
            related_tickets=json.loads(row[18]) if row[18] else [],
            metadata=json.loads(row[19]) if row[19] else {}
        )

    def _calculate_progress(self, stage: str) -> int:
        """Calculate progress percentage based on stage"""
        stage_progress = {
            TicketStage.ORIGIN.value: 0,
            TicketStage.COLLATED.value: 10,
            TicketStage.ASSIGNED.value: 20,
            TicketStage.IN_PROGRESS.value: 40,
            TicketStage.REVIEW.value: 70,
            TicketStage.TESTING.value: 85,
            TicketStage.RESOLVED.value: 95,
            TicketStage.CLOSED.value: 98,
            TicketStage.COMPLETED.value: 100
        }
        return stage_progress.get(stage, 0)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="End-to-End Ticket Tracking System")
    parser.add_argument("--create", action="store_true", help="Create new tracking")
    parser.add_argument("--request-id", type=str, help="@ask Request ID")
    parser.add_argument("--ticket", type=str, help="Helpdesk ticket number")
    parser.add_argument("--change-request", type=str, help="Change request number")
    parser.add_argument("--update-stage", type=str, metavar="STAGE", help="Update stage")
    parser.add_argument("--description", type=str, help="Description for update")
    parser.add_argument("--milestone", type=str, help="Add milestone name")
    parser.add_argument("--report", action="store_true", help="Get progress report")

    args = parser.parse_args()

    tracker = TicketE2ETracker()

    if args.create:
        if not args.request_id or not args.ticket:
            print("❌ --request-id and --ticket required for --create")
            sys.exit(1)

        tracking = tracker.create_tracking(
            request_id=args.request_id,
            helpdesk_ticket=args.ticket,
            change_request=args.change_request
        )
        print(f"✅ Created tracking: {tracking.request_id} -> {tracking.helpdesk_ticket}")

    elif args.update_stage:
        if not args.request_id:
            print("❌ --request-id required for --update-stage")
            sys.exit(1)

        tracker.update_stage(args.request_id, args.update_stage, description=args.description)
        print(f"✅ Updated stage: {args.request_id} -> {args.update_stage}")

    elif args.milestone:
        if not args.request_id:
            print("❌ --request-id required for --milestone")
            sys.exit(1)

        tracker.add_milestone(args.request_id, args.milestone, f"Milestone: {args.milestone}")
        print(f"✅ Added milestone: {args.request_id} -> {args.milestone}")

    elif args.report:
        if not args.request_id:
            print("❌ --request-id required for --report")
            sys.exit(1)

        report = tracker.get_progress_report(args.request_id)
        print(json.dumps(report, indent=2))

    else:
        parser.print_help()
