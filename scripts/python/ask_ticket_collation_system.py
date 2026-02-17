#!/usr/bin/env python3
"""
@ask Ticket Collation System

Creates database-ready collated data linking:
- @ask directives (Request IDs)
- Helpdesk ticket numbers
- GitLens ticket/PR numbers
- Relevant @tags for context
- @syphon pattern extraction
- Delegation and follow-up flags
- Team/individual assignments

Tags: #ASK #HELPDESK #GITLENS #SYPHON #COLLATION #DATABASE @JARVIS @LUMINA
"""

import sys
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from dataclasses import dataclass, asdict, field
from enum import Enum

from lumina_core.paths import get_script_dir, setup_paths
script_dir = get_script_dir()
project_root = script_dir.parent.parent
setup_paths()
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_core.logging import get_logger
    # Using lumina_core.logging.get_logger
except ImportError:
        from lumina_core.logging import get_logger

logger = get_logger("AskTicketCollation")


class TicketStatus(Enum):
    """Ticket status enumeration"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    DELEGATED = "delegated"
    FOLLOW_UP = "follow_up"
    RESOLVED = "resolved"
    CLOSED = "closed"


class DelegationFlag(Enum):
    """Delegation flag types"""
    NONE = "none"
    PENDING = "pending"
    DELEGATED = "delegated"
    FOLLOW_UP_REQUIRED = "follow_up_required"
    ESCALATED = "escalated"


@dataclass
class AskTicketRecord:
    """
    Database-ready record for @ask ticket collation

    Links @ask (Request ID) with helpdesk tickets, GitLens tickets,
    tags, patterns, and assignments.
    """
    # Core identifiers
    ask_id: str  # @ask directive / Request ID
    helpdesk_ticket: Optional[str] = None  # Helpdesk ticket number
    gitlens_ticket: Optional[str] = None  # GitLens issue/ticket number
    gitlens_pr: Optional[str] = None  # GitLens pull request number

    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    source: str = "user_report"  # Source of @ask

    # Content
    ask_text: str = ""  # Original @ask directive text
    description: str = ""  # Expanded description

    # Tags and context
    tags: List[str] = field(default_factory=list)  # All @tags and #tags
    mentions: List[str] = field(default_factory=list)  # @mentions
    hashtags: List[str] = field(default_factory=list)  # #hashtags

    # @syphon pattern extraction
    syphon_patterns: List[str] = field(default_factory=list)  # Extracted patterns
    syphon_intelligence: Dict[str, Any] = field(default_factory=dict)  # SYPHON data

    # Delegation and follow-up
    delegation_flag: str = DelegationFlag.NONE.value
    requires_follow_up: bool = False
    follow_up_notes: str = ""

    # Assignment
    assigned_team: Optional[str] = None
    assigned_individual: Optional[str] = None
    assigned_at: Optional[str] = None

    # Status
    status: str = TicketStatus.PENDING.value
    priority: str = "medium"  # low, medium, high, critical

    # Relationships
    related_asks: List[str] = field(default_factory=list)  # Related @ask IDs
    related_tickets: List[str] = field(default_factory=list)  # Related ticket numbers

    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AskTicketRecord':
        """Create from dictionary"""
        return cls(**data)


class AskTicketCollationSystem:
    """
    Database-ready collation system for @ask, helpdesk, and GitLens tickets

    Creates queryable, cross-referenceable data linking all ticket systems
    with @syphon pattern extraction and delegation management.
    """

    def __init__(self, project_root: Optional[Path] = None, db_path: Optional[Path] = None):
        """Initialize collation system"""
        if project_root is None:
            from lumina_core.paths import get_project_root
        project_root = get_project_root()

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "ask_ticket_collation"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Database path
        if db_path is None:
            db_path = self.data_dir / "ask_tickets.db"
        self.db_path = Path(db_path)

        # Initialize database
        self._init_database()

        logger.info("✅ @ask Ticket Collation System initialized")
        logger.info(f"   Database: {self.db_path}")
        logger.info(f"   Data directory: {self.data_dir}")

    def _init_database(self):
        try:
            """Initialize SQLite database with schema"""
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create main table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ask_tickets (
                    ask_id TEXT PRIMARY KEY,
                    helpdesk_ticket TEXT,
                    gitlens_ticket TEXT,
                    gitlens_pr TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    source TEXT,
                    ask_text TEXT,
                    description TEXT,
                    tags TEXT,  -- JSON array
                    mentions TEXT,  -- JSON array
                    hashtags TEXT,  -- JSON array
                    syphon_patterns TEXT,  -- JSON array
                    syphon_intelligence TEXT,  -- JSON object
                    delegation_flag TEXT,
                    requires_follow_up INTEGER,
                    follow_up_notes TEXT,
                    assigned_team TEXT,
                    assigned_individual TEXT,
                    assigned_at TEXT,
                    status TEXT,
                    priority TEXT,
                    related_asks TEXT,  -- JSON array
                    related_tickets TEXT,  -- JSON array
                    metadata TEXT  -- JSON object
                )
            """)

            # Create indexes for fast queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_helpdesk_ticket 
                ON ask_tickets(helpdesk_ticket)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_gitlens_ticket 
                ON ask_tickets(gitlens_ticket)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_gitlens_pr 
                ON ask_tickets(gitlens_pr)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_status 
                ON ask_tickets(status)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_assigned_team 
                ON ask_tickets(assigned_team)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_assigned_individual 
                ON ask_tickets(assigned_individual)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_delegation_flag 
                ON ask_tickets(delegation_flag)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_requires_follow_up 
                ON ask_tickets(requires_follow_up)
            """)

            conn.commit()
            conn.close()

            logger.info("✅ Database initialized with schema and indexes")

        except Exception as e:
            self.logger.error(f"Error in _init_database: {e}", exc_info=True)
            raise
    def _extract_tags(self, text: str) -> Dict[str, List[str]]:
        """
        Extract @tags and #tags from text

        Returns:
            Dictionary with 'mentions', 'hashtags', and 'tags' lists
        """
        import re

        mentions = re.findall(r'@(\w+)', text)
        hashtags = re.findall(r'#(\w+)', text)

        # Combine all tags
        all_tags = list(set(mentions + hashtags))

        return {
            "mentions": list(set(mentions)),
            "hashtags": list(set(hashtags)),
            "tags": all_tags
        }

    def _syphon_extract_patterns(self, ask_text: str, tags: List[str]) -> Dict[str, Any]:
        """
        Extract patterns using @syphon logic

        Args:
            ask_text: The @ask directive text
            tags: List of tags

        Returns:
            Dictionary with syphon_patterns and syphon_intelligence
        """
        patterns = []
        intelligence = {
            "extracted_at": datetime.now().isoformat(),
            "patterns": [],
            "insights": [],
            "actionable_items": []
        }

        # Pattern extraction logic
        # 1. Extract workflow patterns
        if any(tag in ["workflow", "process", "automation"] for tag in tags):
            patterns.append("workflow_pattern")
            intelligence["insights"].append("Workflow-related request")

        # 2. Extract system patterns
        system_tags = ["jarvis", "r5", "v3", "marvin", "lumina"]
        found_systems = [tag for tag in tags if tag.lower() in system_tags]
        if found_systems:
            patterns.append("system_integration_pattern")
            intelligence["insights"].append(f"Integration with: {', '.join(found_systems)}")

        # 3. Extract error patterns
        error_keywords = ["error", "fix", "bug", "issue", "problem", "fail"]
        if any(keyword in ask_text.lower() for keyword in error_keywords):
            patterns.append("error_resolution_pattern")
            intelligence["insights"].append("Error resolution request")

        # 4. Extract feature patterns
        feature_keywords = ["add", "create", "implement", "new", "feature"]
        if any(keyword in ask_text.lower() for keyword in feature_keywords):
            patterns.append("feature_development_pattern")
            intelligence["insights"].append("Feature development request")

        # 5. Extract optimization patterns
        opt_keywords = ["optimize", "improve", "enhance", "performance", "speed"]
        if any(keyword in ask_text.lower() for keyword in opt_keywords):
            patterns.append("optimization_pattern")
            intelligence["insights"].append("Optimization request")

        intelligence["patterns"] = patterns

        return {
            "syphon_patterns": patterns,
            "syphon_intelligence": intelligence
        }

    def _determine_delegation(self, tags: List[str], patterns: List[str]) -> Dict[str, Any]:
        """
        Determine delegation requirements based on tags and patterns

        Returns:
            Dictionary with delegation_flag and requires_follow_up
        """
        delegation_flag = DelegationFlag.NONE.value
        requires_follow_up = False

        # Check for delegation indicators
        delegation_tags = ["delegate", "assign", "helpdesk", "team"]
        if any(tag.lower() in delegation_tags for tag in tags):
            delegation_flag = DelegationFlag.PENDING.value
            requires_follow_up = True

        # Check for escalation indicators
        escalation_tags = ["escalate", "urgent", "critical", "priority"]
        if any(tag.lower() in escalation_tags for tag in tags):
            delegation_flag = DelegationFlag.ESCALATED.value
            requires_follow_up = True

        # Check for follow-up indicators
        followup_tags = ["followup", "follow_up", "track", "monitor"]
        if any(tag.lower() in followup_tags for tag in tags):
            requires_follow_up = True

        return {
            "delegation_flag": delegation_flag,
            "requires_follow_up": requires_follow_up
        }

    def _assign_ticket(
        self,
        tags: List[str],
        patterns: List[str],
        ask_text: str
    ) -> Dict[str, Optional[str]]:
        """
        Assign ticket to team/individual based on tags and patterns

        Returns:
            Dictionary with assigned_team and assigned_individual
        """
        assigned_team = None
        assigned_individual = None

        # Team assignment logic based on tags
        team_mapping = {
            "jarvis": "JARVIS_TEAM",
            "r5": "R5_TEAM",
            "v3": "V3_TEAM",
            "marvin": "MARVIN_TEAM",
            "helpdesk": "HELPDESK_TEAM",
            "aimlsea": "AIMLSEA_TEAM",
            "systems": "SYSTEMS_TEAM",
            "devops": "DEVOPS_TEAM"
        }

        for tag in tags:
            tag_lower = tag.lower()
            if tag_lower in team_mapping:
                assigned_team = team_mapping[tag_lower]
                break

        # Default to helpdesk if no specific team
        if not assigned_team:
            assigned_team = "HELPDESK_TEAM"

        return {
            "assigned_team": assigned_team,
            "assigned_individual": assigned_individual  # Can be set manually later
        }

    def collate_ask(
        self,
        ask_id: str,
        ask_text: str,
        helpdesk_ticket: Optional[str] = None,
        gitlens_ticket: Optional[str] = None,
        gitlens_pr: Optional[str] = None,
        source: str = "user_report",
        description: Optional[str] = None
    ) -> AskTicketRecord:
        """
        Collate @ask with tickets and extract all relevant data

        Args:
            ask_id: @ask directive / Request ID
            ask_text: Original @ask directive text
            helpdesk_ticket: Helpdesk ticket number
            gitlens_ticket: GitLens ticket/issue number
            gitlens_pr: GitLens pull request number
            source: Source of @ask
            description: Optional expanded description

        Returns:
            AskTicketRecord with all collated data
        """
        logger.info(f"📋 Collating @ask: {ask_id}")

        # Extract tags
        tag_data = self._extract_tags(ask_text)
        mentions = tag_data["mentions"]
        hashtags = tag_data["hashtags"]
        all_tags = tag_data["tags"]

        # Extract @syphon patterns
        syphon_data = self._syphon_extract_patterns(ask_text, all_tags)
        syphon_patterns = syphon_data["syphon_patterns"]
        syphon_intelligence = syphon_data["syphon_intelligence"]

        # Determine delegation
        delegation_data = self._determine_delegation(all_tags, syphon_patterns)

        # Assign ticket
        assignment_data = self._assign_ticket(all_tags, syphon_patterns, ask_text)

        # Create record
        record = AskTicketRecord(
            ask_id=ask_id,
            helpdesk_ticket=helpdesk_ticket,
            gitlens_ticket=gitlens_ticket,
            gitlens_pr=gitlens_pr,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            source=source,
            ask_text=ask_text,
            description=description or ask_text,
            tags=all_tags,
            mentions=mentions,
            hashtags=hashtags,
            syphon_patterns=syphon_patterns,
            syphon_intelligence=syphon_intelligence,
            delegation_flag=delegation_data["delegation_flag"],
            requires_follow_up=delegation_data["requires_follow_up"],
            assigned_team=assignment_data["assigned_team"],
            assigned_individual=assignment_data["assigned_individual"],
            assigned_at=datetime.now().isoformat() if assignment_data["assigned_team"] else None,
            status=TicketStatus.PENDING.value,
            priority="high" if delegation_data["requires_follow_up"] else "medium"
        )

        # Save to database
        self._save_record(record)

        # Send email notification
        try:
            from ask_ticket_email_notifier import AskTicketEmailNotifier
            email_notifier = AskTicketEmailNotifier()
            email_notifier.send_ticket_notification(record)
        except Exception as e:
            logger.warning(f"Could not send email notification: {e}")

        logger.info(f"✅ Collated @ask: {ask_id}")
        logger.info(f"   Helpdesk: {helpdesk_ticket or 'None'}")
        logger.info(f"   GitLens Ticket: {gitlens_ticket or 'None'}")
        logger.info(f"   GitLens PR: {gitlens_pr or 'None'}")
        logger.info(f"   Tags: {len(all_tags)} tags")
        logger.info(f"   Patterns: {len(syphon_patterns)} patterns")
        logger.info(f"   Assigned to: {assignment_data['assigned_team']}")

        return record

    def _save_record(self, record: AskTicketRecord):
        try:
            """Save record to database"""
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            data = record.to_dict()

            # Convert lists/dicts to JSON strings
            data["tags"] = json.dumps(data["tags"])
            data["mentions"] = json.dumps(data["mentions"])
            data["hashtags"] = json.dumps(data["hashtags"])
            data["syphon_patterns"] = json.dumps(data["syphon_patterns"])
            data["syphon_intelligence"] = json.dumps(data["syphon_intelligence"])
            data["related_asks"] = json.dumps(data["related_asks"])
            data["related_tickets"] = json.dumps(data["related_tickets"])
            data["metadata"] = json.dumps(data["metadata"])
            data["requires_follow_up"] = 1 if data["requires_follow_up"] else 0

            # Insert or replace
            cursor.execute("""
                INSERT OR REPLACE INTO ask_tickets (
                    ask_id, helpdesk_ticket, gitlens_ticket, gitlens_pr,
                    created_at, updated_at, source, ask_text, description,
                    tags, mentions, hashtags, syphon_patterns, syphon_intelligence,
                    delegation_flag, requires_follow_up, follow_up_notes,
                    assigned_team, assigned_individual, assigned_at,
                    status, priority, related_asks, related_tickets, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["ask_id"],
                data["helpdesk_ticket"],
                data["gitlens_ticket"],
                data["gitlens_pr"],
                data["created_at"],
                data["updated_at"],
                data["source"],
                data["ask_text"],
                data["description"],
                data["tags"],
                data["mentions"],
                data["hashtags"],
                data["syphon_patterns"],
                data["syphon_intelligence"],
                data["delegation_flag"],
                data["requires_follow_up"],
                data["follow_up_notes"],
                data["assigned_team"],
                data["assigned_individual"],
                data["assigned_at"],
                data["status"],
                data["priority"],
                data["related_asks"],
                data["related_tickets"],
                data["metadata"]
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"Error in _save_record: {e}", exc_info=True)
            raise
    def query(
        self,
        ask_id: Optional[str] = None,
        helpdesk_ticket: Optional[str] = None,
        gitlens_ticket: Optional[str] = None,
        gitlens_pr: Optional[str] = None,
        status: Optional[str] = None,
        assigned_team: Optional[str] = None,
        assigned_individual: Optional[str] = None,
        delegation_flag: Optional[str] = None,
        requires_follow_up: Optional[bool] = None,
        tag: Optional[str] = None
    ) -> List[AskTicketRecord]:
        """
        Query records with cross-referencing

        Args:
            ask_id: Filter by @ask ID
            helpdesk_ticket: Filter by helpdesk ticket
            gitlens_ticket: Filter by GitLens ticket
            gitlens_pr: Filter by GitLens PR
            status: Filter by status
            assigned_team: Filter by assigned team
            assigned_individual: Filter by assigned individual
            delegation_flag: Filter by delegation flag
            requires_follow_up: Filter by follow-up requirement
            tag: Filter by tag (searches in tags, mentions, hashtags)

        Returns:
            List of matching AskTicketRecord objects
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        conditions = []
        params = []

        if ask_id:
            conditions.append("ask_id = ?")
            params.append(ask_id)
        if helpdesk_ticket:
            conditions.append("helpdesk_ticket = ?")
            params.append(helpdesk_ticket)
        if gitlens_ticket:
            conditions.append("gitlens_ticket = ?")
            params.append(gitlens_ticket)
        if gitlens_pr:
            conditions.append("gitlens_pr = ?")
            params.append(gitlens_pr)
        if status:
            conditions.append("status = ?")
            params.append(status)
        if assigned_team:
            conditions.append("assigned_team = ?")
            params.append(assigned_team)
        if assigned_individual:
            conditions.append("assigned_individual = ?")
            params.append(assigned_individual)
        if delegation_flag:
            conditions.append("delegation_flag = ?")
            params.append(delegation_flag)
        if requires_follow_up is not None:
            conditions.append("requires_follow_up = ?")
            params.append(1 if requires_follow_up else 0)
        if tag:
            conditions.append("(tags LIKE ? OR mentions LIKE ? OR hashtags LIKE ?)")
            tag_pattern = f'%"{tag}"%'
            params.extend([tag_pattern, tag_pattern, tag_pattern])

        query = "SELECT * FROM ask_tickets"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        records = []
        for row in rows:
            data = dict(row)
            # Parse JSON fields
            for json_field in ["tags", "mentions", "hashtags", "syphon_patterns", 
                             "syphon_intelligence", "related_asks", "related_tickets", "metadata"]:
                if data[json_field]:
                    data[json_field] = json.loads(data[json_field])
            data["requires_follow_up"] = bool(data["requires_follow_up"])
            records.append(AskTicketRecord.from_dict(data))

        conn.close()

        return records

    def cross_reference(
        self,
        identifier: str,
        identifier_type: str = "auto"
    ) -> Dict[str, Any]:
        """
        Cross-reference across all ticket systems

        Args:
            identifier: The identifier to search for
            identifier_type: Type of identifier (auto, ask_id, helpdesk, gitlens_ticket, gitlens_pr)

        Returns:
            Dictionary with all related records
        """
        if identifier_type == "auto":
            # Auto-detect type
            if identifier.startswith("TICKET-"):
                identifier_type = "helpdesk"
            elif identifier.startswith("#") or identifier.startswith("PR#"):
                if "PR" in identifier.upper():
                    identifier_type = "gitlens_pr"
                else:
                    identifier_type = "gitlens_ticket"
            else:
                identifier_type = "ask_id"

        results = {}

        if identifier_type == "ask_id":
            records = self.query(ask_id=identifier)
            if records:
                record = records[0]
                results["primary"] = record.to_dict()
                # Find related
                if record.helpdesk_ticket:
                    results["helpdesk"] = self.query(helpdesk_ticket=record.helpdesk_ticket)
                if record.gitlens_ticket:
                    results["gitlens_ticket"] = self.query(gitlens_ticket=record.gitlens_ticket)
                if record.gitlens_pr:
                    results["gitlens_pr"] = self.query(gitlens_pr=record.gitlens_pr)

        elif identifier_type == "helpdesk":
            records = self.query(helpdesk_ticket=identifier)
            results["helpdesk"] = [r.to_dict() for r in records]
            # Find related asks
            if records:
                ask_ids = [r.ask_id for r in records]
                results["related_asks"] = [r.to_dict() for r in self.query(ask_id=ask_ids[0]) if ask_ids]

        elif identifier_type == "gitlens_ticket":
            records = self.query(gitlens_ticket=identifier)
            results["gitlens_ticket"] = [r.to_dict() for r in records]

        elif identifier_type == "gitlens_pr":
            records = self.query(gitlens_pr=identifier)
            results["gitlens_pr"] = [r.to_dict() for r in records]

        return results

    def export_to_json(self, output_path: Optional[Path] = None) -> Path:
        try:
            """Export all records to JSON for backup/analysis"""
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = self.data_dir / f"ask_tickets_export_{timestamp}.json"

            records = self.query()
            data = {
                "exported_at": datetime.now().isoformat(),
                "total_records": len(records),
                "records": [r.to_dict() for r in records]
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Exported {len(records)} records to {output_path}")
            return output_path


        except Exception as e:
            self.logger.error(f"Error in export_to_json: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point for testing"""
        import argparse

        parser = argparse.ArgumentParser(
            description="@ask Ticket Collation System - Database-ready ticket tracking"
        )
        parser.add_argument("--collate", nargs=5, metavar=("ASK_ID", "ASK_TEXT", "HELPDESK", "GITLENS_TICKET", "GITLENS_PR"),
                           help="Collate an @ask with tickets")
        parser.add_argument("--query", metavar="ASK_ID", help="Query by @ask ID")
        parser.add_argument("--cross-ref", metavar="IDENTIFIER", help="Cross-reference identifier")
        parser.add_argument("--export", action="store_true", help="Export all to JSON")

        args = parser.parse_args()

        system = AskTicketCollationSystem()

        if args.collate:
            ask_id, ask_text, helpdesk, gitlens_ticket, gitlens_pr = args.collate
            record = system.collate_ask(
                ask_id=ask_id,
                ask_text=ask_text,
                helpdesk_ticket=helpdesk if helpdesk != "None" else None,
                gitlens_ticket=gitlens_ticket if gitlens_ticket != "None" else None,
                gitlens_pr=gitlens_pr if gitlens_pr != "None" else None
            )
            print(f"\n✅ Collated @ask: {ask_id}")
            print(f"   Record: {json.dumps(record.to_dict(), indent=2)}")

        elif args.query:
            records = system.query(ask_id=args.query)
            if records:
                print(f"\n📋 Found {len(records)} record(s):")
                for record in records:
                    print(json.dumps(record.to_dict(), indent=2))
            else:
                print(f"\n❌ No records found for @ask ID: {args.query}")

        elif args.cross_ref:
            results = system.cross_reference(args.cross_ref)
            print(f"\n🔗 Cross-reference results:")
            print(json.dumps(results, indent=2))

        elif args.export:
            output_path = system.export_to_json()
            print(f"\n✅ Exported to: {output_path}")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()