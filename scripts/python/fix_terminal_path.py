#!/usr/bin/env python3
"""
Quick Fix Script for Terminal PATH Issues

This script helps fix invalid PATH entries that may cause terminal issues.
"""

import os
import sys
from pathlib import Path

def clean_path_environment():
    """Clean invalid PATH entries."""
    current_path = os.environ.get("PATH", "")
    path_entries = current_path.split(os.pathsep)

    valid_entries = []
    invalid_entries = []

    for entry in path_entries:
        if entry:
            if os.path.exists(entry):
                valid_entries.append(entry)
            else:
                invalid_entries.append(entry)

    print("PATH Environment Variable Cleanup")
    print("=" * 60)
    print(f"\nTotal PATH entries: {len(path_entries)}")
    print(f"Valid entries: {len(valid_entries)}")
    print(f"Invalid entries: {len(invalid_entries)}")

    if invalid_entries:
        print("\n⚠️  Invalid PATH entries found:")
        for entry in invalid_entries:
            print(f"  - {entry}")

        print("\n📝 To fix these manually:")
        print("1. Open System Properties → Environment Variables")
        print("2. Edit PATH variable (User or System)")
        print("3. Remove the invalid entries listed above")
        print("\nOr use PowerShell (run as Administrator):")
        print("  [Environment]::SetEnvironmentVariable('PATH', $newPath, 'User')")
    else:
        print("\n✓ No invalid PATH entries found!")

    return invalid_entries

if __name__ == "__main__":
    invalid = clean_path_environment()
    sys.exit(0 if not invalid else 1)
