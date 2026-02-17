#!/usr/bin/env python3
"""
Test MANUS Cursor IDE Feature Execution

Tests the execution of Cursor IDE features via MANUS control.

Tags: #MANUS #CURSOR_IDE #TESTING #EXECUTION @JARVIS @LUMINA #PEAK
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, List

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("TestMANUSCursorExecution")

from manus_cursor_complete_control import MANUSCursorCompleteControl


def test_feature_execution(test_features: List[str]) -> Dict[str, Any]:
    """
    Test execution of specific features

    Args:
        test_features: List of feature IDs or names to test

    Returns:
        Test results
    """
    results = {
        "total_tests": len(test_features),
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "results": []
    }

    try:
        control = MANUSCursorCompleteControl()

        for feature_id in test_features:
            test_result = {
                "feature_id": feature_id,
                "status": "unknown",
                "error": None,
                "execution_time": None
            }

            try:
                # Find feature
                feature = None
                for feat in control.complete_features.values():
                    if feat.feature_id == feature_id or feature_id.lower() in feat.name.lower():
                        feature = feat
                        break

                if not feature:
                    test_result["status"] = "skipped"
                    test_result["error"] = "Feature not found"
                    results["skipped"] += 1
                    results["results"].append(test_result)
                    continue

                # Execute feature
                start_time = time.time()
                execution_result = control.execute_feature(
                    feature_id=feature.feature_id,
                    parameters=None
                )
                execution_time = time.time() - start_time

                test_result["execution_time"] = execution_time

                if execution_result.get("success"):
                    test_result["status"] = "passed"
                    results["passed"] += 1
                else:
                    test_result["status"] = "failed"
                    test_result["error"] = execution_result.get("error", "Unknown error")
                    results["failed"] += 1

            except Exception as e:
                test_result["status"] = "failed"
                test_result["error"] = str(e)
                results["failed"] += 1
                logger.error(f"Error testing feature '{feature_id}': {e}", exc_info=True)

            results["results"].append(test_result)

        return results

    except Exception as e:
        logger.error(f"Error in test execution: {e}", exc_info=True)
        return {
            "total_tests": len(test_features),
            "passed": 0,
            "failed": 1,
            "skipped": 0,
            "error": str(e),
            "results": []
        }


def test_basic_features() -> Dict[str, Any]:
    """Test basic commonly-used features"""
    basic_features = [
        "command_palette",
        "go_to_file",
        "save",
        "find",
        "toggle_sidebar",
        "toggle_terminal"
    ]

    logger.info("Testing basic features...")
    return test_feature_execution(basic_features)


def test_ai_features() -> Dict[str, Any]:
    """Test AI-related features"""
    ai_features = [
        "cursor_chat",
        "cursor_composer",
        "inline_edit"
    ]

    logger.info("Testing AI features...")
    return test_feature_execution(ai_features)


def test_navigation_features() -> Dict[str, Any]:
    """Test navigation features"""
    nav_features = [
        "go_to_definition",
        "go_to_symbol",
        "go_to_line"
    ]

    logger.info("Testing navigation features...")
    return test_feature_execution(nav_features)


def main():
    try:
        """CLI entry point"""
        import argparse
        import json

        parser = argparse.ArgumentParser(description="Test MANUS Cursor IDE Feature Execution")
        parser.add_argument("--basic", action="store_true", help="Test basic features")
        parser.add_argument("--ai", action="store_true", help="Test AI features")
        parser.add_argument("--navigation", action="store_true", help="Test navigation features")
        parser.add_argument("--features", nargs="+", help="Test specific features")
        parser.add_argument("--all", action="store_true", help="Test all feature categories")

        args = parser.parse_args()

        print("\n" + "="*80)
        print("🧪 MANUS Cursor IDE Feature Execution Tests")
        print("="*80 + "\n")

        all_results = {}

        if args.all or (not args.basic and not args.ai and not args.navigation and not args.features):
            # Test all categories
            all_results["basic"] = test_basic_features()
            all_results["ai"] = test_ai_features()
            all_results["navigation"] = test_navigation_features()
        else:
            if args.basic:
                all_results["basic"] = test_basic_features()
            if args.ai:
                all_results["ai"] = test_ai_features()
            if args.navigation:
                all_results["navigation"] = test_navigation_features()
            if args.features:
                all_results["custom"] = test_feature_execution(args.features)

        # Print summary
        print("\n" + "="*80)
        print("📊 Test Results Summary")
        print("="*80 + "\n")

        total_passed = 0
        total_failed = 0
        total_skipped = 0

        for category, results in all_results.items():
            print(f"{category.upper()}:")
            print(f"  Passed: {results.get('passed', 0)}")
            print(f"  Failed: {results.get('failed', 0)}")
            print(f"  Skipped: {results.get('skipped', 0)}")
            print()

            total_passed += results.get("passed", 0)
            total_failed += results.get("failed", 0)
            total_skipped += results.get("skipped", 0)

        print("="*80)
        print(f"TOTAL: Passed: {total_passed} | Failed: {total_failed} | Skipped: {total_skipped}")
        print("="*80 + "\n")

        # Print detailed results
        if args.all or len(all_results) > 1:
            print("\n" + "="*80)
            print("📋 Detailed Results")
            print("="*80 + "\n")
            print(json.dumps(all_results, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()