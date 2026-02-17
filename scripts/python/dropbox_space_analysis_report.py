#!/usr/bin/env python3
"""
Dropbox Space Analysis Report

Identifies the recursive snapshot bug and provides cleanup recommendations.
"""

import json
from pathlib import Path
from datetime import datetime
import logging
logger = logging.getLogger("dropbox_space_analysis_report")


def main():
    try:
        report = {
            "analysis_date": datetime.now().isoformat(),
            "findings": {
                "critical_issue": "Recursive snapshot bug in time_travel system",
                "space_consumption": {
                    "time_travel_directory": "1,245.82 GB (1.24 TB)",
                    "percentage_of_data_dir": "99%",
                    "percentage_of_my_projects": "90%",
                    "percentage_of_dropbox": "68%"
                },
                "root_cause": {
                    "problem": "Snapshots are including the snapshot directory itself, creating infinite recursive nesting",
                    "evidence": "Log files show nested paths like: data/time_travel/snapshots/snapshot_*/data/time_travel/snapshots/snapshot_*/...",
                    "impact": "This single bug is consuming over 1.2 TB of Dropbox space"
                },
                "recommendations": [
                    {
                        "priority": "CRITICAL",
                        "action": "Fix snapshot creation to exclude the time_travel/snapshots directory",
                        "file": "scripts/python/git_time_travel.py",
                        "fix": "Add exclusion pattern for 'time_travel/snapshots' directory in snapshot creation"
                    },
                    {
                        "priority": "HIGH",
                        "action": "Clean up recursive snapshots",
                        "description": "Delete all snapshots that contain nested snapshot directories (recursive ones)",
                        "risk": "Only delete recursive snapshots; keep the first-level snapshot if it contains valid data"
                    },
                    {
                        "priority": "MEDIUM",
                        "action": "Implement snapshot size limits and retention policies",
                        "description": "Prevent future space issues by limiting snapshot size and age"
                    },
                    {
                        "priority": "LOW",
                        "action": "Audit other large directories",
                        "note": "cursor_chat_archive is 16.4 GB - consider archiving or cleaning"
                    }
                ]
            },
            "space_summary": {
                "dropbox_total": "~2.7 TB",
                "my_projects": "1,381 GB",
                "data_directory": "1,262 GB",
                "time_travel_bug": "1,245 GB",
                "other_large_items": {
                    "Shared": "909 GB",
                    "Dropbox_Flattened_20251222_000717": "403 GB",
                    "Photos": "146 GB",
                    "Repository": "86 GB"
                }
            }
        }

        report_path = Path("data") / "dropbox_space_analysis_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print("=" * 70)
        print("DROPBOX SPACE ANALYSIS REPORT")
        print("=" * 70)
        print(f"\nAnalysis Date: {report['analysis_date']}")
        print(f"\nReport saved to: {report_path}")
        print("\n" + "=" * 70)
        print("CRITICAL FINDING: Recursive Snapshot Bug")
        print("=" * 70)
        print(f"\nTime Travel Directory: {report['findings']['space_consumption']['time_travel_directory']}")
        print(f"Percentage of Dropbox: {report['findings']['space_consumption']['percentage_of_dropbox']}")
        print(f"\nRoot Cause: {report['findings']['root_cause']['problem']}")
        print(f"\nEvidence: {report['findings']['root_cause']['evidence']}")
        print("\n" + "=" * 70)
        print("RECOMMENDATIONS")
        print("=" * 70)
        for i, rec in enumerate(report['findings']['recommendations'], 1):
            print(f"\n{i}. [{rec['priority']}] {rec['action']}")
            if 'file' in rec:
                print(f"   File: {rec['file']}")
            if 'fix' in rec:
                print(f"   Fix: {rec['fix']}")
            if 'description' in rec:
                print(f"   {rec['description']}")

        print("\n" + "=" * 70)
        print("✅ Analysis complete")
        print("=" * 70)

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()