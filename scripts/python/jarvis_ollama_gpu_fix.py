#!/usr/bin/env python3
"""
JARVIS Ollama GPU Fix
Diagnoses and fixes Ollama GPU utilization issues
Ensures Ollama uses GPU and maintains 50% utilization

Tags: #PERFORMANCE #GPU #OLLAMA @AUTO
"""

import sys
import subprocess
import requests
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISOllamaGPUFix")


class OllamaGPUFix:
    """Fix Ollama GPU utilization issues"""

    def __init__(self):
        self.logger = logger
        self.ollama_url = "http://localhost:11434"

    def check_gpu(self) -> Dict[str, Any]:
        """Check GPU status"""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total,name", 
                 "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                parts = result.stdout.strip().split(',')
                if len(parts) >= 4:
                    return {
                        "utilization": float(parts[0].strip()),
                        "memory_used_mb": float(parts[1].strip()),
                        "memory_total_mb": float(parts[2].strip()),
                        "name": parts[3].strip(),
                        "available": True
                    }
        except Exception as e:
            self.logger.warning(f"   ⚠️  GPU check failed: {e}")
        return {"available": False}

    def check_ollama_models(self) -> list:
        """Check available Ollama models"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                return response.json().get("models", [])
        except Exception as e:
            self.logger.warning(f"   ⚠️  Could not check models: {e}")
        return []

    def check_ollama_processes(self) -> list:
        """Check active Ollama processes"""
        try:
            response = requests.get(f"{self.ollama_url}/api/ps", timeout=5)
            if response.status_code == 200:
                return response.json().get("processes", [])
        except Exception as e:
            self.logger.warning(f"   ⚠️  Could not check processes: {e}")
        return []

    def load_model_with_gpu(self, model: str) -> bool:
        """Load model with explicit GPU configuration"""
        self.logger.info(f"   📦 Loading {model} with GPU acceleration...")

        try:
            # Use generate endpoint with GPU options
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": "Hello, this is a test to load the model on GPU.",
                    "stream": False,
                    "options": {
                        "num_gpu": 1,  # Explicitly use 1 GPU
                        "num_ctx": 4096,  # Context window
                        "num_predict": 50,  # Short prediction for faster load
                        "keep_alive": "10m"  # Keep in memory
                    }
                },
                timeout=180  # 3 minutes for large models
            )

            if response.status_code == 200:
                self.logger.info(f"   ✅ Model {model} loaded with GPU")
                return True
            else:
                self.logger.warning(f"   ⚠️  Model load failed: {response.status_code}")
        except requests.exceptions.Timeout:
            self.logger.warning(f"   ⚠️  Model load timeout - model may be very large")
        except Exception as e:
            self.logger.warning(f"   ⚠️  Model load error: {e}")

        return False

    def maintain_gpu_load(self, model: str, target_util: float = 50.0):
        """Maintain GPU load at target utilization"""
        self.logger.info(f"   🔄 Maintaining GPU load at {target_util}%...")

        prompts = [
            "What is artificial intelligence?",
            "Explain machine learning in one sentence.",
            "What is Python programming?",
            "Tell me about neural networks.",
            "What is deep learning?",
        ]

        for i in range(20):  # Run 20 inferences
            try:
                prompt = prompts[i % len(prompts)]

                response = requests.post(
                    f"{self.ollama_url}/api/generate",
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
                    gpu_status = self.check_gpu()
                    util = gpu_status.get("utilization", 0)
                    self.logger.info(f"   ✅ Inference {i+1}/20 - GPU: {util:.1f}%")

                    if util >= (target_util - 5):
                        self.logger.info(f"   ✅ GPU utilization reached target: {util:.1f}%")
                        break

                time.sleep(1)  # Small delay between requests
            except Exception as e:
                self.logger.warning(f"   ⚠️  Inference error: {e}")
                time.sleep(2)

    def diagnose_and_fix(self):
        """Diagnose and fix GPU utilization issues"""
        self.logger.info("="*80)
        self.logger.info("OLLAMA GPU DIAGNOSTIC & FIX")
        self.logger.info("="*80)

        # Check GPU
        gpu_status = self.check_gpu()
        if not gpu_status.get("available"):
            self.logger.error("   ❌ GPU not available")
            return {"success": False, "error": "GPU not available"}

        self.logger.info(f"   ✅ GPU: {gpu_status.get('name', 'Unknown')}")
        self.logger.info(f"   📊 Current Utilization: {gpu_status.get('utilization', 0):.1f}%")
        self.logger.info(f"   💾 Memory: {gpu_status.get('memory_used_mb', 0):.0f} MB / {gpu_status.get('memory_total_mb', 0):.0f} MB")

        # Check Ollama
        models = self.check_ollama_models()
        if not models:
            self.logger.error("   ❌ No models available in Ollama")
            return {"success": False, "error": "No models available"}

        self.logger.info(f"   ✅ Found {len(models)} models:")
        for model in models[:5]:  # Show first 5
            self.logger.info(f"      - {model.get('name', 'unknown')}")

        # Check active processes
        processes = self.check_ollama_processes()
        if processes:
            self.logger.info(f"   ✅ {len(processes)} active model(s):")
            for proc in processes:
                self.logger.info(f"      - {proc.get('model', 'unknown')}")
        else:
            self.logger.info("   ⚠️  No active models - loading one...")

        # Select SMALLEST model (good rule of thumb for efficiency)
        model_name = None
        smallest_priority = ["1b", "2b", "3b", "7b", "8b", "11b", "13b", "14b", "20b", "30b", "40b", "70b", "72b"]

        for priority in smallest_priority:
            for model in models:
                name = model.get("name", "").lower()
                if priority in name:
                    model_name = model.get("name", "")
                    self.logger.info(f"   ✅ Selected SMALLEST available model: {model_name}")
                    break
            if model_name:
                break

        if not model_name:
            model_name = models[0].get("name", "")
            self.logger.info(f"   📦 Selected model: {model_name}")

        # Load model with GPU
        if not processes or not any(p.get("model", "").startswith(model_name.split(":")[0]) for p in processes):
            if not self.load_model_with_gpu(model_name):
                return {"success": False, "error": "Failed to load model"}

        # Maintain GPU load
        self.maintain_gpu_load(model_name, target_util=50.0)

        # Final check
        final_gpu = self.check_gpu()
        final_util = final_gpu.get("utilization", 0)

        self.logger.info("="*80)
        self.logger.info("FINAL STATUS")
        self.logger.info("="*80)
        self.logger.info(f"GPU Utilization: {final_util:.1f}%")
        self.logger.info(f"Target: 50.0%")

        if abs(final_util - 50.0) <= 5:
            self.logger.info("   ✅ GPU utilization is BALANCED at 50%")
            return {"success": True, "utilization": final_util, "balanced": True}
        else:
            self.logger.warning(f"   ⚠️  GPU utilization: {final_util:.1f}% (target: 50.0%)")
            return {"success": True, "utilization": final_util, "balanced": False}


def main():
    try:
        import argparse

        parser = argparse.ArgumentParser(description="Ollama GPU Fix - Ensure 50% GPU utilization")
        parser.add_argument("--fix", action="store_true", help="Diagnose and fix GPU utilization")

        args = parser.parse_args()

        fixer = OllamaGPUFix()

        if args.fix:
            result = fixer.diagnose_and_fix()
            print(json.dumps(result, indent=2))
        else:
            # Default: run fix
            result = fixer.diagnose_and_fix()
            print(json.dumps(result, indent=2))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()