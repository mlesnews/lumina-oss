#!/usr/bin/env python3
"""
Run Tests
Convenience script to run all tests

Usage:
    python scripts/python/run_tests.py
    python scripts/python/run_tests.py --unit
    python scripts/python/run_tests.py --integration
    python scripts/python/run_tests.py --all
"""

import sys
import argparse
import unittest
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(project_root / "scripts" / "python") not in sys.path:
    sys.path.insert(0, str(project_root / "scripts" / "python"))

try:
    from test_runner import TestRunner
    TEST_RUNNER_AVAILABLE = True
except ImportError:
    TEST_RUNNER_AVAILABLE = False


def run_unit_tests():
    """Run unit tests"""
    loader = unittest.TestLoader()
    start_dir = str(project_root / "tests" / "unit")
    suite = loader.discover(start_dir, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


def run_integration_tests():
    """Run integration tests"""
    loader = unittest.TestLoader()
    start_dir = str(project_root / "tests" / "integration")
    suite = loader.discover(start_dir, pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


def run_all_tests():
    """Run all tests using test runner"""
    if TEST_RUNNER_AVAILABLE:
        test_runner = TestRunner(project_root)
        report = test_runner.run_tests()
        return report["status"] == "passed"
    else:
        # Fallback to unittest discovery
        loader = unittest.TestLoader()
        start_dir = str(project_root / "tests")
        suite = loader.discover(start_dir, pattern="test_*.py")
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()


def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="Run JARVIS Master Agent Tests")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests")

    args = parser.parse_args()

    print("=" * 60)
    print("JARVIS Master Agent - Test Runner")
    print("=" * 60)

    if args.unit:
        print("\nRunning unit tests...")
        success = run_unit_tests()
    elif args.integration:
        print("\nRunning integration tests...")
        success = run_integration_tests()
    else:
        print("\nRunning all tests...")
        success = run_all_tests()

    print("=" * 60)
    sys.exit(0 if success else 1)


if __name__ == "__main__":


    main()