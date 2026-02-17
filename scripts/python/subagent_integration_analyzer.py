#!/usr/bin/env python3
"""
SubAgent Integration Analyzer
Analyzes all frameworks for SubAgent integration opportunities

Tags: #SUBAGENTS #INTEGRATION #OPPORTUNITIES #CHALLENGE @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
import json

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SubAgentIntegrationAnalyzer")


class SubAgentIntegrationAnalyzer:
    """
    Analyzes all frameworks for SubAgent integration opportunities
    """

    def __init__(self, project_root: Path):
        """Initialize analyzer"""
        self.project_root = project_root
        self.logger = logger

        self.scripts_dir = project_root / "scripts" / "python"

        # Framework categories
        self.categories = {
            "orchestrators": [],
            "managers": [],
            "systems": [],
            "controllers": [],
            "coordinators": []
        }

        # Integration status
        self.integration_status = {
            "with_subagents": [],
            "without_subagents": [],
            "opportunities": []
        }

        self.logger.info("🔍 SubAgent Integration Analyzer initialized")

    def analyze_all_frameworks(self) -> Dict[str, Any]:
        """Analyze all frameworks for SubAgent opportunities"""
        self.logger.info("🔍 Analyzing all frameworks...")

        # Find all Python files
        python_files = list(self.scripts_dir.glob("*.py"))

        # Categorize
        for py_file in python_files:
            self._categorize_file(py_file)

        # Check for existing SubAgent integration
        self._check_existing_integration()

        # Calculate opportunities
        opportunities = self._calculate_opportunities()

        self.logger.info(f"   ✅ Analyzed {len(python_files)} files")
        self.logger.info(f"   Opportunities: {opportunities['total']}")

        return {
            "categories": self.categories,
            "integration_status": self.integration_status,
            "opportunities": opportunities
        }

    def _categorize_file(self, file_path: Path):
        """Categorize file by type"""
        name = file_path.stem.lower()

        if "orchestrat" in name:
            self.categories["orchestrators"].append(str(file_path.name))
        elif "manager" in name:
            self.categories["managers"].append(str(file_path.name))
        elif "system" in name:
            self.categories["systems"].append(str(file_path.name))
        elif "controller" in name:
            self.categories["controllers"].append(str(file_path.name))
        elif "coordinat" in name:
            self.categories["coordinators"].append(str(file_path.name))

    def _check_existing_integration(self):
        try:
            """Check which frameworks already have SubAgent integration"""
            # Check JARVIS Master Orchestrator
            master_orch = self.scripts_dir / "jarvis_lumina_master_orchestrator.py"
            if master_orch.exists():
                with open(master_orch, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "SubAgent" in content or "subagent" in content:
                        self.integration_status["with_subagents"].append("jarvis_lumina_master_orchestrator.py")

            # Check others
            for category, files in self.categories.items():
                for file in files:
                    file_path = self.scripts_dir / file
                    if file_path.exists():
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if "SubAgent" in content or "subagent" in content:
                                if file not in self.integration_status["with_subagents"]:
                                    self.integration_status["with_subagents"].append(file)
                            else:
                                if file not in self.integration_status["without_subagents"]:
                                    self.integration_status["without_subagents"].append(file)

        except Exception as e:
            self.logger.error(f"Error in _check_existing_integration: {e}", exc_info=True)
            raise
    def _calculate_opportunities(self) -> Dict[str, Any]:
        """Calculate integration opportunities"""
        total = sum(len(files) for files in self.categories.values())
        with_subagents = len(self.integration_status["with_subagents"])
        without_subagents = len(self.integration_status["without_subagents"])

        opportunities = {
            "total_frameworks": total,
            "with_subagents": with_subagents,
            "without_subagents": without_subagents,
            "total": without_subagents,
            "by_category": {
                "orchestrators": len(self.categories["orchestrators"]),
                "managers": len(self.categories["managers"]),
                "systems": len(self.categories["systems"]),
                "controllers": len(self.categories["controllers"]),
                "coordinators": len(self.categories["coordinators"])
            }
        }

        return opportunities

    def generate_integration_report(self) -> Dict[str, Any]:
        """Generate comprehensive integration report"""
        analysis = self.analyze_all_frameworks()

        report = {
            "summary": {
                "total_frameworks": analysis["opportunities"]["total_frameworks"],
                "with_subagents": analysis["opportunities"]["with_subagents"],
                "without_subagents": analysis["opportunities"]["without_subagents"],
                "integration_opportunities": analysis["opportunities"]["total"]
            },
            "categories": analysis["categories"],
            "integration_status": analysis["integration_status"],
            "recommendations": {
                "priority_1": "Integrate SubAgents into all orchestrators",
                "priority_2": "Integrate SubAgents into key managers",
                "priority_3": "Integrate SubAgents into critical systems",
                "priority_4": "Full integration across all frameworks"
            }
        }

        return report


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="SubAgent Integration Analyzer")
        parser.add_argument("--analyze", action="store_true", help="Analyze all frameworks")
        parser.add_argument("--report", action="store_true", help="Generate integration report")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        analyzer = SubAgentIntegrationAnalyzer(project_root)

        if args.analyze or args.report:
            report = analyzer.generate_integration_report()

            print("\n" + "=" * 80)
            print("SUBAGENT INTEGRATION OPPORTUNITIES")
            print("=" * 80)
            print()
            print("Summary:")
            print(f"  Total Frameworks: {report['summary']['total_frameworks']}")
            print(f"  With SubAgents: {report['summary']['with_subagents']}")
            print(f"  Without SubAgents: {report['summary']['without_subagents']}")
            print(f"  Integration Opportunities: {report['summary']['integration_opportunities']}")
            print()
            print("By Category:")
            for category, count in report['categories'].items():
                print(f"  {category.capitalize()}: {len(count)}")
            print()
            print("Recommendations:")
            for priority, rec in report['recommendations'].items():
                print(f"  {priority}: {rec}")
            print()

            if args.report:
                # Save report
                report_file = project_root / "data" / "subagent_integration_report.json"
                report_file.parent.mkdir(parents=True, exist_ok=True)
                with open(report_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, default=str)
                print(f"✅ Report saved: {report_file}")
        else:
            print("Usage:")
            print("  --analyze  : Analyze all frameworks")
            print("  --report   : Generate and save integration report")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()