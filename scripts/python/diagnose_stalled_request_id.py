#!/usr/bin/env python3
"""
Diagnose Stalled Request ID - Comprehensive Analysis and Recovery

Diagnoses stalled Cursor IDE request IDs and provides recovery recommendations.
Request ID: 7a9f31d7-62ff-479b-ae17-3546c5eafeb3

Tags: #CURSOR_IDE #WORKFLOW_STALL #DIAGNOSTIC #RECOVERY @JARVIS @LUMINA
"""

import sys
import json
import traceback
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

logger = get_logger("StalledRequestDiagnostic")


class StalledRequestDiagnostic:
    """
    Comprehensive diagnostic for stalled Cursor IDE request IDs
    """

    def __init__(self, request_id: str, project_root: Optional[Path] = None):
        """Initialize diagnostic tool"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.request_id = request_id
        self.data_dir = self.project_root / "data" / "diagnostics"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        logger.info("=" * 80)
        logger.info(f"🔍 STALLED REQUEST ID DIAGNOSTIC")
        logger.info("=" * 80)
        logger.info(f"Request ID: {request_id}")
        logger.info("")

    def check_connection_health(self) -> Dict[str, Any]:
        """Check connection health metrics"""
        logger.info("STEP 1: Checking Connection Health Metrics...")
        logger.info("-" * 80)

        try:
            from cursor_connection_health_monitor import CursorConnectionHealthMonitor

            monitor = CursorConnectionHealthMonitor(self.project_root)

            # Check if request ID is in metrics
            found_in_metrics = False
            matching_metrics = []

            for metric in monitor.metrics:
                if self.request_id in str(metric.error_message):
                    found_in_metrics = True
                    matching_metrics.append({
                        "timestamp": metric.timestamp,
                        "error_type": metric.error_type,
                        "error_message": metric.error_message,
                        "retry_attempt": metric.retry_attempt,
                        "success": metric.success
                    })

            result = {
                "status": "checked",
                "found_in_metrics": found_in_metrics,
                "matching_metrics": matching_metrics,
                "stats": monitor.stats.copy(),
                "total_metrics": len(monitor.metrics)
            }

            if found_in_metrics:
                logger.info(f"   ✅ Found {len(matching_metrics)} matching metrics")
                for m in matching_metrics:
                    logger.info(f"      • {m['timestamp']}: {m['error_type']}")
            else:
                logger.warning(f"   ⚠️  Request ID not found in connection health metrics")
                logger.info(f"      Total metrics: {len(monitor.metrics)}")
                logger.info(f"      Failed connections: {monitor.stats['failed_connections']}")
                logger.info(f"      Successful connections: {monitor.stats['successful_connections']}")

            logger.info("")
            return result

        except Exception as e:
            logger.error(f"   ❌ Error checking connection health: {e}")
            logger.debug(traceback.format_exc())
            return {
                "status": "error",
                "error": str(e)
            }

    def check_request_tracking(self) -> Dict[str, Any]:
        """Check request ID tracking"""
        logger.info("STEP 2: Checking Request ID Tracking...")
        logger.info("-" * 80)

        try:
            from track_request_id import RequestIDTracker

            tracker = RequestIDTracker(self.project_root)

            # Try to get request data
            tracking_data = tracker.get_request_data(self.request_id)

            if tracking_data:
                logger.info(f"   ✅ Request ID found in tracking")
                logger.info(f"      Status: {tracking_data.get('status', 'unknown')}")
                logger.info(f"      Source: {tracking_data.get('source', 'unknown')}")
                logger.info(f"      Severity: {tracking_data.get('severity', 'unknown')}")

                # Check for stall indicators
                diagnostics = tracking_data.get('diagnostics', {})
                stall_analysis = diagnostics.get('stall_analysis', {})

                if stall_analysis.get('potential_stall'):
                    logger.warning(f"   ⚠️  Potential stall detected: {stall_analysis.get('reason', 'unknown')}")

                return {
                    "status": "found",
                    "data": tracking_data,
                    "stall_analysis": stall_analysis
                }
            else:
                logger.warning(f"   ⚠️  Request ID not found in tracking")

                # Search for diagnostic files
                diagnostic_files = list(self.data_dir.glob(f"*{self.request_id}*"))
                if diagnostic_files:
                    logger.info(f"   ✅ Found {len(diagnostic_files)} diagnostic files")
                    latest_file = max(diagnostic_files, key=lambda f: f.stat().st_mtime)
                    logger.info(f"      Latest: {latest_file.name}")

                return {
                    "status": "not_found",
                    "diagnostic_files": [str(f) for f in diagnostic_files]
                }

        except Exception as e:
            logger.error(f"   ❌ Error checking request tracking: {e}")
            logger.debug(traceback.format_exc())
            return {
                "status": "error",
                "error": str(e)
            }

    def check_retry_manager(self) -> Dict[str, Any]:
        """Check retry manager status"""
        logger.info("STEP 3: Checking Retry Manager...")
        logger.info("-" * 80)

        try:
            from cursor_chat_retry_manager import CursorChatRetryManager

            manager = CursorChatRetryManager()

            result = {
                "status": "checked",
                "config": {
                    "max_retries": manager.max_retries,
                    "initial_delay": manager.initial_delay,
                    "max_delay": manager.max_delay,
                    "strategy": manager.strategy.value
                },
                "retryable_errors": True  # All errors are retryable
            }

            logger.info(f"   ✅ Retry manager configured")
            logger.info(f"      Max retries: {manager.max_retries}")
            logger.info(f"      Initial delay: {manager.initial_delay}s")
            logger.info(f"      Strategy: {manager.strategy.value}")
            logger.info("")

            return result

        except Exception as e:
            logger.error(f"   ❌ Error checking retry manager: {e}")
            logger.debug(traceback.format_exc())
            return {
                "status": "error",
                "error": str(e)
            }

    def check_notification_tickets(self) -> Dict[str, Any]:
        """Check notification tickets"""
        logger.info("STEP 4: Checking Notification Tickets...")
        logger.info("-" * 80)

        try:
            tickets_file = self.project_root / "data" / "notification_tickets" / "tickets.json"

            if not tickets_file.exists():
                logger.warning(f"   ⚠️  Tickets file not found")
                return {"status": "file_not_found"}

            with open(tickets_file, 'r') as f:
                tickets_data = json.load(f)

            tickets = tickets_data.get("tickets", {})
            matching_tickets = []

            for ticket_id, ticket in tickets.items():
                cursor_request_id = ticket.get("cursor_request_id")
                if cursor_request_id == self.request_id:
                    matching_tickets.append({
                        "ticket_id": ticket_id,
                        "title": ticket.get("title"),
                        "status": ticket.get("status"),
                        "priority": ticket.get("priority"),
                        "created_at": ticket.get("created_at")
                    })

            if matching_tickets:
                logger.info(f"   ✅ Found {len(matching_tickets)} matching tickets")
                for ticket in matching_tickets:
                    logger.info(f"      • {ticket['ticket_id']}: {ticket['title']} ({ticket['status']})")
            else:
                logger.warning(f"   ⚠️  No matching tickets found")

            logger.info("")
            return {
                "status": "checked",
                "matching_tickets": matching_tickets,
                "total_tickets": len(tickets)
            }

        except Exception as e:
            logger.error(f"   ❌ Error checking notification tickets: {e}")
            logger.debug(traceback.format_exc())
            return {
                "status": "error",
                "error": str(e)
            }

    def check_error_logs(self) -> Dict[str, Any]:
        """Check error logs for request ID"""
        logger.info("STEP 5: Checking Error Logs...")
        logger.info("-" * 80)

        try:
            from track_request_id import RequestIDTracker

            tracker = RequestIDTracker(self.project_root)
            log_findings = tracker._search_logs(self.request_id)

            if log_findings:
                logger.info(f"   ✅ Found {len(log_findings)} log entries")
                for finding in log_findings[:5]:  # Show first 5
                    logger.info(f"      • {finding['file']}:{finding['line']}")
            else:
                logger.warning(f"   ⚠️  No log entries found")

            logger.info("")
            return {
                "status": "checked",
                "log_findings": log_findings,
                "count": len(log_findings)
            }

        except Exception as e:
            logger.error(f"   ❌ Error checking error logs: {e}")
            logger.debug(traceback.format_exc())
            return {
                "status": "error",
                "error": str(e)
            }

    def generate_recommendations(self, diagnostic_results: Dict[str, Any]) -> List[str]:
        """Generate recovery recommendations"""
        recommendations = []

        # Check connection health
        health = diagnostic_results.get("connection_health", {})
        if not health.get("found_in_metrics"):
            recommendations.append(
                "Request ID not in connection health metrics - may have failed before logging. "
                "Check Cursor IDE connection status and retry the request."
            )

        stats = health.get("stats", {})
        if stats.get("failed_connections", 0) > stats.get("successful_connections", 0):
            recommendations.append(
                f"Connection health is poor ({stats['failed_connections']} failed, "
                f"{stats['successful_connections']} successful). "
                "Check network connectivity and Cursor IDE service status."
            )

        # Check tracking
        tracking = diagnostic_results.get("request_tracking", {})
        if tracking.get("status") == "not_found":
            recommendations.append(
                "Request ID not found in tracking system. "
                "This suggests the request may be stuck in a pending state. "
                "Try manually retrying the request in Cursor IDE."
            )

        # Check retry manager
        retry_manager = diagnostic_results.get("retry_manager", {})
        if retry_manager.get("status") == "checked":
            recommendations.append(
                f"Retry manager is configured (max {retry_manager['config']['max_retries']} retries). "
                "If request fails, it should be automatically retried."
            )

        # Check tickets
        tickets = diagnostic_results.get("notification_tickets", {})
        matching_tickets = tickets.get("matching_tickets", [])
        if matching_tickets:
            open_tickets = [t for t in matching_tickets if t.get("status") == "open"]
            if open_tickets:
                recommendations.append(
                    f"Found {len(open_tickets)} open ticket(s) for this request ID. "
                    "Review ticket status and follow up if needed."
                )

        # Check logs
        logs = diagnostic_results.get("error_logs", {})
        if logs.get("count", 0) == 0:
            recommendations.append(
                "No log entries found for this request ID. "
                "The request may have failed silently or is still pending. "
                "Monitor Cursor IDE for error notifications."
            )

        # General recommendations
        recommendations.extend([
            "If the request is still pending, wait for timeout or manually cancel/retry in Cursor IDE.",
            "Check Cursor IDE connection status and ensure ULTRON/KAIJU services are running.",
            "Review connection health metrics for patterns of failures.",
            "Consider using the operator retry tracker to manually record retry attempts."
        ])

        return recommendations

    def run_full_diagnostic(self) -> Dict[str, Any]:
        try:
            """Run full diagnostic analysis"""
            logger.info("")

            diagnostic_results = {
                "request_id": self.request_id,
                "timestamp": datetime.now().isoformat(),
                "diagnostics": {}
            }

            # Run all checks
            diagnostic_results["connection_health"] = self.check_connection_health()
            diagnostic_results["request_tracking"] = self.check_request_tracking()
            diagnostic_results["retry_manager"] = self.check_retry_manager()
            diagnostic_results["notification_tickets"] = self.check_notification_tickets()
            diagnostic_results["error_logs"] = self.check_error_logs()

            # Generate recommendations
            logger.info("=" * 80)
            logger.info("📊 DIAGNOSTIC SUMMARY")
            logger.info("=" * 80)
            logger.info("")

            recommendations = self.generate_recommendations(diagnostic_results)
            diagnostic_results["recommendations"] = recommendations

            # Determine stall status
            stall_indicators = []

            if not diagnostic_results["connection_health"].get("found_in_metrics"):
                stall_indicators.append("Not found in connection health metrics")

            if diagnostic_results["request_tracking"].get("status") == "not_found":
                stall_indicators.append("Not found in request tracking")

            if diagnostic_results["error_logs"].get("count", 0) == 0:
                stall_indicators.append("No log entries found")

            diagnostic_results["stall_indicators"] = stall_indicators
            diagnostic_results["likely_stalled"] = len(stall_indicators) >= 2

            # Print summary
            logger.info("🔍 FINDINGS:")
            if stall_indicators:
                logger.warning(f"   ⚠️  Stall Indicators ({len(stall_indicators)}):")
                for indicator in stall_indicators:
                    logger.warning(f"      • {indicator}")
            else:
                logger.info("   ✅ No clear stall indicators")

            logger.info("")
            logger.info("💡 RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                logger.info(f"   {i}. {rec}")

            logger.info("")
            logger.info("=" * 80)

            # Save diagnostic results
            diagnostic_file = self.data_dir / f"stalled_request_diagnostic_{self.request_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(diagnostic_file, 'w', encoding='utf-8') as f:
                json.dump(diagnostic_results, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Diagnostic results saved: {diagnostic_file}")
            logger.info("")

            return diagnostic_results


        except Exception as e:
            self.logger.error(f"Error in run_full_diagnostic: {e}", exc_info=True)
            raise
def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Diagnose Stalled Request ID")
    parser.add_argument(
        "--request-id",
        default="7a9f31d7-62ff-479b-ae17-3546c5eafeb3",
        help="Request ID to diagnose"
    )

    args = parser.parse_args()

    diagnostic = StalledRequestDiagnostic(args.request_id)
    results = diagnostic.run_full_diagnostic()

    logger.info("")
    logger.info("✅ Diagnostic complete")

    if results.get("likely_stalled"):
        logger.warning("⚠️  Request ID appears to be stalled - review recommendations above")
        return 1
    else:
        logger.info("✅ Request ID status unclear - may be pending or completed")
        return 0


if __name__ == "__main__":


    sys.exit(main())