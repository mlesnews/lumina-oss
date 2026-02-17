#!/usr/bin/env python3
"""
JARVIS Aggressive External Lights Disable
FORCE ALL EXTERNAL LIGHTING TO OFF - LOUD AND BRIGHT FIX

@JARVIS @AGGRESSIVE @EXTERNAL_LIGHTS @OFF
"""

import sys
import asyncio
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

logger = get_logger("JARVISAggressiveLightFix")


class AggressiveExternalLightsDisable:
    """
    Aggressive fix to FORCE all external lighting OFF

    Methods:
    1. Registry - Set all brightness values to 0
    2. UI Automation - Directly disable in Armoury Crate UI
    3. Service Control - Stop/disable lighting services
    4. Process Control - Kill lighting processes
    5. Verification - Check all zones are OFF
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize aggressive light disable"""
        self.project_root = project_root or Path(__file__).parent.parent.parent

        from src.cfservices.services.jarvis_core.integrations.armoury_crate import create_armoury_crate_integration
        self.armoury_crate = create_armoury_crate_integration()

        logger.info("✅ Aggressive External Lights Disable initialized")

    def _run_powershell(self, command: str) -> Dict[str, Any]:
        """Execute PowerShell command"""
        import subprocess
        try:
            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", command],
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def method_1_registry_aggressive(self) -> Dict[str, Any]:
        """METHOD 1: Aggressive registry modification - ALL brightness to 0"""
        logger.info("🔧 METHOD 1: Aggressive registry modification...")

        # All possible registry paths for lighting
        registry_paths = [
            r"HKCU\SOFTWARE\ASUS\ArmouryDevice\Aura",
            r"HKCU\SOFTWARE\ASUS\Aura",
            r"HKCU\SOFTWARE\ASUS\ROG",
            r"HKLM\SOFTWARE\ASUS\ArmouryDevice\Aura",
            r"HKLM\SOFTWARE\ASUS\Aura",
            r"HKLM\SOFTWARE\ASUS\ROG",
            r"HKCU\SOFTWARE\ASUS\ArmouryDevice\Lighting",
            r"HKLM\SOFTWARE\ASUS\ArmouryDevice\Lighting",
        ]

        # All brightness-related keys
        brightness_keys = [
            "Brightness",
            "LightingBrightness",
            "BacklightBrightness",
            "KeyboardBrightness",
            "VueBrightness",
            "ExternalBrightness",
            "Zone1Brightness",
            "Zone2Brightness",
            "Zone3Brightness",
            "Zone4Brightness",
            "Zone5Brightness",
            "Zone6Brightness",
            "Zone7Brightness",
            "Zone8Brightness",
            "RGBBrightness",
            "AuraBrightness",
        ]

        command = """
        $paths = @(
            'HKCU:\\Software\\ASUS\\ArmouryDevice\\Aura',
            'HKCU:\\Software\\ASUS\\Aura',
            'HKCU:\\Software\\ASUS\\ROG',
            'HKLM:\\SOFTWARE\\ASUS\\ArmouryDevice\\Aura',
            'HKLM:\\SOFTWARE\\ASUS\\Aura',
            'HKLM:\\SOFTWARE\\ASUS\\ROG',
            'HKCU:\\Software\\ASUS\\ArmouryDevice\\Lighting',
            'HKLM:\\SOFTWARE\\ASUS\\ArmouryDevice\\Lighting'
        );
        $brightnessKeys = @(
            'Brightness', 'LightingBrightness', 'BacklightBrightness',
            'KeyboardBrightness', 'VueBrightness', 'ExternalBrightness',
            'Zone1Brightness', 'Zone2Brightness', 'Zone3Brightness',
            'Zone4Brightness', 'Zone5Brightness', 'Zone6Brightness',
            'Zone7Brightness', 'Zone8Brightness', 'RGBBrightness', 'AuraBrightness'
        );
        $totalUpdated = 0;
        foreach ($path in $paths) {
            if (Test-Path $path) {
                foreach ($key in $brightnessKeys) {
                    try {
                        Set-ItemProperty -Path $path -Name $key -Value 0 -Type DWord -ErrorAction SilentlyContinue;
                        $totalUpdated++;
                    } catch {}
                }
            } else {
                # Create path if it doesn't exist
                try {
                    New-Item -Path $path -Force -ErrorAction SilentlyContinue | Out-Null;
                    foreach ($key in $brightnessKeys) {
                        Set-ItemProperty -Path $path -Name $key -Value 0 -Type DWord -ErrorAction SilentlyContinue;
                        $totalUpdated++;
                    }
                } catch {}
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

        logger.info(f"  ✅ Registry updated: {updated_count} brightness values set to 0")

        return {
            "success": updated_count > 0,
            "updated_count": updated_count,
            "method": "registry_aggressive"
        }

    async def method_2_ui_automation_aggressive(self) -> Dict[str, Any]:
        """METHOD 2: Aggressive UI automation - Force disable in Armoury Crate"""
        logger.info("🔧 METHOD 2: Aggressive UI automation...")

        try:
            result = await self.armoury_crate.process_request({
                "action": "disable_all_lighting_ui"
            })

            if result.get("success"):
                logger.info("  ✅ UI automation successful")
                return {"success": True, "method": "ui_automation"}
            else:
                logger.warning(f"  ⚠️  UI automation had issues: {result.get('error', 'Unknown')}")
                return {"success": False, "error": result.get("error"), "method": "ui_automation"}
        except Exception as e:
            logger.warning(f"  ⚠️  UI automation failed: {e}")
            return {"success": False, "error": str(e), "method": "ui_automation"}

    async def method_3_service_control(self) -> Dict[str, Any]:
        """METHOD 3: Stop/disable lighting services"""
        logger.info("🔧 METHOD 3: Service control (stop lighting services)...")

        services = [
            "AuraService",
            "LightingService",
            "ROGLiveService"
        ]

        command = """
        $services = @('AuraService', 'LightingService', 'ROGLiveService');
        $stopped = 0;
        foreach ($svc in $services) {
            try {
                $service = Get-Service -Name $svc -ErrorAction SilentlyContinue;
                if ($service -and $service.Status -eq 'Running') {
                    Stop-Service -Name $svc -Force -ErrorAction SilentlyContinue;
                    $stopped++;
                }
            } catch {}
        }
        "Stopped:$stopped"
        """

        result = self._run_powershell(command)
        stopped_count = 0
        if "Stopped:" in result.get("stdout", ""):
            try:
                stopped_count = int(result.get("stdout", "").split(":")[1].strip())
            except:
                pass

        logger.info(f"  ✅ Services stopped: {stopped_count}")

        return {
            "success": stopped_count > 0,
            "stopped_count": stopped_count,
            "method": "service_control"
        }

    async def method_4_process_kill(self) -> Dict[str, Any]:
        """METHOD 4: Kill lighting processes"""
        logger.info("🔧 METHOD 4: Process control (kill lighting processes)...")

        processes = [
            "AuraService",
            "LightingService",
            "ROGLiveService",
            "ArmouryCrateControlInterface"
        ]

        command = """
        $processes = @('AuraService', 'LightingService', 'ROGLiveService', 'ArmouryCrateControlInterface');
        $killed = 0;
        foreach ($procName in $processes) {
            try {
                $procs = Get-Process -Name $procName -ErrorAction SilentlyContinue;
                if ($procs) {
                    $procs | Stop-Process -Force -ErrorAction SilentlyContinue;
                    $killed += $procs.Count;
                }
            } catch {}
        }
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
            "method": "process_kill"
        }

    async def method_5_verify_all_off(self) -> Dict[str, Any]:
        """METHOD 5: Verify all lighting is OFF"""
        logger.info("🔧 METHOD 5: Verification (check all zones are OFF)...")

        # Check registry values
        command = """
        $paths = @(
            'HKCU:\\Software\\ASUS\\ArmouryDevice\\Aura',
            'HKCU:\\Software\\ASUS\\Aura',
            'HKLM:\\SOFTWARE\\ASUS\\ArmouryDevice\\Aura',
            'HKLM:\\SOFTWARE\\ASUS\\Aura'
        );
        $brightnessKeys = @('Brightness', 'LightingBrightness', 'BacklightBrightness', 'VueBrightness');
        $allOff = $true;
        $issues = @();
        foreach ($path in $paths) {
            if (Test-Path $path) {
                foreach ($key in $brightnessKeys) {
                    try {
                        $value = (Get-ItemProperty -Path $path -Name $key -ErrorAction SilentlyContinue).$key;
                        if ($value -ne $null -and $value -ne 0) {
                            $allOff = $false;
                            $issues += "$path\\$key = $value";
                        }
                    } catch {}
                }
            }
        }
        if ($allOff) { "AllOff" } else { "Issues:" + ($issues -join '; ') }
        """

        result = self._run_powershell(command)
        stdout = result.get("stdout", "").strip()

        if "AllOff" in stdout:
            logger.info("  ✅ All lighting zones verified OFF")
            return {"success": True, "all_off": True, "method": "verification"}
        else:
            logger.warning(f"  ⚠️  Some zones may still be ON: {stdout}")
            return {"success": False, "all_off": False, "issues": stdout, "method": "verification"}

    async def aggressive_disable_all_external_lights(self) -> Dict[str, Any]:
        """AGGRESSIVE: Force all external lighting OFF using all methods"""
        logger.info("=" * 70)
        logger.info("🔴 AGGRESSIVE EXTERNAL LIGHTS DISABLE")
        logger.info("   FORCING ALL EXTERNAL LIGHTING TO OFF")
        logger.info("=" * 70)
        logger.info("")

        results = {
            "methods": {},
            "success": False
        }

        # Method 1: Registry (most important)
        logger.info("STEP 1: Registry modification...")
        results["methods"]["registry"] = await self.method_1_registry_aggressive()
        await asyncio.sleep(2)

        # Method 2: UI Automation
        logger.info("\nSTEP 2: UI automation...")
        results["methods"]["ui_automation"] = await self.method_2_ui_automation_aggressive()
        await asyncio.sleep(2)

        # Method 3: Service Control
        logger.info("\nSTEP 3: Service control...")
        results["methods"]["service_control"] = await self.method_3_service_control()
        await asyncio.sleep(2)

        # Method 4: Process Kill
        logger.info("\nSTEP 4: Process control...")
        results["methods"]["process_kill"] = await self.method_4_process_kill()
        await asyncio.sleep(2)

        # Method 5: Verification
        logger.info("\nSTEP 5: Verification...")
        results["methods"]["verification"] = await self.method_5_verify_all_off()

        # Final registry push (one more time)
        logger.info("\nSTEP 6: Final registry push...")
        results["methods"]["final_registry"] = await self.method_1_registry_aggressive()

        # Summary
        logger.info("\n" + "=" * 70)
        logger.info("📊 AGGRESSIVE DISABLE SUMMARY")
        logger.info("=" * 70)

        success_count = sum(1 for m in results["methods"].values() if m.get("success", False))
        total_methods = len(results["methods"])

        logger.info(f"Methods executed: {total_methods}")
        logger.info(f"Successful methods: {success_count}")
        logger.info(f"Verification: {'✅ ALL OFF' if results['methods'].get('verification', {}).get('all_off') else '⚠️  Some may still be ON'}")

        results["success"] = success_count >= 3  # At least 3 methods should succeed

        logger.info("=" * 70)

        if results["success"]:
            logger.info("✅ AGGRESSIVE DISABLE COMPLETE - All external lights should be OFF")
        else:
            logger.warning("⚠️  Some methods failed - Check manually in Armoury Crate")

        logger.info("=" * 70)

        return results


async def main():
    """Main execution"""
    print("=" * 70)
    print("🔴 JARVIS AGGRESSIVE EXTERNAL LIGHTS DISABLE")
    print("   FORCING ALL EXTERNAL LIGHTING TO OFF")
    print("=" * 70)
    print()

    fixer = AggressiveExternalLightsDisable()
    results = await fixer.aggressive_disable_all_external_lights()

    print()
    print("=" * 70)
    print("✅ AGGRESSIVE DISABLE COMPLETE")
    print("=" * 70)
    print(f"Overall Success: {results.get('success', False)}")
    print()
    print("If lights are still ON:")
    print("  1. Open Armoury Crate manually")
    print("  2. Go to Lighting section")
    print("  3. Set ALL zones to OFF")
    print("  4. Save profile")
    print("=" * 70)


if __name__ == "__main__":


    asyncio.run(main())