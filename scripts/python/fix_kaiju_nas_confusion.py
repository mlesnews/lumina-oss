#!/usr/bin/env python3
"""
Fix KAIJU/NAS Confusion Script

This script identifies and fixes incorrect references where KAIJU (Desktop PC at <NAS_IP>)
is confused with the NAS (DS2118+ at <NAS_PRIMARY_IP>).

KAIJU Number Eight = Desktop PC at <NAS_IP> (Ollama endpoint)
NAS (DS2118+) = Storage server at <NAS_PRIMARY_IP> (NOT for Ollama)

Tags: #FIX #KAIJU #NAS #SYSTEM_DEFINITIONS
@JARVIS @LUMINA
"""

import re
from pathlib import Path
from typing import List, Tuple, Dict
import sys
import logging
logger = logging.getLogger("fix_kaiju_nas_confusion")


PROJECT_ROOT = Path(__file__).parent.parent.parent


def find_incorrect_references(root: Path) -> List[Tuple[Path, int, str]]:
    """
    Find files with incorrect KAIJU references pointing to .32 instead of .11.

    Returns list of (file_path, line_number, line_content) tuples.
    """
    issues = []

    # Patterns to find incorrect references
    patterns = [
        (r'10\.17\.17\.32.*11434.*[Kk][Aa][Ii][Jj][Uu]', 'KAIJU endpoint using .32 (should be .11)'),
        (r'[Kk][Aa][Ii][Jj][Uu].*10\.17\.17\.32.*11434', 'KAIJU endpoint using .32 (should be .11)'),
        (r'[Kk][Aa][Ii][Jj][Uu].*[Nn][Aa][Ss]', 'KAIJU incorrectly described as NAS'),
        (r'[Nn][Aa][Ss].*[Kk][Aa][Ii][Jj][Uu]', 'NAS incorrectly described as KAIJU'),
        (r'KAIJU.*NAS|NAS.*KAIJU', 'KAIJU/NAS confusion'),
    ]

    # Search Python scripts
    for py_file in root.rglob("*.py"):
        if "venv" in str(py_file) or "__pycache__" in str(py_file):
            continue

        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    for pattern, description in patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            issues.append((py_file, line_num, line.strip(), description))
        except Exception as e:
            print(f"⚠️  Error reading {py_file}: {e}")

    return issues


def generate_report(issues: List[Tuple[Path, int, str, str]]) -> str:
    """Generate a report of all issues found."""
    report = []
    report.append("=" * 80)
    report.append("KAIJU/NAS Confusion Report")
    report.append("=" * 80)
    report.append(f"\nTotal issues found: {len(issues)}\n")

    # Group by file
    by_file: Dict[Path, List[Tuple[int, str, str]]] = {}
    for file_path, line_num, line, desc in issues:
        if file_path not in by_file:
            by_file[file_path] = []
        by_file[file_path].append((line_num, line, desc))

    for file_path, file_issues in sorted(by_file.items()):
        report.append(f"\n📄 {file_path.relative_to(PROJECT_ROOT)}")
        report.append("-" * 80)
        for line_num, line, desc in file_issues:
            report.append(f"  Line {line_num}: {desc}")
            report.append(f"    {line[:100]}...")

    return "\n".join(report)


def main():
    try:
        """Main function."""
        print("🔍 Scanning for KAIJU/NAS confusion issues...")

        issues = find_incorrect_references(PROJECT_ROOT)

        if not issues:
            print("✅ No issues found!")
            return 0

        # Generate report
        report = generate_report(issues)
        print("\n" + report)

        # Save report
        report_file = PROJECT_ROOT / "docs" / "system" / "KAIJU_NAS_CONFUSION_REPORT.md"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# KAIJU/NAS Confusion Report\n\n")
            f.write(f"Generated: {Path(__file__).stat().st_mtime}\n\n")
            f.write(report)

        print(f"\n📄 Report saved to: {report_file.relative_to(PROJECT_ROOT)}")
        print(f"\n⚠️  Found {len(issues)} potential issues that need manual review.")
        print("   See docs/system/SYSTEM_DEFINITIONS.md for correct system definitions.")

        return 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())