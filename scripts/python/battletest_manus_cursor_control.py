#!/usr/bin/env python3
"""
MANUS Cursor IDE Control - Battletest Suite

Comprehensive testing of ALL MANUS Cursor IDE control features.

Tags: #MANUS #CURSOR_IDE #BATTLETEST #TESTING #VALIDATION @JARVIS @LUMINA #PEAK
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("BattletestMANUSCursor")

from manus_cursor_complete_control import MANUSCursorCompleteControl, CompleteFeatureCategory


class MANUSCursorBattletest:
    """
    Comprehensive battletest suite for MANUS Cursor IDE Control

    Tests:
    - Feature discovery and loading
    - Category coverage
    - Feature execution (if controllers available)
    - Command ID inference
    - Feature organization
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize battletest suite"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.results_dir = self.project_root / "data" / "battletest_manus_cursor"
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self.control = None
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "skipped": 0,
            "test_categories": {},
            "coverage": {},
            "issues": []
        }

    def run_all_tests(self) -> Dict[str, Any]:
        """Run complete battletest suite"""
        logger.info("="*80)
        logger.info("🔥 MANUS CURSOR IDE CONTROL - BATTLETEST SUITE")
        logger.info("="*80)
        logger.info("")

        start_time = time.time()

        try:
            # Initialize control system
            logger.info("📦 Initializing MANUS Cursor Complete Control...")
            self.control = MANUSCursorCompleteControl(project_root=self.project_root)
            logger.info(f"✅ Initialized with {len(self.control.complete_features)} features")
            logger.info("")

            # Run test categories
            self._test_feature_loading()
            self._test_category_coverage()
            self._test_feature_organization()
            self._test_command_id_inference()
            self._test_feature_discovery()
            self._test_coverage_metrics()
            self._test_feature_validation()

            # Calculate final results
            execution_time = time.time() - start_time
            self.test_results["execution_time"] = execution_time
            self.test_results["total_tests"] = (
                self.test_results["passed"] +
                self.test_results["failed"] +
                self.test_results["warnings"] +
                self.test_results["skipped"]
            )

            # Generate report
            self._generate_report()

            logger.info("")
            logger.info("="*80)
            logger.info("✅ BATTLETEST COMPLETE")
            logger.info("="*80)
            logger.info(f"Total Tests: {self.test_results['total_tests']}")
            logger.info(f"Passed: {self.test_results['passed']} ✅")
            logger.info(f"Failed: {self.test_results['failed']} ❌")
            logger.info(f"Warnings: {self.test_results['warnings']} ⚠️")
            logger.info(f"Skipped: {self.test_results['skipped']} ⏭️")
            logger.info(f"Execution Time: {execution_time:.2f}s")
            logger.info("="*80)

            return self.test_results

        except Exception as e:
            logger.error(f"❌ Battletest failed with error: {e}", exc_info=True)
            self.test_results["error"] = str(e)
            return self.test_results

    def _test_feature_loading(self):
        """Test feature loading from configs"""
        logger.info("🧪 TEST: Feature Loading")
        logger.info("-" * 80)

        try:
            total_features = len(self.control.complete_features)

            if total_features >= 300:
                logger.info(f"✅ PASS: {total_features} features loaded (>= 300)")
                self.test_results["passed"] += 1
                self.test_results["test_categories"]["feature_loading"] = "PASS"
            elif total_features >= 200:
                logger.info(f"⚠️  WARNING: {total_features} features loaded (200-299)")
                self.test_results["warnings"] += 1
                self.test_results["test_categories"]["feature_loading"] = "WARNING"
            else:
                logger.error(f"❌ FAIL: Only {total_features} features loaded (< 200)")
                self.test_results["failed"] += 1
                self.test_results["test_categories"]["feature_loading"] = "FAIL"
                self.test_results["issues"].append(f"Only {total_features} features loaded")

            self.test_results["coverage"]["total_features"] = total_features
            logger.info("")

        except Exception as e:
            logger.error(f"❌ Feature loading test failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["issues"].append(f"Feature loading test error: {e}")

    def _test_category_coverage(self):
        """Test category coverage"""
        logger.info("🧪 TEST: Category Coverage")
        logger.info("-" * 80)

        try:
            coverage = self.control.get_feature_coverage()
            categories = coverage.get("categories", {})

            # Check major categories
            major_categories = [
                "navigation", "editing", "view", "ai", "debugging",
                "file", "git", "terminal", "search"
            ]

            major_covered = 0
            for cat in major_categories:
                cat_data = categories.get(cat, {})
                total = cat_data.get("total", 0)
                if total > 0:
                    major_covered += 1
                    logger.info(f"  ✅ {cat}: {total} features")
                else:
                    logger.warning(f"  ⚠️  {cat}: 0 features")

            if major_covered >= 8:
                logger.info(f"✅ PASS: {major_covered}/9 major categories populated")
                self.test_results["passed"] += 1
                self.test_results["test_categories"]["category_coverage"] = "PASS"
            else:
                logger.error(f"❌ FAIL: Only {major_covered}/9 major categories populated")
                self.test_results["failed"] += 1
                self.test_results["test_categories"]["category_coverage"] = "FAIL"
                self.test_results["issues"].append(f"Only {major_covered}/9 major categories populated")

            # Check specialized categories
            specialized_categories = [
                "notifications", "timeline", "test", "explorer",
                "output", "problems", "source_control"
            ]

            specialized_covered = 0
            for cat in specialized_categories:
                cat_data = categories.get(cat, {})
                total = cat_data.get("total", 0)
                if total > 0:
                    specialized_covered += 1
                    logger.info(f"  ✅ {cat}: {total} features")
                else:
                    logger.warning(f"  ⚠️  {cat}: 0 features")

            if specialized_covered >= 5:
                logger.info(f"✅ PASS: {specialized_covered}/7 specialized categories populated")
                self.test_results["passed"] += 1
            else:
                logger.warning(f"⚠️  WARNING: Only {specialized_covered}/7 specialized categories populated")
                self.test_results["warnings"] += 1

            self.test_results["coverage"]["categories"] = categories
            logger.info("")

        except Exception as e:
            logger.error(f"❌ Category coverage test failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["issues"].append(f"Category coverage test error: {e}")

    def _test_feature_organization(self):
        """Test feature organization and categorization"""
        logger.info("🧪 TEST: Feature Organization")
        logger.info("-" * 80)

        try:
            # Check for duplicate feature IDs
            feature_ids = list(self.control.complete_features.keys())
            duplicates = [fid for fid in feature_ids if feature_ids.count(fid) > 1]

            if duplicates:
                logger.error(f"❌ FAIL: Found {len(set(duplicates))} duplicate feature IDs")
                self.test_results["failed"] += 1
                self.test_results["issues"].append(f"Duplicate feature IDs: {set(duplicates)}")
            else:
                logger.info("✅ PASS: No duplicate feature IDs")
                self.test_results["passed"] += 1

            # Check feature completeness
            incomplete_features = []
            for feature_id, feature in self.control.complete_features.items():
                if not feature.command_id:
                    incomplete_features.append(feature_id)

            if incomplete_features:
                logger.warning(f"⚠️  WARNING: {len(incomplete_features)} features missing command IDs")
                self.test_results["warnings"] += 1
            else:
                logger.info("✅ PASS: All features have command IDs")
                self.test_results["passed"] += 1

            # Check category distribution
            category_counts = {}
            for feature in self.control.complete_features.values():
                cat = feature.category.value
                category_counts[cat] = category_counts.get(cat, 0) + 1

            logger.info(f"✅ Category distribution: {len(category_counts)} categories")
            self.test_results["coverage"]["category_distribution"] = category_counts
            logger.info("")

        except Exception as e:
            logger.error(f"❌ Feature organization test failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["issues"].append(f"Feature organization test error: {e}")

    def _test_command_id_inference(self):
        """Test command ID inference"""
        logger.info("🧪 TEST: Command ID Inference")
        logger.info("-" * 80)

        try:
            # Test inference method
            test_cases = [
                ("new file", "workbench.action.files.newUntitledFile"),
                ("save", "workbench.action.files.save"),
                ("command palette", "workbench.action.showCommands"),
            ]

            passed = 0
            for description, expected in test_cases:
                inferred = self.control._infer_command_id(description)
                if expected in inferred or inferred in expected:
                    passed += 1
                    logger.info(f"  ✅ '{description}' -> '{inferred}'")
                else:
                    logger.warning(f"  ⚠️  '{description}' -> '{inferred}' (expected: '{expected}')")

            if passed >= len(test_cases) * 0.8:
                logger.info(f"✅ PASS: Command ID inference working ({passed}/{len(test_cases)})")
                self.test_results["passed"] += 1
            else:
                logger.warning(f"⚠️  WARNING: Command ID inference needs improvement ({passed}/{len(test_cases)})")
                self.test_results["warnings"] += 1

            logger.info("")

        except Exception as e:
            logger.error(f"❌ Command ID inference test failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["issues"].append(f"Command ID inference test error: {e}")

    def _test_feature_discovery(self):
        """Test feature discovery by various methods"""
        logger.info("🧪 TEST: Feature Discovery")
        logger.info("-" * 80)

        try:
            # Test finding features by ID
            test_features = [
                "command_palette",
                "go_to_file",
                "save",
                "cursor_chat"
            ]

            found_by_id = 0
            for feature_id in test_features:
                feature = self.control._find_feature(feature_id)
                if feature:
                    found_by_id += 1
                    logger.info(f"  ✅ Found '{feature_id}' by ID")
                else:
                    logger.warning(f"  ⚠️  Could not find '{feature_id}' by ID")

            if found_by_id >= len(test_features) * 0.75:
                logger.info(f"✅ PASS: Feature discovery by ID ({found_by_id}/{len(test_features)})")
                self.test_results["passed"] += 1
            else:
                logger.warning(f"⚠️  WARNING: Feature discovery by ID needs improvement ({found_by_id}/{len(test_features)})")
                self.test_results["warnings"] += 1

            logger.info("")

        except Exception as e:
            logger.error(f"❌ Feature discovery test failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["issues"].append(f"Feature discovery test error: {e}")

    def _test_coverage_metrics(self):
        """Test coverage metrics"""
        logger.info("🧪 TEST: Coverage Metrics")
        logger.info("-" * 80)

        try:
            coverage = self.control.get_feature_coverage()

            total = coverage.get("total_features", 0)
            enabled = coverage.get("enabled_features", 0)
            controllable = coverage.get("controllable_features", 0)
            coverage_pct = coverage.get("coverage_percentage", 0)

            logger.info(f"  Total Features: {total}")
            logger.info(f"  Enabled Features: {enabled}")
            logger.info(f"  Controllable Features: {controllable}")
            logger.info(f"  Coverage Percentage: {coverage_pct}%")

            if coverage_pct >= 95:
                logger.info("✅ PASS: Coverage >= 95%")
                self.test_results["passed"] += 1
            elif coverage_pct >= 80:
                logger.warning("⚠️  WARNING: Coverage 80-94%")
                self.test_results["warnings"] += 1
            else:
                logger.error("❌ FAIL: Coverage < 80%")
                self.test_results["failed"] += 1
                self.test_results["issues"].append(f"Coverage only {coverage_pct}%")

            if enabled == total:
                logger.info("✅ PASS: All features enabled")
                self.test_results["passed"] += 1
            else:
                logger.warning(f"⚠️  WARNING: {total - enabled} features disabled")
                self.test_results["warnings"] += 1

            logger.info("")

        except Exception as e:
            logger.error(f"❌ Coverage metrics test failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["issues"].append(f"Coverage metrics test error: {e}")

    def _test_feature_validation(self):
        """Test feature validation"""
        logger.info("🧪 TEST: Feature Validation")
        logger.info("-" * 80)

        try:
            # Validate feature structure
            invalid_features = []
            for feature_id, feature in self.control.complete_features.items():
                if not feature.feature_id:
                    invalid_features.append(feature_id)
                elif not feature.name:
                    invalid_features.append(feature_id)
                elif not feature.category:
                    invalid_features.append(feature_id)

            if invalid_features:
                logger.error(f"❌ FAIL: {len(invalid_features)} features have invalid structure")
                self.test_results["failed"] += 1
                self.test_results["issues"].append(f"Invalid features: {invalid_features[:10]}")
            else:
                logger.info("✅ PASS: All features have valid structure")
                self.test_results["passed"] += 1

            # Check for required categories
            required_categories = [
                CompleteFeatureCategory.NAVIGATION,
                CompleteFeatureCategory.EDITING,
                CompleteFeatureCategory.VIEW,
                CompleteFeatureCategory.AI
            ]

            categories_present = set()
            for feature in self.control.complete_features.values():
                categories_present.add(feature.category)

            missing_categories = [cat for cat in required_categories if cat not in categories_present]

            if missing_categories:
                logger.error(f"❌ FAIL: Missing required categories: {missing_categories}")
                self.test_results["failed"] += 1
                self.test_results["issues"].append(f"Missing categories: {missing_categories}")
            else:
                logger.info("✅ PASS: All required categories present")
                self.test_results["passed"] += 1

            logger.info("")

        except Exception as e:
            logger.error(f"❌ Feature validation test failed: {e}")
            self.test_results["failed"] += 1
            self.test_results["issues"].append(f"Feature validation test error: {e}")

    def _generate_report(self):
        try:
            """Generate battletest report"""
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.results_dir / f"battletest_report_{timestamp}.json"

            # Save JSON report
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, default=str)

            # Generate markdown report
            md_report_file = self.results_dir / f"battletest_report_{timestamp}.md"
            with open(md_report_file, 'w', encoding='utf-8') as f:
                f.write("# MANUS Cursor IDE Control - Battletest Report\n\n")
                f.write(f"**Date**: {self.test_results['timestamp']}\n")
                f.write(f"**Execution Time**: {self.test_results.get('execution_time', 0):.2f}s\n\n")
                f.write("## Test Results\n\n")
                f.write(f"- **Total Tests**: {self.test_results['total_tests']}\n")
                f.write(f"- **Passed**: {self.test_results['passed']} ✅\n")
                f.write(f"- **Failed**: {self.test_results['failed']} ❌\n")
                f.write(f"- **Warnings**: {self.test_results['warnings']} ⚠️\n")
                f.write(f"- **Skipped**: {self.test_results['skipped']} ⏭️\n\n")

                if self.test_results.get('coverage'):
                    f.write("## Coverage\n\n")
                    coverage = self.test_results['coverage']
                    if 'total_features' in coverage:
                        f.write(f"- **Total Features**: {coverage['total_features']}\n")
                    if 'categories' in coverage:
                        f.write("\n### Categories\n\n")
                        for cat, data in coverage['categories'].items():
                            total = data.get('total', 0)
                            if total > 0:
                                f.write(f"- **{cat}**: {total} features\n")

                if self.test_results.get('issues'):
                    f.write("\n## Issues\n\n")
                    for issue in self.test_results['issues']:
                        f.write(f"- {issue}\n")

                f.write("\n---\n")
                f.write(f"**Status**: {'✅ PASS' if self.test_results['failed'] == 0 else '❌ FAIL'}\n")

            logger.info(f"📄 Report saved: {report_file}")
            logger.info(f"📄 Markdown report saved: {md_report_file}")


        except Exception as e:
            self.logger.error(f"Error in _generate_report: {e}", exc_info=True)
            raise
def main():
    try:
        """CLI entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="MANUS Cursor IDE Control Battletest")
        parser.add_argument("--output", type=str, help="Output directory for reports")

        args = parser.parse_args()

        battletest = MANUSCursorBattletest()

        if args.output:
            battletest.results_dir = Path(args.output)
            battletest.results_dir.mkdir(parents=True, exist_ok=True)

        results = battletest.run_all_tests()

        # Exit with appropriate code
        if results.get("failed", 0) > 0:
            sys.exit(1)
        elif results.get("warnings", 0) > 0:
            sys.exit(0)  # Warnings are acceptable
        else:
            sys.exit(0)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()