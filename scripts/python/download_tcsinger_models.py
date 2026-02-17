#!/usr/bin/env python3
"""
Download TCSinger Models with IDM (Internet Download Manager)

Downloads TCSinger pre-trained models from HuggingFace using IDM for
resume capability and speed acceleration.

Tags: #TCSINGER #DOWNLOAD #MODELS #IDM #REQUIRED @JARVIS @LUMINA
"""

import sys
import subprocess
from pathlib import Path
import time

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DownloadTCSingerIDM")

try:
    from huggingface_hub import hf_hub_url
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HUGGINGFACE_AVAILABLE = False
    logger.error("❌ huggingface_hub not installed. Install with: pip install huggingface_hub")


def find_idm_script() -> Path:
    try:
        """Find the IDM download PowerShell script"""
        script_dir = Path(__file__).parent.parent / "powershell"
        idm_script = script_dir / "Invoke-IDMDownload.ps1"

        if not idm_script.exists():
            raise FileNotFoundError(f"IDM script not found: {idm_script}")

        return idm_script


    except Exception as e:
        logger.error(f"Error in find_idm_script: {e}", exc_info=True)
        raise
def download_tcsinger_models_with_idm():
    """
    Download TCSinger models using IDM

    Returns:
        True if all downloads were queued successfully
    """
    if not HUGGINGFACE_AVAILABLE:
        logger.error("❌ Cannot download: huggingface_hub not available")
        return False

    # PRIORITIZE NAS STORAGE for all downloads
    nas_models_path = Path(r"\\<NAS_PRIMARY_IP>\backups\MATT_Backups\models\singing_synthesis\TCSinger")

    # Check if NAS is accessible
    if nas_models_path.exists() or Path(r"\\<NAS_PRIMARY_IP>\backups").exists():
        models_dir = nas_models_path
        logger.info("✅ Using NAS storage for models")
    else:
        # Fallback to local storage
        models_dir = project_root / "models" / "singing_synthesis" / "TCSinger"
        logger.info("⚠️  NAS not accessible, using local storage")

    checkpoints_dir = models_dir / "checkpoints"
    checkpoints_dir.mkdir(parents=True, exist_ok=True)

    # Find IDM script
    try:
        idm_script = find_idm_script()
    except FileNotFoundError as e:
        logger.error(f"❌ {e}")
        return False

    logger.info("=" * 80)
    logger.info("📥 DOWNLOADING TCSINGER MODELS VIA IDM")
    logger.info("=" * 80)
    logger.info(f"   Repository: AaronZ345/TCSinger")
    logger.info(f"   Destination: {checkpoints_dir}")
    logger.info(f"   Using: Internet Download Manager (IDM)")
    logger.info("=" * 80)

    # Required model files
    required_files = [
        {
            "path": "checkpoints/TCSinger/model_ckpt_steps_200000.ckpt",
            "description": "TCSinger Acoustic Model"
        },
        {
            "path": "checkpoints/SAD/model_ckpt_steps_80000.ckpt",
            "description": "Style Adaptive Decoder"
        },
        {
            "path": "checkpoints/SDLM/model_ckpt_steps_120000.ckpt",
            "description": "Style and Duration Language Model"
        },
        {
            "path": "checkpoints/hifigan/model_ckpt_steps_1000000.ckpt",
            "description": "HIFI-GAN Neural Vocoder"
        },
        {
            "path": "checkpoints/hifigan/config.yaml",
            "description": "HIFI-GAN Config"
        },
    ]

    success_count = 0
    failed_files = []

    for file_info in required_files:
        file_path = file_info["path"]
        description = file_info["description"]
        filename = Path(file_path).name

        # Check if already downloaded
        full_path = checkpoints_dir / file_path
        if full_path.exists():
            size_mb = full_path.stat().st_size / (1024 * 1024)
            logger.info(f"✅ {description} already exists ({size_mb:.1f} MB)")
            success_count += 1
            continue

        try:
            # Get download URL from HuggingFace
            logger.info(f"🔄 Getting download URL for {description}...")
            url = hf_hub_url(
                repo_id="AaronZ345/TCSinger",
                filename=file_path,
                repo_type="model"
            )

            # Fix path - remove duplicate "checkpoints" if present
            # file_path is "checkpoints/TCSinger/..." but checkpoints_dir already includes "checkpoints"
            relative_path = file_path.replace("checkpoints/", "", 1) if file_path.startswith("checkpoints/") else file_path
            full_path = checkpoints_dir / relative_path

            # Ensure destination directory exists (handle case where directory exists but is empty)
            dest_dir = full_path.parent
            try:
                dest_dir.mkdir(parents=True, exist_ok=True)
            except FileExistsError:
                # Directory exists, that's fine
                pass

            # Log storage location
            if "<NAS_PRIMARY_IP>" in str(checkpoints_dir):
                logger.info(f"   📍 Storing on NAS: {checkpoints_dir}")
            else:
                logger.info(f"   📍 Storing locally: {checkpoints_dir}")

            # Download via IDM
            logger.info(f"📥 Adding {description} to IDM queue...")
            logger.info(f"   URL: {url}")
            logger.info(f"   Destination: {full_path}")

            cmd = [
                "powershell.exe",
                "-ExecutionPolicy", "Bypass",
                "-File", str(idm_script),
                "-Url", url,
                "-Destination", str(full_path),
                "-Description", f"TCSinger: {description}"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                logger.info(f"✅ {description} added to IDM queue successfully")
                success_count += 1
                # Small delay to avoid overwhelming IDM
                time.sleep(1)
            else:
                logger.error(f"❌ Failed to add {description} to IDM queue")
                logger.error(f"   Error: {result.stderr}")
                failed_files.append(file_path)

        except Exception as e:
            logger.error(f"❌ Error downloading {description}: {e}")
            failed_files.append(file_path)

    logger.info("=" * 80)
    if success_count == len(required_files):
        logger.info("✅ ALL FILES ADDED TO IDM QUEUE")
        logger.info("=" * 80)
        logger.info("📋 Next Steps:")
        logger.info("   1. Open Internet Download Manager (IDM)")
        logger.info("   2. Monitor download progress in IDM")
        logger.info("   3. Once downloads complete, run the duet again")
        logger.info("   4. System will automatically use AI singing synthesis!")
        logger.info("=" * 80)
        return True
    else:
        logger.warning(f"⚠️  {success_count}/{len(required_files)} files queued")
        if failed_files:
            logger.warning("   Failed files:")
            for file_path in failed_files:
                logger.warning(f"     - {file_path}")
        logger.info("=" * 80)
        return False


if __name__ == "__main__":
    success = download_tcsinger_models_with_idm()
    sys.exit(0 if success else 1)
