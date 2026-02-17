"""
Google OAuth Authentication Script

Executes the OAuth authentication flow and validates success.
Part of LUMINA deployment implementation.
"""
import sys
import pickle
from pathlib import Path
from typing import Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("GoogleOAuthAuth")

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

# Google API imports
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    logger.error("Google API libraries not installed")
    logger.info("Install with: pip install google-auth google-auth-oauthlib google-api-python-client")

class GoogleOAuthAuthenticator:
    """Handles Google OAuth authentication flow."""

    # Scopes for Google APIs
    SCOPES = {
        'drive': ['https://www.googleapis.com/auth/drive.readonly'],
        'gmail': ['https://www.googleapis.com/auth/gmail.readonly'],
        'both': [
            'https://www.googleapis.com/auth/drive.readonly',
            'https://www.googleapis.com/auth/gmail.readonly'
        ]
    }

    def __init__(self, project_root: Path, scopes: list = None):
        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.credentials_file = self.config_dir / "google_drive_credentials.json"
        self.token_file = self.config_dir / "google_drive_token.pickle"

        if scopes is None:
            scopes = self.SCOPES['both']  # Default to both

        self.scopes = scopes
        self.creds = None
        self.service = None

    def load_existing_token(self) -> Optional[Credentials]:
        """Load existing token if available."""
        if not self.token_file.exists():
            return None

        try:
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)

            if creds and creds.valid:
                logger.info("✅ Loaded existing valid token")
                return creds
            elif creds and creds.expired and creds.refresh_token:
                logger.info("🔄 Token expired, refreshing...")
                try:
                    creds.refresh(Request())
                    logger.info("✅ Token refreshed successfully")
                    return creds
                except Exception as e:
                    logger.warning(f"⚠️  Failed to refresh token: {e}")
                    return None
            else:
                logger.info("ℹ️  Existing token invalid, need re-authentication")
                return None
        except Exception as e:
            logger.warning(f"⚠️  Error loading token: {e}")
            return None

    def authenticate(self, force: bool = False) -> bool:
        """Execute OAuth authentication flow."""
        if not GOOGLE_API_AVAILABLE:
            logger.error("❌ Google API libraries not available")
            return False

        # Check credentials file
        if not self.credentials_file.exists():
            logger.error(f"❌ Credentials file not found: {self.credentials_file}")
            logger.info("Run: python scripts/python/setup_google_oauth.py --instructions")
            return False

        # Try to load existing token
        if not force:
            self.creds = self.load_existing_token()
            if self.creds:
                logger.info("✅ Using existing authentication")
                return True

        # Need new authentication
        logger.info("\n" + "="*80)
        logger.info("GOOGLE OAUTH AUTHENTICATION")
        logger.info("="*80)
        logger.info(f"Credentials file: {self.credentials_file}")
        logger.info(f"Scopes: {', '.join(self.scopes)}")
        logger.info("\n📋 A browser window will open for authentication...")
        logger.info("   Please sign in with your Google account and grant permissions.")
        logger.info("="*80 + "\n")

        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.credentials_file), self.scopes
            )
            # run_local_server opens system default browser automatically
            # If Neo browser has network issues, change system default browser temporarily
            self.creds = flow.run_local_server(port=0, open_browser=True)

            # Save credentials for future use
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.creds, token)

            logger.info("\n✅ Authentication successful!")
            logger.info(f"   Token saved to: {self.token_file}")
            return True

        except Exception as e:
            logger.error(f"\n❌ Authentication failed: {e}")
            logger.info("\n💡 Troubleshooting:")
            logger.info("   1. Check if credentials file is valid")
            logger.info("   2. Verify OAuth consent screen is configured")
            logger.info("   3. Ensure you're added as a test user (if app is in testing mode)")
            logger.info("   4. Try clearing browser cache and retry")
            return False

    def build_service(self, service_name: str, version: str = 'v3') -> bool:
        """Build a Google API service."""
        if not self.creds:
            if not self.authenticate():
                return False

        try:
            self.service = build(service_name, version, credentials=self.creds)
            logger.info(f"✅ {service_name} API service built successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to build {service_name} service: {e}")
            return False

    def test_drive_access(self) -> bool:
        """Test Google Drive API access."""
        if not self.build_service('drive'):
            return False

        try:
            results = self.service.files().list(pageSize=1, fields="files(id, name)").execute()
            files = results.get('files', [])
            logger.info(f"✅ Google Drive API test successful (found {len(files)} file(s))")
            return True
        except Exception as e:
            logger.error(f"❌ Google Drive API test failed: {e}")
            return False

    def test_gmail_access(self) -> bool:
        """Test Gmail API access."""
        if not self.build_service('gmail', 'v1'):
            return False

        try:
            profile = self.service.users().getProfile(userId='me').execute()
            email = profile.get('emailAddress', 'Unknown')
            logger.info(f"✅ Gmail API test successful (email: {email})")
            return True
        except Exception as e:
            logger.error(f"❌ Gmail API test failed: {e}")
            return False

    def validate_authentication(self, test_drive: bool = True, test_gmail: bool = True) -> dict:
        try:
            """Validate authentication and test API access."""
            logger.info("\n" + "="*80)
            logger.info("AUTHENTICATION VALIDATION")
            logger.info("="*80)

            results = {
                "authenticated": False,
                "token_saved": False,
                "drive_test": None,
                "gmail_test": None,
                "overall_success": False
            }

            # Authenticate
            if not self.authenticate():
                return results

            results["authenticated"] = True
            results["token_saved"] = self.token_file.exists()

            # Test APIs
            if test_drive and 'drive' in ' '.join(self.scopes):
                results["drive_test"] = self.test_drive_access()

            if test_gmail and 'gmail' in ' '.join(self.scopes):
                results["gmail_test"] = self.test_gmail_access()

            # Overall success
            results["overall_success"] = results["authenticated"] and (
                results["drive_test"] is not False and results["gmail_test"] is not False
            )

            return results

        except Exception as e:
            self.logger.error(f"Error in validate_authentication: {e}", exc_info=True)
            raise
def main():
    """Main authentication function."""
    import argparse
    parser = argparse.ArgumentParser(description="Authenticate with Google OAuth")
    parser.add_argument("--project-root", type=Path, default=project_root)
    parser.add_argument("--force", action="store_true", help="Force re-authentication")
    parser.add_argument("--scopes", choices=['drive', 'gmail', 'both'], default='both',
                        help="Which APIs to authenticate for")
    parser.add_argument("--test", action="store_true", help="Test API access after authentication")
    parser.add_argument("--test-drive-only", action="store_true", help="Test only Drive API")
    parser.add_argument("--test-gmail-only", action="store_true", help="Test only Gmail API")

    args = parser.parse_args()

    # Determine scopes
    scopes_map = {
        'drive': GoogleOAuthAuthenticator.SCOPES['drive'],
        'gmail': GoogleOAuthAuthenticator.SCOPES['gmail'],
        'both': GoogleOAuthAuthenticator.SCOPES['both']
    }
    scopes = scopes_map[args.scopes]

    authenticator = GoogleOAuthAuthenticator(args.project_root, scopes=scopes)

    if args.test or args.test_drive_only or args.test_gmail_only:
        # Validation mode
        test_drive = args.test_drive_only or (args.test and args.scopes in ['drive', 'both'])
        test_gmail = args.test_gmail_only or (args.test and args.scopes in ['gmail', 'both'])

        results = authenticator.validate_authentication(
            test_drive=test_drive,
            test_gmail=test_gmail
        )

        logger.info("\n" + "="*80)
        logger.info("VALIDATION RESULTS")
        logger.info("="*80)
        logger.info(f"Authenticated: {'✅' if results['authenticated'] else '❌'}")
        logger.info(f"Token saved: {'✅' if results['token_saved'] else '❌'}")
        if results['drive_test'] is not None:
            logger.info(f"Drive API test: {'✅' if results['drive_test'] else '❌'}")
        if results['gmail_test'] is not None:
            logger.info(f"Gmail API test: {'✅' if results['gmail_test'] else '❌'}")
        logger.info(f"\nOverall success: {'✅ YES' if results['overall_success'] else '❌ NO'}")

        return 0 if results['overall_success'] else 1
    else:
        # Authentication mode
        success = authenticator.authenticate(force=args.force)
        return 0 if success else 1

if __name__ == "__main__":


    sys.exit(main())