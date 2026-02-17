#!/usr/bin/env python3
"""
Permanent Network Drive Mappings Setup for Lumina Project

Creates persistent, permanent drive mappings that survive reboots and work on all local hosts.
Includes Windows Registry integration, Scheduled Tasks, and Group Policy support.
"""

import os
import sys
import subprocess
import platform
import winreg as reg
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
logger = logging.getLogger("setup_permanent_drive_mappings")


# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

class PermanentDriveMapper:
    """
    Creates permanent, persistent network drive mappings for Lumina project.

    Implements multiple persistence mechanisms:
    - Windows Registry entries
    - Scheduled Tasks at startup
    - Group Policy integration
    - PowerShell profile integration
    """

    def __init__(self):
        self.drive_mappings = self._define_drive_mappings()
        self.registry_paths = {
            "current_user": r"Network",
            "local_machine": r"SYSTEM\CurrentControlSet\Control\NetworkProvider\LanmanWorkstation\Drives"
        }

    def _define_drive_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Define all required drive mappings for permanent setup"""

        return {
            "M:": {
                "description": "AI/ML Model Storage",
                "path": r"\\DS2118PLUS\AI-Models",
                "username": "backupadm",
                "persistent": True,
                "restore_on_startup": True
            },
            "N:": {
                "description": "NAS Primary Storage",
                "path": r"\\DS2118PLUS\Primary",
                "username": "backupadm",
                "persistent": True,
                "restore_on_startup": True
            },
            "O:": {
                "description": "Development Resources",
                "path": r"\\DS2118PLUS\Development",
                "username": "backupadm",
                "persistent": True,
                "restore_on_startup": True
            },
            "P:": {
                "description": "Project Backups",
                "path": r"\\DS2118PLUS\Backups",
                "username": "backupadm",
                "persistent": True,
                "restore_on_startup": True
            },
            "Q:": {
                "description": "Cloud Sync Storage",
                "path": r"\\DS2118PLUS\CloudSync",
                "username": "backupadm",
                "persistent": True,
                "restore_on_startup": True
            },
            "R:": {
                "description": "Research & Data",
                "path": r"\\DS2118PLUS\Research",
                "username": "backupadm",
                "persistent": True,
                "restore_on_startup": True
            },
            "S:": {
                "description": "Media & Creative",
                "path": r"\\DS2118PLUS\Media",
                "username": "backupadm",
                "persistent": True,
                "restore_on_startup": True
            },
            "T:": {
                "description": "Archive Storage",
                "path": r"\\DS2118PLUS\Archive",
                "username": "backupadm",
                "persistent": True,
                "restore_on_startup": True
            }
        }

    def create_registry_entries(self) -> Dict[str, Any]:
        """Create Windows Registry entries for permanent drive mappings"""

        print("🔧 CREATING REGISTRY ENTRIES FOR PERMANENT MAPPINGS")
        print("=" * 60)

        results = {}

        try:
            # Open the Network key in HKEY_CURRENT_USER
            key_path = r"Network"
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_WRITE)

            for drive_letter, config in self.drive_mappings.items():
                drive_key = drive_letter.rstrip(':')

                try:
                    # Create subkey for each drive
                    drive_subkey = reg.CreateKey(key, drive_key)

                    # Set connection type and provider
                    reg.SetValueEx(drive_subkey, "ConnectionType", 0, reg.REG_DWORD, 1)
                    reg.SetValueEx(drive_subkey, "DeferFlags", 0, reg.REG_DWORD, 4)
                    reg.SetValueEx(drive_subkey, "ProviderName", 0, reg.REG_SZ, "Microsoft Windows Network")
                    reg.SetValueEx(drive_subkey, "ProviderType", 0, reg.REG_DWORD, 0x20000)
                    reg.SetValueEx(drive_subkey, "RemotePath", 0, reg.REG_SZ, config['path'])
                    reg.SetValueEx(drive_subkey, "UserName", 0, reg.REG_SZ, config['username'])

                    reg.CloseKey(drive_subkey)

                    results[drive_letter] = {"status": "created", "method": "registry"}
                    print(f"✅ Registry entry created for {drive_letter}")

                except Exception as e:
                    results[drive_letter] = {"status": "failed", "error": str(e)}
                    print(f"❌ Failed to create registry entry for {drive_letter}: {e}")

            reg.CloseKey(key)

        except Exception as e:
            print(f"❌ Failed to access registry: {e}")
            return {"error": f"Registry access failed: {e}"}

        return results

    def create_startup_script(self) -> str:
        """Create a startup script that runs at system boot"""

        startup_script = rf'''# Lumina Project Permanent Drive Mappings
# This script runs at system startup to ensure all network drives are mapped

param(
    [switch]$Force,
    [switch]$Quiet
)

$ErrorActionPreference = "Continue"

# Function to map drives with retry logic
function Map-NetworkDrive {{
    param(
        [string]$DriveLetter,
        [string]$NetworkPath,
        [string]$Description,
        [int]$MaxRetries = 3
    )

    if (-not $Quiet) {{
        Write-Host "Mapping $DriveLetter ($Description)..." -NoNewline
    }}

    for ($i = 1; $i -le $MaxRetries; $i++) {{
        try {{
            # Check if drive is already mapped
            $existing = Get-PSDrive | Where-Object {{ $_.Name -eq $DriveLetter.TrimEnd(':') }}
            if ($existing) {{
                if (-not $Quiet) {{
                    Write-Host " ALREADY MAPPED" -ForegroundColor Yellow
                }}
                return $true
            }}

            # Map the drive
            $net = New-Object -ComObject WScript.Network
            $net.MapNetworkDrive($DriveLetter, $NetworkPath, $true)

            # Verify mapping
            Start-Sleep -Seconds 2
            $verify = Get-PSDrive | Where-Object {{ $_.Name -eq $DriveLetter.TrimEnd(':') }}
            if ($verify) {{
                if (-not $Quiet) {{
                    Write-Host " SUCCESS" -ForegroundColor Green
                }}
                return $true
            }}
        }}
        catch {{
            if ($i -eq $MaxRetries) {{
                if (-not $Quiet) {{
                    Write-Host " FAILED (attempt $i/$MaxRetries)" -ForegroundColor Red
                }}
            }} else {{
                Start-Sleep -Seconds ($i * 5)  # Exponential backoff
            }}
        }}
    }}

    return $false
}}

# Drive mappings configuration
$driveMappings = @(
    @{{ DriveLetter = "M:"; NetworkPath = "\\DS2118PLUS\AI-Models"; Description = "AI/ML Model Storage" }},
    @{{ DriveLetter = "N:"; NetworkPath = "\\DS2118PLUS\Primary"; Description = "NAS Primary Storage" }},
    @{{ DriveLetter = "O:"; NetworkPath = "\\DS2118PLUS\Development"; Description = "Development Resources" }},
    @{{ DriveLetter = "P:"; NetworkPath = "\\DS2118PLUS\Backups"; Description = "Project Backups" }},
    @{{ DriveLetter = "Q:"; NetworkPath = "\\DS2118PLUS\CloudSync"; Description = "Cloud Sync Storage" }},
    @{{ DriveLetter = "R:"; NetworkPath = "\\DS2118PLUS\Research"; Description = "Research & Data" }},
    @{{ DriveLetter = "S:"; NetworkPath = "\\DS2118PLUS\Media"; Description = "Media & Creative" }},
    @{{ DriveLetter = "T:"; NetworkPath = "\\DS2118PLUS\Archive"; Description = "Archive Storage" }}
)

if (-not $Quiet) {{
    Write-Host "🔗 LUMINA PROJECT DRIVE MAPPINGS STARTUP" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Cyan
}}

# Map all drives
$mappedCount = 0
$totalCount = $driveMappings.Count

foreach ($mapping in $driveMappings) {{
    if (Map-NetworkDrive -DriveLetter $mapping.DriveLetter -NetworkPath $mapping.NetworkPath -Description $mapping.Description -Quiet:$Quiet) {{
        $mappedCount++
    }}
}}

if (-not $Quiet) {{
    Write-Host "`n📊 MAPPING SUMMARY: $mappedCount/$totalCount drives successfully mapped" -ForegroundColor Cyan

    if ($mappedCount -eq $totalCount) {{
        Write-Host "✅ All drives mapped successfully!" -ForegroundColor Green
    }} else {{
        Write-Host "⚠️  Some drives failed to map. They will retry on next login." -ForegroundColor Yellow
    }}
}}

# Return success status
exit ($mappedCount -eq $totalCount ? 0 : 1)
'''

        startup_script_path = project_root / "LuminaDriveMappings.ps1"
        with open(startup_script_path, 'w', encoding='utf-8') as f:
            f.write(startup_script)

        return str(startup_script_path)

    def create_scheduled_task(self, script_path: str) -> Dict[str, Any]:
        """Create a Windows Scheduled Task that runs the startup script"""

        print("\n⏰ CREATING SCHEDULED TASK FOR STARTUP MAPPINGS")
        print("-" * 50)

        task_name = "Lumina Network Drive Mappings"
        task_xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mitask">
  <RegistrationInfo>
    <Description>Ensures Lumina project network drives are mapped at system startup</Description>
    <Author>SYSTEM</Author>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
      <Delay>PT30S</Delay>
    </LogonTrigger>
    <BootTrigger>
      <Enabled>true</Enabled>
      <Delay>PT2M</Delay>
    </BootTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-18</UserId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>true</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT10M</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe</Command>
      <Arguments>-ExecutionPolicy Bypass -File "{script_path}" -Quiet</Arguments>
    </Exec>
  </Actions>
</Task>'''

        task_xml_path = project_root / "LuminaDriveMappings.xml"
        with open(task_xml_path, 'w', encoding='utf-16') as f:
            f.write(task_xml)

        # Create the scheduled task
        try:
            result = subprocess.run([
                'schtasks', '/create', '/tn', task_name, '/xml', str(task_xml_path), '/f'
            ], capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                print("✅ Scheduled Task created successfully")
                print(f"   Task Name: {task_name}")
                print("   Triggers: At logon + At startup (with delays)")
                print("   Network Required: Yes")
                return {"status": "created", "task_name": task_name, "xml_path": str(task_xml_path)}
            else:
                print(f"❌ Failed to create scheduled task: {result.stderr}")
                return {"status": "failed", "error": result.stderr}

        except Exception as e:
            print(f"❌ Error creating scheduled task: {e}")
            return {"status": "error", "error": str(e)}

    def create_group_policy_script(self) -> str:
        """Create a Group Policy login script"""

        gp_script = '''@echo off
REM Lumina Project Network Drive Mappings - Group Policy Login Script
REM This script runs when users log in via Group Policy

echo Mapping Lumina project network drives...

REM Drive mappings with error handling
net use M: "\\\\DS2118PLUS\\AI-Models" /persistent:yes 2>nul
if %errorlevel% neq 0 echo Failed to map M: drive

net use N: "\\\\DS2118PLUS\\Primary" /persistent:yes 2>nul
if %errorlevel% neq 0 echo Failed to map N: drive

net use O: "\\\\DS2118PLUS\\Development" /persistent:yes 2>nul
if %errorlevel% neq 0 echo Failed to map O: drive

net use P: "\\\\DS2118PLUS\\Backups" /persistent:yes 2>nul
if %errorlevel% neq 0 echo Failed to map P: drive

net use Q: "\\\\DS2118PLUS\\CloudSync" /persistent:yes 2>nul
if %errorlevel% neq 0 echo Failed to map Q: drive

net use R: "\\\\DS2118PLUS\\Research" /persistent:yes 2>nul
if %errorlevel% neq 0 echo Failed to map R: drive

net use S: "\\\\DS2118PLUS\\Media" /persistent:yes 2>nul
if %errorlevel% neq 0 echo Failed to map S: drive

net use T: "\\\\DS2118PLUS\\Archive" /persistent:yes 2>nul
if %errorlevel% neq 0 echo Failed to map T: drive

echo Drive mapping complete.
exit /b 0
'''

        gp_script_path = project_root / "LuminaGPLogin.bat"
        with open(gp_script_path, 'w') as f:
            f.write(gp_script)

        return str(gp_script_path)

    def update_powershell_profile(self) -> Optional[str]:
        """Update PowerShell profile to include drive mappings"""

        print("\n🔧 UPDATING POWERSHELL PROFILE")
        print("-" * 40)

        try:
            # Get PowerShell profile path
            result = subprocess.run([
                'powershell', '-Command', '$PROFILE'
            ], capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                profile_path = result.stdout.strip()
                print(f"PowerShell profile: {profile_path}")

                # Check if profile exists, create if not
                if not os.path.exists(profile_path):
                    os.makedirs(os.path.dirname(profile_path), exist_ok=True)
                    with open(profile_path, 'w') as f:
                        f.write("# PowerShell Profile\n")

                # Read existing profile
                with open(profile_path, 'r') as f:
                    profile_content = f.read()

                # Add drive mapping function if not present
                if "function Map-LuminaDrives" not in profile_content:
                    mapping_function = '''
# Lumina Project Drive Mappings
function Map-LuminaDrives {
    param([switch]$Force)

    Write-Host "🔗 Mapping Lumina project drives..." -ForegroundColor Cyan

    $driveMappings = @{
        "M:" = "\\\\DS2118PLUS\\AI-Models"
        "N:" = "\\\\DS2118PLUS\\Primary"
        "O:" = "\\\\DS2118PLUS\\Development"
        "P:" = "\\\\DS2118PLUS\\Backups"
        "Q:" = "\\\\DS2118PLUS\\CloudSync"
        "R:" = "\\\\DS2118PLUS\\Research"
        "S:" = "\\\\DS2118PLUS\\Media"
        "T:" = "\\\\DS2118PLUS\\Archive"
    }

    foreach ($drive in $driveMappings.GetEnumerator()) {
        $existing = Get-PSDrive | Where-Object { $_.Name -eq $drive.Key.TrimEnd(':') }
        if (-not $existing -or $Force) {
            try {
                New-PSDrive -Name $drive.Key.TrimEnd(':') -PSProvider FileSystem -Root $drive.Value -Persist -ErrorAction Stop
                Write-Host "  ✅ Mapped $($drive.Key)" -ForegroundColor Green
            } catch {
                Write-Host "  ❌ Failed to map $($drive.Key): $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }
}

# Auto-map drives on profile load (uncomment to enable)
# Map-LuminaDrives
'''

                    with open(profile_path, 'a') as f:
                        f.write(mapping_function)

                    print("✅ PowerShell profile updated with drive mapping function")
                    return profile_path
                else:
                    print("✅ PowerShell profile already contains drive mapping function")
                    return profile_path
            else:
                print("❌ Could not determine PowerShell profile path")
                return None

        except Exception as e:
            print(f"❌ Error updating PowerShell profile: {e}")
            return None

    def run_complete_setup(self) -> Dict[str, Any]:
        """Run the complete permanent drive mapping setup"""

        print("🔒 PERMANENT NETWORK DRIVE MAPPINGS SETUP")
        print("=" * 60)
        print("Creating multiple persistence mechanisms for all local hosts...")

        results = {
            "timestamp": "2026-01-20T18:31:00Z",
            "persistence_methods": []
        }

        # 1. Create Registry entries
        registry_results = self.create_registry_entries()
        results["persistence_methods"].append({
            "method": "windows_registry",
            "description": "HKCU Network registry entries",
            "status": "completed" if "error" not in registry_results else "failed",
            "details": registry_results
        })

        # 2. Create startup PowerShell script
        startup_script_path = self.create_startup_script()
        results["persistence_methods"].append({
            "method": "powershell_startup_script",
            "description": "PowerShell script with retry logic",
            "status": "created",
            "path": startup_script_path
        })

        # 3. Create Scheduled Task
        task_results = self.create_scheduled_task(startup_script_path)
        results["persistence_methods"].append({
            "method": "scheduled_task",
            "description": "Windows Task Scheduler (logon + startup)",
            "status": task_results.get("status", "unknown"),
            "task_name": task_results.get("task_name", "Unknown")
        })

        # 4. Create Group Policy script
        gp_script_path = self.create_group_policy_script()
        results["persistence_methods"].append({
            "method": "group_policy_script",
            "description": "Batch script for GPO deployment",
            "status": "created",
            "path": gp_script_path
        })

        # 5. Update PowerShell profile
        profile_path = self.update_powershell_profile()
        results["persistence_methods"].append({
            "method": "powershell_profile",
            "description": "PowerShell profile integration",
            "status": "updated" if profile_path else "failed",
            "path": profile_path
        })

        # Summary
        print("\n🎉 PERMANENT DRIVE MAPPINGS SETUP COMPLETE")
        print("=" * 60)

        successful_methods = sum(1 for method in results["persistence_methods"] if method["status"] in ["created", "completed", "updated"])
        total_methods = len(results["persistence_methods"])

        print(f"✅ Persistence methods: {successful_methods}/{total_methods} successfully configured")

        print("\n🔄 PERSISTENCE MECHANISMS IMPLEMENTED:")
        for method in results["persistence_methods"]:
            status_icon = "✅" if method["status"] in ["created", "completed", "updated"] else "❌"
            print(f"   {status_icon} {method['method']}: {method['description']}")

        print("\n🚀 ACTIVATION METHODS:")
        print("1. Registry: Active immediately")
        print("2. Scheduled Task: Runs at logon + startup")
        print("3. PowerShell Profile: Run 'Map-LuminaDrives' command")
        print("4. Group Policy: Deploy via GPO for enterprise")

        print("\n💡 MANUAL ACTIVATION:")
        print("• Run PowerShell script: .\\LuminaDriveMappings.ps1")
        print("• Use PowerShell function: Map-LuminaDrives")
        print("• Force remap: Map-LuminaDrives -Force")

        print("\n⚡ FEATURES:")
        print("• Automatic retry with exponential backoff")
        print("• Network availability checking")
        print("• Silent operation with -Quiet flag")
        print("• Comprehensive error handling")

        return results


def main():
    try:
        """Main setup function"""
        if platform.system() != 'Windows':
            print("❌ Permanent drive mappings are Windows-specific")
            return

        drive_mapper = PermanentDriveMapper()
        results = drive_mapper.run_complete_setup()

        # Save results
        output_file = project_root / "PERMANENT_DRIVE_SETUP_RESULTS.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n📄 Detailed results saved to: {output_file}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    main()