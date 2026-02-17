#!/usr/bin/env python3
"""
Verify Complete Email Setup
Comprehensive verification of MailStation, Proton Bridge, and credential management.

Tags: #EMAIL #VERIFICATION #MAILSTATION #PROTONBRIDGE
@JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
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
    # Try importing from same directory
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "get_proton_bridge_credentials",
        Path(__file__).parent / "get_proton_bridge_credentials.py"
    )
    if spec and spec.loader:
        get_proton_bridge_credentials = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(get_proton_bridge_credentials)
        # Check for the class (it's ProtonBridgeCredentialManager)
        if hasattr(get_proton_bridge_credentials, 'ProtonBridgeCredentialManager'):
            GetProtonBridgeCredentials = get_proton_bridge_credentials.ProtonBridgeCredentialManager
            CREDENTIALS_AVAILABLE = True
        else:
            CREDENTIALS_AVAILABLE = False
            GetProtonBridgeCredentials = None
    else:
        CREDENTIALS_AVAILABLE = False
        GetProtonBridgeCredentials = None
except Exception:
    CREDENTIALS_AVAILABLE = False
    GetProtonBridgeCredentials = None

try:
    import socket
    SOCKET_AVAILABLE = True
except ImportError:
    SOCKET_AVAILABLE = False

logger = get_logger("VerifyEmailSetup")


class EmailSetupVerifier:
    """Verify complete email setup"""

    def __init__(self):
        """Initialize verifier"""
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "mailstation": {},
            "proton_bridge": {},
            "credentials": {},
            "outlook": {},
            "n8n": {},
            "summary": {}
        }

        self.credential_manager = None
        if CREDENTIALS_AVAILABLE:
            try:
                self.credential_manager = GetProtonBridgeCredentials()
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize credential manager: {e}")

    def check_port(self, host: str, port: int, timeout: int = 3) -> bool:
        """Check if port is open"""
        if not SOCKET_AVAILABLE:
            return False

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception as e:
            logger.debug(f"Port check error for {host}:{port}: {e}")
            return False

    def verify_mailstation(self) -> Dict[str, Any]:
        """Verify MailStation configuration"""
        logger.info("=" * 80)
        logger.info("📧 VERIFYING MAILSTATION")
        logger.info("=" * 80)

        result = {
            "server": "<NAS_PRIMARY_IP>",
            "imap_port": 993,
            "smtp_port": 25,
            "domain": "<LOCAL_HOSTNAME>",
            "imap_accessible": False,
            "smtp_accessible": False,
            "status": "unknown"
        }

        # Check IMAP port
        logger.info(f"🔍 Checking IMAP port {result['imap_port']}...")
        result["imap_accessible"] = self.check_port(result["server"], result["imap_port"])
        if result["imap_accessible"]:
            logger.info(f"✅ IMAP port {result['imap_port']} is open")
        else:
            logger.warning(f"❌ IMAP port {result['imap_port']} is closed")

        # Check SMTP port
        logger.info(f"🔍 Checking SMTP port {result['smtp_port']}...")
        result["smtp_accessible"] = self.check_port(result["server"], result["smtp_port"])
        if result["smtp_accessible"]:
            logger.info(f"✅ SMTP port {result['smtp_port']} is open")
        else:
            logger.warning(f"❌ SMTP port {result['smtp_port']} is closed")

        # Determine status
        if result["imap_accessible"] and result["smtp_accessible"]:
            result["status"] = "operational"
            logger.info("✅ MailStation is operational")
        elif result["imap_accessible"] or result["smtp_accessible"]:
            result["status"] = "partial"
            logger.warning("⚠️  MailStation is partially accessible")
        else:
            result["status"] = "inaccessible"
            logger.error("❌ MailStation is not accessible")

        logger.info("")
        return result

    def verify_proton_bridge_credentials(self, account_name: str = "mlesn") -> Dict[str, Any]:
        """Verify Proton Bridge credentials"""
        logger.info("=" * 80)
        logger.info(f"🔐 VERIFYING PROTON BRIDGE CREDENTIALS ({account_name})")
        logger.info("=" * 80)

        result = {
            "account_name": account_name,
            "username_retrieved": False,
            "password_retrieved": False,
            "username_source": None,
            "password_source": None,
            "username": None,
            "password_length": None,
            "status": "unknown"
        }

        if not self.credential_manager:
            logger.error("❌ Credential manager not available")
            result["status"] = "error"
            return result

        try:
            # Get username
            logger.info(f"👤 Retrieving username for {account_name}...")
            username = self.credential_manager.get_bridge_username(account_name)
            if username:
                result["username_retrieved"] = True
                result["username"] = username
                result["username_source"] = "retrieved"
                logger.info(f"✅ Username retrieved: {username[:3]}***")
            else:
                logger.warning("⚠️  Username not retrieved")

            # Get password
            logger.info(f"🔐 Retrieving password for {account_name}...")
            password = self.credential_manager.get_bridge_password(account_name)
            if password:
                result["password_retrieved"] = True
                result["password_available"] = True
                result["password_source"] = "retrieved"
                logger.info(f"✅ Password retrieved [REDACTED]")
            else:
                logger.warning("⚠️  Password not retrieved")

            # Determine status
            if result["username_retrieved"] and result["password_retrieved"]:
                result["status"] = "complete"
                logger.info("✅ Credentials are complete")
            elif result["username_retrieved"] or result["password_retrieved"]:
                result["status"] = "partial"
                logger.warning("⚠️  Credentials are partial")
            else:
                result["status"] = "missing"
                logger.error("❌ Credentials are missing")

        except Exception as e:
            logger.error(f"❌ Error verifying credentials: {e}")
            result["status"] = "error"

        logger.info("")
        return result

    def verify_config_files(self) -> Dict[str, Any]:
        """Verify configuration files exist and are valid"""
        logger.info("=" * 80)
        logger.info("📄 VERIFYING CONFIGURATION FILES")
        logger.info("=" * 80)

        result = {
            "files": {},
            "all_valid": True
        }

        config_files = [
            "config/email_accounts_aggregation.json",
            "config/proton_bridge_config.json",
            "config/proton_bridge_accounts.json",
            "config/outlook/mailstation_outlook_config.json",
            "config/n8n/proton_bridge_workflow.json"
        ]

        base_path = Path(__file__).parent.parent.parent

        for config_file in config_files:
            file_path = base_path / config_file
            file_result = {
                "exists": file_path.exists(),
                "valid_json": False,
                "size": 0
            }

            if file_path.exists():
                file_result["size"] = file_path.stat().st_size
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        json.load(f)
                    file_result["valid_json"] = True
                    logger.info(f"✅ {config_file} - Valid JSON ({file_result['size']} bytes)")
                except json.JSONDecodeError:
                    logger.warning(f"⚠️  {config_file} - Invalid JSON")
                    result["all_valid"] = False
                except Exception as e:
                    logger.error(f"❌ {config_file} - Error: {e}")
                    result["all_valid"] = False
            else:
                logger.warning(f"⚠️  {config_file} - Not found")
                result["all_valid"] = False

            result["files"][config_file] = file_result

        logger.info("")
        return result

    def generate_summary(self) -> Dict[str, Any]:
        """Generate verification summary"""
        logger.info("=" * 80)
        logger.info("📊 VERIFICATION SUMMARY")
        logger.info("=" * 80)

        summary = {
            "overall_status": "unknown",
            "components": {},
            "recommendations": []
        }

        # MailStation status
        mailstation = self.results.get("mailstation", {})
        if mailstation.get("status") == "operational":
            summary["components"]["mailstation"] = "✅ Operational"
        elif mailstation.get("status") == "partial":
            summary["components"]["mailstation"] = "⚠️  Partial"
            summary["recommendations"].append("Check MailStation port configuration")
        else:
            summary["components"]["mailstation"] = "❌ Inaccessible"
            summary["recommendations"].append("Verify MailStation is running and accessible")

        # Credentials status
        credentials = self.results.get("credentials", {})
        if credentials.get("status") == "complete":
            summary["components"]["credentials"] = "✅ Complete"
        elif credentials.get("status") == "partial":
            summary["components"]["credentials"] = "⚠️  Partial"
            summary["recommendations"].append("Verify credential storage (ProtonPassCli or Azure Vault)")
        else:
            summary["components"]["credentials"] = "❌ Missing"
            summary["recommendations"].append("Store credentials using: python scripts/python/get_proton_bridge_credentials.py --store")

        # Config files
        configs = self.results.get("config_files", {})
        if configs.get("all_valid"):
            summary["components"]["config_files"] = "✅ All Valid"
        else:
            summary["components"]["config_files"] = "⚠️  Some Issues"
            summary["recommendations"].append("Review configuration files")

        # Overall status
        if all("✅" in str(v) for v in summary["components"].values()):
            summary["overall_status"] = "✅ Ready"
        elif any("❌" in str(v) for v in summary["components"].values()):
            summary["overall_status"] = "❌ Issues Found"
        else:
            summary["overall_status"] = "⚠️  Needs Attention"

        # Log summary
        logger.info(f"Overall Status: {summary['overall_status']}")
        logger.info("")
        logger.info("Components:")
        for component, status in summary["components"].items():
            logger.info(f"  {component}: {status}")

        if summary["recommendations"]:
            logger.info("")
            logger.info("Recommendations:")
            for i, rec in enumerate(summary["recommendations"], 1):
                logger.info(f"  {i}. {rec}")

        logger.info("=" * 80)

        return summary

    def verify_all(self) -> Dict[str, Any]:
        """Run all verifications"""
        logger.info("")
        logger.info("=" * 80)
        logger.info("🔍 COMPLETE EMAIL SETUP VERIFICATION")
        logger.info("=" * 80)
        logger.info("")

        # Verify MailStation
        self.results["mailstation"] = self.verify_mailstation()

        # Verify credentials for both accounts
        self.results["credentials"] = {
            "mlesn": self.verify_proton_bridge_credentials("mlesn"),
            "glesn": self.verify_proton_bridge_credentials("glesn")
        }

        # Verify config files
        self.results["config_files"] = self.verify_config_files()

        # Generate summary
        self.results["summary"] = self.generate_summary()

        return self.results


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Verify Complete Email Setup")
        parser.add_argument("--json", action="store_true", help="Output as JSON")
        parser.add_argument("--save", type=str, help="Save results to file")

        args = parser.parse_args()

        verifier = EmailSetupVerifier()
        results = verifier.verify_all()

        if args.save:
            output_path = Path(args.save)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Results saved to: {output_path}")

        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))

        # Return exit code based on overall status
        overall_status = results.get("summary", {}).get("overall_status", "unknown")
        if "✅" in overall_status:
            return 0
        elif "❌" in overall_status:
            return 1
        else:
            return 2


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    exit(main())