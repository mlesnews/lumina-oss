#!/usr/bin/env python3
"""Clean up duplicate N8N workflows"""
import sys
import requests
from pathlib import Path

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from azure_service_bus_integration import AzureKeyVaultClient

vault = AzureKeyVaultClient(vault_url="https://jarvis-lumina.vault.azure.net/")
api_key = vault.get_secret("n8n-api-token")

n8n_url = "http://<NAS_PRIMARY_IP>:5678"

headers = {
    "X-N8N-API-KEY": api_key,
    "Content-Type": "application/json"
}

print("="*80)
print("🧹 CLEANING UP DUPLICATE WORKFLOWS")
print("="*80)
print()

# Get all workflows
r = requests.get(f"{n8n_url}/api/v1/workflows", headers=headers, timeout=10, verify=False)

if r.status_code == 200:
    workflows = r.json().get("data", [])

    # Find duplicates by name
    workflow_names = {}
    for wf in workflows:
        name = wf.get("name", "")
        if name not in workflow_names:
            workflow_names[name] = []
        workflow_names[name].append(wf)

    # Keep the most recent version of each (by createdAt)
    to_delete = []
    to_keep = []

    for name, wf_list in workflow_names.items():
        if len(wf_list) > 1:
            # Sort by createdAt, keep the newest
            wf_list.sort(key=lambda x: x.get("createdAt", ""), reverse=True)
            to_keep.append(wf_list[0])
            to_delete.extend(wf_list[1:])
            print(f"📋 {name}:")
            print(f"   ✅ Keeping: {wf_list[0].get('id')} (created: {wf_list[0].get('createdAt')})")
            for dup in wf_list[1:]:
                print(f"   🗑️  Deleting: {dup.get('id')} (created: {dup.get('createdAt')})")
                to_delete.append(dup)
        else:
            to_keep.append(wf_list[0])

    print()
    print(f"📊 Summary:")
    print(f"   Total workflows: {len(workflows)}")
    print(f"   To keep: {len(to_keep)}")
    print(f"   To delete: {len(to_delete)}")
    print()

    if to_delete:
        print("🗑️  Deleting duplicates...")
        for wf in to_delete:
            wf_id = wf.get("id")
            wf_name = wf.get("name")
            delete_r = requests.delete(
                f"{n8n_url}/api/v1/workflows/{wf_id}",
                headers=headers,
                timeout=10,
                verify=False
            )
            if delete_r.status_code in [200, 204]:
                print(f"   ✅ Deleted: {wf_name} (ID: {wf_id})")
            else:
                print(f"   ❌ Failed to delete {wf_name}: {delete_r.status_code}")

        print()
        print("✅ Cleanup complete!")
    else:
        print("✅ No duplicates found - all workflows are unique")

    print()
    print("📋 Remaining workflows:")
    for wf in to_keep:
        print(f"   • {wf.get('name')} (ID: {wf.get('id')})")
else:
    print(f"❌ Failed to fetch workflows: {r.status_code}")

print()
print("="*80)
