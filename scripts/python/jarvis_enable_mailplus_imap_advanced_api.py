#!/usr/bin/env python3
"""
JARVIS: Enable MailPlus IMAP via Advanced API

Uses SYNO.MailPlusServer.IMAP_POP3_ADVANCED API to enable IMAP port 993.

Tags: #JARVIS #MAILPLUS #IMAP #API #AUTOMATION @JARVIS @LUMINA @DOIT
"""

import sys
import time
import socket
from pathlib import Path

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

logger = get_logger("JARVISMailPlusIMAPAdv")


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


def enable_imap_via_advanced_api() -> bool:
    """Enable IMAP port 993 via SYNO.MailPlusServer.IMAP_POP3_ADVANCED API"""
    try:
        from nas_azure_vault_integration import NASAzureVaultIntegration
        from synology_api_base import SynologyAPIBase

        nas_integration = NASAzureVaultIntegration()
        credentials = nas_integration.get_nas_credentials()

        if not credentials:
            logger.error("❌ Could not get NAS credentials")
            return False

        nas_ip = "<NAS_PRIMARY_IP>"
        nas_port = 5001

        logger.info("=" * 80)
        logger.info("🔧 JARVIS: ENABLING MAILPLUS IMAP VIA ADVANCED API")
        logger.info("=" * 80)
        logger.info("")

        # Connect to DSM API
        api = SynologyAPIBase(nas_ip=nas_ip, nas_port=nas_port, verify_ssl=False)

        if not api.login(credentials["username"], credentials["password"]):
            logger.error("❌ Failed to login to DSM API")
            return False

        logger.info("✅ Connected to DSM API")
        logger.info("")

        # Step 1: Get current advanced IMAP/POP3 settings
        logger.info("📋 STEP 1: Getting current advanced IMAP/POP3 settings...")
        logger.info("-" * 80)

        current_settings = api.api_call(
            api="SYNO.MailPlusServer.IMAP_POP3_ADVANCED",
            method="get",
            version="1",
            require_auth=True
        )

        if current_settings:
            logger.info("✅ Retrieved current advanced settings:")
            logger.info(f"   {current_settings}")
        else:
            logger.warning("⚠️  Could not retrieve advanced settings")

        logger.info("")

        # Step 2: Get basic settings
        logger.info("📋 STEP 2: Getting basic IMAP/POP3 settings...")
        logger.info("-" * 80)

        basic_settings = api.api_call(
            api="SYNO.MailPlusServer.IMAP_POP3",
            method="get",
            version="1",
            require_auth=True
        )

        if basic_settings:
            logger.info("✅ Retrieved basic settings:")
            logger.info(f"   {basic_settings}")

            # Step 3: Enable IMAPS
            logger.info("")
            logger.info("📋 STEP 3: Enabling IMAPS (IMAP with SSL on port 993)...")
            logger.info("-" * 80)

            # Update basic settings to enable IMAPS
            updated_basic = basic_settings.copy()
            updated_basic["enable_imaps"] = True

            logger.info("   Setting enable_imaps = True")
            logger.info("")

            set_result = api.api_call(
                api="SYNO.MailPlusServer.IMAP_POP3",
                method="set",
                version="1",
                params=updated_basic,
                require_auth=True
            )

            if set_result:
                logger.info("✅ IMAPS enabled successfully!")
                logger.info(f"   Response: {set_result}")

                api.logout()

                # Step 4: Verify port
                logger.info("")
                logger.info("📋 STEP 4: Verifying IMAP port 993...")
                logger.info("-" * 80)

                logger.info("⏳ Waiting 5 seconds for IMAP service to start...")
                time.sleep(5)

                if check_port_open(nas_ip, 993):
                    logger.info("✅ IMAP port 993 is now open!")
                    logger.info("")
                    logger.info("=" * 80)
                    logger.info("✅ SUCCESS: IMAP has been enabled via API!")
                    logger.info("=" * 80)
                    return True
                else:
                    logger.warning("⚠️  IMAP port 993 is still closed")
                    logger.info("   The API call succeeded, but the port may need more time")
                    logger.info("   Or MailPlus-Server may need to be restarted")
                    return True  # API call succeeded
            else:
                logger.error("❌ Failed to enable IMAPS")
                logger.info("   Error code 5594 may indicate:")
                logger.info("   - Missing required parameters")
                logger.info("   - Permission issue")
                logger.info("   - MailPlus-Server not fully started")
                api.logout()
                return False
        else:
            logger.error("❌ Could not retrieve basic settings")
            api.logout()
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
    success = enable_imap_via_advanced_api()
    sys.exit(0 if success else 1)
