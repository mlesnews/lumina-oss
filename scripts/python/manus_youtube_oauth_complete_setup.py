#!/usr/bin/env python3
"""
@MANUS Complete YouTube OAuth & SYPHON Setup

Complete workflow:
1. @MANUS handles OAuth setup
2. @MARVIN identifies roadblocks
3. JARVIS builds solutions
4. Complete SYPHON of YouTube account data
5. Generate affiliate baseline
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ManusYouTubeOAuthCompleteSetup")

from manus_youtube_oauth_setup import ManusYouTubeOAuthSetup
from syphon_youtube_account_data import YouTubeAccountSyphon
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class ManusYouTubeOAuthCompleteSetup:
    """
    Complete @MANUS YouTube OAuth & SYPHON Setup

    Orchestrates the full workflow with @MARVIN & JARVIS support
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(".").resolve()
        self.logger = get_logger("ManusYouTubeOAuthCompleteSetup")

        # Initialize @MANUS OAuth setup
        self.oauth_setup = ManusYouTubeOAuthSetup(project_root)

        # Initialize YouTube Account SYPHON
        self.account_syphon = YouTubeAccountSyphon(project_root)

        self.logger.info("🔧 @MANUS Complete YouTube OAuth & SYPHON Setup")
        self.logger.info("   @MANUS: OAuth setup")
        self.logger.info("   @MARVIN: Roadblock analysis")
        self.logger.info("   JARVIS: Solution building")
        self.logger.info("   SYPHON: Account data extraction")

    def execute_complete_setup(self) -> Dict[str, Any]:
        """Execute complete setup workflow"""
        self.logger.info("\n" + "="*80)
        self.logger.info("🚀 COMPLETE YOUTUBE OAUTH & SYPHON SETUP")
        self.logger.info("="*80 + "\n")

        results = {
            "timestamp": datetime.now().isoformat(),
            "oauth_setup": None,
            "account_syphon": None,
            "status": "in_progress"
        }

        # Step 1: @MANUS OAuth Setup
        self.logger.info("📋 Phase 1: @MANUS OAuth Setup")
        self.logger.info("-" * 80)
        oauth_result = self.oauth_setup.setup_oauth_with_manus()
        results["oauth_setup"] = {
            "status": oauth_result.status,
            "roadblocks": len(oauth_result.roadblocks),
            "solutions": len(oauth_result.solutions),
            "credentials_path": oauth_result.credentials_path
        }

        # Check if OAuth setup was successful
        if oauth_result.status == "success":
            self.logger.info("\n✅ OAuth setup successful!")

            # Step 2: SYPHON Account Data
            self.logger.info("\n📋 Phase 2: SYPHON Account Data")
            self.logger.info("-" * 80)

            try:
                account_data = self.account_syphon.syphon_all_account_data()
                results["account_syphon"] = {
                    "status": "success",
                    "subscriptions": len(account_data.subscriptions),
                    "watch_history": len(account_data.watch_history),
                    "liked_videos": len(account_data.liked_videos),
                    "recommendations": len(account_data.recommendations)
                }
                results["status"] = "success"

            except Exception as e:
                self.logger.error(f"❌ Account SYPHON failed: {e}")
                results["account_syphon"] = {
                    "status": "error",
                    "error": str(e)
                }
                results["status"] = "partial"

        elif oauth_result.status == "partial":
            self.logger.warning("\n⚠️ OAuth setup partial - some roadblocks resolved")
            results["status"] = "partial"

            # Try to continue anyway (credentials might exist)
            self.logger.info("\n📋 Attempting account SYPHON with existing setup...")
            try:
                account_data = self.account_syphon.syphon_all_account_data()
                results["account_syphon"] = {
                    "status": "success",
                    "subscriptions": len(account_data.subscriptions),
                    "watch_history": len(account_data.watch_history),
                    "liked_videos": len(account_data.liked_videos),
                    "recommendations": len(account_data.recommendations)
                }
                results["status"] = "success"
            except Exception as e:
                self.logger.warning(f"⚠️ Account SYPHON failed: {e}")
                results["account_syphon"] = {
                    "status": "error",
                    "error": str(e)
                }

        else:
            self.logger.warning("\n⚠️ OAuth setup not complete - manual setup required")
            results["status"] = "oauth_required"

            # Display instructions
            self._display_oauth_instructions()

        return results

    def _display_oauth_instructions(self):
        """Display OAuth setup instructions"""
        print("\n" + "="*80)
        print("📋 OAUTH SETUP INSTRUCTIONS")
        print("="*80 + "\n")
        print("🤖 JARVIS Instructions:")
        print("   1. Go to https://console.cloud.google.com/")
        print("   2. Select or create a project")
        print("   3. Enable YouTube Data API v3")
        print("   4. Go to APIs & Services > Credentials")
        print("   5. Create OAuth 2.0 Client ID")
        print("      - Application type: Desktop app")
        print("      - Name: LUMINA YouTube OAuth")
        print("   6. Download credentials JSON")
        print("   7. Save to: config/secrets/client_secrets.json")
        print("\n   8. Run this script again to complete setup")
        print("\n" + "="*80 + "\n")

    def display_summary(self, results: Dict[str, Any]):
        """Display complete setup summary"""
        print("\n" + "="*80)
        print("📊 COMPLETE SETUP SUMMARY")
        print("="*80 + "\n")

        print(f"Overall Status: {results['status']}\n")

        # OAuth Setup
        oauth = results.get("oauth_setup", {})
        print("🔧 OAuth Setup:")
        print(f"   Status: {oauth.get('status', 'unknown')}")
        print(f"   Roadblocks: {oauth.get('roadblocks', 0)}")
        print(f"   Solutions: {oauth.get('solutions', 0)}")
        if oauth.get('credentials_path'):
            print(f"   Credentials: {oauth['credentials_path']}")

        # Account SYPHON
        syphon = results.get("account_syphon", {})
        print(f"\n🔄 Account SYPHON:")
        print(f"   Status: {syphon.get('status', 'unknown')}")
        if syphon.get('status') == 'success':
            print(f"   Subscriptions: {syphon.get('subscriptions', 0)}")
            print(f"   Watch History: {syphon.get('watch_history', 0)}")
            print(f"   Liked Videos: {syphon.get('liked_videos', 0)}")
            print(f"   Recommendations: {syphon.get('recommendations', 0)}")
        elif syphon.get('error'):
            print(f"   Error: {syphon['error']}")

        print("\n" + "="*80 + "\n")


def main():
    try:
        """Main execution function"""
        print("\n" + "="*80)
        print("🚀 @MANUS COMPLETE YOUTUBE OAUTH & SYPHON SETUP")
        print("="*80 + "\n")

        project_root = Path(".").resolve()
        setup = ManusYouTubeOAuthCompleteSetup(project_root)

        # Execute complete setup
        results = setup.execute_complete_setup()

        # Display summary
        setup.display_summary(results)

        return results


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()