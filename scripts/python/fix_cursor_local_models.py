#!/usr/bin/env python3
"""
Fix Cursor IDE Local Model Configuration
Fixes "invalid model" errors for ULTRON and IRON LEGION in Cursor IDE

The issue: Cursor IDE validation rejects local models even when correctly configured.
Solution: Use correct format with /v1 endpoint and apiKey field.

Tags: #CURSOR_IDE #ULTRON #IRON_LEGION #LOCAL_MODELS #FIX @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_core.logging import get_logger
    logger = get_logger("FixCursorLocalModels")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("FixCursorLocalModels")


class CursorLocalModelFixer:
    """Fix Cursor IDE local model configuration"""

    def __init__(self):
        """Initialize fixer"""
        self.cursor_settings_path = Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "settings.json"
        self.config_path = project_root / "data" / "cursor_models" / "cursor_models_config.json"

    def fix_cursor_settings(self) -> bool:
        """Fix Cursor IDE settings.json with correct local model format"""
        logger.info("🔧 Fixing Cursor IDE settings.json...")

        if not self.cursor_settings_path.exists():
            logger.error(f"❌ Cursor settings not found: {self.cursor_settings_path}")
            return False

        try:
            # Read current settings
            with open(self.cursor_settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)

            # Get or create customModels array
            if "cursor.chat.customModels" not in settings:
                settings["cursor.chat.customModels"] = []
            if "cursor.composer.customModels" not in settings:
                settings["cursor.composer.customModels"] = []

            # Define correct model configurations
            ultron_models = [
                {
                    "name": "ULTRON",
                    "provider": "ollama",
                    "model": "qwen2.5:72b",
                    "apiBase": "http://localhost:11434/v1",
                    "apiKey": "ollama",
                    "contextLength": 32768
                },
                {
                    "name": "ultron",
                    "provider": "ollama",
                    "model": "qwen2.5:72b",
                    "apiBase": "http://localhost:11434/v1",
                    "apiKey": "ollama",
                    "contextLength": 32768
                }
            ]

            iron_legion_models = [
                {
                    "name": "IRON-LEGION",
                    "provider": "ollama",
                    "model": "codellama:13b",
                    "apiBase": "http://<NAS_IP>:3001/v1",
                    "apiKey": "ollama",
                    "contextLength": 8192
                },
                {
                    "name": "iron-legion",
                    "provider": "ollama",
                    "model": "codellama:13b",
                    "apiBase": "http://<NAS_IP>:3001/v1",
                    "apiKey": "ollama",
                    "contextLength": 8192
                }
            ]

            # Remove old ULTRON/IRON LEGION entries
            def remove_old_models(models_list: List[Dict]) -> List[Dict]:
                """Remove old ULTRON/IRON LEGION entries"""
                filtered = []
                for model in models_list:
                    name = model.get("name", "").lower()
                    if "ultron" not in name and "iron" not in name and "legion" not in name:
                        filtered.append(model)
                return filtered

            # Update chat models
            settings["cursor.chat.customModels"] = remove_old_models(settings["cursor.chat.customModels"])
            settings["cursor.chat.customModels"].extend(ultron_models)
            settings["cursor.chat.customModels"].extend(iron_legion_models)

            # Update composer models
            settings["cursor.composer.customModels"] = remove_old_models(settings["cursor.composer.customModels"])
            settings["cursor.composer.customModels"].extend(ultron_models)
            settings["cursor.composer.customModels"].extend(iron_legion_models)

            # Backup original
            backup_path = self.cursor_settings_path.with_suffix(".json.backup")
            with open(backup_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            logger.info(f"   📄 Backup saved: {backup_path}")

            # Write updated settings
            with open(self.cursor_settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

            logger.info("   ✅ Cursor settings.json updated")
            logger.info("")
            logger.info("   📋 Updated models:")
            logger.info("      - ULTRON (qwen2.5:72b) - http://localhost:11434/v1")
            logger.info("      - IRON-LEGION (codellama:13b) - http://<NAS_IP>:3001/v1")
            logger.info("")
            logger.info("   ⚠️  IMPORTANT: Reload Cursor IDE window (Ctrl+Shift+P → 'Reload Window') for changes to take effect")

            return True

        except Exception as e:
            logger.error(f"❌ Error fixing settings: {e}")
            return False

    def verify_ollama_connection(self) -> Dict[str, bool]:
        """Verify Ollama connections for both models"""
        logger.info("🔍 Verifying Ollama connections...")

        results = {
            "ultron_localhost": False,
            "iron_legion_kaiju": False
        }

        import urllib.request
        import urllib.error

        # Test ULTRON (localhost)
        try:
            url = "http://localhost:11434/api/tags"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read())
                models = [m.get("name", "") for m in data.get("models", [])]
                if any("qwen2.5:72b" in m for m in models):
                    results["ultron_localhost"] = True
                    logger.info("   ✅ ULTRON (localhost:11434) - Model available")
                else:
                    logger.warning("   ⚠️  ULTRON (localhost:11434) - Model not found")
        except Exception as e:
            logger.error(f"   ❌ ULTRON (localhost:11434) - Connection failed: {e}")

        # Test IRON LEGION (KAIJU)
        try:
            url = "http://<NAS_IP>:3001/api/tags"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read())
                models = [m.get("name", "") for m in data.get("models", [])]
                if any("codellama:13b" in m for m in models):
                    results["iron_legion_kaiju"] = True
                    logger.info("   ✅ IRON LEGION (<NAS_IP>:3001) - Model available")
                else:
                    logger.warning("   ⚠️  IRON LEGION (<NAS_IP>:3001) - Model not found")
        except Exception as e:
            logger.error(f"   ❌ IRON LEGION (<NAS_IP>:3001) - Connection failed: {e}")

        return results

    def print_troubleshooting(self):
        """Print troubleshooting steps"""
        logger.info("")
        logger.info("="*80)
        logger.info("🔧 TROUBLESHOOTING")
        logger.info("="*80)
        logger.info("")
        logger.info("If models still show as 'invalid' in Cursor IDE:")
        logger.info("")
        logger.info("1. Reload Cursor IDE Window:")
        logger.info("   - Press Ctrl+Shift+P → Type 'Reload Window' → Enter")
        logger.info("   - Or: View > Command Palette > 'Reload Window'")
        logger.info("")
        logger.info("2. Verify Ollama is Running:")
        logger.info("   - ULTRON: ollama list (should show qwen2.5:72b)")
        logger.info("   - IRON LEGION: curl http://<NAS_IP>:3001/api/tags")
        logger.info("")
        logger.info("3. Check Cursor IDE Subscription:")
        logger.info("   - Some Cursor plans restrict local model usage")
        logger.info("   - Verify your plan supports custom models")
        logger.info("")
        logger.info("4. Test API Directly:")
        logger.info("   - ULTRON: curl http://localhost:11434/v1/models")
        logger.info("   - IRON LEGION: curl http://<NAS_IP>:3001/v1/models")
        logger.info("")
        logger.info("5. Alternative: Use Continue Extension")
        logger.info("   - Continue extension may work better with local models")
        logger.info("   - Configure in .continue/config.json")
        logger.info("")
        logger.info("="*80)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Fix Cursor IDE Local Model Configuration"
    )
    parser.add_argument("--verify", action="store_true", help="Verify Ollama connections")
    parser.add_argument("--troubleshoot", action="store_true", help="Show troubleshooting steps")

    args = parser.parse_args()

    fixer = CursorLocalModelFixer()

    if args.troubleshoot:
        fixer.print_troubleshooting()
        return

    logger.info("="*80)
    logger.info("🔧 Fixing Cursor IDE Local Model Configuration")
    logger.info("="*80)
    logger.info("")

    # Fix settings
    success = fixer.fix_cursor_settings()

    if args.verify:
        logger.info("")
        fixer.verify_ollama_connection()

    if success:
        logger.info("")
        logger.info("="*80)
        logger.info("✅ Configuration Updated")
        logger.info("="*80)
        logger.info("")
        logger.info("⚠️  NEXT STEP: Reload Cursor IDE window (Ctrl+Shift+P → 'Reload Window')")
        logger.info("")
    else:
        logger.info("")
        logger.info("="*80)
        logger.info("❌ Configuration Update Failed")
        logger.info("="*80)
        logger.info("")
        fixer.print_troubleshooting()


if __name__ == "__main__":


    main()