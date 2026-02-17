#!/usr/bin/env python3
"""
JARVIS: Roast & Fix ASK Stack

Applies JARVIS roast & fix to all ASK stack files:
- ask_database_integrated_system.py
- ask_database_checks_balances.py
- ask_intent_vs_implementation_comparison.py
- jarvis_fix_ask_database.py
- jarvis_restack_all_asks.py
- And other ASK-related files
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import logging

# Import the roaster
from jarvis_roast_manus_control import JARVISRoaster

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("JARVIS-ASK-Roast")

# ASK Stack files to review
ASK_STACK_FILES = [
    "scripts/python/ask_database_integrated_system.py",
    "scripts/python/ask_database_checks_balances.py",
    "scripts/python/ask_intent_vs_implementation_comparison.py",
    "scripts/python/jarvis_fix_ask_database.py",
    "scripts/python/jarvis_restack_all_asks.py",
    "scripts/python/collate_unfinished_asks.py",
    "scripts/python/extract_unfinished_asks.py",
    "scripts/python/organize_unfinished_asks.py",
    "scripts/python/session_ask_resolver.py",
    "scripts/python/sub_ask_todo_manager.py",
]


def roast_ask_stack(files: List[str] = None) -> Dict[str, Any]:
    """
    Roast and fix all ASK stack files

    Args:
        files: Optional list of specific files. If None, uses ASK_STACK_FILES

    Returns:
        Dict with results for each file
    """
    files = files or ASK_STACK_FILES

    logger.info(f"🔍 JARVIS reviewing ASK Stack ({len(files)} files)")

    roaster = JARVISRoaster()
    results = {}

    for file_path_str in files:
        file_path = Path(file_path_str)

        if not file_path.exists():
            logger.warning(f"⚠️  File not found: {file_path}")
            results[str(file_path)] = {
                "success": False,
                "error": "File not found"
            }
            continue

        logger.info(f"\n{'='*70}")
        logger.info(f"Reviewing: {file_path.name}")
        logger.info(f"{'='*70}")

        try:
            result = roaster.roast_and_fix(file_path)
            results[str(file_path)] = result

            # Generate report
            report = roaster.generate_report(result)
            print(report)

        except Exception as e:
            logger.error(f"❌ Error reviewing {file_path.name}: {e}")
            results[str(file_path)] = {
                "success": False,
                "error": str(e)
            }

    # Generate summary
    generate_summary(results)

    return results


def generate_summary(results: Dict[str, Any]):
    try:
        """Generate summary of all reviews"""
        print("\n" + "="*70)
        print("ASK STACK ROAST SUMMARY")
        print("="*70)

        total_files = len(results)
        successful = sum(1 for r in results.values() if r.get("success"))
        total_issues = 0
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

        for file_path, result in results.items():
            if result.get("success"):
                issues = result.get("issues", [])
                total_issues += len(issues)

                severity = result.get("severity", {})
                for sev, count in severity.items():
                    severity_counts[sev] = severity_counts.get(sev, 0) + count

        print(f"\nFiles Reviewed: {total_files}")
        print(f"Successful Reviews: {successful}")
        print(f"Total Issues Found: {total_issues}")
        print(f"\nSeverity Breakdown:")
        print(f"  Critical: {severity_counts['critical']}")
        print(f"  High: {severity_counts['high']}")
        print(f"  Medium: {severity_counts['medium']}")
        print(f"  Low: {severity_counts['low']}")

        # Files with most issues
        files_with_issues = [
            (Path(fp).name, len(r.get("issues", [])))
            for fp, r in results.items()
            if r.get("success") and r.get("issues")
        ]
        files_with_issues.sort(key=lambda x: x[1], reverse=True)

        if files_with_issues:
            print(f"\nFiles with Most Issues:")
            for filename, count in files_with_issues[:5]:
                print(f"  {filename}: {count} issues")

        print("\n" + "="*70)


    except Exception as e:
        logger.error(f"Error in generate_summary: {e}", exc_info=True)
        raise
def main():
    try:
        """Main function"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS: Roast & Fix ASK Stack")
        parser.add_argument("--file", type=str, help="Review specific file")
        parser.add_argument("--all", action="store_true", help="Review all ASK stack files")
        parser.add_argument("--list", action="store_true", help="List ASK stack files")

        args = parser.parse_args()

        if args.list:
            print("\nASK Stack Files:")
            for f in ASK_STACK_FILES:
                exists = "✅" if Path(f).exists() else "❌"
                print(f"  {exists} {f}")

        elif args.file:
            # Review single file
            roaster = JARVISRoaster()
            file_path = Path(args.file)
            result = roaster.roast_and_fix(file_path)
            report = roaster.generate_report(result)
            print(report)

        elif args.all:
            # Review all files
            results = roast_ask_stack()

        else:
            parser.print_help()
            print("\nExamples:")
            print("  python jarvis_roast_ask_stack.py --all")
            print("  python jarvis_roast_ask_stack.py --file scripts/python/ask_database_integrated_system.py")
            print("  python jarvis_roast_ask_stack.py --list")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()