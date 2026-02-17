#!/usr/bin/env python3
"""
Network Drive Reconnection Script for Lumina Project

Reconnects all mapped network drives (M: through T:) that may have become disconnected
due to DNS changes, network issues, or system reboots.

Drives:
- M: AI/ML Model Storage (\\\\DS2118PLUS\\AI-Models)
- N: NAS Primary Storage (\\\\DS2118PLUS\\Primary)
- O: Development Resources (\\\\DS2118PLUS\\Development)
- P: Project Backups (\\\\DS2118PLUS\\Backups)
- Q: Cloud Sync Storage (\\\\DS2118PLUS\\CloudSync)
- R: Research & Data (\\\\DS2118PLUS\\Research)
- S: Media & Creative (\\\\DS2118PLUS\\Media)
- T: Archive Storage (\\\\DS2118PLUS\\Archive)
- L: Centralized Logging (\\\\DS2118PLUS\\Logs)
"""

import os
import sys
import subprocess
import platform
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
logger = logging.getLogger("reconnect_network_drives")


# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

class NetworkDriveReconnector:
    """
    Reconnects all Lumina project network drives that may have become disconnected.
    """

    def __init__(self):
        self.drive_mappings = self._define_drive_mappings()
        self.connection_attempts = 3
        self.retry_delay = 5  # seconds

    def _define_drive_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Define all network drive mappings for reconnection"""

        return {
            "M:": {
                "path": r"\\DS2118PLUS\AI-Models",
                "description": "AI/ML Model Storage",
                "username": "backupadm",
                "persistent": True,
                "critical": True
            },
            "N:": {
                "path": r"\\DS2118PLUS\Primary",
                "description": "NAS Primary Storage",
                "username": "backupadm",
                "persistent": True,
                "critical": True
            },
            "O:": {
                "path": r"\\DS2118PLUS\Development",
                "description": "Development Resources",
                "username": "backupadm",
                "persistent": True,
                "critical": True
            },
            "P:": {
                "path": r"\\DS2118PLUS\Backups",
                "description": "Project Backups",
                "username": "backupadm",
                "persistent": True,
                "critical": True
            },
            "Q:": {
                "path": r"\\DS2118PLUS\CloudSync",
                "description": "Cloud Sync Storage",
                "username": "backupadm",
                "persistent": True,
                "critical": False
            },
            "R:": {
                "path": r"\\DS2118PLUS\Research",
                "description": "Research & Data",
                "username": "backupadm",
                "persistent": True,
                "critical": False
            },
            "S:": {
                "path": r"\\DS2118PLUS\Media",
                "description": "Media & Creative",
                "username": "backupadm",
                "persistent": True,
                "critical": False
            },
            "T:": {
                "path": r"\\DS2118PLUS\Archive",
                "description": "Archive Storage",
                "username": "backupadm",
                "persistent": True,
                "critical": False
            },
            "L:": {
                "path": r"\\DS2118PLUS\Logs",
                "description": "Centralized Logging Storage",
                "username": "backupadm",
                "persistent": True,
                "critical": True
            }
        }

    def check_drive_status(self, drive_letter: str) -> Dict[str, Any]:
        """Check the current status of a network drive"""

        try:
            # Use net use to check drive status
            result = subprocess.run(
                ['net', 'use', drive_letter],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                output = result.stdout.lower()
                if 'ok' in output or 'connected' in output:
                    return {
                        "status": "connected",
                        "message": f"{drive_letter} is connected",
                        "connected": True
                    }
                elif 'disconnected' in output or 'unavailable' in output:
                    return {
                        "status": "disconnected",
                        "message": f"{drive_letter} is disconnected",
                        "connected": False
                    }
                else:
                    return {
                        "status": "unknown",
                        "message": f"{drive_letter} status unclear",
                        "connected": False
                    }
            else:
                # Check if drive exists at all
                if os.path.exists(drive_letter):
                    return {
                        "status": "connected",
                        "message": f"{drive_letter} exists and is accessible",
                        "connected": True
                    }
                else:
                    return {
                        "status": "disconnected",
                        "message": f"{drive_letter} does not exist",
                        "connected": False
                    }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Error checking {drive_letter}: {str(e)}",
                "connected": False
            }

    def disconnect_drive(self, drive_letter: str) -> bool:
        """Forcefully disconnect a drive before reconnecting"""

        try:
            result = subprocess.run(
                ['net', 'use', drive_letter, '/delete', '/y'],
                capture_output=True,
                text=True,
                timeout=15
            )

            if result.returncode == 0:
                print(f"✅ Disconnected {drive_letter}")
                return True
            else:
                print(f"⚠️  Could not disconnect {drive_letter} (may not have been connected)")
                return True  # Not an error if already disconnected

        except Exception as e:
            print(f"❌ Error disconnecting {drive_letter}: {e}")
            return False

    def connect_drive(self, drive_letter: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Connect a network drive with retry logic"""

        path = config['path']
        description = config['description']

        for attempt in range(1, self.connection_attempts + 1):
            try:
                print(f"🔗 Connecting {drive_letter} ({description}) - attempt {attempt}/{self.connection_attempts}")

                # Use net use to connect the drive
                cmd = ['net', 'use', drive_letter, path, '/persistent:yes']

                # Add username if specified
                if 'username' in config and config['username']:
                    cmd.extend(['/user:' + config['username']])

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    # Verify connection
                    time.sleep(2)  # Give it a moment to establish

                    if os.path.exists(drive_letter):
                        print(f"✅ Successfully connected {drive_letter} to {path}")
                        return {
                            "success": True,
                            "message": f"Connected {drive_letter} to {path}",
                            "attempts": attempt
                        }
                    else:
                        print(f"⚠️  Connection command succeeded but {drive_letter} not accessible")
                        if attempt < self.connection_attempts:
                            time.sleep(self.retry_delay)
                        continue
                else:
                    error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
                    print(f"❌ Failed to connect {drive_letter}: {error_msg}")

                    if attempt < self.connection_attempts:
                        print(f"⏳ Retrying in {self.retry_delay} seconds...")
                        time.sleep(self.retry_delay)
                    continue

            except subprocess.TimeoutExpired:
                print(f"⏰ Connection attempt {attempt} timed out for {drive_letter}")
                if attempt < self.connection_attempts:
                    time.sleep(self.retry_delay)
                continue
            except Exception as e:
                print(f"❌ Unexpected error connecting {drive_letter}: {e}")
                if attempt < self.connection_attempts:
                    time.sleep(self.retry_delay)
                continue

        return {
            "success": False,
            "message": f"Failed to connect {drive_letter} after {self.connection_attempts} attempts",
            "attempts": self.connection_attempts
        }

    def reconnect_all_drives(self) -> Dict[str, Any]:
        """Reconnect all network drives with comprehensive status reporting"""

        print("🔄 NETWORK DRIVE RECONNECTION FOR LUMINA PROJECT")
        print("=" * 60)

        results = {
            "timestamp": "2026-01-20T18:53:00Z",
            "drives": {},
            "summary": {
                "total_drives": len(self.drive_mappings),
                "already_connected": 0,
                "successfully_connected": 0,
                "failed_connections": 0,
                "critical_failures": 0
            }
        }

        for drive_letter, config in self.drive_mappings.items():
            print(f"\n🔍 Checking {drive_letter} - {config['description']}")
            print("-" * 50)

            # Check current status
            status = self.check_drive_status(drive_letter)
            print(f"   Status: {status['message']}")

            if status['connected']:
                results['summary']['already_connected'] += 1
                results['drives'][drive_letter] = {
                    "status": "already_connected",
                    "description": config['description'],
                    "path": config['path']
                }
                print(f"✅ {drive_letter} is already connected - skipping")
                continue

            # Disconnect if necessary
            print(f"🔌 Disconnecting {drive_letter} (if connected)...")
            self.disconnect_drive(drive_letter)

            # Attempt to connect
            connection_result = self.connect_drive(drive_letter, config)

            if connection_result['success']:
                results['summary']['successfully_connected'] += 1
                results['drives'][drive_letter] = {
                    "status": "connected",
                    "description": config['description'],
                    "path": config['path'],
                    "attempts": connection_result['attempts']
                }
            else:
                results['summary']['failed_connections'] += 1
                if config.get('critical', False):
                    results['summary']['critical_failures'] += 1

                results['drives'][drive_letter] = {
                    "status": "failed",
                    "description": config['description'],
                    "path": config['path'],
                    "error": connection_result['message'],
                    "attempts": connection_result['attempts']
                }

        # Print comprehensive summary
        self._print_summary(results)

        return results

    def _print_summary(self, results: Dict[str, Any]) -> None:
        """Print a comprehensive summary of the reconnection results"""

        print("\n🎉 DRIVE RECONNECTION SUMMARY")
        print("=" * 60)

        summary = results['summary']

        print(f"📊 Total Drives: {summary['total_drives']}")
        print(f"✅ Already Connected: {summary['already_connected']}")
        print(f"🔗 Successfully Connected: {summary['successfully_connected']}")
        print(f"❌ Failed Connections: {summary['failed_connections']}")

        if summary['critical_failures'] > 0:
            print(f"🚨 Critical Failures: {summary['critical_failures']} (immediate attention needed)")

        print("\n📋 DETAILED RESULTS:")
        print("-" * 40)

        for drive_letter, result in results['drives'].items():
            status_icon = {
                "already_connected": "✅",
                "connected": "🔗",
                "failed": "❌"
            }.get(result['status'], "❓")

            print(f"   {status_icon} {drive_letter} - {result['description']}")

            if result['status'] == 'failed':
                print(f"      Error: {result.get('error', 'Unknown error')}")
            elif result['status'] == 'connected':
                print(f"      Path: {result['path']}")
                print(f"      Attempts: {result.get('attempts', 1)}")

        # Success rate calculation
        total_processed = summary['total_drives'] - summary['already_connected']
        if total_processed > 0:
            success_rate = (summary['successfully_connected'] / total_processed) * 100
            print(f"\n📈 Success Rate: {success_rate:.1f}% ({summary['successfully_connected']}/{total_processed} drives reconnected)")

        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        if summary['failed_connections'] > 0:
            print("• Check network connectivity to DS2118PLUS (<NAS_PRIMARY_IP>)")
            print("• Verify NAS is powered on and accessible")
            print("• Confirm backupadm credentials are correct")
            print("• Check firewall settings on pfSense")

        if summary['critical_failures'] > 0:
            print("• CRITICAL: M:, N:, O:, P:, L: drives failed - these are essential for operations")
            print("• Contact network administrator immediately")

        print("• Use 'net use' command to verify drive mappings")
        print("• Check Windows Event Viewer for connection errors")

    def create_powershell_reconnection_script(self) -> str:
        """Create a PowerShell script for manual drive reconnection"""

        ps_script = '''# Lumina Project Network Drive Reconnection Script
# Run this script to reconnect all mapped network drives

param(
    [switch]$Force,
    [switch]$Quiet,
    [int]$MaxRetries = 3
)

$ErrorActionPreference = "Continue"

# Drive mappings configuration
$driveMappings = @(
    @{ DriveLetter = "M:"; NetworkPath = "\\\\DS2118PLUS\\AI-Models"; Description = "AI/ML Model Storage"; Critical = $true },
    @{ DriveLetter = "N:"; NetworkPath = "\\\\DS2118PLUS\\Primary"; Description = "NAS Primary Storage"; Critical = $true },
    @{ DriveLetter = "O:"; NetworkPath = "\\\\DS2118PLUS\\Development"; Description = "Development Resources"; Critical = $true },
    @{ DriveLetter = "P:"; NetworkPath = "\\\\DS2118PLUS\\Backups"; Description = "Project Backups"; Critical = $true },
    @{ DriveLetter = "Q:"; NetworkPath = "\\\\DS2118PLUS\\CloudSync"; Description = "Cloud Sync Storage"; Critical = $false },
    @{ DriveLetter = "R:"; NetworkPath = "\\\\DS2118PLUS\\Research"; Description = "Research & Data"; Critical = $false },
    @{ DriveLetter = "S:"; NetworkPath = "\\\\DS2118PLUS\\Media"; Description = "Media & Creative"; Critical = $false },
    @{ DriveLetter = "T:"; NetworkPath = "\\\\DS2118PLUS\\Archive"; Description = "Archive Storage"; Critical = $false },
    @{ DriveLetter = "L:"; NetworkPath = "\\\\DS2118PLUS\\Logs"; Description = "Centralized Logging Storage"; Critical = $true }
)

function Test-DriveConnection {
    param([string]$DriveLetter)

    try {
        $driveInfo = Get-WmiObject -Query "SELECT * FROM Win32_LogicalDisk WHERE DeviceID = '$DriveLetter'"
        if ($driveInfo -and $driveInfo.ProviderName) {
            return $true
        }
    } catch {
        # Ignore errors
    }
    return $false
}

function Connect-NetworkDrive {
    param(
        [string]$DriveLetter,
        [string]$NetworkPath,
        [string]$Description,
        [bool]$Critical = $false,
        [int]$MaxRetries = 3
    )

    if (-not $Quiet) {
        Write-Host "🔗 Connecting $DriveLetter ($Description)..." -NoNewline
    }

    # Check if already connected
    if ((Test-DriveConnection -DriveLetter $DriveLetter) -and -not $Force) {
        if (-not $Quiet) {
            Write-Host " ALREADY CONNECTED" -ForegroundColor Green
        }
        return $true
    }

    # Disconnect if forcing reconnection
    if ($Force) {
        try {
            net use $DriveLetter /delete /y 2>$null | Out-Null
        } catch {
            # Ignore disconnection errors
        }
    }

    # Attempt connection with retries
    for ($attempt = 1; $attempt -le $MaxRetries; $attempt++) {
        try {
            $net = New-Object -ComObject WScript.Network
            $net.MapNetworkDrive($DriveLetter, $NetworkPath, $true)

            # Verify connection
            Start-Sleep -Seconds 2
            if (Test-DriveConnection -DriveLetter $DriveLetter) {
                if (-not $Quiet) {
                    Write-Host " SUCCESS (attempt $attempt)" -ForegroundColor Green
                }
                return $true
            }
        } catch {
            if ($attempt -eq $MaxRetries) {
                if (-not $Quiet) {
                    Write-Host " FAILED (all $MaxRetries attempts)" -ForegroundColor Red
                    if ($Critical) {
                        Write-Host "   ⚠️  CRITICAL: $Description drive failed to connect" -ForegroundColor Yellow
                    }
                }
                return $false
            }
            Start-Sleep -Seconds ($attempt * 2)  # Exponential backoff
        }
    }

    return $false
}

# Main execution
if (-not $Quiet) {
    Write-Host "🔄 LUMINA PROJECT DRIVE RECONNECTION" -ForegroundColor Cyan
    Write-Host "=" * 50 -ForegroundColor Cyan
    Write-Host "Reconnecting all network drives to DS2118PLUS NAS..." -ForegroundColor Gray
    Write-Host ""
}

$results = @{
    Total = $driveMappings.Count
    Connected = 0
    Failed = 0
    CriticalFailed = 0
}

foreach ($mapping in $driveMappings) {
    $success = Connect-NetworkDrive -DriveLetter $mapping.DriveLetter `
                                   -NetworkPath $mapping.NetworkPath `
                                   -Description $mapping.Description `
                                   -Critical $mapping.Critical `
                                   -MaxRetries $MaxRetries

    if ($success) {
        $results.Connected++
    } else {
        $results.Failed++
        if ($mapping.Critical) {
            $results.CriticalFailed++
        }
    }
}

# Summary
if (-not $Quiet) {
    Write-Host "`n📊 CONNECTION SUMMARY" -ForegroundColor Cyan
    Write-Host "=" * 30 -ForegroundColor Cyan
    Write-Host "Total drives: $($results.Total)" -ForegroundColor Gray
    Write-Host "Connected: $($results.Connected)" -ForegroundColor $(if ($results.Connected -gt 0) { "Green" } else { "Gray" })
    Write-Host "Failed: $($results.Failed)" -ForegroundColor $(if ($results.Failed -gt 0) { "Red" } else { "Gray" })

    if ($results.CriticalFailed -gt 0) {
        Write-Host "Critical failures: $($results.CriticalFailed)" -ForegroundColor Red
        Write-Host "`n🚨 CRITICAL DRIVES FAILED - REQUIRES IMMEDIATE ATTENTION" -ForegroundColor Red
    }

    $successRate = [math]::Round(($results.Connected / $results.Total) * 100, 1)
    Write-Host "Success rate: $successRate%" -ForegroundColor $(if ($successRate -ge 80) { "Green" } elseif ($successRate -ge 50) { "Yellow" } else { "Red" })

    Write-Host "`n💡 TROUBLESHOOTING:" -ForegroundColor Yellow
    Write-Host "• Check network connectivity: ping DS2118PLUS" -ForegroundColor Gray
    Write-Host "• Verify NAS is online: ping <NAS_PRIMARY_IP>" -ForegroundColor Gray
    Write-Host "• Test DNS: nslookup <LOCAL_HOSTNAME>" -ForegroundColor Gray
    Write-Host "• Manual connection: net use M: \\\\DS2118PLUS\\AI-Models /persistent:yes" -ForegroundColor Gray
}

# Return results for scripting
@{
    Total = $results.Total
    Connected = $results.Connected
    Failed = $results.Failed
    CriticalFailed = $results.CriticalFailed
    SuccessRate = [math]::Round(($results.Connected / $results.Total) * 100, 1)
}
'''

        ps_script_path = project_root / "ReconnectDrives.ps1"
        with open(ps_script_path, 'w', encoding='utf-8') as f:
            f.write(ps_script)

        print(f"✅ PowerShell reconnection script created: {ps_script_path.name}")
        return str(ps_script_path)


def main():
    try:
        """Main reconnection function"""
        if platform.system() != 'Windows':
            print("❌ Network drive reconnection is Windows-specific")
            return

        reconnector = NetworkDriveReconnector()

        # Create PowerShell script first
        ps_script = reconnector.create_powershell_reconnection_script()

        # Run the reconnection process
        results = reconnector.reconnect_all_drives()

        # Save results
        output_file = project_root / "DRIVE_RECONNECTION_RESULTS.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n📄 Detailed results saved to: {output_file}")
        print(f"📄 PowerShell script available: {ps_script}")

        # Provide usage instructions
        print("\n🛠️  MANUAL RECONNECTION (if needed):")
        print("PowerShell: .\\ReconnectDrives.ps1")
        print("Force reconnection: .\\ReconnectDrives.ps1 -Force")
        print("Quiet mode: .\\ReconnectDrives.ps1 -Quiet")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    main()