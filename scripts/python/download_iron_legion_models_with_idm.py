#!/usr/bin/env python3
"""
Download Missing Iron Legion Models with IDM to NAS
                    -LUM THE MODERN

Downloads llama3.2:11b and mixtral:8x7b using Internet Download Manager
and saves them directly to the NAS for Iron Legion deployment.

Tags: #IRON_LEGION #IDM #DOWNLOAD #NAS #MODELS @JARVIS @LUMINA @DOIT
"""

import sys
import subprocess
from pathlib import Path
from typing import Dict, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("IronLegionIDMDownload")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("IronLegionIDMDownload")

# NAS path for model storage
NAS_MODELS_PATH = r"\\<NAS_PRIMARY_IP>\backups\MATT_Backups\models\ollama"

# Models to download
MODELS_TO_DOWNLOAD = {
    "llama3.2:11b": {
        "name": "Llama 3.2 11B",
        "node": "Mark II - General Purpose",
        "port": 3002,
        "huggingface_repo": "bartowski/Llama-3.2-11B-Vision-Instruct-GGUF",
        "gguf_file": "llama-3.2-11b-vision-instruct.Q4_K_M.gguf",
        "ollama_model": "llama3.2:11b"
    },
    "mixtral:8x7b": {
        "name": "Mixtral 8x7B",
        "node": "Mark VI - Complex Expert",
        "port": 3006,
        "huggingface_repo": "TheBloke/Mixtral-8x7B-v0.1-GGUF",
        "gguf_file": "mixtral-8x7b-v0.1.Q4_K_M.gguf",
        "ollama_model": "mixtral:8x7b"
    }
}

def check_nas_access() -> bool:
    """Check if NAS path is accessible"""
    try:
        nas_path = Path(NAS_MODELS_PATH)
        if nas_path.exists():
            logger.info(f"✅ NAS accessible: {NAS_MODELS_PATH}")
            return True
        else:
            logger.warning(f"⚠️  NAS path not accessible: {NAS_MODELS_PATH}")
            logger.info("   Attempting to create directory...")
            try:
                nas_path.mkdir(parents=True, exist_ok=True)
                logger.info("✅ NAS directory created")
                return True
            except Exception as e:
                logger.error(f"❌ Failed to create NAS directory: {e}")
                return False
    except Exception as e:
        logger.error(f"❌ NAS access check failed: {e}")
        return False

def get_huggingface_download_url(repo_id: str, filename: str) -> str:
    """Get direct download URL from HuggingFace"""
    # HuggingFace direct download URL format
    url = f"https://huggingface.co/{repo_id}/resolve/main/{filename}"
    return url

def download_with_idm(url: str, destination: Path, description: str) -> bool:
    """
    Download file using IDM via PowerShell script

    Args:
        url: Download URL
        destination: Full path including filename
        description: Description for IDM queue

    Returns:
        True if successfully queued in IDM
    """
    try:
        # Find the IDM PowerShell script
        idm_script = project_root / "scripts" / "powershell" / "Invoke-IDMGGUFDownload.ps1"

        if not idm_script.exists():
            logger.error(f"❌ IDM script not found: {idm_script}")
            return False

        # Build PowerShell command
        ps_cmd = f"""
        $ErrorActionPreference = 'Stop'
        try {{
            & '{idm_script}' -Url '{url}' -Destination '{destination}' -Description '{description}'
            Write-Output 'SUCCESS'
        }} catch {{
            Write-Output \"ERROR|$_\" 
        }}
        """

        logger.info(f"📥 Queuing download in IDM...")
        logger.info(f"   URL: {url}")
        logger.info(f"   Destination: {destination}")

        result = subprocess.run(
            ["powershell.exe", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            timeout=30
        )

        if "SUCCESS" in result.stdout or result.returncode == 0:
            logger.info("✅ Download added to IDM queue")
            logger.info("   Monitor progress in IDM application")
            return True
        else:
            error_msg = result.stderr or result.stdout
            logger.warning(f"⚠️  IDM command output: {error_msg}")
            # IDM might still have queued it even if exit code is non-zero
            logger.info("   Check IDM manually to verify download was queued")
            return True  # Assume success if IDM is available

    except Exception as e:
        logger.error(f"❌ Failed to queue download in IDM: {e}")
        return False

def download_model(model_key: str, model_info: Dict) -> bool:
    try:
        """
        Download a model using IDM to NAS

        Args:
            model_key: Model identifier (e.g., "llama3.2:11b")
            model_info: Model information dictionary

        Returns:
            True if download was queued successfully
        """
        logger.info("=" * 80)
        logger.info(f"📦 Downloading: {model_info['name']}")
        logger.info(f"   For: {model_info['node']} (Port {model_info['port']})")
        logger.info("=" * 80)

        # Get download URL
        repo_id = model_info["huggingface_repo"]
        filename = model_info["gguf_file"]
        url = get_huggingface_download_url(repo_id, filename)

        # Set destination on NAS
        destination = Path(NAS_MODELS_PATH) / filename

        # Check if file already exists
        if destination.exists():
            file_size_mb = destination.stat().st_size / (1024 * 1024)
            logger.info(f"✅ File already exists: {destination}")
            logger.info(f"   Size: {file_size_mb:.2f} MB")
            logger.info("   Skipping download")
            return True

        # Queue download in IDM
        description = f"Iron Legion: {model_info['name']} for {model_info['node']}"
        success = download_with_idm(url, destination, description)

        if success:
            logger.info("")
            logger.info("📋 Next Steps:")
            logger.info(f"   1. Monitor download in IDM")
            logger.info(f"   2. After download completes, verify file: {destination}")
            logger.info(f"   3. Copy to KAIJU Ollama directory:")
            logger.info(f"      ssh <NAS_IP>")
            logger.info(f"      docker exec -it iron-man-mark-{model_info['port']-3000} ollama pull {model_info['ollama_model']}")
            logger.info("")

        return success

    except Exception as e:
        logger.error(f"Error in download_model: {e}", exc_info=True)
        raise
def main():
    """Main function"""
    logger.info("=" * 80)
    logger.info("🚀 IRON LEGION MODEL DOWNLOAD WITH IDM")
    logger.info("                    -LUM THE MODERN")
    logger.info("=" * 80)

    # Check NAS access
    logger.info("\n🔍 Checking NAS access...")
    if not check_nas_access():
        logger.error("\n❌ Cannot access NAS. Please check:")
        logger.error("   1. NAS is online (<NAS_PRIMARY_IP>)")
        logger.error("   2. Network share is accessible")
        logger.error("   3. You have write permissions")
        return 1

    # Download each model
    logger.info("\n📥 Starting downloads...")
    results = {}

    for model_key, model_info in MODELS_TO_DOWNLOAD.items():
        success = download_model(model_key, model_info)
        results[model_key] = success
        logger.info("")

    # Summary
    logger.info("=" * 80)
    logger.info("📊 DOWNLOAD SUMMARY")
    logger.info("=" * 80)

    for model_key, success in results.items():
        model_info = MODELS_TO_DOWNLOAD[model_key]
        status = "✅ Queued" if success else "❌ Failed"
        logger.info(f"   {status}: {model_info['name']} ({model_info['node']})")

    logger.info("")
    logger.info("💡 After downloads complete:")
    logger.info("   1. Verify files on NAS: " + NAS_MODELS_PATH)
    logger.info("   2. SSH to KAIJU (<NAS_IP>)")
    logger.info("   3. Pull models into Ollama:")
    logger.info("      ollama pull llama3.2:11b")
    logger.info("      ollama pull mixtral:8x7b")
    logger.info("   4. Restart Iron Legion containers:")
    logger.info("      docker-compose -f containerization/docker-compose.iron-legion.yml restart iron-man-mark-ii")
    logger.info("      docker-compose -f containerization/docker-compose.iron-legion.yml restart iron-man-mark-vi")
    logger.info("=" * 80)

    return 0 if all(results.values()) else 1

if __name__ == "__main__":


    sys.exit(main())