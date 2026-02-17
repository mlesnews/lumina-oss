#!/usr/bin/env python3
"""
Verify ULTRON Cluster Configuration

Verifies that ULTRON virtual hybrid cluster is properly configured and accessible.
"""

import json
import requests
import sys
from pathlib import Path
from typing import Dict, Any, List
import logging
logger = logging.getLogger("verify_ultron_cluster")


project_root = Path(__file__).parent.parent.parent

def check_ollama_endpoint(endpoint: str, model: str = None) -> Dict[str, Any]:
    """Check if an Ollama endpoint is accessible."""
    try:
        # Check if endpoint is up
        health_url = f"{endpoint}/api/tags"
        response = requests.get(health_url, timeout=5)

        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]

            return {
                "accessible": True,
                "models": model_names,
                "model_found": model in model_names if model else None,
                "total_models": len(models)
            }
        else:
            return {
                "accessible": False,
                "error": f"HTTP {response.status_code}",
                "models": []
            }
    except requests.exceptions.ConnectionError:
        return {
            "accessible": False,
            "error": "Connection refused",
            "models": []
        }
    except Exception as e:
        return {
            "accessible": False,
            "error": str(e),
            "models": []
        }

def verify_ultron_cluster():
    try:
        """Verify ULTRON cluster configuration."""
        print("=" * 70)
        print("🔍 ULTRON Virtual Hybrid Cluster Verification")
        print("=" * 70)
        print()

        settings_file = project_root / ".cursor" / "settings.json"

        if not settings_file.exists():
            print(f"❌ Settings file not found: {settings_file}")
            return False

        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)

        # Check agent models
        print("📋 Agent Model Configuration:")
        print("-" * 70)

        agent_models = settings.get("cursor.agent.customModels", [])
        default_model = settings.get("cursor.agent.defaultModel", "Not set")

        print(f"   Default Agent Model: {default_model}")
        print(f"   Available Agent Models: {len(agent_models)}")
        print()

        for i, model in enumerate(agent_models, 1):
            name = model.get("name", "Unknown")
            title = model.get("title", "Unknown")
            provider = model.get("provider", "Unknown")
            local_only = model.get("localOnly", False)
            api_base = model.get("apiBase", "Not set")
            has_cluster = "cluster" in model

            print(f"   {i}. {title} ({name})")
            print(f"      Provider: {provider}")
            print(f"      Local Only: {local_only}")
            print(f"      API Base: {api_base}")
            print(f"      Has Cluster Config: {has_cluster}")

            if has_cluster:
                cluster = model.get("cluster", {})
                cluster_type = cluster.get("type", "Unknown")
                nodes = cluster.get("nodes", [])
                print(f"      Cluster Type: {cluster_type}")
                print(f"      Cluster Nodes: {len(nodes)}")
                for node in nodes:
                    node_name = node.get("name", "Unknown")
                    node_endpoint = node.get("endpoint", "Unknown")
                    print(f"         - {node_name}: {node_endpoint}")

            print()

        # Check endpoints
        print("🌐 Endpoint Accessibility:")
        print("-" * 70)

        endpoints_to_check = [
            ("ULTRON Local", "http://localhost:11434", "qwen2.5:72b"),
            ("KAIJU", "http://<NAS_PRIMARY_IP>:11434", "llama3.2:3b"),
            ("ULTRON Router", "http://<NAS_PRIMARY_IP>:3008", "qwen2.5:72b"),
        ]

        results = {}
        for name, endpoint, model in endpoints_to_check:
            print(f"   Checking {name} ({endpoint})...")
            result = check_ollama_endpoint(endpoint, model)
            results[name] = result

            if result["accessible"]:
                print(f"      ✅ Accessible")
                print(f"      Models available: {result['total_models']}")
                if result["model_found"] is not None:
                    if result["model_found"]:
                        print(f"      ✅ Required model '{model}' found")
                    else:
                        print(f"      ⚠️  Required model '{model}' NOT found")
                        print(f"      Available models: {', '.join(result['models'][:5])}")
            else:
                print(f"      ❌ Not accessible: {result.get('error', 'Unknown error')}")
            print()

        # Summary
        print("=" * 70)
        print("📊 Summary")
        print("=" * 70)

        accessible_count = sum(1 for r in results.values() if r["accessible"])
        total_count = len(results)

        print(f"   Endpoints Accessible: {accessible_count}/{total_count}")
        print(f"   Default Agent Model: {default_model}")

        if default_model == "ULTRON":
            print("   ✅ ULTRON is set as default agent model")
        else:
            print(f"   ⚠️  ULTRON is NOT set as default (current: {default_model})")

        # Check for ULTRON cluster config
        ultron_model = next((m for m in agent_models if m.get("name") == "ULTRON"), None)
        if ultron_model and "cluster" in ultron_model:
            print("   ✅ ULTRON cluster configuration found")
            cluster_nodes = ultron_model["cluster"].get("nodes", [])
            print(f"   ✅ Cluster has {len(cluster_nodes)} nodes configured")
        else:
            print("   ❌ ULTRON cluster configuration NOT found")

        print()

        # Recommendations
        print("💡 Recommendations:")
        print("-" * 70)

        if default_model != "ULTRON":
            print("   1. Set ULTRON as default agent model in Cursor settings")

        if not ultron_model or "cluster" not in ultron_model:
            print("   2. Ensure ULTRON has cluster configuration with both nodes")

        inaccessible = [name for name, r in results.items() if not r["accessible"]]
        if inaccessible:
            print(f"   3. Fix connectivity to: {', '.join(inaccessible)}")

        missing_models = [
            name for name, r in results.items() 
            if r["accessible"] and r.get("model_found") is False
        ]
        if missing_models:
            print(f"   4. Pull required models on: {', '.join(missing_models)}")

        if not inaccessible and not missing_models and default_model == "ULTRON":
            print("   ✅ All systems operational!")

        print()

        return accessible_count == total_count

    except Exception as e:
        logger.error(f"Error in verify_ultron_cluster: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    success = verify_ultron_cluster()
    sys.exit(0 if success else 1)
