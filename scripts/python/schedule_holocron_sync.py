#!/usr/bin/env python3
import json
import subprocess
import sys
import time
from pathlib import Path

import schedule

# Load Config
CONFIG_PATH = Path("../../config/nas_dsm_jupyter_config.json")
PROJECT_ROOT = Path("../../")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def ensure_auto_accept_service(config):
    """
    Ensures the JARVIS Auto Keep All Manager is running if enabled.
    This provides the "one shot" capability by handling UI prompts automatically.
    """
    if config.get("enable_auto_accept_service", False):
        print("🤖 Checking JARVIS Auto Keep All Service (#EVOLUTION[@EVO])...")
        manager_script = PROJECT_ROOT / "scripts" / "python" / "jarvis_auto_keep_all_manager.py"

        if manager_script.exists():
            try:
                # Check status first (using the manager's status flag)
                # Note: This is a simplified check; in production we might import the class directly
                # For now, we'll just try to start it in auto-start mode which handles its own singleton check
                subprocess.Popen(
                    [sys.executable, str(manager_script), "--auto-start"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                )
                print("   ✅ Auto Keep All Service is ACTIVE (Background)")
            except Exception as e:
                print(f"   ⚠️  Failed to start Auto Keep All Service: {e}")
        else:
            print(f"   ⚠️  Manager script not found: {manager_script}")


def job():
    print(f"⏰ Starting Scheduled Holocron Sync: {time.ctime()}")
    script_path = Path("sync_holocrons_to_nas_dsm.py").absolute()
    try:
        subprocess.run([sys.executable, str(script_path)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Scheduled Sync Failed: {e}")


def maintenance_job():
    print(f"🧹 Starting Scheduled Maintenance: {time.ctime()}")
    script_path = Path("jedi_archives_maintenance.py").absolute()
    try:
        subprocess.run([sys.executable, str(script_path)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Maintenance Job Failed: {e}")


def main():
    print("🤖 Holocron Sync Scheduler Started (#EVOLUTION[@EVO])")
    config = load_config()

    # Enable One-Shot Capability (Auto-Accept)
    ensure_auto_accept_service(config)

    sync_minutes = config.get("sync_interval_minutes", 60)
    maint_hours = config.get("maintenance_interval_hours", 24)

    print(f"   📅 Sync Interval: Every {sync_minutes} minutes")
    print(f"   📅 Maintenance Interval: Every {maint_hours} hours")

    schedule.every(sync_minutes).minutes.do(job)
    schedule.every(maint_hours).hours.do(maintenance_job)

    # Run once immediately
    job()

    while True:
        # Periodically re-check the auto-accept service to ensure it stays alive
        ensure_auto_accept_service(config)
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
