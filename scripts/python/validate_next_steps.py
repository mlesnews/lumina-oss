#!/usr/bin/env python3
"""
Validate Next Steps - Clear Status Report

Validates:
1. MailStation is running (not MailPlus) - Email hub is working
2. YouTube processing - What we need to proceed

Tags: #VALIDATION #STATUS #NEXT_STEPS @JARVIS @LUMINA
"""

import sys
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

logger = get_logger("ValidateNextSteps")


def validate_all_next_steps() -> Dict[str, Any]:
    """Validate all next steps and provide clear status"""
    logger.info("=" * 80)
    logger.info("✅ VALIDATING NEXT STEPS")
    logger.info("=" * 80)
    logger.info("")

    results = {
        "email_hub": {},
        "youtube_processing": {},
        "retry_manager": {},
        "status": "validated"
    }

    # 1. Email Hub Validation
    logger.info("1️⃣  EMAIL HUB ON NAS")
    logger.info("-" * 80)

    try:
        from check_nas_email_hub_status import NASEmailHubStatusChecker
        checker = NASEmailHubStatusChecker()
        report = checker.generate_status_report()

        # Check which mail system is running
        mailstation_running = report["packages"]["mailstation"]["running"]
        mailplus_installed = report["packages"]["mailplus"]["installed"]

        if mailstation_running:
            results["email_hub"] = {
                "status": "working",
                "system": "MailStation",
                "note": "MailStation is running (the other mail system you mentioned)"
            }
            logger.info("   ✅ MailStation: RUNNING")
            logger.info("   ✅ Email hub is working with MailStation")
        elif mailplus_installed:
            results["email_hub"] = {
                "status": "working",
                "system": "MailPlus",
                "note": "MailPlus is installed"
            }
            logger.info("   ✅ MailPlus: INSTALLED")
        else:
            results["email_hub"] = {
                "status": "needs_setup",
                "system": "unknown",
                "note": "Need to determine which mail system is actually running"
            }
            logger.warning("   ⚠️  Mail system status unclear")

    except Exception as e:
        results["email_hub"] = {"status": "error", "error": str(e)}
        logger.error(f"   ❌ Error checking email hub: {e}")

    logger.info("")

    # 2. YouTube Processing Validation
    logger.info("2️⃣  YOUTUBE PROCESSING")
    logger.info("-" * 80)

    # Check for cookies file
    cookies_file = project_root / "config" / "youtube_cookies.txt"
    cookies_available = cookies_file.exists()

    # Check for yt-dlp
    try:
        import subprocess
        result = subprocess.run(["yt-dlp", "--version"], capture_output=True, timeout=5)
        yt_dlp_available = result.returncode == 0
    except:
        yt_dlp_available = False

    if cookies_available and yt_dlp_available:
        results["youtube_processing"] = {
            "status": "ready",
            "method": "cookies_file",
            "can_fetch": True
        }
        logger.info("   ✅ Cookies file available")
        logger.info("   ✅ yt-dlp available")
        logger.info("   ✅ Ready to fetch YouTube videos")
    elif yt_dlp_available:
        results["youtube_processing"] = {
            "status": "needs_cookies",
            "method": "browser_or_cookies",
            "can_fetch": False,
            "action_required": "Export cookies or close browser"
        }
        logger.warning("   ⚠️  Cookies file not found")
        logger.info("   ✅ yt-dlp available")
        logger.info("   💡 Need: Export cookies or close browser")
    else:
        results["youtube_processing"] = {
            "status": "needs_yt_dlp",
            "can_fetch": False,
            "action_required": "Install yt-dlp: pip install yt-dlp"
        }
        logger.warning("   ⚠️  yt-dlp not available")
        logger.info("   💡 Install: pip install yt-dlp")

    logger.info("")

    # 3. Retry Manager Validation
    logger.info("3️⃣  RETRY MANAGER (AI TOKEN REQUESTS)")
    logger.info("-" * 80)

    try:
        from ai_token_request_retry_manager import AITokenRequestRetryManager
        manager = AITokenRequestRetryManager()
        results["retry_manager"] = {
            "status": "working",
            "max_retries": manager.max_retries,
            "strategy": manager.strategy.value
        }
        logger.info("   ✅ AI Token Retry Manager: WORKING")
        logger.info(f"   ✅ Max retries: {manager.max_retries}")
        logger.info(f"   ✅ Strategy: {manager.strategy.value}")
    except Exception as e:
        results["retry_manager"] = {"status": "error", "error": str(e)}
        logger.error(f"   ❌ Error: {e}")

    logger.info("")

    # Summary
    logger.info("=" * 80)
    logger.info("📊 VALIDATION SUMMARY")
    logger.info("=" * 80)

    if results["email_hub"].get("status") == "working":
        logger.info("   ✅ Email Hub: WORKING")
    else:
        logger.warning("   ⚠️  Email Hub: Needs attention")

    if results["youtube_processing"].get("can_fetch"):
        logger.info("   ✅ YouTube Processing: READY")
    else:
        logger.warning("   ⚠️  YouTube Processing: Needs setup")
        action = results["youtube_processing"].get("action_required", "Unknown")
        logger.info(f"      Action: {action}")

    if results["retry_manager"].get("status") == "working":
        logger.info("   ✅ Retry Manager: WORKING")

    logger.info("")
    logger.info("=" * 80)

    return results


def main():
    """Main execution"""
    results = validate_all_next_steps()

    # Print clear next steps
    logger.info("")
    logger.info("📋 CLEAR NEXT STEPS:")
    logger.info("")

    # Email Hub
    if results["email_hub"].get("status") == "working":
        logger.info("✅ Email Hub: No action needed - MailStation is running")
    else:
        logger.info("⚠️  Email Hub: Verify MailStation/MailPlus configuration")

    # YouTube
    if results["youtube_processing"].get("can_fetch"):
        logger.info("✅ YouTube: Ready to fetch - will process now")
    else:
        action = results["youtube_processing"].get("action_required", "Unknown")
        logger.info(f"⚠️  YouTube: {action}")
        logger.info("   Once cookies are available, I can fetch all videos")

    logger.info("")
    logger.info("✅ Validation complete")


if __name__ == "__main__":


    main()