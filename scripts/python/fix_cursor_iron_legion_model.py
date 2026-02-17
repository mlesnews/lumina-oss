#!/usr/bin/env python3
"""
Fix Cursor IDE "llama3.2:3b" Invalid Model Error

This script:
1. Finds Cursor settings files
2. Checks for "llama3.2:3b" or "ULTRON" used as model names
3. Fixes incorrect configurations
4. Provides reboot instructions
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
import platform

class CursorSettingsFixer:
    """Fix Cursor IDE model configuration errors"""

    def __init__(self):
        self.system = platform.system()
        self.fixes_applied = []
        self.errors_found = []

    def find_cursor_settings_paths(self) -> List[Path]:
        try:
            """Find all possible Cursor settings file locations"""
            paths = []

            # Workspace settings
            workspace_root = Path(__file__).parent.parent.parent
            workspace_cursor = workspace_root / ".cursor" / "settings.json"
            if workspace_cursor.exists():
                paths.append(workspace_cursor)

            # User settings (Windows)
            if self.system == "Windows":
                appdata = os.getenv("APPDATA")
                if appdata:
                    user_settings = Path(appdata) / "Cursor" / "User" / "settings.json"
                    if user_settings.exists():
                        paths.append(user_settings)

            # User settings (macOS)
            elif self.system == "Darwin":
                home = Path.home()
                user_settings = home / "Library" / "Application Support" / "Cursor" / "User" / "settings.json"
                if user_settings.exists():
                    paths.append(user_settings)

            # User settings (Linux)
            elif self.system == "Linux":
                home = Path.home()
                user_settings = home / ".config" / "Cursor" / "User" / "settings.json"
                if user_settings.exists():
                    paths.append(user_settings)

            return paths

        except Exception as e:
            self.logger.error(f"Error in find_cursor_settings_paths: {e}", exc_info=True)
            raise
    def check_settings_file(self, file_path: Path) -> Dict[str, any]:
        """Check a settings file for incorrect model configurations"""
        issues = {
            "file": str(file_path),
            "exists": file_path.exists(),
            "errors": [],
            "warnings": [],
            "fixed": False
        }

        if not file_path.exists():
            return issues

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                settings = json.loads(content)
        except Exception as e:
            issues["errors"].append(f"Failed to read/parse file: {e}")
            return issues

        # Check for "llama3.2:3b" as model name
        issues.update(self._check_for_iron_legion_model(settings, file_path))

        # Check for "ULTRON" as model name (ULTRON is a cluster, not a model)
        issues.update(self._check_for_ultron_model(settings, file_path))

        return issues

    def _check_for_iron_legion_model(self, settings: dict, file_path: Path) -> dict:
        """Check for "llama3.2:3b" used as a model name"""
        result = {"errors": [], "warnings": []}

        def check_dict(obj, path=""):
            if isinstance(obj, dict):
                # Check if "llama3.2:3b" is used as a model name
                if "model" in obj and obj["model"] == "llama3.2:3b":
                    result["errors"].append(
                        f"Found 'llama3.2:3b' as model name at {path}.model - "
                        f"Should be an actual Ollama model like 'qwen2.5:72b' or 'llama3'"
                    )
                if "name" in obj and obj["name"] == "llama3.2:3b" and "provider" in obj:
                    result["errors"].append(
                        f"Found 'llama3.2:3b' as model name at {path}.name - "
                        f"Should be an actual Ollama model name"
                    )

                # Recursively check nested dicts
                for key, value in obj.items():
                    check_dict(value, f"{path}.{key}" if path else key)

            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_dict(item, f"{path}[{i}]")

        check_dict(settings)
        return result

    def _check_for_ultron_model(self, settings: dict, file_path: Path) -> dict:
        """Check for 'ULTRON' used as a model name (ULTRON is a cluster, not a model)"""
        result = {"errors": [], "warnings": []}

        def check_dict(obj, path=""):
            if isinstance(obj, dict):
                # Check if "ULTRON" is used as a model name
                if "model" in obj and obj["model"] == "ULTRON":
                    result["errors"].append(
                        f"Found 'ULTRON' as model name at {path}.model - "
                        f"ULTRON is a virtual cluster, not a model. Use actual model like 'qwen2.5:72b'"
                    )
                if "model" in obj and "ULTRON" in str(obj["model"]) and obj["model"] != "qwen2.5:72b":
                    result["warnings"].append(
                        f"Found 'ULTRON' in model name at {path}.model = '{obj['model']}' - "
                        f"Ensure model is an actual Ollama model name"
                    )

                # Recursively check nested dicts
                for key, value in obj.items():
                    check_dict(value, f"{path}.{key}" if path else key)

            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_dict(item, f"{path}[{i}]")

        check_dict(settings)
        return result

    def fix_settings_file(self, file_path: Path) -> bool:
        """Fix incorrect model configurations in a settings file"""
        if not file_path.exists():
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                settings = json.loads(f.read())
        except Exception as e:
            print(f"❌ Failed to read {file_path}: {e}")
            return False

        fixed = False
        backup_path = file_path.with_suffix('.json.backup')

        # Create backup
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            print(f"✅ Backup created: {backup_path}")
        except Exception as e:
            print(f"⚠️  Failed to create backup: {e}")

        # Fix "llama3.2:3b" as model name
        fixed = self._fix_iron_legion_models(settings) or fixed

        # Fix "ULTRON" as model name
        fixed = self._fix_ultron_models(settings) or fixed

        if fixed:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2)
                print(f"✅ Fixed {file_path}")
                return True
            except Exception as e:
                print(f"❌ Failed to write {file_path}: {e}")
                return False

        return False

    def _fix_iron_legion_models(self, obj) -> bool:
        """Fix "llama3.2:3b" used as model name"""
        fixed = False

        if isinstance(obj, dict):
            # Fix model field
            if "model" in obj and obj["model"] == "llama3.2:3b":
                print(f"   🔧 Fixing: model 'llama3.2:3b' → 'qwen2.5:72b'")
                obj["model"] = "qwen2.5:72b"
                fixed = True

            # Fix name field if it's a model name
            if "name" in obj and obj["name"] == "llama3.2:3b" and "provider" in obj:
                if obj.get("provider") != "ollama":
                    print(f"   🔧 Fixing: provider → 'ollama'")
                    obj["provider"] = "ollama"
                if "model" not in obj:
                    print(f"   🔧 Adding: model 'qwen2.5:72b'")
                    obj["model"] = "qwen2.5:72b"
                fixed = True

            # Recursively fix nested objects
            for value in obj.values():
                if self._fix_iron_legion_models(value):
                    fixed = True

        elif isinstance(obj, list):
            for item in obj:
                if self._fix_iron_legion_models(item):
                    fixed = True

        return fixed

    def _fix_ultron_models(self, obj) -> bool:
        """Fix 'ULTRON' used as model name"""
        fixed = False

        if isinstance(obj, dict):
            # Fix model field if it's "ULTRON" (cluster name, not model)
            if "model" in obj and obj["model"] == "ULTRON":
                print(f"   🔧 Fixing: model 'ULTRON' → 'qwen2.5:72b'")
                obj["model"] = "qwen2.5:72b"
                fixed = True

            # Ensure provider is ollama for ULTRON entries
            if "title" in obj and "ULTRON" in obj["title"]:
                if "model" in obj and obj["model"] not in ["qwen2.5:72b", "llama3", "codellama:13b"]:
                    if isinstance(obj["model"], str) and "ULTRON" in obj["model"]:
                        print(f"   🔧 Fixing: model '{obj['model']}' → 'qwen2.5:72b'")
                        obj["model"] = "qwen2.5:72b"
                        fixed = True
                if "provider" not in obj or obj.get("provider") != "ollama":
                    print(f"   🔧 Fixing: provider → 'ollama'")
                    obj["provider"] = "ollama"
                    fixed = True

            # Recursively fix nested objects
            for value in obj.values():
                if self._fix_ultron_models(value):
                    fixed = True

        elif isinstance(obj, list):
            for item in obj:
                if self._fix_ultron_models(item):
                    fixed = True

        return fixed

    def run(self):
        try:
            """Run the fixer"""
            print("="*80)
            print("🔧 Cursor IDE - Fix 'llama3.2:3b' Invalid Model Error")
            print("="*80)
            print()

            # Find settings files
            print("🔍 Searching for Cursor settings files...")
            settings_paths = self.find_cursor_settings_paths()

            if not settings_paths:
                print("⚠️  No Cursor settings files found.")
                print("   Cursor settings are typically in:")
                if self.system == "Windows":
                    print("   - %APPDATA%\\Cursor\\User\\settings.json")
                elif self.system == "Darwin":
                    print("   - ~/Library/Application Support/Cursor/User/settings.json")
                elif self.system == "Linux":
                    print("   - ~/.config/Cursor/User/settings.json")
                print()
                print("   Please check Cursor settings manually:")
                print("   1. Open Cursor Settings (Ctrl+,)")
                print("   2. Search for 'llama3.2:3b' or 'ULTRON'")
                print("   3. Remove any entries where they're used as model names")
                return

            print(f"✅ Found {len(settings_paths)} settings file(s)")
            print()

            # Check each file
            all_issues = []
            for settings_path in settings_paths:
                print(f"📄 Checking: {settings_path}")
                issues = self.check_settings_file(settings_path)
                all_issues.append(issues)

                if issues["errors"]:
                    print(f"   ❌ Found {len(issues['errors'])} error(s):")
                    for error in issues["errors"]:
                        print(f"      - {error}")

                if issues["warnings"]:
                    print(f"   ⚠️  Found {len(issues['warnings'])} warning(s):")
                    for warning in issues["warnings"]:
                        print(f"      - {warning}")

                if not issues["errors"] and not issues["warnings"]:
                    print("   ✅ No issues found")

                print()

            # Fix issues
            has_errors = any(issues["errors"] for issues in all_issues)
            if has_errors:
                print("🔧 Attempting to fix issues...")
                print()

                for settings_path in settings_paths:
                    issues = [i for i in all_issues if i["file"] == str(settings_path)][0]
                    if issues["errors"]:
                        print(f"📝 Fixing: {settings_path}")
                        if self.fix_settings_file(Path(settings_path)):
                            print("   ✅ Fixed!")
                        else:
                            print("   ❌ Failed to fix automatically")
                        print()

            # Print summary
            print("="*80)
            print("📊 SUMMARY")
            print("="*80)

            total_errors = sum(len(issues["errors"]) for issues in all_issues)
            total_warnings = sum(len(issues["warnings"]) for issues in all_issues)

            if total_errors == 0 and total_warnings == 0:
                print("✅ No issues found! Your Cursor settings are correct.")
            else:
                print(f"❌ Found {total_errors} error(s) and {total_warnings} warning(s)")
                if has_errors:
                    print()
                    print("⚠️  IMPORTANT: After fixing, you MUST:")
                    print("   1. Close Cursor IDE completely")
                    print("   2. Restart your PC (recommended)")
                    print("   3. Reopen Cursor IDE")
                    print("   4. Test in Chat (Ctrl+L)")

            print()
            print("="*80)


        except Exception as e:
            self.logger.error(f"Error in run: {e}", exc_info=True)
            raise
def main():
    fixer = CursorSettingsFixer()
    fixer.run()


if __name__ == "__main__":


    main()