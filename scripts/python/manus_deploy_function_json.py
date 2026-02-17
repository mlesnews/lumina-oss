#!/usr/bin/env python3
"""
@MANUS Deploy function.json via Kudu
Deploys the function binding configuration
"""
import sys
import json
import requests
from pathlib import Path
from azure.identity import DefaultAzureCredential

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

function_json_path = project_root / "azure_functions" / "RenderIronLegion" / "function.json"
function_app_name = "jarvis-lumina-functions"

print("=" * 80)
print("🔥 @MANUS: Deploying function.json")
print("=" * 80)

# Get credentials
credential = DefaultAzureCredential(

                    exclude_interactive_browser_credential=False,

                    exclude_shared_token_cache_credential=False

                )
token = credential.get_token("https://management.azure.com/.default").token

# Load function.json
with open(function_json_path, 'r') as f:
    function_json_content = f.read()

# Deploy via Kudu API
kudu_url = f"https://{function_app_name}.scm.azurewebsites.net/api/vfs/site/wwwroot/RenderIronLegion/function.json"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print(f"📤 Uploading function.json...")
response = requests.put(kudu_url, data=function_json_content, headers=headers, timeout=30)

if response.status_code in [200, 201, 204]:
    print("✅ function.json deployed!")

    # Test endpoint
    import time
    print("\n🧪 Testing endpoint...")
    time.sleep(5)

    test_response = requests.post(
        f"https://{function_app_name}.azurewebsites.net/api/RenderIronLegion",
        json={"state": "armor", "animation_frame": 0, "transformation_progress": 1.0, "size": 180},
        timeout=10
    )

    if test_response.status_code == 200:
        print("✅ Endpoint is responding!")
        data = test_response.json()
        print(f"   Image size: {len(data.get('image', ''))} bytes")
        print("\n🎉 REMOTE COMPUTE IS NOW ACTIVE!")
    else:
        print(f"⚠️  Status: {test_response.status_code}")
        print("   Function may need more time to sync")
else:
    print(f"⚠️  Deployment: {response.status_code}")
    print(f"   Response: {response.text[:200]}")

print("\n" + "=" * 80)
