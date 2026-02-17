#!/usr/bin/env python3
"""
JARVIS: Enable MailPlus IMAP via DSM API

Uses SYNO.MailPlusServer.IMAP_POP3 API to enable IMAP port 993.

Tags: #JARVIS #MAILPLUS #IMAP #API #AUTOMATION @JARVIS @LUMINA @DOIT
"""

import sys
import time
import socket
from pathlib import Path
from typing import Dict, Any

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

logger = get_logger("JARVISMailPlusIMAPAPI")


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
    """Enable IMAP port 993 via SYNO.MailPlusServer.IMAP_POP3 API"""
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

        # Step 1: Get current IMAP/POP3 settings
        logger.info("📋 STEP 1: Getting current IMAP/POP3 settings...")
        logger.info("-" * 80)

        current_settings = api.api_call(
            api="SYNO.MailPlusServer.IMAP_POP3",
            method="get",
            version="1",
            require_auth=True
        )

        if current_settings:
            logger.info("✅ Retrieved current settings:")
            logger.info(f"   {current_settings}")
        else:
            logger.warning("⚠️  Could not retrieve current settings, proceeding anyway...")

        logger.info("")

        # Step 2: Enable IMAP
        logger.info("📋 STEP 2: Enabling IMAP service...")
        logger.info("-" * 80)

        # Prepare settings to enable IMAP
        # Based on current settings, use enable_imaps (IMAP with SSL on port 993)
        imap_settings = {
            "enable_imaps": True,  # IMAP with SSL (port 993)
            "enable_imap": False,  # Keep non-SSL IMAP disabled
            "enable_pop3": False,  # Keep POP3 disabled
            "enable_pop3s": False,  # Keep POP3S disabled
            "security_imappop3_auth": True  # Keep security enabled
        }

        logger.info("   Configuring IMAP:")
        logger.info(f"   - Enable IMAPS (SSL): {imap_settings['enable_imaps']}")
        logger.info(f"   - Port: 993 (default for IMAPS)")
        logger.info(f"   - Security Auth: {imap_settings['security_imappop3_auth']}")
        logger.info("")

        # Try to set IMAP settings
        set_result = api.api_call(
            api="SYNO.MailPlusServer.IMAP_POP3",
            method="set",
            version="1",
            params=imap_settings,
            require_auth=True
        )

        if set_result:
            logger.info("✅ IMAP settings updated successfully!")
            logger.info(f"   Response: {set_result}")
        else:
            logger.warning("⚠️  Could not set IMAP via API")
            logger.info("   Error code 5594 may indicate missing parameters or permission issue")
            logger.info("   Trying with all current settings preserved...")

            # Try with all current settings plus enable_imaps
            if current_settings:
                full_settings = current_settings.copy()
                full_settings["enable_imaps"] = True

                set_result = api.api_call(
                    api="SYNO.MailPlusServer.IMAP_POP3",
                    method="set",
                    version="1",
                    params=full_settings,
                    require_auth=True
                )

                if set_result:
                    logger.info("✅ IMAP settings updated successfully!")
                else:
                    logger.warning("⚠️  API call failed - may require GUI interface")
                    api.logout()
                    return False
            else:
                logger.warning("⚠️  Could not set IMAP via API")
                logger.info("   This may require the GUI interface")
                api.logout()
                return False

        api.logout()

        # Step 3: Verify IMAP port is open
        logger.info("")
        logger.info("📋 STEP 3: Verifying IMAP port 993...")
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
            logger.info("")
            logger.info("💡 Try checking the port again in a few seconds:")
            logger.info(f"   python -c \"import socket; print('Open' if socket.socket().connect_ex(('{nas_ip}', 993)) == 0 else 'Closed')\"")
            return True  # API call succeeded even if port not immediately open

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
