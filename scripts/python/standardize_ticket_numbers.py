#!/usr/bin/env python3
"""
Standardize Ticket Numbers - Apply 9-Digit Format Retroactively

All helpdesk tickets/CRs/tasks use the same 9-digit format:
- PM (Problem Management) + 9 digits: PM000000001
- CR (Change Request) + 9 digits: CR000000001  
- T (Task) + 9 digits: T000000001

This script retroactively applies the format to all existing tickets.

Author: LUMINA Helpdesk Team
Date: 2025-01-24
Tags: @helpdesk @C3PO @JARVIS
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)


def extract_number(s: str) -> Optional[int]:
    """Extract numeric part from string"""
    match = re.search(r'(\d+)', s)
    return int(match.group(1)) if match else None


def standardize_cr_number(cr_number: str) -> str:
    """Convert CR number to 9-digit format: CR000000001"""
    if not cr_number:
        return cr_number

    # Already in format CR000000001
    if re.match(r'^CR\d{9}$', cr_number):
        return cr_number

    # Extract number from formats like CR-2025-01-24-001 or CR-001
    number = extract_number(cr_number)
    if number:
        return f"CR{number:09d}"

    return cr_number


def standardize_ticket_file(ticket_file: Path) -> bool:
    """Standardize ticket numbers in a file"""
    logger = get_logger("StandardizeTickets")

    try:
        with open(ticket_file, 'r', encoding='utf-8') as f:
            ticket = json.load(f)

        changed = False
        old_cr = ticket.get("change_request_number", "")

        # Standardize change_request_number
        if old_cr:
            new_cr = standardize_cr_number(old_cr)
            if new_cr != old_cr:
                ticket["change_request_number"] = new_cr
                changed = True
                logger.info(f"  {ticket_file.name}: CR {old_cr} → {new_cr}")

        # Save if changed
        if changed:
            with open(ticket_file, 'w', encoding='utf-8') as f:
                json.dump(ticket, f, indent=2, ensure_ascii=False)
            return True

        return False

    except Exception as e:
        logger.error(f"Error processing {ticket_file.name}: {e}")
        return False


def main():
    try:
        """Standardize all tickets"""
        logger = get_logger("StandardizeTickets")
        project_root = Path(__file__).parent.parent.parent
        tickets_dir = project_root / "data" / "pr_tickets" / "tickets"

        logger.info("🔧 Standardizing ticket numbers to 9-digit format...")

        ticket_files = list(tickets_dir.glob("*.json"))
        logger.info(f"Found {len(ticket_files)} ticket files")

        normalized = 0
        for ticket_file in ticket_files:
            if standardize_ticket_file(ticket_file):
                normalized += 1

        logger.info(f"✅ Standardized {normalized} tickets")
        print(f"\n✅ Standardized {normalized} ticket files")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":

    main()