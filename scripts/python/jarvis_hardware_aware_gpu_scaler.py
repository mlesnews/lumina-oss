#!/usr/bin/env python3
"""
JARVIS Hardware-Aware GPU Scaler
Scales GPU utilization appropriately for hardware and software configurations
Environment-wide scaling for ULTRON and KAIJU

Tags: #PERFORMANCE #GPU #SCALING #HARDWARE @AUTO
"""

import sys
import subprocess
import requests
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from hardware_detector import HardwareDetector
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    HardwareDetector = None

logger = get_logger("JARVISHardwareScaler")


class HardwareAwareGPUScaler:
    """
    Hardware-Aware GPU Scaler

    Scales GPU utilization based on:
    - GPU VRAM capacity
    - Available system memory
    - CPU cores
    - Model availability
    - Target 50% utilization
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.target_utilization = 50.0

        # Hardware detection
        if HardwareDetector:
            self.hardware_detector = HardwareDetector()
        else:
            self.hardware_detector = None

        # Ollama endpoints
        # KAIJU_NO_8 = Desktop PC at <NAS_IP> (NOT the NAS at <NAS_PRIMARY_IP>)
        self.endpoints = {
            "ultron": "http://localhost:11434",
            "kaiju": "http://<NAS_IP>:11434"  # KAIJU_NO_8 Desktop PC
        }

        self.logger.info("✅ Hardware-Aware GPU Scaler initialized")

    def detect_hardware(self) -> Dict[str, Any]:
        """Detect hardware specifications"""
        hardware = {
            "gpu": self._detect_gpu(),
            "cpu": self._detect_cpu(),
            "memory": self._detect_memory(),
            "recommendations": {}
        }

        # Generate recommendations based on hardware
        hardware["recommendations"] = self._generate_recommendations(hardware)

        return hardware

    def _detect_gpu(self) -> Dict[str, Any]:
        """Detect GPU specifications"""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total,memory.used,utilization.gpu", 
                 "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                parts = result.stdout.strip().split(',')
                if len(parts) >= 4:
                    name = parts[0].strip()
                    total_mb = float(parts[1].strip())
                    used_mb = float(parts[2].strip())
                    util = float(parts[3].strip())
                    total_gb = total_mb / 1024
                    used_gb = used_mb / 1024
                    available_gb = total_gb - used_gb

                    return {
                        "name": name,
                        "vram_total_gb": round(total_gb, 1),
                        "vram_used_gb": round(used_gb, 1),
                        "vram_available_gb": round(available_gb, 1),
                        "utilization_percent": util,
                        "available": True
                    }
        except Exception as e:
            self.logger.warning(f"   ⚠️  GPU detection failed: {e}")

        return {"available": False}

    def _detect_cpu(self) -> Dict[str, Any]:
        """Detect CPU specifications"""
        if self.hardware_detector:
            cpu_info = self.hardware_detector._detect_cpu()
            return cpu_info

        # Fallback detection
        try:
            import platform
            import os
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["powershell", "-Command", 
                     "Get-WmiObject Win32_Processor | Select-Object NumberOfCores,NumberOfLogicalProcessors | ConvertTo-Json"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    cpu_data = json.loads(result.stdout.strip())
                    if isinstance(cpu_data, list):
                        cpu_data = cpu_data[0]
                    return {
                        "cores": cpu_data.get("NumberOfCores", 0),
                        "logical_processors": cpu_data.get("NumberOfLogicalProcessors", 0)
                    }
        except:
            pass

        return {"cores": 8, "logical_processors": 16}  # Default fallback

    def _detect_memory(self) -> Dict[str, Any]:
        """Detect system memory"""
        if self.hardware_detector:
            mem_info = self.hardware_detector._detect_memory()
            return mem_info

        # Fallback
        return {"total_gb": 32, "available_for_llm": 25.6}

    def _generate_recommendations(self, hardware: Dict[str, Any]) -> Dict[str, Any]:
        """Generate scaling recommendations based on hardware"""
        gpu = hardware.get("gpu", {})
        cpu = hardware.get("cpu", {})
        memory = hardware.get("memory", {})

        if not gpu.get("available"):
            return {
                "model_size": "cpu_only",
                "gpu_layers": 0,
                "recommendation": "No GPU available - use CPU-only models"
            }

        vram_gb = gpu.get("vram_total_gb", 0)
        available_vram = gpu.get("vram_available_gb", vram_gb)
        cpu_cores = cpu.get("cores", 8)
        mem_gb = memory.get("total_gb", 32)

        # Model size recommendations based on available VRAM
        # Target: Use 50-70% of available VRAM for model
        target_vram_usage = available_vram * 0.6  # 60% of available VRAM

        if target_vram_usage >= 20:  # 20GB+ available
            model_size = "70B-405B"
            recommended_models = ["qwen2.5:72b", "llama3.1:70b", "mixtral:8x7b"]
            gpu_layers = 50  # Max layers
        elif target_vram_usage >= 16:  # 16-20GB
            model_size = "30B-70B"
            recommended_models = ["llama3.1:70b", "mixtral:8x7b", "codellama:34b"]
            gpu_layers = 40
        elif target_vram_usage >= 12:  # 12-16GB
            model_size = "13B-30B"
            recommended_models = ["llama3.2:11b", "codellama:13b", "mistral:7b"]
            gpu_layers = 35
        elif target_vram_usage >= 8:  # 8-12GB
            model_size = "7B-13B"
            recommended_models = ["llama3.2:11b", "llama3.2:3b", "mistral:7b", "codellama:7b"]
            gpu_layers = 30
        elif target_vram_usage >= 4:  # 4-8GB
            model_size = "3B-7B"
            recommended_models = ["llama3.2:3b", "phi3:3.8b", "gemma:2b"]
            gpu_layers = 20
        else:  # <4GB
            model_size = "1B-3B"
            recommended_models = ["llama3.2:1b", "phi3:mini", "gemma:2b"]
            gpu_layers = 10

        # For 50% GPU utilization, we want to use models that can maintain steady load
        # Smaller models can run more concurrent instances
        concurrent_models = max(1, int(available_vram / (target_vram_usage / 2)))

        return {
            "model_size": model_size,
            "recommended_models": recommended_models,
            "gpu_layers": gpu_layers,
            "target_vram_usage_gb": round(target_vram_usage, 1),
            "concurrent_models": concurrent_models,
            "recommendation": f"Use {model_size} models with {gpu_layers} GPU layers for optimal 50% utilization"
        }

    def find_optimal_model(self, endpoint: str, recommendations: Dict[str, Any]) -> Optional[str]:
        """Find optimal model based on hardware recommendations - STRICTLY follow hardware specs"""
        try:
            response = requests.get(f"{endpoint}/api/tags", timeout=5)
            if response.status_code == 200:
                available_models = response.json().get("models", [])
                recommended = recommendations.get("recommended_models", [])
                model_size = recommendations.get("model_size", "")

                # STRICT: Only use models that match hardware recommendations
                # Parse model size range (e.g., "13B-30B" means 13B to 30B)
                max_size = None
                if "-" in model_size:
                    parts = model_size.split("-")
                    if len(parts) == 2:
                        try:
                            max_size = int(parts[1].replace("B", "").strip())
                        except:
                            pass

                # First, try recommended models in order (they match hardware)
                for rec_model in recommended:
                    for avail_model in available_models:
                        model_name = avail_model.get("name", "").lower()
                        if rec_model.lower() in model_name or model_name in rec_model.lower():
                            self.logger.info(f"   ✅ Found hardware-appropriate model: {avail_model.get('name')}")
                            return avail_model.get("name")

                # If no recommended model, find smallest that fits hardware constraints
                if available_models and max_size:
                    # Filter by size - only use models within recommended range
                    size_priority = ["1b", "2b", "3b", "7b", "8b", "11b", "13b", "14b", "20b", "30b"]
                    for priority in size_priority:
                        try:
                            priority_size = int(priority.replace("b", ""))
                            if priority_size <= max_size:  # Only if within hardware limits
                                for model in available_models:
                                    model_name = model.get("name", "").lower()
                                    if priority in model_name:
                                        self.logger.info(f"   ✅ Selected hardware-appropriate model: {model.get('name')} (fits {model_size} range)")
                                        return model.get("name")
                        except:
                            continue

                # If still no match, try to pull recommended models using IDM
                if recommended:
                    self.logger.warning(f"   ⚠️  No suitable model found. Pulling recommended model via IDM...")
                    try:
                        from jarvis_ollama_idm_pull import OllamaIDMPuller
                        puller = OllamaIDMPuller(self.project_root)

                        # Try to pull the first recommended model (smallest)
                        for rec_model in recommended:
                            self.logger.info(f"   📥 Attempting to pull {rec_model} via IDM...")
                            result = puller.pull_model_with_idm(rec_model, endpoint)
                            if result.get("success"):
                                # Wait a bit and check again
                                import time
                                time.sleep(2)

                                # Re-check available models
                                response = requests.get(f"{endpoint}/api/tags", timeout=5)
                                if response.status_code == 200:
                                    available_models = response.json().get("models", [])
                                    for avail_model in available_models:
                                        model_name = avail_model.get("name", "").lower()
                                        if rec_model.lower() in model_name or model_name in rec_model.lower():
                                            self.logger.info(f"   ✅ Model {avail_model.get('name')} now available")
                                            return avail_model.get("name")

                                # If queued in IDM, return None (will need to wait for download)
                                if result.get("action") == "queued_in_idm":
                                    self.logger.warning(f"   ⚠️  Model queued in IDM. Wait for download to complete.")
                                    return None
                            break
                    except Exception as e:
                        self.logger.warning(f"   ⚠️  Failed to pull model via IDM: {e}")

                # If still no match, log warning
                if available_models:
                    self.logger.warning(f"   ⚠️  Available models don't match hardware recommendations ({model_size})")
                    self.logger.warning(f"   ⚠️  Consider pulling a smaller model: {', '.join(recommended[:2])}")
        except Exception as e:
            self.logger.warning(f"   ⚠️  Could not check models: {e}")
        return None

    def load_model_with_scaling(self, endpoint: str, model: str, recommendations: Dict[str, Any]) -> bool:
        """Load model with hardware-appropriate scaling"""
        gpu_layers = recommendations.get("gpu_layers", 0)

        self.logger.info(f"   📦 Loading {model} with {gpu_layers} GPU layers...")

        try:
            response = requests.post(
                f"{endpoint}/api/generate",
                json={
                    "model": model,
                    "prompt": "test",
                    "stream": False,
                    "options": {
                        "num_gpu": 1,
                        "num_gpu_layers": gpu_layers,  # Hardware-appropriate layers
                        "num_ctx": 4096,
                        "keep_alive": "10m"
                    }
                },
                timeout=180
            )

            if response.status_code == 200:
                self.logger.info(f"   ✅ Model {model} loaded with {gpu_layers} GPU layers")
                return True
        except Exception as e:
            self.logger.warning(f"   ⚠️  Model load failed: {e}")

        return False

    def maintain_target_utilization(self, endpoint: str, model: str, target: float = 50.0):
        """Maintain GPU at target utilization"""
        self.logger.info(f"   🔄 Maintaining GPU at {target}% utilization...")

        prompts = [
            "What is artificial intelligence?",
            "Explain machine learning briefly.",
            "What is Python programming?",
            "Tell me about neural networks.",
            "What is deep learning?",
        ]

        for i in range(30):  # Run multiple inferences
            try:
                prompt = prompts[i % len(prompts)]

                response = requests.post(
                    f"{endpoint}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "num_gpu": 1,
                            "num_ctx": 2048,
                            "keep_alive": "10m"
                        }
                    },
                    timeout=60
                )

                if response.status_code == 200:
                    # Check GPU utilization
                    gpu_status = self._detect_gpu()
                    util = gpu_status.get("utilization_percent", 0)
                    self.logger.info(f"   📊 Inference {i+1}/30 - GPU: {util:.1f}%")

                    if util >= (target - 5):
                        self.logger.info(f"   ✅ Target utilization reached: {util:.1f}%")
                        break

                time.sleep(1)
            except Exception as e:
                self.logger.warning(f"   ⚠️  Inference error: {e}")
                time.sleep(2)

    def scale_environment(self) -> Dict[str, Any]:
        """Scale GPU utilization across environment"""
        self.logger.info("="*80)
        self.logger.info("HARDWARE-AWARE GPU SCALING - ENVIRONMENT WIDE")
        self.logger.info("="*80)

        # Detect hardware
        hardware = self.detect_hardware()
        recommendations = hardware.get("recommendations", {})

        self.logger.info("HARDWARE DETECTED:")
        gpu = hardware.get("gpu", {})
        if gpu.get("available"):
            self.logger.info(f"   GPU: {gpu.get('name', 'Unknown')}")
            self.logger.info(f"   VRAM: {gpu.get('vram_total_gb', 0):.1f} GB total, {gpu.get('vram_available_gb', 0):.1f} GB available")
            self.logger.info(f"   Current Utilization: {gpu.get('utilization_percent', 0):.1f}%")
        else:
            self.logger.warning("   ⚠️  No GPU detected")
            return {"success": False, "error": "No GPU available"}

        self.logger.info("RECOMMENDATIONS:")
        self.logger.info(f"   Model Size: {recommendations.get('model_size', 'unknown')}")
        self.logger.info(f"   GPU Layers: {recommendations.get('gpu_layers', 0)}")
        self.logger.info(f"   Recommended Models: {', '.join(recommendations.get('recommended_models', [])[:3])}")

        # Scale each endpoint
        results = {}

        for env_name, endpoint in self.endpoints.items():
            self.logger.info(f"\n{'='*80}")
            self.logger.info(f"SCALING: {env_name.upper()} ({endpoint})")
            self.logger.info(f"{'='*80}")

            try:
                # Check endpoint availability
                response = requests.get(f"{endpoint}/api/tags", timeout=5)
                if response.status_code != 200:
                    self.logger.warning(f"   ⚠️  {env_name} not accessible")
                    results[env_name] = {"success": False, "error": "Not accessible"}
                    continue

                # Find optimal model
                model = self.find_optimal_model(endpoint, recommendations)
                if not model:
                    self.logger.warning(f"   ⚠️  No suitable model found on {env_name}")
                    results[env_name] = {"success": False, "error": "No model available"}
                    continue

                # Load model with scaling
                if self.load_model_with_scaling(endpoint, model, recommendations):
                    # Maintain target utilization
                    self.maintain_target_utilization(endpoint, model, self.target_utilization)

                    # Final check
                    final_gpu = self._detect_gpu()
                    final_util = final_gpu.get("utilization_percent", 0)

                    results[env_name] = {
                        "success": True,
                        "model": model,
                        "gpu_layers": recommendations.get("gpu_layers", 0),
                        "final_utilization": final_util,
                        "balanced": abs(final_util - self.target_utilization) <= 5
                    }

                    self.logger.info(f"   ✅ {env_name} scaled - GPU: {final_util:.1f}%")
                else:
                    results[env_name] = {"success": False, "error": "Failed to load model"}
            except Exception as e:
                self.logger.warning(f"   ⚠️  {env_name} scaling failed: {e}")
                results[env_name] = {"success": False, "error": str(e)}

        # Summary
        self.logger.info("\n" + "="*80)
        self.logger.info("SCALING SUMMARY")
        self.logger.info("="*80)

        for env_name, result in results.items():
            if result.get("success"):
                util = result.get("final_utilization", 0)
                model = result.get("model", "unknown")
                balanced = result.get("balanced", False)
                status = "✅ BALANCED" if balanced else "⚠️  PARTIAL"
                self.logger.info(f"{env_name.upper()}: {status} - {util:.1f}% GPU ({model})")
            else:
                self.logger.warning(f"{env_name.upper()}: ❌ FAILED - {result.get('error', 'unknown')}")

        return {
            "success": True,
            "hardware": hardware,
            "recommendations": recommendations,
            "results": results
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Hardware-Aware GPU Scaler - Environment Wide")
        parser.add_argument("--scale", action="store_true", help="Scale GPU utilization across environment")
        parser.add_argument("--detect", action="store_true", help="Detect hardware only")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        scaler = HardwareAwareGPUScaler(project_root)

        if args.detect:
            hardware = scaler.detect_hardware()
            print(json.dumps(hardware, indent=2, default=str))
        elif args.scale:
            result = scaler.scale_environment()
            print(json.dumps(result, indent=2, default=str))
        else:
            # Default: scale
            result = scaler.scale_environment()
            print(json.dumps(result, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()