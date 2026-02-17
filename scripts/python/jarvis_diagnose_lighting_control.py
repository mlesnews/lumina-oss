#!/usr/bin/env python3
"""
JARVIS Lighting Control Diagnostic
Find what's actually controlling the external lights

@JARVIS @DIAGNOSTIC @LIGHTING @CONTROL
"""

import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, List

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISLightingDiagnostic")


def run_powershell(command: str) -> Dict[str, Any]:
    """Execute PowerShell command"""
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


def diagnose_lighting_control():
    """Diagnose what's controlling the external lights"""
    print("=" * 70)
    print("🔍 JARVIS LIGHTING CONTROL DIAGNOSTIC")
    print("=" * 70)
    print()

    results = {}

    # 1. Check all ASUS registry paths
    print("1. Checking ASUS registry paths...")
    command = """
    $paths = @(
        'HKCU:\\Software\\ASUS',
        'HKLM:\\SOFTWARE\\ASUS'
    );
    $allValues = @();
    foreach ($basePath in $paths) {
        if (Test-Path $basePath) {
            Get-ChildItem -Path $basePath -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
                $path = $_.PSPath;
                try {
                    $props = Get-ItemProperty -Path $path -ErrorAction SilentlyContinue;
                    $props.PSObject.Properties | Where-Object {
                        $_.Name -like '*Brightness*' -or 
                        $_.Name -like '*Lighting*' -or 
                        $_.Name -like '*Aura*' -or
                        $_.Name -like '*Vue*' -or
                        $_.Name -like '*RGB*'
                    } | ForEach-Object {
                        $allValues += [PSCustomObject]@{
                            Path = $path;
                            Key = $_.Name;
                            Value = $_.Value;
                            Type = $_.Value.GetType().Name
                        }
                    }
                } catch {}
            }
        }
    }
    $allValues | ConvertTo-Json -Depth 3
    """

    result = run_powershell(command)
    if result.get("success"):
        import json
        try:
            values = json.loads(result.get("stdout", "[]"))
            print(f"   Found {len(values)} brightness/lighting values:")
            for v in values[:20]:  # Show first 20
                print(f"     {v.get('Path', '')}\\{v.get('Key', '')} = {v.get('Value', '')}")
            results["registry_values"] = values
        except:
            print(f"   Output: {result.get('stdout', '')[:500]}")
    else:
        print(f"   Error: {result.get('error', 'Unknown')}")

    print()

    # 2. Check running processes
    print("2. Checking running processes...")
    command = """
    Get-Process | Where-Object {
        $_.ProcessName -like '*ASUS*' -or
        $_.ProcessName -like '*Aura*' -or
        $_.ProcessName -like '*Lighting*' -or
        $_.ProcessName -like '*Armoury*'
    } | Select-Object ProcessName, Id, Path | ConvertTo-Json
    """

    result = run_powershell(command)
    if result.get("success"):
        import json
        try:
            processes = json.loads(result.get("stdout", "[]"))
            print(f"   Found {len(processes)} ASUS/lighting processes:")
            for p in processes:
                print(f"     {p.get('ProcessName', '')} (PID: {p.get('Id', '')})")
            results["processes"] = processes
        except:
            print(f"   Output: {result.get('stdout', '')[:500]}")
    else:
        print(f"   Error: {result.get('error', 'Unknown')}")

    print()

    # 3. Check services
    print("3. Checking services...")
    command = """
    Get-Service | Where-Object {
        $_.Name -like '*ASUS*' -or
        $_.Name -like '*Aura*' -or
        $_.Name -like '*Lighting*' -or
        $_.Name -like '*Armoury*'
    } | Select-Object Name, Status, StartType | ConvertTo-Json
    """

    result = run_powershell(command)
    if result.get("success"):
        import json
        try:
            services = json.loads(result.get("stdout", "[]"))
            print(f"   Found {len(services)} ASUS/lighting services:")
            for s in services:
                print(f"     {s.get('Name', '')} - {s.get('Status', '')} ({s.get('StartType', '')})")
            results["services"] = services
        except:
            print(f"   Output: {result.get('stdout', '')[:500]}")
    else:
        print(f"   Error: {result.get('error', 'Unknown')}")

    print()

    # 4. Check PnP devices
    print("4. Checking PnP devices...")
    command = """
    Get-PnpDevice | Where-Object {
        $_.FriendlyName -like '*Aura*' -or
        $_.FriendlyName -like '*Lighting*' -or
        $_.FriendlyName -like '*RGB*' -or
        ($_.FriendlyName -like '*ASUS*' -and ($_.FriendlyName -like '*Light*' -or $_.FriendlyName -like '*Aura*'))
    } | Select-Object FriendlyName, Status, Class | ConvertTo-Json
    """

    result = run_powershell(command)
    if result.get("success"):
        import json
        try:
            devices = json.loads(result.get("stdout", "[]"))
            print(f"   Found {len(devices)} lighting devices:")
            for d in devices:
                print(f"     {d.get('FriendlyName', '')} - {d.get('Status', '')} ({d.get('Class', '')})")
            results["devices"] = devices
        except:
            print(f"   Output: {result.get('stdout', '')[:500]}")
    else:
        print(f"   Error: {result.get('error', 'Unknown')}")

    print()

    # 5. Check for other lighting software
    print("5. Checking for other lighting software...")
    command = """
    $software = @('Razer', 'Corsair', 'Logitech', 'SteelSeries', 'MSI', 'Gigabyte');
    $found = @();
    foreach ($sw in $software) {
        $procs = Get-Process | Where-Object { $_.ProcessName -like "*$sw*" };
        if ($procs) {
            $found += $sw;
        }
    }
    if ($found.Count -gt 0) {
        "Found:" + ($found -join ',')
    } else {
        "None"
    }
    """

    result = run_powershell(command)
    if result.get("success"):
        output = result.get("stdout", "").strip()
        print(f"   {output}")
        results["other_software"] = output

    print()
    print("=" * 70)
    print("✅ DIAGNOSTIC COMPLETE")
    print("=" * 70)

    return results


if __name__ == "__main__":
    diagnose_lighting_control()
