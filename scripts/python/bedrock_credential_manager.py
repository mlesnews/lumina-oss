#!/usr/bin/env python3
"""
Bedrock Credential Manager - ProtonPass + Azure Vault Integration

Retrieves AWS Bedrock credentials from ProtonPass CLI and Azure Key Vault.
All secrets MUST be stored in Azure Key Vault first, then synced to ProtonPass.

CRITICAL: +++++ MEMORY PRIORITY - Always use ProtonPass CLI and Azure Vault for ALL secrets

Tags: #BEDROCK #AWS #CREDENTIALS #PROTONPASS #AZURE_VAULT #SECRETS #+++++
@JARVIS @MARVIN @HK-47 @itsec
"""

import sys
import os
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from unified_secret_manager import UnifiedSecretManager, SecretCategory
    UNIFIED_SECRET_MANAGER_AVAILABLE = True
except ImportError:
    UNIFIED_SECRET_MANAGER_AVAILABLE = False
    UnifiedSecretManager = None
    SecretCategory = None

try:
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential
    AZURE_VAULT_AVAILABLE = True
except ImportError:
    AZURE_VAULT_AVAILABLE = False

try:
    from protonpass_manager import ProtonPassManager
    PROTONPASS_AVAILABLE = True
except ImportError:
    PROTONPASS_AVAILABLE = False
    ProtonPassManager = None

logger = get_logger("BedrockCredentialManager")


class BedrockCredentialManager:
    """
    Bedrock Credential Manager

    CRITICAL: +++++ MEMORY PRIORITY
    - ALWAYS uses ProtonPass CLI and Azure Key Vault for ALL secrets
    - NEVER stores credentials in plain text files
    - All AWS credentials MUST be in Azure Key Vault first, then synced to ProtonPass
    """

    # Secret names in Azure Key Vault / ProtonPass
    SECRET_NAMES = {
        "access_key_id": "aws-bedrock-access-key-id",
        "secret_access_key": "aws-bedrock-secret-access-key",
        "session_token": "aws-bedrock-session-token",  # Optional, for temporary credentials
        "region": "aws-bedrock-region"
    }

    def __init__(
        self,
        vault_url: str = "https://jarvis-lumina.vault.azure.net/",
        project_root: Optional[Path] = None
    ):
        """
        Initialize Bedrock Credential Manager

        Args:
            vault_url: Azure Key Vault URL
            project_root: Project root directory
        """
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.vault_url = vault_url

        # Initialize Unified Secret Manager (ProtonPass + Azure Vault)
        self.secret_manager = None
        if UNIFIED_SECRET_MANAGER_AVAILABLE:
            try:
                self.secret_manager = UnifiedSecretManager(
                    azure_vault_url=vault_url,
                    project_root=self.project_root
                )
                logger.info("✅ Unified Secret Manager initialized (ProtonPass + Azure Vault)")
            except Exception as e:
                logger.warning(f"⚠️  Unified Secret Manager not available: {e}")

        # Initialize Azure Vault client directly (fallback)
        self.azure_vault_client = None
        if AZURE_VAULT_AVAILABLE and not self.secret_manager:
            try:
                credential = DefaultAzureCredential(

                                    exclude_interactive_browser_credential=False,

                                    exclude_shared_token_cache_credential=False

                                )
                self.azure_vault_client = SecretClient(
                    vault_url=vault_url,
                    credential=credential
                )
                logger.info("✅ Azure Key Vault client initialized (direct)")
            except Exception as e:
                logger.warning(f"⚠️  Azure Key Vault client not available: {e}")

        # Initialize ProtonPass manager (fallback)
        self.proton_pass = None
        if PROTONPASS_AVAILABLE and not self.secret_manager:
            try:
                self.proton_pass = ProtonPassManager()
                if self.proton_pass.cli_available:
                    logger.info("✅ ProtonPass manager initialized (direct)")
                else:
                    self.proton_pass = None
            except Exception as e:
                logger.warning(f"⚠️  ProtonPass manager not available: {e}")

    def get_credentials(self, use_environment: bool = False) -> Optional[Dict[str, str]]:
        """
        Get AWS Bedrock credentials from ProtonPass + Azure Vault

        CRITICAL: +++++ MEMORY PRIORITY
        - ALWAYS retrieves from ProtonPass CLI and Azure Key Vault
        - NEVER uses plain text files or hardcoded credentials

        Args:
            use_environment: If True, also check environment variables as fallback

        Returns:
            Dict with access_key_id, secret_access_key, session_token (optional), region
            or None if credentials not found
        """
        logger.info("🔐 Retrieving AWS Bedrock credentials from ProtonPass + Azure Vault...")

        credentials = {}

        # Try Unified Secret Manager first (ProtonPass + Azure Vault)
        if self.secret_manager:
            try:
                for key, secret_name in self.SECRET_NAMES.items():
                    secret_value = self.secret_manager.get_secret(
                        secret_name=secret_name,
                        category=SecretCategory.API_KEY if key != "region" else SecretCategory.ENTERPRISE,
                        ai_system="JARVIS"
                    )
                    if secret_value:
                        credentials[key] = secret_value
                        logger.debug(f"   ✅ Retrieved {key} from Unified Secret Manager")
                    else:
                        logger.debug(f"   ⚠️  {key} not found in Unified Secret Manager")

                if len(credentials) >= 2:  # At least access_key_id and secret_access_key
                    logger.info("✅ Credentials retrieved from Unified Secret Manager")
                    return self._validate_credentials(credentials)

            except Exception as e:
                logger.warning(f"⚠️  Error retrieving from Unified Secret Manager: {e}")

        # Fallback: Try Azure Key Vault directly
        if self.azure_vault_client:
            try:
                for key, secret_name in self.SECRET_NAMES.items():
                    try:
                        secret = self.azure_vault_client.get_secret(secret_name)
                        if secret and secret.value:
                            credentials[key] = secret.value
                            logger.debug(f"   ✅ Retrieved {key} from Azure Key Vault")
                    except Exception as e:
                        logger.debug(f"   ⚠️  {key} not found in Azure Key Vault: {e}")

                if len(credentials) >= 2:
                    logger.info("✅ Credentials retrieved from Azure Key Vault")
                    return self._validate_credentials(credentials)

            except Exception as e:
                logger.warning(f"⚠️  Error retrieving from Azure Key Vault: {e}")

        # Fallback: Try ProtonPass directly
        if self.proton_pass and self.proton_pass.cli_available:
            try:
                for key, secret_name in self.SECRET_NAMES.items():
                    result = self.proton_pass.get_password(secret_name)
                    if result and result.get("password"):
                        credentials[key] = result["password"]
                        logger.debug(f"   ✅ Retrieved {key} from ProtonPass")

                if len(credentials) >= 2:
                    logger.info("✅ Credentials retrieved from ProtonPass")
                    return self._validate_credentials(credentials)

            except Exception as e:
                logger.warning(f"⚠️  Error retrieving from ProtonPass: {e}")

        # Final fallback: Environment variables (if allowed)
        if use_environment:
            logger.info("⚠️  Falling back to environment variables...")
            env_mapping = {
                "access_key_id": "AWS_ACCESS_KEY_ID",
                "secret_access_key": "AWS_SECRET_ACCESS_KEY",
                "session_token": "AWS_SESSION_TOKEN",
                "region": "AWS_REGION"
            }

            for key, env_var in env_mapping.items():
                value = os.getenv(env_var)
                if value:
                    credentials[key] = value
                    logger.debug(f"   ✅ Retrieved {key} from environment")

            if len(credentials) >= 2:
                logger.warning("⚠️  Using environment variables (not recommended - use ProtonPass/Azure Vault)")
                return self._validate_credentials(credentials)

        logger.error("❌ AWS Bedrock credentials not found in ProtonPass, Azure Vault, or environment")
        return None

    def _validate_credentials(self, credentials: Dict[str, str]) -> Optional[Dict[str, str]]:
        """Validate credentials structure"""
        required = ["access_key_id", "secret_access_key"]

        for key in required:
            if key not in credentials or not credentials[key]:
                logger.error(f"❌ Missing required credential: {key}")
                return None

        # Set defaults
        if "region" not in credentials or not credentials["region"]:
            credentials["region"] = "us-east-1"
            logger.info("   ℹ️  Using default region: us-east-1")

        # Remove session_token if empty
        if "session_token" in credentials and not credentials["session_token"]:
            del credentials["session_token"]

        return credentials

    def set_environment_variables(self, credentials: Optional[Dict[str, str]] = None) -> bool:
        """
        Set AWS credentials as environment variables (temporary, for current process)

        CRITICAL: +++++ MEMORY PRIORITY
        - This is for runtime use only
        - Credentials are NEVER stored in files
        - Always retrieved from ProtonPass + Azure Vault

        Args:
            credentials: Credentials dict (if None, retrieves from ProtonPass/Azure Vault)

        Returns:
            True if environment variables set successfully
        """
        if credentials is None:
            credentials = self.get_credentials()

        if not credentials:
            logger.error("❌ Cannot set environment variables - credentials not available")
            return False

        # Set environment variables
        os.environ["AWS_ACCESS_KEY_ID"] = credentials["access_key_id"]
        os.environ["AWS_SECRET_ACCESS_KEY"] = credentials["secret_access_key"]

        if "session_token" in credentials:
            os.environ["AWS_SESSION_TOKEN"] = credentials["session_token"]

        if "region" in credentials:
            os.environ["AWS_REGION"] = credentials["region"]
            os.environ["AWS_DEFAULT_REGION"] = credentials["region"]

        logger.info("✅ AWS environment variables set (temporary, for current process)")
        logger.info(f"   Region: {credentials.get('region', 'us-east-1')}")
        logger.info("   Access Key ID: " + credentials["access_key_id"][:8] + "***")

        return True

    def store_credentials(
        self,
        access_key_id: str,
        secret_access_key: str,
        region: str = "us-east-1",
        session_token: Optional[str] = None
    ) -> bool:
        """
        Store AWS Bedrock credentials in Azure Key Vault and ProtonPass

        CRITICAL: +++++ MEMORY PRIORITY
        - ALWAYS stores in Azure Key Vault first
        - Then syncs to ProtonPass
        - NEVER stores in plain text files

        Args:
            access_key_id: AWS Access Key ID
            secret_access_key: AWS Secret Access Key
            region: AWS Region (default: us-east-1)
            session_token: Optional session token (for temporary credentials)

        Returns:
            True if stored successfully
        """
        logger.info("🔐 Storing AWS Bedrock credentials in Azure Key Vault + ProtonPass...")

        if not self.secret_manager:
            logger.error("❌ Unified Secret Manager not available")
            return False

        try:
            # Store in Azure Key Vault first (policy requirement)
            stored = True

            stored &= self.secret_manager.store_secret(
                secret_name=self.SECRET_NAMES["access_key_id"],
                secret_value=access_key_id,
                category=SecretCategory.API_KEY,
                description="AWS Bedrock Access Key ID"
            )

            stored &= self.secret_manager.store_secret(
                secret_name=self.SECRET_NAMES["secret_access_key"],
                secret_value=secret_access_key,
                category=SecretCategory.API_KEY,
                description="AWS Bedrock Secret Access Key"
            )

            stored &= self.secret_manager.store_secret(
                secret_name=self.SECRET_NAMES["region"],
                secret_value=region,
                category=SecretCategory.ENTERPRISE,
                description="AWS Bedrock Region"
            )

            if session_token:
                stored &= self.secret_manager.store_secret(
                    secret_name=self.SECRET_NAMES["session_token"],
                    secret_value=session_token,
                    category=SecretCategory.TOKEN,
                    description="AWS Bedrock Session Token (temporary)"
                )

            if stored:
                logger.info("✅ AWS Bedrock credentials stored in Azure Key Vault + ProtonPass")
            else:
                logger.error("❌ Failed to store some credentials")

            return stored

        except Exception as e:
            logger.error(f"❌ Error storing credentials: {e}")
            return False

    def test_connection(self) -> bool:
        """
        Test Bedrock connection using retrieved credentials

        Returns:
            True if connection successful
        """
        logger.info("🧪 Testing Bedrock connection...")

        credentials = self.get_credentials()
        if not credentials:
            logger.error("❌ Cannot test connection - credentials not available")
            return False

        try:
            import boto3
            from botocore.exceptions import ClientError, NoCredentialsError

            # Set credentials
            self.set_environment_variables(credentials)

            # Test Bedrock connection
            bedrock = boto3.client(
                'bedrock-runtime',
                region_name=credentials.get("region", "us-east-1"),
                aws_access_key_id=credentials["access_key_id"],
                aws_secret_access_key=credentials["secret_access_key"]
            )

            # Try to list foundation models (lightweight test)
            try:
                bedrock_client = boto3.client(
                    'bedrock',
                    region_name=credentials.get("region", "us-east-1"),
                    aws_access_key_id=credentials["access_key_id"],
                    aws_secret_access_key=credentials["secret_access_key"]
                )
                models = bedrock_client.list_foundation_models()
                logger.info(f"✅ Bedrock connection successful - Found {len(models.get('modelSummaries', []))} models")
                return True
            except ClientError as e:
                logger.error(f"❌ Bedrock connection failed: {e}")
                return False
            except NoCredentialsError:
                logger.error("❌ AWS credentials invalid")
                return False

        except ImportError:
            logger.error("❌ boto3 not installed - install with: pip install boto3")
            return False
        except Exception as e:
            logger.error(f"❌ Error testing connection: {e}")
            return False


def main():
    """CLI interface for Bedrock Credential Manager"""
    import argparse

    parser = argparse.ArgumentParser(description="Bedrock Credential Manager (ProtonPass + Azure Vault)")
    parser.add_argument("--get", action="store_true", help="Get credentials from ProtonPass/Azure Vault")
    parser.add_argument("--set-env", action="store_true", help="Set AWS environment variables")
    parser.add_argument("--test", action="store_true", help="Test Bedrock connection")
    parser.add_argument("--store", action="store_true", help="Store credentials (interactive)")
    parser.add_argument("--vault-url", help="Azure Key Vault URL")

    args = parser.parse_args()

    vault_url = args.vault_url or "https://jarvis-lumina.vault.azure.net/"
    manager = BedrockCredentialManager(vault_url=vault_url)

    if args.get:
        credentials = manager.get_credentials()
        if credentials:
            print("\n✅ AWS Bedrock Credentials Retrieved:")
            print(f"   Access Key ID: {credentials['access_key_id'][:8]}***")
            print(f"   Secret Access Key: {'*' * 20}")
            print(f"   Region: {credentials.get('region', 'us-east-1')}")
            if 'session_token' in credentials:
                print(f"   Session Token: {'*' * 20}")
        else:
            print("❌ Credentials not found")

    elif args.set_env:
        if manager.set_environment_variables():
            print("✅ AWS environment variables set")
        else:
            print("❌ Failed to set environment variables")

    elif args.test:
        if manager.test_connection():
            print("✅ Bedrock connection successful")
        else:
            print("❌ Bedrock connection failed")

    elif args.store:
        print("\n🔐 Store AWS Bedrock Credentials")
        print("CRITICAL: +++++ MEMORY PRIORITY - Storing in Azure Key Vault + ProtonPass")
        print()

        access_key_id = input("AWS Access Key ID: ").strip()
        secret_access_key = input("AWS Secret Access Key: ").strip()
        region = input("AWS Region [us-east-1]: ").strip() or "us-east-1"
        session_token = input("Session Token (optional, press Enter to skip): ").strip() or None

        if manager.store_credentials(access_key_id, secret_access_key, region, session_token):
            print("✅ Credentials stored successfully")
        else:
            print("❌ Failed to store credentials")

    else:
        parser.print_help()


if __name__ == "__main__":


    main()