#!/usr/bin/env python3
"""
Deploy N8N Workflows via Session-Based Authentication

Uses session cookies from web login to authenticate API calls.
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

n8n_url = "http://<NAS_PRIMARY_IP>:5678"
workflows_dir = project_root / "data" / "n8n_syphon_workflows" / "workflow_json"

workflows = [
    ("email_syphon.json", "Email SYPHON"),
    ("sms_syphon.json", "SMS SYPHON"),
    ("education_syphon.json", "Education SYPHON")
]

print("="*80)
print("🚀 DEPLOYING N8N WORKFLOWS VIA SESSION")
print("="*80)
print()

# Create session and login
session = requests.Session()
session.verify = False

print("🔐 Authenticating with N8N...")
try:
    # Login via web interface to get session cookie
    login_response = session.get(
        n8n_url,
        auth=HTTPBasicAuth("mlesn", pwd),
        timeout=10
    )
    if login_response.status_code == 200:
        print("   ✅ Session authenticated")
    else:
        print(f"   ⚠️  Login returned {login_response.status_code}")
except Exception as e:
    print(f"   ⚠️  Login failed: {e}")

# Try to get workflows list to verify session
try:
    test_response = session.get(f"{n8n_url}/rest/workflows", timeout=5)
    if test_response.status_code == 200:
        print("   ✅ API access verified with session")
    else:
        print(f"   ⚠️  API test returned {test_response.status_code}")
except Exception as e:
    print(f"   ⚠️  API test failed: {e}")

print()

# Deploy workflows
success_count = 0
for filename, name in workflows:
    workflow_file = workflows_dir / filename
    if not workflow_file.exists():
        print(f"❌ {name}: File not found")
        continue

    with open(workflow_file, 'r', encoding='utf-8') as f:
        workflow_data = json.load(f)

    print(f"📤 Deploying {name}...")

    # Try with session (should have cookies from login)
    try:
        response = session.post(
            f"{n8n_url}/rest/workflows",
            json=workflow_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code in [200, 201]:
            result = response.json()
            workflow_id = result.get("id") or result.get("data", {}).get("id")
            print(f"   ✅ {name}: Deployed (ID: {workflow_id})")
            success_count += 1
            continue
        else:
            print(f"   ⚠️  Session POST returned {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ⚠️  Session POST failed: {e}")

    # Fallback: Try with basic auth in session
    try:
        response = session.post(
            f"{n8n_url}/rest/workflows",
            json=workflow_data,
            auth=HTTPBasicAuth("mlesn", pwd),
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code in [200, 201]:
            result = response.json()
            workflow_id = result.get("id") or result.get("data", {}).get("id")
            print(f"   ✅ {name}: Deployed with basic auth (ID: {workflow_id})")
            success_count += 1
            continue
        else:
            print(f"   ⚠️  Basic auth POST returned {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Basic auth POST failed: {e}")

    print(f"   ❌ {name}: Deployment failed")
    print(f"   💡 Manual import: Access {n8n_url}, go to Workflows → Import from File → {filename}")

print()
print("="*80)
if success_count == len(workflows):
    print("✅ ALL WORKFLOWS DEPLOYED SUCCESSFULLY")
else:
    print(f"⚠️  {success_count}/{len(workflows)} WORKFLOWS DEPLOYED")
    print("   Remaining workflows need manual import via web UI")
print("="*80)
