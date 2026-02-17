#!/usr/bin/env python3
"""
JARVIS Automatic Workflow Archiver

Automatically archives workflows, helpdesk tickets, and business/technical areas when:
1. Certification has passed
2. All documentation is complete and successful
3. No issues remain

Applies to:
- Cursor IDE workflows (and any IDE)
- Framework, agent, and @N8N integrations
- Helpdesk tickets (PM, CM, notification tickets)
- Company business and technical areas
- Maintenance until @EOL and @ROI

Tags: #AUTOMATIC_ARCHIVING #CERTIFICATION #DOCUMENTATION #WORKFLOW #HELPDESK #FINTECH #EOL #ROI
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISAutoArchiver")


class WorkflowCertificationChecker:
    """Checks if workflows meet certification requirements"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.certification_dir = project_root / "data" / "workflow_certifications"
        self.certification_dir.mkdir(parents=True, exist_ok=True)

    def is_certified(self, workflow_id: str, workflow_type: str = "agent") -> bool:
        """Check if workflow has passed certification"""
        cert_file = self.certification_dir / f"{workflow_type}_{workflow_id}_certification.json"

        if not cert_file.exists():
            return False

        try:
            with open(cert_file, 'r', encoding='utf-8') as f:
                cert_data = json.load(f)

            return cert_data.get("status") == "certified" and cert_data.get("passed", False)
        except Exception as e:
            logger.warning(f"   ⚠️  Error checking certification for {workflow_id}: {e}")
            return False

    def get_certification_details(self, workflow_id: str, workflow_type: str = "agent") -> Optional[Dict]:
        """Get certification details"""
        cert_file = self.certification_dir / f"{workflow_type}_{workflow_id}_certification.json"

        if not cert_file.exists():
            return None

        try:
            with open(cert_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None


class DocumentationChecker:
    """Checks if documentation is complete and successful"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.docs_dir = project_root / "docs"
        self.docs_status_dir = project_root / "data" / "documentation_status"
        self.docs_status_dir.mkdir(parents=True, exist_ok=True)

    def is_documentation_complete(self, workflow_id: str, workflow_type: str = "agent") -> tuple[bool, List[str]]:
        """
        Check if documentation is complete and successful

        Returns:
            (is_complete, missing_docs)
        """
        status_file = self.docs_status_dir / f"{workflow_type}_{workflow_id}_docs.json"

        if status_file.exists():
            try:
                with open(status_file, 'r', encoding='utf-8') as f:
                    status = json.load(f)

                if status.get("status") == "complete" and status.get("all_successful", False):
                    return True, []

                missing = status.get("missing_docs", [])
                failed = status.get("failed_docs", [])
                return False, missing + failed
            except Exception as e:
                logger.warning(f"   ⚠️  Error checking docs for {workflow_id}: {e}")

        # Default: assume incomplete if no status file
        return False, ["documentation_status_file_missing"]

    def has_issues(self, workflow_id: str, workflow_type: str = "agent") -> bool:
        """Check if workflow has any documented issues"""
        status_file = self.docs_status_dir / f"{workflow_type}_{workflow_id}_docs.json"

        if status_file.exists():
            try:
                with open(status_file, 'r', encoding='utf-8') as f:
                    status = json.load(f)

                return status.get("has_issues", False) or len(status.get("issues", [])) > 0
            except Exception:
                pass

        return False


class AutomaticWorkflowArchiver:
    """
    Automatic Workflow Archiver

    Archives workflows, tickets, and business areas when they meet all criteria:
    - Certification passed
    - Documentation complete and successful
    - No issues
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Automatic Workflow Archiver"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "workflow_archives"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.cert_checker = WorkflowCertificationChecker(project_root)
        self.docs_checker = DocumentationChecker(project_root)

        # Archive directories
        self.archive_base = self.project_root / "data" / "archives"
        self.archive_base.mkdir(parents=True, exist_ok=True)

        self.helpdesk_archive = self.archive_base / "helpdesk"
        self.workflow_archive = self.archive_base / "workflows"
        self.business_archive = self.archive_base / "business"
        self.technical_archive = self.archive_base / "technical"
        self.n8n_archive = self.archive_base / "n8n"

        for archive_dir in [self.helpdesk_archive, self.workflow_archive, 
                           self.business_archive, self.technical_archive, self.n8n_archive]:
            archive_dir.mkdir(parents=True, exist_ok=True)

        logger.info("✅ Automatic Workflow Archiver initialized")
        logger.info("   🎯 Ready to archive certified, documented, issue-free workflows")

    def check_archiving_criteria(self, item_id: str, item_type: str = "workflow") -> Dict[str, Any]:
        """
        Check if item meets archiving criteria

        Returns:
            {
                "eligible": bool,
                "certified": bool,
                "documentation_complete": bool,
                "no_issues": bool,
                "missing_docs": List[str],
                "issues": List[str]
            }
        """
        certified = self.cert_checker.is_certified(item_id, item_type)
        docs_complete, missing_docs = self.docs_checker.is_documentation_complete(item_id, item_type)
        has_issues = self.docs_checker.has_issues(item_id, item_type)

        eligible = certified and docs_complete and not has_issues

        return {
            "eligible": eligible,
            "certified": certified,
            "documentation_complete": docs_complete,
            "no_issues": not has_issues,
            "missing_docs": missing_docs,
            "issues": [] if not has_issues else ["issues_detected"]
        }

    def archive_helpdesk_ticket(self, ticket_id: str, ticket_type: str = "PM") -> Dict[str, Any]:
        try:
            """Archive a helpdesk ticket if it meets criteria"""
            logger.info(f"   🔍 Checking ticket {ticket_id} for archiving...")

            # Determine ticket file location
            if ticket_type == "PM":
                ticket_file = self.project_root / "data" / "helpdesk" / "tickets" / f"{ticket_id}.json"
            elif ticket_type == "CM":
                ticket_file = self.project_root / "data" / "helpdesk" / "tickets" / f"{ticket_id}.json"
            else:
                # Notification tickets
                tickets_file = self.project_root / "data" / "notification_tickets" / "tickets.json"
                if tickets_file.exists():
                    with open(tickets_file, 'r', encoding='utf-8') as f:
                        tickets_data = json.load(f)
                    ticket = tickets_data.get("tickets", {}).get(ticket_id)
                    if ticket:
                        # Create individual ticket file for archiving
                        ticket_file = self.helpdesk_archive / f"{ticket_id}.json"
                        with open(ticket_file, 'w', encoding='utf-8') as f:
                            json.dump(ticket, f, indent=2, ensure_ascii=False, default=str)
                    else:
                        return {"archived": False, "reason": "ticket_not_found"}
                else:
                    return {"archived": False, "reason": "tickets_file_not_found"}

            if not ticket_file.exists():
                return {"archived": False, "reason": "ticket_file_not_found"}

            # Check criteria
            criteria = self.check_archiving_criteria(ticket_id, f"helpdesk_{ticket_type.lower()}")

            if not criteria["eligible"]:
                return {
                    "archived": False,
                    "reason": "criteria_not_met",
                    "criteria": criteria
                }

            # Read ticket
            with open(ticket_file, 'r', encoding='utf-8') as f:
                ticket_data = json.load(f)

            # Update status to archived
            ticket_data["status"] = "archived"
            ticket_data["archived_at"] = datetime.now().isoformat()
            ticket_data["archived_by"] = "JARVIS_Automatic_Archiver"
            ticket_data["archiving_reason"] = "Certification passed, documentation complete, no issues"
            ticket_data["archive_metadata"] = {
                "certified": True,
                "documentation_complete": True,
                "no_issues": True,
                "certification_details": self.cert_checker.get_certification_details(ticket_id, f"helpdesk_{ticket_type.lower()}")
            }

            # Move to archive
            archive_file = self.helpdesk_archive / f"{ticket_id}_archived_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(archive_file, 'w', encoding='utf-8') as f:
                json.dump(ticket_data, f, indent=2, ensure_ascii=False, default=str)

            # Update original ticket
            ticket_data["archive_location"] = str(archive_file.relative_to(self.project_root))
            with open(ticket_file, 'w', encoding='utf-8') as f:
                json.dump(ticket_data, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"   ✅ Archived ticket {ticket_id}")
            return {"archived": True, "archive_file": str(archive_file)}

        except Exception as e:
            logger.error(f"Error in archive_helpdesk_ticket: {e}", exc_info=True)
            raise

    def archive_workflow(self, workflow_id: str, workflow_type: str = "agent",
                            ide_type: str = "cursor") -> Dict[str, Any]:
        try:
            """Archive an agent workflow if it meets criteria"""
            logger.info(f"   🔍 Checking workflow {workflow_id} ({workflow_type}, {ide_type}) for archiving...")

            # Check criteria
            item_type = f"{ide_type}_{workflow_type}"
            criteria = self.check_archiving_criteria(workflow_id, item_type)

            if not criteria["eligible"]:
                return {
                    "archived": False,
                    "reason": "criteria_not_met",
                    "criteria": criteria
                }

            # Create archive entry
            archive_entry = {
                "workflow_id": workflow_id,
                "workflow_type": workflow_type,
                "ide_type": ide_type,
                "status": "archived",
                "archived_at": datetime.now().isoformat(),
                "archived_by": "JARVIS_Automatic_Archiver",
                "archiving_reason": "Certification passed, documentation complete, no issues",
                "archive_metadata": {
                    "certified": True,
                    "documentation_complete": True,
                    "no_issues": True,
                    "certification_details": self.cert_checker.get_certification_details(workflow_id, item_type),
                    "framework": workflow_type,
                    "ide": ide_type,
                    "maintenance_until_eol": True,
                    "roi_tracking": True
                },
                "eol_tracking": {
                    "end_of_life_date": None,  # To be set when EOL is determined
                    "roi_metrics": {
                        "return_on_investment": None,
                        "tracking_enabled": True
                    }
                }
            }

            # Save to archive
            archive_file = self.workflow_archive / f"{workflow_id}_{ide_type}_{workflow_type}_archived_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(archive_file, 'w', encoding='utf-8') as f:
                json.dump(archive_entry, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"   ✅ Archived workflow {workflow_id}")
            return {"archived": True, "archive_file": str(archive_file)}

        except Exception as e:
            self.logger.error(f"Error in archive_workflow: {e}", exc_info=True)
            raise
    def archive_n8n_integration(self, integration_id: str) -> Dict[str, Any]:
        try:
            """Archive an N8N integration if it meets criteria"""
            logger.info(f"   🔍 Checking N8N integration {integration_id} for archiving...")

            # Check criteria
            criteria = self.check_archiving_criteria(integration_id, "n8n")

            if not criteria["eligible"]:
                return {
                    "archived": False,
                    "reason": "criteria_not_met",
                    "criteria": criteria
                }

            # Create archive entry
            archive_entry = {
                "integration_id": integration_id,
                "integration_type": "n8n",
                "status": "archived",
                "archived_at": datetime.now().isoformat(),
                "archived_by": "JARVIS_Automatic_Archiver",
                "archiving_reason": "Certification passed, documentation complete, no issues",
                "archive_metadata": {
                    "certified": True,
                    "documentation_complete": True,
                    "no_issues": True,
                    "certification_details": self.cert_checker.get_certification_details(integration_id, "n8n"),
                    "maintenance_until_eol": True,
                    "roi_tracking": True
                },
                "eol_tracking": {
                    "end_of_life_date": None,
                    "roi_metrics": {
                        "return_on_investment": None,
                        "tracking_enabled": True
                    }
                }
            }

            # Save to archive
            archive_file = self.n8n_archive / f"{integration_id}_n8n_archived_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(archive_file, 'w', encoding='utf-8') as f:
                json.dump(archive_entry, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"   ✅ Archived N8N integration {integration_id}")
            return {"archived": True, "archive_file": str(archive_file)}

        except Exception as e:
            self.logger.error(f"Error in archive_n8n_integration: {e}", exc_info=True)
            raise
    def archive_business_area(self, area_id: str, area_type: str = "business") -> Dict[str, Any]:
        try:
            """Archive a business or technical area if it meets criteria"""
            logger.info(f"   🔍 Checking {area_type} area {area_id} for archiving...")

            # Check criteria
            criteria = self.check_archiving_criteria(area_id, area_type)

            if not criteria["eligible"]:
                return {
                    "archived": False,
                    "reason": "criteria_not_met",
                    "criteria": criteria
                }

            # Determine archive directory
            archive_dir = self.business_archive if area_type == "business" else self.technical_archive

            # Create archive entry
            archive_entry = {
                "area_id": area_id,
                "area_type": area_type,
                "status": "archived",
                "archived_at": datetime.now().isoformat(),
                "archived_by": "JARVIS_Automatic_Archiver",
                "archiving_reason": "Certification passed, documentation complete, no issues",
                "archive_metadata": {
                    "certified": True,
                    "documentation_complete": True,
                    "no_issues": True,
                    "certification_details": self.cert_checker.get_certification_details(area_id, area_type),
                    "fintech_context": True,
                    "maintenance_until_eol": True,
                    "roi_tracking": True
                },
                "eol_tracking": {
                    "end_of_life_date": None,
                    "roi_metrics": {
                        "return_on_investment": None,
                        "tracking_enabled": True
                    }
                }
            }

            # Save to archive
            archive_file = archive_dir / f"{area_id}_{area_type}_archived_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(archive_file, 'w', encoding='utf-8') as f:
                json.dump(archive_entry, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"   ✅ Archived {area_type} area {area_id}")
            return {"archived": True, "archive_file": str(archive_file)}

        except Exception as e:
            self.logger.error(f"Error in archive_business_area: {e}", exc_info=True)
            raise
    def scan_and_archive_all(self) -> Dict[str, Any]:
        """Scan all items and archive those that meet criteria"""
        logger.info("=" * 80)
        logger.info("🔍 SCANNING FOR ARCHIVABLE ITEMS")
        logger.info("=" * 80)
        logger.info("")

        results = {
            "timestamp": datetime.now().isoformat(),
            "helpdesk_tickets": {"scanned": 0, "archived": 0, "failed": 0},
            "workflows": {"scanned": 0, "archived": 0, "failed": 0},
            "n8n_integrations": {"scanned": 0, "archived": 0, "failed": 0},
            "business_areas": {"scanned": 0, "archived": 0, "failed": 0},
            "technical_areas": {"scanned": 0, "archived": 0, "failed": 0},
            "details": []
        }

        # Scan helpdesk tickets
        logger.info("📋 Scanning helpdesk tickets...")
        tickets_dir = self.project_root / "data" / "helpdesk" / "tickets"
        if tickets_dir.exists():
            for ticket_file in tickets_dir.glob("*.json"):
                if ticket_file.name.startswith("PM"):
                    ticket_type = "PM"
                elif ticket_file.name.startswith("CM"):
                    ticket_type = "CM"
                else:
                    continue

                ticket_id = ticket_file.stem
                results["helpdesk_tickets"]["scanned"] += 1

                try:
                    with open(ticket_file, 'r', encoding='utf-8') as f:
                        ticket_data = json.load(f)

                    # Only archive if status is not already archived
                    if ticket_data.get("status") != "archived":
                        result = self.archive_helpdesk_ticket(ticket_id, ticket_type)
                        if result.get("archived"):
                            results["helpdesk_tickets"]["archived"] += 1
                            results["details"].append({
                                "type": "helpdesk_ticket",
                                "id": ticket_id,
                                "status": "archived"
                            })
                        else:
                            results["helpdesk_tickets"]["failed"] += 1
                except Exception as e:
                    logger.warning(f"   ⚠️  Error processing ticket {ticket_id}: {e}")
                    results["helpdesk_tickets"]["failed"] += 1

        # Scan notification tickets
        notification_tickets_file = self.project_root / "data" / "notification_tickets" / "tickets.json"
        if notification_tickets_file.exists():
            try:
                with open(notification_tickets_file, 'r', encoding='utf-8') as f:
                    tickets_data = json.load(f)

                for ticket_id, ticket_data in tickets_data.get("tickets", {}).items():
                    if ticket_data.get("status") != "archived":
                        results["helpdesk_tickets"]["scanned"] += 1
                        result = self.archive_helpdesk_ticket(ticket_id, "notification")
                        if result.get("archived"):
                            results["helpdesk_tickets"]["archived"] += 1
                            results["details"].append({
                                "type": "notification_ticket",
                                "id": ticket_id,
                                "status": "archived"
                            })
                        else:
                            results["helpdesk_tickets"]["failed"] += 1
            except Exception as e:
                logger.warning(f"   ⚠️  Error processing notification tickets: {e}")

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ ARCHIVING SCAN COMPLETE")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"📊 Summary:")
        logger.info(f"   Helpdesk Tickets: {results['helpdesk_tickets']['scanned']} scanned, "
                   f"{results['helpdesk_tickets']['archived']} archived, "
                   f"{results['helpdesk_tickets']['failed']} failed")
        logger.info(f"   Workflows: {results['workflows']['scanned']} scanned, "
                   f"{results['workflows']['archived']} archived")
        logger.info(f"   N8N Integrations: {results['n8n_integrations']['scanned']} scanned, "
                   f"{results['n8n_integrations']['archived']} archived")
        logger.info("")

        # Save results
        results_file = self.data_dir / f"archiving_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"   📄 Results saved: {results_file.name}")
        logger.info("")

        return results


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Automatic Workflow Archiver")
    parser.add_argument("--scan-all", action="store_true", 
                       help="Scan all items and archive those meeting criteria")
    parser.add_argument("--archive-ticket", type=str, 
                       help="Archive a specific helpdesk ticket (format: TICKET_ID:TYPE)")
    parser.add_argument("--archive-workflow", type=str,
                       help="Archive a specific workflow (format: WORKFLOW_ID:TYPE:IDE)")
    parser.add_argument("--archive-n8n", type=str,
                       help="Archive a specific N8N integration")
    parser.add_argument("--archive-area", type=str,
                       help="Archive a business/technical area (format: AREA_ID:TYPE)")

    args = parser.parse_args()

    archiver = AutomaticWorkflowArchiver()

    if args.scan_all:
        archiver.scan_and_archive_all()
    elif args.archive_ticket:
        parts = args.archive_ticket.split(":")
        ticket_id = parts[0]
        ticket_type = parts[1] if len(parts) > 1 else "PM"
        result = archiver.archive_helpdesk_ticket(ticket_id, ticket_type)
        print(json.dumps(result, indent=2))
    elif args.archive_workflow:
        parts = args.archive_workflow.split(":")
        workflow_id = parts[0]
        workflow_type = parts[1] if len(parts) > 1 else "agent"
        ide_type = parts[2] if len(parts) > 2 else "cursor"
        result = archiver.archive_workflow(workflow_id, workflow_type, ide_type)
        print(json.dumps(result, indent=2))
    elif args.archive_n8n:
        result = archiver.archive_n8n_integration(args.archive_n8n)
        print(json.dumps(result, indent=2))
    elif args.archive_area:
        parts = args.archive_area.split(":")
        area_id = parts[0]
        area_type = parts[1] if len(parts) > 1 else "business"
        result = archiver.archive_business_area(area_id, area_type)
        print(json.dumps(result, indent=2))
    else:
        # Default: scan all
        archiver.scan_and_archive_all()

    return 0


if __name__ == "__main__":


    sys.exit(main())