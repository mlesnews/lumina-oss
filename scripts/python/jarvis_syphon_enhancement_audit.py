#!/usr/bin/env python3
"""
JARVIS SYPHON Enhancement Audit
Audits all static systems in LUMINA for @SYPHON enhancement opportunities.

Tags: #AUDIT #SYPHON #PEAK #ENHANCEMENT @AUTO
"""

import sys
import json
import ast
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISSYPHONAudit")


class SYPHONEnhancementAuditor:
    """
    Audits static systems for SYPHON enhancement opportunities.

    Identifies systems that could benefit from:
    - Intelligence extraction
    - Self-healing capabilities
    - Health monitoring
    - Pattern recognition
    - Data extraction from various sources
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.scripts_dir = project_root / "scripts" / "python"
        self.static_systems: List[Dict[str, Any]] = []
        self.enhancement_opportunities: List[Dict[str, Any]] = []

        # SYPHON enhancement patterns to look for
        self.syphon_patterns = {
            "static_data": ["hardcoded", "static", "config", "constant"],
            "no_extraction": ["no extraction", "manual", "static"],
            "no_health": ["no health", "no monitoring", "no self-healing"],
            "no_intelligence": ["no intelligence", "no pattern", "no learning"]
        }

        # @PEAK patterns that should be integrated
        self.peak_patterns = [
            "@PEAK",
            "peak_pattern",
            "pattern_recognition",
            "workflow_pattern"
        ]

        self.logger.info("✅ SYPHON Enhancement Auditor initialized")

    def _is_static_system(self, file_path: Path) -> bool:
        """Determine if a file represents a static system"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for static indicators
            static_indicators = [
                "class.*System",
                "class.*Manager",
                "class.*Engine",
                "def.*config",
                "STATIC",
                "hardcoded",
                "static.*data"
            ]

            has_static = any(indicator.lower() in content.lower() for indicator in static_indicators)

            # Check if it's a system file (not a utility)
            is_system = any(keyword in file_path.name.lower() for keyword in [
                "system", "manager", "engine", "orchestrator", "controller"
            ])

            return has_static and is_system
        except Exception as e:
            self.logger.warning(f"   ⚠️  Error reading {file_path}: {e}")
            return False

    def _analyze_file_for_syphon(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a file for SYPHON enhancement opportunities"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            analysis = {
                "file": str(file_path.relative_to(self.project_root)),
                "has_syphon": False,
                "has_peak": False,
                "enhancement_opportunities": [],
                "static_indicators": [],
                "recommendations": []
            }

            # Check for existing SYPHON integration
            if "syphon" in content.lower() or "SYPHON" in content:
                analysis["has_syphon"] = True

            # Check for @PEAK patterns
            if any(pattern in content for pattern in self.peak_patterns):
                analysis["has_peak"] = True

            # Check for static data
            if any(indicator in content.lower() for indicator in self.syphon_patterns["static_data"]):
                analysis["static_indicators"].append("static_data")
                if not analysis["has_syphon"]:
                    analysis["enhancement_opportunities"].append({
                        "type": "intelligence_extraction",
                        "description": "Static data could be extracted dynamically via SYPHON",
                        "priority": "medium"
                    })

            # Check for missing health monitoring
            if "class" in content and "health" not in content.lower() and "monitor" not in content.lower():
                analysis["static_indicators"].append("no_health_monitoring")
                analysis["enhancement_opportunities"].append({
                    "type": "self_healing",
                    "description": "System lacks health monitoring - add SYPHON HealthMonitor",
                    "priority": "high"
                })

            # Check for missing extraction capabilities
            if "extract" not in content.lower() and "parse" not in content.lower():
                if "class" in content and any(keyword in file_path.name.lower() for keyword in ["system", "manager"]):
                    analysis["enhancement_opportunities"].append({
                        "type": "intelligence_extraction",
                        "description": "System could benefit from SYPHON extractors for data ingestion",
                        "priority": "medium"
                    })

            # Generate recommendations
            if analysis["enhancement_opportunities"]:
                analysis["recommendations"] = self._generate_recommendations(analysis)

            return analysis
        except Exception as e:
            self.logger.warning(f"   ⚠️  Error analyzing {file_path}: {e}")
            return {"file": str(file_path.relative_to(self.project_root)), "error": str(e)}

    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate specific SYPHON enhancement recommendations"""
        recommendations = []

        for opp in analysis.get("enhancement_opportunities", []):
            if opp["type"] == "self_healing":
                recommendations.append(
                    f"Add SYPHON HealthMonitor and SelfHealingManager for automatic recovery"
                )
            elif opp["type"] == "intelligence_extraction":
                recommendations.append(
                    f"Integrate SYPHON extractors for dynamic data ingestion"
                )

        if not analysis.get("has_peak"):
            recommendations.append(
                "Add @PEAK pattern recognition for workflow optimization"
            )

        return recommendations

    def find_static_systems(self) -> List[Dict[str, Any]]:
        try:
            """Find all static systems in the codebase"""
            self.logger.info("="*80)
            self.logger.info("FINDING STATIC SYSTEMS")
            self.logger.info("="*80)

            static_systems = []

            if not self.scripts_dir.exists():
                self.logger.error(f"   ❌ Scripts directory not found: {self.scripts_dir}")
                return static_systems

            # Scan Python files
            for py_file in self.scripts_dir.rglob("*.py"):
                # Skip test files and __pycache__
                if "test" in py_file.name.lower() or "__pycache__" in str(py_file):
                    continue

                if self._is_static_system(py_file):
                    static_systems.append({
                        "file": str(py_file.relative_to(self.project_root)),
                        "path": str(py_file),
                        "name": py_file.stem
                    })

            self.logger.info(f"   Found {len(static_systems)} static systems")
            self.static_systems = static_systems
            return static_systems

        except Exception as e:
            self.logger.error(f"Error in find_static_systems: {e}", exc_info=True)
            raise
    def audit_for_syphon_enhancement(self) -> Dict[str, Any]:
        try:
            """Audit all static systems for SYPHON enhancement opportunities"""
            self.logger.info("="*80)
            self.logger.info("SYPHON ENHANCEMENT AUDIT - @PEAK INTEGRATION")
            self.logger.info("="*80)

            # Find static systems
            static_systems = self.find_static_systems()

            if not static_systems:
                self.logger.warning("   ⚠️  No static systems found")
                return {"static_systems": [], "enhancements": []}

            # Analyze each system
            enhancements = []
            high_priority = []
            medium_priority = []
            low_priority = []

            self.logger.info(f"\nAnalyzing {len(static_systems)} systems for SYPHON enhancement...")

            for system in static_systems:
                file_path = self.project_root / system["file"]
                if not file_path.exists():
                    continue

                self.logger.info(f"   Analyzing: {system['name']}")
                analysis = self._analyze_file_for_syphon(file_path)

                if analysis.get("enhancement_opportunities"):
                    enhancement = {
                        "system": system["name"],
                        "file": system["file"],
                        "current_state": {
                            "has_syphon": analysis.get("has_syphon", False),
                            "has_peak": analysis.get("has_peak", False),
                            "static_indicators": analysis.get("static_indicators", [])
                        },
                        "opportunities": analysis.get("enhancement_opportunities", []),
                        "recommendations": analysis.get("recommendations", [])
                    }

                    enhancements.append(enhancement)

                    # Categorize by priority
                    priorities = [opp.get("priority", "low") for opp in enhancement["opportunities"]]
                    if "high" in priorities:
                        high_priority.append(enhancement)
                    elif "medium" in priorities:
                        medium_priority.append(enhancement)
                    else:
                        low_priority.append(enhancement)

            # Summary
            self.logger.info("\n" + "="*80)
            self.logger.info("AUDIT SUMMARY")
            self.logger.info("="*80)
            self.logger.info(f"Total Static Systems: {len(static_systems)}")
            self.logger.info(f"Systems Needing Enhancement: {len(enhancements)}")
            self.logger.info(f"   High Priority: {len(high_priority)}")
            self.logger.info(f"   Medium Priority: {len(medium_priority)}")
            self.logger.info(f"   Low Priority: {len(low_priority)}")

            # Print high-priority enhancements
            if high_priority:
                self.logger.info("\n" + "="*80)
                self.logger.info("HIGH PRIORITY ENHANCEMENTS")
                self.logger.info("="*80)
                for enh in high_priority:
                    self.logger.info(f"\n📋 {enh['system']}")
                    self.logger.info(f"   File: {enh['file']}")
                    for rec in enh['recommendations']:
                        self.logger.info(f"   ✅ {rec}")

            audit_result = {
                "timestamp": datetime.now().isoformat(),
                "total_systems": len(static_systems),
                "systems_audited": len(enhancements),
                "high_priority": len(high_priority),
                "medium_priority": len(medium_priority),
                "low_priority": len(low_priority),
                "static_systems": static_systems,
                "enhancements": {
                    "high_priority": high_priority,
                    "medium_priority": medium_priority,
                    "low_priority": low_priority
                }
            }

            self.enhancement_opportunities = enhancements
            return audit_result

        except Exception as e:
            self.logger.error(f"Error in audit_for_syphon_enhancement: {e}", exc_info=True)
            raise
    def save_audit_report(self, audit_result: Dict[str, Any], filename: Optional[str] = None) -> Path:
        try:
            """Save audit report to file"""
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"syphon_enhancement_audit_{timestamp}.json"

            output_dir = self.project_root / "data" / "audits"
            output_dir.mkdir(parents=True, exist_ok=True)

            output_path = output_dir / filename

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(audit_result, f, indent=2, default=str)

            self.logger.info(f"✅ Audit report saved to: {output_path}")
            return output_path


        except Exception as e:
            self.logger.error(f"Error in save_audit_report: {e}", exc_info=True)
            raise
def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="SYPHON Enhancement Audit - @PEAK Integration")
        parser.add_argument("--audit", action="store_true", help="Run full audit")
        parser.add_argument("--save", action="store_true", help="Save audit report")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        auditor = SYPHONEnhancementAuditor(project_root)

        if args.audit or not args.audit:  # Default to audit
            result = auditor.audit_for_syphon_enhancement()

            if args.save:
                auditor.save_audit_report(result)
            else:
                print(json.dumps(result, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()