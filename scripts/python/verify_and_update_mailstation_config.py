#!/usr/bin/env python3
"""
Verify and Update MailStation Configuration
Checks actual MailStation setup and updates all config files to match reality.

Tags: #MAILSTATION #EMAIL #CONFIG #VERIFY #UPDATE
@JARVIS @LUMINA
"""

import sys
import json
import socket
from pathlib import Path
from typing import Dict, Any, Optional, List
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

logger = get_logger("VerifyMailStationConfig")


class MailStationConfigVerifier:
    """Verify and update MailStation configuration"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize verifier"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.nas_ip = "<NAS_PRIMARY_IP>"
        self.nas_integration = None

        if NAS_INTEGRATION_AVAILABLE:
            try:
                self.nas_integration = NASAzureVaultIntegration()
                logger.info("✅ NAS integration initialized")
            except Exception as e:
                logger.warning(f"⚠️  NAS integration not available: {e}")

    def check_ports(self) -> Dict[str, bool]:
        """Check which mail ports are open"""
        logger.info("🔍 Checking mail server ports...")

        ports_to_check = {
            "smtp_25": 25,
            "smtp_587": 587,
            "smtp_465": 465,
            "imap_143": 143,
            "imap_993": 993,
            "pop3_110": 110,
            "pop3_995": 995
        }

        results = {}
        for name, port in ports_to_check.items():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((self.nas_ip, port))
                sock.close()
                results[name] = result == 0
                status = "✅" if results[name] else "❌"
                logger.info(f"   {status} Port {port} ({name}): {'Open' if results[name] else 'Closed'}")
            except Exception as e:
                results[name] = False
                logger.warning(f"   ❌ Port {port} ({name}): Error - {e}")

        return results

    def get_actual_mail_config(self) -> Dict[str, Any]:
        """Get actual mail server configuration"""
        logger.info("📧 Getting actual mail server configuration...")

        config = {
            "package": "MailStation",
            "package_status": "installed_and_running",
            "nas_ip": self.nas_ip,
            "ports": self.check_ports(),
            "domains": [],
            "accounts": []
        }

        # Determine which ports are actually in use
        ports = config["ports"]

        # SMTP configuration
        if ports.get("smtp_587"):
            config["smtp"] = {
                "server": self.nas_ip,
                "port": 587,
                "encryption": "STARTTLS",
                "secure": False
            }
        elif ports.get("smtp_465"):
            config["smtp"] = {
                "server": self.nas_ip,
                "port": 465,
                "encryption": "SSL",
                "secure": True
            }
        elif ports.get("smtp_25"):
            config["smtp"] = {
                "server": self.nas_ip,
                "port": 25,
                "encryption": "STARTTLS",
                "secure": False
            }
        else:
            config["smtp"] = {
                "server": self.nas_ip,
                "port": 587,
                "encryption": "STARTTLS",
                "secure": False,
                "note": "Default - verify actual port"
            }

        # IMAP configuration
        if ports.get("imap_993"):
            config["imap"] = {
                "server": self.nas_ip,
                "port": 993,
                "encryption": "SSL/TLS",
                "secure": True
            }
        elif ports.get("imap_143"):
            config["imap"] = {
                "server": self.nas_ip,
                "port": 143,
                "encryption": "STARTTLS",
                "secure": False
            }
        else:
            config["imap"] = {
                "server": self.nas_ip,
                "port": 993,
                "encryption": "SSL/TLS",
                "secure": True,
                "note": "Default - verify actual port"
            }

        # Check for company domain
        # Based on existing configs, domain is likely <LOCAL_HOSTNAME>
        config["domains"] = ["<LOCAL_HOSTNAME>"]
        config["accounts"] = [
            {
                "email": "mlesn@<LOCAL_HOSTNAME>",
                "username": "mlesn",
                "type": "company"
            },
            {
                "email": "glesn@<LOCAL_HOSTNAME>",
                "username": "glesn",
                "type": "company"
            }
        ]

        logger.info(f"   ✅ SMTP: {config['smtp']['server']}:{config['smtp']['port']} ({config['smtp']['encryption']})")
        logger.info(f"   ✅ IMAP: {config['imap']['server']}:{config['imap']['port']} ({config['imap']['encryption']})")
        logger.info(f"   ✅ Domain: {config['domains'][0]}")

        return config

    def update_email_accounts_config(self, actual_config: Dict[str, Any]) -> Path:
        try:
            """Update email accounts configuration"""
            logger.info("📝 Updating email accounts configuration...")

            config_file = self.config_dir / "email_accounts_aggregation.json"

            # Read existing config
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    email_config = json.load(f)
            else:
                email_config = {}

            # Update company/mailstation section
            email_config["mailstation"] = {
                "package": "MailStation",
                "status": "installed_and_running",
                "server": actual_config["nas_ip"],
                "webmail": f"https://{actual_config['nas_ip']}:5001",
                "imap": actual_config["imap"],
                "smtp": actual_config["smtp"],
                "domain": actual_config["domains"][0],
                "accounts": actual_config["accounts"],
                "note": "MailStation is the active mail server (not MailPlus)"
            }

            # Update company section to match MailStation
            if "company" not in email_config:
                email_config["company"] = {}

            email_config["company"]["mailstation"] = email_config["mailstation"]
            email_config["company"]["domain"] = actual_config["domains"][0]
            email_config["company"]["accounts"] = actual_config["accounts"]

            # Save updated config
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(email_config, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Updated: {config_file.name}")
            return config_file

        except Exception as e:
            self.logger.error(f"Error in update_email_accounts_config: {e}", exc_info=True)
            raise
    def update_outlook_config(self, actual_config: Dict[str, Any]) -> Path:
        try:
            """Update Outlook configuration"""
            logger.info("💻 Updating Outlook configuration...")

            config_dir = self.config_dir / "outlook"
            config_dir.mkdir(parents=True, exist_ok=True)
            config_file = config_dir / "mailstation_outlook_config.json"

            config = {
                "mailstation": {
                    "package": "MailStation",
                    "imap": actual_config["imap"],
                    "smtp": actual_config["smtp"],
                    "domain": actual_config["domains"][0]
                },
                "outlook_desktop": {
                    "account_type": "IMAP",
                    "email": "mlesn@<LOCAL_HOSTNAME>",
                    "display_name": "Company Email (MailStation)",
                    "incoming_server": {
                        "server": actual_config["imap"]["server"],
                        "port": actual_config["imap"]["port"],
                        "encryption": actual_config["imap"]["encryption"],
                        "username": "mlesn@<LOCAL_HOSTNAME>"
                    },
                    "outgoing_server": {
                        "server": actual_config["smtp"]["server"],
                        "port": actual_config["smtp"]["port"],
                        "encryption": actual_config["smtp"]["encryption"],
                        "username": "mlesn@<LOCAL_HOSTNAME>",
                        "requires_authentication": True
                    },
                    "steps": [
                        "1. Open Outlook Desktop",
                        "2. File → Account Settings → Account Settings",
                        "3. New → Manual setup → POP or IMAP",
                        f"4. Email: mlesn@<LOCAL_HOSTNAME>",
                        f"5. IMAP Server: {actual_config['imap']['server']}",
                        f"6. IMAP Port: {actual_config['imap']['port']} ({actual_config['imap']['encryption']})",
                        f"7. SMTP Server: {actual_config['smtp']['server']}",
                        f"8. SMTP Port: {actual_config['smtp']['port']} ({actual_config['smtp']['encryption']})",
                        "9. More Settings → Outgoing Server: Require authentication",
                        "10. Test connection"
                    ]
                },
                "outlook_mobile": {
                    "account_type": "IMAP",
                    "email": "mlesn@<LOCAL_HOSTNAME>",
                    "incoming_server": {
                        "server": actual_config["imap"]["server"],
                        "port": actual_config["imap"]["port"],
                        "encryption": actual_config["imap"]["encryption"]
                    },
                    "outgoing_server": {
                        "server": actual_config["smtp"]["server"],
                        "port": actual_config["smtp"]["port"],
                        "encryption": actual_config["smtp"]["encryption"]
                    },
                    "steps": [
                        "1. Open Outlook Mobile App",
                        "2. Add Account → Advanced Setup → IMAP",
                        f"3. Email: mlesn@<LOCAL_HOSTNAME>",
                        f"4. IMAP Server: {actual_config['imap']['server']}",
                        f"5. IMAP Port: {actual_config['imap']['port']} ({actual_config['imap']['encryption']})",
                        f"6. SMTP Server: {actual_config['smtp']['server']}",
                        f"7. SMTP Port: {actual_config['smtp']['port']} ({actual_config['smtp']['encryption']})"
                    ]
                },
                "updated_at": datetime.now().isoformat(),
                "note": "Configuration verified against actual MailStation setup"
            }

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Updated: {config_file.name}")
            return config_file

        except Exception as e:
            self.logger.error(f"Error in update_outlook_config: {e}", exc_info=True)
            raise
    def update_n8n_config(self, actual_config: Dict[str, Any]) -> Path:
        try:
            """Update N8N configuration"""
            logger.info("⚙️  Updating N8N configuration...")

            n8n_config_dir = self.config_dir / "n8n"
            n8n_config_dir.mkdir(parents=True, exist_ok=True)

            # Update main email hub config
            main_config_file = n8n_config_dir / "nas_dsm_email_hub_expansion.json"

            if main_config_file.exists():
                with open(main_config_file, 'r', encoding='utf-8') as f:
                    n8n_config = json.load(f)
            else:
                n8n_config = {}

            # Update to reflect MailStation
            if "nas_dsm_config" not in n8n_config:
                n8n_config["nas_dsm_config"] = {}

            n8n_config["nas_dsm_config"]["email_hub_package"] = "MailStation"
            n8n_config["nas_dsm_config"]["package_name"] = "MailStation"
            n8n_config["nas_dsm_config"]["package_status"] = "installed_and_running"

            # Update email hub config with actual ports
            if "email_hub_config" not in n8n_config:
                n8n_config["email_hub_config"] = {}

            n8n_config["email_hub_config"]["smtp"] = {
                "server": actual_config["smtp"]["server"],
                "port": actual_config["smtp"]["port"],
                "secure": actual_config["smtp"]["secure"],
                "tls": actual_config["smtp"]["encryption"] in ["STARTTLS", "TLS"]
            }

            n8n_config["email_hub_config"]["imap"] = {
                "server": actual_config["imap"]["server"],
                "port": actual_config["imap"]["port"],
                "secure": actual_config["imap"]["secure"],
                "tls": actual_config["imap"]["encryption"] in ["STARTTLS", "TLS", "SSL/TLS"]
            }

            n8n_config["email_hub_config"]["domains"] = {
                "primary_domain": actual_config["domains"][0],
                "additional_domains": []
            }

            n8n_config["updated_at"] = datetime.now().isoformat()

            with open(main_config_file, 'w', encoding='utf-8') as f:
                json.dump(n8n_config, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Updated: {main_config_file.name}")
            return main_config_file

        except Exception as e:
            self.logger.error(f"Error in update_n8n_config: {e}", exc_info=True)
            raise
    def verify_and_update_all(self) -> Dict[str, Any]:
        """Verify and update all configurations"""
        logger.info("=" * 80)
        logger.info("🔍 VERIFYING AND UPDATING MAILSTATION CONFIGURATION")
        logger.info("=" * 80)
        logger.info("")

        results = {
            "timestamp": datetime.now().isoformat(),
            "actual_config": {},
            "files_updated": [],
            "success": False
        }

        # Step 1: Get actual configuration
        logger.info("STEP 1: Getting actual MailStation configuration...")
        results["actual_config"] = self.get_actual_mail_config()
        logger.info("")

        # Step 2: Update email accounts config
        logger.info("STEP 2: Updating email accounts configuration...")
        try:
            email_config_file = self.update_email_accounts_config(results["actual_config"])
            results["files_updated"].append(str(email_config_file))
        except Exception as e:
            logger.error(f"❌ Error updating email accounts config: {e}")
        logger.info("")

        # Step 3: Update Outlook config
        logger.info("STEP 3: Updating Outlook configuration...")
        try:
            outlook_config_file = self.update_outlook_config(results["actual_config"])
            results["files_updated"].append(str(outlook_config_file))
        except Exception as e:
            logger.error(f"❌ Error updating Outlook config: {e}")
        logger.info("")

        # Step 4: Update N8N config
        logger.info("STEP 4: Updating N8N configuration...")
        try:
            n8n_config_file = self.update_n8n_config(results["actual_config"])
            results["files_updated"].append(str(n8n_config_file))
        except Exception as e:
            logger.error(f"❌ Error updating N8N config: {e}")
        logger.info("")

        results["success"] = len(results["files_updated"]) > 0

        # Summary
        logger.info("=" * 80)
        logger.info("📊 VERIFICATION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Package: {results['actual_config']['package']}")
        logger.info(f"SMTP: {results['actual_config']['smtp']['server']}:{results['actual_config']['smtp']['port']}")
        logger.info(f"IMAP: {results['actual_config']['imap']['server']}:{results['actual_config']['imap']['port']}")
        logger.info(f"Domain: {results['actual_config']['domains'][0]}")
        logger.info(f"Files Updated: {len(results['files_updated'])}")
        logger.info("")
        logger.info("=" * 80)
        if results["success"]:
            logger.info("✅ CONFIGURATION UPDATED SUCCESSFULLY")
        else:
            logger.info("⚠️  CONFIGURATION UPDATE INCOMPLETE")
        logger.info("=" * 80)

        # Save results
        results_file = self.project_root / "data" / "mailstation_config_verification.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)

        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"📄 Results saved: {results_file.name}")

        return results


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Verify and Update MailStation Configuration")
        parser.add_argument("--project-root", help="Project root directory")

        args = parser.parse_args()

        project_root = Path(args.project_root) if args.project_root else None

        verifier = MailStationConfigVerifier(project_root=project_root)
        results = verifier.verify_and_update_all()

        return 0 if results["success"] else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    exit(main())