#!/usr/bin/env python3
"""
Fix Invalid Model Error for Iron Legion
MANUS Framework - Comprehensive Model Error Resolution

This script fixes the "invalid model error" by:
1. Detecting where "llama3.2:3b" is used as a model name (invalid)
2. Replacing with actual model names from available models
3. Validating model configuration
4. Fixing config files

@JARVIS @MANUS @IRON_LEGION @FIX
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))


class InvalidModelErrorFixer:
    """Fix invalid model errors for Iron Legion"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.fixes_applied = []
        self.errors_found = []

    def find_invalid_model_references(self) -> List[Dict[str, Any]]:
        """Find all invalid "llama3.2:3b" model references"""
        invalid_refs = []

        # Common patterns for invalid model references
        invalid_patterns = [
            r'"llama3.2:3b"',
            r'"llama3.2:3b"',
            r'model["\']?\s*[:=]\s*["\']?iron legion["\']?',
            r'"llama3.2:3b"',
            r'"llama3.2:3b"',
            r"llama3.2:3b",  # As model name (not endpoint/config name)
        ]

        # Files to check
        files_to_check = [
            "config/cursor_ultron_model_config.json",
            "config/cursor_ide_complete_keyboard_shortcuts.json",
            "scripts/python/intelligent_llm_router.py",
            "scripts/python/jarvis_cursor_ide_engineer.py",
        ]

        for file_path in files_to_check:
            full_path = self.project_root / file_path
            if not full_path.exists():
                continue

            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                for line_num, line in enumerate(lines, 1):
                    for pattern in invalid_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            invalid_refs.append({
                                "file": str(full_path),
                                "line": line_num,
                                "line_content": line.strip(),
                                "pattern": pattern,
                                "issue": "Invalid model name 'llama3.2:3b' found"
                            })
            except Exception as e:
                self.errors_found.append(f"Error reading {full_path}: {e}")

        return invalid_refs

    def fix_config_file(self, config_path: Path) -> Dict[str, Any]:
        """Fix model references in a config file"""
        result = {
            "file": str(config_path),
            "fixed": False,
            "changes": [],
            "errors": []
        }

        if not config_path.exists():
            result["errors"].append("File does not exist")
            return result

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            original_config = json.dumps(config, indent=2)
            changed = False

            # Fix models array
            if "models" in config:
                for model in config["models"]:
                    # If model name is "llama3.2:3b" or similar, replace with actual model
                    if "name" in model:
                        name_lower = model["name"].lower()
                        if "llama3.2:3b" in name_lower and ":" not in model.get("model", ""):
                            # This is an invalid model name
                            # Replace with a valid default or remove model field
                            if "model" not in model or model["model"] == "auto":
                                # Keep as "auto" - that's valid
                                pass
                            elif model.get("model", "").lower() in ["llama3.2:3b", "llama3.2:3b", "llama3.2:3b"]:
                                # Replace with "auto" or a valid model
                                old_model = model["model"]
                                model["model"] = "auto"
                                result["changes"].append(f"Replaced invalid model '{old_model}' with 'auto'")
                                changed = True

                    # Fix model field if it's "llama3.2:3b"
                    if "model" in model:
                        model_val = model["model"].lower()
                        if model_val in ["llama3.2:3b", "llama3.2:3b", "llama3.2:3b"]:
                            old_val = model["model"]
                            model["model"] = "auto"
                            result["changes"].append(f"Replaced invalid model '{old_val}' with 'auto'")
                            changed = True

            if changed:
                new_config = json.dumps(config, indent=2)
                if new_config != original_config:
                    with open(config_path, 'w', encoding='utf-8') as f:
                        f.write(new_config)
                    result["fixed"] = True
                    self.fixes_applied.append(str(config_path))

        except json.JSONDecodeError as e:
            result["errors"].append(f"Invalid JSON: {e}")
        except Exception as e:
            result["errors"].append(f"Error: {e}")

        return result

    def fix_all_configs(self) -> Dict[str, Any]:
        try:
            """Fix all config files with invalid model references"""
            results = {
                "files_checked": 0,
                "files_fixed": 0,
                "total_changes": 0,
                "errors": []
            }

            config_files = [
                self.project_root / "config" / "cursor_ultron_model_config.json",
            ]

            for config_file in config_files:
                if not config_file.exists():
                    continue

                results["files_checked"] += 1
                fix_result = self.fix_config_file(config_file)

                if fix_result["fixed"]:
                    results["files_fixed"] += 1
                    results["total_changes"] += len(fix_result["changes"])

                if fix_result["errors"]:
                    results["errors"].extend(fix_result["errors"])

            return results

        except Exception as e:
            self.logger.error(f"Error in fix_all_configs: {e}", exc_info=True)
            raise
    def generate_report(self) -> str:
        """Generate fix report"""
        invalid_refs = self.find_invalid_model_references()
        fix_results = self.fix_all_configs()

        report = []
        report.append("=" * 80)
        report.append("INVALID MODEL ERROR FIX REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)
        report.append("")

        # Invalid references found
        report.append(f"📋 INVALID MODEL REFERENCES FOUND: {len(invalid_refs)}")
        report.append("-" * 80)
        if invalid_refs:
            for ref in invalid_refs[:10]:  # Show first 10
                report.append(f"\nFile: {ref['file']}")
                report.append(f"Line {ref['line']}: {ref['line_content']}")
                report.append(f"Issue: {ref['issue']}")
        else:
            report.append("✅ No invalid model references found!")

        # Fix results
        report.append("\n")
        report.append("🔧 FIX RESULTS:")
        report.append("-" * 80)
        report.append(f"Files checked: {fix_results['files_checked']}")
        report.append(f"Files fixed: {fix_results['files_fixed']}")
        report.append(f"Total changes: {fix_results['total_changes']}")

        if fix_results['errors']:
            report.append(f"\nErrors: {len(fix_results['errors'])}")
            for error in fix_results['errors']:
                report.append(f"  - {error}")

        # Recommendations
        report.append("\n")
        report.append("💡 RECOMMENDATIONS:")
        report.append("-" * 80)
        if invalid_refs:
            report.append("1. Review invalid model references above")
            report.append("2. Replace 'llama3.2:3b' with actual model names like:")
            report.append("   - 'codellama:13b' for code generation")
            report.append("   - 'llama3.2:11b' for general tasks")
            report.append("   - 'auto' for automatic selection")
            report.append("3. Use 'KAIJU Iron Legion' for endpoint/config names (not model names)")
        else:
            report.append("✅ No fixes needed - all model references are valid!")

        report.append("\n")
        report.append("=" * 80)

        return "\n".join(report)


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Fix Invalid Model Error for Iron Legion")
    parser.add_argument("action", choices=["find", "fix", "report"], 
                       help="Action to perform")

    args = parser.parse_args()

    fixer = InvalidModelErrorFixer()

    if args.action == "find":
        invalid_refs = fixer.find_invalid_model_references()
        print(f"\nFound {len(invalid_refs)} invalid model references:")
        for ref in invalid_refs:
            print(f"\n{ref['file']}:{ref['line']}")
            print(f"  {ref['line_content']}")
            print(f"  Issue: {ref['issue']}")

    elif args.action == "fix":
        results = fixer.fix_all_configs()
        print(f"\n✅ Fixed {results['files_fixed']} files")
        print(f"   Total changes: {results['total_changes']}")
        if results['errors']:
            print(f"\n⚠️  Errors: {len(results['errors'])}")
            for error in results['errors']:
                print(f"   - {error}")

    elif args.action == "report":
        report = fixer.generate_report()
        print(report)


if __name__ == "__main__":


    main()