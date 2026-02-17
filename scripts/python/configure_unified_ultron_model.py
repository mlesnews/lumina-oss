#!/usr/bin/env python3
"""
Configure unified ULTRON model for Cursor using the cluster router
"""

import json
import os
from pathlib import Path
import requests

def get_cursor_settings_path():
    """Get the Cursor settings file path"""
    return Path(os.environ.get('APPDATA', '')) / 'Cursor' / 'User' / 'settings.json'

def test_router_connection():
    """Test if ULTRON router is reachable"""
    try:
        response = requests.get('http://localhost:8080/health', timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ ULTRON Router is healthy")
            print(f"   Status: {health_data.get('status', 'unknown')}")
            print(f"   Current Cluster: {health_data.get('cluster', 'unknown')}")
            print(f"   ULTRON Health: {health_data.get('ultron_health', 0)}%")
            return True
    except Exception as e:
        print(f"❌ ULTRON Router not reachable: {e}")
    return False

def create_unified_model_config():
    """Create a unified ULTRON model configuration for Cursor"""
    return {
        "title": "ULTRON",
        "name": "ultron",
        "provider": "ollama",
        "model": "ultron",
        "apiBase": "http://localhost:8080",
        "contextLength": 32768,
        "description": "ULTRON - Unified AI Cluster with 12-node virtual cluster, intelligent routing, and failover capabilities. Powered by qwen2.5-coder:7b, llama3.2:3b, and qwen2.5:72b models.",
        "localOnly": True,
        "skipProviderSelection": True,
        "cluster": {
            "type": "virtual_hybrid",
            "nodes": 12,
            "routing": "intelligent",
            "failover": "iron_legion",
            "description": "12-node ULTRON cluster with Iron Legion failover"
        }
    }

def update_cursor_settings():
    """Update Cursor settings with unified ULTRON model"""
    settings_path = get_cursor_settings_path()

    # Load existing settings
    if settings_path.exists():
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
    else:
        settings = {}

    # Create unified model config
    unified_model = create_unified_model_config()
    print(f"\nCreating unified ULTRON model: {unified_model['name']}")

    # Initialize settings structure
    if "cursor.chat" not in settings:
        settings["cursor.chat"] = {}
    if "customModels" not in settings["cursor.chat"]:
        settings["cursor.chat"]["customModels"] = []

    # Remove individual ULTRON models if they exist
    existing_names = {m.get("name") for m in settings["cursor.chat"]["customModels"]}
    if "ultron" not in existing_names:
        print(f"Adding unified ULTRON model to chat customModels")
        settings["cursor.chat"]["customModels"].append(unified_model)

    # Remove individual model entries (optional but cleaner)
    settings["cursor.chat"]["customModels"] = [
        m for m in settings["cursor.chat"]["customModels"] 
        if not (m.get("name", "").startswith("ultron-") and m.get("name", "") != "ultron")
    ]

    # Set as default model
    settings["cursor.chat"]["defaultModel"] = "ultron"

    # Apply to other Cursor components
    if "cursor.composer" not in settings:
        settings["cursor.composer"] = {}
    settings["cursor.composer"]["customModels"] = settings["cursor.chat"]["customModels"]
    settings["cursor.composer"]["defaultModel"] = settings["cursor.chat"]["defaultModel"]

    if "cursor.agent" not in settings:
        settings["cursor.agent"] = {}
    settings["cursor.agent"]["customModels"] = settings["cursor.chat"]["customModels"]
    settings["cursor.agent"]["defaultModel"] = settings["cursor.chat"]["defaultModel"]

    # Save settings
    with open(settings_path, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2)

    print(f"\n✅ Updated Cursor settings at: {settings_path}")
    print(f"   Total custom models: {len(settings['cursor.chat']['customModels'])}")
    print(f"   Default model: {settings['cursor.chat']['defaultModel']}")

    return settings

if __name__ == "__main__":
    print("Configuring Unified ULTRON Model for Cursor")
    print("=" * 50)

    if test_router_connection():
        update_cursor_settings()
        print("\n📋 Next Steps:")
        print("   1. Restart Cursor IDE")
        print("   2. Open Settings > Models")
        print("   3. ULTRON should appear as a single unified model")
        print("   4. Select ULTRON as default model")
    else:
        print("\n❌ Cannot configure ULTRON model - router not reachable")
