#!/usr/bin/env python3
"""
JARVIS: Check and Add SMOL LLM to Local AI Cluster

Checks for SMOL LLM availability and adds it to Cursor configuration.

Tags: #SMOL #SMOL_LLM #SMALL_MODEL #ULTRON #IRON_LEGION @JARVIS @LUMINA
"""

import json
import sys
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
settings_file = project_root / ".cursor" / "settings.json"

try:
    from lumina_core.logging import get_logger
    logger = get_logger("JARVISSmolLLM")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("JARVISSmolLLM")


def check_ollama_models(endpoint: str = "http://<NAS_PRIMARY_IP>:11434") -> List[str]:
    """Check available models on Ollama endpoint"""
    try:
        response = requests.get(f"{endpoint}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [m.get("name", "") for m in data.get("models", [])]
            return models
    except Exception as e:
        logger.error(f"Error checking Ollama models: {e}")
    return []


def check_smol_models_available(models: List[str]) -> Dict[str, bool]:
    """Check which SMOL models are available"""
    smol_variants = [
        "smollm",
        "smollm-135m",
        "smollm-360m",
        "smollm-1.7b",
        "smollm3",
        "smollm-3b"
    ]

    available = {}
    for variant in smol_variants:
        # Check exact match or partial match
        available[variant] = any(variant.lower() in model.lower() for model in models)

    return available


def add_smol_model_to_settings(settings: Dict[str, Any], model_name: str = "smollm-1.7b", endpoint: str = "http://<NAS_PRIMARY_IP>:11434") -> int:
    """Add SMOL LLM model to Cursor settings"""
    smol_config = {
        "title": "SMOL LLM",
        "name": "SMOL",
        "provider": "ollama",
        "model": model_name,
        "apiBase": endpoint,
        "contextLength": 8192,
        "description": f"SMOL LLM - Small efficient model ({model_name}) - LOCAL ONLY, NO API KEY",
        "localOnly": True,
        "skipProviderSelection": True
    }

    sections_to_update = [
        "cursor.agent.customModels",
        "cursor.chat.customModels",
        "cursor.composer.customModels",
        "cursor.inlineCompletion.customModels",
        "cursor.model.customModels"
    ]

    changes = 0

    for section_key in sections_to_update:
        if section_key not in settings:
            settings[section_key] = []

        models = settings[section_key]

        # Check if SMOL already exists
        existing = next((m for m in models if m.get("name") == "SMOL" or "SMOL" in (m.get("title", "") or m.get("name", "")).upper()), None)

        if existing:
            # Update existing
            existing.update(smol_config)
            changes += 1
            logger.info(f"Updated SMOL in {section_key}")
        else:
            # Add new
            models.append(smol_config)
            changes += 1
            logger.info(f"Added SMOL to {section_key}")

    return changes


def main():
    try:
        """Main workflow"""
        print("=" * 80)
        print("🤖 JARVIS: SMOL LLM CHECK & CONFIGURATION")
        print("=" * 80)
        print()

        # Check available models
        print("🔍 Checking available models on NAS Ollama...")
        print()

        nas_endpoint = "http://<NAS_PRIMARY_IP>:11434"
        available_models = check_ollama_models(nas_endpoint)

        print(f"📋 Available models on {nas_endpoint}:")
        for model in available_models:
            print(f"  - {model}")
        print()

        # Check for SMOL models
        print("🔍 Checking for SMOL LLM variants...")
        print()

        smol_available = check_smol_models_available(available_models)

        found_smol = False
        smol_model_name = None

        for variant, available in smol_available.items():
            status = "✅" if available else "❌"
            print(f"  {status} {variant}: {'Available' if available else 'Not available'}")
            if available and not found_smol:
                found_smol = True
                # Find the exact model name
                smol_model_name = next((m for m in available_models if variant.lower() in m.lower()), variant)

        print()

        if not found_smol:
            print("⚠️  No SMOL LLM models found on NAS Ollama")
            print()
            print("💡 To add SMOL LLM, you can pull one of these models:")
            print("   - smollm-135m-base (135M parameters - smallest)")
            print("   - smollm-360m-base (360M parameters)")
            print("   - smollm-1.7b (1.7B parameters - recommended)")
            print("   - smollm3 (3B parameters - larger)")
            print()
            print("   Example command (SSH to NAS):")
            print("   ollama pull smollm-1.7b")
            print()

            # Ask if user wants to add SMOL anyway (for future use)
            print("📝 Would you like to add SMOL LLM configuration anyway?")
            print("   (It will be ready when you pull the model)")
            print()

            # Default to adding smollm-1.7b as recommended
            smol_model_name = "smollm-1.7b"
            print(f"✅ Adding SMOL LLM configuration with model: {smol_model_name}")
            print()
        else:
            print(f"✅ Found SMOL LLM: {smol_model_name}")
            print()

        # Read settings
        if not settings_file.exists():
            print(f"❌ Settings file not found: {settings_file}")
            return 1

        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)

        # Add SMOL to settings
        print("🔧 Adding SMOL LLM to Cursor configuration...")
        print()

        changes = add_smol_model_to_settings(settings, smol_model_name, nas_endpoint)

        if changes > 0:
            # Write back
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

            print(f"✅ Added SMOL LLM to {changes} configuration section(s)!")
            print()

            print("📋 SMOL LLM Configuration:")
            print(f"  Model: {smol_model_name}")
            print(f"  Endpoint: {nas_endpoint}")
            print(f"  Provider: ollama")
            print(f"  Local Only: true")
            print()

            print("=" * 80)
            print("✅ CONFIGURATION COMPLETE")
            print("=" * 80)
            print()

            if not found_smol:
                print("📝 Next Steps:")
                print("   1. Pull SMOL LLM model on NAS:")
                print(f"      ollama pull {smol_model_name}")
                print("   2. Restart Cursor IDE")
                print("   3. Select 'SMOL' from model selector")
            else:
                print("📝 Next Steps:")
                print("   1. Restart Cursor IDE")
                print("   2. Select 'SMOL' from model selector")
            print()

            return 0
        else:
            print("✅ SMOL LLM already configured")
            return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())