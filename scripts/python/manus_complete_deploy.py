#!/usr/bin/env python3
"""
@MANUS Complete Deployment Solution
Handles all deployment scenarios including subscription issues
"""
import sys
import subprocess
import json
import requests
import time
import zipfile
import io
from pathlib import Path
from azure.identity import DefaultAzureCredential

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

function_code_path = project_root / "azure_functions" / "RenderIronLegion" / "__init__.py"
function_app_name = "jarvis-lumina-functions"
resource_group = "jarvis-lumina-rg"

print("=" * 80)
print("🔥 @MANUS: Complete Deployment Solution")
print("=" * 80)

# Get Azure credentials
try:
    credential = DefaultAzureCredential(

                        exclude_interactive_browser_credential=False,

                        exclude_shared_token_cache_credential=False

                    )
    token = credential.get_token("https://management.azure.com/.default").token
    print("✅ Azure credentials obtained")
except Exception as e:
    print(f"❌ Credential error: {e}")
    sys.exit(1)

# Get subscription from current account
az_cmd = r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
result = subprocess.run([az_cmd, "account", "show", "--output", "json"],
                       capture_output=True, text=True, timeout=10, shell=True)
if result.returncode == 0:
    account = json.loads(result.stdout)
    subscription_id = account.get('id')
    print(f"✅ Using subscription: {subscription_id}")
else:
    print("❌ Could not get subscription")
    sys.exit(1)

# Load function code
with open(function_code_path, 'r', encoding='utf-8') as f:
    function_code = f.read()

# Setup API
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Check/create storage account
storage_account = "jarvisluminastorage"
storage_api_url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Storage/storageAccounts/{storage_account}"

print(f"\n🏗️  Setting up resources...")
check_response = requests.get(storage_api_url + "?api-version=2023-01-01", headers=headers, timeout=10)
if check_response.status_code == 404:
    print(f"   Creating storage account: {storage_account}...")
    storage_config = {
        "location": "eastus",
        "sku": {"name": "Standard_LRS"},
        "kind": "StorageV2"
    }
    create_response = requests.put(storage_api_url + "?api-version=2023-01-01",
                                  json=storage_config, headers=headers, timeout=60)
    if create_response.status_code in [200, 201, 202]:
        print("   ✅ Storage account created/creating")
        time.sleep(5)  # Wait for provisioning
    else:
        print(f"   ⚠️  Storage creation: {create_response.status_code}")
elif check_response.status_code == 200:
    print(f"   ✅ Storage account exists")
else:
    print(f"   ⚠️  Storage check: {check_response.status_code}")

# Get storage connection string
storage_key_url = f"{storage_api_url}/listKeys?api-version=2023-01-01"
storage_keys = requests.post(storage_key_url, headers=headers, timeout=10)
if storage_keys.status_code == 200:
    keys_data = storage_keys.json()
    storage_key = keys_data.get('keys', [{}])[0].get('value', '')
    storage_conn_str = f"DefaultEndpointsProtocol=https;AccountName={storage_account};AccountKey={storage_key};EndpointSuffix=core.windows.net"
else:
    storage_conn_str = f"DefaultEndpointsProtocol=https;AccountName={storage_account};EndpointSuffix=core.windows.net"

# Create App Service Plan
plan_name = f"{function_app_name}-plan"
plan_api_url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Web/serverfarms/{plan_name}"

print("   Creating App Service Plan...")
plan_check = requests.get(plan_api_url + "?api-version=2022-03-01", headers=headers, timeout=10)
if plan_check.status_code == 200:
    print("   ✅ App Service Plan exists")
    plan_id = plan_api_url
else:
    plan_config = {
        "location": "eastus",
        "sku": {
            "name": "Y1",
            "tier": "Dynamic"
        }
    }
    plan_response = requests.put(plan_api_url + "?api-version=2022-03-01", json=plan_config, headers=headers, timeout=60)
    if plan_response.status_code in [200, 201, 202]:
        print("   ✅ App Service Plan created")
        plan_id = plan_api_url
    else:
        print(f"   ⚠️  Plan creation: {plan_response.status_code}")
        plan_id = plan_api_url  # Use anyway

# Create Function App
function_app_api_url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Web/sites/{function_app_name}"

print(f"\n📦 Creating Function App: {function_app_name}...")
function_app_config = {
    "location": "eastus",
    "kind": "functionapp,linux",
    "properties": {
        "serverFarmId": plan_id,
        "siteConfig": {
            "linuxFxVersion": "Python|3.11",
            "appSettings": [
                {"name": "AzureWebJobsStorage", "value": storage_conn_str},
                {"name": "WEBSITE_CONTENTAZUREFILECONNECTIONSTRING", "value": storage_conn_str},
                {"name": "WEBSITE_CONTENTSHARE", "value": function_app_name.lower()[:63]},
                {"name": "FUNCTIONS_EXTENSION_VERSION", "value": "~4"},
                {"name": "FUNCTIONS_WORKER_RUNTIME", "value": "python"}
            ]
        }
    }
}

app_response = requests.put(function_app_api_url + "?api-version=2022-03-01", json=function_app_config, headers=headers, timeout=120)
if app_response.status_code in [200, 201, 202]:
    print("✅ Function App created!")

    # Wait for provisioning
    print("   Waiting for Function App to provision...")
    time.sleep(15)

    # Deploy function code
    print("\n📤 Deploying function code...")

    # Create ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("RenderIronLegion/__init__.py", function_code)
        zip_file.writestr("host.json", json.dumps({
            "version": "2.0",
            "extensionBundle": {
                "id": "Microsoft.Azure.Functions.ExtensionBundle",
                "version": "[3.*, 4.0.0)"
            }
        }))
        zip_file.writestr("requirements.txt", "azure-functions\nPillow>=10.0.0")

    zip_data = zip_buffer.getvalue()

    # Deploy via Kudu
    kudu_url = f"https://{function_app_name}.scm.azurewebsites.net/api/zipdeploy"
    kudu_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/zip"
    }

    deploy_response = requests.post(kudu_url, data=zip_data, headers=kudu_headers, timeout=120)

    if deploy_response.status_code in [200, 202]:
        print("✅ Function code deployed!")
        print(f"\n🌐 Endpoint: https://{function_app_name}.azurewebsites.net/api/RenderIronLegion")
        print("   Remote compute is now ACTIVE")

        # Test
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
            else:
                print(f"⚠️  Status: {test_response.status_code}")
        except Exception as e:
            print(f"⚠️  Test error: {e}")
    else:
        print(f"⚠️  Deployment status: {deploy_response.status_code}")
        print("   Function App created but code deployment had issues")
else:
    print(f"❌ Function App creation failed: {app_response.status_code}")
    print(f"   Response: {app_response.text[:500]}")

print("\n" + "=" * 80)
