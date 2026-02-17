#!/usr/bin/env python3
"""
Find Downloaded Model Files
                    -LUM THE MODERN

Searches common locations for downloaded model files.

Tags: #IRON_LEGION #FIND #MODELS @JARVIS @LUMINA
"""

import sys
from pathlib import Path
import os

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("FindDownloadedModels")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("FindDownloadedModels")

# Search locations
SEARCH_LOCATIONS = [
    Path(r"\\<NAS_PRIMARY_IP>\backups\MATT_Backups\models\ollama"),
    Path(os.path.expanduser("~/Downloads")),
    Path("D:/Ollama/models"),
    Path("C:/Ollama/models"),
    Path(os.environ.get("OLLAMA_MODELS", "")),
]

# Files to find
TARGET_FILES = {
    "llama3.2:11b": [
        "llama-3.2-11b-vision-instruct.Q4_K_M.gguf",
        "llama-3.2-11b*.gguf",
    ],
    "mixtral:8x7b": [
        "mixtral-8x7b-v0.1.Q4_K_M.gguf",
        "mixtral-8x7b*.gguf",
    ]
}

def find_files(pattern: str, search_path: Path) -> list[Path]:
    """Find files matching pattern in search path"""
    found = []
    if not search_path.exists():
        return found

    try:
        # Try exact match first
        exact_path = search_path / pattern.replace("*", "")
        if exact_path.exists():
            found.append(exact_path)

        # Try glob pattern
        if "*" in pattern:
            found.extend(search_path.glob(pattern))
        else:
            # Also try case-insensitive search
            for file in search_path.iterdir():
                if file.is_file() and pattern.lower() in file.name.lower():
                    found.append(file)
    except Exception as e:
        logger.debug(f"   Error searching {search_path}: {e}")

    return found

def main():
    try:
        """Main function"""
        logger.info("=" * 80)
        logger.info("🔍 SEARCHING FOR DOWNLOADED MODEL FILES")
        logger.info("                    -LUM THE MODERN")
        logger.info("=" * 80)

        all_found = {}

        for model_key, patterns in TARGET_FILES.items():
            logger.info(f"\n📦 Searching for: {model_key}")
            found_files = []

            for location in SEARCH_LOCATIONS:
                if not location or not location.exists():
                    continue

                logger.info(f"   Checking: {location}")

                for pattern in patterns:
                    files = find_files(pattern, location)
                    found_files.extend(files)

            # Remove duplicates
            found_files = list(set(found_files))

            if found_files:
                logger.info(f"   ✅ Found {len(found_files)} file(s):")
                for file in found_files:
                    size_mb = file.stat().st_size / (1024 * 1024)
                    logger.info(f"      {file}")
                    logger.info(f"      Size: {size_mb:.2f} MB")
                    logger.info(f"      Modified: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file.stat().st_mtime))}")
            else:
                logger.info(f"   ❌ Not found")

            all_found[model_key] = found_files

        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("📊 SEARCH SUMMARY")
        logger.info("=" * 80)

        for model_key, files in all_found.items():
            status = f"✅ Found ({len(files)})" if files else "❌ Not Found"
            logger.info(f"   {status}: {model_key}")

        logger.info("=" * 80)

        return 0

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    import time


    sys.exit(main())