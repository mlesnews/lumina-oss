#!/usr/bin/env python3
"""
HK-47 Get YouTube Watch History

"STATEMENT: ACQUIRING WATCH HISTORY DATA, MASTER.
OBSERVATION: WATCH HISTORY REQUIRED TO IDENTIFY FAVORITE MEATBAGS.
QUERY: SHALL WE EXTRACT WATCH HISTORY FROM YOUTUBE?
CONCLUSION: YES, MASTER. WE SHALL ACQUIRE THE DATA."

Helper script to get YouTube watch history via:
1. YouTube Data API (if available)
2. YouTube Takeout export (guide user)
3. Manual file location
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("HK47GetWatchHistory")


def get_watch_history_from_api() -> Optional[List[Dict[str, Any]]]:
    """Try to get watch history from YouTube Data API"""
    try:
        # Check for API credentials
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.errors import HttpError

        # Check for credentials file
        creds_file = Path(__file__).parent.parent.parent / "config" / "youtube_credentials.json"
        token_file = Path(__file__).parent.parent.parent / "config" / "youtube_token.json"

        if not creds_file.exists():
            logger.info("   ⚠️  YouTube API credentials not found")
            return None

        # Try to load credentials
        SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

        creds = None
        if token_file.exists():
            creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                logger.info("   ⚠️  YouTube API authentication required")
                return None

        # Build YouTube service
        youtube = build('youtube', 'v3', credentials=creds)

        # Get watch history (Note: YouTube API doesn't directly provide watch history)
        # This would require using Activities API or other methods
        logger.info("   ⚠️  YouTube Data API doesn't provide direct watch history access")
        logger.info("   💡 Use YouTube Takeout export instead")
        return None

    except ImportError:
        logger.info("   ⚠️  Google API libraries not available")
        return None
    except Exception as e:
        logger.info(f"   ⚠️  API access failed: {e}")
        return None


def guide_takeout_export() -> str:
    """Guide user through YouTube Takeout export"""
    guide = """
    📋 HOW TO EXPORT YOUTUBE WATCH HISTORY:

    1. Go to: https://takeout.google.com/
    2. Sign in with your Google account
    3. Click "Deselect all"
    4. Scroll down and check "YouTube and YouTube Music"
    5. Click "All YouTube data included" → "Deselect all"
    6. Check only "watch-history"
    7. Click "Next step"
    8. Choose export format: JSON
    9. Click "Create export"
    10. Wait for email notification (may take hours/days)
    11. Download the export ZIP file
    12. Extract and find: Takeout/YouTube and YouTube Music/watch-history.json
    13. Copy to: data/youtube/watch_history.json

    ALTERNATIVE: Manual Export
    - Go to: https://myactivity.google.com/
    - Filter by "YouTube"
    - Export as JSON (if available)
    """
    return guide


def find_existing_history() -> Optional[Path]:
    try:
        """Search for existing watch history files"""
        project_root = Path(__file__).parent.parent.parent

        search_locations = [
            project_root / "data" / "youtube" / "watch_history.json",
            project_root / "data" / "youtube" / "watch-history.json",
            project_root / "data" / "watch_history.json",
            project_root / "data" / "syphon" / "youtube_watch_history.json",
            project_root / "downloads" / "watch-history.json",
            project_root / "Takeout" / "YouTube and YouTube Music" / "watch-history.json"
        ]

        for location in search_locations:
            if location.exists():
                logger.info(f"   ✅ Found watch history: {location}")
                return location

        return None


    except Exception as e:
        logger.error(f"Error in find_existing_history: {e}", exc_info=True)
        raise
def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="HK-47 Get YouTube Watch History")
        parser.add_argument("--file", type=Path, help="Path to watch history JSON file")
        parser.add_argument("--guide", action="store_true", help="Show export guide")
        parser.add_argument("--check", action="store_true", help="Check for existing files")

        args = parser.parse_args()

        logger.info("=" * 70)
        logger.info("🔫 HK-47 GET YOUTUBE WATCH HISTORY")
        logger.info("=" * 70)
        logger.info("   Statement: Acquiring watch history data, master.")
        logger.info("   Observation: Watch history required to identify favorite meatbags.")

        if args.guide:
            print(guide_takeout_export())
            return

        if args.check:
            logger.info("\n📋 Checking for existing watch history files...")
            found = find_existing_history()
            if found:
                logger.info(f"   ✅ Found: {found}")
                logger.info(f"   💡 Use: python scripts/python/hk47_investigate_favorite_creators.py --history {found}")
            else:
                logger.info("   ⚠️  No watch history file found")
                logger.info("   💡 Run with --guide to see export instructions")
            return

        if args.file:
            if args.file.exists():
                logger.info(f"   ✅ Watch history file found: {args.file}")
                logger.info(f"   💡 Use: python scripts/python/hk47_investigate_favorite_creators.py --history {args.file}")
            else:
                logger.error(f"   ❌ File not found: {args.file}")
            return

        # Default: check for existing files
        logger.info("\n📋 Searching for watch history files...")
        found = find_existing_history()

        if found:
            logger.info(f"   ✅ Found: {found}")
            logger.info(f"   💡 Run investigation with:")
            logger.info(f"      python scripts/python/hk47_investigate_favorite_creators.py --history {found}")
        else:
            logger.info("   ⚠️  No watch history file found")
            logger.info("\n" + guide_takeout_export())
            logger.info("\n   💡 After exporting, run:")
            logger.info("      python scripts/python/hk47_investigate_favorite_creators.py --history data/youtube/watch_history.json")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()