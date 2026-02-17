#!/usr/bin/env python3
"""
JARVIS Azure Storage Integration

Full integration with Azure Blob Storage for terminal log archival,
voice transcript storage, and workflow data persistence.

Tags: #AZURE #STORAGE #BLOB #ARCHIVAL #LUMINA @JARVIS
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("JARVISAzureStorage")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("JARVISAzureStorage")

# Azure Storage SDK
try:
    from azure.storage.blob import BlobServiceClient
    AZURE_STORAGE_AVAILABLE = True
except ImportError:
    AZURE_STORAGE_AVAILABLE = False
    logger.warning("Azure Storage SDK not available. Install with: pip install azure-storage-blob")

# Azure Key Vault for secrets
try:
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential
    AZURE_KV_AVAILABLE = True
except ImportError:
    AZURE_KV_AVAILABLE = False


class AzureStorageIntegration:
    """Azure Storage integration for JARVIS/LUMINA"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_file = project_root / "config" / "azure_services_config.json"
        self.config = self.load_config()
        self.blob_service_client = None
        self.connection_string = None
        self.storage_account = self.config.get("storage", {}).get("accounts", {}).get("primary", {}).get("name", "jarvisluminastorage")

        self._initialize_client()

    def load_config(self) -> Dict[str, Any]:
        """Load Azure services configuration"""
        default_config = {
            "storage": {
                "enabled": False,
                "accounts": {
                    "primary": {
                        "name": "jarvisluminastorage",
                        "connection_string_secret": "azure-storage-connection-string"
                    }
                }
            }
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    azure_config = data.get("azure_services_config", {})
                    if azure_config.get("storage"):
                        default_config["storage"].update(azure_config["storage"])
            except Exception as e:
                logger.error(f"Error loading Azure config: {e}")

        return default_config

    def _get_connection_string(self) -> Optional[str]:
        """Get Storage connection string from Key Vault or environment"""
        # Try Key Vault first
        if AZURE_KV_AVAILABLE:
            try:
                vault_url = self.config.get("key_vault", {}).get("vault_url") or "https://jarvis-lumina.vault.azure.net/"
                secret_name = self.config.get("storage", {}).get("accounts", {}).get("primary", {}).get("connection_string_secret", "azure-storage-connection-string")

                credential = DefaultAzureCredential(


                                    exclude_interactive_browser_credential=False,


                                    exclude_shared_token_cache_credential=False


                                )
                secret_client = SecretClient(vault_url=vault_url, credential=credential)
                connection_string = secret_client.get_secret(secret_name).value
                return connection_string
            except Exception as e:
                logger.debug(f"Could not get connection string from Key Vault: {e}")

        # Fallback to environment variable
        import os
        return os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    def _initialize_client(self):
        """Initialize Blob Service Client"""
        if not AZURE_STORAGE_AVAILABLE:
            logger.warning("Azure Storage SDK not available")
            return

        if not self.config.get("storage", {}).get("enabled", False):
            logger.info("Azure Storage not enabled in config")
            return

        try:
            self.connection_string = self._get_connection_string()
            if not self.connection_string:
                logger.warning("Storage connection string not found")
                return

            self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
            logger.info("✅ Azure Storage client initialized")
        except Exception as e:
            logger.error(f"Error initializing Storage client: {e}")

    def upload_blob(self, container_name: str, blob_name: str, data: bytes, content_type: str = None) -> Dict[str, Any]:
        """Upload blob to Azure Storage"""
        if not self.blob_service_client:
            return {
                "success": False,
                "error": "Storage client not initialized"
            }

        try:
            blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
            blob_client.upload_blob(data, overwrite=True, content_settings={"content_type": content_type} if content_type else None)

            return {
                "success": True,
                "container": container_name,
                "blob": blob_name,
                "url": blob_client.url
            }
        except Exception as e:
            logger.error(f"Error uploading blob: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def upload_file(self, container_name: str, blob_name: str, file_path: Path) -> Dict[str, Any]:
        """Upload file to Azure Storage"""
        if not self.blob_service_client:
            return {
                "success": False,
                "error": "Storage client not initialized"
            }

        try:
            with open(file_path, 'rb') as f:
                data = f.read()

            content_type = None
            if file_path.suffix == '.json':
                content_type = 'application/json'
            elif file_path.suffix == '.log':
                content_type = 'text/plain'
            elif file_path.suffix == '.txt':
                content_type = 'text/plain'

            return self.upload_blob(container_name, blob_name, data, content_type)
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def archive_terminal_log(self, log_file: Path, container_name: str = "work-logs") -> Dict[str, Any]:
        try:
            """Archive terminal log to Azure Storage"""
            if not log_file.exists():
                return {
                    "success": False,
                    "error": "Log file does not exist"
                }

            # Create blob name with date path
            date_path = datetime.now().strftime("%Y/%m/%d")
            blob_name = f"terminal-logs/{date_path}/{log_file.name}"

            return self.upload_file(container_name, blob_name, log_file)

        except Exception as e:
            self.logger.error(f"Error in archive_terminal_log: {e}", exc_info=True)
            raise
    def archive_voice_transcript(self, transcript_data: Dict[str, Any], container_name: str = "session-data") -> Dict[str, Any]:
        try:
            """Archive voice transcript to Azure Storage"""
            data = json.dumps(transcript_data, indent=2, default=str).encode('utf-8')

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            blob_name = f"voice-transcripts/{timestamp}.json"

            return self.upload_blob(container_name, blob_name, data, "application/json")

        except Exception as e:
            self.logger.error(f"Error in archive_voice_transcript: {e}", exc_info=True)
            raise
    def ensure_container_exists(self, container_name: str) -> bool:
        """Ensure container exists, create if not"""
        if not self.blob_service_client:
            return False

        try:
            container_client = self.blob_service_client.get_container_client(container_name)
            if not container_client.exists():
                container_client.create_container()
                logger.info(f"✅ Created container: {container_name}")
            return True
        except Exception as e:
            logger.error(f"Error ensuring container exists: {e}")
            return False


def get_azure_storage(project_root_path: Path = None) -> AzureStorageIntegration:
    try:
        """Get or create Azure Storage integration instance"""
        if project_root_path is None:
            project_root_path = Path(__file__).parent.parent.parent
        return AzureStorageIntegration(project_root_path)


    except Exception as e:
        logger.error(f"Error in get_azure_storage: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    # Test
    storage = get_azure_storage()
    print(f"Storage client initialized: {storage.blob_service_client is not None}")
