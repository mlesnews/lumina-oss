#!/usr/bin/env python3
"""
Kenny Safe Mode Launcher
Starts Kenny with zero integrations to verify core visibility.
"""
import subprocess
import sys
import os
from pathlib import Path
import logging
logger = logging.getLogger("start_kenny_safe_mode")


def main():
    try:
        project_root = Path(__file__).parent.parent.parent
        kenny_script = project_root / "scripts" / "python" / "kenny_imva_enhanced.py"

        # Force environment variables for Tkinter visibility
        os.environ["TK_SILENT_ERROR"] = "0"

        print("🚀 Starting Kenny in SAFE MODE...")
        # Run WITHOUT integrations and WITH a fresh console
        # We pass arguments that don't exist yet to trigger the 'else' blocks in integrations
        process = subprocess.Popen(
            [sys.executable, str(kenny_script)],
            cwd=str(project_root),
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        print(f"✅ Kenny Safe Mode PID: {process.pid}")

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()