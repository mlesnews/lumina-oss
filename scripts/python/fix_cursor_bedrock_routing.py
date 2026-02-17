#!/usr/bin/env python3
"""
Fix Cursor Bedrock/ULTRON Routing Issue
Prevents Bedrock from trying to handle local ULTRON models

Tags: #JARVIS #FIX #CURSOR #BEDROCK #ULTRON @JARVIS @DOIT
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("FixCursorBedrockRouting")

# Cursor settings paths (multiple possible locations)
CURSOR_SETTINGS_PATHS = [
    Path.home() / ".cursor" / "settings.json",
    Path.home() / ".cursor" / "User" / "settings.json",
    Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "settings.json",
    Path.home() / "Library" / "Application Support" / "Cursor" / "User" / "settings.json",
]


def find_cursor_settings() -> Optional[Path]:
    try:
        """Find Cursor settings.json file"""
        for path in CURSOR_SETTINGS_PATHS:
            if path.exists():
                logger.info(f"✅ Found Cursor settings: {path}")
                return path

        logger.warning("⚠️  Cursor settings.json not found in standard locations")
        return None


    except Exception as e:
        logger.error(f"Error in find_cursor_settings: {e}", exc_info=True)
        raise
def load_settings(settings_path: Path) -> Dict[str, Any]:
    """Load Cursor settings"""
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        logger.info(f"✅ Loaded settings from {settings_path}")
        return settings
    except Exception as e:
        logger.error(f"❌ Failed to load settings: {e}")
        return {}


def save_settings(settings_path: Path, settings: Dict[str, Any]) -> bool:
    """Save Cursor settings"""
    try:
        # Create backup
        backup_path = settings_path.with_suffix('.json.backup')
        if settings_path.exists():
            import shutil
            shutil.copy2(settings_path, backup_path)
            logger.info(f"📦 Backup created: {backup_path}")

        # Write settings
        with open(settings_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)

        logger.info(f"✅ Settings saved to {settings_path}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to save settings: {e}")
        return False


def fix_bedrock_routing(settings: Dict[str, Any]) -> tuple[Dict[str, Any], bool]:
    """
    Fix Bedrock routing issues

    Returns:
        (updated_settings, changes_made)
    """
    changes_made = False

    # Local models that should NEVER go to Bedrock
    LOCAL_MODELS = [
        "ULTRON",
        "ultron",
        "qwen2.5:72b",
        "qwen2.5",
        "llama3",
        "llama3.2",
        "codellama",
        "mistral",
        "mixtral",
        "gemma",
        "ollama"
    ]

    logger.info("🔧 Fixing Cursor model routing...")

    # Fix default models - ensure they route to Ollama, not Bedrock
    model_settings = [
        "cursor.chat.defaultModel",
        "cursor.composer.defaultModel", 
        "cursor.inlineCompletion.defaultModel",
        "cursor.chat.model",
        "cursor.composer.model",
    ]

    for setting_key in model_settings:
        current_value = settings.get(setting_key, "")

        # If it's a local model but being sent to Bedrock, fix it
        if any(local_model in str(current_value).lower() for local_model in LOCAL_MODELS):
            if "bedrock" in str(current_value).lower() or "aws" in str(current_value).lower():
                logger.warning(f"⚠️  {setting_key} is routing local model through Bedrock!")
                # Force it to use Ollama endpoint
                settings[setting_key] = "qwen2.5:72b"  # Explicit local model
                changes_made = True
                logger.info(f"   ✅ Fixed: {setting_key} → qwen2.5:72b (local)")

    # Disable Bedrock for local models
    if "cursor.chat" not in settings:
        settings["cursor.chat"] = {}

    if "cursor.composer" not in settings:
        settings["cursor.composer"] = {}

    # Ensure Ollama is enabled and prioritized
    settings.setdefault("cursor.chat", {})["enableOllama"] = True
    settings.setdefault("cursor.composer", {})["enableOllama"] = True

    # Set Ollama endpoint
    settings.setdefault("cursor.chat", {})["ollamaEndpoint"] = "http://localhost:11434"
    settings.setdefault("cursor.composer", {})["ollamaEndpoint"] = "http://localhost:11434"

    # Disable Bedrock provider for local-first routing
    if "awsBedrock" in settings:
        bedrock_settings = settings["awsBedrock"]
        if bedrock_settings.get("enabled", False):
            logger.warning("⚠️  Bedrock is enabled - ensuring it doesn't handle local models")
            # Add exclusion list
            bedrock_settings["excludeModels"] = LOCAL_MODELS
            bedrock_settings["localFirst"] = True
            changes_made = True
            logger.info("   ✅ Added local model exclusions to Bedrock")

    # Ensure local-first enforcement
    if "lumina" not in settings:
        settings["lumina"] = {}

    settings["lumina"]["localFirstEnforced"] = True
    settings["lumina"]["cloudRequiresApproval"] = True
    settings["lumina"]["preventBedrockLocalModels"] = True

    changes_made = True
    logger.info("   ✅ Local-first enforcement enabled")

    return settings, changes_made


def main():
    """Main fix function"""
    logger.info("=" * 80)
    logger.info("🔧 FIXING CURSOR BEDROCK/ULTRON ROUTING ISSUE")
    logger.info("=" * 80)
    logger.info("")

    # Find settings
    settings_path = find_cursor_settings()
    if not settings_path:
        logger.error("❌ Cannot find Cursor settings.json")
        logger.info("")
        logger.info("💡 Please ensure Cursor is installed and settings exist")
        return 1

    # Load settings
    settings = load_settings(settings_path)
    if not settings:
        logger.error("❌ Failed to load settings")
        return 1

    # Fix routing
    updated_settings, changes_made = fix_bedrock_routing(settings)

    if not changes_made:
        logger.info("✅ No changes needed - routing is correct")
        return 0

    # Save settings
    if save_settings(settings_path, updated_settings):
        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ CURSOR ROUTING FIXED!")
        logger.info("=" * 80)
        logger.info("")
        logger.info("📋 Changes applied:")
        logger.info("   1. ✅ Local models (ULTRON/qwen2.5:72b) route to Ollama")
        logger.info("   2. ✅ Bedrock excluded from handling local models")
        logger.info("   3. ✅ Local-first enforcement enabled")
        logger.info("   4. ✅ Ollama endpoint configured")
        logger.info("")
        logger.info("💡 Restart Cursor for changes to take effect")
        return 0
    else:
        logger.error("❌ Failed to save settings")
        return 1


if __name__ == "__main__":


    sys.exit(main())