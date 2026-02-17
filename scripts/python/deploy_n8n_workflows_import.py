#!/usr/bin/env python3
"""
Deploy N8N Workflows via Import Endpoint

Uses N8N's import functionality which may work differently than direct API.
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
print("🚀 DEPLOYING N8N WORKFLOWS VIA IMPORT")
print("="*80)
print()

for filename, name in workflows:
    workflow_file = workflows_dir / filename
    if not workflow_file.exists():
        print(f"❌ {name}: File not found")
        continue

    with open(workflow_file, 'r', encoding='utf-8') as f:
        workflow_data = json.load(f)

    # Try different import methods
    print(f"📤 Deploying {name}...")

    # Method 1: POST to /rest/workflows with full workflow
    try:
        response = requests.post(
            f"{n8n_url}/rest/workflows",
            json=workflow_data,
            auth=auth,
            headers={"Content-Type": "application/json"},
            timeout=10,
            verify=False
        )
        if response.status_code in [200, 201]:
            result = response.json()
            workflow_id = result.get("id") or result.get("data", {}).get("id")
            print(f"   ✅ {name}: Deployed via /rest/workflows (ID: {workflow_id})")
            continue
        else:
            print(f"   ⚠️  /rest/workflows returned {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  /rest/workflows failed: {e}")

    # Method 2: Try import endpoint
    try:
        import_data = {"workflow": workflow_data}
        response = requests.post(
            f"{n8n_url}/rest/workflows/import",
            json=import_data,
            auth=auth,
            headers={"Content-Type": "application/json"},
            timeout=10,
            verify=False
        )
        if response.status_code in [200, 201]:
            result = response.json()
            workflow_id = result.get("id") or result.get("data", {}).get("id")
            print(f"   ✅ {name}: Deployed via /rest/workflows/import (ID: {workflow_id})")
            continue
        else:
            print(f"   ⚠️  /rest/workflows/import returned {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  /rest/workflows/import failed: {e}")

    # Method 3: Try without auth (some N8N configs allow this)
    try:
        response = requests.post(
            f"{n8n_url}/rest/workflows",
            json=workflow_data,
            headers={"Content-Type": "application/json"},
            timeout=10,
            verify=False
        )
        if response.status_code in [200, 201]:
            result = response.json()
            workflow_id = result.get("id") or result.get("data", {}).get("id")
            print(f"   ✅ {name}: Deployed without auth (ID: {workflow_id})")
            continue
        else:
            print(f"   ⚠️  No-auth attempt returned {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  No-auth attempt failed: {e}")

    print(f"   ❌ {name}: All import methods failed")
    print(f"   💡 Manual import: Access {n8n_url}, go to Workflows → Import from File → {filename}")

print()
print("="*80)
print("✅ DEPLOYMENT ATTEMPT COMPLETE")
print("="*80)
