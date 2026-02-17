#!/usr/bin/env python3
"""
Final N8N Workflow Deployment - All Methods

Tries all possible methods to deploy workflows to N8N.
"""

import sys
import json
import requests
from pathlib import Path
from requests.auth import HTTPBasicAuth

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from azure_service_bus_integration import AzureKeyVaultClient

vault = AzureKeyVaultClient(vault_url="https://jarvis-lumina.vault.azure.net/")
pwd = vault.get_secret("n8n-password")
auth = HTTPBasicAuth("mlesn", pwd)

n8n_url = "http://<NAS_PRIMARY_IP>:5678"
workflows_dir = project_root / "data" / "n8n_syphon_workflows" / "workflow_json"

workflows = [
    ("email_syphon.json", "Email SYPHON"),
    ("sms_syphon.json", "SMS SYPHON"),
    ("education_syphon.json", "Education SYPHON")
]

print("="*80)
print("🚀 FINAL N8N WORKFLOW DEPLOYMENT ATTEMPT")
print("="*80)
print()

# Create session
session = requests.Session()
session.verify = False

# Login to get session
print("🔐 Establishing session...")
login_r = session.get(n8n_url, auth=auth, timeout=10)
if login_r.status_code == 200:
    print("   ✅ Session established")
else:
    print(f"   ⚠️  Login returned {login_r.status_code}")

success_count = 0
for filename, name in workflows:
    workflow_file = workflows_dir / filename
    if not workflow_file.exists():
        print(f"❌ {name}: File not found")
        continue

    with open(workflow_file, 'r', encoding='utf-8') as f:
        workflow_data = json.load(f)

    print(f"\n📤 Deploying {name}...")

    # Method 1: Try with session + basic auth
    try:
        response = session.post(
            f"{n8n_url}/rest/workflows",
            json=workflow_data,
            auth=auth,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code in [200, 201]:
            result = response.json()
            workflow_id = result.get("id") or result.get("data", {}).get("id")
            print(f"   ✅ {name}: Deployed via session+auth (ID: {workflow_id})")
            success_count += 1
            continue
    except Exception as e:
        pass

    # Method 2: Try PUT instead of POST (some N8N versions)
    try:
        response = session.put(
            f"{n8n_url}/rest/workflows",
            json=workflow_data,
            auth=auth,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code in [200, 201]:
            result = response.json()
            workflow_id = result.get("id") or result.get("data", {}).get("id")
            print(f"   ✅ {name}: Deployed via PUT (ID: {workflow_id})")
            success_count += 1
            continue
    except Exception as e:
        pass

    # Method 3: Try with workflow name in URL
    try:
        workflow_name_safe = workflow_data.get("name", "").replace(" ", "-").lower()
        response = session.post(
            f"{n8n_url}/rest/workflows/{workflow_name_safe}",
            json=workflow_data,
            auth=auth,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code in [200, 201]:
            result = response.json()
            workflow_id = result.get("id") or result.get("data", {}).get("id")
            print(f"   ✅ {name}: Deployed via named endpoint (ID: {workflow_id})")
            success_count += 1
            continue
    except Exception as e:
        pass

    print(f"   ❌ {name}: All API methods failed")
    print(f"   📋 File ready: {workflow_file}")
    print(f"   💡 Manual import required via web UI")

print()
print("="*80)
if success_count == len(workflows):
    print("✅ ALL WORKFLOWS DEPLOYED SUCCESSFULLY")
elif success_count > 0:
    print(f"⚠️  {success_count}/{len(workflows)} WORKFLOWS DEPLOYED")
    print("   Remaining workflows need manual import")
else:
    print("❌ API DEPLOYMENT FAILED - MANUAL IMPORT REQUIRED")
    print()
    print("📋 Manual Import Steps:")
    print("   1. Open: http://<NAS_PRIMARY_IP>:5678")
    print("   2. Login: mlesn / <password from Azure Vault>")
    print("   3. Click 'Workflows' → '+' → 'Import from File'")
    print(f"   4. Import files from: {workflows_dir}")
print("="*80)
