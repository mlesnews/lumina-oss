#!/usr/bin/env python3
"""
Execute Experimental AutoHotkey Tests
Orchestrates the experimental testing process
"""

import subprocess
import sys
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
autohotkey_dir = project_root / "scripts" / "autohotkey"

print("=" * 70)
print("JARVIS: Executing Experimental Tests")
print("=" * 70)
print("")
print("This will guide you through experimental testing")
print("")

# Check if scripts exist
siphon_script = autohotkey_dir / "siphon_cursor_ide.ahk"
experimental_script = autohotkey_dir / "experimental_live_test.ahk"

if not siphon_script.exists():
    print(f"ERROR: {siphon_script} not found!")
    sys.exit(1)

if not experimental_script.exists():
    print(f"ERROR: {experimental_script} not found!")
    sys.exit(1)

print("✓ Scripts found")
print("")
print("=" * 70)
print("EXECUTION PLAN")
print("=" * 70)
print("")
print("STEP 1: Load Siphon Script")
print("  File: scripts\\autohotkey\\siphon_cursor_ide.ahk")
print("  Action: Load in AutoHotkey")
print("")
print("STEP 2: Prepare Cursor IDE")
print("  - Open Cursor IDE")
print("  - Close chat if open (Ctrl+L to toggle)")
print("  - Have terminal open (to simulate your scenario)")
print("")
print("STEP 3: Execute Tests")
print("  Press F1: Discover keyboard shortcuts")
print("  Press F2: Discover UI elements")
print("  Press F3: Discover focus behavior")
print("  Press F4: Monitor layout changes")
print("  Press F5: Rapid fire (try everything)")
print("  Press F6: Test @doit with all methods")
print("")
print("STEP 4: Review Results")
print("  Check log: logs\\Siphon_CursorIDE_YYYYMMDD.log")
print("  Look for what worked!")
print("")
print("=" * 70)
print("READY TO EXECUTE")
print("=" * 70)
print("")
print("Instructions:")
print("  1. Open AutoHotkey")
print("  2. Load: scripts\\autohotkey\\siphon_cursor_ide.ahk")
print("  3. Open Cursor IDE and prepare as above")
print("  4. Press F1-F6 to run tests")
print("  5. Check log file for results")
print("")
print("Or load: scripts\\autohotkey\\experimental_live_test.ahk")
print("  for more focused testing (F1-F8)")
print("")
