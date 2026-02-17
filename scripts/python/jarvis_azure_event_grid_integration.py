#!/usr/bin/env python3
"""
JARVIS Azure Event Grid Integration

Full integration with Azure Event Grid for real-time event routing
and event-driven architecture.

Tags: #AZURE #EVENT_GRID #EVENT_DRIVEN #REALTIME #LUMINA @JARVIS
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
    logger = get_comprehensive_logger("JARVISAzureEventGrid")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("JARVISAzureEventGrid")

# Azure Event Grid SDK
try:
    from azure.eventgrid import EventGridPublisherClient
    from azure.core.credentials import AzureKeyCredential
    from azure.core import exceptions
    AZURE_EVENT_GRID_AVAILABLE = True
except ImportError:
    AZURE_EVENT_GRID_AVAILABLE = False
    logger.warning("Azure Event Grid SDK not available. Install with: pip install azure-eventgrid")

# Azure Key Vault for secrets
try:
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential
    AZURE_KV_AVAILABLE = True
except ImportError:
    AZURE_KV_AVAILABLE = False


class AzureEventGridIntegration:
    """Azure Event Grid integration for JARVIS/LUMINA"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_file = project_root / "config" / "azure_services_config.json"
        self.config = self.load_config()
        self.publisher_clients: Dict[str, EventGridPublisherClient] = {}
        self.topic_endpoints: Dict[str, str] = {}

        self._initialize_clients()

    def load_config(self) -> Dict[str, Any]:
        """Load Azure services configuration"""
        default_config = {
            "event_grid": {
                "enabled": False,
                "topics": {}
            }
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    azure_config = data.get("azure_services_config", {})
                    if azure_config.get("event_grid"):
                        default_config["event_grid"].update(azure_config["event_grid"])
            except Exception as e:
                logger.error(f"Error loading Azure config: {e}")

        return default_config

    def _get_topic_key(self, topic_name: str) -> Optional[str]:
        """Get Event Grid topic key from Key Vault"""
        if AZURE_KV_AVAILABLE:
            try:
                vault_url = self.config.get("key_vault", {}).get("vault_url") or "https://jarvis-lumina.vault.azure.net/"
                secret_name = f"event-grid-{topic_name}-key"

                credential = DefaultAzureCredential(


                                    exclude_interactive_browser_credential=False,


                                    exclude_shared_token_cache_credential=False


                                )
                secret_client = SecretClient(vault_url=vault_url, credential=credential)
                key = secret_client.get_secret(secret_name).value
                return key
            except Exception as e:
                logger.debug(f"Could not get topic key from Key Vault: {e}")

        import os
        return os.getenv(f"AZURE_EVENT_GRID_{topic_name.upper()}_KEY")

    def _get_topic_endpoint(self, topic_name: str) -> Optional[str]:
        """Get Event Grid topic endpoint"""
        # Try config first
        topics = self.config.get("event_grid", {}).get("topics", {})
        for topic_key, topic_config in topics.items():
            if topic_config.get("name") == topic_name:
                # Construct endpoint URL
                return f"https://{topic_name}.{self.config.get('location', 'eastus')}.eventgrid.azure.net/api/events"

        # Fallback to environment variable
        import os
        return os.getenv(f"AZURE_EVENT_GRID_{topic_name.upper()}_ENDPOINT")

    def _initialize_clients(self):
        """Initialize Event Grid publisher clients for all topics"""
        if not AZURE_EVENT_GRID_AVAILABLE:
            logger.warning("Azure Event Grid SDK not available")
            return

        if not self.config.get("event_grid", {}).get("enabled", False):
            logger.info("Azure Event Grid not enabled in config")
            return

        topics = self.config.get("event_grid", {}).get("topics", {})
        for topic_key, topic_config in topics.items():
            topic_name = topic_config.get("name")
            if not topic_name:
                continue

            try:
                endpoint = self._get_topic_endpoint(topic_name)
                key = self._get_topic_key(topic_name)

                if endpoint and key:
                    credential = AzureKeyCredential(key)
                    client = EventGridPublisherClient(endpoint, credential)
                    self.publisher_clients[topic_name] = client
                    self.topic_endpoints[topic_name] = endpoint
                    logger.info(f"✅ Event Grid client initialized for topic: {topic_name}")
            except Exception as e:
                logger.debug(f"Could not initialize Event Grid client for {topic_name}: {e}")

    def publish_event(self, topic_name: str, event_type: str, data: Dict[str, Any], subject: str = None) -> Dict[str, Any]:
        """Publish event to Event Grid topic"""
        if topic_name not in self.publisher_clients:
            return {
                "success": False,
                "error": f"Topic '{topic_name}' not initialized"
            }

        try:
            from azure.eventgrid import EventGridEvent

            event = EventGridEvent(
                subject=subject or f"lumina/{event_type}",
                data=data,
                event_type=event_type,
                data_version="1.0"
            )

            client = self.publisher_clients[topic_name]
            client.send([event])

            return {
                "success": True,
                "topic": topic_name,
                "event_type": event_type
            }
        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def publish_system_event(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Publish system event to system-events topic"""
        return self.publish_event("jarvis-system-events", event_type, data, subject="lumina/system")

    def publish_terminal_output(self, output_data: Dict[str, Any]) -> Dict[str, Any]:
        """Publish terminal output event"""
        return self.publish_system_event("lumina.terminal.output", output_data)

    def publish_voice_transcript(self, transcript_data: Dict[str, Any]) -> Dict[str, Any]:
        """Publish voice transcript event"""
        return self.publish_system_event("lumina.voice.transcript", transcript_data)


def get_azure_event_grid(project_root: Path = None) -> AzureEventGridIntegration:
    try:
        """Get or create Azure Event Grid integration instance"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        return AzureEventGridIntegration(project_root)


    except Exception as e:
        logger.error(f"Error in get_azure_event_grid: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    # Test
    event_grid = get_azure_event_grid()
    print(f"Event Grid clients initialized: {len(event_grid.publisher_clients)}")
