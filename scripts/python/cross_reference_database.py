#!/usr/bin/env python3
"""
Cross-Reference Database for All LUMINA Databases

Cross-references Helpdesk/GitHub/CursorID tickets, Request IDs, and all LUMINA databases.
Provides unified cross-referencing across the entire system.

Tags: #CROSS_REFERENCE #DATABASE #HELPDESK #GITHUB #CURSOR_ID #LUMINA @JARVIS
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CrossReferenceDatabase")


class CrossReferenceDatabase:
    """
    Cross-Reference Database for All LUMINA Databases

    Cross-references:
    - Request IDs
    - Helpdesk Tickets
    - GitHub PRs
    - Cursor ID tickets
    - All LUMINA databases
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize cross-reference database"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "cross_reference"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.db_file = self.data_dir / "cross_reference_database.json"
        self.database: Dict[str, Any] = {
            "request_ids": {},
            "helpdesk_tickets": {},
            "github_prs": {},
            "cursor_id_tickets": {},
            "lumina_databases": {},
            "cross_references": defaultdict(list),
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "version": "1.0.0"
            }
        }

        # Load existing database
        self._load_database()

        logger.info("✅ Cross-Reference Database initialized")
        logger.info(f"   Database file: {self.db_file}")

    def _load_database(self):
        """Load existing cross-reference database"""
        try:
            if self.db_file.exists():
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    self.database = json.load(f)
                    # Convert defaultdict back
                    if "cross_references" in self.database:
                        self.database["cross_references"] = defaultdict(
                            list,
                            self.database["cross_references"]
                        )
                    logger.info(f"   ✅ Loaded {len(self.database.get('request_ids', {}))} Request IDs")
        except Exception as e:
            logger.warning(f"   Could not load database: {e}")

    def _save_database(self):
        """Save cross-reference database"""
        try:
            self.database["metadata"]["last_updated"] = datetime.now().isoformat()
            # Convert defaultdict to dict for JSON
            db_copy = self.database.copy()
            if "cross_references" in db_copy:
                db_copy["cross_references"] = dict(db_copy["cross_references"])

            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(db_copy, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"   ❌ Error saving database: {e}")

    def add_cross_reference(
        self,
        request_id: Optional[str] = None,
        helpdesk_ticket: Optional[str] = None,
        github_pr: Optional[str] = None,
        cursor_id_ticket: Optional[str] = None,
        ticket_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add cross-reference entry"""

        ref_id = request_id or helpdesk_ticket or github_pr or cursor_id_ticket
        if not ref_id:
            logger.warning("   ⚠️  No identifier provided for cross-reference")
            return

        timestamp = datetime.now().isoformat()

        # Add to appropriate category
        if request_id:
            self.database["request_ids"][request_id] = {
                "timestamp": timestamp,
                "helpdesk_ticket": helpdesk_ticket,
                "github_pr": github_pr,
                "cursor_id_ticket": cursor_id_ticket,
                "ticket_type": ticket_type,
                "metadata": metadata or {}
            }

        if helpdesk_ticket:
            self.database["helpdesk_tickets"][helpdesk_ticket] = {
                "timestamp": timestamp,
                "request_id": request_id,
                "github_pr": github_pr,
                "cursor_id_ticket": cursor_id_ticket,
                "metadata": metadata or {}
            }

        if github_pr:
            self.database["github_prs"][github_pr] = {
                "timestamp": timestamp,
                "request_id": request_id,
                "helpdesk_ticket": helpdesk_ticket,
                "cursor_id_ticket": cursor_id_ticket,
                "metadata": metadata or {}
            }

        if cursor_id_ticket:
            self.database["cursor_id_tickets"][cursor_id_ticket] = {
                "timestamp": timestamp,
                "request_id": request_id,
                "helpdesk_ticket": helpdesk_ticket,
                "github_pr": github_pr,
                "metadata": metadata or {}
            }

        # Add to cross-reference index
        if request_id:
            self.database["cross_references"][request_id].append({
                "type": "request_id",
                "value": request_id,
                "related": {
                    "helpdesk_ticket": helpdesk_ticket,
                    "github_pr": github_pr,
                    "cursor_id_ticket": cursor_id_ticket
                },
                "timestamp": timestamp,
                "metadata": metadata or {}
            })

        self._save_database()
        logger.info(f"   ✅ Cross-reference added: {ref_id}")

    def find_references(self, identifier: str) -> List[Dict[str, Any]]:
        """Find all cross-references for an identifier"""
        references = []

        # Check request IDs
        if identifier in self.database["request_ids"]:
            ref = self.database["request_ids"][identifier]
            references.append({
                "type": "request_id",
                "identifier": identifier,
                "related": {
                    "helpdesk_ticket": ref.get("helpdesk_ticket"),
                    "github_pr": ref.get("github_pr"),
                    "cursor_id_ticket": ref.get("cursor_id_ticket")
                },
                "metadata": ref.get("metadata", {})
            })

        # Check helpdesk tickets
        if identifier in self.database["helpdesk_tickets"]:
            ref = self.database["helpdesk_tickets"][identifier]
            references.append({
                "type": "helpdesk_ticket",
                "identifier": identifier,
                "related": {
                    "request_id": ref.get("request_id"),
                    "github_pr": ref.get("github_pr"),
                    "cursor_id_ticket": ref.get("cursor_id_ticket")
                },
                "metadata": ref.get("metadata", {})
            })

        # Check GitHub PRs
        if identifier in self.database["github_prs"]:
            ref = self.database["github_prs"][identifier]
            references.append({
                "type": "github_pr",
                "identifier": identifier,
                "related": {
                    "request_id": ref.get("request_id"),
                    "helpdesk_ticket": ref.get("helpdesk_ticket"),
                    "cursor_id_ticket": ref.get("cursor_id_ticket")
                },
                "metadata": ref.get("metadata", {})
            })

        # Check cursor ID tickets
        if identifier in self.database["cursor_id_tickets"]:
            ref = self.database["cursor_id_tickets"][identifier]
            references.append({
                "type": "cursor_id_ticket",
                "identifier": identifier,
                "related": {
                    "request_id": ref.get("request_id"),
                    "helpdesk_ticket": ref.get("helpdesk_ticket"),
                    "github_pr": ref.get("github_pr")
                },
                "metadata": ref.get("metadata", {})
            })

        return references

    def cross_reference_all_lumina_databases(self):
        """Cross-reference all LUMINA databases"""
        logger.info("🔍 Cross-referencing all LUMINA databases...")

        # Scan data directory for databases
        data_dir = self.project_root / "data"

        databases_found = []

        for db_path in data_dir.rglob("*.json"):
            try:
                with open(db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    # Look for Request IDs, tickets, PRs
                    db_info = {
                        "path": str(db_path.relative_to(self.project_root)),
                        "request_ids": [],
                        "tickets": [],
                        "prs": []
                    }

                    # Search for identifiers in data
                    data_str = json.dumps(data)

                    # Find Request IDs (UUID format)
                    import re
                    request_ids = re.findall(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', data_str, re.I)
                    db_info["request_ids"] = list(set(request_ids))

                    databases_found.append(db_info)
            except Exception as e:
                logger.debug(f"   Could not process {db_path}: {e}")

        self.database["lumina_databases"] = {
            "scanned_at": datetime.now().isoformat(),
            "databases": databases_found,
            "total_databases": len(databases_found)
        }

        self._save_database()
        logger.info(f"   ✅ Scanned {len(databases_found)} databases")

        return databases_found


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Cross-Reference Database")
    parser.add_argument("--add", action="store_true", help="Add cross-reference")
    parser.add_argument("--request-id", help="Request ID")
    parser.add_argument("--helpdesk-ticket", help="Helpdesk ticket")
    parser.add_argument("--github-pr", help="GitHub PR")
    parser.add_argument("--cursor-id-ticket", help="Cursor ID ticket")
    parser.add_argument("--find", help="Find references for identifier")
    parser.add_argument("--scan-all", action="store_true", help="Scan all LUMINA databases")

    args = parser.parse_args()

    db = CrossReferenceDatabase()

    if args.add:
        db.add_cross_reference(
            request_id=args.request_id,
            helpdesk_ticket=args.helpdesk_ticket,
            github_pr=args.github_pr,
            cursor_id_ticket=args.cursor_id_ticket
        )

    if args.find:
        refs = db.find_references(args.find)
        print(f"\nFound {len(refs)} references:")
        for ref in refs:
            print(f"  {ref}")

    if args.scan_all:
        db.cross_reference_all_lumina_databases()

    return 0


if __name__ == "__main__":


    sys.exit(main())