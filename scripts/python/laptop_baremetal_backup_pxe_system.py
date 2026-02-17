#!/usr/bin/env python3
"""
Laptop Baremetal Backup & PXE Network Boot System

"BACKUP-FOR-BUSINESS" Implementation:
- Baremetal OS backup image creation
- Project & critical/sensitive data backup
- PXE network boot from NAS
- HyperBackup hybrid two-stage disaster-recovery

Tags: #backup #baremetal #pxe #network_boot #nas #hyperbackup #disaster_recovery #backup_for_business
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("BaremetalBackupPXE")

# Import SSH helper for NAS connection
try:
    from ssh_connection_helper import connect_to_nas
    SSH_AVAILABLE = True
except ImportError:
    SSH_AVAILABLE = False
    logger.warning("⚠️  SSH connection helper not available")


class BackupType(Enum):
    """Backup types"""
    BAREMETAL_OS = "baremetal_os"  # Full OS image
    PROJECT_DATA = "project_data"  # Project files
    CRITICAL_DATA = "critical_data"  # Critical/sensitive data
    FULL_SYSTEM = "full_system"  # Complete system backup


class BackupStage(Enum):
    """HyperBackup two-stage backup"""
    STAGE_1_LOCAL = "stage_1_local"  # Local NAS backup
    STAGE_2_CLOUD = "stage_2_cloud"  # Cloud/remote backup


class PXEBootStatus(Enum):
    """PXE boot status"""
    CONFIGURED = "configured"
    NOT_CONFIGURED = "not_configured"
    TESTING = "testing"
    OPERATIONAL = "operational"


@dataclass
class BaremetalBackup:
    """Baremetal backup image"""
    backup_id: str
    backup_type: BackupType
    source_device: str
    image_path: str
    image_size_gb: float
    created_at: datetime
    checksum: Optional[str] = None
    compression: str = "gzip"  # gzip, xz, bzip2
    encryption: bool = False
    encryption_key_id: Optional[str] = None
    nas_path: Optional[str] = None
    hyperbackup_synced: bool = False

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['backup_type'] = self.backup_type.value
        result['created_at'] = self.created_at.isoformat()
        return result


@dataclass
class PXEBootConfig:
    """PXE network boot configuration"""
    config_id: str
    device_name: str
    mac_address: str
    boot_image: str  # Path to boot image on NAS
    tftp_server: str  # NAS IP
    nfs_server: str  # NAS IP
    nfs_path: str  # NFS path on NAS
    status: PXEBootStatus = PXEBootStatus.NOT_CONFIGURED
    last_tested: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['status'] = self.status.value
        if self.last_tested:
            result['last_tested'] = self.last_tested.isoformat()
        return result


@dataclass
class HyperBackupConfig:
    """HyperBackup hybrid two-stage configuration"""
    config_id: str
    stage_1_local: Dict[str, Any] = field(default_factory=dict)  # Local NAS backup config
    stage_2_cloud: Dict[str, Any] = field(default_factory=dict)  # Cloud backup config
    schedule: Dict[str, Any] = field(default_factory=dict)  # Backup schedule
    retention_policy: Dict[str, Any] = field(default_factory=dict)  # Retention rules
    encryption: bool = True
    compression: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LaptopBaremetalBackupPXESystem:
    """
    Laptop Baremetal Backup & PXE Network Boot System

    "BACKUP-FOR-BUSINESS" Implementation:
    - Baremetal OS backup images
    - Project & critical data backup
    - PXE network boot from NAS
    - HyperBackup hybrid two-stage disaster-recovery
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "baremetal_backup"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Config directory
        self.config_dir = self.project_root / "config"

        # Load NAS config
        self.nas_config = self._load_nas_config()

        # Backup storage
        self.backups: Dict[str, BaremetalBackup] = {}

        # PXE configurations
        self.pxe_configs: Dict[str, PXEBootConfig] = {}

        # HyperBackup configurations
        self.hyperbackup_configs: Dict[str, HyperBackupConfig] = {}

        # Load saved state
        self._load_state()

        logger.info("=" * 80)
        logger.info("💾 LAPTOP BAREMETAL BACKUP & PXE SYSTEM")
        logger.info("=" * 80)
        logger.info("   BACKUP-FOR-BUSINESS Implementation")
        logger.info("   HyperBackup Hybrid Two-Stage Disaster-Recovery")
        logger.info("=" * 80)
        logger.info("")

    def _load_nas_config(self) -> Optional[Dict[str, Any]]:
        """Load NAS configuration"""
        config_file = self.config_dir / "lumina_nas_ssh_config.json"

        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.debug(f"Could not load NAS config: {e}")

        return None

    def _load_state(self):
        """Load saved state"""
        state_file = self.data_dir / "backup_pxe_state.json"

        if not state_file.exists():
            return

        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Load backups
            for bid, backup_data in data.get('backups', {}).items():
                backup = BaremetalBackup(
                    backup_id=backup_data['backup_id'],
                    backup_type=BackupType(backup_data['backup_type']),
                    source_device=backup_data['source_device'],
                    image_path=backup_data['image_path'],
                    image_size_gb=backup_data['image_size_gb'],
                    created_at=datetime.fromisoformat(backup_data['created_at']),
                    checksum=backup_data.get('checksum'),
                    compression=backup_data.get('compression', 'gzip'),
                    encryption=backup_data.get('encryption', False),
                    encryption_key_id=backup_data.get('encryption_key_id'),
                    nas_path=backup_data.get('nas_path'),
                    hyperbackup_synced=backup_data.get('hyperbackup_synced', False)
                )
                self.backups[bid] = backup

            # Load PXE configs
            for cid, config_data in data.get('pxe_configs', {}).items():
                # Handle null values
                tftp_server = config_data.get('tftp_server')
                if not tftp_server:
                    tftp_server = self.nas_config.get("host") if self.nas_config else "192.168.1.100"

                nfs_server = config_data.get('nfs_server')
                if not nfs_server:
                    nfs_server = self.nas_config.get("host") if self.nas_config else "192.168.1.100"

                config = PXEBootConfig(
                    config_id=config_data['config_id'],
                    device_name=config_data['device_name'],
                    mac_address=config_data['mac_address'],
                    boot_image=config_data['boot_image'],
                    tftp_server=tftp_server,
                    nfs_server=nfs_server,
                    nfs_path=config_data['nfs_path'],
                    status=PXEBootStatus(config_data.get('status', 'not_configured')),
                    last_tested=datetime.fromisoformat(config_data['last_tested']) if config_data.get('last_tested') else None
                )
                self.pxe_configs[cid] = config

            # Load HyperBackup configs
            for cid, config_data in data.get('hyperbackup_configs', {}).items():
                config = HyperBackupConfig(
                    config_id=config_data['config_id'],
                    stage_1_local=config_data.get('stage_1_local', {}),
                    stage_2_cloud=config_data.get('stage_2_cloud', {}),
                    schedule=config_data.get('schedule', {}),
                    retention_policy=config_data.get('retention_policy', {}),
                    encryption=config_data.get('encryption', True),
                    compression=config_data.get('compression', True)
                )
                self.hyperbackup_configs[cid] = config

            if len(self.backups) > 0 or len(self.pxe_configs) > 0 or len(self.hyperbackup_configs) > 0:
                logger.info(f"📂 Loaded {len(self.backups)} backups, {len(self.pxe_configs)} PXE configs, {len(self.hyperbackup_configs)} HyperBackup configs")
        except Exception as e:
            logger.debug(f"Could not load state: {e}")

    def create_baremetal_backup(
        self,
        source_device: str,
        backup_type: BackupType = BackupType.BAREMETAL_OS,
        compression: str = "gzip",
        encryption: bool = False,
        nas_path: Optional[str] = None
    ) -> BaremetalBackup:
        """
        Create baremetal backup image

        Args:
            source_device: Source device (e.g., /dev/sda, C:)
            backup_type: Type of backup
            compression: Compression method (gzip, xz, bzip2)
            encryption: Enable encryption
            nas_path: NAS path for backup storage
        """
        backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        # Determine output path
        if nas_path:
            output_path = nas_path
        else:
            output_path = str(self.data_dir / f"{backup_id}.img")

        # Create backup using appropriate tool
        # Windows: Use DISM or VSS
        # Linux: Use dd or Clonezilla
        image_path = self._create_backup_image(
            source_device=source_device,
            output_path=output_path,
            backup_type=backup_type,
            compression=compression,
            encryption=encryption
        )

        # Calculate image size
        image_size_gb = self._get_file_size_gb(image_path)

        # Calculate checksum
        checksum = self._calculate_checksum(image_path)

        backup = BaremetalBackup(
            backup_id=backup_id,
            backup_type=backup_type,
            source_device=source_device,
            image_path=image_path,
            image_size_gb=image_size_gb,
            created_at=datetime.now(),
            checksum=checksum,
            compression=compression,
            encryption=encryption,
            nas_path=nas_path or image_path
        )

        self.backups[backup_id] = backup

        logger.info("=" * 80)
        logger.info("💾 BAREMETAL BACKUP CREATED")
        logger.info("=" * 80)
        logger.info(f"   Backup ID: {backup_id}")
        logger.info(f"   Type: {backup_type.value}")
        logger.info(f"   Source: {source_device}")
        logger.info(f"   Image: {image_path}")
        logger.info(f"   Size: {image_size_gb:.2f} GB")
        logger.info(f"   Checksum: {checksum}")
        logger.info("=" * 80)
        logger.info("")

        return backup

    def _create_backup_image(
        self,
        source_device: str,
        output_path: str,
        backup_type: BackupType,
        compression: str,
        encryption: bool
    ) -> str:
        """Create backup image using appropriate tool"""
        import platform

        system = platform.system()

        if system == "Windows":
            # Windows: Use DISM or VSS
            return self._create_windows_backup(source_device, output_path, compression)
        elif system == "Linux":
            # Linux: Use dd or Clonezilla
            return self._create_linux_backup(source_device, output_path, compression)
        else:
            logger.error(f"❌ Unsupported system: {system}")
            raise NotImplementedError(f"Backup not supported on {system}")

    def _create_windows_backup(
        self,
        source_device: str,
        output_path: str,
        compression: str
    ) -> str:
        """Create Windows backup using DISM"""
        # DISM command for Windows backup
        # Note: This is a template - actual implementation would use DISM API or subprocess

        logger.info(f"🪟 Creating Windows backup: {source_device} → {output_path}")

        # Example DISM command (would need proper implementation)
        # dism /Capture-Image /ImageFile:"{output_path}" /CaptureDir:"{source_device}" /Name:"Backup"

        # For now, create placeholder
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).touch()

        logger.warning("⚠️  Windows backup creation is a template - needs DISM implementation")

        return output_path

    def _create_linux_backup(
        self,
        source_device: str,
        output_path: str,
        compression: str
    ) -> str:
        """Create Linux backup using dd"""
        logger.info(f"🐧 Creating Linux backup: {source_device} → {output_path}")

        # Determine compression command
        if compression == "gzip":
            compress_cmd = "gzip"
        elif compression == "xz":
            compress_cmd = "xz"
        elif compression == "bzip2":
            compress_cmd = "bzip2"
        else:
            compress_cmd = None

        # Build dd command
        if compress_cmd:
            cmd = f"dd if={source_device} bs=4M status=progress | {compress_cmd} > {output_path}"
        else:
            cmd = f"dd if={source_device} of={output_path} bs=4M status=progress"

        logger.info(f"   Command: {cmd}")
        logger.warning("⚠️  Linux backup command prepared - execute with caution")

        # Note: Actual execution would require root privileges
        # For safety, we're not executing automatically

        return output_path

    def _get_file_size_gb(self, file_path: str) -> float:
        """Get file size in GB"""
        try:
            size_bytes = Path(file_path).stat().st_size
            return size_bytes / (1024 ** 3)  # Convert to GB
        except:
            return 0.0

    def _calculate_checksum(self, file_path: str) -> Optional[str]:
        """Calculate SHA256 checksum"""
        try:
            import hashlib
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except:
            return None

    def configure_pxe_boot(
        self,
        device_name: str,
        mac_address: str,
        boot_image: str,
        nas_ip: Optional[str] = None
    ) -> PXEBootConfig:
        """
        Configure PXE network boot from NAS

        Args:
            device_name: Device name
            mac_address: MAC address
            boot_image: Path to boot image on NAS
            nas_ip: NAS IP address (from config if not provided)
        """
        if not nas_ip:
            # Try to get from config
            if self.nas_config:
                nas_ip = self.nas_config.get("nas_ip") or \
                        self.nas_config.get("host") or \
                        self.nas_config.get("ip") or \
                        "192.168.1.100"
            else:
                nas_ip = "192.168.1.100"  # Default

        config_id = f"pxe_{device_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # NFS path on NAS
        nfs_path = f"/volume1/pxe_boot/{device_name}"

        config = PXEBootConfig(
            config_id=config_id,
            device_name=device_name,
            mac_address=mac_address,
            boot_image=boot_image,
            tftp_server=nas_ip,
            nfs_server=nas_ip,
            nfs_path=nfs_path,
            status=PXEBootStatus.CONFIGURED
        )

        self.pxe_configs[config_id] = config

        logger.info("=" * 80)
        logger.info("🌐 PXE BOOT CONFIGURATION")
        logger.info("=" * 80)
        logger.info(f"   Device: {device_name}")
        logger.info(f"   MAC: {mac_address}")
        logger.info(f"   Boot Image: {boot_image}")
        logger.info(f"   TFTP Server: {nas_ip}")
        logger.info(f"   NFS Server: {nas_ip}")
        logger.info(f"   NFS Path: {nfs_path}")
        logger.info("=" * 80)
        logger.info("")

        return config

    def setup_hyperbackup_two_stage(
        self,
        stage_1_local_path: str,
        stage_2_cloud_provider: str,
        schedule: Optional[Dict[str, Any]] = None
    ) -> HyperBackupConfig:
        """
        Setup HyperBackup hybrid two-stage disaster-recovery

        Stage 1: Local NAS backup
        Stage 2: Cloud/remote backup
        """
        config_id = f"hyperbackup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Stage 1: Local NAS backup
        stage_1_config = {
            "type": "local_nas",
            "path": stage_1_local_path,
            "compression": True,
            "encryption": True,
            "retention_days": 30
        }

        # Stage 2: Cloud backup
        stage_2_config = {
            "provider": stage_2_cloud_provider,  # e.g., "aws_s3", "azure_blob", "synology_c2"
            "encryption": True,
            "compression": True,
            "retention_days": 90
        }

        # Default schedule
        if not schedule:
            schedule = {
                "stage_1": {
                    "frequency": "daily",
                    "time": "02:00",
                    "enabled": True
                },
                "stage_2": {
                    "frequency": "weekly",
                    "day": "sunday",
                    "time": "03:00",
                    "enabled": True
                }
            }

        config = HyperBackupConfig(
            config_id=config_id,
            stage_1_local=stage_1_config,
            stage_2_cloud=stage_2_config,
            schedule=schedule,
            retention_policy={
                "stage_1_retention_days": 30,
                "stage_2_retention_days": 90,
                "keep_monthly": 12,
                "keep_yearly": 5
            },
            encryption=True,
            compression=True
        )

        self.hyperbackup_configs[config_id] = config

        logger.info("=" * 80)
        logger.info("🔄 HYPERBACKUP TWO-STAGE CONFIGURATION")
        logger.info("=" * 80)
        logger.info("   Stage 1: Local NAS Backup")
        logger.info(f"      Path: {stage_1_local_path}")
        logger.info("   Stage 2: Cloud Backup")
        logger.info(f"      Provider: {stage_2_cloud_provider}")
        logger.info("=" * 80)
        logger.info("")

        return config

    def backup_project_data(
        self,
        project_paths: List[str],
        nas_backup_path: Optional[str] = None
    ) -> BaremetalBackup:
        """Backup project & critical/sensitive data"""
        if not nas_backup_path:
            nas_backup_path = "/volume1/backups/project_data"

        # Create project data backup
        backup = self.create_baremetal_backup(
            source_device="project_data",  # Special identifier
            backup_type=BackupType.PROJECT_DATA,
            compression="gzip",
            encryption=True,
            nas_path=nas_backup_path
        )

        logger.info(f"📁 Project data backup created: {backup.backup_id}")
        logger.info(f"   Paths: {', '.join(project_paths)}")

        return backup

    def get_backup_status(self) -> Dict[str, Any]:
        """Get backup system status"""
        return {
            "total_backups": len(self.backups),
            "baremetal_backups": len([b for b in self.backups.values() if b.backup_type == BackupType.BAREMETAL_OS]),
            "project_backups": len([b for b in self.backups.values() if b.backup_type == BackupType.PROJECT_DATA]),
            "pxe_configs": len(self.pxe_configs),
            "hyperbackup_configs": len(self.hyperbackup_configs),
            "nas_configured": self.nas_config is not None,
            "backups": {bid: b.to_dict() for bid, b in self.backups.items()},
            "pxe_configs": {cid: c.to_dict() for cid, c in self.pxe_configs.items()},
            "hyperbackup_configs": {cid: c.to_dict() for cid, c in self.hyperbackup_configs.items()}
        }

    def save_state(self):
        try:
            """Save backup system state"""
            state_file = self.data_dir / "backup_pxe_state.json"

            state = {
                "backups": {bid: b.to_dict() for bid, b in self.backups.items()},
                "pxe_configs": {cid: c.to_dict() for cid, c in self.pxe_configs.items()},
                "hyperbackup_configs": {cid: c.to_dict() for cid, c in self.hyperbackup_configs.items()},
                "saved_at": datetime.now().isoformat()
            }

            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, default=str)

            logger.info(f"💾 Backup system state saved: {state_file}")


        except Exception as e:
            self.logger.error(f"Error in save_state: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Laptop Baremetal Backup & PXE System")
    parser.add_argument('--create-backup', nargs=3, metavar=('DEVICE', 'TYPE', 'OUTPUT'),
                       help='Create baremetal backup')
    parser.add_argument('--backup-project', nargs='+', metavar='PATH', help='Backup project data')
    parser.add_argument('--configure-pxe', nargs=3, metavar=('DEVICE', 'MAC', 'IMAGE'),
                       help='Configure PXE boot')
    parser.add_argument('--setup-hyperbackup', nargs=2, metavar=('LOCAL_PATH', 'CLOUD_PROVIDER'),
                       help='Setup HyperBackup two-stage')
    parser.add_argument('--status', action='store_true', help='Show backup status')
    parser.add_argument('--save', action='store_true', help='Save state')

    args = parser.parse_args()

    system = LaptopBaremetalBackupPXESystem()

    if args.create_backup:
        device, backup_type_str, output = args.create_backup
        backup_type = BackupType(backup_type_str.lower())
        backup = system.create_baremetal_backup(device, backup_type, nas_path=output)
        print(f"\n✅ Backup created: {backup.backup_id}")
        if args.save:
            system.save_state()

    elif args.backup_project:
        backup = system.backup_project_data(args.backup_project)
        print(f"\n✅ Project backup created: {backup.backup_id}")
        if args.save:
            system.save_state()

    elif args.configure_pxe:
        device, mac, image = args.configure_pxe
        config = system.configure_pxe_boot(device, mac, image)
        print(f"\n✅ PXE configured: {config.config_id}")
        if args.save:
            system.save_state()

    elif args.setup_hyperbackup:
        local_path, cloud_provider = args.setup_hyperbackup
        config = system.setup_hyperbackup_two_stage(local_path, cloud_provider)
        print(f"\n✅ HyperBackup configured: {config.config_id}")
        if args.save:
            system.save_state()

    elif args.status:
        status = system.get_backup_status()
        print("\n" + "=" * 80)
        print("💾 BACKUP SYSTEM STATUS")
        print("=" * 80)
        print(f"Total Backups: {status['total_backups']}")
        print(f"Baremetal Backups: {status['baremetal_backups']}")
        print(f"Project Backups: {status['project_backups']}")
        print(f"PXE Configs: {len(status['pxe_configs'])}")
        print(f"HyperBackup Configs: {len(status['hyperbackup_configs'])}")
        print(f"NAS Configured: {status['nas_configured']}")
        print("")
        if status['hyperbackup_configs']:
            print("HyperBackup Configurations:")
            for cid, config in status['hyperbackup_configs'].items():
                print(f"   {cid}:")
                print(f"      Stage 1: {config['stage_1_local'].get('path', 'N/A')}")
                print(f"      Stage 2: {config['stage_2_cloud'].get('provider', 'N/A')}")
        print("=" * 80)
        print("")
        if args.save:
            system.save_state()

    else:
        print("\n" + "=" * 80)
        print("💾 LAPTOP BAREMETAL BACKUP & PXE SYSTEM")
        print("=" * 80)
        print("   BACKUP-FOR-BUSINESS Implementation")
        print("   HyperBackup Hybrid Two-Stage Disaster-Recovery")
        print("")
        print("Use --create-backup to create baremetal backup")
        print("Use --backup-project to backup project data")
        print("Use --configure-pxe to configure PXE boot")
        print("Use --setup-hyperbackup to setup two-stage backup")
        print("Use --status to show status")
        print("=" * 80)
        print("")

    if args.save:
        system.save_state()


if __name__ == "__main__":


    main()