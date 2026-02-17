#!/usr/bin/env python3
"""
VS Code / Cursor IDE Notification Lifecycle Diagnostic & Remediation System

This module provides comprehensive diagnostics for notification lifecycle failures,
simulates common failure scenarios, and generates remediation strategies.

Tags: #JARVIS #NOTIFICATIONS #DIAGNOSTICS #C3PO @JARVIS @C3PO
"""

import hashlib
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("NotificationDiagnostics")


class NotificationLifecycleAnalyzer:
    """
    Analyzes VS Code/Cursor notification lifecycle and identifies failure points.

    Lifecycle stages:
    1. Notification Generation (VS Code internal)
    2. Notification Capture (Extension/hook)
    3. Pattern Matching (Regex/Signature matching)
    4. Ticket Creation (PM/C/T tickets)
    5. C-3PO Assignment
    6. Team Processing
    7. Resolution & Closure
    """

    # Known notification patterns with failure modes
    NOTIFICATION_PATTERNS = {

        "extension_dependency_error": {
            "pattern": r"(?:Cannot activate|Extension .+ failed to activate).+depends on|ERROR: .+missing dependency",

            "pattern": r"Cannot activate '(.+)' extension because it depends on an unknown '(.+)' extension",
            "severity": "high",
            "common_causes": [
                "Extension not installed but referenced in dependencies",
                "Workspace storage has stale extension state",
                "Extension manifest references non-existent extension",
                "Version mismatch between dependent extensions",
            ],
            "failure_modes": {
                "notification_missed": "Pattern not matched - false negative",
                "wrong_classification": "Misclassified as different issue type",
                "incomplete_context": "Missing dependency name in notification",
                "duplicate_tickets": "Same issue creates multiple tickets",
            },
        },
        "extension_format_error": {
            "pattern": r".+\s*\((?:bad|invalid|malformed)\s*format",
            "severity": "medium",
            "common_causes": [
                "Workspace file has malformed extension ID",
                "Extension recommendation lacks publisher prefix",
                "Cached extension state corrupted",
                "Extension manifest validation failed",
            ],
            "failure_modes": {
                "notification_missed": "Pattern regex doesn't match all variations",
                "wrong_classification": "Misclassified as dependency error",
                "incomplete_context": "Missing the malformed extension ID",
                "duplicate_tickets": "Same workspace storage creates multiple tickets",
            },
        },
        "server_crash": {
            "pattern": r"(.+) server crashed (\d+) times in the last (\d+) minutes",
            "severity": "high",
            "common_causes": [
                "Extension memory leak",
                "Incompatible extension with VS Code version",
                "Corrupted extension state",
                "Resource exhaustion (memory/CPU)",
            ],
            "failure_modes": {
                "notification_missed": "Crash happens too fast to capture",
                "wrong_classification": "Misidentified which server crashed",
                "incomplete_context": "Missing crash log location",
                "duplicate_tickets": "Multiple crash reports for same issue",
            },
        },

        "extension_activation_failed": {
            "pattern": r"(?:Extension|ELEMENT): .+?(?:failed to activate|failed to load|activation (?:was|cancelled|failed))",

            "pattern": r"Extension '.+' failed to activate",
            "severity": "medium",
            "common_causes": [
                "Extension initialization error",
                "Missing dependency",
                "Invalid configuration",
                "License/activation issue",
            ],
            "failure_modes": {
                "notification_missed": "Error logged but not shown as notification",
                "wrong_classification": "Generic error misclassified",
                "incomplete_context": "Missing activation error details",
                "duplicate_tickets": "Retry creates duplicate",
            },
        },

        "github_access_error": {
            "pattern": r"(?:No GitHub|GitHub authentication|ERROR: GitHub token|invalid.*GitHub)",

            "pattern": r"No GitHub access token found with access to repository",
            "severity": "high",
            "common_causes": [
                "GitHub Copilot not authenticated",
                "Token expired or revoked",
                "Missing repository permissions",
                "VS Code GitHub authentication stale",
            ],
            "failure_modes": {
                "notification_missed": "Error only in output panel",
                "wrong_classification": "Misclassified as git extension error",
                "incomplete_context": "Missing which repository",
                "duplicate_tickets": "Multiple actions trigger same error",
            },
        },
    }

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.diagnostics_file = self.project_root / "data/notification_diagnostics.json"
        self.tickets_file = self.project_root / "data/notification_tickets/tickets.json"

    def analyze_notification_lifecycle(self, notification_text: str) -> Dict[str, Any]:
        """
        Analyze a notification through the full lifecycle and identify failure points.

        Args:
            notification_text: The raw notification text

        Returns:
            Analysis report with lifecycle stages and failure points
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "notification_text": notification_text,
            "lifecycle_stages": [],
            "identified_failure_modes": [],
            "recommendations": [],
        }

        # Stage 1: Pattern Matching
        pattern_analysis = self._analyze_pattern_matching(notification_text)
        report["lifecycle_stages"].append(
            {
                "stage": "pattern_matching",
                "status": "passed" if pattern_analysis["matched"] else "failed",
                "details": pattern_analysis,
            }
        )

        if not pattern_analysis["matched"]:
            report["identified_failure_modes"].append(
                {
                    "mode": "notification_missed",
                    "stage": "pattern_matching",
                    "reason": pattern_analysis.get("no_match_reason", "Unknown"),
                }
            )

        # Stage 2: Context Extraction
        context_analysis = self._analyze_context_extraction(notification_text, pattern_analysis)
        report["lifecycle_stages"].append(
            {
                "stage": "context_extraction",
                "status": "passed" if context_analysis["success"] else "failed",
                "details": context_analysis,
            }
        )

        # Stage 3: Ticket Creation
        ticket_analysis = self._analyze_ticket_creation(notification_text, pattern_analysis)
        report["lifecycle_stages"].append(
            {
                "stage": "ticket_creation",
                "status": "passed" if ticket_analysis["success"] else "failed",
                "details": ticket_analysis,
            }
        )

        # Generate recommendations
        report["recommendations"] = self._generate_recommendations(report)

        return report

    def _analyze_pattern_matching(self, notification_text: str) -> Dict[str, Any]:
        """Analyze pattern matching stage."""
        result = {
            "matched": False,
            "matched_pattern": None,
            "matched_groups": None,
            "no_match_reason": None,
        }

        for pattern_name, pattern_info in self.NOTIFICATION_PATTERNS.items():
            pattern = pattern_info["pattern"]
            match = re.search(pattern, notification_text, re.IGNORECASE)
            if match:
                result["matched"] = True
                result["matched_pattern"] = pattern_name
                result["matched_groups"] = match.groups()
                break

        if not result["matched"]:
            # Check if close match exists
            for pattern_name, pattern_info in self.NOTIFICATION_PATTERNS.items():
                pattern = pattern_info["pattern"]
                # Remove anchors for fuzzy matching
                fuzzy_pattern = pattern.replace("^", "").replace("$", "")
                matches = re.findall(fuzzy_pattern, notification_text, re.IGNORECASE)
                if matches:
                    result["no_match_reason"] = (
                        f"Close match with {pattern_name} but full pattern didn't match"
                    )
                    break
            else:
                result["no_match_reason"] = "No pattern matches found - unknown notification type"

        return result

    def _analyze_context_extraction(
        self, notification_text: str, pattern_analysis: Dict
    ) -> Dict[str, Any]:
        """Analyze context extraction stage."""
        result = {"success": True, "extracted_context": {}, "missing_context": []}

        if not pattern_analysis["matched"]:
            result["success"] = False
            result["missing_context"].append("Unable to extract context - no pattern matched")
            return result

        pattern_name = pattern_analysis["matched_pattern"]
        groups = pattern_analysis.get("matched_groups", [])

        # Extract common context fields
        result["extracted_context"]["notification_type"] = pattern_name
        result["extracted_context"]["severity"] = self.NOTIFICATION_PATTERNS[pattern_name][
            "severity"
        ]

        # Extract pattern-specific context
        if pattern_name == "extension_dependency_error" and len(groups) >= 2:
            result["extracted_context"]["dependent_extension"] = groups[0]
            result["extracted_context"]["missing_extension"] = groups[1]
        elif pattern_name == "extension_format_error" and len(groups) >= 1:
            result["extracted_context"]["malformed_id"] = groups[0]
        elif pattern_name == "server_crash" and len(groups) >= 3:
            result["extracted_context"]["server_name"] = groups[0]
            result["extracted_context"]["crash_count"] = groups[1]
            result["extracted_context"]["time_window"] = groups[2]

        return result

    def _analyze_ticket_creation(
        self, notification_text: str, pattern_analysis: Dict
    ) -> Dict[str, Any]:
        """Analyze ticket creation stage."""
        result = {"success": True, "ticket_ids": {}, "errors": []}

        if not pattern_analysis["matched"]:
            result["success"] = False
            result["errors"].append("Cannot create tickets - no pattern matched")
            return result

        # Simulate ticket creation
        request_id = f"REQ-VSCODE-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        ticket_id = hashlib.md5(f"{notification_text}|{request_id}".encode()).hexdigest()[:14]

        result["ticket_ids"] = {
            "pm_ticket": f"PM{hashlib.md5(f'{ticket_id}_PM'.encode()).hexdigest()[:9]}",
            "c_ticket": f"C{hashlib.md5(f'{ticket_id}_C'.encode()).hexdigest()[:9]}",
            "t_ticket": f"T{hashlib.md5(f'{ticket_id}_T'.encode()).hexdigest()[:9]}",
        }

        return result

    def _generate_recommendations(self, report: Dict) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []

        for failure_mode in report.get("identified_failure_modes", []):
            mode = failure_mode["mode"]
            stage = failure_mode.get("stage", "unknown")

            if mode == "notification_missed":
                if stage == "pattern_matching":
                    recommendations.extend(
                        [
                            "Add more pattern variations to NOTIFICATION_PATTERNS",
                            "Implement fuzzy matching for near-miss patterns",
                            "Log unmatched notifications for pattern expansion",
                        ]
                    )

            elif mode == "wrong_classification":
                recommendations.extend(
                    [
                        "Review pattern priorities - more specific patterns first",
                        "Add confidence scoring for pattern matches",
                        "Implement multi-pass classification",
                    ]
                )

            elif mode == "incomplete_context":
                recommendations.extend(
                    [
                        "Add secondary extraction patterns",
                        "Cross-reference with VS Code logs",
                        "Implement context enrichment from workspace state",
                    ]
                )

            elif mode == "duplicate_tickets":
                recommendations.extend(
                    [
                        "Implement deduplication based on notification signature",
                        "Add cooldown period for same issue type",
                        "Check existing open tickets before creation",
                    ]
                )

        return recommendations

    def run_diagnostic_simulation(self, scenario: str = "all") -> Dict[str, Any]:
        """
        Run diagnostic simulations for various failure scenarios.

        Args:
            scenario: Specific scenario to test or "all" for all scenarios

        Returns:
            Simulation results with pass/fail status
        """
        scenarios = {

        "extension_dependency_error": {
            "pattern": r"(?:Cannot activate|Extension .+ failed to activate).+depends on|ERROR: .+missing dependency",

                "notifications": [
                    "Cannot activate 'Lumina Core' extension because it depends on an unknown 'github.copilot' extension",
                    "Extension 'eamodio.gitlens' failed to activate - depends on 'github.copilot'",
                    "ERROR: Cannot activate extension - missing dependency: ms-vscode.live-server",
                ],
                "expected_outcome": "Pattern matched, PM/C/T tickets created",
            },
            "extension_format_error": {
                "notifications": [
                    "undefined_publisher.lumina-ai (bad format) Expected: <provider>.<name>",
                    "malformed.extension.id (bad format) - publisher.name format required",
                    "Extension recommendation 'bad_format' has invalid format",
                ],
                "expected_outcome": "Pattern matched, format error ticket created",
            },
            "server_crash": {
                "notifications": [
                    "Microsoft Edge Tools server crashed 5 times in the last 3 minutes",
                    "HTML Language Server crashed 3 times in the last 2 minutes",
                    "CRITICAL: Pylance server crashed 10 times in the last 5 minutes",
                ],
                "expected_outcome": "Crash detected, high-priority ticket created",
            },

        "extension_activation_failed": {
            "pattern": r"(?:Extension|ELEMENT): .+?(?:failed to activate|failed to load|activation (?:was|cancelled|failed))",

                "notifications": [
                    "Extension 'msjsdiag.vscode-edge-debug2' failed to activate",
                    "ERROR: Extension 'bracket-pair-colorizer' failed to load",
                    "WARN: GitLens extension activation was cancelled",
                ],
                "expected_outcome": "Activation failure detected, ticket created",
            },

        "github_access_error": {
            "pattern": r"(?:No GitHub|GitHub authentication|ERROR: GitHub token|invalid.*GitHub)",

                "notifications": [
                    "No GitHub access token found with access to repository 'mlesnews/lumina-ai'",
                    "GitHub authentication required for Copilot features",
                    "ERROR: GitHub token invalid or expired",
                ],
                "expected_outcome": "GitHub error detected, auth ticket created",
            },
        }

        results = {
            "timestamp": datetime.now().isoformat(),
            "scenarios_tested": [],
            "overall_pass_rate": 0.0,
            "failures": [],
        }

        scenarios_to_run = scenarios.keys() if scenario == "all" else [scenario]

        for scenario_name in scenarios_to_run:
            scenario_data = scenarios[scenario_name]
            scenario_result = {
                "scenario": scenario_name,
                "tests_run": len(scenario_data["notifications"]),
                "tests_passed": 0,
                "tests_failed": 0,
                "details": [],
            }

            for notification in scenario_data["notifications"]:
                analysis = self.analyze_notification_lifecycle(notification)
                test_passed = analysis["lifecycle_stages"][0]["status"] == "passed"

                scenario_result["details"].append(
                    {
                        "notification": notification[:80] + "..."
                        if len(notification) > 80
                        else notification,
                        "pattern_matched": analysis["lifecycle_stages"][0]["status"],
                        "passed": test_passed,
                    }
                )

                if test_passed:
                    scenario_result["tests_passed"] += 1
                else:
                    scenario_result["tests_failed"] += 1
                    results["failures"].append(
                        {"scenario": scenario_name, "notification": notification}
                    )

            results["scenarios_tested"].append(scenario_result)

        # Calculate pass rate
        total_tests = sum(s["tests_run"] for s in results["scenarios_tested"])
        total_passed = sum(s["tests_passed"] for s in results["scenarios_tested"])
        results["overall_pass_rate"] = (total_passed / total_tests * 100) if total_tests > 0 else 0

        return results

    def correlate_with_system_events(self, ticket_data: Dict) -> Dict[str, Any]:
        """
        Correlate notification patterns with system events.

        Args:
            ticket_data: Ticket data from notification_tickets

        Returns:
            Correlation analysis with system events
        """
        correlation = {
            "timestamp": datetime.now().isoformat(),
            "patterns_found": [],
            "event_correlations": [],
            "recommendations": [],
        }

        # Load existing tickets
        tickets = {}
        if self.tickets_file.exists():
            try:
                with open(self.tickets_file) as f:
                    data = json.load(f)
                    tickets = data.get("tickets", {})
            except Exception as e:
                logger.warning(f"Could not load tickets: {e}")

        # Analyze patterns in existing tickets
        notification_types = {}
        for ticket_id, ticket in tickets.items():
            notif_type = ticket.get("notification_type", "unknown")
            notification_types[notif_type] = notification_types.get(notif_type, 0) + 1

        correlation["patterns_found"] = notification_types

        # Correlate with common events
        event_correlations = {
            "extension_dependency_error": [
                "New extension installed without dependencies",
                "Extension update removed dependency",
                "Workspace opened on different machine",
                "Extension cache corrupted",
            ],
            "extension_format_error": [
                "Workspace file edited manually",
                "Extension recommendation added incorrectly",
                "Workspace migration from older VS Code version",
                "Multiple workspace configurations merged",
            ],
            "server_crash": [
                "Memory-intensive operation",
                "Large file opened",
                "Extension update",
                "System resource pressure",
            ],
            "extension_activation_failed": [
                "License expired",
                "Configuration error",
                "Missing API key",
                "Dependency version mismatch",
            ],
        }

        for notif_type, events in event_correlations.items():
            if notif_type in notification_types:
                correlation["event_correlations"].append(
                    {
                        "notification_type": notif_type,
                        "occurrence_count": notification_types[notif_type],
                        "common_triggers": events,
                    }
                )

        # Generate recommendations based on correlations
        if notification_types:
            most_common = max(notification_types, key=notification_types.get)
            correlation["recommendations"].extend(
                [
                    f"Focus remediation efforts on '{most_common}' (most common: {notification_types[most_common]} occurrences)",
                    "Consider proactive monitoring for high-frequency issue types",
                    "Implement preventive measures for common trigger events",
                ]
            )

        return correlation

    def generate_remediation_report(self, diagnostics: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate comprehensive remediation report.

        Args:
            diagnostics: Optional pre-computed diagnostics

        Returns:
            Complete remediation report with strategies
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "executive_summary": {},
            "root_cause_analysis": {},
            "remediation_strategies": {},
            "implementation_plan": [],
            "prevention_measures": [],
        }

        # Run diagnostics if not provided
        if not diagnostics:
            diagnostics = self.run_diagnostic_simulation("all")

        # Executive Summary
        report["executive_summary"] = {
            "total_scenarios_tested": len(diagnostics.get("scenarios_tested", [])),
            "overall_pass_rate": diagnostics.get("overall_pass_rate", 0),
            "failure_count": len(diagnostics.get("failures", [])),
            "status": "HEALTHY"
            if diagnostics.get("overall_pass_rate", 0) >= 80
            else "NEEDS_ATTENTION",
        }

        # Root Cause Analysis
        report["root_cause_analysis"] = {
            "notification_missed": {
                "description": "Notifications that don't match any pattern",
                "contributing_factors": [
                    "Pattern regex too restrictive",
                    "New notification types not yet added",
                    "Case sensitivity issues",
                    "Whitespace variations not handled",
                ],
                "impact": "Issues go undetected and untracked",
            },
            "duplicate_tickets": {
                "description": "Same issue creating multiple tickets",
                "contributing_factors": [
                    "No deduplication before ticket creation",
                    "Cooldown period too short",
                    "Similar but slightly different notifications",
                ],
                "impact": "Team overhead managing duplicates",
            },
            "incomplete_context": {
                "description": "Missing information in ticket descriptions",
                "contributing_factors": [
                    "Pattern groups don't capture all details",
                    "No secondary extraction patterns",
                    "VS Code notification format variations",
                ],
                "impact": "Team lacks info to resolve issues",
            },
        }

        # Remediation Strategies
        report["remediation_strategies"] = {
            "pattern_improvement": {
                "priority": "HIGH",
                "actions": [
                    "Add fuzzy matching for near-miss patterns",
                    "Implement pattern version tracking",
                    "Add case-insensitive flag to all patterns",
                    r"Handle whitespace variations with \s+ patterns",
                ],
                "expected_improvement": "30% reduction in missed notifications",
            },
            "deduplication": {
                "priority": "HIGH",
                "actions": [
                    "Implement notification signature hashing",
                    "Add 5-minute cooldown for same notification type",
                    "Check existing open tickets before creation",
                    "Implement ticket merge functionality",
                ],
                "expected_improvement": "50% reduction in duplicate tickets",
            },
            "context_enrichment": {
                "priority": "MEDIUM",
                "actions": [
                    "Add secondary extraction from VS Code logs",
                    "Cross-reference with workspace state",
                    "Include recent file/extension activity",
                    "Add system resource context",
                ],
                "expected_improvement": "40% improvement in ticket completeness",
            },
        }

        # Implementation Plan
        report["implementation_plan"] = [
            {
                "phase": 1,
                "duration": "1 day",
                "tasks": [
                    "Add fuzzy pattern matching to monitor_vscode_notifications.py",
                    "Implement notification deduplication logic",
                    "Add cooldown period configuration",
                ],
            },
            {
                "phase": 2,
                "duration": "2 days",
                "tasks": [
                    "Enhance context extraction for all patterns",
                    "Add VS Code log parsing for additional context",
                    "Implement ticket merge functionality",
                ],
            },
            {
                "phase": 3,
                "duration": "3 days",
                "tasks": [
                    "Test all scenarios with new patterns",
                    "Run full diagnostic suite",
                    "Update documentation and runbooks",
                ],
            },
        ]

        # Prevention Measures
        report["prevention_measures"] = [
            "Monitor extension compatibility before updates",
            "Validate workspace configurations on load",
            "Implement health checks for extensions",
            "Regular workspace storage cleanup",
            "Track extension installation/uninstallation events",
        ]

        return report


def main():
    """Main entry point for diagnostics."""
    import argparse

    parser = argparse.ArgumentParser(description="VS Code Notification Diagnostics")
    parser.add_argument("--analyze", type=str, help="Analyze specific notification text")
    parser.add_argument(
        "--simulate",
        type=str,
        default="all",
        choices=["all"] + list(NotificationLifecycleAnalyzer.NOTIFICATION_PATTERNS.keys()),
        help="Run diagnostic simulation",
    )
    parser.add_argument("--correlate", action="store_true", help="Correlate with system events")
    parser.add_argument("--report", action="store_true", help="Generate full remediation report")
    parser.add_argument("--output", type=str, help="Output file path")

    args = parser.parse_args()

    analyzer = NotificationLifecycleAnalyzer()

    if args.analyze:
        report = analyzer.analyze_notification_lifecycle(args.analyze)
        print(json.dumps(report, indent=2))

    if args.simulate:
        results = analyzer.run_diagnostic_simulation(args.simulate)
        print(json.dumps(results, indent=2))

    if args.correlate:
        # Load existing ticket data (index + per-ticket files, mirror helpdesk)
        tickets_file = analyzer.project_root / "data/notification_tickets/tickets.json"
        tickets_dir = tickets_file.parent / "tickets"
        try:
            from monitor_vscode_notifications import _load_notification_tickets_from_storage
            tickets = _load_notification_tickets_from_storage(tickets_file, tickets_dir)
        except Exception as e:
            tickets = {}
            if tickets_file.exists():
                try:
                    with open(tickets_file) as f:
                        data = json.load(f)
                        tickets = data.get("tickets", {})
                except Exception as e2:
                    print(f"Error loading tickets: {e2}")
            else:
                print(f"Error loading tickets: {e}")
        correlation = analyzer.correlate_with_system_events(tickets)
        print(json.dumps(correlation, indent=2))

    if args.report:
        remediation = analyzer.generate_remediation_report()
        if args.output:
            with open(args.output, "w") as f:
                json.dump(remediation, f, indent=2)
        print(json.dumps(remediation, indent=2))

    return 0


if __name__ == "__main__":

    sys.exit(main())