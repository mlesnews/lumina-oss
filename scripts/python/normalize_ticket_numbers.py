#!/usr/bin/env python3
"""
Normalize Ticket Numbers - Standardize to 9-Digit Format

All helpdesk tickets/CRs/tasks use the same 9-digit format with prefix:
- PM (Problem Management) for tickets
- CR (Change Request) for change requests
- T (Task) for tasks

Format: PREFIX + 9 digits (e.g., PM000000001, CR000000001, T000000001)

Author: LUMINA Helpdesk Team
Date: 2025-01-24
Tags: @helpdesk @C3PO @JARVIS
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)


class TicketNumberNormalizer:
    """Normalize ticket numbers to 9-digit format"""

    # Ticket type prefixes
    PREFIX_TICKET = "PM"  # Problem Management
    PREFIX_CHANGE_REQUEST = "CR"  # Change Request
    PREFIX_TASK = "T"  # Task

    def __init__(self, project_root: Optional[Path] = None):
        self.logger = get_logger("TicketNumberNormalizer")
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.tickets_dir = self.project_root / "data" / "pr_tickets" / "tickets"

        # Track renames
        self.renames: List[Tuple[str, str]] = []

    def extract_number_from_ticket_number(self, ticket_number: str) -> Optional[int]:
        """Extract numeric part from ticket number"""
        # Remove prefix and extract digits
        match = re.search(r'(\d+)', ticket_number)
        if match:
            return int(match.group(1))
        return None

    def normalize_ticket_number(self, ticket_number: str, ticket_type: str = "ticket") -> str:
        """
        Normalize ticket number to 9-digit format

        Args:
            ticket_number: Current ticket number
            ticket_type: Type of ticket (ticket, change_request, task)

        Returns:
            Normalized ticket number (PREFIX + 9 digits)
        """
        # Determine prefix
        prefix_map = {
            "ticket": self.PREFIX_TICKET,
            "change_request": self.PREFIX_CHANGE_REQUEST,
            "task": self.PREFIX_TASK
        }

        # If ticket_number already has a prefix, try to determine type
        if ticket_number.startswith(self.PREFIX_TICKET):
            prefix = self.PREFIX_TICKET
            ticket_type = "ticket"
        elif ticket_number.startswith(self.PREFIX_CHANGE_REQUEST):
            prefix = self.PREFIX_CHANGE_REQUEST
            ticket_type = "change_request"
        elif ticket_number.startswith(self.PREFIX_TASK):
            prefix = self.PREFIX_TASK
            ticket_type = "task"
        else:
            # Use provided type or default to ticket
            prefix = prefix_map.get(ticket_type, self.PREFIX_TICKET)

        # Extract number
        number = self.extract_number_from_ticket_number(ticket_number)
        if number is None:
            self.logger.warning(f"Could not extract number from {ticket_number}")
            return ticket_number

        # Format as 9 digits with leading zeros
        normalized = f"{prefix}{number:09d}"
        return normalized

    def normalize_change_request_number(self, cr_number: str) -> str:
        """
        Normalize change request number to 9-digit format

        Args:
            cr_number: Current CR number (e.g., CR-2025-01-24-001)

        Returns:
            Normalized CR number (CR000000001)
        """
        # Extract number from formats like CR-2025-01-24-001 or CR-001
        match = re.search(r'(\d+)$', cr_number)
        if match:
            number = int(match.group(1))
            return f"{self.PREFIX_CHANGE_REQUEST}{number:09d}"

        # If it's already in format CR000000001, extract and re-normalize
        if cr_number.startswith(self.PREFIX_CHANGE_REQUEST):
            number = self.extract_number_from_ticket_number(cr_number)
            if number:
                return f"{self.PREFIX_CHANGE_REQUEST}{number:09d}"

        return cr_number

    def normalize_ticket_file(self, ticket_file: Path) -> bool:
        """
        Normalize ticket number in a ticket file

        Args:
            ticket_file: Path to ticket JSON file

        Returns:
            True if normalized successfully
        """
        try:
            # Read ticket
            with open(ticket_file, 'r', encoding='utf-8') as f:
                ticket = json.load(f)

            old_ticket_number = ticket.get("ticket_number", "")
            old_cr_number = ticket.get("change_request_number", "")

            changed = False

            # Normalize ticket_number
            if old_ticket_number:
                new_ticket_number = self.normalize_ticket_number(
                    old_ticket_number,
                    ticket.get("change_type", "ticket")
                )

                if new_ticket_number != old_ticket_number:
                    ticket["ticket_number"] = new_ticket_number
                    changed = True
                    self.logger.info(f"  Ticket number: {old_ticket_number} → {new_ticket_number}")

            # Normalize change_request_number if present
            if old_cr_number:
                new_cr_number = self.normalize_change_request_number(old_cr_number)

                if new_cr_number != old_cr_number:
                    ticket["change_request_number"] = new_cr_number
                    changed = True
                    self.logger.info(f"  CR number: {old_cr_number} → {new_cr_number}")

            # Determine new filename
            new_ticket_number = ticket.get("ticket_number", old_ticket_number)
            new_filename = f"{new_ticket_number}.json"
            new_filepath = self.tickets_dir / new_filename

            # Save updated ticket
            with open(ticket_file, 'w', encoding='utf-8') as f:
                json.dump(ticket, f, indent=2, ensure_ascii=False)

            # Rename file if needed
            if ticket_file.name != new_filename:
                if new_filepath.exists() and new_filepath != ticket_file:
                    self.logger.warning(f"  Target file {new_filename} already exists, keeping original name")
                else:
                    ticket_file.rename(new_filepath)
                    self.renames.append((ticket_file.name, new_filename))
                    self.logger.info(f"  Renamed: {ticket_file.name} → {new_filename}")

            return changed

        except Exception as e:
            self.logger.error(f"Error normalizing {ticket_file.name}: {e}")
            return False

    def normalize_all_tickets(self) -> Dict[str, Any]:
        """
        Normalize all ticket files

        Returns:
            Dictionary with normalization results
        """
        self.logger.info("🔧 Normalizing all ticket numbers to 9-digit format...")

        ticket_files = list(self.tickets_dir.glob("*.json"))
        self.logger.info(f"Found {len(ticket_files)} ticket files")

        normalized_count = 0
        error_count = 0

        for ticket_file in ticket_files:
            self.logger.info(f"\n📋 Processing: {ticket_file.name}")
            try:
                if self.normalize_ticket_file(ticket_file):
                    normalized_count += 1
            except Exception as e:
                self.logger.error(f"Error processing {ticket_file.name}: {e}")
                error_count += 1

        result = {
            "total_files": len(ticket_files),
            "normalized": normalized_count,
            "errors": error_count,
            "renames": len(self.renames)
        }

        self.logger.info(f"\n✅ Normalization complete:")
        self.logger.info(f"  Total files: {result['total_files']}")
        self.logger.info(f"  Normalized: {result['normalized']}")
        self.logger.info(f"  Errors: {result['errors']}")
        self.logger.info(f"  Files renamed: {result['renames']}")

        return result


def main():
    """Normalize all tickets"""
    normalizer = TicketNumberNormalizer()
    result = normalizer.normalize_all_tickets()

    print(f"\n📊 Normalization Summary:")
    print(f"  Total: {result['total_files']}")
    print(f"  Normalized: {result['normalized']}")
    print(f"  Errors: {result['errors']}")
    print(f"  Renames: {result['renames']}")


if __name__ == "__main__":

    main()