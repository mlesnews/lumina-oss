#!/usr/bin/env python3
"""
JARVIS Fix Cursor Ollama Model Format

Fixes the persistent "invalid model" error by ensuring Cursor model configuration
matches the exact format Cursor expects for Ollama models.

The issue: Cursor may be interpreting the custom model name "ULTRON" as the actual
model identifier instead of using the "model" field value "qwen2.5:72b".

Tags: #ULTRON #CURSOR-IDE #FIX #TROUBLESHOOTING
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISFixOllamaFormat")


class JARVISFixCursorOllamaFormat:
    """
    Fix Cursor Ollama model format to resolve "invalid model" errors
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent

        # Workspace settings
        self.workspace_settings = self.project_root / ".cursor" / "settings.json"

        # User settings (Windows: %APPDATA%\Cursor\User\settings.json)
        appdata = os.getenv("APPDATA")
        if appdata:
            self.user_settings = Path(appdata) / "Cursor" / "User" / "settings.json"
        else:
            home = Path.home()
            self.user_settings = home / ".config" / "Cursor" / "User" / "settings.json"

        self.logger = logger
        self.fixes_applied = []

        self.logger.info("✅ JARVIS Ollama Format Fixer initialized")
        self.logger.info(f"   Workspace: {self.workspace_settings}")
        self.logger.info(f"   User: {self.user_settings}")

    def get_correct_ollama_config(self) -> Dict[str, Any]:
        """
        Get the CORRECT format for Ollama models in Cursor.

        Key insight: Cursor may need the model identifier to be explicit,
        and the custom name should not conflict with model resolution.
        """
        return {
            "title": "ULTRON",
            "name": "ULTRON",
            "provider": "ollama",
            "model": "qwen2.5:72b",  # This is the actual Ollama model name
            "apiBase": "http://localhost:11434",  # Base URL, not full endpoint
            "contextLength": 32768,
            "description": "ULTRON Virtual Hybrid Cluster - qwen2.5:72b"
        }

    def fix_model_config(self, model_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fix a single model configuration to ensure correct format
        """
        fixed = model_config.copy()

        # Ensure required fields exist
        if "provider" not in fixed or fixed["provider"] != "ollama":
            fixed["provider"] = "ollama"
            self.fixes_applied.append("Set provider to 'ollama'")

        # Ensure model field exists and is valid
        if "model" not in fixed or not fixed["model"]:
            if "name" in fixed and fixed["name"]:
                # Use name as fallback, but this might be the issue
                fixed["model"] = fixed["name"]
                self.fixes_applied.append(f"Set model field from name: {fixed['model']}")
            else:
                fixed["model"] = "qwen2.5:72b"
                self.fixes_applied.append("Set default model: qwen2.5:72b")

        # Ensure apiBase is correct format (base URL, not full endpoint)
        if "apiBase" in fixed:
            api_base = fixed["apiBase"]
            # Remove /api/generate or /api/chat if present
            if "/api/" in api_base:
                fixed["apiBase"] = api_base.split("/api/")[0]
                self.fixes_applied.append(f"Fixed apiBase format: {fixed['apiBase']}")

        # Ensure apiBase exists
        if "apiBase" not in fixed:
            fixed["apiBase"] = "http://localhost:11434"
            self.fixes_applied.append("Added apiBase")

        # Remove any conflicting fields that might confuse Cursor
        # Some configs might have "endpoint" which conflicts with "apiBase"
        if "endpoint" in fixed and "apiBase" in fixed:
            # Keep apiBase, remove endpoint
            del fixed["endpoint"]
            self.fixes_applied.append("Removed conflicting 'endpoint' field")

        return fixed

    def fix_settings_file(self, settings_file: Path, is_user_settings: bool = False) -> Dict[str, Any]:
        """Fix model configurations in a settings file"""
        self.logger.info(f"🔧 Fixing settings: {settings_file}")

        if not settings_file.exists():
            self.logger.warning(f"⚠️  Settings file not found: {settings_file}")
            return {"success": False, "error": "File not found"}

        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        except Exception as e:
            self.logger.error(f"❌ Failed to read settings: {e}")
            return {"success": False, "error": str(e)}

        file_fixes = []

        # Fix all model configuration sections
        sections_to_fix = [
            "cursor.model.customModels",
            "cursor.chat.customModels",
            "cursor.composer.customModels",
            "cursor.agent.customModels"
        ]

        for section_path in sections_to_fix:
            parts = section_path.split(".")
            current = settings

            # Navigate to the section
            for part in parts[:-1]:
                if part not in current:
                    break
                current = current[part]
            else:
                # We're at the parent, now check for the last part
                section_name = parts[-1]
                if section_name in current and isinstance(current[section_name], list):
                    models = current[section_name]
                    for i, model in enumerate(models):
                        if isinstance(model, dict) and model.get("provider") == "ollama":
                            fixed_model = self.fix_model_config(model)
                            if fixed_model != model:
                                models[i] = fixed_model
                                file_fixes.append(f"Fixed model in {section_path}")

        # Write back if changes were made
        if file_fixes:
            try:
                with open(settings_file, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2, ensure_ascii=False)
                self.logger.info(f"✅ Fixed {len(file_fixes)} issues in {settings_file}")
                return {"success": True, "fixes": file_fixes, "file": str(settings_file)}
            except Exception as e:
                self.logger.error(f"❌ Failed to write settings: {e}")
                return {"success": False, "error": str(e)}
        else:
            self.logger.info(f"✅ No fixes needed in {settings_file}")
            return {"success": True, "fixes": [], "file": str(settings_file)}

    def verify_ollama_connection(self) -> Dict[str, Any]:
        """Verify Ollama is accessible and model exists"""
        import requests

        self.logger.info("🔍 Verifying Ollama connection...")

        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=3)
            if response.status_code == 200:
                data = response.json()
                models = [m["name"] for m in data.get("models", [])]

                has_qwen = any("qwen" in m.lower() for m in models)

                return {
                    "accessible": True,
                    "models": models,
                    "has_qwen": has_qwen,
                    "qwen_models": [m for m in models if "qwen" in m.lower()]
                }
            else:
                return {"accessible": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"accessible": False, "error": str(e)}

    def fix_all(self) -> Dict[str, Any]:
        try:
            """Fix both workspace and user settings"""
            self.logger.info("🚀 Starting comprehensive Ollama format fix...")

            results = {
                "timestamp": datetime.now().isoformat(),
                "workspace": None,
                "user": None,
                "ollama_check": None,
                "success": False
            }

            # Check Ollama first
            results["ollama_check"] = self.verify_ollama_connection()
            if not results["ollama_check"]["accessible"]:
                self.logger.warning("⚠️  Ollama not accessible - fixes may not work")

            # Fix workspace settings
            if self.workspace_settings.exists():
                results["workspace"] = self.fix_settings_file(self.workspace_settings, is_user_settings=False)
            else:
                results["workspace"] = {"success": False, "error": "File not found"}

            # Fix user settings
            if self.user_settings.exists():
                results["user"] = self.fix_settings_file(self.user_settings, is_user_settings=True)
            else:
                results["user"] = {"success": False, "error": "File not found"}
                self.logger.warning(f"⚠️  User settings not found: {self.user_settings}")

            # Overall success
            workspace_ok = results["workspace"] and results["workspace"].get("success", False)
            user_ok = results["user"] and results["user"].get("success", False)

            results["success"] = workspace_ok or user_ok

            if results["success"]:
                self.logger.info("✅ Format fixes complete!")
                self.logger.info("")
                self.logger.info("📋 Next Steps:")
                self.logger.info("   1. RESTART Cursor IDE completely")
                self.logger.info("   2. Test ULTRON in Chat")
                self.logger.info("   3. Check for 'invalid model' errors")
            else:
                self.logger.warning("⚠️  Some fixes failed")

            return results


        except Exception as e:
            self.logger.error(f"Error in fix_all: {e}", exc_info=True)
            raise
def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Fix Cursor Ollama model format")
        parser.add_argument("--verify-only", action="store_true", help="Only verify, don't fix")

        args = parser.parse_args()

        fixer = JARVISFixCursorOllamaFormat()

        if args.verify_only:
            ollama_check = fixer.verify_ollama_connection()
            print(json.dumps(ollama_check, indent=2, default=str))
        else:
            result = fixer.fix_all()
            print(json.dumps(result, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()