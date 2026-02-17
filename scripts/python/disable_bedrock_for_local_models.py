#!/usr/bin/env python3
"""
Disable Bedrock Provider for Local Models

Ensures that local Ollama models (ULTRON, KAIJU) are NOT routed to AWS Bedrock.
This prevents "subscription/API key" errors for local models.

Tags: #FIX #BEDROCK #LOCAL #ULTRON #OLLAMA
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

logger = get_logger("DisableBedrockForLocal")

def disable_bedrock_for_local_models(project_root: Optional[Path] = None) -> bool:
    try:
        """
        Disable Bedrock provider routing for local models

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
        logger.info("🔧 DISABLE BEDROCK FOR LOCAL MODELS")
        logger.info("=" * 80)
        logger.info("")

        # Read settings
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)

        changed = False

        # Option 1: Disable Bedrock provider entirely (if you don't need it)
        # Uncomment these if you want to completely disable Bedrock:
        # bedrock_keys = [
        #     "cursor.agent.bedrockEnabled",
        #     "cursor.chat.bedrockEnabled",
        #     "cursor.composer.bedrockEnabled"
        # ]
        # for key in bedrock_keys:
        #     if settings.get(key, True):  # If enabled or not set
        #         settings[key] = False
        #         logger.info(f"   Disabled {key}")
        #         changed = True

        # Option 2: Ensure local models have explicit provider settings
        # This is the preferred approach - keep Bedrock available for cloud models,
        # but ensure local models explicitly use Ollama

        model_sections = [
            "cursor.agent.customModels",
            "cursor.chat.customModels",
            "cursor.composer.customModels",
            "cursor.inlineCompletion.customModels"
        ]

        local_models = ["ULTRON", "KAIJU", "qwen2.5:72b", "llama3", "llama3.1", "llama3.2"]

        for section_key in model_sections:
            if section_key not in settings:
                continue

            models = settings[section_key]
            for model in models:
                model_name = model.get("name", "")
                model_title = model.get("title", "")
                is_local = (
                    model.get("localOnly") or
                    model.get("provider") == "ollama" or
                    any(local in model_name for local in local_models) or
                    any(local in model_title for local in local_models) or
                    (model.get("apiBase", "").startswith("http://localhost") or 
                     model.get("apiBase", "").startswith("http://127.0.0.1"))
                )

                if is_local:
                    # Ensure local models explicitly prevent Bedrock routing
                    if not model.get("localOnly"):
                        model["localOnly"] = True
                        logger.info(f"   Set localOnly=true for {model_name or model_title} in {section_key}")
                        changed = True

                    if model.get("provider") != "ollama":
                        model["provider"] = "ollama"
                        logger.info(f"   Set provider=ollama for {model_name or model_title} in {section_key}")
                        changed = True

                    if not model.get("skipProviderSelection"):
                        model["skipProviderSelection"] = True
                        logger.info(f"   Set skipProviderSelection=true for {model_name or model_title} in {section_key}")
                        changed = True

                    # Remove any Bedrock-related fields
                    if "bedrock" in str(model).lower():
                        logger.info(f"   Warning: {model_name or model_title} may have Bedrock references")

        # Write back if changes were made
        if changed:
            logger.info("")
            logger.info("💾 Writing fixed settings...")
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ BEDROCK DISABLED FOR LOCAL MODELS")
            logger.info("=" * 80)
            logger.info("")
            logger.info("📋 Summary:")
            logger.info("   ✅ All local models now have localOnly: true")
            logger.info("   ✅ All local models now have provider: 'ollama'")
            logger.info("   ✅ All local models now have skipProviderSelection: true")
            logger.info("")
            logger.info("⚠️  IMPORTANT: Restart Cursor for changes to take effect!")
            logger.info("")
            return True
        else:
            logger.info("")
            logger.info("✅ All local models are already configured correctly")
            logger.info("")
            return True


    except Exception as e:
        logger.error(f"Error in disable_bedrock_for_local_models: {e}", exc_info=True)
        raise
def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Disable Bedrock for Local Models")
        parser.add_argument("--project-root", help="Project root directory")

        args = parser.parse_args()

        project_root = Path(args.project_root) if args.project_root else None

        success = disable_bedrock_for_local_models(project_root=project_root)

        sys.exit(0 if success else 1)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()