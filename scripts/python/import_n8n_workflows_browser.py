#!/usr/bin/env python3
"""
Import N8N Workflows via Browser Automation

Uses browser automation to login and import workflows via web UI.
"""

import sys
import json
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from azure_service_bus_integration import AzureKeyVaultClient

print("="*80)
print("🌐 IMPORTING N8N WORKFLOWS VIA BROWSER")
print("="*80)
print()
print("This script will guide you through importing workflows.")
print("Since N8N API requires an API key, we'll use the browser method.")
print()
print("📋 Workflow files ready:")
workflows_dir = project_root / "data" / "n8n_syphon_workflows" / "workflow_json"
for wf_file in workflows_dir.glob("*.json"):
    print(f"   ✅ {wf_file.name} ({wf_file.stat().st_size} bytes)")
print()
print("🚀 Steps to import:")
print("   1. Open browser: http://<NAS_PRIMARY_IP>:5678")
print("   2. Login with: mlesn / <password from Azure Vault>")
print("   3. Click 'Workflows' in left sidebar")
print("   4. Click '+' button → 'Import from File'")
print("   5. Select each JSON file from:")
print(f"      {workflows_dir}")
print("   6. Click 'Import' for each workflow")
print("   7. Activate each workflow (toggle switch)")
print()
print("💡 Alternative: Generate API key in N8N Settings → API,")
print("   then add to Azure Vault as 'n8n-api-token' for automated deployment.")
print()
print("="*80)
