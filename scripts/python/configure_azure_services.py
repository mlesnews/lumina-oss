#!/usr/bin/env python3
"""
Configure Azure Services - Add credentials to Azure Key Vault
Helps configure all Azure services by adding secrets to Key Vault

Tags: #AZURE #KEY_VAULT #CONFIGURATION #SETUP @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("ConfigureAzureServices")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ConfigureAzureServices")

# Azure Key Vault
try:
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
    AZURE_KV_AVAILABLE = True
except ImportError:
    AZURE_KV_AVAILABLE = False
    logger.warning("Azure Key Vault SDK not available")


def load_config() -> Dict[str, Any]:
    try:
        """Load Azure services configuration"""
        config_file = project_root / "config" / "azure_services_config.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("azure_services_config", {})
        return {}


    except Exception as e:
        logger.error(f"Error in load_config: {e}", exc_info=True)
        raise
def get_key_vault_client(vault_url: str):
    """Get Azure Key Vault client"""
    if not AZURE_KV_AVAILABLE:
        return None

    try:
        # Try DefaultAzureCredential first (works with managed identity, VS Code, Azure CLI)
        credential = DefaultAzureCredential(

                            exclude_interactive_browser_credential=False,

                            exclude_shared_token_cache_credential=False

                        )
        client = SecretClient(vault_url=vault_url, credential=credential)
        # Test connection
        try:
            client.list_properties_of_secrets()
            return client
        except Exception:
            # Fallback to interactive browser credential
            logger.info("   Trying interactive browser authentication...")
            credential = InteractiveBrowserCredential()
            client = SecretClient(vault_url=vault_url, credential=credential)
            return client
    except Exception as e:
        logger.warning(f"   Could not connect to Key Vault: {e}")
        return None


def list_required_secrets(config: Dict[str, Any]) -> List[Dict[str, str]]:
    """List all required secrets for Azure services"""
    secrets = []

    # Service Bus
    if config.get("service_bus", {}).get("enabled"):
        secrets.append({
            "name": config.get("service_bus", {}).get("connection_string_secret", "azure-service-bus-connection-string"),
            "service": "Service Bus",
            "description": "Service Bus namespace connection string",
            "format": "Endpoint=sb://<namespace>.servicebus.windows.net/;SharedAccessKeyName=...;SharedAccessKey=..."
        })

    # Storage
    if config.get("storage", {}).get("enabled"):
        secrets.append({
            "name": "azure-storage-connection-string",
            "service": "Storage",
            "description": "Storage account connection string",
            "format": "DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...;EndpointSuffix=core.windows.net"
        })

    # Event Grid
    if config.get("event_grid", {}).get("enabled"):
        secrets.append({
            "name": "azure-event-grid-key",
            "service": "Event Grid",
            "description": "Event Grid topic access key",
            "format": "Access key from Event Grid topic"
        })
        secrets.append({
            "name": "azure-event-grid-endpoint",
            "service": "Event Grid",
            "description": "Event Grid topic endpoint URL",
            "format": "https://<topic-name>.<region>-1.eventgrid.azure.net/api/events"
        })

    # Cognitive Services
    cognitive = config.get("cognitive_services", {})
    if cognitive.get("enabled"):
        services = cognitive.get("services", {})
        if services.get("speech"):
            secrets.append({
                "name": services["speech"].get("key_secret", "cognitive-speech-key"),
                "service": "Cognitive Services - Speech",
                "description": "Speech service API key",
                "format": "API key from Azure Speech resource"
            })
        if services.get("text_analytics"):
            secrets.append({
                "name": services["text_analytics"].get("key_secret", "cognitive-text-analytics-key"),
                "service": "Cognitive Services - Text Analytics",
                "description": "Text Analytics API key",
                "format": "API key from Azure Text Analytics resource"
            })
        if services.get("vision"):
            secrets.append({
                "name": services["vision"].get("key_secret", "cognitive-vision-key"),
                "service": "Cognitive Services - Vision",
                "description": "Computer Vision API key",
                "format": "API key from Azure Computer Vision resource"
            })

    # Cosmos DB
    cosmos = config.get("cosmos_db", {})
    if cosmos.get("enabled"):
        secrets.append({
            "name": cosmos.get("endpoint_secret", "cosmos-db-endpoint"),
            "service": "Cosmos DB",
            "description": "Cosmos DB account endpoint URL",
            "format": "https://<account-name>.documents.azure.com:443/"
        })
        secrets.append({
            "name": cosmos.get("key_secret", "cosmos-db-key"),
            "service": "Cosmos DB",
            "description": "Cosmos DB account primary key",
            "format": "Primary key from Cosmos DB account"
        })

    # Application Insights
    monitor = config.get("monitor", {})
    if monitor.get("enabled"):
        app_insights = monitor.get("application_insights", {})
        if app_insights:
            secrets.append({
                "name": app_insights.get("instrumentation_key_secret", "app-insights-instrumentation-key"),
                "service": "Application Insights",
                "description": "Application Insights instrumentation key",
                "format": "Instrumentation key from Application Insights resource"
            })

    return secrets


def check_secrets_status(client: SecretClient, secrets: List[Dict[str, str]]) -> Dict[str, bool]:
    """Check which secrets exist in Key Vault"""
    status = {}
    if not client:
        return {s["name"]: False for s in secrets}

    try:
        existing_secrets = {s.name for s in client.list_properties_of_secrets()}
        for secret in secrets:
            status[secret["name"]] = secret["name"] in existing_secrets
    except Exception as e:
        logger.warning(f"   Could not list secrets: {e}")
        return {s["name"]: False for s in secrets}

    return status


def add_secret_to_vault(client: SecretClient, secret_name: str, secret_value: str) -> bool:
    """Add a secret to Key Vault"""
    if not client:
        return False

    try:
        client.set_secret(secret_name, secret_value)
        logger.info(f"   ✅ Secret '{secret_name}' added to Key Vault")
        return True
    except Exception as e:
        logger.error(f"   ❌ Failed to add secret '{secret_name}': {e}")
        return False


def main():
    """Main configuration interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Configure Azure Services")
    # Note: These are CLI argument definitions, not hardcoded secrets
    # The actual secret values are provided at runtime via command-line arguments
    # JARVIS-Roast: False positive - these are argument parser definitions, not secrets
    parser.add_argument("--interactive", action="store_true", 
                       help="Interactive mode to configure Azure services")
    parser.add_argument("--add-secret", nargs=2, metavar=("NAME", "VALUE"), 
                       help="Add a configuration value to Key Vault (secrets provided at runtime)")
    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("🔧 AZURE SERVICES CONFIGURATION")
    logger.info("=" * 80)
    logger.info("")

    # Load config
    config = load_config()
    key_vault_config = config.get("key_vault", {})
    vault_url = key_vault_config.get("vault_url", "https://jarvis-lumina.vault.azure.net/")
    vault_name = key_vault_config.get("vault_name", "jarvis-lumina")

    logger.info(f"📋 Key Vault: {vault_name}")
    logger.info(f"   URL: {vault_url}")
    logger.info("")

    # Get required secrets
    required_secrets = list_required_secrets(config)

    logger.info("📋 Required Secrets:")
    logger.info("")
    for i, secret in enumerate(required_secrets, 1):
        logger.info(f"   {i}. {secret['service']}")
        logger.info(f"      Name: {secret['name']}")
        logger.info(f"      Description: {secret['description']}")
        logger.info(f"      Format: {secret['format']}")
        logger.info("")

    # Try to connect to Key Vault
    logger.info("🔍 Connecting to Azure Key Vault...")
    client = get_key_vault_client(vault_url)

    if client:
        logger.info("   ✅ Connected to Key Vault")
        logger.info("")

        # Check which secrets exist
        logger.info("📊 Checking existing secrets...")
        status = check_secrets_status(client, required_secrets)

        logger.info("")
        logger.info("📋 Secret Status:")
        for secret in required_secrets:
            name = secret["name"]
            exists = status.get(name, False)
            status_icon = "✅" if exists else "❌"
            logger.info(f"   {status_icon} {name}: {'EXISTS' if exists else 'MISSING'}")

        logger.info("")
        logger.info("=" * 80)
        logger.info("📝 CONFIGURATION INSTRUCTIONS")
        logger.info("=" * 80)
        logger.info("")
        logger.info("To add missing secrets:")
        logger.info("")
        logger.info("Option 1: Azure Portal")
        logger.info(f"   1. Go to: https://portal.azure.com")
        logger.info(f"   2. Navigate to Key Vault: {vault_name}")
        logger.info("   3. Go to 'Secrets' section")
        logger.info("   4. Click 'Generate/Import' for each missing secret")
        logger.info("")
        logger.info("Option 2: Azure CLI")
        logger.info("   az keyvault secret set --vault-name jarvis-lumina --name <secret-name> --value <secret-value>")
        logger.info("")
        logger.info("Option 3: Python Script (interactive)")
        logger.info("   Run this script with --interactive flag to add secrets interactively")
        logger.info("")

        missing = [s for s in required_secrets if not status.get(s["name"], False)]
        if missing:
            logger.info(f"⚠️  {len(missing)} secret(s) need to be added:")
            for secret in missing:
                logger.info(f"   - {secret['name']} ({secret['service']})")
        else:
            logger.info("✅ All required secrets are configured!")

        # Interactive mode
        if args.interactive and missing:
            logger.info("")
            logger.info("=" * 80)
            logger.info("📝 INTERACTIVE MODE: Add Missing Secrets")
            logger.info("=" * 80)
            logger.info("")

            for secret in missing:
                logger.info(f"Adding: {secret['name']} ({secret['service']})")
                logger.info(f"Description: {secret['description']}")
                logger.info(f"Format: {secret['format']}")
                value = input(f"Enter value for '{secret['name']}' (or press Enter to skip): ").strip()

                if value:
                    if add_secret_to_vault(client, secret['name'], value):
                        logger.info(f"   ✅ Secret '{secret['name']}' added successfully")
                    else:
                        logger.warning(f"   ⚠️  Failed to add secret '{secret['name']}'")
                else:
                    logger.info(f"   ⏭️  Skipped '{secret['name']}'")
                logger.info("")

        # Add single secret via command line
        if args.add_secret:
            secret_name, secret_value = args.add_secret
            if add_secret_to_vault(client, secret_name, secret_value):
                logger.info(f"✅ Secret '{secret_name}' added successfully")
            else:
                logger.error(f"❌ Failed to add secret '{secret_name}'")

    else:
        logger.warning("   ⚠️  Could not connect to Key Vault")
        logger.info("")
        logger.info("📝 Manual Configuration:")
        logger.info("")
        logger.info("1. Ensure you're logged into Azure:")
        logger.info("   az login")
        logger.info("")
        logger.info("2. Or use Azure Portal to add secrets:")
        logger.info(f"   https://portal.azure.com -> Key Vaults -> {vault_name} -> Secrets")
        logger.info("")
        logger.info("3. Add the following secrets:")
        for secret in required_secrets:
            logger.info(f"   - {secret['name']}: {secret['description']}")

    logger.info("")
    logger.info("=" * 80)
    logger.info("✅ CONFIGURATION CHECK COMPLETE")
    logger.info("=" * 80)
    logger.info("")


if __name__ == "__main__":


    main()