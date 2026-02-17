#!/usr/bin/env python3
"""
LUMINA NAS Network Storage for YouTube Content

"USE NAS NETWORK STORAGE FOR AND MAP OUT THE DRIVE FOR LUMINA-YT"

This system:
- Maps NAS network drive for LUMINA YouTube content
- Configures storage paths for video production
- Manages NAS storage for episodes, trailers, and content
- Integrates with video production system
"""

import sys
import json
import subprocess
import platform
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LuminaNASYTStorage")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class StorageType(Enum):
    """Storage types"""
    TRAILERS = "trailers"
    EPISODES = "episodes"
    RAW_FOOTAGE = "raw_footage"
    EDITED_CONTENT = "edited_content"
    EIGHTIES_SEGMENTS = "eighties_segments"
    THUMBNAILS = "thumbnails"
    ASSETS = "assets"
    ARCHIVE = "archive"


@dataclass
class NASStorageConfig:
    """NAS storage configuration"""
    nas_host: str
    nas_ip: str
    nas_username: str
    share_name: str
    mount_point: str  # Windows drive letter or Linux mount point
    lumina_yt_base_path: str
    storage_types: Dict[StorageType, str] = field(default_factory=dict)
    is_mapped: bool = False
    last_mapped: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["storage_types"] = {k.value: v for k, v in self.storage_types.items()}
        return data


class LuminaNASYTStorage:
    """
    LUMINA NAS Network Storage for YouTube Content

    Maps NAS network drive and configures storage paths for:
    - Video production
    - Episode storage
    - Trailer storage
    - 1980s segments
    - Assets and archives
    """

    # Default NAS configuration (Synology NAS)
    DEFAULT_NAS_IP = "<NAS_PRIMARY_IP>"
    DEFAULT_NAS_HOST = "nas"
    DEFAULT_SHARE_NAME = "LUMINA-YT"
    DEFAULT_MOUNT_POINT = "Y:"  # Windows drive letter

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize NAS Storage System"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("LuminaNASYTStorage")

        # NAS configuration
        self.config: Optional[NASStorageConfig] = None

        # Data storage
        self.data_dir = self.project_root / "data" / "lumina_nas_yt_storage"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load or create configuration
        self._load_config()

        # Initialize storage paths
        self._initialize_storage_paths()

        self.logger.info("💾 LUMINA NAS YouTube Storage initialized")
        self.logger.info(f"   NAS IP: {self.config.nas_ip}")
        self.logger.info(f"   Share: {self.config.share_name}")
        self.logger.info(f"   Mount Point: {self.config.mount_point}")

    def _load_config(self) -> None:
        """Load NAS configuration"""
        config_file = self.data_dir / "nas_config.json"

        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    storage_types = {
                        StorageType(k): v for k, v in data.get('storage_types', {}).items()
                    }
                    self.config = NASStorageConfig(
                        storage_types=storage_types,
                        **{k: v for k, v in data.items() if k != 'storage_types'}
                    )
                self.logger.info("  ✅ Loaded existing NAS configuration")
            except Exception as e:
                self.logger.warning(f"  ⚠️  Could not load config: {e}")
                self._create_default_config()
        else:
            self._create_default_config()

    def _create_default_config(self) -> None:
        """Create default NAS configuration"""
        # Try to get NAS credentials from Azure Key Vault
        nas_username = "backupadm"  # Default
        nas_password = None

        try:
            from nas_azure_vault_integration import NASAzureVaultIntegration
            vault = NASAzureVaultIntegration()
            # Try to get username/password from vault (if methods exist)
            try:
                if hasattr(vault, 'get_nas_username'):
                    nas_username = vault.get_nas_username() or nas_username
                # Password retrieval would be handled during mapping
            except Exception:
                pass  # Use defaults
            self.logger.info("  ✅ NAS Azure Vault integration available")
        except Exception as e:
            self.logger.warning(f"  ⚠️  Could not load from Key Vault: {e}")

        # Base path on NAS
        lumina_yt_base = f"/volume1/{self.DEFAULT_SHARE_NAME}"

        # Storage type paths
        storage_types = {
            StorageType.TRAILERS: f"{lumina_yt_base}/trailers",
            StorageType.EPISODES: f"{lumina_yt_base}/episodes",
            StorageType.RAW_FOOTAGE: f"{lumina_yt_base}/raw_footage",
            StorageType.EDITED_CONTENT: f"{lumina_yt_base}/edited_content",
            StorageType.EIGHTIES_SEGMENTS: f"{lumina_yt_base}/eighties_segments",
            StorageType.THUMBNAILS: f"{lumina_yt_base}/thumbnails",
            StorageType.ASSETS: f"{lumina_yt_base}/assets",
            StorageType.ARCHIVE: f"{lumina_yt_base}/archive"
        }

        self.config = NASStorageConfig(
            nas_host=self.DEFAULT_NAS_HOST,
            nas_ip=self.DEFAULT_NAS_IP,
            nas_username=nas_username,
            share_name=self.DEFAULT_SHARE_NAME,
            mount_point=self.DEFAULT_MOUNT_POINT,
            lumina_yt_base_path=lumina_yt_base,
            storage_types=storage_types
        )

        self._save_config()
        self.logger.info("  ✅ Created default NAS configuration")

    def _save_config(self) -> None:
        try:
            """Save NAS configuration"""
            config_file = self.data_dir / "nas_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config.to_dict(), f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_config: {e}", exc_info=True)
            raise
    def _initialize_storage_paths(self) -> None:
        """Initialize storage directory paths on NAS"""
        # This would create directories on NAS if needed
        # For now, just log the paths
        self.logger.info("  📁 Storage paths configured:")
        for storage_type, path in self.config.storage_types.items():
            self.logger.info(f"     {storage_type.value}: {path}")

    def map_network_drive(self) -> bool:
        """
        Map NAS network drive

        Returns: True if mapping successful
        """
        if platform.system() != "Windows":
            self.logger.warning("  ⚠️  Network drive mapping is Windows-specific")
            return False

        self.logger.info(f"  🔌 Mapping network drive: {self.config.mount_point}")
        self.logger.info(f"     NAS: \\\\{self.config.nas_ip}\\{self.config.share_name}")

        # Windows net use command
        # net use Y: \\<NAS_PRIMARY_IP>\LUMINA-YT /user:username password /persistent:yes
        try:
            # Try to get password from Azure Key Vault
            password = None
            try:
                from nas_azure_vault_integration import NASAzureVaultIntegration
                vault = NASAzureVaultIntegration()
                credentials = vault.get_nas_credentials()
                if credentials:
                    password = credentials.get("password")
                    if not self.config.nas_username or self.config.nas_username == "backupadm":
                        self.config.nas_username = credentials.get("username", self.config.nas_username)
            except Exception as e:
                logger.debug(f"Could not get credentials from vault: {e}")

            # Always use persistent mapping (/persistent:yes)
            mount_point = self.config.mount_point.rstrip(":")
            network_path = f"\\\\{self.config.nas_ip}\\{self.config.share_name}"

            # Ensure persistent mapping is always used
            if not password:
                self.logger.warning("  ⚠️  Password not available - mapping may require manual authentication")
                # Try mapping with persistent flag - user will be prompted for password
                command = [
                    "net", "use",
                    f"{mount_point}:",
                    network_path,
                    "/persistent:yes"
                ]
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    check=False
                )
            else:
                # Use PowerShell for secure password handling with persistent mapping
                password_escaped = password.replace('"', '`"').replace('$', '`$').replace('&', '`&')
                ps_command = f'''
$password = ConvertTo-SecureString -String "{password_escaped}" -AsPlainText -Force;
$credential = New-Object System.Management.Automation.PSCredential("{self.config.nas_username}", $password);
New-PSDrive -Name "{mount_point}" -PSProvider FileSystem -Root "{network_path}" -Credential $credential -Persist -Scope Global;
Set-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\NetworkProvider" -Name "RestoreConnection" -Value 1 -ErrorAction SilentlyContinue
'''
                try:
                    result = subprocess.run(
                        ["powershell", "-Command", ps_command],
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    if result.returncode == 0:
                        self.config.is_mapped = True
                        self.config.last_mapped = datetime.now().isoformat()
                        self._save_config()
                        self.logger.info(f"  ✅ Network drive mapped persistently: {mount_point}:")
                        return True
                except Exception as e:
                    logger.debug(f"PowerShell mapping failed: {e}")

                # Fallback to net use with persistent flag
                # Note: Password in command line is less secure but necessary for automation
                command = [
                    "net", "use",
                    f"{mount_point}:",
                    network_path,
                    f"/user:{self.config.nas_username}",
                    password,
                    "/persistent:yes"  # Always persistent
                ]
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    check=False,
                    input=password if not password else None
                )

            # Check result
            if result.returncode == 0 or "successfully" in result.stdout.lower() or "successfully" in result.stderr.lower():
                # Verify persistent setting
                verify_command = ["net", "use", f"{mount_point}:"]
                verify_result = subprocess.run(verify_command, capture_output=True, text=True, check=False)
                if "Persistent" in verify_result.stdout or "/persistent:yes" in str(result.stdout + result.stderr):
                    self.config.is_mapped = True
                    self.config.last_mapped = datetime.now().isoformat()
                    self._save_config()
                    self.logger.info(f"  ✅ Network drive mapped with persistent connection: {mount_point}:")
                    return True

            if result.returncode == 0 or "successfully" in result.stdout.lower():
                self.config.is_mapped = True
                self.config.last_mapped = datetime.now().isoformat()
                self._save_config()
                self.logger.info(f"  ✅ Network drive mapped: {self.config.mount_point}:")
                return True
            else:
                self.logger.warning(f"  ⚠️  Mapping failed: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"  ❌ Error mapping drive: {e}")
            return False

    def unmap_network_drive(self) -> bool:
        """Unmap network drive"""
        if platform.system() != "Windows":
            return False

        self.logger.info(f"  🔌 Unmapping network drive: {self.config.mount_point}")

        try:
            command = ["net", "use", f"{self.config.mount_point}:", "/delete", "/yes"]
            result = subprocess.run(command, capture_output=True, text=True, check=False)

            if result.returncode == 0:
                self.config.is_mapped = False
                self._save_config()
                self.logger.info(f"  ✅ Network drive unmapped: {self.config.mount_point}:")
                return True
            else:
                self.logger.warning(f"  ⚠️  Unmapping failed: {result.stderr}")
                return False
        except Exception as e:
            self.logger.error(f"  ❌ Error unmapping drive: {e}")
            return False

    def check_drive_mapped(self) -> bool:
        """Check if network drive is mapped"""
        if platform.system() != "Windows":
            # For non-Windows, check if mount point exists
            mount_path = Path(self.config.mount_point)
            return mount_path.exists() and mount_path.is_dir()

        try:
            command = ["net", "use"]
            result = subprocess.run(command, capture_output=True, text=True, check=True)

            mount_point = f"{self.config.mount_point}:"
            is_mapped = mount_point in result.stdout

            if is_mapped != self.config.is_mapped:
                self.config.is_mapped = is_mapped
                self._save_config()

            return is_mapped
        except Exception:
            return False

    def get_storage_path(self, storage_type: StorageType) -> Path:
        try:
            """
            Get storage path for given type

            Returns: Path object (local mount point + NAS path)
            """
            nas_path = self.config.storage_types.get(storage_type, "")

            # Convert NAS path to Windows path if needed
            if platform.system() == "Windows":
                # Remove /volume1 prefix and get relative path
                if nas_path.startswith("/volume1/"):
                    relative_path = nas_path.replace("/volume1/", "")
                else:
                    relative_path = nas_path.lstrip("/")

                # Convert to Windows path format
                relative_path = relative_path.replace("/", "\\")

                # Mount point should be like "Y:" (not "Y::")
                mount = self.config.mount_point.rstrip(":")
                local_path = Path(f"{mount}:\\{relative_path}")
            else:
                # Linux/Mac - use mount point directly
                relative_path = nas_path.lstrip("/")
                local_path = Path(self.config.mount_point) / relative_path

            return local_path

        except Exception as e:
            self.logger.error(f"Error in get_storage_path: {e}", exc_info=True)
            raise
    def ensure_storage_paths(self) -> None:
        """Ensure all storage directories exist"""
        self.logger.info("  📁 Ensuring storage directories exist...")

        if not self.check_drive_mapped():
            self.logger.warning("  ⚠️  Network drive not mapped - cannot create directories")
            return

        for storage_type, nas_path in self.config.storage_types.items():
            local_path = self.get_storage_path(storage_type)
            try:
                local_path.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"  ✅ {storage_type.value}: {local_path}")
            except Exception as e:
                self.logger.warning(f"  ⚠️  Could not create {storage_type.value}: {e}")

    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary"""
        return {
            "nas_ip": self.config.nas_ip,
            "nas_host": self.config.nas_host,
            "share_name": self.config.share_name,
            "mount_point": self.config.mount_point,
            "is_mapped": self.config.is_mapped,
            "last_mapped": self.config.last_mapped,
            "storage_paths": {
                storage_type.value: str(self.get_storage_path(storage_type))
                for storage_type in StorageType
            }
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="LUMINA NAS YouTube Storage")
    parser.add_argument("--map", action="store_true", help="Map network drive")
    parser.add_argument("--unmap", action="store_true", help="Unmap network drive")
    parser.add_argument("--check", action="store_true", help="Check if drive is mapped")
    parser.add_argument("--ensure-paths", action="store_true", help="Ensure storage directories exist")
    parser.add_argument("--summary", action="store_true", help="Get configuration summary")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    storage = LuminaNASYTStorage()

    if args.map:
        success = storage.map_network_drive()
        print(f"{'✅' if success else '❌'} Drive mapping: {'Success' if success else 'Failed'}")

    elif args.unmap:
        success = storage.unmap_network_drive()
        print(f"{'✅' if success else '❌'} Drive unmapping: {'Success' if success else 'Failed'}")

    elif args.check:
        is_mapped = storage.check_drive_mapped()
        print(f"{'✅' if is_mapped else '❌'} Drive status: {'Mapped' if is_mapped else 'Not Mapped'}")

    elif args.ensure_paths:
        storage.ensure_storage_paths()
        print("✅ Storage paths ensured")

    elif args.summary:
        summary = storage.get_config_summary()
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print(f"\n💾 LUMINA NAS YouTube Storage")
            print(f"   NAS IP: {summary['nas_ip']}")
            print(f"   Share: {summary['share_name']}")
            print(f"   Mount Point: {summary['mount_point']}")
            print(f"   Status: {'Mapped' if summary['is_mapped'] else 'Not Mapped'}")
            print(f"\n   Storage Paths:")
            for storage_type, path in summary['storage_paths'].items():
                print(f"     {storage_type}: {path}")

    else:
        parser.print_help()
        print("\n💾 LUMINA NAS YouTube Storage")
        print("   Maps NAS network drive for LUMINA-YT content")

