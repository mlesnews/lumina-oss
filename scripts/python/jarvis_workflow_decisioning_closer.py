#!/usr/bin/env python3
"""
JARVIS Workflow Decisioning Closer
Uses #DECISIONING to update/close tickets, PM tasks, change requests, and archive chat sessions

Workflow:
1. #DECISIONING - Determine if workflow is complete
2. Update and close all applicable tickets, PM tasks, change requests
3. Archive agent chat session

Tags: #DECISIONING #WORKFLOW #TICKETS #ARCHIVE @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
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

# Import decisioning engine
try:
    from lumina_decisioning_engine import LuminaDecisioningEngine, DecisionContext, DecisionAction
    DECISIONING_AVAILABLE = True
except ImportError:
    DECISIONING_AVAILABLE = False
    LuminaDecisioningEngine = None

# Import ticket processor
try:
    from jarvis_ticket_resolution_processor import JARVISTicketResolutionProcessor
    TICKET_PROCESSOR_AVAILABLE = True
except ImportError:
    TICKET_PROCESSOR_AVAILABLE = False
    JARVISTicketResolutionProcessor = None

# Import archiver
try:
    from walk_agent_sessions_to_archive import WalkAgentSessionsToArchive
    ARCHIVER_AVAILABLE = True
except ImportError:
    ARCHIVER_AVAILABLE = False
    WalkAgentSessionsToArchive = None

# Import MANUS full control
try:
    from jarvis_manus_cursor_full_control import JARVISManusCursorFullControl
    MANUS_FULL_CONTROL_AVAILABLE = True
except ImportError:
    MANUS_FULL_CONTROL_AVAILABLE = False
    JARVISManusCursorFullControl = None

logger = get_logger("JARVISWorkflowDecisioningCloser")

PROJECT_ROOT = Path(__file__).parent.parent.parent


class WorkflowDecisioningCloser:
    """
    Workflow closer using #DECISIONING

    Workflow:
    1. #DECISIONING - Determine completion status
    2. Update/close tickets, PM tasks, change requests
    3. Archive chat session
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root

        # Initialize decisioning engine
        if DECISIONING_AVAILABLE:
            self.decisioning_engine = LuminaDecisioningEngine(project_root)
        else:
            self.decisioning_engine = None
            logger.warning("⚠️  Decisioning engine not available")

        # Initialize ticket processor
        if TICKET_PROCESSOR_AVAILABLE:
            self.ticket_processor = JARVISTicketResolutionProcessor(project_root)
        else:
            self.ticket_processor = None
            logger.warning("⚠️  Ticket processor not available")

        # Initialize archiver
        if ARCHIVER_AVAILABLE:
            self.archiver = WalkAgentSessionsToArchive(project_root)
        else:
            self.archiver = None
            logger.warning("⚠️  Archiver not available")

        # Initialize MANUS full control
        if MANUS_FULL_CONTROL_AVAILABLE:
            try:
                self.manus_full_control = JARVISManusCursorFullControl(project_root)
                logger.info("✅ MANUS Full Control of Cursor IDE initialized")
            except Exception as e:
                self.manus_full_control = None
                logger.warning(f"⚠️  MANUS Full Control initialization failed: {e}")
        else:
            self.manus_full_control = None
            logger.warning("⚠️  MANUS Full Control not available")

        # Data directories
        self.tickets_dir = project_root / "data" / "pr_tickets" / "tickets"
        self.pm_tasks_dir = project_root / "data" / "pm_tasks"
        self.change_requests_dir = project_root / "data" / "change_requests"
        self.sessions_dir = project_root / "data" / "agent_sessions"

        self.logger = logger

    def decision_workflow_complete(self, session_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use #DECISIONING to determine if workflow is complete

        Args:
            session_id: Chat session ID
            workflow_data: Workflow data including tasks, tickets, etc.

        Returns:
            Decision result with completion status
        """
        self.logger.info("=" * 80)
        self.logger.info("🎯 #DECISIONING: Workflow Completion Assessment")
        self.logger.info("=" * 80)
        self.logger.info("")

        if not self.decisioning_engine:
            # Fallback decision logic
            return self._fallback_decision(workflow_data)

        # Use decisioning engine
        context = DecisionContext.WORKFLOW_TRIGGER

        # Gather decision factors
        factors = {
            "session_id": session_id,
            "tasks_completed": workflow_data.get("tasks_completed", []),
            "tickets_resolved": workflow_data.get("tickets_resolved", []),
            "pm_tasks_completed": workflow_data.get("pm_tasks_completed", []),
            "change_requests_closed": workflow_data.get("change_requests_closed", []),
            "documentation_complete": workflow_data.get("documentation_complete", False),
            "verification_passed": workflow_data.get("verification_passed", False)
        }

        # Make decision
        decision = self.decisioning_engine.make_decision(
            context=context,
            factors=factors
        )

        self.logger.info(f"✅ Decision: {decision.get('action')}")
        self.logger.info(f"   Confidence: {decision.get('confidence', 0):.0%}")
        self.logger.info("")

        return decision

    def _fallback_decision(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback decision logic if decisioning engine unavailable"""
        # Simple completion check
        tasks_complete = len(workflow_data.get("tasks_completed", [])) > 0
        tickets_resolved = len(workflow_data.get("tickets_resolved", [])) > 0

        is_complete = tasks_complete or tickets_resolved

        return {
            "action": "keep_all" if is_complete else "review",
            "confidence": 0.8 if is_complete else 0.5,
            "reasoning": "Fallback decision based on tasks/tickets",
            "complete": is_complete
        }

    def update_and_close_tickets(self, session_id: str, ticket_ids: List[str]) -> Dict[str, Any]:
        """
        Update and close all applicable tickets

        Args:
            session_id: Chat session ID
            ticket_ids: List of ticket IDs to close

        Returns:
            Update results
        """
        self.logger.info("=" * 80)
        self.logger.info("🎫 UPDATING AND CLOSING TICKETS")
        self.logger.info("=" * 80)
        self.logger.info("")

        if not self.ticket_processor:
            self.logger.warning("⚠️  Ticket processor not available - skipping")
            return {"updated": 0, "closed": 0, "errors": []}

        results = {
            "updated": 0,
            "closed": 0,
            "errors": []
        }

        for ticket_id in ticket_ids:
            try:
                # Update ticket with session completion info
                ticket_file = self.tickets_dir / f"{ticket_id}.json"
                if not ticket_file.exists():
                    self.logger.warning(f"⚠️  Ticket {ticket_id} not found")
                    results["errors"].append(f"Ticket {ticket_id} not found")
                    continue

                # Load ticket
                with open(ticket_file, 'r') as f:
                    ticket = json.load(f)

                # Update ticket
                ticket["status"] = "resolved"
                ticket["resolution_date"] = datetime.now().isoformat()
                ticket["resolved_by"] = "JARVIS Workflow Decisioning Closer"
                ticket["resolution_notes"] = f"Workflow completed via session {session_id}"
                ticket["session_id"] = session_id

                # Save updated ticket
                with open(ticket_file, 'w') as f:
                    json.dump(ticket, f, indent=2)

                results["updated"] += 1
                results["closed"] += 1
                self.logger.info(f"✅ Updated and closed ticket: {ticket_id}")

            except Exception as e:
                self.logger.error(f"❌ Error updating ticket {ticket_id}: {e}")
                results["errors"].append(f"Ticket {ticket_id}: {str(e)}")

        self.logger.info("")
        self.logger.info(f"📊 Tickets: {results['updated']} updated, {results['closed']} closed")
        if results["errors"]:
            self.logger.warning(f"⚠️  {len(results['errors'])} errors")
        self.logger.info("")

        return results

    def update_and_close_pm_tasks(self, session_id: str, task_ids: List[str]) -> Dict[str, Any]:
        """
        Update and close PM tasks

        Args:
            session_id: Chat session ID
            task_ids: List of PM task IDs to close

        Returns:
            Update results
        """
        self.logger.info("=" * 80)
        self.logger.info("📋 UPDATING AND CLOSING PM TASKS")
        self.logger.info("=" * 80)
        self.logger.info("")

        results = {
            "updated": 0,
            "closed": 0,
            "errors": []
        }

        self.pm_tasks_dir.mkdir(parents=True, exist_ok=True)

        for task_id in task_ids:
            try:
                # Find PM task file
                task_file = self.pm_tasks_dir / f"{task_id}.json"
                if not task_file.exists():
                    # Try alternative naming
                    task_files = list(self.pm_tasks_dir.glob(f"*{task_id}*.json"))
                    if task_files:
                        task_file = task_files[0]
                    else:
                        self.logger.warning(f"⚠️  PM task {task_id} not found")
                        results["errors"].append(f"PM task {task_id} not found")
                        continue

                # Load task
                with open(task_file, 'r') as f:
                    task = json.load(f)

                # Update task
                task["status"] = "completed"
                task["completion_date"] = datetime.now().isoformat()
                task["completed_by"] = "JARVIS Workflow Decisioning Closer"
                task["completion_notes"] = f"Workflow completed via session {session_id}"
                task["session_id"] = session_id

                # Save updated task
                with open(task_file, 'w') as f:
                    json.dump(task, f, indent=2)

                results["updated"] += 1
                results["closed"] += 1
                self.logger.info(f"✅ Updated and closed PM task: {task_id}")

            except Exception as e:
                self.logger.error(f"❌ Error updating PM task {task_id}: {e}")
                results["errors"].append(f"PM task {task_id}: {str(e)}")

        self.logger.info("")
        self.logger.info(f"📊 PM Tasks: {results['updated']} updated, {results['closed']} closed")
        if results["errors"]:
            self.logger.warning(f"⚠️  {len(results['errors'])} errors")
        self.logger.info("")

        return results

    def update_and_close_change_requests(self, session_id: str, cr_ids: List[str]) -> Dict[str, Any]:
        """
        Update and close change requests

        Args:
            session_id: Chat session ID
            cr_ids: List of change request IDs to close

        Returns:
            Update results
        """
        self.logger.info("=" * 80)
        self.logger.info("🔄 UPDATING AND CLOSING CHANGE REQUESTS")
        self.logger.info("=" * 80)
        self.logger.info("")

        results = {
            "updated": 0,
            "closed": 0,
            "errors": []
        }

        self.change_requests_dir.mkdir(parents=True, exist_ok=True)

        for cr_id in cr_ids:
            try:
                # Find change request file
                cr_file = self.change_requests_dir / f"{cr_id}.json"
                if not cr_file.exists():
                    # Try alternative naming
                    cr_files = list(self.change_requests_dir.glob(f"*{cr_id}*.json"))
                    if cr_files:
                        cr_file = cr_files[0]
                    else:
                        self.logger.warning(f"⚠️  Change request {cr_id} not found")
                        results["errors"].append(f"Change request {cr_id} not found")
                        continue

                # Load change request
                with open(cr_file, 'r') as f:
                    cr = json.load(f)

                # Update change request
                cr["status"] = "closed"
                cr["closure_date"] = datetime.now().isoformat()
                cr["closed_by"] = "JARVIS Workflow Decisioning Closer"
                cr["closure_notes"] = f"Workflow completed via session {session_id}"
                cr["session_id"] = session_id

                # Save updated change request
                with open(cr_file, 'w') as f:
                    json.dump(cr, f, indent=2)

                results["updated"] += 1
                results["closed"] += 1
                self.logger.info(f"✅ Updated and closed change request: {cr_id}")

            except Exception as e:
                self.logger.error(f"❌ Error updating change request {cr_id}: {e}")
                results["errors"].append(f"Change request {cr_id}: {str(e)}")

        self.logger.info("")
        self.logger.info(f"📊 Change Requests: {results['updated']} updated, {results['closed']} closed")
        if results["errors"]:
            self.logger.warning(f"⚠️  {len(results['errors'])} errors")
        self.logger.info("")

        return results

    def archive_chat_session(self, session_id: str) -> Dict[str, Any]:
        """
        Archive agent chat session

        Args:
            session_id: Chat session ID to archive

        Returns:
            Archive results
        """
        self.logger.info("=" * 80)
        self.logger.info("📦 ARCHIVING CHAT SESSION")
        self.logger.info("=" * 80)
        self.logger.info("")

        if not self.archiver:
            self.logger.warning("⚠️  Archiver not available - skipping")
            return {"archived": False, "error": "Archiver not available"}

        try:
            # Use archiver to archive session
            result = self.archiver.archive_session(session_id)

            if result.get("archived"):
                self.logger.info(f"✅ Archived chat session: {session_id}")
            else:
                self.logger.warning(f"⚠️  Could not archive session: {session_id}")
                self.logger.warning(f"   Reason: {result.get('error', 'Unknown')}")

            return result

        except Exception as e:
            self.logger.error(f"❌ Error archiving session {session_id}: {e}")
            return {"archived": False, "error": str(e)}

    def close_workflow(self, session_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            """
            Complete workflow closing process

            Workflow:
            1. #DECISIONING - Determine completion
            2. Update/close tickets, PM tasks, change requests
            3. Archive chat session

            Args:
                session_id: Chat session ID
                workflow_data: Workflow data including tickets, tasks, etc.

            Returns:
                Complete workflow closing results
            """
            self.logger.info("=" * 80)
            self.logger.info("🚀 JARVIS WORKFLOW DECISIONING CLOSER")
            self.logger.info("=" * 80)
            self.logger.info("")
            self.logger.info(f"Session ID: {session_id}")
            self.logger.info("")

            results = {
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "decision": None,
                "tickets": None,
                "pm_tasks": None,
                "change_requests": None,
                "archive": None,
                "success": False
            }

            # Step 1: #DECISIONING
            self.logger.info("Step 1: #DECISIONING - Assessing workflow completion...")
            self.logger.info("")
            decision = self.decision_workflow_complete(session_id, workflow_data)
            results["decision"] = decision

            if decision.get("action") not in ["keep_all", "save", "continue"]:
                self.logger.warning("⚠️  Workflow not ready for closure")
                self.logger.warning(f"   Decision: {decision.get('action')}")
                self.logger.warning("   Skipping closure steps")
                return results

            # Step 2: Update and close tickets, PM tasks, change requests
            self.logger.info("Step 2: Updating and closing tickets, PM tasks, change requests...")
            self.logger.info("")

            # Extract IDs from workflow data
            ticket_ids = workflow_data.get("ticket_ids", [])
            pm_task_ids = workflow_data.get("pm_task_ids", [])
            change_request_ids = workflow_data.get("change_request_ids", [])

            # Update and close tickets
            if ticket_ids:
                results["tickets"] = self.update_and_close_tickets(session_id, ticket_ids)

            # Update and close PM tasks
            if pm_task_ids:
                results["pm_tasks"] = self.update_and_close_pm_tasks(session_id, pm_task_ids)

            # Update and close change requests
            if change_request_ids:
                results["change_requests"] = self.update_and_close_change_requests(session_id, change_request_ids)

            # Step 3: Ensure MANUS full control of Cursor IDE
            if self.manus_full_control:
                self.logger.info("Step 3: Verifying MANUS full control of Cursor IDE...")
                self.logger.info("")

                # Get visibility of current Cursor IDE state
                visibility = self.manus_full_control.get_visibility()
                results["manus_control"] = {
                    "available": True,
                    "visibility": visibility,
                    "features_available": len(self.manus_full_control.get_all_features().get("features", {}))
                }

                self.logger.info(f"✅ MANUS Full Control: {results['manus_control']['features_available']} features available")
                self.logger.info("")
            else:
                results["manus_control"] = {
                    "available": False,
                    "error": "MANUS Full Control not available"
                }
                self.logger.warning("⚠️  MANUS Full Control not available")
                self.logger.info("")

            # Step 4: Archive chat session
            self.logger.info("Step 4: Archiving chat session...")
            self.logger.info("")
            results["archive"] = self.archive_chat_session(session_id)

            # Final summary
            self.logger.info("")
            self.logger.info("=" * 80)
            self.logger.info("✅ WORKFLOW CLOSURE COMPLETE")
            self.logger.info("=" * 80)
            self.logger.info("")

            tickets_closed = results.get("tickets", {}).get("closed", 0) if results.get("tickets") else 0
            pm_tasks_closed = results.get("pm_tasks", {}).get("closed", 0) if results.get("pm_tasks") else 0
            crs_closed = results.get("change_requests", {}).get("closed", 0) if results.get("change_requests") else 0
            archived = results.get("archive", {}).get("archived", False) if results.get("archive") else False

            self.logger.info(f"📊 Summary:")
            self.logger.info(f"   Tickets closed: {tickets_closed}")
            self.logger.info(f"   PM tasks closed: {pm_tasks_closed}")
            self.logger.info(f"   Change requests closed: {crs_closed}")
            self.logger.info(f"   Session archived: {'✅' if archived else '❌'}")
            self.logger.info("")

            results["success"] = archived and (tickets_closed > 0 or pm_tasks_closed > 0 or crs_closed > 0)

            return results


        except Exception as e:
            self.logger.error(f"Error in close_workflow: {e}", exc_info=True)
            raise
def main():
    try:
        """CLI entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Workflow Decisioning Closer")
        parser.add_argument('--session-id', required=True, help='Chat session ID')
        parser.add_argument('--ticket-ids', nargs='+', default=[], help='Ticket IDs to close')
        parser.add_argument('--pm-task-ids', nargs='+', default=[], help='PM task IDs to close')
        parser.add_argument('--change-request-ids', nargs='+', default=[], help='Change request IDs to close')
        parser.add_argument('--workflow-data', type=Path, help='Workflow data JSON file')
        parser.add_argument('--project-root', type=Path, help='Project root directory')

        args = parser.parse_args()

        closer = WorkflowDecisioningCloser(project_root=args.project_root or PROJECT_ROOT)

        # Load workflow data
        workflow_data = {}
        if args.workflow_data and args.workflow_data.exists():
            with open(args.workflow_data, 'r') as f:
                workflow_data = json.load(f)

        # Override with CLI args
        if args.ticket_ids:
            workflow_data["ticket_ids"] = args.ticket_ids
        if args.pm_task_ids:
            workflow_data["pm_task_ids"] = args.pm_task_ids
        if args.change_request_ids:
            workflow_data["change_request_ids"] = args.change_request_ids

        # Close workflow
        results = closer.close_workflow(args.session_id, workflow_data)

        # Save results
        results_file = PROJECT_ROOT / "data" / "workflow_closures" / f"{args.session_id}_closure_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

        return 0 if results["success"] else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())