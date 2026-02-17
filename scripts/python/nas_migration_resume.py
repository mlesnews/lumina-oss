#!/usr/bin/env python3
"""
NAS Migration Resume System
Automatically resumes interrupted migrations for JARVIS
"""

import os
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime
import logging
logger = logging.getLogger("nas_migration_resume")


# Migration configuration
MIGRATIONS = {
    "docker": {
        "source": os.path.expanduser(r"~\AppData\Local\Docker"),
        "destination": r"\\<NAS_PRIMARY_IP>\homes\mlesn\docker",
        "size_gb": 134,
        "status_file": os.path.expanduser(r"~\.lumina\data\nas_migration_docker.json")
    },
    "cursor": {
        "source": os.path.expanduser(r"~\AppData\Roaming\Cursor"),
        "destination": r"\\<NAS_PRIMARY_IP>\homes\mlesn\cursor_cache",
        "size_gb": 33.4,
        "status_file": os.path.expanduser(r"~\.lumina\data\nas_migration_cursor.json")
    }
}

def load_status(migration_name):
    try:
        """Load migration status from file"""
        status_file = MIGRATIONS[migration_name]["status_file"]
        status_dir = os.path.dirname(status_file)
        os.makedirs(status_dir, exist_ok=True)

        if os.path.exists(status_file):
            with open(status_file, 'r') as f:
                return json.load(f)
        return {"status": "pending", "last_check": None, "attempts": 0}

    except Exception as e:
        logger.error(f"Error in load_status: {e}", exc_info=True)
        raise
def save_status(migration_name, status_data):
    try:
        """Save migration status to file"""
        status_file = MIGRATIONS[migration_name]["status_file"]
        status_dir = os.path.dirname(status_file)
        os.makedirs(status_dir, exist_ok=True)

        status_data["last_check"] = datetime.now().isoformat()
        with open(status_file, 'w') as f:
            json.dump(status_data, f, indent=2)

    except Exception as e:
        logger.error(f"Error in save_status: {e}", exc_info=True)
        raise
def check_migration_progress(migration_name):
    """Check if migration is complete or needs resuming"""
    config = MIGRATIONS[migration_name]
    source = config["source"]
    destination = config["destination"]

    # Check if source exists
    if not os.path.exists(source):
        return {"status": "error", "message": "Source path does not exist"}

    # Check if destination exists
    if not os.path.exists(destination):
        return {"status": "pending", "message": "Destination does not exist, starting migration"}

    # Use robocopy to check differences (dry run)
    # Exit codes: 0 = no differences, 1 = files copied, 2 = extra files, 4 = mismatched files
    try:
        result = subprocess.run(
            ["robocopy", source, destination, "/L", "/NJH", "/NJS", "/NDL", "/NP"],
            capture_output=True,
            text=True,
            timeout=300
        )

        # Parse robocopy output to estimate progress
        output_lines = result.stdout.split('\n')
        files_to_copy = 0
        files_copied = 0

        for line in output_lines:
            if "Files:" in line:
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        files_to_copy = int(parts[1])
                        files_copied = int(parts[3])
                    except (ValueError, IndexError):
                        pass

        # Check destination size
        dest_size = 0
        if os.path.exists(destination):
            for root, dirs, files in os.walk(destination):
                for file in files:
                    try:
                        dest_size += os.path.getsize(os.path.join(root, file))
                    except:
                        pass

        dest_size_gb = dest_size / (1024**3)
        target_size_gb = config["size_gb"]
        progress_percent = min(100, (dest_size_gb / target_size_gb) * 100) if target_size_gb > 0 else 0

        if progress_percent >= 99:
            return {"status": "complete", "progress": 100, "message": "Migration appears complete"}
        elif progress_percent > 0:
            return {
                "status": "in_progress",
                "progress": round(progress_percent, 1),
                "message": f"Migration {progress_percent:.1f}% complete, resuming..."
            }
        else:
            return {"status": "pending", "progress": 0, "message": "Migration not started"}

    except subprocess.TimeoutExpired:
        return {"status": "checking", "message": "Still checking migration status..."}
    except Exception as e:
        return {"status": "error", "message": f"Error checking migration: {str(e)}"}

def resume_migration(migration_name):
    """Resume a migration using robocopy with resume support"""
    config = MIGRATIONS[migration_name]
    source = config["source"]
    destination = config["destination"]

    # Ensure destination exists
    os.makedirs(destination, exist_ok=True)

    # Robocopy options:
    # /E = copy subdirectories including empty ones
    # /R:3 = retry 3 times on failure
    # /W:5 = wait 5 seconds between retries
    # /MT:8 = use 8 threads for faster copying
    # /Z = copy files in restartable mode (resumable)
    # /NP = no progress (for background)
    # /NFL = no file list
    # /NDL = no directory list
    # /NJH = no job header
    # /NJS = no job summary

    robocopy_cmd = [
        "robocopy",
        source,
        destination,
        "/E",      # Copy subdirectories
        "/Z",      # Restartable mode (resumable)
        "/R:3",    # Retry 3 times
        "/W:5",    # Wait 5 seconds
        "/MT:8",   # 8 threads
        "/NP",     # No progress
        "/NFL",    # No file list
        "/NDL",    # No directory list
        "/NJH",    # No job header
        "/NJS"     # No job summary
    ]

    try:
        # Run robocopy in background
        process = subprocess.Popen(
            robocopy_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        return {
            "status": "resuming",
            "pid": process.pid,
            "message": f"Migration resumed (PID: {process.pid})"
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to resume migration: {str(e)}"}

def monitor_and_resume(migration_name):
    """Monitor migration and resume if needed"""
    status = load_status(migration_name)
    check_result = check_migration_progress(migration_name)

    if check_result["status"] == "complete":
        status["status"] = "complete"
        status["completed_at"] = datetime.now().isoformat()
        save_status(migration_name, status)
        return {"action": "none", "message": "Migration complete"}

    elif check_result["status"] == "in_progress":
        # Migration in progress, check if robocopy process is running
        # If not, resume it
        status["status"] = "in_progress"
        status["progress"] = check_result.get("progress", 0)
        status["attempts"] = status.get("attempts", 0) + 1
        save_status(migration_name, status)

        # Try to resume
        resume_result = resume_migration(migration_name)
        return {
            "action": "resumed",
            "message": check_result["message"],
            "resume": resume_result
        }

    elif check_result["status"] == "pending":
        # Start migration
        status["status"] = "starting"
        status["attempts"] = status.get("attempts", 0) + 1
        save_status(migration_name, status)

        resume_result = resume_migration(migration_name)
        return {
            "action": "started",
            "message": "Starting migration",
            "resume": resume_result
        }

    else:
        # Error state
        status["status"] = "error"
        status["error"] = check_result.get("message", "Unknown error")
        save_status(migration_name, status)
        return {
            "action": "error",
            "message": check_result.get("message", "Unknown error")
        }

def main():
    """Main function for JARVIS to call"""
    results = {}

    for migration_name in MIGRATIONS.keys():
        print(f"\n=== Checking {migration_name.upper()} migration ===")
        result = monitor_and_resume(migration_name)
        results[migration_name] = result
        print(f"Status: {result.get('action', 'unknown')}")
        print(f"Message: {result.get('message', 'No message')}")
        if "resume" in result:
            print(f"Resume: {result['resume']}")

    return results

if __name__ == "__main__":


    main()