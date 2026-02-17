"""
PUBLIC: Spring Cleaning Analyzer
Location: scripts/python/spring_cleaning_analyzer.py
License: MIT

Analyzes repository to identify cleanup candidates for spring cleaning.
SAFE - Only analyzes, never deletes.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SpringCleaningAnalyzer:
    """Analyze repository for cleanup candidates."""

    def __init__(self, project_root: Path):
        """
        Initialize analyzer.

        Args:
            project_root: Path to project root
        """
        self.project_root = project_root
        self.data_path = project_root / "data"
        self.config_path = project_root / "config"
        self.logs_path = project_root / ".lumina" / "logs"

        self.analysis = {
            "analyzed_at": datetime.now().isoformat(),
            "project": "LUMINA",
            "categories": {},
            "summary": {},
            "recommendations": []
        }

    def analyze_config_backups(self) -> Dict[str, Any]:
        try:
            """
            Analyze config backup files.

            Returns:
                Analysis of config backups
            """
            logger.info("Analyzing config backups...")

            backup_files = list(self.config_path.glob("*backup*.json"))
            backup_files.extend(self.config_path.glob("*backup*.encrypted"))

            # Group by base name
            backups_by_base = defaultdict(list)
            for backup in backup_files:
                # Extract base name (before backup timestamp)
                name = backup.stem
                if ".encrypted" in name:
                    name = name.replace(".encrypted", "")

                # Try to extract base
                if "backup_" in name:
                    base = name.split("backup_")[0]
                    backups_by_base[base].append(backup)

            # Analyze
            total_backups = len(backup_files)
            total_size = sum(f.stat().st_size for f in backup_files if f.exists())

            # Find files with many backups
            excessive_backups = {
                base: files
                for base, files in backups_by_base.items()
                if len(files) > 10
            }

            return {
                "category": "config_backups",
                "total_files": total_backups,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "files_by_base": len(backups_by_base),
                "excessive_backups": {
                    base: len(files)
                    for base, files in excessive_backups.items()
                },
                "recommendation": "Archive all but latest 3 backups per file",
                "estimated_savings_files": max(0, total_backups - (len(backups_by_base) * 3)),
                "estimated_savings_mb": round(total_size * 0.7 / (1024 * 1024), 2)  # Keep 30%
            }

        except Exception as e:
            self.logger.error(f"Error in analyze_config_backups: {e}", exc_info=True)
            raise
    def analyze_old_sessions(self, days_to_keep: int = 30) -> Dict[str, Any]:
        """
        Analyze old session files.

        Args:
            days_to_keep: Number of days to keep

        Returns:
            Analysis of old sessions
        """
        logger.info("Analyzing old session files...")

        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        old_sessions = []
        total_size = 0

        # Find session files
        session_patterns = [
            "**/session*.json",
            "**/session_*.json",
            "**/*session*.json"
        ]

        for pattern in session_patterns:
            try:
                for session_file in self.data_path.glob(pattern):
                    try:
                        mtime = datetime.fromtimestamp(session_file.stat().st_mtime)
                        if mtime < cutoff_date:
                            old_sessions.append(session_file)
                            total_size += session_file.stat().st_size
                    except (OSError, ValueError):
                        continue
            except Exception as e:
                logger.warning(f"Error analyzing {pattern}: {e}")

        return {
            "category": "old_sessions",
            "total_old_files": len(old_sessions),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "cutoff_date": cutoff_date.isoformat(),
            "days_to_keep": days_to_keep,
            "recommendation": f"Archive sessions older than {days_to_keep} days",
            "estimated_savings_files": len(old_sessions),
            "estimated_savings_mb": round(total_size / (1024 * 1024), 2)
        }

    def analyze_extension_data(self) -> Dict[str, Any]:
        """
        Analyze extension data files.

        Returns:
            Analysis of extension data
        """
        logger.info("Analyzing extension data...")

        ext_path = self.data_path / "extensions"
        if not ext_path.exists():
            return {
                "category": "extension_data",
                "total_files": 0,
                "total_size_mb": 0,
                "recommendation": "No extension data found"
            }

        # Count files (memory-efficient)
        file_count = 0
        total_size = 0

        try:
            for ext_dir in ext_path.iterdir():
                if ext_dir.is_dir():
                    try:
                        # Count files in extension directory
                        for file in ext_dir.rglob("*"):
                            if file.is_file():
                                file_count += 1
                                try:
                                    total_size += file.stat().st_size
                                except OSError:
                                    pass
                    except Exception as e:
                        logger.warning(f"Error analyzing {ext_dir}: {e}")
        except Exception as e:
            logger.error(f"Error analyzing extension data: {e}")
            return {
                "category": "extension_data",
                "error": str(e),
                "note": "Too large to analyze completely"
            }

        return {
            "category": "extension_data",
            "total_files": file_count,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "recommendation": "Review and remove unused extension data",
            "estimated_savings_files": file_count // 2,  # Estimate 50% can be removed
            "estimated_savings_mb": round(total_size * 0.5 / (1024 * 1024), 2)
        }

    def analyze_old_analytics(self, days_to_keep: int = 90) -> Dict[str, Any]:
        """
        Analyze old analytics reports.

        Args:
            days_to_keep: Number of days to keep

        Returns:
            Analysis of old analytics
        """
        logger.info("Analyzing old analytics...")

        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        old_reports = []
        total_size = 0

        # Find analytics reports
        analytics_paths = [
            self.data_path / "lumina_metrics" / "analytics",
            self.data_path / "request_tracking",
            self.data_path / "universal_measurement"
        ]

        for analytics_path in analytics_paths:
            if not analytics_path.exists():
                continue

            try:
                for report_file in analytics_path.glob("*.json"):
                    try:
                        mtime = datetime.fromtimestamp(report_file.stat().st_mtime)
                        if mtime < cutoff_date:
                            old_reports.append(report_file)
                            total_size += report_file.stat().st_size
                    except (OSError, ValueError):
                        continue
            except Exception as e:
                logger.warning(f"Error analyzing {analytics_path}: {e}")

        return {
            "category": "old_analytics",
            "total_old_files": len(old_reports),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "cutoff_date": cutoff_date.isoformat(),
            "days_to_keep": days_to_keep,
            "recommendation": f"Archive analytics older than {days_to_keep} days",
            "estimated_savings_files": len(old_reports),
            "estimated_savings_mb": round(total_size / (1024 * 1024), 2)
        }

    def analyze_temporary_files(self) -> Dict[str, Any]:
        """
        Analyze temporary files.

        Returns:
            Analysis of temporary files
        """
        logger.info("Analyzing temporary files...")

        temp_patterns = [
            "**/*.tmp",
            "**/*.cache",
            "**/*.swp",
            "**/*.bak",
            "**/*~",
            "**/.DS_Store",
            "**/Thumbs.db"
        ]

        temp_files = []
        total_size = 0

        for pattern in temp_patterns:
            try:
                for temp_file in self.project_root.glob(pattern):
                    if temp_file.is_file():
                        temp_files.append(temp_file)
                        try:
                            total_size += temp_file.stat().st_size
                        except OSError:
                            pass
            except Exception as e:
                logger.warning(f"Error analyzing {pattern}: {e}")

        return {
            "category": "temporary_files",
            "total_files": len(temp_files),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "recommendation": "Safe to delete - temporary files",
            "estimated_savings_files": len(temp_files),
            "estimated_savings_mb": round(total_size / (1024 * 1024), 2)
        }

    def analyze_all(self) -> Dict[str, Any]:
        """
        Analyze all cleanup categories.

        Returns:
            Complete analysis
        """
        logger.info("Starting comprehensive spring cleaning analysis...")

        # Analyze each category
        try:
            self.analysis["categories"]["config_backups"] = self.analyze_config_backups()
        except Exception as e:
            logger.error(f"Error analyzing config backups: {e}")
            self.analysis["categories"]["config_backups"] = {"error": str(e)}

        try:
            self.analysis["categories"]["old_sessions"] = self.analyze_old_sessions()
        except Exception as e:
            logger.error(f"Error analyzing old sessions: {e}")
            self.analysis["categories"]["old_sessions"] = {"error": str(e)}

        try:
            self.analysis["categories"]["extension_data"] = self.analyze_extension_data()
        except Exception as e:
            logger.error(f"Error analyzing extension data: {e}")
            self.analysis["categories"]["extension_data"] = {"error": str(e)}

        try:
            self.analysis["categories"]["old_analytics"] = self.analyze_old_analytics()
        except Exception as e:
            logger.error(f"Error analyzing old analytics: {e}")
            self.analysis["categories"]["old_analytics"] = {"error": str(e)}

        try:
            self.analysis["categories"]["temporary_files"] = self.analyze_temporary_files()
        except Exception as e:
            logger.error(f"Error analyzing temporary files: {e}")
            self.analysis["categories"]["temporary_files"] = {"error": str(e)}

        # Generate summary
        total_files = sum(
            cat.get("estimated_savings_files", 0)
            for cat in self.analysis["categories"].values()
            if isinstance(cat, dict) and "estimated_savings_files" in cat
        )

        total_size_mb = sum(
            cat.get("estimated_savings_mb", 0)
            for cat in self.analysis["categories"].values()
            if isinstance(cat, dict) and "estimated_savings_mb" in cat
        )

        self.analysis["summary"] = {
            "total_categories": len(self.analysis["categories"]),
            "estimated_files_to_remove": total_files,
            "estimated_size_savings_mb": round(total_size_mb, 2),
            "estimated_size_savings_gb": round(total_size_mb / 1024, 2),
            "priority": "HIGH" if total_files > 5000 else "MEDIUM"
        }

        # Generate recommendations
        self.analysis["recommendations"] = [
            cat.get("recommendation", "")
            for cat in self.analysis["categories"].values()
            if isinstance(cat, dict) and "recommendation" in cat
        ]

        return self.analysis

    def print_analysis(self):
        """Print formatted analysis results."""
        print("\n" + "=" * 80)
        print("SPRING CLEANING ANALYSIS - LUMINA")
        print("=" * 80)
        print(f"Analyzed: {self.analysis['analyzed_at']}")
        print()

        summary = self.analysis["summary"]
        print("SUMMARY")
        print("-" * 80)
        print(f"Categories Analyzed: {summary.get('total_categories', 0)}")
        print(f"Estimated Files to Remove: {summary.get('estimated_files_to_remove', 0):,}")
        print(f"Estimated Size Savings: {summary.get('estimated_size_savings_mb', 0):.2f} MB")
        print(f"Estimated Size Savings: {summary.get('estimated_size_savings_gb', 0):.2f} GB")
        print(f"Priority: {summary.get('priority', 'UNKNOWN')}")
        print()

        print("DETAILED BREAKDOWN")
        print("-" * 80)

        for category, data in self.analysis["categories"].items():
            if isinstance(data, dict) and "error" not in data:
                print(f"\n{category.upper().replace('_', ' ')}")
                print(f"  Files: {data.get('total_files', data.get('total_old_files', 0)):,}")
                print(f"  Size: {data.get('total_size_mb', 0):.2f} MB")
                print(f"  Estimated Savings: {data.get('estimated_savings_files', 0):,} files")
                print(f"  Estimated Savings: {data.get('estimated_savings_mb', 0):.2f} MB")
                print(f"  Recommendation: {data.get('recommendation', 'N/A')}")

        print()
        print("=" * 80)
        print()

        print("RECOMMENDATIONS")
        print("-" * 80)
        for i, rec in enumerate(self.analysis["recommendations"], 1):
            if rec:
                print(f"{i}. {rec}")
        print()


def main():
    try:
        """Main function to run analysis."""
        script_path = Path(__file__).resolve()
        project_root = script_path.parent.parent.parent

        print("🧹 Starting Spring Cleaning Analysis...")
        print("   (This is SAFE - only analyzes, never deletes)")
        print()

        analyzer = SpringCleaningAnalyzer(project_root)
        analysis = analyzer.analyze_all()

        analyzer.print_analysis()

        # Save analysis
        output_path = project_root / "data" / "time_tracking" / f"spring_cleaning_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)

        print(f"💾 Analysis saved to: {output_path}")
        print()
        print("NEXT STEPS:")
        print("1. Review the analysis above")
        print("2. Check the saved JSON file for details")
        print("3. Plan cleanup based on recommendations")
        print("4. Use spring_cleaning_executor.py for safe cleanup")
        print()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()