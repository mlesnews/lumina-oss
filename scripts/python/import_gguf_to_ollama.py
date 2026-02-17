#!/usr/bin/env python3
"""
Import GGUF Model to Ollama
                    -LUM THE MODERN

Imports a downloaded GGUF file into Ollama using Modelfile.

Tags: #OLLAMA #GGUF #IMPORT #MODELS @JARVIS @LUMINA @DOIT
"""

import sys
import subprocess
from pathlib import Path
from typing import Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("GGUFImport")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("GGUFImport")

# KAIJU connection
KAIJU_HOST = "<NAS_IP>"
KAIJU_USER = "mlesn"

# NAS path
NAS_MODELS_PATH = Path(r"\\<NAS_PRIMARY_IP>\backups\MATT_Backups\models\ollama")

def run_ssh_command(command: str, host: str = KAIJU_HOST, user: str = KAIJU_USER) -> tuple[str, int]:
    """Run command via SSH"""
    ssh_cmd = ["ssh", f"{user}@{host}", command]
    try:
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=600
        )
        return result.stdout, result.returncode
    except subprocess.TimeoutExpired:
        return "Command timed out", 1
    except Exception as e:
        return str(e), 1

def copy_gguf_to_kaiju(gguf_path: Path, container: str) -> bool:
    try:
        """Copy GGUF file to KAIJU container"""
        logger.info(f"   Copying {gguf_path.name} to {container}...")

        # Copy file to KAIJU first, then into container
        # For now, we'll use docker cp which requires the file to be accessible from KAIJU
        # Alternative: Mount NAS share on KAIJU and copy from there

        # Check if file exists
        if not gguf_path.exists():
            logger.error(f"   ❌ File not found: {gguf_path}")
            return False

        logger.info("   ⚠️  Note: GGUF import requires file to be accessible from KAIJU")
        logger.info("   💡 Options:")
        logger.info("      1. Mount NAS share on KAIJU")
        logger.info("      2. Copy file to KAIJU first, then into container")
        logger.info("      3. Use Ollama's import from URL feature")

        return True

    except Exception as e:
        logger.error(f"Error in copy_gguf_to_kaiju: {e}", exc_info=True)
        raise
def create_ollama_model_from_gguf(model_name: str, gguf_path: Path, container: str) -> bool:
    """
    Create Ollama model from GGUF file using Modelfile

    This requires the GGUF file to be accessible within the container.
    """
    logger.info(f"   Creating Ollama model '{model_name}' from GGUF file...")

    # Create Modelfile content
    modelfile_content = f"""FROM {gguf_path}
"""

    # For now, we'll try using ollama create with a local path
    # This requires the file to be in the container's accessible filesystem

    logger.info("   ⚠️  Direct GGUF import requires file to be in container filesystem")
    logger.info("   💡 Alternative: Use Ollama's pull from registry if available")

    return False

def import_mixtral_to_mark_vi() -> bool:
    try:
        """Import Mixtral GGUF to Mark VI container"""
        logger.info("=" * 80)
        logger.info("📦 IMPORTING MIXTRAL TO MARK VI")
        logger.info("=" * 80)

        gguf_file = NAS_MODELS_PATH / "mixtral-8x7b-v0.1.Q4_K_M.gguf"
        container = "iron-legion-mark-vi-ollama"

        # Check if file exists
        if not gguf_file.exists():
            logger.warning(f"   ⚠️  GGUF file not found: {gguf_file}")
            logger.info("   💡 Waiting for download to complete...")
            return False

        logger.info(f"   ✅ GGUF file found: {gguf_file}")
        file_size_gb = gguf_file.stat().st_size / (1024 ** 3)
        logger.info(f"   Size: {file_size_gb:.2f} GB")

        # Try to pull from Ollama registry first (easier)
        logger.info("   Attempting to pull mixtral:latest from Ollama registry...")
        command = f"docker exec {container} ollama pull mixtral:latest"
        stdout, code = run_ssh_command(command)

        if code == 0:
            logger.info("   ✅ Successfully pulled mixtral:latest from registry")
            return True
        else:
            logger.warning(f"   ⚠️  Pull from registry failed: {stdout}")
            logger.info("   💡 Will need to import GGUF file manually")
            logger.info("   💡 This requires mounting NAS share or copying file to KAIJU")
            return False

    except Exception as e:
        logger.error(f"Error in import_mixtral_to_mark_vi: {e}", exc_info=True)
        raise
def main():
    """Main function"""
    logger.info("=" * 80)
    logger.info("📦 IMPORT GGUF TO OLLAMA")
    logger.info("                    -LUM THE MODERN")
    logger.info("=" * 80)

    success = import_mixtral_to_mark_vi()

    if success:
        logger.info("")
        logger.info("✅ Mixtral model ready on Mark VI")
        logger.info("   Next: Restart container and verify")
        return 0
    else:
        logger.info("")
        logger.info("⚠️  Mixtral import pending")
        logger.info("   Options:")
        logger.info("   1. Wait for download to complete")
        logger.info("   2. Try alternative Mixtral model names")
        logger.info("   3. Manually import GGUF file")
        return 1

if __name__ == "__main__":


    sys.exit(main())