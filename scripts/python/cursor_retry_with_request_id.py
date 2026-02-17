#!/usr/bin/env python3
"""
Cursor IDE Retry Manager with Automatic Request ID Inclusion

When @RETRY is clicked, automatically includes the Request ID in the next @OP @SEND of @REQUEST.
Cross-references with Helpdesk/GitHub/CursorID tickets and sends to Jupyter Problem Management notebook.

Tags: #CURSOR_IDE #RETRY #REQUEST_ID #HELPDESK #CROSS_REFERENCE @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

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

logger = get_logger("CursorRetryWithRequestID")


class CursorRetryWithRequestID:
    """
    Cursor IDE Retry Manager with Automatic Request ID Inclusion

    Last step of stock OEM mechanic Cursor-IDE @RETRY should automatically
    include the "Request ID" in the next @OP @SEND of @REQUEST.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize retry manager with Request ID tracking"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "cursor_retry_tracking"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        try:
            from cursor_operator_retry_tracker import CursorOperatorRetryTracker
            self.retry_tracker = CursorOperatorRetryTracker(self.project_root)
        except Exception as e:
            logger.warning(f"Could not initialize retry tracker: {e}")
            self.retry_tracker = None

        try:
            from cursor_notification_ticket_tracker import CursorNotificationTicketTracker
            self.ticket_tracker = CursorNotificationTicketTracker(self.project_root)
        except Exception as e:
            logger.warning(f"Could not initialize ticket tracker: {e}")
            self.ticket_tracker = None

        try:
            from cross_reference_database import CrossReferenceDatabase
            self.cross_ref_db = CrossReferenceDatabase(self.project_root)
        except Exception as e:
            logger.warning(f"Could not initialize cross-reference database: {e}")
            self.cross_ref_db = None

        logger.info("✅ Cursor Retry with Request ID initialized")

    def handle_retry_with_request_id(
        self,
        request_id: str,
        original_error: Optional[str] = None,
        operator: str = "@OP"
    ) -> Dict[str, Any]:
        """
        Handle retry with automatic Request ID inclusion

        Args:
            request_id: The Request ID from the failed request
            original_error: Original error message
            operator: Operator identifier (default: @OP)

        Returns:
            Dictionary with retry information and next request template
        """
        logger.info("=" * 80)
        logger.info("🔄 RETRY WITH REQUEST ID")
        logger.info("=" * 80)
        logger.info(f"   Request ID: {request_id}")
        logger.info(f"   Operator: {operator}")
        logger.info("")

        # Step 1: Record retry action
        retry_action = None
        if self.retry_tracker:
            retry_action = self.retry_tracker.record_operator_retry(
                request_id=request_id,
                original_error_message=original_error,
                operator=operator,
                notes="Automatic Request ID inclusion in next @SEND"
            )

        # Step 2: Cross-reference with tickets
        cross_references = self._cross_reference_tickets(request_id)

        # Step 3: Generate next request template with Request ID
        next_request_template = self._generate_next_request_template(
            request_id=request_id,
            cross_references=cross_references,
            original_error=original_error
        )

        # Step 4: Send to Jupyter Problem Management notebook
        jupyter_result = self._send_to_jupyter_problem_management(
            request_id=request_id,
            retry_action=retry_action,
            cross_references=cross_references,
            original_error=original_error
        )

        # Step 5: Update cross-reference database
        if self.cross_ref_db:
            self.cross_ref_db.add_cross_reference(
                request_id=request_id,
                ticket_type="cursor_retry",
                metadata={
                    "retry_action": str(retry_action) if retry_action else None,
                    "cross_references": cross_references,
                    "jupyter_notebook": jupyter_result
                }
            )

        result = {
            "request_id": request_id,
            "retry_recorded": retry_action is not None,
            "cross_references": cross_references,
            "next_request_template": next_request_template,
            "jupyter_sent": jupyter_result.get("success", False),
            "timestamp": datetime.now().isoformat()
        }

        logger.info("")
        logger.info("✅ RETRY PROCESSED")
        logger.info(f"   Next @SEND should include: Request ID: {request_id}")
        logger.info(f"   Cross-references: {len(cross_references)} found")
        logger.info("")

        return result

    def _cross_reference_tickets(self, request_id: str) -> List[Dict[str, Any]]:
        """Cross-reference Request ID with Helpdesk/GitHub/CursorID tickets"""
        cross_refs = []

        if not self.ticket_tracker:
            return cross_refs

        # Search for tickets with this Request ID
        tickets = self.ticket_tracker.tickets

        for ticket_id, ticket in tickets.items():
            if ticket.cursor_request_id == request_id:
                cross_refs.append({
                    "type": "notification_ticket",
                    "ticket_id": ticket_id,
                    "title": ticket.title,
                    "status": ticket.status,
                    "priority": ticket.priority,
                    "help_desk_ticket": ticket.help_desk_ticket,
                    "github_pr": ticket.github_pr
                })

        # Search cross-reference database
        if self.cross_ref_db:
            db_refs = self.cross_ref_db.find_references(request_id)
            cross_refs.extend(db_refs)

        return cross_refs

    def _generate_next_request_template(
        self,
        request_id: str,
        cross_references: List[Dict[str, Any]],
        original_error: Optional[str] = None
    ) -> str:
        """Generate next @OP @SEND template with Request ID included"""

        template_parts = [
            "@OP @SEND @REQUEST",
            "",
            f"Request ID: {request_id}",
            ""
        ]

        if cross_references:
            template_parts.append("Cross-References:")
            for ref in cross_references:
                if ref.get("help_desk_ticket"):
                    template_parts.append(f"  Helpdesk Ticket: {ref['help_desk_ticket']}")
                if ref.get("github_pr"):
                    template_parts.append(f"  GitHub PR: {ref['github_pr']}")
                if ref.get("ticket_id"):
                    template_parts.append(f"  Ticket ID: {ref['ticket_id']}")
            template_parts.append("")

        if original_error:
            template_parts.append(f"Original Error: {original_error}")
            template_parts.append("")

        template_parts.append("[Your request here - Request ID automatically included]")

        return "\n".join(template_parts)

    def _send_to_jupyter_problem_management(
        self,
        request_id: str,
        retry_action: Optional[Any],
        cross_references: List[Dict[str, Any]],
        original_error: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send retry information to Jupyter Problem Management notebook"""

        notebooks_dir = self.project_root / "notebooks" / "problem_management"
        notebooks_dir.mkdir(parents=True, exist_ok=True)

        # Create JSON data file for Jupyter notebook
        data_file = notebooks_dir / f"retry_{request_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        data = {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "retry_action": str(retry_action) if retry_action else None,
            "cross_references": cross_references,
            "original_error": original_error,
            "type": "cursor_retry",
            "team": "problem_management"
        }

        try:
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"   ✅ Sent to Jupyter Problem Management: {data_file}")

            return {
                "success": True,
                "data_file": str(data_file),
                "notebook": "notebooks/problem_management/problem_management.ipynb"
            }
        except Exception as e:
            logger.error(f"   ❌ Error sending to Jupyter: {e}")
            return {
                "success": False,
                "error": str(e)
            }


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Cursor Retry with Request ID")
    parser.add_argument("--request-id", required=True, help="Request ID to retry")
    parser.add_argument("--error", help="Original error message")
    parser.add_argument("--operator", default="@OP", help="Operator identifier")

    args = parser.parse_args()

    manager = CursorRetryWithRequestID()
    result = manager.handle_retry_with_request_id(
        request_id=args.request_id,
        original_error=args.error,
        operator=args.operator
    )

    print("\n" + "=" * 80)
    print("NEXT @OP @SEND TEMPLATE:")
    print("=" * 80)
    print(result["next_request_template"])
    print("=" * 80)

    return 0


if __name__ == "__main__":


    sys.exit(main())