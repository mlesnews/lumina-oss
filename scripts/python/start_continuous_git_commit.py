#!/usr/bin/env python3
"""
Start Continuous Git Commit Service

Ensures the continuous git commit service is running in the background.
This should be called during system startup or when needed.
"""

import sys
import subprocess
import time
from pathlib import Path

def start_continuous_git_commit():
    """Start the continuous git commit service"""
    print("🚀 Starting Continuous Git Commit Service...")

    script_path = Path(__file__).parent / "jarvis_continuous_git_commit.py"
    project_root = Path(__file__).parent.parent.parent

    if not script_path.exists():
        print(f"❌ Continuous git commit script not found: {script_path}")
        return False

    try:
        # Check if already running
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq python.exe", "/FO", "CSV"],
            capture_output=True,
            text=True
        )

        if "jarvis_continuous_git_commit.py" in result.stdout:
            print("✅ Continuous git commit service already running")
            return True

        # Start the service in background
        print("📦 Starting continuous git commit service...")
        process = subprocess.Popen([
            sys.executable,
            str(script_path),
            "--start"
        ], cwd=project_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait a moment to see if it starts successfully
        time.sleep(2)

        if process.poll() is None:
            print("✅ Continuous git commit service started successfully")
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Failed to start continuous git commit service: {stderr.decode()}")
            return False

    except Exception as e:
        print(f"❌ Error starting continuous git commit service: {e}")
        return False

if __name__ == "__main__":
    success = start_continuous_git_commit()
    sys.exit(0 if success else 1)
