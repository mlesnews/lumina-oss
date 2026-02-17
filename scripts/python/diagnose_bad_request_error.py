#!/usr/bin/env python3
"""
Diagnose Bad Request Error - Request ID: 190bb1d5-5473-4079-8509-7bb88b348d96

Investigates and attempts to resolve ERROR_BAD_REQUEST errors.

Tags: #ERROR #DIAGNOSTIC #REQUEST #TROUBLESHOOTING @JARVIS @RR
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DiagnoseBadRequest")

# Request tracking
try:
    from request_tracking_system import RequestTracker
    REQUEST_TRACKING_AVAILABLE = True
except ImportError:
    REQUEST_TRACKING_AVAILABLE = False
    RequestTracker = None

# Universal workflow troubleshooting
try:
    from universal_workflow_troubleshooting import UniversalWorkflowTroubleshooting
    TROUBLESHOOTING_AVAILABLE = True
except ImportError:
    TROUBLESHOOTING_AVAILABLE = False
    UniversalWorkflowTroubleshooting = None


class BadRequestDiagnostic:
    """
    Diagnostic tool for ERROR_BAD_REQUEST errors
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize diagnostic tool"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.error_logs_dir = self.data_dir / "error_logs"
        self.error_logs_dir.mkdir(parents=True, exist_ok=True)

        # Request tracker
        self.request_tracker = None
        if REQUEST_TRACKING_AVAILABLE:
            try:
                self.request_tracker = RequestTracker(project_root=self.project_root)
                logger.info("✅ Request tracker initialized")
            except Exception as e:
                logger.warning(f"⚠️  Request tracker not available: {e}")

        # Troubleshooting system
        self.troubleshooter = None
        if TROUBLESHOOTING_AVAILABLE:
            try:
                self.troubleshooter = UniversalWorkflowTroubleshooting(project_root=self.project_root)
                logger.info("✅ Workflow troubleshooter initialized")
            except Exception as e:
                logger.warning(f"⚠️  Troubleshooter not available: {e}")

        logger.info("✅ Bad Request Diagnostic initialized")

    def diagnose_request_error(self, request_id: str, error_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Diagnose a bad request error

        Args:
            request_id: The request ID that failed
            error_data: The error response data

        Returns:
            Diagnostic report with findings and recommendations
        """
        logger.info(f"🔍 Diagnosing bad request error: {request_id}")

        diagnostic = {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "error_type": error_data.get("error", "UNKNOWN"),
            "error_details": error_data.get("details", {}),
            "is_retryable": error_data.get("isRetryable", False),
            "is_expected": error_data.get("isExpected", False),
            "findings": [],
            "recommendations": [],
            "actions_taken": []
        }

        # Analyze error details
        details = error_data.get("details", {})
        title = details.get("title", "")
        detail = details.get("detail", "")

        # Finding 1: Check if request ID exists in tracking
        if self.request_tracker:
            try:
                tracked_request = self.request_tracker.get_request(request_id)
                if tracked_request:
                    diagnostic["findings"].append({
                        "type": "request_found",
                        "message": f"Request {request_id} found in tracking system",
                        "data": tracked_request
                    })
                else:
                    diagnostic["findings"].append({
                        "type": "request_not_found",
                        "message": f"Request {request_id} not found in tracking system",
                        "severity": "medium"
                    })
            except Exception as e:
                diagnostic["findings"].append({
                    "type": "tracking_error",
                    "message": f"Error checking request tracking: {e}",
                    "severity": "low"
                })

        # Finding 2: Analyze error message
        if "Bad request" in title or "Bad Request" in detail:
            diagnostic["findings"].append({
                "type": "bad_request",
                "message": "Generic bad request error - likely invalid parameters or malformed request",
                "severity": "high",
                "common_causes": [
                    "Invalid API parameters",
                    "Malformed request body",
                    "Missing required fields",
                    "Invalid authentication",
                    "Rate limiting",
                    "Request size too large"
                ]
            })

        # Finding 3: Check retryability
        if not error_data.get("isRetryable", False):
            diagnostic["findings"].append({
                "type": "not_retryable",
                "message": "Error is not retryable - indicates permanent failure",
                "severity": "high",
                "recommendation": "Fix the request before retrying"
            })

        # Finding 4: Check if expected
        if error_data.get("isExpected", False):
            diagnostic["findings"].append({
                "type": "expected_error",
                "message": "Error is marked as expected - may be handled gracefully",
                "severity": "low"
            })

        # Finding 5: Check for additional info
        additional_info = details.get("additionalInfo", {})
        if additional_info:
            diagnostic["findings"].append({
                "type": "additional_info",
                "message": "Additional error information available",
                "data": additional_info
            })

        # Generate recommendations
        diagnostic["recommendations"] = self._generate_recommendations(diagnostic)

        # Attempt automatic fixes
        diagnostic["actions_taken"] = self._attempt_fixes(diagnostic)

        # Save diagnostic report
        self._save_diagnostic(diagnostic)

        return diagnostic

    def _generate_recommendations(self, diagnostic: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on findings"""
        recommendations = []

        findings = diagnostic.get("findings", [])

        # Recommendation 1: Validate request parameters
        bad_request_found = any(f.get("type") == "bad_request" for f in findings)
        if bad_request_found:
            recommendations.append({
                "priority": "high",
                "action": "validate_request_parameters",
                "message": "Review and validate all request parameters",
                "steps": [
                    "Check required fields are present",
                    "Validate parameter types and formats",
                    "Verify parameter values are within acceptable ranges",
                    "Check for special characters or encoding issues"
                ]
            })

        # Recommendation 2: Check authentication
        recommendations.append({
            "priority": "medium",
            "action": "check_authentication",
            "message": "Verify authentication credentials are valid",
            "steps": [
                "Check API keys/tokens are not expired",
                "Verify authentication headers are correct",
                "Ensure credentials have necessary permissions"
            ]
        })

        # Recommendation 3: Review request format
        recommendations.append({
            "priority": "medium",
            "action": "review_request_format",
            "message": "Ensure request follows API specification",
            "steps": [
                "Check request body format (JSON, XML, etc.)",
                "Verify Content-Type header matches body format",
                "Check for proper encoding (UTF-8)",
                "Validate JSON structure if applicable"
            ]
        })

        # Recommendation 4: Check rate limits
        recommendations.append({
            "priority": "low",
            "action": "check_rate_limits",
            "message": "Verify not exceeding API rate limits",
            "steps": [
                "Check current request rate",
                "Review API rate limit documentation",
                "Implement exponential backoff if needed"
            ]
        })

        # Recommendation 5: Use troubleshooting system
        if self.troubleshooter:
            recommendations.append({
                "priority": "high",
                "action": "run_troubleshooting",
                "message": "Run universal workflow troubleshooting",
                "steps": [
                    "Execute workflow troubleshooting system",
                    "Review AI/JARVIS/MARVIN evaluation",
                    "Apply recommended fixes"
                ]
            })

        return recommendations

    def _attempt_fixes(self, diagnostic: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Attempt automatic fixes"""
        actions = []

        # Action 1: Log error for analysis
        actions.append({
            "action": "logged_error",
            "status": "completed",
            "message": "Error logged for analysis"
        })

        # Action 2: Check if request can be reconstructed
        request_id = diagnostic.get("request_id")
        if self.request_tracker and request_id:
            try:
                # Try to get request details
                request_data = self.request_tracker.get_request(request_id)
                if request_data:
                    actions.append({
                        "action": "retrieved_request_data",
                        "status": "completed",
                        "message": f"Retrieved request data for {request_id}",
                        "data": request_data
                    })
            except Exception as e:
                actions.append({
                    "action": "retrieve_request_failed",
                    "status": "failed",
                    "message": f"Could not retrieve request data: {e}"
                })

        # Action 3: Run troubleshooting if available
        if self.troubleshooter:
            try:
                # Create a workflow issue from the error
                workflow_issue = {
                    "type": "api_error",
                    "error": diagnostic.get("error_type"),
                    "request_id": request_id,
                    "details": diagnostic.get("error_details")
                }

                # Run troubleshooting
                troubleshooting_result = self.troubleshooter.diagnose_and_fix(workflow_issue)

                actions.append({
                    "action": "ran_troubleshooting",
                    "status": "completed",
                    "message": "Workflow troubleshooting executed",
                    "result": troubleshooting_result
                })
            except Exception as e:
                actions.append({
                    "action": "troubleshooting_failed",
                    "status": "failed",
                    "message": f"Troubleshooting failed: {e}"
                })

        return actions

    def _save_diagnostic(self, diagnostic: Dict[str, Any]):
        try:
            """Save diagnostic report"""
            request_id = diagnostic.get("request_id", "unknown")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            report_file = self.error_logs_dir / f"bad_request_{request_id}_{timestamp}.json"

            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(diagnostic, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"✅ Diagnostic report saved: {report_file}")

            # Also save to main error log
            error_log_file = self.error_logs_dir / "bad_request_errors.jsonl"
            with open(error_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(diagnostic, ensure_ascii=False, default=str) + "\n")


        except Exception as e:
            self.logger.error(f"Error in _save_diagnostic: {e}", exc_info=True)
            raise
if __name__ == "__main__":
    print("\n" + "="*80)
    print("🔍 Bad Request Error Diagnostic Tool")
    print("="*80 + "\n")

    # Error data from user
    request_id = "190bb1d5-5473-4079-8509-7bb88b348d96"
    error_data = {
        "error": "ERROR_BAD_REQUEST",
        "details": {
            "title": "Bad request.",
            "detail": "Bad Request",
            "isRetryable": False,
            "additionalInfo": {},
            "buttons": [],
            "planChoices": []
        },
        "isExpected": True
    }

    diagnostic_tool = BadRequestDiagnostic()
    result = diagnostic_tool.diagnose_request_error(request_id, error_data)

    print(f"\n📊 Diagnostic Report for Request: {request_id}")
    print(f"   Error Type: {result['error_type']}")
    print(f"   Retryable: {result['is_retryable']}")
    print(f"   Expected: {result['is_expected']}")
    print(f"\n🔍 Findings: {len(result['findings'])}")
    for finding in result['findings']:
        print(f"   - {finding.get('type', 'unknown')}: {finding.get('message', '')}")

    print(f"\n💡 Recommendations: {len(result['recommendations'])}")
    for rec in result['recommendations']:
        print(f"   [{rec.get('priority', 'unknown').upper()}] {rec.get('action', 'unknown')}: {rec.get('message', '')}")

    print(f"\n⚙️  Actions Taken: {len(result['actions_taken'])}")
    for action in result['actions_taken']:
        status_icon = "✅" if action.get('status') == "completed" else "❌"
        print(f"   {status_icon} {action.get('action', 'unknown')}: {action.get('message', '')}")

    print("\n✅ Diagnostic Complete")
    print("="*80 + "\n")
