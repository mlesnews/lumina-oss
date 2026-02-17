#!/usr/bin/env python3
"""
LUMINA Real Deal Migration Script - V2 (Byte-Level Progress)
Moves Ollama models to NAS with transparent progress tracking.
"""

import sys
import os
import time
import json
import shutil
from pathlib import Path
from datetime import datetime

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

try:
    from jarvis_progress_tracker import get_progress_tracker
except ImportError:
    print("Error: Could not import JARVISProgressTracker.")
    sys.exit(1)

def run_visual_meter(process, total_bytes, current_bytes, message="", complete=False):
    # Scale bytes to a manageable number for the tracker (MB)
    total_mb = int(total_bytes / (1024 * 1024))
    current_mb = int(current_bytes / (1024 * 1024))

    tracker = get_progress_tracker(project_root)
    process_id = "ollama_nas_move_v2"

    if process_id not in tracker.processes:
        tracker.register_process(process_id, process, "Migration-V2", total_mb)

    tracker.update_progress(process_id, current_mb, total_mb)

    if complete:
        tracker.complete_process(process_id)

    # Terminal progress
    percent = (current_bytes / total_bytes * 100) if total_bytes > 0 else 0
    bar_len = 40
    filled_len = int(bar_len * current_bytes // total_bytes) if total_bytes > 0 else 0
    bar = '█' * filled_len + '-' * (bar_len - filled_len)

    print(f"\r🚀 {process} |{bar}| {percent:.1f}% ({current_mb}/{total_mb} MB) {message}", end="", flush=True)
    if complete:
        print()

def migrate_with_transparency():
    source_root = Path.home() / ".ollama"
    dest_root = Path("\\\\<NAS_PRIMARY_IP>\\backups\\OllamaModels")
    process_name = "Ollama NAS Move"

    print(f"🚀 Starting Byte-Level Migration: {source_root} -> {dest_root}")

    if not source_root.exists():
        print(f"❌ Source {source_root} not found.")
        return

    # 1. Stop Ollama
    print("🛑 Stopping Ollama...")
    os.system("powershell -Command \"Stop-Process -Name ollama* -Force -ErrorAction SilentlyContinue\"")
    time.sleep(2)

    # 2. Collect all files and total size
    print("📋 Scanning source files...")
    all_files = []
    total_bytes = 0
    for root, dirs, files in os.walk(source_root):
        for f in files:
            source_path = Path(root) / f
            rel_path = source_path.relative_to(source_root)
            dest_path = dest_root / rel_path

            size = source_path.stat().st_size
            all_files.append({
                "source": source_path,
                "dest": dest_path,
                "rel": rel_path,
                "size": size
            })
            total_bytes += size

    print(f"📊 Total: {len(all_files)} files, {total_bytes / (1024**3):.2f} GB")

    # 3. Move files one by one with chunked progress
    processed_bytes = 0
    errors = []

    for file_info in all_files:
        src = file_info["source"]
        dst = file_info["dest"]
        f_size = file_info["size"]

        # Ensure destination dir exists
        dst.parent.mkdir(parents=True, exist_ok=True)

        # Skip if already exists and matches size
        if dst.exists() and dst.stat().st_size == f_size:
            print(f"\n⏭️  Skipping existing: {file_info['rel']}")
            processed_bytes += f_size
            continue

        print(f"\n📦 Moving: {file_info['rel']} ({f_size / (1024**2):.1f} MB)")

        try:
            # Chunked copy
            with open(src, "rb") as fsrc:
                with open(dst, "wb") as fdst:
                    file_processed = 0
                    while True:
                        buf = fsrc.read(4 * 1024 * 1024) # 4MB chunks
                        if not buf:
                            break
                        fdst.write(buf)
                        file_processed += len(buf)
                        processed_bytes += len(buf)

                        # Update meter
                        msg = f"| Current: {str(file_info['rel'])[:20]}..."
                        run_visual_meter(process_name, total_bytes, processed_bytes, msg)

            # Remove source after successful copy
            os.remove(src)

        except Exception as e:
            errors.append(f"{file_info['rel']}: {str(e)}")
            print(f"\n❌ Error moving {file_info['rel']}: {e}")
            # If we failed during copy, cleanup partial destination file
            if dst.exists():
                try: dst.unlink()
                except: pass
            # Continue to next file
            continue

    if errors:
        print("\n" + "!" * 80)
        print(f"⚠️  Migration completed with {len(errors)} errors:")
        for err in errors[:10]:
            print(f"  - {err}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more.")
    else:
        print("\n✅ All files moved successfully!")
        run_visual_meter(process_name, total_bytes, total_bytes, "Complete", complete=True)

if __name__ == "__main__":
    migrate_with_transparency()
