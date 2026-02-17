#!/usr/bin/env python3
"""
Test AutoHotkey Key Remapping
Quick test to verify RALT and F23 are being captured

Tags: #AUTOHOTKEY #TEST #KEYBOARD
"""

import time
import subprocess
from pathlib import Path

print("=" * 80)
print("🧪 AUTOHOTKEY KEY REMAPPING TEST")
print("=" * 80)
print()
print("This script will check if AutoHotkey is running and capturing keys.")
print()
print("Instructions:")
print("   1. Press RIGHT ALT key - should send @doit + Enter")
print("   2. Press COPILOT KEY (F23) - should activate voice input")
print("   3. Check if remappings are working")
print()
print("Checking AutoHotkey status...")
print()

# Check if AutoHotkey is running
try:
    result = subprocess.run(
        ['powershell', '-Command', 'Get-Process | Where-Object {$_.Name -like "*AutoHotkey*"} | Select-Object ProcessName, Id'],
        capture_output=True,
        text=True,
        timeout=5
    )

    if "AutoHotkey" in result.stdout:
        print("✅ AutoHotkey is RUNNING")
        print()
        print("Active Script:")
        result2 = subprocess.run(
            ['powershell', '-Command', 'Get-WmiObject Win32_Process | Where-Object {$_.Name -like "*AutoHotkey*"} | Select-Object CommandLine | Format-List'],
            capture_output=True,
            text=True,
            timeout=5
        )
        for line in result2.stdout.split('\n'):
            if '.ahk' in line:
                print(f"   {line.strip()}")
    else:
        print("❌ AutoHotkey is NOT running")
        print("   Run: scripts\\powershell\\start_autohotkey.ps1")
except Exception as e:
    print(f"⚠️  Error checking AutoHotkey: {e}")

print()
print("=" * 80)
print("📋 TESTING INSTRUCTIONS")
print("=" * 80)
print()
print("1. RIGHT ALT KEY TEST:")
print("   - Press RIGHT ALT key")
print("   - Expected: Should type '@doit' and press Enter in Cursor chat")
print("   - If it doesn't work: AutoHotkey may not be capturing RALT")
print()
print("2. COPILOT KEY (F23) TEST:")
print("   - Press the COPILOT key (to the right of PRTSC)")
print("   - Expected: Should activate Cursor voice input (Ctrl+Shift+Space)")
print("   - If it doesn't work: AutoHotkey may not be capturing F23")
print()
print("3. If keys revert to OEM functions:")
print("   - Another program may be intercepting keys first")
print("   - Windows may be handling keys at a lower level")
print("   - AutoHotkey script may need to be reloaded")
print()
print("=" * 80)
print("Press RIGHT ALT or COPILOT key now to test...")
print("=" * 80)
print()

# Wait a bit for user to test
time.sleep(5)

print()
print("✅ Test complete. Check if remappings worked above.")
print()
