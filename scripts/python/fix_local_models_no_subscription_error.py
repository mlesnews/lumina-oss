#!/usr/bin/env python3
"""
Fix Local Models - Remove Subscription/API Key Errors (PERMANENT FIX)

PERSISTENT ISSUE: Local models (ULTRON, KAIJU) getting "invalid model" errors
with subscription plan and API key messages - even though they're LOCAL models.

This script PERMANENTLY fixes this by:
1. Ensuring all local models explicitly bypass cloud validation
2. Removing any subscription/API key requirements
3. Adding explicit "noProvider" flags
4. Setting models to skip all cloud provider checks

Tags: #FIX #LOCAL_MODELS #SUBSCRIPTION_ERROR #PERMANENT #ULTRON #KAIJU
@JARVIS @MARVIN @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("FixLocalModelsNoSubscription")

def fix_local_model(model: Dict[str, Any], model_name: str, section: str) -> bool:
    """
    Fix a single local model to remove subscription/API key errors

    Returns True if changes were made
    """
    changed = False

    # CRITICAL: Set all flags to prevent cloud validation
    required_flags = {
        "localOnly": True,  # Tells Cursor this is local - NO cloud validation
        "skipProviderSelection": True,  # Skip provider selection (prevents cloud routing)
        "provider": "ollama",  # Explicitly set to ollama (local provider)
        "noProvider": True,  # NEW: Explicitly tell Cursor NO provider validation needed
        "bypassCloudValidation": True,  # NEW: Bypass all cloud validation
        "requiresApiKey": False,  # CRITICAL: No API key needed (it's local!)
        "requiresSubscription": False,  # CRITICAL: No subscription needed (it's local!)
    }

    for key, value in required_flags.items():
        if model.get(key) != value:
            logger.info(f"   Setting {key} = {value}")
            model[key] = value
            changed = True

    # CRITICAL: Remove ALL cloud-related fields that cause validation
    fields_to_remove = [
        "apiKey",
        "authType",
        "authHeader",
        "subscriptionTier",
        "subscriptionPlan",
        "bedrockEnabled",
        "bedrockRegion",
        "awsRegion",
        "cloudProvider",
        "providerType",  # Remove if it's set to cloud
    ]

    for key in fields_to_remove:
        if key in model:
            logger.info(f"   Removing {key} (cloud-related field)")
            del model[key]
            changed = True

    # Ensure apiBase is local (localhost or local IP)
    if "apiBase" in model:
        api_base = model.get("apiBase", "")
        if api_base:
            # If it's not localhost or local IP, fix it
            if "localhost" not in api_base and "127.0.0.1" not in api_base and "<NAS_PRIMARY_IP>" not in api_base:
                logger.warning(f"   ⚠️  apiBase points to non-local: {api_base}")
                # Don't change it if it's KAIJU (<NAS_PRIMARY_IP> is local NAS)
                if "<NAS_PRIMARY_IP>" not in api_base:
                    logger.info(f"   Updating apiBase to localhost")
                    model["apiBase"] = "http://localhost:11434"
                    changed = True

    # Ensure model name is set
    if "model" not in model or not model.get("model"):
        if "qwen" in model_name.lower() or "ultron" in model_name.lower():
            model["model"] = "qwen2.5:72b"
            logger.info("   Setting model = qwen2.5:72b")
            changed = True
        elif "llama" in model_name.lower() or "kaiju" in model_name.lower():
            model["model"] = "llama3.2:3b"
            logger.info("   Setting model = llama3.2:3b")
            changed = True

    return changed

def fix_all_local_models(project_root: Path) -> bool:
    """
    Fix ALL local models in Cursor settings to remove subscription errors

    Returns True if any changes were made
    """
    settings_file = project_root / ".cursor" / "settings.json"

    if not settings_file.exists():
        logger.error(f"❌ Settings file not found: {settings_file}")
        return False

    logger.info("=" * 80)
    logger.info("🔧 FIX LOCAL MODELS - REMOVE SUBSCRIPTION/API KEY ERRORS")
    logger.info("=" * 80)
    logger.info("")

    # Read settings
    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)
    except Exception as e:
        logger.error(f"❌ Failed to read settings: {e}")
        return False

    changed = False

    # All model sections to fix
    model_sections = [
        "cursor.model.customModels",
        "cursor.agent.customModels",
        "cursor.chat.customModels",
        "cursor.composer.customModels",
        "cursor.inlineCompletion.customModels",
    ]

    # Local model identifiers
    local_model_names = ["ULTRON", "KAIJU", "qwen2.5:72b", "llama3.2:3b", "llama3", "codellama"]

    for section_key in model_sections:
        if section_key not in settings:
            continue

        models = settings[section_key]
        if not isinstance(models, list):
            continue

        logger.info(f"📋 Checking {section_key}...")

        for model in models:
            if not isinstance(model, dict):
                continue

            model_name = model.get("name", "") or model.get("title", "")

            # Check if this is a local model
            is_local = (
                model.get("localOnly") or
                model.get("provider") == "ollama" or
                any(local in str(model_name).lower() for local in local_model_names) or
                (model.get("apiBase", "").startswith("http://localhost")) or
                (model.get("apiBase", "").startswith("http://127.0.0.1")) or
                (model.get("apiBase", "").startswith("http://<NAS_PRIMARY_IP>"))  # KAIJU NAS
            )

            if is_local:
                logger.info(f"   🔧 Fixing local model: {model_name}")
                if fix_local_model(model, model_name, section_key):
                    changed = True
                    logger.info(f"   ✅ Fixed {model_name} in {section_key}")
                else:
                    logger.info(f"   ✅ {model_name} already correct")

    # Add global settings to prevent cloud validation
    if "cursor.model" not in settings:
        settings["cursor.model"] = {}

    # Add global flags to prevent cloud validation for all local models
    global_flags = {
        "disableCloudValidation": True,
        "preferLocalModels": True,
        "skipProviderValidation": True,
    }

    for key, value in global_flags.items():
        if settings["cursor.model"].get(key) != value:
            settings["cursor.model"][key] = value
            changed = True
            logger.info(f"   Setting global flag: {key} = {value}")

    # Write back if changes were made
    if changed:
        logger.info("")
        logger.info("💾 Writing fixed settings...")
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ LOCAL MODELS FIXED - NO SUBSCRIPTION ERRORS")
            logger.info("=" * 80)
            logger.info("")
            logger.info("📋 Changes Made:")
            logger.info("   ✅ Set localOnly: true (prevents cloud validation)")
            logger.info("   ✅ Set skipProviderSelection: true (skips provider dialog)")
            logger.info("   ✅ Set provider: 'ollama' (explicit local provider)")
            logger.info("   ✅ Set noProvider: true (no provider validation)")
            logger.info("   ✅ Set bypassCloudValidation: true (bypass all cloud checks)")
            logger.info("   ✅ Set requiresApiKey: false (no API key needed)")
            logger.info("   ✅ Set requiresSubscription: false (no subscription needed)")
            logger.info("   ✅ Removed all cloud-related fields")
            logger.info("")
            logger.info("⚠️  IMPORTANT: Restart Cursor for changes to take effect!")
            logger.info("")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to write settings: {e}")
            return False
    else:
        logger.info("")
        logger.info("✅ All local models are already configured correctly")
        logger.info("")
        return True

def main():
    """Main execution"""
    success = fix_all_local_models(project_root)
    sys.exit(0 if success else 1)

if __name__ == "__main__":


    main()