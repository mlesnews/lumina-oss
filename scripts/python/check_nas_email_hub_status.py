#!/usr/bin/env python3
"""
Check NAS Company Email Hub Status

Checks the current status of NAS DSM email hub setup and determines
which mail package (MailPlus vs MailStation) should be used.

Tags: #NAS #EMAIL #DSM #MAILPLUS #MAILSTATION #SETUP
@JARVIS @MARVIN
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
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
    from nas_azure_vault_integration import NASAzureVaultIntegration
    NAS_INTEGRATION_AVAILABLE = True
except ImportError:
    NAS_INTEGRATION_AVAILABLE = False
    NASAzureVaultIntegration = None

logger = get_logger("CheckNASEmailHubStatus")


class NASEmailHubStatusChecker:
    """Check NAS DSM email hub status and package configuration"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize status checker"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.nas_integration = None

        if NAS_INTEGRATION_AVAILABLE:
            try:
                self.nas_integration = NASAzureVaultIntegration()
                logger.info("✅ NAS integration initialized")
            except Exception as e:
                logger.warning(f"⚠️  NAS integration not available: {e}")

    def check_dsm_packages(self) -> Dict[str, Any]:
        """
        Check which DSM mail packages are installed

        Returns:
            Dict with package status for MailPlus and MailStation
        """
        logger.info("📦 Checking DSM mail packages...")

        packages_status = {
            "mailplus": {
                "installed": False,
                "running": False,
                "version": None,
                "license_required": True,
                "features": [
                    "Advanced email management",
                    "Webmail interface",
                    "Mobile app support",
                    "Calendar integration",
                    "Contact management",
                    "Email filtering rules",
                    "Anti-spam/Anti-virus",
                    "Email archiving",
                    "Email backup"
                ]
            },
            "mailstation": {
                "installed": False,
                "running": False,
                "version": None,
                "license_required": False,
                "features": [
                    "Basic email server",
                    "SMTP/IMAP/POP3",
                    "Email forwarding",
                    "Basic filtering"
                ]
            },
            "mail_server": {
                "installed": False,
                "running": False,
                "version": None,
                "license_required": False,
                "note": "Basic mail server package (vanilla)"
            }
        }

        if not self.nas_integration:
            logger.warning("⚠️  Cannot check packages - NAS integration not available")
            return packages_status

        try:
            # Try to get SSH connection
            ssh_client = self.nas_integration.get_ssh_client()
            if not ssh_client:
                logger.warning("⚠️  Cannot connect to NAS via SSH")
                return packages_status

            # Check each package - try multiple methods
            for package_name in ["MailPlus", "MailStation", "MailServer"]:
                try:
                    # Method 1: Try synopkg (may not be available via SSH)
                    stdin, stdout, stderr = ssh_client.exec_command(
                        f"synopkg status {package_name} 2>/dev/null || echo 'not_found'"
                    )
                    output = stdout.read().decode().strip()

                    # Method 2: Check if package directory exists
                    if "not_found" in output or "not installed" in output.lower() or "command not found" in output.lower():
                        # Try checking package directory
                        stdin2, stdout2, stderr2 = ssh_client.exec_command(
                            f"test -d /var/packages/{package_name} && echo 'exists' || echo 'not_exists'"
                        )
                        dir_check = stdout2.read().decode().strip()

                        if dir_check == "exists":
                            # Package directory exists - likely installed
                            output = "installed"
                        else:
                            continue

                    # Determine which package this is
                    if package_name == "MailPlus":
                        packages_status["mailplus"]["installed"] = True
                        packages_status["mailplus"]["running"] = "started" in output.lower() or "running" in output.lower() or "installed" in output.lower()
                    elif package_name == "MailStation":
                        packages_status["mailstation"]["installed"] = True
                        packages_status["mailstation"]["running"] = "started" in output.lower() or "running" in output.lower() or "installed" in output.lower()
                    elif package_name == "MailServer":
                        packages_status["mail_server"]["installed"] = True
                        packages_status["mail_server"]["running"] = "started" in output.lower() or "running" in output.lower() or "installed" in output.lower()

                    logger.info(f"   ✅ {package_name}: {'Running' if packages_status.get(package_name.lower().replace('mail', 'mail_'), {}).get('running') else 'Installed'}")

                except Exception as e:
                    logger.debug(f"   ⚠️  Error checking {package_name}: {e}")

            # Also check if ports are open (indicates mail server running)
            try:
                import socket
                # Check IMAP port
                imap_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                imap_sock.settimeout(2)
                imap_result = imap_sock.connect_ex(('<NAS_PRIMARY_IP>', 993))
                imap_sock.close()

                if imap_result == 0:
                    # IMAP port is open - mail server is likely running
                    # Assume MailPlus if configured, otherwise MailStation
                    if not packages_status["mailplus"]["installed"] and not packages_status["mailstation"]["installed"]:
                        packages_status["mailplus"]["installed"] = True
                        packages_status["mailplus"]["running"] = True
                        logger.info("   ✅ Mail server detected via port check (IMAP 993 open)")
            except:
                pass

        except Exception as e:
            logger.warning(f"⚠️  Error checking packages: {e}")

        return packages_status

    def get_recommendation(self, packages_status: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get recommendation on which package to use

        Args:
            packages_status: Status from check_dsm_packages()

        Returns:
            Recommendation with reasoning
        """
        recommendation = {
            "recommended_package": None,
            "reason": "",
            "alternatives": [],
            "setup_required": False
        }

        mailplus = packages_status.get("mailplus", {})
        mailstation = packages_status.get("mailstation", {})
        mail_server = packages_status.get("mail_server", {})

        # Check what's already installed
        if mailplus.get("installed") and mailplus.get("running"):
            recommendation["recommended_package"] = "MailPlus"
            recommendation["reason"] = "MailPlus is already installed and running - use it for full feature set"
            recommendation["setup_required"] = False
        elif mailstation.get("installed") and mailstation.get("running"):
            recommendation["recommended_package"] = "MailStation"
            recommendation["reason"] = "MailStation is already installed and running - basic features available"
            recommendation["setup_required"] = False
            recommendation["alternatives"] = [
                "Consider upgrading to MailPlus for advanced features (calendar, webmail, mobile app)"
            ]
        elif mail_server.get("installed") and mail_server.get("running"):
            recommendation["recommended_package"] = "Mail Server"
            recommendation["reason"] = "Mail Server (vanilla) is installed - basic SMTP/IMAP only"
            recommendation["setup_required"] = False
            recommendation["alternatives"] = [
                "Consider MailStation for better management interface",
                "Consider MailPlus for full enterprise features (requires license)"
            ]
        else:
            # Nothing installed - recommend based on requirements
            recommendation["recommended_package"] = "MailPlus"
            recommendation["reason"] = "For company email hub, MailPlus provides: webmail, calendar, contacts, mobile apps, advanced filtering"
            recommendation["setup_required"] = True
            recommendation["alternatives"] = [
                "MailStation: Good middle ground if MailPlus license not available",
                "Mail Server: Basic option if only SMTP/IMAP needed"
            ]

        return recommendation

    def check_email_hub_config(self) -> Dict[str, Any]:
        """Check if email hub is configured"""
        logger.info("📧 Checking email hub configuration...")

        config_status = {
            "n8n_configured": False,
            "email_accounts_configured": False,
            "smtp_configured": False,
            "imap_configured": False,
            "syphon_integration": False
        }

        # Check n8n config
        n8n_config_file = self.config_dir / "n8n" / "nas_dsm_email_hub_expansion.json"
        if n8n_config_file.exists():
            try:
                with open(n8n_config_file, 'r', encoding='utf-8') as f:
                    n8n_config = json.load(f)
                    config_status["n8n_configured"] = n8n_config.get("n8n_expansion", {}).get("status") == "active"
                    config_status["smtp_configured"] = "smtp" in n8n_config.get("email_hub_config", {})
                    config_status["imap_configured"] = "imap" in n8n_config.get("email_hub_config", {})
                    config_status["syphon_integration"] = n8n_config.get("integration_points", {}).get("syphon", {}).get("enabled", False)
            except Exception as e:
                logger.warning(f"⚠️  Error reading n8n config: {e}")

        # Check email accounts config
        email_config_file = self.project_root / "data" / "syphon" / "nas_dsm_mail" / "nas_dsm_mail_config.json"
        if email_config_file.exists():
            try:
                with open(email_config_file, 'r', encoding='utf-8') as f:
                    email_config = json.load(f)
                    accounts = email_config.get("accounts", [])
                    config_status["email_accounts_configured"] = len(accounts) > 0
            except Exception as e:
                logger.warning(f"⚠️  Error reading email config: {e}")

        return config_status

    def generate_status_report(self) -> Dict[str, Any]:
        """Generate complete status report"""
        logger.info("=" * 80)
        logger.info("📊 NAS COMPANY EMAIL HUB STATUS REPORT")
        logger.info("=" * 80)
        logger.info("")

        # Check packages
        packages_status = self.check_dsm_packages()

        # Get recommendation
        recommendation = self.get_recommendation(packages_status)

        # Check configuration
        config_status = self.check_email_hub_config()

        report = {
            "timestamp": datetime.now().isoformat(),
            "packages": packages_status,
            "recommendation": recommendation,
            "configuration": config_status,
            "setup_complete": False
        }

        # Determine if setup is complete
        package_installed = (
            packages_status.get("mailplus", {}).get("installed") or
            packages_status.get("mailstation", {}).get("installed") or
            packages_status.get("mail_server", {}).get("installed")
        )

        package_running = (
            packages_status.get("mailplus", {}).get("running") or
            packages_status.get("mailstation", {}).get("running") or
            packages_status.get("mail_server", {}).get("running")
        )

        report["setup_complete"] = (
            package_installed and
            package_running and
            config_status.get("n8n_configured", False) and
            config_status.get("email_accounts_configured", False)
        )

        # Print summary
        logger.info("📦 PACKAGE STATUS:")
        for pkg_name, pkg_status in packages_status.items():
            installed = pkg_status.get("installed", False)
            running = pkg_status.get("running", False)
            status_icon = "✅" if (installed and running) else ("⚠️" if installed else "❌")
            logger.info(f"   {status_icon} {pkg_name.replace('_', ' ').title()}: {'Running' if running else ('Installed' if installed else 'Not Installed')}")

        logger.info("")
        logger.info("💡 RECOMMENDATION:")
        logger.info(f"   Package: {recommendation['recommended_package']}")
        logger.info(f"   Reason: {recommendation['reason']}")
        if recommendation.get("alternatives"):
            logger.info("   Alternatives:")
            for alt in recommendation["alternatives"]:
                logger.info(f"      - {alt}")

        logger.info("")
        logger.info("⚙️  CONFIGURATION STATUS:")
        for config_item, configured in config_status.items():
            status_icon = "✅" if configured else "❌"
            logger.info(f"   {status_icon} {config_item.replace('_', ' ').title()}: {'Configured' if configured else 'Not Configured'}")

        logger.info("")
        logger.info("=" * 80)
        if report["setup_complete"]:
            logger.info("✅ EMAIL HUB SETUP COMPLETE")
        else:
            logger.info("⚠️  EMAIL HUB SETUP INCOMPLETE")
            logger.info("   Run setup script to complete configuration")
        logger.info("=" * 80)

        return report


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Check NAS Company Email Hub Status")
        parser.add_argument("--project-root", help="Project root directory")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        project_root = Path(args.project_root) if args.project_root else None

        checker = NASEmailHubStatusChecker(project_root=project_root)
        report = checker.generate_status_report()

        if args.json:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            # Report already printed by generate_status_report
            pass


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()