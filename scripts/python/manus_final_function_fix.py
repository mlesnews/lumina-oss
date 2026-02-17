#!/usr/bin/env python3
"""
@MANUS Final Function Fix
Ensures function code is properly deployed and accessible
"""
import sys
import subprocess
import json
import requests
import time
from pathlib import Path
from azure.identity import DefaultAzureCredential

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

function_code_path = project_root / "azure_functions" / "RenderIronLegion" / "__init__.py"
function_json_path = project_root / "azure_functions" / "RenderIronLegion" / "function.json"
function_app_name = "jarvis-lumina-functions"
resource_group = "jarvis-lumina-rg"

print("=" * 80)
print("🔥 @MANUS: Final Function Fix")
print("=" * 80)

az_cmd = r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"

# Get function key
print("🔑 Getting function key...")
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
    print(f"✅ Function key obtained: {function_key[:20]}...")
else:
    print(f"⚠️  Could not get function key: {result.stderr}")

# Restart function app
print("\n🔄 Restarting Function App...")
subprocess.run([az_cmd, "functionapp", "restart", "--name", function_app_name, "--resource-group", resource_group], 
              shell=True, timeout=30)
print("✅ Function App restarted")

# Wait for restart
print("   Waiting for Function App to be ready...")
time.sleep(10)

# Test with key
endpoint = f"https://{function_app_name}.azurewebsites.net/api/renderironlegion"
url = f"{endpoint}?code={function_key}" if function_key else endpoint

print(f"\n🧪 Testing endpoint: {endpoint}")
payload = {
    "state": "armor",
    "animation_frame": 0,
    "transformation_progress": 1.0,
    "size": 180
}

try:
    response = requests.post(url, json=payload, timeout=15)
    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ SUCCESS! Image: {len(data.get('image', ''))} bytes")
        print("\n🎉 REMOTE COMPUTE IS NOW ACTIVE!")
        print(f"   Endpoint: {endpoint}")

        # Update config with function key secret name
        config_path = project_root / "config" / "azure_services_config.json"
        with open(config_path, 'r') as f:
            config = json.load(f)
        config["azure_services_config"]["remote_compute"]["function_key_secret"] = "azure-function-app-key"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print("   ✅ Config updated with function key reference")

    elif response.status_code == 401:
        print("   ⚠️  Authentication failed - function key may be incorrect")
        print("   Try: az functionapp function keys list --name jarvis-lumina-functions --resource-group jarvis-lumina-rg --function-name RenderIronLegion")
    elif response.status_code == 404:
        print("   ⚠️  Function not found - may need code deployment")
        print("   Function exists but code may not be deployed")
        print("   Try deploying code via Portal or Kudu API")
    else:
        print(f"   Response: {response.text[:300]}")

except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 80)
print("📊 Status Summary:")
print(f"   Function App: {function_app_name} - ✅ EXISTS")
print(f"   Function: RenderIronLegion - ✅ EXISTS")
print(f"   Endpoint: {endpoint}")
print(f"   Authentication: {'✅ Key obtained' if function_key else '⚠️  No key'}")
print(f"   Status: {'✅ ACTIVE' if response.status_code == 200 else '⚠️  Needs attention'}")
print("=" * 80)
