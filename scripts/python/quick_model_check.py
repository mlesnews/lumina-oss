#!/usr/bin/env python3
"""
Quick Model Check - Retry
                    -LUM THE MODERN

Quick verification of model locations and status.

Tags: #MODELS #VERIFY #RETRY @JARVIS @LUMINA @DOIT
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("QuickModelCheck")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("QuickModelCheck")

def check_model(model_name: str, paths: list) -> dict:
    try:
        """Check if model exists in any of the given paths"""
        for path_str in paths:
            path = Path(path_str)
            if path.exists():
                size_gb = path.stat().st_size / (1024 ** 3)
                return {
                    "found": True,
                    "path": str(path),
                    "size_gb": size_gb,
                    "valid": True
                }
        return {"found": False}

    except Exception as e:
        logger.error(f"Error in check_model: {e}", exc_info=True)
        raise
def main():
    """Main function"""
    logger.info("=" * 80)
    logger.info("🔍 QUICK MODEL CHECK - RETRY")
    logger.info("                    -LUM THE MODERN")
    logger.info("=" * 80)

    # Check Llama model
    logger.info("\n🎯 LLAMA 3.2 11B")
    llama_paths = [
        "\\\\<NAS_PRIMARY_IP>\\backups\\MATT_Backups\\models\\ollama\\Llama-3.2-11B-Vision-Instruct.Q4_K_M.gguf",
        "\\\\<NAS_PRIMARY_IP>\\backups\\MATT_Backups\\Llama-3.2-11B-Vision-Instruct.Q4_K_M.gguf",
    ]

    llama_result = check_model("llama3.2:11b", llama_paths)
    if llama_result["found"]:
        logger.info(f"   ✅ Found: {llama_result['path']}")
        logger.info(f"   Size: {llama_result['size_gb']:.2f} GB")
        if "models\\ollama" in llama_result["path"]:
            logger.info("   Location: ✅ Correct (models/ollama)")
        else:
            logger.info("   Location: ⚠️  Needs to be moved to models/ollama")
    else:
        logger.info("   ❌ Not found")

    # Check Mixtral model
    logger.info("\n🎯 MIXTRAL 8X7B")
    mixtral_paths = [
        "\\\\<NAS_PRIMARY_IP>\\backups\\MATT_Backups\\models\\ollama\\mixtral-8x7b-v0.1.Q4_K_M.gguf",
        "\\\\<NAS_PRIMARY_IP>\\backups\\MATT_Backups\\mixtral-8x7b-v0.1.Q4_K_M.gguf",
        "C:\\Users\\mlesn\\Downloads\\mixtral-8x7b-v0.1.Q4_K_M.gguf",
    ]

    mixtral_result = check_model("mixtral:8x7b", mixtral_paths)
    if mixtral_result["found"]:
        logger.info(f"   ✅ Found: {mixtral_result['path']}")
        logger.info(f"   Size: {mixtral_result['size_gb']:.2f} GB")
        if "models\\ollama" in mixtral_result["path"]:
            logger.info("   Location: ✅ Correct (models/ollama)")
        else:
            logger.info("   Location: ⚠️  Needs to be moved to models/ollama")
    else:
        logger.info("   ❌ Not found")
        logger.info("   💡 Check IDM download queue")

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("📊 STATUS")
    logger.info("=" * 80)

    llama_path = llama_result.get('path', '')
    llama_status = '✅ Ready' if llama_result['found'] and 'models/ollama' in llama_path.replace('\\', '/') else ('⚠️  Found but needs move' if llama_result['found'] else '❌ Not found')
    logger.info(f"   Llama 3.2 11B:  {llama_status}")

    mixtral_path = mixtral_result.get('path', '')
    mixtral_status = '✅ Ready' if mixtral_result['found'] and 'models/ollama' in mixtral_path.replace('\\', '/') else ('⚠️  Found but needs move' if mixtral_result['found'] else '❌ Not found')
    logger.info(f"   Mixtral 8x7B:   {mixtral_status}")
    logger.info("=" * 80)

    return 0

if __name__ == "__main__":


    sys.exit(main())