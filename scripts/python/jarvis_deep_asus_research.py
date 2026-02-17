#!/usr/bin/env python3
"""
JARVIS: Deep ASUS Research - Find Official Sources
Research ASUS ROG Strix SCAR 18 G835LX to restore OEM functionality

@JARVIS @ASUS @RESEARCH @OEM @LIGHTING @FUNCTION_KEYS
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVIS_ASUS_Research")


class JARVISDeepASUSResearch:
    """
    Deep research on ASUS ROG Strix SCAR 18 G835LX
    Find what changed from OEM working state
    """

    def __init__(self):
        self.project_root = project_root
        self.model = "ROG Strix SCAR 18 G835LX"
        self.manufacturer = "ASUS"
        self.research_data: Dict[str, Any] = {
            "model": self.model,
            "manufacturer": self.manufacturer,
            "timestamp": datetime.now().isoformat(),
            "findings": []
        }
        logger.info("🔍 JARVIS: Deep ASUS Research Initialized")

    def check_system_info(self) -> Dict[str, Any]:
        """Get detailed system information"""
        logger.info("📋 Gathering System Information...")

        info = {}

        # BIOS Info
        try:
            ps_command = """
            $bios = Get-WmiObject -Class Win32_BIOS -ErrorAction SilentlyContinue;
            $system = Get-WmiObject -Class Win32_ComputerSystem -ErrorAction SilentlyContinue;
            $os = Get-WmiObject -Class Win32_OperatingSystem -ErrorAction SilentlyContinue;
            @{
                BIOS_Manufacturer = $bios.Manufacturer;
                BIOS_Version = $bios.Version;
                BIOS_ReleaseDate = $bios.ReleaseDate;
                System_Manufacturer = $system.Manufacturer;
                System_Model = $system.Model;
                System_SKU = $system.SystemSKUNumber;
                OS_Version = $os.Version;
                OS_Build = $os.BuildNumber
            } | ConvertTo-Json
            """

            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.stdout:
                import json as json_lib
                info = json_lib.loads(result.stdout)
        except Exception as e:
            logger.error(f"Error getting system info: {e}")

        # Installed ASUS Software
        try:
            ps_command = """
            $asusSoftware = @();
            $paths = @('C:\\Program Files\\ASUS', 'C:\\Program Files (x86)\\ASUS');
            foreach ($path in $paths) {
                if (Test-Path $path) {
                    $dirs = Get-ChildItem -Path $path -Directory -ErrorAction SilentlyContinue;
                    foreach ($dir in $dirs) {
                        $exe = Get-ChildItem -Path $dir.FullName -Filter '*.exe' -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1;
                        if ($exe) {
                            $version = (Get-ItemProperty -Path $exe.FullName -ErrorAction SilentlyContinue).VersionInfo;
                            $asusSoftware += @{
                                Name = $dir.Name;
                                Path = $dir.FullName;
                                Exe = $exe.FullName;
                                Version = $version.FileVersion
                            }
                        }
                    }
                }
            }
            $asusSoftware | ConvertTo-Json
            """

            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=15
            )

            if result.stdout:
                import json as json_lib
                info["asus_software"] = json_lib.loads(result.stdout)
        except Exception as e:
            logger.error(f"Error getting ASUS software: {e}")

        # Registry - All ASUS entries
        try:
            ps_command = """
            $regPaths = @(
                'HKCU:\\Software\\ASUS',
                'HKLM:\\SOFTWARE\\ASUS',
                'HKLM:\\SYSTEM\\CurrentControlSet\\Services'
            );
            $asusReg = @();
            foreach ($path in $regPaths) {
                if (Test-Path $path) {
                    $keys = Get-ChildItem -Path $path -Recurse -ErrorAction SilentlyContinue | Select-Object -First 20;
                    foreach ($key in $keys) {
                        $props = Get-ItemProperty -Path $key.PSPath -ErrorAction SilentlyContinue;
                        $fnKeys = $props | Get-Member -MemberType NoteProperty | Where-Object {
                            $_.Name -like '*FN*' -or $_.Name -like '*Function*' -or 
                            $_.Name -like '*Light*' -or $_.Name -like '*Hotkey*' -or
                            $_.Name -like '*Lock*'
                        };
                        if ($fnKeys) {
                            $asusReg += @{
                                Path = $key.PSPath;
                                Keys = ($fnKeys | ForEach-Object { $_.Name })
                            }
                        }
                    }
                }
            }
            $asusReg | ConvertTo-Json
            """

            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=20
            )

            if result.stdout:
                import json as json_lib
                info["asus_registry"] = json_lib.loads(result.stdout)
        except Exception as e:
            logger.error(f"Error getting ASUS registry: {e}")

        self.research_data["system_info"] = info
        return info

    def check_armoury_crate_state(self) -> Dict[str, Any]:
        """Check current Armoury Crate installation and state"""
        logger.info("🔍 Checking Armoury Crate State...")

        state = {}

        # Check if installed
        try:
            ps_command = """
            $armouryPaths = @(
                'C:\\Program Files\\ASUS\\ARMOURY CRATE Service',
                'C:\\Program Files (x86)\\ASUS\\ARMOURY CRATE Service',
                '$env:LOCALAPPDATA\\Programs\\ASUS\\ARMOURY CRATE'
            );
            $found = $false;
            $version = '';
            foreach ($path in $armouryPaths) {
                $expanded = [System.Environment]::ExpandEnvironmentVariables($path);
                if (Test-Path $expanded) {
                    $exe = Get-ChildItem -Path $expanded -Filter 'ArmouryCrate.exe' -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1;
                    if ($exe) {
                        $found = $true;
                        $version = (Get-ItemProperty -Path $exe.FullName -ErrorAction SilentlyContinue).VersionInfo.FileVersion;
                        Write-Host "Found:$expanded|$version"
                        break;
                    }
                }
            }
            if (-not $found) {
                Write-Host "NotFound"
            }
            """

            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=15
            )

            if "Found:" in result.stdout:
                parts = result.stdout.split("|")
                state["installed"] = True
                state["path"] = parts[0].replace("Found:", "")
                state["version"] = parts[1] if len(parts) > 1 else "Unknown"
            else:
                state["installed"] = False
        except Exception as e:
            logger.error(f"Error checking Armoury Crate: {e}")

        # Check service state
        try:
            ps_command = """
            $svc = Get-Service -Name 'ArmouryCrateService' -ErrorAction SilentlyContinue;
            if ($svc) {
                "$($svc.Status)|$($svc.StartType)|$($svc.DisplayName)"
            } else {
                "ServiceNotFound"
            }
            """

            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=5
            )

            if "ServiceNotFound" not in result.stdout:
                parts = result.stdout.split("|")
                state["service"] = {
                    "status": parts[0],
                    "start_type": parts[1],
                    "display_name": parts[2] if len(parts) > 2 else ""
                }
        except Exception as e:
            logger.error(f"Error checking service: {e}")

        self.research_data["armoury_crate"] = state
        return state

    def generate_research_report(self) -> Dict[str, Any]:
        """Generate comprehensive research report"""
        logger.info("📊 Generating Research Report...")

        # Gather all data
        system_info = self.check_system_info()
        armoury_state = self.check_armoury_crate_state()

        # Research URLs and sources
        research_sources = {
            "official_support": [
                f"https://www.asus.com/support/Download-Center/",
                f"https://www.asus.com/support/FAQ/{self.model.replace(' ', '-')}",
                "https://www.asus.com/support/FAQ/1048368/",  # Function Key FAQ
            ],
            "documentation": [
                "https://www.asus.com/support/FAQ/1048368/",  # Function Key Behavior
                "https://www.asus.com/support/FAQ/1048369/",  # Armoury Crate
            ],
            "model_specific": [
                f"https://www.asus.com/laptops/for-gaming/rog-strix/rog-strix-scar-18-g835/helpdesk_download/",
            ]
        }

        self.research_data["research_sources"] = research_sources
        self.research_data["recommendations"] = [
            "1. Visit ASUS Support: https://www.asus.com/support/",
            f"2. Download latest drivers for {self.model}",
            "3. Download latest Armoury Crate from ASUS",
            "4. Check BIOS version and update if needed",
            "5. Review ASUS Function Key FAQ: https://www.asus.com/support/FAQ/1048368/",
            "6. Check if ASUS ATK Package is installed (required for function keys)",
            "7. Verify all ASUS services are running",
            "8. Check Windows Update for ASUS driver updates"
        ]

        return self.research_data

    def save_report(self) -> Path:
        try:
            """Save research report"""
            data_dir = self.project_root / "data" / "asus_research"
            data_dir.mkdir(parents=True, exist_ok=True)

            filename = data_dir / f"asus_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.research_data, f, indent=2, default=str)

            logger.info(f"✅ Report saved: {filename}")
            return filename


        except Exception as e:
            self.logger.error(f"Error in save_report: {e}", exc_info=True)
            raise
def main():
    """Main execution"""
    print("=" * 70)
    print("🔍 JARVIS: DEEP ASUS RESEARCH")
    print("   Finding Official Sources to Restore OEM Functionality")
    print("=" * 70)
    print()

    researcher = JARVISDeepASUSResearch()
    report = researcher.generate_research_report()
    filename = researcher.save_report()

    print()
    print("=" * 70)
    print("📊 RESEARCH SUMMARY")
    print("=" * 70)
    print()

    if "system_info" in report:
        sys_info = report["system_info"]
        if "System_Model" in sys_info:
            print(f"Model: {sys_info.get('System_Model', 'Unknown')}")
        if "BIOS_Version" in sys_info:
            print(f"BIOS Version: {sys_info.get('BIOS_Version', 'Unknown')}")
        if "asus_software" in sys_info:
            print(f"ASUS Software Installed: {len(sys_info['asus_software'])} packages")

    if "armoury_crate" in report:
        ac = report["armoury_crate"]
        print(f"Armoury Crate Installed: {ac.get('installed', False)}")
        if ac.get("version"):
            print(f"Armoury Crate Version: {ac['version']}")

    print()
    print("🔗 OFFICIAL ASUS SOURCES:")
    if "research_sources" in report:
        for category, urls in report["research_sources"].items():
            print(f"\n{category.replace('_', ' ').title()}:")
            for url in urls:
                print(f"  • {url}")

    print()
    print("💡 RECOMMENDATIONS:")
    if "recommendations" in report:
        for rec in report["recommendations"]:
            print(f"  {rec}")

    print()
    print(f"✅ Full report: {filename}")
    print("=" * 70)


if __name__ == "__main__":


    main()