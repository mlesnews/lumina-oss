#!/usr/bin/env python3
"""
Force Keyboard Lighting ON
Aggressively enables keyboard backlight using multiple methods
"""

import sys
import subprocess
import time
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ForceKeyboardLighting")


def set_registry_brightness():
    """Set keyboard brightness via registry with all possible keys"""
    logger.info("Setting registry brightness values...")

    script = """
$paths = @(
    'HKCU:\\Software\\ASUS\\ArmouryDevice\\Aura',
    'HKCU:\\Software\\ASUS\\Aura',
    'HKLM:\\SOFTWARE\\ASUS\\ArmouryDevice\\Aura',
    'HKLM:\\SOFTWARE\\ASUS\\Aura',
    'HKCU:\\Software\\ASUS\\ROG',
    'HKLM:\\SOFTWARE\\ASUS\\ROG'
)

$values = @{
    'Brightness' = 100
    'BacklightBrightness' = 100
    'KeyboardBrightness' = 100
    'LightingBrightness' = 100
    'KeyBrightness' = 100
    'Enable' = 1
    'Enabled' = 1
    'LightingEnabled' = 1
    'BacklightEnabled' = 1
    'KeyboardEnabled' = 1
    'State' = 1
    'On' = 1
}

$updated = 0
foreach ($path in $paths) {
    try {
        if (-not (Test-Path $path)) {
            New-Item -Path $path -Force -ErrorAction SilentlyContinue | Out-Null
        }
        if (Test-Path $path) {
            foreach ($key in $values.Keys) {
                Set-ItemProperty -Path $path -Name $key -Value $values[$key] -Type DWord -ErrorAction SilentlyContinue
            }
            $updated++
        }
    } catch {}
}

Write-Output "Updated $updated paths"
"""

    result = subprocess.run(
        ["powershell", "-Command", script],
        capture_output=True,
        text=True,
        timeout=30
    )

    if result.returncode == 0:
        logger.info(f"✅ Registry updated: {result.stdout.strip()}")
        return True
    else:
        logger.warning(f"⚠️  Registry update: {result.stderr}")
        return False


def press_fn_f4_multiple_times(count=10):
    """Press fn+F4 multiple times to cycle keyboard lighting"""
    logger.info(f"Pressing fn+F4 {count} times to cycle keyboard lighting...")

    try:
        import pyautogui
        pyautogui.FAILSAFE = False

        for i in range(count):
            logger.info(f"  Press {i+1}/{count}...")
            pyautogui.hotkey('fn', 'f4')
            time.sleep(0.8)  # Wait between presses

        logger.info("✅ fn+F4 simulation completed")
        return True
    except ImportError:
        logger.error("❌ PyAutoGUI not available")
        return False
    except Exception as e:
        logger.error(f"❌ fn+F4 simulation failed: {e}")
        return False


def try_windows_brightness_api():
    """Try using Windows brightness API"""
    logger.info("Attempting Windows brightness API...")

    try:
        import ctypes
        from ctypes import wintypes

        # Try to set keyboard brightness via Windows API
        # This is a fallback method
        logger.info("  Windows API method (experimental)")
        return False
    except Exception as e:
        logger.warning(f"  Windows API not available: {e}")
        return False


def main():
    """Main execution"""
    logger.info("=" * 70)
    logger.info("FORCE KEYBOARD LIGHTING ON")
    logger.info("=" * 70)
    logger.info("")

    results = {
        "registry": False,
        "fn_f4": False,
        "windows_api": False
    }

    # Method 1: Registry
    logger.info("METHOD 1: Registry settings...")
    results["registry"] = set_registry_brightness()
    time.sleep(1)

    # Method 2: fn+F4 simulation
    logger.info("")
    logger.info("METHOD 2: fn+F4 key simulation...")
    results["fn_f4"] = press_fn_f4_multiple_times(count=10)
    time.sleep(1)

    # Method 3: Windows API (if available)
    logger.info("")
    logger.info("METHOD 3: Windows API...")
    results["windows_api"] = try_windows_brightness_api()

    # Summary
    logger.info("")
    logger.info("=" * 70)
    logger.info("SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Registry: {'✅' if results['registry'] else '❌'}")
    logger.info(f"fn+F4: {'✅' if results['fn_f4'] else '❌'}")
    logger.info(f"Windows API: {'✅' if results['windows_api'] else '❌'}")
    logger.info("")
    logger.info("If keyboard is still black:")
    logger.info("  1. Check Armoury Crate is running")
    logger.info("  2. Manually press fn+F4 on keyboard")
    logger.info("  3. Check Armoury Crate settings > Lighting")
    logger.info("=" * 70)

    return 0 if any(results.values()) else 1


if __name__ == "__main__":


    sys.exit(main())