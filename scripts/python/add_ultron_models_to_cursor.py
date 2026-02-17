#!/usr/bin/env python3
"""
Add ULTRON cluster models to Cursor settings
"""

import json
import os
from pathlib import Path

def get_cursor_settings_path():
    """Get the Cursor settings file path"""
    return Path(os.environ.get('APPDATA', '')) / 'Cursor' / 'User' / 'settings.json'

def get_ultron_models():
    """Get available ULTRON models from local Ollama"""
    import requests

    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [m['name'] for m in data.get('models', [])]
    except Exception as e:
        print(f"Error fetching models from Ollama: {e}")

    # Fallback to default models
    return [
        "qwen2.5:72b",
        "qwen2.5:7b",
        "codellama:13b",
        "llama3.2:3b",
        "qwen2.5-coder:7b",
        "gpt-oss:20b"
    ]

def create_model_config(model_name, api_base="http://localhost:11434"):
    """Create a model configuration for Cursor"""
    return {
        "title": f"ULTRON/{model_name.split(':')[0]}",
        "name": f"ultron-{model_name.replace(':', '-')}",
        "provider": "ollama",
        "model": model_name,
        "apiBase": api_base,
        "contextLength": 32768,
        "description": f"ULTRON Local - {model_name}",
        "localOnly": True,
        "skipProviderSelection": True
    }

def update_cursor_settings():
    """Update Cursor settings with ULTRON models"""
    settings_path = get_cursor_settings_path()

    # Load existing settings
    if settings_path.exists():
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
    else:
        settings = {}

    # Get available models
    models = get_ultron_models()
    print(f"Found {len(models)} models in ULTRON cluster")

    # Create model configurations
    custom_models = []
    for model in models:
        config = create_model_config(model)
        custom_models.append(config)
        print(f"  - {config['name']}: {config['title']}")

    # Update settings for different Cursor components
    if "cursor.chat" not in settings:
        settings["cursor.chat"] = {}
    if "customModels" not in settings["cursor.chat"]:
        settings["cursor.chat"]["customModels"] = []

    # Merge with existing models (avoid duplicates)
    existing_names = {m.get("name") for m in settings["cursor.chat"]["customModels"]}
    for model in custom_models:
        if model["name"] not in existing_names:
            settings["cursor.chat"]["customModels"].append(model)
            existing_names.add(model["name"])

    # Set default model
    if custom_models:
        settings["cursor.chat"]["defaultModel"] = custom_models[0]["name"]

    if "cursor.composer" not in settings:
        settings["cursor.composer"] = {}
    settings["cursor.composer"]["customModels"] = settings["cursor.chat"]["customModels"]
    settings["cursor.composer"]["defaultModel"] = settings["cursor.chat"]["defaultModel"]

    if "cursor.agent" not in settings:
        settings["cursor.agent"] = {}
    settings["cursor.agent"]["customModels"] = settings["cursor.chat"]["customModels"]
    settings["cursor.agent"]["defaultModel"] = settings["cursor.chat"]["defaultModel"]

    # Save settings
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    with open(settings_path, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2)

    print(f"\n✅ Updated Cursor settings at: {settings_path}")
    print(f"   Total custom models: {len(settings['cursor.chat']['customModels'])}")
    print(f"   Default model: {settings['cursor.chat']['defaultModel']}")

    return settings

if __name__ == "__main__":
    update_cursor_settings()
