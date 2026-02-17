#!/usr/bin/env python3
"""
ProtonPass CLI Lock Resolver

Diagnoses and resolves the file lock preventing ProtonPass CLI operations.
"""

import subprocess
import os
import sys
from pathlib import Path
import logging
logger = logging.getLogger("protonpass_lock_resolver")


def find_protonpass_processes():
    """Find all ProtonPass-related processes."""
    print("🔍 Scanning for ProtonPass processes...")

    try:
        result = subprocess.run(
            ["tasklist", "/v", "/fo", "csv"],
            capture_output=True,
            text=True,
            timeout=30
        )

        processes = []
        for line in result.stdout.splitlines()[1:]:  # Skip header
            line_lower = line.lower()
            if any(term in line_lower for term in ["proton", "pass-cli", "protonpass"]):
                # Parse CSV line
                parts = line.split('","')
                if len(parts) >= 2:
                    name = parts[0].strip('"')
                    pid = parts[1].strip('"') if len(parts) > 1 else "?"
                    processes.append((name, pid))

        return processes
    except Exception as e:
        print(f"❌ Error scanning processes: {e}")
        return []

def find_protonpass_data_dir():
    try:
        """Find ProtonPass data directory."""
        possible_paths = [
            Path(os.environ.get("LOCALAPPDATA", "")) / "ProtonPass",
            Path(os.environ.get("APPDATA", "")) / "ProtonPass",
            Path(os.environ.get("USERPROFILE", "")) / ".protonpass",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "ProtonPass",
        ]

        for p in possible_paths:
            if p.exists():
                return p
        return None

    except Exception as e:
        logger.error(f"Error in find_protonpass_data_dir: {e}", exc_info=True)
        raise
def check_lock_files(data_dir: Path):
    """Check for lock files in the ProtonPass data directory."""
    if not data_dir:
        return []

    lock_files = []
    try:
        for f in data_dir.rglob("*.lock"):
            lock_files.append(f)
        for f in data_dir.rglob("*-journal"):
            lock_files.append(f)
        for f in data_dir.rglob("*.db-wal"):
            lock_files.append(f)
        for f in data_dir.rglob("*.db-shm"):
            lock_files.append(f)
    except Exception as e:
        print(f"⚠️  Error scanning for lock files: {e}")

    return lock_files

def kill_process(pid: str, name: str):
    """Kill a process by PID."""
    try:
        result = subprocess.run(
            ["taskkill", "/F", "/PID", pid],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"   ✅ Killed: {name} (PID {pid})")
            return True
        else:
            print(f"   ❌ Failed to kill {name}: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"   ❌ Error killing {name}: {e}")
        return False

def attempt_protonpass_login():
    """Attempt to log in to ProtonPass CLI."""
    cli_path = Path(r"C:\Users\mlesn\AppData\Local\Programs\ProtonPass\pass-cli.exe")

    if not cli_path.exists():
        print("❌ ProtonPass CLI not found at expected path.")
        return False

    print("\n🔑 Checking ProtonPass CLI login status...")
    try:
        result = subprocess.run(
            [str(cli_path), "status"],
            capture_output=True,
            text=True,
            timeout=15
        )
        print(f"   Status output: {result.stdout.strip()}")
        if result.stderr:
            print(f"   Status error: {result.stderr.strip()}")

        if "logged in" in result.stdout.lower():
            print("   ✅ Already logged in!")
            return True
        else:
            print("   ⚠️  Not logged in. Manual login required.")
            print(f"\n   Run this command manually:")
            print(f"   {cli_path} login")
            return False
    except Exception as e:
        print(f"   ❌ Error checking status: {e}")
        return False

def main():
    print("=" * 60)
    print("🔧 ProtonPass CLI Lock Resolver")
    print("=" * 60)

    # Step 1: Find ProtonPass processes
    processes = find_protonpass_processes()

    if processes:
        print(f"\n📋 Found {len(processes)} ProtonPass-related process(es):")
        for name, pid in processes:
            print(f"   - {name} (PID: {pid})")

        # Step 2: Offer to kill them
        print("\n🛑 Stopping ProtonPass processes to release locks...")
        killed_any = False
        for name, pid in processes:
            if "pass-cli" not in name.lower():  # Don't kill our own CLI calls
                if kill_process(pid, name):
                    killed_any = True

        if killed_any:
            print("\n⏳ Waiting for processes to terminate...")
            import time
            time.sleep(2)
    else:
        print("\n✅ No ProtonPass background processes found.")

    # Step 3: Check for lock files
    data_dir = find_protonpass_data_dir()
    if data_dir:
        print(f"\n📁 ProtonPass data directory: {data_dir}")
        lock_files = check_lock_files(data_dir)
        if lock_files:
            print(f"   Found {len(lock_files)} lock/journal file(s):")
            for lf in lock_files[:5]:  # Show first 5
                print(f"      - {lf.name}")
            if len(lock_files) > 5:
                print(f"      ... and {len(lock_files) - 5} more")
    else:
        print("\n⚠️  Could not locate ProtonPass data directory.")

    # Step 4: Check login status
    attempt_protonpass_login()

    print("\n" + "=" * 60)
    print("📝 Next Steps:")
    print("   1. If ProtonPass Desktop is still running, close it manually")
    print("   2. Run: pass-cli.exe login")
    print("   3. Re-run the Triad Baseline Sync")
    print("=" * 60)

if __name__ == "__main__":


    main()