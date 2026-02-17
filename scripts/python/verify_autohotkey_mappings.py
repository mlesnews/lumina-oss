#!/usr/bin/env python3
"""
Verify AutoHotkey Mappings Are Active
Quick verification that RALT and F23 remappings are working

Tags: #AUTOHOTKEY #VERIFY #KEYBOARD
"""

import subprocess
import sys
from pathlib import Path

print("=" * 80)
print("🔍 VERIFYING AUTOHOTKEY MAPPINGS")
print("=" * 80)
print()

# Check AutoHotkey is running
print("📋 Step 1: Checking AutoHotkey process...")
try:
    result = subprocess.run(
        ['powershell', '-Command', 'Get-Process | Where-Object {$_.ProcessName -like "*AutoHotkey*"} | Select-Object ProcessName, Id'],
        capture_output=True,
        text=True,
        timeout=5
    )

    if "AutoHotkey" in result.stdout:
        print("   ✅ AutoHotkey is RUNNING")
        for line in result.stdout.strip().split('\n'):
            if 'AutoHotkey' in line and 'ProcessName' not in line:
                print(f"      {line.strip()}")
    else:
        print("   ❌ AutoHotkey is NOT running")
        print("   Run: scripts\\powershell\\start_autohotkey.ps1")
        sys.exit(1)
except Exception as e:
    print(f"   ⚠️  Error: {e}")
    sys.exit(1)

print()

# Check which script is running
print("📋 Step 2: Checking active script...")
try:
    result = subprocess.run(
        ['powershell', '-Command', 'Get-WmiObject Win32_Process | Where-Object {$_.Name -like "*AutoHotkey*"} | Select-Object CommandLine | Format-List'],
        capture_output=True,
        text=True,
        timeout=5
    )

    if result.stdout and '.ahk' in result.stdout:
        for line in result.stdout.split('\n'):
            if '.ahk' in line:
                script_path = line.strip()
                print(f"   ✅ Script: {script_path}")
                if 'left_alt_doit_fixed' in script_path:
                    print("      ✅ Using correct script with RALT and F23 mappings")
except Exception as e:
    print(f"   ⚠️  Error: {e}")

print()

# Check Windows Copilot registry
print("📋 Step 3: Checking Windows Copilot key status...")
try:
    result = subprocess.run(
        ['powershell', '-Command', 'Get-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" -Name "DisableCopilot" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty DisableCopilot'],
        capture_output=True,
        text=True,
        timeout=5
    )

    if result.stdout.strip() == "1":
        print("   ✅ Windows Copilot key is DISABLED (registry)")
    elif result.stdout.strip() == "0":
        print("   ⚠️  Windows Copilot key is ENABLED (may interfere)")
        print("   Run: scripts\\powershell\\disable_windows_copilot_key.ps1")
    else:
        print("   ⚠️  Copilot registry key not set")
        print("   Run: scripts\\powershell\\disable_windows_copilot_key.ps1")
except Exception as e:
    print(f"   ⚠️  Could not check registry: {e}")

print()

# Summary
print("=" * 80)
print("📊 VERIFICATION SUMMARY")
print("=" * 80)
print()
print("Expected Mappings:")
print("   • RIGHT ALT → @doit + Enter")
print("   • COPILOT KEY (F23) → Voice Input (Ctrl+Shift+Space)")
print()
print("🧪 Test Instructions:")
print("   1. Press RIGHT ALT - should type '@doit' and send message")
print("   2. Press COPILOT KEY (F23) - should activate voice input")
print()
print("⚠️  If mappings don't work:")
print("   • Windows may still be intercepting Copilot key")
print("   • Try signing out/in or restarting")
print("   • Check Windows Settings → Personalization → Taskbar")
print("   • Disable Copilot in Windows Settings")
print()
print("=" * 80)
