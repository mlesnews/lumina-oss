#!/usr/bin/env python3
"""
JARVIS Integration Verifier

Verifies all JARVIS system integrations are properly connected and working.
Checks all major systems: SYPHON, R5, KAIJU, ULTRON, MANUS, @helpdesk, etc.

Tags: #JARVIS #INTEGRATION #VERIFICATION #SYSTEM_CHECK @JARVIS @DOIT
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import importlib
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISIntegrationVerifier")


@dataclass
class IntegrationCheck:
    """Result of an integration check"""
    name: str
    module_path: str
    class_name: Optional[str] = None
    status: str = "unknown"  # "pass", "fail", "warning", "skip"
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class IntegrationReport:
    """Complete integration verification report"""
    timestamp: datetime = field(default_factory=datetime.now)
    checks: List[IntegrationCheck] = field(default_factory=list)
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    skipped: int = 0

    def add_check(self, check: IntegrationCheck):
        """Add a check result"""
        self.checks.append(check)
        self.total_checks += 1
        if check.status == "pass":
            self.passed += 1
        elif check.status == "fail":
            self.failed += 1
        elif check.status == "warning":
            self.warnings += 1
        elif check.status == "skip":
            self.skipped += 1

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of verification"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "total_checks": self.total_checks,
            "passed": self.passed,
            "failed": self.failed,
            "warnings": self.warnings,
            "skipped": self.skipped,
            "success_rate": (self.passed / self.total_checks * 100) if self.total_checks > 0 else 0.0
        }


class JARVISIntegrationVerifier:
    """
    Verifies all JARVIS system integrations
    """

    # Core JARVIS systems to verify
    CORE_SYSTEMS = [
        {
            "name": "JARVIS Full-Time Super Agent",
            "module": "jarvis_fulltime_super_agent",
            "class": "JARVISFullTimeSuperAgent"
        },
        {
            "name": "JARVIS Communication Bridge",
            "module": "jarvis_communication_bridge",
            "class": "JARVISCommunicationBridge"
        },
        {
            "name": "JARVIS Persistent Memory",
            "module": "jarvis_persistent_memory",
            "class": "JARVISPersistentMemory"
        },
        {
            "name": "JARVIS Auto Keep All Manager",
            "module": "jarvis_auto_keep_all_manager",
            "class": "JARVISAutoKeepAllManager"
        },
    ]

    # SYPHON system
    SYPHON_SYSTEMS = [
        {
            "name": "SYPHON System",
            "module": "syphon",
            "class": "SYPHONSystem"
        },
    ]

    # R5 system
    R5_SYSTEMS = [
        {
            "name": "R5 Living Context Matrix",
            "module": "r5_living_context_matrix",
            "class": "R5LivingContextMatrix"
        },
    ]

    # @helpdesk systems
    HELPDESK_SYSTEMS = [
        {
            "name": "JARVIS Helpdesk Integration",
            "module": "jarvis_helpdesk_integration",
            "class": "JARVISHelpdeskIntegration"
        },
        {
            "name": "Droid Actor System",
            "module": "droid_actor_system",
            "class": "DroidActorSystem"
        },
    ]

    # Voice/TTS systems
    VOICE_SYSTEMS = [
        {
            "name": "JARVIS ElevenLabs TTS",
            "module": "jarvis_elevenlabs_integration",
            "class": "JARVISElevenLabsTTS"
        },
    ]

    # Incomplete @ASKS systems
    ASKS_SYSTEMS = [
        {
            "name": "JARVIS Mine Incomplete Asks",
            "module": "jarvis_mine_incomplete_asks_inception",
            "class": "JARVISMineIncompleteAsksInception"
        },
        {
            "name": "JARVIS Batch Processing Manager",
            "module": "jarvis_manage_batch_processing",
            "class": "JARVISBatchProcessingManager"
        },
    ]

    # Decision systems
    DECISION_SYSTEMS = [
        {
            "name": "Universal Decision Tree",
            "module": "universal_decision_tree",
            "class": "UniversalDecisionTree"
        },
    ]

    # NAS systems
    NAS_SYSTEMS = [
        {
            "name": "NAS Azure Vault Integration",
            "module": "nas_azure_vault_integration",
            "class": "NASAzureVaultIntegration"
        },
    ]

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize verifier"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger
        self.report = IntegrationReport()

    def verify_all(self) -> IntegrationReport:
        """Verify all integrations"""
        self.logger.info("🔍 Starting JARVIS Integration Verification...")
        self.logger.info("="*80)

        # Verify core systems
        self.logger.info("\n📋 Verifying Core JARVIS Systems...")
        self._verify_systems("Core JARVIS", self.CORE_SYSTEMS)

        # Verify SYPHON
        self.logger.info("\n📋 Verifying SYPHON Systems...")
        self._verify_systems("SYPHON", self.SYPHON_SYSTEMS)

        # Verify R5
        self.logger.info("\n📋 Verifying R5 Systems...")
        self._verify_systems("R5", self.R5_SYSTEMS)

        # Verify @helpdesk
        self.logger.info("\n📋 Verifying @helpdesk Systems...")
        self._verify_systems("@helpdesk", self.HELPDESK_SYSTEMS)

        # Verify voice systems
        self.logger.info("\n📋 Verifying Voice/TTS Systems...")
        self._verify_systems("Voice/TTS", self.VOICE_SYSTEMS)

        # Verify incomplete @ASKS systems
        self.logger.info("\n📋 Verifying Incomplete @ASKS Systems...")
        self._verify_systems("Incomplete @ASKS", self.ASKS_SYSTEMS)

        # Verify decision systems
        self.logger.info("\n📋 Verifying Decision Systems...")
        self._verify_systems("Decision", self.DECISION_SYSTEMS)

        # Verify NAS systems
        self.logger.info("\n📋 Verifying NAS Systems...")
        self._verify_systems("NAS", self.NAS_SYSTEMS)

        # Print summary
        self._print_summary()

        return self.report

    def _verify_systems(self, category: str, systems: List[Dict[str, str]]):
        """Verify a list of systems"""
        for system in systems:
            check = self._check_system(system["name"], system["module"], system.get("class"))
            check.details["category"] = category
            self.report.add_check(check)

    def _check_system(self, name: str, module_name: str, class_name: Optional[str] = None) -> IntegrationCheck:
        """Check if a system is available and can be imported"""
        check = IntegrationCheck(
            name=name,
            module_path=module_name,
            class_name=class_name
        )

        try:
            # Check if module file exists
            module_file = self.project_root / "scripts" / "python" / f"{module_name}.py"
            if not module_file.exists():
                # Check if it's a package
                module_dir = self.project_root / "scripts" / "python" / module_name
                if not module_dir.exists() or not (module_dir / "__init__.py").exists():
                    check.status = "fail"
                    check.message = f"Module file not found: {module_file}"
                    return check

            # Try to import module
            try:
                module = importlib.import_module(module_name)
                check.status = "pass"
                check.message = f"Module imported successfully"
                check.details["module_available"] = True

                # If class name provided, check if class exists
                if class_name:
                    if hasattr(module, class_name):
                        cls = getattr(module, class_name)
                        check.details["class_available"] = True
                        check.details["class_type"] = str(type(cls))

                        # Try to instantiate if it has project_root parameter
                        try:
                            if "project_root" in cls.__init__.__code__.co_varnames:
                                instance = cls(project_root=self.project_root)
                                check.details["instantiable"] = True
                                check.message = f"Module and class imported, instantiated successfully"
                        except Exception as e:
                            check.status = "warning"
                            check.message = f"Module imported but instantiation failed: {str(e)}"
                            check.details["instantiation_error"] = str(e)
                    else:
                        check.status = "warning"
                        check.message = f"Module imported but class '{class_name}' not found"
                        check.details["class_available"] = False

            except ImportError as e:
                check.status = "fail"
                check.message = f"Import failed: {str(e)}"
                check.details["import_error"] = str(e)
            except Exception as e:
                check.status = "warning"
                check.message = f"Unexpected error: {str(e)}"
                check.details["error"] = str(e)

        except Exception as e:
            check.status = "fail"
            check.message = f"Check failed: {str(e)}"
            check.details["error"] = str(e)

        return check

    def _print_summary(self):
        """Print verification summary"""
        self.logger.info("\n" + "="*80)
        self.logger.info("📊 VERIFICATION SUMMARY")
        self.logger.info("="*80)

        summary = self.report.get_summary()
        self.logger.info(f"Total Checks: {summary['total_checks']}")
        self.logger.info(f"✅ Passed: {summary['passed']}")
        self.logger.info(f"❌ Failed: {summary['failed']}")
        self.logger.info(f"⚠️  Warnings: {summary['warnings']}")
        self.logger.info(f"⏭️  Skipped: {summary['skipped']}")
        self.logger.info(f"Success Rate: {summary['success_rate']:.1f}%")

        # Print failed checks
        if summary['failed'] > 0:
            self.logger.info("\n❌ FAILED CHECKS:")
            for check in self.report.checks:
                if check.status == "fail":
                    self.logger.info(f"  - {check.name}: {check.message}")

        # Print warnings
        if summary['warnings'] > 0:
            self.logger.info("\n⚠️  WARNINGS:")
            for check in self.report.checks:
                if check.status == "warning":
                    self.logger.info(f"  - {check.name}: {check.message}")

        self.logger.info("="*80)

    def save_report(self, output_path: Optional[Path] = None) -> Path:
        try:
            """Save verification report to file"""
            if output_path is None:
                output_path = self.project_root / "data" / "jarvis_integration_verification" / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            output_path.parent.mkdir(parents=True, exist_ok=True)

            import json
            report_data = {
                "summary": self.report.get_summary(),
                "checks": [
                    {
                        "name": check.name,
                        "module_path": check.module_path,
                        "class_name": check.class_name,
                        "status": check.status,
                        "message": check.message,
                        "details": check.details,
                        "timestamp": check.timestamp.isoformat()
                    }
                    for check in self.report.checks
                ]
            }

            with open(output_path, 'w') as f:
                json.dump(report_data, f, indent=2)

            self.logger.info(f"💾 Report saved to: {output_path}")
            return output_path


        except Exception as e:
            self.logger.error(f"Error in save_report: {e}", exc_info=True)
            raise
def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Integration Verifier")
    parser.add_argument("--project-root", type=Path, help="Project root directory")
    parser.add_argument("--save-report", action="store_true", help="Save report to file")
    parser.add_argument("--output", type=Path, help="Output path for report")

    args = parser.parse_args()

    verifier = JARVISIntegrationVerifier(project_root=args.project_root)
    report = verifier.verify_all()

    if args.save_report or args.output:
        verifier.save_report(args.output)

    # Exit with error code if any failures
    if report.failed > 0:
        sys.exit(1)
    elif report.warnings > 0:
        sys.exit(0)
    else:
        sys.exit(0)


if __name__ == "__main__":


    main()