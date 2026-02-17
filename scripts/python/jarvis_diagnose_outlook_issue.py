#!/usr/bin/env python3
"""
JARVIS: Diagnose Outlook Email Issue

Checks MailPlus account status and Outlook configuration to diagnose issues.

Tags: #JARVIS #OUTLOOK #MAILPLUS #DIAGNOSTIC @JARVIS @LUMINA
"""

import sys
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

logger = get_logger("JARVISDiagnoseOutlook")

ACCOUNT_EMAIL = "mlesn@<LOCAL_HOSTNAME>"
NAS_IP = "<NAS_PRIMARY_IP>"


def check_imap_port():
    """Check if IMAP port 993 is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((NAS_IP, 993))
        sock.close()
        return result == 0
    except Exception:
        return False


def check_smtp_port():
    """Check if SMTP port 587 is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((NAS_IP, 587))
        sock.close()
        return result == 0
    except Exception:
        return False


def check_mailplus_account():
    """Check if account exists in MailPlus"""
    try:
        from nas_azure_vault_integration import NASAzureVaultIntegration
        from synology_api_base import SynologyAPIBase

        nas_integration = NASAzureVaultIntegration()
        credentials = nas_integration.get_nas_credentials()

        if not credentials:
            return None, "Could not get NAS credentials"

        api = SynologyAPIBase(nas_ip=NAS_IP, nas_port=5001, verify_ssl=False)

        if not api.login(credentials["username"], credentials["password"]):
            return None, "Failed to login to DSM API"

        # Try to get account list
        accounts = api.api_call(
            api="SYNO.MailPlusServer.Account",
            method="list",
            version="1",
            require_auth=True
        )

        api.logout()

        if accounts:
            account_list = accounts.get('accounts', [])
            for acc in account_list:
                if acc.get('email', '').lower() == ACCOUNT_EMAIL.lower():
                    return acc, "Account found"
            return None, f"Account not found. Found {len(account_list)} account(s)"
        else:
            return None, "Could not retrieve account list"

    except Exception as e:
        return None, f"Error: {e}"


def diagnose():
    """Run full diagnosis"""
    logger.info("=" * 80)
    logger.info("🔍 JARVIS: DIAGNOSING OUTLOOK EMAIL ISSUE")
    logger.info("=" * 80)
    logger.info("")
    logger.info(f"Account: {ACCOUNT_EMAIL}")
    logger.info(f"NAS IP: {NAS_IP}")
    logger.info("")

    # Check 1: IMAP Port
    logger.info("📋 CHECK 1: IMAP Port 993")
    logger.info("-" * 80)
    imap_open = check_imap_port()
    if imap_open:
        logger.info("✅ IMAP port 993 is OPEN")
    else:
        logger.error("❌ IMAP port 993 is CLOSED")
        logger.info("   This is a critical issue - IMAP must be enabled in MailPlus")
    logger.info("")

    # Check 2: SMTP Port
    logger.info("📋 CHECK 2: SMTP Port 587")
    logger.info("-" * 80)
    smtp_open = check_smtp_port()
    if smtp_open:
        logger.info("✅ SMTP port 587 is OPEN")
    else:
        logger.warning("⚠️  SMTP port 587 is CLOSED")
        logger.info("   SMTP may use port 25 or 465 instead")
    logger.info("")

    # Check 3: MailPlus Account
    logger.info("📋 CHECK 3: MailPlus Account Existence")
    logger.info("-" * 80)
    account, message = check_mailplus_account()
    if account:
        logger.info(f"✅ {message}")
        logger.info(f"   Account details: {account}")
    else:
        logger.error(f"❌ {message}")
        logger.info("")
        logger.info("💡 SOLUTION: Create the account in MailPlus first")
        logger.info("   1. Login to DSM → MailPlus → Account")
        logger.info("   2. Click 'Create' or 'Add'")
        logger.info(f"   3. Email: {ACCOUNT_EMAIL}")
        logger.info("   4. Set password (can use NAS password)")
        logger.info("   5. Save the account")
    logger.info("")

    # Summary
    logger.info("=" * 80)
    logger.info("📊 DIAGNOSIS SUMMARY")
    logger.info("=" * 80)
    logger.info("")

    issues = []
    if not imap_open:
        issues.append("IMAP port 993 is closed")
    if not account:
        issues.append(f"Account {ACCOUNT_EMAIL} does not exist in MailPlus")

    if issues:
        logger.error("❌ ISSUES FOUND:")
        for issue in issues:
            logger.error(f"   - {issue}")
        logger.info("")
        logger.info("💡 RECOMMENDED ACTIONS:")
        if not account:
            logger.info("   1. CREATE ACCOUNT IN MAILPLUS (CRITICAL)")
            logger.info("      - DSM → MailPlus → Account → Create")
            logger.info(f"      - Email: {ACCOUNT_EMAIL}")
            logger.info("      - Password: (use NAS password or set new one)")
        if not imap_open:
            logger.info("   2. ENABLE IMAP IN MAILPLUS")
            logger.info("      - DSM → MailPlus → Settings → Mail Service")
            logger.info("      - Enable 'IMAP SSL/TLS' checkbox")
            logger.info("      - Port: 993")
            logger.info("      - Click Apply")
        logger.info("")
        logger.info("   3. After fixing, re-run Outlook setup:")
        logger.info("      python scripts/python/jarvis_complete_outlook_setup_with_password.py")
    else:
        logger.info("✅ All checks passed!")
        logger.info("")
        logger.info("💡 If Outlook still doesn't work:")
        logger.info("   1. Check Outlook account settings manually")
        logger.info("   2. Verify password is correct")
        logger.info("   3. Check Outlook error messages")
        logger.info("   4. Try removing and re-adding the account")

    return len(issues) == 0


if __name__ == "__main__":
    success = diagnose()
    sys.exit(0 if success else 1)
