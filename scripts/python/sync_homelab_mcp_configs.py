#!/usr/bin/env python3
"""
Sync Homelab MCP Configurations
#JARVIS #HOMELAB #MCP #SYNC

Synchronizes MCP configurations between NAS DSM Container Manager and localhost Docker MCP toolkits.
Ensures all homelab devices use both NAS and localhost services in a hybrid configuration.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HomelabMCPSync:
    """Sync MCP configurations across homelab devices"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.config_dir = self.project_root / "config"
        self.cursor_dir = self.project_root / ".cursor"

        # Load hybrid configuration
        self.hybrid_config_path = self.config_dir / "homelab_mcp_hybrid_config.json"
        self.mcp_config_path = self.cursor_dir / "mcp_config.json"
        self.mcp_hybrid_path = self.cursor_dir / "mcp_config_hybrid.json"

        self.hybrid_config = self._load_config(self.hybrid_config_path)
        self.mcp_config = self._load_config(self.mcp_config_path)

    def _load_config(self, path: Path) -> Dict[str, Any]:
        """Load JSON configuration file"""
        try:
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Failed to load {path}: {e}")
            return {}

    def _save_config(self, path: Path, config: Dict[str, Any]) -> bool:
        """Save JSON configuration file"""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Saved: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save {path}: {e}")
            return False

    def merge_hybrid_config(self) -> Dict[str, Any]:
        """Merge NAS and localhost MCP configurations into hybrid config"""
        logger.info("🔄 Merging hybrid MCP configuration...")

        merged = {
            "mcpServers": {},
            "routing": {
                "strategy": "hybrid_failover",
                "primary": "nas",  # Option B: NAS primary for all devices
                "fallback": "localhost",  # Localhost fallback for all devices
                "health_check_interval": 30
            },
            "devices": {
                "nas": {
                    "ip": "<NAS_PRIMARY_IP>",
                    "type": "dsm_container_manager"
                },
                "localhost": {
                    "ip": "127.0.0.1",
                    "type": "docker_compose"
                }
            }
        }

        # Get NAS servers from hybrid config
        nas_servers = self.hybrid_config.get("mcp_servers", {}).get("nas_servers", {})
        localhost_servers = self.hybrid_config.get("mcp_servers", {}).get("localhost_servers", {})

        # Merge NAS servers with localhost fallbacks
        for server_name, nas_config in nas_servers.items():
            merged["mcpServers"][server_name] = {
                "command": nas_config.get("command", "ssh"),
                "args": nas_config.get("args", []),
                "env": nas_config.get("env", {})
            }

            # Add fallback if available
            fallback_name = nas_config.get("fallback")
            if fallback_name and fallback_name in localhost_servers:
                localhost_config = localhost_servers[fallback_name]
                merged["mcpServers"][server_name]["fallback"] = {
                    "command": localhost_config.get("command", "docker"),
                    "args": localhost_config.get("args", []),
                    "env": localhost_config.get("env", {})
                }

        # Add localhost-only servers
        for server_name, localhost_config in localhost_servers.items():
            if server_name not in merged["mcpServers"]:
                merged["mcpServers"][server_name] = {
                    "command": localhost_config.get("command", "docker"),
                    "args": localhost_config.get("args", []),
                    "env": localhost_config.get("env", {})
                }

                # Add NAS fallback if available
                fallback_name = localhost_config.get("fallback")
                if fallback_name:
                    # Try to find corresponding NAS server
                    for nas_name, nas_config in nas_servers.items():
                        if fallback_name.replace("nas_", "") in nas_name.lower():
                            merged["mcpServers"][server_name]["fallback"] = {
                                "command": nas_config.get("command", "ssh"),
                                "args": nas_config.get("args", []),
                                "env": nas_config.get("env", {})
                            }
                            break

        return merged

    def update_mcp_config(self) -> bool:
        """Update .cursor/mcp_config.json with hybrid configuration"""
        logger.info("📝 Updating MCP configuration...")

        merged_config = self.merge_hybrid_config()

        # Update existing mcp_config.json
        if self.mcp_config:
            # Preserve existing structure, add hybrid routing
            self.mcp_config.update({
                "routing": merged_config["routing"],
                "devices": merged_config["devices"]
            })

            # Add fallbacks to existing servers
            for server_name, server_config in self.mcp_config.get("mcpServers", {}).items():
                if server_name in merged_config["mcpServers"]:
                    merged_server = merged_config["mcpServers"][server_name]
                    if "fallback" in merged_server:
                        server_config["fallback"] = merged_server["fallback"]
        else:
            self.mcp_config = merged_config

        # Save updated config
        return self._save_config(self.mcp_config_path, self.mcp_config)

    def create_device_configs(self) -> Dict[str, bool]:
        """Create device-specific MCP configurations"""
        logger.info("📱 Creating device-specific configurations...")

        results = {}
        devices = self.hybrid_config.get("devices", {})

        for device_name, device_config in devices.items():
            device_type = device_config.get("type", "unknown")
            device_ip = device_config.get("ip", "unknown")

            logger.info(f"  Creating config for {device_name} ({device_type})...")

            # Create device-specific config
            device_config_path = self.config_dir / f"mcp_config_{device_name}.json"
            device_mcp_config = {
                "device": device_name,
                "type": device_type,
                "ip": device_ip,
                "mcpServers": {},
                "routing": {
                    "strategy": "hybrid_failover",
                    "primary": "nas",  # Option B: NAS primary for all devices
                    "fallback": "localhost"  # Localhost fallback for all devices
                }
            }

            # Add servers based on device type
            if device_type == "nas":
                # NAS uses DSM Container Manager servers
                nas_servers = self.hybrid_config.get("mcp_servers", {}).get("nas_servers", {})
                for server_name, server_config in nas_servers.items():
                    device_mcp_config["mcpServers"][server_name] = {
                        "command": "docker",
                        "args": [
                            "exec",
                            "-i",
                            server_config.get("name", server_name.lower().replace("_", "-")),
                            "python3",
                            "-m",
                            server_name.lower().replace("_", "")
                        ],
                        "env": server_config.get("env", {})
                    }
            elif device_type == "local":
                # Localhost uses Docker Compose servers
                localhost_servers = self.hybrid_config.get("mcp_servers", {}).get("localhost_servers", {})
                for server_name, server_config in localhost_servers.items():
                    device_mcp_config["mcpServers"][server_name] = {
                        "command": server_config.get("command", "docker"),
                        "args": server_config.get("args", []),
                        "env": server_config.get("env", {})
                    }

            results[device_name] = self._save_config(device_config_path, device_mcp_config)

        return results

    def sync_all(self) -> bool:
        """Sync all configurations"""
        logger.info("🚀 Starting homelab MCP configuration sync...")
        logger.info("=" * 70)

        # Update main MCP config
        if not self.update_mcp_config():
            logger.error("Failed to update MCP config")
            return False

        # Create device-specific configs
        device_results = self.create_device_configs()

        # Summary
        logger.info("\n" + "=" * 70)
        logger.info("📊 Sync Summary:")
        logger.info(f"  ✅ Main MCP config updated: {self.mcp_config_path}")

        for device, success in device_results.items():
            status = "✅" if success else "❌"
            logger.info(f"  {status} {device} config: {'Success' if success else 'Failed'}")

        all_success = all(device_results.values())

        if all_success:
            logger.info("\n✅ All configurations synced successfully!")
        else:
            logger.warning("\n⚠️  Some configurations failed. Check logs for details.")

        return all_success


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(
            description="Sync Homelab MCP Configurations"
        )
        parser.add_argument(
            "action",
            choices=["sync", "merge", "devices"],
            help="Action to perform"
        )

        args = parser.parse_args()

        sync = HomelabMCPSync()

        if args.action == "sync":
            success = sync.sync_all()
            sys.exit(0 if success else 1)
        elif args.action == "merge":
            merged = sync.merge_hybrid_config()
            print(json.dumps(merged, indent=2))
        elif args.action == "devices":
            results = sync.create_device_configs()
            for device, success in results.items():
                print(f"{'✅' if success else '❌'} {device}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()