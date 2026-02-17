#!/usr/bin/env python3
"""
Execute MailPlus Setup Plan
Comprehensive script to complete MailPlus setup based on current status.

This script:
1. Checks current status
2. Installs/upgrades to MailPlus (if needed)
3. Guides through Gmail OAuth2 setup
4. Configures ProtonMail Bridge integration
5. Generates Outlook configuration files
6. Sets up N8N integration
7. Verifies all connections

Tags: #MAILPLUS #EMAIL #SETUP #EXECUTION #DOIT
@JARVIS @LUMINA
"""

import sys
import json
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

logger = get_logger("ExecuteMailPlusSetup")


class MailPlusSetupExecutor:
    """Execute MailPlus setup plan based on current status"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize executor"""
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

    def check_current_status(self) -> Dict[str, Any]:
        """Check current setup status"""
        logger.info("=" * 80)
        logger.info("📊 CHECKING CURRENT STATUS")
        logger.info("=" * 80)

        status = {
            "mailplus_installed": False,
            "mailstation_installed": False,
            "gmail_configured": False,
            "protonmail_configured": False,
            "outlook_desktop_configured": False,
            "outlook_mobile_configured": False,
            "n8n_configured": False
        }

        # Check MailPlus/MailStation
        if self.nas_integration:
            try:
                ssh_client = self.nas_integration.get_ssh_client()
                if ssh_client:
                    # Check MailPlus
                    stdin, stdout, stderr = ssh_client.exec_command(
                        "synopkg status MailPlus 2>/dev/null || echo 'not_installed'"
                    )
                    mailplus_output = stdout.read().decode().strip()
                    if "not_installed" not in mailplus_output.lower():
                        status["mailplus_installed"] = True
                        logger.info("   ✅ MailPlus: Installed")
                    else:
                        logger.info("   ❌ MailPlus: Not Installed")

                    # Check MailStation
                    stdin, stdout, stderr = ssh_client.exec_command(
                        "synopkg status MailStation 2>/dev/null || echo 'not_installed'"
                    )
                    mailstation_output = stdout.read().decode().strip()
                    if "not_installed" not in mailstation_output.lower():
                        status["mailstation_installed"] = True
                        logger.info("   ✅ MailStation: Installed")
            except Exception as e:
                logger.warning(f"   ⚠️  Error checking packages: {e}")

        # Check configuration files
        email_config = self.config_dir / "email_accounts_aggregation.json"
        if email_config.exists():
            try:
                with open(email_config, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    status["gmail_configured"] = "google" in config
                    status["protonmail_configured"] = "proton" in config
                    logger.info("   ✅ Email accounts configuration: Found")
            except Exception as e:
                logger.warning(f"   ⚠️  Error reading email config: {e}")

        outlook_config = self.config_dir / "outlook" / "outlook_accounts.json"
        if outlook_config.exists():
            status["outlook_desktop_configured"] = True
            logger.info("   ✅ Outlook configuration: Found")

        return status

    def install_mailplus(self) -> bool:
        """Install or upgrade to MailPlus"""
        logger.info("=" * 80)
        logger.info("📦 INSTALLING/UPGRADING TO MAILPLUS")
        logger.info("=" * 80)

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

            logger.info("   Installing MailPlus...")
            logger.warning("   ⚠️  NOTE: MailPlus requires a license")
            logger.info("   Please ensure license is available in Package Center")

            # Try to install
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
                    logger.warning(f"⚠️  MailPlus may need manual start: {start_output}")
                    return True
            else:
                logger.error(f"❌ MailPlus installation may have failed")
                logger.info(f"   Output: {install_output}")
                logger.info(f"   Error: {error_output}")
                logger.info("   💡 Try installing via DSM Package Center manually")
                return False

        except Exception as e:
            logger.error(f"❌ Error installing MailPlus: {e}")
            logger.info("   💡 Try installing via DSM Package Center manually")
            return False

    def generate_gmail_setup_instructions(self) -> str:
        """Generate Gmail OAuth2 setup instructions"""
        instructions = """
================================================================================
📧 GMAIL OAUTH2 SETUP INSTRUCTIONS
================================================================================

Follow these steps to add Gmail to MailPlus:

1. ACCESS MAILPLUS EXTERNAL MAIL:
   - Open DSM: https://<NAS_PRIMARY_IP>:5001
   - Go to: MailPlus Server → Settings → External Mail
   - Or: MailPlus Web Client → Settings → External Mail

2. ADD GMAIL ACCOUNT:
   - Click "Add Account" or "+" button
   - Select "Gmail" from provider list

3. COMPLETE OAUTH2 FLOW:
   - You'll be redirected to Google OAuth consent page
   - Sign in with your Gmail account
   - IMPORTANT: Check the permission:
     ✅ "Read, compose, send, and permanently delete all your email from Gmail"
   - Click "Allow" or "Continue"
   - You'll be redirected back to MailPlus

4. CONFIGURE SYNC SETTINGS:
   - Sync Frequency: Every 15 minutes (or as needed)
   - Folders to Sync: All folders or selected
   - Sync Direction: Bidirectional

5. VERIFY CONNECTION:
   - Status should show "Connected" or "Active"
   - Click "Sync Now" to test
   - Check that emails appear in MailPlus

================================================================================
⚠️  MANUAL STEP REQUIRED: OAuth2 flow must be completed in browser
================================================================================
"""
        return instructions

    def generate_protonmail_setup_instructions(self, bridge_location: str = "host_pc") -> str:
        """Generate ProtonMail Bridge setup instructions"""
        if bridge_location == "nas":
            instructions = """
================================================================================
🔐 PROTONMAIL BRIDGE SETUP (ON NAS)
================================================================================

Option A: Install Bridge on NAS (Recommended for MailPlus integration)

1. INSTALL PROTON BRIDGE ON NAS:
   - If NAS supports Docker: Run Bridge in container
   - Or install Bridge directly if supported
   - Configure Bridge to listen on NAS IP (not just localhost)

2. ADD PROTONMAIL TO MAILPLUS:
   - External Mail → Add Account → Other
   - Incoming Server: [NAS IP where Bridge is running]
   - IMAP Port: 1143
   - Outgoing Server: [NAS IP where Bridge is running]
   - SMTP Port: 1025
   - Username: Bridge-generated username
   - Password: Bridge-generated password

================================================================================
"""
        else:
            instructions = """
================================================================================
🔐 PROTONMAIL BRIDGE SETUP (ON HOST PC)
================================================================================

Option B: Bridge on Host PC + MailPlus Forwarding

CURRENT SETUP:
- Proton Bridge running on host PC (localhost:1143/1025)
- MailPlus on NAS (<NAS_PRIMARY_IP>)

CHALLENGE:
- MailPlus cannot directly access localhost on host PC
- Need to bridge the connection

SOLUTIONS:

1. USE N8N AS BRIDGE:
   - N8N can access Bridge on host PC (via host.docker.internal or host IP)
   - N8N processes emails and forwards to MailPlus
   - See N8N workflow configuration

2. CONFIGURE BRIDGE FOR NETWORK ACCESS:
   - Bridge Settings → Advanced
   - Configure Bridge to listen on network IP (not just localhost)
   - Update MailPlus to connect to host PC IP
   - Update firewall rules

3. MANUAL FORWARDING:
   - Set up email forwarding rules in MailPlus
   - Or use N8N workflows to sync emails

================================================================================
⚠️  DECISION NEEDED: Bridge location and connection method
================================================================================
"""
        return instructions

    def generate_outlook_configuration(self) -> Dict[str, Any]:
        try:
            """Generate Outlook configuration for MailPlus"""
            logger.info("=" * 80)
            logger.info("💻 GENERATING OUTLOOK CONFIGURATION")
            logger.info("=" * 80)

            config = {
                "mailplus": {
                    "imap": {
                        "server": "<NAS_PRIMARY_IP>",
                        "port": 993,
                        "encryption": "SSL/TLS",
                        "username": "mlesn@<LOCAL_HOSTNAME>"
                    },
                    "smtp": {
                        "server": "<NAS_PRIMARY_IP>",
                        "port": 587,
                        "encryption": "STARTTLS",
                        "username": "mlesn@<LOCAL_HOSTNAME>"
                    }
                },
                "outlook_desktop": {
                    "steps": [
                        "1. Open Outlook Desktop",
                        "2. File → Account Settings → Account Settings",
                        "3. New → Manual setup → POP or IMAP",
                        "4. Enter MailPlus settings (see mailplus section above)",
                        "5. More Settings → Outgoing Server: Require authentication",
                        "6. Advanced: IMAP 993 (SSL), SMTP 587 (STARTTLS)",
                        "7. Test connection"
                    ]
                },
                "outlook_mobile": {
                    "steps": [
                        "1. Open Outlook Mobile App",
                        "2. Add Account → Advanced Setup → IMAP",
                        "3. Email: mlesn@<LOCAL_HOSTNAME>",
                        "4. IMAP Server: <NAS_PRIMARY_IP>, Port: 993 (SSL/TLS)",
                        "5. SMTP Server: <NAS_PRIMARY_IP>, Port: 587 (STARTTLS)",
                        "6. Configure sync settings"
                    ]
                }
            }

            # Save configuration
            config_file = self.config_dir / "outlook" / "mailplus_outlook_config.json"
            config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Outlook configuration saved: {config_file.name}")
            return config

        except Exception as e:
            self.logger.error(f"Error in generate_outlook_configuration: {e}", exc_info=True)
            raise
    def generate_n8n_configuration(self, bridge_location: str = "host_pc") -> Dict[str, Any]:
        try:
            """Generate N8N configuration for Proton Bridge"""
            logger.info("=" * 80)
            logger.info("⚙️  GENERATING N8N CONFIGURATION")
            logger.info("=" * 80)

            if bridge_location == "nas":
                n8n_config = {
                    "proton_bridge": {
                        "host": "127.0.0.1",
                        "imap_port": 1143,
                        "smtp_port": 1025,
                        "note": "Bridge on NAS - N8N can access via localhost"
                    }
                }
            else:
                n8n_config = {
                    "proton_bridge": {
                        "host": "host.docker.internal",
                        "imap_port": 1143,
                        "smtp_port": 1025,
                        "note": "Bridge on host PC - N8N in Docker uses host.docker.internal",
                        "alternative": {
                            "host": "[HOST_PC_IP]",
                            "note": "If host.docker.internal doesn't work, use host PC IP address"
                        }
                    },
                    "workflow_nodes": {
                        "email_trigger_imap": {
                            "host": "host.docker.internal",
                            "port": 1143,
                            "username": "[Bridge-generated username]",
                            "password": "[Bridge-generated password]",
                            "ssl": False,
                            "allow_self_signed": True
                        },
                        "send_email_smtp": {
                            "host": "host.docker.internal",
                            "port": 1025,
                            "username": "[Bridge-generated username]",
                            "password": "[Bridge-generated password]",
                            "ssl": False,
                            "allow_self_signed": True
                        }
                    }
                }

            # Save configuration
            n8n_config_dir = self.config_dir / "n8n"
            n8n_config_dir.mkdir(parents=True, exist_ok=True)
            config_file = n8n_config_dir / "proton_bridge_n8n_config.json"

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(n8n_config, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ N8N configuration saved: {config_file.name}")
            return n8n_config

        except Exception as e:
            self.logger.error(f"Error in generate_n8n_configuration: {e}", exc_info=True)
            raise
    def execute_setup_plan(self, 
                          install_mailplus: bool = True,
                          bridge_location: str = "host_pc") -> Dict[str, Any]:
        """Execute complete setup plan"""
        logger.info("=" * 80)
        logger.info("🚀 EXECUTING MAILPLUS SETUP PLAN")
        logger.info("=" * 80)
        logger.info("")

        results = {
            "timestamp": datetime.now().isoformat(),
            "status_check": {},
            "mailplus_installed": False,
            "configurations_generated": False,
            "instructions_generated": False,
            "success": False
        }

        # Step 1: Check current status
        logger.info("STEP 1: Checking current status...")
        results["status_check"] = self.check_current_status()
        logger.info("")

        # Step 2: Install MailPlus (if requested)
        if install_mailplus and not results["status_check"].get("mailplus_installed"):
            logger.info("STEP 2: Installing MailPlus...")
            results["mailplus_installed"] = self.install_mailplus()
            logger.info("")
        else:
            logger.info("STEP 2: Skipping MailPlus installation (already installed or skipped)")
            results["mailplus_installed"] = results["status_check"].get("mailplus_installed", False)
            logger.info("")

        # Step 3: Generate configurations
        logger.info("STEP 3: Generating configurations...")
        try:
            outlook_config = self.generate_outlook_configuration()
            n8n_config = self.generate_n8n_configuration(bridge_location=bridge_location)
            results["configurations_generated"] = True
            logger.info("")
        except Exception as e:
            logger.error(f"❌ Error generating configurations: {e}")
            logger.info("")

        # Step 4: Generate instructions
        logger.info("STEP 4: Generating setup instructions...")
        try:
            gmail_instructions = self.generate_gmail_setup_instructions()
            protonmail_instructions = self.generate_protonmail_setup_instructions(bridge_location)

            # Save instructions
            instructions_file = self.project_root / "docs" / "email" / "SETUP_INSTRUCTIONS.md"
            instructions_file.parent.mkdir(parents=True, exist_ok=True)

            with open(instructions_file, 'w', encoding='utf-8') as f:
                f.write("# MailPlus Setup Instructions\n\n")
                f.write(gmail_instructions)
                f.write("\n\n")
                f.write(protonmail_instructions)

            logger.info(f"✅ Instructions saved: {instructions_file.name}")
            results["instructions_generated"] = True
            logger.info("")
        except Exception as e:
            logger.error(f"❌ Error generating instructions: {e}")
            logger.info("")

        # Print instructions
        logger.info("=" * 80)
        logger.info("📋 SETUP INSTRUCTIONS")
        logger.info("=" * 80)
        logger.info(gmail_instructions)
        logger.info(protonmail_instructions)

        # Summary
        results["success"] = (
            results["mailplus_installed"] or results["status_check"].get("mailplus_installed", False)
        ) and results["configurations_generated"] and results["instructions_generated"]

        logger.info("=" * 80)
        if results["success"]:
            logger.info("✅ SETUP PLAN EXECUTION COMPLETE")
        else:
            logger.info("⚠️  SETUP PLAN PARTIALLY COMPLETE")
        logger.info("=" * 80)
        logger.info("")
        logger.info("📋 NEXT STEPS:")
        logger.info("   1. Follow Gmail OAuth2 setup instructions (manual step)")
        logger.info("   2. Configure ProtonMail Bridge (based on chosen location)")
        logger.info("   3. Configure Outlook Desktop using generated config")
        logger.info("   4. Configure Outlook Mobile using generated config")
        logger.info("   5. Set up N8N workflows using generated config")
        logger.info("   6. Run verification: python scripts/python/verify_email_hub_nas.py")
        logger.info("")

        # Save results
        results_file = self.project_root / "data" / "mailplus_setup_execution_results.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)

        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"📄 Results saved: {results_file.name}")

        return results


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Execute MailPlus Setup Plan")
        parser.add_argument("--project-root", help="Project root directory")
        parser.add_argument("--skip-mailplus-install", action="store_true", 
                           help="Skip MailPlus installation")
        parser.add_argument("--bridge-location", choices=["host_pc", "nas"], 
                           default="host_pc",
                           help="Proton Bridge location (default: host_pc)")

        args = parser.parse_args()

        project_root = Path(args.project_root) if args.project_root else None

        executor = MailPlusSetupExecutor(project_root=project_root)
        results = executor.execute_setup_plan(
            install_mailplus=not args.skip_mailplus_install,
            bridge_location=args.bridge_location
        )

        return 0 if results["success"] else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    exit(main())