#!/usr/bin/env python3
"""
JARVIS Azure Cosmos DB Integration

Full integration with Azure Cosmos DB for holocron, agent sessions,
and workflow data storage with global distribution.

Tags: #AZURE #COSMOS_DB #NOSQL #GLOBAL #LUMINA @JARVIS
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("JARVISAzureCosmosDB")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("JARVISAzureCosmosDB")

# Azure Cosmos DB SDK
try:
    from azure.cosmos import CosmosClient, PartitionKey, exceptions
    AZURE_COSMOS_AVAILABLE = True
except ImportError:
    AZURE_COSMOS_AVAILABLE = False
    logger.warning("Azure Cosmos DB SDK not available. Install with: pip install azure-cosmos")

# Azure Key Vault for secrets
try:
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential
    AZURE_KV_AVAILABLE = True
except ImportError:
    AZURE_KV_AVAILABLE = False


class AzureCosmosDBIntegration:
    """Azure Cosmos DB integration for JARVIS/LUMINA"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_file = project_root / "config" / "azure_services_config.json"
        self.config = self.load_config()
        self.client = None
        self.database = None
        self.endpoint = None
        self.key = None

        self._initialize_client()

    def load_config(self) -> Dict[str, Any]:
        """Load Azure services configuration"""
        default_config = {
            "cosmos_db": {
                "enabled": False,
                "account": "jarvis-lumina-cosmos",
                "database": "lumina",
                "containers": {
                    "holocron": {"partition_key": "/id"},
                    "agent_sessions": {"partition_key": "/session_id"},
                    "workflow_data": {"partition_key": "/workflow_id"}
                }
            }
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    azure_config = data.get("azure_services_config", {})
                    if azure_config.get("cosmos_db"):
                        default_config["cosmos_db"].update(azure_config["cosmos_db"])
            except Exception as e:
                logger.error(f"Error loading Azure config: {e}")

        return default_config

    def _get_endpoint_and_key(self) -> tuple[Optional[str], Optional[str]]:
        """Get Cosmos DB endpoint and key from Key Vault"""
        if AZURE_KV_AVAILABLE:
            try:
                vault_url = self.config.get("key_vault", {}).get("vault_url") or "https://jarvis-lumina.vault.azure.net/"

                credential = DefaultAzureCredential(


                                    exclude_interactive_browser_credential=False,


                                    exclude_shared_token_cache_credential=False


                                )
                secret_client = SecretClient(vault_url=vault_url, credential=credential)

                endpoint_secret = secret_client.get_secret("cosmos-db-endpoint").value
                key_secret = secret_client.get_secret("cosmos-db-key").value

                return endpoint_secret, key_secret
            except Exception as e:
                logger.debug(f"Could not get Cosmos DB credentials from Key Vault: {e}")

        import os
        endpoint = os.getenv("AZURE_COSMOS_DB_ENDPOINT")
        key = os.getenv("AZURE_COSMOS_DB_KEY")
        return endpoint, key

    def _initialize_client(self):
        """Initialize Cosmos DB client"""
        if not AZURE_COSMOS_AVAILABLE:
            logger.warning("Azure Cosmos DB SDK not available")
            return

        if not self.config.get("cosmos_db", {}).get("enabled", False):
            logger.info("Azure Cosmos DB not enabled in config")
            return

        try:
            self.endpoint, self.key = self._get_endpoint_and_key()
            if not self.endpoint or not self.key:
                logger.warning("Cosmos DB endpoint or key not found")
                return

            self.client = CosmosClient(self.endpoint, self.key)
            database_name = self.config.get("cosmos_db", {}).get("database", "lumina")
            self.database = self.client.get_database_client(database_name)

            # Ensure database exists
            try:
                self.database.read()
            except exceptions.CosmosResourceNotFoundError:
                self.database = self.client.create_database(database_name)
                logger.info(f"✅ Created Cosmos DB database: {database_name}")

            # Ensure containers exist
            containers = self.config.get("cosmos_db", {}).get("containers", {})
            for container_name, container_config in containers.items():
                self._ensure_container_exists(container_name, container_config.get("partition_key", "/id"))

            logger.info("✅ Azure Cosmos DB client initialized")
        except Exception as e:
            logger.error(f"Error initializing Cosmos DB client: {e}")

    def _ensure_container_exists(self, container_name: str, partition_key: str = "/id"):
        """Ensure container exists, create if not"""
        if not self.database:
            return False

        try:
            container = self.database.get_container_client(container_name)
            try:
                container.read()
            except exceptions.CosmosResourceNotFoundError:
                self.database.create_container(
                    id=container_name,
                    partition_key=PartitionKey(path=partition_key)
                )
                logger.info(f"✅ Created Cosmos DB container: {container_name}")
            return True
        except Exception as e:
            logger.error(f"Error ensuring container exists: {e}")
            return False

    def create_item(self, container_name: str, item: Dict[str, Any]) -> Dict[str, Any]:
        """Create item in Cosmos DB container"""
        if not self.database:
            return {
                "success": False,
                "error": "Cosmos DB client not initialized"
            }

        try:
            container = self.database.get_container_client(container_name)
            result = container.create_item(item)
            return {
                "success": True,
                "id": result.get("id"),
                "item": result
            }
        except Exception as e:
            logger.error(f"Error creating item: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def read_item(self, container_name: str, item_id: str, partition_key: str) -> Dict[str, Any]:
        """Read item from Cosmos DB container"""
        if not self.database:
            return {
                "success": False,
                "error": "Cosmos DB client not initialized"
            }

        try:
            container = self.database.get_container_client(container_name)
            item = container.read_item(item=item_id, partition_key=partition_key)
            return {
                "success": True,
                "item": item
            }
        except Exception as e:
            logger.error(f"Error reading item: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def query_items(self, container_name: str, query: str, parameters: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Query items from Cosmos DB container"""
        if not self.database:
            return {
                "success": False,
                "error": "Cosmos DB client not initialized"
            }

        try:
            container = self.database.get_container_client(container_name)
            items = list(container.query_items(query=query, parameters=parameters or []))
            return {
                "success": True,
                "items": items,
                "count": len(items)
            }
        except Exception as e:
            logger.error(f"Error querying items: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def store_holocron_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Store holocron entry in Cosmos DB"""
        entry["id"] = entry.get("id") or f"holocron_{datetime.now().isoformat()}"
        entry["timestamp"] = datetime.now().isoformat()
        return self.create_item("holocron", entry)

    def store_agent_session(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Store agent session in Cosmos DB"""
        session["id"] = session.get("session_id") or f"session_{datetime.now().isoformat()}"
        session["timestamp"] = datetime.now().isoformat()
        return self.create_item("agent_sessions", session)


def get_azure_cosmos_db(project_root: Path = None) -> AzureCosmosDBIntegration:
    try:
        """Get or create Azure Cosmos DB integration instance"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        return AzureCosmosDBIntegration(project_root)


    except Exception as e:
        logger.error(f"Error in get_azure_cosmos_db: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    # Test
    cosmos = get_azure_cosmos_db()
    print(f"Cosmos DB client initialized: {cosmos.client is not None}")
