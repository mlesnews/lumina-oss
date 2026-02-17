#!/usr/bin/env python3
"""
Verify IDM Queue Status
                    -LUM THE MODERN

Checks if downloads are queued in IDM and provides status.

Tags: #IDM #QUEUE #VERIFY @JARVIS @LUMINA @DOIT
"""

import sys
import subprocess
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("IDMQueueVerify")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("IDMQueueVerify")

def check_idm_running() -> bool:
    """Check if IDM is running"""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq idman.exe"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return "idman.exe" in result.stdout
    except:
        return False

def get_idm_default_folder() -> Path:
    """Try to get IDM's default download folder"""
    try:
        # Try registry
        ps_cmd = """
        $regPath = "HKCU:\\Software\\DownloadManager"
        if (Test-Path $regPath) {
            $defaultFolder = (Get-ItemProperty -Path $regPath -Name "DefaultFolder" -ErrorAction SilentlyContinue).DefaultFolder
            if ($defaultFolder) {
                Write-Output $defaultFolder
            }
        }
        """

        result = subprocess.run(
            ["powershell.exe", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.stdout.strip():
            return Path(result.stdout.strip())
    except:
        pass

    # Fallback to common locations
    return Path.home() / "Downloads"

def main():
    """Main function"""
    logger.info("=" * 80)
    logger.info("🔍 VERIFYING IDM QUEUE STATUS")
    logger.info("                    -LUM THE MODERN")
    logger.info("=" * 80)

    # Check if IDM is running
    idm_running = check_idm_running()
    logger.info(f"   IDM Running: {'✅ Yes' if idm_running else '❌ No'}")

    # Get default folder
    default_folder = get_idm_default_folder()
    logger.info(f"   IDM Default Folder: {default_folder}")

    # Check for model files
    logger.info("\n📦 Checking for model files in default location...")

    models_to_check = {
        "llama3.2:11b": ["*llama*3.2*", "*llama-3.2-11b*"],
        "mixtral:8x7b": ["*mixtral*8x7b*", "*mixtral-8x7b*"]
    }

    found_files = {}
    for model_key, patterns in models_to_check.items():
        found_files[model_key] = []
        for pattern in patterns:
            try:
                files = list(default_folder.glob(pattern))
                found_files[model_key].extend(files)
            except:
                pass

    for model_key, files in found_files.items():
        if files:
            logger.info(f"   ✅ {model_key}: Found {len(files)} file(s)")
            for file in files[:3]:  # Show first 3
                size_mb = file.stat().st_size / (1024 * 1024)
                logger.info(f"      {file.name} ({size_mb:.1f} MB)")
        else:
            logger.info(f"   ❌ {model_key}: Not found")

    logger.info("\n💡 Instructions:")
    logger.info("   1. Open Internet Download Manager")
    logger.info("   2. Check 'Unfinished' or 'Queues' category")
    logger.info("   3. Look for:")
    logger.info("      - llama-3.2-11b-vision-instruct.Q4_K_M.gguf")
    logger.info("      - mixtral-8x7b-v0.1.Q4_K_M.gguf")
    logger.info("   4. If not queued, re-run download script:")
    logger.info("      python scripts/python/download_iron_legion_models_with_idm.py")
    logger.info("=" * 80)

    return 0

if __name__ == "__main__":


    sys.exit(main())