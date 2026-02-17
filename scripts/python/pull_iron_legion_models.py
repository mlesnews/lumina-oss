#!/usr/bin/env python3
"""
Pull Iron Legion Models
Automatically pulls all required models for Iron Legion Mark services
"""

import subprocess
import logging
import time
from typing import Dict, List, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Model mappings for each Iron Legion Mark
IRON_LEGION_MODELS = {
    "iron-legion-mark-i": "codellama:13b",
    "iron-legion-mark-ii": "llama3.2:11b",
    "iron-legion-mark-iii": "qwen2.5-coder:1.5b-base",
    "iron-legion-mark-iv": "llama3:8b",
    "iron-legion-mark-v": "mistral:7b",
    "iron-legion-mark-vi": "mixtral:8x7b",
    "iron-legion-mark-vii": "gemma:2b",
}


def check_container_running(container: str) -> bool:
    """Check if container is running"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={container}", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return container in result.stdout
    except Exception as e:
        logger.error(f"Error checking container {container}: {e}")
        return False


def pull_model(container: str, model: str) -> Tuple[bool, str]:
    """Pull model in container"""
    logger.info(f"📥 Pulling {model} in {container}...")

    try:
        process = subprocess.Popen(
            ["docker", "exec", container, "ollama", "pull", model],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Stream output
        output_lines = []
        for line in process.stdout:
            output_lines.append(line.strip())
            logger.info(f"  {line.strip()}")

        process.wait()

        if process.returncode == 0:
            logger.info(f"✅ Successfully pulled {model} in {container}")
            return True, "\n".join(output_lines)
        else:
            error = process.stderr.read()
            logger.error(f"❌ Failed to pull {model} in {container}: {error}")
            return False, error
    except Exception as e:
        logger.error(f"❌ Error pulling {model} in {container}: {e}")
        return False, str(e)


def verify_model(container: str, model: str) -> bool:
    """Verify model is available in container"""
    try:
        result = subprocess.run(
            ["docker", "exec", container, "ollama", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            return model in result.stdout
        return False
    except Exception as e:
        logger.error(f"Error verifying model in {container}: {e}")
        return False


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Pull Iron Legion Models")
    parser.add_argument(
        "--container",
        help="Pull model for specific container only"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Only verify models, don't pull"
    )

    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("🚀 IRON LEGION MODEL PULL")
    logger.info("=" * 80)

    containers_to_process = []
    if args.container:
        if args.container in IRON_LEGION_MODELS:
            containers_to_process = [args.container]
        else:
            logger.error(f"Unknown container: {args.container}")
            return
    else:
        containers_to_process = list(IRON_LEGION_MODELS.keys())

    results = {}

    for container in containers_to_process:
        model = IRON_LEGION_MODELS[container]

        logger.info(f"\n{'='*80}")
        logger.info(f"Processing: {container} → {model}")
        logger.info(f"{'='*80}")

        # Check container running
        if not check_container_running(container):
            logger.warning(f"⚠️ Container {container} is not running, skipping")
            results[container] = {"status": "skipped", "reason": "container_not_running"}
            continue

        # Verify model
        if verify_model(container, model):
            logger.info(f"✅ Model {model} already available in {container}")
            results[container] = {"status": "already_available", "model": model}
            continue

        if args.verify:
            logger.warning(f"❌ Model {model} not found in {container}")
            results[container] = {"status": "missing", "model": model}
            continue

        # Pull model
        success, output = pull_model(container, model)
        results[container] = {
            "status": "success" if success else "failed",
            "model": model,
            "output": output
        }

        if success:
            # Verify after pull
            time.sleep(2)
            if verify_model(container, model):
                logger.info(f"✅ Verified: {model} is now available in {container}")
            else:
                logger.warning(f"⚠️ Model pulled but verification failed")

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("📊 SUMMARY")
    logger.info("=" * 80)

    for container, result in results.items():
        status = result.get("status", "unknown")
        model = result.get("model", "unknown")

        if status == "success":
            logger.info(f"✅ {container}: {model} - Pulled successfully")
        elif status == "already_available":
            logger.info(f"✅ {container}: {model} - Already available")
        elif status == "failed":
            logger.error(f"❌ {container}: {model} - Pull failed")
        elif status == "missing":
            logger.warning(f"⚠️ {container}: {model} - Missing")
        elif status == "skipped":
            logger.warning(f"⚠️ {container}: {model} - Skipped ({result.get('reason')})")

    success_count = sum(1 for r in results.values() if r.get("status") in ["success", "already_available"])
    total_count = len(results)

    logger.info(f"\n✅ {success_count}/{total_count} containers have models available")

    if success_count == total_count:
        logger.info("🎉 All Iron Legion models are ready!")
    else:
        logger.warning("⚠️ Some models still need to be pulled")


if __name__ == "__main__":


    main()