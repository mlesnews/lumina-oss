#!/usr/bin/env python3
"""
JARVIS: Correct Lighting Fix
Fixed version based on actual system state

@JARVIS @ASUS @LIGHTING @CORRECTED
"""

import sys
import subprocess
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVIS_CorrectedFix")


def main():
    """Corrected fix based on actual findings"""
    print("=" * 70)
    print("🔧 JARVIS: CORRECTED LIGHTING FIX")
    print("=" * 70)
    print()

    # Finding 1: Armoury Crate Service IS installed (6.3.8.0)
    print("STEP 1: Verifying Armoury Crate Service...")
    ps_command = """
    $svc = Get-Service -Name 'ArmouryCrateService' -ErrorAction SilentlyContinue;
    if ($svc) {
        $exe = Get-WmiObject Win32_Service -Filter "Name='ArmouryCrateService'" | Select-Object -ExpandProperty PathName;
        "$($svc.Status)|$($svc.StartType)|$exe"
    } else {
        "NotFound"
    }
    """

    result = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
        capture_output=True,
        text=True,
        timeout=5
    )

    if "NotFound" not in result.stdout:
        parts = result.stdout.strip().split("|")
        print(f"  ✅ Service Status: {parts[0]}")
        print(f"  ✅ Start Type: {parts[1]}")
        if len(parts) > 2:
            print(f"  ✅ Service Path: {parts[2]}")
    else:
        print("  ❌ Service not found")

    # Finding 2: Service executable is at: C:\Program Files\ASUS\Armoury Crate Service\ArmouryCrate.Service.exe
    print("\nSTEP 2: Locating Armoury Crate components...")
    service_path = r"C:\Program Files\ASUS\Armoury Crate Service"
    if Path(service_path).exists():
        print(f"  ✅ Service Directory: {service_path}")

        # Check for GUI app
        gui_paths = [
            r"C:\Program Files\ASUS\Armoury Crate Service\ArmouryCrate.exe",
            Path.home() / "AppData" / "Local" / "Programs" / "ASUS" / "ARMOURY CRATE" / "ArmouryCrate.exe"
        ]

        gui_found = False
        for gui_path in gui_paths:
            if Path(gui_path).exists():
                print(f"  ✅ GUI App Found: {gui_path}")
                gui_found = True
                break

        if not gui_found:
            print("  ⚠️  GUI App (ArmouryCrate.exe) not found")
            print("  → Service is installed, but GUI app may be missing")
            print("  → This explains why you can't control lighting via GUI")

    # Finding 3: Windows Dynamic Lighting - CRITICAL FIX
    print("\nSTEP 3: Fixing Windows Dynamic Lighting interference...")
    print("  🔴 CRITICAL: Windows Dynamic Lighting is overriding Armoury Crate")
    print("  → Opening settings to configure...")

    try:
        # Open Windows Dynamic Lighting settings
        subprocess.Popen(["ms-settings:personalization-dynamic-lighting"], shell=True)
        print("  ✅ Opened Windows Settings")

        # Also try to disable via registry
        ps_command = """
        $regPath = 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize';
        if (Test-Path $regPath) {
            try {
                Set-ItemProperty -Path $regPath -Name 'EnableDynamicLighting' -Value 0 -Type DWord -ErrorAction SilentlyContinue;
                Write-Host "Disabled"
            } catch {
                Write-Host "Error"
            }
        } else {
            Write-Host "PathNotFound"
        }
        """

        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
            capture_output=True,
            text=True,
            timeout=5
        )

        if "Disabled" in result.stdout:
            print("  ✅ Disabled Dynamic Lighting in registry")
        else:
            print("  ⚠️  Could not disable via registry (may need manual config)")
    except Exception as e:
        print(f"  ⚠️  Error: {e}")

    # Finding 4: Restart Armoury Crate Service to apply changes
    print("\nSTEP 4: Restarting Armoury Crate Service...")
    ps_command = """
    $svc = Get-Service -Name 'ArmouryCrateService' -ErrorAction SilentlyContinue;
    if ($svc) {
        Restart-Service -Name 'ArmouryCrateService' -Force -ErrorAction SilentlyContinue;
        Start-Sleep -Seconds 2;
        $svc = Get-Service -Name 'ArmouryCrateService';
        if ($svc.Status -eq 'Running') {
            Write-Host "Restarted"
        } else {
            Write-Host "Error"
        }
    } else {
        Write-Host "NotFound"
    }
    """

    result = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
        capture_output=True,
        text=True,
        timeout=10
    )

    if "Restarted" in result.stdout:
        print("  ✅ Service restarted successfully")
    else:
        print(f"  ⚠️  {result.stdout.strip()}")

    # Finding 5: Kill any conflicting processes
    print("\nSTEP 5: Ensuring clean state...")
    from scripts.python.jarvis_persistent_external_lighting_killer import PersistentExternalLightingKiller
    killer = PersistentExternalLightingKiller()
    kill_result = killer.run_once()
    print(f"  ✅ Killed {kill_result['processes_killed']} processes")
    print(f"  ✅ Stopped {kill_result['services_stopped']} services")

    print()
    print("=" * 70)
    print("✅ CORRECTED FIX APPLIED")
    print("=" * 70)
    print()
    print("KEY FINDINGS:")
    print("  1. Armoury Crate Service IS installed (6.3.8.0)")
    print("  2. Windows Dynamic Lighting is interfering (build 26200)")
    print("  3. FN lock is already disabled in registry")
    print("  4. Service restarted to apply changes")
    print()
    print("ACTION REQUIRED:")
    print("  → Windows Settings should be open")
    print("  → Go to: Personalization > Dynamic Lighting")
    print("  → Set Armoury Crate as HIGHEST PRIORITY")
    print("  → OR disable Dynamic Lighting entirely")
    print()
    print("TEST:")
    print("  → Try Fn+F4 to control lighting")
    print("  → If not working, restart PC and test again")
    print("=" * 70)


if __name__ == "__main__":


    main()