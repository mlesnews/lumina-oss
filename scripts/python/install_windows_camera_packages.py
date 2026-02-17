#!/usr/bin/env python3
"""
Install Windows Camera API Packages

Installs required packages for accessing ASUS IR camera via Windows APIs.

Tags: #INSTALL #WINDOWS #CAMERA #IR_CAMERA @JARVIS @LUMINA
"""

import sys
import subprocess
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

print("=" * 80)
print("📦 INSTALLING WINDOWS CAMERA API PACKAGES")
print("=" * 80)
print()

packages = [
    "winrt-runtime",  # Core WinRT runtime
    "winrt-Windows.Media.Capture",  # MediaCapture API
    "winrt-Windows.Media.Capture.Frames",  # Frame-level capture (for IR)
]

print("Packages to install:")
for pkg in packages:
    print(f"  • {pkg}")
print()

for pkg in packages:
    print(f"Installing {pkg}...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", pkg],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            print(f"  ✅ {pkg} installed successfully")
        else:
            print(f"  ⚠️  {pkg} installation had issues:")
            print(f"     {result.stderr[:200]}")
    except subprocess.TimeoutExpired:
        print(f"  ⚠️  {pkg} installation timed out")
    except Exception as e:
        print(f"  ❌ Error installing {pkg}: {e}")
    print()

print("=" * 80)
print("INSTALLATION COMPLETE")
print("=" * 80)
print()
print("Next steps:")
print("  1. Test IR camera access: python scripts/python/windows_ir_camera_access.py")
print("  2. If successful, integrate into camera system")
print()
print("=" * 80)
