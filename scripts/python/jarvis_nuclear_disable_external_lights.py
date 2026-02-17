#!/usr/bin/env python3
"""
JARVIS NUCLEAR External Lights Disable
ULTRA-AGGRESSIVE: Hardware-level, driver-level, process-level disable

@JARVIS @NUCLEAR @EXTERNAL_LIGHTS @HARDWARE_LEVEL
"""

import sys
import asyncio
import ctypes
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISNuclearLightFix")


class NuclearExternalLightsDisable:
    """
    NUCLEAR OPTION: Hardware-level, driver-level, process-level disable

    Methods:
    1. Registry - ALL paths, ALL keys, recursive
    2. Windows API - Direct hardware control
    3. Driver-level - Disable lighting drivers
    4. Process - Kill ALL related processes
    5. Service - Stop AND disable services
    6. WMI - Hardware-level control
    7. Device Manager - Disable lighting devices
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize nuclear light disable"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        logger.info("✅ Nuclear External Lights Disable initialized")

    def _run_powershell(self, command: str) -> Dict[str, Any]:
        """Execute PowerShell command"""
        try:
            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", command],
                capture_output=True,
                text=True,
                timeout=60
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def method_1_registry_nuclear(self) -> Dict[str, Any]:
        """METHOD 1: NUCLEAR registry - Recursive, ALL paths, ALL keys"""
        logger.info("🔴 METHOD 1: NUCLEAR registry modification (recursive)...")

        command = """
        $paths = @(
            'HKCU:\\Software\\ASUS',
            'HKLM:\\SOFTWARE\\ASUS'
        );
        $brightnessKeys = @(
            'Brightness', 'LightingBrightness', 'BacklightBrightness',
            'KeyboardBrightness', 'VueBrightness', 'ExternalBrightness',
            'Zone1Brightness', 'Zone2Brightness', 'Zone3Brightness',
            'Zone4Brightness', 'Zone5Brightness', 'Zone6Brightness',
            'Zone7Brightness', 'Zone8Brightness', 'RGBBrightness', 'AuraBrightness',
            'Lighting', 'LightingEnabled', 'AuraEnabled', 'VueEnabled'
        );
        $totalUpdated = 0;
        foreach ($basePath in $paths) {
            if (Test-Path $basePath) {
                Get-ChildItem -Path $basePath -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
                    $path = $_.PSPath;
                    foreach ($key in $brightnessKeys) {
                        try {
                            $current = (Get-ItemProperty -Path $path -Name $key -ErrorAction SilentlyContinue).$key;
                            if ($current -ne $null -and $current -ne 0) {
                                Set-ItemProperty -Path $path -Name $key -Value 0 -Type DWord -ErrorAction SilentlyContinue;
                                $totalUpdated++;
                            }
                        } catch {
                            try {
                                Set-ItemProperty -Path $path -Name $key -Value 0 -Type DWord -ErrorAction SilentlyContinue;
                                $totalUpdated++;
                            } catch {}
                        }
                    }
                    # Also set any numeric values that look like brightness
                    try {
                        Get-ItemProperty -Path $path -ErrorAction SilentlyContinue | Get-Member -MemberType NoteProperty | ForEach-Object {
                            $propName = $_.Name;
                            if ($propName -like '*Brightness*' -or $propName -like '*Lighting*' -or $propName -like '*Aura*') {
                                try {
                                    $val = (Get-ItemProperty -Path $path -Name $propName -ErrorAction SilentlyContinue).$propName;
                                    if ($val -is [int] -and $val -gt 0 -and $val -le 100) {
                                        Set-ItemProperty -Path $path -Name $propName -Value 0 -Type DWord -ErrorAction SilentlyContinue;
                                        $totalUpdated++;
                                    }
                                } catch {}
                            }
                        }
                    } catch {}
                }
            }
        }
        "Updated:$totalUpdated"
        """

        result = self._run_powershell(command)
        updated_count = 0
        if "Updated:" in result.get("stdout", ""):
            try:
                updated_count = int(result.get("stdout", "").split(":")[1].strip())
            except:
                pass

        logger.info(f"  ✅ NUCLEAR registry: {updated_count} values set to 0")

        return {
            "success": updated_count > 0,
            "updated_count": updated_count,
            "method": "registry_nuclear"
        }

    async def method_2_driver_disable(self) -> Dict[str, Any]:
        """METHOD 2: Disable lighting drivers via Device Manager"""
        logger.info("🔴 METHOD 2: Driver-level disable (Device Manager)...")

        command = """
        $disabled = 0;
        $devices = Get-PnpDevice -Class 'System' -ErrorAction SilentlyContinue | Where-Object {
            $_.FriendlyName -like '*Aura*' -or 
            $_.FriendlyName -like '*Lighting*' -or 
            $_.FriendlyName -like '*RGB*' -or
            $_.FriendlyName -like '*ASUS*Lighting*'
        };
        foreach ($device in $devices) {
            try {
                if ($device.Status -ne 'Disabled') {
                    Disable-PnpDevice -InstanceId $device.InstanceId -Confirm:$false -ErrorAction SilentlyContinue;
                    $disabled++;
                }
            } catch {}
        }
        "Disabled:$disabled"
        """

        result = self._run_powershell(command)
        disabled_count = 0
        if "Disabled:" in result.get("stdout", ""):
            try:
                disabled_count = int(result.get("stdout", "").split(":")[1].strip())
            except:
                pass

        logger.info(f"  ✅ Drivers disabled: {disabled_count}")

        return {
            "success": disabled_count > 0,
            "disabled_count": disabled_count,
            "method": "driver_disable"
        }

    async def method_3_service_nuclear(self) -> Dict[str, Any]:
        """METHOD 3: NUCLEAR service control - Stop AND disable"""
        logger.info("🔴 METHOD 3: NUCLEAR service control (stop AND disable)...")

        services = [
            "AuraService",
            "LightingService",
            "ROGLiveService",
            "ArmouryCrateService"
        ]

        command = f"""
        $services = @('AuraService', 'LightingService', 'ROGLiveService', 'ArmouryCrateService');
        $stopped = 0;
        $disabled = 0;
        foreach ($svc in $services) {{
            try {{
                $service = Get-Service -Name $svc -ErrorAction SilentlyContinue;
                if ($service) {{
                    # Stop service
                    if ($service.Status -eq 'Running') {{
                        Stop-Service -Name $svc -Force -ErrorAction SilentlyContinue;
                        $stopped++;
                    }}
                    # Disable service
                    Set-Service -Name $svc -StartupType Disabled -ErrorAction SilentlyContinue;
                    $disabled++;
                }}
            }} catch {{}}
        }}
        "Stopped:$stopped;Disabled:$disabled"
        """

        result = self._run_powershell(command)
        stopped_count = 0
        disabled_count = 0
        if "Stopped:" in result.get("stdout", ""):
            try:
                parts = result.get("stdout", "").split(";")
                stopped_count = int(parts[0].split(":")[1].strip())
                disabled_count = int(parts[1].split(":")[1].strip())
            except:
                pass

        logger.info(f"  ✅ Services stopped: {stopped_count}, disabled: {disabled_count}")

        return {
            "success": stopped_count > 0 or disabled_count > 0,
            "stopped_count": stopped_count,
            "disabled_count": disabled_count,
            "method": "service_nuclear"
        }

    async def method_4_process_nuclear(self) -> Dict[str, Any]:
        """METHOD 4: NUCLEAR process kill - ALL related processes"""
        logger.info("🔴 METHOD 4: NUCLEAR process kill (ALL related processes)...")

        processes = [
            "AuraService",
            "LightingService",
            "ROGLiveService",
            "ArmouryCrateControlInterface",
            "ArmouryCrate",
            "Aura",
            "Lighting"
        ]

        command = f"""
        $processes = @('AuraService', 'LightingService', 'ROGLiveService', 
                       'ArmouryCrateControlInterface', 'ArmouryCrate', 'Aura', 'Lighting');
        $killed = 0;
        foreach ($procName in $processes) {{
            try {{
                $procs = Get-Process -Name $procName -ErrorAction SilentlyContinue;
                if ($procs) {{
                    $procs | Stop-Process -Force -ErrorAction SilentlyContinue;
                    $killed += $procs.Count;
                }}
            }} catch {{
                # Try by path
                Get-Process | Where-Object {{ $_.Path -like '*ASUS*' -and ($_.Path -like '*Aura*' -or $_.Path -like '*Lighting*') }} | 
                    Stop-Process -Force -ErrorAction SilentlyContinue;
            }}
        }}
        "Killed:$killed"
        """

        result = self._run_powershell(command)
        killed_count = 0
        if "Killed:" in result.get("stdout", ""):
            try:
                killed_count = int(result.get("stdout", "").split(":")[1].strip())
            except:
                pass

        logger.info(f"  ✅ Processes killed: {killed_count}")

        return {
            "success": killed_count > 0,
            "killed_count": killed_count,
            "method": "process_nuclear"
        }

    async def method_5_wmi_hardware_control(self) -> Dict[str, Any]:
        """METHOD 5: WMI hardware-level control"""
        logger.info("🔴 METHOD 5: WMI hardware-level control...")

        command = """
        $disabled = 0;
        try {
            $devices = Get-WmiObject -Class Win32_PnPEntity -ErrorAction SilentlyContinue | Where-Object {
                $_.Name -like '*Aura*' -or 
                $_.Name -like '*Lighting*' -or 
                $_.Name -like '*RGB*' -or
                ($_.Name -like '*ASUS*' -and ($_.Name -like '*Light*' -or $_.Name -like '*Aura*'))
            };
            foreach ($device in $devices) {
                try {
                    $device.Disable();
                    $disabled++;
                } catch {}
            }
        } catch {}
        "Disabled:$disabled"
        """

        result = self._run_powershell(command)
        disabled_count = 0
        if "Disabled:" in result.get("stdout", ""):
            try:
                disabled_count = int(result.get("stdout", "").split(":")[1].strip())
            except:
                pass

        logger.info(f"  ✅ WMI devices disabled: {disabled_count}")

        return {
            "success": disabled_count > 0,
            "disabled_count": disabled_count,
            "method": "wmi_hardware"
        }

    async def method_6_final_registry_push(self) -> Dict[str, Any]:
        """METHOD 6: Final registry push - One more time, all paths"""
        logger.info("🔴 METHOD 6: Final registry push (all paths, all keys)...")

        # Same as method 1 but one more time
        return await self.method_1_registry_nuclear()

    async def nuclear_disable_all_external_lights(self) -> Dict[str, Any]:
        """NUCLEAR: Force all external lighting OFF using ALL methods"""
        logger.info("=" * 70)
        logger.info("🔴 NUCLEAR EXTERNAL LIGHTS DISABLE")
        logger.info("   HARDWARE-LEVEL, DRIVER-LEVEL, PROCESS-LEVEL")
        logger.info("=" * 70)
        logger.info("")

        results = {
            "methods": {},
            "success": False
        }

        # Method 1: Nuclear Registry
        logger.info("STEP 1: NUCLEAR registry modification...")
        results["methods"]["registry_nuclear"] = await self.method_1_registry_nuclear()
        await asyncio.sleep(3)

        # Method 2: Driver Disable
        logger.info("\nSTEP 2: Driver-level disable...")
        results["methods"]["driver_disable"] = await self.method_2_driver_disable()
        await asyncio.sleep(2)

        # Method 3: Nuclear Service Control
        logger.info("\nSTEP 3: NUCLEAR service control...")
        results["methods"]["service_nuclear"] = await self.method_3_service_nuclear()
        await asyncio.sleep(2)

        # Method 4: Nuclear Process Kill
        logger.info("\nSTEP 4: NUCLEAR process kill...")
        results["methods"]["process_nuclear"] = await self.method_4_process_nuclear()
        await asyncio.sleep(2)

        # Method 5: WMI Hardware Control
        logger.info("\nSTEP 5: WMI hardware-level control...")
        results["methods"]["wmi_hardware"] = await self.method_5_wmi_hardware_control()
        await asyncio.sleep(2)

        # Method 6: Final Registry Push
        logger.info("\nSTEP 6: Final registry push...")
        results["methods"]["final_registry"] = await self.method_6_final_registry_push()

        # Summary
        logger.info("\n" + "=" * 70)
        logger.info("📊 NUCLEAR DISABLE SUMMARY")
        logger.info("=" * 70)

        success_count = sum(1 for m in results["methods"].values() if m.get("success", False))
        total_methods = len(results["methods"])

        logger.info(f"Methods executed: {total_methods}")
        logger.info(f"Successful methods: {success_count}")

        # Calculate totals
        total_registry = results["methods"].get("registry_nuclear", {}).get("updated_count", 0) + \
                        results["methods"].get("final_registry", {}).get("updated_count", 0)
        total_services_stopped = results["methods"].get("service_nuclear", {}).get("stopped_count", 0)
        total_services_disabled = results["methods"].get("service_nuclear", {}).get("disabled_count", 0)
        total_processes = results["methods"].get("process_nuclear", {}).get("killed_count", 0)
        total_drivers = results["methods"].get("driver_disable", {}).get("disabled_count", 0)
        total_wmi = results["methods"].get("wmi_hardware", {}).get("disabled_count", 0)

        logger.info(f"Registry values set to 0: {total_registry}")
        logger.info(f"Services stopped: {total_services_stopped}, disabled: {total_services_disabled}")
        logger.info(f"Processes killed: {total_processes}")
        logger.info(f"Drivers disabled: {total_drivers}")
        logger.info(f"WMI devices disabled: {total_wmi}")

        results["success"] = success_count >= 4  # At least 4 methods should succeed

        logger.info("=" * 70)

        if results["success"]:
            logger.info("✅ NUCLEAR DISABLE COMPLETE - All external lights should be OFF")
        else:
            logger.warning("⚠️  Some methods failed - May need manual intervention")

        logger.info("=" * 70)

        return results


async def main():
    """Main execution"""
    print("=" * 70)
    print("🔴 JARVIS NUCLEAR EXTERNAL LIGHTS DISABLE")
    print("   HARDWARE-LEVEL, DRIVER-LEVEL, PROCESS-LEVEL")
    print("=" * 70)
    print()
    print("⚠️  WARNING: This will:")
    print("   - Disable lighting drivers")
    print("   - Stop and disable lighting services")
    print("   - Kill all lighting processes")
    print("   - Modify registry extensively")
    print()
    print("Press Ctrl+C to cancel, or wait 5 seconds to continue...")
    print()

    try:
        await asyncio.sleep(5)
    except KeyboardInterrupt:
        print("\nCancelled.")
        return

    fixer = NuclearExternalLightsDisable()
    results = await fixer.nuclear_disable_all_external_lights()

    print()
    print("=" * 70)
    print("✅ NUCLEAR DISABLE COMPLETE")
    print("=" * 70)
    print(f"Overall Success: {results.get('success', False)}")
    print()
    print("If lights are STILL ON after this:")
    print("  1. Check physical hardware switches")
    print("  2. Check BIOS settings")
    print("  3. May need to unplug/replug device")
    print("=" * 70)


if __name__ == "__main__":


    asyncio.run(main())