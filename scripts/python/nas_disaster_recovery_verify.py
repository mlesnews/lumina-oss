#!/usr/bin/env python3
"""
NAS Disaster Recovery Verification (Robust)
Checks status of Active Backup for Business and Hyper Backup via SSH.
Attempts to verify actual backup activity, not just service status.
"""

import datetime
import json
import sys
from pathlib import Path
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
import logging
logger = logging.getLogger("nas_disaster_recovery_verify")


# Add current directory to path to find nas_azure_vault_integration
sys.path.append(str(Path(__file__).parent))

try:
    from nas_azure_vault_integration import NASAzureVaultIntegration
except ImportError:
    print("❌ Could not import NASAzureVaultIntegration.")
    sys.exit(1)

# Load Config
CONFIG_PATH = (
    Path(__file__).parent.parent.parent / "config" / "lumina_nas_ssh_config.json"
)



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def load_config():
    try:
        if not CONFIG_PATH.exists():
            print(f"❌ Config file not found at {CONFIG_PATH}")
            sys.exit(1)
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)


    except Exception as e:
        logger.error(f"Error in load_config: {e}", exc_info=True)
        raise
def parse_timestamp(ts_str):
    try:
        return datetime.datetime.fromtimestamp(int(ts_str))
    except Exception:
        return None


def verify_disaster_recovery():
    print("🛡️  Starting Robust Disaster Recovery Verification...")

    config = load_config()
    dr_config = config.get("operations", {}).get("disaster_recovery", {})
    nas_ip = config["nas"]["host"]

    integration = NASAzureVaultIntegration(nas_ip=nas_ip)

    # 1. Connectivity Check
    print(f"🔌 Connecting to NAS ({nas_ip})...")
    ssh_client = integration.get_ssh_client()
    if not ssh_client:
        print("❌ CRITICAL: Cannot connect to NAS via SSH. Verification failed.")
        return

    print("✅ SSH Connection Established.")

    # 2. System Time Check
    stdin, stdout, stderr = ssh_client.exec_command("date")
    nas_time = stdout.read().decode().strip()
    print(f"🕒 NAS System Time: {nas_time}")

    # 3. Active Backup for Business Verification
    print("\n🔍 Verifying Active Backup for Business (Bare-Metal)...")
    abb_config = dr_config.get("active_backup_for_business", {})
    if abb_config.get("enabled"):
        # Service Status via Process List (more reliable without root)
        stdin, stdout, stderr = ssh_client.exec_command("ps aux | grep ActiveBackup")
        processes = stdout.read().decode().strip()
        if "synoabb" in processes or "ActiveBackup" in processes:
            print("   ✅ Service Process: DETECTED (Running)")
        else:
            print("   ⚠️ Service Process: NOT DETECTED")

        # Deep Check: Look for recent activity logs or data
        # Common path for ABB data
        abb_path = "/volume1/ActiveBackupforBusiness"
        stdin, stdout, stderr = ssh_client.exec_command(f"ls -ld {abb_path}")
        if stdout.channel.recv_exit_status() == 0:
            print(f"   ✅ Data Directory Found: {abb_path}")
            # Check for recent modification in the data directory (Last 7 days)
            # Find the newest file in the directory
            cmd = f"find {abb_path} -maxdepth 3 -type f -printf '%T@ %p\n' | sort -n | tail -1"
            stdin, stdout, stderr = ssh_client.exec_command(cmd)
            newest_file = stdout.read().decode().strip()

            if newest_file:
                try:
                    ts_str, path = newest_file.split(" ", 1)
                    last_backup_time = parse_timestamp(ts_str.split(".")[0])
                    print(f"   📅 Last Activity Detected: {last_backup_time}")

                    # Check if within 24h
                    if (
                        datetime.datetime.now() - last_backup_time
                    ).total_seconds() < 86400:
                        print("   ✅ Status: HEALTHY (Activity < 24h)")
                    elif (
                        datetime.datetime.now() - last_backup_time
                    ).total_seconds() < 604800:
                        print("   ⚠️ Status: WARNING (Activity < 7 days)")
                    else:
                        print("   ❌ Status: CRITICAL (No activity > 7 days)")
                except:
                    print(f"   ⚠️ Could not parse file timestamp: {newest_file}")
            else:
                print("   ⚠️ No files found to check timestamps.")
        else:
            print(
                f"   ⚠️ Data Directory not found at default location ({abb_path}). Cannot verify backup data."
            )

    # 4. Hyper Backup Verification
    print("\n🔍 Verifying Hyper Backup (NAS Data)...")
    hb_config = dr_config.get("hyper_backup", {})
    if hb_config.get("enabled"):
        # Service Status via Process List
        stdin, stdout, stderr = ssh_client.exec_command("ps aux | grep HyperBackup")
        processes = stdout.read().decode().strip()
        if "synoimgbkptool" in processes or "HyperBackup" in processes:
            print("   ✅ Service Process: DETECTED (Running)")
        else:
            print("   ⚠️ Service Process: NOT DETECTED")

        # Deep Check: Look for running tasks or logs
        # Hyper Backup logs are often in /var/log/synolog/synobackup.log or similar
        # Try to find where the logs are
        log_candidates = ["/var/log/synolog/synobackup.log", "/var/log/messages"]
        found_logs = False

        for log_path in log_candidates:
            stdin, stdout, stderr = ssh_client.exec_command(f"ls {log_path}")
            if stdout.channel.recv_exit_status() == 0:
                # Grep for Hyper Backup success/fail
                cmd = f"grep -i 'Hyper Backup' {log_path} | tail -n 3"
                stdin, stdout, stderr = ssh_client.exec_command(cmd)
                logs = stdout.read().decode().strip()
                if logs:
                    print(f"   📄 Recent Logs ({log_path}):")
                    for line in logs.split("\n"):
                        print(f"      {line}")
                    found_logs = True
                    break

        if not found_logs:
            print("   ⚠️ Could not access or find Hyper Backup logs.")

    ssh_client.close()
    print("\n🏁 Verification Complete.")


if __name__ == "__main__":
    verify_disaster_recovery()
