#!/usr/bin/env python3
"""
Create Standardization Change Management Tickets

Creates @ask tickets for standardization implementation through helpdesk
and change management system.

Tags: #STANDARDIZATION #CHANGE_MANAGEMENT #HELPDESK #TICKETS @JARVIS @LUMINA @DOIT
"""

import argparse
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from ask_ticket_collation_system import AskTicketCollationSystem
from lumina_core.paths import get_script_dir

script_dir = get_script_dir()
project_root_global = script_dir.parent.parent
from lumina_core.paths import setup_paths

setup_paths()

try:
    from lumina_core.logging import get_logger
    from lumina_core.paths import get_project_root
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    def get_logger(name: str):
        """Fallback logger"""
        return logging.getLogger(name)
    def get_project_root():
        """Fallback project root"""
        return script_dir.parent.parent

logger = get_logger("CreateStandardizationTickets")


STANDARDIZATION_TICKETS = [
    {
        "ask_id": str(uuid.uuid4()),
        "ask_text": (
            "@ask @jarvis @r5 #standardization #lumina_core implement STD-001: "
            "Core Logging Standardization - Create lumina_core.logging module for "
            "standardized logger initialization across all 2,595 Python files"
        ),
        "description": (
            "Implement standardized logging module (lumina_core.logging) to replace "
            "inconsistent logger initialization patterns. This affects all scripts "
            "and ensures consistent error handling."
        ),
        "tags": ["@jarvis", "@r5", "#standardization", "#lumina_core", "#logging",
                 "#high_priority"],
        "priority": "high",
        "assigned_team": "JARVIS_TEAM",
        "status": "in_progress"
    },
    {
        "ask_id": str(uuid.uuid4()),
        "ask_text": (
            "@ask @jarvis @r5 #standardization #lumina_core implement STD-002: "
            "Path Management Standardization - Create lumina_core.paths module for "
            "standardized path management"
        ),
        "description": (
            "Implement standardized path management module (lumina_core.paths) to "
            "replace inconsistent project root detection and sys.path management patterns."
        ),
        "tags": ["@jarvis", "@r5", "#standardization", "#lumina_core", "#paths",
                 "#high_priority"],
        "priority": "high",
        "assigned_team": "JARVIS_TEAM",
        "status": "pending"
    },
    {
        "ask_id": str(uuid.uuid4()),
        "ask_text": (
            "@ask @jarvis @r5 #standardization #lumina_core implement STD-003: "
            "Configuration Loading Standardization - Create lumina_core.config module"
        ),
        "description": (
            "Implement standardized configuration loading module (lumina_core.config) "
            "with ConfigLoader class for JSON, YAML, and environment variable configs."
        ),
        "tags": ["@jarvis", "@r5", "#standardization", "#lumina_core", "#config",
                 "#medium_priority"],
        "priority": "medium",
        "assigned_team": "JARVIS_TEAM",
        "status": "pending"
    },
    {
        "ask_id": str(uuid.uuid4()),
        "ask_text": (
            "@ask @jarvis @r5 #standardization #lumina_core implement STD-004: "
            "Daemon Base Class Standardization - Create lumina_core.daemon module"
        ),
        "description": (
            "Standardize daemon implementation using BaseDaemon class. Migrate "
            "existing daemons to use standardized base class with consistent "
            "logging and signal handling."
        ),
        "tags": ["@jarvis", "@r5", "#standardization", "#lumina_core", "#daemon",
                 "#high_priority"],
        "priority": "high",
        "assigned_team": "JARVIS_TEAM",
        "status": "pending"
    },
    {
        "ask_id": str(uuid.uuid4()),
        "ask_text": (
            "@ask @jarvis @r5 #standardization #lumina_core implement STD-005: "
            "Manager/Service/Helper Standardization - Create lumina_core.managers module"
        ),
        "description": (
            "Standardize manager/service/helper class patterns with base classes "
            "and standard interfaces. Migrate existing managers to use standardized patterns."
        ),
        "tags": ["@jarvis", "@r5", "#standardization", "#lumina_core", "#managers",
                 "#medium_priority"],
        "priority": "medium",
        "assigned_team": "JARVIS_TEAM",
        "status": "pending"
    },
    {
        "ask_id": str(uuid.uuid4()),
        "ask_text": (
            "@ask @jarvis @r5 #standardization #modularization implement STD-006: "
            "Feature Module Modularization - Create lumina_ask_ticket, lumina_apicli, "
            "lumina_cron, lumina_daemon modules"
        ),
        "description": (
            "Modularize feature-specific functionality into separate modules: "
            "lumina_ask_ticket, lumina_apicli, lumina_cron, lumina_daemon. "
            "Migrate existing code and test thoroughly."
        ),
        "tags": ["@jarvis", "@r5", "#standardization", "#modularization", "#features",
                 "#medium_priority"],
        "priority": "medium",
        "assigned_team": "JARVIS_TEAM",
        "status": "pending"
    }
]


def create_standardization_tickets():
    """Create standardization tickets in the @ask ticket system"""
    logger.info("=" * 80)
    logger.info("Creating Standardization Change Management Tickets")
    logger.info("=" * 80)
    logger.info("")

    collation = AskTicketCollationSystem()

    created_tickets = []

    for ticket_data in STANDARDIZATION_TICKETS:
        logger.info("Creating ticket: %s...", ticket_data['ask_text'][:60])

        try:
            # Create ticket record using collate_ask
            record = collation.collate_ask(
                ask_id=ticket_data["ask_id"],
                ask_text=ticket_data["ask_text"],
                description=ticket_data.get("description"),
                source="standardization_implementation"
            )

            # Update with additional metadata
            if ticket_data.get("assigned_team"):
                record.assigned_team = ticket_data["assigned_team"]
            if ticket_data.get("status"):
                record.status = ticket_data["status"]
            if ticket_data.get("priority"):
                record.priority = ticket_data["priority"]

            # Re-save with updates
            collation._save_record(record)

            created_tickets.append({
                "ask_id": ticket_data["ask_id"],
                "helpdesk_ticket": record.helpdesk_ticket,
                "status": record.status
            })

            logger.info("  ✅ Created: %s", record.ask_id)
            if record.helpdesk_ticket:
                logger.info("     Helpdesk: %s", record.helpdesk_ticket)

        except Exception as e:
            logger.error("  ❌ Error creating ticket: %s", e)

    logger.info("")
    logger.info("=" * 80)
    logger.info("✅ Ticket Creation Complete")
    logger.info("=" * 80)
    logger.info("   Tickets created: %d", len(created_tickets))
    logger.info("")
    logger.info("Created tickets:")
    for ticket in created_tickets:
        logger.info("   - %s: %s", ticket['ask_id'], ticket['status'])

    return created_tickets


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Create Standardization Change Management Tickets"
    )
    parser.add_argument("--create", action="store_true", help="Create tickets")

    args = parser.parse_args()

    if args.create:
        tickets = create_standardization_tickets()
        print(f"\n📋 Created {len(tickets)} standardization tickets")
        for ticket in tickets:
            print(f"   - {ticket['ask_id']}")
    else:
        parser.print_help()


if __name__ == "__main__":


    main()