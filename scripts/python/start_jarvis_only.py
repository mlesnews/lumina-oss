#!/usr/bin/env python3
"""
Start JARVIS Only

Starts only JARVIS_VA and JARVIS_CHAT (required VAs).
IMVA and ACVA are optional and not started by default.

Tags: #VA #JARVIS #ONLY #REQUIRED @JARVIS @LUMINA
"""

import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("StartJARVISOnly")


def start_jarvis_only():
    """Start only JARVIS (required VAs)"""
    logger.info("=" * 80)
    logger.info("🎯 STARTING JARVIS ONLY")
    logger.info("=" * 80)
    logger.info("")
    logger.info("   📋 Starting required VAs only")
    logger.info("   ⏭️  IMVA and ACVA skipped (optional)")
    logger.info("")

    # Only required VAs
    required_vas = {
        "JARVIS_VA": {
            "script": "jarvis_default_va.py",
            "name": "JARVIS Virtual Assistant",
            "window": True
        },
        "JARVIS_CHAT": {
            "script": "jarvis_va_chat_coordinator.py",
            "name": "JARVIS Chat Coordinator",
            "window": False
        }
    }

    started = []
    failed = []

    for va_id, config in required_vas.items():
        script_path = project_root / "scripts" / "python" / config["script"]

        if not script_path.exists():
            logger.error(f"   ❌ {va_id}: Script not found")
            failed.append(va_id)
            continue

        try:
            logger.info(f"   🚀 Starting: {config['name']}")

            if config["window"]:
                # GUI VA - launch with window
                subprocess.Popen(
                    ["python", str(script_path)],
                    cwd=str(project_root),
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:
                # Background VA
                subprocess.Popen(
                    ["python", str(script_path)],
                    cwd=str(project_root)
                )

            started.append(va_id)
            logger.info(f"      ✅ Started: {config['name']}")
            time.sleep(2)

        except Exception as e:
            logger.error(f"      ❌ Failed to start {va_id}: {e}")
            failed.append(va_id)

    logger.info("")
    logger.info("=" * 80)
    logger.info("✅ JARVIS ONLY START COMPLETE")
    logger.info("=" * 80)
    logger.info(f"   Started: {len(started)}")
    logger.info(f"   Failed: {len(failed)}")
    logger.info("")

    if started:
        logger.info("   ✅ Started:")
        for va_id in started:
            logger.info(f"      • {required_vas[va_id]['name']}")

    if failed:
        logger.info("")
        logger.warning("   ⚠️  Failed:")
        for va_id in failed:
            logger.warning(f"      • {required_vas[va_id]['name']}")

    logger.info("")

    return len(started), len(failed)


if __name__ == "__main__":
    start_jarvis_only()
