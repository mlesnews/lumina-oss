#!/usr/bin/env python3
"""
Fetch and Process YouTube Channel: @MatthewLesnewski

Fetches all videos from @MatthewLesnewski channel and processes to Holocron.

Tags: #YOUTUBE #CHANNEL #MATTHEWLESNEWSKI #HOLOCRON @JARVIS @LUMINA
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

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

logger = get_logger("FetchMLESNEWSChannel")


class MLESNEWSChannelFetcher:
    """
    Fetch and process @MatthewLesnewski YouTube channel
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize channel fetcher"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = project_root / "data"
        self.youtube_dir = self.data_dir / "youtube"
        self.holocron_dir = self.data_dir / "holocron" / "youtube_curated"

        # Ensure directories exist
        for dir_path in [self.youtube_dir, self.holocron_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        self.channel_handle = "@MatthewLesnewski"
        # Try multiple URL formats
        self.channel_urls = [
            f"https://www.youtube.com/{self.channel_handle}",
            f"https://www.youtube.com/c/{self.channel_handle.replace('@', '')}",
            f"https://www.youtube.com/channel/{self.channel_handle.replace('@', '')}",
            f"https://www.youtube.com/user/{self.channel_handle.replace('@', '')}",
        ]
        self.channel_url = self.channel_urls[0]  # Default

        # Neo browser cookies
        self.cookies_file = self.project_root / "config" / "youtube_cookies.txt"
        self.neo_cookies_path = self.project_root / "config" / "neo_youtube_cookies.txt"

        logger.info("✅ MLESNEWS Channel Fetcher initialized")
        logger.info(f"   Channel: {self.channel_handle}")
        logger.info(f"   URL: {self.channel_url}")

    def check_yt_dlp_available(self) -> bool:
        """Check if yt-dlp is available"""
        try:
            result = subprocess.run(
                ["yt-dlp", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def get_neo_cookies_path(self) -> Optional[Path]:
        try:
            """Get Neo browser cookies path"""
            # Check if exported cookies file exists first (preferred)
            if self.neo_cookies_path.exists():
                logger.info(f"   ✅ Found exported Neo cookies: {self.neo_cookies_path}")
                return self.neo_cookies_path

            # Try to find Neo cookies database (requires export)
            neo_cookie_paths = [
                Path.home() / "AppData" / "Local" / "Neo" / "User Data" / "Default" / "Cookies",
                Path.home() / "AppData" / "Local" / "neo-browser" / "User Data" / "Default" / "Cookies",
                Path.home() / "AppData" / "Roaming" / "Neo" / "Cookies",
            ]

            for path in neo_cookie_paths:
                if path.exists():
                    logger.info(f"   ✅ Found Neo cookies database: {path}")
                    logger.info("   💡 Note: yt-dlp can use '--cookies-from-browser chrome' if Neo uses Chromium")
                    return path

            return None

        except Exception as e:
            self.logger.error(f"Error in get_neo_cookies_path: {e}", exc_info=True)
            raise
    def fetch_channel_videos(self, max_videos: int = 100) -> List[Dict[str, Any]]:
        """Fetch all videos from @MLESNEWS channel"""
        logger.info("=" * 80)
        logger.info(f"📺 Fetching Channel: {self.channel_handle}")
        logger.info("=" * 80)
        logger.info("")

        if not self.check_yt_dlp_available():
            logger.error("   ❌ yt-dlp not available - install: pip install yt-dlp")
            return []

        videos = []

        # Try each URL format until one works
        for channel_url in self.channel_urls:
            try:
                # Build command
                cmd = [
                    "yt-dlp",
                    channel_url,
                    "--flat-playlist",
                    "--print", "%(id)s|%(title)s|%(channel)s|%(channel_id)s|%(upload_date)s|%(duration)s|%(view_count)s",
                    f"--playlist-items", f"1-{max_videos}",
                    "--skip-download",
                    "--no-warnings"
                ]

                # Try Neo browser cookies first
                neo_cookies = self.get_neo_cookies_path()
                if neo_cookies and self.neo_cookies_path.exists():
                    logger.info(f"   Using Neo cookies file: {self.neo_cookies_path}")
                    cmd.extend(["--cookies", str(self.neo_cookies_path)])
                elif self.cookies_file.exists():
                    logger.info(f"   Using cookies file: {self.cookies_file}")
                    cmd.extend(["--cookies", str(self.cookies_file)])
                else:
                    # Try Neo browser directly (if it uses Chromium, yt-dlp can access it)
                    logger.info("   Trying Neo browser cookies (Neo may use Chromium)...")
                    try:
                        cmd.extend(["--cookies-from-browser", "chrome"])  # Neo may use Chromium
                    except:
                        pass
                    logger.warning("   ⚠️  No cookies file - trying without authentication")
                    logger.info("   💡 Public channel videos should still work")
                    logger.info("   💡 To export Neo cookies: Use 'Get cookies.txt LOCALLY' extension in Neo")

                logger.info(f"   Trying URL: {channel_url}")
                logger.info(f"   Executing: yt-dlp {self.channel_handle} (max {max_videos} videos)")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if '|' in line:
                            parts = line.split('|')
                            if len(parts) >= 3:
                                video = {
                                    "video_id": parts[0],
                                    "title": parts[1] if len(parts) > 1 else "Unknown",
                                    "channel": parts[2] if len(parts) > 2 else self.channel_handle,
                                    "channel_id": parts[3] if len(parts) > 3 else "",
                                    "upload_date": parts[4] if len(parts) > 4 else "",
                                    "duration": parts[5] if len(parts) > 5 else "",
                                    "view_count": parts[6] if len(parts) > 6 else "0",
                                    "description": parts[7] if len(parts) > 7 else "",
                                    "url": f"https://www.youtube.com/watch?v={parts[0]}",
                                    "source": "youtube_channel",
                                    "channel_handle": self.channel_handle,
                                    "fetched_at": datetime.now().isoformat()
                                }
                                videos.append(video)

                    logger.info(f"   ✅ Fetched {len(videos)} videos from {self.channel_handle}")
                    self.channel_url = channel_url  # Update to working URL
                    break  # Success - stop trying other URLs
                else:
                    logger.debug(f"   URL failed: {result.stderr[:200]}")
                    continue  # Try next URL format

            except subprocess.TimeoutExpired:
                logger.warning("   ⚠️  Timeout - trying next URL format")
                continue
            except Exception as e:
                logger.debug(f"   Error with URL {channel_url}: {e}")
                continue

        if not videos:
            logger.warning(f"   ⚠️  Could not fetch videos from any URL format")
            logger.info("   💡 Tried URLs:")
            for url in self.channel_urls:
                logger.info(f"      - {url}")
            logger.info("   💡 Tip: Export cookies from Neo browser or verify channel handle")

        return videos

    def process_to_holocron(self, videos: List[Dict[str, Any]]) -> int:
        """
        Process videos to Holocron

        IMPORTANT: Only processes NEW or UPDATED videos.
        Does NOT reprocess videos that have already been processed.
        """
        logger.info("")
        logger.info("🔮 Processing Videos to Holocron...")
        logger.info("-" * 80)
        logger.info("")
        logger.info("   ⚠️  IMPORTANT: Only processing NEW or UPDATED videos")
        logger.info("   ⏭️  Skipping already-processed videos (no reprocessing)")
        logger.info("")

        try:
            from youtube_curated_to_holocron import YouTubeCuratedToHolocron
            from youtube_processed_tracker import YouTubeProcessedTracker

            processor = YouTubeCuratedToHolocron(self.project_root)
            tracker = YouTubeProcessedTracker(self.project_root)

            # Filter to only new or updated videos
            videos_to_process = tracker.filter_new_or_updated_videos(videos)

            if not videos_to_process:
                logger.info("   ✅ All videos already processed (no updates detected)")
                return 0

            logger.info(f"   📹 Processing {len(videos_to_process)} videos (new or updated)")
            logger.info("")

            processed = 0
            for video in videos_to_process:
                try:
                    # Determine category (Lumina YouTube account)
                    holocron_entry = processor.process_curated_video(video, category="lumina_youtube_account")
                    if holocron_entry:
                        # Mark as processed
                        tracker.mark_video_processed(video, holocron_entry)
                        processed += 1
                except Exception as e:
                    logger.debug(f"   Error processing video {video.get('video_id', 'unknown')}: {e}")

            logger.info("")
            logger.info(f"   ✅ Processed {processed}/{len(videos_to_process)} new/updated videos to Holocron")
            logger.info(f"   ⏭️  Skipped {len(videos) - len(videos_to_process)} already-processed videos")
            return processed

        except ImportError as e:
            logger.warning(f"   ⚠️  Required module not available: {e}")
            return 0
        except Exception as e:
            logger.error(f"   ❌ Error processing to Holocron: {e}")
            return 0

    def fetch_and_process_all(self, max_videos: int = 100) -> Dict[str, Any]:
        try:
            """Fetch and process all channel videos"""
            logger.info("=" * 80)
            logger.info(f"🎯 FETCHING AND PROCESSING @MatthewLesnewski CHANNEL")
            logger.info("=" * 80)
            logger.info("")

            # Fetch videos
            videos = self.fetch_channel_videos(max_videos=max_videos)

            if not videos:
                logger.warning("   ⚠️  No videos fetched")
                return {
                    "timestamp": datetime.now().isoformat(),
                    "channel": self.channel_handle,
                    "videos_fetched": 0,
                    "videos_processed": 0
                }

            # Save videos
            channel_file = self.youtube_dir / f"channel_matthewlesnewski.json"
            with open(channel_file, 'w', encoding='utf-8') as f:
                json.dump(videos, f, indent=2, ensure_ascii=False)
            logger.info(f"   ✅ Saved to: {channel_file}")

            # Process to Holocron
            processed = self.process_to_holocron(videos)

            results = {
                "timestamp": datetime.now().isoformat(),
                "channel": self.channel_handle,
                "channel_url": self.channel_url,
                "videos_fetched": len(videos),
                "videos_processed": processed,
                "videos": videos[:10]  # First 10 for summary
            }

            # Save results
            results_file = self.data_dir / "youtube_fetch_results" / f"matthewlesnewski_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            results_file.parent.mkdir(parents=True, exist_ok=True)
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            logger.info("")
            logger.info("=" * 80)
            logger.info("📊 SUMMARY")
            logger.info("=" * 80)
            logger.info(f"Channel: {self.channel_handle}")
            logger.info(f"Videos Fetched: {len(videos)}")
            logger.info(f"Videos Processed to Holocron: {processed}")
            logger.info(f"Results saved: {results_file}")
            logger.info("=" * 80)

            return results


        except Exception as e:
            self.logger.error(f"Error in fetch_and_process_all: {e}", exc_info=True)
            raise
def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Fetch and Process @MatthewLesnewski YouTube Channel")
    parser.add_argument("--max-videos", type=int, default=100, help="Maximum videos to fetch")

    args = parser.parse_args()

    fetcher = MLESNEWSChannelFetcher()
    results = fetcher.fetch_and_process_all(max_videos=args.max_videos)

    logger.info("")
    logger.info("✅ Channel fetching and processing complete")


if __name__ == "__main__":


    main()