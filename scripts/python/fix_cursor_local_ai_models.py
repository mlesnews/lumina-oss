#!/usr/bin/env python3
"""
Fix Cursor IDE Local AI Model Configuration
                    -LUM THE MODERN

Fixes "invalid model" errors by ensuring Cursor IDE uses LOCAL AI models
instead of cloud models that require subscription/API keys.

@SCOTTY @PEAK @LUMINA @DT -LUM_THE_MODERN
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("FixCursorLocalAI")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("FixCursorLocalAI")


class CursorLocalAIFixer:
    """
    Fixes Cursor IDE configuration to use LOCAL AI models only.
    Prevents "invalid model" errors from cloud models requiring subscription/API keys.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.cursor_settings_path = self.project_root / ".cursor" / "settings.json"
        self.local_ai_config_path = self.project_root / "config" / "local_ai_config.json"

        logger.info("=" * 80)
        logger.info("🔧 Fix Cursor IDE Local AI Model Configuration")
        logger.info("                    -LUM THE MODERN")
        logger.info("=" * 80)

    def get_local_ollama_endpoints(self) -> List[Dict[str, Any]]:
        """Get local Ollama endpoints from config"""
        endpoints = [
            {
                "title": "ULTRON (Local)",
                "name": "ULTRON",
                "provider": "ollama",
                "model": "qwen2.5:72b",
                "apiBase": "http://localhost:11434",
                "contextLength": 32768,
                "description": "ULTRON - Local Ollama (qwen2.5:72b) - LOCAL ONLY, NO API KEY",
                "localOnly": True,
                "skipProviderSelection": True,
                "requiresApiKey": False
            },
            {
                "title": "KAIJU (NAS)",
                "name": "KAIJU",
                "provider": "ollama",
                "model": "llama3.2:11b",
                "apiBase": "http://<NAS_PRIMARY_IP>:11434",
                "contextLength": 8192,
                "description": "KAIJU NAS Ollama (llama3.2:11b) - LOCAL ONLY, NO API KEY",
                "localOnly": True,
                "skipProviderSelection": True,
                "requiresApiKey": False
            },
            {
                "title": "SMOL LLM",
                "name": "SMOL",
                "provider": "ollama",
                "model": "smollm:135m",
                "apiBase": "http://localhost:11434",
                "contextLength": 8192,
                "description": "SMOL LLM - Small efficient model - LOCAL ONLY, NO API KEY",
                "localOnly": True,
                "skipProviderSelection": True,
                "requiresApiKey": False
            }
        ]

        # Try to load from local_ai_config.json
        if self.local_ai_config_path.exists():
            try:
                with open(self.local_ai_config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if "base_url" in config:
                        endpoints[0]["apiBase"] = config["base_url"]
                    if "model" in config:
                        endpoints[0]["model"] = config["model"]
            except Exception as e:
                logger.warning(f"Could not load local_ai_config.json: {e}")

        return endpoints

    def fix_cursor_settings(self) -> bool:
        """Fix Cursor settings.json to use local models only"""
        logger.info("\n🔧 Fixing Cursor settings.json...")

        if not self.cursor_settings_path.exists():
            logger.error(f"❌ Cursor settings not found: {self.cursor_settings_path}")
            return False

        try:
            # Read current settings
            with open(self.cursor_settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)

            # Get local models
            local_models = self.get_local_ollama_endpoints()

            # Fix agent models
            if "cursor.agent.customModels" not in settings:
                settings["cursor.agent.customModels"] = []

            # Replace with local models only
            settings["cursor.agent.customModels"] = local_models
            settings["cursor.agent.defaultModel"] = "ULTRON"

            # Ensure local-only enforcement
            settings["cursor.agent.localOnly"] = True
            settings["cursor.agent.requireApiKey"] = False
            settings["cursor.agent.blockCloudModels"] = True

            # Fix chat models
            if "cursor.chat.customModels" not in settings:
                settings["cursor.chat.customModels"] = []

            settings["cursor.chat.customModels"] = local_models
            settings["cursor.chat.defaultModel"] = "ULTRON"
            settings["cursor.chat.localOnly"] = True
            settings["cursor.chat.blockCloudModels"] = True

            # Fix composer models
            if "cursor.composer.customModels" not in settings:
                settings["cursor.composer.customModels"] = []

            settings["cursor.composer.customModels"] = local_models
            settings["cursor.composer.defaultModel"] = "ULTRON"
            settings["cursor.composer.localOnly"] = True
            settings["cursor.composer.blockCloudModels"] = True

            # Fix inline completion models
            if "cursor.inlineCompletion.customModels" not in settings:
                settings["cursor.inlineCompletion.customModels"] = []

            settings["cursor.inlineCompletion.customModels"] = local_models
            settings["cursor.inlineCompletion.defaultModel"] = "ULTRON"
            settings["cursor.inlineCompletion.localOnly"] = True

            # Add enforcement settings
            if "lumina" not in settings:
                settings["lumina"] = {}

            settings["lumina"]["local_first_enforced"] = True
            settings["lumina"]["cloud_requires_approval"] = True
            settings["lumina"]["block_cloud_models"] = True
            settings["lumina"]["enforcement_strict"] = True

            # Add comment
            settings["_comment_local_ai_fix"] = "FIXED: All models configured to use LOCAL AI only. Cloud models blocked. No API keys required."

            # Write back
            with open(self.cursor_settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

            logger.info("✅ Cursor settings.json fixed")
            logger.info(f"   - Agent models: {len(local_models)} local models configured")
            logger.info(f"   - Chat models: {len(local_models)} local models configured")
            logger.info(f"   - Composer models: {len(local_models)} local models configured")
            logger.info(f"   - Cloud models: BLOCKED")
            logger.info(f"   - Default model: ULTRON (local)")

            return True

        except Exception as e:
            logger.error(f"❌ Error fixing Cursor settings: {e}")
            return False

    def create_cursor_user_settings_override(self) -> bool:
        try:
            """Create instructions for user settings override"""
            logger.info("\n📝 Creating user settings override instructions...")

            user_settings_instructions = {
                "instructions": "Add these settings to Cursor User Settings (Cmd/Ctrl+,) > Settings > Features",
                "settings": {
                    "cursor.chat.defaultModel": "ULTRON",
                    "cursor.composer.defaultModel": "ULTRON",
                    "cursor.agent.defaultModel": "ULTRON",
                    "cursor.inlineCompletion.defaultModel": "ULTRON",
                    "cursor.model.defaultModel": "ULTRON",
                    "cursor.chat.localOnly": True,
                    "cursor.composer.localOnly": True,
                    "cursor.agent.localOnly": True,
                    "cursor.inlineCompletion.localOnly": True,
                    "cursor.chat.blockCloudModels": True,
                    "cursor.composer.blockCloudModels": True,
                    "cursor.agent.blockCloudModels": True
                },
                "note": "These settings ensure LOCAL AI models are used by default and cloud models are blocked"
            }

            instructions_path = self.project_root / "docs" / "operations" / "CURSOR_LOCAL_AI_SETUP.md"
            instructions_path.parent.mkdir(parents=True, exist_ok=True)

            with open(instructions_path, 'w', encoding='utf-8') as f:
                f.write("# Cursor IDE Local AI Setup Instructions\n\n")
                f.write("## Quick Fix\n\n")
                f.write("1. Open Cursor Settings (Cmd/Ctrl+,)\n")
                f.write("2. Search for 'model' or 'agent'\n")
                f.write("3. Set default model to 'ULTRON' for:\n")
                f.write("   - Chat\n")
                f.write("   - Composer\n")
                f.write("   - Agent\n")
                f.write("   - Inline Completion\n")
                f.write("4. Verify 'ULTRON' is selected in model selector (top-right)\n\n")
                f.write("## JSON Settings\n\n")
                f.write("Add to User Settings JSON:\n\n")
                f.write("```json\n")
                f.write(json.dumps(user_settings_instructions["settings"], indent=2))
                f.write("\n```\n")

            logger.info(f"✅ Instructions created: {instructions_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error in create_cursor_user_settings_override: {e}", exc_info=True)
            raise
    def verify_local_models_accessible(self) -> bool:
        """Verify local Ollama endpoints are accessible"""
        logger.info("\n🔍 Verifying local Ollama endpoints...")

        import requests

        endpoints_to_check = [
            ("http://localhost:11434/api/tags", "Local Ollama"),
            ("http://<NAS_PRIMARY_IP>:11434/api/tags", "KAIJU NAS Ollama")
        ]

        all_accessible = True
        for endpoint, name in endpoints_to_check:
            try:
                response = requests.get(endpoint, timeout=5)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    logger.info(f"   ✅ {name}: Accessible ({len(models)} models available)")
                else:
                    logger.warning(f"   ⚠️  {name}: HTTP {response.status_code}")
                    all_accessible = False
            except Exception as e:
                logger.warning(f"   ⚠️  {name}: Not accessible ({e})")
                all_accessible = False

        return all_accessible

    def fix_all(self) -> Dict[str, Any]:
        """Fix all Cursor IDE local AI model issues"""
        logger.info("\n" + "=" * 80)
        logger.info("🔧 FIXING ALL CURSOR IDE LOCAL AI MODEL ISSUES")
        logger.info("=" * 80)

        results = {
            "settings_fixed": False,
            "instructions_created": False,
            "endpoints_accessible": False,
            "all_fixed": False
        }

        # Fix settings
        results["settings_fixed"] = self.fix_cursor_settings()

        # Create instructions
        results["instructions_created"] = self.create_cursor_user_settings_override()

        # Verify endpoints
        results["endpoints_accessible"] = self.verify_local_models_accessible()

        # Overall status
        results["all_fixed"] = results["settings_fixed"] and results["instructions_created"]

        logger.info("\n" + "=" * 80)
        logger.info("📊 FIX RESULTS")
        logger.info("=" * 80)
        logger.info(f"   Settings Fixed: {'✅' if results['settings_fixed'] else '❌'}")
        logger.info(f"   Instructions Created: {'✅' if results['instructions_created'] else '❌'}")
        logger.info(f"   Endpoints Accessible: {'✅' if results['endpoints_accessible'] else '⚠️'}")
        logger.info(f"   All Fixed: {'✅' if results['all_fixed'] else '⚠️'}")
        logger.info("=" * 80)

        if results["all_fixed"]:
            logger.info("\n✅ ALL CURSOR IDE LOCAL AI MODEL ISSUES FIXED!")
            logger.info("\n📝 NEXT STEPS:")
            logger.info("   1. Restart Cursor IDE")
            logger.info("   2. Verify 'ULTRON' is selected in model selector (top-right)")
            logger.info("   3. Check Settings > Features > Agent > Default Model = 'ULTRON'")
            logger.info("   4. Test agent mode - should use local ULTRON model")
        else:
            logger.warning("\n⚠️  Some issues remain. Check logs above.")

        return results


def main():
    """CLI interface"""
    fixer = CursorLocalAIFixer()
    results = fixer.fix_all()

    if results["all_fixed"]:
        print("\n✅ ALL FIXED!")
        sys.exit(0)
    else:
        print("\n⚠️  Some issues remain. Check logs.")
        sys.exit(1)


if __name__ == "__main__":


    main()