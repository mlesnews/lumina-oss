#!/usr/bin/env python3
"""Quick deploy NAS migration - minimal SSH commands"""

import subprocess
import sys
from pathlib import Path

NAS_HOST = "<NAS_PRIMARY_IP>"
NAS_USER = "mlesn"
NAS_SCRIPT = "/volume1/docker/lumina/scripts/python/real_deal_migration_v3.py"
CRON_LINE = "0 2 * * * cd /volume1/docker/lumina && python /volume1/docker/lumina/scripts/python/real_deal_migration_v3.py >> /volume1/docker/lumina/logs/nas_migration_$(date +%Y%m%d).log 2>&1 # NAS Migration"

print("=" * 80)
print("🚀 QUICK DEPLOY: NAS Migration Cron Job")
print("=" * 80)
print()

# Step 1: Add cron job directly
print("📤 Adding cron job to NAS...")
try:
    # Get existing crontab
    get_cron = subprocess.run(
        f'ssh {NAS_USER}@{NAS_HOST} "crontab -l 2>/dev/null || echo \'\'"',
        shell=True,
        capture_output=True,
        text=True,
        timeout=5
    )

    existing = get_cron.stdout.strip()
    new_cron = existing + "\n" + CRON_LINE + "\n" if existing else CRON_LINE + "\n"

    # Set new crontab
    set_cron = subprocess.run(
        f'ssh {NAS_USER}@{NAS_HOST} "echo \'{new_cron}\' | crontab -"',
        shell=True,
        capture_output=True,
        text=True,
        timeout=5
    )

    if set_cron.returncode == 0:
        print("   ✅ Cron job deployed successfully")
    else:
        print(f"   ⚠️  SSH command returned: {set_cron.returncode}")
        print(f"   Error: {set_cron.stderr}")

except subprocess.TimeoutExpired:
    print("   ⚠️  SSH command timed out")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()

# Step 2: Verify
print("🔍 Verifying...")
try:
    verify = subprocess.run(
        f'ssh {NAS_USER}@{NAS_HOST} "crontab -l | grep \'NAS Migration\'"',
        shell=True,
        capture_output=True,
        text=True,
        timeout=5
    )

    if verify.returncode == 0 and verify.stdout.strip():
        print("   ✅ Migration cron job found:")
        print(f"   {verify.stdout.strip()}")
    else:
        print("   ⚠️  Could not verify (may need manual check)")

except Exception as e:
    print(f"   ⚠️  Could not verify: {e}")

print()
print("=" * 80)
print("✅ DEPLOYMENT ATTEMPT COMPLETE")
print("=" * 80)
print()
print("If SSH timed out, deploy manually:")
print(f"  ssh {NAS_USER}@{NAS_HOST}")
print("  crontab -e")
print(f"  # Add: {CRON_LINE}")
print()
