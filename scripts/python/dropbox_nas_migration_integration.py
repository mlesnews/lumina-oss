"""
Dropbox to NAS Migration Integration
Integrates Dropbox to NAS migration system with JARVIS, R5, and LUMINA.

This module provides:
- JARVIS workflow integration for migration automation
- R5 knowledge aggregation for migration patterns
- MANUS automation control for migration execution
- LUMINA extension registration
- Health monitoring and status reporting

Tags: #JARVIS #LUMINA #NAS #MIGRATION #CLOUD-STORAGE #DSM #NETWORK-DRIVE @JARVIS @LUMINA @NAS
"""

import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from lumina_logger import get_logger
    logger = get_logger("DropboxNASMigration")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("DropboxNASMigration")

try:
    from r5_living_context_matrix import R5LivingContextMatrix
    R5_AVAILABLE = True
except ImportError:
    R5_AVAILABLE = False
    logger.warning("R5 Living Context Matrix not available")

try:
    from jarvis_helpdesk_integration import JARVISHelpdeskIntegration
    JARVIS_AVAILABLE = True
except ImportError:
    JARVIS_AVAILABLE = False
    logger.warning("JARVIS Helpdesk Integration not available")

try:
    from nas_azure_vault_integration import NASAzureVaultIntegration
    NAS_INTEGRATION_AVAILABLE = True
except ImportError:
    NAS_INTEGRATION_AVAILABLE = False
    logger.warning("NAS Azure Vault Integration not available")


class DropboxNASMigrationIntegration:
    """
    Dropbox to NAS Migration Integration with LUMINA ecosystem.

    Integrates migration system with:
    - JARVIS for workflow automation
    - R5 for knowledge aggregation
    - MANUS for automation control
    - NAS integration for storage management
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize Dropbox to NAS Migration Integration.

        Args:
            project_root: Project root directory
        """
        if project_root is None:
            # Auto-detect project root
            current = Path(__file__).parent.parent.parent
            if (current / "config").exists():
                project_root = current
            else:
                project_root = Path("N:/my_projects")  # Use N: drive if available

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.scripts_dir = self.project_root / "scripts"
        self.powershell_dir = self.scripts_dir / "powershell"

        # Configuration files
        self.migration_config = self.config_dir / "dsm_cloud_storage_aggregator.json"
        self.network_drives_config = self.scripts_dir / "network_drives_config.json"
        self.lumina_config = self.config_dir / "lumina_extensions_integration.json"

        # Initialize integrations
        self.r5_system: Optional[R5LivingContextMatrix] = None
        self.jarvis_integration: Optional[JARVISHelpdeskIntegration] = None
        self.nas_integration: Optional[Any] = None

        self._initialize_integrations()

    def _initialize_integrations(self):
        """Initialize LUMINA ecosystem integrations."""
        # Initialize R5 for knowledge aggregation
        if R5_AVAILABLE:
            try:
                self.r5_system = R5LivingContextMatrix(self.project_root)
                logger.info("✅ R5 Living Context Matrix integrated")
            except Exception as e:
                logger.warning(f"⚠️  R5 integration failed: {e}")

        # Initialize JARVIS for workflow automation
        if JARVIS_AVAILABLE:
            try:
                self.jarvis_integration = JARVISHelpdeskIntegration(self.project_root)
                logger.info("✅ JARVIS Helpdesk Integration integrated")
            except Exception as e:
                logger.warning(f"⚠️  JARVIS integration failed: {e}")

        # Initialize NAS integration
        if NAS_INTEGRATION_AVAILABLE:
            try:
                self.nas_integration = NASAzureVaultIntegration()
                logger.info("✅ NAS Azure Vault Integration integrated")
            except Exception as e:
                logger.warning(f"⚠️  NAS integration failed: {e}")

    def get_migration_status(self) -> Dict[str, Any]:
        """
        Get current migration status.

        Returns:
            Migration status dictionary
        """
        status = {
            "migration_ready": False,
            "n_drive_mapped": False,
            "nas_accessible": False,
            "cloud_sync_configured": False,
            "last_check": datetime.now().isoformat()
        }

        # Check N: drive mapping
        try:
            n_drive = Path("N:/")
            if n_drive.exists():
                status["n_drive_mapped"] = True
                status["n_drive_path"] = str(n_drive)
        except Exception as e:
            logger.debug(f"N: drive check failed: {e}")

        # Check NAS accessibility
        if self.nas_integration:
            try:
                # Test NAS connection
                nas_path = Path("\\\\<NAS_PRIMARY_IP>\\backups\\MATT_Backups")
                if nas_path.exists():
                    status["nas_accessible"] = True
            except Exception as e:
                logger.debug(f"NAS accessibility check failed: {e}")

        # Check cloud sync configuration
        if self.migration_config.exists():
            try:
                with open(self.migration_config, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if config.get("dsm_cloud_storage_aggregator", {}).get("status") == "active":
                        status["cloud_sync_configured"] = True
            except Exception as e:
                logger.debug(f"Cloud sync config check failed: {e}")

        # Overall migration readiness
        status["migration_ready"] = (
            status["n_drive_mapped"] and
            status["nas_accessible"] and
            status["cloud_sync_configured"]
        )

        return status

    def execute_migration(
        self,
        source_path: str = "",
        dest_path: str = "N:\\my_projects",
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Execute Dropbox to NAS migration.

        Args:
            source_path: Source Dropbox path
            dest_path: Destination NAS path
            dry_run: Perform dry run without making changes

        Returns:
            Migration result dictionary
        """
        result = {
            "success": False,
            "dry_run": dry_run,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "errors": [],
            "warnings": [],
            "files_migrated": 0,
            "migration_log": None
        }

        migration_script = self.powershell_dir / "migrate_dropbox_to_nas.ps1"

        if not migration_script.exists():
            result["errors"].append(f"Migration script not found: {migration_script}")
            return result

        try:
            # Build PowerShell command
            cmd = [
                "powershell.exe",
                "-ExecutionPolicy", "Bypass",
                "-NoProfile",
                "-File", str(migration_script)
            ]

            if source_path:
                cmd.extend(["-SourcePath", source_path])

            cmd.extend(["-DestPath", dest_path])

            if dry_run:
                cmd.append("-DryRun")

            # Execute migration
            logger.info(f"Executing migration: {' '.join(cmd)}")
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )

            result["end_time"] = datetime.now().isoformat()
            result["return_code"] = process.returncode
            result["stdout"] = process.stdout
            result["stderr"] = process.stderr

            if process.returncode == 0:
                result["success"] = True
                logger.info("✅ Migration completed successfully")

                # Aggregate knowledge to R5
                if self.r5_system:
                    self._aggregate_migration_knowledge(result)
            else:
                result["errors"].append(f"Migration failed with return code: {process.returncode}")
                logger.error(f"❌ Migration failed: {process.stderr}")

        except subprocess.TimeoutExpired:
            result["errors"].append("Migration timed out after 1 hour")
            logger.error("❌ Migration timed out")
        except Exception as e:
            result["errors"].append(str(e))
            logger.error(f"❌ Migration error: {e}", exc_info=True)

        return result

    def _aggregate_migration_knowledge(self, migration_result: Dict[str, Any]):
        """
        Aggregate migration knowledge to R5.

        Args:
            migration_result: Migration result dictionary
        """
        if not self.r5_system:
            return

        try:
            knowledge = {
                "type": "migration_pattern",
                "system": "dropbox_nas_migration",
                "timestamp": datetime.now().isoformat(),
                "result": migration_result,
                "tags": ["#migration", "#dropbox", "#nas", "#cloud-storage"],
                "context": {
                    "source": "dropbox_local",
                    "destination": "nas_network_storage",
                    "drive": "N:",
                    "cloud_sync": "dsm_cloud_sync_aggregator"
                }
            }

            # Ingest to R5
            self.r5_system.ingest_knowledge(
                content=json.dumps(knowledge, indent=2),
                source="dropbox_nas_migration_integration",
                tags=["migration", "dropbox", "nas", "cloud-storage"]
            )

            logger.info("✅ Migration knowledge aggregated to R5")
        except Exception as e:
            logger.warning(f"⚠️  Failed to aggregate migration knowledge: {e}")

    def update_path_references(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Update path references from Dropbox to N: drive.

        Args:
            dry_run: Perform dry run without making changes

        Returns:
            Update result dictionary
        """
        result = {
            "success": False,
            "dry_run": dry_run,
            "files_updated": 0,
            "files_skipped": 0,
            "errors": []
        }

        update_script = self.powershell_dir / "update_path_references_to_nas.ps1"

        if not update_script.exists():
            result["errors"].append(f"Path update script not found: {update_script}")
            return result

        try:
            cmd = [
                "powershell.exe",
                "-ExecutionPolicy", "Bypass",
                "-NoProfile",
                "-File", str(update_script),
                "-SearchPath", str(self.project_root)
            ]

            if dry_run:
                cmd.append("-DryRun")

            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )

            result["return_code"] = process.returncode
            result["stdout"] = process.stdout
            result["stderr"] = process.stderr

            if process.returncode == 0:
                result["success"] = True
                logger.info("✅ Path references updated successfully")
            else:
                result["errors"].append(f"Path update failed with return code: {process.returncode}")

        except Exception as e:
            result["errors"].append(str(e))
            logger.error(f"❌ Path update error: {e}", exc_info=True)

        return result

    def register_with_lumina(self) -> Dict[str, Any]:
        """
        Register migration system with LUMINA extensions.

        Returns:
            Registration result
        """
        if not self.lumina_config.exists():
            logger.warning(f"LUMINA config not found: {self.lumina_config}")
            return {"success": False, "error": "LUMINA config not found"}

        try:
            # Load existing config
            with open(self.lumina_config, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Add migration system registration
            extensions = config.get("extensions", {})
            extensions["dropbox_nas_migration"] = {
                "name": "Dropbox to NAS Migration System",
                "type": "storage_migration",
                "enabled": True,
                "module": "scripts/python/dropbox_nas_migration_integration.py",
                "class": "DropboxNASMigrationIntegration",
                "version": "1.0.0",
                "features": [
                    "automated_migration",
                    "path_reference_updates",
                    "cloud_sync_aggregation",
                    "health_monitoring",
                    "r5_knowledge_aggregation",
                    "jarvis_workflow_integration"
                ],
                "integration_points": {
                    "pre_migration": "jarvis_workflow_verification",
                    "post_migration": "r5_knowledge_ingestion",
                    "monitoring": "jarvis_health_checks",
                    "automation": "manus_control"
                },
                "config": {
                    "migration_script": "scripts/powershell/migrate_dropbox_to_nas.ps1",
                    "path_update_script": "scripts/powershell/update_path_references_to_nas.ps1",
                    "cloud_sync_config": "config/dsm_cloud_storage_aggregator.json",
                    "network_drives_config": "scripts/network_drives_config.json"
                },
                "tags": [
                    "#JARVIS",
                    "#LUMINA",
                    "#NAS",
                    "#MIGRATION",
                    "#CLOUD-STORAGE",
                    "#DSM",
                    "#NETWORK-DRIVE"
                ]
            }

            # Update registered systems
            registered = config.get("registered_systems", [])
            if "dropbox_nas_migration" not in registered:
                registered.append("dropbox_nas_migration")

            config["extensions"] = extensions
            config["registered_systems"] = registered
            config["updated_at"] = datetime.now().isoformat()

            # Save updated config
            with open(self.lumina_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            logger.info("✅ Registered Dropbox to NAS Migration with LUMINA")

            return {
                "success": True,
                "registered": "dropbox_nas_migration",
                "updated_at": config["updated_at"]
            }

        except Exception as e:
            logger.error(f"❌ Failed to register with LUMINA: {e}", exc_info=True)
            return {"success": False, "error": str(e)}


def main():
    try:
        """Main entry point for CLI usage."""
        import argparse

        parser = argparse.ArgumentParser(description="Dropbox to NAS Migration Integration")
        parser.add_argument("--status", action="store_true", help="Check migration status")
        parser.add_argument("--migrate", action="store_true", help="Execute migration")
        parser.add_argument("--dry-run", action="store_true", help="Perform dry run")
        parser.add_argument("--update-paths", action="store_true", help="Update path references")
        parser.add_argument("--register", action="store_true", help="Register with LUMINA")
        parser.add_argument("--source", type=str, help="Source Dropbox path")
        parser.add_argument("--dest", type=str, default="N:\\my_projects", help="Destination NAS path")

        args = parser.parse_args()

        integration = DropboxNASMigrationIntegration()

        if args.status:
            status = integration.get_migration_status()
            print(json.dumps(status, indent=2))

        if args.migrate:
            result = integration.execute_migration(
                source_path=args.source or "",
                dest_path=args.dest,
                dry_run=args.dry_run
            )
            print(json.dumps(result, indent=2))

        if args.update_paths:
            result = integration.update_path_references(dry_run=args.dry_run)
            print(json.dumps(result, indent=2))

        if args.register:
            result = integration.register_with_lumina()
            print(json.dumps(result, indent=2))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()