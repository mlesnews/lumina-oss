#!/usr/bin/env python3
"""
JARVIS: Restore OEM Lighting Control
Based on deep ASUS research - fix what changed from OEM working state

@JARVIS @ASUS @OEM @LIGHTING @WINDOWS_DYNAMIC_LIGHTING
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Any

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVIS_RestoreOEM")


class JARVISRestoreOEMLighting:
    """
    Restore OEM lighting control based on research findings
    """

    def __init__(self):
        self.project_root = project_root
        logger.info("✅ JARVIS: Restore OEM Lighting Control initialized")

    def check_windows_dynamic_lighting(self) -> Dict[str, Any]:
        """Check Windows Dynamic Lighting settings - KEY FINDING from research"""
        logger.info("=" * 70)
        logger.info("🔍 CHECKING WINDOWS DYNAMIC LIGHTING")
        logger.info("   Research shows: Windows can override Armoury Crate!")
        logger.info("=" * 70)

        result = {
            "windows_version": None,
            "dynamic_lighting_enabled": None,
            "armoury_crate_priority": None,
            "fix_applied": False
        }

        # Check Windows version
        try:
            ps_command = """
            $os = Get-WmiObject -Class Win32_OperatingSystem -ErrorAction SilentlyContinue;
            "$($os.Version)|$($os.BuildNumber)"
            """

            output = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=5
            ).stdout.strip()

            if "|" in output:
                parts = output.split("|")
                result["windows_version"] = parts[0]
                result["build_number"] = parts[1]

                # Check if build 22621.2361 or later (has Dynamic Lighting)
                try:
                    build = int(parts[1])
                    if build >= 22621:
                        logger.info(f"  ⚠️  Windows Build {build} - Has Dynamic Lighting feature")
                        logger.info("  → This can override Armoury Crate!")
                except:
                    pass
        except Exception as e:
            logger.error(f"Error checking Windows version: {e}")

        # Check Dynamic Lighting registry
        try:
            ps_command = """
            $regPath = 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize';
            if (Test-Path $regPath) {
                $enabled = (Get-ItemProperty -Path $regPath -Name 'EnableTransparency' -ErrorAction SilentlyContinue).EnableTransparency;
                $dynamicLighting = (Get-ItemProperty -Path $regPath -Name 'EnableDynamicLighting' -ErrorAction SilentlyContinue).EnableDynamicLighting;
                "$enabled|$dynamicLighting"
            } else {
                "PathNotFound"
            }
            """

            output = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=5
            ).stdout.strip()

            if "|" in output:
                result["dynamic_lighting_enabled"] = output
        except Exception as e:
            logger.error(f"Error checking Dynamic Lighting: {e}")

        # Try to open Windows Settings to Dynamic Lighting
        logger.info("\n📋 Opening Windows Dynamic Lighting Settings...")
        logger.info("   MANUAL STEP REQUIRED:")
        logger.info("   1. Windows Settings should open")
        logger.info("   2. Navigate to: Personalization > Dynamic Lighting")
        logger.info("   3. Set Armoury Crate as HIGHEST PRIORITY")
        logger.info("   4. Or disable Dynamic Lighting entirely")

        try:
            # Open Windows Settings to Dynamic Lighting
            subprocess.Popen([
                "ms-settings:personalization-dynamic-lighting"
            ], shell=True)
            logger.info("  ✅ Opened Windows Settings to Dynamic Lighting")
        except Exception as e:
            logger.warning(f"  ⚠️  Could not open settings automatically: {e}")
            logger.info("  → Manually: Windows Settings > Personalization > Dynamic Lighting")

        return result

    def check_armoury_crate_installation(self) -> Dict[str, Any]:
        """Check if Armoury Crate is properly installed"""
        logger.info("\n" + "=" * 70)
        logger.info("🔍 CHECKING ARMOURY CRATE INSTALLATION")
        logger.info("=" * 70)

        result = {
            "installed": False,
            "path": None,
            "version": None,
            "needs_reinstall": False
        }

        # Check installation paths
        paths = [
            r"C:\Program Files\ASUS\ARMOURY CRATE Service",
            r"C:\Program Files (x86)\ASUS\ARMOURY CRATE Service",
            r"%LOCALAPPDATA%\Programs\ASUS\ARMOURY CRATE"
        ]

        for path_template in paths:
            try:
                expanded = Path(path_template).expanduser() if "%" not in path_template else Path(subprocess.run(
                    ["powershell", "-Command", f"[Environment]::ExpandEnvironmentVariables('{path_template}')"],
                    capture_output=True,
                    text=True
                ).stdout.strip())

                exe_path = expanded / "ArmouryCrate.exe"
                if exe_path.exists():
                    result["installed"] = True
                    result["path"] = str(exe_path)

                    # Get version
                    try:
                        ps_command = f"""
                        $version = (Get-ItemProperty -Path '{exe_path}' -ErrorAction SilentlyContinue).VersionInfo.FileVersion;
                        Write-Host $version
                        """
                        version = subprocess.run(
                            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
                            capture_output=True,
                            text=True,
                            timeout=5
                        ).stdout.strip()
                        result["version"] = version
                    except:
                        pass

                    logger.info(f"  ✅ Found: {exe_path}")
                    logger.info(f"     Version: {result['version'] or 'Unknown'}")
                    break
            except Exception as e:
                continue

        if not result["installed"]:
            logger.warning("  ❌ Armoury Crate NOT FOUND")
            logger.warning("  → This is the problem! It was working OEM because Armoury Crate was installed.")
            result["needs_reinstall"] = True

        return result

    def check_asus_atk_package(self) -> Dict[str, Any]:
        try:
            """Check ASUS ATK Package - required for function keys"""
            logger.info("\n" + "=" * 70)
            logger.info("🔍 CHECKING ASUS ATK PACKAGE")
            logger.info("   Required for Function Key control")
            logger.info("=" * 70)

            result = {
                "installed": False,
                "path": None
            }

            paths = [
                r"C:\Program Files\ASUS\ATK Package",
                r"C:\Program Files (x86)\ASUS\ATK Package"
            ]

            for path in paths:
                if Path(path).exists():
                    result["installed"] = True
                    result["path"] = path
                    logger.info(f"  ✅ Found: {path}")
                    break

            if not result["installed"]:
                logger.warning("  ❌ ASUS ATK Package NOT FOUND")
                logger.warning("  → Function keys won't work without this!")

            return result

        except Exception as e:
            self.logger.error(f"Error in check_asus_atk_package: {e}", exc_info=True)
            raise
    def generate_fix_plan(self) -> Dict[str, Any]:
        """Generate comprehensive fix plan based on research"""
        logger.info("\n" + "=" * 70)
        logger.info("📋 GENERATING FIX PLAN")
        logger.info("=" * 70)

        # Run all checks
        wdl_check = self.check_windows_dynamic_lighting()
        ac_check = self.check_armoury_crate_installation()
        atk_check = self.check_asus_atk_package()

        fix_plan = {
            "issues_found": [],
            "fixes_required": [],
            "download_links": []
        }

        # Issue 1: Windows Dynamic Lighting
        if wdl_check.get("build_number") and int(wdl_check["build_number"]) >= 22621:
            fix_plan["issues_found"].append("Windows Dynamic Lighting can override Armoury Crate")
            fix_plan["fixes_required"].append({
                "priority": "HIGH",
                "issue": "Windows Dynamic Lighting interference",
                "fix": "Set Armoury Crate as highest priority in Windows Settings > Personalization > Dynamic Lighting",
                "manual": True
            })

        # Issue 2: Armoury Crate not installed
        if not ac_check["installed"]:
            fix_plan["issues_found"].append("Armoury Crate is NOT installed (was working OEM)")
            fix_plan["fixes_required"].append({
                "priority": "CRITICAL",
                "issue": "Armoury Crate missing",
                "fix": "Download and install Armoury Crate from ASUS",
                "download": "https://www.asus.com/support/Download-Center/",
                "manual": True
            })
            fix_plan["download_links"].append({
                "name": "Armoury Crate",
                "url": "https://www.asus.com/support/Download-Center/",
                "model": "ROG Strix SCAR 18 G835LX"
            })

        # Issue 3: ASUS ATK Package missing
        if not atk_check["installed"]:
            fix_plan["issues_found"].append("ASUS ATK Package missing (required for function keys)")
            fix_plan["fixes_required"].append({
                "priority": "HIGH",
                "issue": "ASUS ATK Package missing",
                "fix": "Download and install ASUS ATK Package",
                "download": "https://www.asus.com/support/Download-Center/",
                "manual": True
            })
            fix_plan["download_links"].append({
                "name": "ASUS ATK Package",
                "url": "https://www.asus.com/support/Download-Center/",
                "model": "ROG Strix SCAR 18 G835LX"
            })

        return fix_plan

    def print_fix_instructions(self, fix_plan: Dict[str, Any]):
        """Print detailed fix instructions"""
        logger.info("\n" + "=" * 70)
        logger.info("🔧 FIX INSTRUCTIONS - RESTORE OEM FUNCTIONALITY")
        logger.info("=" * 70)

        logger.info("\n📋 ISSUES FOUND:")
        for i, issue in enumerate(fix_plan["issues_found"], 1):
            logger.info(f"  {i}. {issue}")

        logger.info("\n🔧 FIXES REQUIRED (in priority order):")
        for i, fix in enumerate(fix_plan["fixes_required"], 1):
            logger.info(f"\n  {i}. [{fix['priority']}] {fix['issue']}")
            logger.info(f"     Fix: {fix['fix']}")
            if "download" in fix:
                logger.info(f"     Download: {fix['download']}")

        logger.info("\n📥 DOWNLOAD LINKS:")
        for link in fix_plan["download_links"]:
            logger.info(f"  • {link['name']}: {link['url']}")
            logger.info(f"    Model: {link['model']}")

        logger.info("\n" + "=" * 70)
        logger.info("🎯 ROOT CAUSE IDENTIFIED:")
        logger.info("   Lighting was working OEM because:")
        logger.info("   1. Armoury Crate was installed")
        logger.info("   2. Windows Dynamic Lighting didn't exist yet")
        logger.info("   3. ASUS ATK Package was installed")
        logger.info("")
        logger.info("   Now it's broken because:")
        for issue in fix_plan["issues_found"]:
            logger.info(f"   • {issue}")
        logger.info("=" * 70)


def main():
    """Main execution"""
    print("=" * 70)
    print("🔧 JARVIS: RESTORE OEM LIGHTING CONTROL")
    print("   Based on Deep ASUS Research")
    print("=" * 70)
    print()

    fixer = JARVISRestoreOEMLighting()
    fix_plan = fixer.generate_fix_plan()
    fixer.print_fix_instructions(fix_plan)

    print()
    print("=" * 70)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 70)
    print()
    print("NEXT STEPS:")
    print("  1. Windows Settings should be open - configure Dynamic Lighting")
    print("  2. Download and install Armoury Crate from ASUS")
    print("  3. Download and install ASUS ATK Package if missing")
    print("  4. Restart and test function keys (Fn+F4 for lighting)")
    print("=" * 70)


if __name__ == "__main__":


    main()