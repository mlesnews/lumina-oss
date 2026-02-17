#!/usr/bin/env python3
"""
Fix ALL Local Models - NO API Keys, NO Cloud Configuration
SYPHON: "THE REASON WHY WE KEEP TRYING TO CONFIGURE LOCAL AI MODELS AS CLOUD AI MODELS?"

Rule: ALL LOCAL LLMs and ALL OTHER AI MODELS = NO SUBSCRIPTION PLANS, NO API KEYS
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import logging
logger = logging.getLogger("fix_all_local_models_no_api_keys")


# Local model providers (NO API KEYS)
LOCAL_PROVIDERS = ["ollama", "local", "self-hosted"]
LOCAL_ENDPOINTS = ["localhost", "127.0.0.1", "<NAS_IP>", "<NAS_PRIMARY_IP>"]

project_root = Path(__file__).parent.parent.parent

def is_local_model(model: Dict) -> bool:
    """Check if model is local (no API keys needed)"""
    provider = model.get("provider", "").lower()
    api_base = model.get("apiBase", "").lower()

    # Check provider
    if provider in LOCAL_PROVIDERS:
        return True

    # Check endpoint
    for local_endpoint in LOCAL_ENDPOINTS:
        if local_endpoint in api_base:
            return True

    return False

def fix_model_config(model: Dict) -> Dict:
    """Fix a single model config - remove API keys, set local flags"""
    fixed = model.copy()

    # If it's a local model, ensure NO API keys
    if is_local_model(model):
        # Remove ALL API key fields
        for key in ["apiKey", "api_key", "API_KEY", "requiresApiKey", "requires_api_key", "subscription", "subscriptionPlan"]:
            if key in fixed:
                del fixed[key]

        # Set local flags
        fixed["localOnly"] = True
        fixed["requiresApiKey"] = False
        fixed["skipProviderSelection"] = True

        # Ensure provider is ollama for local models
        if "ollama" in fixed.get("apiBase", "").lower() or fixed.get("provider", "").lower() == "ollama":
            fixed["provider"] = "ollama"

        # Add LOCAL ONLY to description
        desc = fixed.get("description", "")
        if "LOCAL ONLY" not in desc.upper():
            fixed["description"] = f"{desc} - LOCAL ONLY, NO API KEY"

    return fixed

def fix_cursor_models_config():
    try:
        """Fix cursor_models_config.json"""
        config_file = project_root / "data" / "cursor_models" / "cursor_models_config.json"

        if not config_file.exists():
            print(f"⚠️  Config not found: {config_file}")
            return False

        print(f"📝 Fixing: {config_file}")

        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        fixed_count = 0

        # Fix all model sections
        for section in ["cursor.chat.customModels", "cursor.composer.customModels", "cursor.agent.customModels", "cursor.inlineCompletion.customModels"]:
            if section in config:
                for i, model in enumerate(config[section]):
                    original = model.copy()
                    fixed = fix_model_config(model)

                    if fixed != original:
                        config[section][i] = fixed
                        fixed_count += 1
                        print(f"  ✅ Fixed: {fixed.get('name', 'unknown')} ({section})")

        # Write back
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print(f"✅ Fixed {fixed_count} models in cursor_models_config.json")
        return True

    except Exception as e:
        logger.error(f"Error in fix_cursor_models_config: {e}", exc_info=True)
        raise
def fix_cursor_settings():
    try:
        """Fix .cursor/settings.json"""
        settings_file = project_root / ".cursor" / "settings.json"

        if not settings_file.exists():
            print(f"⚠️  Settings not found: {settings_file}")
            return False

        print(f"📝 Fixing: {settings_file}")

        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)

        fixed_count = 0

        # Fix all model sections
        for section in ["cursor.chat.customModels", "cursor.composer.customModels", "cursor.agent.customModels", "cursor.inlineCompletion.customModels"]:
            if section in settings:
                for i, model in enumerate(settings[section]):
                    original = model.copy()
                    fixed = fix_model_config(model)

                    if fixed != original:
                        settings[section][i] = fixed
                        fixed_count += 1
                        print(f"  ✅ Fixed: {fixed.get('name', 'unknown')} ({section})")

        # Write back
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)

        print(f"✅ Fixed {fixed_count} models in settings.json")
        return True

    except Exception as e:
        logger.error(f"Error in fix_cursor_settings: {e}", exc_info=True)
        raise
def fix_all_configs():
    """Fix all configuration files"""
    print("=" * 80)
    print("FIXING ALL LOCAL MODELS - NO API KEYS")
    print("=" * 80)
    print()
    print("Rule: ALL LOCAL LLMs = NO SUBSCRIPTION PLANS, NO API KEYS")
    print()

    results = []

    # Fix cursor models config
    results.append(("cursor_models_config.json", fix_cursor_models_config()))

    # Fix cursor settings
    results.append(("settings.json", fix_cursor_settings()))

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")

    all_success = all(success for _, success in results)

    if all_success:
        print()
        print("✅ ALL LOCAL MODELS FIXED - NO API KEYS")
        print("   - All local models have localOnly: true")
        print("   - All local models have requiresApiKey: false")
        print("   - All API key fields removed from local models")
        print("   - All local models marked as LOCAL ONLY")

    return all_success

if __name__ == "__main__":
    success = fix_all_configs()
    sys.exit(0 if success else 1)
