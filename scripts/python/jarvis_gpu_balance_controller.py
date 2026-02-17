#!/usr/bin/env python3
"""
JARVIS GPU Balance Controller
Ensures GPU runs at balanced 50% utilization
Automatically configures Ollama and maintains GPU load

Tags: #PERFORMANCE #GPU #AUTOMATION @AUTO
"""

import sys
import subprocess
import requests
import time
import json
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

logger = get_logger("JARVISGPUBalance")


class GPUBalanceController:
    """Maintains GPU at 50% utilization"""

    def __init__(self):
        self.logger = logger
        self.target_util = 50.0
        self.ollama_url = "http://localhost:11434"

    def get_gpu_util(self) -> float:
        """Get current GPU utilization"""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return float(result.stdout.strip())
        except:
            pass
        return 0.0

    def ensure_model_loaded(self, model: str) -> bool:
        """Ensure a model is loaded with GPU"""
        try:
            # Check if model is already loaded
            ps_response = requests.get(f"{self.ollama_url}/api/ps", timeout=5)
            if ps_response.status_code == 200:
                processes = ps_response.json().get("processes", [])
                for proc in processes:
                    if proc.get("model", "").startswith(model.split(":")[0]):
                        self.logger.info(f"   ✅ Model {model} already loaded")
                        return True

            # Load model with GPU
            self.logger.info(f"   📦 Loading model {model} with GPU...")
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model,
                    "prompt": "test",
                    "stream": False,
                    "options": {
                        "num_gpu": 1,
                        "num_ctx": 2048,
                        "keep_alive": "10m"
                    }
                },
                timeout=120
            )

            if response.status_code == 200:
                self.logger.info(f"   ✅ Model {model} loaded with GPU")
                return True
        except Exception as e:
            self.logger.warning(f"   ⚠️  Failed to load model: {e}")
        return False

    def maintain_load(self, model: str = None):
        """Maintain GPU load - uses smallest available model if none specified"""
        if not model:
            # Auto-detect smallest model
            try:
                response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    if models:
                        # Prefer smallest models first
                        smallest_priority = ["1b", "2b", "3b", "7b", "8b", "11b", "13b"]
                        for priority in smallest_priority:
                            for m in models:
                                if priority in m.get("name", "").lower():
                                    model = m.get("name", "")
                                    self.logger.info(f"   ✅ Auto-selected smallest model: {model}")
                                    break
                            if model:
                                break
                        if not model:
                            model = models[0].get("name", "")
            except:
                model = "llama3.2:11b"  # Fallback
        """Maintain GPU load at 50%"""
        self.logger.info("="*80)
        self.logger.info("GPU BALANCE CONTROLLER - TARGET 50%")
        self.logger.info("="*80)

        # Get current utilization
        current = self.get_gpu_util()
        self.logger.info(f"Current GPU Utilization: {current:.1f}%")
        self.logger.info(f"Target: {self.target_util:.1f}%")

        if current < (self.target_util - 5):
            self.logger.info("   📈 GPU utilization too low - loading model and maintaining load...")

            # Ensure model is loaded
            if self.ensure_model_loaded(model):
                # Run continuous inference to maintain load
                self.logger.info("   🔄 Running continuous inference to maintain GPU load...")

                prompts = [
                    "What is artificial intelligence?",
                    "Explain machine learning briefly.",
                    "What is Python programming?",
                    "Tell me about neural networks.",
                ]

                for i in range(10):  # Run 10 inferences
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
                            new_util = self.get_gpu_util()
                            self.logger.info(f"   ✅ Inference {i+1}/10 - GPU: {new_util:.1f}%")

                            if new_util >= (self.target_util - 5):
                                self.logger.info(f"   ✅ GPU utilization reached target!")
                                break

                        time.sleep(2)
                    except Exception as e:
                        self.logger.warning(f"   ⚠️  Inference error: {e}")
                        time.sleep(5)

        # Final check
        final_util = self.get_gpu_util()
        self.logger.info("="*80)
        self.logger.info(f"Final GPU Utilization: {final_util:.1f}%")

        if abs(final_util - self.target_util) <= 5:
            self.logger.info("   ✅ GPU utilization is BALANCED at 50%")
        else:
            self.logger.warning(f"   ⚠️  GPU utilization: {final_util:.1f}% (target: {self.target_util:.1f}%)")

        self.logger.info("="*80)

        return {
            "current_utilization": final_util,
            "target_utilization": self.target_util,
            "balanced": abs(final_util - self.target_util) <= 5
        }


def main():
    try:
        import argparse

        parser = argparse.ArgumentParser(description="GPU Balance Controller - Maintain 50% GPU utilization")
        parser.add_argument("--model", default="llama3.2:11b", help="Model to use for GPU load")
        parser.add_argument("--maintain", action="store_true", help="Maintain GPU load continuously")

        args = parser.parse_args()

        controller = GPUBalanceController()

        if args.maintain:
            while True:
                result = controller.maintain_load(args.model)
                if result.get("balanced"):
                    logger.info("   ✅ GPU balanced - waiting 30s before next check...")
                    time.sleep(30)
                else:
                    time.sleep(10)
        else:
            result = controller.maintain_load(args.model)
            print(json.dumps(result, indent=2))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()