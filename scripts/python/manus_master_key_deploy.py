#!/usr/bin/env python3
"""
@MANUS Master Key Deploy
Uses master key to deploy function code via Admin API
"""
import sys
import json
import requests
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

function_code_path = project_root / "azure_functions" / "RenderIronLegion" / "__init__.py"
function_json_path = project_root / "azure_functions" / "RenderIronLegion" / "function.json"
function_app_name = "jarvis-lumina-functions"

print("=" * 80)
print("🔥 @MANUS: Master Key Deploy")
print("=" * 80)

# Get master key
az_cmd = r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
import subprocess
result = subprocess.run(
    [az_cmd, "functionapp", "keys", "list",
     "--name", function_app_name,
     "--resource-group", "jarvis-lumina-rg",
     "--output", "json"],
    capture_output=True, text=True, timeout=10, shell=True
)

master_key = None
if result.returncode == 0:
    keys_data = json.loads(result.stdout)
    master_key = keys_data.get("masterKey", "")
    print(f"✅ Master key obtained")
else:
    print(f"❌ Could not get master key")

# Load files
with open(function_code_path, 'r', encoding='utf-8') as f:
    function_code = f.read()

with open(function_json_path, 'r') as f:
    function_json_data = json.load(f)

# Use Admin API with master key
admin_url = f"https://{function_app_name}.azurewebsites.net/admin/functions/RenderIronLegion"

headers = {
    "x-functions-key": master_key if master_key else "",
    "Content-Type": "application/json"
}

# Get function
print("🔍 Getting function...")
get_response = requests.get(admin_url, headers=headers, timeout=30)

if get_response.status_code == 200:
    print("✅ Function accessible")
    current = get_response.json()

    # Update files
    print("📤 Updating function code...")
    update_data = current.copy()
    if "files" not in update_data:
        update_data["files"] = {}
    update_data["files"]["__init__.py"] = function_code

    # Update config
    if "config" not in update_data:
        update_data["config"] = {}
    update_data["config"]["bindings"] = function_json_data.get("bindings", [])

    update_response = requests.put(admin_url, json=update_data, headers=headers, timeout=60)

    if update_response.status_code in [200, 201, 202]:
        print("✅ Function updated!")

        import time
        time.sleep(5)

        # Test
        endpoint = f"https://{function_app_name}.azurewebsites.net/api/renderironlegion"
        url = f"{endpoint}?code={master_key}"

        print(f"\n🧪 Testing: {endpoint}")
        payload = {"state": "armor", "animation_frame": 0, "transformation_progress": 1.0, "size": 180}

        try:
            response = requests.post(url, json=payload, timeout=15)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS! Image: {len(data.get('image', ''))} bytes")
                print("\n🎉 REMOTE COMPUTE IS NOW ACTIVE!")
            else:
                print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    else:
        print(f"⚠️  Update: {update_response.status_code}")
else:
    print(f"⚠️  Get: {get_response.status_code}")
    print(f"   Response: {get_response.text[:200]}")

print("\n" + "=" * 80)
