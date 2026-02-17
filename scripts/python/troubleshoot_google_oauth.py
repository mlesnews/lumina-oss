"""
Troubleshoot Google OAuth Consent Screen Issues

This script helps diagnose Google OAuth authentication problems.
"""
import sys
from pathlib import Path
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GoogleOAuthTroubleshooter")

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

def check_oauth_credentials():
    """Check if OAuth credentials files exist."""
    logger.info("\n" + "="*80)
    logger.info("GOOGLE OAUTH TROUBLESHOOTING")
    logger.info("="*80)

    credentials_file = project_root / "config" / "google_drive_credentials.json"
    token_file = project_root / "config" / "google_drive_token.pickle"

    logger.info(f"\n1. Checking credential files:")
    logger.info(f"   Credentials file: {credentials_file}")
    logger.info(f"   Exists: {credentials_file.exists()}")

    if credentials_file.exists():
        try:
            with open(credentials_file, 'r') as f:
                creds_data = json.load(f)
                logger.info(f"   ✅ Credentials file is valid JSON")
                logger.info(f"   Client ID: {creds_data.get('installed', {}).get('client_id', 'N/A')[:30]}...")
                logger.info(f"   Auth URI: {creds_data.get('installed', {}).get('auth_uri', 'N/A')[:50]}...")
        except Exception as e:
            logger.error(f"   ❌ Error reading credentials: {e}")

    logger.info(f"\n2. Checking token file:")
    logger.info(f"   Token file: {token_file}")
    logger.info(f"   Exists: {token_file.exists()}")

    return credentials_file.exists(), token_file.exists()

def check_google_api_libraries():
    """Check if required Google API libraries are installed."""
    logger.info(f"\n3. Checking Google API libraries:")

    libraries = {
        'google.auth': 'google-auth',
        'google_auth_oauthlib.flow': 'google-auth-oauthlib',
        'google.auth.transport.requests': 'google-auth',
        'googleapiclient.discovery': 'google-api-python-client'
    }

    all_available = True
    for module, package in libraries.items():
        try:
            __import__(module)
            logger.info(f"   ✅ {package} ({module})")
        except ImportError:
            logger.error(f"   ❌ {package} ({module}) - NOT INSTALLED")
            logger.info(f"      Install with: pip install {package}")
            all_available = False

    return all_available

def diagnose_oauth_issues():
    """Provide diagnosis and solutions for common OAuth issues."""
    logger.info(f"\n4. Common OAuth Issues & Solutions:")
    logger.info(f"\n   ISSUE: OAuth consent screen not loading/working")
    logger.info(f"   Possible causes:")
    logger.info(f"   a) Invalid or expired OAuth credentials")
    logger.info(f"   b) OAuth consent screen not configured in Google Cloud Console")
    logger.info(f"   c) Required scopes not approved")
    logger.info(f"   d) App not published (still in testing mode)")
    logger.info(f"   e) Redirect URI mismatch")
    logger.info(f"   f) Browser/cookie issues")

    logger.info(f"\n   SOLUTIONS:")
    logger.info(f"   1. Verify OAuth credentials in Google Cloud Console:")
    logger.info(f"      - Go to: https://console.cloud.google.com/apis/credentials")
    logger.info(f"      - Check OAuth 2.0 Client IDs")
    logger.info(f"      - Verify client_id matches your credentials file")
    logger.info(f"      - Check Authorized redirect URIs")

    logger.info(f"\n   2. Check OAuth consent screen configuration:")
    logger.info(f"      - Go to: https://console.cloud.google.com/apis/credentials/consent")
    logger.info(f"      - Verify app information is complete")
    logger.info(f"      - Check scopes are added")
    logger.info(f"      - If in testing mode, add test users")

    logger.info(f"\n   3. Verify redirect URI:")
    logger.info(f"      - For desktop apps: http://localhost:PORT or urn:ietf:wg:oauth:2.0:oob")
    logger.info(f"      - Check Authorized redirect URIs in OAuth client settings")

    logger.info(f"\n   4. Clear browser cache/cookies for Google accounts")

    logger.info(f"\n   5. Try incognito/private browsing mode")

    logger.info(f"\n   6. Re-authenticate:")
    logger.info(f"      - Delete token file: config/google_drive_token.pickle")
    logger.info(f"      - Run authentication script again")

    logger.info(f"\n   7. Check if app needs to be published:")
    logger.info(f"      - Testing mode only works for test users")
    logger.info(f"      - Publishing allows any Google account to use")

def check_azure_key_vault_credentials():
    """Check Azure Key Vault for Google credentials."""
    logger.info(f"\n5. Checking Azure Key Vault for Google credentials:")

    try:
        from scripts.python.azure_service_bus_integration import AzureKeyVaultClient
        import os

        vault_url = os.getenv("AZURE_KEY_VAULT_URL", "https://jarvis-lumina.vault.azure.net/")
        vault_client = AzureKeyVaultClient(vault_url=vault_url)

        secret_names = [
            "google-drive-credentials",
            "google-oauth2-credentials",
            "gmail-oauth2-credentials",
            "google-api-credentials"
        ]

        found = False
        for name in secret_names:
            try:
                value = vault_client.get_secret(name)
                logger.info(f"   ✅ Found: {name}")
                found = True
                # Don't print full value, just indicate it exists
                if value.strip().startswith('{'):
                    logger.info(f"      Format: JSON credentials")
                else:
                    logger.info(f"      Format: Text/Other")
            except Exception as e:
                if "SecretNotFound" not in str(e):
                    logger.warning(f"   ⚠️  Error checking {name}: {e}")

        if not found:
            logger.info(f"   ⚠️  No Google OAuth credentials found in Key Vault")
            logger.info(f"      Consider storing credentials there for secure access")

    except ImportError:
        logger.warning(f"   ⚠️  Azure Key Vault integration not available")
    except Exception as e:
        logger.warning(f"   ⚠️  Error accessing Key Vault: {e}")

def main():
    """Main troubleshooting function."""
    creds_exist, token_exist = check_oauth_credentials()
    libs_available = check_google_api_libraries()
    check_azure_key_vault_credentials()
    diagnose_oauth_issues()

    logger.info(f"\n" + "="*80)
    logger.info("SUMMARY")
    logger.info("="*80)

    if not creds_exist:
        logger.warning(f"\n⚠️  OAuth credentials file NOT FOUND")
        logger.info(f"   Action: Download credentials from Google Cloud Console")
        logger.info(f"   Save as: config/google_drive_credentials.json")

    if not token_exist:
        logger.info(f"\nℹ️  Token file NOT FOUND (this is normal for first-time auth)")
        logger.info(f"   Action: Run authentication flow to create token")

    if not libs_available:
        logger.warning(f"\n⚠️  Required Google API libraries NOT INSTALLED")
        logger.info(f"   Action: pip install google-auth google-auth-oauthlib google-api-python-client")

    logger.info(f"\n📋 Next steps:")
    logger.info(f"   1. Verify credentials file exists and is valid")
    logger.info(f"   2. Check Google Cloud Console OAuth settings")
    logger.info(f"   3. Try authentication in a different browser/incognito")
    logger.info(f"   4. Check if app is in testing mode and add yourself as test user")
    logger.info(f"   5. Clear browser cache and try again")

if __name__ == "__main__":


    main()