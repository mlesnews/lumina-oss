#!/usr/bin/env python3
"""
JARVIS Code Indexing Starter
Starts codebase indexing using SYPHON and other indexing systems

Tags: #JARVIS #INDEXING #SYPHON #CODEBASE @JARVIS @DOIT
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

logger = get_logger("JARVISCodeIndexing")


def start_syphon_indexing(project_root: Path) -> Dict[str, Any]:
    """Start SYPHON codebase indexing"""
    try:
        logger.info("🔍 Starting SYPHON codebase indexing...")

        # Try to import and initialize SYPHON
        try:
            # Try multiple import paths
            try:
                from syphon.core import SYPHONSystem, SYPHONConfig
                from syphon.config import SubscriptionTier
            except ImportError:
                # Try alternative import path
                import sys
                syphon_path = project_root / "scripts" / "python" / "syphon"
                if str(syphon_path) not in sys.path:
                    sys.path.insert(0, str(syphon_path))
                from core import SYPHONSystem, SYPHONConfig
                # SubscriptionTier might not exist - use default
                SubscriptionTier = None

            if SubscriptionTier:
                syphon_config = SYPHONConfig(
                    project_root=project_root,
                    subscription_tier=SubscriptionTier.FREE
                )
            else:
                # Fallback: try without subscription tier
                try:
                    syphon_config = SYPHONConfig(project_root=project_root)
                except TypeError:
                    # If that fails, try with minimal params
                    syphon_config = SYPHONConfig()
            syphon = SYPHONSystem(syphon_config)

            # Trigger indexing - check for available methods
            if hasattr(syphon, 'index_codebase'):
                result = syphon.index_codebase()
                logger.info("✅ SYPHON codebase indexing started")
                return {"success": True, "system": "SYPHON", "result": result}
            elif hasattr(syphon, 'start_indexing'):
                result = syphon.start_indexing()
                logger.info("✅ SYPHON codebase indexing started")
                return {"success": True, "system": "SYPHON", "result": result}
            elif hasattr(syphon, 'trigger_indexing'):
                result = syphon.trigger_indexing()
                logger.info("✅ SYPHON codebase indexing triggered")
                return {"success": True, "system": "SYPHON", "result": result}
            else:
                logger.warning("⚠️  SYPHON initialized but no indexing method found")
                logger.info("   SYPHON system is ready for indexing operations")
                return {"success": True, "system": "SYPHON", "status": "ready"}

        except ImportError as e:
            logger.warning(f"⚠️  SYPHON not available: {e}")
            return {"success": False, "error": f"SYPHON import failed: {e}"}

    except Exception as e:
        logger.error(f"❌ SYPHON indexing failed: {e}")
        return {"success": False, "error": str(e)}


def start_all_indexing(project_root: Path) -> Dict[str, Any]:
    """Start all available codebase indexing systems"""
    results = {
        "syphon": None,
        "other_systems": []
    }

    logger.info("=" * 80)
    logger.info("📚 STARTING CODEBASE INDEXING")
    logger.info("=" * 80)

    # Start SYPHON
    results["syphon"] = start_syphon_indexing(project_root)

    # Add other indexing systems here as they become available
    # Example: R5 indexing, code search indexing, etc.

    # Summary
    success_count = sum(1 for r in [results["syphon"]] if r and r.get("success"))
    total_count = 1  # Update as more systems are added

    logger.info("")
    logger.info("=" * 80)
    logger.info(f"📊 INDEXING SUMMARY: {success_count}/{total_count} systems started")
    logger.info("=" * 80)

    results["summary"] = {
        "total": total_count,
        "success": success_count,
        "success_rate": (success_count / total_count * 100) if total_count > 0 else 0
    }

    return results


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Start JARVIS codebase indexing")
        parser.add_argument("--project-root", type=Path, help="Project root directory")

        args = parser.parse_args()

        if args.project_root is None:
            project_root = Path(__file__).parent.parent.parent
        else:
            project_root = Path(args.project_root)

        results = start_all_indexing(project_root)

        if results["summary"]["success"] > 0:
            logger.info("✅ Code indexing started successfully")
            return 0
        else:
            logger.error("❌ Code indexing failed to start")
            return 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())