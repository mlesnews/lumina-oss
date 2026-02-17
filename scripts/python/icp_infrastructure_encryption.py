#!/usr/bin/env python3
"""
ICP (Internet Computer Protocol) Infrastructure Encryption

Re-enciphers all infrastructure components using ICP encryption:
- Configuration files
- Data storage
- Network communications
- API endpoints
- Integration points
"""

import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ICPInfrastructureEncryption")


class ICPEncryptionManager:
    """Manage ICP-style encryption for infrastructure"""

    def __init__(self, project_root: Path, encryption_key: Optional[str] = None):
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "icp_encryption"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger("ICPEncryptionManager")

        # Generate or load encryption key
        self.encryption_key = encryption_key or self._generate_icp_key()
        self.cipher = self._create_cipher()

        # ICP configuration
        self.icp_config = {
            "protocol": "ICP",
            "encryption_method": "Fernet (ICP-compatible)",
            "key_derivation": "PBKDF2-HMAC-SHA256",
            "key_rotation_interval": "90_days",
            "encryption_scope": "infrastructure_wide"
        }

    def _generate_icp_key(self) -> str:
        """Generate ICP-compatible encryption key"""
        # Use project-specific seed for deterministic key generation
        seed = f"ICP_LUMINA_{self.project_root.name}_{datetime.now().strftime('%Y%m')}"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'lumina_icp_salt',
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(seed.encode()))
        return key.decode()

    def _create_cipher(self) -> Fernet:
        """Create Fernet cipher for encryption"""
        return Fernet(self.encryption_key.encode())

    def encrypt_infrastructure(self, infrastructure_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            """Encrypt infrastructure components"""
            self.logger.info("=" * 70)
            self.logger.info("ICP: Encrypting Infrastructure Components")
            self.logger.info("=" * 70)

            encrypted_infrastructure = {
                "timestamp": datetime.now().isoformat(),
                "icp_config": self.icp_config,
                "encrypted_components": {},
                "encryption_status": {}
            }

            # Encrypt configurations
            config_dir = self.project_root / "config"
            if config_dir.exists():
                encrypted_infrastructure["encrypted_components"]["configurations"] = self._encrypt_directory(
                    config_dir, 
                    exclude_patterns=["*.md", "*.txt"]
                )

            # Encrypt sensitive data
            data_dir = self.project_root / "data"
            if data_dir.exists():
                encrypted_infrastructure["encrypted_components"]["data"] = self._encrypt_directory(
                    data_dir,
                    exclude_patterns=["*.log", "*.tmp", "*.cache"],
                    include_patterns=["*secret*", "*password*", "*key*", "*token*", "*credential*"]
                )

            # Encrypt integration credentials
            encrypted_infrastructure["encrypted_components"]["integrations"] = self._encrypt_integrations()

            # Save encryption manifest
            manifest_file = self.data_dir / f"encryption_manifest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(manifest_file, 'w', encoding='utf-8') as f:
                json.dump(encrypted_infrastructure, f, indent=2, ensure_ascii=False, default=str)

            self.logger.info(f"Encryption manifest saved to: {manifest_file}")

            return encrypted_infrastructure

        except Exception as e:
            self.logger.error(f"Error in encrypt_infrastructure: {e}", exc_info=True)
            raise
    def _encrypt_directory(
        self, 
        directory: Path, 
        exclude_patterns: List[str] = None,
        include_patterns: List[str] = None
    ) -> Dict[str, Any]:
        """Encrypt files in directory"""
        encrypted_files = {}
        exclude_patterns = exclude_patterns or []
        include_patterns = include_patterns or []

        for file_path in directory.rglob("*"):
            if not file_path.is_file():
                continue

            # Check exclude patterns
            if any(file_path.match(pattern) for pattern in exclude_patterns):
                continue

            # Check include patterns (if specified)
            if include_patterns and not any(file_path.match(pattern) for pattern in include_patterns):
                continue

            # Skip already encrypted files
            if file_path.suffix == ".encrypted":
                continue

            try:
                # Read file
                with open(file_path, 'rb') as f:
                    file_data = f.read()

                # Encrypt
                encrypted_data = self.cipher.encrypt(file_data)

                # Save encrypted version
                encrypted_file = file_path.with_suffix(file_path.suffix + ".encrypted")
                with open(encrypted_file, 'wb') as f:
                    f.write(encrypted_data)

                encrypted_files[str(file_path.relative_to(self.project_root))] = {
                    "encrypted_file": str(encrypted_file.relative_to(self.project_root)),
                    "original_size": len(file_data),
                    "encrypted_size": len(encrypted_data),
                    "encrypted_at": datetime.now().isoformat()
                }

                self.logger.debug(f"Encrypted: {file_path.relative_to(self.project_root)}")

            except Exception as e:
                self.logger.warning(f"Error encrypting {file_path}: {e}")

        return encrypted_files

    def _encrypt_integrations(self) -> Dict[str, Any]:
        """Encrypt integration credentials"""
        integrations = {}

        # Encrypt API keys, tokens, credentials from config files
        config_files = [
            self.project_root / "config" / "lumina_extensions_integration.json",
            self.project_root / "config" / "r5" / "r5_config.json",
            self.project_root / "config" / "helpdesk" / "helpdesk_structure.json"
        ]

        for config_file in config_files:
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        config_data = json.load(f)

                    # Extract and encrypt sensitive fields
                    sensitive_fields = self._extract_sensitive_fields(config_data)
                    if sensitive_fields:
                        encrypted_fields = {}
                        for field, value in sensitive_fields.items():
                            encrypted_value = self.cipher.encrypt(str(value).encode())
                            encrypted_fields[field] = base64.urlsafe_b64encode(encrypted_value).decode()

                        integrations[str(config_file.relative_to(self.project_root))] = {
                            "encrypted_fields": encrypted_fields,
                            "encrypted_at": datetime.now().isoformat()
                        }

                except Exception as e:
                    self.logger.debug(f"Error processing {config_file}: {e}")

        return integrations

    def _extract_sensitive_fields(self, data: Any, prefix: str = "") -> Dict[str, str]:
        """Recursively extract sensitive fields from data structure"""
        sensitive_fields = {}
        sensitive_keywords = ["key", "token", "password", "secret", "credential", "api_key", "auth"]

        if isinstance(data, dict):
            for key, value in data.items():
                key_lower = key.lower()
                if any(keyword in key_lower for keyword in sensitive_keywords):
                    field_name = f"{prefix}.{key}" if prefix else key
                    sensitive_fields[field_name] = str(value)
                elif isinstance(value, (dict, list)):
                    sensitive_fields.update(self._extract_sensitive_fields(value, f"{prefix}.{key}" if prefix else key))

        elif isinstance(data, list):
            for i, item in enumerate(data):
                sensitive_fields.update(self._extract_sensitive_fields(item, f"{prefix}[{i}]"))

        return sensitive_fields

    def decrypt_file(self, encrypted_file: Path) -> bytes:
        try:
            """Decrypt an encrypted file"""
            with open(encrypted_file, 'rb') as f:
                encrypted_data = f.read()

            decrypted_data = self.cipher.decrypt(encrypted_data)
            return decrypted_data


        except Exception as e:
            self.logger.error(f"Error in decrypt_file: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="ICP Infrastructure Encryption")
        parser.add_argument(
            "--project-root",
            type=str,
            default=str(project_root),
            help="Project root directory"
        )
        parser.add_argument(
            "--encryption-key",
            type=str,
            help="Encryption key (optional, will generate if not provided)"
        )
        parser.add_argument(
            "--infrastructure-file",
            type=str,
            help="Infrastructure extraction JSON file from SYPHON"
        )

        args = parser.parse_args()

        # Load infrastructure data if provided
        infrastructure_data = {}
        if args.infrastructure_file:
            infrastructure_file = Path(args.infrastructure_file)
            if infrastructure_file.exists():
                with open(infrastructure_file, 'r') as f:
                    infrastructure_data = json.load(f)

        # Initialize encryption manager
        encryption_manager = ICPEncryptionManager(
            Path(args.project_root),
            args.encryption_key
        )

        # Encrypt infrastructure
        encrypted_infrastructure = encryption_manager.encrypt_infrastructure(infrastructure_data)

        logger.info("")
        logger.info("=" * 70)
        logger.info("ICP ENCRYPTION COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Configurations encrypted: {len(encrypted_infrastructure['encrypted_components'].get('configurations', {}))}")
        logger.info(f"Data files encrypted: {len(encrypted_infrastructure['encrypted_components'].get('data', {}))}")
        logger.info(f"Integrations encrypted: {len(encrypted_infrastructure['encrypted_components'].get('integrations', {}))}")
        logger.info("=" * 70)

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    sys.exit(main())