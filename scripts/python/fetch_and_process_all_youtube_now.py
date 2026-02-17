#!/usr/bin/env python3
"""
Fetch and Process ALL YouTube Videos NOW

Actively fetches and processes:
1. Your YouTube channel videos
2. Recommended feed
3. 30-day watch history
4. Recently viewed

Then processes them to Holocron immediately.

Tags: #YOUTUBE #FETCH #PROCESS #HOLOCRON #NOW @JARVIS @LUMINA
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

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

logger = get_logger("FetchProcessYouTubeNow")


class FetchAndProcessYouTubeNow:
    """
    Fetch and process ALL YouTube videos NOW

    No waiting - actively fetches:
    - Your YouTube channel
    - Recommended feed
    - 30-day watch history
    - Recently viewed
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize fetcher"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = project_root / "data"
        self.youtube_dir = self.data_dir / "youtube"
        self.syphon_dir = self.data_dir / "syphon" / "youtube_history"
        self.learning_dir = self.data_dir / "lumina_youtube_learning"
        self.holocron_dir = self.data_dir / "holocron" / "youtube_curated"

        # Ensure directories exist
        for dir_path in [self.youtube_dir, self.syphon_dir, self.learning_dir, self.holocron_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Cookies file
        self.cookies_file = self.project_root / "config" / "youtube_cookies.txt"

        logger.info("✅ Fetch and Process YouTube NOW initialized")
        logger.info("   🎯 Actively fetching videos (not waiting)")

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

    def fetch_recommended_feed(self, max_videos: int = 100) -> List[Dict[str, Any]]:
        """Fetch recommended feed videos"""
        logger.info("📺 Fetching Recommended Feed...")

        if not self.check_yt_dlp_available():
            logger.warning("   ⚠️  yt-dlp not available - install: pip install yt-dlp")
            return []

        videos = []

        try:
            # Build command
            cmd = [
                "yt-dlp",
                "https://www.youtube.com/feed/recommended",
                "--flat-playlist",
                "--print", "%(id)s|%(title)s|%(channel)s|%(channel_id)s|%(upload_date)s|%(duration)s|%(view_count)s",
                f"--playlist-items", f"1-{max_videos}",
                "--skip-download",
                "--no-warnings"
            ]

            # Add cookies if available
            if self.cookies_file.exists():
                cmd.extend(["--cookies", str(self.cookies_file)])
            else:
                # Try browser cookies
                cmd.extend(["--cookies-from-browser", "edge"])

            logger.info(f"   Executing: yt-dlp recommended feed (max {max_videos} videos)")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if '|' in line:
                        parts = line.split('|')
                        if len(parts) >= 3:
                            video = {
                                "video_id": parts[0],
                                "title": parts[1] if len(parts) > 1 else "Unknown",
                                "channel": parts[2] if len(parts) > 2 else "Unknown",
                                "channel_id": parts[3] if len(parts) > 3 else "",
                                "upload_date": parts[4] if len(parts) > 4 else "",
                                "duration": parts[5] if len(parts) > 5 else "",
                                "view_count": parts[6] if len(parts) > 6 else "0",
                                "source": "recommended_feed",
                                "fetched_at": datetime.now().isoformat()
                            }
                            videos.append(video)

                logger.info(f"   ✅ Fetched {len(videos)} recommended videos")
            else:
                logger.warning(f"   ⚠️  yt-dlp failed: {result.stderr[:200]}")
                if "cookies" in result.stderr.lower() or "login" in result.stderr.lower():
                    logger.info("   💡 Tip: Export cookies or close browser and try again")

        except subprocess.TimeoutExpired:
            logger.warning("   ⚠️  Timeout - try with fewer videos")
        except Exception as e:
            logger.error(f"   ❌ Error fetching recommended feed: {e}")

        return videos

    def fetch_30_day_history(self, max_videos: int = 200, days: int = 90) -> List[Dict[str, Any]]:
        """
        Fetch watch history (configurable days, default 90)

        Args:
            max_videos: Maximum videos to fetch
            days: Number of days to look back (default: 90)
        """
        logger.info(f"📺 Fetching {days}-Day Watch History...")

        if not self.check_yt_dlp_available():
            logger.warning("   ⚠️  yt-dlp not available")
            return []

        videos = []

        try:
            # Build command
            cmd = [
                "yt-dlp",
                "https://www.youtube.com/feed/history",
                "--flat-playlist",
                "--print", "%(id)s|%(title)s|%(channel)s|%(channel_id)s|%(upload_date)s",
                f"--playlist-items", f"1-{max_videos}",
                "--skip-download",
                "--no-warnings"
            ]

            # Add cookies if available
            if self.cookies_file.exists():
                cmd.extend(["--cookies", str(self.cookies_file)])
            else:
                # Try browser cookies
                cmd.extend(["--cookies-from-browser", "edge"])

            logger.info(f"   Executing: yt-dlp watch history (max {max_videos} videos)")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            if result.returncode == 0:
                cutoff_date = datetime.now() - timedelta(days=days)

                for line in result.stdout.strip().split('\n'):
                    if '|' in line:
                        parts = line.split('|')
                        if len(parts) >= 3:
                            video = {
                                "video_id": parts[0],
                                "title": parts[1] if len(parts) > 1 else "Unknown",
                                "channel": parts[2] if len(parts) > 2 else "Unknown",
                                "channel_id": parts[3] if len(parts) > 3 else "",
                                "upload_date": parts[4] if len(parts) > 4 else "",
                                "source": f"{days}_day_history",
                                "fetched_at": datetime.now().isoformat()
                            }

                            # Filter by date if we have upload_date
                            try:
                                if video.get("upload_date"):
                                    upload_date = datetime.strptime(video["upload_date"], "%Y%m%d")
                                    if upload_date >= cutoff_date:
                                        videos.append(video)
                                else:
                                    # Include if no date (recent history)
                                    videos.append(video)
                            except:
                                videos.append(video)

                logger.info(f"   ✅ Fetched {len(videos)} videos from {days}-day history")
            else:
                logger.warning(f"   ⚠️  yt-dlp failed: {result.stderr[:200]}")
                if "cookies" in result.stderr.lower() or "login" in result.stderr.lower():
                    logger.info("   💡 Tip: Export cookies or close browser and try again")

        except subprocess.TimeoutExpired:
            logger.warning("   ⚠️  Timeout - try with fewer videos")
        except Exception as e:
            logger.error(f"   ❌ Error fetching history: {e}")

        return videos

    def fetch_youtube_channel(self, channel_url: Optional[str] = None, max_videos: int = 100) -> List[Dict[str, Any]]:
        """Fetch videos from your YouTube channel"""
        logger.info("📺 Fetching YouTube Channel Videos...")

        if not channel_url:
            logger.warning("   ⚠️  No channel URL provided")
            logger.info("   💡 Provide channel URL or channel ID")
            return []

        if not self.check_yt_dlp_available():
            logger.warning("   ⚠️  yt-dlp not available")
            return []

        videos = []

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

            logger.info(f"   Executing: yt-dlp channel {channel_url} (max {max_videos} videos)")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if '|' in line:
                        parts = line.split('|')
                        if len(parts) >= 3:
                            video = {
                                "video_id": parts[0],
                                "title": parts[1] if len(parts) > 1 else "Unknown",
                                "channel": parts[2] if len(parts) > 2 else "Unknown",
                                "channel_id": parts[3] if len(parts) > 3 else "",
                                "upload_date": parts[4] if len(parts) > 4 else "",
                                "duration": parts[5] if len(parts) > 5 else "",
                                "view_count": parts[6] if len(parts) > 6 else "0",
                                "source": "youtube_channel",
                                "fetched_at": datetime.now().isoformat()
                            }
                            videos.append(video)

                logger.info(f"   ✅ Fetched {len(videos)} videos from channel")
            else:
                logger.warning(f"   ⚠️  yt-dlp failed: {result.stderr[:200]}")

        except subprocess.TimeoutExpired:
            logger.warning("   ⚠️  Timeout")
        except Exception as e:
            logger.error(f"   ❌ Error fetching channel: {e}")

        return videos

    def process_videos_to_holocron(self, videos: List[Dict[str, Any]], category: str = "ai_news") -> int:
        """
        Process videos to Holocron

        IMPORTANT: Only processes NEW or UPDATED videos.
        Does NOT reprocess videos that have already been processed.
        """
        logger.info(f"🔮 Processing videos to Holocron ({category})...")
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
                    holocron_entry = processor.process_curated_video(video, category)
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

    def fetch_and_process_all(self, channel_url: Optional[str] = None, history_days: int = 90, max_history_videos: Optional[int] = None, max_recommended_videos: Optional[int] = None, max_channel_videos: Optional[int] = None, use_dynamic_scaling: bool = True) -> Dict[str, Any]:
        """
        Fetch and process ALL YouTube videos NOW

        Args:
            channel_url: Your YouTube channel URL (optional)
            history_days: Number of days to look back (default: 90)
            max_history_videos: Maximum history videos to fetch (None = auto from dynamic scaling)
            max_recommended_videos: Maximum recommended videos to fetch (None = auto from dynamic scaling)
            max_channel_videos: Maximum channel videos to fetch (None = auto from dynamic scaling)
            use_dynamic_scaling: Use dynamic scaling to calculate optimal parameters (default: True)

        Returns:
            Processing results
        """
        logger.info("=" * 80)
        logger.info("🎯 FETCHING AND PROCESSING ALL YOUTUBE VIDEOS NOW")
        logger.info("=" * 80)
        logger.info("")

        # Get dynamic scaling parameters if enabled
        if use_dynamic_scaling:
            try:
                from youtube_dynamic_scaling import YouTubeDynamicScaling
                scaler = YouTubeDynamicScaling(self.project_root)
                scaling_params = scaler.get_scaling_parameters()

                # Use dynamic scaling parameters if not explicitly provided
                if max_history_videos is None:
                    max_history_videos = scaling_params.max_history_videos
                if max_recommended_videos is None:
                    max_recommended_videos = scaling_params.max_recommended_videos
                if max_channel_videos is None:
                    max_channel_videos = scaling_params.max_channel_videos

                logger.info("📈 Dynamic Scaling Active")
                logger.info(f"   Activity Level: {scaling_params.activity_level}")
                logger.info(f"   Scaling Factor: {scaling_params.scaling_factor:.2f}x")
                logger.info(f"   Max History: {max_history_videos} videos")
                logger.info(f"   Max Recommended: {max_recommended_videos} videos")
                logger.info(f"   Max Channel: {max_channel_videos} videos")
                logger.info("")
            except ImportError:
                logger.warning("   ⚠️  Dynamic scaling not available, using defaults")
                if max_history_videos is None:
                    max_history_videos = 500
                if max_recommended_videos is None:
                    max_recommended_videos = 100
                if max_channel_videos is None:
                    max_channel_videos = 100
        else:
            # Use defaults if not provided
            if max_history_videos is None:
                max_history_videos = 500
            if max_recommended_videos is None:
                max_recommended_videos = 100
            if max_channel_videos is None:
                max_channel_videos = 100

            results = {
            "timestamp": datetime.now().isoformat(),
            "recommended_feed": {"fetched": 0, "processed": 0},
            "90_day_history": {"fetched": 0, "processed": 0},  # Updated from 30_day_history
            "youtube_channel": {"fetched": 0, "processed": 0},
            "total_fetched": 0,
            "total_processed": 0,
            "history_window_days": history_days  # Configurable window
        }

        # 1. Fetch Recommended Feed
        logger.info("STEP 1: Fetching Recommended Feed")
        logger.info("-" * 80)
        recommended_videos = self.fetch_recommended_feed(max_videos=max_recommended_videos)
        results["recommended_feed"]["fetched"] = len(recommended_videos)

        if recommended_videos:
            # Save recommended feed
            recommended_file = self.youtube_dir / "recommended_feed.json"
            with open(recommended_file, 'w', encoding='utf-8') as f:
                json.dump(recommended_videos, f, indent=2, ensure_ascii=False)
            logger.info(f"   ✅ Saved to: {recommended_file}")

            # Process to Holocron
            processed = self.process_videos_to_holocron(recommended_videos, category="ai_news")
            results["recommended_feed"]["processed"] = processed

        logger.info("")

        # 2. Fetch History (configurable days, default 90)
        logger.info(f"STEP 2: Fetching {history_days}-Day Watch History")
        logger.info("-" * 80)
        history_videos = self.fetch_30_day_history(max_videos=max_history_videos, days=history_days)
        results["90_day_history"]["fetched"] = len(history_videos)

        if history_videos:
            # Save history
            history_file = self.syphon_dir / "watch_history_90_days.json"
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history_videos, f, indent=2, ensure_ascii=False)
            logger.info(f"   ✅ Saved to: {history_file}")

            # Process to Holocron
            processed = self.process_videos_to_holocron(history_videos, category="ai_news")
            results["90_day_history"]["processed"] = processed

        logger.info("")

        # 3. Fetch YouTube Channel (if URL provided)
        if channel_url:
            logger.info("STEP 3: Fetching YouTube Channel")
            logger.info("-" * 80)
            channel_videos = self.fetch_youtube_channel(channel_url, max_videos=max_channel_videos)
            results["youtube_channel"]["fetched"] = len(channel_videos)

            if channel_videos:
                # Save channel videos
                channel_file = self.youtube_dir / "channel_videos.json"
                with open(channel_file, 'w', encoding='utf-8') as f:
                    json.dump(channel_videos, f, indent=2, ensure_ascii=False)
                logger.info(f"   ✅ Saved to: {channel_file}")

                # Process to Holocron
                processed = self.process_videos_to_holocron(channel_videos, category="lumina_youtube_account")
                results["youtube_channel"]["processed"] = processed

        logger.info("")

        # Calculate totals
        results["total_fetched"] = (
            results["recommended_feed"]["fetched"] +
            results["90_day_history"]["fetched"] +
            results["youtube_channel"]["fetched"]
        )
        results["total_processed"] = (
            results["recommended_feed"]["processed"] +
            results["90_day_history"]["processed"] +
            results["youtube_channel"]["processed"]
        )

        # Summary
        logger.info("=" * 80)
        logger.info("📊 FETCHING AND PROCESSING SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Recommended Feed: {results['recommended_feed']['fetched']} fetched, {results['recommended_feed']['processed']} processed")
        logger.info(f"90-Day History: {results['90_day_history']['fetched']} fetched, {results['90_day_history']['processed']} processed")
        logger.info(f"YouTube Channel: {results['youtube_channel']['fetched']} fetched, {results['youtube_channel']['processed']} processed")
        logger.info("")
        logger.info(f"Total: {results['total_fetched']} videos fetched, {results['total_processed']} processed to Holocron")
        logger.info("=" * 80)

        # Record activity for dynamic scaling
        if use_dynamic_scaling:
            try:
                from youtube_dynamic_scaling import YouTubeDynamicScaling
                scaler = YouTubeDynamicScaling(self.project_root)
                scaler.record_activity(
                    videos_fetched=results['total_fetched'],
                    videos_processed=results['total_processed'],
                    days=history_days
                )
                logger.info("   📊 Activity recorded for dynamic scaling")
            except Exception as e:
                logger.debug(f"   Could not record activity: {e}")

        # Save results
        results_file = self.data_dir / "youtube_fetch_results" / f"fetch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Results saved: {results_file}")

        return results


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Fetch and Process ALL YouTube Videos NOW")
    parser.add_argument("--channel", help="Your YouTube channel URL or ID")
    parser.add_argument("--max-recommended", type=int, default=100, help="Max recommended videos")
    parser.add_argument("--max-history", type=int, default=500, help="Max history videos (increased for 90-day window)")
    parser.add_argument("--history-days", type=int, default=90, help="Number of days to look back in history (default: 90)")

    args = parser.parse_args()

    fetcher = FetchAndProcessYouTubeNow()
    results = fetcher.fetch_and_process_all(
        channel_url=args.channel,
        history_days=args.history_days,
        max_history_videos=args.max_history,
        max_recommended_videos=args.max_recommended,
        max_channel_videos=100  # Default channel limit
    )

    logger.info("")
    logger.info("✅ Fetching and processing complete")
    logger.info(f"   📊 {results['total_fetched']} videos fetched")
    logger.info(f"   🔮 {results['total_processed']} videos processed to Holocron")


if __name__ == "__main__":


    main()