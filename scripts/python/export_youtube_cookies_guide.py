#!/usr/bin/env python3
"""
Export YouTube Cookies Guide

To access YouTube watch history via yt-dlp, we need browser cookies.
Since the browser is currently running and cookies are locked, we need to export them manually.

OPTION 1: Export via Browser Extension (EASIEST)
OPTION 2: Close browser and run yt-dlp
OPTION 3: Use YouTube Data API with OAuth
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import logging
logger = logging.getLogger("export_youtube_cookies_guide")


def print_guide():
    print("="*70)
    print("📺 YOUTUBE HISTORY ACCESS GUIDE")
    print("="*70)
    print()

    print("🔐 CURRENT SITUATION:")
    print("   - Browser is running, so cookies are locked")
    print("   - yt-dlp can't access cookies while browser is open")
    print()

    print("="*70)
    print("OPTION 1: Export Cookies via Browser Extension (EASIEST)")
    print("="*70)
    print("""
    1. Install 'Get cookies.txt LOCALLY' extension for Edge:
       https://microsoftedge.microsoft.com/addons/detail/get-cookiestxt-locally/

    2. Go to: https://www.youtube.com
    3. Click the extension icon
    4. Click 'Export' or 'Download cookies.txt'
    5. Save as: C:\\Users\\mlesn\\Dropbox\\my_projects\\.lumina\\config\\youtube_cookies.txt

    6. Then run:
       yt-dlp --cookies config/youtube_cookies.txt "https://www.youtube.com/feed/history" --flat-playlist --print "%(id)s | %(title)s | %(channel)s" --playlist-items 1-50
    """)

    print("="*70)
    print("OPTION 2: Close Browser Temporarily")
    print("="*70)
    print("""
    1. Close ALL Edge browser windows
    2. Run this command:
       yt-dlp --cookies-from-browser edge "https://www.youtube.com/feed/history" --flat-playlist --print "%(id)s | %(title)s | %(channel)s" --playlist-items 1-50
    3. Reopen browser
    """)

    print("="*70)
    print("OPTION 3: YouTube Data API with OAuth (MOST ROBUST)")
    print("="*70)
    print("""
    This requires setting up a Google Cloud project:

    1. Go to: https://console.cloud.google.com/
    2. Create a new project or select existing
    3. Enable 'YouTube Data API v3'
    4. Create OAuth 2.0 credentials (Desktop app type)
    5. Download the credentials JSON
    6. Save as: C:\\Users\\mlesn\\Dropbox\\my_projects\\.lumina\\config\\youtube_credentials.json
    7. Run: python scripts/python/syphon_youtube_account_data.py --auth

    NOTE: Watch history is not directly available via API.
    API provides: Subscriptions, Liked Videos, Playlists
    """)

    print("="*70)
    print("OPTION 4: Google Takeout (COMPLETE HISTORY)")
    print("="*70)
    print("""
    For COMPLETE watch history (not just recent):

    1. Go to: https://takeout.google.com/
    2. Click 'Deselect all'
    3. Scroll to 'YouTube and YouTube Music' → Check it
    4. Click 'All YouTube data included' → 'Deselect all'
    5. Check ONLY 'watch-history'
    6. Click 'Next step'
    7. Choose format: JSON, Frequency: Export once
    8. Click 'Create export'
    9. Wait for email (can take hours)
    10. Download ZIP and extract
    11. Find: Takeout/YouTube and YouTube Music/watch-history.json
    12. Copy to: C:\\Users\\mlesn\\Dropbox\\my_projects\\.lumina\\data\\youtube\\watch_history.json
    """)

    print()
    print("="*70)
    print("📋 RECOMMENDED ACTION:")
    print("="*70)
    print("""
    For IMMEDIATE access to recent history:
    → Use OPTION 1 (browser extension) or OPTION 2 (close browser)

    For COMPLETE historical data:
    → Use OPTION 4 (Google Takeout) - includes all watched videos ever
    """)

def check_cookies_file():
    try:
        """Check if cookies file exists"""
        cookies_path = Path(__file__).parent.parent.parent / "config" / "youtube_cookies.txt"
        if cookies_path.exists():
            print(f"\n✅ Cookies file found: {cookies_path}")
            print("   Run: yt-dlp --cookies config/youtube_cookies.txt \"https://www.youtube.com/feed/history\" --flat-playlist --print \"%(id)s | %(title)s | %(channel)s\" --playlist-items 1-50")
            return True
        return False

    except Exception as e:
        logger.error(f"Error in check_cookies_file: {e}", exc_info=True)
        raise
def main():
    print_guide()

    if not check_cookies_file():
        print("\n⚠️ No cookies file found at config/youtube_cookies.txt")
        print("   Please export cookies using one of the options above.")

if __name__ == "__main__":



    main()