#!/usr/bin/env python3
"""
Executive Change Report Generator

Generates board member-level change report for major milestones.
Aggregates features from all personal assistance, coding assistance, and IDE systems.
Gives credit to all contributing extensions and systems.

Tags: #RELEASE_NOTES #CHANGELOG #EXECUTIVE_REPORT #MILESTONE @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    logger = get_logger("ExecutiveChangeReport")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ExecutiveChangeReport")


class ExecutiveChangeReportGenerator:
    """
    Generates executive-level change reports for major milestones

    Aggregates features from:
    - Personal assistance systems
    - Coding assistance systems
    - IDE features
    - All extensions and integrations
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.blueprint_file = self.project_root / "config" / "one_ring_blueprint.json"
        self.reports_dir = self.project_root / "data" / "executive_reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        logger.info("=" * 80)
        logger.info("📊 EXECUTIVE CHANGE REPORT GENERATOR")
        logger.info("=" * 80)
        logger.info("   Board member-level change report")
        logger.info("   Aggregating all features under one roof")
        logger.info("   Crediting all contributing systems")
        logger.info("")

    def load_current_version(self) -> Dict[str, Any]:
        """Load current version information"""
        version_info = {
            "version": "1.0.0",  # Current version
            "previous_version": "0.9.0",  # Previous version
            "release_date": datetime.now().strftime("%Y-%m-%d"),
            "milestone": "Major Milestone Release"
        }

        # Try to load from blueprint
        if self.blueprint_file.exists():
            try:
                with open(self.blueprint_file, 'r', encoding='utf-8') as f:
                    blueprint = json.load(f)
                    metadata = blueprint.get("metadata", {})
                    if "version" in metadata:
                        version_info["version"] = metadata["version"]
                    if "previous_version" in metadata:
                        version_info["previous_version"] = metadata.get("previous_version", "0.9.0")
            except Exception as e:
                logger.warning(f"Could not load version from blueprint: {e}")

        return version_info

    def identify_features(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Identify all features from various systems

        Groups features by category and credits contributing systems
        """
        features = {
            "personal_assistance": [],
            "coding_assistance": [],
            "ide_features": [],
            "ai_integration": [],
            "infrastructure": [],
            "communication": [],
            "security": [],
            "performance": []
        }

        # Load One Ring Blueprint to identify systems
        if self.blueprint_file.exists():
            try:
                with open(self.blueprint_file, 'r', encoding='utf-8') as f:
                    blueprint = json.load(f)

                    # Extract core systems
                    core_systems = blueprint.get("core_systems", {})
                    initiatives = blueprint.get("initiatives", [])

                    # Personal Assistance Features
                    if "jarvis" in str(core_systems).lower():
                        features["personal_assistance"].append({
                            "name": "JARVIS Personal Assistant",
                            "description": "AI-powered personal assistant with voice commands, gaze sync, and autonomous operation",
                            "contributing_systems": ["JARVIS", "JARVIS Narrator Avatar", "Gaze Sync System"],
                            "key_features": [
                                "Voice command recognition",
                                "Gaze synchronization with operator",
                                "Autonomous workflow execution",
                                "Self-awareness and intelligent gaze",
                                "Flow state detection"
                            ]
                        })

                    # Coding Assistance Features
                    features["coding_assistance"].append({
                        "name": "AI Coding Assistant",
                        "description": "Comprehensive coding assistance with multiple AI models and local-first policy",
                        "contributing_systems": ["JARVIS Unified AI Actions", "Local-First LLM Router", "AI Coordination"],
                        "key_features": [
                            "Multi-model AI routing (Ollama, Kaiju, Ultron)",
                            "Local-first AI policy enforcement",
                            "Intelligent model selection",
                            "Code quality analysis",
                            "Autonomous code generation"
                        ]
                    })

                    # IDE Features
                    features["ide_features"].append({
                        "name": "Cursor IDE Integration",
                        "description": "Deep integration with Cursor IDE for enhanced development experience",
                        "contributing_systems": ["Cursor IDE Todo Display", "Cursor IDE Integration", "MANUS Controller"],
                        "key_features": [
                            "Master TODO list integration",
                            "Real-time status display",
                            "Autonomous workflow execution",
                            "IDE UI/UX modification capability"
                        ]
                    })

                    # AI Integration Features
                    features["ai_integration"].append({
                        "name": "Multi-Agent AI System",
                        "description": "Advanced AI agent collaboration and coordination",
                        "contributing_systems": ["JARVIS", "MARVIN", "ULTRON", "Agent Collaboration System"],
                        "key_features": [
                            "Parallel agent sessions (Goldilocks Zone: 4 sessions)",
                            "Agent collaboration and coordination",
                            "Subagent delegation",
                            "Autonomous workflow execution",
                            "AI-to-AI communication"
                        ]
                    })

                    # Infrastructure Features
                    if any("dyno" in str(i).lower() for i in initiatives):
                        features["performance"].append({
                            "name": "DYNO Performance Testing",
                            "description": "Dynamometer-style performance testing and optimization",
                            "contributing_systems": ["MARVIN DYNO Stress Tester", "Agent Session DYNO Test"],
                            "key_features": [
                                "Baseline establishment and calibration",
                                "A/B experiment framework",
                                "Stress testing with multiple vectors",
                                "Performance optimization",
                                "Goldilocks Zone identification"
                            ]
                        })

                    # Communication Features
                    features["communication"].append({
                        "name": "Unified Communication Gateway",
                        "description": "Centralized communication routing via NAS n8n",
                        "contributing_systems": ["n8n Workflow Engine", "Email Routing", "SMS Gateway"],
                        "key_features": [
                            "Email endpoint routing (9 endpoints)",
                            "SMS via ElevenLabs integration",
                            "Multi-channel communication support",
                            "Workflow automation"
                        ]
                    })

                    # Security Features
                    features["security"].append({
                        "name": "Enhanced Security Framework",
                        "description": "Comprehensive security monitoring and secret management",
                        "contributing_systems": ["MARVIN Secret Leak Detector", "Azure Key Vault", "Dead Man Switch"],
                        "key_features": [
                            "Real-time secret leak detection",
                            "Azure Key Vault integration",
                            "SMS approval system",
                            "Security audit logging"
                        ]
                    })

            except Exception as e:
                logger.error(f"Error identifying features: {e}")

        return features

    def generate_report(
        self,
        previous_version: Optional[str] = None,
        current_version: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate executive change report"""

        version_info = self.load_current_version()
        if previous_version:
            version_info["previous_version"] = previous_version
        if current_version:
            version_info["version"] = current_version

        features = self.identify_features()

        # Count total features
        total_features = sum(len(f) for f in features.values())

        # Generate report
        report = {
            "report_type": "Executive Change Report",
            "report_level": "Board Member",
            "version_info": version_info,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_new_features": total_features,
                "categories": {k: len(v) for k, v in features.items() if v}
            },
            "features_by_category": features,
            "contributing_systems": self._extract_contributing_systems(features),
            "executive_summary": self._generate_executive_summary(version_info, features),
            "detailed_changes": self._generate_detailed_changes(features)
        }

        return report

    def _extract_contributing_systems(self, features: Dict[str, List[Dict]]) -> List[str]:
        """Extract all contributing systems"""
        systems = set()

        for category_features in features.values():
            for feature in category_features:
                contributing = feature.get("contributing_systems", [])
                systems.update(contributing)

        return sorted(list(systems))

    def _generate_executive_summary(
        self,
        version_info: Dict[str, Any],
        features: Dict[str, List[Dict]]
    ) -> str:
        """Generate executive summary"""
        total = sum(len(f) for f in features.values())

        summary = f"""
LUMINA {version_info['version']} - Executive Change Report

This major milestone release represents a significant evolution of the LUMINA platform,
consolidating features and functionality from multiple personal assistance, coding assistance,
and IDE systems under one unified roof.

KEY HIGHLIGHTS:
- {total} major new features and enhancements
- Integration of multiple AI systems (JARVIS, MARVIN, ULTRON)
- Enhanced IDE integration with Cursor
- Performance optimization with DYNO testing framework
- Unified communication gateway
- Advanced security framework

All features credit the work done by separate extensions and systems that continue to
contribute to the platform's evolution.
"""
        return summary.strip()

    def _generate_detailed_changes(self, features: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """Generate detailed changes by category"""
        return features

    def save_report(self, report: Dict[str, Any], format: str = "both") -> Dict[str, Path]:
        try:
            """Save report in multiple formats"""
            saved_files = {}

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            version = report["version_info"]["version"]

            # JSON format
            if format in ["json", "both"]:
                json_file = self.reports_dir / f"change_report_v{version}_{timestamp}.json"
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                saved_files["json"] = json_file
                logger.info(f"📁 JSON report saved: {json_file}")

            # Markdown format (executive-friendly)
            if format in ["markdown", "both"]:
                md_file = self.reports_dir / f"change_report_v{version}_{timestamp}.md"
                md_content = self._format_markdown(report)
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                saved_files["markdown"] = md_file
                logger.info(f"📁 Markdown report saved: {md_file}")

            return saved_files

        except Exception as e:
            self.logger.error(f"Error in save_report: {e}", exc_info=True)
            raise
    def _format_markdown(self, report: Dict[str, Any]) -> str:
        """Format report as markdown for executive presentation"""
        version_info = report["version_info"]
        features = report["features_by_category"]
        summary = report["summary"]

        md = f"""# LUMINA {version_info['version']} - Executive Change Report

**Report Level:** Board Member  
**Release Date:** {version_info['release_date']}  
**Previous Version:** {version_info['previous_version']}  
**Current Version:** {version_info['version']}  
**Milestone:** {version_info['milestone']}

---

## Executive Summary

{report['executive_summary']}

---

## Overview

This release consolidates features and functionality from multiple personal assistance,
coding assistance, and IDE systems, bringing them together under one unified platform.
We acknowledge and credit all the work done by separate extensions and systems that
continue to contribute to LUMINA's evolution.

**Total New Features:** {summary['total_new_features']}

---

## Features by Category

"""

        # Personal Assistance
        if features.get("personal_assistance"):
            md += "### 🤖 Personal Assistance\n\n"
            for feature in features["personal_assistance"]:
                md += f"#### {feature['name']}\n\n"
                md += f"{feature['description']}\n\n"
                md += "**Contributing Systems:**\n"
                for system in feature.get("contributing_systems", []):
                    md += f"- {system}\n"
                md += "\n**Key Features:**\n"
                for key_feature in feature.get("key_features", []):
                    md += f"- {key_feature}\n"
                md += "\n"

        # Coding Assistance
        if features.get("coding_assistance"):
            md += "### 💻 Coding Assistance\n\n"
            for feature in features["coding_assistance"]:
                md += f"#### {feature['name']}\n\n"
                md += f"{feature['description']}\n\n"
                md += "**Contributing Systems:**\n"
                for system in feature.get("contributing_systems", []):
                    md += f"- {system}\n"
                md += "\n**Key Features:**\n"
                for key_feature in feature.get("key_features", []):
                    md += f"- {key_feature}\n"
                md += "\n"

        # IDE Features
        if features.get("ide_features"):
            md += "### 🛠️ IDE Features\n\n"
            for feature in features["ide_features"]:
                md += f"#### {feature['name']}\n\n"
                md += f"{feature['description']}\n\n"
                md += "**Contributing Systems:**\n"
                for system in feature.get("contributing_systems", []):
                    md += f"- {system}\n"
                md += "\n**Key Features:**\n"
                for key_feature in feature.get("key_features", []):
                    md += f"- {key_feature}\n"
                md += "\n"

        # AI Integration
        if features.get("ai_integration"):
            md += "### 🧠 AI Integration\n\n"
            for feature in features["ai_integration"]:
                md += f"#### {feature['name']}\n\n"
                md += f"{feature['description']}\n\n"
                md += "**Contributing Systems:**\n"
                for system in feature.get("contributing_systems", []):
                    md += f"- {system}\n"
                md += "\n**Key Features:**\n"
                for key_feature in feature.get("key_features", []):
                    md += f"- {key_feature}\n"
                md += "\n"

        # Performance
        if features.get("performance"):
            md += "### ⚡ Performance\n\n"
            for feature in features["performance"]:
                md += f"#### {feature['name']}\n\n"
                md += f"{feature['description']}\n\n"
                md += "**Contributing Systems:**\n"
                for system in feature.get("contributing_systems", []):
                    md += f"- {system}\n"
                md += "\n**Key Features:**\n"
                for key_feature in feature.get("key_features", []):
                    md += f"- {key_feature}\n"
                md += "\n"

        # Communication
        if features.get("communication"):
            md += "### 📡 Communication\n\n"
            for feature in features["communication"]:
                md += f"#### {feature['name']}\n\n"
                md += f"{feature['description']}\n\n"
                md += "**Contributing Systems:**\n"
                for system in feature.get("contributing_systems", []):
                    md += f"- {system}\n"
                md += "\n**Key Features:**\n"
                for key_feature in feature.get("key_features", []):
                    md += f"- {key_feature}\n"
                md += "\n"

        # Security
        if features.get("security"):
            md += "### 🔒 Security\n\n"
            for feature in features["security"]:
                md += f"#### {feature['name']}\n\n"
                md += f"{feature['description']}\n\n"
                md += "**Contributing Systems:**\n"
                for system in feature.get("contributing_systems", []):
                    md += f"- {system}\n"
                md += "\n**Key Features:**\n"
                for key_feature in feature.get("key_features", []):
                    md += f"- {key_feature}\n"
                md += "\n"

        # Contributing Systems
        md += "---\n\n"
        md += "## Contributing Systems\n\n"
        md += "We acknowledge and credit all systems and extensions that contribute to LUMINA:\n\n"
        for system in sorted(report["contributing_systems"]):
            md += f"- {system}\n"
        md += "\n"

        md += "---\n\n"
        md += f"*Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

        return md

    def print_report(self, report: Dict[str, Any]):
        """Print formatted report"""
        version_info = report["version_info"]
        summary = report["summary"]

        print("=" * 80)
        print(f"📊 EXECUTIVE CHANGE REPORT - LUMINA {version_info['version']}")
        print("=" * 80)
        print(f"   Previous Version: {version_info['previous_version']}")
        print(f"   Current Version: {version_info['version']}")
        print(f"   Release Date: {version_info['release_date']}")
        print(f"   Milestone: {version_info['milestone']}")
        print("")
        print("EXECUTIVE SUMMARY")
        print("=" * 80)
        print(report["executive_summary"])
        print("")
        print("FEATURES SUMMARY")
        print("=" * 80)
        print(f"   Total New Features: {summary['total_new_features']}")
        print("")
        for category, count in summary['categories'].items():
            if count > 0:
                print(f"   {category.replace('_', ' ').title()}: {count}")
        print("")
        print("CONTRIBUTING SYSTEMS")
        print("=" * 80)
        for system in report["contributing_systems"]:
            print(f"   - {system}")
        print("")


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate executive change report")
    parser.add_argument("--previous-version", help="Previous version number")
    parser.add_argument("--current-version", help="Current version number")
    parser.add_argument("--format", choices=["json", "markdown", "both"], default="both",
                       help="Output format")
    parser.add_argument("--no-save", action="store_true", help="Don't save report")

    args = parser.parse_args()

    generator = ExecutiveChangeReportGenerator()
    report = generator.generate_report(
        previous_version=args.previous_version,
        current_version=args.current_version
    )

    generator.print_report(report)

    if not args.no_save:
        saved_files = generator.save_report(report, format=args.format)
        print("")
        print("=" * 80)
        print("📁 REPORTS SAVED")
        print("=" * 80)
        for fmt, path in saved_files.items():
            print(f"   {fmt.upper()}: {path}")

    return report


if __name__ == "__main__":

    main()