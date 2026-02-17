#!/usr/bin/env python3
"""
Complete Lumina Audit System

Comprehensive audit covering:
- Build process
- Development workflow
- Testing workflow
- Production deployment
- All environments (dev, test, prod)
- Extension activation
- Complete workflow verification

Author: <COMPANY_NAME> LLC
Date: 2025-01-28
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
logger = get_logger("lumina_complete_audit")


try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)


@dataclass
class AuditFinding:
    """Audit finding"""
    category: str
    severity: str  # critical, high, medium, low
    finding: str
    status: str  # pass, fail, warning
    details: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class LuminaCompleteAudit:
    """Complete Lumina audit system"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.logger = get_logger("LuminaAudit")
        self.findings: List[AuditFinding] = []

        # Key directories
        self.src_dir = self.project_root / "src"
        self.scripts_dir = self.project_root / "scripts"
        self.config_dir = self.project_root / "config"
        self.docs_dir = self.project_root / "docs"
        self.data_dir = self.project_root / "data"

    def run_complete_audit(self) -> Dict[str, Any]:
        """Run complete audit"""
        self.logger.info("=" * 60)
        self.logger.info("LUMINA COMPLETE AUDIT")
        self.logger.info("=" * 60)

        # Phase 1: Build Process Audit
        self.logger.info("\nPhase 1: Build Process Audit")
        self._audit_build_process()

        # Phase 2: Development Workflow Audit
        self.logger.info("\nPhase 2: Development Workflow Audit")
        self._audit_development_workflow()

        # Phase 3: Testing Workflow Audit
        self.logger.info("\nPhase 3: Testing Workflow Audit")
        self._audit_testing_workflow()

        # Phase 4: Production Deployment Audit
        self.logger.info("\nPhase 4: Production Deployment Audit")
        self._audit_production_deployment()

        # Phase 5: Environment Configuration Audit
        self.logger.info("\nPhase 5: Environment Configuration Audit")
        self._audit_environments()

        # Phase 6: Extension Activation Audit
        self.logger.info("\nPhase 6: Extension Activation Audit")
        self._audit_extension_activation()

        # Phase 7: Workflow Verification Audit
        self.logger.info("\nPhase 7: Workflow Verification Audit")
        self._audit_workflow_verification()

        # Phase 8: Integration Audit
        self.logger.info("\nPhase 8: Integration Audit")
        self._audit_integrations()

        # Generate report
        return self._generate_report()

    def _audit_build_process(self):
        try:
            """Audit build process"""
            # Check for build scripts
            build_scripts = [
                "package.json",
                "tsconfig.json",
                "webpack.config.js",
                "vite.config.js",
                ".vscodeignore",
                "package-lock.json"
            ]

            for script in build_scripts:
                path = self.project_root / script
                if path.exists():
                    self._add_finding("build", "pass", f"Build file exists: {script}", "pass")
                else:
                    self._add_finding("build", "medium", f"Build file missing: {script}", "fail", {
                        "recommendations": [f"Create {script} for build process"]
                    })

            # Check for build documentation
            build_docs = self.docs_dir.glob("*build*.md")
            if list(build_docs):
                self._add_finding("build", "pass", "Build documentation exists", "pass")
            else:
                self._add_finding("build", "low", "Build documentation missing", "warning", {
                    "recommendations": ["Document build process"]
                })

        except Exception as e:
            self.logger.error(f"Error in _audit_build_process: {e}", exc_info=True)
            raise
    def _audit_development_workflow(self):
        try:
            """Audit development workflow"""
            # Check for development scripts
            dev_scripts = [
                "scripts/python/deploy_activate_lumina.py",
                "scripts/python/workflow_base.py",
                "scripts/python/workflow_completion_verifier.py"
            ]

            for script in dev_scripts:
                path = self.project_root / script
                if path.exists():
                    self._add_finding("development", "pass", f"Development script exists: {script}", "pass")
                else:
                    self._add_finding("development", "high", f"Development script missing: {script}", "fail")

            # Check for workflow tracking
            workflow_tracking = self.data_dir / "workflows"
            if workflow_tracking.exists():
                self._add_finding("development", "pass", "Workflow tracking directory exists", "pass")
            else:
                self._add_finding("development", "medium", "Workflow tracking directory missing", "warning")

        except Exception as e:
            self.logger.error(f"Error in _audit_development_workflow: {e}", exc_info=True)
            raise
    def _audit_testing_workflow(self):
        try:
            """Audit testing workflow"""
            # Check for test files
            test_files = list(self.project_root.rglob("*test*.py"))
            test_files.extend(self.project_root.rglob("*test*.ts"))
            test_files.extend(self.project_root.rglob("*test*.js"))

            if test_files:
                self._add_finding("testing", "pass", f"Test files found: {len(test_files)}", "pass")
            else:
                self._add_finding("testing", "high", "No test files found", "fail", {
                    "recommendations": ["Create test files for critical components"]
                })

            # Check for test configuration
            test_configs = [
                "jest.config.js",
                "pytest.ini",
                ".testrc",
                "vitest.config.js"
            ]

            found_config = False
            for config in test_configs:
                if (self.project_root / config).exists():
                    found_config = True
                    break

            if found_config:
                self._add_finding("testing", "pass", "Test configuration exists", "pass")
            else:
                self._add_finding("testing", "medium", "Test configuration missing", "warning")

        except Exception as e:
            self.logger.error(f"Error in _audit_testing_workflow: {e}", exc_info=True)
            raise
    def _audit_production_deployment(self):
        try:
            """Audit production deployment"""
            # Check for deployment scripts
            deploy_scripts = [
                "scripts/python/deploy_activate_lumina.py",
                "docs/DEPLOYMENT.md"
            ]

            for script in deploy_scripts:
                path = self.project_root / script
                if path.exists():
                    self._add_finding("deployment", "pass", f"Deployment resource exists: {script}", "pass")
                else:
                    self._add_finding("deployment", "high", f"Deployment resource missing: {script}", "fail")

            # Check for environment configuration
            env_files = [
                ".env.example",
                ".env.production",
                "config/production.json"
            ]

            found_env = False
            for env_file in env_files:
                if (self.project_root / env_file).exists():
                    found_env = True
                    break

            if found_env:
                self._add_finding("deployment", "pass", "Environment configuration exists", "pass")
            else:
                self._add_finding("deployment", "high", "Environment configuration missing", "fail")

        except Exception as e:
            self.logger.error(f"Error in _audit_production_deployment: {e}", exc_info=True)
            raise
    def _audit_environments(self):
        try:
            """Audit environment configurations"""
            environments = ["dev", "test", "prod", "staging"]

            for env in environments:
                # Check for environment-specific configs
                env_configs = [
                    f"config/{env}.json",
                    f".env.{env}",
                    f"config/{env}_config.yaml"
                ]

                found = False
                for config in env_configs:
                    if (self.project_root / config).exists():
                        found = True
                        break

                if found:
                    self._add_finding("environments", "pass", f"{env} environment configuration exists", "pass")
                else:
                    self._add_finding("environments", "medium", f"{env} environment configuration missing", "warning")

        except Exception as e:
            self.logger.error(f"Error in _audit_environments: {e}", exc_info=True)
            raise
    def _audit_extension_activation(self):
        """Audit extension activation"""
        # Check for activation scripts
        activation_scripts = [
            "scripts/python/deploy_activate_lumina.py",
            "src/extension.ts",
            "package.json"
        ]

        for script in activation_scripts:
            path = self.project_root / script
            if path.exists():
                self._add_finding("activation", "pass", f"Activation resource exists: {script}", "pass")
            else:
                self._add_finding("activation", "critical", f"Activation resource missing: {script}", "fail")

        # Check for extension registration
        lumina_config = self.config_dir / "lumina_extensions_integration.json"
        if lumina_config.exists():
            try:
                with open(lumina_config, 'r') as f:
                    config = json.load(f)
                    if config.get("extensions"):
                        self._add_finding("activation", "pass", "Extension registration exists", "pass")
                    else:
                        self._add_finding("activation", "high", "Extension registration empty", "fail")
            except Exception as e:
                self._add_finding("activation", "high", f"Extension registration invalid: {e}", "fail")
        else:
            self._add_finding("activation", "critical", "Extension registration missing", "fail")

    def _audit_workflow_verification(self):
        try:
            """Audit workflow verification"""
            # Check for verification scripts
            verification_scripts = [
                "scripts/python/workflow_completion_verifier.py",
                "scripts/python/v3_verification.py",
                "scripts/python/workflow_base.py"
            ]

            for script in verification_scripts:
                path = self.project_root / script
                if path.exists():
                    self._add_finding("verification", "pass", f"Verification script exists: {script}", "pass")
                else:
                    self._add_finding("verification", "high", f"Verification script missing: {script}", "fail")

            # Check for verification data
            verification_data = self.data_dir / "workflow_verification"
            if verification_data.exists():
                self._add_finding("verification", "pass", "Verification data directory exists", "pass")
            else:
                self._add_finding("verification", "medium", "Verification data directory missing", "warning")

        except Exception as e:
            self.logger.error(f"Error in _audit_workflow_verification: {e}", exc_info=True)
            raise
    def _audit_integrations(self):
        try:
            """Audit integrations"""
            # Check for integration configs
            integration_configs = [
                "config/lumina_extensions_integration.json",
                "config/helpdesk/droids.json",
                "config/droid_actor_routing.json"
            ]

            for config in integration_configs:
                path = self.project_root / config
                if path.exists():
                    self._add_finding("integration", "pass", f"Integration config exists: {config}", "pass")
                else:
                    self._add_finding("integration", "high", f"Integration config missing: {config}", "fail")

        except Exception as e:
            self.logger.error(f"Error in _audit_integrations: {e}", exc_info=True)
            raise
    def _add_finding(
        self,
        category: str,
        severity: str,
        finding: str,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Add audit finding"""
        finding_obj = AuditFinding(
            category=category,
            severity=severity,
            finding=finding,
            status=status,
            details=details or {},
            recommendations=details.get("recommendations", []) if details else []
        )
        self.findings.append(finding_obj)

        status_icon = "✅" if status == "pass" else "❌" if status == "fail" else "⚠️"
        self.logger.info(f"{status_icon} [{category.upper()}] {finding}")

    def _generate_report(self) -> Dict[str, Any]:
        """Generate audit report"""
        by_category = {}
        by_severity = {}
        by_status = {}

        for finding in self.findings:
            # By category
            if finding.category not in by_category:
                by_category[finding.category] = {"total": 0, "pass": 0, "fail": 0, "warning": 0}
            by_category[finding.category]["total"] += 1
            by_category[finding.category][finding.status] += 1

            # By severity
            if finding.severity not in by_severity:
                by_severity[finding.severity] = 0
            by_severity[finding.severity] += 1

            # By status
            if finding.status not in by_status:
                by_status[finding.status] = 0
            by_status[finding.status] += 1

        critical_failures = [
            f for f in self.findings
            if f.severity == "critical" and f.status == "fail"
        ]

        return {
            "audit_date": datetime.now().isoformat(),
            "total_findings": len(self.findings),
            "by_category": by_category,
            "by_severity": by_severity,
            "by_status": by_status,
            "critical_failures": len(critical_failures),
            "critical_failure_details": [
                {
                    "category": f.category,
                    "finding": f.finding,
                    "recommendations": f.recommendations
                }
                for f in critical_failures
            ],
            "findings": [
                {
                    "category": f.category,
                    "severity": f.severity,
                    "finding": f.finding,
                    "status": f.status,
                    "recommendations": f.recommendations
                }
                for f in self.findings
            ]
        }


def main():
    try:
        """Run complete audit"""
        import sys

        project_root = Path(__file__).parent.parent.parent
        audit = LuminaCompleteAudit(project_root)

        report = audit.run_complete_audit()

        # Save report
        report_file = project_root / "data" / "audits" / f"lumina_complete_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # Print summary
        print("\n" + "=" * 60)
        print("LUMINA COMPLETE AUDIT SUMMARY")
        print("=" * 60)
        print(f"Total Findings: {report['total_findings']}")
        print(f"Pass: {report['by_status'].get('pass', 0)}")
        print(f"Fail: {report['by_status'].get('fail', 0)}")
        print(f"Warning: {report['by_status'].get('warning', 0)}")
        print(f"Critical Failures: {report['critical_failures']}")
        print(f"\nReport saved to: {report_file}")

        if report['critical_failures'] > 0:
            print("\n🔴 CRITICAL FAILURES:")
            for failure in report['critical_failure_details']:
                print(f"  - [{failure['category']}] {failure['finding']}")
                if failure['recommendations']:
                    for rec in failure['recommendations']:
                        print(f"    → {rec}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()