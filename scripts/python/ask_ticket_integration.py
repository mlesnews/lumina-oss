#!/usr/bin/env python3
"""
@ask Ticket Integration

Integrates Request ID tracking with @ask ticket collation system.
Automatically collates @ask directives with helpdesk and GitLens tickets.

Tags: #ASK #INTEGRATION #AUTOMATION @JARVIS @LUMINA
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from ask_ticket_collation_system import AskTicketCollationSystem
from lumina_core.paths import get_script_dir
from track_request_id import RequestIDTracker

script_dir = get_script_dir()
project_root_global = script_dir.parent.parent
from lumina_core.paths import setup_paths

setup_paths()
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_core.logging import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    def get_logger(name: str):
        """Fallback logger"""
        return logging.getLogger(name)

logger = get_logger("AskTicketIntegration")


class AskTicketIntegration:
    """
    Integration between Request ID tracking and @ask ticket collation

    Automatically creates collated records when @ask directives are tracked.
    """

    def __init__(self, root_path: Optional[Path] = None):
        """Initialize integration"""
        if root_path is None:
            from lumina_core.paths import get_project_root
            self.project_root = Path(get_project_root())
        else:
            self.project_root = Path(root_path)

        self.request_tracker = RequestIDTracker(self.project_root)
        self.collation_system = AskTicketCollationSystem(self.project_root)

        logger.info("✅ @ask Ticket Integration initialized")

    def track_and_collate(
        self,
        request_id: str,
        ask_text: str,
        helpdesk_ticket: Optional[str] = None,
        gitlens_ticket: Optional[str] = None,
        gitlens_pr: Optional[str] = None,
        error_type: Optional[str] = None,
        source: str = "user_report"
    ):
        """
        Track Request ID and collate with tickets

        Args:
            request_id: @ask directive / Request ID
            ask_text: Original @ask directive text
            helpdesk_ticket: Helpdesk ticket number
            gitlens_ticket: GitLens ticket/issue number
            gitlens_pr: GitLens pull request number
            error_type: Type of error (if applicable)
            source: Source of @ask
        """
        logger.info("🔄 Tracking and collating @ask: %s", request_id)

        # Track Request ID
        context = {
            "ask_text": ask_text,
            "helpdesk_ticket": helpdesk_ticket,
            "gitlens_ticket": gitlens_ticket,
            "gitlens_pr": gitlens_pr
        }

        diagnostic = self.request_tracker.track_request_id(
            request_id=request_id,
            source=source,
            error_type=error_type,
            context=context
        )

        # Collate with tickets
        record = self.collation_system.collate_ask(
            ask_id=request_id,
            ask_text=ask_text,
            helpdesk_ticket=helpdesk_ticket,
            gitlens_ticket=gitlens_ticket,
            gitlens_pr=gitlens_pr,
            source=source,
            description=diagnostic.get("context", {}).get("purpose", ask_text)
        )

        logger.info("✅ Tracked and collated @ask: %s", request_id)
        logger.info("   Helpdesk: %s", helpdesk_ticket or 'None')
        logger.info("   GitLens Ticket: %s", gitlens_ticket or 'None')
        logger.info("   GitLens PR: %s", gitlens_pr or 'None')
        logger.info("   Assigned to: %s", record.assigned_team)
        logger.info("   Follow-up required: %s", record.requires_follow_up)

        return {
            "diagnostic": diagnostic,
            "collated_record": record.to_dict()
        }


def main():
    try:
        """Main entry point"""
        parser = argparse.ArgumentParser(
            description="@ask Ticket Integration - Track and collate @ask directives"
        )
        parser.add_argument("--track-collate", nargs=6,
                           metavar=("ID", "TEXT", "HD", "GT", "GPR", "ERR"),
                           help="Track Request ID and collate with tickets")

        args = parser.parse_args()

        integration = AskTicketIntegration()

        if args.track_collate:
            request_id, ask_text, helpdesk, gitlens_ticket, gitlens_pr, error_type = args.track_collate
            result = integration.track_and_collate(
                request_id=request_id,
                ask_text=ask_text,
                helpdesk_ticket=helpdesk if helpdesk != "None" else None,
                gitlens_ticket=gitlens_ticket if gitlens_ticket != "None" else None,
                gitlens_pr=gitlens_pr if gitlens_pr != "None" else None,
                error_type=error_type if error_type != "None" else None
            )
            print("\n✅ Tracked and collated:")
            print(json.dumps(result, indent=2))
        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()