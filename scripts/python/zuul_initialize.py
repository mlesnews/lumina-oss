#!/usr/bin/env python3
"""
ZUUL Initialization Script

Scans Azure Key Vault and initializes the rotation schedule.
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime, timedelta

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from zuul_rotation_engine import ZUULRotationEngine, RotationType

PROJECT_ROOT = Path(r"C:\Users\mlesn\Dropbox\my_projects\.lumina")


def get_azure_secrets():
    """Get list of all secrets from Azure Key Vault."""
    az_cmd = r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"

    try:
        result = subprocess.run(
            f'"{az_cmd}" keyvault secret list --vault-name jarvis-lumina --query "[].name" -o json',
            capture_output=True,
            text=True,
            timeout=60,
            shell=True
        )

        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception as e:
        print(f"Error: {e}")

    return []


def main():
    print("=" * 60)
    print("⚡ ZUUL Initialization")
    print("   Scanning Azure Key Vault and setting up rotation schedule")
    print("=" * 60)

    # Get secrets from Azure
    print("\n📦 Fetching secrets from GATEKEEPER (Azure Key Vault)...")
    secrets = get_azure_secrets()

    if not secrets:
        print("❌ No secrets found or Azure access failed")
        return

    print(f"✅ Found {len(secrets)} secrets")

    # Initialize ZUUL
    zuul = ZUULRotationEngine(PROJECT_ROOT)

    # Assign each secret to rotation schedule
    print("\n📅 Assigning secrets to rotation groups...")

    groups = {"alpha": [], "beta": [], "gamma": [], "delta": []}
    types = {"standard": [], "critical": [], "gating": [], "static": []}

    for secret_name in secrets:
        rot_type = zuul._determine_rotation_type(secret_name)
        group = zuul._determine_group(secret_name)
        interval = zuul._get_rotation_interval(rot_type)

        # Set initial state - assume rotated today (so first rotation in 30 days)
        now = datetime.now()

        zuul.state["secrets"][secret_name] = {
            "rotation_type": rot_type.value,
            "group": group,
            "last_rotated": now.isoformat(),
            "next_rotation": (now + timedelta(days=interval)).isoformat(),
            "rotation_count": 0,
            "hash_prefix": "initial"
        }

        groups[group].append(secret_name)
        types[rot_type.value].append(secret_name)

    # Save state
    zuul._save_state()

    # Summary
    print("\n" + "=" * 60)
    print("📊 Initialization Summary")
    print("=" * 60)

    print("\nBy Rotation Type:")
    for rot_type, secret_list in types.items():
        if secret_list:
            interval = zuul._get_rotation_interval(RotationType(rot_type))
            print(f"  {rot_type.upper()} ({interval} days): {len(secret_list)} secrets")

    print("\nBy Round-Robin Group:")
    for group, secret_list in groups.items():
        day = zuul.config.get("round_robin_groups", {}).get(group, {}).get("rotation_day", "?")
        print(f"  {group.upper()} (day {day}): {len(secret_list)} secrets")

    # List excluded (gating) secrets
    excluded = zuul.config.get("excluded_from_keymaster", [])
    gating = [s for s in secrets if s in excluded]
    if gating:
        print(f"\n🔒 Gating Secrets (Azure only, never synced to ProtonPass):")
        for s in gating:
            print(f"  - {s}")

    print("\n✅ ZUUL initialization complete!")
    print("   First rotations will occur on scheduled group days.")
    print("   Run: python zuul_rotation_engine.py --status")


if __name__ == "__main__":


    main()