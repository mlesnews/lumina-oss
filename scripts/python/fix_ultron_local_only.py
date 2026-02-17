#!/usr/bin/env python3
"""
Fix ULTRON to be Local Only (No Bedrock/Cloud Routing)

Ensures ULTRON is configured as a LOCAL Ollama model that will NEVER
be routed to AWS Bedrock or any cloud provider that requires subscription/API keys.

Tags: #FIX #ULTRON #LOCAL #BEDROCK #OLLAMA
@JARVIS @MARVIN
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("FixUltronLocalOnly")

def fix_ultron_local_only(project_root: Optional[Path] = None) -> bool:
    try:
        """
        Fix ULTRON to be local-only and prevent Bedrock/cloud routing

        Args:
            project_root: Project root directory

        Returns:
            True if successful, False otherwise
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        settings_file = project_root / ".cursor" / "settings.json"

        if not settings_file.exists():
            logger.error(f"Settings file not found: {settings_file}")
            return False

        logger.info("=" * 80)
        logger.info("🔧 FIX ULTRON TO BE LOCAL ONLY (NO BEDROCK/CLOUD)")
        logger.info("=" * 80)
        logger.info("")

        # Read settings
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)

        changed = False

        # Fix ULTRON in all model sections
        model_sections = [
            "cursor.agent.customModels",
            "cursor.chat.customModels",
            "cursor.composer.customModels",
            "cursor.inlineCompletion.customModels"
        ]

        for section_key in model_sections:
            if section_key not in settings:
                continue

            models = settings[section_key]
            for model in models:
                if model.get("name") == "ULTRON" or model.get("title") == "ULTRON":
                    logger.info(f"Found ULTRON in {section_key}")

                    # CRITICAL: Set all flags to prevent cloud routing
                    required_changes = {
                        "localOnly": True,  # CRITICAL: Tells Cursor this is local
                        "skipProviderSelection": True,  # CRITICAL: Skip provider selection dialog
                        "provider": "ollama",  # CRITICAL: Explicitly set to ollama
                    }

                    # Remove any cloud-related fields
                    fields_to_remove = [
                        "apiKey",
                        "requiresApiKey",
                        "apiBase",  # Remove if it points to cloud
                        "authType",
                        "authHeader",
                        "subscriptionTier",
                        "requiresSubscription"
                    ]

                    for key, value in required_changes.items():
                        if model.get(key) != value:
                            logger.info(f"   Setting {key} = {value}")
                            model[key] = value
                            changed = True

                    for key in fields_to_remove:
                        if key in model:
                            # Only remove apiBase if it's not localhost
                            if key == "apiBase":
                                api_base = model.get(key, "")
                                if api_base and "localhost" not in api_base and "127.0.0.1" not in api_base:
                                    logger.info(f"   Removing {key} (points to cloud: {api_base})")
                                    del model[key]
                                    changed = True
                            else:
                                logger.info(f"   Removing {key} (cloud-related field)")
                                del model[key]
                                changed = True

                    # Ensure apiBase points to localhost (if present)
                    if "apiBase" in model:
                        api_base = model.get("apiBase", "")
                        if "localhost" not in api_base and "127.0.0.1" not in api_base:
                            logger.info(f"   Updating apiBase to localhost")
                            model["apiBase"] = "http://localhost:11434"
                            changed = True

                    # Ensure model field is set correctly
                    if "model" not in model or not model["model"]:
                        model["model"] = "qwen2.5:72b"
                        logger.info("   Setting model = qwen2.5:72b")
                        changed = True

                    logger.info(f"   ✅ ULTRON fixed in {section_key}")
                    logger.info("")

        # Ensure default model is ULTRON (if not already)
        if settings.get("cursor.agent.defaultModel") != "ULTRON":
            logger.info("Setting ULTRON as default agent model")
            settings["cursor.agent.defaultModel"] = "ULTRON"
            changed = True

        # Write back if changes were made
        if changed:
            logger.info("💾 Writing fixed settings...")
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ ULTRON FIXED - NOW LOCAL ONLY")
            logger.info("=" * 80)
            logger.info("")
            logger.info("📋 Changes Made:")
            logger.info("   ✅ Set localOnly: true (prevents cloud routing)")
            logger.info("   ✅ Set skipProviderSelection: true (skips provider dialog)")
            logger.info("   ✅ Set provider: 'ollama' (explicit local provider)")
            logger.info("   ✅ Removed cloud-related fields (apiKey, requiresApiKey, etc.)")
            logger.info("   ✅ Ensured apiBase points to localhost")
            logger.info("")
            logger.info("⚠️  IMPORTANT: Restart Cursor for changes to take effect!")
            logger.info("")
            return True
        else:
            logger.info("")
            logger.info("✅ ULTRON is already configured correctly (no changes needed)")
            logger.info("")
            return True


    except Exception as e:
        logger.error(f"Error in fix_ultron_local_only: {e}", exc_info=True)
        raise
def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Fix ULTRON to be Local Only")
        parser.add_argument("--project-root", help="Project root directory")

        args = parser.parse_args()

        project_root = Path(args.project_root) if args.project_root else None

        success = fix_ultron_local_only(project_root=project_root)

        sys.exit(0 if success else 1)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()