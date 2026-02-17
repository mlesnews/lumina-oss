#!/usr/bin/env python3
"""
Setup MailPlus Email Hub - Complete Email Aggregation

Installs and configures MailPlus on NAS, then sets up n8n workflows
to aggregate emails from all sources:
- Google/Gmail
- Proton Family Suite (via Proton Bridge on host PC)
- Xfinity
- Apple/.me
- Yahoo
- Outlook
- Others

Tags: #NAS #MAILPLUS #EMAIL #AGGREGATION #N8N #PROTONBRIDGE
@JARVIS @MARVIN
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
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

logger = get_logger("SetupMailPlusEmailHub")


class MailPlusEmailHubSetup:
    """Setup MailPlus and configure email aggregation"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize setup"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.n8n_config_dir = self.config_dir / "n8n"
        self.nas_integration = None

        if NAS_INTEGRATION_AVAILABLE:
            try:
                self.nas_integration = NASAzureVaultIntegration()
                logger.info("✅ NAS integration initialized")
            except Exception as e:
                logger.warning(f"⚠️  NAS integration not available: {e}")

    def install_mailplus(self) -> bool:
        """Install MailPlus on NAS"""
        logger.info("📦 Installing MailPlus on NAS...")

        if not self.nas_integration:
            logger.error("❌ NAS integration not available")
            return False

        try:
            ssh_client = self.nas_integration.get_ssh_client()
            if not ssh_client:
                logger.error("❌ Cannot connect to NAS")
                return False

            # Check if MailPlus is already installed
            stdin, stdout, stderr = ssh_client.exec_command("synopkg status MailPlus")
            output = stdout.read().decode().strip()

            if "started" in output.lower() or "running" in output.lower():
                logger.info("✅ MailPlus is already installed and running")
                return True

            # Install MailPlus
            logger.info("   Installing MailPlus package...")
            stdin, stdout, stderr = ssh_client.exec_command("synopkg install MailPlus")
            install_output = stdout.read().decode().strip()
            error_output = stderr.read().decode().strip()

            if "successfully" in install_output.lower() or "installed" in install_output.lower():
                logger.info("✅ MailPlus installed successfully")

                # Start MailPlus
                logger.info("   Starting MailPlus...")
                stdin, stdout, stderr = ssh_client.exec_command("synopkg start MailPlus")
                start_output = stdout.read().decode().strip()

                if "started" in start_output.lower():
                    logger.info("✅ MailPlus started successfully")
                    return True
                else:
                    logger.warning(f"⚠️  MailPlus installed but may not have started: {start_output}")
                    return True
            else:
                logger.error(f"❌ MailPlus installation failed: {error_output}")
                return False

        except Exception as e:
            logger.error(f"❌ Error installing MailPlus: {e}")
            return False

    def create_email_accounts_config(self) -> Dict[str, Any]:
        try:
            """Create configuration for all email accounts"""
            logger.info("📧 Creating email accounts configuration...")

            # Company email accounts (<LOCAL_HOSTNAME> domain)
            company_accounts = {
                "mlesn": {
                    "email": "mlesn@<LOCAL_HOSTNAME>",
                    "username": "mlesn",
                    "full_name": "mlesn",
                    "domain": "<LOCAL_HOSTNAME>",
                    "type": "company",
                    "description": "Primary company email account"
                },
                "glesn": {
                    "email": "glesn@<LOCAL_HOSTNAME>",
                    "username": "glesn",
                    "full_name": "glesn",
                    "domain": "<LOCAL_HOSTNAME>",
                    "type": "company",
                    "description": "Company email account"
                }
            }

            email_accounts = {
                "google": {
                    "provider": "Gmail",
                    "type": "oauth2",
                    "imap": {
                        "server": "imap.gmail.com",
                        "port": 993,
                        "ssl": True,
                        "auth": "oauth2"
                    },
                    "smtp": {
                        "server": "smtp.gmail.com",
                        "port": 587,
                        "ssl": True,
                        "auth": "oauth2"
                    },
                    "notes": "Requires OAuth2 setup in Google Cloud Console"
                },
                "proton": {
                    "provider": "ProtonMail",
                    "type": "bridge",
                    "accounts": {
                        "mlesn": {
                            "protonmail_email": "mlesn@protonmail.com",
                            "bridge_username": "mlesn",
                            "imap": {
                                "server": "127.0.0.1",
                                "port": 1143,
                                "ssl": False,
                                "auth": "password",
                                "note": "Proton Bridge must be running on host PC"
                            },
                            "smtp": {
                                "server": "127.0.0.1",
                                "port": 1025,
                                "ssl": False,
                                "auth": "password",
                                "note": "Proton Bridge must be running on host PC"
                            },
                            "enabled": True,
                            "description": "Primary ProtonMail account - has emails"
                        },
                        "glesn": {
                            "protonmail_email": "glesn@protonmail.com",
                            "bridge_username": "glesn",
                            "imap": {
                                "server": "127.0.0.1",
                                "port": 1143,
                                "ssl": False,
                                "auth": "password",
                                "note": "Proton Bridge must be running on host PC (may need separate Bridge instance or different port)"
                            },
                            "smtp": {
                                "server": "127.0.0.1",
                                "port": 1025,
                                "ssl": False,
                                "auth": "password",
                                "note": "Proton Bridge must be running on host PC"
                            },
                            "enabled": True,
                            "description": "Glenda's ProtonMail account - newly created, no emails yet",
                            "note": "Account exists but is empty - will sync when emails arrive"
                        }
                    },
                    "bridge": {
                        "host": "localhost",
                        "imap_port": 1143,
                        "smtp_port": 1025,
                        "running_on": "host_pc",
                        "note": "If using multiple accounts, may need separate Bridge instances or Proton Family with shared Bridge"
                    }
                },
                "xfinity": {
                    "provider": "Xfinity",
                    "type": "imap",
                    "imap": {
                        "server": "imap.comcast.net",
                        "port": 993,
                        "ssl": True,
                        "auth": "password"
                    },
                    "smtp": {
                        "server": "smtp.comcast.net",
                        "port": 587,
                        "ssl": True,
                        "auth": "password"
                    }
                },
                "apple": {
                    "provider": "Apple/iCloud",
                    "type": "imap",
                    "imap": {
                        "server": "imap.mail.me.com",
                        "port": 993,
                        "ssl": True,
                        "auth": "app_specific_password",
                        "note": "Requires App-Specific Password from Apple ID"
                    },
                    "smtp": {
                        "server": "smtp.mail.me.com",
                        "port": 587,
                        "ssl": True,
                        "auth": "app_specific_password"
                    }
                },
                "yahoo": {
                    "provider": "Yahoo Mail",
                    "type": "oauth2",
                    "imap": {
                        "server": "imap.mail.yahoo.com",
                        "port": 993,
                        "ssl": True,
                        "auth": "oauth2"
                    },
                    "smtp": {
                        "server": "smtp.mail.yahoo.com",
                        "port": 587,
                        "ssl": True,
                        "auth": "oauth2"
                    },
                    "notes": "OAuth2 preferred, or App Password"
                },
                "outlook": {
                    "provider": "Outlook/Microsoft 365",
                    "type": "oauth2",
                    "imap": {
                        "server": "outlook.office365.com",
                        "port": 993,
                        "ssl": True,
                        "auth": "oauth2"
                    },
                    "smtp": {
                        "server": "smtp.office365.com",
                        "port": 587,
                        "ssl": True,
                        "auth": "oauth2"
                    },
                    "notes": "OAuth2 preferred, or App Password"
                }
            }

            # Add company email accounts (<LOCAL_HOSTNAME> domain)
            email_accounts["company"] = {
                "domain": "<LOCAL_HOSTNAME>",
                "accounts": {
                    "mlesn": {
                        "email": "mlesn@<LOCAL_HOSTNAME>",
                        "username": "mlesn",
                        "full_name": "mlesn",
                        "type": "company",
                        "description": "Primary company email account",
                        "windows_account": "mlesn",
                        "quota_mb": 5000
                    },
                    "glesn": {
                        "email": "glesn@<LOCAL_HOSTNAME>",
                        "username": "glesn",
                        "full_name": "glesn",
                        "type": "company",
                        "description": "Company email account",
                        "windows_account": "glesn",
                        "quota_mb": 5000
                    }
                },
                "mailplus": {
                    "domain": "<LOCAL_HOSTNAME>",
                    "server": "<NAS_PRIMARY_IP>",
                    "webmail": "https://<NAS_PRIMARY_IP>:5001/mailplus",
                    "imap": {
                        "server": "<NAS_PRIMARY_IP>",
                        "port": 993,
                        "ssl": True
                    },
                    "smtp": {
                        "server": "<NAS_PRIMARY_IP>",
                        "port": 587,
                        "ssl": True
                    }
                }
            }

            # Save configuration
            config_file = self.config_dir / "email_accounts_aggregation.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(email_accounts, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Email accounts configuration saved: {config_file.name}")
            logger.info(f"   ✅ Company domain: <LOCAL_HOSTNAME>")
            logger.info(f"   ✅ Company accounts: mlesn, glesn")
            return email_accounts

        except Exception as e:
            self.logger.error(f"Error in create_email_accounts_config: {e}", exc_info=True)
            raise
    def create_n8n_email_aggregation_workflows(self) -> Dict[str, Any]:
        try:
            """Create n8n workflows for email aggregation"""
            logger.info("🔄 Creating n8n email aggregation workflows...")

            workflows = {
                "email_aggregation_google": {
                    "name": "Email Aggregation - Google/Gmail",
                    "workflow_id": "email_aggregation_google",
                    "trigger": {
                        "type": "schedule",
                        "interval_minutes": 5
                    },
                    "nodes": [
                        {
                            "type": "schedule",
                            "name": "Check Every 5 Minutes",
                            "settings": {
                                "rule": {
                                    "interval": [{"field": "minutes", "minutesInterval": 5}]
                                }
                            }
                        },
                        {
                            "type": "http",
                            "name": "Get Gmail OAuth Token",
                            "settings": {
                                "url": "{{$env.GOOGLE_OAUTH_TOKEN_URL}}",
                                "method": "POST",
                                "authentication": "genericCredentialType",
                                "genericAuthType": "httpHeaderAuth"
                            }
                        },
                        {
                            "type": "imap",
                            "name": "Fetch Gmail Emails",
                            "settings": {
                                "host": "imap.gmail.com",
                                "port": 993,
                                "secure": True,
                                "user": "={{$json.email}}",
                                "password": "={{$json.access_token}}",
                                "mailbox": "INBOX",
                                "options": {"seen": False, "new": True}
                            }
                        },
                        {
                            "type": "webhook",
                            "name": "Send to SYPHON",
                            "settings": {
                                "url": "http://localhost:8000/api/syphon/email",
                                "method": "POST"
                            }
                        },
                        {
                            "type": "webhook",
                            "name": "Store in NAS MailPlus",
                            "settings": {
                                "url": "https://<NAS_PRIMARY_IP>:5001/webapi/entry.cgi",
                                "method": "POST",
                                "body": {
                                    "api": "SYNO.MailPlus.Mail",
                                    "method": "store",
                                    "version": "1"
                                }
                            }
                        }
                    ]
                },
                "email_aggregation_proton": {
                    "name": "Email Aggregation - ProtonMail (Bridge)",
                    "workflow_id": "email_aggregation_proton",
                    "trigger": {
                        "type": "schedule",
                        "interval_minutes": 5
                    },
                    "nodes": [
                        {
                            "type": "schedule",
                            "name": "Check Every 5 Minutes",
                            "settings": {
                                "rule": {
                                    "interval": [{"field": "minutes", "minutesInterval": 5}]
                                }
                            }
                        },
                        {
                            "type": "http",
                            "name": "Check Proton Bridge Status",
                            "settings": {
                                "url": "http://localhost:8080/api/v1/status",
                                "method": "GET",
                                "note": "Proton Bridge API on host PC"
                            }
                        },
                        {
                            "type": "imap",
                            "name": "Fetch ProtonMail via Bridge",
                            "settings": {
                                "host": "127.0.0.1",
                                "port": 1143,
                                "secure": False,
                                "user": "={{$json.proton_username}}",
                                "password": "={{$json.proton_bridge_password}}",
                                "mailbox": "INBOX",
                                "options": {"seen": False, "new": True},
                                "note": "Proton Bridge must be running on host PC"
                            }
                        },
                        {
                            "type": "webhook",
                            "name": "Send to SYPHON",
                            "settings": {
                                "url": "http://localhost:8000/api/syphon/email",
                                "method": "POST"
                            }
                        }
                    ]
                },
                "email_aggregation_xfinity": {
                    "name": "Email Aggregation - Xfinity",
                    "workflow_id": "email_aggregation_xfinity",
                    "trigger": {
                        "type": "schedule",
                        "interval_minutes": 5
                    },
                    "nodes": [
                        {
                            "type": "schedule",
                            "name": "Check Every 5 Minutes"
                        },
                        {
                            "type": "http",
                            "name": "Get Xfinity Credentials from Azure Vault",
                            "settings": {
                                "url": "{{$env.AZURE_KEY_VAULT_URL}}/secrets/xfinity-email-password",
                                "method": "GET"
                            }
                        },
                        {
                            "type": "imap",
                            "name": "Fetch Xfinity Emails",
                            "settings": {
                                "host": "imap.comcast.net",
                                "port": 993,
                                "secure": True,
                                "user": "={{$json.email}}",
                                "password": "={{$json.password}}",
                                "mailbox": "INBOX"
                            }
                        },
                        {
                            "type": "webhook",
                            "name": "Send to SYPHON"
                        }
                    ]
                },
                "email_aggregation_apple": {
                    "name": "Email Aggregation - Apple/iCloud",
                    "workflow_id": "email_aggregation_apple",
                    "trigger": {
                        "type": "schedule",
                        "interval_minutes": 5
                    },
                    "nodes": [
                        {
                            "type": "schedule",
                            "name": "Check Every 5 Minutes"
                        },
                        {
                            "type": "http",
                            "name": "Get Apple Credentials from Azure Vault",
                            "settings": {
                                "url": "{{$env.AZURE_KEY_VAULT_URL}}/secrets/apple-email-password",
                                "method": "GET",
                                "note": "Requires App-Specific Password"
                            }
                        },
                        {
                            "type": "imap",
                            "name": "Fetch Apple/iCloud Emails",
                            "settings": {
                                "host": "imap.mail.me.com",
                                "port": 993,
                                "secure": True,
                                "user": "={{$json.email}}",
                                "password": "={{$json.app_specific_password}}",
                                "mailbox": "INBOX"
                            }
                        },
                        {
                            "type": "webhook",
                            "name": "Send to SYPHON"
                        }
                    ]
                },
                "email_aggregation_yahoo": {
                    "name": "Email Aggregation - Yahoo",
                    "workflow_id": "email_aggregation_yahoo",
                    "trigger": {
                        "type": "schedule",
                        "interval_minutes": 5
                    },
                    "nodes": [
                        {
                            "type": "schedule",
                            "name": "Check Every 5 Minutes"
                        },
                        {
                            "type": "imap",
                            "name": "Fetch Yahoo Emails",
                            "settings": {
                                "host": "imap.mail.yahoo.com",
                                "port": 993,
                                "secure": True,
                                "user": "={{$json.email}}",
                                "password": "={{$json.password}}",
                                "mailbox": "INBOX",
                                "note": "OAuth2 or App Password"
                            }
                        },
                        {
                            "type": "webhook",
                            "name": "Send to SYPHON"
                        }
                    ]
                },
                "email_aggregation_outlook": {
                    "name": "Email Aggregation - Outlook/Microsoft 365",
                    "workflow_id": "email_aggregation_outlook",
                    "trigger": {
                        "type": "schedule",
                        "interval_minutes": 5
                    },
                    "nodes": [
                        {
                            "type": "schedule",
                            "name": "Check Every 5 Minutes"
                        },
                        {
                            "type": "imap",
                            "name": "Fetch Outlook Emails",
                            "settings": {
                                "host": "outlook.office365.com",
                                "port": 993,
                                "secure": True,
                                "user": "={{$json.email}}",
                                "password": "={{$json.password}}",
                                "mailbox": "INBOX",
                                "note": "OAuth2 or App Password"
                            }
                        },
                        {
                            "type": "webhook",
                            "name": "Send to SYPHON"
                        }
                    ]
                },
                "email_aggregation_unified": {
                    "name": "Email Aggregation - Unified Processing",
                    "workflow_id": "email_aggregation_unified",
                    "trigger": {
                        "type": "webhook",
                        "path": "/email/aggregate/all"
                    },
                    "nodes": [
                        {
                            "type": "webhook",
                            "name": "Receive Aggregation Request"
                        },
                        {
                            "type": "function",
                            "name": "Aggregate All Email Sources",
                            "description": "Calls all email aggregation workflows"
                        },
                        {
                            "type": "webhook",
                            "name": "Send to SYPHON for Intelligence Extraction"
                        },
                        {
                            "type": "webhook",
                            "name": "Store in NAS MailPlus Archive"
                        },
                        {
                            "type": "webhook",
                            "name": "Notify JARVIS"
                        }
                    ]
                }
            }

            # Save workflows configuration
            workflows_file = self.n8n_config_dir / "email_aggregation_workflows.json"
            workflows_file.parent.mkdir(parents=True, exist_ok=True)

            with open(workflows_file, 'w', encoding='utf-8') as f:
                json.dump(workflows, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ n8n workflows configuration saved: {workflows_file.name}")
            logger.info(f"   Created {len(workflows)} workflows")

            return workflows

        except Exception as e:
            self.logger.error(f"Error in create_n8n_email_aggregation_workflows: {e}", exc_info=True)
            raise
    def create_proton_bridge_config(self) -> Dict[str, Any]:
        try:
            """Create Proton Bridge configuration"""
            logger.info("🔐 Creating Proton Bridge configuration...")

            proton_bridge_config = {
                "bridge": {
                    "name": "Proton Bridge on Host PC",
                    "host": "localhost",
                    "imap": {
                        "port": 1143,
                        "ssl": False,
                        "note": "Proton Bridge IMAP port"
                    },
                    "smtp": {
                        "port": 1025,
                        "ssl": False,
                        "note": "Proton Bridge SMTP port"
                    },
                    "api": {
                        "port": 8080,
                        "endpoint": "http://localhost:8080/api/v1",
                        "note": "Proton Bridge API (if available)"
                    },
                    "installation": {
                        "platform": "windows",
                        "download_url": "https://proton.me/mail/bridge",
                        "note": "Install Proton Bridge on host PC"
                    },
                    "setup": {
                        "steps": [
                            "1. Download and install Proton Bridge from proton.me/mail/bridge",
                            "2. Sign in with Proton Family account",
                            "3. Enable IMAP/SMTP in Bridge settings",
                            "4. Note IMAP port (default: 1143) and SMTP port (default: 1025)",
                            "5. Configure n8n to connect to localhost:1143 (IMAP) and localhost:1025 (SMTP)"
                        ]
                    }
                },
                "n8n_integration": {
                    "note": "n8n must run on host PC or have network access to host PC",
                    "connection": {
                        "type": "local",
                        "host": "127.0.0.1",
                        "imap_port": 1143,
                        "smtp_port": 1025
                    }
                },
                "credentials": {
                    "storage": "azure_key_vault",
                    "secrets": [
                        "proton-bridge-username",
                        "proton-bridge-password",
                        "proton-family-accounts"
                    ],
                    "note": "Store Proton Bridge credentials in Azure Key Vault"
                }
            }

            # Save configuration
            config_file = self.config_dir / "proton_bridge_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(proton_bridge_config, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Proton Bridge configuration saved: {config_file.name}")
            return proton_bridge_config

        except Exception as e:
            self.logger.error(f"Error in create_proton_bridge_config: {e}", exc_info=True)
            raise
    def run_complete_setup(self) -> Dict[str, Any]:
        """Run complete email hub setup"""
        logger.info("=" * 80)
        logger.info("🚀 COMPLETE EMAIL HUB SETUP")
        logger.info("=" * 80)
        logger.info("")

        results = {
            "timestamp": datetime.now().isoformat(),
            "mailplus_installed": False,
            "email_accounts_configured": False,
            "n8n_workflows_created": False,
            "proton_bridge_configured": False,
            "success": False
        }

        # Step 1: Install MailPlus
        logger.info("STEP 1: Installing MailPlus...")
        results["mailplus_installed"] = self.install_mailplus()
        logger.info("")

        # Step 2: Create email accounts configuration
        logger.info("STEP 2: Creating email accounts configuration...")
        email_accounts = self.create_email_accounts_config()
        results["email_accounts_configured"] = True
        logger.info(f"   ✅ Configured {len(email_accounts)} email providers")
        logger.info("")

        # Step 3: Create n8n workflows
        logger.info("STEP 3: Creating n8n email aggregation workflows...")
        workflows = self.create_n8n_email_aggregation_workflows()
        results["n8n_workflows_created"] = True
        logger.info(f"   ✅ Created {len(workflows)} workflows")
        logger.info("")

        # Step 4: Configure Proton Bridge
        logger.info("STEP 4: Configuring Proton Bridge integration...")
        proton_config = self.create_proton_bridge_config()
        results["proton_bridge_configured"] = True
        logger.info("   ✅ Proton Bridge configuration created")
        logger.info("")

        # Summary
        results["success"] = all([
            results["mailplus_installed"],
            results["email_accounts_configured"],
            results["n8n_workflows_created"],
            results["proton_bridge_configured"]
        ])

        logger.info("=" * 80)
        if results["success"]:
            logger.info("✅ EMAIL HUB SETUP COMPLETE")
        else:
            logger.info("⚠️  EMAIL HUB SETUP PARTIALLY COMPLETE")
        logger.info("=" * 80)
        logger.info("")
        logger.info("📋 NEXT STEPS:")
        logger.info("   1. Install Proton Bridge on host PC (if not already installed)")
        logger.info("   2. Configure OAuth2 for Google/Yahoo/Outlook (if using)")
        logger.info("   3. Store email credentials in Azure Key Vault")
        logger.info("   4. Import n8n workflows from config/n8n/email_aggregation_workflows.json")
        logger.info("   5. Test email aggregation workflows")
        logger.info("")

        return results


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Setup MailPlus Email Hub with Complete Aggregation")
        parser.add_argument("--project-root", help="Project root directory")
        parser.add_argument("--skip-install", action="store_true", help="Skip MailPlus installation")

        args = parser.parse_args()

        project_root = Path(args.project_root) if args.project_root else None

        setup = MailPlusEmailHubSetup(project_root=project_root)

        if args.skip_install:
            # Just create configurations
            setup.create_email_accounts_config()
            setup.create_n8n_email_aggregation_workflows()
            setup.create_proton_bridge_config()
        else:
            # Full setup
            results = setup.run_complete_setup()

            # Save results
            results_file = setup.project_root / "data" / "email_hub_setup_results.json"
            results_file.parent.mkdir(parents=True, exist_ok=True)
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            logger.info(f"📄 Results saved: {results_file.name}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()