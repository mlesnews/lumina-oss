#!/usr/bin/env python3
"""
JARVIS Tickets to Holocron & Database
Migrates tickets to Holocron Archive and imports into enhanced_memory database.

Tags: #TICKETS #HOLOCRON #DATABASE #HELPDESK @AUTO @R5
"""

import sys
import json
import sqlite3
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

logger = get_logger("JARVISTicketsToHolocronDB")


class TicketsToHolocronDB:
    """
    Migrates tickets to Holocron Archive and imports into enhanced_memory database.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Directories
        self.ticket_dir = project_root / "data" / "pr_tickets" / "tickets"
        self.holocron_dir = project_root / "data" / "holocron"
        self.tickets_holocron_dir = self.holocron_dir / "tickets"
        self.tickets_holocron_dir.mkdir(parents=True, exist_ok=True)
        self.holocron_index_file = self.holocron_dir / "HOLOCRON_INDEX.json"

        # Database
        self.db_path = project_root / "data" / "jarvis_memory" / "enhanced_memory.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.logger.info("✅ Tickets to Holocron & DB Migrator initialized")
        self.logger.info(f"   Ticket Directory: {self.ticket_dir}")
        self.logger.info(f"   Holocron Directory: {self.tickets_holocron_dir}")
        self.logger.info(f"   Database: {self.db_path}")

    def _ensure_database_tables(self) -> bool:
        """Ensure tickets table exists in database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Create tickets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    ticket_number TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    change_type TEXT,
                    severity TEXT,
                    status TEXT,
                    created_at TEXT,
                    assigned_by TEXT,
                    assigned_at TEXT,
                    location TEXT,
                    pr_number TEXT,
                    files_changed TEXT,
                    related_issues TEXT,
                    team_assignment TEXT,
                    holocron_entry_id TEXT,
                    holocron_location TEXT,
                    created_timestamp TEXT,
                    updated_timestamp TEXT,
                    FOREIGN KEY (pr_number) REFERENCES prs(pr_number)
                )
            """)

            # Create PRs table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prs (
                    pr_number TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    change_type TEXT,
                    severity TEXT,
                    status TEXT,
                    created_at TEXT,
                    files_changed TEXT,
                    related_issues TEXT,
                    ticket_number TEXT,
                    gitlens_reference TEXT,
                    github_url TEXT,
                    created_timestamp TEXT,
                    updated_timestamp TEXT,
                    FOREIGN KEY (ticket_number) REFERENCES tickets(ticket_number)
                )
            """)

            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tickets_team ON tickets(team_assignment)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tickets_created ON tickets(created_at)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_prs_status ON prs(status)
            """)

            conn.commit()
            conn.close()

            self.logger.info("✅ Database tables ensured")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to ensure database tables: {e}", exc_info=True)
            return False

    def _generate_holocron_entry_id(self, ticket_number: str) -> str:
        """Generate Holocron entry ID for ticket"""
        # Format: HOLOCRON-TICKET-XXXX or PMXXXXXXXXX
        if ticket_number.startswith("HELPDESK-"):
            ticket_num = ticket_number.replace("HELPDESK-", "")
            return f"HOLOCRON-TICKET-{ticket_num}"
        else:
            # For PM syntax, use it directly as the entry ID suffix
            return f"HOLOCRON-TICKET-{ticket_number}"

    def _create_holocron_entry(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        try:
            """Create Holocron entry for ticket"""
            ticket_number = ticket.get("ticket_number", "UNKNOWN")
            entry_id = self._generate_holocron_entry_id(ticket_number)

            # Generate markdown content
            markdown_content = self._generate_markdown_content(ticket)

            # Save markdown file
            markdown_filename = f"{ticket_number}.md"
            markdown_filepath = self.tickets_holocron_dir / markdown_filename
            with open(markdown_filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            # Save JSON file
            json_filename = f"{ticket_number}.json"
            json_filepath = self.tickets_holocron_dir / json_filename
            with open(json_filepath, 'w', encoding='utf-8') as f:
                json.dump(ticket, f, indent=2, default=str)

            # Create entry metadata
            team_assignment = ticket.get("team_assignment", {})
            tags = [
                "#ticket",
                "#helpdesk",
                f"#{ticket.get('change_type', 'unknown')}",
                f"#{ticket.get('severity', 'unknown')}",
                f"#{ticket.get('status', 'unknown')}"
            ]

            if team_assignment:
                tags.append(f"#{team_assignment.get('team_id', 'unknown')}")
                tags.append(f"#{team_assignment.get('division', 'unknown').lower().replace(' ', '_')}")

            entry = {
                "entry_id": entry_id,
                "title": ticket.get("title", "Unknown Ticket"),
                "location": str(markdown_filepath.relative_to(self.project_root)),
                "json_location": str(json_filepath.relative_to(self.project_root)),
                "classification": "Helpdesk Ticket",
                "helpdesk_location": ticket.get("location", "@helpdesk"),
                "associated_droids": [
                    team_assignment.get("team_manager", "@c3po"),
                    team_assignment.get("technical_lead", "@r2d2")
                ] if team_assignment else ["@c3po"],
                "tags": tags,
                "status": ticket.get("status", "open"),
                "last_updated": ticket.get("assigned_at") or ticket.get("created_at", datetime.now().isoformat()),
                "integration_points": {
                    "primary_droid": team_assignment.get("team_manager", "@c3po") if team_assignment else "@c3po",
                    "supporting_droids": [
                        team_assignment.get("technical_lead", "@r2d2")
                    ] if team_assignment and team_assignment.get("technical_lead") else ["@r2d2"],
                    "workflow_triggers": [
                        "@helpdesk",
                        "@ticket",
                        ticket_number
                    ],
                    "related_entries": []
                },
                "metadata": {
                    "ticket_number": ticket_number,
                    "pr_number": ticket.get("pr_number"),
                    "change_type": ticket.get("change_type"),
                    "severity": ticket.get("severity"),
                    "team_id": team_assignment.get("team_id") if team_assignment else None,
                    "team_name": team_assignment.get("team_name") if team_assignment else None,
                    "generated_by": "jarvis_tickets_to_holocron_db.py",
                    "generated_at": datetime.now().isoformat()
                }
            }

            return entry

        except Exception as e:
            self.logger.error(f"Error in _create_holocron_entry: {e}", exc_info=True)
            raise
    def _generate_markdown_content(self, ticket: Dict[str, Any]) -> str:
        """Generate markdown content for ticket"""
        ticket_number = ticket.get("ticket_number", "UNKNOWN")
        team_assignment = ticket.get("team_assignment", {})

        md = []
        md.append(f"# {ticket.get('title', 'Unknown Ticket')}")
        md.append("")
        md.append(f"**Ticket Number:** {ticket_number}")
        md.append(f"**Entry ID:** {self._generate_holocron_entry_id(ticket_number)}")
        md.append(f"**Status:** {ticket.get('status', 'unknown')}")
        md.append(f"**Created:** {ticket.get('created_at', 'unknown')}")
        md.append("")

        if ticket.get("pr_number"):
            md.append(f"**Related PR:** {ticket.get('pr_number')}")
            md.append("")

        md.append("## Description")
        md.append("")
        md.append(ticket.get("description", "No description provided"))
        md.append("")

        if team_assignment:
            md.append("## Team Assignment")
            md.append("")
            md.append(f"- **Team:** {team_assignment.get('team_name', 'N/A')}")
            md.append(f"- **Division:** {team_assignment.get('division', 'N/A')}")
            md.append(f"- **Team Manager:** {team_assignment.get('team_manager', 'N/A')}")
            md.append(f"- **Technical Lead:** {team_assignment.get('technical_lead', 'N/A')}")
            if team_assignment.get('business_lead'):
                md.append(f"- **Business Lead:** {team_assignment.get('business_lead')}")
            md.append(f"- **Primary Assignee:** {team_assignment.get('primary_assignee', 'N/A')}")
            md.append("")

        md.append("## Details")
        md.append("")
        md.append(f"- **Change Type:** {ticket.get('change_type', 'N/A')}")
        md.append(f"- **Severity:** {ticket.get('severity', 'N/A')}")
        md.append(f"- **Assigned By:** {ticket.get('assigned_by', 'N/A')}")
        md.append(f"- **Location:** {ticket.get('location', 'N/A')}")
        md.append("")

        if ticket.get("files_changed"):
            md.append("## Files Changed")
            md.append("")
            for file in ticket.get("files_changed", []):
                md.append(f"- {file}")
            md.append("")

        if ticket.get("related_issues"):
            md.append("## Related Issues")
            md.append("")
            for issue in ticket.get("related_issues", []):
                md.append(f"- {issue}")
            md.append("")

        return "\n".join(md)

    def _import_ticket_to_database(self, ticket: Dict[str, Any], holocron_entry: Dict[str, Any]) -> bool:
        """Import ticket into database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Prepare ticket data
            team_assignment_json = json.dumps(ticket.get("team_assignment", {}))
            files_changed_json = json.dumps(ticket.get("files_changed", []))
            related_issues_json = json.dumps(ticket.get("related_issues", []))

            # Insert or update ticket
            cursor.execute("""
                INSERT OR REPLACE INTO tickets (
                    ticket_number, title, description, change_type, severity, status,
                    created_at, assigned_by, assigned_at, location, pr_number,
                    files_changed, related_issues, team_assignment,
                    holocron_entry_id, holocron_location,
                    created_timestamp, updated_timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ticket.get("ticket_number"),
                ticket.get("title"),
                ticket.get("description"),
                ticket.get("change_type"),
                ticket.get("severity"),
                ticket.get("status"),
                ticket.get("created_at"),
                ticket.get("assigned_by"),
                ticket.get("assigned_at"),
                ticket.get("location"),
                ticket.get("pr_number"),
                files_changed_json,
                related_issues_json,
                team_assignment_json,
                holocron_entry.get("entry_id"),
                holocron_entry.get("location"),
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))

            conn.commit()
            conn.close()

            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to import ticket to database: {e}", exc_info=True)
            return False

    def _import_pr_to_database(self, pr: Dict[str, Any]) -> bool:
        """Import PR into database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Prepare PR data
            files_changed_json = json.dumps(pr.get("files_changed", []))
            related_issues_json = json.dumps(pr.get("related_issues", []))

            # Insert or update PR
            cursor.execute("""
                INSERT OR REPLACE INTO prs (
                    pr_number, title, description, change_type, severity, status,
                    created_at, files_changed, related_issues, ticket_number,
                    gitlens_reference, github_url,
                    created_timestamp, updated_timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pr.get("pr_number"),
                pr.get("title"),
                pr.get("description"),
                pr.get("change_type"),
                pr.get("severity"),
                pr.get("status"),
                pr.get("created_at"),
                files_changed_json,
                related_issues_json,
                pr.get("ticket_number"),
                pr.get("gitlens_reference"),
                pr.get("github_url"),
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))

            conn.commit()
            conn.close()

            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to import PR to database: {e}", exc_info=True)
            return False

    def _update_holocron_index(self, entry: Dict[str, Any]) -> bool:
        """Update HOLOCRON_INDEX.json with ticket entry"""
        try:
            # Read existing index
            if self.holocron_index_file.exists():
                with open(self.holocron_index_file, 'r', encoding='utf-8') as f:
                    index = json.load(f)
            else:
                index = {
                    "archive_metadata": {
                        "name": "Holocron Archive - Master Index",
                        "version": "1.0.0",
                        "last_updated": datetime.now().isoformat(),
                        "status": "operational",
                        "classification": "general_access",
                        "purpose": "Central catalog of all @helpdesk tagged entries and system documentation",
                        "location": "data/holocron/",
                        "maintained_by": "@r5 (Knowledge & Context Matrix Specialist)"
                    },
                    "entries": {}
                }

            # Ensure tickets category exists
            if "entries" not in index:
                index["entries"] = {}
            if "tickets" not in index["entries"]:
                index["entries"]["tickets"] = {}

            # Add ticket entry
            ticket_number = entry["metadata"]["ticket_number"]
            index["entries"]["tickets"][ticket_number] = entry

            # Update metadata
            index["archive_metadata"]["last_updated"] = datetime.now().isoformat()

            # Write back
            with open(self.holocron_index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to update HOLOCRON_INDEX.json: {e}", exc_info=True)
            return False

    def migrate_ticket(self, ticket_number: str) -> Dict[str, Any]:
        """Migrate single ticket to Holocron and database"""
        self.logger.info(f"Migrating ticket {ticket_number}...")

        # Load ticket
        ticket_file = self.ticket_dir / f"{ticket_number}.json"
        if not ticket_file.exists():
            return {"success": False, "error": f"Ticket {ticket_number} not found"}

        try:
            with open(ticket_file, 'r', encoding='utf-8') as f:
                ticket = json.load(f)
        except Exception as e:
            return {"success": False, "error": f"Failed to load ticket: {e}"}

        # Ensure database tables
        if not self._ensure_database_tables():
            return {"success": False, "error": "Failed to ensure database tables"}

        # Create Holocron entry
        holocron_entry = self._create_holocron_entry(ticket)

        # Update Holocron index
        if not self._update_holocron_index(holocron_entry):
            self.logger.warning(f"⚠️  Failed to update Holocron index for {ticket_number}")

        # Import to database
        if not self._import_ticket_to_database(ticket, holocron_entry):
            self.logger.warning(f"⚠️  Failed to import ticket to database: {ticket_number}")

        # Import PR if exists
        if ticket.get("pr_number"):
            pr_file = self.project_root / "data" / "pr_tickets" / "prs" / f"{ticket.get('pr_number')}.json"
            if pr_file.exists():
                try:
                    with open(pr_file, 'r', encoding='utf-8') as f:
                        pr = json.load(f)
                    self._import_pr_to_database(pr)
                except Exception as e:
                    self.logger.warning(f"⚠️  Failed to import PR: {e}")

        self.logger.info(f"✅ Migrated ticket {ticket_number}")

        return {
            "success": True,
            "ticket_number": ticket_number,
            "holocron_entry_id": holocron_entry.get("entry_id"),
            "holocron_location": holocron_entry.get("location")
        }

    def migrate_all_tickets(self) -> Dict[str, Any]:
        """Migrate all tickets to Holocron and database"""
        self.logger.info("="*80)
        self.logger.info("MIGRATING ALL TICKETS TO HOLOCRON & DATABASE")
        self.logger.info("="*80)

        # Ensure database tables
        if not self._ensure_database_tables():
            return {"success": False, "error": "Failed to ensure database tables"}

        results = []

        # Find all tickets
        for ticket_file in self.ticket_dir.glob("PM*.json"):
            ticket_number = ticket_file.stem
            result = self.migrate_ticket(ticket_number)
            results.append(result)

        # Also find any remaining HELPDESK tickets
        for ticket_file in self.ticket_dir.glob("HELPDESK-*.json"):
            ticket_number = ticket_file.stem
            result = self.migrate_ticket(ticket_number)
            results.append(result)

        successful = sum(1 for r in results if r.get("success"))
        self.logger.info(f"✅ Migrated {successful}/{len(results)} tickets")

        return {
            "success": True,
            "total_tickets": len(results),
            "successful": successful,
            "failed": len(results) - successful,
            "results": results
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Migrate tickets to Holocron & Database")
        parser.add_argument("--ticket", type=str, help="Migrate specific ticket (HELPDESK-XXXX)")
        parser.add_argument("--all", action="store_true", help="Migrate all tickets")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        migrator = TicketsToHolocronDB(project_root)

        if args.ticket:
            result = migrator.migrate_ticket(args.ticket)
            print(json.dumps(result, indent=2, default=str))
        elif args.all:
            result = migrator.migrate_all_tickets()
            print(json.dumps(result, indent=2, default=str))
        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()