#!/usr/bin/env python3
"""
Run Chat Focus Tests and Compare Results
Executes diagnostic tool, test script, then compares results
Optionally runs through Syphon for pattern analysis
"""

import subprocess
import sys
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

print("=" * 60)
print("Chat Focus Testing & Comparison")
print("=" * 60)
print("")
print("This script will:")
print("  1. Guide you to run the AutoHotkey diagnostic tool")
print("  2. Guide you to run the test script")
print("  3. Compare the results")
print("  4. Optionally run through Syphon for analysis")
print("")
print("=" * 60)
print("")

# Step 1: Instructions for diagnostic tool
print("STEP 1: Run AutoHotkey Diagnostic Tool")
print("-" * 60)
print("1. Open Cursor IDE")
print("2. Open a terminal (to simulate your scenario)")
print("3. Load: scripts\\autohotkey\\chat_focus_diagnostic.ahk")
print("4. Press F1 to run diagnostic")
print("5. Wait for it to complete")
print("")
input("Press Enter when diagnostic is complete...")
print("")

# Step 2: Instructions for test script
print("STEP 2: Run Test Script")
print("-" * 60)
print("1. Make sure Cursor IDE is in the same state")
print("2. Load: scripts\\autohotkey\\left_alt_doit_TEST.ahk")
print("3. Press RAlt (quick press)")
print("4. Observe what happens")
print("")
input("Press Enter when test is complete...")
print("")

# Step 3: Run comparison
print("STEP 3: Comparing Results")
print("-" * 60)
print("Running comparison tool...")
print("")

try:
    result = subprocess.run(
        [sys.executable, str(script_dir / "compare_chat_focus_results.py")],
        cwd=str(project_root),
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)

except Exception as e:
    print(f"Error running comparison: {e}")
    print("")
    print("You can manually run:")
    print(f"  python {script_dir / 'compare_chat_focus_results.py'}")

print("")
print("=" * 60)
print("Testing Complete!")
print("=" * 60)
print("")
print("Next steps:")
print("  1. Review the comparison results above")
print("  2. Check the JSON output file in logs/")
print("  3. Use the recommendations to fix the script")
print("")
