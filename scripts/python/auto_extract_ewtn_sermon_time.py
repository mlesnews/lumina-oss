#!/usr/bin/env python3
"""
Automated EWTN Sermon on TIME Extraction
Attempts to find and extract EWTN sermon on TIME automatically

@SYPHON @EWTN @YOUTUBE @SOURCES
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import logging
logger = logging.getLogger("auto_extract_ewtn_sermon_time")


script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

def check_yt_dlp():
    """Check if yt-dlp is available"""
    try:
        result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def search_ewtn_with_yt_dlp(query="sermon time", max_results=10):
    """Search EWTN YouTube channel using yt-dlp"""
    if not check_yt_dlp():
        print("⚠️  yt-dlp not found. Install with: pip install yt-dlp")
        return []

    try:
        # Search EWTN channel
        channel_url = "https://www.youtube.com/@EWTN"
        cmd = [
            'yt-dlp',
            '--flat-playlist',
            '--print', '%(id)s|%(title)s|%(url)s',
            f'{channel_url}/search?query={query}',
            '--max-downloads', str(max_results)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            videos = []
            for line in result.stdout.strip().split('\n'):
                if '|' in line:
                    parts = line.split('|', 2)
                    if len(parts) >= 2:
                        video_id = parts[0]
                        title = parts[1]
                        url = f"https://www.youtube.com/watch?v={video_id}"
                        videos.append({
                            'id': video_id,
                            'title': title,
                            'url': url
                        })
            return videos
    except Exception as e:
        print(f"⚠️  yt-dlp search error: {e}")

    return []

def main():
    try:
        """Main execution"""
        print("🔍 Automated EWTN Sermon on TIME Extraction")
        print("=" * 80)

        # Try to search with yt-dlp
        print("\n🔍 Searching EWTN YouTube channel for 'sermon time'...")
        videos = search_ewtn_with_yt_dlp("sermon time", max_results=20)

        if videos:
            print(f"\n✅ Found {len(videos)} potential videos:")
            print("\n" + "-" * 80)
            for i, video in enumerate(videos[:10], 1):
                print(f"{i}. {video['title']}")
                print(f"   URL: {video['url']}")
                print()

            # Look for TIME-related videos
            time_videos = [v for v in videos if 'time' in v['title'].lower() or 'TIME' in v['title']]

            if time_videos:
                print(f"\n🎯 Found {len(time_videos)} videos with 'TIME' in title:")
                for i, video in enumerate(time_videos[:5], 1):
                    print(f"{i}. {video['title']}")
                    print(f"   URL: {video['url']}")
                    print()

                # Use the first TIME-related video
                selected = time_videos[0]
                print(f"\n📹 Selected: {selected['title']}")
                print(f"   URL: {selected['url']}")
                print("\n🚀 Running SYPHON extraction...")
                print("=" * 80)

                # Run extraction
                extract_script = project_root / "scripts" / "python" / "extract_ewtn_sermon_time_syphon.py"
                if extract_script.exists():
                    result = subprocess.run(
                        [sys.executable, str(extract_script), selected['url']],
                        cwd=str(project_root)
                    )
                    return result.returncode
                else:
                    print(f"❌ Extraction script not found: {extract_script}")
                    return 1
            else:
                print("\n⚠️  No videos found with 'TIME' in title")
                print("   Please review the list above and run extraction manually:")
                print(f"   python scripts/python/extract_ewtn_sermon_time_syphon.py <url>")
                return 1
        else:
            print("\n⚠️  Could not automatically search EWTN channel")
            print("\n📋 Manual Search Options:")
            print("   1. Visit: https://www.youtube.com/@EWTN/videos")
            print("   2. Search for: 'sermon time' or 'TIME sermon'")
            print("   3. Find the recent sermon you watched")
            print("   4. Copy the YouTube URL")
            print("   5. Run: python scripts/python/extract_ewtn_sermon_time_syphon.py <url>")
            print("\n💡 Alternative: Check your Comcast/Xfinity DVR for the recording")
            return 1

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())