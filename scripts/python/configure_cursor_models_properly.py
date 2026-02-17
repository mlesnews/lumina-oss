#!/usr/bin/env python3
"""
Configure Cursor IDE Models Properly
Adds proper configuration (localOnly, skipProviderSelection, requiresApiKey) to all local models
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import logging
logger = logging.getLogger("configure_cursor_models_properly")


project_root = Path(__file__).parent.parent.parent
settings_file = project_root / ".cursor" / "settings.json"

# Local model providers (NO API KEYS)
LOCAL_PROVIDERS = ["ollama", "local", "self-hosted"]
LOCAL_ENDPOINTS = ["localhost", "127.0.0.1", "<NAS_IP>", "<NAS_PRIMARY_IP>"]

def is_local_model(model: Dict) -> bool:
    """Check if model is local"""
    provider = model.get("provider", "").lower()
    api_base = model.get("apiBase", "").lower()

    if provider in LOCAL_PROVIDERS:
        return True

    for local_endpoint in LOCAL_ENDPOINTS:
        if local_endpoint in api_base:
            return True

    return False

def ensure_proper_config(model: Dict) -> Dict:
    """Ensure model has proper local configuration"""
    fixed = model.copy()

    if is_local_model(model):
        # Add/ensure proper local config
        fixed["localOnly"] = True
        fixed["skipProviderSelection"] = True
        fixed["requiresApiKey"] = False

        # Remove any API key fields
        for key in ["apiKey", "api_key", "API_KEY", "subscription", "subscriptionPlan"]:
            if key in fixed:
                del fixed[key]

        # Ensure description mentions LOCAL ONLY
        desc = fixed.get("description", "")
        if "LOCAL ONLY" not in desc.upper() and "NO API KEY" not in desc.upper():
            fixed["description"] = f"{desc} - LOCAL ONLY, NO API KEY"

    return fixed

def fix_all_model_sections(settings: Dict) -> int:
    """Fix all model sections in settings"""
    fixed_count = 0

    # All sections that can have customModels
    model_sections = [
        "cursor.chat.customModels",
        "cursor.composer.customModels",
        "cursor.agent.customModels",
        "cursor.inlineCompletion.customModels",
        "cursor.model.customModels"
    ]

    for section in model_sections:
        if section in settings and isinstance(settings[section], list):
            for i, model in enumerate(settings[section]):
                original = model.copy()
                fixed = ensure_proper_config(model)

                if fixed != original:
                    settings[section][i] = fixed
                    fixed_count += 1
                    model_name = fixed.get("name", fixed.get("title", "unknown"))
                    print(f"  ✅ Fixed: {model_name} ({section})")

    return fixed_count

def main():
    try:
        """Main function"""
        print("=" * 80)
        print("CONFIGURING CURSOR IDE MODELS PROPERLY")
        print("=" * 80)
        print()
        print("Location: .cursor/settings.json")
        print("Sections:")
        print("  - cursor.chat.customModels")
        print("  - cursor.composer.customModels")
        print("  - cursor.agent.customModels")
        print("  - cursor.inlineCompletion.customModels")
        print()

        if not settings_file.exists():
            print(f"❌ Settings file not found: {settings_file}")
            print()
            print("To configure models in Cursor IDE:")
            print("  1. Open Cursor Settings (Ctrl+Shift+,)")
            print("  2. Search for 'Models'")
            print("  3. Add models to each section:")
            print("     - Chat Models")
            print("     - Composer Models")
            print("     - Agent Models")
            print("     - Inline Completion Models")
            print()
            print("  4. For LOCAL models, ensure these fields are set:")
            print("     - localOnly: true")
            print("     - skipProviderSelection: true")
            print("     - requiresApiKey: false")
            return False

        print(f"📝 Reading: {settings_file}")
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)

        print()
        print("Fixing all model configurations...")
        print("-" * 80)

        fixed_count = fix_all_model_sections(settings)

        if fixed_count > 0:
            print()
            print(f"💾 Writing {fixed_count} fixes to: {settings_file}")
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

            print()
            print("✅ All models properly configured!")
            print()
            print("Configuration added to all local models:")
            print("  - localOnly: true")
            print("  - skipProviderSelection: true")
            print("  - requiresApiKey: false")
            print("  - Description updated with 'LOCAL ONLY, NO API KEY'")
        else:
            print()
            print("✅ All models already properly configured!")

        print()
        print("=" * 80)
        print("HOW TO ADD MODELS IN CURSOR IDE")
        print("=" * 80)
        print()
        print("Method 1: Via Settings UI")
        print("  1. Open Cursor Settings (Ctrl+Shift+,)")
        print("  2. Search for 'Models' or 'customModels'")
        print("  3. Click 'Edit in settings.json'")
        print("  4. Add your model to the appropriate section:")
        print("     - cursor.chat.customModels (for Chat)")
        print("     - cursor.composer.customModels (for Composer)")
        print("     - cursor.agent.customModels (for Agent)")
        print("     - cursor.inlineCompletion.customModels (for Inline)")
        print()
        print("Method 2: Direct JSON Edit")
        print("  1. Open: .cursor/settings.json")
        print("  2. Find the section (e.g., cursor.chat.customModels)")
        print("  3. Add your model JSON object")
        print("  4. Run this script to auto-add proper config")
        print()
        print("REQUIRED FIELDS FOR LOCAL MODELS:")
        print("  {")
        print('    "title": "Model Name",')
        print('    "name": "model-name",')
        print('    "provider": "ollama",')
        print('    "model": "model-id",')
        print('    "apiBase": "http://localhost:11434",')
        print('    "localOnly": true,          ← REQUIRED')
        print('    "skipProviderSelection": true,  ← REQUIRED')
        print('    "requiresApiKey": false,    ← REQUIRED')
        print('    "description": "... - LOCAL ONLY, NO API KEY"')
        print("  }")
        print()

        return True

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    sys.exit(0 if success else 1)


    success = main()