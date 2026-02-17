#!/usr/bin/env python3
"""
Find Moved Model Files
                    -LUM THE MODERN

Searches for previously downloaded model files that may have been moved,
and verifies if they match the required models for Iron Legion.

Tags: #MODELS #SEARCH #VERIFY @JARVIS @LUMINA @DOIT
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("FindMovedModels")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("FindMovedModels")

# Required models for Iron Legion
REQUIRED_MODELS = {
    "llama3.2:11b": {
        "patterns": [
            "*llama*3.2*11b*",
            "*llama-3.2-11b*",
            "*llama3.2-11b*"
        ],
        "expected_size_gb": (5.0, 6.5),  # Approximate range
        "node": "Mark II",
        "port": 3002
    },
    "mixtral:8x7b": {
        "patterns": [
            "*mixtral*8x7b*",
            "*mixtral-8x7b*",
            "*mixtral8x7b*"
        ],
        "expected_size_gb": (20.0, 30.0),  # Approximate range
        "node": "Mark VI",
        "port": 3006
    }
}

def get_drive_letters() -> List[str]:
    """Get all available drive letters"""
    try:
        ps_cmd = "Get-PSDrive -PSProvider FileSystem | Select-Object -ExpandProperty Name"
        result = subprocess.run(
            ["powershell.exe", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            timeout=10
        )
        drives = [d.strip() for d in result.stdout.strip().split('\n') if d.strip()]
        return drives
    except:
        return []

def check_nas_paths() -> List[Path]:
    """Check common NAS paths"""
    nas_paths = [
        Path("M:\\"),
        Path("\\\\<NAS_PRIMARY_IP>\\backups\\MATT_Backups\\models"),
        Path("\\\\<NAS_PRIMARY_IP>\\backups\\MATT_Backups\\models\\ollama"),
        Path("\\\\<NAS_PRIMARY_IP>\\models"),
    ]

    accessible = []
    for path in nas_paths:
        try:
            if path.exists():
                accessible.append(path)
        except:
            pass

    return accessible

def search_for_models(search_paths: List[Path], max_depth: int = 5) -> Dict[str, List[Dict]]:
    """Search for model files in specified paths"""
    found_models = {key: [] for key in REQUIRED_MODELS.keys()}

    for search_path in search_paths:
        if not search_path.exists():
            continue

        logger.info(f"🔍 Searching: {search_path}")

        for model_key, model_info in REQUIRED_MODELS.items():
            for pattern in model_info["patterns"]:
                try:
                    # Convert glob pattern to search
                    files = list(search_path.rglob(pattern))

                    for file in files:
                        if file.suffix.lower() == ".gguf":
                            size_gb = file.stat().st_size / (1024 ** 3)

                            # Check if size is in expected range
                            min_size, max_size = model_info["expected_size_gb"]
                            size_match = min_size <= size_gb <= max_size

                            found_models[model_key].append({
                                "path": file,
                                "size_gb": size_gb,
                                "size_match": size_match,
                                "last_modified": file.stat().st_mtime,
                                "search_path": search_path
                            })
                except Exception as e:
                    logger.debug(f"   Error searching {pattern} in {search_path}: {e}")

    return found_models

def verify_model_file(file_path: Path, model_key: str) -> Dict:
    """Verify if a file matches the required model"""
    model_info = REQUIRED_MODELS[model_key]

    try:
        stat = file_path.stat()
        size_gb = stat.st_size / (1024 ** 3)
        min_size, max_size = model_info["expected_size_gb"]
        size_match = min_size <= size_gb <= max_size

        return {
            "valid": size_match,
            "size_gb": size_gb,
            "expected_range": f"{min_size:.1f}-{max_size:.1f} GB",
            "path": str(file_path),
            "on_nas": "\\\\" in str(file_path) or "M:\\" in str(file_path)
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }

def main():
    try:
        """Main function"""
        logger.info("=" * 80)
        logger.info("🔍 FINDING MOVED MODEL FILES")
        logger.info("                    -LUM THE MODERN")
        logger.info("=" * 80)

        # Get search paths
        search_paths = []

        # Check M: drive
        logger.info("\n📁 Checking drive mappings...")
        drives = get_drive_letters()
        logger.info(f"   Available drives: {', '.join(drives)}")

        if "M" in drives:
            m_drive = Path("M:\\")
            if m_drive.exists():
                logger.info("   ✅ M: drive accessible")
                search_paths.append(m_drive)
            else:
                logger.info("   ⚠️  M: drive mapped but not accessible")
        else:
            logger.info("   ⚠️  M: drive not found")

        # Check NAS paths
        logger.info("\n📁 Checking NAS paths...")
        nas_paths = check_nas_paths()
        for nas_path in nas_paths:
            logger.info(f"   ✅ NAS accessible: {nas_path}")
            search_paths.append(nas_path)

        # Add common download locations
        common_paths = [
            Path.home() / "Downloads",
            Path("D:\\Downloads"),
            Path("D:\\"),
            Path("C:\\Users\\mlesn\\Downloads"),
        ]

        for path in common_paths:
            if path.exists():
                search_paths.append(path)

        logger.info(f"\n🔍 Searching {len(search_paths)} locations...")

        # Search for models
        found_models = search_for_models(search_paths, max_depth=5)

        # Report findings
        logger.info("\n" + "=" * 80)
        logger.info("📊 SEARCH RESULTS")
        logger.info("=" * 80)

        all_found = False

        for model_key, model_info in REQUIRED_MODELS.items():
            logger.info(f"\n🎯 {model_key.upper()}")
            logger.info(f"   Required for: {model_info['node']} (Port {model_info['port']})")
            logger.info(f"   Expected size: {model_info['expected_size_gb'][0]:.1f}-{model_info['expected_size_gb'][1]:.1f} GB")

            files = found_models[model_key]

            if not files:
                logger.info("   ❌ Not found")
            else:
                all_found = True
                # Remove duplicates (same file path)
                unique_files = {}
                for file_info in files:
                    path_str = str(file_info["path"])
                    if path_str not in unique_files:
                        unique_files[path_str] = file_info

                for file_info in unique_files.values():
                    file_path = file_info["path"]
                    size_gb = file_info["size_gb"]
                    size_match = file_info["size_match"]
                    on_nas = "\\\\" in str(file_path) or "M:\\" in str(file_path)

                    status = "✅" if (size_match and on_nas) else ("⚠️ " if size_match else "❌")

                    logger.info(f"   {status} {file_path.name}")
                    logger.info(f"      Path: {file_path}")
                    logger.info(f"      Size: {size_gb:.2f} GB {'✅' if size_match else '❌ (size mismatch)'}")
                    logger.info(f"      On NAS: {'✅ Yes' if on_nas else '❌ No'}")
                    logger.info(f"      Last Modified: {Path(file_path).stat().st_mtime}")

        logger.info("\n" + "=" * 80)
        logger.info("💡 RECOMMENDATIONS")
        logger.info("=" * 80)

        if all_found:
            logger.info("   ✅ Found model files!")
            logger.info("   📋 Next steps:")
            logger.info("      1. Verify files are on NAS (M: drive or \\\\<NAS_PRIMARY_IP>\\...)")
            logger.info("      2. If not on NAS, copy them to: \\\\<NAS_PRIMARY_IP>\\backups\\MATT_Backups\\models\\ollama\\")
            logger.info("      3. Deploy to KAIJU using: python scripts/python/deploy_iron_legion_models_to_kaiju.py")
        else:
            logger.info("   ⚠️  Models not found in searched locations")
            logger.info("   📋 Next steps:")
            logger.info("      1. Check IDM download history/completed folder")
            logger.info("      2. Check if downloads were moved to a different location")
            logger.info("      3. Re-queue downloads if needed: python scripts/python/download_iron_legion_models_with_idm.py")

        logger.info("=" * 80)

        return 0

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())