#!/usr/bin/env python3
"""
Deploy Azure Function: RenderIronLegion
Actually deploys the function to Azure
"""
import subprocess
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
function_dir = project_root / "azure_functions"
function_app_name = "jarvis-lumina-functions"

def check_azure_cli():
    """Check if Azure CLI is installed"""
    try:
        result = subprocess.run(["az", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Azure CLI is installed")
            return True
        return False
    except FileNotFoundError:
        print("❌ Azure CLI not found")
        return False

def check_func_tools():
    """Check if Azure Functions Core Tools is installed"""
    try:
        result = subprocess.run(["func", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Azure Functions Core Tools: {result.stdout.strip()}")
            return True
        return False
    except FileNotFoundError:
        print("❌ Azure Functions Core Tools not found")
        print("   Install: npm install -g azure-functions-core-tools@4")
        return False

def deploy_function():
    """Deploy the function"""
    print(f"🚀 Deploying to {function_app_name}...")
    print(f"   Function directory: {function_dir}")

    try:
        # Change to function directory
        result = subprocess.run(
            ["func", "azure", "functionapp", "publish", function_app_name],
            cwd=str(function_dir),
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("✅ Function deployed successfully!")
            print(result.stdout)
            return True
        else:
            print("❌ Deployment failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Deployment error: {e}")
        return False

def main():
    print("=" * 80)
    print("🚀 Azure Function Deployment")
    print("=" * 80)

    # Check prerequisites
    if not check_azure_cli():
        print("\n📋 Install Azure CLI: https://aka.ms/installazurecliwindows")
        return 1

    if not check_func_tools():
        print("\n📋 Install Functions Core Tools: npm install -g azure-functions-core-tools@4")
        return 1

    # Deploy
    if deploy_function():
        print("\n✅ Deployment complete!")
        print(f"   Endpoint: https://{function_app_name}.azurewebsites.net/api/RenderIronLegion")
        return 0
    else:
        print("\n❌ Deployment failed - check errors above")
        return 1

if __name__ == "__main__":


    sys.exit(main())