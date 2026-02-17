#!/usr/bin/env python3
"""
Remap Voice Input Button to Caps Lock
Maps the default voice input trigger to Caps Lock key
"""

import sys
import subprocess
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("Remap Voice Input Button to Caps Lock")
print("=" * 70)
print()

# Windows voice input default key is usually Windows Key + H
# We'll remap Caps Lock to trigger voice input

print("CURRENT SETUP:")
print("  Default voice input: Windows Key + H")
print("  Target: Caps Lock → Voice Input")
print()

# Method 1: Using PowerShell to remap via registry (Scancode Map)
print("METHOD 1: Registry-based remapping (Scancode Map)")
print("-" * 70)

# Caps Lock scan code: 0x003A (58 decimal)
# We need to map it to Windows Key + H
# But Scancode Map is complex - better to use a tool

ps_script = """
# Check current Caps Lock state
$capsLock = [Console]::CapsLock
Write-Host "Current Caps Lock state: $capsLock"

# Note: Direct registry remapping requires admin and is complex
# Recommendation: Use PowerToys or SharpKeys for reliable remapping
Write-Host ""
Write-Host "RECOMMENDATION: Use one of these methods:"
Write-Host "  1. PowerToys Keyboard Manager (Recommended)"
Write-Host "  2. SharpKeys (Simple registry-based)"
Write-Host "  3. AutoHotkey script (Most flexible)"
"""

result = subprocess.run(
    ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
    capture_output=True,
    text=True,
    timeout=10
)
print(result.stdout)

print()
print("=" * 70)
print("RECOMMENDATIONS")
print("=" * 70)
print()

recommendations = [
    "1. POWERTOYS KEYBOARD MANAGER (BEST OPTION)",
    "   - Download: https://aka.ms/PowerToysSetup",
    "   - Install PowerToys",
    "   - Open Keyboard Manager",
    "   - Remap: Caps Lock → Windows Key + H",
    "   - Pros: Easy, reliable, reversible",
    "   - Cons: Requires PowerToys installation",
    "",
    "2. SHARPKEYS (SIMPLE REGISTRY-BASED)",
    "   - Download: https://github.com/randyrants/sharpkeys",
    "   - Run SharpKeys",
    "   - Add: Caps Lock → Windows Key",
    "   - Then use Windows Key + H for voice input",
    "   - Pros: Lightweight, registry-based",
    "   - Cons: Less flexible",
    "",
    "3. AUTOHOTKEY SCRIPT (MOST FLEXIBLE)",
    "   - Download: https://www.autohotkey.com/",
    "   - Create script: Caps Lock → Send Windows Key + H",
    "   - Pros: Very flexible, can add conditions",
    "   - Cons: Requires AutoHotkey runtime",
    "",
    "4. REGISTRY DIRECT (ADVANCED)",
    "   - Modify: HKLM\\SYSTEM\\CurrentControlSet\\Control\\Keyboard Layout",
    "   - Use Scancode Map (complex, requires admin)",
    "   - Pros: System-level, no extra software",
    "   - Cons: Complex, risky if done wrong"
]

for rec in recommendations:
    print(rec)

print()
print("=" * 70)
print("QUICK AUTOHOTKEY SOLUTION")
print("=" * 70)
print()

autohotkey_script = """
; Remap Caps Lock to Voice Input (Windows Key + H)
; Save as: remap_capslock_to_voice.ahk

; Disable Caps Lock default behavior
SetCapsLockState, AlwaysOff

; Map Caps Lock to Windows Key + H (Voice Input)
CapsLock::
    Send, {LWin down}h{LWin up}
return

; Optional: Keep original Caps Lock with Shift + Caps Lock
+CapsLock::
    SetCapsLockState, % GetKeyState("CapsLock", "T") ? "Off" : "On"
return
"""

print("AutoHotkey Script:")
print("-" * 70)
print(autohotkey_script)
print("-" * 70)
print()

# Save AutoHotkey script
autohotkey_file = project_root / "scripts" / "autohotkey" / "remap_capslock_to_voice.ahk"
autohotkey_file.parent.mkdir(parents=True, exist_ok=True)
autohotkey_file.write_text(autohotkey_script.strip())

print(f"✅ AutoHotkey script saved to: {autohotkey_file}")
print()
print("To use:")
print("  1. Install AutoHotkey: https://www.autohotkey.com/")
print(f"  2. Run: {autohotkey_file}")
print("  3. Caps Lock will now trigger voice input")
print()

print("=" * 70)
print("POWERTOYS QUICK SETUP (RECOMMENDED)")
print("=" * 70)
print()
print("If you have PowerToys installed:")
print("  1. Open PowerToys Settings")
print("  2. Go to Keyboard Manager")
print("  3. Click 'Remap a key'")
print("  4. Map: Caps Lock → Windows Key + H")
print("  5. Save")
print()

print("=" * 70)
