#!/usr/bin/env python3
"""
Setup UI Automation for Armoury Crate
Installs required packages for UI automation
"""

import subprocess
import sys

def install_packages():
    """Install UI automation packages"""
    packages = ["pyautogui", "pygetwindow", "Pillow"]

    print("=" * 70)
    print("🔧 SETTING UP UI AUTOMATION FOR ARMOURY CRATE")
    print("=" * 70)
    print()
    print("Installing required packages...")
    print()

    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False

    print()
    print("=" * 70)
    print("✅ UI AUTOMATION SETUP COMPLETE!")
    print("=" * 70)
    print()
    print("You can now use:")
    print("  - 'disable_all_lighting_ui' action for full UI automation")
    print("  - 'disable_all_lighting' action for service-based automation")
    print()

    return True

if __name__ == "__main__":
    success = install_packages()
    sys.exit(0 if success else 1)
