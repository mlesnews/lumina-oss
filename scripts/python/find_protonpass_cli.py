#!/usr/bin/env python3
"""Find ProtonPass CLI installation"""
import subprocess
import os
from pathlib import Path

print("🔍 Searching for ProtonPass CLI...")

# Common locations
locations = [
    Path(r"C:\Users\mlesn\AppData\Local\Programs\ProtonPass\pass-cli.exe"),
    Path(r"C:\Program Files\ProtonPass\pass-cli.exe"),
    Path(os.path.expanduser("~/.protonpass/pass-cli.exe")),
    Path(os.path.expanduser("~/AppData/Local/ProtonPass/pass-cli.exe")),
    Path(os.path.expanduser("~/AppData/Roaming/ProtonPass/pass-cli.exe")),
]

# Check each location
for loc in locations:
    if loc.exists():
        print(f"✅ Found: {loc}")
        # Test it
        try:
            result = subprocess.run([str(loc), "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"   Version: {result.stdout.strip()}")
                print(f"   ✅ Working!")
                break
        except:
            print(f"   ⚠️  Found but may not be working")
    else:
        print(f"❌ Not found: {loc}")

# Try in PATH
print("\n🔍 Checking PATH...")
try:
    result = subprocess.run(["protonpass", "--version"], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        print(f"✅ Found in PATH: protonpass")
        print(f"   Version: {result.stdout.strip()}")
except:
    print("❌ Not in PATH")

# Try alternative names
for cmd in ["ppass", "pass", "proton-pass"]:
    try:
        result = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Found as '{cmd}': {result.stdout.strip()}")
    except:
        pass

print("\n💡 If not found, ProtonPass CLI may be:")
print("   - Installed via browser extension (not accessible via CLI)")
print("   - Installed in a custom location")
print("   - Need to be installed: https://github.com/ProtonPass/protonpass-cli")
