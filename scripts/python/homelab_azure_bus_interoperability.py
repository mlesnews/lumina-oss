#!/usr/bin/env python3
"""
Homelab Azure Service Bus Interoperability System

Provides async Azure Service Bus connectivity for all @HOMELAB assets at multiple
infrastructure and inference layers, coordinating interconnectivity, security,
network, and system engineering teams.

@FALC @NAS @PFSENSEFW @KAIJU_NO_8 @HOMELAB @COMPANY
#AZURE_SERVICE_BUS #INTEROPERABILITY #INFRASTRUCTURE #INFERENCE #ASYNC
"""

import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import threading

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("HomelabAzureBusInterop")

# Import Azure Service Bus integration
try:
    from azure_service_bus_integration import (
        AzureServiceBusClient,
        ServiceBusMessage,
        MessageType,
        get_service_bus_client,
        get_key_vault_client
    )
    AZURE_BUS_AVAILABLE = True
except ImportError:
    AZURE_BUS_AVAILABLE = False
    AzureServiceBusClient = None
    ServiceBusMessage = None
    MessageType = None
    logger.warning("⚠️  Azure Service Bus integration not available")


class AssetType(Enum):
    """Homelab asset types"""
    SYSTEM = "system"
    STORAGE = "storage"
    FIREWALL = "firewall"
    WORKSTATION = "workstation"
    INFRASTRUCTURE = "infrastructure"
    ORGANIZATION = "organization"


class LayerType(Enum):
    """Infrastructure and inference layer types"""
    INFRASTRUCTURE = "infrastructure"
    INFERENCE = "inference"


class TeamType(Enum):
    """Engineering team types"""
    INTERCONNECTIVITY_TEAM = "interconnectivity_team"
    SECURITY_TEAM = "security_team"
    NETWORK_TEAM = "network_team"
    SYSTEM_ENGINEERING_TEAM = "system_engineering_team"


@dataclass
class HomelabAsset:
    """Homelab asset configuration"""
    asset_id: str
    name: str
    asset_type: AssetType
    ip_address: Optional[str] = None
    hostname: Optional[str] = None
    topics: List[str] = field(default_factory=list)
    queues: List[str] = field(default_factory=list)
    subscriptions: List[str] = field(default_factory=list)
    infrastructure_topics: List[str] = field(default_factory=list)
    inference_topics: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EngineeringTeam:
    """Engineering team configuration"""
    team_id: str
    name: str
    team_type: TeamType
    topics: List[str] = field(default_factory=list)
    queues: List[str] = field(default_factory=list)
    assets: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class HomelabAzureBusInteroperability:
    """
    Homelab Azure Service Bus Interoperability System

    Provides async Azure Service Bus connectivity for:
    - @FALC
    - @NAS (<NAS_PRIMARY_IP>)
    - @PFSENSEFW (<NAS_IP>)
    - @KAIJU_NO_8 (<NAS_IP>)
    - @HOMELAB (entire homelab)
    - @COMPANY (entire company)

    At multiple infrastructure and inference layers, coordinating:
    - Interconnectivity Engineering Team
    - Security Engineering Team
    - Network Engineering Team
    - System Engineering Team
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Load configuration
        self.config_file = project_root / "config" / "homelab_azure_bus_interoperability.json"
        self.config = self._load_config()

        # Initialize Azure Service Bus client
        self.service_bus_client: Optional[AzureServiceBusClient] = None
        if AZURE_BUS_AVAILABLE:
            try:
                key_vault_client = get_key_vault_client()

                # Try to get namespace from Key Vault, fall back to config
                namespace = None
                if self.config["azure_service_bus"].get("namespace_secret"):
                    try:
                        namespace = key_vault_client.get_secret(
                            self.config["azure_service_bus"].get("namespace_secret", "service-bus-namespace")
                        )
                    except Exception as e:
                        self.logger.warning(f"⚠️  Failed to get namespace from Key Vault: {e}")

                # Fall back to config if Key Vault failed
                if not namespace:
                    namespace = self.config["azure_service_bus"].get("namespace", "jarvis-lumina-bus.servicebus.windows.net")

                self.service_bus_client = get_service_bus_client(
                    namespace=namespace,
                    key_vault_client=key_vault_client
                )
                self.logger.info("✅ Azure Service Bus client initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  Azure Service Bus initialization failed: {e}")

        # Load assets
        self.assets: Dict[str, HomelabAsset] = {}
        self._load_assets()

        # Load teams
        self.teams: Dict[str, EngineeringTeam] = {}
        self._load_teams()

        # Message handlers
        self.message_handlers: Dict[str, List[Callable]] = {}

        # Async message processing
        self.processing_active = False
        self.processing_thread: Optional[threading.Thread] = None

        self.logger.info("✅ Homelab Azure Service Bus Interoperability initialized")
        self.logger.info(f"   Assets: {len(self.assets)}")
        self.logger.info(f"   Teams: {len(self.teams)}")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            else:
                self.logger.warning(f"⚠️  Config file not found: {self.config_file}")
                return {}
        except Exception as e:
            self.logger.error(f"❌ Failed to load config: {e}")
            return {}

    def _load_assets(self):
        """Load homelab assets from configuration"""
        assets_config = self.config.get("homelab_assets", {})

        for asset_id, asset_data in assets_config.items():
            try:
                asset = HomelabAsset(
                    asset_id=asset_id,
                    name=asset_data.get("name", asset_id),
                    asset_type=AssetType(asset_data.get("type", "system")),
                    ip_address=asset_data.get("ip_address"),
                    hostname=asset_data.get("hostname"),
                    topics=asset_data.get("azure_bus_integration", {}).get("topics", []),
                    queues=asset_data.get("azure_bus_integration", {}).get("queues", []),
                    subscriptions=asset_data.get("azure_bus_integration", {}).get("subscriptions", []),
                    infrastructure_topics=asset_data.get("infrastructure_layer", {}).get("topics", []),
                    inference_topics=asset_data.get("inference_layer", {}).get("topics", []),
                    metadata=asset_data
                )
                self.assets[asset_id] = asset
                self.logger.info(f"   ✅ Loaded asset: {asset.name} ({asset.asset_type.value})")
            except Exception as e:
                self.logger.warning(f"   ⚠️  Failed to load asset {asset_id}: {e}")

    def _load_teams(self):
        """Load engineering teams from configuration"""
        teams_config = self.config.get("engineering_teams", {})

        for team_id, team_data in teams_config.items():
            try:
                # Map team_id to TeamType enum value
                team_type_map = {
                    "interconnectivity_team": TeamType.INTERCONNECTIVITY_TEAM,
                    "security_team": TeamType.SECURITY_TEAM,
                    "network_team": TeamType.NETWORK_TEAM,
                    "system_engineering_team": TeamType.SYSTEM_ENGINEERING_TEAM
                }
                team_type = team_type_map.get(team_id, TeamType.INTERCONNECTIVITY_TEAM)

                team = EngineeringTeam(
                    team_id=team_id,
                    name=team_data.get("name", team_id),
                    team_type=team_type,
                    topics=team_data.get("azure_bus_topics", []),
                    queues=team_data.get("azure_bus_queues", []),
                    assets=team_data.get("assets", []),
                    metadata=team_data
                )
                self.teams[team_id] = team
                self.logger.info(f"   ✅ Loaded team: {team.name}")
            except Exception as e:
                self.logger.warning(f"   ⚠️  Failed to load team {team_id}: {e}")

    def publish_asset_message(
        self,
        asset_id: str,
        topic: str,
        message_type: MessageType,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> bool:
        """
        Publish message from asset to Azure Service Bus

        Args:
            asset_id: Asset ID (falc, nas, pfsensefw, kaiju_no_8, homelab, company)
            topic: Topic name
            message_type: Message type
            payload: Message payload
            correlation_id: Optional correlation ID
        """
        if not self.service_bus_client:
            self.logger.error("❌ Azure Service Bus client not available")
            return False

        if asset_id not in self.assets:
            self.logger.error(f"❌ Asset not found: {asset_id}")
            return False

        asset = self.assets[asset_id]

        try:
            message = ServiceBusMessage(
                message_id=f"{asset_id}_{datetime.now().isoformat()}",
                message_type=message_type,
                timestamp=datetime.now(),
                source=asset.name,
                destination=topic,
                payload=payload,
                correlation_id=correlation_id,
                metadata={
                    "asset_id": asset_id,
                    "asset_type": asset.asset_type.value,
                    "ip_address": asset.ip_address
                }
            )

            success = self.service_bus_client.publish_to_topic(topic, message)
            if success:
                self.logger.info(f"✅ Published message from {asset.name} to {topic}")
            return success

        except Exception as e:
            self.logger.error(f"❌ Failed to publish message: {e}")
            return False

    def publish_team_message(
        self,
        team_id: str,
        topic: str,
        message_type: MessageType,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> bool:
        """
        Publish message from engineering team to Azure Service Bus

        Args:
            team_id: Team ID (interconnectivity, security, network, system_engineering)
            topic: Topic name
            message_type: Message type
            payload: Message payload
            correlation_id: Optional correlation ID
        """
        if not self.service_bus_client:
            self.logger.error("❌ Azure Service Bus client not available")
            return False

        if team_id not in self.teams:
            self.logger.error(f"❌ Team not found: {team_id}")
            return False

        team = self.teams[team_id]

        try:
            message = ServiceBusMessage(
                message_id=f"{team_id}_{datetime.now().isoformat()}",
                message_type=message_type,
                timestamp=datetime.now(),
                source=team.name,
                destination=topic,
                payload=payload,
                correlation_id=correlation_id,
                metadata={
                    "team_id": team_id,
                    "team_type": team.team_type.value
                }
            )

            success = self.service_bus_client.publish_to_topic(topic, message)
            if success:
                self.logger.info(f"✅ Published message from {team.name} to {topic}")
            return success

        except Exception as e:
            self.logger.error(f"❌ Failed to publish message: {e}")
            return False

    def subscribe_asset_topic(
        self,
        asset_id: str,
        topic: str,
        subscription: str,
        handler: Callable[[Dict[str, Any]], None]
    ):
        """
        Subscribe asset to Azure Service Bus topic

        Args:
            asset_id: Asset ID
            topic: Topic name
            subscription: Subscription name
            handler: Message handler function
        """
        if not self.service_bus_client:
            self.logger.error("❌ Azure Service Bus client not available")
            return

        if asset_id not in self.assets:
            self.logger.error(f"❌ Asset not found: {asset_id}")
            return

        asset = self.assets[asset_id]

        # Register handler
        handler_key = f"{asset_id}:{topic}:{subscription}"
        if handler_key not in self.message_handlers:
            self.message_handlers[handler_key] = []
        self.message_handlers[handler_key].append(handler)

        self.logger.info(f"✅ Subscribed {asset.name} to {topic} (subscription: {subscription})")

    def subscribe_team_topic(
        self,
        team_id: str,
        topic: str,
        subscription: str,
        handler: Callable[[Dict[str, Any]], None]
    ):
        """
        Subscribe team to Azure Service Bus topic

        Args:
            team_id: Team ID
            topic: Topic name
            subscription: Subscription name
            handler: Message handler function
        """
        if not self.service_bus_client:
            self.logger.error("❌ Azure Service Bus client not available")
            return

        if team_id not in self.teams:
            self.logger.error(f"❌ Team not found: {team_id}")
            return

        team = self.teams[team_id]

        # Register handler
        handler_key = f"{team_id}:{topic}:{subscription}"
        if handler_key not in self.message_handlers:
            self.message_handlers[handler_key] = []
        self.message_handlers[handler_key].append(handler)

        self.logger.info(f"✅ Subscribed {team.name} to {topic} (subscription: {subscription})")

    def start_async_processing(self):
        """Start async message processing"""
        if self.processing_active:
            return

        self.processing_active = True
        self.processing_thread = threading.Thread(target=self._async_processing_loop, daemon=True)
        self.processing_thread.start()
        self.logger.info("✅ Async message processing started")

    def stop_async_processing(self):
        """Stop async message processing"""
        self.processing_active = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5.0)
        self.logger.info("✅ Async message processing stopped")

    def _async_processing_loop(self):
        """Async message processing loop"""
        while self.processing_active:
            try:
                # Process messages from all subscriptions
                for handler_key, handlers in self.message_handlers.items():
                    asset_id, topic, subscription = handler_key.split(":", 2)

                    if self.service_bus_client:
                        def message_handler(message_body: Dict[str, Any]):
                            for handler in handlers:
                                try:
                                    handler(message_body)
                                except Exception as e:
                                    logger.error(f"❌ Handler error: {e}")

                        self.service_bus_client.subscribe_to_topic(
                            topic_name=topic,
                            subscription_name=subscription,
                            handler=message_handler
                        )

                # Sleep before next iteration
                import time
                time.sleep(10)

            except Exception as e:
                self.logger.error(f"❌ Async processing error: {e}")
                import time
                time.sleep(30)

    def get_asset_status(self, asset_id: str) -> Dict[str, Any]:
        """Get asset status and connectivity"""
        if asset_id not in self.assets:
            return {"error": f"Asset not found: {asset_id}"}

        asset = self.assets[asset_id]

        return {
            "asset_id": asset_id,
            "name": asset.name,
            "type": asset.asset_type.value,
            "ip_address": asset.ip_address,
            "hostname": asset.hostname,
            "topics": asset.topics,
            "queues": asset.queues,
            "subscriptions": asset.subscriptions,
            "infrastructure_topics": asset.infrastructure_topics,
            "inference_topics": asset.inference_topics,
            "azure_bus_connected": self.service_bus_client is not None
        }

    def get_team_status(self, team_id: str) -> Dict[str, Any]:
        """Get team status"""
        if team_id not in self.teams:
            return {"error": f"Team not found: {team_id}"}

        team = self.teams[team_id]

        return {
            "team_id": team_id,
            "name": team.name,
            "type": team.team_type.value,
            "topics": team.topics,
            "queues": team.queues,
            "assets": team.assets,
            "azure_bus_connected": self.service_bus_client is not None
        }

    def get_interoperability_summary(self) -> Dict[str, Any]:
        """Get interoperability summary"""
        return {
            "assets": {
                asset_id: {
                    "name": asset.name,
                    "type": asset.asset_type.value,
                    "topics_count": len(asset.topics),
                    "queues_count": len(asset.queues)
                }
                for asset_id, asset in self.assets.items()
            },
            "teams": {
                team_id: {
                    "name": team.name,
                    "type": team.team_type.value,
                    "topics_count": len(team.topics),
                    "assets_count": len(team.assets)
                }
                for team_id, team in self.teams.items()
            },
            "azure_bus_connected": self.service_bus_client is not None,
            "async_processing_active": self.processing_active
        }


# Global instance
_global_interop: Optional[HomelabAzureBusInteroperability] = None


def get_homelab_interoperability(project_root: Optional[Path] = None) -> HomelabAzureBusInteroperability:
    try:
        """Get or create global homelab interoperability instance"""
        global _global_interop

        if _global_interop is None:
            if project_root is None:
                project_root = Path(__file__).parent.parent.parent
            _global_interop = HomelabAzureBusInteroperability(project_root)

        return _global_interop


    except Exception as e:
        logger.error(f"Error in get_homelab_interoperability: {e}", exc_info=True)
        raise
def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Homelab Azure Service Bus Interoperability")
    parser.add_argument("--status", action="store_true", help="Show interoperability status")
    parser.add_argument("--asset", type=str, help="Get asset status (asset_id)")
    parser.add_argument("--team", type=str, help="Get team status (team_id)")
    parser.add_argument("--summary", action="store_true", help="Show interoperability summary")
    parser.add_argument("--publish", type=str, help="Publish message (asset_id:topic:message_type)")
    parser.add_argument("--start", action="store_true", help="Start async processing")
    parser.add_argument("--stop", action="store_true", help="Stop async processing")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    interop = HomelabAzureBusInteroperability(project_root)

    if args.status:
        summary = interop.get_interoperability_summary()
        print("\n" + "="*80)
        print("HOMELAB AZURE SERVICE BUS INTEROPERABILITY STATUS")
        print("="*80)
        print(f"Azure Bus Connected: {summary['azure_bus_connected']}")
        print(f"Async Processing: {summary['async_processing_active']}")
        print(f"\nAssets: {len(summary['assets'])}")
        for asset_id, asset_info in summary['assets'].items():
            print(f"  - {asset_info['name']}: {asset_info['topics_count']} topics, {asset_info['queues_count']} queues")
        print(f"\nTeams: {len(summary['teams'])}")
        for team_id, team_info in summary['teams'].items():
            print(f"  - {team_info['name']}: {team_info['topics_count']} topics, {team_info['assets_count']} assets")
        print("="*80)

    if args.asset:
        status = interop.get_asset_status(args.asset)
        print("\n" + "="*80)
        print(f"ASSET STATUS: {args.asset}")
        print("="*80)
        print(json.dumps(status, indent=2))
        print("="*80)

    if args.team:
        status = interop.get_team_status(args.team)
        print("\n" + "="*80)
        print(f"TEAM STATUS: {args.team}")
        print("="*80)
        print(json.dumps(status, indent=2))
        print("="*80)

    if args.summary:
        summary = interop.get_interoperability_summary()
        print(json.dumps(summary, indent=2))

    if args.start:
        interop.start_async_processing()
        print("✅ Async processing started")

    if args.stop:
        interop.stop_async_processing()
        print("✅ Async processing stopped")

    if args.publish:
        parts = args.publish.split(":", 2)
        if len(parts) == 3:
            asset_id, topic, message_type_str = parts
            try:
                message_type = MessageType(message_type_str)
                success = interop.publish_asset_message(
                    asset_id=asset_id,
                    topic=topic,
                    message_type=message_type,
                    payload={"test": True}
                )
                print(f"{'✅ Published' if success else '❌ Failed'}: {asset_id} → {topic}")
            except ValueError:
                print(f"❌ Invalid message type: {message_type_str}")
        else:
            print("❌ Format: --publish asset_id:topic:message_type")

    if not any([args.status, args.asset, args.team, args.summary, args.publish, args.start, args.stop]):
        parser.print_help()


if __name__ == "__main__":


    main()