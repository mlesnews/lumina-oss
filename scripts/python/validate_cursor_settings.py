#!/usr/bin/env python3
"""
Validate Cursor IDE / VS Code Settings for LUMINA
End-to-end validation of settings.json and SYPHON configuration

Tags: #VALIDATION #CURSOR_IDE #SETTINGS #SYPHON #LUMINA @JARVIS @V3 @END2END
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CursorSettingsValidator")


class CursorSettingsValidator:
    """
    Validates Cursor IDE / VS Code settings for LUMINA
    """

    def __init__(self):
        """Initialize validator"""
        self.project_root = project_root
        self.settings_file = self.project_root / ".vscode" / "settings.json"
        self.syphon_config = self.project_root / "config" / "syphon_whitelist_blacklist.json"
        self.issues = []
        self.warnings = []
        self.successes = []

        logger.info("=" * 80)
        logger.info("🔍 CURSOR IDE SETTINGS VALIDATOR")
        logger.info("=" * 80)

    def validate_all(self) -> Dict[str, Any]:
        try:
            """Validate all settings"""
            results = {
                "timestamp": datetime.now().isoformat(),
                "settings_file_exists": False,
                "syphon_config_exists": False,
                "settings_valid": False,
                "syphon_config_valid": False,
                "integration_valid": False,
                "issues": [],
                "warnings": [],
                "successes": [],
                "confidence_score": 0.0
            }

            # Validate settings.json
            if self.settings_file.exists():
                results["settings_file_exists"] = True
                self.successes.append("✅ settings.json exists")
                settings_result = self._validate_settings()
                results["settings_valid"] = settings_result["valid"]
                results["issues"].extend(settings_result.get("issues", []))
                results["warnings"].extend(settings_result.get("warnings", []))
                results["successes"].extend(settings_result.get("successes", []))
            else:
                self.issues.append("❌ settings.json not found")
                results["issues"].append("settings.json not found")

            # Validate syphon config
            if self.syphon_config.exists():
                results["syphon_config_exists"] = True
                self.successes.append("✅ syphon_whitelist_blacklist.json exists")
                syphon_result = self._validate_syphon_config()
                results["syphon_config_valid"] = syphon_result["valid"]
                results["issues"].extend(syphon_result.get("issues", []))
                results["warnings"].extend(syphon_result.get("warnings", []))
                results["successes"].extend(syphon_result.get("successes", []))
            else:
                self.issues.append("❌ syphon_whitelist_blacklist.json not found")
                results["issues"].append("syphon_whitelist_blacklist.json not found")

            # Validate integration
            if results["settings_valid"] and results["syphon_config_valid"]:
                integration_result = self._validate_integration()
                results["integration_valid"] = integration_result["valid"]
                results["issues"].extend(integration_result.get("issues", []))
                results["warnings"].extend(integration_result.get("warnings", []))
                results["successes"].extend(integration_result.get("successes", []))

            # Calculate confidence score
            total_checks = len(results["successes"]) + len(results["warnings"]) + len(results["issues"])
            if total_checks > 0:
                results["confidence_score"] = (
                    (len(results["successes"]) * 1.0 + len(results["warnings"]) * 0.5) / total_checks
                ) * 100

            results["issues"] = self.issues
            results["warnings"] = self.warnings
            results["successes"] = self.successes

            return results

        except Exception as e:
            self.logger.error(f"Error in validate_all: {e}", exc_info=True)
            raise
    def _validate_settings(self) -> Dict[str, Any]:
        """Validate settings.json (JSONC - JSON with Comments)"""
        result = {
            "valid": False,
            "issues": [],
            "warnings": [],
            "successes": []
        }

        try:
            # Read file and strip comments (JSONC support)
            with open(self.settings_file, encoding='utf-8') as f:
                content = f.read()

            # Strip single-line comments (// ...)
            import re
            content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
            # Strip multi-line comments (/* ... */)
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

            # Parse as JSON
            settings = json.loads(content)

            # Check required sections
            required_sections = [
                "files.exclude",
                "search.exclude",
                "cursor.aiContextExclude",
                "cursor.aiContextInclude",
                "python.analysis.exclude",
                "lumina.syphon.enabled"
            ]

            for section in required_sections:
                if section in settings:
                    result["successes"].append(f"✅ {section} present")
                else:
                    result["warnings"].append(f"⚠️ {section} missing")

            # Validate SYPHON settings
            if "lumina.syphon.enabled" in settings and settings["lumina.syphon.enabled"]:
                result["successes"].append("✅ SYPHON enabled in settings")
            else:
                result["warnings"].append("⚠️ SYPHON not enabled")

            # Validate AI context limits
            if "cursor.aiContextMaxSize" in settings:
                max_size = settings["cursor.aiContextMaxSize"]
                if max_size <= 1000000:
                    result["successes"].append(f"✅ AI context max size: {max_size:,} bytes")
                else:
                    result["warnings"].append(f"⚠️ AI context max size too large: {max_size:,} bytes")

            if "cursor.aiContextMaxFiles" in settings:
                max_files = settings["cursor.aiContextMaxFiles"]
                if max_files <= 50:
                    result["successes"].append(f"✅ AI context max files: {max_files}")
                else:
                    result["warnings"].append(f"⚠️ AI context max files too large: {max_files}")

            # Validate exclusions
            if "files.exclude" in settings:
                exclude_count = len(settings["files.exclude"])
                result["successes"].append(f"✅ {exclude_count} file exclusions configured")

            if "search.exclude" in settings:
                search_exclude_count = len(settings["search.exclude"])
                result["successes"].append(f"✅ {search_exclude_count} search exclusions configured")

            if "cursor.aiContextExclude" in settings:
                ai_exclude_count = len(settings["cursor.aiContextExclude"])
                result["successes"].append(f"✅ {ai_exclude_count} AI context exclusions configured")

            if "cursor.aiContextInclude" in settings:
                ai_include_count = len(settings["cursor.aiContextInclude"])
                result["successes"].append(f"✅ {ai_include_count} AI context inclusions configured")

            result["valid"] = True

        except json.JSONDecodeError as e:
            result["issues"].append(f"❌ Invalid JSON in settings.json: {e}")
        except Exception as e:
            result["issues"].append(f"❌ Error validating settings.json: {e}")

        return result

    def _validate_syphon_config(self) -> Dict[str, Any]:
        """Validate syphon_whitelist_blacklist.json"""
        result = {
            "valid": False,
            "issues": [],
            "warnings": [],
            "successes": []
        }

        try:
            with open(self.syphon_config, encoding='utf-8') as f:
                config = json.load(f)

            # Check required sections
            required_sections = ["whitelist", "blacklist", "ai_context", "search", "tags"]

            for section in required_sections:
                if section in config:
                    result["successes"].append(f"✅ {section} section present")
                else:
                    result["warnings"].append(f"⚠️ {section} section missing")

            # Validate whitelist
            if "whitelist" in config:
                whitelist = config["whitelist"]
                if "patterns" in whitelist:
                    pattern_count = len(whitelist["patterns"])
                    result["successes"].append(f"✅ {pattern_count} whitelist patterns")
                if "directories" in whitelist:
                    dir_count = len(whitelist["directories"])
                    result["successes"].append(f"✅ {dir_count} whitelist directories")

            # Validate blacklist
            if "blacklist" in config:
                blacklist = config["blacklist"]
                if "patterns" in blacklist:
                    pattern_count = len(blacklist["patterns"])
                    result["successes"].append(f"✅ {pattern_count} blacklist patterns")
                if "directories" in blacklist:
                    dir_count = len(blacklist["directories"])
                    result["successes"].append(f"✅ {dir_count} blacklist directories")

            # Validate AI context section
            if "ai_context" in config:
                ai_context = config["ai_context"]
                if "whitelist" in ai_context and "blacklist" in ai_context:
                    result["successes"].append("✅ AI context whitelist/blacklist configured")

            # Validate tags section
            if "tags" in config:
                tags = config["tags"]
                if "syphon_tag" in tags and tags["syphon_tag"] == "#syphon":
                    result["successes"].append("✅ SYPHON tag configured correctly")
                if "grep_tag" in tags and tags["grep_tag"] == "@grep":
                    result["successes"].append("✅ GREP tag configured correctly")

            result["valid"] = True

        except json.JSONDecodeError as e:
            result["issues"].append(f"❌ Invalid JSON in syphon config: {e}")
        except Exception as e:
            result["issues"].append(f"❌ Error validating syphon config: {e}")

        return result

    def _validate_integration(self) -> Dict[str, Any]:
        """Validate integration between settings.json and syphon config"""
        result = {
            "valid": False,
            "issues": [],
            "warnings": [],
            "successes": []
        }

        try:
            # Load settings.json (JSONC - strip comments)
            import re
            with open(self.settings_file, encoding='utf-8') as f:
                settings_content = f.read()
            settings_content = re.sub(r'//.*?$', '', settings_content, flags=re.MULTILINE)
            settings_content = re.sub(r'/\*.*?\*/', '', settings_content, flags=re.DOTALL)
            settings = json.loads(settings_content)

            # Load syphon config (pure JSON)
            with open(self.syphon_config, encoding='utf-8') as f:
                syphon_config = json.load(f)

            # Check if SYPHON patterns match
            if "lumina.syphon.patterns" in settings and "whitelist" in syphon_config:
                settings_patterns = set(settings["lumina.syphon.patterns"])
                syphon_patterns = set(syphon_config["whitelist"].get("patterns", []))

                # Check for overlap
                overlap = settings_patterns.intersection(syphon_patterns)
                if overlap:
                    result["successes"].append(f"✅ {len(overlap)} patterns match between settings and syphon config")
                else:
                    result["warnings"].append("⚠️ No pattern overlap between settings and syphon config")

            # Check if exclusions match
            if "lumina.syphon.exclude" in settings and "blacklist" in syphon_config:
                settings_exclude = set(settings["lumina.syphon.exclude"])
                syphon_exclude = set(syphon_config["blacklist"].get("patterns", []))

                overlap = settings_exclude.intersection(syphon_exclude)
                if overlap:
                    result["successes"].append(f"✅ {len(overlap)} exclusions match between settings and syphon config")

            # Check AI context integration
            if "cursor.aiContextInclude" in settings and "ai_context" in syphon_config:
                settings_include = set(settings["cursor.aiContextInclude"])
                syphon_include = set(syphon_config["ai_context"].get("whitelist", {}).get("patterns", []))

                overlap = settings_include.intersection(syphon_include)
                if overlap:
                    result["successes"].append(f"✅ {len(overlap)} AI context patterns match")

            result["valid"] = True

        except Exception as e:
            result["issues"].append(f"❌ Error validating integration: {e}")

        return result

    def print_report(self, results: Dict[str, Any]):
        """Print validation report"""
        print("=" * 80)
        print("📊 CURSOR IDE SETTINGS VALIDATION REPORT")
        print("=" * 80)
        print()

        print(f"Timestamp: {results['timestamp']}")
        print()

        print("File Status:")
        print(f"  settings.json: {'✅ EXISTS' if results['settings_file_exists'] else '❌ MISSING'}")
        print(f"  syphon_whitelist_blacklist.json: {'✅ EXISTS' if results['syphon_config_exists'] else '❌ MISSING'}")
        print()

        print("Validation Status:")
        print(f"  settings.json: {'✅ VALID' if results['settings_valid'] else '❌ INVALID'}")
        print(f"  syphon config: {'✅ VALID' if results['syphon_config_valid'] else '❌ INVALID'}")
        print(f"  integration: {'✅ VALID' if results['integration_valid'] else '❌ INVALID'}")
        print()

        print(f"Confidence Score: {results['confidence_score']:.1f}%")
        print()

        if results["successes"]:
            print("✅ Successes:")
            for success in results["successes"]:
                print(f"  {success}")
            print()

        if results["warnings"]:
            print("⚠️ Warnings:")
            for warning in results["warnings"]:
                print(f"  {warning}")
            print()

        if results["issues"]:
            print("❌ Issues:")
            for issue in results["issues"]:
                print(f"  {issue}")
            print()

        print("=" * 80)


def main():
    """Main entry point"""
    validator = CursorSettingsValidator()
    results = validator.validate_all()
    validator.print_report(results)

    # Return exit code based on results
    if results["issues"]:
        return 1
    elif results["warnings"]:
        return 0
    else:
        return 0


if __name__ == "__main__":


    sys.exit(main())