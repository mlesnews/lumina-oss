#!/usr/bin/env python3
"""
Configure Laptop GPU-Accelerated Ollama (RTX 5090)

Configures Ollama on laptop to use RTX 5090 GPU for inference.
GPU uses VRAM (not disk space) - safe even with 92.6% disk usage.

Tags: #GPU #RTX5090 #OLLAMA #LAPTOP @JARVIS @LUMINA
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from typing import Dict, Any

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ConfigureLaptopGPUOllama")


def check_gpu():
    """Check if RTX 5090 is available"""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            gpu_info = result.stdout.strip()
            if "5090" in gpu_info or "RTX" in gpu_info:
                logger.info(f"✅ GPU detected: {gpu_info}")
                return True
        return False
    except FileNotFoundError:
        logger.warning("⚠️  nvidia-smi not found - GPU may not be available")
        return False
    except Exception as e:
        logger.warning(f"⚠️  Error checking GPU: {e}")
        return False


def configure_ollama_gpu():
    """Configure Ollama to use GPU"""
    logger.info("=" * 80)
    logger.info("🚀 CONFIGURING OLLAMA FOR RTX 5090 GPU")
    logger.info("=" * 80)
    logger.info("")

    # Check GPU
    if not check_gpu():
        logger.warning("⚠️  RTX 5090 not detected - continuing with CPU mode")

    # Set environment variables
    gpu_config = {
        "OLLAMA_NUM_GPU": "1",
        "OLLAMA_GPU_LAYERS": "35",  # Use GPU for most layers
        "CUDA_VISIBLE_DEVICES": "0"  # Use first GPU
    }

    logger.info("📝 GPU Configuration:")
    for key, value in gpu_config.items():
        logger.info(f"   {key}={value}")

    # Update Ollama config
    ollama_config_dir = Path.home() / ".ollama"
    ollama_config_file = ollama_config_dir / "config.json"

    config = {}
    if ollama_config_file.exists():
        try:
            with open(ollama_config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            pass

    # Add GPU settings
    config.update(gpu_config)

    try:
        ollama_config_dir.mkdir(parents=True, exist_ok=True)
        with open(ollama_config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        logger.info(f"✅ Updated Ollama config: {ollama_config_file}")
    except Exception as e:
        logger.error(f"❌ Error updating config: {e}")

    # Set system environment (Windows)
    try:
        for key, value in gpu_config.items():
            subprocess.run(
                ["setx", key, value],
                check=False,
                timeout=5
            )
        logger.info("✅ Set system environment variables")
    except Exception as e:
        logger.warning(f"⚠️  Could not set system env vars: {e}")

    logger.info("")
    logger.info("💡 GPU Configuration Complete!")
    logger.info("   - GPU uses VRAM (24GB available)")
    logger.info("   - Does NOT use disk space")
    logger.info("   - Safe with 92.6% disk usage")
    logger.info("")
    logger.info("⚠️  Restart Ollama to apply GPU settings:")
    logger.info("   - Restart Ollama Desktop")
    logger.info("   - Or: docker restart ollama-online")
    logger.info("")


def verify_gpu_usage():
    """Verify Ollama is using GPU"""
    logger.info("🔍 Verifying GPU usage...")

    try:
        # Check nvidia-smi
        result = subprocess.run(
            ["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory", "--format=csv"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            if "ollama" in result.stdout.lower():
                logger.info("✅ Ollama is using GPU!")
                print(result.stdout)
            else:
                logger.warning("⚠️  Ollama not detected in GPU processes")
                logger.info("   May need to restart Ollama")
    except Exception as e:
        logger.warning(f"⚠️  Could not verify GPU usage: {e}")


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Configure Laptop GPU for Ollama")
    parser.add_argument("--verify", action="store_true", help="Verify GPU usage")

    args = parser.parse_args()

    if args.verify:
        verify_gpu_usage()
    else:
        configure_ollama_gpu()
        verify_gpu_usage()


if __name__ == "__main__":

    main()