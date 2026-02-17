#!/usr/bin/env python3
"""
Apply MANUS Improvements to ASK Stack

Applies all the improvements from MANUS User Control Interface to ASK stack:
- Comprehensive error handling
- Missing docstrings
- Better logging
- Import error handling
- Configuration management
- Task execution patterns

This ensures consistency across all systems.
"""

import os
import sys
import ast
from pathlib import Path
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ApplyMANUSImprovements")

# ASK Stack files to improve
ASK_STACK_FILES = [
    "scripts/python/ask_database_integrated_system.py",
    "scripts/python/ask_database_checks_balances.py",
    "scripts/python/jarvis_fix_ask_database.py",
    "scripts/python/jarvis_restack_all_asks.py",
    "scripts/python/ask_intent_vs_implementation_comparison.py",
]


def apply_improvements():
    try:
        """Apply MANUS improvements to all ASK stack files"""
        from jarvis_roast_manus_control import JARVISRoaster

        roaster = JARVISRoaster()
        results = []

        print("\n" + "="*70)
        print("APPLYING MANUS IMPROVEMENTS TO ASK STACK")
        print("="*70)
        print()

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
                # Show summary
                severity = result.get("severity", {})
                total_issues = len(result['issues'])

                print(f"\n📊 Found {total_issues} issues:")
                print(f"   Critical: {severity.get('critical', 0)}")
                print(f"   High: {severity.get('high', 0)}")
                print(f"   Medium: {severity.get('medium', 0)}")
                print(f"   Low: {severity.get('low', 0)}")

                # Show high/medium issues
                important_issues = [
                    issue for issue in result['issues']
                    if issue.get('severity') in ['critical', 'high', 'medium']
                ]

                if important_issues:
                    print(f"\n⚠️  Important Issues ({len(important_issues)}):")
                    for issue in important_issues[:5]:  # Show first 5
                        print(f"   [{issue['severity'].upper()}] Line {issue['line']}: {issue['type']}")
                        print(f"      {issue['message']}")

                results.append({
                    "file": str(file_path),
                    "total_issues": total_issues,
                    "severity": severity,
                    "important_issues": len(important_issues),
                    "result": result
                })
            else:
                print(f"❌ Error reviewing {file_path.name}: {result.get('error')}")

        # Overall summary
        print(f"\n{'='*70}")
        print("OVERALL SUMMARY")
        print('='*70)

        total_files = len(results)
        total_issues = sum(r["total_issues"] for r in results)
        total_important = sum(r["important_issues"] for r in results)

        print(f"Files Reviewed: {total_files}")
        print(f"Total Issues Found: {total_issues}")
        print(f"Important Issues (Critical/High/Medium): {total_important}")

        if total_important > 0:
            print(f"\n⚠️  {total_important} important issues need attention")
            print("   Review the detailed reports above for fixes")
        else:
            print(f"\n✅ No critical issues found!")

        print("\n" + "="*70)
        print("RECOMMENDATIONS")
        print("="*70)
        print("1. Review all 'medium' and 'high' severity issues")
        print("2. Add error handling where missing")
        print("3. Add docstrings to methods without them")
        print("4. Improve import error handling")
        print("5. Add proper logging to all methods")
        print("="*70)

        return results


    except Exception as e:
        logger.error(f"Error in apply_improvements: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    apply_improvements()

