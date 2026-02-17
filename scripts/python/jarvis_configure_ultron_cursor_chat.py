#!/usr/bin/env python3
"""
JARVIS Configure ULTRON for Cursor Chat

Configures ULTRON as a selectable model in Cursor IDE AI Chat dropdown.

Tags: #ULTRON #CURSOR-IDE #CONFIGURATION @CURSOR-ENGINEER
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISULTRONConfig")


class JARVISConfigureULTRONCursorChat:
    """
    Configure ULTRON for Cursor IDE AI Chat
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.settings_file = project_root / ".cursor" / "settings.json"

        self.logger.info("✅ ULTRON Cursor Chat Configurator initialized")

    def get_ultron_config(self) -> Dict[str, Any]:
        """Get ULTRON configuration from cluster"""
        try:
            from jarvis_ultron_hybrid_cluster import ULTRONHybridCluster
            cluster = ULTRONHybridCluster(self.project_root)
            return cluster.register_as_cursor_model()
        except Exception as e:
            self.logger.warning(f"⚠️  Could not get ULTRON config from cluster: {e}")
            # Return default config
            return {
                "name": "ULTRON",
                "title": "ULTRON Virtual Hybrid Cluster",
                "provider": "ollama",
                "model": "qwen2.5:72b",
                "apiBase": "http://localhost:11434",
                "contextLength": 32768,
                "description": "ULTRON Virtual Hybrid Cluster - Laptop ULTRON + KAIJU (Auto-failover, Load-balanced)",
                "priority": 1,
                "cluster": {
                    "type": "virtual_hybrid",
                    "nodes": [
                        {
                            "name": "ULTRON Local",
                            "endpoint": "http://localhost:11434",
                            "priority": 1
                        },
                        {
                            "name": "KAIJU",
                            "endpoint": "http://<NAS_PRIMARY_IP>:11434",
                            "priority": 2
                        }
                    ],
                    "routing": "load_balanced"
                }
            }

    def configure_chat_models(self) -> Dict[str, Any]:
        """Configure ULTRON for Cursor Chat"""
        self.logger.info("⚙️  Configuring ULTRON for Cursor Chat...")

        if not self.settings_file.exists():
            return {"success": False, "error": "settings.json not found"}

        try:
            # Read current settings
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)

            # Get ULTRON config
            ultron_config = self.get_ultron_config()

            # Ensure cursor.chat.customModels exists
            if "cursor.chat.customModels" not in settings:
                settings["cursor.chat.customModels"] = []

            # Check if ULTRON already exists
            chat_models = settings["cursor.chat.customModels"]
            ultron_exists = any(m.get("name") == "ULTRON" for m in chat_models)

            if ultron_exists:
                # Update existing ULTRON
                for i, model in enumerate(chat_models):
                    if model.get("name") == "ULTRON":
                        chat_models[i] = ultron_config
                        break
                self.logger.info("🔄 Updated existing ULTRON in chat models")
            else:
                # Add ULTRON at the beginning (priority)
                chat_models.insert(0, ultron_config)
                self.logger.info("✅ Added ULTRON to chat models")

            # Set ULTRON as default
            settings["cursor.chat.defaultModel"] = "ULTRON"

            # Write back
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

            self.logger.info("✅ ULTRON configured for Cursor Chat")
            return {
                "success": True,
                "action": "updated" if ultron_exists else "added",
                "default_model": "ULTRON"
            }

        except Exception as e:
            self.logger.error(f"❌ Failed to configure ULTRON: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def configure_agent_models(self) -> Dict[str, Any]:
        """Configure ULTRON for Cursor Agent"""
        self.logger.info("⚙️  Configuring ULTRON for Cursor Agent...")

        if not self.settings_file.exists():
            return {"success": False, "error": "settings.json not found"}

        try:
            # Read current settings
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)

            # Get ULTRON config
            ultron_config = self.get_ultron_config()

            # Ensure cursor.agent.customModels exists
            if "cursor.agent.customModels" not in settings:
                settings["cursor.agent.customModels"] = []

            # Check if ULTRON already exists
            agent_models = settings["cursor.agent.customModels"]
            ultron_exists = any(m.get("name") == "ULTRON" for m in agent_models)

            if ultron_exists:
                # Update existing ULTRON
                for i, model in enumerate(agent_models):
                    if model.get("name") == "ULTRON":
                        agent_models[i] = ultron_config
                        break
                self.logger.info("🔄 Updated existing ULTRON in agent models")
            else:
                # Add ULTRON at the beginning (priority)
                agent_models.insert(0, ultron_config)
                self.logger.info("✅ Added ULTRON to agent models")

            # Set ULTRON as default
            settings["cursor.agent.defaultModel"] = "ULTRON"

            # Write back
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

            self.logger.info("✅ ULTRON configured for Cursor Agent")
            return {
                "success": True,
                "action": "updated" if ultron_exists else "added",
                "default_model": "ULTRON"
            }

        except Exception as e:
            self.logger.error(f"❌ Failed to configure ULTRON: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def configure_all(self) -> Dict[str, Any]:
        """Configure ULTRON for all Cursor features"""
        self.logger.info("🚀 Configuring ULTRON for all Cursor features...")

        results = {
            "timestamp": datetime.now().isoformat(),
            "chat": self.configure_chat_models(),
            "agent": self.configure_agent_models()
        }

        results["summary"] = {
            "chat_configured": results["chat"]["success"],
            "agent_configured": results["agent"]["success"],
            "all_configured": results["chat"]["success"] and results["agent"]["success"]
        }

        return results


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Configure ULTRON for Cursor Chat")
        parser.add_argument("--chat", action="store_true", help="Configure for Chat")
        parser.add_argument("--agent", action="store_true", help="Configure for Agent")
        parser.add_argument("--all", action="store_true", help="Configure for all")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        configurator = JARVISConfigureULTRONCursorChat(project_root)

        if args.chat:
            result = configurator.configure_chat_models()
            print(json.dumps(result, indent=2, default=str))

        elif args.agent:
            result = configurator.configure_agent_models()
            print(json.dumps(result, indent=2, default=str))

        elif args.all:
            result = configurator.configure_all()
            print(json.dumps(result, indent=2, default=str))

        else:
            # Default: configure all
            result = configurator.configure_all()
            print(json.dumps(result, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()