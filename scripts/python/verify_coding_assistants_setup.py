#!/usr/bin/env python3
"""
Verify Coding Assistants Setup

This script verifies that all coding assistants (Kilo Code, Continue, Cline, etc.)
are properly configured and set up for maximum potential across all IDEs.

Author: <COMPANY_NAME> LLC
Date: 2024-12-19
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "python"))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda: logging.getLogger(__name__)

logger = get_logger()



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class AssistantStatus(Enum):
    """Status of coding assistant"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CONFIGURED = "configured"
    NOT_CONFIGURED = "not_configured"
    ERROR = "error"


@dataclass
class AssistantVerification:
    """Verification result for a coding assistant"""
    name: str
    status: AssistantStatus
    ide: str
    configured: bool
    errors: List[str]
    warnings: List[str]
    recommendations: List[str]


@dataclass
class VerificationReport:
    """Complete verification report"""
    timestamp: str
    total_assistants: int
    active_assistants: int
    configured_assistants: int
    assistants: List[AssistantVerification]
    overall_status: str
    recommendations: List[str]


class CodingAssistantsVerifier:
    """Verifies coding assistants setup"""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize verifier"""
        self.config_dir = config_dir or (project_root / "config")
        self.registry_path = self.config_dir / "coding_assistants_registry.json"
        self.kilo_code_config_path = self.config_dir / "kilo_code_optimized_config.json"
        self.multi_ide_config_path = self.config_dir / "multi_ide_optimal_settings.json"
        self.llm_orchestration_path = self.config_dir / "llm_orchestration_config.json"

    def verify_config_files(self) -> Tuple[bool, List[str]]:
        try:
            """Verify all configuration files exist"""
            errors = []
            required_files = [
                self.registry_path,
                self.kilo_code_config_path,
                self.multi_ide_config_path,
                self.llm_orchestration_path
            ]

            for file_path in required_files:
                if not file_path.exists():
                    errors.append(f"Missing configuration file: {file_path}")

            return len(errors) == 0, errors

        except Exception as e:
            self.logger.error(f"Error in verify_config_files: {e}", exc_info=True)
            raise
    def verify_kilo_code_config(self) -> Tuple[bool, List[str], List[str]]:
        """Verify Kilo Code configuration"""
        errors = []
        warnings = []

        if not self.kilo_code_config_path.exists():
            errors.append("Kilo Code configuration file not found")
            return False, errors, warnings

        try:
            with open(self.kilo_code_config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            # Verify Iron Legion configuration
            llm_config = config.get("llm_config", {})
            primary_llm = llm_config.get("primary_llm", {})

            if primary_llm.get("base_url") != "http://localhost:11437":
                warnings.append("Iron Legion URL may not be configured correctly")

            # Verify Peak integration
            peak_integration = config.get("peak_integration", {})
            if not peak_integration.get("enabled", False):
                warnings.append("Peak integration is not enabled")

            # Verify Cursor IDE integration
            ide_integration = config.get("ide_integration", {})
            cursor_config = ide_integration.get("cursor", {})
            if not cursor_config.get("enabled", False):
                warnings.append("Cursor IDE integration is not enabled")

            # Verify R5 integration
            context_management = config.get("context_management", {})
            r5_integration = context_management.get("r5_integration", {})
            if not r5_integration.get("enabled", False):
                warnings.append("R5 Living Context Matrix integration is not enabled")

        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in Kilo Code config: {e}")
            return False, errors, warnings
        except Exception as e:
            errors.append(f"Error reading Kilo Code config: {e}")
            return False, errors, warnings

        return True, errors, warnings

    def verify_iron_legion_connection(self) -> Tuple[bool, List[str]]:
        """Verify Iron Legion local LLM cluster connection"""
        errors = []

        try:
            import requests

            base_url = "http://localhost:11437"
            timeout = 5

            # Try to connect to Ollama API
            try:
                response = requests.get(f"{base_url}/api/tags", timeout=timeout)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    required_models = ["codellama:13b", "llama3.2:11b", "qwen2.5-coder:1.5b-base"]
                    available_models = [m.get("name", "") for m in models]

                    missing_models = [m for m in required_models if m not in available_models]
                    if missing_models:
                        errors.append(f"Iron Legion missing models: {', '.join(missing_models)}")
                else:
                    errors.append(f"Iron Legion API returned status {response.status_code}")
            except requests.exceptions.ConnectionError:
                errors.append("Cannot connect to Iron Legion at http://localhost:11437 - is Ollama running?")
            except requests.exceptions.Timeout:
                errors.append("Iron Legion connection timeout")
            except Exception as e:
                errors.append(f"Error connecting to Iron Legion: {e}")

        except ImportError:
            errors.append("requests library not installed - cannot verify Iron Legion connection")

        return len(errors) == 0, errors

    def verify_ide_setup(self, ide: str) -> Tuple[bool, List[str], List[str]]:
        """Verify IDE-specific setup"""
        errors = []
        warnings = []

        if not self.multi_ide_config_path.exists():
            errors.append("Multi-IDE configuration file not found")
            return False, errors, warnings

        try:
            with open(self.multi_ide_config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            ide_config = config.get(ide.lower(), {})
            if not ide_config:
                warnings.append(f"No configuration found for {ide}")
                return False, errors, warnings

            kilo_code_settings = ide_config.get("settings", {}).get("kilo_code", {})
            if not kilo_code_settings.get("enabled", False):
                warnings.append(f"Kilo Code not enabled for {ide}")

        except Exception as e:
            errors.append(f"Error reading multi-IDE config: {e}")
            return False, errors, warnings

        return True, errors, warnings

    def generate_recommendations(self, verification_results: List[AssistantVerification]) -> List[str]:
        """Generate recommendations based on verification results"""
        recommendations = []

        # Check if Kilo Code is properly configured
        kilo_code_results = [r for r in verification_results if r.name == "kilo_code"]
        if not kilo_code_results or not any(r.configured for r in kilo_code_results):
            recommendations.append("Configure Kilo Code as primary assistant for maximum potential")

        # Check Iron Legion connection
        if any("llama3.2:3b" in str(r.errors) for r in verification_results):
            recommendations.append("Start Ollama service and ensure Iron Legion is running on http://localhost:11437")

        # Check Peak integration
        if any("Peak" in str(r.warnings) for r in verification_results):
            recommendations.append("Enable Peak integration in Kilo Code for nutrient-dense, reusable patterns")

        # Check R5 integration
        if any("R5" in str(r.warnings) for r in verification_results):
            recommendations.append("Enable R5 Living Context Matrix integration for aggregated knowledge")

        # Check Cursor setup
        cursor_results = [r for r in verification_results if r.ide == "cursor"]
        if not cursor_results or not any(r.configured for r in cursor_results):
            recommendations.append("Set up Kilo Code in Cursor IDE for optimal experience")

        return recommendations

    def verify_all(self) -> VerificationReport:
        try:
            """Verify all coding assistants setup"""
            logger.info("Starting coding assistants verification...")

            # Verify config files
            config_ok, config_errors = self.verify_config_files()
            if not config_ok:
                logger.error(f"Configuration files missing: {config_errors}")
                return VerificationReport(
                    timestamp=str(Path(__file__).stat().st_mtime),
                    total_assistants=0,
                    active_assistants=0,
                    configured_assistants=0,
                    assistants=[],
                    overall_status="error",
                    recommendations=["Create missing configuration files"]
                )

            assistants = []

            # Verify Kilo Code
            kilo_code_ok, kilo_code_errors, kilo_code_warnings = self.verify_kilo_code_config()
            iron_legion_ok, iron_legion_errors = self.verify_iron_legion_connection()

            all_errors = kilo_code_errors + iron_legion_errors
            all_warnings = kilo_code_warnings

            # Verify for each IDE
            for ide in ["cursor", "vscode", "jetbrains", "neovim"]:
                ide_ok, ide_errors, ide_warnings = self.verify_ide_setup(ide)
                all_errors.extend(ide_errors)
                all_warnings.extend(ide_warnings)

                assistants.append(AssistantVerification(
                    name="kilo_code",
                    status=AssistantStatus.CONFIGURED if (kilo_code_ok and ide_ok) else AssistantStatus.NOT_CONFIGURED,
                    ide=ide,
                    configured=kilo_code_ok and ide_ok,
                    errors=[e for e in all_errors if ide in e.lower() or "kilo" in e.lower()],
                    warnings=[w for w in all_warnings if ide in w.lower() or "kilo" in w.lower()],
                    recommendations=[]
                ))

            # Generate recommendations
            recommendations = self.generate_recommendations(assistants)

            # Calculate overall status
            configured_count = sum(1 for a in assistants if a.configured)
            total_count = len(assistants)

            if configured_count == total_count and not all_errors:
                overall_status = "optimal"
            elif configured_count > 0:
                overall_status = "partial"
            else:
                overall_status = "needs_setup"

            report = VerificationReport(
                timestamp=str(Path(__file__).stat().st_mtime),
                total_assistants=total_count,
                active_assistants=configured_count,
                configured_assistants=configured_count,
                assistants=assistants,
                overall_status=overall_status,
                recommendations=recommendations
            )

            logger.info(f"Verification complete: {overall_status} ({configured_count}/{total_count} configured)")

            return report

        except Exception as e:
            self.logger.error(f"Error in verify_all: {e}", exc_info=True)
            raise
    def print_report(self, report: VerificationReport) -> None:
        """Print verification report"""
        print("\n" + "=" * 80)
        print("CODING ASSISTANTS VERIFICATION REPORT")
        print("=" * 80)
        print(f"\nOverall Status: {report.overall_status.upper()}")
        print(f"Configured: {report.configured_assistants}/{report.total_assistants}")
        print(f"\nTimestamp: {report.timestamp}")

        print("\n" + "-" * 80)
        print("ASSISTANT DETAILS")
        print("-" * 80)

        for assistant in report.assistants:
            status_icon = "✓" if assistant.configured else "✗"
            print(f"\n{status_icon} {assistant.name} ({assistant.ide})")
            print(f"   Status: {assistant.status.value}")

            if assistant.errors:
                print(f"   Errors:")
                for error in assistant.errors:
                    print(f"     - {error}")

            if assistant.warnings:
                print(f"   Warnings:")
                for warning in assistant.warnings:
                    print(f"     - {warning}")

        if report.recommendations:
            print("\n" + "-" * 80)
            print("RECOMMENDATIONS")
            print("-" * 80)
            for i, rec in enumerate(report.recommendations, 1):
                print(f"{i}. {rec}")

        print("\n" + "=" * 80 + "\n")


def main() -> int:
    """Main entry point"""
    verifier = CodingAssistantsVerifier()
    report = verifier.verify_all()
    verifier.print_report(report)

    # Return exit code based on status
    if report.overall_status == "optimal":
        return 0
    elif report.overall_status == "partial":
        return 1
    else:
        return 2


if __name__ == "__main__":



    sys.exit(main())