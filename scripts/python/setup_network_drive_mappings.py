#!/usr/bin/env python3
"""
Complete Network Drive Mappings Setup for Lumina Project

Sets up all required and commonly used network drive mappings:
- AI Model Storage (M:)
- NAS Storage (N:, O:, P:)
- Project Backups (Q:)
- Development Resources (R:)
- Cloud Storage (S:)
- Archive Storage (T:)

Customized for RTX 5090 Mobile workstation with DS2118plus NAS.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Any
import logging
logger = logging.getLogger("setup_network_drive_mappings")


# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

class NetworkDriveMapper:
    """
    Comprehensive network drive mapping manager for Lumina project.

    Maps all required drives for:
    - AI/ML development
    - Project storage
    - Backup systems
    - NAS resources
    - Cloud integration
    """

    def __init__(self):
        self.drive_mappings = self._define_drive_mappings()
        self.network_resources = self._define_network_resources()

    def _define_drive_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Define all required drive mappings for the project"""

        return {
            "M:": {
                "description": "AI/ML Model Storage",
                "path": r"\\DS2118PLUS\AI-Models",
                "purpose": "Primary storage for AI models, datasets, checkpoints",
                "subdirs": [
                    "AI/Models/Text", "AI/Models/Vision", "AI/Models/Audio",
                    "stable-diffusion/models", "comfyui/models", "ollama/models",
                    "datasets", "checkpoints", "embeddings"
                ],
                "capacity": "2TB+",
                "backup": "Daily incremental"
            },
            "N:": {
                "description": "NAS Primary Storage",
                "path": r"\\DS2118PLUS\Primary",
                "purpose": "General project storage and documents",
                "subdirs": [
                    "Projects", "Documents", "Media", "Archives",
                    "Software", "Tools", "Scripts"
                ],
                "capacity": "4TB+",
                "backup": "Real-time sync"
            },
            "O:": {
                "description": "Development Resources",
                "path": r"\\DS2118PLUS\Development",
                "purpose": "Development tools, SDKs, libraries, containers",
                "subdirs": [
                    "Docker", "Kubernetes", "SDKs", "Libraries",
                    "VirtualMachines", "DevTools", "IDEs"
                ],
                "capacity": "1TB+",
                "backup": "Weekly full"
            },
            "P:": {
                "description": "Project Backups",
                "path": r"\\DS2118PLUS\Backups",
                "purpose": "Automated backups of all project data",
                "subdirs": [
                    "Daily", "Weekly", "Monthly", "Archives",
                    "Snapshots", "Offsite"
                ],
                "capacity": "2TB+",
                "backup": "Multi-level retention"
            },
            "Q:": {
                "description": "Cloud Sync Storage",
                "path": r"\\DS2118PLUS\CloudSync",
                "purpose": "Synchronized cloud storage (Dropbox, OneDrive, etc.)",
                "subdirs": [
                    "Dropbox", "OneDrive", "GoogleDrive", "Mega",
                    "Sync", "Shared", "Public"
                ],
                "capacity": "500GB+",
                "backup": "Cloud-native"
            },
            "R:": {
                "description": "Research & Data",
                "path": r"\\DS2118PLUS\Research",
                "purpose": "Research data, publications, datasets",
                "subdirs": [
                    "Papers", "Datasets", "Experiments", "Results",
                    "Notebooks", "Presentations", "References"
                ],
                "capacity": "1TB+",
                "backup": "Version controlled"
            },
            "S:": {
                "description": "Media & Creative",
                "path": r"\\DS2118PLUS\Media",
                "purpose": "Media files, creative assets, videos",
                "subdirs": [
                    "Videos", "Images", "Audio", "Graphics",
                    "Projects", "Assets", "Templates"
                ],
                "capacity": "2TB+",
                "backup": "Content-aware"
            },
            "T:": {
                "description": "Archive Storage",
                "path": r"\\DS2118PLUS\Archive",
                "purpose": "Long-term archive storage",
                "subdirs": [
                    "2023", "2024", "2025", "Legacy",
                    "Compliance", "Legal", "Historical"
                ],
                "capacity": "4TB+",
                "backup": "Cold storage"
            }
        }

    def _define_network_resources(self) -> Dict[str, Dict[str, Any]]:
        """Define network resources and their configurations"""

        return {
            "nas_primary": {
                "name": "DS2118PLUS",
                "ip": "<NAS_PRIMARY_IP>",
                "description": "Synology DS2118+ NAS - Primary storage server",
                "services": ["SMB", "NFS", "Docker", "Backup"],
                "volumes": ["AI-Models", "Primary", "Development", "Backups", "CloudSync", "Research", "Media", "Archive"]
            },
            "firewall": {
                "name": "pfSense",
                "ip": "<NAS_IP>",
                "description": "pfSense firewall and router",
                "services": ["DHCP", "DNS", "VPN", "Firewall"],
                "ports": ["22 (SSH)", "80/443 (Web)", "445 (SMB)", "2049 (NFS)"]
            },
            "ultron_cluster": {
                "nodes": [
                    {"name": "RTX5090-Laptop", "ip": "<NAS_IP>", "role": "Primary GPU"},
                    {"name": "RTX3090-Desktop", "ip": "<NAS_PRIMARY_IP>", "role": "Secondary GPU"},
                    {"name": "NAS-CPU-Cluster", "ip": "<NAS_PRIMARY_IP>", "role": "CPU Workers"}
                ],
                "services": ["Ollama", "StableDiffusion", "Docker", "Kubernetes"]
            }
        }

    def map_all_drives(self) -> Dict[str, Any]:
        """Map all required network drives"""

        print("🔗 MAPPING NETWORK DRIVES FOR LUMINA PROJECT")
        print("=" * 60)

        results = {}

        if platform.system() != 'Windows':
            print("❌ Drive mapping only supported on Windows")
            return {"error": "Windows only feature"}

        for drive_letter, config in self.drive_mappings.items():
            print(f"\n🖴 Mapping {drive_letter} - {config['description']}")
            print(f"   Path: {config['path']}")
            print(f"   Purpose: {config['purpose']}")

            success = self._map_drive(drive_letter, config['path'])
            results[drive_letter] = {
                "success": success,
                "description": config['description'],
                "path": config['path'],
                "purpose": config['purpose']
            }

            if success:
                print("   ✅ Successfully mapped")
                # Create subdirectories
                self._create_subdirectories(drive_letter, config.get('subdirs', []))
            else:
                print("   ❌ Failed to map")

        return results

    def _map_drive(self, drive_letter: str, network_path: str) -> bool:
        """Map a specific network drive"""

        try:
            # First, try to disconnect if already mapped
            subprocess.run(['net', 'use', drive_letter, '/delete', '/y'],
                         capture_output=True, timeout=10)

            # Map the drive
            result = subprocess.run([
                'net', 'use', drive_letter, network_path, '/persistent:yes'
            ], capture_output=True, text=True, timeout=15)

            return result.returncode == 0

        except Exception as e:
            print(f"   Error mapping {drive_letter}: {e}")
            return False

    def _create_subdirectories(self, drive_letter: str, subdirs: List[str]):
        """Create required subdirectories on mapped drive"""

        for subdir in subdirs:
            full_path = f"{drive_letter.rstrip(':')}:\\{subdir}"
            try:
                os.makedirs(full_path, exist_ok=True)
                print(f"   📁 Created: {subdir}")
            except Exception as e:
                print(f"   ⚠️  Failed to create {subdir}: {e}")

    def verify_mappings(self) -> Dict[str, Any]:
        """Verify all drive mappings are working"""

        print("\n🔍 VERIFYING DRIVE MAPPINGS")
        print("=" * 40)

        verification_results = {}

        for drive_letter, config in self.drive_mappings.items():
            print(f"\nChecking {drive_letter} - {config['description']}")

            if os.path.exists(drive_letter):
                try:
                    # Test write access
                    test_file = os.path.join(drive_letter, 'test_write.tmp')
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)

                    verification_results[drive_letter] = {
                        "status": "accessible",
                        "write_access": True,
                        "description": config['description']
                    }
                    print("   ✅ Accessible with write permissions")

                except Exception as e:
                    verification_results[drive_letter] = {
                        "status": "read_only",
                        "write_access": False,
                        "error": str(e),
                        "description": config['description']
                    }
                    print(f"   ⚠️  Read-only access: {e}")
            else:
                verification_results[drive_letter] = {
                    "status": "not_mapped",
                    "description": config['description']
                }
                print("   ❌ Not mapped or accessible")

        return verification_results

    def create_powershell_script(self) -> str:
        """Create a PowerShell script for drive mappings"""

        script_content = """# Lumina Project Network Drive Mappings
# Run this script as Administrator to map all required drives

Write-Host "Setting up Lumina Project Network Drives..." -ForegroundColor Green

# Drive mappings
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
    $driveLetter = $drive.Key
    $networkPath = $drive.Value

    Write-Host "Mapping $driveLetter to $networkPath..." -NoNewline

    # Disconnect if already mapped
    try {
        net use $driveLetter /delete /y 2>$null
    } catch {}

    # Map the drive
    try {
        net use $driveLetter $networkPath /persistent:yes
        Write-Host " SUCCESS" -ForegroundColor Green
    } catch {
        Write-Host " FAILED" -ForegroundColor Red
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

Write-Host "`nDrive mapping complete!" -ForegroundColor Green
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
"""

        script_path = project_root / "setup_network_drives.ps1"
        with open(script_path, 'w') as f:
            f.write(script_content)

        return str(script_path)

    def display_drive_map(self):
        """Display a comprehensive drive mapping guide"""

        print("\n🗺️  LUMINA PROJECT DRIVE MAPPING GUIDE")
        print("=" * 60)

        print("\n📍 PRIMARY DRIVE MAPPINGS:")
        print("-" * 40)

        for drive_letter, config in self.drive_mappings.items():
            print(f"\n{drive_letter} → {config['path']}")
            print(f"   {config['description']}")
            print(f"   Purpose: {config['purpose']}")
            print(f"   Capacity: {config['capacity']}")
            print(f"   Backup: {config['backup']}")

            if 'subdirs' in config and config['subdirs']:
                print("   Key Directories:")
                for subdir in config['subdirs'][:5]:  # Show first 5
                    print(f"     • {subdir}")
                if len(config['subdirs']) > 5:
                    print(f"     ... and {len(config['subdirs'])-5} more")

        print("\n🌐 NETWORK RESOURCES:")
        print("-" * 40)

        for resource_name, resource_config in self.network_resources.items():
            resource_title = resource_config.get('name', resource_name.title())
            print(f"\n{resource_title} ({resource_config['ip']})")
            print(f"   {resource_config['description']}")

            if 'services' in resource_config:
                print("   Services:")
                for service in resource_config['services']:
                    print(f"     • {service}")

            if 'volumes' in resource_config:
                print("   Volumes:")
                for volume in resource_config['volumes']:
                    print(f"     • {volume}")

        print("\n🔧 SETUP INSTRUCTIONS:")
        print("-" * 40)
        print("1. Ensure DS2118PLUS is accessible at <NAS_PRIMARY_IP>")
        print("2. Configure SMB shares on NAS for each volume")
        print("3. Run this script as Administrator:")
        print("   PowerShell: .\\setup_network_drives.ps1")
        print("4. Verify mappings with: net use")
        print("5. Create subdirectories as needed")

        print("\n⚡ AUTOMATION:")
        print("-" * 40)
        print("• PowerShell script created: setup_network_drives.ps1")
        print("• Run on startup: Add to Task Scheduler")
        print("• Persistent mappings: /persistent:yes flag used")

    def run_complete_setup(self) -> Dict[str, Any]:
        """Run the complete drive mapping setup"""

        # Map all drives
        mapping_results = self.map_all_drives()

        # Verify mappings
        verification_results = self.verify_mappings()

        # Create PowerShell script
        ps_script_path = self.create_powershell_script()

        # Display guide
        self.display_drive_map()

        # Summary
        successful_mappings = sum(1 for result in mapping_results.values() if result.get('success'))

        print(f"\n🎉 SETUP SUMMARY")
        print("=" * 30)
        print(f"✅ Drive mappings attempted: {len(self.drive_mappings)}")
        print(f"✅ Successful mappings: {successful_mappings}")
        print(f"📄 PowerShell script: {ps_script_path}")

        if successful_mappings == len(self.drive_mappings):
            print("🎯 All drives mapped successfully!")
        else:
            print(f"⚠️  {len(self.drive_mappings) - successful_mappings} drives failed to map")

        return {
            "mappings": mapping_results,
            "verification": verification_results,
            "powershell_script": ps_script_path,
            "network_resources": self.network_resources
        }


def main():
    try:
        """Main setup function"""
        print("🚀 LUMINA PROJECT NETWORK DRIVE MAPPINGS SETUP")
        print("=" * 60)

        drive_mapper = NetworkDriveMapper()
        results = drive_mapper.run_complete_setup()

        # Save results
        output_file = project_root / "NETWORK_DRIVE_SETUP_RESULTS.json"
        with open(output_file, 'w') as f:
            # Convert Path objects to strings for JSON serialization
            json_results = {}
            for key, value in results.items():
                if isinstance(value, dict):
                    json_results[key] = {}
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, Path):
                            json_results[key][sub_key] = str(sub_value)
                        else:
                            json_results[key][sub_key] = sub_value
                else:
                    json_results[key] = str(value) if isinstance(value, Path) else value

            json.dump(json_results, f, indent=2)

        print(f"\n📄 Detailed results saved to: {output_file}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    main()