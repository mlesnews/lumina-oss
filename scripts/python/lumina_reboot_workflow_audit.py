#!/usr/bin/env python3
"""
LUMINA Reboot Workflow Audit

Comprehensive audit of the reboot workflow system.
Identifies gaps, pain points, and issues.
Creates definitive plan for development, build, deploy, and activation.

Tags: #AUDIT #REBOOT #WORKFLOW #PLANNING #LUMINA_CORE @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from lumina_adaptive_logger import get_adaptive_logger

logger = get_adaptive_logger("RebootWorkflowAudit")


class IssueSeverity(Enum):
    """Issue severity levels"""
    CRITICAL = "critical"  # Blocks functionality
    HIGH = "high"  # Major impact
    MEDIUM = "medium"  # Moderate impact
    LOW = "low"  # Minor impact
    INFO = "info"  # Informational


class GapCategory(Enum):
    """Gap categories"""
    MISSING_FEATURE = "missing_feature"
    INCOMPLETE_IMPLEMENTATION = "incomplete_implementation"
    INTEGRATION_ISSUE = "integration_issue"
    CONFIGURATION_ISSUE = "configuration_issue"
    TESTING_GAP = "testing_gap"
    DOCUMENTATION_GAP = "documentation_gap"


class RebootWorkflowAudit:
    """
    Comprehensive audit of reboot workflow

    Sees everything - what's right, what's wrong.
    Knows the difference.
    Forms definitive plan.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize audit"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.audit_results: Dict[str, Any] = {}
        self.gaps: List[Dict[str, Any]] = []
        self.pain_points: List[Dict[str, Any]] = []
        self.issues: List[Dict[str, Any]] = []

        # Directories to check
        self.evaluation_dir = self.project_root / "data" / "system_evaluation"
        self.health_check_dir = self.project_root / "data" / "health_checks"
        self.scripts_dir = self.project_root / "scripts" / "python"

    def run_comprehensive_audit(self) -> Dict[str, Any]:
        """Run comprehensive audit of reboot workflow"""
        logger.info("="*80)
        logger.info("🔍 LUMINA REBOOT WORKFLOW COMPREHENSIVE AUDIT")
        logger.info("="*80)
        logger.info("")

        # 1. Audit Pre-Reboot System
        logger.info("1️⃣  Auditing Pre-Reboot System...")
        pre_reboot_audit = self._audit_pre_reboot()

        # 2. Audit Reboot Process
        logger.info("2️⃣  Auditing Reboot Process...")
        reboot_audit = self._audit_reboot_process()

        # 3. Audit Post-Reboot System
        logger.info("3️⃣  Auditing Post-Reboot System...")
        post_reboot_audit = self._audit_post_reboot()

        # 4. Audit Service Restart
        logger.info("4️⃣  Auditing Service Restart...")
        service_audit = self._audit_service_restart()

        # 5. Audit Evaluation System
        logger.info("5️⃣  Auditing Evaluation System...")
        evaluation_audit = self._audit_evaluation_system()

        # 6. Audit Integration Points
        logger.info("6️⃣  Auditing Integration Points...")
        integration_audit = self._audit_integration_points()

        # 7. Audit Data Persistence
        logger.info("7️⃣  Auditing Data Persistence...")
        persistence_audit = self._audit_data_persistence()

        # 8. Audit Error Handling
        logger.info("8️⃣  Auditing Error Handling...")
        error_audit = self._audit_error_handling()

        # Compile results
        self.audit_results = {
            "timestamp": datetime.now().isoformat(),
            "pre_reboot": pre_reboot_audit,
            "reboot_process": reboot_audit,
            "post_reboot": post_reboot_audit,
            "service_restart": service_audit,
            "evaluation": evaluation_audit,
            "integration": integration_audit,
            "persistence": persistence_audit,
            "error_handling": error_audit,
            "gaps": self.gaps,
            "pain_points": self.pain_points,
            "issues": self.issues
        }

        # Generate plan
        plan = self._generate_plan()

        logger.info("")
        logger.info("="*80)
        logger.info("📊 AUDIT COMPLETE")
        logger.info("="*80)
        logger.info(f"   Gaps Found: {len(self.gaps)}")
        logger.info(f"   Pain Points: {len(self.pain_points)}")
        logger.info(f"   Issues: {len(self.issues)}")
        logger.info("")

        return {
            "audit": self.audit_results,
            "plan": plan
        }

    def _audit_pre_reboot(self) -> Dict[str, Any]:
        """Audit pre-reboot system"""
        issues = []
        gaps = []

        # Check if pre-reboot evaluation exists
        pre_reboot_script = self.scripts_dir / "lumina_holistic_system_evaluation.py"
        if not pre_reboot_script.exists():
            gaps.append({
                "category": GapCategory.MISSING_FEATURE.value,
                "severity": IssueSeverity.CRITICAL.value,
                "issue": "Pre-reboot evaluation script missing",
                "impact": "Cannot evaluate system before reboot"
            })

        # Check if evaluation runs before reboot
        reboot_script = self.scripts_dir / "lumina_system_reboot.py"
        if reboot_script.exists():
            try:
                content = reboot_script.read_text()
                if "run_evaluation" not in content and "holistic" not in content.lower():
                    gaps.append({
                        "category": GapCategory.INCOMPLETE_IMPLEMENTATION.value,
                        "severity": IssueSeverity.HIGH.value,
                        "issue": "Pre-reboot evaluation not integrated",
                        "impact": "Missing baseline before reboot"
                    })
            except Exception as e:
                issues.append({
                    "severity": IssueSeverity.MEDIUM.value,
                    "issue": f"Cannot read reboot script: {e}"
                })

        return {
            "status": "audited",
            "gaps": gaps,
            "issues": issues
        }

    def _audit_reboot_process(self) -> Dict[str, Any]:
        """Audit reboot process"""
        issues = []
        gaps = []

        # Check if RunOnce registry setup works
        reboot_script = self.scripts_dir / "lumina_system_reboot.py"
        if reboot_script.exists():
            try:
                content = reboot_script.read_text()
                if "RunOnce" not in content and "runonce" not in content.lower():
                    gaps.append({
                        "category": GapCategory.MISSING_FEATURE.value,
                        "severity": IssueSeverity.CRITICAL.value,
                        "issue": "RunOnce registry setup missing",
                        "impact": "Post-reboot evaluation won't run automatically"
                    })
            except Exception as e:
                issues.append({
                    "severity": IssueSeverity.MEDIUM.value,
                    "issue": f"Cannot audit reboot script: {e}"
                })

        # Check if shutdown command is correct
        if "shutdown" in content.lower():
            if "/r" not in content or "/t" not in content:
                gaps.append({
                    "category": GapCategory.INCOMPLETE_IMPLEMENTATION.value,
                    "severity": IssueSeverity.HIGH.value,
                    "issue": "Reboot command may be incomplete",
                    "impact": "Reboot may not work correctly"
                })

        return {
            "status": "audited",
            "gaps": gaps,
            "issues": issues
        }

    def _audit_post_reboot(self) -> Dict[str, Any]:
        """Audit post-reboot system"""
        issues = []
        gaps = []

        # Check if post-reboot script exists
        post_reboot_script = self.scripts_dir / "lumina_post_reboot_evaluation.py"
        if not post_reboot_script.exists():
            gaps.append({
                "category": GapCategory.MISSING_FEATURE.value,
                "severity": IssueSeverity.CRITICAL.value,
                "issue": "Post-reboot evaluation script missing",
                "impact": "No evaluation after reboot"
            })
        else:
            # Check if it waits for system stabilization
            try:
                content = post_reboot_script.read_text()
                if "time.sleep" not in content or "30" not in content:
                    gaps.append({
                        "category": GapCategory.INCOMPLETE_IMPLEMENTATION.value,
                        "severity": IssueSeverity.MEDIUM.value,
                        "issue": "System stabilization wait may be insufficient",
                        "impact": "Evaluation may run before system ready"
                    })
            except Exception as e:
                issues.append({
                    "severity": IssueSeverity.LOW.value,
                    "issue": f"Cannot read post-reboot script: {e}"
                })

        # Check if health check is integrated
        if post_reboot_script.exists():
            try:
                content = post_reboot_script.read_text()
                if "startup_health_check" not in content.lower():
                    gaps.append({
                        "category": GapCategory.INTEGRATION_ISSUE.value,
                        "severity": IssueSeverity.HIGH.value,
                        "issue": "Startup health check not integrated",
                        "impact": "Missing intelligent health check on startup"
                    })
            except Exception:
                pass

        return {
            "status": "audited",
            "gaps": gaps,
            "issues": issues
        }

    def _audit_service_restart(self) -> Dict[str, Any]:
        """Audit service restart"""
        issues = []
        gaps = []

        # Check if AutoHotkey restart is implemented
        post_reboot_script = self.scripts_dir / "lumina_post_reboot_evaluation.py"
        if post_reboot_script.exists():
            try:
                content = post_reboot_script.read_text()
                if "autohotkey" not in content.lower() and "hotkey" not in content.lower():
                    gaps.append({
                        "category": GapCategory.MISSING_FEATURE.value,
                        "severity": IssueSeverity.HIGH.value,
                        "issue": "AutoHotkey restart not implemented",
                        "impact": "Hotkeys won't work after reboot"
                    })
            except Exception:
                pass

        # Check if other services are restarted
        services_to_check = ["n8n", "syphon", "elevenlabs"]
        for service in services_to_check:
            if service not in content.lower():
                gaps.append({
                    "category": GapCategory.MISSING_FEATURE.value,
                    "severity": IssueSeverity.MEDIUM.value,
                    "issue": f"{service.upper()} service restart not implemented",
                    "impact": f"{service.upper()} may not be available after reboot"
                })

        return {
            "status": "audited",
            "gaps": gaps,
            "issues": issues
        }

    def _audit_evaluation_system(self) -> Dict[str, Any]:
        try:
            """Audit evaluation system"""
            issues = []
            gaps = []

            # Check if evaluation results are saved
            if not self.evaluation_dir.exists():
                gaps.append({
                    "category": GapCategory.MISSING_FEATURE.value,
                    "severity": IssueSeverity.HIGH.value,
                    "issue": "Evaluation results directory missing",
                    "impact": "Cannot track evaluation history"
                })
            else:
                # Check if results are being saved
                results = list(self.evaluation_dir.glob("*.json"))
                if len(results) == 0:
                    gaps.append({
                        "category": GapCategory.TESTING_GAP.value,
                        "severity": IssueSeverity.MEDIUM.value,
                        "issue": "No evaluation results found",
                        "impact": "Cannot verify evaluation is working"
                    })

            # Check if health check results are saved
            if not self.health_check_dir.exists():
                gaps.append({
                    "category": GapCategory.MISSING_FEATURE.value,
                    "severity": IssueSeverity.MEDIUM.value,
                    "issue": "Health check results directory missing",
                    "impact": "Cannot track health check history"
                })

            return {
                "status": "audited",
                "gaps": gaps,
                "issues": issues
            }

        except Exception as e:
            self.logger.error(f"Error in _audit_evaluation_system: {e}", exc_info=True)
            raise
    def _audit_integration_points(self) -> Dict[str, Any]:
        """Audit integration points"""
        issues = []
        gaps = []

        # Check if decisioning engine is integrated
        post_reboot_script = self.scripts_dir / "lumina_post_reboot_evaluation.py"
        if post_reboot_script.exists():
            try:
                content = post_reboot_script.read_text()
                if "decisioning" not in content.lower():
                    gaps.append({
                        "category": GapCategory.INTEGRATION_ISSUE.value,
                        "severity": IssueSeverity.MEDIUM.value,
                        "issue": "Decisioning engine not integrated",
                        "impact": "Missing automatic decision-making"
                    })
            except Exception:
                pass

        # Check if notification system is integrated
        if "notification" not in content.lower():
            gaps.append({
                "category": GapCategory.INTEGRATION_ISSUE.value,
                "severity": IssueSeverity.LOW.value,
                "issue": "Notification system not integrated",
                "impact": "No notifications during reboot process"
            })

        return {
            "status": "audited",
            "gaps": gaps,
            "issues": issues
        }

    def _audit_data_persistence(self) -> Dict[str, Any]:
        try:
            """Audit data persistence"""
            issues = []
            gaps = []

            # Check if progress is saved
            progress_dirs = [
                "data/system_evaluation",
                "data/health_checks",
                "data/decisioning_states",
                "data/voice_inputs"
            ]

            for dir_path in progress_dirs:
                full_path = self.project_root / dir_path
                if not full_path.exists():
                    gaps.append({
                        "category": GapCategory.MISSING_FEATURE.value,
                        "severity": IssueSeverity.MEDIUM.value,
                        "issue": f"Data directory missing: {dir_path}",
                        "impact": "Data may not persist across reboots"
                    })

            return {
                "status": "audited",
                "gaps": gaps,
                "issues": issues
            }

        except Exception as e:
            self.logger.error(f"Error in _audit_data_persistence: {e}", exc_info=True)
            raise
    def _audit_error_handling(self) -> Dict[str, Any]:
        """Audit error handling"""
        issues = []
        gaps = []

        # Check if error handling exists in scripts
        scripts_to_check = [
            "lumina_system_reboot.py",
            "lumina_post_reboot_evaluation.py",
            "lumina_holistic_system_evaluation.py"
        ]

        for script_name in scripts_to_check:
            script_path = self.scripts_dir / script_name
            if script_path.exists():
                try:
                    content = script_path.read_text()
                    if "try:" not in content or "except" not in content:
                        gaps.append({
                            "category": GapCategory.INCOMPLETE_IMPLEMENTATION.value,
                            "severity": IssueSeverity.MEDIUM.value,
                            "issue": f"Error handling missing in {script_name}",
                            "impact": "Scripts may crash on errors"
                        })
                except Exception:
                    pass

        return {
            "status": "audited",
            "gaps": gaps,
            "issues": issues
        }

    def _generate_plan(self) -> Dict[str, Any]:
        """Generate definitive plan"""
        # Collect all gaps and issues
        all_gaps = []
        all_issues = []

        for section in ["pre_reboot", "reboot_process", "post_reboot", "service_restart", 
                       "evaluation", "integration", "persistence", "error_handling"]:
            if section in self.audit_results:
                all_gaps.extend(self.audit_results[section].get("gaps", []))
                all_issues.extend(self.audit_results[section].get("issues", []))

        # Categorize by severity
        critical = [g for g in all_gaps if g.get("severity") == IssueSeverity.CRITICAL.value]
        high = [g for g in all_gaps if g.get("severity") == IssueSeverity.HIGH.value]
        medium = [g for g in all_gaps if g.get("severity") == IssueSeverity.MEDIUM.value]

        # Generate plan
        plan = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_gaps": len(all_gaps),
                "critical": len(critical),
                "high": len(high),
                "medium": len(medium),
                "total_issues": len(all_issues)
            },
            "phases": {
                "phase_1_develop": {
                    "name": "DEVELOP",
                    "priority": "critical",
                    "tasks": [g["issue"] for g in critical],
                    "description": "Fix critical gaps that block functionality"
                },
                "phase_2_build": {
                    "name": "BUILD",
                    "priority": "high",
                    "tasks": [g["issue"] for g in high],
                    "description": "Build missing features and integrations"
                },
                "phase_3_deploy": {
                    "name": "DEPLOY",
                    "priority": "medium",
                    "tasks": [g["issue"] for g in medium],
                    "description": "Deploy improvements and optimizations"
                },
                "phase_4_activate": {
                    "name": "ACTIVATE",
                    "priority": "all",
                    "tasks": [
                        "Test complete reboot workflow",
                        "Verify all services restart",
                        "Confirm evaluation runs",
                        "Validate data persistence",
                        "Test error handling"
                    ],
                    "description": "Activate and validate complete system"
                }
            },
            "detailed_gaps": all_gaps,
            "detailed_issues": all_issues
        }

        return plan


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="LUMINA Reboot Workflow Audit")
        parser.add_argument("--run", action="store_true", help="Run comprehensive audit")
        parser.add_argument("--output", help="Output file for results")

        args = parser.parse_args()

        audit = RebootWorkflowAudit()

        if args.run:
            results = audit.run_comprehensive_audit()

            # Save results
            output_file = Path(args.output) if args.output else audit.project_root / "data" / "reboot_workflow_audit.json"
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)

            logger.info(f"   💾 Results saved to: {output_file}")

            # Print summary
            plan = results["plan"]
            print("\n" + "="*80)
            print("📋 DEFINITIVE PLAN")
            print("="*80)
            print(f"\nSummary: {plan['summary']}")
            print(f"\nPhase 1 - DEVELOP (Critical): {len(plan['phases']['phase_1_develop']['tasks'])} tasks")
            print(f"Phase 2 - BUILD (High): {len(plan['phases']['phase_2_build']['tasks'])} tasks")
            print(f"Phase 3 - DEPLOY (Medium): {len(plan['phases']['phase_3_deploy']['tasks'])} tasks")
            print(f"Phase 4 - ACTIVATE: Complete system validation")
            print("\n" + "="*80)

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())