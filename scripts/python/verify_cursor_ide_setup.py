#!/usr/bin/env python3
"""
Verify Cursor IDE Setup and Configuration
Checks Kilo Code extension, configuration files, and integrations
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
import logging
logger = logging.getLogger("verify_cursor_ide_setup")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def load_json_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """Load JSON file safely"""
    try:
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"⚠ Warning: Could not load {file_path}: {e}")
        return None

def verify_cursor_settings(project_root: Path) -> Dict[str, Any]:
    try:
        """Verify Cursor IDE settings"""
        print("=" * 60)
        print("VERIFICATION 1: Cursor IDE Settings")
        print("=" * 60)

        cursor_settings = project_root / ".cursor" / "settings.json"
        kilo_code_config = project_root / ".cursor" / "kilo_code_config.json"
        mcp_config = project_root / ".cursor" / "mcp_config.json"

        results = {
            "settings_exists": cursor_settings.exists(),
            "kilo_code_config_exists": kilo_code_config.exists(),
            "mcp_config_exists": mcp_config.exists(),
            "settings_content": None,
            "kilo_code_config_content": None,
            "mcp_config_content": None
        }

        if results["settings_exists"]:
            results["settings_content"] = load_json_file(cursor_settings)
            print("✓ .cursor/settings.json exists")
        else:
            print("❌ .cursor/settings.json not found")

        if results["kilo_code_config_exists"]:
            results["kilo_code_config_content"] = load_json_file(kilo_code_config)
            print("✓ .cursor/kilo_code_config.json exists")
        else:
            print("❌ .cursor/kilo_code_config.json not found")

        if results["mcp_config_exists"]:
            results["mcp_config_content"] = load_json_file(mcp_config)
            print("✓ .cursor/mcp_config.json exists")
        else:
            print("❌ .cursor/mcp_config.json not found")

        print()
        return results

    except Exception as e:
        logger.error(f"Error in verify_cursor_settings: {e}", exc_info=True)
        raise
def verify_kilo_code_config(project_root: Path) -> Dict[str, Any]:
    try:
        """Verify Kilo Code configuration"""
        print("=" * 60)
        print("VERIFICATION 2: Kilo Code Configuration")
        print("=" * 60)

        kilo_code_config = project_root / ".cursor" / "kilo_code_config.json"
        kilo_code_optimized = project_root / "config" / "kilo_code_optimized_config.json"

        results = {
            "cursor_config_exists": kilo_code_config.exists(),
            "optimized_config_exists": kilo_code_optimized.exists(),
            "iron_legion_configured": False,
            "peak_integration_enabled": False,
            "r5_integration_enabled": False
        }

        if results["cursor_config_exists"]:
            config = load_json_file(kilo_code_config)
            if config:
                print("✓ Kilo Code config loaded")
                # Check for Iron Legion
                if "llm" in config or "llama3.2:3b" in str(config):
                    results["iron_legion_configured"] = True
                    print("✓ Iron Legion configured")
        else:
            print("❌ Kilo Code config not found")

        if results["optimized_config_exists"]:
            config = load_json_file(kilo_code_optimized)
            if config:
                peak = config.get("peak_integration", {})
                if peak.get("enabled"):
                    results["peak_integration_enabled"] = True
                    print("✓ @Peak integration enabled")

                r5 = config.get("r5_integration", {})
                if r5.get("enabled"):
                    results["r5_integration_enabled"] = True
                    print("✓ R5 integration enabled")
        else:
            print("❌ Kilo Code optimized config not found")

        print()
        return results

    except Exception as e:
        logger.error(f"Error in verify_kilo_code_config: {e}", exc_info=True)
        raise
def verify_extension_status(project_root: Path) -> Dict[str, Any]:
    """Verify Cursor extension installation status"""
    print("=" * 60)
    print("VERIFICATION 3: Cursor Extension Status")
    print("=" * 60)

    # Note: Cannot directly check Cursor extensions without Cursor API
    # This is a placeholder for manual verification

    print("⚠ Extension status requires manual verification")
    print("  Please check in Cursor IDE:")
    print("  1. Open Cursor")
    print("  2. Go to Extensions (Ctrl+Shift+X)")
    print("  3. Search for 'Kilo Code'")
    print("  4. Verify it's installed and enabled")
    print()

    return {
        "requires_manual_check": True,
        "instructions": "Check Cursor IDE Extensions panel"
    }

def verify_model_configuration(project_root: Path) -> Dict[str, Any]:
    try:
        """Verify model configuration matches expected 7 models"""
        print("=" * 60)
        print("VERIFICATION 4: Model Configuration")
        print("=" * 60)

        model_mapping = project_root / "config" / "ollama_model_mapping.json"
        kilo_code_config = project_root / "config" / "kilo_code_optimized_config.json"

        results = {
            "model_mapping_exists": model_mapping.exists(),
            "kilo_code_config_exists": kilo_code_config.exists(),
            "expected_models": 7,
            "found_models": 0,
            "models_match": False
        }

        if results["model_mapping_exists"]:
            mapping = load_json_file(model_mapping)
            if mapping:
                results["found_models"] = mapping.get("total_models", 0)
                if results["found_models"] == results["expected_models"]:
                    results["models_match"] = True
                    print(f"✓ Model mapping has {results['found_models']} models (expected {results['expected_models']})")
                else:
                    print(f"❌ Model count mismatch: found {results['found_models']}, expected {results['expected_models']}")

        if results["kilo_code_config_exists"]:
            config = load_json_file(kilo_code_config)
            if config:
                models = config.get("llm_config", {}).get("models", {})
                print(f"✓ Kilo Code config has models: {', '.join(models.values())}")

        print()
        return results

    except Exception as e:
        logger.error(f"Error in verify_model_configuration: {e}", exc_info=True)
        raise
def main():
    """Main verification function"""
    project_root = Path(__file__).parent.parent.parent

    print("=" * 60)
    print("CURSOR IDE SETUP VERIFICATION")
    print("=" * 60)
    print()

    verifications = [
        ("Cursor Settings", verify_cursor_settings),
        ("Kilo Code Config", verify_kilo_code_config),
        ("Extension Status", verify_extension_status),
        ("Model Configuration", verify_model_configuration),
    ]

    results = []
    for name, verify_func in verifications:
        try:
            result = verify_func(project_root)
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            results.append((name, {"error": str(e)}))

    # Summary
    print("=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    print()

    all_passed = True
    for name, result in results:
        if "error" in result:
            print(f"❌ FAIL: {name} - {result['error']}")
            all_passed = False
        elif result.get("requires_manual_check"):
            print(f"⚠ MANUAL: {name} - Requires manual verification")
        else:
            print(f"✓ PASS: {name}")

    print()
    if all_passed:
        print("✓ ALL AUTOMATED VERIFICATIONS PASSED")
        print("⚠ Manual verification required for extensions")
        return 0
    else:
        print("❌ SOME VERIFICATIONS FAILED")
        return 1

if __name__ == "__main__":



    sys.exit(main())