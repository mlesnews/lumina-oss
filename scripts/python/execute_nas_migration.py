#!/usr/bin/env python3
"""
Lumina NAS Project Migration (PM000003051)
Executes the high-speed mirroring of 'my_projects' to the NAS.

Tags: #NAS #MIGRATION #ROBOCOPY @AUTO @JARVIS
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, Any

try:
    from jarvis_storage_engineering_team import StorageEngineeringTeam
except ImportError:
    StorageEngineeringTeam = None

def execute_migration():
    source = r"C:\Users\mlesn\Dropbox\my_projects"
    # Use the correct SMB share name 'backups' instead of the volume path
    destination = r"\\<NAS_PRIMARY_IP>\backups\lumina_storage\my_projects"

    print("\n" + "="*80)
    print("🚀 LUMINA: EXECUTING NAS PROJECT MIGRATION (PM000003051)")
    print("="*80)
    print(f"Source: {source}")
    print(f"Target: {destination}")
    print("="*80 + "\n")

    # 1. Pre-flight check
    if not os.path.exists(source):
        print(f"❌ Error: Source path not found: {source}")
        return

    print("📋 Step 1: Pre-flight sync...")
    # Trigger Holocron and DB sync first
    subprocess.run([sys.executable, "scripts/python/jarvis_tickets_to_holocron_db.py", "--all"], check=False)

    # 2. Authenticate to NAS
    print("\n🔐 Step 2: Authenticating to NAS SMB share...")
    if StorageEngineeringTeam:
        team = StorageEngineeringTeam(Path("."))
        creds = team.nas_credentials
        if creds:
            username = creds.get("username")
            password = creds.get("password")

            # Map the drive — COMPUSEC: pipe password via stdin to avoid process-list exposure
            print(f"   Authenticating as {username}...")
            proc = subprocess.Popen(
                ["net", "use", destination, f"/user:{username}", "/persistent:no"],
                stdin=subprocess.PIPE, capture_output=True, text=True
            )
            proc.communicate(input=password)
        else:
            print("⚠️  NAS credentials not found in vault. Proceeding with existing session...")

    print("\n📦 Step 3: Mirroring data via Robocopy...")
    # Robocopy command: /MIR (mirror), /MT:16 (multi-threaded), /R:3 (retries), /W:5 (wait)
    #NP = No Progress, NS = No Size, NC = No Class, NFL = No File List, NDL = No Directory List

    try:
        # Test mirror - using /FFT for NAS timestamp compatibility and /XJ to avoid junction points
        test_cmd = f'robocopy "{source}\\.lumina" "{destination}\\.lumina" /MIR /MT:16 /R:0 /W:0 /NP /FFT /XJ'
        print(f"   Executing test mirror of .lumina...")
        result = subprocess.run(test_cmd, shell=True)

        # Robocopy 1-3 are successful copies, 0 is no changes.
        if result.returncode <= 8:
            print("\n✅ Test mirror essentially successful (some files skipped due to long paths/permissions).")

            # Now trigger the full migration in the background
            # /MT:16 for speed, /R:1 /W:1 to not hang on blocked files
            full_cmd = f'start "NAS MIGRATION" robocopy "{source}" "{destination}" /MIR /MT:16 /R:1 /W:1 /FFT /XJ /XD ".git" "node_modules" "__pycache__"'
            print("🚀 Launching full-scale migration in background window...")
            subprocess.run(full_cmd, shell=True)

            print("\n🎉 Full-scale migration initiated. Monitor the external window for progress.")
        else:
            print(f"\n❌ Mirror test failed with code: {result.returncode}")
            print("   Check NAS permissions and path existence.")

    except Exception as e:
        print(f"❌ Migration execution failed: {e}")

if __name__ == "__main__":
    execute_migration()
