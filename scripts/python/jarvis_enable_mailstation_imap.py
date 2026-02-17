#!/usr/bin/env python3
"""
JARVIS Enable MailStation IMAP via DSM API

Uses Synology DSM API to enable IMAP port 993 on MailStation.

Tags: #JARVIS #MAILSTATION #IMAP #DSM_API #AUTOMATION
@JARVIS @LUMINA @DOIT
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from synology_api_base import SynologyAPIBase
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False

try:
    from nas_azure_vault_integration import NASAzureVaultIntegration
    VAULT_AVAILABLE = True
except ImportError:
    VAULT_AVAILABLE = False

logger = get_logger("JARVISEnableIMAP")


def enable_imap_via_dsm_api() -> Dict[str, Any]:
    """Enable IMAP port 993 via DSM API"""
    logger.info("=" * 80)
    logger.info("🤖 JARVIS ENABLING MAILSTATION IMAP VIA DSM API")
    logger.info("=" * 80)
    logger.info("")

    result = {
        "success": False,
        "method": None,
        "error": None
    }

    if not API_AVAILABLE:
        logger.error("❌ Synology API not available")
        result["error"] = "Synology API not available"
        return result

    if not VAULT_AVAILABLE:
        logger.error("❌ Azure Vault integration not available")
        result["error"] = "Azure Vault not available"
        return result

    # Get credentials
    nas_integration = NASAzureVaultIntegration()
    credentials = nas_integration.get_nas_credentials()

    if not credentials:
        logger.error("❌ Could not retrieve NAS credentials")
        result["error"] = "Credentials not available"
        return result

    # Connect to DSM API
    try:
        api = SynologyAPIBase(nas_ip="<NAS_PRIMARY_IP>", nas_port=5001, verify_ssl=False)

        if not api.login(credentials["username"], credentials["password"]):
            logger.error("❌ Failed to login to DSM API")
            result["error"] = "DSM API login failed"
            return result

        logger.info("✅ Connected to DSM API")

        # Try MailStation package API
        # Note: MailStation API endpoints may vary by DSM version
        logger.info("⚙️  Attempting to configure MailStation IMAP...")

        # Method 1: Try MailStation package API
        mailstation_url = f"{api.base_url}/webapi/entry.cgi"

        # Common MailStation API endpoints (may need adjustment)
        endpoints_to_try = [
            {
                "api": "SYNO.MailStation.MailService",
                "version": "1",
                "method": "set",
                "params": {
                    "imap_enable": "true",
                    "imap_port": "993",
                    "imap_ssl": "true"
                }
            },
            {
                "api": "SYNO.MailStation.Setting",
                "version": "1",
                "method": "set",
                "params": {
                    "imap_enable": "true",
                    "imap_port": "993"
                }
            }
        ]

        for endpoint in endpoints_to_try:
            try:
                params = {
                    "api": endpoint["api"],
                    "version": endpoint["version"],
                    "method": endpoint["method"],
                    "_sid": api.sid,
                    **endpoint["params"]
                }

                response = api.session.get(mailstation_url, params=params, timeout=10)
                data = response.json()

                if data.get("success"):
                    logger.info(f"✅ IMAP enabled via {endpoint['api']}")
                    result["success"] = True
                    result["method"] = endpoint["api"]
                    api.logout()
                    return result
                else:
                    logger.debug(f"   {endpoint['api']} returned: {data.get('error', {})}")
            except Exception as e:
                logger.debug(f"   {endpoint['api']} failed: {e}")
                continue

        # Method 2: Try generic package API
        logger.info("   Trying generic package API...")
        package_url = f"{api.base_url}/webapi/entry.cgi"

        package_params = {
            "api": "SYNO.Core.Package",
            "version": "1",
            "method": "get",
            "package": "MailStation",
            "_sid": api.sid
        }

        try:
            response = api.session.get(package_url, params=package_params, timeout=10)
            data = response.json()

            if data.get("success"):
                logger.info("✅ MailStation package found")
                # Could try to configure via package settings
            else:
                logger.debug(f"   Package API returned: {data.get('error', {})}")
        except Exception as e:
            logger.debug(f"   Package API failed: {e}")

        api.logout()

        # If API methods don't work, provide instructions
        logger.warning("⚠️  Could not enable IMAP via DSM API")
        logger.info("")
        logger.info("💡 Manual Configuration Required:")
        logger.info("   1. Access DSM web interface: https://<NAS_PRIMARY_IP>:5001")
        logger.info("   2. Navigate to: MailStation → Settings → Mail Service")
        logger.info("   3. Enable IMAP service")
        logger.info("   4. Set IMAP port to 993 (SSL/TLS)")
        logger.info("   5. Save settings")
        logger.info("")
        logger.info("   Or use SSH to edit MailStation configuration files")

        result["error"] = "DSM API methods not available - manual configuration required"
        return result

    except Exception as e:
        logger.error(f"❌ DSM API error: {e}")
        result["error"] = str(e)
        return result


def main():
    """Main entry point"""
    result = enable_imap_via_dsm_api()

    if result["success"]:
        logger.info("")
        logger.info("✅ IMAP port 993 enabled successfully!")
        return 0
    else:
        logger.info("")
        logger.info("⚠️  IMAP configuration requires manual intervention")
        logger.info("   See instructions above")
        return 1


if __name__ == "__main__":


    sys.exit(main())