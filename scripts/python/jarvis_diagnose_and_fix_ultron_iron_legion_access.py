#!/usr/bin/env python3
"""
JARVIS: Diagnose and Fix ULTRON and IRON LEGION Access Issues

Comprehensive diagnostic and fix script for ULTRON and IRON LEGION local AI clusters.
Checks connectivity, validates configuration, and fixes Cursor settings.

Tags: #FIX #ULTRON #IRON_LEGION #KUBE #DIAGNOSTIC #LOCAL_AI @JARVIS @LUMINA
"""

import json
import sys
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
settings_file = project_root / ".cursor" / "settings.json"

try:
    from lumina_core.logging import get_logger
    logger = get_logger("JARVISUltronIronLegionFix")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("JARVISUltronIronLegionFix")


def check_endpoint_connectivity(endpoint: str, timeout: int = 5) -> Tuple[bool, Optional[str]]:
    """Check if an endpoint is accessible"""
    try:
        # Try health check endpoint first
        health_url = f"{endpoint.rstrip('/')}/health"
        response = requests.get(health_url, timeout=timeout)
        if response.status_code == 200:
            return True, "Health check passed"
    except requests.exceptions.RequestException:
        pass

    try:
        # Try OpenAI-compatible API endpoint
        if "/v1" in endpoint:
            # Try models endpoint
            models_url = f"{endpoint.rstrip('/')}/models"
            response = requests.get(models_url, timeout=timeout)
            if response.status_code == 200:
                return True, "Models endpoint accessible"
        else:
            # Try Ollama API endpoint
            tags_url = f"{endpoint.rstrip('/')}/api/tags"
            response = requests.get(tags_url, timeout=timeout)
            if response.status_code == 200:
                return True, "Ollama API accessible"
    except requests.exceptions.ConnectionError:
        return False, "Connection refused"
    except requests.exceptions.Timeout:
        return False, "Connection timeout"
    except Exception as e:
        return False, str(e)

    return False, "Unknown error"


def check_kube_endpoint() -> Dict[str, Any]:
    """Check KUBE endpoint status"""
    kube_endpoint = "http://<NAS_PRIMARY_IP>:8000"
    kube_v1_endpoint = f"{kube_endpoint}/v1"

    print("=" * 80)
    print("🔍 CHECKING KUBE ENDPOINT CONNECTIVITY")
    print("=" * 80)
    print()

    # Check base endpoint
    print(f"Checking KUBE base endpoint: {kube_endpoint}")
    base_accessible, base_error = check_endpoint_connectivity(kube_endpoint)
    print(f"  {'✅' if base_accessible else '❌'} Base endpoint: {base_error}")
    print()

    # Check v1 endpoint
    print(f"Checking KUBE v1 endpoint: {kube_v1_endpoint}")
    v1_accessible, v1_error = check_endpoint_connectivity(kube_v1_endpoint)
    print(f"  {'✅' if v1_accessible else '❌'} V1 endpoint: {v1_error}")
    print()

    # Try to get models list
    models_available = []
    if v1_accessible:
        try:
            models_url = f"{kube_v1_endpoint}/models"
            response = requests.get(models_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "data" in data:
                    models_available = [m.get("id", "") for m in data["data"]]
                elif isinstance(data, list):
                    models_available = [m.get("id", "") for m in data]
                print(f"  ✅ Available models: {', '.join(models_available) if models_available else 'None found'}")
            else:
                print(f"  ⚠️  Models endpoint returned: {response.status_code}")
        except Exception as e:
            print(f"  ⚠️  Could not fetch models list: {e}")
    print()

    return {
        "base_endpoint": kube_endpoint,
        "v1_endpoint": kube_v1_endpoint,
        "base_accessible": base_accessible,
        "v1_accessible": v1_accessible,
        "base_error": base_error,
        "v1_error": v1_error,
        "models_available": models_available
    }


def check_ollama_endpoints() -> Dict[str, Any]:
    """Check Ollama endpoints (localhost and NAS)"""
    print("=" * 80)
    print("🔍 CHECKING OLLAMA ENDPOINTS")
    print("=" * 80)
    print()

    endpoints_to_check = [
        ("ULTRON Local", "http://localhost:11434", "qwen2.5:72b"),
        ("KAIJU NAS", "http://<NAS_PRIMARY_IP>:11434", "llama3.2:3b"),
    ]

    results = {}
    for name, endpoint, expected_model in endpoints_to_check:
        print(f"Checking {name}: {endpoint}")
        accessible, error = check_endpoint_connectivity(endpoint)
        print(f"  {'✅' if accessible else '❌'} Status: {error}")

        # Try to get models list
        models_available = []
        if accessible:
            try:
                tags_url = f"{endpoint}/api/tags"
                response = requests.get(tags_url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    models_available = [m.get("name", "") for m in data.get("models", [])]
                    model_found = expected_model in models_available
                    print(f"  {'✅' if model_found else '⚠️'} Expected model '{expected_model}': {'Found' if model_found else 'Not found'}")
                    if models_available:
                        print(f"  📋 Available models: {', '.join(models_available[:5])}")
            except Exception as e:
                print(f"  ⚠️  Could not fetch models: {e}")

        results[name] = {
            "endpoint": endpoint,
            "accessible": accessible,
            "error": error,
            "models_available": models_available,
            "expected_model": expected_model
        }
        print()

    return results


def fix_model_config(model: Dict[str, Any], model_name: str) -> bool:
    """Fix a single model configuration to be properly local"""
    changed = False

    # Ensure it's marked as local-only
    if model.get("localOnly") != True:
        model["localOnly"] = True
        changed = True
        logger.info(f"Set {model_name} localOnly: true")

    if model.get("skipProviderSelection") != True:
        model["skipProviderSelection"] = True
        changed = True
        logger.info(f"Set {model_name} skipProviderSelection: true")

    # Remove any API key requirements (causes "invalid model" errors)
    for key in ["apiKey", "requiresApiKey", "subscription", "requiresSubscription"]:
        if key in model:
            del model[key]
            changed = True
            logger.info(f"Removed {model_name} {key}")

    # Ensure apiBase is set correctly
    api_base = model.get("apiBase", "")
    if not api_base or "8000" not in api_base:
        # Default to KUBE endpoint
        model["apiBase"] = "http://<NAS_PRIMARY_IP>:8000/v1"
        changed = True
        logger.info(f"Set {model_name} apiBase: {model['apiBase']}")

    # Ensure provider is set correctly for KUBE (OpenAI-compatible)
    if "8000" in api_base or "kube" in api_base.lower():
        if model.get("provider") != "openai":
            model["provider"] = "openai"
            changed = True
            logger.info(f"Set {model_name} provider: openai (KUBE endpoint)")

    return changed


def fix_ultron_models(models: List[Dict[str, Any]]) -> bool:
    """Fix all ULTRON models"""
    changed = False

    for model in models:
        name = model.get("name", "") or model.get("title", "")
        name_lower = name.lower()

        if "ultron" in name_lower:
            if fix_model_config(model, name):
                changed = True

    return changed


def fix_iron_legion_models(models: List[Dict[str, Any]]) -> bool:
    """Fix all Iron Legion/KAIJU models"""
    changed = False

    for model in models:
        name = model.get("name", "") or model.get("title", "")
        name_lower = name.lower()

        if any(keyword in name_lower for keyword in ["iron legion", "kaiju", "iron_legion"]):
            if fix_model_config(model, name):
                changed = True

    return changed


def fix_cursor_settings() -> bool:
    try:
        """Fix Cursor settings to resolve invalid model errors"""

        if not settings_file.exists():
            logger.error(f"Settings file not found: {settings_file}")
            print(f"❌ Settings file not found: {settings_file}")
            return False

        print("=" * 80)
        print("🔧 FIXING CURSOR SETTINGS")
        print("=" * 80)
        print()

        logger.info(f"Reading settings from: {settings_file}")
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)

        sections_to_fix = [
            "cursor.agent.customModels",
            "cursor.chat.customModels",
            "cursor.composer.customModels",
            "cursor.inlineCompletion.customModels",
            "cursor.model.customModels"
        ]

        total_changes = 0

        for section_key in sections_to_fix:
            if section_key not in settings:
                continue

            models = settings[section_key]
            section_changed = False

            # Fix ULTRON
            if fix_ultron_models(models):
                section_changed = True
                total_changes += 1

            # Fix Iron Legion models
            if fix_iron_legion_models(models):
                section_changed = True
                total_changes += 1

            if section_changed:
                settings[section_key] = models
                logger.info(f"Fixed {section_key}")

        # Ensure ULTRON is the default agent model
        if settings.get("cursor.agent.defaultModel") != "ULTRON":
            settings["cursor.agent.defaultModel"] = "ULTRON"
            total_changes += 1
            logger.info("Set ULTRON as default agent model")

        # Write back if changes were made
        if total_changes > 0:
            logger.info(f"Writing fixed settings to: {settings_file}")
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

            print(f"✅ Fixed {total_changes} configuration issue(s)!")
            print()
            return True
        else:
            print("✅ No changes needed - models are already properly configured")
            print()
            return True


    except Exception as e:
        logger.error(f"Error in fix_cursor_settings: {e}", exc_info=True)
        raise
def main():
    """Main diagnostic and fix workflow"""
    print("=" * 80)
    print("🤖 JARVIS: ULTRON & IRON LEGION ACCESS DIAGNOSTIC & FIX")
    print("=" * 80)
    print()

    # Step 1: Check KUBE endpoint
    kube_status = check_kube_endpoint()

    # Step 2: Check Ollama endpoints
    ollama_status = check_ollama_endpoints()

    # Step 3: Fix Cursor settings
    settings_fixed = fix_cursor_settings()

    # Step 4: Summary and recommendations
    print("=" * 80)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 80)
    print()

    print("KUBE Endpoint Status:")
    print(f"  {'✅' if kube_status['v1_accessible'] else '❌'} V1 Endpoint: {kube_status['v1_endpoint']}")
    if kube_status['models_available']:
        print(f"  📋 Available models: {', '.join(kube_status['models_available'])}")
    print()

    print("Ollama Endpoints Status:")
    for name, status in ollama_status.items():
        print(f"  {'✅' if status['accessible'] else '❌'} {name}: {status['endpoint']}")
    print()

    print("Cursor Settings:")
    print(f"  {'✅' if settings_fixed else '❌'} Settings fixed: {settings_fixed}")
    print()

    # Recommendations
    print("=" * 80)
    print("💡 RECOMMENDATIONS")
    print("=" * 80)
    print()

    if not kube_status['v1_accessible']:
        print("❌ KUBE endpoint is not accessible!")
        print("   → Check if KUBE service is running on NAS (<NAS_PRIMARY_IP>:8000)")
        print("   → Verify network connectivity to NAS")
        print("   → Check firewall rules")
        print()

    if not ollama_status.get("ULTRON Local", {}).get("accessible", False):
        print("⚠️  Local Ollama endpoint is not accessible!")
        print("   → Check if Ollama is running on localhost:11434")
        print("   → Start Ollama service if needed")
        print()

    if not ollama_status.get("KAIJU NAS", {}).get("accessible", False):
        print("⚠️  NAS Ollama endpoint is not accessible!")
        print("   → Check if Ollama is running on NAS (<NAS_PRIMARY_IP>:11434)")
        print("   → Verify NAS container status")
        print()

    if settings_fixed:
        print("✅ Cursor settings have been fixed")
        print("   → Restart Cursor IDE for changes to take effect")
        print()

    if kube_status['v1_accessible'] and settings_fixed:
        print("✅ All systems should be operational after Cursor restart!")
    else:
        print("⚠️  Some issues remain - please address connectivity issues first")

    print()

    return 0 if (kube_status['v1_accessible'] or any(s.get('accessible', False) for s in ollama_status.values())) else 1


if __name__ == "__main__":


    sys.exit(main())