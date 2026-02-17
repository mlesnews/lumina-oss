#!/usr/bin/env python3
"""
JARVIS Activate ULTRON in Cursor IDE

Activates ULTRON in Cursor IDE by updating both workspace and USER settings.
This ensures ULTRON appears in the model dropdown.

Tags: #ULTRON #CURSOR-IDE #ACTIVATION @CURSOR-ENGINEER
"""

import sys
import json
import os
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

logger = get_logger("JARVISULTRONActivate")


class JARVISActivateULTRONCursor:
    """
    Activate ULTRON in Cursor IDE
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Workspace settings
        self.workspace_settings = project_root / ".cursor" / "settings.json"

        # User settings (Windows: %APPDATA%\Cursor\User\settings.json)
        appdata = os.getenv("APPDATA")
        if appdata:
            self.user_settings = Path(appdata) / "Cursor" / "User" / "settings.json"
        else:
            # Fallback for other OS
            home = Path.home()
            self.user_settings = home / ".config" / "Cursor" / "User" / "settings.json"

        self.logger.info(f"✅ ULTRON Cursor Activator initialized")
        self.logger.info(f"   Workspace settings: {self.workspace_settings}")
        self.logger.info(f"   User settings: {self.user_settings}")

    def get_ultron_config(self) -> Dict[str, Any]:
        """Get ULTRON model configuration"""
        return {
            "title": "ULTRON",
            "name": "ULTRON",
            "provider": "ollama",
            "model": "qwen2.5:72b",
            "apiBase": "http://localhost:11434",
            "contextLength": 32768,
            "description": "ULTRON Virtual Hybrid Cluster - Laptop ULTRON + KAIJU Iron Legion",
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

    def update_settings_file(self, settings_file: Path, is_user_settings: bool = False) -> Dict[str, Any]:
        """Update a settings file with ULTRON configuration"""
        self.logger.info(f"📝 Updating settings: {settings_file}")

        # Create directory if it doesn't exist
        settings_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing settings or create new
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            except Exception as e:
                self.logger.warning(f"⚠️  Could not read existing settings: {e}. Creating new file.")
                settings = {}
        else:
            settings = {}

        ultron_config = self.get_ultron_config()
        changes_made = []

        # Update workspace settings (full config)
        if not is_user_settings:
            # cursor.model.customModels
            if "cursor.model" not in settings:
                settings["cursor.model"] = {}
            if "customModels" not in settings["cursor.model"]:
                settings["cursor.model"]["customModels"] = []

            models = settings["cursor.model"]["customModels"]
            if not any(m.get("name") == "ULTRON" or m.get("title") == "ULTRON" for m in models):
                models.insert(0, ultron_config.copy())
                changes_made.append("Added ULTRON to cursor.model.customModels")

            # cursor.chat.customModels
            if "cursor.chat.customModels" not in settings:
                settings["cursor.chat.customModels"] = []

            chat_models = settings["cursor.chat.customModels"]
            if not any(m.get("name") == "ULTRON" or m.get("title") == "ULTRON" for m in chat_models):
                chat_models.insert(0, ultron_config.copy())
                changes_made.append("Added ULTRON to cursor.chat.customModels")

            # cursor.composer.customModels
            if "cursor.composer.customModels" not in settings:
                settings["cursor.composer.customModels"] = []

            composer_models = settings["cursor.composer.customModels"]
            if not any(m.get("name") == "ULTRON" or m.get("title") == "ULTRON" for m in composer_models):
                composer_models.insert(0, ultron_config.copy())
                changes_made.append("Added ULTRON to cursor.composer.customModels")

            # cursor.agent.customModels
            if "cursor.agent.customModels" not in settings:
                settings["cursor.agent.customModels"] = []

            agent_models = settings["cursor.agent.customModels"]
            if not any(m.get("name") == "ULTRON" or m.get("title") == "ULTRON" for m in agent_models):
                agent_models.insert(0, ultron_config.copy())
                changes_made.append("Added ULTRON to cursor.agent.customModels")

        # Update user settings (simpler config, just what's needed)
        else:
            # For user settings, we add minimal config
            if "cursor.chat.customModels" not in settings:
                settings["cursor.chat.customModels"] = []

            chat_models = settings["cursor.chat.customModels"]
            if not any(m.get("name") == "ULTRON" or m.get("title") == "ULTRON" for m in chat_models):
                # Simpler config for user settings
                simple_ultron = {
                    "name": "ULTRON",
                    "title": "ULTRON",
                    "provider": "ollama",
                    "model": "qwen2.5:72b",
                    "apiBase": "http://localhost:11434",
                    "contextLength": 32768,
                    "description": "ULTRON Virtual Hybrid Cluster"
                }
                chat_models.insert(0, simple_ultron)
                changes_made.append("Added ULTRON to cursor.chat.customModels (user settings)")

            if "cursor.agent.customModels" not in settings:
                settings["cursor.agent.customModels"] = []

            agent_models = settings["cursor.agent.customModels"]
            if not any(m.get("name") == "ULTRON" or m.get("title") == "ULTRON" for m in agent_models):
                simple_ultron = {
                    "name": "ULTRON",
                    "title": "ULTRON",
                    "provider": "ollama",
                    "model": "qwen2.5:72b",
                    "apiBase": "http://localhost:11434",
                    "contextLength": 32768,
                    "description": "ULTRON Virtual Hybrid Cluster"
                }
                agent_models.insert(0, simple_ultron)
                changes_made.append("Added ULTRON to cursor.agent.customModels (user settings)")

        # Set defaults
        if settings.get("cursor.chat.defaultModel") != "ULTRON":
            settings["cursor.chat.defaultModel"] = "ULTRON"
            changes_made.append("Set cursor.chat.defaultModel to ULTRON")

        if settings.get("cursor.composer.defaultModel") != "ULTRON":
            settings["cursor.composer.defaultModel"] = "ULTRON"
            changes_made.append("Set cursor.composer.defaultModel to ULTRON")

        if settings.get("cursor.agent.defaultModel") != "ULTRON":
            settings["cursor.agent.defaultModel"] = "ULTRON"
            changes_made.append("Set cursor.agent.defaultModel to ULTRON")

        # Set Ollama endpoint
        if settings.get("ollama.endpoint") != "http://localhost:11434":
            settings["ollama.endpoint"] = "http://localhost:11434"
            changes_made.append("Set ollama.endpoint to http://localhost:11434")

        if settings.get("ollama.defaultModel") != "qwen2.5:72b":
            settings["ollama.defaultModel"] = "qwen2.5:72b"
            changes_made.append("Set ollama.defaultModel to qwen2.5:72b")

        # Write back
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            self.logger.info(f"✅ Updated {settings_file}")
            return {"success": True, "changes": changes_made, "file": str(settings_file)}
        except Exception as e:
            self.logger.error(f"❌ Failed to write settings: {e}")
            return {"success": False, "error": str(e), "file": str(settings_file)}

    def activate(self) -> Dict[str, Any]:
        """Activate ULTRON in both workspace and user settings"""
        self.logger.info("🚀 Activating ULTRON in Cursor IDE...")

        results = {
            "timestamp": datetime.now().isoformat(),
            "workspace": None,
            "user": None,
            "success": False
        }

        # Update workspace settings
        if self.workspace_settings.exists() or True:  # Create if doesn't exist
            results["workspace"] = self.update_settings_file(self.workspace_settings, is_user_settings=False)
        else:
            results["workspace"] = {"success": False, "error": "Workspace settings file not found"}

        # Update user settings
        try:
            results["user"] = self.update_settings_file(self.user_settings, is_user_settings=True)
        except Exception as e:
            results["user"] = {"success": False, "error": str(e)}
            self.logger.warning(f"⚠️  Could not update user settings: {e}")
            self.logger.warning("   You may need to manually update user settings")

        # Overall success
        workspace_ok = results["workspace"] and results["workspace"].get("success", False)
        user_ok = results["user"] and results["user"].get("success", False)

        results["success"] = workspace_ok  # At least workspace should work

        if results["success"]:
            self.logger.info("✅ ULTRON activation complete!")
            self.logger.info("")
            self.logger.info("📋 Next Steps:")
            self.logger.info("   1. RESTART Cursor IDE completely (close all windows)")
            self.logger.info("   2. Open Cursor Chat (Ctrl+L)")
            self.logger.info("   3. Check model dropdown - ULTRON should appear")
            self.logger.info("   4. Select ULTRON if not already selected")
        else:
            self.logger.warning("⚠️  Activation partially completed")
            if not workspace_ok:
                self.logger.warning("   Workspace settings update failed")
            if not user_ok:
                self.logger.warning("   User settings update failed - may need manual update")

        return results


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Activate ULTRON in Cursor IDE")
        parser.add_argument("--workspace-only", action="store_true", help="Only update workspace settings")
        parser.add_argument("--user-only", action="store_true", help="Only update user settings")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        activator = JARVISActivateULTRONCursor(project_root)

        if args.workspace_only:
            result = activator.update_settings_file(activator.workspace_settings, is_user_settings=False)
            print(json.dumps(result, indent=2, default=str))
        elif args.user_only:
            result = activator.update_settings_file(activator.user_settings, is_user_settings=True)
            print(json.dumps(result, indent=2, default=str))
        else:
            result = activator.activate()
            print(json.dumps(result, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()