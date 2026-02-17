#!/usr/bin/env python3
"""
Comprehensive Cluster Diagnostic and Repair Tool

All-in-one tool that:
- Diagnoses all configuration issues
- Validates endpoint health
- Detects configuration drift
- Applies automated fixes
- Generates comprehensive reports

Tags: #DIAGNOSTIC #REPAIR #COMPREHENSIVE #AUTOMATION @JARVIS @LUMINA
"""

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import our tools
try:
    from cluster_config_manager import ClusterConfigManager
    from discover_cluster_endpoints import EndpointDiscovery
    from ide_workaround_automation import IDEWorkaroundAutomation
    from lumina_logger import get_logger
    from validate_cluster_config import ClusterConfigValidator, ValidationResult
except ImportError as e:
    import logging

    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    logger = get_logger("cluster_diagnostic_repair")
    logger.warning(f"Some modules not available: {e}")

logger = get_logger("cluster_diagnostic_repair")


@dataclass
class DiagnosticResult:
    """Comprehensive diagnostic result"""

    category: str
    severity: str  # "critical", "error", "warning", "info"
    issue: str
    location: str
    fix_available: bool = False
    fix_applied: bool = False
    fix_description: Optional[str] = None


@dataclass
class ComprehensiveReport:
    """Comprehensive diagnostic report"""

    timestamp: str
    validation_results: Optional[ValidationResult] = None
    discovered_endpoints: int = 0
    drift_detected: int = 0
    drift_fixed: int = 0
    diagnostics: List[DiagnosticResult] = field(default_factory=list)
    health_status: Dict[str, str] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class ClusterDiagnosticRepair:
    """Comprehensive diagnostic and repair system"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.validator = ClusterConfigValidator(project_root)
        self.discovery = EndpointDiscovery(project_root)
        self.manager = ClusterConfigManager(project_root)
        self.automation = IDEWorkaroundAutomation(project_root)
        self.diagnostics: List[DiagnosticResult] = []

    def run_full_diagnostic(
        self, check_health: bool = True, discover_endpoints: bool = True, detect_drift: bool = True
    ) -> ComprehensiveReport:
        """Run comprehensive diagnostic"""
        logger.info("Starting comprehensive diagnostic...")

        report = ComprehensiveReport(timestamp=datetime.now().isoformat())

        # 1. Validate configuration
        logger.info("Validating configuration...")
        validation_result = self.validator.validate_all(check_health=check_health)
        report.validation_results = validation_result

        # Convert validation issues to diagnostics
        for issue in validation_result.issues:
            self.diagnostics.append(
                DiagnosticResult(
                    category=issue.category,
                    severity=issue.severity,
                    issue=issue.issue,
                    location=issue.file_path,
                    fix_available=issue.fix_suggestion is not None,
                    fix_description=issue.fix_suggestion,
                )
            )

        # 2. Discover endpoints
        if discover_endpoints:
            logger.info("Discovering endpoints...")
            discovered = self.discovery.discover_all(scan_network=False)  # Localhost only for speed
            report.discovered_endpoints = len(discovered)

        # 3. Detect configuration drift
        if detect_drift:
            logger.info("Detecting configuration drift...")
            drift_list = self.manager.detect_drift()
            report.drift_detected = len(drift_list)

        # 4. Check endpoint health
        if check_health and report.validation_results:
            logger.info("Checking endpoint health...")
            registry = self.validator.registry
            endpoints = registry.get("endpoints", {})

            for endpoint_id, endpoint in endpoints.items():
                health_check = endpoint.get("health_check")
                if health_check:
                    try:
                        response = requests.get(health_check, timeout=5)
                        if response.status_code == 200:
                            report.health_status[endpoint_id] = "operational"
                        else:
                            report.health_status[endpoint_id] = "degraded"
                            self.diagnostics.append(
                                DiagnosticResult(
                                    category="health",
                                    severity="warning",
                                    issue=f"Endpoint {endpoint_id} returned HTTP {response.status_code}",
                                    location=endpoint_id,
                                    fix_available=False,
                                )
                            )
                    except Exception as e:
                        report.health_status[endpoint_id] = "offline"
                        self.diagnostics.append(
                            DiagnosticResult(
                                category="health",
                                severity="error",
                                issue=f"Endpoint {endpoint_id} is offline: {e}",
                                location=endpoint_id,
                                fix_available=True,
                                fix_description="Check service status, network connectivity, firewall rules",
                            )
                        )

        # 5. Generate recommendations
        report.recommendations = self._generate_recommendations(report)

        report.diagnostics = self.diagnostics

        logger.info("Diagnostic complete")
        return report

    def apply_auto_fixes(
        self, report: ComprehensiveReport, dry_run: bool = False
    ) -> Dict[str, int]:
        """Apply automatic fixes"""
        fixes_applied = {"validation": 0, "drift": 0, "health": 0, "workarounds": 0}

        # Fix configuration drift
        if report.drift_detected > 0:
            fixed, failed = self.manager.fix_drift(dry_run=dry_run)
            fixes_applied["drift"] = fixed
            report.drift_fixed = fixed

        # Setup IDE workarounds for offline endpoints
        offline_endpoints = [
            endpoint_id
            for endpoint_id, status in report.health_status.items()
            if status == "offline"
        ]

        if offline_endpoints and not dry_run:
            # Check if port forwarding can help
            registry = self.validator.registry
            for endpoint_id in offline_endpoints:
                endpoint = registry.get("endpoints", {}).get(endpoint_id, {})
                forwarding = endpoint.get("forwarding")
                if forwarding and forwarding.get("type") == "ssh_tunnel":
                    success = self.automation.start_port_forward(
                        forward_id=endpoint_id,
                        local_port=forwarding.get("local_port"),
                        remote_host=forwarding.get("remote_host"),
                        remote_port=forwarding.get("remote_port"),
                        ssh_host=forwarding.get("ssh_host"),
                        ssh_user=forwarding.get("ssh_user", "mlesn"),
                    )
                    if success:
                        fixes_applied["workarounds"] += 1

        return fixes_applied

    def _generate_recommendations(self, report: ComprehensiveReport) -> List[str]:
        """Generate recommendations based on diagnostic results"""
        recommendations = []

        # Validation issues
        if report.validation_results:
            errors = [d for d in report.diagnostics if d.severity == "error"]
            if errors:
                recommendations.append(
                    f"Fix {len(errors)} configuration errors (run --fix-validation)"
                )

        # Drift issues
        if report.drift_detected > 0:
            recommendations.append(
                f"Synchronize {report.drift_detected} configuration drift issues (run --fix-drift)"
            )

        # Health issues
        offline_count = sum(1 for status in report.health_status.values() if status == "offline")
        if offline_count > 0:
            recommendations.append(
                f"Investigate {offline_count} offline endpoints (check services, network)"
            )

        # Discovery
        if report.discovered_endpoints == 0:
            recommendations.append(
                "No endpoints discovered - check network connectivity and service status"
            )

        # Registry
        if not self.validator.registry_path.exists():
            recommendations.append(
                "Create endpoint registry (config/cluster_endpoint_registry.json)"
            )

        return recommendations

    def print_comprehensive_report(self, report: ComprehensiveReport):
        """Print comprehensive diagnostic report"""
        print("=" * 80)
        print("COMPREHENSIVE CLUSTER DIAGNOSTIC REPORT")
        print("=" * 80)
        print(f"Timestamp: {report.timestamp}")
        print()

        # Summary
        print("SUMMARY")
        print("-" * 80)
        if report.validation_results:
            print(
                f"Configuration Valid: {'✅ YES' if report.validation_results.valid else '❌ NO'}"
            )
            print(f"  Issues: {len(report.validation_results.issues)}")
            print(f"  Endpoints Checked: {report.validation_results.endpoints_checked}")
            print(f"  Endpoints Healthy: {report.validation_results.endpoints_healthy}")
            print(f"  Endpoints Unhealthy: {report.validation_results.endpoints_unhealthy}")

        print(f"Endpoints Discovered: {report.discovered_endpoints}")
        print(f"Configuration Drift: {report.drift_detected} detected, {report.drift_fixed} fixed")
        print()

        # Diagnostics
        if report.diagnostics:
            print("DIAGNOSTICS")
            print("-" * 80)

            # Group by severity
            critical = [d for d in report.diagnostics if d.severity == "critical"]
            errors = [d for d in report.diagnostics if d.severity == "error"]
            warnings = [d for d in report.diagnostics if d.severity == "warning"]
            infos = [d for d in report.diagnostics if d.severity == "info"]

            if critical:
                print(f"\n🔴 CRITICAL ({len(critical)}):")
                for diag in critical:
                    print(f"  [{diag.category}] {diag.location}")
                    print(f"    {diag.issue}")
                    if diag.fix_description:
                        print(f"    Fix: {diag.fix_description}")

            if errors:
                print(f"\n❌ ERRORS ({len(errors)}):")
                for diag in errors:
                    print(f"  [{diag.category}] {diag.location}")
                    print(f"    {diag.issue}")
                    if diag.fix_description:
                        print(f"    Fix: {diag.fix_description}")

            if warnings:
                print(f"\n⚠️  WARNINGS ({len(warnings)}):")
                for diag in warnings[:10]:  # Show first 10
                    print(f"  [{diag.category}] {diag.location}")
                    print(f"    {diag.issue}")

            if infos:
                print(f"\nℹ️  INFO ({len(infos)}):")
                for diag in infos[:5]:  # Show first 5
                    print(f"  [{diag.category}] {diag.location}")
                    print(f"    {diag.issue}")

        # Health Status
        if report.health_status:
            print("\nENDPOINT HEALTH STATUS")
            print("-" * 80)
            for endpoint_id, status in report.health_status.items():
                icon = "✅" if status == "operational" else "⚠️" if status == "degraded" else "❌"
                print(f"  {icon} {endpoint_id}: {status}")

        # Recommendations
        if report.recommendations:
            print("\nRECOMMENDATIONS")
            print("-" * 80)
            for i, rec in enumerate(report.recommendations, 1):
                print(f"  {i}. {rec}")

        print("\n" + "=" * 80)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Comprehensive cluster diagnostic and repair tool")
    parser.add_argument("--diagnose", action="store_true", help="Run full diagnostic")
    parser.add_argument("--fix", action="store_true", help="Apply automatic fixes")
    parser.add_argument(
        "--no-health-check", action="store_true", help="Skip endpoint health checks"
    )
    parser.add_argument("--no-discovery", action="store_true", help="Skip endpoint discovery")
    parser.add_argument("--no-drift", action="store_true", help="Skip drift detection")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be fixed without making changes"
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    diagnostic = ClusterDiagnosticRepair(project_root)

    # Run diagnostic
    report = diagnostic.run_full_diagnostic(
        check_health=not args.no_health_check,
        discover_endpoints=not args.no_discovery,
        detect_drift=not args.no_drift,
    )

    # Apply fixes if requested
    if args.fix:
        fixes = diagnostic.apply_auto_fixes(report, dry_run=args.dry_run)
        report.drift_fixed = fixes.get("drift", 0)
        if fixes.get("workarounds", 0) > 0:
            print(f"\n✅ Applied {fixes['workarounds']} workaround fixes")

    # Output results
    if args.json:
        # Output as JSON
        output = {
            "timestamp": report.timestamp,
            "validation": {
                "valid": report.validation_results.valid if report.validation_results else None,
                "issues": len(report.validation_results.issues) if report.validation_results else 0,
                "endpoints_checked": report.validation_results.endpoints_checked
                if report.validation_results
                else 0,
                "endpoints_healthy": report.validation_results.endpoints_healthy
                if report.validation_results
                else 0,
                "endpoints_unhealthy": report.validation_results.endpoints_unhealthy
                if report.validation_results
                else 0,
            },
            "discovered_endpoints": report.discovered_endpoints,
            "drift": {"detected": report.drift_detected, "fixed": report.drift_fixed},
            "health_status": report.health_status,
            "diagnostics": [
                {
                    "category": d.category,
                    "severity": d.severity,
                    "issue": d.issue,
                    "location": d.location,
                    "fix_available": d.fix_available,
                    "fix_description": d.fix_description,
                }
                for d in report.diagnostics
            ],
            "recommendations": report.recommendations,
        }
        print(json.dumps(output, indent=2))
    else:
        diagnostic.print_comprehensive_report(report)

    # Exit code based on issues
    if report.validation_results and not report.validation_results.valid:
        sys.exit(1)
    if report.drift_detected > report.drift_fixed:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
    main()
