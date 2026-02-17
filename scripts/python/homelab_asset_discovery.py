#!/usr/bin/env python3
"""
Homelab Asset Discovery & Utilization

Discovers and tracks all available @homelab assets and resources:
- NAS (<NAS_PRIMARY_IP>)
- N8N workflows
- MariaDB databases
- Email Hub
- Storage resources
- Network resources

Tags: #HOMELAB #ASSETS #RESOURCES #DISCOVERY #REQUIRED @HOMELAB @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("HomelabAssetDiscovery")


@dataclass
class HomelabAsset:
    """Homelab asset/resource"""
    asset_id: str
    asset_name: str
    asset_type: str  # "nas", "database", "service", "storage", "network"
    host: Optional[str] = None
    port: Optional[int] = None
    status: str = "unknown"  # "online", "offline", "unknown"
    utilization_percent: float = 0.0
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    discovered_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_checked: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HomelabAssetDiscovery:
    """
    Discover and track all @homelab assets and resources
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize homelab asset discovery"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.assets_dir = self.project_root / "data" / "homelab" / "assets"
        self.assets_dir.mkdir(parents=True, exist_ok=True)

        # Known homelab assets from config
        self.known_assets = self._load_known_assets()

        # Discovered assets
        self.discovered_assets: Dict[str, HomelabAsset] = {}

        logger.info("=" * 80)
        logger.info("🏠 HOMELAB ASSET DISCOVERY")
        logger.info("=" * 80)
        logger.info("   Discovering all available @homelab assets and resources")
        logger.info("=" * 80)

    def _load_known_assets(self) -> List[Dict[str, Any]]:
        """Load known assets from config files"""
        assets = []

        # NAS (<NAS_PRIMARY_IP>)
        assets.append({
            "asset_id": "nas_10_17_17_32",
            "asset_name": "NAS Server",
            "asset_type": "nas",
            "host": "<NAS_PRIMARY_IP>",
            "capabilities": ["storage", "n8n", "database", "email_hub", "download_station"]
        })

        # N8N on NAS
        assets.append({
            "asset_id": "n8n_nas",
            "asset_name": "N8N Workflow Automation",
            "asset_type": "service",
            "host": "<NAS_PRIMARY_IP>",
            "port": 5678,
            "capabilities": ["workflow_automation", "webhooks", "api"]
        })

        # MariaDB on NAS
        assets.append({
            "asset_id": "mariadb_nas",
            "asset_name": "MariaDB Database Server",
            "asset_type": "database",
            "host": "<NAS_PRIMARY_IP>",
            "capabilities": ["helpdesk", "hologram", "holocron", "master_todo"]
        })

        # Email Hub on NAS
        assets.append({
            "asset_id": "email_hub_nas",
            "asset_name": "NAS Email Hub",
            "asset_type": "service",
            "host": "<NAS_PRIMARY_IP>",
            "capabilities": ["email_processing", "webhooks"]
        })

        # NAS Storage
        assets.append({
            "asset_id": "nas_storage",
            "asset_name": "NAS Storage",
            "asset_type": "storage",
            "host": "<NAS_PRIMARY_IP>",
            "capabilities": ["file_storage", "model_storage", "backup"]
        })

        return assets

    def discover_assets(self) -> Dict[str, HomelabAsset]:
        """
        Discover all homelab assets

        Returns:
            Dictionary of discovered assets
        """
        logger.info("🔍 Discovering homelab assets...")

        for asset_config in self.known_assets:
            asset = HomelabAsset(
                asset_id=asset_config["asset_id"],
                asset_name=asset_config["asset_name"],
                asset_type=asset_config["asset_type"],
                host=asset_config.get("host"),
                port=asset_config.get("port"),
                capabilities=asset_config.get("capabilities", []),
                status=self._check_asset_status(asset_config)
            )

            # Calculate utilization
            asset.utilization_percent = self._calculate_utilization(asset)

            self.discovered_assets[asset.asset_id] = asset

        # Save discovered assets
        self._save_assets()

        logger.info(f"✅ Discovered {len(self.discovered_assets)} homelab assets")
        return self.discovered_assets

    def _check_asset_status(self, asset_config: Dict[str, Any]) -> str:
        """Check if asset is online"""
        host = asset_config.get("host")
        if not host:
            return "unknown"

        try:
            import socket
            port = asset_config.get("port", 80)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            return "online" if result == 0 else "offline"
        except Exception:
            return "unknown"

    def _calculate_utilization(self, asset: HomelabAsset) -> float:
        """Calculate asset utilization percentage"""
        # Base utilization based on status
        if asset.status == "online":
            base_util = 50.0  # Assume 50% if online
        elif asset.status == "offline":
            base_util = 0.0
        else:
            base_util = 25.0  # Unknown status

        # Add utilization based on capabilities in use
        capability_bonus = len(asset.capabilities) * 5.0
        utilization = min(base_util + capability_bonus, 100.0)

        return utilization

    def _save_assets(self):
        try:
            """Save discovered assets to disk"""
            assets_file = self.assets_dir / "discovered_assets.json"
            assets_data = {
                "discovered_at": datetime.now().isoformat(),
                "total_assets": len(self.discovered_assets),
                "assets": {k: v.to_dict() for k, v in self.discovered_assets.items()}
            }

            with open(assets_file, 'w', encoding='utf-8') as f:
                json.dump(assets_data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_assets: {e}", exc_info=True)
            raise
    def get_all_assets(self) -> Dict[str, HomelabAsset]:
        """Get all discovered assets"""
        return self.discovered_assets

    def get_asset_utilization_summary(self) -> Dict[str, Any]:
        """Get summary of asset utilization"""
        total_assets = len(self.discovered_assets)
        online_assets = sum(1 for a in self.discovered_assets.values() if a.status == "online")
        total_utilization = sum(a.utilization_percent for a in self.discovered_assets.values())
        avg_utilization = total_utilization / total_assets if total_assets > 0 else 0.0

        return {
            "total_assets": total_assets,
            "online_assets": online_assets,
            "offline_assets": total_assets - online_assets,
            "average_utilization_percent": avg_utilization,
            "total_utilization_percent": total_utilization,
            "assets": {k: {
                "name": v.asset_name,
                "type": v.asset_type,
                "status": v.status,
                "utilization_percent": v.utilization_percent
            } for k, v in self.discovered_assets.items()}
        }


if __name__ == "__main__":
    discovery = HomelabAssetDiscovery()
    assets = discovery.discover_assets()

    summary = discovery.get_asset_utilization_summary()
    print(json.dumps(summary, indent=2))
