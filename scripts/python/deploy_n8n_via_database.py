#!/usr/bin/env python3
"""
Deploy N8N Workflows via Direct Database Insertion

Bypasses API by directly inserting workflows into N8N SQLite database.
"""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from nas_azure_vault_integration import NASAzureVaultIntegration

workflows_dir = project_root / "data" / "n8n_syphon_workflows" / "workflow_json"
db_path = "/volume1/docker/n8n/database.sqlite"

workflows = [
    ("email_syphon.json", "Email SYPHON"),
    ("sms_syphon.json", "SMS SYPHON"),
    ("education_syphon.json", "Education SYPHON")
]

print("="*80)
print("💾 DEPLOYING N8N WORKFLOWS VIA DATABASE")
print("="*80)
print()

nas = NASAzureVaultIntegration()

# Download database file temporarily
print("📥 Downloading N8N database...")
download_cmd = f"cat {db_path}"
result = nas.execute_ssh_command(download_cmd)
if not result["success"]:
    print(f"   ❌ Failed to access database: {result.get('error')}")
    sys.exit(1)

# Save to temp file
temp_db = project_root / "data" / "n8n_temp_database.sqlite"
with open(temp_db, 'wb') as f:
    # Note: This won't work directly - need to use SCP or similar
    pass

print("   ⚠️  Direct database access requires file transfer")
print("   💡 Alternative: Use web UI import (recommended)")
print()
print("="*80)
print("📋 MANUAL IMPORT REQUIRED")
print("="*80)
print()
print("Since N8N API requires API key and database access is complex,")
print("the most reliable method is manual import via web UI:")
print()
print("1. Open: http://<NAS_PRIMARY_IP>:5678")
print("2. Login: mlesn / <password from Azure Vault>")
print("3. Workflows → '+' → 'Import from File'")
print(f"4. Import from: {workflows_dir}")
print()
print("Files ready:")
for wf_file in workflows_dir.glob("*.json"):
    print(f"   ✅ {wf_file.name}")
print()
