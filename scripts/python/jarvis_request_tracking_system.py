#!/usr/bin/env python3
"""
JARVIS Request Tracking System

Tracks all requests by Request ID. Request ID is the confirmation - no double confirmations needed.
Integrates with Problem Management and Change Management for feedback, sign-off, and status tracking.
Generates escalation reports based on decisioning trees when needed.
Provides analytics and metrics for all tickets/requests.

Tags: #REQUEST_TRACKING #PROBLEM_MANAGEMENT #CHANGE_MANAGEMENT #ESCALATION #ANALYTICS #METRICS @JARVIS @LUMINA
"""

import sys
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("JARVISRequestTracking")
except ImportError:
    try:
        from lumina_logger import get_logger
        logger = get_logger("JARVISRequestTracking")
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("JARVISRequestTracking")


class RequestStatus(Enum):
    """Request statuses"""
    PENDING = "pending"
    IN_FLIGHT = "in_flight"
    PARTIAL = "partial"
    APPROVED = "approved"
    DISAPPROVED = "disapproved"
    COMPLETED = "completed"
    FAILED = "failed"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"


class EscalationReason(Enum):
    """Escalation reasons"""
    DECISIONING_TREE_TRIGGER = "decisioning_tree_trigger"
    HIGH_IMPACT = "high_impact"
    RESOURCE_CONSTRAINT = "resource_constraint"
    TIMEOUT = "timeout"
    ERROR = "error"
    APPROVAL_REQUIRED = "approval_required"
    CHANGE_MANAGEMENT_REQUIRED = "change_management_required"
    PROBLEM_MANAGEMENT_REQUIRED = "problem_management_required"


class RequestTrackingSystem:
    """Request tracking system with PM/CM integration"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "request_tracking"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.requests_file = self.data_dir / "requests.json"
        self.escalations_file = self.data_dir / "escalations.jsonl"
        self.analytics_file = self.data_dir / "analytics.json"

        # Load problem and change management configs
        self.problem_mgmt_config = self._load_team_config("problem_management_team.json")
        self.change_mgmt_config = self._load_team_config("change_management_team.json")

        # Load existing requests
        self.requests = self._load_requests()

    def _load_team_config(self, config_file: str) -> Dict[str, Any]:
        """Load team configuration"""
        config_path = self.project_root / "config" / "helpdesk" / config_file
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading {config_file}: {e}")
        return {}

    def _load_requests(self) -> Dict[str, Any]:
        """Load existing requests"""
        if self.requests_file.exists():
            try:
                with open(self.requests_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading requests: {e}")
        return {"requests": {}, "metadata": {"last_updated": None, "total_requests": 0}}

    def _save_requests(self):
        """Save requests to file"""
        self.requests["metadata"]["last_updated"] = datetime.now().isoformat()
        self.requests["metadata"]["total_requests"] = len(self.requests.get("requests", {}))
        try:
            with open(self.requests_file, 'w', encoding='utf-8') as f:
                json.dump(self.requests, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving requests: {e}")

    def create_request(
        self,
        request_id: str,
        description: str,
        requires_escalation: bool = False,
        escalation_reason: Optional[EscalationReason] = None,
        requires_problem_mgmt: bool = False,
        requires_change_mgmt: bool = False
    ) -> Dict[str, Any]:
        """Create a new request - Request ID is the confirmation"""
        request = {
            "request_id": request_id,
            "description": description,
            "status": RequestStatus.PENDING.value,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "requires_escalation": requires_escalation,
            "escalation_reason": escalation_reason.value if escalation_reason else None,
            "requires_problem_mgmt": requires_problem_mgmt,
            "requires_change_mgmt": requires_change_mgmt,
            "problem_management": {
                "required": requires_problem_mgmt,
                "feedback": None,
                "sign_off": None,
                "sign_off_by": None,
                "sign_off_at": None,
                "status": None
            },
            "change_management": {
                "required": requires_change_mgmt,
                "feedback": None,
                "sign_off": None,
                "sign_off_by": None,
                "sign_off_at": None,
                "status": None
            },
            "escalation_reports": [],
            "analytics": {
                "time_to_completion": None,
                "time_in_status": {},
                "escalation_count": 0,
                "status_changes": []
            }
        }

        self.requests.setdefault("requests", {})[request_id] = request
        self._save_requests()

        logger.info(f"✅ Request created: {request_id} - {description}")

        # Generate escalation report if needed
        if requires_escalation:
            self._generate_escalation_report(request_id, escalation_reason)

        return request

    def update_request_status(
        self,
        request_id: str,
        status: RequestStatus,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update request status"""
        if request_id not in self.requests.get("requests", {}):
            return {"error": f"Request not found: {request_id}"}

        request = self.requests["requests"][request_id]
        old_status = request["status"]
        request["status"] = status.value
        request["updated_at"] = datetime.now().isoformat()

        # Track status change
        request["analytics"]["status_changes"].append({
            "from": old_status,
            "to": status.value,
            "timestamp": datetime.now().isoformat(),
            "notes": notes
        })

        # Track time in status
        if old_status not in request["analytics"]["time_in_status"]:
            request["analytics"]["time_in_status"][old_status] = 0

        self._save_requests()

        logger.info(f"📝 Request status updated: {request_id} - {old_status} → {status.value}")

        return request

    def add_problem_management_feedback(
        self,
        request_id: str,
        feedback: str,
        sign_off: str,  # "approved", "disapproved", "pending"
        sign_off_by: str = "@marvin"
    ) -> Dict[str, Any]:
        """Add problem management feedback and sign-off"""
        if request_id not in self.requests.get("requests", {}):
            return {"error": f"Request not found: {request_id}"}

        request = self.requests["requests"][request_id]
        request["problem_management"]["feedback"] = feedback
        request["problem_management"]["sign_off"] = sign_off
        request["problem_management"]["sign_off_by"] = sign_off_by
        request["problem_management"]["sign_off_at"] = datetime.now().isoformat()
        request["problem_management"]["status"] = sign_off
        request["updated_at"] = datetime.now().isoformat()

        self._save_requests()

        logger.info(f"📋 Problem Management feedback added: {request_id} - {sign_off}")

        return request

    def add_change_management_feedback(
        self,
        request_id: str,
        feedback: str,
        sign_off: str,  # "approved", "disapproved", "pending"
        sign_off_by: str = "@c3po"
    ) -> Dict[str, Any]:
        """Add change management feedback and sign-off"""
        if request_id not in self.requests.get("requests", {}):
            return {"error": f"Request not found: {request_id}"}

        request = self.requests["requests"][request_id]
        request["change_management"]["feedback"] = feedback
        request["change_management"]["sign_off"] = sign_off
        request["change_management"]["sign_off_by"] = sign_off_by
        request["change_management"]["sign_off_at"] = datetime.now().isoformat()
        request["change_management"]["status"] = sign_off
        request["updated_at"] = datetime.now().isoformat()

        self._save_requests()

        logger.info(f"📋 Change Management feedback added: {request_id} - {sign_off}")

        return request

    def _generate_escalation_report(
        self,
        request_id: str,
        reason: Optional[EscalationReason]
    ) -> Dict[str, Any]:
        """Generate escalation report based on decisioning tree"""
        if request_id not in self.requests.get("requests", {}):
            return {}

        request = self.requests["requests"][request_id]

        escalation_report = {
            "escalation_id": f"escal_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "reason": reason.value if reason else "unknown",
            "decisioning_tree": self._get_decisioning_tree(reason),
            "impact": self._assess_impact(request),
            "recommendations": self._get_recommendations(reason, request),
            "status": "open"
        }

        request["escalation_reports"].append(escalation_report)
        request["analytics"]["escalation_count"] = len(request["escalation_reports"])
        request["status"] = RequestStatus.ESCALATED.value

        # Log escalation
        try:
            with open(self.escalations_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(escalation_report) + '\n')
        except Exception as e:
            logger.error(f"Error logging escalation: {e}")

        logger.warning(f"🚨 ESCALATION REPORT: {request_id} - {reason.value if reason else 'unknown'}")

        return escalation_report

    def _get_decisioning_tree(self, reason: Optional[EscalationReason]) -> Dict[str, Any]:
        """Get decisioning tree based on escalation reason"""
        trees = {
            EscalationReason.DECISIONING_TREE_TRIGGER: {
                "name": "Decisioning Tree Trigger",
                "steps": [
                    "Assess request complexity",
                    "Evaluate resource requirements",
                    "Check approval requirements",
                    "Determine escalation path"
                ]
            },
            EscalationReason.HIGH_IMPACT: {
                "name": "High Impact Escalation",
                "steps": [
                    "Assess impact scope",
                    "Identify affected systems",
                    "Evaluate risk level",
                    "Require PM/CM sign-off"
                ]
            },
            EscalationReason.APPROVAL_REQUIRED: {
                "name": "Approval Required",
                "steps": [
                    "Route to Problem Management",
                    "Route to Change Management",
                    "Wait for sign-off",
                    "Proceed based on approval"
                ]
            }
        }

        return trees.get(reason, {"name": "Standard Escalation", "steps": ["Review", "Assess", "Decide"]})

    def _assess_impact(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Assess impact of request"""
        return {
            "scope": "unknown",
            "severity": "medium",
            "affected_systems": [],
            "risk_level": "medium",
            "estimated_duration": None
        }

    def _get_recommendations(
        self,
        reason: Optional[EscalationReason],
        request: Dict[str, Any]
    ) -> List[str]:
        """Get recommendations based on escalation reason"""
        recommendations = []

        if reason == EscalationReason.PROBLEM_MANAGEMENT_REQUIRED:
            recommendations.append("Route to Problem Management team for analysis")
            recommendations.append("Require PM sign-off before proceeding")

        if reason == EscalationReason.CHANGE_MANAGEMENT_REQUIRED:
            recommendations.append("Route to Change Management team for impact analysis")
            recommendations.append("Require CM sign-off before deployment")

        if request.get("requires_problem_mgmt"):
            recommendations.append("Problem Management review required")

        if request.get("requires_change_mgmt"):
            recommendations.append("Change Management review required")

        return recommendations

    def get_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        try:
            """Get request by ID"""
            return self.requests.get("requests", {}).get(request_id)

        except Exception as e:
            self.logger.error(f"Error in get_request: {e}", exc_info=True)
            raise
    def get_all_requests(
        self,
        status: Optional[RequestStatus] = None,
        requires_pm: Optional[bool] = None,
        requires_cm: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """Get all requests with optional filters"""
        requests = list(self.requests.get("requests", {}).values())

        if status:
            requests = [r for r in requests if r["status"] == status.value]

        if requires_pm is not None:
            requests = [r for r in requests if r["requires_problem_mgmt"] == requires_pm]

        if requires_cm is not None:
            requests = [r for r in requests if r["requires_change_mgmt"] == requires_cm]

        return requests

    def generate_analytics(self) -> Dict[str, Any]:
        """Generate analytics and metrics for all requests"""
        requests = list(self.requests.get("requests", {}).values())

        analytics = {
            "generated_at": datetime.now().isoformat(),
            "total_requests": len(requests),
            "by_status": {},
            "by_escalation": {
                "escalated": 0,
                "not_escalated": 0
            },
            "by_management": {
                "requires_pm": 0,
                "requires_cm": 0,
                "requires_both": 0,
                "requires_none": 0
            },
            "sign_offs": {
                "pm_approved": 0,
                "pm_disapproved": 0,
                "pm_pending": 0,
                "cm_approved": 0,
                "cm_disapproved": 0,
                "cm_pending": 0
            },
            "average_time_to_completion": None,
            "escalation_reasons": {},
            "status_transitions": {}
        }

        # Count by status
        for request in requests:
            status = request["status"]
            analytics["by_status"][status] = analytics["by_status"].get(status, 0) + 1

            # Escalation
            if request.get("requires_escalation") or request["status"] == RequestStatus.ESCALATED.value:
                analytics["by_escalation"]["escalated"] += 1
            else:
                analytics["by_escalation"]["not_escalated"] += 1

            # Management requirements
            requires_pm = request.get("requires_problem_mgmt", False)
            requires_cm = request.get("requires_change_mgmt", False)

            if requires_pm and requires_cm:
                analytics["by_management"]["requires_both"] += 1
            elif requires_pm:
                analytics["by_management"]["requires_pm"] += 1
            elif requires_cm:
                analytics["by_management"]["requires_cm"] += 1
            else:
                analytics["by_management"]["requires_none"] += 1

            # Sign-offs
            pm_sign_off = request.get("problem_management", {}).get("sign_off")
            if pm_sign_off:
                analytics["sign_offs"][f"pm_{pm_sign_off}"] = analytics["sign_offs"].get(f"pm_{pm_sign_off}", 0) + 1

            cm_sign_off = request.get("change_management", {}).get("sign_off")
            if cm_sign_off:
                analytics["sign_offs"][f"cm_{cm_sign_off}"] = analytics["sign_offs"].get(f"cm_{cm_sign_off}", 0) + 1

            # Escalation reasons
            escalation_reason = request.get("escalation_reason")
            if escalation_reason:
                analytics["escalation_reasons"][escalation_reason] = analytics["escalation_reasons"].get(escalation_reason, 0) + 1

        # Save analytics
        try:
            with open(self.analytics_file, 'w', encoding='utf-8') as f:
                json.dump(analytics, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving analytics: {e}")

        return analytics


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Request Tracking System")
        parser.add_argument("--create", type=str, nargs=2, metavar=("REQUEST_ID", "DESCRIPTION"),
                           help="Create new request")
        parser.add_argument("--update-status", type=str, nargs=2, metavar=("REQUEST_ID", "STATUS"),
                           help="Update request status")
        parser.add_argument("--pm-feedback", type=str, nargs=4, metavar=("REQUEST_ID", "FEEDBACK", "SIGN_OFF", "SIGN_OFF_BY"),
                           help="Add problem management feedback")
        parser.add_argument("--cm-feedback", type=str, nargs=4, metavar=("REQUEST_ID", "FEEDBACK", "SIGN_OFF", "SIGN_OFF_BY"),
                           help="Add change management feedback")
        parser.add_argument("--get", type=str, metavar="REQUEST_ID", help="Get request by ID")
        parser.add_argument("--list", action="store_true", help="List all requests")
        parser.add_argument("--analytics", action="store_true", help="Generate analytics")
        parser.add_argument("--escalate", type=str, nargs=2, metavar=("REQUEST_ID", "REASON"),
                           help="Escalate request")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        system = RequestTrackingSystem(project_root)

        if args.create:
            request = system.create_request(args.create[0], args.create[1])
            print("=" * 80)
            print("REQUEST CREATED")
            print("=" * 80)
            print(json.dumps(request, indent=2, default=str))

        elif args.update_status:
            status = RequestStatus(args.update_status[1])
            request = system.update_request_status(args.update_status[0], status)
            print("=" * 80)
            print("REQUEST STATUS UPDATED")
            print("=" * 80)
            print(json.dumps(request, indent=2, default=str))

        elif args.pm_feedback:
            request = system.add_problem_management_feedback(
                args.pm_feedback[0],
                args.pm_feedback[1],
                args.pm_feedback[2],
                args.pm_feedback[3] if len(args.pm_feedback) > 3 else "@marvin"
            )
            print("=" * 80)
            print("PROBLEM MANAGEMENT FEEDBACK ADDED")
            print("=" * 80)
            print(json.dumps(request, indent=2, default=str))

        elif args.cm_feedback:
            request = system.add_change_management_feedback(
                args.cm_feedback[0],
                args.cm_feedback[1],
                args.cm_feedback[2],
                args.cm_feedback[3] if len(args.cm_feedback) > 3 else "@c3po"
            )
            print("=" * 80)
            print("CHANGE MANAGEMENT FEEDBACK ADDED")
            print("=" * 80)
            print(json.dumps(request, indent=2, default=str))

        elif args.get:
            request = system.get_request(args.get)
            if request:
                print("=" * 80)
                print("REQUEST DETAILS")
                print("=" * 80)
                print(json.dumps(request, indent=2, default=str))
            else:
                print(f"Request not found: {args.get}")

        elif args.list:
            requests = system.get_all_requests()
            print("=" * 80)
            print(f"ALL REQUESTS ({len(requests)})")
            print("=" * 80)
            for req in requests:
                print(f"{req['request_id']}: {req['status']} - {req['description'][:50]}...")

        elif args.analytics:
            analytics = system.generate_analytics()
            print("=" * 80)
            print("ANALYTICS AND METRICS")
            print("=" * 80)
            print(json.dumps(analytics, indent=2, default=str))

        elif args.escalate:
            reason = EscalationReason(args.escalate[1])
            report = system._generate_escalation_report(args.escalate[0], reason)
            print("=" * 80)
            print("ESCALATION REPORT")
            print("=" * 80)
            print(json.dumps(report, indent=2, default=str))

        else:
            print("JARVIS Request Tracking System")
            print("Use --help for usage information")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()