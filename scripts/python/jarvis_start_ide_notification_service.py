#!/usr/bin/env python3
"""
JARVIS Start IDE Notification Service

Starts the IDE notification service in the background.
Can be run on startup or manually.

Tags: #CURSOR-IDE #AUTOMATION #SERVICE @CURSOR-ENGINEER
"""

import sys
import subprocess
from pathlib import Path
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISStartIDEService")


def start_service():
    """Start the IDE notification service"""
    project_root = Path(__file__).parent.parent.parent
    service_script = project_root / "scripts" / "python" / "jarvis_ide_notification_service.py"

    logger.info("🚀 Starting IDE Notification Service...")

    try:
        # Start service in background
        process = subprocess.Popen(
            [sys.executable, str(service_script), "--start", "--interval", "30"],
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )

        logger.info(f"✅ IDE Notification Service started (PID: {process.pid})")
        return {"success": True, "pid": process.pid}

    except Exception as e:
        logger.error(f"❌ Failed to start service: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    result = start_service()
    if result.get("success"):
        print(f"✅ Service started (PID: {result.get('pid')})")
    else:
        print(f"❌ Failed: {result.get('error')}")
