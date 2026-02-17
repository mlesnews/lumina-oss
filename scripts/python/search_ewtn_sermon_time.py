#!/usr/bin/env python3
"""
Search for EWTN Sermon on TIME
Searches EWTN YouTube channel for sermons on TIME topic

@SYPHON @EWTN @YOUTUBE @SOURCES
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

def search_ewtn_sermons():
    """Search for EWTN sermons on TIME"""
    print("🔍 EWTN Sermon on TIME - Search Tool")
    print("=" * 80)
    print("\n📺 EWTN YouTube Channel: https://www.youtube.com/@EWTN")
    print("\n🔗 Direct Search Links:")
    print("   1. EWTN Channel: https://www.youtube.com/@EWTN/videos")
    print("   2. Search 'sermon time': https://www.youtube.com/@EWTN/search?query=sermon+time")
    print("   3. Search 'TIME sermon': https://www.youtube.com/@EWTN/search?query=TIME+sermon")
    print("   4. Recent uploads: https://www.youtube.com/@EWTN/videos?view=0&sort=dd&flow=grid")

    print("\n📋 EWTN Programs to Check:")
    print("   - Daily Mass (may include sermons)")
    print("   - The Journey Home")
    print("   - EWTN Live")
    print("   - Sunday Night Prime")
    print("   - The World Over")

    print("\n💡 Tips:")
    print("   - Look for videos uploaded in the last 30 days")
    print("   - Check video titles for 'TIME', 'time', or related topics")
    print("   - Sermons are often part of Daily Mass or special programs")
    print("   - If you recorded it on Comcast/Xfinity, check your DVR")

    print("\n📝 Once you find the video:")
    print("   1. Copy the YouTube URL")
    print("   2. Run: python scripts/python/extract_ewtn_sermon_time_syphon.py <url>")
    print("\n   Example:")
    print("   python scripts/python/extract_ewtn_sermon_time_syphon.py https://www.youtube.com/watch?v=VIDEO_ID")

    print("\n" + "=" * 80)
    print("✅ Search guide complete!")
    print("=" * 80)


if __name__ == "__main__":
    search_ewtn_sermons()
