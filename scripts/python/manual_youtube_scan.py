#!/usr/bin/env python3
"""
Manual YouTube Source Scan

Manually trigger a comprehensive YouTube scan for:
- Subscribed channels
- Recommendations feed
- Watch history (used as bookmarks)

Extracts video summaries and intelligence for videos you want to watch later.

Tags: #YOUTUBE #SYPHON #MANUAL_SCAN #EXTERNAL_SOURCES @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

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

logger = get_logger("ManualYouTubeScan")

# Import source sweeps system
from syphon_source_sweeps_scans import SyphonSourceSweepsScans, ScanType, SourceCategory


class ManualYouTubeScanner:
    """Manual YouTube scanner for channels, recommendations, and history"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize manual YouTube scanner"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.sweeps_scans = SyphonSourceSweepsScans(project_root)

        # YouTube data directory
        self.youtube_data_dir = self.project_root / "data" / "syphon_youtube_financial"
        self.youtube_data_dir.mkdir(parents=True, exist_ok=True)

        logger.info("✅ Manual YouTube Scanner initialized")

    def scan_youtube_channels(self, max_videos_per_channel: int = 10) -> Dict[str, Any]:
        """Scan subscribed YouTube channels"""
        logger.info("="*80)
        logger.info("📺 SCANNING YOUTUBE SUBSCRIBED CHANNELS")
        logger.info("="*80)

        try:
            # Try to use existing YouTube SYPHON
            from jarvis_syphon_youtube_financial_creators import SyphonYouTubeFinancialCreators
            youtube_syphon = SyphonYouTubeFinancialCreators(self.project_root)

            # Load subscribed channels
            subscribed_channels = youtube_syphon._load_subscribed_channels()
            logger.info(f"   Found {len(subscribed_channels)} subscribed channels")

            all_intelligence = []
            channels_scanned = 0

            for channel in subscribed_channels[:20]:  # Limit to 20 channels
                try:
                    channel_name = channel.get("name", "Unknown")
                    channel_id = channel.get("channel_id", "")

                    logger.info(f"   📺 Scanning: {channel_name}")

                    # Extract channel content
                    import asyncio
                    channel_results = asyncio.run(youtube_syphon._extract_channel_content(channel))

                    videos = channel_results.get("videos", [])
                    strategies = channel_results.get("strategies", [])

                    # Convert to intelligence format
                    for video in videos[:max_videos_per_channel]:
                        intelligence = {
                            "title": video.get("title", "Untitled Video"),
                            "content": video.get("description", video.get("transcript", "")),
                            "summary": video.get("summary", video.get("description", "")[:500]),
                            "url": f"https://www.youtube.com/watch?v={video.get('video_id', '')}",
                            "source": "youtube_channels",
                            "source_name": "YouTube Subscribed Channels",
                            "timestamp": video.get("published_at", datetime.now().isoformat()),
                            "scan_type": "manual",
                            "channel": channel_name,
                            "channel_id": channel_id,
                            "video_id": video.get("video_id", ""),
                            "duration": video.get("duration", ""),
                            "view_count": video.get("view_count", 0)
                        }
                        all_intelligence.append(intelligence)

                    channels_scanned += 1
                    logger.info(f"      ✅ Found {len(videos)} videos from {channel_name}")

                except Exception as e:
                    logger.error(f"   ❌ Error scanning channel {channel.get('name', 'unknown')}: {e}")
                    continue

            logger.info(f"✅ Scanned {channels_scanned} channels, found {len(all_intelligence)} videos")

            return {
                "channels_scanned": channels_scanned,
                "videos_found": len(all_intelligence),
                "intelligence": all_intelligence
            }

        except ImportError:
            logger.warning("⚠️  YouTube SYPHON not available, using fallback method")
            return self._scan_youtube_fallback("channels")

    def scan_youtube_recommendations(self, max_videos: int = 50) -> Dict[str, Any]:
        """Scan YouTube recommendations feed"""
        logger.info("="*80)
        logger.info("📺 SCANNING YOUTUBE RECOMMENDATIONS")
        logger.info("="*80)

        try:
            # Try to use YouTube account data syphon
            from syphon_youtube_account_data import YouTubeAccountSyphon
            account_syphon = YouTubeAccountSyphon(self.project_root)

            # Get recommendations
            account_data = account_syphon.extract_account_data()
            recommendations = account_data.get("recommendations", [])

            logger.info(f"   Found {len(recommendations)} recommendations")

            all_intelligence = []

            for rec in recommendations[:max_videos]:
                intelligence = {
                    "title": rec.get("title", "Untitled Video"),
                    "content": rec.get("description", ""),
                    "summary": rec.get("description", "")[:500] if rec.get("description") else "",
                    "url": f"https://www.youtube.com/watch?v={rec.get('video_id', '')}",
                    "source": "youtube_recommendations",
                    "source_name": "YouTube Recommendations",
                    "timestamp": rec.get("published_at", datetime.now().isoformat()),
                    "scan_type": "manual",
                    "channel": rec.get("channel_title", ""),
                    "video_id": rec.get("video_id", ""),
                    "view_count": rec.get("view_count", 0)
                }
                all_intelligence.append(intelligence)

            logger.info(f"✅ Found {len(all_intelligence)} recommendation videos")

            return {
                "videos_found": len(all_intelligence),
                "intelligence": all_intelligence
            }

        except ImportError:
            logger.warning("⚠️  YouTube Account SYPHON not available, using fallback")
            return self._scan_youtube_fallback("recommendations")

    def scan_youtube_history(self, max_videos: int = 100) -> Dict[str, Any]:
        """Scan YouTube watch history (used as bookmarks)"""
        logger.info("="*80)
        logger.info("📺 SCANNING YOUTUBE WATCH HISTORY (BOOKMARKS)")
        logger.info("="*80)

        try:
            # Use watch history syphon
            from syphon_youtube_watch_history_30_days import YouTubeWatchHistorySyphon
            history_syphon = YouTubeWatchHistorySyphon(self.project_root, days=90)

            # Check available methods
            methods = history_syphon.check_access_methods()
            logger.info(f"   Available methods: {methods}")

            videos = []

            # Try cookies file first
            if methods.get("cookies_file"):
                logger.info("   Using cookies file method...")
                videos = history_syphon.syphon_via_cookies_file(max_videos=max_videos)
            # Try browser cookies
            elif methods.get("browser_edge"):
                logger.info("   Using Edge browser cookies...")
                videos = history_syphon.syphon_via_browser("edge", max_videos=max_videos)
            elif methods.get("browser_chrome"):
                logger.info("   Using Chrome browser cookies...")
                videos = history_syphon.syphon_via_browser("chrome", max_videos=max_videos)
            # Try takeout file
            elif methods.get("takeout_file"):
                logger.info("   Using Google Takeout file...")
                videos = history_syphon.syphon_via_takeout(max_videos=max_videos)

            if not videos:
                logger.warning("   ⚠️  No videos found - may need to export cookies or use Google Takeout")
                return {"videos_found": 0, "intelligence": []}

            logger.info(f"   Found {len(videos)} videos in history")

            # Convert to intelligence format
            all_intelligence = []

            for video in videos[:max_videos]:
                # Get video details using yt-dlp
                video_details = self._get_video_details(video.get("video_id", ""))

                intelligence = {
                    "title": video.get("title", video_details.get("title", "Untitled Video")),
                    "content": video_details.get("description", ""),
                    "summary": video_details.get("description", "")[:500] if video_details.get("description") else "",
                    "url": f"https://www.youtube.com/watch?v={video.get('video_id', '')}",
                    "source": "youtube_history",
                    "source_name": "YouTube Watch History (Bookmarks)",
                    "timestamp": video.get("watched_at", video.get("syphoned_at", datetime.now().isoformat())),
                    "scan_type": "manual",
                    "channel": video.get("channel", video_details.get("channel", "")),
                    "video_id": video.get("video_id", ""),
                    "duration": video.get("duration", video_details.get("duration", "")),
                    "watched_at": video.get("watched_at", "")
                }
                all_intelligence.append(intelligence)

            logger.info(f"✅ Processed {len(all_intelligence)} videos from history")

            return {
                "videos_found": len(all_intelligence),
                "intelligence": all_intelligence
            }

        except ImportError:
            logger.warning("⚠️  YouTube History SYPHON not available, using fallback")
            return self._scan_youtube_fallback("history")

    def _get_video_details(self, video_id: str) -> Dict[str, Any]:
        """Get video details using yt-dlp"""
        if not video_id:
            return {}

        try:
            import subprocess
            import json as json_module

            cmd = [
                "yt-dlp",
                f"https://www.youtube.com/watch?v={video_id}",
                "--skip-download",
                "--print", "%(title)s|%(description)s|%(channel)s|%(duration)s"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0 and '|' in result.stdout:
                parts = result.stdout.strip().split('|')
                return {
                    "title": parts[0] if len(parts) > 0 else "",
                    "description": parts[1] if len(parts) > 1 else "",
                    "channel": parts[2] if len(parts) > 2 else "",
                    "duration": parts[3] if len(parts) > 3 else ""
                }
        except Exception as e:
            logger.debug(f"Could not get video details for {video_id}: {e}")

        return {}

    def _scan_youtube_fallback(self, scan_type: str) -> Dict[str, Any]:
        """Fallback method if YouTube SYPHON not available"""
        logger.info(f"   Using fallback method for {scan_type}")

        # Check for existing YouTube data files
        youtube_files = list(self.youtube_data_dir.glob("*.json"))

        if youtube_files:
            # Use most recent file
            latest_file = sorted(youtube_files, key=lambda x: x.stat().st_mtime, reverse=True)[0]
            logger.info(f"   Using existing data from: {latest_file.name}")

            try:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    # Extract intelligence from existing data
                    all_intelligence = []

                    if isinstance(data, dict):
                        # Extract from various data structures
                        videos = data.get("videos", data.get("strategies_extracted", []))
                        for video in videos[:50]:
                            intelligence = {
                                "title": video.get("title", "Untitled"),
                                "content": video.get("content", video.get("text", "")),
                                "summary": (video.get("summary", video.get("content", "")) or "")[:500],
                                "url": video.get("url", f"https://www.youtube.com/watch?v={video.get('video_id', '')}"),
                                "source": f"youtube_{scan_type}",
                                "source_name": f"YouTube {scan_type.title()}",
                                "timestamp": video.get("timestamp", datetime.now().isoformat()),
                                "scan_type": "manual"
                            }
                            all_intelligence.append(intelligence)

                    return {
                        "videos_found": len(all_intelligence),
                        "intelligence": all_intelligence
                    }
            except Exception as e:
                logger.error(f"Error reading YouTube data file: {e}")

        return {"videos_found": 0, "intelligence": []}

    def run_full_scan(self, include_channels: bool = True, include_recommendations: bool = True, 
                     include_history: bool = True) -> Dict[str, Any]:
        """Run full YouTube scan"""
        logger.info("="*80)
        logger.info("🎬 MANUAL YOUTUBE SOURCE SCAN")
        logger.info("="*80)
        logger.info("")

        results = {
            "scan_started": datetime.now().isoformat(),
            "channels": {},
            "recommendations": {},
            "history": {},
            "total_intelligence": 0
        }

        # Scan channels
        if include_channels:
            try:
                results["channels"] = self.scan_youtube_channels()
                results["total_intelligence"] += results["channels"].get("videos_found", 0)
                logger.info("")
            except Exception as e:
                logger.error(f"Error scanning channels: {e}")
                results["channels"] = {"error": str(e)}

        # Scan recommendations
        if include_recommendations:
            try:
                results["recommendations"] = self.scan_youtube_recommendations()
                results["total_intelligence"] += results["recommendations"].get("videos_found", 0)
                logger.info("")
            except Exception as e:
                logger.error(f"Error scanning recommendations: {e}")
                results["recommendations"] = {"error": str(e)}

        # Scan history
        if include_history:
            try:
                results["history"] = self.scan_youtube_history()
                results["total_intelligence"] += results["history"].get("videos_found", 0)
                logger.info("")
            except Exception as e:
                logger.error(f"Error scanning history: {e}")
                results["history"] = {"error": str(e)}

        results["scan_completed"] = datetime.now().isoformat()

        # Process all intelligence through source sweeps system
        all_intelligence = []
        all_intelligence.extend(results["channels"].get("intelligence", []))
        all_intelligence.extend(results["recommendations"].get("intelligence", []))
        all_intelligence.extend(results["history"].get("intelligence", []))

        # Filter duplicates and assess value
        new_intelligence = []
        duplicates_skipped = 0
        updates_found = 0
        mission_critical_count = 0
        high_value_count = 0

        for intelligence in all_intelligence:
            is_duplicate, existing_hash, update_type = self.sweeps_scans._check_intelligence_duplicate(
                intelligence, "youtube_manual_scan"
            )

            if is_duplicate:
                duplicates_skipped += 1
            elif update_type:
                new_intelligence.append(intelligence)
                self.sweeps_scans._register_intelligence(intelligence, "youtube_manual_scan", update_type)
                updates_found += 1
            else:
                new_intelligence.append(intelligence)
                self.sweeps_scans._register_intelligence(intelligence, "youtube_manual_scan", "new")

            # Assess intelligence value
            if self.sweeps_scans.intelligence_analyzer:
                assessment = self.sweeps_scans.intelligence_analyzer.assess_intelligence(intelligence)
                if assessment.value.value == "mission_critical":
                    mission_critical_count += 1
                elif assessment.value.value == "high_value":
                    high_value_count += 1

        results["intelligence_processed"] = len(new_intelligence)
        results["duplicates_skipped"] = duplicates_skipped
        results["updates_found"] = updates_found
        results["mission_critical_count"] = mission_critical_count
        results["high_value_count"] = high_value_count

        # Save results
        output_file = self.youtube_data_dir / f"manual_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)

        logger.info("="*80)
        logger.info("✅ MANUAL YOUTUBE SCAN COMPLETE")
        logger.info(f"   Total Videos Found: {results['total_intelligence']}")
        logger.info(f"   New Intelligence: {results['intelligence_processed']}")
        logger.info(f"   Duplicates Skipped: {duplicates_skipped}")
        logger.info(f"   Mission Critical: {mission_critical_count}")
        logger.info(f"   High Value: {high_value_count}")
        logger.info(f"   Results saved to: {output_file}")
        logger.info("="*80)

        return results


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Manual YouTube Source Scan")
    parser.add_argument("--channels-only", action="store_true", help="Scan only subscribed channels")
    parser.add_argument("--recommendations-only", action="store_true", help="Scan only recommendations")
    parser.add_argument("--history-only", action="store_true", help="Scan only watch history")
    parser.add_argument("--no-channels", action="store_true", help="Skip channel scan")
    parser.add_argument("--no-recommendations", action="store_true", help="Skip recommendations scan")
    parser.add_argument("--no-history", action="store_true", help="Skip history scan")

    args = parser.parse_args()

    scanner = ManualYouTubeScanner()

    # Determine what to scan
    include_channels = not args.no_channels and (args.channels_only or not any([
        args.channels_only, args.recommendations_only, args.history_only
    ]))
    include_recommendations = not args.no_recommendations and (args.recommendations_only or not any([
        args.channels_only, args.recommendations_only, args.history_only
    ]))
    include_history = not args.no_history and (args.history_only or not any([
        args.channels_only, args.recommendations_only, args.history_only
    ]))

    scanner.run_full_scan(
        include_channels=include_channels,
        include_recommendations=include_recommendations,
        include_history=include_history
    )


if __name__ == "__main__":


    main()