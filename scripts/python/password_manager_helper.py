#!/usr/bin/env python3
"""
Password Manager Helper - Unified Access to Triad Password Managers

Provides unified access to:
- Azure Key Vault (@triad primary)
- ProtonPass (personal/CLI)
- Dashlane (backup/human-accessible)

Tags: #SECURITY #PASSWORD_MANAGER #TRIAD @JARVIS
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
import logging
logger = logging.getLogger("password_manager_helper")


# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from unified_secret_manager import UnifiedSecretManager, SecretCategory
except ImportError:
    UnifiedSecretManager = None
    SecretCategory = None

try:
    from get_vault_secret import get_secret as get_azure_secret
except ImportError:
    get_azure_secret = None


def get_credential(
    secret_name: str,
    source: str = "auto",
    vault_url: str = "https://jarvis-lumina.vault.azure.net/"
) -> Optional[str]:
    """
    Get credential from password managers with fallback

    Args:
        secret_name: Name of the secret/credential
        source: Preferred source ("azure", "protonpass", "dashlane", "auto")
        vault_url: Azure Key Vault URL

    Returns:
        Credential value or None if not found
    """
    # Try unified secret manager first
    if UnifiedSecretManager:
        try:
            manager = UnifiedSecretManager(azure_vault_url=vault_url)

            # Determine category based on source preference
            if source == "azure" or source == "auto":
                category = SecretCategory.ENTERPRISE if SecretCategory else None
            elif source == "protonpass":
                category = SecretCategory.PERSONAL if SecretCategory else None
            else:
                category = None

            secret = manager.get_secret(secret_name, category=category)
            if secret:
                return secret
        except Exception as e:
            print(f"Warning: UnifiedSecretManager failed: {e}", file=sys.stderr)

    # Fallback to direct Azure Key Vault
    if get_azure_secret and (source == "azure" or source == "auto"):
        try:
            secret = get_azure_secret(secret_name, vault_url)
            if secret:
                return secret
        except Exception as e:
            print(f"Warning: Direct Azure access failed: {e}", file=sys.stderr)

    return None


def get_huggingface_credentials() -> Dict[str, Optional[str]]:
    """
    Get HuggingFace credentials from password managers

    Returns:
        Dict with 'token', 'username', 'password' keys
    """
    credentials = {
        'token': None,
        'username': None,
        'password': None
    }

    # Try to get HuggingFace token
    token = get_credential("huggingface-token", source="auto")
    if token:
        credentials['token'] = token

    # Try to get HuggingFace username
    username = get_credential("huggingface-username", source="auto")
    if username:
        credentials['username'] = username

    # Try to get HuggingFace password
    password = get_credential("huggingface-password", source="auto")
    if password:
        credentials['password'] = password

    return credentials


def get_account_credentials(service_name: str) -> Dict[str, Optional[str]]:
    """
    Get account credentials for a service from password managers

    Args:
        service_name: Name of the service (e.g., "huggingface", "ollama", "github")

    Returns:
        Dict with 'username', 'password', 'token' keys
    """
    credentials = {
        'username': None,
        'password': None,
        'token': None
    }

    # Try service-specific secret names
    username = get_credential(f"{service_name}-username", source="auto")
    password = get_credential(f"{service_name}-password", source="auto")
    token = get_credential(f"{service_name}-token", source="auto")

    if username:
        credentials['username'] = username
    if password:
        credentials['password'] = password
    if token:
        credentials['token'] = token

    return credentials


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Get credentials from password managers")
        parser.add_argument("--secret", type=str, help="Secret name to retrieve")
        parser.add_argument("--service", type=str, help="Service name for account credentials")
        parser.add_argument("--source", type=str, default="auto",
                           choices=["auto", "azure", "protonpass", "dashlane"],
                           help="Preferred source")

        args = parser.parse_args()

        if args.secret:
            credential = get_credential(args.secret, source=args.source)
            if credential:
                print(credential)
                return 0
            else:
                print(f"❌ Secret '{args.secret}' not found", file=sys.stderr)
                return 1

        elif args.service:
            credentials = get_account_credentials(args.service)
            import json
            print(json.dumps(credentials, indent=2))
            return 0

        else:
            parser.print_help()
            return 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":

    sys.exit(main())