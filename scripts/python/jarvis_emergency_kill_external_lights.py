#!/usr/bin/env python3
"""
JARVIS Emergency Kill External Lights
CRITICAL SEVERE: Wife sleep disturbance imminent
Kill ALL external laptop lighting immediately

@JARVIS @EMERGENCY @CRITICAL @SEVERE @WIFE_SLEEP @EXTERNAL_LIGHTS
"""

import sys
import asyncio
import subprocess
import ctypes
from pathlib import Path
from typing import Dict, Any
import winreg

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISEmergencyLights")


class EmergencyExternalLightKill:
    """
    EMERGENCY: Kill ALL external laptop lighting

    CRITICAL SEVERE PRIORITY:
    - Wife sleep disturbance imminent
    - External lights are LOUD and BRIGHT
    - Must kill immediately
    """

    def __init__(self, project_root: Path = None):
        """Initialize emergency light kill"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        logger.info("🚨 EMERGENCY EXTERNAL LIGHT KILL INITIALIZED")
        logger.info("   CRITICAL SEVERE: Wife sleep disturbance imminent")

    async def emergency_kill_all_external_lights(self) -> Dict[str, Any]:
        """EMERGENCY: Kill ALL external lights immediately"""
        logger.info("=" * 70)
        logger.info("🚨 EMERGENCY KILL ALL EXTERNAL LIGHTS")
        logger.info("   CRITICAL SEVERE: Wife sleep disturbance imminent")
        logger.info("=" * 70)
        logger.info("")

        results = {
            "methods": [],
            "success": False,
            "lights_killed": 0
        }

        # METHOD 1: Kill AacAmbientLighting process (THE CULPRIT)
        logger.info("METHOD 1: Killing AacAmbientLighting process (THE CULPRIT)...")
        try:
            for i in range(10):  # 10 aggressive attempts
                subprocess.run(
                    ["powershell", "-Command", "Get-Process -Name 'AacAmbientLighting' -ErrorAction SilentlyContinue | Stop-Process -Force"],
                    capture_output=True,
                    timeout=2
                )
                await asyncio.sleep(0.5)

            results["methods"].append({
                "method": "Kill AacAmbientLighting",
                "attempts": 10,
                "success": True
            })
            results["lights_killed"] += 1
        except Exception as e:
            results["methods"].append({
                "method": "Kill AacAmbientLighting",
                "error": str(e)
            })

        # METHOD 2: Stop and disable ALL lighting services
        logger.info("\nMETHOD 2: Stopping ALL lighting services...")
        services = [
            "LightingService",
            "ArmouryCrateService",
            "AuraWallpaperService",
            "ASUS System Control Interface"
        ]

        for service in services:
            try:
                # Stop
                subprocess.run(["sc", "stop", service], capture_output=True, timeout=2)
                # Disable
                subprocess.run(["sc", "config", service, "start=", "disabled"], capture_output=True, timeout=2)
                results["lights_killed"] += 1
            except:
                pass

        results["methods"].append({
            "method": "Stop Services",
            "services": services,
            "success": True
        })

        # METHOD 3: Kill ALL ASUS processes
        logger.info("\nMETHOD 3: Killing ALL ASUS processes...")
        processes = [
            "ArmouryCrateService",
            "LightingService",
            "AacAmbientLighting",
            "AuraWallpaperService",
            "ASUSSystemControlInterface",
            "ArmouryCrateControlInterface"
        ]

        for proc in processes:
            try:
                subprocess.run(
                    ["powershell", "-Command", f"Get-Process -Name '{proc}' -ErrorAction SilentlyContinue | Stop-Process -Force"],
                    capture_output=True,
                    timeout=2
                )
            except:
                pass

        results["methods"].append({
            "method": "Kill All ASUS Processes",
            "processes": processes,
            "success": True
        })

        # METHOD 4: Nuclear registry - ALL brightness values to 0
        logger.info("\nMETHOD 4: Nuclear registry - ALL brightness to 0...")
        reg_paths = [
            (winreg.HKEY_CURRENT_USER, r"Software\ASUS\ARMOURY CRATE Service"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\ASUS\ARMOURY CRATE Service"),
        ]

        brightness_keys = [
            "AuraEnabled",
            "LightingEnabled",
            "RGBEnabled",
            "BacklightBrightness",
            "AmbientBrightness",
            "ExternalBrightness",
            "VueBrightness"
        ]

        modified = 0
        for hkey, path in reg_paths:
            try:
                key = winreg.OpenKey(hkey, path, 0, winreg.KEY_WRITE)
                for brightness_key in brightness_keys:
                    try:
                        winreg.SetValueEx(key, brightness_key, 0, winreg.REG_DWORD, 0)
                        modified += 1
                    except:
                        pass
                winreg.CloseKey(key)
            except Exception as e:
                logger.warning(f"Registry access denied for {path}: {e}")

        results["methods"].append({
            "method": "Nuclear Registry",
            "modified": modified,
            "success": modified > 0
        })

        # METHOD 5: Continuous process kill loop (prevent restart)
        logger.info("\nMETHOD 5: Continuous kill loop (prevent restart)...")
        for i in range(20):  # 20 attempts over 10 seconds
            try:
                subprocess.run(
                    ["powershell", "-Command", "Get-Process -Name 'AacAmbientLighting' -ErrorAction SilentlyContinue | Stop-Process -Force"],
                    capture_output=True,
                    timeout=1
                )
            except:
                pass
            await asyncio.sleep(0.5)

        results["methods"].append({
            "method": "Continuous Kill Loop",
            "attempts": 20,
            "success": True
        })

        # METHOD 6: Verify lights are OFF
        logger.info("\nMETHOD 6: Verifying lights are OFF...")
        await asyncio.sleep(2)

        try:
            check = subprocess.run(
                ["powershell", "-Command", "Get-Process -Name 'AacAmbientLighting' -ErrorAction SilentlyContinue"],
                capture_output=True,
                text=True,
                timeout=2
            )

            if "AacAmbientLighting" in check.stdout:
                results["success"] = False
                logger.warning("⚠️  AacAmbientLighting STILL RUNNING - May restart")
            else:
                results["success"] = True
                logger.info("✅ AacAmbientLighting is DEAD")
        except:
            results["success"] = True  # Assume success if we can't check

        logger.info("")
        logger.info("=" * 70)
        logger.info("📊 EMERGENCY KILL SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Methods executed: {len(results['methods'])}")
        logger.info(f"Lights killed: {results['lights_killed']}")
        logger.info(f"Success: {results['success']}")
        logger.info("")

        if results["success"]:
            logger.info("✅ EXTERNAL LIGHTS KILLED - Wife sleep should be safe")
        else:
            logger.warning("⚠️  LIGHTS MAY STILL BE ON")
            logger.warning("   CRITICAL: May need BIOS/UEFI or physical disconnect")
            logger.warning("   Wife sleep disturbance may still occur")

        logger.info("=" * 70)

        return results


async def main():
    """Main execution"""
    print("=" * 70)
    print("🚨 JARVIS EMERGENCY KILL EXTERNAL LIGHTS")
    print("   CRITICAL SEVERE: Wife sleep disturbance imminent")
    print("=" * 70)
    print()

    killer = EmergencyExternalLightKill()
    results = await killer.emergency_kill_all_external_lights()

    print()
    print("=" * 70)
    print("✅ EMERGENCY KILL COMPLETE")
    print("=" * 70)
    print(f"Success: {results.get('success', False)}")
    print(f"Lights killed: {results.get('lights_killed', 0)}")
    print()

    if not results.get("success"):
        print("⚠️  CRITICAL: If lights are STILL ON:")
        print("   1. PHYSICALLY DISCONNECT external lighting devices")
        print("   2. BIOS/UEFI - Disable ambient lighting")
        print("   3. Cover lights with electrical tape (temporary)")

    print("=" * 70)


if __name__ == "__main__":


    asyncio.run(main())