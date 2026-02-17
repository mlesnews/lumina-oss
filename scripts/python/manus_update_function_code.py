#!/usr/bin/env python3
"""
@MANUS Update Function Code via Management API
Updates the function code directly via Azure Management API
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
resource_group = "jarvis-lumina-rg"

print("=" * 80)
print("🔥 @MANUS: Update Function Code via Management API")
print("=" * 80)

# Get credentials
credential = DefaultAzureCredential(

                    exclude_interactive_browser_credential=False,

                    exclude_shared_token_cache_credential=False

                )
token = credential.get_token("https://management.azure.com/.default").token

# Get subscription
az_cmd = r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
import subprocess
result = subprocess.run([az_cmd, "account", "show", "--output", "json"], 
                       capture_output=True, text=True, timeout=10, shell=True)
subscription_id = json.loads(result.stdout).get('id')

# Load files
with open(function_code_path, 'r', encoding='utf-8') as f:
    function_code = f.read()

with open(function_json_path, 'r') as f:
    function_json_data = json.load(f)

# Update function via Management API
function_api_url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Web/sites/{function_app_name}/functions/RenderIronLegion"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Get current function config first
print("🔍 Getting current function configuration...")
get_response = requests.get(function_api_url + "?api-version=2022-03-01", headers=headers, timeout=30)

if get_response.status_code == 200:
    current_config = get_response.json()
    print("✅ Function configuration retrieved")

    # Update with new code
    print("📤 Updating function code...")
    function_config = {
        "properties": {
            "config": function_json_data.get("bindings", []),
            "files": {
                "__init__.py": function_code
            },
            "test_data": ""
        }
    }

    # Use PATCH to update
    update_response = requests.patch(function_api_url + "?api-version=2022-03-01", json=function_config, headers=headers, timeout=60)

    if update_response.status_code in [200, 201]:
        print("✅ Function code updated!")

        # Wait and test
        import time
        print("⏳ Waiting for function to sync...")
        time.sleep(10)

        # Get function key
        result = subprocess.run(
            [az_cmd, "functionapp", "function", "keys", "list",
             "--name", function_app_name,
             "--resource-group", resource_group,
             "--function-name", "RenderIronLegion",
             "--output", "json"],
            capture_output=True, text=True, timeout=10, shell=True
        )

        function_key = None
        if result.returncode == 0:
            keys_data = json.loads(result.stdout)
            function_key = keys_data.get("default", "")

        # Test
        endpoint = f"https://{function_app_name}.azurewebsites.net/api/renderironlegion"
        url = f"{endpoint}?code={function_key}" if function_key else endpoint

        print(f"\n🧪 Testing: {endpoint}")
        payload = {"state": "armor", "animation_frame": 0, "transformation_progress": 1.0, "size": 180}

        try:
            response = requests.post(url, json=payload, timeout=15)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ SUCCESS! Image: {len(data.get('image', ''))} bytes")
                print("\n🎉 REMOTE COMPUTE IS NOW ACTIVE!")
                print(f"   Endpoint: {endpoint}")
            else:
                print(f"   Response: {response.text[:200]}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    else:
        print(f"❌ Update failed: {update_response.status_code}")
        print(f"   Response: {update_response.text[:300]}")
else:
    print(f"❌ Could not get function: {get_response.status_code}")

print("\n" + "=" * 80)
