#!/usr/bin/env python3
"""
Deploy N8N Workflows via SSH + curl

Uses SSH to execute curl commands on NAS for workflow deployment.
"""

import sys
import json
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from nas_azure_vault_integration import NASAzureVaultIntegration
from azure_service_bus_integration import AzureKeyVaultClient

vault = AzureKeyVaultClient(vault_url="https://jarvis-lumina.vault.azure.net/")
n8n_pwd = vault.get_secret("n8n-password")

n8n_url = "http://<NAS_PRIMARY_IP>:5678"
workflows_dir = project_root / "data" / "n8n_syphon_workflows" / "workflow_json"

workflows = [
    ("email_syphon.json", "Email SYPHON"),
    ("sms_syphon.json", "SMS SYPHON"),
    ("education_syphon.json", "Education SYPHON")
]

print("="*80)
print("🚀 DEPLOYING N8N WORKFLOWS VIA SSH + CURL")
print("="*80)
print()

nas = NASAzureVaultIntegration()

success_count = 0
for filename, name in workflows:
    workflow_file = workflows_dir / filename
    if not workflow_file.exists():
        print(f"❌ {name}: File not found")
        continue

    with open(workflow_file, 'r', encoding='utf-8') as f:
        workflow_data = json.load(f)

    # Escape JSON for shell
    import shlex
    workflow_json = json.dumps(workflow_data)
    escaped_json = shlex.quote(workflow_json)
    escaped_pwd = shlex.quote(n8n_pwd)

    print(f"📤 Deploying {name}...")

    # Try curl POST via SSH
    curl_cmd = f"""curl -X POST '{n8n_url}/rest/workflows' \\
  -u 'mlesn:{escaped_pwd}' \\
  -H 'Content-Type: application/json' \\
  -d '{escaped_json}' \\
  2>&1"""

    result = nas.execute_ssh_command(curl_cmd)

    if result["success"]:
        output = result["output"].strip()
        if '"id"' in output or '"status":"success"' in output.lower():
            print(f"   ✅ {name}: Deployed via curl")
            success_count += 1
            continue
        else:
            print(f"   ⚠️  Response: {output[:200]}")
    else:
        print(f"   ⚠️  Error: {result.get('error', 'Unknown')}")

    print(f"   ❌ {name}: Deployment failed")

print()
print("="*80)
if success_count == len(workflows):
    print("✅ ALL WORKFLOWS DEPLOYED")
else:
    print(f"⚠️  {success_count}/{len(workflows)} DEPLOYED")
    print("   Remaining require manual import")
print("="*80)
