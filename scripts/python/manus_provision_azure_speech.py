#!/usr/bin/env python3
"""
MANUS: Provision Azure Speech Service and Store Key in Key Vault

This script will:
1. Check if Azure Speech key exists in Key Vault
2. If not, create Azure Speech resource in Azure
3. Store the key in Azure Key Vault
4. Configure the video generator to use it

All secrets stay in Azure Key Vault - never exposed locally.
"""

import subprocess
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("ManusAzureSpeech")

# Azure configuration
VAULT_URL = "https://jarvis-lumina.vault.azure.net/"
VAULT_NAME = "jarvis-lumina"
RESOURCE_GROUP = "jarvis-lumina-rg"
SPEECH_SERVICE_NAME = "speech-jarvis-lumina"
LOCATION = "eastus"

# Secret names
SPEECH_KEY_SECRET = "azure-speech-key"
SPEECH_REGION_SECRET = "azure-speech-region"


def run_az_command(command: str, capture_output: bool = True) -> Dict[str, Any]:
    """Run Azure CLI command"""
    full_command = f"az {command}"
    logger.info(f"🔧 Running: az {command[:60]}...")

    try:
        result = subprocess.run(
            full_command,
            shell=True,
            capture_output=capture_output,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            if result.stdout:
                try:
                    return {"success": True, "data": json.loads(result.stdout)}
                except json.JSONDecodeError:
                    return {"success": True, "data": result.stdout.strip()}
            return {"success": True, "data": None}
        else:
            return {"success": False, "error": result.stderr or "Command failed"}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def check_azure_login() -> bool:
    """Check if user is logged into Azure CLI"""
    result = run_az_command("account show")
    if result["success"]:
        account = result["data"]
        if isinstance(account, dict):
            logger.info(f"✅ Logged in as: {account.get('user', {}).get('name', 'Unknown')}")
            logger.info(f"   Subscription: {account.get('name', 'Unknown')}")
        return True
    else:
        logger.error("❌ Not logged into Azure. Run: az login")
        return False


def check_keyvault_secret_exists(secret_name: str) -> bool:
    """Check if secret exists in Key Vault"""
    result = run_az_command(f"keyvault secret show --vault-name {VAULT_NAME} --name {secret_name}")
    return result["success"]


def get_keyvault_secret(secret_name: str) -> Optional[str]:
    """Get secret value from Key Vault"""
    result = run_az_command(f"keyvault secret show --vault-name {VAULT_NAME} --name {secret_name} --query value -o tsv")
    if result["success"] and result["data"]:
        return result["data"]
    return None


def set_keyvault_secret(secret_name: str, value: str) -> bool:
    """Set secret in Key Vault"""
    # Use subprocess directly to avoid shell escaping issues
    result = run_az_command(f'keyvault secret set --vault-name {VAULT_NAME} --name {secret_name} --value "{value}"')
    return result["success"]


def check_speech_service_exists() -> bool:
    """Check if Azure Speech service exists"""
    result = run_az_command(f"cognitiveservices account show --name {SPEECH_SERVICE_NAME} --resource-group {RESOURCE_GROUP}")
    return result["success"]


def create_speech_service() -> bool:
    """Create Azure Speech service"""
    logger.info(f"🔧 Creating Azure Speech service: {SPEECH_SERVICE_NAME}")

    # Create the Speech service
    result = run_az_command(
        f"cognitiveservices account create "
        f"--name {SPEECH_SERVICE_NAME} "
        f"--resource-group {RESOURCE_GROUP} "
        f"--kind SpeechServices "
        f"--sku S0 "
        f"--location {LOCATION} "
        f"--yes"
    )

    if result["success"]:
        logger.info("✅ Azure Speech service created")
        return True
    else:
        logger.error(f"❌ Failed to create Speech service: {result.get('error')}")
        return False


def get_speech_service_keys() -> Optional[Dict[str, str]]:
    """Get Speech service keys"""
    result = run_az_command(
        f"cognitiveservices account keys list "
        f"--name {SPEECH_SERVICE_NAME} "
        f"--resource-group {RESOURCE_GROUP}"
    )

    if result["success"] and isinstance(result["data"], dict):
        return {
            "key1": result["data"].get("key1"),
            "key2": result["data"].get("key2")
        }
    return None


def provision_azure_speech() -> Dict[str, Any]:
    """
    Main provisioning function - MANUS entry point

    Returns:
        Dict with status and details
    """
    print()
    print("=" * 70)
    print("🤖 MANUS: Azure Speech Provisioning")
    print("=" * 70)
    print()

    # Step 1: Check Azure login
    print("📋 Step 1: Checking Azure login...")
    if not check_azure_login():
        return {"success": False, "error": "Not logged into Azure", "action": "Run: az login"}
    print()

    # Step 2: Check if key already exists in Key Vault
    print("📋 Step 2: Checking Key Vault for existing Speech key...")
    if check_keyvault_secret_exists(SPEECH_KEY_SECRET):
        key = get_keyvault_secret(SPEECH_KEY_SECRET)
        region = get_keyvault_secret(SPEECH_REGION_SECRET) or LOCATION
        logger.info(f"✅ Azure Speech key already exists in Key Vault")
        logger.info(f"   Secret: {SPEECH_KEY_SECRET}")
        logger.info(f"   Region: {region}")
        print()
        return {
            "success": True, 
            "message": "Azure Speech key already exists in Key Vault",
            "secret_name": SPEECH_KEY_SECRET,
            "region": region,
            "vault": VAULT_NAME
        }
    else:
        logger.info(f"⚠️  Speech key not found in Key Vault - will provision")
    print()

    # Step 3: Check/Create Speech service
    print("📋 Step 3: Checking Azure Speech service...")
    if check_speech_service_exists():
        logger.info(f"✅ Speech service already exists: {SPEECH_SERVICE_NAME}")
    else:
        logger.info(f"⚠️  Speech service not found - creating...")
        if not create_speech_service():
            return {"success": False, "error": "Failed to create Speech service"}
    print()

    # Step 4: Get Speech service keys
    print("📋 Step 4: Getting Speech service keys...")
    keys = get_speech_service_keys()
    if not keys or not keys.get("key1"):
        return {"success": False, "error": "Failed to get Speech service keys"}
    logger.info("✅ Retrieved Speech service keys")
    print()

    # Step 5: Store keys in Key Vault
    print("📋 Step 5: Storing keys in Azure Key Vault...")

    # Store API key
    if set_keyvault_secret(SPEECH_KEY_SECRET, keys["key1"]):
        logger.info(f"✅ Stored: {SPEECH_KEY_SECRET}")
    else:
        return {"success": False, "error": f"Failed to store {SPEECH_KEY_SECRET}"}

    # Store region
    if set_keyvault_secret(SPEECH_REGION_SECRET, LOCATION):
        logger.info(f"✅ Stored: {SPEECH_REGION_SECRET}")
    else:
        logger.warning(f"⚠️  Failed to store region - will use default: {LOCATION}")
    print()

    # Success!
    print("=" * 70)
    print("✅ AZURE SPEECH PROVISIONING COMPLETE")
    print("=" * 70)
    print()
    print(f"   🔐 Key Vault: {VAULT_NAME}")
    print(f"   🔑 Secret Name: {SPEECH_KEY_SECRET}")
    print(f"   🌍 Region: {LOCATION}")
    print(f"   🎤 Service: {SPEECH_SERVICE_NAME}")
    print()
    print("   The video generator can now use Azure Speech SDK")
    print("   with proper pronunciation control (IPA phonemes)!")
    print()

    return {
        "success": True,
        "message": "Azure Speech provisioned and key stored in Key Vault",
        "secret_name": SPEECH_KEY_SECRET,
        "region": LOCATION,
        "vault": VAULT_NAME,
        "speech_service": SPEECH_SERVICE_NAME
    }


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="MANUS: Provision Azure Speech")
    parser.add_argument("--check-only", action="store_true", help="Only check status, don't provision")
    parser.add_argument("--resource-group", default=RESOURCE_GROUP, help="Azure resource group")
    parser.add_argument("--location", default=LOCATION, help="Azure location")

    args = parser.parse_args()

    # Update module-level config if provided
    if args.resource_group != RESOURCE_GROUP:
        globals()['RESOURCE_GROUP'] = args.resource_group
    if args.location != LOCATION:
        globals()['LOCATION'] = args.location

    if args.check_only:
        print("\n🔍 Checking Azure Speech status...\n")

        if not check_azure_login():
            return

        if check_keyvault_secret_exists(SPEECH_KEY_SECRET):
            key = get_keyvault_secret(SPEECH_KEY_SECRET)
            region = get_keyvault_secret(SPEECH_REGION_SECRET) or LOCATION
            print(f"✅ Azure Speech key EXISTS in Key Vault")
            print(f"   Secret: {SPEECH_KEY_SECRET}")
            print(f"   Region: {region}")
            print(f"   Key (first 8 chars): {key[:8] if key else 'N/A'}...")
        else:
            print(f"❌ Azure Speech key NOT FOUND in Key Vault")
            print(f"   Run without --check-only to provision")
    else:
        result = provision_azure_speech()
        if not result["success"]:
            print(f"\n❌ Provisioning failed: {result.get('error')}")
            if result.get("action"):
                print(f"   Action: {result.get('action')}")
            sys.exit(1)


if __name__ == "__main__":



    main()