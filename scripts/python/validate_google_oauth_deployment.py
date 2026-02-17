"""
Google OAuth Deployment Validation Script

Validates complete Google OAuth deployment and integration.
Part of LUMINA deployment implementation.
"""
import sys
from pathlib import Path
from typing import Dict, Any, List
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("GoogleOAuthValidation")

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

class GoogleOAuthDeploymentValidator:
    """Validates Google OAuth deployment."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.results = {}

    def validate_credentials_setup(self) -> Dict[str, Any]:
        """Validate credentials setup."""
        logger.info("\n1. Validating credentials setup...")

        from scripts.python.setup_google_oauth import GoogleOAuthSetup

        setup = GoogleOAuthSetup(self.project_root)
        results = setup.validate_credentials()

        return results

    def validate_authentication(self) -> Dict[str, Any]:
        """Validate authentication."""
        logger.info("\n2. Validating authentication...")

        from scripts.python.authenticate_google_oauth import GoogleOAuthAuthenticator

        authenticator = GoogleOAuthAuthenticator(self.project_root)
        results = authenticator.validate_authentication()

        return results

    def validate_integration(self) -> Dict[str, Any]:
        """Validate integration with existing systems."""
        logger.info("\n3. Validating integration...")

        results = {
            "google_drive_access_available": False,
            "gmail_integration_available": False,
            "integration_success": False
        }

        # Check if google_drive_access.py exists and works
        try:
            from scripts.python.google_drive_access import GoogleDriveAccess
            drive_access = GoogleDriveAccess(project_root=self.project_root)
            if drive_access.service:
                results["google_drive_access_available"] = True
            elif drive_access.initialize_api():
                results["google_drive_access_available"] = True
        except Exception as e:
            logger.warning(f"Google Drive access check: {e}")

        # Check if gmail integration exists
        try:
            gmail_module = self.project_root / "scripts" / "python" / "lumina_gmail_integration_system.py"
            if gmail_module.exists():
                results["gmail_integration_available"] = True
        except Exception as e:
            logger.warning(f"Gmail integration check: {e}")

        results["integration_success"] = (
            results["google_drive_access_available"] or
            results["gmail_integration_available"]
        )

        return results

    def run_full_validation(self) -> Dict[str, Any]:
        """Run complete validation."""
        logger.info("="*80)
        logger.info("GOOGLE OAUTH DEPLOYMENT VALIDATION")
        logger.info("="*80)

        validation_results = {
            "credentials_setup": {},
            "authentication": {},
            "integration": {},
            "overall_success": False
        }

        # Validate credentials
        validation_results["credentials_setup"] = self.validate_credentials_setup()

        # Validate authentication (only if credentials are set up)
        if validation_results["credentials_setup"].get("setup_complete", False):
            validation_results["authentication"] = self.validate_authentication()
        else:
            logger.warning("\n⚠️  Skipping authentication validation (credentials not set up)")
            validation_results["authentication"] = {"skipped": True}

        # Validate integration
        validation_results["integration"] = self.validate_integration()

        # Overall success
        validation_results["overall_success"] = (
            validation_results["credentials_setup"].get("setup_complete", False) and
            validation_results["authentication"].get("overall_success", False) and
            validation_results["integration"].get("integration_success", False)
        )

        return validation_results

    def print_results(self, results: Dict[str, Any]):
        """Print validation results."""
        logger.info("\n" + "="*80)
        logger.info("VALIDATION RESULTS SUMMARY")
        logger.info("="*80)

        # Credentials setup
        logger.info("\n📋 Credentials Setup:")
        creds = results.get("credentials_setup", {})
        logger.info(f"   File exists: {'✅' if creds.get('credentials_file_exists') else '❌'}")
        logger.info(f"   File valid: {'✅' if creds.get('credentials_file_valid') else '❌'}")
        logger.info(f"   Setup complete: {'✅' if creds.get('setup_complete') else '❌'}")

        # Authentication
        logger.info("\n🔐 Authentication:")
        auth = results.get("authentication", {})
        if auth.get("skipped"):
            logger.info("   ⚠️  Skipped (credentials not set up)")
        else:
            logger.info(f"   Authenticated: {'✅' if auth.get('authenticated') else '❌'}")
            logger.info(f"   Token saved: {'✅' if auth.get('token_saved') else '❌'}")
            if auth.get('drive_test') is not None:
                logger.info(f"   Drive API: {'✅' if auth.get('drive_test') else '❌'}")
            if auth.get('gmail_test') is not None:
                logger.info(f"   Gmail API: {'✅' if auth.get('gmail_test') else '❌'}")

        # Integration
        logger.info("\n🔗 Integration:")
        integration = results.get("integration", {})
        logger.info(f"   Drive access: {'✅' if integration.get('google_drive_access_available') else '❌'}")
        logger.info(f"   Gmail integration: {'✅' if integration.get('gmail_integration_available') else '❌'}")

        # Overall
        logger.info("\n" + "="*80)
        overall = results.get("overall_success", False)
        logger.info(f"OVERALL DEPLOYMENT STATUS: {'✅ SUCCESS' if overall else '❌ NOT COMPLETE'}")
        logger.info("="*80)

        if not overall:
            logger.info("\n📋 Next steps:")
            if not creds.get("setup_complete"):
                logger.info("   1. Set up credentials: python scripts/python/setup_google_oauth.py --instructions")
            elif not auth.get("overall_success"):
                logger.info("   2. Authenticate: python scripts/python/authenticate_google_oauth.py --test")
            elif not integration.get("integration_success"):
                logger.info("   3. Check integration modules")

def main():
    """Main validation function."""
    import argparse
    parser = argparse.ArgumentParser(description="Validate Google OAuth deployment")
    parser.add_argument("--project-root", type=Path, default=project_root)

    args = parser.parse_args()

    validator = GoogleOAuthDeploymentValidator(args.project_root)
    results = validator.run_full_validation()
    validator.print_results(results)

    return 0 if results.get("overall_success", False) else 1

if __name__ == "__main__":


    sys.exit(main())