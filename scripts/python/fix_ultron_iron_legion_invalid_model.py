#!/usr/bin/env python3
"""
Fix ULTRON and IRON LEGION "Invalid Model" Errors

Fixes the issue where Cursor validates ULTRON and IRON LEGION as cloud models
requiring API keys/subscriptions when they should be local Ollama models.

Tags: #FIX #ULTRON #IRON_LEGION #INVALID_MODEL #API_KEY @JARVIS @LUMINA
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
settings_file = project_root / ".cursor" / "settings.json"

try:
    from lumina_core.logging import get_logger
    logger = get_logger("FixUltronIronLegion")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("FixUltronIronLegion")


def fix_model_config(model: Dict[str, Any], model_name: str) -> bool:
    """Fix a single model configuration to be properly local"""
    changed = False

    # Ensure it's marked as local-only Ollama
    if model.get("localOnly") != True:
        model["localOnly"] = True
        changed = True
        logger.info(f"Set {model_name} localOnly: true")

    if model.get("skipProviderSelection") != True:
        model["skipProviderSelection"] = True
        changed = True
        logger.info(f"Set {model_name} skipProviderSelection: true")

    # Keep provider as-is if using KUBE (OpenAI-compatible API)
    # Only change to ollama if using actual Ollama endpoint
    api_base = model.get("apiBase", "")
    if "ollama" in api_base.lower() or "11434" in api_base or "11437" in api_base:
        if model.get("provider") != "ollama":
            model["provider"] = "ollama"
            changed = True
            logger.info(f"Set {model_name} provider: ollama (Ollama endpoint detected)")
    elif "8000" in api_base or "kube" in api_base.lower():
        # KUBE uses OpenAI-compatible API, keep provider as "openai"
        if model.get("provider") != "openai":
            model["provider"] = "openai"
            changed = True
            logger.info(f"Set {model_name} provider: openai (KUBE endpoint detected)")

    # Remove any API key requirements (causes "invalid model" errors)
    if "apiKey" in model:
        del model["apiKey"]
        changed = True
        logger.info(f"Removed {model_name} apiKey")

    if "requiresApiKey" in model:
        del model["requiresApiKey"]
        changed = True
        logger.info(f"Removed {model_name} requiresApiKey")

    if "subscription" in model:
        del model["subscription"]
        changed = True
        logger.info(f"Removed {model_name} subscription")

    if "requiresSubscription" in model:
        del model["requiresSubscription"]
        changed = True
        logger.info(f"Removed {model_name} requiresSubscription")

    # Ensure apiBase is set for local Ollama
    if "apiBase" not in model or not model["apiBase"]:
        if "ULTRON" in model_name.upper():
            model["apiBase"] = "http://localhost:11434"
        elif "IRON" in model_name.upper() or "KAIJU" in model_name.upper():
            model["apiBase"] = "http://<NAS_IP>:3000"
        changed = True
        logger.info(f"Set {model_name} apiBase")

    return changed


def fix_ultron_model(models: List[Dict[str, Any]]) -> bool:
    """Ensure ULTRON is properly configured"""
    ultron = next((m for m in models if m.get("name") == "ULTRON" or m.get("title") == "ULTRON"), None)

    if not ultron:
        # Add ULTRON if missing
        ultron = {
            "title": "ULTRON",
            "name": "ULTRON",
            "provider": "ollama",
            "model": "qwen2.5:72b",
            "apiBase": "http://localhost:11434",
            "contextLength": 32768,
            "description": "ULTRON Virtual Hybrid Cluster - Laptop ULTRON + KAIJU (LOCAL ONLY)",
            "localOnly": True,
            "skipProviderSelection": True
        }
        models.insert(0, ultron)
        logger.info("Added ULTRON model")
        return True

    return fix_model_config(ultron, "ULTRON")


def fix_iron_legion_models(models: List[Dict[str, Any]]) -> bool:
    """Fix all Iron Legion/KAIJU models"""
    changed = False

    for model in models:
        name = model.get("name", "") or model.get("title", "")
        name_lower = name.lower()

        # Check if this is an Iron Legion or KAIJU model
        if any(keyword in name_lower for keyword in ["iron legion", "kaiju", "iron_legion"]):
            if fix_model_config(model, name):
                changed = True

    return changed


def fix_cursor_settings() -> bool:
    try:
        """Fix Cursor settings to resolve invalid model errors"""

        if not settings_file.exists():
            logger.error(f"Settings file not found: {settings_file}")
            print(f"❌ Settings file not found: {settings_file}")
            return False

        print("="*80)
        print("🔧 FIXING ULTRON AND IRON LEGION INVALID MODEL ERRORS")
        print("="*80)
        print()

        logger.info(f"Reading settings from: {settings_file}")
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)

        sections_to_fix = [
            "cursor.agent.customModels",
            "cursor.chat.customModels",
            "cursor.composer.customModels",
            "cursor.inlineCompletion.customModels"
        ]

        total_changes = 0

        for section_key in sections_to_fix:
            if section_key not in settings:
                settings[section_key] = []
                continue

            models = settings[section_key]
            section_changed = False

            # Fix ULTRON
            if fix_ultron_model(models):
                section_changed = True
                total_changes += 1

            # Fix Iron Legion models
            if fix_iron_legion_models(models):
                section_changed = True
                total_changes += 1

            if section_changed:
                settings[section_key] = models
                logger.info(f"Fixed {section_key}")

        # Ensure ULTRON is the default agent model
        if settings.get("cursor.agent.defaultModel") != "ULTRON":
            settings["cursor.agent.defaultModel"] = "ULTRON"
            total_changes += 1
            logger.info("Set ULTRON as default agent model")

        # Write back if changes were made
        if total_changes > 0:
            logger.info(f"Writing fixed settings to: {settings_file}")
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

            print(f"✅ Fixed {total_changes} configuration issue(s)!")
            print()
            print("📋 Changes made:")
            print("   - Ensured ULTRON is properly configured as local-only Ollama")
            print("   - Fixed all Iron Legion/KAIJU models to be local-only")
            print("   - Removed API key/subscription requirements (causes 'invalid model' errors)")
            print("   - Set skipProviderSelection: true (prevents cloud validation)")
            print("   - Set localOnly: true (prevents subscription checks)")
            print("   - Ensured ULTRON is the default agent model")
            print()
            print("⚠️  IMPORTANT: Restart Cursor IDE for changes to take effect")
            print()
            return True
        else:
            print("✅ No changes needed - models are already properly configured")
            print()
            return True


    except Exception as e:
        logger.error(f"Error in fix_cursor_settings: {e}", exc_info=True)
        raise
def main():
    """Main entry point"""
    success = fix_cursor_settings()
    return 0 if success else 1


if __name__ == "__main__":


    sys.exit(main())