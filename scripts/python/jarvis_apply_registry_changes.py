#!/usr/bin/env python3
"""
JARVIS: Apply Registry Changes Immediately
🔄 Forces immediate application of registry changes without reboot
"""

import sys
import asyncio
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cfservices.services.jarvis_core.integrations.armoury_crate import create_armoury_crate_integration

async def main():
    """Apply registry changes immediately"""
    print("=" * 70)
    print("🔄 JARVIS: Apply Registry Changes Immediately")
    print("=" * 70)
    print()

    integration = create_armoury_crate_integration()

    # Restart all Armoury Crate related services and processes
    print("🔄 Restarting all Armoury Crate components...")
    print("-" * 70)

    # Services
    services = ["ArmouryCrateService", "ROGLiveService", "AuraService", "LightingService"]
    for service in services:
        try:
            ps_cmd = (
                f"$svc = Get-Service -Name '{service}' -ErrorAction SilentlyContinue; "
                f"if ($svc) {{ "
                f"  Restart-Service -Name '{service}' -Force -ErrorAction SilentlyContinue; "
                f"  Write-Host 'RESTARTED' "
                f"}} else {{ Write-Host 'NOT_FOUND' }}"
            )
            result = integration._run_powershell(ps_cmd)
            if isinstance(result, dict):
                output = result.get("stdout", "")
            else:
                output = str(result) if result else ""

            if "RESTARTED" in output:
                print(f"  ✅ {service}: Restarted")
        except:
            pass

    # Processes
    processes = ["ArmouryCrateControlInterface", "ArmouryCrate", "ArmouryCrate.UserSessionHelper"]
    for process in processes:
        try:
            ps_cmd = (
                f"$proc = Get-Process -Name '{process}' -ErrorAction SilentlyContinue; "
                f"if ($proc) {{ "
                f"  Stop-Process -Name '{process}' -Force -ErrorAction SilentlyContinue; "
                f"  Start-Sleep -Milliseconds 2000; "
                f"  $paths = @("
                f"    'C:\\Program Files\\ASUS\\ArmouryDevice\\{process}.exe', "
                f"    'C:\\Program Files (x86)\\ASUS\\ArmouryDevice\\{process}.exe', "
                f"    (Get-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\{process}.exe' -ErrorAction SilentlyContinue).'(default)' "
                f"  ); "
                f"  foreach ($path in $paths) {{ "
                f"    if ($path -and (Test-Path $path)) {{ "
                f"      Start-Process -FilePath $path -WindowStyle Hidden; "
                f"      Write-Host 'RESTARTED'; break "
                f"    }} "
                f"  }} "
                f"}} else {{ Write-Host 'NOT_RUNNING' }}"
            )
            result = integration._run_powershell(ps_cmd)
            if isinstance(result, dict):
                output = result.get("stdout", "")
            else:
                output = str(result) if result else ""

            if "RESTARTED" in output:
                print(f"  ✅ {process}: Restarted")
        except:
            pass

    print()
    print("=" * 70)
    print("💡 Registry changes applied")
    print("  ⚠️  Check if lock symbols disappeared")
    print("  ⚠️  If not, restart computer to fully apply changes")
    print("=" * 70)

if __name__ == "__main__":


    asyncio.run(main())