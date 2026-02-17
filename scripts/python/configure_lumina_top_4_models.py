#!/usr/bin/env python3
"""
Configure Lumina with Top 4 Recommended Models

Sets up auto-selection and ensures the top 4 models are properly configured.
"""

import json
import sys
import requests
from pathlib import Path
from typing import Dict, Any, List
import logging
logger = logging.getLogger("configure_lumina_top_4_models")


project_root = Path(__file__).parent.parent.parent

# Top 4 models configuration
TOP_4_MODELS = {
    "qwen2.5:72b": {
        "name": "ULTRON",
        "title": "ULTRON (qwen2.5:72b)",
        "endpoint": "http://localhost:11434",
        "context": 32768,
        "priority": 1,
        "description": "Primary - Best overall quality, large context window",
        "best_for": ["complex_code", "large_files", "architecture", "deep_reasoning"]
    },
    "codellama:13b": {
        "name": "KAIJU Code",
        "title": "KAIJU Code (codellama:13b)",
        "endpoint": "http://<NAS_PRIMARY_IP>:11434",
        "context": 8192,
        "priority": 2,
        "description": "Code specialist - Excellent for Python and code generation",
        "best_for": ["code_generation", "python", "bug_fixes", "code_explanations"]
    },
    "llama3.2:11b": {
        "name": "KAIJU General",
        "title": "KAIJU General (llama3.2:11b)",
        "endpoint": "http://<NAS_PRIMARY_IP>:11434",
        "context": 8192,
        "priority": 3,
        "description": "General purpose - Balanced performance for mixed tasks",
        "best_for": ["general_coding", "documentation", "code_review", "quick_questions"]
    },
    "qwen2.5-coder:1.5b-base": {
        "name": "KAIJU Fast",
        "title": "KAIJU Fast (qwen2.5-coder:1.5b)",
        "endpoint": "http://<NAS_PRIMARY_IP>:11434",
        "context": 4096,
        "priority": 4,
        "description": "Lightweight speed - Ultra-fast for quick tasks",
        "best_for": ["inline_completion", "quick_suggestions", "simple_tasks", "low_resource"]
    }
}

def check_model_availability(endpoint: str, model: str) -> bool:
    """Check if a model is available at an endpoint."""
    try:
        response = requests.get(f"{endpoint}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            return model in model_names or any(model in name for name in model_names)
        return False
    except:
        return False

def update_cursor_settings():
    try:
        """Update Cursor settings with top 4 models and auto-selection."""
        settings_file = project_root / ".cursor" / "settings.json"

        if not settings_file.exists():
            print(f"❌ Settings file not found: {settings_file}")
            return False

        print(f"📝 Reading settings from: {settings_file}")
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)

        # Update agent models with top 4
        agent_models = []

        # ULTRON (Primary)
        ultron_config = TOP_4_MODELS["qwen2.5:72b"]
        agent_models.append({
            "title": ultron_config["title"],
            "name": ultron_config["name"],
            "provider": "ollama",
            "model": "qwen2.5:72b",
            "apiBase": ultron_config["endpoint"],
            "contextLength": ultron_config["context"],
            "description": ultron_config["description"],
            "localOnly": True,
            "skipProviderSelection": True,
            "priority": ultron_config["priority"],
            "cluster": {
                "type": "virtual_hybrid",
                "nodes": [
                    {
                        "name": "ULTRON Local",
                        "endpoint": "http://localhost:11434",
                        "priority": 1
                    },
                    {
                        "name": "KAIJU",
                        "endpoint": "http://<NAS_PRIMARY_IP>:11434",
                        "priority": 2
                    }
                ],
                "routing": "load_balanced",
                "auto_selection": True,
                "selection_criteria": {
                    "complexity": {
                        "low": "qwen2.5-coder:1.5b-base",
                        "medium": "llama3.2:11b",
                        "high": "qwen2.5:72b"
                    },
                    "context_size": {
                        "small": "qwen2.5-coder:1.5b-base",
                        "medium": "llama3.2:11b",
                        "large": "qwen2.5:72b"
                    },
                    "task_type": {
                        "code_generation": "codellama:13b",
                        "code_review": "llama3.2:11b",
                        "documentation": "llama3.2:11b",
                        "architecture": "qwen2.5:72b",
                        "autocomplete": "qwen2.5-coder:1.5b-base"
                    }
                }
            }
        })

        # Add other top 3 models
        for model_key in ["codellama:13b", "llama3.2:11b", "qwen2.5-coder:1.5b-base"]:
            config = TOP_4_MODELS[model_key]
            agent_models.append({
                "title": config["title"],
                "name": config["name"],
                "provider": "ollama",
                "model": model_key,
                "apiBase": config["endpoint"],
                "contextLength": config["context"],
                "description": config["description"],
                "localOnly": True,
                "skipProviderSelection": True,
                "priority": config["priority"]
            })

        settings["cursor.agent.customModels"] = agent_models
        settings["cursor.agent.defaultModel"] = "ULTRON"

        # Enable auto-selection
        settings["cursor.agent.autoModelSelection"] = True
        settings["cursor.agent.adaptiveRouting"] = True

        # Write back
        print(f"💾 Writing updated settings to: {settings_file}")
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)

        print("✅ Settings updated!")
        return True

    except Exception as e:
        logger.error(f"Error in update_cursor_settings: {e}", exc_info=True)
        raise
def verify_models():
    """Verify which of the top 4 models are available."""
    print("=" * 70)
    print("🔍 Verifying Top 4 Models Availability")
    print("=" * 70)
    print()

    results = {}
    for model_key, config in TOP_4_MODELS.items():
        endpoint = config["endpoint"]
        print(f"Checking {config['title']} at {endpoint}...")
        available = check_model_availability(endpoint, model_key)
        results[model_key] = {
            "available": available,
            "config": config
        }
        status = "✅ Available" if available else "❌ Not Available"
        print(f"   {status}")
        print()

    # Summary
    print("=" * 70)
    print("📊 Summary")
    print("=" * 70)

    available_count = sum(1 for r in results.values() if r["available"])
    total_count = len(results)

    print(f"   Available Models: {available_count}/{total_count}")
    print()

    print("Available Models:")
    for model_key, result in results.items():
        if result["available"]:
            config = result["config"]
            print(f"   ✅ {config['title']} - {config['description']}")

    print()

    print("Missing Models:")
    for model_key, result in results.items():
        if not result["available"]:
            config = result["config"]
            print(f"   ❌ {config['title']} - Needs to be pulled")
            print(f"      Command: ollama pull {model_key}")
            print(f"      Endpoint: {config['endpoint']}")

    print()

    return available_count == total_count

def main():
    """Main function."""
    print("=" * 70)
    print("🚀 Configuring Lumina with Top 4 Models")
    print("=" * 70)
    print()

    # Verify models
    all_available = verify_models()

    # Update settings
    print()
    print("=" * 70)
    print("⚙️  Updating Configuration")
    print("=" * 70)
    print()

    success = update_cursor_settings()

    if success:
        print()
        print("=" * 70)
        print("✅ Configuration Complete!")
        print("=" * 70)
        print()
        print("📋 What was configured:")
        print("   ✅ Top 4 models added to agent configuration")
        print("   ✅ ULTRON set as default (with auto-selection)")
        print("   ✅ Auto-selection enabled with adaptive routing")
        print("   ✅ Selection criteria configured")
        print()
        print("💡 Next Steps:")
        print("   1. Reload Cursor IDE to apply changes")
        print("   2. Select 'ULTRON' as your agent model")
        print("   3. Auto-selection will pick the best model for each task")
        if not all_available:
            print("   4. Pull missing models on KAIJU if needed")
        print()
    else:
        print("❌ Configuration failed!")
        return 1

    return 0

if __name__ == "__main__":


    sys.exit(main())