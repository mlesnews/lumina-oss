#!/usr/bin/env python3
"""
JARVIS Ticket Query System
Query tickets from Holocron and database.

Tags: #TICKETS #QUERY #HOLOCRON #DATABASE @AUTO
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

logger = get_logger("JARVISTicketQuery")


class TicketQuerySystem:
    """
    Query tickets from Holocron and database.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Database
        self.db_path = project_root / "data" / "jarvis_memory" / "enhanced_memory.db"

        # Holocron
        self.holocron_index_file = project_root / "data" / "holocron" / "HOLOCRON_INDEX.json"
        self.tickets_holocron_dir = project_root / "data" / "holocron" / "tickets"

        self.logger.info("✅ Ticket Query System initialized")

    def query_ticket_from_db(self, ticket_number: str) -> Optional[Dict[str, Any]]:
        """Query ticket from database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM tickets WHERE ticket_number = ?
            """, (ticket_number,))

            row = cursor.fetchone()
            conn.close()

            if row:
                ticket = dict(row)
                # Parse JSON fields
                if ticket.get("files_changed"):
                    ticket["files_changed"] = json.loads(ticket["files_changed"])
                if ticket.get("related_issues"):
                    ticket["related_issues"] = json.loads(ticket["related_issues"])
                if ticket.get("team_assignment"):
                    ticket["team_assignment"] = json.loads(ticket["team_assignment"])
                return ticket
            return None

        except Exception as e:
            self.logger.error(f"❌ Failed to query ticket from database: {e}", exc_info=True)
            return None

    def query_tickets_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Query tickets by status"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM tickets WHERE status = ? ORDER BY created_at DESC
            """, (status,))

            rows = cursor.fetchall()
            conn.close()

            tickets = []
            for row in rows:
                ticket = dict(row)
                # Parse JSON fields
                if ticket.get("files_changed"):
                    ticket["files_changed"] = json.loads(ticket["files_changed"])
                if ticket.get("related_issues"):
                    ticket["related_issues"] = json.loads(ticket["related_issues"])
                if ticket.get("team_assignment"):
                    ticket["team_assignment"] = json.loads(ticket["team_assignment"])
                tickets.append(ticket)

            return tickets

        except Exception as e:
            self.logger.error(f"❌ Failed to query tickets by status: {e}", exc_info=True)
            return []

    def query_tickets_by_team(self, team_id: str) -> List[Dict[str, Any]]:
        """Query tickets by team"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM tickets WHERE team_assignment LIKE ? ORDER BY created_at DESC
            """, (f'%"team_id": "{team_id}"%',))

            rows = cursor.fetchall()
            conn.close()

            tickets = []
            for row in rows:
                ticket = dict(row)
                # Parse JSON fields
                if ticket.get("files_changed"):
                    ticket["files_changed"] = json.loads(ticket["files_changed"])
                if ticket.get("related_issues"):
                    ticket["related_issues"] = json.loads(ticket["related_issues"])
                if ticket.get("team_assignment"):
                    ticket["team_assignment"] = json.loads(ticket["team_assignment"])
                tickets.append(ticket)

            return tickets

        except Exception as e:
            self.logger.error(f"❌ Failed to query tickets by team: {e}", exc_info=True)
            return []

    def query_tickets_by_severity(self, severity: str) -> List[Dict[str, Any]]:
        """Query tickets by severity"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM tickets WHERE severity = ? ORDER BY created_at DESC
            """, (severity,))

            rows = cursor.fetchall()
            conn.close()

            tickets = []
            for row in rows:
                ticket = dict(row)
                # Parse JSON fields
                if ticket.get("files_changed"):
                    ticket["files_changed"] = json.loads(ticket["files_changed"])
                if ticket.get("related_issues"):
                    ticket["related_issues"] = json.loads(ticket["related_issues"])
                if ticket.get("team_assignment"):
                    ticket["team_assignment"] = json.loads(ticket["team_assignment"])
                tickets.append(ticket)

            return tickets

        except Exception as e:
            self.logger.error(f"❌ Failed to query tickets by severity: {e}", exc_info=True)
            return []

    def search_tickets(self, query: str) -> List[Dict[str, Any]]:
        """Search tickets by title or description"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM tickets 
                WHERE title LIKE ? OR description LIKE ?
                ORDER BY created_at DESC
            """, (f'%{query}%', f'%{query}%'))

            rows = cursor.fetchall()
            conn.close()

            tickets = []
            for row in rows:
                ticket = dict(row)
                # Parse JSON fields
                if ticket.get("files_changed"):
                    ticket["files_changed"] = json.loads(ticket["files_changed"])
                if ticket.get("related_issues"):
                    ticket["related_issues"] = json.loads(ticket["related_issues"])
                if ticket.get("team_assignment"):
                    ticket["team_assignment"] = json.loads(ticket["team_assignment"])
                tickets.append(ticket)

            return tickets

        except Exception as e:
            self.logger.error(f"❌ Failed to search tickets: {e}", exc_info=True)
            return []

    def get_ticket_from_holocron(self, ticket_number: str) -> Optional[Dict[str, Any]]:
        """Get ticket entry from Holocron index"""
        try:
            if not self.holocron_index_file.exists():
                return None

            with open(self.holocron_index_file, 'r', encoding='utf-8') as f:
                index = json.load(f)

            tickets = index.get("entries", {}).get("tickets", {})
            return tickets.get(ticket_number)

        except Exception as e:
            self.logger.error(f"❌ Failed to get ticket from Holocron: {e}", exc_info=True)
            return None

    def get_all_tickets_summary(self) -> Dict[str, Any]:
        """Get summary of all tickets"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Count by status
            cursor.execute("""
                SELECT status, COUNT(*) as count FROM tickets GROUP BY status
            """)
            status_counts = {row[0]: row[1] for row in cursor.fetchall()}

            # Count by severity
            cursor.execute("""
                SELECT severity, COUNT(*) as count FROM tickets GROUP BY severity
            """)
            severity_counts = {row[0]: row[1] for row in cursor.fetchall()}

            # Count by team
            cursor.execute("""
                SELECT team_assignment, COUNT(*) as count FROM tickets GROUP BY team_assignment
            """)
            team_counts = {}
            for row in cursor.fetchall():
                if row[0]:
                    try:
                        team_assignment = json.loads(row[0])
                        team_id = team_assignment.get("team_id", "unknown")
                        team_counts[team_id] = row[1]
                    except:
                        pass

            # Total count
            cursor.execute("SELECT COUNT(*) FROM tickets")
            total_count = cursor.fetchone()[0]

            conn.close()

            return {
                "total_tickets": total_count,
                "by_status": status_counts,
                "by_severity": severity_counts,
                "by_team": team_counts
            }

        except Exception as e:
            self.logger.error(f"❌ Failed to get tickets summary: {e}", exc_info=True)
            return {}


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Query tickets from Holocron & Database")
        parser.add_argument("--ticket", type=str, help="Query specific ticket (HELPDESK-XXXX)")
        parser.add_argument("--status", type=str, help="Query tickets by status")
        parser.add_argument("--team", type=str, help="Query tickets by team")
        parser.add_argument("--severity", type=str, help="Query tickets by severity")
        parser.add_argument("--search", type=str, help="Search tickets by query")
        parser.add_argument("--summary", action="store_true", help="Get summary of all tickets")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        query_system = TicketQuerySystem(project_root)

        if args.ticket:
            ticket = query_system.query_ticket_from_db(args.ticket)
            if ticket:
                print(json.dumps(ticket, indent=2, default=str))
            else:
                print(f"Ticket {args.ticket} not found")
        elif args.status:
            tickets = query_system.query_tickets_by_status(args.status)
            print(json.dumps(tickets, indent=2, default=str))
        elif args.team:
            tickets = query_system.query_tickets_by_team(args.team)
            print(json.dumps(tickets, indent=2, default=str))
        elif args.severity:
            tickets = query_system.query_tickets_by_severity(args.severity)
            print(json.dumps(tickets, indent=2, default=str))
        elif args.search:
            tickets = query_system.search_tickets(args.search)
            print(json.dumps(tickets, indent=2, default=str))
        elif args.summary:
            summary = query_system.get_all_tickets_summary()
            print(json.dumps(summary, indent=2, default=str))
        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()