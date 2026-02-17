#!/usr/bin/env python3
"""
JARVIS Logging Harmony Checker

Ensures all systems (old and new) use comprehensive logging consistently.
Achieves harmony and balance throughout the ecosystem.

Tags: #LOGGING #HARMONY #BALANCE #ECOSYSTEM @JARVIS @LUMINA
"""

import sys
import json
import ast
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("JARVISLoggingHarmony")
except ImportError:
    try:
        from lumina_logger import get_logger
        logger = get_logger("JARVISLoggingHarmony")
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("JARVISLoggingHarmony")


class LoggingHarmonyChecker:
    """Check logging harmony across all systems"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "logging_harmony"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.scripts_dir = project_root / "scripts" / "python"
        self.report_file = self.data_dir / f"harmony_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        self.findings = {
            "comprehensive_logging": [],
            "base_logging": [],
            "standard_logging": [],
            "no_logging": [],
            "mixed_logging": []
        }

    def check_file(self, file_path: Path) -> Dict[str, Any]:
        """Check a single Python file for logging usage"""
        result = {
            "file": str(file_path.relative_to(self.project_root)),
            "uses_comprehensive": False,
            "uses_base": False,
            "uses_standard": False,
            "logging_imports": [],
            "logger_instances": [],
            "status": "unknown"
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for comprehensive logger
            if "lumina_logger_comprehensive" in content or "get_comprehensive_logger" in content:
                result["uses_comprehensive"] = True
                result["status"] = "comprehensive"

            # Check for base logger
            elif "from lumina_logger import" in content or "import lumina_logger" in content:
                result["uses_base"] = True
                result["status"] = "base"

            # Check for standard logging
            elif "import logging" in content or "from logging import" in content:
                result["uses_standard"] = True
                result["status"] = "standard"

            # Check if no logging at all
            if not any([result["uses_comprehensive"], result["uses_base"], result["uses_standard"]]):
                result["status"] = "no_logging"

            # Extract logger imports
            if "get_logger" in content:
                result["logging_imports"].append("get_logger")
            if "get_comprehensive_logger" in content:
                result["logging_imports"].append("get_comprehensive_logger")
            if "LuminaLogger" in content:
                result["logging_imports"].append("LuminaLogger")

        except Exception as e:
            result["error"] = str(e)
            result["status"] = "error"

        return result

    def check_all_scripts(self) -> Dict[str, Any]:
        try:
            """Check all Python scripts for logging harmony"""
            logger.info("🔍 Checking logging harmony across all scripts...")

            if not self.scripts_dir.exists():
                return {
                    "error": "Scripts directory not found",
                    "scripts_dir": str(self.scripts_dir)
                }

            all_results = []

            # Check all Python files
            for py_file in self.scripts_dir.rglob("*.py"):
                # Skip test files and this file
                if "test" in py_file.name.lower() or py_file.name == "jarvis_logging_harmony_checker.py":
                    continue

                result = self.check_file(py_file)
                all_results.append(result)

                # Categorize findings
                status = result.get("status", "unknown")
                if status == "comprehensive":
                    self.findings["comprehensive_logging"].append(result["file"])
                elif status == "base":
                    self.findings["base_logging"].append(result["file"])
                elif status == "standard":
                    self.findings["standard_logging"].append(result["file"])
                elif status == "no_logging":
                    self.findings["no_logging"].append(result["file"])
                else:
                    self.findings["mixed_logging"].append(result["file"])

            report = {
                "checked_at": datetime.now().isoformat(),
                "total_files": len(all_results),
                "findings": self.findings,
                "summary": {
                    "comprehensive": len(self.findings["comprehensive_logging"]),
                    "base": len(self.findings["base_logging"]),
                    "standard": len(self.findings["standard_logging"]),
                    "no_logging": len(self.findings["no_logging"]),
                    "mixed": len(self.findings["mixed_logging"])
                },
                "harmony_score": self._calculate_harmony_score(),
                "recommendations": self._generate_recommendations(),
                "detailed_results": all_results
            }

            # Save report
            with open(self.report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)

            logger.info(f"✅ Harmony check complete. Report saved: {self.report_file}")

            return report

        except Exception as e:
            self.logger.error(f"Error in check_all_scripts: {e}", exc_info=True)
            raise
    def _calculate_harmony_score(self) -> float:
        """Calculate harmony score (0-100)"""
        total = sum(len(files) for files in self.findings.values())
        if total == 0:
            return 0.0

        # Comprehensive logging gets full points
        comprehensive = len(self.findings["comprehensive_logging"])
        # Base logging gets partial points
        base = len(self.findings["base_logging"])
        # Standard logging gets minimal points
        standard = len(self.findings["standard_logging"])
        # No logging gets zero points
        no_logging = len(self.findings["no_logging"])

        score = (
            (comprehensive * 1.0) +
            (base * 0.7) +
            (standard * 0.3) +
            (no_logging * 0.0)
        ) / total * 100

        return round(score, 2)

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations for improving harmony"""
        recommendations = []

        if self.findings["no_logging"]:
            recommendations.append(
                f"Add logging to {len(self.findings['no_logging'])} files without logging"
            )

        if self.findings["standard_logging"]:
            recommendations.append(
                f"Migrate {len(self.findings['standard_logging'])} files from standard logging to comprehensive logger"
            )

        if self.findings["base_logging"]:
            recommendations.append(
                f"Consider upgrading {len(self.findings['base_logging'])} files to comprehensive logger for Azure Monitor integration"
            )

        harmony_score = self._calculate_harmony_score()
        if harmony_score < 80:
            recommendations.append(
                f"Harmony score is {harmony_score:.1f}% - aim for 80%+ for full ecosystem balance"
            )

        if not recommendations:
            recommendations.append("✅ Excellent logging harmony across all systems!")

        return recommendations


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Logging Harmony Checker")
        parser.add_argument("--check", action="store_true", help="Check logging harmony")
        parser.add_argument("--report", action="store_true", help="Show last report")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        checker = LoggingHarmonyChecker(project_root)

        if args.check:
            report = checker.check_all_scripts()
            print("=" * 80)
            print("LOGGING HARMONY REPORT")
            print("=" * 80)
            print(f"\nHarmony Score: {report['harmony_score']}%")
            print(f"\nSummary:")
            print(f"  Comprehensive: {report['summary']['comprehensive']}")
            print(f"  Base: {report['summary']['base']}")
            print(f"  Standard: {report['summary']['standard']}")
            print(f"  No Logging: {report['summary']['no_logging']}")
            print(f"\nRecommendations:")
            for rec in report['recommendations']:
                print(f"  • {rec}")
            print(f"\n📄 Full report: {checker.report_file}")
            print("=" * 80)

        elif args.report:
            # Show last report
            reports_dir = checker.data_dir
            reports = sorted(reports_dir.glob("harmony_report_*.json"), reverse=True)
            if reports:
                with open(reports[0], 'r', encoding='utf-8') as f:
                    report = json.load(f)
                print(json.dumps(report, indent=2, default=str))
            else:
                print("No reports found. Run with --check first.")

        else:
            # Default: run check
            report = checker.check_all_scripts()
            print(json.dumps(report, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()