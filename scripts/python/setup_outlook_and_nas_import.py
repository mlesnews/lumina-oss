"""
Complete Setup: Outlook + NAS Email Import
Master script that sets up Outlook and configures email import to NAS mail hub.

This script:
1. Sets up Outlook with Gmail and ProtonMail
2. Configures email import to NAS MailPlus
3. Sets up scheduled import daemon
4. Verifies all connections

#JARVIS #LUMINA #OUTLOOK #NAS #EMAIL #SETUP
"""

import sys
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("SetupOutlookAndNASImport")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("SetupOutlookAndNASImport")

from scripts.python.setup_outlook_gmail_protonmail import OutlookSetupHelper
from scripts.python.automated_outlook_setup import AutomatedOutlookSetup
from scripts.python.import_emails_to_nas_hub import NASEmailImporter


class CompleteOutlookNASSetup:
    """
    Complete setup for Outlook and NAS email import.
    """

    def __init__(self, project_root: Path):
        """
        Initialize complete setup.

        Args:
            project_root: Project root directory
        """
        self.project_root = Path(project_root)
        self.setup_helper = OutlookSetupHelper(project_root)
        self.automated_setup = AutomatedOutlookSetup(project_root)
        self.email_importer = NASEmailImporter(project_root)

    def run_complete_setup(self) -> Dict[str, Any]:
        """
        Run complete setup process.

        Returns:
            Setup results dictionary
        """
        logger.info("="*80)
        logger.info("COMPLETE OUTLOOK + NAS EMAIL IMPORT SETUP")
        logger.info("="*80)
        logger.info("")

        results = {
            "timestamp": datetime.now().isoformat(),
            "outlook_setup": {},
            "nas_import_config": {},
            "test_import": {},
            "success": False
        }

        # Step 1: Check Outlook setup prerequisites
        logger.info("STEP 1: Checking Outlook Setup Prerequisites")
        logger.info("-" * 80)
        outlook_check = self.setup_helper.run_setup_check()
        results["outlook_setup"]["check"] = outlook_check
        logger.info("")

        # Step 2: Generate Outlook configuration
        logger.info("STEP 2: Generating Outlook Configuration")
        logger.info("-" * 80)
        try:
            nas_config = self.automated_setup.create_import_to_nas_config()
            results["nas_import_config"] = nas_config
            logger.info("✅ NAS import configuration created")
        except Exception as e:
            logger.error(f"❌ Failed to create NAS import config: {e}")
        logger.info("")

        # Step 3: Create automated setup scripts
        logger.info("STEP 3: Creating Automated Setup Scripts")
        logger.info("-" * 80)
        try:
            # This will create PowerShell script if credentials are available
            setup_results = self.automated_setup.run_setup()
            results["outlook_setup"]["automated"] = setup_results
            logger.info("✅ Automated setup scripts created")
        except Exception as e:
            logger.warning(f"⚠️  Automated setup script creation: {e}")
        logger.info("")

        # Step 4: Test email import (dry run)
        logger.info("STEP 4: Testing Email Import System")
        logger.info("-" * 80)
        try:
            # Test with small date range
            test_results = self.email_importer.run_import(days_back=7, sources=["gmail", "protonmail"])
            results["test_import"] = test_results
            logger.info("✅ Email import system tested")
        except Exception as e:
            logger.warning(f"⚠️  Email import test: {e}")
        logger.info("")

        # Step 5: Create scheduled import daemon
        logger.info("STEP 5: Setting Up Scheduled Import")
        logger.info("-" * 80)
        try:
            daemon_config = self._create_import_daemon_config()
            results["scheduled_import"] = daemon_config
            logger.info("✅ Scheduled import daemon configuration created")
        except Exception as e:
            logger.warning(f"⚠️  Scheduled import setup: {e}")
        logger.info("")

        # Summary
        results["success"] = (
            results.get("nas_import_config") and
            results.get("outlook_setup", {}).get("check", {}).get("config_files_generated", False)
        )

        logger.info("="*80)
        if results["success"]:
            logger.info("✅ SETUP COMPLETE")
        else:
            logger.info("⚠️  SETUP PARTIALLY COMPLETE")
        logger.info("="*80)
        logger.info("")

        self._print_next_steps(results)

        return results

    def _create_import_daemon_config(self) -> Dict[str, Any]:
        try:
            """Create configuration for scheduled import daemon."""
            daemon_config = {
                "name": "email_import_to_nas_daemon",
                "description": "Scheduled email import from Gmail/ProtonMail to NAS MailPlus",
                "script": "scripts/python/import_emails_to_nas_hub.py",
                "schedule": {
                    "enabled": True,
                    "interval_minutes": 15,
                    "run_at_startup": True
                },
                "settings": {
                    "days_back": 30,
                    "sources": ["gmail", "protonmail"],
                    "skip_duplicates": True
                },
                "log_file": "data/email_import/daemon.log"
            }

            config_file = self.project_root / "config" / "outlook" / "import_daemon_config.json"
            config_file.parent.mkdir(parents=True, exist_ok=True)

            import json
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(daemon_config, f, indent=2, ensure_ascii=False)

            logger.info(f"   📄 Daemon config: {config_file}")
            return daemon_config

        except Exception as e:
            self.logger.error(f"Error in _create_import_daemon_config: {e}", exc_info=True)
            raise
    def _print_next_steps(self, results: Dict[str, Any]):
        """Print next steps for user."""
        logger.info("📋 NEXT STEPS:")
        logger.info("")

        logger.info("1. OUTLOOK SETUP:")
        logger.info("   - Install Proton Bridge: https://proton.me/mail/bridge")
        logger.info("   - Follow instructions: config/outlook/OUTLOOK_SETUP_INSTRUCTIONS.md")
        logger.info("   - Or run PowerShell script: config/outlook/setup_outlook_accounts.ps1")
        logger.info("")

        logger.info("2. EMAIL IMPORT:")
        logger.info("   - Test import: python scripts/python/import_emails_to_nas_hub.py --days-back 7")
        logger.info("   - Full import: python scripts/python/import_emails_to_nas_hub.py --days-back 365")
        logger.info("")

        logger.info("3. SCHEDULED IMPORT:")
        logger.info("   - Review daemon config: config/outlook/import_daemon_config.json")
        logger.info("   - Set up Windows Task Scheduler or cron job")
        logger.info("   - Or use JARVIS daemon system")
        logger.info("")

        logger.info("4. VERIFICATION:")
        logger.info("   - Check imported emails: data/email_import/archive/")
        logger.info("   - Verify NAS MailPlus receives emails")
        logger.info("   - Monitor import logs: data/email_import/daemon.log")
        logger.info("")


def main():
    try:
        """Main function."""
        import argparse

        parser = argparse.ArgumentParser(
            description="Complete Setup: Outlook + NAS Email Import"
        )

        parser.add_argument(
            "--project-root",
            type=Path,
            default=Path(__file__).parent.parent.parent,
            help="Project root directory"
        )
        parser.add_argument(
            "--test-import",
            action="store_true",
            help="Run test import after setup"
        )

        args = parser.parse_args()

        setup = CompleteOutlookNASSetup(args.project_root)
        results = setup.run_complete_setup()

        if args.test_import:
            logger.info("")
            logger.info("Running test import...")
            importer = NASEmailImporter(args.project_root)
            test_results = importer.run_import(days_back=7)
            logger.info(f"Test import complete: {test_results['total_imported']} emails imported")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()