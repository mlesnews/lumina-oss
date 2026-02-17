#!/usr/bin/env python3
"""
BIOS Settings Reader
Read Fan RPM Settings from BIOS

Attempts to read BIOS fan settings for comparison with measured values.
Performance tuning and stress testing integration.

Tags: #BIOS #FAN-SETTINGS #PERFORMANCE-TUNING
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("BIOSSettingsReader")


class BIOSSettingsReader:
    """
    BIOS Settings Reader

    Reads fan RPM settings from BIOS for comparison with measured values.
    """

    def __init__(self, project_root: Path):
        """Initialize BIOS Settings Reader"""
        self.project_root = project_root
        self.logger = logger

        # Data paths
        self.data_path = project_root / "data"
        self.bios_path = self.data_path / "bios_settings"
        self.bios_path.mkdir(parents=True, exist_ok=True)

        # Settings file
        self.settings_file = self.bios_path / "bios_fan_settings.json"

        self.logger.info("⚙️  BIOS Settings Reader initialized")
        self.logger.info("   Reading: Fan RPM settings from BIOS")
        self.logger.info("   Purpose: Performance tuning comparison")

    def read_bios_fan_settings(self) -> Dict[str, Any]:
        """
        Read fan RPM settings from BIOS

        Attempts multiple methods to read BIOS settings.
        """
        self.logger.info("⚙️  Reading BIOS fan settings...")

        settings = {
            "timestamp": datetime.now().isoformat(),
            "cpu_fan_rpm": None,
            "case_fan_rpm": None,
            "gpu_fan_rpm": None,
            "fan_curves": {},
            "performance_mode": None,
            "methods_attempted": [],
            "status": "attempting"
        }

        # Method 1: WMI - System BIOS
        try:
            result = subprocess.run(
                ["wmic", "bios", "get", "Version,Manufacturer"],
                capture_output=True,
                text=True,
                timeout=5
            )
            settings["methods_attempted"].append("wmi_bios")

            if result.returncode == 0:
                settings["bios_info"] = result.stdout.strip()
                self.logger.info("   BIOS info retrieved via WMI")
        except Exception as e:
            self.logger.debug(f"   WMI BIOS method: {e}")

        # Method 2: Try to read from registry (Windows)
        try:
            result = subprocess.run(
                ["reg", "query", "HKEY_LOCAL_MACHINE\\HARDWARE\\DESCRIPTION\\System\\BIOS"],
                capture_output=True,
                text=True,
                timeout=5
            )
            settings["methods_attempted"].append("registry")

            if result.returncode == 0:
                settings["bios_registry"] = "available"
                self.logger.info("   BIOS registry data available")
        except Exception as e:
            self.logger.debug(f"   Registry method: {e}")

        # Method 3: Check for manufacturer-specific tools
        # ASUS: AISuite, MSI: Dragon Center, etc.
        manufacturer_tools = {
            "asus": "AISuite",
            "msi": "DragonCenter",
            "gigabyte": "AppCenter",
            "asus_armoury": "ArmouryCrate"
        }

        for mfg, tool in manufacturer_tools.items():
            settings["methods_attempted"].append(f"manufacturer_{mfg}")

        # Note: Actual BIOS fan settings typically require:
        # 1. BIOS/UEFI access during boot
        # 2. Manufacturer-specific software
        # 3. Hardware monitoring tools (OpenHardwareMonitor, HWiNFO, etc.)

        settings["status"] = "requires_manual_input"
        settings["note"] = "BIOS fan settings typically require manual entry or manufacturer software. Framework ready for integration."

        self.logger.info("   BIOS settings framework ready")
        self.logger.info("   Note: Manual entry or manufacturer software may be required")

        return settings

    def save_bios_settings(self, settings: Dict[str, Any]):
        """Save BIOS settings to file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            self.logger.info("✅ BIOS settings saved")
        except Exception as e:
            self.logger.error(f"❌ Error saving BIOS settings: {e}")

    def load_bios_settings(self) -> Dict[str, Any]:
        """Load BIOS settings from file"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"⚠️  Error loading BIOS settings: {e}")

        return {
            "cpu_fan_rpm": None,
            "case_fan_rpm": None,
            "gpu_fan_rpm": None,
            "fan_curves": {},
            "performance_mode": None,
            "note": "BIOS settings not yet configured"
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="BIOS Settings Reader")
        parser.add_argument("--read", action="store_true", help="Read BIOS fan settings")
        parser.add_argument("--set-cpu", type=int, help="Set CPU fan RPM (manual)")
        parser.add_argument("--set-case", type=int, help="Set case fan RPM (manual)")
        parser.add_argument("--set-gpu", type=int, help="Set GPU fan RPM (manual)")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        reader = BIOSSettingsReader(project_root)

        if args.read:
            settings = reader.read_bios_fan_settings()
            reader.save_bios_settings(settings)

            if args.json:
                print(json.dumps(settings, indent=2, default=str))
            else:
                print("⚙️  BIOS Fan Settings:")
                print(f"   CPU Fan: {settings.get('cpu_fan_rpm', 'N/A')} RPM")
                print(f"   Case Fan: {settings.get('case_fan_rpm', 'N/A')} RPM")
                print(f"   GPU Fan: {settings.get('gpu_fan_rpm', 'N/A')} RPM")
                print(f"   Status: {settings.get('status', 'Unknown')}")

        elif args.set_cpu or args.set_case or args.set_gpu:
            settings = reader.load_bios_settings()

            if args.set_cpu:
                settings["cpu_fan_rpm"] = args.set_cpu
            if args.set_case:
                settings["case_fan_rpm"] = args.set_case
            if args.set_gpu:
                settings["gpu_fan_rpm"] = args.set_gpu

            settings["last_updated"] = datetime.now().isoformat()
            settings["source"] = "manual_entry"

            reader.save_bios_settings(settings)

            if args.json:
                print(json.dumps(settings, indent=2, default=str))
            else:
                print("✅ BIOS settings updated")
                print(f"   CPU Fan: {settings.get('cpu_fan_rpm', 'N/A')} RPM")
                print(f"   Case Fan: {settings.get('case_fan_rpm', 'N/A')} RPM")
                print(f"   GPU Fan: {settings.get('gpu_fan_rpm', 'N/A')} RPM")

        else:
            settings = reader.read_bios_fan_settings()
            print("⚙️  BIOS Settings Reader")
            print("   Use --read to attempt reading from system")
            print("   Use --set-cpu/--set-case/--set-gpu to manually configure")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()