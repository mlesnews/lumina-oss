"""
Execute Complete Outlook Classic Setup
Runs all setup steps: email import, Outlook configuration, verification.

#JARVIS #LUMINA #OUTLOOK #DOIT #CONTINUE
"""

import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("ExecuteCompleteOutlookSetup")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ExecuteCompleteOutlookSetup")


class CompleteOutlookSetupExecutor:
    """
    Execute complete Outlook Classic setup process.
    """

    def __init__(self, project_root: Path):
        """Initialize executor."""
        self.project_root = Path(project_root)
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "email_import": {"status": "pending", "imported": 0},
            "outlook_setup": {"status": "pending"},
            "verification": {"status": "pending"},
            "success": False
        }

    def step1_import_emails_to_nas_hub(self) -> bool:
        """
        Step 1: Import emails from Gmail and ProtonMail to NAS Mail Hub.

        Returns:
            True if successful
        """
        logger.info("="*80)
        logger.info("STEP 1: IMPORTING EMAILS TO NAS MAIL HUB")
        logger.info("="*80)
        logger.info("")

        try:
            # Run email import
            import_script = self.project_root / "scripts" / "python" / "import_emails_to_nas_hub.py"

            logger.info("Running email import (last 30 days for initial setup)...")
            logger.info("This may take a few minutes...")
            logger.info("")

            result = subprocess.run(
                [sys.executable, str(import_script), "--days-back", "30"],
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )

            if result.returncode == 0:
                # Parse results if possible
                output = result.stdout
                if "imported" in output.lower():
                    logger.info("✅ Email import completed")
                    self.results["email_import"]["status"] = "completed"
                    # Try to extract count
                    for line in output.split("\n"):
                        if "imported" in line.lower() and "skipped" in line.lower():
                            logger.info(f"   {line.strip()}")
                else:
                    logger.info("✅ Email import process completed")
                    self.results["email_import"]["status"] = "completed"

                logger.info("")
                return True
            else:
                logger.warning(f"⚠️  Email import had issues (exit code: {result.returncode})")
                logger.warning("   This is OK - you can run import manually later")
                logger.info("")
                self.results["email_import"]["status"] = "partial"
                return True  # Continue anyway

        except subprocess.TimeoutExpired:
            logger.warning("⚠️  Email import timed out")
            logger.info("   This is OK - you can run import manually later")
            logger.info("")
            self.results["email_import"]["status"] = "timeout"
            return True  # Continue anyway
        except Exception as e:
            logger.warning(f"⚠️  Email import error: {e}")
            logger.info("   This is OK - you can run import manually later")
            logger.info("")
            self.results["email_import"]["status"] = "error"
            return True  # Continue anyway

    def step2_configure_outlook(self) -> bool:
        """
        Step 2: Configure Outlook Classic via PowerShell script.

        Returns:
            True if successful
        """
        logger.info("="*80)
        logger.info("STEP 2: CONFIGURING OUTLOOK CLASSIC")
        logger.info("="*80)
        logger.info("")

        try:
            # Run PowerShell setup script
            ps_script = self.project_root / "config" / "outlook" / "setup_outlook_nas_hub.ps1"

            if not ps_script.exists():
                logger.error(f"❌ Setup script not found: {ps_script}")
                return False

            logger.info("Running Outlook setup script...")
            logger.info("")

            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(ps_script)],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=60
            )

            output = (result.stdout or "") + (result.stderr or "")

            if "Outlook is installed" in output or "Outlook is accessible" in output:
                logger.info("✅ Outlook setup script executed")
                logger.info("")

                if "Account already exists" in output or "account already configured" in output.lower():
                    logger.info("✅ NAS Mail Hub account is already configured!")
                    self.results["outlook_setup"]["status"] = "already_configured"
                    return True
                elif "MANUAL SETUP REQUIRED" in output:
                    logger.info("⚠️  Manual setup required (Outlook COM API limitations)")
                    logger.info("")
                    logger.info("Please complete setup manually:")
                    logger.info("  1. Open Outlook")
                    logger.info("  2. File → Account Settings → Account Settings")
                    logger.info("  3. Click 'New...'")
                    logger.info("  4. Follow: config/outlook/OUTLOOK_QUICK_SETUP.md")
                    logger.info("")
                    self.results["outlook_setup"]["status"] = "manual_required"
                    return True
                else:
                    logger.info("✅ Setup script completed")
                    self.results["outlook_setup"]["status"] = "completed"
                    return True
            else:
                logger.warning("⚠️  Could not verify Outlook setup")
                logger.info("   Please check manually")
                self.results["outlook_setup"]["status"] = "unknown"
                return True  # Continue to verification

        except Exception as e:
            logger.warning(f"⚠️  Outlook setup error: {e}")
            logger.info("   Please complete setup manually")
            logger.info("   See: config/outlook/OUTLOOK_QUICK_SETUP.md")
            logger.info("")
            self.results["outlook_setup"]["status"] = "error"
            return True  # Continue to verification

    def step3_verify_setup(self) -> bool:
        """
        Step 3: Verify Outlook setup.

        Returns:
            True if verified
        """
        logger.info("="*80)
        logger.info("STEP 3: VERIFYING SETUP")
        logger.info("="*80)
        logger.info("")

        try:
            verify_script = self.project_root / "scripts" / "python" / "verify_outlook_nas_hub_setup.py"

            result = subprocess.run(
                [sys.executable, str(verify_script)],
                capture_output=True,
                text=True,
                timeout=30
            )

            output = result.stdout + result.stderr

            if result.returncode == 0:
                logger.info("✅ Verification completed")
                if "NAS MAIL HUB ACCOUNT IS CONFIGURED" in output:
                    logger.info("✅ NAS Mail Hub account is configured!")
                    self.results["verification"]["status"] = "configured"
                    self.results["success"] = True
                    return True
                else:
                    logger.warning("⚠️  NAS Mail Hub account not yet configured")
                    logger.info("   Please complete manual setup")
                    self.results["verification"]["status"] = "not_configured"
                    return False
            else:
                logger.warning("⚠️  Verification had issues")
                self.results["verification"]["status"] = "error"
                return False

        except Exception as e:
            logger.warning(f"⚠️  Verification error: {e}")
            self.results["verification"]["status"] = "error"
            return False

    def print_summary(self):
        """Print setup summary."""
        logger.info("")
        logger.info("="*80)
        logger.info("SETUP SUMMARY")
        logger.info("="*80)
        logger.info("")

        # Email Import
        import_status = self.results["email_import"]["status"]
        status_icon = "✅" if import_status == "completed" else "⚠️"
        logger.info(f"{status_icon} Email Import: {import_status}")

        # Outlook Setup
        outlook_status = self.results["outlook_setup"]["status"]
        if outlook_status == "already_configured":
            status_icon = "✅"
        elif outlook_status == "manual_required":
            status_icon = "⚠️"
        else:
            status_icon = "⏳"
        logger.info(f"{status_icon} Outlook Setup: {outlook_status}")

        # Verification
        verify_status = self.results["verification"]["status"]
        status_icon = "✅" if verify_status == "configured" else "⚠️"
        logger.info(f"{status_icon} Verification: {verify_status}")

        logger.info("")

        if self.results["success"]:
            logger.info("="*80)
            logger.info("✅ SETUP COMPLETE - OUTLOOK IS READY!")
            logger.info("="*80)
        else:
            logger.info("="*80)
            logger.info("⚠️  SETUP PARTIALLY COMPLETE")
            logger.info("="*80)
            logger.info("")
            logger.info("Next Steps:")
            logger.info("  1. Complete Outlook manual setup:")
            logger.info("     - Open Outlook")
            logger.info("     - File → Account Settings → Account Settings")
            logger.info("     - Follow: config/outlook/OUTLOOK_QUICK_SETUP.md")
            logger.info("")
            logger.info("  2. Verify email import:")
            logger.info("     python scripts/python/import_emails_to_nas_hub.py --days-back 365")
            logger.info("")

    def execute_all(self) -> Dict[str, Any]:
        """
        Execute all setup steps.

        Returns:
            Results dictionary
        """
        logger.info("="*80)
        logger.info("EXECUTING COMPLETE OUTLOOK CLASSIC SETUP")
        logger.info("="*80)
        logger.info("")
        logger.info("This will:")
        logger.info("  1. Import emails from Gmail/ProtonMail to NAS Mail Hub")
        logger.info("  2. Configure Outlook Classic to connect to NAS Mail Hub")
        logger.info("  3. Verify the setup")
        logger.info("")
        logger.info("Starting in 3 seconds...")
        time.sleep(3)
        logger.info("")

        # Step 1: Import emails
        self.step1_import_emails_to_nas_hub()
        time.sleep(2)

        # Step 2: Configure Outlook
        self.step2_configure_outlook()
        time.sleep(2)

        # Step 3: Verify
        self.step3_verify_setup()

        # Print summary
        self.print_summary()

        return self.results


def main():
    try:
        """Main function."""
        import argparse

        parser = argparse.ArgumentParser(
            description="Execute Complete Outlook Classic Setup"
        )

        parser.add_argument(
            "--project-root",
            type=Path,
            default=Path(__file__).parent.parent.parent,
            help="Project root directory"
        )

        args = parser.parse_args()

        executor = CompleteOutlookSetupExecutor(args.project_root)
        results = executor.execute_all()

        # Save results
        results_file = args.project_root / "config" / "outlook" / "setup_results.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)

        import json
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info("")
        logger.info(f"📄 Results saved: {results_file}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()