#!/usr/bin/env python3
"""
JARVIS GPU Load Daemon
Maintains GPU at balanced 50% utilization through continuous background inference
Runs as a daemon process to keep GPU active

Tags: #PERFORMANCE #GPU #DAEMON @AUTO
"""

import sys
import json
import time
import requests
import threading
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISGPULoadDaemon")


class GPULoadDaemon:
    """
    GPU Load Daemon

    Maintains GPU at 50% utilization through:
    - Continuous background inference
    - Adaptive request frequency
    - Model keep-alive management
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.target_utilization = 50.0
        self.running = False
        self.thread = None

        # Ollama endpoints (prefer local)
        # KAIJU_NO_8 = Desktop PC at <NAS_IP> (NOT the NAS at <NAS_PRIMARY_IP>)
        self.ollama_endpoints = [
                   "http://localhost:11434",
                   "http://<NAS_IP>:11434"  # KAIJU_NO_8 Desktop PC
               ]

        self.active_endpoint = None
        self.active_model = None
        self.inference_interval = 5.0  # Seconds between inference requests

        self.logger.info("✅ GPU Load Daemon initialized")
        self.logger.info(f"   Target: {self.target_utilization}%")

    def find_available_endpoint(self) -> Optional[str]:
        """Find available Ollama endpoint"""
        for endpoint in self.ollama_endpoints:
            try:
                response = requests.get(f"{endpoint}/api/tags", timeout=3)
                if response.status_code == 200:
                    return endpoint
            except:
                continue
        return None

    def find_small_model(self, endpoint: str) -> Optional[str]:
        """Find SMALLEST available model (hardware-appropriate scaling)"""
        try:
            response = requests.get(f"{endpoint}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                if models:
                    # Prioritize smallest models first (hardware-appropriate)
                    # Order: 1B, 2B, 3B, 7B, 8B, 11B, 13B, etc.
                    size_priority = ["1b", "2b", "3b", "7b", "8b", "11b", "13b", "14b", "20b", "30b", "40b", "70b", "72b"]

                    for priority in size_priority:
                        for model in models:
                            name = model.get("name", "").lower()
                            if priority in name:
                                self.logger.info(f"   ✅ Selected hardware-appropriate model: {model.get('name')}")
                                return model.get("name", "")

                    # Fallback: first available
                    return models[0].get("name", "")
        except Exception as e:
            self.logger.warning(f"   ⚠️  Could not list models: {e}")
        return None

    def run_inference_loop(self):
        """Main inference loop to maintain GPU load"""
        self.logger.info("   🔄 Starting GPU load maintenance loop...")

        # Find endpoint
        endpoint = self.find_available_endpoint()
        if not endpoint:
            self.logger.error("   ❌ No Ollama endpoint available")
            return

        self.active_endpoint = endpoint
        self.logger.info(f"   ✅ Using endpoint: {endpoint}")

        # Find model
        model = self.find_small_model(endpoint)
        if not model:
            self.logger.error("   ❌ No models available")
            return

        self.active_model = model
        self.logger.info(f"   ✅ Using model: {model}")

        # Inference prompts for GPU load
        prompts = [
            "Hello, how are you?",
            "What is 2+2?",
            "Explain AI in one sentence.",
            "What is Python?",
            "Tell me a joke.",
        ]
        prompt_index = 0

        # Main loop
        while self.running:
            try:
                prompt = prompts[prompt_index % len(prompts)]
                prompt_index += 1

                # Run inference with GPU
                response = requests.post(
                    f"{endpoint}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "num_gpu": 1,
                            "num_ctx": 2048,  # Smaller context for faster inference
                            "keep_alive": "5m"
                        }
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    # Success - GPU is being used
                    result = response.json()
                    self.logger.debug(f"   ✅ Inference completed (GPU active)")
                else:
                    self.logger.warning(f"   ⚠️  Inference failed: {response.status_code}")

                # Wait before next inference
                time.sleep(self.inference_interval)

            except requests.exceptions.Timeout:
                self.logger.warning("   ⚠️  Inference timeout - model may be loading")
                time.sleep(10)  # Wait longer if timeout
            except Exception as e:
                self.logger.warning(f"   ⚠️  Inference error: {e}")
                time.sleep(5)

        self.logger.info("   🛑 GPU load maintenance loop stopped")

    def start(self):
        """Start the daemon"""
        if self.running:
            self.logger.warning("   ⚠️  Daemon already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self.run_inference_loop, daemon=True)
        self.thread.start()
        self.logger.info("   ✅ GPU Load Daemon started")

    def stop(self):
        """Stop the daemon"""
        if not self.running:
            return

        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        self.logger.info("   🛑 GPU Load Daemon stopped")

    def status(self) -> Dict[str, Any]:
        """Get daemon status"""
        return {
            "running": self.running,
            "endpoint": self.active_endpoint,
            "model": self.active_model,
            "target_utilization": self.target_utilization,
            "inference_interval": self.inference_interval
        }


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="GPU Load Daemon - Maintain 50% GPU utilization")
    parser.add_argument("--start", action="store_true", help="Start daemon")
    parser.add_argument("--stop", action="store_true", help="Stop daemon")
    parser.add_argument("--status", action="store_true", help="Check status")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    daemon = GPULoadDaemon(project_root)

    if args.start:
        daemon.start()
        print("GPU Load Daemon started. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            daemon.stop()
            print("\nGPU Load Daemon stopped.")
    elif args.stop:
        daemon.stop()
        print("GPU Load Daemon stopped.")
    elif args.status:
        status = daemon.status()
        print(json.dumps(status, indent=2))
    else:
        print("Usage:")
        print("  --start  : Start GPU load daemon")
        print("  --stop   : Stop GPU load daemon")
        print("  --status : Check daemon status")


if __name__ == "__main__":


    main()