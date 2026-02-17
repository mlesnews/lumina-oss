#!/usr/bin/env python3
"""
JARVIS Fix Screen Brightness
Fixes laptop screen dimming/brightening by disabling auto-brightness and setting to light mode.

Tags: #DISPLAY #BRIGHTNESS #POWER #WINDOWS @AUTO
"""

import sys
import subprocess
from pathlib import Path
from typing import Dict, Any
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISFixScreenBrightness")


class ScreenBrightnessFixer:
    """
    Fixes screen brightness issues on Windows.
    """

    def __init__(self):
        self.logger = logger
        self.logger.info("✅ Screen Brightness Fixer initialized")

    def disable_auto_brightness(self) -> bool:
        """Disable Windows auto-brightness"""
        try:
            # Disable adaptive brightness via powercfg
            self.logger.info("🔧 Disabling adaptive brightness...")

            # Get active power scheme
            result = subprocess.run(
                ["powercfg", "/getactivescheme"],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode != 0:
                self.logger.warning("⚠️  Could not get active power scheme")
                return False

            # Extract GUID from output (format: Power Scheme GUID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx  (Name))
            output = result.stdout
            guid = None
            for line in output.split('\n'):
                if 'Power Scheme GUID:' in line:
                    parts = line.split('Power Scheme GUID:')
                    if len(parts) > 1:
                        guid = parts[1].strip().split()[0]
                        break

            if not guid:
                self.logger.warning("⚠️  Could not extract power scheme GUID")
                return False

            # Disable adaptive brightness for both AC and DC
            # GUID for display brightness: 7516b95f-f776-4464-8c53-06167f40cc99
            # SubGUID for adaptive brightness: f1fbfde2-a960-4165-8131-a70c2980a89a

            commands = [
                # AC power (plugged in)
                ["powercfg", "/setacvalueindex", guid, 
                 "7516b95f-f776-4464-8c53-06167f40cc99", 
                 "f1fbfde2-a960-4165-8131-a70c2980a89a", "0"],
                # DC power (battery)
                ["powercfg", "/setdcvalueindex", guid,
                 "7516b95f-f776-4464-8c53-06167f40cc99",
                 "f1fbfde2-a960-4165-8131-a70c2980a89a", "0"]
            ]

            for cmd in commands:
                result = subprocess.run(cmd, capture_output=True, text=True, check=False)
                if result.returncode != 0:
                    self.logger.warning(f"⚠️  Failed to set brightness setting: {result.stderr}")

            # Apply the changes
            subprocess.run(["powercfg", "/setactive", guid], check=False)

            self.logger.info("✅ Adaptive brightness disabled")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to disable auto-brightness: {e}", exc_info=True)
            return False

    def set_brightness_level(self, level: int = 80) -> bool:
        """Set brightness to specific level (0-100)"""
        try:
            if not (0 <= level <= 100):
                self.logger.warning(f"⚠️  Invalid brightness level: {level} (must be 0-100)")
                return False

            self.logger.info(f"🔧 Setting brightness to {level}%...")

            # Use PowerShell to set brightness
            ps_script = f"""
            (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {level})
            """

            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                self.logger.info(f"✅ Brightness set to {level}%")
                return True
            else:
                self.logger.warning(f"⚠️  Failed to set brightness: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Failed to set brightness: {e}", exc_info=True)
            return False

    def set_light_mode(self) -> bool:
        """Set Windows to light mode (daytime mode)"""
        try:
            self.logger.info("🔧 Setting Windows to light mode...")

            # Set Windows theme to light mode via registry
            # HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize
            # SystemUsesLightTheme = 1 (light mode)
            # AppsUseLightTheme = 1 (light mode)

            ps_script = """
            Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" -Name "SystemUsesLightTheme" -Value 1 -Type DWord
            Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" -Name "AppsUseLightTheme" -Value 1 -Type DWord
            """

            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                self.logger.info("✅ Windows set to light mode")
                return True
            else:
                self.logger.warning(f"⚠️  Failed to set light mode: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Failed to set light mode: {e}", exc_info=True)
            return False

    def fix_all(self, brightness_level: int = 80) -> Dict[str, Any]:
        """Fix all brightness and display issues"""
        self.logger.info("="*80)
        self.logger.info("FIXING SCREEN BRIGHTNESS AND DISPLAY")
        self.logger.info("="*80)

        results = {
            "auto_brightness_disabled": False,
            "brightness_set": False,
            "light_mode_set": False
        }

        # Disable auto-brightness
        results["auto_brightness_disabled"] = self.disable_auto_brightness()

        # Set brightness level
        results["brightness_set"] = self.set_brightness_level(brightness_level)

        # Set light mode
        results["light_mode_set"] = self.set_light_mode()

        success = all(results.values())

        if success:
            self.logger.info("✅ All display settings fixed")
        else:
            self.logger.warning("⚠️  Some settings may not have been applied")

        return {
            "success": success,
            "results": results
        }


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Fix screen brightness and display settings")
    parser.add_argument("--disable-auto", action="store_true", help="Disable auto-brightness")
    parser.add_argument("--set-brightness", type=int, help="Set brightness level (0-100)")
    parser.add_argument("--light-mode", action="store_true", help="Set Windows to light mode")
    parser.add_argument("--fix-all", action="store_true", help="Fix all display issues")
    parser.add_argument("--brightness", type=int, default=80, help="Brightness level for --fix-all (default: 80)")

    args = parser.parse_args()

    fixer = ScreenBrightnessFixer()

    if args.disable_auto:
        fixer.disable_auto_brightness()
    elif args.set_brightness is not None:
        fixer.set_brightness_level(args.set_brightness)
    elif args.light_mode:
        fixer.set_light_mode()
    elif args.fix_all:
        result = fixer.fix_all(args.brightness)
        print(f"Success: {result['success']}")
        print(f"Results: {result['results']}")
    else:
        parser.print_help()


if __name__ == "__main__":


    main()