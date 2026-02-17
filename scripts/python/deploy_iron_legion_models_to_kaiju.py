#!/usr/bin/env python3
"""
Deploy Iron Legion Models to KAIJU
                    -LUM THE MODERN

After downloads complete, deploy models to KAIJU and restart containers.

Tags: #IRON_LEGION #DEPLOY #KAIJU #OLLAMA @JARVIS @LUMINA @DOIT
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("IronLegionDeploy")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("IronLegionDeploy")

# KAIJU connection
KAIJU_HOST = "<NAS_IP>"
KAIJU_USER = "mlesn"  # Adjust if needed

# Models to deploy
# Note: Ollama model names may differ from expected format
MODELS_TO_DEPLOY = {
    "llama3.2:11b": {
        "node": "Mark II",
        "container": "iron-legion-mark-ii-ollama",
        "port": 3002,
        "ollama_name": "llama3.2:latest"  # Actual Ollama model name
    },
    "mixtral:8x7b": {
        "node": "Mark VI",
        "container": "iron-legion-mark-vi-ollama",
        "port": 3006,
        "ollama_name": "mixtral:latest"  # Actual Ollama model name
    }
}

def run_ssh_command(command: str, host: str = KAIJU_HOST, user: str = KAIJU_USER) -> tuple[str, int]:
    """Run command via SSH"""
    ssh_cmd = ["ssh", f"{user}@{host}", command]
    try:
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.stdout, result.returncode
    except subprocess.TimeoutExpired:
        return "Command timed out", 1
    except Exception as e:
        return str(e), 1

def check_model_on_kaiju(model_name: str, container: str) -> bool:
    """Check if model exists on KAIJU"""
    logger.info(f"   Checking if {model_name} exists in {container}...")

    # Check via Ollama list
    command = f"docker exec {container} ollama list 2>/dev/null | Select-String -Pattern '{model_name}' || echo 'NOT_FOUND'"
    stdout, code = run_ssh_command(command)

    if "NOT_FOUND" in stdout or code != 0:
        return False

    return True

def pull_model_on_kaiju(ollama_name: str, container: str, display_name: str = None) -> bool:
    """Pull model into Ollama on KAIJU"""
    display = display_name or ollama_name
    logger.info(f"   Pulling {display} (Ollama: {ollama_name}) into container {container}...")
    logger.info(f"   ⏳ This may take several minutes for large models...")

    command = f"docker exec {container} ollama pull {ollama_name}"
    stdout, code = run_ssh_command(command)

    if code == 0:
        logger.info(f"   ✅ {display} pulled successfully")
        return True
    else:
        logger.error(f"   ❌ Failed to pull {display}: {stdout}")
        return False

def restart_container(container_name: str) -> bool:
    """Restart Iron Legion container"""
    logger.info(f"   Restarting container {container_name}...")

    command = f"docker restart {container_name}"
    stdout, code = run_ssh_command(command)

    if code == 0:
        logger.info(f"   ✅ Container {container_name} restarted")
        return True
    else:
        logger.error(f"   ❌ Failed to restart {container_name}: {stdout}")
        return False

def deploy_model(model_key: str, model_info: Dict) -> bool:
    """Deploy a model to KAIJU"""
    logger.info("=" * 80)
    logger.info(f"🚀 Deploying: {model_key}")
    logger.info(f"   Node: {model_info['node']} (Port {model_info['port']})")
    logger.info("=" * 80)

    # Get Ollama model name (use ollama_name if specified, otherwise use model_key)
    ollama_name = model_info.get("ollama_name", model_key)

    # Check if model already exists
    if check_model_on_kaiju(ollama_name, model_info["container"]):
        logger.info(f"   ✅ {model_key} (Ollama: {ollama_name}) already exists on KAIJU")
    else:
        # Pull model
        if not pull_model_on_kaiju(ollama_name, model_info["container"], model_key):
            return False

    # Restart container
    if not restart_container(model_info["container"]):
        return False

    logger.info(f"   ✅ {model_key} deployment complete")
    return True

def main():
    """Main function"""
    logger.info("=" * 80)
    logger.info("🚀 DEPLOY IRON LEGION MODELS TO KAIJU")
    logger.info("                    -LUM THE MODERN")
    logger.info("=" * 80)
    logger.info(f"   KAIJU Host: {KAIJU_HOST}")
    logger.info("=" * 80)

    # Deploy each model
    results = {}
    for model_key, model_info in MODELS_TO_DEPLOY.items():
        success = deploy_model(model_key, model_info)
        results[model_key] = success
        logger.info("")

    # Summary
    logger.info("=" * 80)
    logger.info("📊 DEPLOYMENT SUMMARY")
    logger.info("=" * 80)

    for model_key, success in results.items():
        model_info = MODELS_TO_DEPLOY[model_key]
        status = "✅ Deployed" if success else "❌ Failed"
        logger.info(f"   {status}: {model_key} ({model_info['node']})")

    logger.info("")
    logger.info("💡 Next Steps:")
    logger.info("   1. Verify model assignment:")
    logger.info("      python scripts/python/fix_iron_legion_model_assignments.py")
    logger.info("   2. Run battle test Phase 1:")
    logger.info("      python scripts/python/battletest_ultron_iron_legion_comprehensive.py --phase 1")
    logger.info("=" * 80)

    return 0 if all(results.values()) else 1

if __name__ == "__main__":


    sys.exit(main())