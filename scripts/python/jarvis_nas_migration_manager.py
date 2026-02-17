#!/usr/bin/env python3
"""
JARVIS NAS Migration Manager

Intelligently migrates local data to NAS and reorganizes network drive mappings.
Identifies large files, Docker volumes, logs, backups, and other data for migration.

Tags: #NAS-MIGRATION #NETWORK-DRIVES #DATA-MANAGEMENT
"""

import sys
import os
import shutil
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
import subprocess

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from nas_azure_vault_integration import NASAzureVaultIntegration
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    NASAzureVaultIntegration = None

logger = get_logger("JARVISNASMigration")


class JARVISNASMigrationManager:
    """
    JARVIS NAS Migration Manager

    Manages intelligent migration of local data to NAS and network drive mappings.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.nas_ip = "<NAS_PRIMARY_IP>"
        self.nas_base_path = f"\\\\{self.nas_ip}\\backups\\MATT_Backups"
        self.nas_integration = None

        # Network drive mappings configuration
        self.drive_mappings_file = project_root / "config" / "network_drives_config.json"
        self.drive_mappings_file.parent.mkdir(parents=True, exist_ok=True)

        # Migration configuration
        self.migration_config_file = project_root / "config" / "nas_migration_config.json"
        self.migration_config_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialize NAS integration
        if NASAzureVaultIntegration:
            try:
                self.nas_integration = NASAzureVaultIntegration(nas_ip=self.nas_ip)
                self.logger.info("✅ NAS integration initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  NAS integration not available: {e}")

        self.logger.info("✅ JARVIS NAS Migration Manager initialized")

    def get_network_drive_mappings(self) -> Dict[str, Any]:
        """Get current network drive mappings configuration"""
        if self.drive_mappings_file.exists():
            try:
                with open(self.drive_mappings_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"❌ Error reading drive mappings: {e}", exc_info=True)

        # Default configuration
        default_config = {
            "mappings": [
                {
                    "drive": "K",
                    "path": f"\\\\{self.nas_ip}\\backups\\MATT_Backups",
                    "description": "KAIJU - Main Backups",
                    "persistent": True,
                    "auto_reconnect": True
                },
                {
                    "drive": "L",
                    "path": f"\\\\{self.nas_ip}\\backups\\MATT_Backups\\lumina_data",
                    "description": "LUMINA Project Data",
                    "persistent": True,
                    "auto_reconnect": True
                },
                {
                    "drive": "M",
                    "path": f"\\\\{self.nas_ip}\\backups\\MATT_Backups\\docker_volumes",
                    "description": "Docker Volumes",
                    "persistent": True,
                    "auto_reconnect": True
                },
                {
                    "drive": "N",
                    "path": f"\\\\{self.nas_ip}\\backups\\MATT_Backups\\logs",
                    "description": "System Logs",
                    "persistent": True,
                    "auto_reconnect": True
                },
                {
                    "drive": "O",
                    "path": f"\\\\{self.nas_ip}\\backups\\MATT_Backups\\databases",
                    "description": "Database Backups",
                    "persistent": True,
                    "auto_reconnect": True
                }
            ],
            "options": {
                "reconnect_on_startup": True,
                "verify_on_mapping": True,
                "log_file": str(Path(os.environ.get("TEMP", "C:\\Temp")) / "network_drives.log"),
                "retry_attempts": 3,
                "retry_delay_seconds": 5
            }
        }

        # Save default config
        with open(self.drive_mappings_file, 'w') as f:
            json.dump(default_config, f, indent=2)

        return default_config

    def map_network_drives(self) -> Dict[str, Any]:
        """Map network drives using PowerShell"""
        self.logger.info("🗺️  Mapping network drives...")

        config = self.get_network_drive_mappings()
        results = {
            "mapped": [],
            "failed": [],
            "already_mapped": []
        }

        for mapping in config["mappings"]:
            drive_letter = mapping["drive"].upper().rstrip(':')
            network_path = mapping["path"]
            description = mapping.get("description", "")
            persistent = mapping.get("persistent", True)

            self.logger.info(f"   Mapping {drive_letter}: to {network_path} ({description})...")

            try:
                # Check if drive is already mapped
                result = subprocess.run(
                    ["powershell", "-Command", f"Get-PSDrive -Name {drive_letter} -ErrorAction SilentlyContinue"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0 and result.stdout.strip():
                    # Drive exists, check if it's the same path
                    existing_path = subprocess.run(
                        ["powershell", "-Command", f"(Get-PSDrive -Name {drive_letter}).Root"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )

                    if existing_path.stdout.strip().replace('\\', '/') == network_path.replace('\\', '/'):
                        self.logger.info(f"   ✅ {drive_letter}: already mapped correctly")
                        results["already_mapped"].append({
                            "drive": drive_letter,
                            "path": network_path,
                            "description": description
                        })
                        continue
                    else:
                        # Remove existing mapping
                        subprocess.run(
                            ["powershell", "-Command", f"Remove-PSDrive -Name {drive_letter} -Force -ErrorAction SilentlyContinue"],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )

                # Get NAS credentials from Azure Key Vault
                cred_username = None
                cred_password = None

                if self.nas_integration:
                    try:
                        nas_creds = self.nas_integration.get_nas_credentials()
                        if nas_creds:
                            cred_username = nas_creds.get("username")
                            cred_password = nas_creds.get("password")
                    except Exception as e:
                        self.logger.debug(f"   Could not get NAS credentials: {e}")

                # Map the drive with credentials if available
                persistent_flag = "-Persist" if persistent else ""

                if cred_username and cred_password:
                    # Use credentials for mapping
                    map_command = f"""
                        $username = '{cred_username}'
                        $password = ConvertTo-SecureString '{cred_password}' -AsPlainText -Force
                        $cred = New-Object System.Management.Automation.PSCredential($username, $password)
                        $netPath = '{network_path}'
                        try {{
                            New-PSDrive -Name {drive_letter} -PSProvider FileSystem -Root $netPath {persistent_flag} -Credential $cred -ErrorAction Stop | Out-Null
                            Write-Output "SUCCESS"
                        }} catch {{
                            Write-Output "FAILED: $($_.Exception.Message)"
                        }}
                    """
                else:
                    # Try without credentials (may work if already authenticated)
                    map_command = f"""
                        $netPath = '{network_path}'
                        try {{
                            New-PSDrive -Name {drive_letter} -PSProvider FileSystem -Root $netPath {persistent_flag} -ErrorAction Stop | Out-Null
                            Write-Output "SUCCESS"
                        }} catch {{
                            Write-Output "FAILED: $($_.Exception.Message)"
                        }}
                    """

                result = subprocess.run(
                    ["powershell", "-Command", map_command],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if "SUCCESS" in result.stdout:
                    self.logger.info(f"   ✅ {drive_letter}: mapped successfully")
                    results["mapped"].append({
                        "drive": drive_letter,
                        "path": network_path,
                        "description": description
                    })
                else:
                    error_msg = result.stdout.strip() or result.stderr.strip()
                    self.logger.error(f"   ❌ Failed to map {drive_letter}: {error_msg}")
                    results["failed"].append({
                        "drive": drive_letter,
                        "path": network_path,
                        "error": error_msg
                    })

            except Exception as e:
                self.logger.error(f"   ❌ Error mapping {drive_letter}: {e}", exc_info=True)
                results["failed"].append({
                    "drive": drive_letter,
                    "path": network_path,
                    "error": str(e)
                })

        return results

    def identify_migration_candidates(self) -> Dict[str, Any]:
        """Identify data that should be migrated to NAS"""
        self.logger.info("🔍 Identifying migration candidates...")

        candidates = {
            "docker_volumes": [],
            "large_files": [],
            "logs": [],
            "backups": [],
            "data_directories": [],
            "total_size_gb": 0.0
        }

        # Docker volumes (from disk space report)
        docker_volumes = [
            {
                "name": "laptop-optimized-llm_laptop_llm_models",
                "size_gb": 47.42,
                "source": "Docker",
                "priority": "HIGH",
                "target": f"{self.nas_base_path}\\docker_volumes\\llm_models"
            }
        ]
        candidates["docker_volumes"] = docker_volumes
        candidates["total_size_gb"] += 47.42

        # Large data directories in project
        data_dirs = [
            {
                "path": self.project_root / "data" / "holocron",
                "size_gb": 0.0,  # Will be calculated
                "target": f"{self.nas_base_path}\\lumina_data\\holocron",
                "priority": "MEDIUM"
            },
            {
                "path": self.project_root / "data" / "logs",
                "size_gb": 0.0,
                "target": f"{self.nas_base_path}\\logs\\lumina",
                "priority": "LOW"
            },
            {
                "path": self.project_root / "data" / "jarvis_memory",
                "size_gb": 0.0,
                "target": f"{self.nas_base_path}\\lumina_data\\jarvis_memory",
                "priority": "HIGH"
            }
        ]

        # Calculate sizes
        for data_dir in data_dirs:
            if data_dir["path"].exists():
                try:
                    total_size = sum(
                        f.stat().st_size for f in data_dir["path"].rglob('*') if f.is_file()
                    )
                    data_dir["size_gb"] = round(total_size / (1024**3), 2)
                    candidates["total_size_gb"] += data_dir["size_gb"]
                except Exception as e:
                    self.logger.debug(f"   Error calculating size for {data_dir['path']}: {e}")

        candidates["data_directories"] = [d for d in data_dirs if d["size_gb"] > 0.01]

        self.logger.info(f"   Found {candidates['total_size_gb']:.2f} GB of migration candidates")

        return candidates

    def migrate_data(self, candidates: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
        """Migrate identified data to NAS"""
        self.logger.info(f"🚀 Starting data migration (dry_run={dry_run})...")

        migration_results = {
            "docker_volumes": [],
            "data_directories": [],
            "total_migrated_gb": 0.0,
            "errors": []
        }

        # Migrate Docker volumes
        for volume in candidates.get("docker_volumes", []):
            self.logger.info(f"   Migrating Docker volume: {volume['name']} ({volume['size_gb']} GB)...")

            if dry_run:
                migration_results["docker_volumes"].append({
                    "name": volume["name"],
                    "status": "DRY_RUN",
                    "target": volume["target"]
                })
                continue

            # Docker volume migration requires stopping containers and using docker cp or volume backup
            # This is complex and should be done carefully
            migration_results["docker_volumes"].append({
                "name": volume["name"],
                "status": "PENDING",
                "note": "Requires container stop and volume backup"
            })

        # Migrate data directories
        for data_dir in candidates.get("data_directories", []):
            source_path = data_dir["path"]
            target_path = Path(data_dir["target"])

            self.logger.info(f"   Migrating directory: {source_path.name} ({data_dir['size_gb']} GB)...")

            if dry_run:
                migration_results["data_directories"].append({
                    "source": str(source_path),
                    "target": str(target_path),
                    "status": "DRY_RUN",
                    "size_gb": data_dir["size_gb"]
                })
                continue

            try:
                # Ensure target directory exists
                target_path.mkdir(parents=True, exist_ok=True)

                # Copy files (using robocopy for better performance and resume capability)
                robocopy_cmd = [
                    "robocopy",
                    str(source_path),
                    str(target_path),
                    "/E",  # Copy subdirectories including empty ones
                    "/R:3",  # Retry 3 times
                    "/W:5",  # Wait 5 seconds between retries
                    "/MT:8",  # Multi-threaded (8 threads)
                    "/LOG+:" + str(target_path.parent / f"migration_{source_path.name}.log")
                ]

                result = subprocess.run(
                    robocopy_cmd,
                    capture_output=True,
                    text=True,
                    timeout=3600  # 1 hour timeout
                )

                # Robocopy returns 0-7 for success, 8+ for errors
                if result.returncode < 8:
                    migration_results["data_directories"].append({
                        "source": str(source_path),
                        "target": str(target_path),
                        "status": "SUCCESS",
                        "size_gb": data_dir["size_gb"]
                    })
                    migration_results["total_migrated_gb"] += data_dir["size_gb"]
                    self.logger.info(f"   ✅ Migrated {source_path.name}")
                else:
                    error_msg = result.stderr or result.stdout
                    migration_results["errors"].append({
                        "source": str(source_path),
                        "error": error_msg
                    })
                    self.logger.error(f"   ❌ Failed to migrate {source_path.name}: {error_msg}")

            except Exception as e:
                self.logger.error(f"   ❌ Error migrating {source_path}: {e}", exc_info=True)
                migration_results["errors"].append({
                    "source": str(source_path),
                    "error": str(e)
                })

        return migration_results

    def create_migration_plan(self) -> Dict[str, Any]:
        try:
            """Create comprehensive migration plan"""
            self.logger.info("📋 Creating migration plan...")

            # Get network drive mappings
            drive_mappings = self.get_network_drive_mappings()

            # Identify migration candidates
            candidates = self.identify_migration_candidates()

            # Create plan
            plan = {
                "timestamp": datetime.now().isoformat(),
                "network_drives": {
                    "config_file": str(self.drive_mappings_file),
                    "mappings": drive_mappings["mappings"],
                    "status": "PENDING"
                },
                "migration_candidates": candidates,
                "estimated_space_freed_gb": candidates["total_size_gb"],
                "steps": [
                    {
                        "step": 1,
                        "action": "Map network drives",
                        "description": "Create persistent network drive mappings (K:, L:, M:, N:, O:)",
                        "status": "PENDING"
                    },
                    {
                        "step": 2,
                        "action": "Migrate Docker volumes",
                        "description": "Move large Docker volumes to NAS (47.42 GB)",
                        "status": "PENDING",
                        "priority": "HIGH"
                    },
                    {
                        "step": 3,
                        "action": "Migrate data directories",
                        "description": "Move large data directories to NAS",
                        "status": "PENDING"
                    },
                    {
                        "step": 4,
                        "action": "Update path references",
                        "description": "Update code/config to use network drive mappings",
                        "status": "PENDING"
                    },
                    {
                        "step": 5,
                        "action": "Verify migration",
                        "description": "Verify all data migrated successfully",
                        "status": "PENDING"
                    }
                ]
            }

            # Save plan
            plan_file = self.project_root / "data" / "system" / "nas_migration_plan.json"
            plan_file.parent.mkdir(parents=True, exist_ok=True)
            with open(plan_file, 'w') as f:
                json.dump(plan, f, indent=2, default=str)

            self.logger.info(f"   ✅ Plan saved to {plan_file}")

            return plan

        except Exception as e:
            self.logger.error(f"Error in create_migration_plan: {e}", exc_info=True)
            raise
    def execute_migration_plan(self, dry_run: bool = False) -> Dict[str, Any]:
        """Execute the migration plan"""
        self.logger.info(f"🚀 Executing migration plan (dry_run={dry_run})...")

        plan = self.create_migration_plan()
        execution_results = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "steps_completed": [],
            "steps_failed": [],
            "total_space_freed_gb": 0.0
        }

        # Step 1: Map network drives
        self.logger.info("Step 1: Mapping network drives...")
        drive_results = self.map_network_drives()
        if drive_results["mapped"] or drive_results["already_mapped"]:
            execution_results["steps_completed"].append({
                "step": 1,
                "action": "Map network drives",
                "result": drive_results
            })
        else:
            execution_results["steps_failed"].append({
                "step": 1,
                "action": "Map network drives",
                "result": drive_results
            })

        # Step 2-3: Migrate data
        candidates = plan["migration_candidates"]
        migration_results = self.migrate_data(candidates, dry_run=dry_run)

        if migration_results.get("total_migrated_gb", 0) > 0:
            execution_results["steps_completed"].append({
                "step": 2,
                "action": "Migrate data",
                "result": migration_results
            })
            execution_results["total_space_freed_gb"] = migration_results["total_migrated_gb"]
        else:
            execution_results["steps_failed"].append({
                "step": 2,
                "action": "Migrate data",
                "result": migration_results
            })

        return execution_results


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS NAS Migration Manager")
        parser.add_argument("--plan", action="store_true", help="Create migration plan")
        parser.add_argument("--map-drives", action="store_true", help="Map network drives")
        parser.add_argument("--migrate", action="store_true", help="Execute migration")
        parser.add_argument("--dry-run", action="store_true", help="Dry run (no actual migration)")
        parser.add_argument("--identify", action="store_true", help="Identify migration candidates")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        manager = JARVISNASMigrationManager(project_root)

        if args.plan:
            plan = manager.create_migration_plan()
            print(json.dumps(plan, indent=2, default=str))

        elif args.map_drives:
            results = manager.map_network_drives()
            print(json.dumps(results, indent=2, default=str))

        elif args.migrate:
            results = manager.execute_migration_plan(dry_run=args.dry_run)
            print(json.dumps(results, indent=2, default=str))

        elif args.identify:
            candidates = manager.identify_migration_candidates()
            print(json.dumps(candidates, indent=2, default=str))

        else:
            # Default: create plan
            plan = manager.create_migration_plan()
            print(json.dumps(plan, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()