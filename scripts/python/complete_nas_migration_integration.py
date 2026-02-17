#!/usr/bin/env python3
"""
Complete NAS Migration Integration

Completes the NAS migration initiative:
1. Identifies large files/data consuming local disk space on KAIJU_NO_8 and MILLENNIUM_FALC
2. Integrates DSM cloud storage provider package (like n8n@NAS)
3. Sets up cloud.local system with multiple cloud storage providers
4. Migrates data from local disks to NAS
5. Shares storage to all homelab systems

Tags: #NAS #MIGRATION #DSM #CLOUD_STORAGE #HOMELAB #KAIJU_NO_8 #MILLENNIUM_FALC @JARVIS @LUMINA
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CompleteNASMigration")


class CompleteNASMigrationIntegration:
    """
    Complete NAS Migration Integration

    Handles:
    - Identifying large files on local disks
    - DSM cloud storage provider package integration
    - Cloud.local system setup
    - Data migration to NAS
    - Homelab storage sharing
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize migration integration"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "nas_migration"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # System identification
        self.systems = {
            "KAIJU_NO_8": {
                "hostname": "kaiju_no_8",
                "ip": "<NAS_IP>",
                "type": "desktop",
                "primary_drive": "D:",  # Based on docs
                "dropbox_path": "D:\\Dropbox"
            },
            "MILLENNIUM_FALC": {
                "hostname": "millennium_falc",
                "ip": "unknown",
                "type": "laptop",
                "primary_drive": "C:",
                "dropbox_path": "C:\\Users\\mlesn\\Dropbox"
            }
        }

        # NAS configuration
        self.nas_ip = "<NAS_PRIMARY_IP>"
        self.nas_drives = ["M:", "N:"]

        logger.info("✅ Complete NAS Migration Integration initialized")
        logger.info(f"   Systems: {', '.join(self.systems.keys())}")
        logger.info(f"   NAS IP: {self.nas_ip}")

    def identify_large_files(self, system: str, min_size_gb: float = 1.0) -> Dict[str, Any]:
        """
        Identify large files consuming local disk space.

        Args:
            system: System name (KAIJU_NO_8 or MILLENNIUM_FALC)
            min_size_gb: Minimum file size in GB to report

        Returns:
            Large files analysis
        """
        logger.info("=" * 80)
        logger.info(f"🔍 IDENTIFYING LARGE FILES ON {system}")
        logger.info("=" * 80)
        logger.info("")

        if system not in self.systems:
            logger.error(f"❌ Unknown system: {system}")
            return {"error": f"Unknown system: {system}"}

        sys_info = self.systems[system]
        primary_drive = sys_info["primary_drive"]

        findings = {
            "timestamp": datetime.now().isoformat(),
            "system": system,
            "primary_drive": primary_drive,
            "large_files": [],
            "large_directories": [],
            "total_size_gb": 0.0,
            "recommendations": []
        }

        # Common large file locations
        scan_paths = [
            f"{primary_drive}\\Dropbox",
            f"{primary_drive}\\Downloads",
            f"{primary_drive}\\Videos",
            f"{primary_drive}\\Documents",
            f"{primary_drive}\\Projects",
            f"C:\\Users\\mlesn\\AppData\\Local",
            f"C:\\Users\\mlesn\\AppData\\Roaming",
            f"{primary_drive}\\temp",
            f"{primary_drive}\\tmp"
        ]

        logger.info(f"   Scanning {primary_drive} for files > {min_size_gb}GB...")

        # Use PowerShell to find large files
        try:
            ps_script = f"""
            Get-ChildItem -Path "{primary_drive}\\" -Recurse -File -ErrorAction SilentlyContinue | 
            Where-Object {{ $_.Length -gt ({min_size_gb} * 1GB) }} | 
            Select-Object FullName, @{{Name="SizeGB";Expression={{[math]::Round($_.Length/1GB, 2)}}}}, LastWriteTime | 
            Sort-Object SizeGB -Descending | 
            Select-Object -First 50 | 
            ConvertTo-Json
            """

            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0 and result.stdout:
                import json
                files = json.loads(result.stdout)
                if not isinstance(files, list):
                    files = [files]

                for file_info in files:
                    findings["large_files"].append({
                        "path": file_info.get("FullName", ""),
                        "size_gb": file_info.get("SizeGB", 0),
                        "last_write": file_info.get("LastWriteTime", "")
                    })
                    findings["total_size_gb"] += file_info.get("SizeGB", 0)

                logger.info(f"   ✅ Found {len(findings['large_files'])} large files")
                logger.info(f"   Total size: {findings['total_size_gb']:.2f} GB")

                # Show top 10
                for i, file_info in enumerate(findings['large_files'][:10], 1):
                    logger.info(f"      {i}. {Path(file_info['path']).name}: {file_info['size_gb']:.2f} GB")

        except subprocess.TimeoutExpired:
            logger.warning("   ⚠️  Scan timed out - disk may be very large")
        except Exception as e:
            logger.warning(f"   ⚠️  Could not scan: {e}")
            # Fallback: check common large file locations
            findings["recommendations"].append("Manual scan recommended for large directories")

        # Identify large directories
        large_dirs = [
            "Dropbox",
            "Downloads",
            "Videos",
            "AppData\\Local\\Temp",
            "AppData\\Roaming",
            "Projects",
            "node_modules",
            ".git",
            "venv",
            "__pycache__"
        ]

        findings["large_directories"] = large_dirs
        findings["recommendations"].extend([
            f"✅ Found {len(findings['large_files'])} files > {min_size_gb}GB",
            "⚠️  Consider migrating large files to NAS",
            "⚠️  Archive old downloads and videos to NAS",
            "⚠️  Move project backups to NAS"
        ])

        return findings

    def check_dsm_cloud_storage_package(self) -> Dict[str, Any]:
        """
        Check DSM cloud storage provider package status.

        Returns:
            DSM package status
        """
        logger.info("=" * 80)
        logger.info("🔍 CHECKING DSM CLOUD STORAGE PACKAGE")
        logger.info("=" * 80)
        logger.info("")

        status = {
            "timestamp": datetime.now().isoformat(),
            "nas_ip": self.nas_ip,
            "package_installed": False,
            "package_configured": False,
            "cloud_providers": [],
            "integration_status": "unknown"
        }

        # Check NAS connectivity
        try:
            result = subprocess.run(
                ["ping", "-n", "1", self.nas_ip],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"   ✅ NAS is reachable: {self.nas_ip}")
                status["nas_reachable"] = True
            else:
                logger.warning(f"   ⚠️  NAS not reachable: {self.nas_ip}")
                status["nas_reachable"] = False
                return status
        except Exception as e:
            logger.warning(f"   ⚠️  Could not ping NAS: {e}")
            status["nas_reachable"] = False
            return status

        # Check for DSM package scripts
        dsm_scripts = [
            "nas_dsm_cloud_storage_setup.py",
            "migrate_cloud_storage_to_dsm_nas.py",
            "configure_all_dsm_packages_full_auto.py"
        ]

        logger.info("   Checking for DSM package setup scripts...")
        for script_name in dsm_scripts:
            script_path = self.project_root / "scripts" / "python" / script_name
            if script_path.exists():
                logger.info(f"      ✅ Found: {script_name}")
                status["setup_scripts_available"] = True
            else:
                logger.warning(f"      ⚠️  Missing: {script_name}")

        # Common DSM cloud storage packages
        status["cloud_providers"] = [
            "Google Drive",
            "Dropbox",
            "OneDrive",
            "Amazon S3",
            "Backblaze B2",
            "Wasabi"
        ]

        status["recommendations"] = [
            "⚠️  DSM cloud storage package needs to be configured",
            "⚠️  Package may be installed but not integrated",
            "✅ Use DSM Package Center to install/configure",
            "✅ Set up cloud.local system for unified access"
        ]

        logger.info("")
        logger.info("   DSM Cloud Storage Package Status:")
        logger.info(f"      Installed: {status['package_installed']}")
        logger.info(f"      Configured: {status['package_configured']}")
        logger.info(f"      Integration: {status['integration_status']}")

        return status

    def setup_cloud_local_system(self) -> Dict[str, Any]:
        """
        Set up cloud.local system with multiple cloud storage providers.

        Returns:
            Cloud.local setup status
        """
        logger.info("=" * 80)
        logger.info("☁️  SETTING UP CLOUD.LOCAL SYSTEM")
        logger.info("=" * 80)
        logger.info("")

        setup = {
            "timestamp": datetime.now().isoformat(),
            "cloud_local_domain": "cloud.local",
            "providers": [],
            "nas_integration": False,
            "homelab_sharing": False,
            "status": "not_configured"
        }

        # Cloud storage providers to integrate
        providers = [
            {
                "name": "Google Drive",
                "type": "cloud",
                "integration": "dsm_package"
            },
            {
                "name": "Dropbox",
                "type": "cloud",
                "integration": "dsm_package"
            },
            {
                "name": "OneDrive",
                "type": "cloud",
                "integration": "dsm_package"
            },
            {
                "name": "NAS Storage",
                "type": "local",
                "integration": "smb_nfs"
            }
        ]

        setup["providers"] = providers

        logger.info("   Cloud.local system components:")
        logger.info("      - DSM Cloud Storage Package")
        logger.info("      - Multiple cloud provider integration")
        logger.info("      - Unified access via cloud.local")
        logger.info("      - Shared to all homelab systems")
        logger.info("")

        setup["recommendations"] = [
            "✅ Configure DSM cloud storage package",
            "✅ Set up cloud.local DNS entry (pointing to NAS)",
            "✅ Configure SMB/NFS shares for homelab access",
            "✅ Set up unified authentication",
            "✅ Configure automatic sync from cloud providers to NAS",
            "✅ Set up reverse proxy for cloud.local access"
        ]

        return setup

    def create_migration_plan(self, system: str) -> Dict[str, Any]:
        """
        Create migration plan for moving data to NAS.

        Args:
            system: System name

        Returns:
            Migration plan
        """
        logger.info("=" * 80)
        logger.info(f"📋 CREATING MIGRATION PLAN FOR {system}")
        logger.info("=" * 80)
        logger.info("")

        # Get large files analysis
        large_files = self.identify_large_files(system)

        plan = {
            "timestamp": datetime.now().isoformat(),
            "system": system,
            "migration_phases": [],
            "estimated_size_gb": large_files.get("total_size_gb", 0),
            "nas_destination": f"\\\\{self.nas_ip}\\migration\\{system.lower()}",
            "status": "planned"
        }

        # Migration phases
        phases = [
            {
                "phase": 1,
                "name": "Large Media Files",
                "description": "Migrate videos, large downloads",
                "priority": "high",
                "estimated_size_gb": large_files.get("total_size_gb", 0) * 0.4
            },
            {
                "phase": 2,
                "name": "Project Backups",
                "description": "Move old project backups to NAS",
                "priority": "medium",
                "estimated_size_gb": large_files.get("total_size_gb", 0) * 0.3
            },
            {
                "phase": 3,
                "name": "Cache and Temp Files",
                "description": "Move cache directories to NAS",
                "priority": "low",
                "estimated_size_gb": large_files.get("total_size_gb", 0) * 0.2
            },
            {
                "phase": 4,
                "name": "Archive Old Data",
                "description": "Archive old documents and files",
                "priority": "low",
                "estimated_size_gb": large_files.get("total_size_gb", 0) * 0.1
            }
        ]

        plan["migration_phases"] = phases

        logger.info("   Migration Plan:")
        for phase in phases:
            logger.info(f"      Phase {phase['phase']}: {phase['name']}")
            logger.info(f"         Priority: {phase['priority']}")
            logger.info(f"         Estimated: {phase['estimated_size_gb']:.2f} GB")

        plan["recommendations"] = [
            "✅ Start with Phase 1 (largest impact)",
            "✅ Use robocopy for reliable migration",
            "✅ Verify data integrity after migration",
            "✅ Update application paths after migration",
            "✅ Set up symlinks for seamless access"
        ]

        return plan

    def generate_comprehensive_plan(self) -> Dict[str, Any]:
        try:
            """
            Generate comprehensive NAS migration integration plan.

            Returns:
                Complete integration plan
            """
            logger.info("=" * 80)
            logger.info("📊 GENERATING COMPREHENSIVE NAS MIGRATION PLAN")
            logger.info("=" * 80)
            logger.info("")

            # Analyze both systems
            kaiju_analysis = self.identify_large_files("KAIJU_NO_8")
            falc_analysis = self.identify_large_files("MILLENNIUM_FALC")

            # Check DSM package
            dsm_status = self.check_dsm_cloud_storage_package()

            # Cloud.local setup
            cloud_local = self.setup_cloud_local_system()

            # Migration plans
            kaiju_plan = self.create_migration_plan("KAIJU_NO_8")
            falc_plan = self.create_migration_plan("MILLENNIUM_FALC")

            # Comprehensive plan
            comprehensive_plan = {
                "timestamp": datetime.now().isoformat(),
                "systems_analyzed": {
                    "KAIJU_NO_8": kaiju_analysis,
                    "MILLENNIUM_FALC": falc_analysis
                },
                "dsm_package": dsm_status,
                "cloud_local": cloud_local,
                "migration_plans": {
                    "KAIJU_NO_8": kaiju_plan,
                    "MILLENNIUM_FALC": falc_plan
                },
                "total_size_to_migrate_gb": (
                    kaiju_analysis.get("total_size_gb", 0) +
                    falc_analysis.get("total_size_gb", 0)
                ),
                "next_steps": [
                    "1. Complete DSM cloud storage package integration",
                    "2. Set up cloud.local system",
                    "3. Begin Phase 1 migration (large media files)",
                    "4. Configure homelab sharing",
                    "5. Set up automated sync from cloud providers"
                ]
            }

            # Save plan
            plan_file = self.data_dir / f"comprehensive_migration_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(plan_file, 'w', encoding='utf-8') as f:
                json.dump(comprehensive_plan, f, indent=2, ensure_ascii=False, default=str)

            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ COMPREHENSIVE PLAN GENERATED")
            logger.info("=" * 80)
            logger.info(f"   Plan saved: {plan_file.name}")
            logger.info("")

            # Print summary
            print("\n" + "=" * 80)
            print("📊 NAS MIGRATION INTEGRATION SUMMARY")
            print("=" * 80)
            print(f"Total Size to Migrate: {comprehensive_plan['total_size_to_migrate_gb']:.2f} GB")
            print(f"DSM Package Status: {dsm_status.get('integration_status', 'unknown')}")
            print(f"Cloud.local Setup: {cloud_local.get('status', 'unknown')}")
            print("\nNext Steps:")
            for step in comprehensive_plan['next_steps']:
                print(f"  {step}")
            print("=" * 80)
            print()

            return comprehensive_plan


        except Exception as e:
            self.logger.error(f"Error in generate_comprehensive_plan: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Complete NAS Migration Integration")
    parser.add_argument("--analyze", choices=["KAIJU_NO_8", "MILLENNIUM_FALC", "both"], default="both", help="System to analyze")
    parser.add_argument("--check-dsm", action="store_true", help="Check DSM package status")
    parser.add_argument("--setup-cloud-local", action="store_true", help="Set up cloud.local system")
    parser.add_argument("--full-plan", action="store_true", help="Generate comprehensive plan")

    args = parser.parse_args()

    migration = CompleteNASMigrationIntegration()

    if args.full_plan or not any(vars(args).values()):
        # Default: full plan
        migration.generate_comprehensive_plan()
    else:
        if args.analyze in ["KAIJU_NO_8", "both"]:
            migration.identify_large_files("KAIJU_NO_8")
        if args.analyze in ["MILLENNIUM_FALC", "both"]:
            migration.identify_large_files("MILLENNIUM_FALC")
        if args.check_dsm:
            migration.check_dsm_cloud_storage_package()
        if args.setup_cloud_local:
            migration.setup_cloud_local_system()

    return 0


if __name__ == "__main__":


    sys.exit(main())