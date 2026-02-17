#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

# Configuration
CONFIG_PATH = Path("../../config/nas_dsm_jupyter_config.json")
LOCAL_HOLOCRONS_DIR = Path("../../data/holocrons")  # Assumed local path


def load_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config not found: {CONFIG_PATH}")
    with open(CONFIG_PATH) as f:
        return json.load(f)


def sync_to_nas(config):
    nas_host = config["nas_host"]
    nas_user = config["nas_user"]
    remote_path = config["holocron_path"]

    # Ensure local directory exists
    if not LOCAL_HOLOCRONS_DIR.exists():
        print(f"⚠️  Local Holocron directory not found: {LOCAL_HOLOCRONS_DIR}")
        return

    print(f"🚀 Syncing Holocrons to {nas_user}@{nas_host}:{remote_path}...")

    # Using SCP/Rsync (assuming SSH keys are set up via deploy_ultron_cron.ps1)
    # Using rsync for efficiency if available, else scp

    # Construct rsync command
    # -a: archive mode
    # -v: verbose
    # -z: compress
    # --delete: delete extraneous files from dest dirs
    cmd = [
        "rsync",
        "-avz",
        "--delete",
        str(LOCAL_HOLOCRONS_DIR) + "/",
        f"{nas_user}@{nas_host}:{remote_path}/",
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Sync Complete!")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("❌ Sync Failed!")
        print(e.stderr)
    except FileNotFoundError:
        print("⚠️  'rsync' not found. Falling back to simple copy (not implemented for remote yet).")
        # In a real scenario, we might use paramiko here for python-native scp


def main():
    try:
        config = load_config()
        sync_to_nas(config)
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
