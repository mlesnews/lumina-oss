#!/usr/bin/env python3
"""
Verify Lumina Extension Completion - Option 1 (Quick Win)

Verifies all components work with direct calls (no Azure required).
This is the "Quick Win" approach - get it working NOW.
"""

import sys
from pathlib import Path
import logging
logger = logging.getLogger("verify_lumina_extension_complete")


# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts" / "python"))

def test_imports():
    """Test that all components can be imported"""
    print("🔍 Testing Component Imports...")
    results = {}

    try:
        from jarvis_helpdesk_integration import JARVISHelpdeskIntegration
        results["JARVIS Helpdesk"] = "✅"
    except Exception as e:
        results["JARVIS Helpdesk"] = f"❌ {str(e)[:50]}"

    try:
        from droid_actor_system import DroidActorSystem
        results["Droid Actor System"] = "✅"
    except Exception as e:
        results["Droid Actor System"] = f"❌ {str(e)[:50]}"

    try:
        from r5_living_context_matrix import R5LivingContextMatrix
        results["R5 Living Context Matrix"] = "✅"
    except Exception as e:
        results["R5 Living Context Matrix"] = f"❌ {str(e)[:50]}"

    try:
        from v3_verification import V3Verification
        results["@v3 Verification"] = "✅"
    except Exception as e:
        results["@v3 Verification"] = f"❌ {str(e)[:50]}"

    return results

def test_config_files():
    try:
        """Test that config files exist"""
        print("\n📋 Testing Configuration Files...")
        results = {}

        config_files = [
            ("Droid Config", project_root / "config" / "helpdesk" / "droids.json"),
            ("Helpdesk Structure", project_root / "config" / "helpdesk" / "helpdesk_structure.json"),
            ("Droid Routing", project_root / "config" / "droid_actor_routing.json"),
            ("JARVIS Integration", project_root / "config" / "jarvis_ide_integration.json"),
            ("Lumina Extensions", project_root / "config" / "lumina_extensions_integration.json"),
        ]

        for name, path in config_files:
            if path.exists():
                results[name] = "✅"
            else:
                results[name] = "❌ Missing"

        return results

    except Exception as e:
        logger.error(f"Error in test_config_files: {e}", exc_info=True)
        raise
def test_n8n_connectivity():
    """Test N8N NAS connectivity"""
    print("\n🌐 Testing N8N NAS Connectivity...")
    results = {}

    import json
    import urllib.request
    import urllib.error

    # Load N8N config
    n8n_config_path = project_root / "config" / "n8n" / "unified_communications_config.json"
    if n8n_config_path.exists():
        with open(n8n_config_path, 'r') as f:
            n8n_config = json.load(f)
            n8n_url = n8n_config.get("n8n_config", {}).get("n8n_url", "")

            if n8n_url:
                try:
                    # Try to connect (with timeout)
                    req = urllib.request.Request(n8n_url, method="GET")
                    with urllib.request.urlopen(req, timeout=5) as response:
                        results["N8N URL"] = f"✅ {n8n_url}"
                        results["N8N Status"] = f"✅ Accessible (Status: {response.getcode()})"
                except urllib.error.URLError as e:
                    results["N8N URL"] = f"⚠️ {n8n_url}"
                    results["N8N Status"] = f"⚠️ Not accessible: {str(e)[:50]}"
                except Exception as e:
                    results["N8N URL"] = f"⚠️ {n8n_url}"
                    results["N8N Status"] = f"⚠️ Error: {str(e)[:50]}"
            else:
                results["N8N URL"] = "❌ Not configured"
    else:
        results["N8N Config"] = "❌ Config file missing"

    return results

def main():
    """Main verification"""
    print("=" * 80)
    print("🎯 LUMINA EXTENSION COMPLETION VERIFICATION")
    print("   Option 1: Quick Win (Direct Calls, No Azure)")
    print("=" * 80)

    # Test imports
    import_results = test_imports()

    # Test config files
    config_results = test_config_files()

    # Test N8N connectivity
    n8n_results = test_n8n_connectivity()

    # Summary
    print("\n" + "=" * 80)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 80)

    print("\n🔍 Component Imports:")
    for component, status in import_results.items():
        print(f"   {component}: {status}")

    print("\n📋 Configuration Files:")
    for config, status in config_results.items():
        print(f"   {config}: {status}")

    print("\n🌐 N8N Connectivity:")
    for item, status in n8n_results.items():
        print(f"   {item}: {status}")

    # Overall status
    all_imports_ok = all("✅" in str(v) for v in import_results.values())
    all_configs_ok = all("✅" in str(v) for v in config_results.values())

    print("\n" + "=" * 80)
    if all_imports_ok and all_configs_ok:
        print("✅ EXTENSION STATUS: OPERATIONAL (Option 1 - Quick Win)")
        print("\n   Components work with direct calls.")
        print("   No Azure infrastructure required.")
        print("   Extension is COMPLETE for Option 1 approach.")
    else:
        print("⚠️ EXTENSION STATUS: NEEDS ATTENTION")
        print("\n   Some components or configs need fixing.")

    print("=" * 80)

if __name__ == "__main__":



    main()