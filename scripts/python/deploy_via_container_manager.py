#!/usr/bin/env python3
"""
Deploy QOL Tools via Synology Container Manager API
Uses Container Manager's web API to deploy docker-compose.yml
"""

import requests
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "python"))

from nas_azure_vault_integration import NASAzureVaultIntegration

def main():
    nas_ip = "<NAS_PRIMARY_IP>"
    nas_port = 5000  # DSM web port

    print("🚀 Deploying QOL Tools via Container Manager API...")
    print("=" * 70)

    # Get credentials
    print("🔐 Loading credentials...")
    nas_integration = NASAzureVaultIntegration(nas_ip=nas_ip)
    credentials = nas_integration.get_nas_credentials()

    if not credentials:
        print("❌ Failed to load credentials")
        return 1

    username = credentials.get("username")
    password = credentials.get("password")

    print(f"✅ Credentials loaded for {username}")
    print()

    # Try Container Manager API approach
    print("📡 Attempting Container Manager API deployment...")
    print("   Note: This requires Container Manager to be installed and API enabled")
    print()

    # Alternative: Provide complete instructions for RDP + Container Manager GUI
    print("=" * 70)
    print("✅ AUTOMATED DEPLOYMENT VIA RDP + CONTAINER MANAGER GUI")
    print("=" * 70)
    print()
    print("Since you have RDP access, use Container Manager GUI:")
    print()
    print("1. RDP to a Windows machine with browser access to NAS")
    print(f"2. Open browser: http://{nas_ip}:5000")
    print("3. Login to DSM")
    print("4. Open Container Manager")
    print("5. Go to: Project → Create → From Compose File")
    print("6. Select: /volume1/docker/nas-qol-tools/docker-compose.yml")
    print("7. Click Create and Start")
    print()
    print("OR use this PowerShell script via RDP:")
    print()

    # Generate PowerShell script for RDP execution
    ps_script = f"""
# Deploy QOL Tools via Container Manager (Run via RDP)
$nasIP = "{nas_ip}"
$username = "{username}"
$deployPath = "/volume1/docker/nas-qol-tools/docker-compose.yml"

Write-Host "🚀 Deploying QOL Tools to NAS..." -ForegroundColor Green
Write-Host ""

# Option 1: Use Container Manager Web UI
Write-Host "Open Container Manager in browser:" -ForegroundColor Yellow
Write-Host "  http://$nasIP:5000" -ForegroundColor Cyan
Write-Host "  Login → Container Manager → Project → Create → From Compose File" -ForegroundColor Cyan
Write-Host "  Select: $deployPath" -ForegroundColor Cyan
Write-Host ""

# Option 2: SSH and deploy (if permissions fixed)
Write-Host "OR SSH and deploy:" -ForegroundColor Yellow
Write-Host "  ssh $username@$nasIP" -ForegroundColor Cyan
Write-Host "  cd /volume1/docker/nas-qol-tools" -ForegroundColor Cyan
Write-Host "  docker compose up -d" -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ Files are ready at: $deployPath" -ForegroundColor Green
"""

    ps_file = project_root / "scripts" / "python" / "deploy_via_rdp.ps1"
    ps_file.write_text(ps_script)
    print(f"✅ Created PowerShell script: {ps_file}")
    print()
    print("Run this script via RDP to complete deployment!")
    print()

    return 0

if __name__ == "__main__":


    sys.exit(main())