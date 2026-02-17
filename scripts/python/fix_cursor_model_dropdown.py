#!/usr/bin/env python3
"""
Fix Cursor Model Dropdown - Only Show Available Models

Removes unavailable models from configuration so they don't clutter the dropdown.
Ensures ULTRON is visible and properly configured.
"""

import json
import sys
import requests
from pathlib import Path
from typing import Dict, Any, List, Set
import logging
logger = logging.getLogger("fix_cursor_model_dropdown")


project_root = Path(__file__).parent.parent.parent
settings_file = project_root / ".cursor" / "settings.json"

def check_model_available(endpoint: str, model_name: str) -> bool:
    """Check if a model is available at an endpoint."""
    try:
        response = requests.get(f"{endpoint}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            # Check exact match or partial match
            return model_name in model_names or any(model_name in name for name in model_names)
        return False
    except:
        return False

def get_available_models() -> Dict[str, Dict[str, Any]]:
    """Get list of available models from all endpoints."""
    available = {}

    endpoints = {
        "ULTRON Local": "http://localhost:11434",
        "KAIJU": "http://<NAS_PRIMARY_IP>:11434"
    }

    for endpoint_name, endpoint_url in endpoints.items():
        try:
            response = requests.get(f"{endpoint_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                for model in models:
                    model_name = model.get("name", "")
                    if model_name:
                        available[model_name] = {
                            "endpoint": endpoint_url,
                            "endpoint_name": endpoint_name,
                            "full_name": model_name
                        }
        except Exception as e:
            print(f"   ⚠️  Could not check {endpoint_name}: {e}")

    return available

def fix_cursor_settings():
    try:
        """Fix Cursor settings to only show available models."""

        if not settings_file.exists():
            print(f"❌ Settings file not found: {settings_file}")
            return False

        print("=" * 70)
        print("🔍 Checking Available Models")
        print("=" * 70)
        print()

        available_models = get_available_models()

        print(f"📊 Found {len(available_models)} available models:")
        for model_name, info in available_models.items():
            print(f"   ✅ {model_name} ({info['endpoint_name']})")
        print()

        if not available_models:
            print("❌ No models found! Please ensure Ollama is running.")
            return False

        print("=" * 70)
        print("📝 Reading Current Settings")
        print("=" * 70)
        print()

        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)

        # Fix agent models - only keep available ones
        print("🔧 Fixing Agent Models...")
        print("-" * 70)

        original_agent_models = settings.get("cursor.agent.customModels", [])
        filtered_agent_models = []

        # Always include ULTRON first (even if model name doesn't match exactly)
        ultron_found = False
        for model in original_agent_models:
            if model.get("name") == "ULTRON":
                # Verify ULTRON endpoint is accessible
                endpoint = model.get("apiBase", "")
                if endpoint and check_model_available(endpoint, "qwen2.5:72b"):
                    filtered_agent_models.append(model)
                    ultron_found = True
                    print(f"   ✅ ULTRON - Available at {endpoint}")
                else:
                    # ULTRON endpoint not accessible, but keep it anyway as primary
                    print(f"   ⚠️  ULTRON - Endpoint {endpoint} not accessible, but keeping as primary")
                    filtered_agent_models.append(model)
                    ultron_found = True
                break

        # If ULTRON not found, create it
        if not ultron_found:
            print("   ➕ Creating ULTRON configuration...")
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
            filtered_agent_models.insert(0, ultron_model)
            print("   ✅ ULTRON created")

        # Filter other models - only keep if available
        for model in original_agent_models:
            if model.get("name") == "ULTRON":
                continue  # Already handled

            model_name = model.get("name", "")
            model_title = model.get("title", "")
            endpoint = model.get("apiBase", "")
            model_id = model.get("model", "")

            # Check if this model is available
            is_available = False
            if endpoint and model_id:
                is_available = check_model_available(endpoint, model_id)

            if is_available:
                filtered_agent_models.append(model)
                print(f"   ✅ {model_title} ({model_name}) - Available")
            else:
                print(f"   ❌ {model_title} ({model_name}) - Not available, removing")

        settings["cursor.agent.customModels"] = filtered_agent_models
        settings["cursor.agent.defaultModel"] = "ULTRON"

        # Also fix chat and composer models
        for section in ["cursor.chat.customModels", "cursor.composer.customModels"]:
            if section in settings:
                original = settings[section]
                filtered = []

                for model in original:
                    if model.get("name") == "ULTRON":
                        filtered.append(model)  # Always include ULTRON
                    else:
                        endpoint = model.get("apiBase", "")
                        model_id = model.get("model", "")
                        if endpoint and model_id and check_model_available(endpoint, model_id):
                            filtered.append(model)

                settings[section] = filtered

        # Write back
        print()
        print("=" * 70)
        print("💾 Writing Fixed Settings")
        print("=" * 70)
        print()

        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)

        print("✅ Settings fixed!")
        print()
        print("📋 Summary:")
        print(f"   - Agent models: {len(filtered_agent_models)} (was {len(original_agent_models)})")
        print(f"   - ULTRON: {'✅ Visible' if ultron_found else '✅ Created'}")
        print(f"   - Available models only: ✅")
        print()
        print("💡 Next Steps:")
        print("   1. Reload Cursor IDE (close and reopen)")
        print("   2. Check model dropdown - ULTRON should be visible")
        print("   3. Select ULTRON as your agent model")
        print()

        return True

    except Exception as e:
        logger.error(f"Error in fix_cursor_settings: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    success = fix_cursor_settings()
    sys.exit(0 if success else 1)
