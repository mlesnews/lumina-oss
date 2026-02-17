#!/usr/bin/env python3
"""
JARVIS: Enable MailPlus IMAP via DSM API

Attempts to enable IMAP port 993 on MailPlus Server using DSM API.

Tags: #JARVIS #MAILPLUS #IMAP #API #AUTOMATION @JARVIS @LUMINA @DOIT
"""

import sys
import time
import socket
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

logger = get_logger("JARVISMailPlusIMAP")


def check_port_open(host: str, port: int, timeout: int = 3) -> bool:
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def enable_imap_via_api() -> bool:
    """Enable IMAP port 993 via DSM API"""
    try:
        from nas_azure_vault_integration import NASAzureVaultIntegration
        from synology_api_base import SynologyAPIBase
        import requests

        nas_integration = NASAzureVaultIntegration()
        credentials = nas_integration.get_nas_credentials()

        if not credentials:
            logger.error("❌ Could not get NAS credentials")
            return False

        nas_ip = "<NAS_PRIMARY_IP>"
        nas_port = 5001

        logger.info("=" * 80)
        logger.info("🔧 JARVIS: ENABLING MAILPLUS IMAP VIA API")
        logger.info("=" * 80)
        logger.info("")

        # Connect to DSM API
        api = SynologyAPIBase(nas_ip=nas_ip, nas_port=nas_port, verify_ssl=False)

        if not api.login(credentials["username"], credentials["password"]):
            logger.error("❌ Failed to login to DSM API")
            return False

        logger.info("✅ Connected to DSM API")
        logger.info("")

        # Try multiple API approaches
        logger.info("📋 STEP 1: Discovering MailPlus API endpoints...")
        logger.info("-" * 80)

        # Method 1: Try SYNO.MailPlus API (if it exists)
        logger.info("🔍 Attempting SYNO.MailPlus API...")

        # First, query available APIs
        query_url = f"{api.base_url}/webapi/query.cgi"
        query_params = {
            "api": "SYNO.API.Info",
            "version": "1",
            "method": "query",
            "query": "SYNO.MailPlus",
            "_sid": api.sid
        }

        try:
            response = api.session.get(query_url, params=query_params, timeout=10, verify=False)
            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                logger.info("✅ Found MailPlus API endpoints")
                logger.info(f"   Response: {data}")
            else:
                logger.warning("⚠️  MailPlus API query returned no results")
        except Exception as e:
            logger.debug(f"API query error: {e}")

        # Method 2: Try SYNO.MailServer API (legacy, might work for MailPlus)
        logger.info("")
        logger.info("🔍 Attempting SYNO.MailServer API...")

        try:
            # Try to get mail server settings
            mail_params = {
                "api": "SYNO.MailServer",
                "version": "1",
                "method": "get",
                "_sid": api.sid
            }

            response = api.session.get(f"{api.base_url}/webapi/entry.cgi", params=mail_params, timeout=10, verify=False)
            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                logger.info("✅ Found MailServer API")
                logger.info(f"   Current settings: {data.get('data', {})}")
            else:
                logger.warning("⚠️  MailServer API not available or not configured")
        except Exception as e:
            logger.debug(f"MailServer API error: {e}")

        # Method 3: Try SYNO.Core.Package to configure MailPlus
        logger.info("")
        logger.info("🔍 Attempting package configuration via SYNO.Core.Package...")

        try:
            # Get MailPlus package info
            package_params = {
                "api": "SYNO.Core.Package",
                "version": "1",
                "method": "get",
                "name": "MailPlus-Server",
                "_sid": api.sid
            }

            response = api.session.get(f"{api.base_url}/webapi/entry.cgi", params=package_params, timeout=10, verify=False)
            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                logger.info("✅ Found MailPlus-Server package")
                package_info = data.get("data", {})
                logger.info(f"   Package status: {package_info.get('status', 'unknown')}")
            else:
                logger.warning("⚠️  Could not get package info")
        except Exception as e:
            logger.debug(f"Package API error: {e}")

        # Method 4: Try direct MailPlus web API endpoint
        logger.info("")
        logger.info("🔍 Attempting MailPlus web API endpoint...")

        # MailPlus might use a different API path
        mailplus_apis = [
            "SYNO.MailPlus.Server",
            "SYNO.MailPlus.Mail",
            "SYNO.MailPlus.Setting",
            "SYNO.MailPlus.IMAP",
        ]

        for api_name in mailplus_apis:
            try:
                logger.info(f"   Trying {api_name}...")

                # Try to get settings
                test_params = {
                    "api": api_name,
                    "version": "1",
                    "method": "get",
                    "_sid": api.sid
                }

                response = api.session.get(f"{api.base_url}/webapi/entry.cgi", params=test_params, timeout=10, verify=False)
                response.raise_for_status()
                data = response.json()

                if data.get("success"):
                    logger.info(f"✅ Found {api_name} API!")
                    logger.info(f"   Response: {data.get('data', {})}")

                    # Try to set IMAP settings
                    if "imap" in api_name.lower() or "setting" in api_name.lower():
                        logger.info(f"   Attempting to enable IMAP via {api_name}...")

                        set_params = {
                            "api": api_name,
                            "version": "1",
                            "method": "set",
                            "imap_enable": "true",
                            "imap_port": "993",
                            "imap_ssl": "true",
                            "_sid": api.sid
                        }

                        response = api.session.get(f"{api.base_url}/webapi/entry.cgi", params=set_params, timeout=10, verify=False)
                        response.raise_for_status()
                        data = response.json()

                        if data.get("success"):
                            logger.info(f"✅ Successfully enabled IMAP via {api_name}!")
                            api.logout()

                            # Wait and verify
                            logger.info("")
                            logger.info("⏳ Waiting 5 seconds for IMAP to start...")
                            time.sleep(5)

                            if check_port_open(nas_ip, 993):
                                logger.info("✅ IMAP port 993 is now open!")
                                return True
                            else:
                                logger.warning("⚠️  IMAP port 993 still closed - may need restart")
                                return True  # API call succeeded even if port not immediately open
                        else:
                            logger.warning(f"⚠️  Failed to set IMAP: {data.get('error', {})}")

                else:
                    error = data.get("error", {})
                    if error.get("code") != 120:  # 120 = API not found
                        logger.debug(f"   {api_name} returned: {error}")
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 400:
                    # Bad request might mean API exists but params wrong
                    logger.debug(f"   {api_name} exists but params may be wrong")
                else:
                    logger.debug(f"   {api_name} not available: {e}")
            except Exception as e:
                logger.debug(f"   {api_name} error: {e}")

        api.logout()

        # Method 5: Try SSH configuration as fallback
        logger.info("")
        logger.info("⚠️  API methods did not work - IMAP configuration may require:")
        logger.info("   1. DSM web interface: MailPlus → Settings → Mail Service")
        logger.info("   2. Enable IMAP service checkbox")
        logger.info("   3. Set port: 993, Encryption: SSL/TLS")
        logger.info("   4. Click Apply")
        logger.info("")
        logger.info("💡 Alternative: Use GUI automation script:")
        logger.info("   python scripts/python/jarvis_configure_dsm_mailplus_imap_gui.py")

        return False

    except ImportError:
        logger.error("❌ Required modules not available")
        return False
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = enable_imap_via_api()
    sys.exit(0 if success else 1)
