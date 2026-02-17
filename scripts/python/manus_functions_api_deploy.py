#!/usr/bin/env python3
"""
@MANUS Direct Azure Functions API Deployment
Deploys function code directly via Functions Runtime API
"""
import sys
import json
import requests
import base64
from pathlib import Path
from azure.identity import DefaultAzureCredential

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

function_code_path = project_root / "azure_functions" / "RenderIronLegion" / "__init__.py"
function_app_name = "jarvis-lumina-functions"
function_name = "RenderIronLegion"

print("=" * 80)
print("🔥 @MANUS: Direct Functions API Deployment")
print("=" * 80)

# Get Azure credentials
credential = DefaultAzureCredential(

                    exclude_interactive_browser_credential=False,

                    exclude_shared_token_cache_credential=False

                )
token = credential.get_token("https://management.azure.com/.default").token

# Load function code
with open(function_code_path, 'r', encoding='utf-8') as f:
    function_code = f.read()

# Function App management endpoint
subscription_id = "9835b511-4369-4619-94ae-4c505e74cff0"
resource_group = "jarvis-lumina-rg"
api_version = "2022-03-01"

# Deploy via Kudu API (Functions runtime)
kudu_url = f"https://{function_app_name}.scm.azurewebsites.net/api/vfs/site/wwwroot/{function_name}/__init__.py"

print(f"📤 Uploading function code to: {kudu_url}")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "text/plain"
}

try:
    response = requests.put(kudu_url, data=function_code, headers=headers, timeout=30)

    if response.status_code in [200, 201, 204]:
        print("✅ Function code deployed successfully!")
        print(f"   Endpoint: https://{function_app_name}.azurewebsites.net/api/{function_name}")

        # Test the endpoint
        test_url = f"https://{function_app_name}.azurewebsites.net/api/{function_name}"
        test_payload = {
            "state": "armor",
            "animation_frame": 0,
            "transformation_progress": 1.0,
            "size": 180
        }

        print("\n🧪 Testing endpoint...")
        test_response = requests.post(test_url, json=test_payload, timeout=10)

        if test_response.status_code == 200:
            print("✅ Endpoint is responding!")
            data = test_response.json()
            print(f"   Image size: {len(data.get('image', ''))} bytes")
        else:
            print(f"⚠️  Endpoint returned: {test_response.status_code}")
            print("   Function may need a moment to activate")
    else:
        print(f"❌ Deployment failed: {response.status_code}")
        print(f"   Response: {response.text[:200]}")

except Exception as e:
    print(f"❌ Deployment error: {e}")
    print("\n💡 Browser automation is running as backup")
    print("   Check the Chrome window for deployment progress")
