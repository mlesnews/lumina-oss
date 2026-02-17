#!/usr/bin/env python3
"""
Request ID Tracking System

Tracks Request IDs for connection error debugging, retry manager correlation,
and distributed tracing. Supports #AIMLSEA responsibilities for connection
error handling and observability.

Tags: #AIMLSEA #CONNECTION_ERROR #RETRY_MANAGER #OBSERVABILITY #REQUEST_ID @JARVIS @LUMINA
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        get_logger = lambda name: logging.getLogger(name)

logger = get_logger("RequestIDTracker")


class RequestIDTracker:
    """
    Request ID Tracker for Connection Error Diagnostics

    Tracks Request IDs with full context and observability for debugging
    connection errors, retry manager correlation, and distributed tracing.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Request ID tracker"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.diagnostics_dir = self.project_root / "data" / "diagnostics"
        self.diagnostics_dir.mkdir(parents=True, exist_ok=True)

        logger.info("✅ Request ID Tracker initialized")
        logger.info(f"   Diagnostics directory: {self.diagnostics_dir}")

    def track_request_id(
        self,
        request_id: str,
        source: str = "user_report",
        error_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Track a Request ID with full context

        Args:
            request_id: The Request ID to track
            source: Source of the Request ID (user_report, system, etc.)
            error_type: Type of error (ECONNRESET, ECONNREFUSED, etc.)
            context: Additional context dictionary

        Returns:
            Diagnostic entry dictionary
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"request_id_tracking_{request_id}_{timestamp}.json"
        filepath = self.diagnostics_dir / filename

        # Determine error type from context if not provided
        if error_type is None and context:
            error_type = context.get("error_type") or context.get("user_error", "").upper()
            if "ECONNRESET" in error_type:
                error_type = "ECONNRESET"
            elif "ECONNREFUSED" in error_type:
                error_type = "ECONNREFUSED"
            elif "ETIMEDOUT" in error_type:
                error_type = "ETIMEDOUT"
            else:
                error_type = "UNKNOWN"

        # Build diagnostic entry
        diagnostic = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "status": "tracked",
            "source": source,
            "tags": [
                "#CURSOR_IDE",
                f"#{error_type}" if error_type else "#CONNECT_ERROR",
                "#CONNECT_ERROR",
                "@JARVIS",
                "@LUMINA",
                "#AIMLSEA"
            ],
            "context": {
                "tracked_at": datetime.now().isoformat(),
                "tracked_by": source,
                "purpose": "Request ID tracking for connection error investigation",
                "user_error": context.get("user_error", "") if context else "",
                "related_systems": [
                    "@JARVIS",
                    "@LUMINA",
                    "#CURSOR_IDE",
                    "#AIMLSEA"
                ],
                **(context or {})
            },
            "error_tracking": {
                "connection_errors": [error_type] if error_type else [],
                "retry_manager_events": [],
                "distributed_trace_events": [],
                "error_correlation": []
            },
            "observability": {
                "request_correlation": {
                    "correlation_id": request_id,
                    "trace_enabled": True,
                    "logging_enabled": True
                },
                "monitoring": {
                    "track_retries": True,
                    "track_errors": True,
                    "track_latency": True,
                    "track_success": True
                }
            },
            "diagnostics": {
                "connection_status": "investigating",
                "retry_status": "unknown",
                "error_status": "logged",
                "trace_status": "pending",
                "workflow_status": "tracking",
                "stall_analysis": {
                    "found_in_metrics": False,
                    "found_in_logs": False,
                    "found_in_tickets": False,
                    "potential_stall": False,
                    "reason": "Request ID tracked for investigation"
                }
            },
            "findings": [
                f"Request ID {request_id} tracked for investigation",
                f"Source: {source}",
                f"Error type: {error_type or 'Unknown'}"
            ],
            "recommendations": [
                "Monitor this Request ID for subsequent retry attempts",
                "Check if request is retried automatically by Cursor IDE",
                "Check Cursor IDE connection status",
                "Verify if the error persists across multiple requests",
                "Use connection retry manager for automatic recovery"
            ],
            "next_steps": [
                "Search logs for related events",
                "Monitor for related errors",
                "Update cursor connection health metrics",
                "Implement retry mechanism if not already present"
            ],
            "severity": "high" if error_type else "medium",
            "priority": "high",
            "log_findings": []
        }

        # Save diagnostic entry
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(diagnostic, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Request ID tracked: {request_id}")
        logger.info(f"   Diagnostic file: {filepath}")
        logger.info(f"   Error type: {error_type or 'Unknown'}")

        return diagnostic

    def investigate_request_id(self, request_id: str) -> Dict[str, Any]:
        try:
            """
            Investigate a Request ID with comprehensive diagnostics

            Args:
                request_id: The Request ID to investigate

            Returns:
                Comprehensive diagnostic report
            """
            logger.info(f"🔍 Investigating Request ID: {request_id}")

            # Search for existing diagnostic files
            pattern = f"request_id_tracking_{request_id}_*.json"
            existing_files = list(self.diagnostics_dir.glob(pattern))

            if existing_files:
                # Load most recent diagnostic
                latest_file = max(existing_files, key=lambda p: p.stat().st_mtime)
                with open(latest_file, 'r', encoding='utf-8') as f:
                    diagnostic = json.load(f)

                logger.info(f"   Found existing diagnostic: {latest_file}")
                return diagnostic

            # Create new diagnostic entry
            logger.info("   Creating new diagnostic entry")
            return self.track_request_id(request_id, source="investigation")

        except Exception as e:
            self.logger.error(f"Error in investigate_request_id: {e}", exc_info=True)
            raise
    def search_logs(self, request_id: str) -> List[str]:
        """
        Search logs for Request ID occurrences

        Args:
            request_id: The Request ID to search for

        Returns:
            List of log findings
        """
        logger.info(f"🔍 Searching logs for Request ID: {request_id}")

        findings = []

        # Search in common log locations
        log_dirs = [
            self.project_root / "logs",
            self.project_root / "data" / "logs",
            self.project_root / "data" / "gitlens_followup_automation"
        ]

        for log_dir in log_dirs:
            if not log_dir.exists():
                continue

            # Search in JSONL files
            for log_file in log_dir.glob("*.jsonl"):
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            if request_id in line:
                                findings.append(f"Found in {log_file.name}:{line_num}")
                except Exception as e:
                    logger.debug(f"   Error reading {log_file}: {e}")

        if findings:
            logger.info(f"   Found {len(findings)} occurrences")
        else:
            logger.info("   No occurrences found in logs")

        return findings


def main():
    """Main entry point for Request ID tracking"""
    parser = argparse.ArgumentParser(
        description="Track and investigate Request IDs for connection error diagnostics"
    )
    parser.add_argument(
        "--track",
        metavar="REQUEST_ID",
        help="Track a Request ID"
    )
    parser.add_argument(
        "--investigate",
        metavar="REQUEST_ID",
        help="Investigate a Request ID"
    )
    parser.add_argument(
        "--error-type",
        metavar="ERROR_TYPE",
        help="Error type (ECONNRESET, ECONNREFUSED, etc.)"
    )
    parser.add_argument(
        "--source",
        metavar="SOURCE",
        default="user_report",
        help="Source of Request ID (default: user_report)"
    )

    args = parser.parse_args()

    tracker = RequestIDTracker()

    if args.track:
        context = {}
        if args.error_type:
            context["error_type"] = args.error_type

        diagnostic = tracker.track_request_id(
            request_id=args.track,
            source=args.source,
            error_type=args.error_type,
            context=context
        )

        print(f"\n✅ Request ID tracked: {args.track}")
        print(f"   Diagnostic file created")
        print(f"   Status: {diagnostic['status']}")
        print(f"   Severity: {diagnostic['severity']}")

    elif args.investigate:
        diagnostic = tracker.investigate_request_id(args.investigate)
        findings = tracker.search_logs(args.investigate)

        print(f"\n🔍 Investigation Results for: {args.investigate}")
        print(f"   Status: {diagnostic['status']}")
        print(f"   Severity: {diagnostic['severity']}")
        print(f"   Findings: {len(diagnostic['findings'])}")
        print(f"   Log occurrences: {len(findings)}")

        if diagnostic['findings']:
            print("\n   Findings:")
            for finding in diagnostic['findings']:
                print(f"     - {finding}")

        if findings:
            print("\n   Log occurrences:")
            for finding in findings[:10]:  # Limit to first 10
                print(f"     - {finding}")
    else:
        parser.print_help()


if __name__ == "__main__":


    main()