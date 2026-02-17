#!/usr/bin/env python3
"""List all workflows in N8N"""
import sys
import requests
from pathlib import Path

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from azure_service_bus_integration import AzureKeyVaultClient

vault = AzureKeyVaultClient(vault_url="https://jarvis-lumina.vault.azure.net/")
api_key = vault.get_secret("n8n-api-token")

n8n_url = "http://<NAS_PRIMARY_IP>:5678"

print("="*80)
print("📋 LISTING ALL N8N WORKFLOWS")
print("="*80)
print()

headers = {
    "X-N8N-API-KEY": api_key,
    "Content-Type": "application/json"
}

# Get all workflows
print("Fetching workflows from N8N...")
r = requests.get(f"{n8n_url}/api/v1/workflows", headers=headers, timeout=10, verify=False)

if r.status_code == 200:
    workflows = r.json().get("data", [])
    print(f"✅ Found {len(workflows)} workflow(s):")
    print()

    if workflows:
        for i, wf in enumerate(workflows, 1):
            wf_id = wf.get("id", "Unknown")
            wf_name = wf.get("name", "Unnamed")
            wf_active = wf.get("active", False)
            status = "🟢 Active" if wf_active else "⚪ Inactive"
            print(f"{i}. {wf_name}")
            print(f"   ID: {wf_id}")
            print(f"   Status: {status}")
            print()
    else:
        print("⚠️  No workflows found")
        print()
        print("💡 The workflows may not have been deployed successfully.")
        print("   Let me check the deployment status...")
else:
    print(f"❌ Failed to fetch workflows: {r.status_code}")
    print(f"   Response: {r.text[:300]}")

print("="*80)
