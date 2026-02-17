#!/usr/bin/env python3
"""
JARVIS: Fix ULTRON and IRON LEGION Endpoints

Updates Cursor settings to use working endpoints (NAS Ollama) instead of non-functional KUBE.

Tags: #FIX #ULTRON #IRON_LEGION #ENDPOINTS #NAS_OLLAMA @JARVIS @LUMINA
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
    logger = get_logger("JARVISFixEndpoints")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("JARVISFixEndpoints")


def update_model_endpoint(model: Dict[str, Any], model_name: str, use_ollama: bool = True) -> bool:
    """Update model endpoint to use working NAS Ollama instead of KUBE"""
    changed = False

    current_api_base = model.get("apiBase", "")

    # Determine target endpoint based on model
    if "ULTRON" in model_name.upper():
        # ULTRON: Try local Ollama first, fallback to NAS Ollama
        if use_ollama:
            target_endpoint = "http://<NAS_PRIMARY_IP>:11434"  # NAS Ollama (working)
            target_provider = "ollama"
        else:
            target_endpoint = "http://<NAS_PRIMARY_IP>:8000/v1"  # KUBE (not working)
            target_provider = "openai"
    elif "KAIJU" in model_name.upper() or "IRON" in model_name.upper():
        # KAIJU/IRON LEGION: Use NAS Ollama
        target_endpoint = "http://<NAS_PRIMARY_IP>:11434"  # NAS Ollama (working)
        target_provider = "ollama"
    else:
        # Default to NAS Ollama
        target_endpoint = "http://<NAS_PRIMARY_IP>:11434"
        target_provider = "ollama"

    # Update if different
    if current_api_base != target_endpoint:
        model["apiBase"] = target_endpoint
        changed = True
        logger.info(f"Updated {model_name} apiBase: {current_api_base} → {target_endpoint}")

    # Update provider if needed
    if model.get("provider") != target_provider:
        model["provider"] = target_provider
        changed = True
        logger.info(f"Updated {model_name} provider: {model.get('provider')} → {target_provider}")

    # Ensure local-only settings
    if model.get("localOnly") != True:
        model["localOnly"] = True
        changed = True

    if model.get("skipProviderSelection") != True:
        model["skipProviderSelection"] = True
        changed = True

    # Remove API key requirements
    for key in ["apiKey", "requiresApiKey", "subscription", "requiresSubscription"]:
        if key in model:
            del model[key]
            changed = True

    return changed


def fix_all_models(settings: Dict[str, Any], use_ollama: bool = True) -> int:
    """Fix all model configurations"""
    sections_to_fix = [
        "cursor.agent.customModels",
        "cursor.chat.customModels",
        "cursor.composer.customModels",
        "cursor.inlineCompletion.customModels",
        "cursor.model.customModels"
    ]

    total_changes = 0

    for section_key in sections_to_fix:
        if section_key not in settings:
            continue

        models = settings[section_key]
        for model in models:
            name = model.get("name", "") or model.get("title", "")
            if update_model_endpoint(model, name, use_ollama):
                total_changes += 1

    return total_changes


def main():
    try:
        """Main fix workflow"""
        print("=" * 80)
        print("🔧 JARVIS: FIXING ULTRON & IRON LEGION ENDPOINTS")
        print("=" * 80)
        print()

        if not settings_file.exists():
            print(f"❌ Settings file not found: {settings_file}")
            return 1

        # Read settings
        logger.info(f"Reading settings from: {settings_file}")
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)

        print("📋 Current Configuration:")
        print("-" * 80)

        # Show current ULTRON config
        agent_models = settings.get("cursor.agent.customModels", [])
        ultron = next((m for m in agent_models if "ULTRON" in (m.get("name", "") or m.get("title", "")).upper()), None)
        if ultron:
            print(f"  ULTRON:")
            print(f"    apiBase: {ultron.get('apiBase', 'Not set')}")
            print(f"    provider: {ultron.get('provider', 'Not set')}")
            print(f"    localOnly: {ultron.get('localOnly', False)}")
        print()

        # Fix all models to use NAS Ollama
        print("🔧 Updating endpoints to use NAS Ollama (working endpoint)...")
        print()

        changes = fix_all_models(settings, use_ollama=True)

        if changes > 0:
            # Write back
            logger.info(f"Writing fixed settings to: {settings_file}")
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

            print(f"✅ Updated {changes} model configuration(s)!")
            print()

            # Show new ULTRON config
            agent_models = settings.get("cursor.agent.customModels", [])
            ultron = next((m for m in agent_models if "ULTRON" in (m.get("name", "") or m.get("title", "")).upper()), None)
            if ultron:
                print("📋 New Configuration:")
                print("-" * 80)
                print(f"  ULTRON:")
                print(f"    apiBase: {ultron.get('apiBase', 'Not set')}")
                print(f"    provider: {ultron.get('provider', 'Not set')}")
                print(f"    localOnly: {ultron.get('localOnly', False)}")
                print()

            print("=" * 80)
            print("✅ FIX COMPLETE")
            print("=" * 80)
            print()
            print("📝 Next Steps:")
            print("   1. Restart Cursor IDE for changes to take effect")
            print("   2. Select 'ULTRON' from the model selector in Cursor")
            print("   3. Verify ULTRON is working in chat/agent")
            print()
            print("💡 Note: Models are now using NAS Ollama endpoint (<NAS_PRIMARY_IP>:11434)")
            print("   This endpoint is confirmed working with KAIJU (llama3.2:3b)")
            print()

            return 0
        else:
            print("✅ No changes needed - endpoints are already correct")
            print()
            return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())