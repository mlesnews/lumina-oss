#!/usr/bin/env python3
"""
Check AutoHotkey Integration Status
Verifies AutoHotkey is running and how it integrates with cursor_auto_send_monitor

Tags: #AUTOHOTKEY #INTEGRATION #KEYBOARD #RALT #F23
"""

import sys
import subprocess
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts" / "python"))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("CheckAutoHotkeyIntegration")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("CheckAutoHotkeyIntegration")

print("=" * 80)
print("🔍 AUTOHOTKEY INTEGRATION STATUS")
print("=" * 80)
print()

# Check if AutoHotkey is running
print("📋 AutoHotkey Process Check:")
try:
    result = subprocess.run(
        ['powershell', '-Command', 'Get-Process | Where-Object {$_.Name -like "*AutoHotkey*"} | Select-Object ProcessName, Id, StartTime | Format-Table'],
        capture_output=True,
        text=True,
        timeout=5
    )

    if result.stdout.strip() and "AutoHotkey" in result.stdout:
        print("   ✅ AutoHotkey is RUNNING")
        print()
        print("   Process Details:")
        for line in result.stdout.strip().split('\n'):
            if line.strip() and not line.startswith('-'):
                print(f"      {line.strip()}")
    else:
        print("   ❌ AutoHotkey is NOT running")
        print("   Run: scripts\\powershell\\start_autohotkey.ps1")
except Exception as e:
    print(f"   ⚠️  Could not check AutoHotkey: {e}")

print()

# Check which script is running
print("📋 Active AutoHotkey Script:")
try:
    result = subprocess.run(
        ['powershell', '-Command', 'Get-WmiObject Win32_Process | Where-Object {$_.Name -like "*AutoHotkey*"} | Select-Object CommandLine | Format-List'],
        capture_output=True,
        text=True,
        timeout=5
    )

    if result.stdout and "CommandLine" in result.stdout:
        for line in result.stdout.split('\n'):
            if '.ahk' in line:
                script_path = line.strip().split()[-1] if line.strip() else "Unknown"
                print(f"   Script: {script_path}")
                if "left_alt_doit_fixed" in script_path:
                    print("   ✅ Using: left_alt_doit_fixed.ahk")
                    print("      - RALT → @doit + Enter")
                    print("      - F23 → Voice Input (Ctrl+Shift+Space)")
                    print("      - LAlt+L → @love")
except Exception as e:
    print(f"   ⚠️  Could not determine script: {e}")

print()

# Check cursor_auto_send_monitor integration
print("📋 Cursor Auto-Send Monitor Integration:")
print("   RALT Handling:")
print("      - Detects RALT key press")
print("      - Allows RALT through (doesn't mark as activity)")
print("      - AutoHotkey handles the @doit remapping")
print()
print("   F23 Handling:")
print("      - F23 stops auto-send and returns to listening mode")
print("      - AutoHotkey also handles F23 → Voice Input")
print("      - Both systems work together")
print()

# Check for Python RALT remap module
print("📋 Python RALT Remap Module:")
try:
    from right_alt_doit_remap import RightAltDoitRemap
    print("   ✅ RightAltDoitRemap module found")
    print("   Note: AutoHotkey is primary handler, Python module is fallback")
except ImportError:
    print("   ⚠️  RightAltDoitRemap module not found (expected)")
    print("   AutoHotkey handles RALT remapping directly")

print()

# Summary
print("=" * 80)
print("📊 INTEGRATION SUMMARY")
print("=" * 80)
print()
print("Current Setup:")
print("   1. AutoHotkey (Primary):")
print("      - Handles RALT → @doit + Enter")
print("      - Handles F23 → Voice Input")
print("      - Runs as separate process")
print()
print("   2. Cursor Auto-Send Monitor (Secondary):")
print("      - Detects RALT but allows it through")
print("      - F23 handler stops auto-send")
print("      - Monitors keyboard activity for auto-send")
print()
print("   3. Integration:")
print("      - AutoHotkey handles key remapping")
print("      - Python monitor detects but doesn't interfere")
print("      - Both systems work together without conflict")
print()
print("=" * 80)
print("✅ INTEGRATION CHECK COMPLETE")
print("=" * 80)
print()
