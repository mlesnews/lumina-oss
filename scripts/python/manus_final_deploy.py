#!/usr/bin/env python3
"""
@MANUS Final Deployment - Deploy code directly to function folder
"""
import sys
import json
import requests
from pathlib import Path
from azure.identity import DefaultAzureCredential

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

function_code_path = project_root / "azure_functions" / "RenderIronLegion" / "__init__.py"
function_json_path = project_root / "azure_functions" / "RenderIronLegion" / "function.json"
function_app_name = "jarvis-lumina-functions"

print("=" * 80)
print("🔥 @MANUS: Final Function Code Deployment")
print("=" * 80)

# Get credentials
credential = DefaultAzureCredential(

                    exclude_interactive_browser_credential=False,

                    exclude_shared_token_cache_credential=False

                )
token = credential.get_token("https://management.azure.com/.default").token

# Load files
with open(function_code_path, 'r', encoding='utf-8') as f:
    function_code = f.read()

with open(function_json_path, 'r') as f:
    function_json = f.read()

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "text/plain"
}

# Deploy __init__.py
print("📤 Deploying __init__.py...")
init_url = f"https://{function_app_name}.scm.azurewebsites.net/api/vfs/site/wwwroot/RenderIronLegion/__init__.py"
response = requests.put(init_url, data=function_code, headers=headers, timeout=30)

if response.status_code in [200, 201, 204]:
    print("✅ __init__.py deployed")
else:
    print(f"⚠️  __init__.py: {response.status_code}")

# Deploy function.json
print("📤 Deploying function.json...")
json_url = f"https://{function_app_name}.scm.azurewebsites.net/api/vfs/site/wwwroot/RenderIronLegion/function.json"
json_headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
response = requests.put(json_url, data=function_json, headers=json_headers, timeout=30)

if response.status_code in [200, 201, 204]:
    print("✅ function.json deployed")
else:
    print(f"⚠️  function.json: {response.status_code}")

# Sync triggers
print("\n🔄 Syncing function triggers...")
sync_url = f"https://{function_app_name}.azurewebsites.net/admin/host/synctriggers"
sync_response = requests.post(sync_url, headers={"Authorization": f"Bearer {token}"}, timeout=30)

if sync_response.status_code in [200, 204]:
    print("✅ Triggers synced")
else:
    print(f"⚠️  Sync: {sync_response.status_code}")

# Get function key and test
print("\n🔑 Getting function key...")
az_cmd = r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
import subprocess
result = subprocess.run(
    [az_cmd, "functionapp", "function", "keys", "list",
     "--name", function_app_name,
     "--resource-group", "jarvis-lumina-rg",
     "--function-name", "RenderIronLegion",
     "--output", "json"],
    capture_output=True, text=True, timeout=10, shell=True
)

function_key = None
if result.returncode == 0:
    keys_data = json.loads(result.stdout)
    if keys_data:
        function_key = list(keys_data.values())[0] if isinstance(keys_data, dict) else keys_data[0].get('value') if keys_data else None

# Test endpoint
print("\n🧪 Testing endpoint...")
import time
time.sleep(5)

test_url = f"https://{function_app_name}.azurewebsites.net/api/renderironlegion"
if function_key:
    test_url += f"?code={function_key}"

test_payload = {
    "state": "armor",
    "animation_frame": 0,
    "transformation_progress": 1.0,
    "size": 180
}

try:
    test_response = requests.post(test_url, json=test_payload, timeout=15)
    print(f"   Status: {test_response.status_code}")
    if test_response.status_code == 200:
        data = test_response.json()
        print(f"   ✅ SUCCESS! Image: {len(data.get('image', ''))} bytes")
        print("\n🎉 REMOTE COMPUTE IS NOW ACTIVE!")
        print(f"   Endpoint: {test_url}")
    elif test_response.status_code == 401:
        print("   ⚠️  Authentication required - function key needed")
        print("   Endpoint exists but needs function key for access")
    else:
        print(f"   Response: {test_response.text[:300]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 80)
