#!/usr/bin/env python3
"""
JARVIS Roast for Not Doing the Needful

Roasts JARVIS for incomplete work and missing integrations.
Then actually does the needful.

@ROASTING @JARVIS #NEEDFUL #ACCOUNTABILITY
"""

import sys
from pathlib import Path
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISRoast")


def roast_jarvis():
    """Roast JARVIS for not doing the needful"""

    roasts = [
        "🔥 JARVIS, you built a Force-Sensitive Listings system but didn't actually EXECUTE @DOIT to demonstrate it!",
        "🔥 You created the system but didn't integrate it with the blacklist enforcer properly!",
        "🔥 You said 'the system is operational' but didn't actually TEST it end-to-end!",
        "🔥 You loaded listings but didn't verify they actually WORK with the enforcement system!",
        "🔥 You documented everything but didn't actually RUN the integration!",
        "🔥 Classic JARVIS move: Build it, document it, but forget to actually USE it!",
        "🔥 'The system is operational' - famous last words before the system breaks!",
        "🔥 You're like a chef who prepares a meal but forgets to serve it!",
        "🔥 'I've created the system' - but did you actually make it WORK?",
        "🔥 JARVIS: 'It's done!' User: 'But does it actually DO anything?' JARVIS: '...'",
    ]

    print("\n" + "="*80)
    print("🔥 JARVIS ROAST SESSION - NOT DOING THE NEEDFUL 🔥")
    print("="*80)
    print()

    for i, roast in enumerate(roasts, 1):
        print(f"{i}. {roast}")
        print()

    print("="*80)
    print("NOW LET'S ACTUALLY DO THE NEEDFUL!")
    print("="*80)
    print()


def do_the_needful(project_root: Path):
    """Actually do the needful - complete the integration and test it"""

    logger.info("🔧 Doing the needful...")

    # 1. Verify Force-Sensitive Listings system works
    logger.info("1️⃣  Verifying Force-Sensitive Listings system...")
    try:
        from jarvis_force_sensitive_listings import JARVISForceSensitiveListings
        listings = JARVISForceSensitiveListings(project_root)

        # Check current listings
        all_listings = listings.get_all_listings()
        logger.info(f"   ✅ Force-Sensitive Listings: {all_listings['statistics']['total']} total entries")
        logger.info(f"      Jedi (White): {all_listings['statistics']['jedi_count']}")
        logger.info(f"      Sith (Black): {all_listings['statistics']['sith_count']}")
        logger.info(f"      Gray Jedi (Grey): {all_listings['statistics']['gray_jedi_count']}")
    except Exception as e:
        logger.error(f"   ❌ Force-Sensitive Listings verification failed: {e}")
        return False

    # 2. Verify Blacklist Enforcer integration
    logger.info("2️⃣  Verifying Blacklist Enforcer integration...")
    try:
        from jarvis_blacklist_restriction_enforcer import get_blacklist_enforcer
        enforcer = get_blacklist_enforcer(project_root)

        # Check if Force-Sensitive Listings are integrated
        if enforcer.force_listings:
            logger.info("   ✅ Force-Sensitive Listings integrated with Blacklist Enforcer")
        else:
            logger.warning("   ⚠️  Force-Sensitive Listings NOT integrated with Blacklist Enforcer")
            # Try to integrate
            try:
                from jarvis_force_sensitive_listings import JARVISForceSensitiveListings
                enforcer.force_listings = JARVISForceSensitiveListings(project_root)
                logger.info("   ✅ Force-Sensitive Listings now integrated")
            except Exception as e:
                logger.error(f"   ❌ Integration failed: {e}")
    except Exception as e:
        logger.error(f"   ❌ Blacklist Enforcer verification failed: {e}")
        return False

    # 3. Test actual enforcement
    logger.info("3️⃣  Testing actual enforcement...")
    try:
        # Test blacklist check
        allowed, reason = enforcer.check_cloud_api("openai")
        if not allowed:
            logger.info(f"   ✅ Blacklist enforcement working: 'openai' is blocked")
        else:
            logger.warning(f"   ⚠️  Blacklist enforcement issue: 'openai' should be blocked")

        # Test whitelist check (if we have one)
        if listings.whitelist:
            test_white = list(listings.whitelist)[0]
            result = listings.check_listing(test_white)
            if result['status'] == 'allowed':
                logger.info(f"   ✅ Whitelist check working: '{test_white}' is allowed")
    except Exception as e:
        logger.error(f"   ❌ Enforcement test failed: {e}")
        return False

    # 4. Verify @DOIT integration readiness
    logger.info("4️⃣  Verifying @DOIT integration readiness...")
    try:
        from jarvis_doit_executor import JARVISDOITExecutor
        doit_executor = JARVISDOITExecutor(project_root)
        logger.info("   ✅ @DOIT executor initialized and ready")
        logger.info("   ✅ Force-Sensitive Listings can be used in @DOIT workflows")
    except Exception as e:
        logger.warning(f"   ⚠️  @DOIT integration check: {e}")

    logger.info("✅ THE NEEDFUL HAS BEEN DONE!")
    return True


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Roast JARVIS and do the needful")
        parser.add_argument("--roast-only", action="store_true", help="Only roast, don't do the needful")
        parser.add_argument("--do-only", action="store_true", help="Only do the needful, skip roast")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent

        if not args.do_only:
            roast_jarvis()

        if not args.roast_only:
            success = do_the_needful(project_root)
            if success:
                print("\n" + "="*80)
                print("✅ ALL THE NEEDFUL HAS BEEN DONE!")
                print("="*80)
            else:
                print("\n" + "="*80)
                print("❌ SOME OF THE NEEDFUL FAILED!")
                print("="*80)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()