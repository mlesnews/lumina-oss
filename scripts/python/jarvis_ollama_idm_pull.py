#!/usr/bin/env python3
"""
JARVIS Ollama Model Puller with IDM CLI
Pulls Ollama models using IDM CLI for all downloads

Tags: #AUTOMATION #IDM #MODELS @AUTO
"""

import sys
import json
import subprocess
import os
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from idm_kaiju_integration import IDMKaijuIntegration
    from download_gguf_with_idm import download_gguf_with_idm, get_gguf_url
except ImportError as e:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    IDMKaijuIntegration = None
    download_gguf_with_idm = None
    get_gguf_url = None
    logging.warning(f"Some imports failed: {e}")

logger = get_logger("JARVISOllamaIDM")


class OllamaIDMPuller:
    """
    Pull Ollama models using IDM CLI

    Uses IDM for all model downloads, then imports to Ollama.
    Works for both ULTRON (local) and KAIJU (remote/NAS).
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Load model mapping
        self.model_mapping_path = project_root / "config" / "ollama_model_mapping.json"
        self.model_mapping = self._load_model_mapping()

        # Initialize IDM integration
        self.idm = None
        if IDMKaijuIntegration:
            try:
                self.idm = IDMKaijuIntegration()
                if self.idm.is_available():
                    self.logger.info("✅ IDM integration available")
                else:
                    self.logger.warning("⚠️  IDM not available - will use fallback")
            except Exception as e:
                self.logger.warning(f"⚠️  IDM initialization failed: {e}")

        self.logger.info("✅ Ollama IDM Puller initialized")

    def _load_model_mapping(self) -> Dict[str, Any]:
        """Load Ollama model mapping from JSON"""
        try:
            if self.model_mapping_path.exists():
                with open(self.model_mapping_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                self.logger.warning(f"⚠️  Model mapping not found: {self.model_mapping_path}")
                return {}
        except Exception as e:
            self.logger.warning(f"⚠️  Failed to load model mapping: {e}")
            return {}

    def _get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get model info from mapping"""
        if not self.model_mapping:
            return None

        models = self.model_mapping.get("models", {})
        # Try exact match first
        if model_name in models:
            return models[model_name]

        # Try with different separators (colon vs hyphen)
        alt_name = model_name.replace(":", "-")
        if alt_name in models:
            return models[alt_name]

        # Try reverse (hyphen to colon)
        alt_name2 = model_name.replace("-", ":")
        if alt_name2 in models:
            return models[alt_name2]

        return None

    def _construct_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Construct model info from model name when mapping is missing"""
        # Common HuggingFace patterns (using public repositories - TheBloke/bartowski)
        base_name = model_name.split(":")[0].replace("-", "_")
        tag = model_name.split(":")[1] if ":" in model_name else "latest"

        # Try to construct common patterns (all use public repos - no auth required)
        common_repos = {
            "mixtral": "TheBloke/Mixtral-8x7B-v0.1-GGUF",
            "qwen2.5": "TheBloke/Qwen2.5-{size}-Instruct-GGUF",
            "qwen2.5_coder": "TheBloke/Qwen2.5-Coder-{size}-Instruct-GGUF",
            "qwen_vl": "TheBloke/Qwen2-VL-{size}-Instruct-GGUF",
            "llama3.2": "bartowski/Llama-3.2-{size}-Instruct-GGUF",
            "codellama": "TheBloke/CodeLlama-{size}-GGUF",
            "mistral": "TheBloke/Mistral-7B-v0.1-GGUF",
            "gemma": "bartowski/gemma-{size}-it-GGUF",
            "llava": "TheBloke/llava-v1.6-{size}-GGUF",
            "bakllava": "TheBloke/bakllava-1-GGUF",
        }

        for pattern, repo_template in common_repos.items():
            if base_name.startswith(pattern):
                # Extract size from tag
                size = tag.replace("b", "B") if "b" in tag else tag
                repo = repo_template.replace("{size}", size)

                # Construct filename
                filename = f"{base_name.replace('_', '-')}-{size}-instruct-q4_k_m.gguf"
                if "coder" in base_name:
                    filename = f"qwen2.5-coder-{size}-instruct-q4_k_m.gguf"
                elif "mixtral" in base_name:
                    filename = "mixtral-8x7b-v0.1.Q4_K_M.gguf"

                return {
                    "huggingface_repo": repo,
                    "gguf_filename": filename,
                    "model_name": model_name,
                    "size_gb": 0,  # Unknown
                    "constructed": True
                }

        return None

    def _check_model_available(self, endpoint: str, model_name: str) -> bool:
        """Check if model is already available on Ollama endpoint"""
        try:
            response = requests.get(f"{endpoint}/api/tags", timeout=5)
            if response.status_code == 200:
                available_models = response.json().get("models", [])
                for model in available_models:
                    if model.get("name", "").startswith(model_name.split(":")[0]):
                        return True
        except Exception as e:
            self.logger.debug(f"Could not check model availability: {e}")
        return False

    def pull_model_with_idm(
        self,
        model_name: str,
        endpoint: str = "http://localhost:11434",
        destination: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Pull Ollama model using IDM CLI

        Args:
            model_name: Ollama model name (e.g., "llama3.2:11b")
            endpoint: Ollama endpoint URL
            destination: Optional destination for GGUF file (defaults to IDM download path)

        Returns:
            Dict with success status and details
        """
        self.logger.info(f"📥 Pulling model via IDM: {model_name}")

        # Check if already available
        if self._check_model_available(endpoint, model_name):
            self.logger.info(f"   ✅ Model {model_name} already available")
            return {
                "success": True,
                "action": "already_available",
                "model": model_name
            }

        # Get model info from mapping
        model_info = self._get_model_info(model_name)
        if not model_info:
            # Try to construct URL from model name (IDM only - no Ollama fallback)
            self.logger.warning(f"   ⚠️  No mapping found for {model_name}")
            self.logger.info(f"   🔍 Attempting to construct HuggingFace URL from model name...")

            # Try common patterns
            constructed_info = self._construct_model_info(model_name)
            if constructed_info:
                model_info = constructed_info
                self.logger.info(f"   ✅ Constructed mapping for {model_name}")
            else:
                self.logger.error(f"   ❌ Cannot download {model_name} - no mapping found and cannot construct URL")
                self.logger.error(f"   ❌ IDM is required - cannot fall back to Ollama")
                return {
                    "success": False,
                    "error": f"No mapping found for {model_name} and cannot construct HuggingFace URL",
                    "model": model_name,
                    "note": "Please add mapping to config/ollama_model_mapping.json or ensure model name matches HuggingFace format"
                }

        # Use IDM to download GGUF file
        repo_id = model_info.get("huggingface_repo")
        gguf_filename = model_info.get("gguf_filename")
        size_gb = model_info.get("size_gb", 0)

        self.logger.info(f"   📦 Model: {model_name}")
        self.logger.info(f"   📦 Repo: {repo_id}")
        self.logger.info(f"   📦 File: {gguf_filename}")
        self.logger.info(f"   📦 Size: ~{size_gb}GB")

        # Check if file already exists on M drive before downloading
        if destination:
            dest_file = Path(destination) / gguf_filename
        elif os.path.exists("M:\\"):
            dest_file = Path("M:\\Ollama\\models\\gguf") / gguf_filename
        elif os.environ.get("OLLAMA_MODELS"):
            dest_file = Path(os.environ["OLLAMA_MODELS"]) / "gguf" / gguf_filename
        else:
            dest_file = None

        if dest_file and dest_file.exists():
            file_size = dest_file.stat().st_size
            if file_size > 0:
                self.logger.info(f"   ✅ Model file already exists: {gguf_filename}")
                self.logger.info(f"   📊 Size: {file_size:,} bytes ({file_size / (1024**3):.2f} GB)")
                self.logger.info(f"   ⏭️  Skipping download (file exists and appears valid)")
                return {
                    "success": True,
                    "action": "already_exists",
                    "model": model_name,
                    "repo_id": repo_id,
                    "gguf_filename": gguf_filename,
                    "size_gb": size_gb,
                    "file_path": str(dest_file),
                    "file_size": file_size,
                    "note": "Model file already exists on M drive, skipping download"
                }

        # Download via IDM
        if download_gguf_with_idm:
            try:
                self.logger.info(f"   🚀 Adding to IDM queue...")
                success = download_gguf_with_idm(
                    repo_id=repo_id,
                    filename=gguf_filename,
                    model_name=model_name,
                    destination=str(destination) if destination else None
                )

                if success:
                    self.logger.info(f"   ✅ Successfully added {model_name} to IDM queue")
                    self.logger.info(f"   📊 Monitor download progress in IDM")
                    self.logger.info(f"   ⚠️  After download completes, import to Ollama:")
                    self.logger.info(f"      ollama create {model_name} -f Modelfile")

                    return {
                        "success": True,
                        "action": "queued_in_idm",
                        "model": model_name,
                        "repo_id": repo_id,
                        "gguf_filename": gguf_filename,
                        "size_gb": size_gb,
                        "note": "Download queued in IDM. Import to Ollama after download completes."
                    }
                else:
                    self.logger.error(f"   ❌ Failed to add to IDM queue")
                    return {
                        "success": False,
                        "error": "IDM queue failed",
                        "model": model_name,
                        "note": "IDM is required - cannot fall back to Ollama"
                    }
            except Exception as e:
                self.logger.error(f"   ❌ IDM download failed: {e}")
                return {
                    "success": False,
                    "error": f"IDM download failed: {e}",
                    "model": model_name,
                    "note": "IDM is required - cannot fall back to Ollama"
                }
        else:
            self.logger.error(f"   ❌ IDM helper not available")
            return {
                "success": False,
                "error": "IDM helper not available",
                "model": model_name,
                "note": "IDM is required - cannot fall back to Ollama"
            }

    def _fallback_ollama_pull(self, model_name: str, endpoint: str) -> Dict[str, Any]:
        """
        DEPRECATED: Ollama fallback is disabled - IDM is required for all downloads.
        This method should never be called. If it is, it indicates a configuration error.
        """
        self.logger.error(f"   ❌ INTERNAL ERROR: Ollama fallback called for {model_name}")
        self.logger.error(f"   ❌ IDM is required - Ollama fallback is disabled")
        return {
            "success": False,
            "error": "Ollama fallback disabled - IDM is required for all downloads",
            "model": model_name,
            "note": "This should never happen - please report this error"
        }

    def pull_models_for_hardware(
        self,
        recommended_models: List[str],
        endpoint: str = "http://localhost:11434",
        priority: str = "smallest_first"
    ) -> Dict[str, Any]:
        """
        Pull models recommended for hardware, using IDM

        Args:
            recommended_models: List of recommended model names
            endpoint: Ollama endpoint URL
            priority: "smallest_first" or "recommended_order"

        Returns:
            Dict with results for each model
        """
        self.logger.info(f"📥 Pulling models for hardware (priority: {priority})...")

        # Sort models by priority
        if priority == "smallest_first":
            # Sort by size (smallest first)
            model_sizes = {}
            for model_name in recommended_models:
                model_info = self._get_model_info(model_name)
                if model_info:
                    model_sizes[model_name] = model_info.get("size_gb", 999)
                else:
                    model_sizes[model_name] = 999

            sorted_models = sorted(recommended_models, key=lambda m: model_sizes.get(m, 999))
        else:
            sorted_models = recommended_models

        results = {}
        for model_name in sorted_models:
            self.logger.info(f"\n{'='*60}")
            result = self.pull_model_with_idm(model_name, endpoint)
            results[model_name] = result

            if result.get("success"):
                # If already available or successfully queued, we can continue
                pass
            else:
                self.logger.warning(f"   ⚠️  Failed to pull {model_name}")

        return {
            "success": True,
            "results": results,
            "total": len(recommended_models),
            "successful": sum(1 for r in results.values() if r.get("success"))
        }


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Pull Ollama models using IDM CLI")
    parser.add_argument("model", nargs="?", help="Model name to pull (e.g., llama3.2:11b)")
    parser.add_argument("--endpoint", default="http://localhost:11434", help="Ollama endpoint")
    parser.add_argument("--hardware", action="store_true", help="Pull models recommended for hardware")
    parser.add_argument("--models", nargs="+", help="List of models to pull")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    puller = OllamaIDMPuller(project_root)

    if args.hardware:
        # Get recommended models from hardware scaler
        try:
            from jarvis_hardware_aware_gpu_scaler import HardwareAwareGPUScaler
            scaler = HardwareAwareGPUScaler(project_root)
            hardware = scaler.detect_hardware()
            recommendations = hardware.get("recommendations", {})
            recommended_models = recommendations.get("recommended_models", [])

            if recommended_models:
                result = puller.pull_models_for_hardware(recommended_models, args.endpoint)
                print(json.dumps(result, indent=2, default=str))
            else:
                print("No recommended models found")
        except Exception as e:
            logger.error(f"Failed to get hardware recommendations: {e}")
    elif args.models:
        # Pull multiple models
        results = {}
        for model in args.models:
            result = puller.pull_model_with_idm(model, args.endpoint)
            results[model] = result
        print(json.dumps(results, indent=2, default=str))
    elif args.model:
        # Pull single model
        result = puller.pull_model_with_idm(args.model, args.endpoint)
        print(json.dumps(result, indent=2, default=str))
    else:
        parser.print_help()


if __name__ == "__main__":


    main()