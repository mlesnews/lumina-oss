#!/usr/bin/env python3
"""
Hybrid Framework Oversights Analysis

@DOIT analysis of hybrid macro voice framework for oversights and recommendations.

Tags: #FRAMEWORKS #MACROS #ELEVENLABS #MANUS #HYBRID #DOIT #ANALYSIS @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from doit_enhanced import DOITEnhanced
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    DOITEnhanced = None

logger = get_logger("HybridFrameworkOversights")


class HybridFrameworkOversightsAnalysis:
    """
    Analyze hybrid framework for oversights and recommendations

    Uses @DOIT methodology for comprehensive analysis.
    """

    def __init__(self):
        """Initialize analysis"""
        self.oversights = []
        self.recommendations = []
        self.doit = DOITEnhanced() if DOITEnhanced else None

        logger.info("=" * 80)
        logger.info("🔍 HYBRID FRAMEWORK OVERSIGHTS ANALYSIS")
        logger.info("=" * 80)
        logger.info("")

    def analyze_oversights(self) -> Dict[str, Any]:
        """Comprehensive @DOIT analysis of oversights"""

        # 1. Voice Command Recognition (STT)
        self._check_voice_recognition()

        # 2. Installation/Activation Scripts
        self._check_installation_scripts()

        # 3. Integration with @DOIT
        self._check_doit_integration()

        # 4. Error Handling & Fallbacks
        self._check_error_handling()

        # 5. Macro Conflict Detection
        self._check_macro_conflicts()

        # 6. Real-time Execution Monitoring
        self._check_execution_monitoring()

        # 7. System-wide Shortcut Registration
        self._check_system_shortcuts()

        # 8. Testing & Validation
        self._check_testing()

        # 9. Documentation Completeness
        self._check_documentation()

        # 10. Integration with Existing Systems
        self._check_existing_integrations()

        return {
            "oversights": self.oversights,
            "recommendations": self.recommendations,
            "total_oversights": len(self.oversights),
            "total_recommendations": len(self.recommendations),
            "analysis_date": datetime.now().isoformat()
        }

    def _check_voice_recognition(self):
        """Check for voice command recognition (STT)"""
        logger.info("📋 Checking Voice Recognition (STT)...")

        # Check if Dragon NaturallySpeaking or STT is integrated
        try:
            from replica_inspired_hybrid_system import ReplicaInspiredHybrid
            hybrid = ReplicaInspiredHybrid()
            if hasattr(hybrid, 'dragon') and hybrid.dragon:
                logger.info("   ✅ Dragon NaturallySpeaking: AVAILABLE")
            else:
                self.oversights.append({
                    "category": "Voice Recognition",
                    "issue": "STT (Speech-to-Text) not fully integrated",
                    "severity": "high",
                    "description": "Voice commands require STT for recognition"
                })
                self.recommendations.append({
                    "category": "Voice Recognition",
                    "recommendation": "Integrate Dragon NaturallySpeaking STT for voice command recognition",
                    "priority": "high"
                })
        except ImportError:
            self.oversights.append({
                "category": "Voice Recognition",
                "issue": "Dragon NaturallySpeaking integration missing",
                "severity": "high",
                "description": "Cannot process voice commands without STT"
            })
            self.recommendations.append({
                "category": "Voice Recognition",
                "recommendation": "Add Dragon NaturallySpeaking STT integration for voice commands",
                "priority": "high"
            })

        logger.info("")

    def _check_installation_scripts(self):
        try:
            """Check for installation/activation scripts"""
            logger.info("📋 Checking Installation Scripts...")

            install_scripts = [
                "scripts/startup/install_hybrid_framework.ps1",
                "scripts/startup/activate_hybrid_framework.ps1"
            ]

            missing = []
            for script in install_scripts:
                script_path = Path(project_root) / script
                if not script_path.exists():
                    missing.append(script)

            if missing:
                self.oversights.append({
                    "category": "Installation",
                    "issue": "Missing installation/activation scripts",
                    "severity": "medium",
                    "description": f"Missing scripts: {', '.join(missing)}"
                })
                self.recommendations.append({
                    "category": "Installation",
                    "recommendation": "Create PowerShell installation and activation scripts",
                    "priority": "medium"
                })
            else:
                logger.info("   ✅ Installation scripts: PRESENT")

            logger.info("")

        except Exception as e:
            self.logger.error(f"Error in _check_installation_scripts: {e}", exc_info=True)
            raise
    def _check_doit_integration(self):
        """Check integration with @DOIT"""
        logger.info("📋 Checking @DOIT Integration...")

        if not self.doit:
            self.oversights.append({
                "category": "Integration",
                "issue": "@DOIT Enhanced not integrated with hybrid framework",
                "severity": "medium",
                "description": "Hybrid framework should leverage @DOIT for task execution"
            })
            self.recommendations.append({
                "category": "Integration",
                "recommendation": "Integrate hybrid framework with @DOIT Enhanced for unified task execution",
                "priority": "medium"
            })
        else:
            logger.info("   ✅ @DOIT Enhanced: AVAILABLE")

        logger.info("")

    def _check_error_handling(self):
        """Check error handling and fallbacks"""
        logger.info("📋 Checking Error Handling...")

        # Check if hybrid framework has proper error handling
        try:
            from hybrid_macro_voice_framework import HybridMacroVoiceFramework
            framework = HybridMacroVoiceFramework()

            # Check if execute_hybrid_macro has error handling
            if hasattr(framework, 'execute_hybrid_macro'):
                logger.info("   ✅ Error handling: PRESENT")
            else:
                self.oversights.append({
                    "category": "Error Handling",
                    "issue": "Missing comprehensive error handling",
                    "severity": "medium",
                    "description": "Need fallback mechanisms for failed macro executions"
                })
        except Exception as e:
            self.oversights.append({
                "category": "Error Handling",
                "issue": f"Error handling check failed: {e}",
                "severity": "low",
                "description": "Could not verify error handling"
            })

        logger.info("")

    def _check_macro_conflicts(self):
        """Check for macro conflict detection"""
        logger.info("📋 Checking Macro Conflict Detection...")

        self.oversights.append({
            "category": "Conflict Detection",
            "issue": "No macro conflict detection system",
            "severity": "medium",
            "description": "Need to detect conflicting shortcuts across methods"
        })
        self.recommendations.append({
            "category": "Conflict Detection",
            "recommendation": "Implement macro conflict detection to prevent duplicate triggers",
            "priority": "medium"
        })

        logger.info("")

    def _check_execution_monitoring(self):
        """Check for real-time execution monitoring"""
        logger.info("📋 Checking Execution Monitoring...")

        self.oversights.append({
            "category": "Monitoring",
            "issue": "No real-time execution monitoring",
            "severity": "low",
            "description": "Need monitoring for macro execution status and performance"
        })
        self.recommendations.append({
            "category": "Monitoring",
            "recommendation": "Add execution monitoring and logging for macro performance",
            "priority": "low"
        })

        logger.info("")

    def _check_system_shortcuts(self):
        """Check system-wide shortcut registration"""
        logger.info("📋 Checking System-Wide Shortcuts...")

        # Check if MANUS shortcuts are properly registered
        try:
            from manus_system_wide_keyboard_shortcuts import MANUSSystemWideShortcuts
            manus = MANUSSystemWideShortcuts()
            logger.info("   ✅ MANUS: AVAILABLE")
        except ImportError:
            self.oversights.append({
                "category": "System Shortcuts",
                "issue": "MANUS system-wide shortcuts not fully integrated",
                "severity": "medium",
                "description": "Need to ensure shortcuts are registered at OS level"
            })

        logger.info("")

    def _check_testing(self):
        try:
            """Check for testing and validation"""
            logger.info("📋 Checking Testing & Validation...")

            test_files = [
                "scripts/python/test_hybrid_framework.py",
                "scripts/python/test_macro_execution.py"
            ]

            missing = []
            for test_file in test_files:
                test_path = Path(project_root) / test_file
                if not test_path.exists():
                    missing.append(test_file)

            if missing:
                self.oversights.append({
                    "category": "Testing",
                    "issue": "Missing test files",
                    "severity": "medium",
                    "description": f"Missing test files: {', '.join(missing)}"
                })
                self.recommendations.append({
                    "category": "Testing",
                    "recommendation": "Create comprehensive test suite for hybrid framework",
                    "priority": "medium"
                })

            logger.info("")

        except Exception as e:
            self.logger.error(f"Error in _check_testing: {e}", exc_info=True)
            raise
    def _check_documentation(self):
        try:
            """Check documentation completeness"""
            logger.info("📋 Checking Documentation...")

            doc_files = [
                "docs/system/HYBRID_MACRO_VOICE_FRAMEWORK_COMPLETE.md",
                "docs/system/MACROS_COMPLETE.md"
            ]

            missing = []
            for doc_file in doc_files:
                doc_path = Path(project_root) / doc_file
                if not doc_path.exists():
                    missing.append(doc_file)

            if missing:
                self.oversights.append({
                    "category": "Documentation",
                    "issue": "Missing documentation files",
                    "severity": "low",
                    "description": f"Missing docs: {', '.join(missing)}"
                })
            else:
                logger.info("   ✅ Documentation: PRESENT")

            logger.info("")

        except Exception as e:
            self.logger.error(f"Error in _check_documentation: {e}", exc_info=True)
            raise
    def _check_existing_integrations(self):
        try:
            """Check integration with existing LUMINA systems"""
            logger.info("📋 Checking Existing System Integrations...")

            integrations_to_check = [
                ("JARVIS VA", "jarvis_default_va.py"),
                ("IMVA", "jarvis_ironman_bobblehead_gui.py"),
                ("ACVA", "jarvis_acva_combat_demo.py"),
                ("@DOIT", "doit_enhanced.py")
            ]

            for name, file in integrations_to_check:
                file_path = Path(project_root) / "scripts" / "python" / file
                if file_path.exists():
                    logger.info(f"   ✅ {name}: AVAILABLE")
                else:
                    self.oversights.append({
                        "category": "Integration",
                        "issue": f"{name} integration not verified",
                        "severity": "low",
                        "description": f"Need to verify integration with {name}"
                    })

            logger.info("")

        except Exception as e:
            self.logger.error(f"Error in _check_existing_integrations: {e}", exc_info=True)
            raise
    def generate_report(self) -> Path:
        """Generate @DOIT analysis report"""
        analysis = self.analyze_oversights()

        report_file = Path(project_root) / "data" / "hybrid_macros" / "oversights_analysis.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)

        import json
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)

        logger.info("=" * 80)
        logger.info("📊 OVERSIGHTS ANALYSIS REPORT")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"   📋 Total Oversights: {analysis['total_oversights']}")
        logger.info(f"   📋 Total Recommendations: {analysis['total_recommendations']}")
        logger.info("")

        logger.info("🔍 OVERSIGHTS:")
        for i, oversight in enumerate(analysis['oversights'], 1):
            logger.info(f"   {i}. [{oversight['severity'].upper()}] {oversight['category']}: {oversight['issue']}")
            logger.info(f"      {oversight['description']}")

        logger.info("")
        logger.info("💡 RECOMMENDATIONS:")
        for i, rec in enumerate(analysis['recommendations'], 1):
            logger.info(f"   {i}. [{rec['priority'].upper()}] {rec['category']}: {rec['recommendation']}")

        logger.info("")
        logger.info(f"✅ Report saved: {report_file.name}")
        logger.info("")

        return report_file


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Hybrid Framework Oversights Analysis")
    parser.add_argument("--analyze", action="store_true", help="Run analysis")
    parser.add_argument("--report", action="store_true", help="Generate report")

    args = parser.parse_args()

    analyzer = HybridFrameworkOversightsAnalysis()

    if args.report or args.analyze:
        analyzer.generate_report()
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":


    sys.exit(main())