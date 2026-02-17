#!/usr/bin/env python3
"""
Register All Local AI Models with Azure AI Foundry

Discovers all local models (Ollama, Iron Legion, ULTRON) and registers them
with Azure AI Foundry for unified access through Microsoft AI Foundry extension.

Tags: #AZURE #AI_FOUNDRY #MODEL_REGISTRATION #CLUSTER @LUMINA
"""

import sys
import json
import os
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("RegisterLocalModels")


class LocalModelRegistry:
    """Register local models with Azure AI Foundry"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.config_dir = self.project_root / "config"
        self.config_dir.mkdir(exist_ok=True)

        # Load configurations
        self.model_mapping_file = self.config_dir / "ollama_model_mapping.json"
        self.iron_legion_config_file = self.config_dir / "iron_legion_cluster_config.json"
        self.azure_foundry_config_file = self.config_dir / "azure_ai_foundry_config.json"

        self.model_mapping = self._load_json(self.model_mapping_file, {})
        self.iron_legion_config = self._load_json(self.iron_legion_config_file, {})
        self.azure_foundry_config = self._load_json(self.azure_foundry_config_file, {})

    def _load_json(self, file_path: Path, default: Any = None) -> Any:
        """Load JSON file"""
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading {file_path}: {e}")
        return default if default is not None else {}

    def discover_ollama_models(self) -> List[Dict[str, Any]]:
        """Discover all Ollama models from M drive and local"""
        models = []

        # Check M drive first
        m_drive_paths = [
            "M:\\Ollama\\models",
            "M:\\Ollama\\models\\gguf",
        ]

        # Check local paths
        local_paths = [
            os.path.expanduser("~/.ollama/models"),
            os.path.join(os.environ.get("OLLAMA_MODELS", ""), "models") if os.environ.get("OLLAMA_MODELS") else None,
        ]

        all_paths = [p for p in m_drive_paths + local_paths if p and os.path.exists(p)]

        # Get models from mapping
        model_mappings = self.model_mapping.get("models", {})

        for model_name, model_info in model_mappings.items():
            models.append({
                "name": model_name,
                "display_name": model_info.get("model_name", model_name),
                "type": "ollama",
                "endpoint": "http://localhost:11434",
                "api_type": "ollama",
                "size_gb": model_info.get("size_gb", 0),
                "role": model_info.get("role", "general"),
                "capabilities": self._get_capabilities(model_info),
                "multimodal": model_info.get("multimodal", False),
                "supports": model_info.get("supports", []),
                "description": model_info.get("description", ""),
            })

        # Also check Ollama API for available models
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                ollama_models = response.json().get("models", [])
                for model in ollama_models:
                    model_name = model.get("name", "")
                    # Skip if already in mapping
                    if not any(m["name"] == model_name for m in models):
                        models.append({
                            "name": model_name,
                            "display_name": model_name,
                            "type": "ollama",
                            "endpoint": "http://localhost:11434",
                            "api_type": "ollama",
                            "size_gb": 0,
                            "role": "general",
                            "capabilities": ["text_generation"],
                            "multimodal": False,
                            "description": f"Ollama model: {model_name}",
                        })
        except Exception as e:
            logger.debug(f"Could not query Ollama API: {e}")

        return models

    def _get_capabilities(self, model_info: Dict[str, Any]) -> List[str]:
        """Extract capabilities from model info"""
        capabilities = []

        intent = model_info.get("intent", "")
        if "code" in intent.lower():
            capabilities.append("code_generation")
        if "vision" in intent.lower() or model_info.get("multimodal"):
            capabilities.append("vision_understanding")
            capabilities.append("image_analysis")
        if "reasoning" in intent.lower():
            capabilities.append("reasoning")
        if "general" in intent.lower():
            capabilities.append("text_generation")
            capabilities.append("conversation")

        # Add based on supports
        supports = model_info.get("supports", [])
        if "images" in supports:
            capabilities.append("image_understanding")
        if "videos" in supports:
            capabilities.append("video_analysis")

        if not capabilities:
            capabilities = ["text_generation"]

        return capabilities

    def discover_iron_legion_models(self) -> List[Dict[str, Any]]:
        """Discover Iron Legion cluster models"""
        models = []

        standalone = self.iron_legion_config.get("standalone_access", {})
        mark_models = standalone.get("models", {})

        for mark_id, mark_info in mark_models.items():
            models.append({
                "name": mark_id,
                "display_name": mark_info.get("name", mark_id),
                "type": "iron_legion",
                "endpoint": mark_info.get("endpoint", ""),
                "api_type": "openai_compatible",
                "model": mark_info.get("model", ""),
                "status": mark_info.get("status", "unknown"),
                "capabilities": ["expert_routing", "text_generation"],
                "cluster": "iron_legion",
                "description": f"Iron Legion {mark_info.get('name', mark_id)}",
            })

        # Add cluster endpoint
        cluster_info = self.iron_legion_config.get("cluster_info", {})
        if cluster_info.get("cluster_endpoint"):
            models.append({
                "name": "iron_legion_cluster",
                "display_name": "Iron Legion Cluster",
                "type": "iron_legion",
                "endpoint": cluster_info["cluster_endpoint"],
                "api_type": "expert_router",
                "capabilities": ["expert_routing", "load_balancing", "text_generation"],
                "cluster": "iron_legion",
                "description": "Iron Legion expert routing cluster",
            })

        return models

    def discover_ultron_models(self) -> List[Dict[str, Any]]:
        """Discover ULTRON models"""
        models = []

        # ULTRON local endpoint
        models.append({
            "name": "ultron_local",
            "display_name": "ULTRON Local",
            "type": "ultron",
            "endpoint": "http://localhost:11434",
            "api_type": "ollama",
            "capabilities": ["text_generation", "conversation"],
            "cluster": "ultron",
            "description": "ULTRON local Ollama instance",
        })

        return models

    def register_with_azure_foundry(self, models: List[Dict[str, Any]]) -> Dict[str, Any]:
        try:
            """Register models with Azure AI Foundry configuration"""
            # Update Azure Foundry config
            if "local_models" not in self.azure_foundry_config:
                self.azure_foundry_config["local_models"] = {}

            # Group by type
            ollama_models = [m for m in models if m["type"] == "ollama"]
            iron_legion_models = [m for m in models if m["type"] == "iron_legion"]
            ultron_models = [m for m in models if m["type"] == "ultron"]

            # Register Ollama models
            if ollama_models:
                self.azure_foundry_config["local_models"]["ollama"] = {
                    "endpoint": "http://localhost:11434",
                    "models": [m["name"] for m in ollama_models],
                    "model_details": {m["name"]: {
                        "display_name": m["display_name"],
                        "capabilities": m["capabilities"],
                        "multimodal": m.get("multimodal", False),
                        "size_gb": m.get("size_gb", 0),
                    } for m in ollama_models}
                }

            # Register Iron Legion
            if iron_legion_models:
                self.azure_foundry_config["local_models"]["iron_legion"] = {
                    "endpoint": self.iron_legion_config.get("cluster_info", {}).get("cluster_endpoint", "http://<NAS_IP>:3000"),
                    "models": {m["name"]: {
                        "endpoint": m["endpoint"],
                        "display_name": m["display_name"],
                        "model": m.get("model", ""),
                        "capabilities": m["capabilities"],
                    } for m in iron_legion_models}
                }

            # Register ULTRON
            if ultron_models:
                self.azure_foundry_config["local_models"]["ultron"] = {
                    "endpoint": "http://localhost:11434",
                    "models": [m["name"] for m in ultron_models],
                    "model_details": {m["name"]: {
                        "display_name": m["display_name"],
                        "capabilities": m["capabilities"],
                    } for m in ultron_models}
                }

            # Save updated config
            with open(self.azure_foundry_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.azure_foundry_config, f, indent=2, ensure_ascii=False)

            return {
                "registered": len(models),
                "ollama": len(ollama_models),
                "iron_legion": len(iron_legion_models),
                "ultron": len(ultron_models),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error in register_with_azure_foundry: {e}", exc_info=True)
            raise
    def generate_model_registry(self) -> Dict[str, Any]:
        try:
            """Generate complete model registry"""
            logger.info("=" * 80)
            logger.info("🔍 DISCOVERING LOCAL AI MODELS")
            logger.info("=" * 80)

            # Discover all models
            ollama_models = self.discover_ollama_models()
            iron_legion_models = self.discover_iron_legion_models()
            ultron_models = self.discover_ultron_models()

            all_models = ollama_models + iron_legion_models + ultron_models

            logger.info(f"✅ Discovered {len(all_models)} models:")
            logger.info(f"   - Ollama: {len(ollama_models)}")
            logger.info(f"   - Iron Legion: {len(iron_legion_models)}")
            logger.info(f"   - ULTRON: {len(ultron_models)}")

            # Register with Azure Foundry
            logger.info("\n" + "=" * 80)
            logger.info("📝 REGISTERING WITH AZURE AI FOUNDRY")
            logger.info("=" * 80)

            registration_result = self.register_with_azure_foundry(all_models)

            logger.info(f"✅ Registered {registration_result['registered']} models")
            logger.info(f"   Config saved to: {self.azure_foundry_config_file}")

            # Generate registry summary
            registry = {
                "timestamp": datetime.now().isoformat(),
                "total_models": len(all_models),
                "models_by_type": {
                    "ollama": len(ollama_models),
                    "iron_legion": len(iron_legion_models),
                    "ultron": len(ultron_models),
                },
                "models": all_models,
                "registration": registration_result,
            }

            # Save registry
            registry_file = self.project_root / "data" / "azure_foundry_model_registry.json"
            registry_file.parent.mkdir(parents=True, exist_ok=True)
            with open(registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Registry saved to: {registry_file}")

            return registry


        except Exception as e:
            self.logger.error(f"Error in generate_model_registry: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Register Local Models with Azure AI Foundry")
        parser.add_argument("--list", action="store_true", help="List discovered models")
        parser.add_argument("--register", action="store_true", help="Register models with Azure Foundry")
        parser.add_argument("--output", type=str, help="Output file for registry")

        args = parser.parse_args()

        registry = LocalModelRegistry()

        if args.list or args.register or not any([args.list, args.register]):
            result = registry.generate_model_registry()

            if args.list:
                print("\n📋 Discovered Models:")
                for model in result["models"]:
                    print(f"   {model['name']} ({model['type']}) - {model.get('endpoint', 'N/A')}")

            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"\n✅ Registry saved to: {args.output}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":

    main()