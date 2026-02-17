#!/usr/bin/env python3
"""
Test Runner
Runs all test suites and generates test reports
"""

import sys
import json
import unittest
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(project_root / "scripts" / "python") not in sys.path:
    sys.path.insert(0, str(project_root / "scripts" / "python"))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("TestRunner")


class TestRunner:
    """Runs all test suites"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.test_results_dir = self.project_root / "data" / "test_results"
        self.test_results_dir.mkdir(parents=True, exist_ok=True)

    def discover_tests(self) -> unittest.TestSuite:
        """Discover all tests"""
        loader = unittest.TestLoader()
        start_dir = str(self.project_root / "tests")
        suite = loader.discover(start_dir, pattern="test_*.py")
        return suite

    def run_tests(self) -> Dict[str, Any]:
        try:
            """Run all tests and generate report"""
            print("=" * 60)
            print("JARVIS Master Agent - Test Runner")
            print("=" * 60)

            suite = self.discover_tests()

            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)

            # Generate test report
            report = {
                "test_run_date": datetime.now().isoformat(),
                "tests_run": result.testsRun,
                "tests_passed": result.testsRun - len(result.failures) - len(result.errors),
                "tests_failed": len(result.failures),
                "tests_errored": len(result.errors),
                "tests_skipped": len(result.skipped) if hasattr(result, 'skipped') else 0,
                "success_rate": (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun if result.testsRun > 0 else 0,
                "failures": [
                    {
                        "test": str(f[0]),
                        "error": str(f[1])
                    }
                    for f in result.failures
                ],
                "errors": [
                    {
                        "test": str(e[0]),
                        "error": str(e[1])
                    }
                    for e in result.errors
                ],
                "status": "passed" if result.wasSuccessful() else "failed"
            }

            # Save report
            report_file = self.test_results_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)

            print("\n" + "=" * 60)
            print("Test Results Summary")
            print("=" * 60)
            print(f"Tests Run: {report['tests_run']}")
            print(f"Tests Passed: {report['tests_passed']}")
            print(f"Tests Failed: {report['tests_failed']}")
            print(f"Tests Errored: {report['tests_errored']}")
            print(f"Success Rate: {report['success_rate']:.2%}")
            print(f"Status: {report['status'].upper()}")
            print(f"\nReport saved to: {report_file}")
            print("=" * 60)

            return report


        except Exception as e:
            self.logger.error(f"Error in run_tests: {e}", exc_info=True)
            raise
def main():
    try:
        """Main test runner function"""
        project_root = Path(__file__).parent.parent.parent
        test_runner = TestRunner(project_root)
        report = test_runner.run_tests()

        sys.exit(0 if report["status"] == "passed" else 1)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    from typing import Optional


    main()