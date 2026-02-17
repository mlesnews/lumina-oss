#!/usr/bin/env python3
"""
Fix Cursor Iron Legion / ULTRON Configuration

Fixes the issue where Cursor is trying to validate "Iron Legion" as a cloud model
when it should be recognized as a local Ollama model. Also ensures ULTRON cluster
is properly visible.
"""

import json
import sys
from pathlib import Path
import logging
logger = logging.getLogger("fix_cursor_iron_legion_ultron_config")


project_root = Path(__file__).parent.parent.parent
settings_file = project_root / ".cursor" / "settings.json"

def fix_cursor_settings():
    try:
        """Fix Cursor settings to ensure local models are properly configured."""

        if not settings_file.exists():
            print(f"❌ Settings file not found: {settings_file}")
            return False

        print(f"📝 Reading settings from: {settings_file}")
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)

        # Ensure all agent models are properly configured
        if "cursor.agent.customModels" not in settings:
            settings["cursor.agent.customModels"] = []

        # Find and fix any "Iron Legion" references that might be causing issues
        agent_models = settings["cursor.agent.customModels"]

        # Remove any models with "Iron Legion" in the name that aren't properly configured
        agent_models = [
            model for model in agent_models 
            if not (model.get("name", "").lower() == "iron legion" or 
                    model.get("title", "").lower() == "iron legion")
        ]

        # Ensure ULTRON is the first and default agent model
        ultron_found = False
        for model in agent_models:
            if model.get("name") == "ULTRON":
                ultron_found = True
                # Ensure it has all required properties
                model["localOnly"] = True
                model["skipProviderSelection"] = True
                model["provider"] = "ollama"
                # Ensure cluster config is present
                if "cluster" not in model:
                    model["cluster"] = {
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
                break

        # If ULTRON not found, add it
        if not ultron_found:
            ultron_model = {
                "title": "ULTRON",
                "name": "ULTRON",
                "provider": "ollama",
                "model": "qwen2.5:72b",
                "apiBase": "http://localhost:11434",
                "contextLength": 32768,
                "description": "ULTRON Virtual Hybrid Cluster - Laptop ULTRON + KAIJU (LOCAL ONLY)",
                "localOnly": True,
                "skipProviderSelection": True,
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
            agent_models.insert(0, ultron_model)

        # Ensure KAIJU (Iron Legion) is properly configured as local
        for model in agent_models:
            if model.get("name") == "KAIJU" or "Iron Legion" in model.get("title", ""):
                model["localOnly"] = True
                model["skipProviderSelection"] = True
                model["provider"] = "ollama"
                # Remove any API key requirements
                if "apiKey" in model:
                    del model["apiKey"]
                if "requiresApiKey" in model:
                    del model["requiresApiKey"]

        settings["cursor.agent.customModels"] = agent_models

        # Ensure default agent model is ULTRON
        settings["cursor.agent.defaultModel"] = "ULTRON"

        # Ensure all other model sections also have proper local config
        for section in ["cursor.chat.customModels", "cursor.composer.customModels", "cursor.inlineCompletion.customModels"]:
            if section in settings:
                for model in settings[section]:
                    if model.get("provider") == "ollama":
                        model["localOnly"] = True
                        model["skipProviderSelection"] = True
                        # Remove any API key requirements
                        if "apiKey" in model:
                            del model["apiKey"]
                        if "requiresApiKey" in model:
                            del model["requiresApiKey"]

        # Write back
        print(f"💾 Writing fixed settings to: {settings_file}")
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)

        print("✅ Settings fixed!")
        print("\n📋 Changes made:")
        print("   - Ensured ULTRON is the default agent model")
        print("   - Removed any 'Iron Legion' models that might cause validation issues")
        print("   - Ensured all Ollama models have localOnly: true")
        print("   - Ensured all Ollama models have skipProviderSelection: true")
        print("   - Removed any API key requirements from local models")
        print("   - Ensured ULTRON cluster configuration is present")

        return True

    except Exception as e:
        logger.error(f"Error in fix_cursor_settings: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    success = fix_cursor_settings()
    sys.exit(0 if success else 1)
