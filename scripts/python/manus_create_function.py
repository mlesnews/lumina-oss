#!/usr/bin/env python3
"""
@MANUS Create Function in Function App
Creates the RenderIronLegion function within the existing Function App
"""
import sys
import subprocess
import json
import requests
from pathlib import Path
from azure.identity import DefaultAzureCredential

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

function_code_path = project_root / "azure_functions" / "RenderIronLegion" / "__init__.py"
function_app_name = "jarvis-lumina-functions"
resource_group = "jarvis-lumina-rg"

print("=" * 80)
print("🔥 @MANUS: Creating Function in Function App")
print("=" * 80)

# Get credentials
credential = DefaultAzureCredential(

                    exclude_interactive_browser_credential=False,

                    exclude_shared_token_cache_credential=False

                )
token = credential.get_token("https://management.azure.com/.default").token

# Get subscription
az_cmd = r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
result = subprocess.run([az_cmd, "account", "show", "--output", "json"],
                       capture_output=True, text=True, timeout=10, shell=True)
subscription_id = json.loads(result.stdout).get('id')

# Load function code
with open(function_code_path, 'r', encoding='utf-8') as f:
    function_code = f.read()

# Create function via Functions API
function_api_url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Web/sites/{function_app_name}/functions/RenderIronLegion"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

function_config = {
    "properties": {
        "config": {
            "bindings": [
                {
                    "authLevel": "function",
                    "type": "httpTrigger",
                    "direction": "in",
                    "name": "req",
                    "methods": ["post"]
                },
                {
                    "type": "http",
                    "direction": "out",
                    "name": "$return"
                }
            ]
        },
        "files": {
            "__init__.py": function_code
        },
        "test_data": ""
    }
}

print(f"📦 Creating function: RenderIronLegion...")
response = requests.put(function_api_url + "?api-version=2022-03-01", json=function_config, headers=headers, timeout=60)

if response.status_code in [200, 201]:
    print("✅ Function created!")
    print(f"\n🌐 Endpoint: https://{function_app_name}.azurewebsites.net/api/RenderIronLegion")

    # Test
    import time
    print("\n🧪 Testing endpoint...")
    time.sleep(5)
    try:
        test_response = requests.post(
            f"https://{function_app_name}.azurewebsites.net/api/RenderIronLegion",
            json={"state": "armor", "animation_frame": 0, "transformation_progress": 1.0, "size": 180},
            timeout=10
        )
        if test_response.status_code == 200:
            print("✅ Endpoint responding!")
            data = test_response.json()
            print(f"   Image size: {len(data.get('image', ''))} bytes")
            print("\n🎉 REMOTE COMPUTE IS NOW ACTIVE!")
        else:
            print(f"⚠️  Status: {test_response.status_code}")
            print("   Function may need a moment to activate")
    except Exception as e:
        print(f"⚠️  Test error: {e}")
else:
    print(f"❌ Function creation failed: {response.status_code}")
    print(f"   Response: {response.text[:500]}")

print("\n" + "=" * 80)
