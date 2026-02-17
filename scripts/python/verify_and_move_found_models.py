#!/usr/bin/env python3
"""
Verify and Move Found Models
                    -LUM THE MODERN

Verifies found model files and moves them to the correct NAS location.

Tags: #MODELS #VERIFY #MOVE @JARVIS @LUMINA @DOIT
"""

import sys
import shutil
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("VerifyMoveModels")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("VerifyMoveModels")

# Model locations and requirements
MODELS = {
    "llama3.2:11b": {
        "found_path": Path("\\\\<NAS_PRIMARY_IP>\\backups\\MATT_Backups\\Llama-3.2-11B-Vision-Instruct.Q4_K_M.gguf"),
        "target_path": Path("\\\\<NAS_PRIMARY_IP>\\backups\\MATT_Backups\\models\\ollama\\Llama-3.2-11B-Vision-Instruct.Q4_K_M.gguf"),
        "expected_size_gb": (5.0, 6.5),
        "node": "Mark II",
        "port": 3002
    },
    "mixtral:8x7b": {
        "found_path": None,  # Not found yet
        "target_path": Path("\\\\<NAS_PRIMARY_IP>\\backups\\MATT_Backups\\models\\ollama\\mixtral-8x7b-v0.1.Q4_K_M.gguf"),
        "expected_size_gb": (20.0, 30.0),
        "node": "Mark VI",
        "port": 3006
    }
}

def verify_model_file(file_path: Path, model_key: str) -> dict:
    """Verify a model file"""
    model_info = MODELS[model_key]
    min_size, max_size = model_info["expected_size_gb"]

    try:
        if not file_path.exists():
            return {
                "exists": False,
                "valid": False,
                "error": "File not found"
            }

        stat = file_path.stat()
        size_gb = stat.st_size / (1024 ** 3)
        size_valid = min_size <= size_gb <= max_size

        return {
            "exists": True,
            "valid": size_valid,
            "size_gb": size_gb,
            "expected_range": f"{min_size:.1f}-{max_size:.1f} GB",
            "last_modified": stat.st_mtime,
            "path": str(file_path)
        }
    except Exception as e:
        return {
            "exists": False,
            "valid": False,
            "error": str(e)
        }

def move_model(source: Path, target: Path, model_key: str) -> bool:
    """Move model file to target location"""
    try:
        # Ensure target directory exists
        target.parent.mkdir(parents=True, exist_ok=True)

        # Check if target already exists
        if target.exists():
            logger.warning(f"⚠️  Target file already exists: {target}")
            logger.info("   Skipping move (file already in correct location)")
            return True

        logger.info(f"📦 Moving {model_key}...")
        logger.info(f"   From: {source}")
        logger.info(f"   To:   {target}")

        # Move file
        shutil.move(str(source), str(target))

        logger.info("✅ Move completed successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to move file: {e}")
        return False

def main():
    """Main function"""
    logger.info("=" * 80)
    logger.info("🔍 VERIFYING AND MOVING FOUND MODELS")
    logger.info("                    -LUM THE MODERN")
    logger.info("=" * 80)

    # Verify Llama model
    logger.info("\n🎯 LLAMA 3.2 11B MODEL")
    logger.info("=" * 80)

    llama_info = MODELS["llama3.2:11b"]
    llama_verification = verify_model_file(llama_info["found_path"], "llama3.2:11b")

    if llama_verification["exists"]:
        logger.info(f"✅ File found: {llama_info['found_path']}")
        logger.info(f"   Size: {llama_verification['size_gb']:.2f} GB")
        logger.info(f"   Expected: {llama_verification['expected_range']}")
        logger.info(f"   Valid: {'✅ Yes' if llama_verification['valid'] else '❌ No (size mismatch)'}")
        logger.info(f"   Last Modified: {llama_verification['last_modified']}")

        # Check if already in correct location
        if llama_info["target_path"].exists():
            logger.info(f"\n✅ Model already in correct location:")
            logger.info(f"   {llama_info['target_path']}")
        else:
            logger.info(f"\n📋 Current location: {llama_info['found_path']}")
            logger.info(f"📋 Target location:   {llama_info['target_path']}")

            # Ask to move
            logger.info("\n💡 Moving model to correct location...")
            if move_model(llama_info["found_path"], llama_info["target_path"], "llama3.2:11b"):
                logger.info("✅ Llama model moved successfully")
            else:
                logger.error("❌ Failed to move Llama model")
    else:
        logger.warning("❌ Llama model not found at expected location")
        logger.info(f"   Searched: {llama_info['found_path']}")

    # Check Mixtral model
    logger.info("\n🎯 MIXTRAL 8X7B MODEL")
    logger.info("=" * 80)

    mixtral_info = MODELS["mixtral:8x7b"]

    # Search for Mixtral in common locations
    search_paths = [
        Path("\\\\<NAS_PRIMARY_IP>\\backups\\MATT_Backups"),
        Path("\\\\<NAS_PRIMARY_IP>\\backups\\MATT_Backups\\models"),
    ]

    mixtral_found = False
    for search_path in search_paths:
        if not search_path.exists():
            continue

        try:
            for file in search_path.rglob("*mixtral*8x7b*.gguf"):
                mixtral_verification = verify_model_file(file, "mixtral:8x7b")
                if mixtral_verification["exists"] and mixtral_verification["valid"]:
                    logger.info(f"✅ File found: {file}")
                    logger.info(f"   Size: {mixtral_verification['size_gb']:.2f} GB")
                    logger.info(f"   Expected: {mixtral_verification['expected_range']}")

                    # Check if already in correct location
                    if mixtral_info["target_path"].exists():
                        logger.info(f"\n✅ Model already in correct location:")
                        logger.info(f"   {mixtral_info['target_path']}")
                    else:
                        logger.info(f"\n💡 Moving model to correct location...")
                        if move_model(file, mixtral_info["target_path"], "mixtral:8x7b"):
                            logger.info("✅ Mixtral model moved successfully")

                    mixtral_found = True
                    break
        except Exception as e:
            logger.debug(f"   Error searching {search_path}: {e}")

    if not mixtral_found:
        logger.warning("❌ Mixtral model not found")
        logger.info("   Model needs to be downloaded")
        logger.info("   Run: python scripts/python/download_iron_legion_models_with_idm.py")

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("📊 SUMMARY")
    logger.info("=" * 80)

    llama_ready = llama_info["target_path"].exists() if llama_verification.get("exists") else False
    mixtral_ready = mixtral_info["target_path"].exists()

    logger.info(f"   Llama 3.2 11B:  {'✅ Ready' if llama_ready else '❌ Not ready'}")
    logger.info(f"   Mixtral 8x7B:   {'✅ Ready' if mixtral_ready else '❌ Not ready'}")

    if llama_ready and mixtral_ready:
        logger.info("\n✅ Both models ready for deployment!")
        logger.info("   Next step: python scripts/python/deploy_iron_legion_models_to_kaiju.py")
    elif llama_ready:
        logger.info("\n⚠️  Llama ready, Mixtral still downloading")
        logger.info("   Monitor IDM for Mixtral download completion")
    else:
        logger.info("\n⚠️  Models not ready")
        logger.info("   Check download status and file locations")

    logger.info("=" * 80)

    return 0

if __name__ == "__main__":


    sys.exit(main())