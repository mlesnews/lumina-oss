#!/usr/bin/env python3
"""
#syphon → @grep: Lighting & Function Key Lock Analysis

*** DISABLED - FN KEY TESTING NO LONGER REQUIRED ***
Disabled: 2026-01-21
Reason: FN key testing removed from startup. Lighting controlled via registry only.

Original purpose: Comprehensive analysis of why software fixes aren't working
Status: DISABLED - Script exits immediately

@syphon @grep @lighting @function_key @hardware_level @armoury_crate
@DEPRECATED @DISABLED
"""

import sys

# ============================================================================
# SCRIPT DISABLED - FN KEY TESTING NO LONGER REQUIRED
# ============================================================================
# To re-enable, comment out the following block:
print("=" * 70)
print("SCRIPT DISABLED: syphon_lighting_function_key_analysis.py")
print("FN key testing is no longer required.")
print("Lighting is now controlled via registry settings only.")
print("=" * 70)
sys.exit(0)
# ============================================================================

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

logger = get_logger("SyphonLightingAnalysis")


class SyphonLightingFunctionKeyAnalysis:
    """
    #syphon analysis: Why software fixes aren't working
    Pipes findings to actionable solutions
    """

    def __init__(self):
        self.project_root = project_root
        self.findings: List[Dict[str, Any]] = []
        logger.info("🔍 #syphon → @grep: Lighting & Function Key Analysis")

    def check_function_key_lock_state(self) -> Dict[str, Any]:
        """Check FN key lock state via registry and hardware"""
        logger.info("🔍 Checking Function Key Lock State...")

        finding = {
            "check": "Function Key Lock State",
            "timestamp": datetime.now().isoformat(),
            "methods": []
        }

        # Method 1: Check registry for FN lock
        try:
            ps_command = """
            $regPaths = @(
                'HKCU:\\Keyboard Layout',
                'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Keyboard Layout',
                'HKCU:\\Software\\ASUS',
                'HKLM:\\SOFTWARE\\ASUS'
            );
            $found = @();
            foreach ($path in $regPaths) {
                if (Test-Path $path) {
                    $props = Get-ItemProperty -Path $path -ErrorAction SilentlyContinue;
                    $fnKeys = $props | Get-Member -MemberType NoteProperty | Where-Object {
                        $_.Name -like '*FN*' -or $_.Name -like '*Function*' -or $_.Name -like '*FnLock*'
                    };
                    if ($fnKeys) {
                        foreach ($key in $fnKeys) {
                            $val = $props.$($key.Name);
                            $found += "$path\\$($key.Name)=$val";
                        }
                    }
                }
            }
            if ($found.Count -gt 0) {
                $found -join '|'
            } else {
                'NoFNKeysFound'
            }
            """

            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=10
            )

            if "NoFNKeysFound" not in result.stdout:
                finding["methods"].append({
                    "method": "Registry Check",
                    "status": "Found",
                    "details": result.stdout.strip()
                })
            else:
                finding["methods"].append({
                    "method": "Registry Check",
                    "status": "Not Found",
                    "details": "No FN key registry entries found"
                })
        except Exception as e:
            finding["methods"].append({
                "method": "Registry Check",
                "status": "Error",
                "details": str(e)
            })

        # Method 2: Check BIOS/UEFI settings (via WMI)
        try:
            ps_command = """
            try {
                $bios = Get-WmiObject -Class Win32_BIOS -ErrorAction SilentlyContinue;
                $system = Get-WmiObject -Class Win32_ComputerSystem -ErrorAction SilentlyContinue;
                "$($bios.Manufacturer)|$($bios.Version)|$($system.Manufacturer)|$($system.Model)"
            } catch {
                'BIOSInfoUnavailable'
            }
            """

            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=10
            )

            finding["methods"].append({
                "method": "BIOS/UEFI Info",
                "status": "Found" if "BIOSInfoUnavailable" not in result.stdout else "Unavailable",
                "details": result.stdout.strip()
            })
        except Exception as e:
            finding["methods"].append({
                "method": "BIOS/UEFI Info",
                "status": "Error",
                "details": str(e)
            })

        # Method 3: Check for ASUS-specific FN lock utilities
        try:
            ps_command = """
            $asusUtils = @(
                'C:\\Program Files\\ASUS',
                'C:\\Program Files (x86)\\ASUS',
                'C:\\ProgramData\\ASUS'
            );
            $found = @();
            foreach ($path in $asusUtils) {
                if (Test-Path $path) {
                    $fnUtils = Get-ChildItem -Path $path -Recurse -Filter '*FN*' -ErrorAction SilentlyContinue;
                    $fnUtils += Get-ChildItem -Path $path -Recurse -Filter '*Function*' -ErrorAction SilentlyContinue;
                    if ($fnUtils) {
                        $found += ($fnUtils | Select-Object -First 5 | ForEach-Object { $_.FullName });
                    }
                }
            }
            if ($found.Count -gt 0) {
                $found -join '|'
            } else {
                'NoASUSFNUtils'
            }
            """

            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=15
            )

            if "NoASUSFNUtils" not in result.stdout:
                finding["methods"].append({
                    "method": "ASUS FN Utilities",
                    "status": "Found",
                    "details": result.stdout.strip()
                })
            else:
                finding["methods"].append({
                    "method": "ASUS FN Utilities",
                    "status": "Not Found",
                    "details": "No ASUS FN utilities found"
                })
        except Exception as e:
            finding["methods"].append({
                "method": "ASUS FN Utilities",
                "status": "Error",
                "details": str(e)
            })

        self.findings.append(finding)
        return finding

    def check_armoury_crate_lighting_control(self) -> Dict[str, Any]:
        """Check why Armoury Crate lighting controls aren't working"""
        logger.info("🔍 Checking Armoury Crate Lighting Control...")

        finding = {
            "check": "Armoury Crate Lighting Control",
            "timestamp": datetime.now().isoformat(),
            "methods": []
        }

        # Method 1: Check if Armoury Crate is running
        try:
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq ArmouryCrate.exe"],
                capture_output=True,
                text=True,
                timeout=5
            )

            is_running = "ArmouryCrate.exe" in result.stdout
            finding["methods"].append({
                "method": "Process Check",
                "status": "Running" if is_running else "Not Running",
                "details": f"ArmouryCrate.exe: {'Running' if is_running else 'Not found'}"
            })
        except Exception as e:
            finding["methods"].append({
                "method": "Process Check",
                "status": "Error",
                "details": str(e)
            })

        # Method 2: Check Armoury Crate service status
        try:
            ps_command = """
            $svc = Get-Service -Name 'ArmouryCrateService' -ErrorAction SilentlyContinue;
            if ($svc) {
                "$($svc.Status)|$($svc.StartType)"
            } else {
                'ServiceNotFound'
            }
            """

            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=5
            )

            finding["methods"].append({
                "method": "Service Status",
                "status": "Found" if "ServiceNotFound" not in result.stdout else "Not Found",
                "details": result.stdout.strip()
            })
        except Exception as e:
            finding["methods"].append({
                "method": "Service Status",
                "status": "Error",
                "details": str(e)
            })

        # Method 3: Check Armoury Crate registry settings
        try:
            ps_command = """
            $regPaths = @(
                'HKCU:\\Software\\ASUS\\ArmouryDevice',
                'HKLM:\\SOFTWARE\\ASUS\\ArmouryDevice',
                'HKCU:\\Software\\ASUS\\AURA',
                'HKLM:\\SOFTWARE\\ASUS\\AURA'
            );
            $found = @();
            foreach ($path in $regPaths) {
                if (Test-Path $path) {
                    $props = Get-ItemProperty -Path $path -ErrorAction SilentlyContinue;
                    $lighting = $props | Get-Member -MemberType NoteProperty | Where-Object {
                        $_.Name -like '*Light*' -or $_.Name -like '*Bright*' -or $_.Name -like '*Enable*'
                    };
                    if ($lighting) {
                        foreach ($key in $lighting) {
                            $val = $props.$($key.Name);
                            $found += "$path\\$($key.Name)=$val";
                        }
                    }
                }
            }
            if ($found.Count -gt 0) {
                $found -join '|'
            } else {
                'NoLightingRegKeys'
            }
            """

            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=10
            )

            if "NoLightingRegKeys" not in result.stdout:
                finding["methods"].append({
                    "method": "Registry Settings",
                    "status": "Found",
                    "details": result.stdout.strip()
                })
            else:
                finding["methods"].append({
                    "method": "Registry Settings",
                    "status": "Not Found",
                    "details": "No lighting registry keys found"
                })
        except Exception as e:
            finding["methods"].append({
                "method": "Registry Settings",
                "status": "Error",
                "details": str(e)
            })

        self.findings.append(finding)
        return finding

    def check_hardware_level_control(self) -> Dict[str, Any]:
        """Check if lighting is hardware-controlled vs software-controlled"""
        logger.info("🔍 Checking Hardware-Level Control...")

        finding = {
            "check": "Hardware-Level Control",
            "timestamp": datetime.now().isoformat(),
            "methods": []
        }

        # Method 1: Check for hardware lighting devices
        try:
            ps_command = """
            $devices = Get-PnpDevice -Class 'System' -ErrorAction SilentlyContinue | Where-Object {
                $_.FriendlyName -like '*Light*' -or $_.FriendlyName -like '*RGB*' -or 
                $_.FriendlyName -like '*Aura*' -or $_.FriendlyName -like '*ASUS*Light*'
            };
            if ($devices) {
                $devices | ForEach-Object { "$($_.FriendlyName)|$($_.Status)|$($_.InstanceId)" } | Select-Object -First 10
            } else {
                'NoLightingDevices'
            }
            """

            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=10
            )

            if "NoLightingDevices" not in result.stdout:
                finding["methods"].append({
                    "method": "Hardware Devices",
                    "status": "Found",
                    "details": result.stdout.strip()
                })
            else:
                finding["methods"].append({
                    "method": "Hardware Devices",
                    "status": "Not Found",
                    "details": "No lighting hardware devices found"
                })
        except Exception as e:
            finding["methods"].append({
                "method": "Hardware Devices",
                "status": "Error",
                "details": str(e)
            })

        # Method 2: Check keyboard hardware (for FN key lock)
        try:
            ps_command = """
            $keyboards = Get-PnpDevice -Class 'Keyboard' -ErrorAction SilentlyContinue;
            $asusKeyboards = $keyboards | Where-Object {
                $_.FriendlyName -like '*ASUS*' -or $_.FriendlyName -like '*ROG*'
            };
            if ($asusKeyboards) {
                $asusKeyboards | ForEach-Object { "$($_.FriendlyName)|$($_.Status)" } | Select-Object -First 5
            } else {
                'NoASUSKeyboards'
            }
            """

            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=10
            )

            if "NoASUSKeyboards" not in result.stdout:
                finding["methods"].append({
                    "method": "Keyboard Hardware",
                    "status": "Found",
                    "details": result.stdout.strip()
                })
            else:
                finding["methods"].append({
                    "method": "Keyboard Hardware",
                    "status": "Not Found",
                    "details": "No ASUS keyboard hardware found"
                })
        except Exception as e:
            finding["methods"].append({
                "method": "Keyboard Hardware",
                "status": "Error",
                "details": str(e)
            })

        self.findings.append(finding)
        return finding

    def generate_analysis_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        logger.info("📊 Generating Analysis Report...")

        # Run all checks
        self.check_function_key_lock_state()
        self.check_armoury_crate_lighting_control()
        self.check_hardware_level_control()

        report = {
            "report_id": f"syphon_lighting_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "#syphon → @grep: Lighting & Function Key Analysis",
            "findings": self.findings,
            "conclusions": [],
            "recommendations": []
        }

        # Generate conclusions
        fn_lock_issue = any(
            f["check"] == "Function Key Lock State" and 
            any(m["status"] == "Found" for m in f["methods"])
            for f in self.findings
        )

        armoury_crate_issue = any(
            f["check"] == "Armoury Crate Lighting Control" and
            any(m["status"] in ["Not Running", "Not Found"] for m in f["methods"])
            for f in self.findings
        )

        hardware_control = any(
            f["check"] == "Hardware-Level Control" and
            any(m["status"] == "Found" for m in f["methods"])
            for f in self.findings
        )

        if fn_lock_issue:
            report["conclusions"].append(
                "Function key lock may be preventing hardware-level lighting control"
            )

        if armoury_crate_issue:
            report["conclusions"].append(
                "Armoury Crate service/process may not be running, preventing software control"
            )

        if hardware_control:
            report["conclusions"].append(
                "Lighting appears to be hardware-controlled, requiring BIOS/UEFI or physical controls"
            )

        # Generate recommendations
        report["recommendations"].extend([
            "1. Check BIOS/UEFI settings for FN key lock and lighting control",
            "2. Try Fn+Esc to toggle FN lock (may require multiple attempts)",
            "3. Check if Armoury Crate needs to be reinstalled or updated",
            "4. Verify hardware-level lighting switches in BIOS",
            "5. Check for ASUS-specific keyboard driver updates",
            "6. Try physical keyboard shortcuts: Fn+F4 (brightness), Fn+Esc (FN lock toggle)",
            "7. If all else fails, lighting may be firmware-controlled and require BIOS reset"
        ])

        return report

    def save_report(self, report: Dict[str, Any]) -> Path:
        try:
            """Save analysis report"""
            data_dir = self.project_root / "data" / "syphon_analysis"
            data_dir.mkdir(parents=True, exist_ok=True)

            filename = data_dir / f"lighting_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)

            logger.info(f"✅ Report saved: {filename}")
            return filename


        except Exception as e:
            self.logger.error(f"Error in save_report: {e}", exc_info=True)
            raise
def main():
    """Main execution"""
    print("=" * 70)
    print("#syphon → @grep: Lighting & Function Key Analysis")
    print("=" * 70)
    print()

    analyzer = SyphonLightingFunctionKeyAnalysis()
    report = analyzer.generate_analysis_report()
    filename = analyzer.save_report(report)

    print()
    print("=" * 70)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 70)
    print(f"Total Findings: {len(report['findings'])}")
    print(f"Conclusions: {len(report['conclusions'])}")
    print(f"Recommendations: {len(report['recommendations'])}")
    print()

    if report['conclusions']:
        print("🔍 CONCLUSIONS:")
        for conclusion in report['conclusions']:
            print(f"  • {conclusion}")
        print()

    if report['recommendations']:
        print("💡 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"  {rec}")
        print()

    print(f"✅ Full report: {filename}")
    print("=" * 70)


if __name__ == "__main__":


    main()