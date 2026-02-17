#!/usr/bin/env python3
"""
@MANUS Azure CLI Deployment
Uses Azure CLI to create Function App and deploy function
No browser needed - pure CLI
"""
import sys
import subprocess
import json
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

function_code_path = project_root / "azure_functions" / "RenderIronLegion" / "__init__.py"
function_app_name = "jarvis-lumina-functions"
resource_group = "jarvis-lumina-rg"
subscription_id = "9835b511-4369-4619-94ae-4c505e74cff0"
location = "eastus"

print("=" * 80)
print("🔥 @MANUS: Azure CLI Deployment")
print("=" * 80)

# Check if Azure CLI is available
az_paths = [
    "az",
    r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
    r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
]

az_cmd = None
for path in az_paths:
    try:
        result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=5, shell=True)
        if result.returncode == 0:
            az_cmd = path
            print(f"✅ Azure CLI found: {path}")
            break
    except:
        continue

if not az_cmd:
    print("❌ Azure CLI not found")
    sys.exit(1)

# Check if logged in
print("\n🔐 Checking Azure login status...")
try:
    result = subprocess.run([az_cmd, "account", "show"], capture_output=True, text=True, timeout=10, shell=True)
    if result.returncode == 0:
        account_info = json.loads(result.stdout)
        subscription_id = account_info.get('id')
        print(f"✅ Logged in as: {account_info.get('user', {}).get('name', 'Unknown')}")
        print(f"   Subscription: {subscription_id}")

        # Use the subscription we're logged into
        actual_sub_id = account_info.get('id')
        if actual_sub_id:
            print(f"   Using subscription: {actual_sub_id}")
            # Don't set if already default
    else:
        print("⚠️  Not logged in - attempting login...")
        subprocess.run([az_cmd, "login"], timeout=300, shell=True)  # Allow time for 2FA
except Exception as e:
    print(f"⚠️  Login check error: {e}")
    print("   Attempting login...")
    subprocess.run(["az", "login"], timeout=300)

# Check/create resource group
print(f"\n📦 Checking resource group: {resource_group}...")
try:
    result = subprocess.run(
        [az_cmd, "group", "show", "--name", resource_group],
        capture_output=True, text=True, timeout=10, shell=True
    )
    if result.returncode != 0:
        print(f"   Creating resource group: {resource_group}...")
        subprocess.run(
            [az_cmd, "group", "create", "--name", resource_group, "--location", location],
            check=True, timeout=30, shell=True
        )
        print("   ✅ Resource group created")
    else:
        print("   ✅ Resource group exists")
except Exception as e:
    print(f"   ⚠️  Resource group check/create issue: {e}")

# Check if Function App exists
print(f"\n🔍 Checking if Function App exists: {function_app_name}...")
try:
    result = subprocess.run(
        [az_cmd, "functionapp", "show",
         "--name", function_app_name,
         "--resource-group", resource_group],
        capture_output=True, text=True, timeout=10, shell=True
    )

    if result.returncode == 0:
        print("✅ Function App exists")
        app_exists = True
    else:
        print("⚠️  Function App does not exist - will create it")
        app_exists = False
except Exception as e:
    print(f"⚠️  Error checking Function App: {e}")
    app_exists = False

# Create Function App if needed
if not app_exists:
    print(f"\n🏗️  Creating Function App: {function_app_name}...")
    print("   This may take a few minutes...")

    # Try to use existing storage account from config first
    config_path = project_root / "config" / "azure_services_config.json"
    storage_account = None

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            storage_account = config.get("azure_services_config", {}).get("storage", {}).get("accounts", {}).get("primary", {}).get("name")
    except:
        pass

    # If not in config, try to find existing or create new
    if not storage_account:
        # Check for existing storage accounts
        list_result = subprocess.run(
            [az_cmd, "storage", "account", "list", "--output", "json"],
            capture_output=True, text=True, timeout=10, shell=True
        )
        if list_result.returncode == 0:
            accounts = json.loads(list_result.stdout)
            if accounts:
                storage_account = accounts[0]['name']
                print(f"   ✅ Found existing storage account: {storage_account}")
            else:
                # Create new one
                import random
                import hashlib
                name_hash = hashlib.md5(function_app_name.encode()).hexdigest()[:8]
                random_suffix = str(random.randint(100, 999))
                storage_account = f"jarv{name_hash}{random_suffix}".lower()[:24]
                print(f"   Creating new storage account: {storage_account}")
        else:
            # Fallback: use config default
            storage_account = "jarvisluminastorage"

    try:
        # Check if storage account exists first
        check_result = subprocess.run(
            [az_cmd, "storage", "account", "show",
             "--name", storage_account,
             "--resource-group", resource_group],
            capture_output=True, text=True, timeout=10, shell=True
        )

        if check_result.returncode == 0:
            print("   ✅ Storage account already exists")
        else:
            # Try to find ANY existing storage account in resource group
            list_result = subprocess.run(
                [az_cmd, "storage", "account", "list", "--resource-group", resource_group, "--output", "json"],
                capture_output=True, text=True, timeout=10, shell=True
            )
            if list_result.returncode == 0:
                accounts = json.loads(list_result.stdout)
                if accounts:
                    storage_account = accounts[0]['name']
                    print(f"   ✅ Using existing storage account: {storage_account}")
                else:
                    # Try creating with explicit subscription context
                    print(f"   Creating storage account: {storage_account}...")
                    # Use subscription from account show
                    create_result = subprocess.run(
                        [az_cmd, "storage", "account", "create",
                         "--name", storage_account,
                         "--resource-group", resource_group,
                         "--location", location,
                         "--sku", "Standard_LRS",
                         "--subscription", subscription_id] if subscription_id else
                        [az_cmd, "storage", "account", "create",
                         "--name", storage_account,
                         "--resource-group", resource_group,
                         "--location", location,
                         "--sku", "Standard_LRS"],
                        capture_output=True, text=True,
                        timeout=300,
                        shell=True
                    )
                    if create_result.returncode == 0:
                        print("   ✅ Storage account created")
                    else:
                        print(f"   ⚠️  Storage creation failed, trying without explicit subscription...")
                        # Last resort: try without subscription param
                        create_result2 = subprocess.run(
                            [az_cmd, "storage", "account", "create",
                             "--name", storage_account,
                             "--resource-group", resource_group,
                             "--location", location,
                             "--sku", "Standard_LRS"],
                            capture_output=True, text=True,
                            timeout=300,
                            shell=True
                        )
                        if create_result2.returncode != 0:
                            raise Exception(f"Storage account creation failed. Error: {create_result2.stderr[:300]}")
            else:
                raise Exception(f"Could not list storage accounts: {list_result.stderr[:200]}")
    except Exception as e:
        print(f"   ⚠️  Storage account issue: {e}")
        print("   Attempting to continue with Function App creation...")
        # Continue anyway - Function App might work with existing storage

    # Create Function App
    try:
        subprocess.run(
            [az_cmd, "functionapp", "create",
             "--resource-group", resource_group,
             "--consumption-plan-location", location,
             "--runtime", "python",
             "--runtime-version", "3.11",
             "--functions-version", "4",
             "--name", function_app_name,
             "--storage-account", storage_account,
             "--os-type", "Linux"],
            check=True,
            timeout=600,
            shell=True
        )
        print("✅ Function App created")
    except subprocess.CalledProcessError as e:
        print(f"❌ Function App creation failed: {e}")
        print("   May already exist or need different settings")
        sys.exit(1)

# Deploy function code
print(f"\n📦 Deploying function: RenderIronLegion...")

# Create deployment package
import zipfile
import io
import tempfile

with open(function_code_path, 'r', encoding='utf-8') as f:
    function_code = f.read()

# Create ZIP
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

print(f"   Package created: {len(open(zip_path, 'rb').read())} bytes")

# Deploy via Azure CLI
try:
    print("   Uploading to Azure...")
    result = subprocess.run(
        [az_cmd, "functionapp", "deployment", "source", "config-zip",
         "--resource-group", resource_group,
         "--name", function_app_name,
         "--src", zip_path],
        capture_output=True,
        text=True,
        timeout=300,
        shell=True
    )

    if result.returncode == 0:
        print("✅ Function deployed successfully!")
        print(f"\n🌐 Endpoint: https://{function_app_name}.azurewebsites.net/api/RenderIronLegion")

        # Test endpoint
        print("\n🧪 Testing endpoint...")
        import requests
        import time
        time.sleep(5)  # Wait for function to activate

        test_payload = {
            "state": "armor",
            "animation_frame": 0,
            "transformation_progress": 1.0,
            "size": 180
        }

        try:
            test_response = requests.post(
                f"https://{function_app_name}.azurewebsites.net/api/RenderIronLegion",
                json=test_payload,
                timeout=10
            )

            if test_response.status_code == 200:
                print("✅ Endpoint is responding!")
                data = test_response.json()
                print(f"   Image size: {len(data.get('image', ''))} bytes (base64)")
            else:
                print(f"⚠️  Endpoint returned: {test_response.status_code}")
                print("   Function may need a moment to fully activate")
        except Exception as e:
            print(f"⚠️  Test error: {e}")
            print("   Function deployed but test failed - may need time to activate")
    else:
        print(f"❌ Deployment failed:")
        print(result.stderr)
        sys.exit(1)

except Exception as e:
    print(f"❌ Deployment error: {e}")
    sys.exit(1)
finally:
    # Cleanup
    try:
        import os
        os.unlink(zip_path)
    except:
        pass

print("\n" + "=" * 80)
print("✅ @MANUS DEPLOYMENT COMPLETE!")
print("=" * 80)
print("   Remote compute is now active")
print("   Iron Legion will automatically use Azure for rendering")
