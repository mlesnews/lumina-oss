#!/usr/bin/env python3
"""
JARVIS Active Control - LUMINA Body Health Audit

JARVIS takes active control over @LUMINA and performs comprehensive audit
of all outstanding "body" health issues across all LUMINA systems.

JARVIS = Brain/Command Center
LUMINA = Body (all systems, services, integrations)

Tags: #JARVIS #LUMINA #BODY_HEALTH #AUDIT #ACTIVE_CONTROL @JARVIS @LUMINA @DOIT
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISLuminaBodyHealthAudit")

PROJECT_ROOT = Path(__file__).parent.parent.parent


class HealthSeverity(Enum):
    """Health issue severity"""
    CRITICAL = "critical"  # System down or severely degraded
    HIGH = "high"  # Major functionality impacted
    MEDIUM = "medium"  # Moderate impact
    LOW = "low"  # Minor impact
    INFO = "info"  # Informational


class BodyPartCategory(Enum):
    """Body part categories"""
    SENSE = "sense"  # Sensory systems
    LIMB = "limb"  # Execution systems
    ORGAN = "organ"  # Internal systems
    SYSTEM = "system"  # Complex systems
    INTEGRATION = "integration"  # External integrations


@dataclass
class BodyHealthIssue:
    """A body health issue"""
    issue_id: str
    body_part_id: str
    body_part_name: str
    category: BodyPartCategory
    severity: HealthSeverity
    status: str  # healthy, degraded, down, unknown
    health_score: float  # 0-100
    description: str
    symptoms: List[str] = field(default_factory=list)
    root_cause: Optional[str] = None
    impact: str = ""
    recommended_action: str = ""
    last_checked: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BodyHealthAuditResult:
    """Complete body health audit result"""
    timestamp: str
    overall_health_score: float
    overall_status: str
    total_body_parts: int
    healthy_parts: int
    degraded_parts: int
    down_parts: int
    unknown_parts: int
    critical_issues: List[BodyHealthIssue]
    high_issues: List[BodyHealthIssue]
    medium_issues: List[BodyHealthIssue]
    low_issues: List[BodyHealthIssue]
    body_parts: Dict[str, Dict[str, Any]]
    recommendations: List[str]
    action_plan: List[str]


class JARVISLuminaBodyHealthAudit:
    """
    JARVIS Active Control - LUMINA Body Health Audit

    Takes active control and performs comprehensive audit of all
    outstanding body health issues.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "jarvis_body_health"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Set logger first
        self.logger = logger

        # Initialize health systems
        self.body_integration = None
        self.unified_health = None
        self.all_systems_checker = None
        self.comprehensive_audit = None

        self._initialize_health_systems()

        # Active control state
        self.active_control = False
        self.audit_results: List[BodyHealthAuditResult] = []

    def _initialize_health_systems(self):
        """Initialize all health monitoring systems"""
        # Body Integration
        try:
            from jarvis_body_integration import JARVISBodyIntegration
            self.body_integration = JARVISBodyIntegration(project_root=self.project_root)
            self.logger.info("✅ Body Integration system initialized")
        except ImportError as e:
            self.logger.warning(f"⚠️  Body Integration not available: {e}")

        # Unified Health System
        try:
            from jarvis_unified_health_system import UnifiedHealthSystem
            self.unified_health = UnifiedHealthSystem(project_root=self.project_root)
            self.logger.info("✅ Unified Health System initialized")
        except ImportError as e:
            self.logger.warning(f"⚠️  Unified Health System not available: {e}")

        # All Systems Checker
        try:
            from jarvis_all_systems_check import JARVISAllSystemsChecker
            self.all_systems_checker = JARVISAllSystemsChecker(project_root=self.project_root)
            self.logger.info("✅ All Systems Checker initialized")
        except ImportError as e:
            self.logger.warning(f"⚠️  All Systems Checker not available: {e}")

        # Comprehensive Audit
        try:
            from lumina_comprehensive_audit_triage_bau import LuminaComprehensiveAudit
            self.comprehensive_audit = LuminaComprehensiveAudit(project_root=self.project_root)
            self.logger.info("✅ Comprehensive Audit initialized")
        except ImportError as e:
            self.logger.warning(f"⚠️  Comprehensive Audit not available: {e}")

        # Homelab Body Health Audit (@BODY = #HOMELAB)
        try:
            from jarvis_homelab_body_health_audit import JARVISHomelabBodyHealthAudit
            self.homelab_audit = JARVISHomelabBodyHealthAudit(project_root=self.project_root)
            self.logger.info("✅ Homelab Body Health Audit initialized (@BODY = #HOMELAB)")
        except ImportError as e:
            self.logger.warning(f"⚠️  Homelab Body Health Audit not available: {e}")
            self.homelab_audit = None

    def take_active_control(self) -> bool:
        """Take active control over @LUMINA"""
        self.logger.info("=" * 80)
        self.logger.info("🎮 JARVIS TAKING ACTIVE CONTROL OVER @LUMINA")
        self.logger.info("=" * 80)
        self.logger.info("")

        try:
            # Activate all monitoring systems
            if self.unified_health:
                self.unified_health.start_unified_monitoring()
                self.logger.info("✅ Unified health monitoring started")

            if self.body_integration:
                # Get three-foot bubble awareness
                awareness = self.body_integration.bubble.get_awareness()
                self.logger.info(f"✅ Three-foot bubble awareness: {awareness.get('systems_in_bubble', 0)} systems")

            self.active_control = True
            self.logger.info("")
            self.logger.info("✅ ACTIVE CONTROL ESTABLISHED")
            self.logger.info("")

            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to take active control: {e}")
            return False

    def audit_body_health(self) -> BodyHealthAuditResult:
        """
        Perform comprehensive audit of all body health issues

        Returns:
            Complete audit result with all issues identified
        """
        self.logger.info("=" * 80)
        self.logger.info("🏥 LUMINA BODY HEALTH AUDIT")
        self.logger.info("=" * 80)
        self.logger.info("")

        issues: List[BodyHealthIssue] = []
        body_parts: Dict[str, Dict[str, Any]] = {}

        # 1. Check Body Integration (Three-Foot Bubble)
        self.logger.info("Step 1: Checking Body Integration (Three-Foot Bubble)...")
        if self.body_integration:
            try:
                awareness = self.body_integration.bubble.get_awareness()
                pain_points = self.body_integration.bubble.detect_pain_points()

                for system in awareness.get("systems", []):
                    part_id = system.get("part_id", "unknown")
                    body_parts[part_id] = system

                    if system.get("health_score", 100) < 80 or system.get("status") != "healthy":
                        severity = HealthSeverity.CRITICAL if system.get("health_score", 100) < 50 else HealthSeverity.HIGH
                        issues.append(BodyHealthIssue(
                            issue_id=f"body_{part_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            body_part_id=part_id,
                            body_part_name=system.get("name", "Unknown"),
                            category=BodyPartCategory.SYSTEM,
                            severity=severity,
                            status=system.get("status", "unknown"),
                            health_score=system.get("health_score", 100),
                            description=f"Body part {system.get('name')} health score: {system.get('health_score', 100)}",
                            symptoms=[f"Status: {system.get('status')}", f"Health score: {system.get('health_score', 100)}"],
                            last_checked=system.get("last_checked", datetime.now().isoformat())
                        ))

                self.logger.info(f"   Found {len(pain_points)} pain points")

            except Exception as e:
                self.logger.warning(f"⚠️  Error checking body integration: {e}")

        # 2. Check Unified Health System
        self.logger.info("Step 2: Checking Unified Health System...")
        if self.unified_health:
            try:
                health_status = self.unified_health.get_unified_health_status()

                overall_health = health_status.get("overall_health", "UNKNOWN")
                if overall_health != "HEALTHY":
                    issues.append(BodyHealthIssue(
                        issue_id=f"unified_health_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        body_part_id="unified_health",
                        body_part_name="Unified Health System",
                        category=BodyPartCategory.SYSTEM,
                        severity=HealthSeverity.HIGH if overall_health == "CRITICAL" else HealthSeverity.MEDIUM,
                        status="degraded",
                        health_score=50 if overall_health == "CRITICAL" else 70,
                        description=f"Unified health status: {overall_health}",
                        symptoms=[f"Overall health: {overall_health}"],
                        last_checked=health_status.get("timestamp", datetime.now().isoformat())
                    ))

                self.logger.info(f"   Overall health: {overall_health}")

            except Exception as e:
                self.logger.warning(f"⚠️  Error checking unified health: {e}")

        # 3. Check All Systems
        self.logger.info("Step 3: Checking All Systems...")
        if self.all_systems_checker:
            try:
                # Run comprehensive checks
                all_statuses = []

                # IDE Queues
                ide_statuses = self.all_systems_checker.check_all_ide_queues()
                all_statuses.extend(ide_statuses)

                # Localhost
                localhost_statuses = self.all_systems_checker.check_localhost()
                all_statuses.extend(localhost_statuses)

                # OS
                os_statuses = self.all_systems_checker.check_os()
                all_statuses.extend(os_statuses)

                # Convert to body health issues
                for status in all_statuses:
                    if status.status in ["error", "critical", "warning"]:
                        severity_map = {
                            "critical": HealthSeverity.CRITICAL,
                            "error": HealthSeverity.HIGH,
                            "warning": HealthSeverity.MEDIUM
                        }

                        issues.append(BodyHealthIssue(
                            issue_id=f"system_{status.category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            body_part_id=status.category.lower(),
                            body_part_name=status.category,
                            category=BodyPartCategory.SYSTEM,
                            severity=severity_map.get(status.status, HealthSeverity.MEDIUM),
                            status="degraded" if status.status == "warning" else "down",
                            health_score=30 if status.status == "critical" else 50 if status.status == "error" else 70,
                            description=status.message,
                            symptoms=[status.message],
                            metadata=status.details if hasattr(status, 'details') else {},
                            last_checked=status.timestamp
                        ))

                self.logger.info(f"   Checked {len(all_statuses)} system categories")

            except Exception as e:
                self.logger.warning(f"⚠️  Error checking all systems: {e}")

        # 4. #HOMELAB Body Health Audit (@BODY = #HOMELAB)
        self.logger.info("Step 4: Performing #HOMELAB Body Health Audit (@BODY = #HOMELAB)...")
        homelab_issues = []
        if self.homelab_audit:
            try:
                homelab_result = self.homelab_audit.audit_homelab_body_health()

                # Convert homelab issues to body health issues
                for system_id, system in homelab_result.systems.items():
                    if system.status != "healthy":
                        severity = HealthSeverity.CRITICAL if system.status == "down" else HealthSeverity.HIGH
                        homelab_issues.append(BodyHealthIssue(
                            issue_id=f"homelab_{system_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            body_part_id=system_id,
                            body_part_name=system.system_name,
                            category=BodyPartCategory.INTEGRATION,
                            severity=severity,
                            status=system.status,
                            health_score=system.health_score,
                            description=f"#HOMELAB system {system.system_name} status: {system.status}",
                            symptoms=system.issues.copy(),
                            last_checked=system.last_checked,
                            metadata={"endpoint": system.endpoint, "system_type": system.system_type.value}
                        ))

                self.logger.info(f"   Found {len(homelab_issues)} #HOMELAB issues")
                issues.extend(homelab_issues)

            except Exception as e:
                self.logger.warning(f"⚠️  Error in homelab audit: {e}")

        # 5. Comprehensive Codebase Audit
        self.logger.info("Step 5: Performing Comprehensive Codebase Audit...")
        if self.comprehensive_audit:
            try:
                codebase_issues = self.comprehensive_audit.scan_codebase_for_issues()

                # Convert to body health issues (focus on critical/high)
                for issue in codebase_issues:
                    # Check severity (may be string or enum)
                    issue_severity = issue.severity
                    if hasattr(issue_severity, 'value'):
                        issue_severity = issue_severity.value
                    elif hasattr(issue_severity, 'name'):
                        issue_severity = issue_severity.name.lower()

                    if issue_severity in ["critical", "high"] or (hasattr(issue, 'severity') and str(issue.severity).lower() in ["critical", "high"]):
                        severity_map = {
                            "critical": HealthSeverity.CRITICAL,
                            "high": HealthSeverity.HIGH
                        }

                        severity_str = str(issue_severity).lower() if isinstance(issue_severity, str) else "medium"
                        health_severity = severity_map.get(severity_str, HealthSeverity.MEDIUM)

                        issues.append(BodyHealthIssue(
                            issue_id=f"codebase_{issue.id}",
                            body_part_id=issue.file_path,
                            body_part_name=f"Codebase: {issue.file_path}",
                            category=BodyPartCategory.SYSTEM,
                            severity=health_severity,
                            status="degraded",
                            health_score=40 if severity_str == "critical" else 60,
                            description=issue.description,
                            symptoms=[f"Category: {getattr(issue.category, 'value', issue.category)}", f"Line: {issue.line_number}"],
                            root_cause=getattr(issue, 'original_text', issue.description),
                            last_checked=datetime.now().isoformat(),
                            metadata={"file_path": issue.file_path, "line_number": issue.line_number}
                        ))

                self.logger.info(f"   Found {len(codebase_issues)} codebase issues")

            except Exception as e:
                self.logger.warning(f"⚠️  Error in comprehensive audit: {e}")

        # 6. Categorize and analyze
        self.logger.info("")
        self.logger.info("Step 6: Analyzing results...")

        critical_issues = [i for i in issues if i.severity == HealthSeverity.CRITICAL]
        high_issues = [i for i in issues if i.severity == HealthSeverity.HIGH]
        medium_issues = [i for i in issues if i.severity == HealthSeverity.MEDIUM]
        low_issues = [i for i in issues if i.severity == HealthSeverity.LOW]

        # Calculate overall health
        healthy_parts = sum(1 for p in body_parts.values() if p.get("status") == "healthy")
        degraded_parts = sum(1 for p in body_parts.values() if p.get("status") == "degraded")
        down_parts = sum(1 for p in body_parts.values() if p.get("status") == "down")
        unknown_parts = sum(1 for p in body_parts.values() if p.get("status") == "unknown")

        total_parts = len(body_parts)
        if total_parts > 0:
            overall_health_score = (healthy_parts / total_parts) * 100
        else:
            overall_health_score = 100.0

        # Adjust for issues (cap penalty to prevent going to 0)
        critical_penalty = min(len(critical_issues) * 2, 30)  # Max 30 point penalty
        high_penalty = min(len(high_issues) * 1, 20)  # Max 20 point penalty

        overall_health_score = max(0, min(100, overall_health_score - critical_penalty - high_penalty))

        overall_status = "healthy" if overall_health_score >= 80 else "degraded" if overall_health_score >= 50 else "critical"

        # Generate recommendations
        recommendations = self._generate_recommendations(issues, body_parts)
        action_plan = self._generate_action_plan(critical_issues, high_issues)

        # Create audit result
        audit_result = BodyHealthAuditResult(
            timestamp=datetime.now().isoformat(),
            overall_health_score=overall_health_score,
            overall_status=overall_status,
            total_body_parts=total_parts,
            healthy_parts=healthy_parts,
            degraded_parts=degraded_parts,
            down_parts=down_parts,
            unknown_parts=unknown_parts,
            critical_issues=critical_issues,
            high_issues=high_issues,
            medium_issues=medium_issues,
            low_issues=low_issues,
            body_parts=body_parts,
            recommendations=recommendations,
            action_plan=action_plan
        )

        self.audit_results.append(audit_result)

        # Save audit result
        self._save_audit_result(audit_result)

        # Display summary
        self._display_audit_summary(audit_result)

        return audit_result

    def _generate_recommendations(self, issues: List[BodyHealthIssue], body_parts: Dict[str, Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on audit"""
        recommendations = []

        critical_count = len([i for i in issues if i.severity == HealthSeverity.CRITICAL])
        if critical_count > 0:
            recommendations.append(f"🚨 URGENT: Address {critical_count} critical health issues immediately")

        high_count = len([i for i in issues if i.severity == HealthSeverity.HIGH])
        if high_count > 0:
            recommendations.append(f"⚠️  HIGH PRIORITY: Resolve {high_count} high-severity issues")

        degraded_count = sum(1 for p in body_parts.values() if p.get("status") == "degraded")
        if degraded_count > 0:
            recommendations.append(f"🔧 MAINTENANCE: Restore {degraded_count} degraded body parts")

        if not recommendations:
            recommendations.append("✅ All body parts appear healthy - continue monitoring")

        return recommendations

    def _generate_action_plan(self, critical_issues: List[BodyHealthIssue], high_issues: List[BodyHealthIssue]) -> List[str]:
        """Generate action plan"""
        actions = []

        # Critical issues first
        for issue in critical_issues[:5]:  # Top 5
            actions.append(f"CRITICAL: Fix {issue.body_part_name} - {issue.description[:50]}")

        # High issues
        for issue in high_issues[:5]:  # Top 5
            actions.append(f"HIGH: Address {issue.body_part_name} - {issue.description[:50]}")

        if not actions:
            actions.append("No immediate actions required - system healthy")

        return actions

    def _save_audit_result(self, result: BodyHealthAuditResult):
        """Save audit result to file"""
        try:
            audit_file = self.data_dir / f"body_health_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            # Convert to dict
            result_dict = asdict(result)

            with open(audit_file, 'w') as f:
                json.dump(result_dict, f, indent=2, default=str)

            self.logger.info(f"📄 Audit result saved: {audit_file}")

        except Exception as e:
            self.logger.warning(f"⚠️  Failed to save audit result: {e}")

    def _display_audit_summary(self, result: BodyHealthAuditResult):
        """Display audit summary"""
        self.logger.info("")
        self.logger.info("=" * 80)
        self.logger.info("📊 BODY HEALTH AUDIT SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info("")
        self.logger.info(f"Overall Health Score: {result.overall_health_score:.1f}/100")
        self.logger.info(f"Overall Status: {result.overall_status.upper()}")
        self.logger.info("")
        self.logger.info(f"Body Parts:")
        self.logger.info(f"   Total: {result.total_body_parts}")
        self.logger.info(f"   Healthy: {result.healthy_parts}")
        self.logger.info(f"   Degraded: {result.degraded_parts}")
        self.logger.info(f"   Down: {result.down_parts}")
        self.logger.info(f"   Unknown: {result.unknown_parts}")
        self.logger.info("")
        self.logger.info(f"Issues by Severity:")
        self.logger.info(f"   Critical: {len(result.critical_issues)}")
        self.logger.info(f"   High: {len(result.high_issues)}")
        self.logger.info(f"   Medium: {len(result.medium_issues)}")
        self.logger.info(f"   Low: {len(result.low_issues)}")
        self.logger.info("")

        if result.critical_issues:
            self.logger.info("🚨 CRITICAL ISSUES:")
            for issue in result.critical_issues[:5]:
                self.logger.info(f"   - {issue.body_part_name}: {issue.description[:60]}")
            self.logger.info("")

        if result.recommendations:
            self.logger.info("💡 RECOMMENDATIONS:")
            for rec in result.recommendations:
                self.logger.info(f"   {rec}")
            self.logger.info("")

        self.logger.info("=" * 80)
        self.logger.info("")

    def perform_full_audit(self) -> BodyHealthAuditResult:
        """Perform full audit: take control + audit"""
        # Take active control
        if not self.take_active_control():
            self.logger.error("❌ Failed to take active control - audit may be incomplete")

        # Perform audit
        return self.audit_body_health()


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS LUMINA Body Health Audit")
    parser.add_argument('--project-root', type=Path, help='Project root directory')
    parser.add_argument('--take-control', action='store_true', help='Take active control first')
    parser.add_argument('--audit-only', action='store_true', help='Perform audit only (no control)')

    args = parser.parse_args()

    auditor = JARVISLuminaBodyHealthAudit(project_root=args.project_root or PROJECT_ROOT)

    if args.audit_only:
        result = auditor.audit_body_health()
    else:
        result = auditor.perform_full_audit()

    return 0 if result.overall_status != "critical" else 1


if __name__ == "__main__":


    sys.exit(main())