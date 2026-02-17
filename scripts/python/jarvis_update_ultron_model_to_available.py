#!/usr/bin/env python3
"""
JARVIS: Update ULTRON to Use Available Model

Temporarily updates ULTRON to use llama3.2:3b (available on NAS) until qwen2.5:72b is pulled.

Tags: #FIX #ULTRON #MODEL #TEMPORARY @JARVIS @LUMINA
"""

import json
import sys
from pathlib import Path

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
settings_file = project_root / ".cursor" / "settings.json"

try:
    from lumina_core.logging import get_logger
    logger = get_logger("JARVISUpdateUltronModel")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("JARVISUpdateUltronModel")


def update_ultron_model(settings: dict, available_model: str = "llama3.2:3b") -> int:
    """Update ULTRON to use available model"""
    sections_to_fix = [
        "cursor.agent.customModels",
        "cursor.chat.customModels",
        "cursor.composer.customModels",
        "cursor.inlineCompletion.customModels",
        "cursor.model.customModels"
    ]

    changes = 0

    for section_key in sections_to_fix:
        if section_key not in settings:
            continue

        models = settings[section_key]
        for model in models:
            name = model.get("name", "") or model.get("title", "")
            if "ULTRON" in name.upper() and model.get("model") != available_model:
                old_model = model.get("model", "Not set")
                model["model"] = available_model
                # Update context length for llama3.2:3b (8K instead of 32K)
                if available_model == "llama3.2:3b":
                    model["contextLength"] = 8192
                changes += 1
                logger.info(f"Updated {name} model: {old_model} → {available_model}")

    return changes


def main():
    try:
        """Main update workflow"""
        print("=" * 80)
        print("🔧 JARVIS: UPDATING ULTRON TO USE AVAILABLE MODEL")
        print("=" * 80)
        print()

        if not settings_file.exists():
            print(f"❌ Settings file not found: {settings_file}")
            return 1

        # Read settings
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)

        print("📋 Current ULTRON Configuration:")
        agent_models = settings.get("cursor.agent.customModels", [])
        ultron = next((m for m in agent_models if "ULTRON" in (m.get("name", "") or m.get("title", "")).upper()), None)
        if ultron:
            print(f"  Model: {ultron.get('model', 'Not set')}")
            print(f"  Context Length: {ultron.get('contextLength', 'Not set')}")
        print()

        print("🔧 Updating ULTRON to use llama3.2:3b (available on NAS)...")
        print()

        changes = update_ultron_model(settings, "llama3.2:3b")

        if changes > 0:
            # Write back
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

            print(f"✅ Updated {changes} ULTRON configuration(s)!")
            print()

            # Show new config
            agent_models = settings.get("cursor.agent.customModels", [])
            ultron = next((m for m in agent_models if "ULTRON" in (m.get("name", "") or m.get("title", "")).upper()), None)
            if ultron:
                print("📋 New ULTRON Configuration:")
                print(f"  Model: {ultron.get('model', 'Not set')}")
                print(f"  Context Length: {ultron.get('contextLength', 'Not set')}")
                print(f"  Endpoint: {ultron.get('apiBase', 'Not set')}")
            print()

            print("=" * 80)
            print("✅ UPDATE COMPLETE")
            print("=" * 80)
            print()
            print("📝 Next Steps:")
            print("   1. Restart Cursor IDE for changes to take effect")
            print("   2. ULTRON will now use llama3.2:3b (available on NAS)")
            print("   3. To use qwen2.5:72b later, pull it on NAS: ollama pull qwen2.5:72b")
            print()

            return 0
        else:
            print("✅ ULTRON already configured correctly")
            return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())