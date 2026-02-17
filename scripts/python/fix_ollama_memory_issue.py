#!/usr/bin/env python3
"""
Fix Ollama Memory Issue
Pulls smaller/quantized models that fit in available memory (14.8 GiB)
"""

import subprocess
import logging
import requests
from typing import List, Dict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Memory-efficient models that fit in 14.8 GiB
MEMORY_EFFICIENT_MODELS = [
    "llama3.2:3b",           # ~2GB - Very small, fast
    "llama3.2:1b",           # ~700MB - Minimal
    "gemma:2b",              # ~1.4GB - Small
    "qwen2.5:1.5b",          # ~1GB - Very small
    "mistral:7b-instruct-q4_0",  # Quantized - ~4GB
    "llama3:8b-instruct-q4_0",   # Quantized - ~4.5GB
    "codellama:7b-instruct-q4_0", # Quantized - ~4GB
]

OLLAMA_ENDPOINT = "http://localhost:11434"
OLLAMA_CONTAINER = "homelab-ollama"


def check_ollama_health() -> bool:
    """Check if Ollama is accessible"""
    try:
        response = requests.get(f"{OLLAMA_ENDPOINT}/api/tags", timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Ollama not accessible: {e}")
        return False


def get_current_models() -> List[str]:
    """Get list of currently available models"""
    try:
        response = requests.get(f"{OLLAMA_ENDPOINT}/api/tags", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return [model.get("name", "") for model in data.get("models", [])]
        return []
    except Exception as e:
        logger.error(f"Error getting model list: {e}")
        return []


def pull_model(model: str) -> bool:
    """Pull a model"""
    logger.info(f"📥 Pulling {model}...")
    try:
        result = subprocess.run(
            ["docker", "exec", OLLAMA_CONTAINER, "ollama", "pull", model],
            capture_output=True,
            text=True,
            timeout=1800  # 30 minutes max
        )

        if result.returncode == 0:
            logger.info(f"✅ Successfully pulled {model}")
            return True
        else:
            logger.error(f"❌ Failed to pull {model}: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        logger.warning(f"⏱️  Pull timeout for {model} (may still be downloading)")
        return False
    except Exception as e:
        logger.error(f"❌ Error pulling {model}: {e}")
        return False


def test_model_generation(model: str) -> bool:
    """Test if model can generate text"""
    logger.info(f"🧪 Testing {model} generation...")
    try:
        response = requests.post(
            f"{OLLAMA_ENDPOINT}/api/generate",
            json={
                "model": model,
                "prompt": "Hello",
                "stream": False,
                "options": {"num_predict": 10}
            },
            timeout=30
        )

        if response.status_code == 200:
            logger.info(f"✅ {model} generation successful")
            return True
        else:
            error_msg = response.text[:200]
            logger.error(f"❌ {model} generation failed: {error_msg}")
            return False
    except Exception as e:
        logger.error(f"❌ Error testing {model}: {e}")
        return False


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Fix Ollama Memory Issue")
    parser.add_argument(
        "--pull",
        action="store_true",
        help="Pull memory-efficient models"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test model generation"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List current models"
    )

    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("🔧 OLLAMA MEMORY ISSUE FIX")
    logger.info("=" * 80)

    # Check Ollama health
    if not check_ollama_health():
        logger.error("❌ Ollama is not accessible. Is the container running?")
        return

    # List current models
    current_models = get_current_models()
    logger.info(f"\n📋 Current models: {len(current_models)}")
    for model in current_models:
        logger.info(f"   - {model}")

    if args.list:
        return

    # Pull memory-efficient models
    if args.pull:
        logger.info("\n📥 Pulling memory-efficient models...")
        pulled_models = []

        for model in MEMORY_EFFICIENT_MODELS:
            # Skip if already available
            if model in current_models:
                logger.info(f"✅ {model} already available, skipping")
                pulled_models.append(model)
                continue

            if pull_model(model):
                pulled_models.append(model)

        logger.info(f"\n✅ Pulled {len(pulled_models)}/{len(MEMORY_EFFICIENT_MODELS)} models")

    # Test model generation
    if args.test:
        logger.info("\n🧪 Testing model generation...")
        current_models = get_current_models()

        # Test smallest models first
        test_models = [m for m in MEMORY_EFFICIENT_MODELS if m in current_models]

        if not test_models:
            logger.warning("⚠️  No memory-efficient models available to test")
            logger.info("   Run with --pull first")
            return

        # Test first available model
        test_model = test_models[0]
        if test_model_generation(test_model):
            logger.info(f"\n✅ Memory issue resolved! {test_model} works with available memory")
        else:
            logger.warning(f"\n⚠️  {test_model} still has issues")


if __name__ == "__main__":


    main()