#!/usr/bin/env python3
"""
Apply JARVIS Fixes to ASK Stack

Applies all the improvements from MANUS User Control Interface to ASK stack:
- Comprehensive error handling
- Missing docstrings
- Better logging
- Import error handling
"""

import os
import sys
from pathlib import Path
from typing import List
import logging
logger = logging.getLogger("apply_jarvis_fixes_to_ask_stack")


# ASK Stack files to fix
ASK_STACK_FILES = [
    "scripts/python/ask_database_integrated_system.py",
    "scripts/python/ask_database_checks_balances.py",
    "scripts/python/jarvis_fix_ask_database.py",
    "scripts/python/marvin_roast_ask_database.py",
]

def apply_jarvis_fixes():
    try:
        """Apply JARVIS fixes to all ASK stack files"""
        from jarvis_roast_manus_control import JARVISRoaster

        roaster = JARVISRoaster()
        results = []

        for file_path_str in ASK_STACK_FILES:
            file_path = Path(file_path_str)

            if not file_path.exists():
                print(f"⚠️  File not found: {file_path}")
                continue

            print(f"\n{'='*70}")
            print(f"Reviewing: {file_path.name}")
            print('='*70)

            result = roaster.roast_and_fix(file_path)

            if result["success"]:
                report = roaster.generate_report(result)
                print(report)
                results.append(result)

                # Show summary
                severity = result.get("severity", {})
                print(f"\n📊 Summary:")
                print(f"   Total Issues: {len(result['issues'])}")
                print(f"   Critical: {severity.get('critical', 0)}")
                print(f"   High: {severity.get('high', 0)}")
                print(f"   Medium: {severity.get('medium', 0)}")
                print(f"   Low: {severity.get('low', 0)}")
            else:
                print(f"❌ Error reviewing {file_path.name}: {result.get('error')}")

        # Overall summary
        print(f"\n{'='*70}")
        print("OVERALL SUMMARY")
        print('='*70)
        total_issues = sum(len(r["issues"]) for r in results)
        total_files = len(results)

        print(f"Files Reviewed: {total_files}")
        print(f"Total Issues Found: {total_issues}")

        return results


    except Exception as e:
        logger.error(f"Error in apply_jarvis_fixes: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    apply_jarvis_fixes()

