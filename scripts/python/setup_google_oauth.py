"""
Google OAuth Setup and Deployment Script

This script helps set up Google OAuth credentials and validates the configuration.
Part of LUMINA deployment implementation.
"""
import sys
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("GoogleOAuthSetup")

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.azure_service_bus_integration import AzureKeyVaultClient
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    logger.warning("Azure Key Vault integration not available")

class GoogleOAuthSetup:
    """Manages Google OAuth credential setup and validation."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.credentials_file = self.config_dir / "google_drive_credentials.json"
        self.token_file = self.config_dir / "google_drive_token.pickle"

        self.vault_client = None
        if AZURE_AVAILABLE:
            try:
                vault_url = os.getenv("AZURE_KEY_VAULT_URL", "https://jarvis-lumina.vault.azure.net/")
                self.vault_client = AzureKeyVaultClient(vault_url=vault_url)
                logger.info("✅ Azure Key Vault client initialized")
            except Exception as e:
                logger.warning(f"Azure Key Vault not available: {e}")

    def check_credentials_file(self) -> bool:
        """Check if credentials file exists and is valid."""
        if not self.credentials_file.exists():
            logger.warning(f"❌ Credentials file not found: {self.credentials_file}")
            return False

        try:
            with open(self.credentials_file, 'r') as f:
                creds = json.load(f)

            # Validate structure
            if 'installed' in creds or 'web' in creds:
                logger.info(f"✅ Credentials file exists and appears valid")
                logger.info(f"   File: {self.credentials_file}")
                if 'installed' in creds:
                    client_id = creds['installed'].get('client_id', 'N/A')
                    logger.info(f"   Client ID: {client_id[:30]}...")
                return True
            else:
                logger.error(f"❌ Invalid credentials file structure")
                return False
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in credentials file: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error reading credentials file: {e}")
            return False

    def check_token_file(self) -> bool:
        try:
            """Check if token file exists."""
            if self.token_file.exists():
                logger.info(f"✅ Token file exists: {self.token_file}")
                return True
            else:
                logger.info(f"ℹ️  Token file not found (will be created on first auth): {self.token_file}")
                return False

        except Exception as e:
            self.logger.error(f"Error in check_token_file: {e}", exc_info=True)
            raise
    def check_vault_credentials(self) -> Optional[str]:
        """Check Azure Key Vault for credentials."""
        if not self.vault_client:
            return None

        secret_names = [
            "google-api-credentials",
            "google-drive-credentials",
            "google-oauth2-credentials",
            "gmail-oauth2-credentials"
        ]

        for name in secret_names:
            try:
                value = self.vault_client.get_secret(name)
                logger.info(f"✅ Found credentials in Azure Key Vault: {name}")
                return value
            except Exception:
                continue

        logger.info("ℹ️  No credentials found in Azure Key Vault")
        return None

    def download_from_vault(self) -> bool:
        """Download credentials from Azure Key Vault to local file."""
        creds_json = self.check_vault_credentials()
        if not creds_json:
            return False

        try:
            # Validate JSON
            json.loads(creds_json)

            # Write to local file
            with open(self.credentials_file, 'w') as f:
                f.write(creds_json)

            logger.info(f"✅ Downloaded credentials from Azure Key Vault to: {self.credentials_file}")
            return True
        except json.JSONDecodeError:
            logger.error("❌ Credentials from vault are not valid JSON")
            return False
        except Exception as e:
            logger.error(f"❌ Error downloading credentials: {e}")
            return False

    def validate_credentials(self) -> Dict[str, Any]:
        try:
            """Validate OAuth credentials setup."""
            logger.info("\n" + "="*80)
            logger.info("GOOGLE OAUTH CREDENTIALS VALIDATION")
            logger.info("="*80)

            results = {
                "credentials_file_exists": False,
                "credentials_file_valid": False,
                "token_file_exists": False,
                "vault_credentials_available": False,
                "setup_complete": False
            }

            # Check local credentials file
            if self.credentials_file.exists():
                results["credentials_file_exists"] = True
                results["credentials_file_valid"] = self.check_credentials_file()
            else:
                # Try to download from vault
                if self.download_from_vault():
                    results["credentials_file_exists"] = True
                    results["credentials_file_valid"] = self.check_credentials_file()

            # Check vault
            if self.check_vault_credentials():
                results["vault_credentials_available"] = True

            # Check token
            results["token_file_exists"] = self.check_token_file()

            # Overall status
            results["setup_complete"] = results["credentials_file_valid"]

            return results

        except Exception as e:
            self.logger.error(f"Error in validate_credentials: {e}", exc_info=True)
            raise
    def print_setup_instructions(self):
        """Print instructions for setting up credentials."""
        logger.info("\n" + "="*80)
        logger.info("GOOGLE OAUTH CREDENTIALS SETUP INSTRUCTIONS")
        logger.info("="*80)
        logger.info("\n📋 To set up Google OAuth credentials:\n")
        logger.info("1. Go to Google Cloud Console:")
        logger.info("   https://console.cloud.google.com/apis/credentials")
        logger.info("\n2. Create OAuth 2.0 Client ID:")
        logger.info("   - Click '+ CREATE CREDENTIALS' → 'OAuth client ID'")
        logger.info("   - Application type: Desktop app")
        logger.info("   - Name: 'LUMINA Google Integration' (or your choice)")
        logger.info("   - Click 'CREATE'")
        logger.info("\n3. Download credentials:")
        logger.info("   - Click download icon (⬇️) next to your OAuth client")
        logger.info(f"   - Save as: {self.credentials_file}")
        logger.info("\n4. Configure OAuth Consent Screen:")
        logger.info("   - Go to: https://console.cloud.google.com/apis/credentials/consent")
        logger.info("   - If in Testing mode, add yourself as a test user")
        logger.info("   - Or publish the app for production use")
        logger.info("\n5. Run authentication:")
        logger.info("   python scripts/python/authenticate_google_oauth.py")
        logger.info("\n" + "="*80)

def main():
    """Main setup and validation function."""
    import argparse
    parser = argparse.ArgumentParser(description="Setup and validate Google OAuth credentials")
    parser.add_argument("--project-root", type=Path, default=project_root)
    parser.add_argument("--download-from-vault", action="store_true", help="Download credentials from Azure Key Vault")
    parser.add_argument("--instructions", action="store_true", help="Print setup instructions")

    args = parser.parse_args()

    setup = GoogleOAuthSetup(args.project_root)

    if args.instructions:
        setup.print_setup_instructions()
        return

    if args.download_from_vault:
        if setup.download_from_vault():
            logger.info("✅ Credentials downloaded from Azure Key Vault")
        else:
            logger.error("❌ Failed to download credentials from Azure Key Vault")
        return

    # Validate setup
    results = setup.validate_credentials()

    logger.info("\n" + "="*80)
    logger.info("VALIDATION RESULTS")
    logger.info("="*80)
    logger.info(f"Credentials file exists: {'✅' if results['credentials_file_exists'] else '❌'}")
    logger.info(f"Credentials file valid: {'✅' if results['credentials_file_valid'] else '❌'}")
    logger.info(f"Token file exists: {'✅' if results['token_file_exists'] else 'ℹ️ '}")
    logger.info(f"Vault credentials available: {'✅' if results['vault_credentials_available'] else 'ℹ️ '}")
    logger.info(f"\nSetup complete: {'✅ YES' if results['setup_complete'] else '❌ NO'}")

    if not results['setup_complete']:
        logger.info("\n⚠️  Credentials not set up. Run with --instructions for setup guide")
        setup.print_setup_instructions()
    else:
        logger.info("\n✅ Credentials are set up. Ready for authentication.")
        logger.info("   Next step: Run authentication script")

if __name__ == "__main__":


    main()