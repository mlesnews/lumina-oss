#!/usr/bin/env python3
"""
JARVIS Fix Codebase Indexing
Ensures codebase is properly indexed and Cursor knows about it

Tags: #JARVIS #INDEXING #SYPHON #CODEBASE @JARVIS @FIX
"""

import sys
from pathlib import Path
from typing import Dict, Any
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISFixCodebaseIndexing")


def fix_codebase_indexing(project_root: Path) -> Dict[str, Any]:
    """Fix codebase indexing issues"""

    logger.info("="*80)
    logger.info("🔍 FIXING CODEBASE INDEXING")
    logger.info("="*80)
    logger.info("")

    results = {
        "syphon_indexing": None,
        "cursor_indexing": None,
        "status": {}
    }

    # Step 1: Start SYPHON indexing
    logger.info("1️⃣  Starting SYPHON Codebase Indexing...")
    try:
        from jarvis_start_code_indexing import start_all_indexing
        syphon_result = start_all_indexing(project_root)
        results["syphon_indexing"] = syphon_result

        if syphon_result.get("summary", {}).get("success", 0) > 0:
            logger.info("   ✅ SYPHON indexing started")
        else:
            logger.warning("   ⚠️  SYPHON indexing had issues")
    except Exception as e:
        logger.error(f"   ❌ SYPHON indexing failed: {e}")
        results["syphon_indexing"] = {"error": str(e)}

    # Step 2: Ensure Cursor knows about indexing
    logger.info("")
    logger.info("2️⃣  Ensuring Cursor Codebase Indexing...")

    # Cursor uses its own indexing - we can't directly control it
    # But we can ensure files are present and accessible

    # Check for .cursorrules or similar
    cursor_files = [
        project_root / ".cursorrules",
        project_root / ".cursor" / "index",
        project_root / ".vscode" / "settings.json"
    ]

    found_files = []
    for file_path in cursor_files:
        if file_path.exists():
            found_files.append(str(file_path))

    if found_files:
        logger.info(f"   ✅ Found {len(found_files)} Cursor configuration files")
        results["cursor_indexing"] = {
            "status": "files_present",
            "files": found_files
        }
    else:
        logger.info("   ⚠️  No Cursor configuration files found")
        results["cursor_indexing"] = {
            "status": "no_files",
            "note": "Cursor should auto-index, but no config files found"
        }

    # Step 3: Trigger re-indexing if needed
    logger.info("")
    logger.info("3️⃣  Triggering Codebase Re-indexing...")

    # Create/update a marker file to trigger re-indexing
    try:
        index_marker = project_root / ".cursor" / "index_marker.txt"
        index_marker.parent.mkdir(exist_ok=True)
        index_marker.write_text(f"Index marker updated: {Path(__file__).stat().st_mtime}")
        logger.info("   ✅ Index marker created/updated")
        results["status"]["index_marker"] = "created"
    except Exception as e:
        logger.warning(f"   ⚠️  Could not create index marker: {e}")

    # Summary
    logger.info("")
    logger.info("="*80)
    logger.info("📊 INDEXING FIX SUMMARY")
    logger.info("="*80)
    logger.info("")

    if results["syphon_indexing"] and results["syphon_indexing"].get("summary", {}).get("success", 0) > 0:
        logger.info("✅ SYPHON indexing: ACTIVE")
    else:
        logger.warning("⚠️  SYPHON indexing: Needs attention")

    logger.info("")
    logger.info("💡 To fix 'CODEBASE NOT INDEXED' in Cursor:")
    logger.info("   1. Wait for SYPHON to complete indexing")
    logger.info("   2. Restart Cursor IDE to trigger re-indexing")
    logger.info("   3. Check Cursor settings → Codebase Indexing")
    logger.info("")

    return results


def main():
    try:
        """CLI interface"""
        project_root = Path(__file__).parent.parent.parent
        results = fix_codebase_indexing(project_root)

        if results.get("syphon_indexing", {}).get("summary", {}).get("success", 0) > 0:
            print("\n✅ Codebase indexing fix applied!")
            return 0
        else:
            print("\n⚠️  Some indexing issues may remain")
            return 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())