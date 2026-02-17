#!/usr/bin/env python3
"""
Setup Network Drive Mappings on KAIJU_NO_8

Maps all network drives from this PC to KAIJU_NO_8 (<NAS_IP>) to mirror
the same NAS network drive structure.

This ensures Iron Legion has access to the same network resources as ULTRON.

Tags: #NETWORK #DRIVE_MAPPING #KAIJU #IRON_LEGION @LUMINA
"""

import sys
import subprocess
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SetupKaijuDrives")


class KaijuNetworkDriveMapper:
    """Map network drives on KAIJU_NO_8 to mirror this PC's setup"""

    def __init__(self, kaiju_ip: str = "<NAS_IP>"):
        self.kaiju_ip = kaiju_ip
        self.kaiju_hostname = "KAIJU_NO_8"

        # Network drive mappings (from PowerShell profile and current PC)
        self.drive_mappings = {
            "M:": {
                "path": "\\\\DS2118PLUS\\AI-Models",
                "alt_path": "\\\\<NAS_PRIMARY_IP>\\homes\\mlesn\\Ollama\\models",
                "description": "AI/ML Model Storage",
                "critical": True,
                "models_path": "M:\\Ollama\\models",
                "iron_legion_path": "M:\\Ollama\\models\\iron_legion"
            },
            "N:": {
                "path": "\\\\DS2118PLUS\\Primary",
                "description": "NAS Primary Storage",
                "critical": True
            },
            "O:": {
                "path": "\\\\DS2118PLUS\\Development",
                "description": "Development Resources",
                "critical": True
            },
            "P:": {
                "path": "\\\\DS2118PLUS\\Backups",
                "alt_path": "\\\\<NAS_PRIMARY_IP>\\homes",
                "description": "Project Backups",
                "critical": True
            },
            "Q:": {
                "path": "\\\\DS2118PLUS\\CloudSync",
                "description": "Cloud Sync Storage",
                "critical": False
            },
            "R:": {
                "path": "\\\\DS2118PLUS\\Research",
                "description": "Research & Data",
                "critical": False
            },
            "S:": {
                "path": "\\\\DS2118PLUS\\Media",
                "alt_path": "\\\\<NAS_PRIMARY_IP>\\surveillance",
                "description": "Media & Creative",
                "critical": False
            },
            "T:": {
                "path": "\\\\DS2118PLUS\\Archive",
                "alt_path": "\\\\<NAS_PRIMARY_IP>\\web_packages",
                "description": "Archive Storage",
                "critical": False
            },
            "L:": {
                "path": "\\\\DS2118PLUS\\Logs",
                "description": "Centralized Logging",
                "critical": True
            },
            "B:": {
                "path": "\\\\<NAS_PRIMARY_IP>\\backups",
                "description": "Backups Share",
                "critical": False
            },
            "H:": {
                "path": "\\\\<NAS_PRIMARY_IP>\\home",
                "description": "Home Share",
                "critical": False
            },
            "J:": {
                "path": "\\\\<NAS_PRIMARY_IP>\\jupyter",
                "description": "Jupyter Share",
                "critical": False
            },
            "U:": {
                "path": "\\\\<NAS_PRIMARY_IP>\\ActiveBackupforBusiness",
                "description": "Active Backup Share",
                "critical": False
            },
            "W:": {
                "path": "\\\\<NAS_PRIMARY_IP>\\web",
                "description": "Web Share",
                "critical": False
            }
        }

    def create_powershell_script_for_kaiju(self) -> str:
        """Create PowerShell script to run on KAIJU_NO_8"""

        script_content = f"""# Network Drive Mappings for KAIJU_NO_8
# Run this script on KAIJU_NO_8 (<NAS_IP>) to map all network drives
# Mirrors the drive mappings from the primary workstation

Write-Host "🔗 MAPPING NETWORK DRIVES ON KAIJU_NO_8" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Drive mappings - mirroring primary workstation
$driveMappings = @{{
    "M:" = @{{ Path = "\\\\DS2118PLUS\\AI-Models"; AltPath = "\\\\<NAS_PRIMARY_IP>\\homes\\mlesn\\Ollama\\models"; Critical = $true }};
    "N:" = @{{ Path = "\\\\DS2118PLUS\\Primary"; Critical = $true }};
    "O:" = @{{ Path = "\\\\DS2118PLUS\\Development"; Critical = $true }};
    "P:" = @{{ Path = "\\\\DS2118PLUS\\Backups"; AltPath = "\\\\<NAS_PRIMARY_IP>\\homes"; Critical = $true }};
    "Q:" = @{{ Path = "\\\\DS2118PLUS\\CloudSync"; Critical = $false }};
    "R:" = @{{ Path = "\\\\DS2118PLUS\\Research"; Critical = $false }};
    "S:" = @{{ Path = "\\\\DS2118PLUS\\Media"; AltPath = "\\\\<NAS_PRIMARY_IP>\\surveillance"; Critical = $false }};
    "T:" = @{{ Path = "\\\\DS2118PLUS\\Archive"; AltPath = "\\\\<NAS_PRIMARY_IP>\\web_packages"; Critical = $false }};
    "L:" = @{{ Path = "\\\\DS2118PLUS\\Logs"; Critical = $true }};
    "B:" = @{{ Path = "\\\\<NAS_PRIMARY_IP>\\backups"; Critical = $false }};
    "H:" = @{{ Path = "\\\\<NAS_PRIMARY_IP>\\home"; Critical = $false }};
    "J:" = @{{ Path = "\\\\<NAS_PRIMARY_IP>\\jupyter"; Critical = $false }};
    "U:" = @{{ Path = "\\\\<NAS_PRIMARY_IP>\\ActiveBackupforBusiness"; Critical = $false }};
    "W:" = @{{ Path = "\\\\<NAS_PRIMARY_IP>\\web"; Critical = $false }}
}}

function Test-DriveConnection {{
    param([string]$DriveLetter)
    try {{
        $driveInfo = Get-WmiObject -Query "SELECT * FROM Win32_LogicalDisk WHERE DeviceID = '$DriveLetter'"
        if ($driveInfo -and $driveInfo.ProviderName) {{
            return $true
        }}
    }} catch {{
        return $false
    }}
    return $false
}}

function Map-NetworkDrive {{
    param(
        [string]$DriveLetter,
        [string]$NetworkPath,
        [string]$AltPath = $null,
        [bool]$Critical = $false
    )

    $driveName = $DriveLetter.TrimEnd(':')
    Write-Host "Mapping $DriveLetter..." -NoNewline

    # Check if already mapped
    if (Test-DriveConnection -DriveLetter $DriveLetter) {{
        Write-Host " ALREADY MAPPED" -ForegroundColor Green
        return $true
    }}

    # Disconnect if exists but not connected
    try {{
        net use $DriveLetter /delete /y 2>$null | Out-Null
    }} catch {{
        # Ignore
    }}

    # Try primary path first
    $success = $false
    try {{
        $result = net use $DriveLetter $NetworkPath /persistent:yes 2>&1
        if ($LASTEXITCODE -eq 0) {{
            Start-Sleep -Seconds 2
            if (Test-DriveConnection -DriveLetter $DriveLetter) {{
                $success = $true
            }}
        }}
    }} catch {{
        # Try alternative path if available
        if ($AltPath -and -not $success) {{
            try {{
                $result = net use $DriveLetter $AltPath /persistent:yes 2>&1
                if ($LASTEXITCODE -eq 0) {{
                    Start-Sleep -Seconds 2
                    if (Test-DriveConnection -DriveLetter $DriveLetter) {{
                        $success = $true
                    }}
                }}
            }} catch {{
                # Both failed
            }}
        }}
    }}

    if ($success) {{
        Write-Host " SUCCESS" -ForegroundColor Green
        return $true
    }} else {{
        $status = if ($Critical) {{ "CRITICAL FAILURE" }} else {{ "FAILED" }}
        $color = if ($Critical) {{ "Red" }} else {{ "Yellow" }}
        Write-Host " $status" -ForegroundColor $color
        return $false
    }}
}}

# Map all drives
$results = @{{
    Total = $driveMappings.Count
    Success = 0
    Failed = 0
    CriticalFailed = 0
}}

foreach ($drive in $driveMappings.GetEnumerator()) {{
    $driveLetter = $drive.Key
    $config = $drive.Value

    $success = Map-NetworkDrive -DriveLetter $driveLetter `
                                -NetworkPath $config.Path `
                                -AltPath $config.AltPath `
                                -Critical $config.Critical

    if ($success) {{
        $results.Success++
    }} else {{
        $results.Failed++
        if ($config.Critical) {{
            $results.CriticalFailed++
        }}
    }}
}}

# Create directory structure for Iron Legion models
Write-Host ""
Write-Host "📁 Creating directory structure for Iron Legion models..." -ForegroundColor Cyan

if (Test-DriveConnection -DriveLetter "M:") {{
    $ironLegionPath = "M:\\Ollama\\models\\iron_legion"
    try {{
        New-Item -ItemType Directory -Path $ironLegionPath -Force | Out-Null
        Write-Host "✅ Created: $ironLegionPath" -ForegroundColor Green
    }} catch {{
        Write-Host "⚠️  Could not create $ironLegionPath" -ForegroundColor Yellow
    }}

    # Create subdirectories for each Mark
    $markDirs = @("mark_i", "mark_ii", "mark_iii", "mark_iv", "mark_v", "mark_vi", "mark_vii")
    foreach ($markDir in $markDirs) {{
        $markPath = Join-Path $ironLegionPath $markDir
        try {{
            New-Item -ItemType Directory -Path $markPath -Force | Out-Null
            Write-Host "  ✅ Created: $markPath" -ForegroundColor Gray
        }} catch {{
            Write-Host "  ⚠️  Could not create $markPath" -ForegroundColor Yellow
        }}
    }}
}} else {{
    Write-Host "❌ M: drive not accessible - cannot create Iron Legion directories" -ForegroundColor Red
}}

# Summary
Write-Host ""
Write-Host "📊 MAPPING SUMMARY" -ForegroundColor Cyan
Write-Host "=" * 30 -ForegroundColor Cyan
Write-Host "Total drives: $($results.Total)" -ForegroundColor Gray
Write-Host "Successfully mapped: $($results.Success)" -ForegroundColor Green
Write-Host "Failed: $($results.Failed)" -ForegroundColor $(if ($results.Failed -gt 0) {{ "Red" }} else {{ "Gray" }})

if ($results.CriticalFailed -gt 0) {{
    Write-Host "CRITICAL FAILURES: $($results.CriticalFailed)" -ForegroundColor Red
    Write-Host "⚠️  Critical drives failed - requires immediate attention" -ForegroundColor Yellow
}}

$successRate = [math]::Round(($results.Success / $results.Total) * 100, 1)
Write-Host "Success rate: $successRate%" -ForegroundColor $(if ($successRate -ge 80) {{ "Green" }} elseif ($successRate -ge 50) {{ "Yellow" }} else {{ "Red" }})

Write-Host ""
Write-Host "✅ Network drive mapping complete!" -ForegroundColor Green
Write-Host "💡 Verify with: net use" -ForegroundColor Gray
"""

        script_path = project_root / "scripts" / "powershell" / "Map-KaijuNetworkDrives.ps1"
        script_path.parent.mkdir(parents=True, exist_ok=True)

        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)

        logger.info(f"✅ PowerShell script created: {script_path}")
        return str(script_path)

    def create_deployment_instructions(self) -> str:
        """Create deployment instructions document"""

        instructions_content = f"""# Network Drive Mapping Deployment for KAIJU_NO_8

## 📋 Overview

This document provides instructions for mapping all network drives on KAIJU_NO_8 (<NAS_IP>)
to mirror the drive mappings from the primary workstation.

## 🚀 Deployment Steps

### Step 1: Copy PowerShell Script

Copy the drive mapping script to KAIJU_NO_8:

**From this PC:**
```powershell
copy "C:\\Users\\mlesn\\Dropbox\\my_projects\\.lumina\\scripts\\powershell\\Map-KaijuNetworkDrives.ps1" "\\\\<NAS_IP>\\c$\\Users\\mlesn\\Map-KaijuNetworkDrives.ps1"
```

### Step 2: Execute on KAIJU_NO_8

**On KAIJU_NO_8**, open PowerShell as Administrator and run:

```powershell
powershell.exe -ExecutionPolicy Bypass -File "C:\\Users\\mlesn\\Map-KaijuNetworkDrives.ps1"
```

### Step 3: Verify Mappings

**On KAIJU_NO_8**, verify all drives are mapped:

```powershell
net use
```

### Step 4: Verify Directory Structure

**On KAIJU_NO_8**, verify M drive structure:

```powershell
dir M:\\Ollama\\models
dir M:\\Ollama\\models\\iron_legion
```

## 📊 Expected Drive Mappings

The script will map the following drives:

- **M:** → `\\\\DS2118PLUS\\AI-Models` (AI/ML Model Storage) - CRITICAL
- **N:** → `\\\\DS2118PLUS\\Primary` (NAS Primary Storage) - CRITICAL
- **O:** → `\\\\DS2118PLUS\\Development` (Development Resources) - CRITICAL
- **P:** → `\\\\DS2118PLUS\\Backups` (Project Backups) - CRITICAL
- **Q:** → `\\\\DS2118PLUS\\CloudSync` (Cloud Sync Storage)
- **R:** → `\\\\DS2118PLUS\\Research` (Research & Data)
- **S:** → `\\\\DS2118PLUS\\Media` (Media & Creative)
- **T:** → `\\\\DS2118PLUS\\Archive` (Archive Storage)
- **L:** → `\\\\DS2118PLUS\\Logs` (Centralized Logging) - CRITICAL
- **B:** → `\\\\<NAS_PRIMARY_IP>\\backups` (Backups Share)
- **H:** → `\\\\<NAS_PRIMARY_IP>\\home` (Home Share)
- **J:** → `\\\\<NAS_PRIMARY_IP>\\jupyter` (Jupyter Share)
- **U:** → `\\\\<NAS_PRIMARY_IP>\\ActiveBackupforBusiness` (Active Backup)
- **W:** → `\\\\<NAS_PRIMARY_IP>\\web` (Web Share)

## ✅ Verification Checklist

- [ ] All drives mapped successfully
- [ ] M: drive accessible
- [ ] Directory structure created: `M:\\Ollama\\models\\iron_legion\\`
- [ ] All Mark subdirectories created
- [ ] Iron Legion can access M drive

## 🎯 Next Steps

After drive mapping is complete:
1. Configure Iron Legion services to use M drive
2. Move existing models to M drive (if needed)
3. Update service configurations
4. Test model loading from M drive
"""

        instructions_file = project_root / "docs" / "KAJU_NO_8_DRIVE_MAPPING_DEPLOYMENT.md"
        instructions_file.parent.mkdir(parents=True, exist_ok=True)

        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write(instructions_content)

        logger.info(f"✅ Deployment instructions created: {instructions_file}")
        return str(instructions_file)

    def generate_setup_instructions(self) -> Dict[str, Any]:
        """Generate setup instructions"""

        instructions = {
            "kaiju_ip": self.kaiju_ip,
            "kaiju_hostname": self.kaiju_hostname,
            "drive_mappings": self.drive_mappings,
            "setup_steps": [
                "1. Copy Map-KaijuNetworkDrives.ps1 to KAIJU_NO_8",
                "2. Run PowerShell as Administrator on KAIJU_NO_8",
                "3. Execute: powershell.exe -ExecutionPolicy Bypass -File Map-KaijuNetworkDrives.ps1",
                "4. Verify mappings with: net use",
                "5. Verify M: drive structure: dir M:\\Ollama\\models"
            ],
            "directory_structure": {
                "M:\\Ollama\\models": "Root for all Ollama models",
                "M:\\Ollama\\models\\iron_legion": "Iron Legion cluster models",
                "M:\\Ollama\\models\\iron_legion\\mark_i": "Mark I model files",
                "M:\\Ollama\\models\\iron_legion\\mark_ii": "Mark II model files",
                # ... etc for all marks
            },
            "verification": [
                "net use",
                "dir M:\\Ollama\\models",
                "dir M:\\Ollama\\models\\iron_legion"
            ]
        }

        return instructions


def main():
    try:
        """Main setup function"""
        import argparse

        parser = argparse.ArgumentParser(description="Setup Network Drives on KAIJU_NO_8")
        parser.add_argument("--kaiju-ip", type=str, default="<NAS_IP>", help="KAIJU_NO_8 IP address")
        parser.add_argument("--generate-script", action="store_true", help="Generate PowerShell script")
        parser.add_argument("--instructions", action="store_true", help="Show setup instructions")

        args = parser.parse_args()

        mapper = KaijuNetworkDriveMapper(kaiju_ip=args.kaiju_ip)

        if args.generate_script or not any([args.generate_script, args.instructions]):
            logger.info("=" * 80)
            logger.info("🔗 SETTING UP NETWORK DRIVE MAPPINGS FOR KAIJU_NO_8")
            logger.info("=" * 80)

            # Generate PowerShell script
            ps_script = mapper.create_powershell_script_for_kaiju()
            logger.info(f"✅ PowerShell script created: {ps_script}")

            # Generate deployment instructions
            instructions_file = mapper.create_deployment_instructions()
            logger.info(f"✅ Deployment instructions created: {instructions_file}")

            # Generate instructions
            instructions = mapper.generate_setup_instructions()

            # Save instructions
            instructions_file = project_root / "data" / "kaiju_network_drive_setup.json"
            instructions_file.parent.mkdir(parents=True, exist_ok=True)
            with open(instructions_file, 'w', encoding='utf-8') as f:
                json.dump(instructions, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Instructions saved: {instructions_file}")

            if args.instructions:
                print("\n📋 SETUP INSTRUCTIONS:")
                print("=" * 60)
                for step in instructions["setup_steps"]:
                    print(f"  {step}")

        elif args.instructions:
            instructions = mapper.generate_setup_instructions()
            print("\n📋 SETUP INSTRUCTIONS:")
            print("=" * 60)
            for step in instructions["setup_steps"]:
                print(f"  {step}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":

    main()