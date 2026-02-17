#!/usr/bin/env python3
"""
LUMINA Real Deal Migration Script
Moves Ollama models to NAS and tracks progress with the Visual Meter.
"""

import sys
import subprocess
import os
import re
import time
from pathlib import Path
import logging
logger = logging.getLogger("real_deal_migration")


# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(script_dir))

def run_visual_meter(process, total, current, complete=False):
    try:
        cmd = [
            sys.executable,
            "scripts/python/lumina_visual_meter.py",
            "--process", process,
            "--total", str(total),
            "--current", str(current),
            "--show-bar"
        ]
        if complete:
            cmd.append("--complete")
        subprocess.run(cmd)

    except Exception as e:
        logger.error(f"Error in run_visual_meter: {e}", exc_info=True)
        raise
def migrate_ollama():
    try:
        source = Path.home() / ".ollama"
        dest = Path("\\\\<NAS_PRIMARY_IP>\\backups\\OllamaModels")
        process_name = "Ollama NAS Move"

        print(f"🚀 Starting Real Deal Migration: {source} -> {dest}")

        if not source.exists():
            print(f"❌ Source {source} not found.")
            return

        # 0. Create destination if needed
        if not dest.exists():
            print(f"📁 Creating destination: {dest}")
            os.makedirs(dest, exist_ok=True)

        # 1. Stop Ollama to release file locks
        print("🛑 Stopping Ollama...")
        subprocess.run(["powershell", "-Command", "Stop-Process -Name ollama -ErrorAction SilentlyContinue"], capture_output=True)
        time.sleep(2) # Give it a moment to release locks

        # 2. Get total file count for progress tracking
        print("📋 Calculating total files...")
        total_files = 0
        for root, dirs, files in os.walk(source):
            total_files += len(files)

        print(f"📊 Total files to move: {total_files}")
        run_visual_meter(process_name, total_files, 0)

        # 2. Use Robocopy to move data
        # /MOVE - Move files and dirs (delete from source after copy)
        # /E - Subdirectories including empty ones
        # /Z - Restartable mode
        # /ZB - Restartable mode; if access denied use Backup mode
        # /R:3 - 3 retries
        # /W:5 - 5 seconds between retries
        # /NDL - No Directory List
        # /NFL - No File List (we'll parse for progress instead)
        # /BYTES - Show sizes in bytes

        cmd = [
            "robocopy", str(source), str(dest),
            "/MOVE", "/E", "/MT:8", "/R:3", "/W:5", "/V", "/TS", "/FP"
        ]

        # We'll use a simplified progress update because parsing Robocopy's
        # real-time stdout can be tricky in some environments.
        # Instead, we'll run robocopy and poll the destination for progress.

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        moved_count = 0
        while True:
            line = proc.stdout.readline()
            if not line and proc.poll() is not None:
                break

            # Robocopy marks moved files with certain patterns
            if "New File" in line or "New Dir" in line or "100%" in line:
                # Polling the destination count is more reliable for "Total/Current"
                current_moved = 0
                for root, dirs, files in os.walk(dest):
                    current_moved += len(files)

                if current_moved != moved_count:
                    moved_count = current_moved
                    run_visual_meter(process_name, total_files, min(moved_count, total_files))

        if proc.returncode < 8: # Robocopy returns < 8 for success/minor issues
            print(f"✅ Migration successful.")
            run_visual_meter(process_name, total_files, total_files, complete=True)
        else:
            print(f"❌ Robocopy failed with return code {proc.returncode}")

    except Exception as e:
        logger.error(f"Error in migrate_ollama: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    migrate_ollama()
