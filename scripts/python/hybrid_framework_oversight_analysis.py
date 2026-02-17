#!/usr/bin/env python3
"""
Hybrid Framework Oversight Analysis

@DOIT analysis of oversights and recommendations for Hybrid Macro Voice Framework.

Tags: #DOIT #OVERSIGHTS #RECOMMENDATIONS #ANALYSIS @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import json

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
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    DOITEnhanced = None

logger = get_logger("HybridFrameworkOversightAnalysis")


class HybridFrameworkOversightAnalysis:
    """
    Analyze Hybrid Framework for oversights and recommendations

    Uses @DOIT enhanced analysis to identify gaps.
    """

    def __init__(self):
        """Initialize oversight analysis"""
        self.oversights = []
        self.recommendations = []
        self.doit = DOITEnhanced() if DOITEnhanced else None

        logger.info("✅ Hybrid Framework Oversight Analysis initialized")

    def analyze_oversights(self) -> Dict[str, Any]:
        """
        Analyze for oversights using @DOIT

        Returns:
            Analysis results with oversights and recommendations
        """
        logger.info("=" * 80)
        logger.info("🔍 ANALYZING HYBRID FRAMEWORK FOR OVERSIGHTS")
        logger.info("=" * 80)
        logger.info("")

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "oversights": [],
            "recommendations": [],
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }

        # 1. Voice Command Recognition (STT)
        self._analyze_voice_recognition(analysis)

        # 2. Installation & Activation
        self._analyze_installation(analysis)

        # 3. Error Handling & Fallbacks
        self._analyze_error_handling(analysis)

        # 4. Status Monitoring
        self._analyze_status_monitoring(analysis)

        # 5. Configuration Management
        self._analyze_configuration(analysis)

        # 6. Integration Testing
        self._analyze_testing(analysis)

        # 7. Auto-Startup
        self._analyze_autostart(analysis)

        # 8. Documentation
        self._analyze_documentation(analysis)

        # 9. Voice Feedback Integration
        self._analyze_voice_feedback(analysis)

        # 10. MANUS Verification
        self._analyze_manus_verification(analysis)

        # Use @DOIT to prioritize
        if self.doit:
            for item in analysis["oversights"] + analysis["recommendations"]:
                priority = self.doit._infer_triage_priority(item.get("description", ""))
                analysis[priority.lower()].append(item)

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ OVERSIGHT ANALYSIS COMPLETE")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"   📋 Total Oversights: {len(analysis['oversights'])}")
        logger.info(f"   📋 Total Recommendations: {len(analysis['recommendations'])}")
        logger.info(f"   🔴 Critical: {len(analysis['critical'])}")
        logger.info(f"   🟠 High: {len(analysis['high'])}")
        logger.info(f"   🟡 Medium: {len(analysis['medium'])}")
        logger.info(f"   🟢 Low: {len(analysis['low'])}")
        logger.info("")

        return analysis

    def _analyze_voice_recognition(self, analysis: Dict[str, Any]):
        """Analyze voice command recognition (STT) integration"""
        logger.info("   🔍 Analyzing Voice Recognition...")

        oversight = {
            "category": "Voice Recognition",
            "type": "oversight",
            "priority": "high",
            "description": "Voice command recognition (STT) not fully integrated - macros can be triggered by voice but no active listening service",
            "impact": "Users cannot trigger macros via voice commands in real-time",
            "recommendation": "Implement continuous voice recognition service that listens for voice commands and triggers macros",
            "files_affected": [
                "scripts/python/hybrid_macro_voice_framework.py",
                "scripts/python/lumina_jarvis_hybrid_voice_system.py"
            ]
        }
        analysis["oversights"].append(oversight)
        analysis["recommendations"].append({
            "category": "Voice Recognition",
            "type": "recommendation",
            "priority": "high",
            "description": "Add voice command listener service that continuously monitors for voice commands and triggers hybrid macros",
            "implementation": "Create voice_command_listener.py that uses Dragon NaturallySpeaking or Windows Speech Recognition"
        })

    def _analyze_installation(self, analysis: Dict[str, Any]):
        """Analyze installation and activation"""
        logger.info("   🔍 Analyzing Installation...")

        oversight = {
            "category": "Installation",
            "type": "oversight",
            "priority": "medium",
            "description": "No unified installation/activation script for hybrid framework - each component must be installed separately",
            "impact": "Complex setup process for users",
            "recommendation": "Create install_hybrid_framework.ps1 that installs and configures all components",
            "files_affected": ["scripts/startup/"]
        }
        analysis["oversights"].append(oversight)
        analysis["recommendations"].append({
            "category": "Installation",
            "type": "recommendation",
            "priority": "medium",
            "description": "Create unified installation script that: 1) Installs PowerToys config, 2) Sets up AutoHotkey, 3) Registers Armoury Crate macros, 4) Configures ElevenLabs, 5) Sets up MANUS shortcuts",
            "implementation": "scripts/startup/install_hybrid_framework.ps1"
        })

    def _analyze_error_handling(self, analysis: Dict[str, Any]):
        """Analyze error handling and fallbacks"""
        logger.info("   🔍 Analyzing Error Handling...")

        oversight = {
            "category": "Error Handling",
            "type": "oversight",
            "priority": "high",
            "description": "Limited error handling and fallback mechanisms - if one method fails, entire macro may fail",
            "impact": "Unreliable macro execution",
            "recommendation": "Implement graceful degradation - if one method fails, continue with others",
            "files_affected": ["scripts/python/hybrid_macro_voice_framework.py"]
        }
        analysis["oversights"].append(oversight)
        analysis["recommendations"].append({
            "category": "Error Handling",
            "type": "recommendation",
            "priority": "high",
            "description": "Add try-catch blocks for each method execution with fallback to next method if one fails",
            "implementation": "Enhance execute_hybrid_macro() with per-method error handling"
        })

    def _analyze_status_monitoring(self, analysis: Dict[str, Any]):
        """Analyze status monitoring"""
        logger.info("   🔍 Analyzing Status Monitoring...")

        oversight = {
            "category": "Status Monitoring",
            "type": "oversight",
            "priority": "medium",
            "description": "No status monitoring or health checks for framework components",
            "impact": "Cannot detect if components are running or need restart",
            "recommendation": "Add health check system that monitors PowerToys, AutoHotkey, ElevenLabs, MANUS status",
            "files_affected": ["scripts/python/hybrid_macro_voice_framework.py"]
        }
        analysis["oversights"].append(oversight)
        analysis["recommendations"].append({
            "category": "Status Monitoring",
            "type": "recommendation",
            "priority": "medium",
            "description": "Create health_check() method that verifies all components are active and responding",
            "implementation": "Add component status checks using psutil and service queries"
        })

    def _analyze_configuration(self, analysis: Dict[str, Any]):
        """Analyze configuration management"""
        logger.info("   🔍 Analyzing Configuration...")

        oversight = {
            "category": "Configuration",
            "type": "oversight",
            "priority": "low",
            "description": "No centralized configuration management - each component has separate config files",
            "impact": "Configuration changes require multiple file edits",
            "recommendation": "Create unified config manager that syncs all component configs",
            "files_affected": ["config/"]
        }
        analysis["oversights"].append(oversight)
        analysis["recommendations"].append({
            "category": "Configuration",
            "type": "recommendation",
            "priority": "low",
            "description": "Create hybrid_framework_config.json that manages all component configurations in one place",
            "implementation": "config/hybrid_framework_config.json"
        })

    def _analyze_testing(self, analysis: Dict[str, Any]):
        """Analyze integration testing"""
        logger.info("   🔍 Analyzing Testing...")

        oversight = {
            "category": "Testing",
            "type": "oversight",
            "priority": "high",
            "description": "No integration tests or verification scripts for hybrid framework",
            "impact": "Cannot verify framework works end-to-end",
            "recommendation": "Create test_hybrid_framework.py that tests all components and macro execution",
            "files_affected": []
        }
        analysis["oversights"].append(oversight)
        analysis["recommendations"].append({
            "category": "Testing",
            "type": "recommendation",
            "priority": "high",
            "description": "Create comprehensive test suite that: 1) Tests each component individually, 2) Tests macro execution, 3) Tests voice commands, 4) Tests error handling",
            "implementation": "scripts/python/test_hybrid_framework.py"
        })

    def _analyze_autostart(self, analysis: Dict[str, Any]):
        """Analyze auto-startup configuration"""
        logger.info("   🔍 Analyzing Auto-Startup...")

        oversight = {
            "category": "Auto-Startup",
            "type": "oversight",
            "priority": "medium",
            "description": "No auto-startup configuration for hybrid framework components",
            "impact": "Components must be manually started after reboot",
            "recommendation": "Add hybrid framework to post-reboot startup sequence",
            "files_affected": ["scripts/startup/post_reboot_startup.ps1"]
        }
        analysis["oversights"].append(oversight)
        analysis["recommendations"].append({
            "category": "Auto-Startup",
            "type": "recommendation",
            "priority": "medium",
            "description": "Integrate hybrid framework startup into post_reboot_startup.ps1",
            "implementation": "Add hybrid framework initialization to startup sequence"
        })

    def _analyze_documentation(self, analysis: Dict[str, Any]):
        """Analyze documentation"""
        logger.info("   🔍 Analyzing Documentation...")

        oversight = {
            "category": "Documentation",
            "type": "oversight",
            "priority": "low",
            "description": "Missing quick start guide and troubleshooting documentation",
            "impact": "Users may struggle to get started",
            "recommendation": "Create QUICK_START.md and TROUBLESHOOTING.md",
            "files_affected": ["docs/system/"]
        }
        analysis["oversights"].append(oversight)
        analysis["recommendations"].append({
            "category": "Documentation",
            "type": "recommendation",
            "priority": "low",
            "description": "Create user-friendly quick start guide with step-by-step setup instructions",
            "implementation": "docs/system/HYBRID_FRAMEWORK_QUICK_START.md"
        })

    def _analyze_voice_feedback(self, analysis: Dict[str, Any]):
        """Analyze voice feedback integration"""
        logger.info("   🔍 Analyzing Voice Feedback...")

        oversight = {
            "category": "Voice Feedback",
            "type": "oversight",
            "priority": "medium",
            "description": "Voice feedback (TTS) is defined but not actively executed - needs integration with ElevenLabs TTS service",
            "impact": "No audio confirmation after macro execution",
            "recommendation": "Implement actual TTS execution using ElevenLabs API",
            "files_affected": ["scripts/python/hybrid_macro_voice_framework.py"]
        }
        analysis["oversights"].append(oversight)
        analysis["recommendations"].append({
            "category": "Voice Feedback",
            "type": "recommendation",
            "priority": "medium",
            "description": "Enhance _execute_voice_feedback() to actually call ElevenLabs TTS API and play audio",
            "implementation": "Integrate with ElevenLabs TTS in hybrid_macro_voice_framework.py"
        })

    def _analyze_manus_verification(self, analysis: Dict[str, Any]):
        """Analyze MANUS verification"""
        logger.info("   🔍 Analyzing MANUS Verification...")

        oversight = {
            "category": "MANUS Verification",
            "type": "oversight",
            "priority": "low",
            "description": "MANUS shortcuts are defined but not verified to be active system-wide",
            "impact": "MANUS shortcuts may not work as expected",
            "recommendation": "Add verification that MANUS shortcuts are registered and active",
            "files_affected": ["scripts/python/hybrid_macro_voice_framework.py"]
        }
        analysis["oversights"].append(oversight)
        analysis["recommendations"].append({
            "category": "MANUS Verification",
            "type": "recommendation",
            "priority": "low",
            "description": "Add verify_manus_shortcuts() method that checks if shortcuts are active",
            "implementation": "Enhance MANUS integration with verification"
        })

    def generate_report(self, analysis: Dict[str, Any]) -> Path:
        try:
            """Generate oversight analysis report"""
            report_dir = Path(__file__).parent.parent.parent / "data" / "hybrid_framework_analysis"
            report_dir.mkdir(parents=True, exist_ok=True)

            report_file = report_dir / f"oversight_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Oversight analysis report generated: {report_file.name}")
            return report_file


        except Exception as e:
            self.logger.error(f"Error in generate_report: {e}", exc_info=True)
            raise
def main():
    """CLI interface"""
    analyzer = HybridFrameworkOversightAnalysis()
    analysis = analyzer.analyze_oversights()
    report_file = analyzer.generate_report(analysis)

    print("\n" + "=" * 80)
    print("📋 OVERSIGHT ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"\nReport saved to: {report_file}")
    print(f"\nTotal Oversights: {len(analysis['oversights'])}")
    print(f"Total Recommendations: {len(analysis['recommendations'])}")
    print(f"\nPriority Breakdown:")
    print(f"  🔴 Critical: {len(analysis['critical'])}")
    print(f"  🟠 High: {len(analysis['high'])}")
    print(f"  🟡 Medium: {len(analysis['medium'])}")
    print(f"  🟢 Low: {len(analysis['low'])}")

    return 0


if __name__ == "__main__":


    sys.exit(main())