#!/usr/bin/env python3
"""
GPU Utilities Module

Provides helper functions for configuring GPU settings across the project.
"""

import logging
import os
import subprocess

logger = logging.getLogger("GPUUtils")


def set_ollama_gpu(num_gpus: int = 1) -> bool:
    """Set the OLLAMA_NUM_GPU environment variable.

    Args:
        num_gpus: Number of GPUs to expose to Ollama.

    Returns:
        True if the variable was set successfully.
    """
    try:
        os.environ["OLLAMA_NUM_GPU"] = str(num_gpus)
        logger.info(f"OLLAMA_NUM_GPU={num_gpus} set in process environment")
        # Persist to system environment on Windows
        if os.name == "nt":
            subprocess.run(["setx", "OLLAMA_NUM_GPU", str(num_gpus)], check=False, timeout=5)
            logger.info("OLLAMA_NUM_GPU set in system environment")
        return True
    except Exception as e:
        logger.warning(f"Failed to set OLLAMA_NUM_GPU: {e}")
        return False


def verify_docker_gpu_config(docker_compose_path: str) -> bool:
    """Verify that the docker-compose file contains GPU runtime.

    Args:
        docker_compose_path: Path to docker-compose.yml.

    Returns:
        True if GPU runtime is configured.
    """
    try:
        with open(docker_compose_path, encoding="utf-8") as f:
            content = f.read()
        return "runtime: nvidia" in content or "device_requests:" in content
    except Exception as e:
        logger.warning(f"Could not read docker-compose file: {e}")
        return False


def recommend_gpu_setup() -> list[str]:
    """Return a list of recommended GPU setup steps."""
    return [
        "Restart Ollama with OLLAMA_NUM_GPU=1",
        "Restart Docker containers with GPU support",
        "Monitor GPU usage with nvidia-smi -l 1",
        "Verify Ollama GPU with ollama ps",
    ]


# End of gpu_utils.py
