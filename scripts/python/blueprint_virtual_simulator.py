#!/usr/bin/env python3
"""
Blueprint Virtual Simulator

Simulates the master blueprint against actual project state to detect:
- Design inconsistencies
- Missing components
- Version mismatches
- Integration gaps
- State drift

Compares blueprint expectations to reality.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import subprocess
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - 🔬 BlueprintSimulator - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BlueprintVirtualSimulator:
    """
    Virtual Simulator for One Ring Blueprint

    Compares blueprint to actual project state
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.blueprint_path = self.project_root / "config" / "one_ring_blueprint.json"

    def load_blueprint(self) -> Dict[str, Any]:
        """Load the master blueprint"""
        try:
            with open(self.blueprint_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load blueprint: {e}")
            return {}

    def scan_project_structure(self) -> Dict[str, Any]:
        try:
            """Scan actual project structure"""
            structure = {
                "files": {},
                "directories": {},
                "scripts": {},
                "configs": {},
                "docs": {},
                "systems": {}
            }

            # Scan key directories
            key_dirs = {
                "scripts": self.project_root / "scripts",
                "config": self.project_root / "config",
                "docs": self.project_root / "docs",
                "data": self.project_root / "data"
            }

            for name, path in key_dirs.items():
                if path.exists():
                    structure["directories"][name] = {
                        "exists": True,
                        "path": str(path.relative_to(self.project_root)),
                        "files": self._scan_directory(path)
                    }
                else:
                    structure["directories"][name] = {
                        "exists": False,
                        "path": str(path.relative_to(self.project_root))
                    }

            # Scan Python scripts
            scripts_dir = self.project_root / "scripts" / "python"
            if scripts_dir.exists():
                structure["scripts"]["python"] = [
                    str(f.relative_to(self.project_root))
                    for f in scripts_dir.rglob("*.py")
                ]

            return structure

        except Exception as e:
            self.logger.error(f"Error in scan_project_structure: {e}", exc_info=True)
            raise
    def _scan_directory(self, path: Path, max_depth: int = 3, current_depth: int = 0) -> List[str]:
        """Recursively scan directory"""
        files = []
        if current_depth >= max_depth:
            return files

        try:
            for item in path.iterdir():
                if item.is_file():
                    files.append(str(item.relative_to(self.project_root)))
                elif item.is_dir() and not item.name.startswith('.'):
                    files.extend(self._scan_directory(item, max_depth, current_depth + 1))
        except PermissionError:
            pass

        return files

    def check_system_exists(self, system_name: str, system_config: Dict[str, Any]) -> Dict[str, Any]:
        """Check if a system exists and matches blueprint"""
        result = {
            "system": system_name,
            "exists": False,
            "matches": False,
            "issues": [],
            "location": system_config.get("location", ""),
            "status": system_config.get("status", "unknown")
        }

        # Check if location exists (file, directory, or architecture)
        if "location" in system_config and system_config["location"]:
            file_path = self.project_root / system_config["location"]
            if file_path.exists():
                result["exists"] = True

                # Check if it's a Python file
                if file_path.suffix == ".py":
                    try:
                        # Try to read and check for key components
                        content = file_path.read_text(encoding='utf-8')

                        # Basic validation
                        if "class" in content or "def" in content:
                            result["matches"] = True
                        else:
                            result["issues"].append("File exists but appears empty or invalid")
                    except Exception as e:
                        result["issues"].append(f"Error reading file: {e}")
                # Check if it's a directory (valid for directory-based systems)
                elif file_path.is_dir():
                    # Directory exists = valid for directory-based systems
                    result["matches"] = True
                else:
                    # File exists but not .py - still valid if it exists
                    result["matches"] = True
            else:
                result["issues"].append(f"Location not found: {system_config['location']}")
        # Architecture-defined systems (no location) are valid if status is architecture_defined
        elif system_config.get("status") in ["architecture_defined", "ACTIVE", "operational"]:
            result["exists"] = True
            result["matches"] = True

        return result

    def compare_blueprint_to_state(self) -> Dict[str, Any]:
        try:
            """Main comparison: Blueprint vs Actual State"""
            logger.info("🔬 Starting blueprint simulation...")

            blueprint = self.load_blueprint()
            actual_state = self.scan_project_structure()

            comparison = {
                "timestamp": datetime.now().isoformat(),
                "blueprint_version": blueprint.get("blueprint_metadata", {}).get("version", "unknown"),
                "blueprint_last_updated": blueprint.get("blueprint_metadata", {}).get("last_updated", "unknown"),
                "comparison_results": {
                    "core_systems": {},
                    "integrations": {},
                    "components": {},
                    "inconsistencies": [],
                    "missing_components": [],
                    "version_mismatches": [],
                    "integration_gaps": []
                },
                "overall_status": "unknown"
            }

            # Check core systems
            core_systems = blueprint.get("core_systems", {})
            for system_name, system_config in core_systems.items():
                check_result = self.check_system_exists(system_name, system_config)
                comparison["comparison_results"]["core_systems"][system_name] = check_result

                if not check_result["exists"]:
                    comparison["comparison_results"]["missing_components"].append({
                        "type": "core_system",
                        "name": system_name,
                        "expected_location": system_config.get("location", "unknown")
                    })

                if check_result["exists"] and not check_result["matches"]:
                    comparison["comparison_results"]["inconsistencies"].append({
                        "type": "design_inconsistency",
                        "system": system_name,
                        "issues": check_result["issues"]
                    })

            # Check integrations
            integrations = blueprint.get("integrations", {})
            for integration_name, integration_config in integrations.items():
                # Similar check for integrations
                if "location" in integration_config:
                    file_path = self.project_root / integration_config["location"]
                    if not file_path.exists():
                        comparison["comparison_results"]["integration_gaps"].append({
                            "type": "integration",
                            "name": integration_name,
                            "expected_location": integration_config["location"]
                        })

            # Calculate overall status
            total_systems = len(core_systems)
            existing_systems = sum(1 for r in comparison["comparison_results"]["core_systems"].values() if r["exists"])
            matching_systems = sum(1 for r in comparison["comparison_results"]["core_systems"].values() if r["matches"])

            if total_systems == 0:
                comparison["overall_status"] = "unknown"
            elif existing_systems == total_systems and matching_systems == total_systems:
                comparison["overall_status"] = "fully_aligned"
            elif existing_systems == total_systems:
                comparison["overall_status"] = "exists_but_inconsistent"
            elif existing_systems > total_systems * 0.5:
                comparison["overall_status"] = "partially_aligned"
            else:
                comparison["overall_status"] = "significantly_drifted"

            comparison["metrics"] = {
                "total_systems": total_systems,
                "existing_systems": existing_systems,
                "matching_systems": matching_systems,
                "alignment_percentage": (matching_systems / total_systems * 100) if total_systems > 0 else 0,
                "missing_count": len(comparison["comparison_results"]["missing_components"]),
                "inconsistencies_count": len(comparison["comparison_results"]["inconsistencies"]),
                "integration_gaps_count": len(comparison["comparison_results"]["integration_gaps"])
            }

            logger.info(f"✅ Simulation complete - Status: {comparison['overall_status']}")
            logger.info(f"   Alignment: {comparison['metrics']['alignment_percentage']:.1f}%")
            logger.info(f"   Missing: {comparison['metrics']['missing_count']}")
            logger.info(f"   Inconsistencies: {comparison['metrics']['inconsistencies_count']}")

            return comparison

        except Exception as e:
            self.logger.error(f"Error in compare_blueprint_to_state: {e}", exc_info=True)
            raise
    def generate_report(self, comparison: Optional[Dict[str, Any]] = None) -> str:
        """Generate human-readable report"""
        if comparison is None:
            comparison = self.compare_blueprint_to_state()

        report_lines = [
            "=" * 80,
            "🔬 BLUEPRINT VIRTUAL SIMULATOR REPORT",
            "=" * 80,
            "",
            f"Timestamp: {comparison['timestamp']}",
            f"Blueprint Version: {comparison['blueprint_version']}",
            f"Blueprint Last Updated: {comparison['blueprint_last_updated']}",
            "",
            "OVERALL STATUS",
            "-" * 80,
            f"Status: {comparison['overall_status'].upper().replace('_', ' ')}",
            f"Alignment: {comparison['metrics']['alignment_percentage']:.1f}%",
            f"Existing Systems: {comparison['metrics']['existing_systems']}/{comparison['metrics']['total_systems']}",
            f"Matching Systems: {comparison['metrics']['matching_systems']}/{comparison['metrics']['total_systems']}",
            "",
            "ISSUES DETECTED",
            "-" * 80,
            f"Missing Components: {comparison['metrics']['missing_count']}",
            f"Design Inconsistencies: {comparison['metrics']['inconsistencies_count']}",
            f"Integration Gaps: {comparison['metrics']['integration_gaps_count']}",
            ""
        ]

        # Missing components
        if comparison["comparison_results"]["missing_components"]:
            report_lines.append("MISSING COMPONENTS:")
            for item in comparison["comparison_results"]["missing_components"]:
                report_lines.append(f"  ❌ {item['name']} ({item['type']})")
                report_lines.append(f"     Expected: {item['expected_location']}")
            report_lines.append("")

        # Inconsistencies
        if comparison["comparison_results"]["inconsistencies"]:
            report_lines.append("DESIGN INCONSISTENCIES:")
            for item in comparison["comparison_results"]["inconsistencies"]:
                report_lines.append(f"  ⚠️ {item['system']}")
                for issue in item["issues"]:
                    report_lines.append(f"     - {issue}")
            report_lines.append("")

        # Integration gaps
        if comparison["comparison_results"]["integration_gaps"]:
            report_lines.append("INTEGRATION GAPS:")
            for item in comparison["comparison_results"]["integration_gaps"]:
                report_lines.append(f"  ⚠️ {item['name']}")
                report_lines.append(f"     Expected: {item['expected_location']}")
            report_lines.append("")

        report_lines.append("=" * 80)

        return "\n".join(report_lines)


def main():
    try:
        """CLI entry point"""
        simulator = BlueprintVirtualSimulator()

        print("\n" + "=" * 80)
        print("🔬 BLUEPRINT VIRTUAL SIMULATOR")
        print("=" * 80)
        print()

        # Run simulation
        comparison = simulator.compare_blueprint_to_state()

        # Generate and print report
        report = simulator.generate_report(comparison)
        print(report)

        # Save results
        output_dir = simulator.project_root / "data" / "blueprint_simulations"
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = output_dir / f"simulation_{timestamp}.json"
        report_path = output_dir / f"simulation_report_{timestamp}.md"

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(comparison, f, indent=2)

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n✅ Results saved:")
        print(f"   JSON: {json_path}")
        print(f"   Report: {report_path}")
        print()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()