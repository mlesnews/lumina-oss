#!/usr/bin/env python3
"""
JARVIS Fix Cursor Model Name Issue - ROOT CAUSE FIX

The persistent "invalid model" error is caused by Cursor using the "name" field
("ULTRON") as the model identifier instead of the "model" field ("qwen2.5:72b").

FIX: Set the "name" field to match the actual Ollama model name so Cursor sends
the correct model identifier to Ollama.

Tags: #ULTRON #CURSOR-IDE #ROOT-CAUSE-FIX #TROUBLESHOOTING
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, Any
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

logger = get_logger("JARVISFixModelName")


class JARVISFixCursorModelName:
    """
    Fix the root cause: Cursor using 'name' field instead of 'model' field
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.workspace_settings = self.project_root / ".cursor" / "settings.json"

        appdata = os.getenv("APPDATA")
        if appdata:
            self.user_settings = Path(appdata) / "Cursor" / "User" / "settings.json"
        else:
            home = Path.home()
            self.user_settings = home / ".config" / "Cursor" / "User" / "settings.json"

        self.logger = logger
        self.fixes_applied = []

    def fix_model_name_issue(self, settings_file: Path) -> Dict[str, Any]:
        """
        Fix model configurations by ensuring 'name' matches 'model' field value.

        ROOT CAUSE: Cursor may be using 'name' field as the model identifier
        when calling Ollama. If 'name' is "ULTRON" but Ollama expects "qwen2.5:72b",
        Cursor will send "ULTRON" to Ollama, causing "invalid model" error.

        SOLUTION: Set 'name' to match the actual Ollama model name.
        """
        self.logger.info(f"🔧 Fixing model name issue in: {settings_file}")

        if not settings_file.exists():
            return {"success": False, "error": "File not found"}

        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        except Exception as e:
            return {"success": False, "error": str(e)}

        file_fixes = []
        sections_fixed = []

        # Fix all model sections
        sections = [
            ("cursor.model", "customModels"),
            ("cursor.chat", "customModels"),
            ("cursor.composer", "customModels"),
            ("cursor.agent", "customModels")
        ]

        for parent_key, child_key in sections:
            try:
                # Navigate to section
                current = settings
                for key in parent_key.split("."):
                    if key in current:
                        current = current[key]
                    else:
                        break
                else:
                    if child_key in current and isinstance(current[child_key], list):
                        models = current[child_key]
                        for i, model in enumerate(models):
                            if isinstance(model, dict) and model.get("provider") == "ollama":
                                original_name = model.get("name", "")
                                model_name = model.get("model", "")

                                # CRITICAL FIX: If name doesn't match model, fix it
                                if model_name and original_name != model_name:
                                    # Keep title as the display name, but set name to match model
                                    model["name"] = model_name
                                    model["title"] = original_name if original_name else model_name

                                    fix_msg = f"Fixed {parent_key}.{child_key}[{i}]: name '{original_name}' -> '{model_name}'"
                                    file_fixes.append(fix_msg)
                                    sections_fixed.append(f"{parent_key}.{child_key}")
                                    self.logger.info(f"  ✅ {fix_msg}")
            except Exception as e:
                self.logger.warning(f"  ⚠️  Error fixing {parent_key}.{child_key}: {e}")

        # Write back if changes were made
        if file_fixes:
            try:
                with open(settings_file, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2, ensure_ascii=False)
                self.logger.info(f"✅ Applied {len(file_fixes)} fixes to {settings_file}")
                return {
                    "success": True,
                    "fixes": file_fixes,
                    "sections_fixed": list(set(sections_fixed)),
                    "file": str(settings_file)
                }
            except Exception as e:
                return {"success": False, "error": str(e)}
        else:
            self.logger.info(f"✅ No fixes needed in {settings_file}")
            return {"success": True, "fixes": [], "file": str(settings_file)}

    def fix_all(self) -> Dict[str, Any]:
        try:
            """Fix both workspace and user settings"""
            self.logger.info("="*80)
            self.logger.info("JARVIS: ROOT CAUSE FIX - Model Name Issue")
            self.logger.info("="*80)
            self.logger.info("")
            self.logger.info("ISSUE: Cursor using 'name' field ('ULTRON') as model identifier")
            self.logger.info("FIX: Set 'name' to match 'model' field ('qwen2.5:72b')")
            self.logger.info("")

            results = {
                "timestamp": datetime.now().isoformat(),
                "workspace": None,
                "user": None,
                "success": False
            }

            # Fix workspace
            if self.workspace_settings.exists():
                results["workspace"] = self.fix_model_name_issue(self.workspace_settings)
            else:
                results["workspace"] = {"success": False, "error": "File not found"}

            # Fix user settings
            if self.user_settings.exists():
                results["user"] = self.fix_model_name_issue(self.user_settings)
            else:
                results["user"] = {"success": False, "error": "File not found"}

            results["success"] = (
                (results["workspace"] and results["workspace"].get("success")) or
                (results["user"] and results["user"].get("success"))
            )

            self.logger.info("")
            self.logger.info("="*80)
            if results["success"]:
                self.logger.info("✅ ROOT CAUSE FIX COMPLETE")
                self.logger.info("")
                self.logger.info("📋 Next Steps:")
                self.logger.info("   1. RESTART Cursor IDE completely")
                self.logger.info("   2. ULTRON should now work (name matches model)")
                self.logger.info("   3. If still errors, check memory (72B model needs 44.8 GiB)")
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

        parser = argparse.ArgumentParser(description="Fix Cursor model name issue (root cause)")
        args = parser.parse_args()

        fixer = JARVISFixCursorModelName()
        result = fixer.fix_all()

        print("\n" + "="*80)
        print("FIX RESULTS")
        print("="*80)
        print(json.dumps(result, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()