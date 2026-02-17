#!/usr/bin/env python3
"""
SYPHON: YouTube Watch History (Configurable Days - Default: 90 Days)

This system extracts and processes your YouTube watch history from the past N days (default: 90),
identifying patterns, favorite creators, and key topics for LUMINA intelligence.

"The fact that I can talk to something and it feels like a human" - User

Methods:
1. Browser cookies (if browser closed)
2. Cookies.txt file (exported via browser extension)
3. Google Takeout (most complete)

For each video, we extract:
- Title, channel, video ID
- Watch date/time
- Topics/themes
- Key insights for LUMINA
"""

import subprocess
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SyphonWatchHistory")


class YouTubeWatchHistorySyphon:
    """
    SYPHON your YouTube watch history for the past N days (default: 90 days)
    """

    def __init__(self, project_root: Optional[Path] = None, days: int = 90):
        """
        Initialize YouTube watch history syphon

        Args:
            project_root: Project root path
            days: Number of days to look back (default: 90)
        """
        self.days = days
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        
        # Load storage policy
        policy_file = self.project_root / "config" / "storage_policy.json"
        storage_policy = {"zero_local_storage_enforced": False}
        if policy_file.exists():
            with open(policy_file, "r", encoding="utf-8") as f:
                storage_policy = json.load(f)

        if storage_policy.get("zero_local_storage_enforced"):
            self.output_dir = Path(storage_policy["nas_paths"]["youtube_history"])
            logger.info(f"🛡️  Enforcing Zero-Local-Storage Policy. Using NAS: {self.output_dir}")
        else:
            self.output_dir = self.project_root / "data" / "syphon" / "youtube_history"
            
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.cookies_file = self.project_root / "config" / "youtube_cookies.txt"
        self.history_file = self.project_root / "data" / "youtube" / "watch_history.json"

        self.videos = []
        self.channels = Counter()
        self.topics = Counter()

    def check_access_methods(self) -> Dict[str, bool]:
        """Check available access methods"""
        methods = {
            "cookies_file": self.cookies_file.exists(),
            "takeout_file": self.history_file.exists(),
            "browser_edge": False,
            "browser_chrome": False,
            "browser_firefox": False
        }

        # Check if browsers available (will fail if running)
        for browser in ["edge", "chrome", "firefox"]:
            try:
                result = subprocess.run(
                    ["yt-dlp", "--cookies-from-browser", browser, "--version"],
                    capture_output=True, timeout=5
                )
                methods[f"browser_{browser}"] = result.returncode == 0
            except:
                pass

        return methods

    def syphon_via_cookies_file(self, max_videos: int = 200) -> List[Dict[str, Any]]:
        """Syphon watch history using exported cookies file"""
        if not self.cookies_file.exists():
            logger.warning("Cookies file not found. Please export cookies first.")
            return []

        logger.info(f"📺 Syphoning watch history via cookies file...")
        logger.info(f"   Max videos: {max_videos}")

        try:
            cmd = [
                "yt-dlp",
                "--cookies", str(self.cookies_file),
                "https://www.youtube.com/feed/history",
                "--flat-playlist",
                "--print", "%(id)s|%(title)s|%(channel)s|%(channel_id)s|%(upload_date)s|%(duration)s",
                f"--playlist-items", f"1-{max_videos}",
                "--skip-download"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode != 0:
                logger.error(f"yt-dlp failed: {result.stderr[:500]}")
                return []

            videos = []
            for line in result.stdout.strip().split('\n'):
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        video = {
                            "video_id": parts[0],
                            "title": parts[1],
                            "channel": parts[2],
                            "channel_id": parts[3] if len(parts) > 3 else "",
                            "upload_date": parts[4] if len(parts) > 4 else "",
                            "duration": parts[5] if len(parts) > 5 else "",
                            "syphoned_at": datetime.now().isoformat()
                        }
                        videos.append(video)

            logger.info(f"   ✅ Syphoned {len(videos)} videos")
            return videos

        except subprocess.TimeoutExpired:
            logger.error("Timeout - try with fewer videos")
            return []
        except Exception as e:
            logger.error(f"Error: {e}")
            return []

    def syphon_via_browser(self, browser: str = "edge", max_videos: int = 200) -> List[Dict[str, Any]]:
        """Syphon watch history directly from browser (must be closed)"""

        logger.info(f"📺 Syphoning watch history via {browser} browser...")
        logger.info(f"   ⚠️  Browser must be CLOSED for this to work")

        try:
            cmd = [
                "yt-dlp",
                "--cookies-from-browser", browser,
                "https://www.youtube.com/feed/history",
                "--flat-playlist",
                "--print", "%(id)s|%(title)s|%(channel)s|%(channel_id)s",
                f"--playlist-items", f"1-{max_videos}",
                "--skip-download"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode != 0:
                if "could not find" in result.stderr.lower() or "copy" in result.stderr.lower():
                    logger.warning(f"   ⚠️  {browser} browser may be running. Close it and try again.")
                return []

            videos = []
            for line in result.stdout.strip().split('\n'):
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        video = {
                            "video_id": parts[0],
                            "title": parts[1],
                            "channel": parts[2],
                            "channel_id": parts[3] if len(parts) > 3 else "",
                            "syphoned_at": datetime.now().isoformat()
                        }
                        videos.append(video)

            logger.info(f"   ✅ Syphoned {len(videos)} videos")
            return videos

        except Exception as e:
            logger.error(f"Error: {e}")
            return []

    def syphon_via_takeout(self) -> List[Dict[str, Any]]:
        """Syphon watch history from Google Takeout export"""

        if not self.history_file.exists():
            logger.warning("Takeout file not found.")
            return []

        logger.info(f"📺 Syphoning watch history via Google Takeout...")

        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Google Takeout format
            videos = []
            cutoff_date = datetime.now() - timedelta(days=self.days)

            for item in data:
                # Parse watch time
                if "time" in item:
                    try:
                        watch_time = datetime.fromisoformat(item["time"].replace("Z", "+00:00"))
                        if watch_time.replace(tzinfo=None) < cutoff_date:
                            continue  # Skip videos older than configured days
                    except:
                        pass

                video = {
                    "title": item.get("title", "").replace("Watched ", ""),
                    "url": item.get("titleUrl", ""),
                    "channel": item.get("subtitles", [{}])[0].get("name", ""),
                    "channel_url": item.get("subtitles", [{}])[0].get("url", ""),
                    "watch_time": item.get("time", ""),
                    "syphoned_at": datetime.now().isoformat()
                }

                # Extract video ID from URL
                if "v=" in video["url"]:
                    video["video_id"] = video["url"].split("v=")[1].split("&")[0]

                videos.append(video)

            logger.info(f"   ✅ Syphoned {len(videos)} videos (past {self.days} days)")
            return videos

        except Exception as e:
            logger.error(f"Error: {e}")
            return []

    def analyze_history(self, videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze watch history for patterns and insights"""

        if not videos:
            return {"error": "No videos to analyze"}

        logger.info(f"🔍 Analyzing {len(videos)} videos...")

        # Count channels
        channels = Counter()
        for v in videos:
            channel = v.get("channel", "Unknown")
            if channel:
                channels[channel] += 1

        # Identify topics from titles
        ai_keywords = ["ai", "artificial intelligence", "gpt", "claude", "llm", "machine learning",
                      "openai", "anthropic", "deepmind", "neural", "chatgpt", "agi", "superintelligence"]
        tech_keywords = ["nvidia", "google", "microsoft", "apple", "meta", "tesla", "coding", "programming"]
        creator_keywords = ["wes roth", "dylan curious", "fireship", "lex fridman", "andrej karpathy"]

        ai_videos = []
        tech_videos = []
        creator_videos = []

        for v in videos:
            title_lower = v.get("title", "").lower()
            channel_lower = v.get("channel", "").lower()

            if any(kw in title_lower or kw in channel_lower for kw in ai_keywords):
                ai_videos.append(v)
            if any(kw in title_lower or kw in channel_lower for kw in tech_keywords):
                tech_videos.append(v)
            if any(kw in channel_lower for kw in creator_keywords):
                creator_videos.append(v)

        analysis = {
            "total_videos": len(videos),
            "analysis_date": datetime.now().isoformat(),
            "period": f"past_{self.days}_days",
            "top_channels": dict(channels.most_common(20)),
            "ai_related_videos": len(ai_videos),
            "tech_related_videos": len(tech_videos),
            "key_creator_videos": len(creator_videos),
            "categories": {
                "ai_content": [{"title": v.get("title"), "channel": v.get("channel")} for v in ai_videos[:20]],
                "tech_content": [{"title": v.get("title"), "channel": v.get("channel")} for v in tech_videos[:20]],
                "key_creators": [{"title": v.get("title"), "channel": v.get("channel")} for v in creator_videos[:20]]
            },
            "insights": []
        }

        # Generate insights
        if channels:
            top_channel = channels.most_common(1)[0]
            analysis["insights"].append(f"Most watched channel: {top_channel[0]} ({top_channel[1]} videos)")

        if ai_videos:
            analysis["insights"].append(f"High AI interest: {len(ai_videos)} AI-related videos ({len(ai_videos)/len(videos)*100:.1f}%)")

        if creator_videos:
            analysis["insights"].append(f"Following key creators: {len(creator_videos)} videos from Wes Roth, Dylan Curious, etc.")

        return analysis

    def save_syphon_results(self, videos: List[Dict[str, Any]], analysis: Dict[str, Any]):
        try:
            """Save syphon results to files"""

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Save raw video list
            videos_file = self.output_dir / f"watch_history_{timestamp}.json"
            with open(videos_file, 'w', encoding='utf-8') as f:
                json.dump(videos, f, indent=2)
            logger.info(f"   📁 Videos saved: {videos_file}")

            # Save analysis
            analysis_file = self.output_dir / f"watch_history_analysis_{timestamp}.json"
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2)
            logger.info(f"   📁 Analysis saved: {analysis_file}")

            return videos_file, analysis_file

        except Exception as e:
            self.logger.error(f"Error in save_syphon_results: {e}", exc_info=True)
            raise
    def print_analysis_report(self, analysis: Dict[str, Any]):
        """Print a human-readable analysis report"""

        print()
        print("="*70)
        print(f"📺 YOUTUBE WATCH HISTORY ANALYSIS - PAST {self.days} DAYS")
        print("="*70)
        print()
        print(f"📊 Total Videos: {analysis.get('total_videos', 0)}")
        print(f"🤖 AI-Related: {analysis.get('ai_related_videos', 0)}")
        print(f"💻 Tech-Related: {analysis.get('tech_related_videos', 0)}")
        print(f"🎙️ Key Creators: {analysis.get('key_creator_videos', 0)}")
        print()

        print("🏆 TOP CHANNELS:")
        print("-"*50)
        for channel, count in list(analysis.get("top_channels", {}).items())[:10]:
            bar = "█" * min(count, 20)
            print(f"   {count:3d} {bar} {channel}")
        print()

        print("💡 INSIGHTS:")
        print("-"*50)
        for insight in analysis.get("insights", []):
            print(f"   • {insight}")
        print()

        print("🎯 AI CONTENT HIGHLIGHTS:")
        print("-"*50)
        for item in analysis.get("categories", {}).get("ai_content", [])[:5]:
            print(f"   📹 {item.get('title', 'Unknown')[:60]}...")
            print(f"      Channel: {item.get('channel', 'Unknown')}")
        print()

    def run(self, method: str = "auto", max_videos: int = 200):
        """Run the syphon process"""

        print("="*70)
        print(f"🎯 SYPHON: YOUTUBE WATCH HISTORY (PAST {self.days} DAYS)")
        print("="*70)
        print()

        # Check available methods
        methods = self.check_access_methods()
        print("📋 Available access methods:")
        for method_name, available in methods.items():
            status = "✅" if available else "❌"
            print(f"   {status} {method_name}")
        print()

        videos = []

        # Try methods in order of preference
        if method == "auto":
            if methods["cookies_file"]:
                videos = self.syphon_via_cookies_file(max_videos)
            elif methods["takeout_file"]:
                videos = self.syphon_via_takeout()
            elif methods["browser_edge"]:
                videos = self.syphon_via_browser("edge", max_videos)
            elif methods["browser_chrome"]:
                videos = self.syphon_via_browser("chrome", max_videos)
        elif method == "cookies":
            videos = self.syphon_via_cookies_file(max_videos)
        elif method == "takeout":
            videos = self.syphon_via_takeout()
        elif method in ["edge", "chrome", "firefox"]:
            videos = self.syphon_via_browser(method, max_videos)

        if not videos:
            print()
            print("⚠️  NO VIDEOS SYPHONED. To enable syphoning:")
            print()
            print("   OPTION 1: Export cookies via browser extension")
            print("   1. Install 'Get cookies.txt LOCALLY' extension")
            print("   2. Go to YouTube.com")
            print("   3. Export cookies")
            print(f"   4. Save to: {self.cookies_file}")
            print()
            print("   OPTION 2: Close browser and run again")
            print("   1. Close ALL Edge/Chrome windows")
            print("   2. Run: python scripts/python/syphon_youtube_watch_history_30_days.py --method edge")
            print()
            print("   OPTION 3: Google Takeout (complete history)")
            print("   1. Go to takeout.google.com")
            print("   2. Export YouTube watch history")
            print(f"   3. Save to: {self.history_file}")
            return None

        # Analyze
        analysis = self.analyze_history(videos)

        # Save
        self.save_syphon_results(videos, analysis)

        # Report
        self.print_analysis_report(analysis)

        return analysis


def main():
    import argparse

    parser = argparse.ArgumentParser(description="SYPHON YouTube Watch History")
    parser.add_argument("--method", choices=["auto", "cookies", "takeout", "edge", "chrome", "firefox"],
                       default="auto", help="Access method to use")
    parser.add_argument("--max-videos", type=int, default=500, help="Maximum videos to fetch (increased for 90-day window)")
    parser.add_argument("--days", type=int, default=90, help="Number of days to look back (default: 90)")

    args = parser.parse_args()

    syphon = YouTubeWatchHistorySyphon(days=args.days)
    syphon.run(method=args.method, max_videos=args.max_videos)


if __name__ == "__main__":



    main()