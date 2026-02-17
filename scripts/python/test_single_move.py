import os
import shutil
import sys
import time
import subprocess
from pathlib import Path

def test_single_move():
    source = Path.home() / ".ollama" / "models" / "blobs" / "sha256-2bada8a7450677000f678be90653b85d364de7db25eb5ea54136ada5f3933730"
    dest = Path("\\\\<NAS_PRIMARY_IP>\\backups\\OllamaModels\\models\\blobs\\sha256-2bada8a7450677000f678be90653b85d364de7db25eb5ea54136ada5f3933730")

    print(f"Testing move of: {source}")
    print(f"To: {dest}")

    if not source.exists():
        print("Source file does not exist!")
        return

    # Check if locked
    try:
        with open(source, "rb+") as f:
            print("Successfully opened source file for read/write (not locked).")
    except Exception as e:
        print(f"Could not open source file: {e}")
        return

    # Try copying in chunks with progress
    file_size = source.stat().st_size
    print(f"File size: {file_size / (1024**3):.2f} GB")

    start_time = time.time()
    try:
        print("Attempting shutil.copy2...")
        shutil.copy2(source, dest)
        print("\nCopy complete!")
    except Exception as e:
        print(f"\nError during shutil.copy2: {e}")

        print("Attempting system copy command...")
        cmd = ["cmd", "/c", "copy", str(source), str(dest)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("System copy complete!")
        else:
            print(f"System copy failed: {result.stderr}")

if __name__ == "__main__":
    test_single_move()
