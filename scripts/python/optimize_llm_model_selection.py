#!/usr/bin/env python3
"""
Optimize LLM Model Selection
Checks available models and configures optimal model selection based on memory
#JARVIS #AI #LLM #OPTIMIZATION
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import requests

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("OptimizeLLMModelSelection")


class LLMModelOptimizer:
    """Optimize LLM model selection based on available resources"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.providers = {
            "local": "http://localhost:11434",
            "kaiju": "http://<NAS_PRIMARY_IP>:11434"
        }

    def get_available_models(self, provider: str) -> List[Dict[str, Any]]:
        """Get list of available models from a provider"""
        base_url = self.providers.get(provider)
        if not base_url:
            return []

        try:
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = []
                for model in data.get("models", []):
                    model_info = {
                        "name": model.get("name", ""),
                        "size": model.get("size", 0),
                        "modified": model.get("modified_at", ""),
                        "digest": model.get("digest", "")
                    }
                    models.append(model_info)
                return models
        except Exception as e:
            logger.warning(f"Could not get models from {provider}: {e}")

        return []

    def get_system_memory(self) -> Optional[float]:
        """Get available system memory in GB"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            # Return available memory in GB
            return memory.available / (1024 ** 3)
        except ImportError:
            logger.warning("psutil not available, cannot check memory")
            return None
        except Exception as e:
            logger.warning(f"Could not check memory: {e}")
            return None

    def recommend_models(self) -> Dict[str, Any]:
        """Recommend optimal models based on available resources"""
        results = {
            "system_memory_gb": None,
            "providers": {},
            "recommendations": []
        }

        # Check system memory
        memory_gb = self.get_system_memory()
        results["system_memory_gb"] = memory_gb

        if memory_gb:
            logger.info(f"💾 Available memory: {memory_gb:.2f} GB")

        # Check each provider
        for provider_name, base_url in self.providers.items():
            logger.info(f"🔍 Checking {provider_name} provider...")
            models = self.get_available_models(provider_name)

            if models:
                logger.info(f"   ✅ Found {len(models)} models")
                results["providers"][provider_name] = {
                    "available": True,
                    "models": models,
                    "count": len(models)
                }
            else:
                logger.warning(f"   ⚠️  No models found or provider unavailable")
                results["providers"][provider_name] = {
                    "available": False,
                    "models": [],
                    "count": 0
                }

        # Generate recommendations
        recommendations = []

        # If memory is limited, recommend smaller models
        if memory_gb and memory_gb < 50:
            recommendations.append({
                "priority": "high",
                "message": "System memory is limited",
                "suggestion": "Use smaller/quantized models (3B, 7B, or 13B instead of 72B)",
                "models": ["llama3.2:3b", "llama3.2:11b", "codellama:13b"]
            })

        # Check for lightweight models
        all_models = []
        for provider_data in results["providers"].values():
            all_models.extend([m["name"] for m in provider_data.get("models", [])])

        lightweight_models = [m for m in all_models if any(size in m.lower() for size in ["3b", "7b", "1.5b", "1b"])]
        if lightweight_models:
            recommendations.append({
                "priority": "medium",
                "message": "Lightweight models available",
                "suggestion": "Use lightweight models for faster responses",
                "models": lightweight_models[:5]  # Top 5
            })

        results["recommendations"] = recommendations

        return results

    def update_config(self, preferred_models: List[str]) -> bool:
        """Update local-first LLM config with preferred models"""
        config_file = self.project_root / "config" / "local_first_llm_config.json"

        try:
            import json

            # Load existing config
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
            else:
                config = {}

            # Update preferred model
            if preferred_models:
                config["preferred_model"] = preferred_models[0]
                config["fallback_models"] = preferred_models[1:] if len(preferred_models) > 1 else []

            # Save config
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)

            logger.info(f"✅ Updated config: {config_file}")
            return True

        except Exception as e:
            logger.error(f"❌ Error updating config: {e}")
            return False


def main():
    try:
        """CLI interface"""
        import argparse
        import json

        parser = argparse.ArgumentParser(description="Optimize LLM Model Selection")
        parser.add_argument("--update-config", action="store_true", help="Update config with recommendations")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        optimizer = LLMModelOptimizer(project_root)
        results = optimizer.recommend_models()

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print("=" * 70)
            print("   LLM MODEL OPTIMIZATION ANALYSIS")
            print("=" * 70)
            print("")

            if results["system_memory_gb"]:
                print(f"💾 System Memory: {results['system_memory_gb']:.2f} GB")
            print("")

            for provider_name, provider_data in results["providers"].items():
                if provider_data["available"]:
                    print(f"✅ {provider_name.upper()}: {provider_data['count']} models available")
                    for model in provider_data["models"][:5]:  # Show first 5
                        size_gb = model.get("size", 0) / (1024**3) if model.get("size") else 0
                        print(f"   • {model['name']} ({size_gb:.1f} GB)" if size_gb else f"   • {model['name']}")
                else:
                    print(f"❌ {provider_name.upper()}: Unavailable")
            print("")

            if results["recommendations"]:
                print("💡 Recommendations:")
                for rec in results["recommendations"]:
                    print(f"   [{rec['priority'].upper()}] {rec['message']}")
                    print(f"      {rec['suggestion']}")
                    if rec.get("models"):
                        print(f"      Models: {', '.join(rec['models'])}")
                print("")

                if args.update_config:
                    # Get recommended models
                    recommended_models = []
                    for rec in results["recommendations"]:
                        if rec.get("models"):
                            recommended_models.extend(rec["models"])

                    if recommended_models:
                        # Remove duplicates, keep order
                        unique_models = []
                        for m in recommended_models:
                            if m not in unique_models:
                                unique_models.append(m)

                        if optimizer.update_config(unique_models[:3]):  # Top 3
                            print("✅ Config updated with recommended models")
                        else:
                            print("❌ Failed to update config")

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())