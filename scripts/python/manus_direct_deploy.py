#!/usr/bin/env python3
"""
@MANUS Direct Deployment - Bypass subscription issues
Deploys function code directly if Function App already exists
"""
import sys
import subprocess
import json
import zipfile
import tempfile
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

function_code_path = project_root / "azure_functions" / "RenderIronLegion" / "__init__.py"
function_app_name = "jarvis-lumina-functions"
resource_group = "jarvis-lumina-rg"

print("=" * 80)
print("🔥 @MANUS: Direct Function Deployment")
print("=" * 80)

# Check if Function App exists
az_cmd = r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"

print(f"\n🔍 Checking Function App: {function_app_name}...")
result = subprocess.run(
    [az_cmd, "functionapp", "show", "--name", function_app_name, "--resource-group", resource_group],
    capture_output=True, text=True, timeout=10, shell=True
)

if result.returncode != 0:
    print("❌ Function App does not exist")
    print("   Need to create Function App first via Azure Portal")
    print(f"   Go to: https://portal.azure.com/#@/resource/subscriptions/resourceGroups/{resource_group}")
    sys.exit(1)

print("✅ Function App exists - deploying function code...")

# Load function code
with open(function_code_path, 'r', encoding='utf-8') as f:
    function_code = f.read()

# Create deployment package
with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp_zip:
    zip_path = tmp_zip.name
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("RenderIronLegion/__init__.py", function_code)
        zip_file.writestr("host.json", json.dumps({
            "version": "2.0",
            "extensionBundle": {
                "id": "Microsoft.Azure.Functions.ExtensionBundle",
                "version": "[3.*, 4.0.0)"
            }
        }))
        zip_file.writestr("requirements.txt", "azure-functions\nPillow>=10.0.0")

print(f"📦 Package created: {len(open(zip_path, 'rb').read())} bytes")

# Deploy
print("📤 Deploying...")
deploy_result = subprocess.run(
    [az_cmd, "functionapp", "deployment", "source", "config-zip",
     "--resource-group", resource_group,
     "--name", function_app_name,
     "--src", zip_path],
    capture_output=True, text=True, timeout=300, shell=True
)

if deploy_result.returncode == 0:
    print("✅ Function deployed!")
    print(f"\n🌐 Endpoint: https://{function_app_name}.azurewebsites.net/api/RenderIronLegion")

    # Test
    import requests
    import time
    print("\n🧪 Testing endpoint...")
    time.sleep(3)

    try:
        test_response = requests.post(
            f"https://{function_app_name}.azurewebsites.net/api/RenderIronLegion",
            json={"state": "armor", "animation_frame": 0, "transformation_progress": 1.0, "size": 180},
            timeout=10
        )
        if test_response.status_code == 200:
            print("✅ Endpoint responding!")
        else:
            print(f"⚠️  Status: {test_response.status_code}")
    except Exception as e:
        print(f"⚠️  Test error: {e}")
else:
    print(f"❌ Deployment failed: {deploy_result.stderr[:500]}")

# Cleanup
import os
try:
    os.unlink(zip_path)
except:
    pass
