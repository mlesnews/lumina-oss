#!/usr/bin/env python3
"""
Cursor Active Model Tracker

Tracks and displays the currently active model in Cursor IDE.
Monitors model selection and writes status to a file for UI display.

@CURSOR @MODEL @TRACKING #TRANSPARENCY
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import sys

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CursorActiveModelTracker")


class CursorActiveModelTracker:
    """Track and display the currently active model in Cursor IDE."""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize the tracker."""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.cursor_settings_file = self.project_root / ".cursor" / "settings.json"
        self.status_file = self.project_root / "data" / "cursor_active_model_status.json"
        self.status_file.parent.mkdir(parents=True, exist_ok=True)

        # Ensure status file exists
        if not self.status_file.exists():
            self._write_status({
                "active_model": "Unknown",
                "model_type": "unknown",
                "last_updated": datetime.now().isoformat(),
                "status": "monitoring"
            })

    def _read_cursor_settings(self) -> Dict[str, Any]:
        """Read Cursor settings.json file."""
        try:
            if not self.cursor_settings_file.exists():
                logger.warning(f"Cursor settings file not found: {self.cursor_settings_file}")
                return {}

            with open(self.cursor_settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading Cursor settings: {e}")
            return {}

    def _write_status(self, status: Dict[str, Any]):
        """Write status to file."""
        try:
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(status, f, indent=2)
        except Exception as e:
            logger.error(f"Error writing status file: {e}")

    def get_active_model(self) -> Dict[str, Any]:
        """
        Determine the currently active model from Cursor settings.

        Returns:
            Dict with active_model, model_type, provider, endpoint, etc.
        """
        settings = self._read_cursor_settings()

        # Check agent model (highest priority)
        agent_default = settings.get("cursor.agent.defaultModel", None)
        agent_models = settings.get("cursor.agent.customModels", [])

        # Check chat model
        chat_default = settings.get("cursor.chat.defaultModel", None)
        chat_models = settings.get("cursor.chat.customModels", [])

        # Check composer model
        composer_default = settings.get("cursor.composer.defaultModel", None)
        composer_models = settings.get("cursor.composer.customModels", [])

        # Determine active model (agent takes priority)
        active_model_name = None
        active_model_config = None
        model_type = "unknown"
        provider = "unknown"
        endpoint = None
        is_local = False

        # Check if explicitly set to "auto" or empty (which means auto)
        is_explicit_auto = (
            agent_default == "auto" or agent_default == "" or agent_default is None
        ) and (
            composer_default == "auto" or composer_default == "" or composer_default is None
        ) and (
            chat_default == "auto" or chat_default == "" or chat_default is None
        )

        # Priority: agent > composer > chat
        if agent_default and agent_default != "auto" and agent_default != "":
            # Find the model config
            for model in agent_models:
                if model.get("name") == agent_default or model.get("title") == agent_default:
                    active_model_config = model
                    active_model_name = model.get("title") or model.get("name") or agent_default
                    provider = model.get("provider", "unknown")
                    endpoint = model.get("apiBase")
                    is_local = model.get("localOnly", False)
                    break

            if not active_model_config:
                active_model_name = agent_default
                model_type = "agent_default"
        elif composer_default and composer_default != "auto" and composer_default != "":
            for model in composer_models:
                if model.get("name") == composer_default or model.get("title") == composer_default:
                    active_model_config = model
                    active_model_name = model.get("title") or model.get("name") or composer_default
                    provider = model.get("provider", "unknown")
                    endpoint = model.get("apiBase")
                    is_local = model.get("localOnly", False)
                    break

            if not active_model_config:
                active_model_name = composer_default
                model_type = "composer_default"
        elif chat_default and chat_default != "auto" and chat_default != "":
            for model in chat_models:
                if model.get("name") == chat_default or model.get("title") == chat_default:
                    active_model_config = model
                    active_model_name = model.get("title") or model.get("name") or chat_default
                    provider = model.get("provider", "unknown")
                    endpoint = model.get("apiBase")
                    is_local = model.get("localOnly", False)
                    break

            if not active_model_config:
                active_model_name = chat_default
                model_type = "chat_default"
        else:
            # Check if "auto" mode is set
            # Try to detect which model is actually being used
            # Check if there's a last-known model from status file
            last_model = None
            try:
                if self.status_file.exists():
                    with open(self.status_file, 'r') as f:
                        last_status = json.load(f)
                        last_model = last_status.get("actual_model") or last_status.get("active_model")
            except:
                pass

            # If we have a last-known model, use it
            if last_model and last_model != "Auto (Selecting...)" and not last_model.startswith("AUTO\\"):
                active_model_name = f"AUTO\\{last_model}"
            else:
                # Check available models - use first one as fallback
                all_models = agent_models + composer_models + chat_models
                if all_models:
                    first_model = all_models[0]
                    fallback_name = first_model.get("name") or first_model.get("title", "UNKNOWN")
                    active_model_name = f"AUTO\\{fallback_name}"
                else:
                    active_model_name = "AUTO\\SELECTING..."

        # Determine model type
        is_auto_mode = active_model_name.startswith("AUTO\\")

        if active_model_config:
            if active_model_config.get("cluster"):
                model_type = "virtual_cluster"
            elif is_local:
                model_type = "local"
            else:
                model_type = "cloud"
        elif is_auto_mode:
            model_type = "auto"
            # Extract actual model name for provider/endpoint lookup
            actual_model_name = active_model_name.replace("AUTO\\", "")
            # Try to find config for the actual model
            all_models = agent_models + composer_models + chat_models
            for model in all_models:
                if model.get("name") == actual_model_name or model.get("title") == actual_model_name:
                    provider = model.get("provider", "unknown")
                    endpoint = model.get("apiBase")
                    is_local = model.get("localOnly", False)
                    active_model_config = model
                    break
        else:
            model_type = "unknown"

        # Get model details
        model_details = {
            "name": active_model_name or "Unknown",
            "type": model_type,
            "provider": provider,
            "endpoint": endpoint,
            "is_local": is_local,
            "context_length": active_model_config.get("contextLength") if active_model_config else None,
            "description": active_model_config.get("description") if active_model_config else None,
            "is_auto_mode": is_auto_mode,
            "actual_model": active_model_name.replace("AUTO\\", "") if is_auto_mode else active_model_name
        }

        # Check for cluster configuration
        if active_model_config and active_model_config.get("cluster"):
            cluster = active_model_config.get("cluster", {})
            nodes = cluster.get("nodes", [])
            model_details["cluster_nodes"] = len(nodes)
            model_details["cluster_type"] = cluster.get("type", "unknown")
            model_details["cluster_routing"] = cluster.get("routing", "unknown")

        return model_details

    def update_status(self):
        """Update the active model status."""
        try:
            model_details = self.get_active_model()

            # Store both formatted name and actual model for next detection
            status = {
                "active_model": model_details["name"],  # Formatted: "AUTO\ULTRON" or "ULTRON"
                "actual_model": model_details.get("actual_model") or model_details["name"],  # Just model name
                "model_type": model_details["type"],
                "provider": model_details["provider"],
                "endpoint": model_details["endpoint"],
                "is_local": model_details["is_local"],
                "is_auto_mode": model_details.get("is_auto_mode", False),
                "context_length": model_details["context_length"],
                "description": model_details.get("description"),
                "cluster_nodes": model_details.get("cluster_nodes"),
                "cluster_type": model_details.get("cluster_type"),
                "cluster_routing": model_details.get("cluster_routing"),
                "last_updated": datetime.now().isoformat(),
                "status": "active"
            }

            self._write_status(status)

            # Format log message
            display_name = model_details["name"]
            if model_details.get("is_auto_mode"):
                display_name = f"AUTO\\{model_details.get('actual_model', 'SELECTING')}"

            logger.info(f"✅ Active model updated: {display_name} ({model_details['type']})")

            return status
        except Exception as e:
            logger.error(f"Error updating status: {e}")
            return None

    def get_status(self) -> Dict[str, Any]:
        """Get current status from file."""
        try:
            if not self.status_file.exists():
                return {
                    "active_model": "Unknown",
                    "model_type": "unknown",
                    "last_updated": None,
                    "status": "not_monitoring"
                }

            with open(self.status_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading status: {e}")
            return {
                "active_model": "Error",
                "model_type": "error",
                "last_updated": None,
                "status": "error"
            }

    def monitor(self, interval: float = 1.0):
        """Monitor and update status continuously."""
        logger.info("🔍 Starting active model monitoring...")
        logger.info(f"   Status file: {self.status_file}")
        logger.info(f"   Update interval: {interval}s")
        logger.info("")

        try:
            while True:
                self.update_status()
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("🛑 Monitoring stopped by user")
        except Exception as e:
            logger.error(f"❌ Monitoring error: {e}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Track Cursor IDE active model")
    parser.add_argument("--update", action="store_true", help="Update status once and exit")
    parser.add_argument("--monitor", action="store_true", help="Monitor continuously")
    parser.add_argument("--interval", type=float, default=1.0, help="Update interval in seconds (default: 1.0)")
    parser.add_argument("--status", action="store_true", help="Show current status")

    args = parser.parse_args()

    tracker = CursorActiveModelTracker()

    if args.status:
        status = tracker.get_status()
        print("\n" + "=" * 70)
        print("📊 CURSOR ACTIVE MODEL STATUS")
        print("=" * 70)
        active_model = status.get('active_model', 'Unknown')
        is_auto = status.get('is_auto_mode', False)

        # Format display
        if is_auto or active_model.startswith("AUTO\\"):
            display_model = active_model if active_model.startswith("AUTO\\") else f"AUTO\\{active_model}"
            print(f"   Active Model: {display_model}")
        else:
            print(f"   Active Model: {active_model}")

        print(f"   Model Type: {status.get('model_type', 'unknown')}")
        print(f"   Provider: {status.get('provider', 'unknown')}")
        print(f"   Local: {status.get('is_local', False)}")
        if status.get('endpoint'):
            print(f"   Endpoint: {status.get('endpoint')}")
        if status.get('cluster_nodes'):
            print(f"   Cluster Nodes: {status.get('cluster_nodes')}")
            print(f"   Cluster Type: {status.get('cluster_type')}")
        print(f"   Last Updated: {status.get('last_updated', 'Never')}")
        print("=" * 70 + "\n")
    elif args.update:
        tracker.update_status()
        print("✅ Status updated")
    elif args.monitor:
        tracker.monitor(interval=args.interval)
    else:
        # Default: update once
        tracker.update_status()
        status = tracker.get_status()
        active_model = status.get('active_model', 'Unknown')
        is_auto = status.get('is_auto_mode', False)

        # Format display
        if is_auto or active_model.startswith("AUTO\\"):
            display_model = active_model if active_model.startswith("AUTO\\") else f"AUTO\\{active_model}"
            print(f"✅ Active Model: {display_model}")
        else:
            print(f"✅ Active Model: {active_model}")


if __name__ == "__main__":


    main()