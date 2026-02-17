#!/usr/bin/env python3
"""
Optimize Ollama GPU Settings

Sets OLLAMA_NUM_GPU=1 to enable GPU acceleration for Ollama.
Target: 50% GPU utilization.

Tags: #GPU #OLLAMA #OPTIMIZATION @JARVIS @LUMINA @DOIT
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import Dict, Any
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("OptimizeOllamaGPU")


def optimize_ollama_gpu() -> Dict[str, Any]:
    """Optimize Ollama GPU settings"""
    logger.info("=" * 80)
    logger.info("🚀 OLLAMA GPU OPTIMIZATION")
    logger.info("=" * 80)
    logger.info("")

    result = {
        "environment_set": False,
        "ollama_restart_needed": False,
        "recommendations": []
    }

    # Set OLLAMA_NUM_GPU environment variable
    try:
        os.environ["OLLAMA_NUM_GPU"] = "1"
        logger.info("   ✅ Set OLLAMA_NUM_GPU=1 in environment")
        result["environment_set"] = True
    except Exception as e:
        logger.error(f"   ❌ Failed to set OLLAMA_NUM_GPU: {e}")

    # Check if Ollama is running
    try:
        result_ps = subprocess.run(
            ["ollama", "ps"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result_ps.returncode == 0:
            logger.info("   ✅ Ollama is running")
            logger.info("   ⚠️  Restart Ollama to apply GPU settings:")
            logger.info("      ollama serve (or restart Ollama service)")
            result["ollama_restart_needed"] = True
        else:
            logger.warning("   ⚠️  Ollama not running or not in PATH")
    except FileNotFoundError:
        logger.warning("   ⚠️  Ollama not found in PATH")
    except Exception as e:
        logger.warning(f"   ⚠️  Could not check Ollama: {e}")

    # Recommendations
    result["recommendations"] = [
        "Set OLLAMA_NUM_GPU=1 in system environment variables",
        "Restart Ollama service: ollama serve",
        "Verify GPU usage: nvidia-smi",
        "Check Ollama is using GPU: ollama ps",
        "Monitor GPU utilization: nvidia-smi -l 1"
    ]

    logger.info("")
    logger.info("📋 Recommendations:")
    for i, rec in enumerate(result["recommendations"], 1):
        logger.info(f"   {i}. {rec}")
    logger.info("")

    return result


if __name__ == "__main__":
    optimize_ollama_gpu()
