#!/usr/bin/env python3
"""
Transform Specific YouTube Channels to Holocron Entries

Transforms specific YouTube channels (Star Wars Theory, Dashstar, Badger)
into powerful Holocron entries using the Inception-style transformation system.

Channels:
- Star Wars Theory
- Dashstar
- Badger
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from youtube_deep_crawl_sme_mapper import YouTubeDeepCrawler
    from youtube_to_holocron_transformer import YouTubeToHolocronTransformer
except ImportError as e:
    logger.error(f"❌ Import error: {e}")
    sys.exit(1)

class SpecificChannelTransformer:
    """
    Transform specific YouTube channels to Holocron entries
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize transformer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.crawler = YouTubeDeepCrawler(project_root=project_root)
        self.transformer = YouTubeToHolocronTransformer(project_root=project_root)

        # Channel definitions with direct channel URLs
        # These can be found by visiting the channel and copying the URL
        self.target_channels = {
            "star_wars_theory": {
                "name": "Star Wars Theory",
                "channel_url": "https://www.youtube.com/@StarWarsTheory",  # Modern @handle format
                "alternative_urls": [
                    "https://www.youtube.com/c/StarWarsTheory",
                    "https://www.youtube.com/channel/UCnY0aKk0GKqV1oa_nmKZ3fw",  # Common channel ID
                    "https://www.youtube.com/user/StarWarsTheory"
                ],
                "search_queries": [
                    "Star Wars Theory",
                    "@StarWarsTheory"
                ]
            },
            "dashstar": {
                "name": "Dashstar",
                "channel_url": None,  # Need to find
                "alternative_urls": [],
                "search_queries": [
                    "Dashstar",
                    "@Dashstar",
                    "Dashstar youtube"
                ]
            },
            "badger": {
                "name": "Badger",
                "channel_url": None,  # Need to find - could be "Badger" or "TheRussianBadger"
                "alternative_urls": [],
                "search_queries": [
                    "Badger youtube",
                    "TheRussianBadger",
                    "@TheRussianBadger",
                    "Badger gaming"
                ]
            }
        }

        logger.info("🎯 Specific Channel Transformer initialized")

    def find_channel_by_search(self, channel_name: str, search_queries: List[str]) -> Optional[Dict[str, Any]]:
        """
        Find a channel by searching for it

        Args:
            channel_name: Name of the channel
            search_queries: List of search queries to try

        Returns:
            Channel information dictionary or None
        """
        logger.info(f"🔍 Searching for channel: {channel_name}")

        for query in search_queries:
            try:
                # Use yt-dlp to search for channel
                command = [
                    "yt-dlp",
                    f"ytsearch1:{query}",
                    "--flat-playlist",
                    "--print", "channel",
                    "--print", "channel_id",
                    "--print", "uploader",
                    "--print", "channel_url",
                    "--skip-download"
                ]

                result = subprocess.run(command, capture_output=True, text=True, timeout=30)

                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    channel_info = {}

                    for line in lines:
                        if line.startswith("channel="):
                            channel_info["channel_name"] = line.replace("channel=", "").strip()
                        elif line.startswith("channel_id="):
                            channel_info["channel_id"] = line.replace("channel_id=", "").strip()
                        elif line.startswith("uploader="):
                            channel_info["uploader"] = line.replace("uploader=", "").strip()
                        elif line.startswith("http") and "channel" in line:
                            channel_info["url"] = line.strip()

                    if channel_info.get("channel_id"):
                        # Verify it matches (case-insensitive)
                        found_name = channel_info.get("channel_name", "").lower()
                        target_name = channel_name.lower()
                        if target_name in found_name or found_name in target_name:
                            logger.info(f"✅ Found channel: {channel_info.get('channel_name')}")
                            return channel_info

            except subprocess.TimeoutExpired:
                logger.warning(f"⚠️  Search timeout for query: {query}")
                continue
            except Exception as e:
                logger.warning(f"⚠️  Search error for query {query}: {e}")
                continue

        logger.warning(f"⚠️  Could not find channel: {channel_name}")
        return None

    def find_channel_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract channel information from a known URL

        Args:
            url: YouTube channel URL

        Returns:
            Channel information dictionary or None
        """
        logger.info(f"🔍 Extracting channel info from URL: {url}")

        try:
            # Try to get channel info by listing videos from the channel
            # Add /videos to channel URL if it's a channel URL
            if "/channel/" in url or "/@" in url or "/c/" in url or "/user/" in url:
                if not url.endswith("/videos"):
                    test_url = url.rstrip("/") + "/videos"
                else:
                    test_url = url
            else:
                test_url = url

            command = [
                "yt-dlp",
                test_url,
                "--flat-playlist",
                "--playlist-end", "1",  # Just get first video to extract channel info
                "--print", "%(channel)s",
                "--print", "%(channel_id)s",
                "--print", "%(uploader)s",
                "--print", "%(channel_url)s",
                "--skip-download",
                "--quiet"
            ]

            result = subprocess.run(command, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                output = result.stdout.strip()
                lines = output.split('\n')

                channel_info = {}
                for line in lines:
                    if line and not line.startswith("http") and not line.startswith("WARNING"):
                        # Try to extract channel name (usually first non-empty line)
                        if not channel_info.get("channel_name") and line.strip():
                            channel_info["channel_name"] = line.strip()

                # If we got channel name, try to get channel ID with a different approach
                if channel_info.get("channel_name"):
                    # Try getting channel ID by searching for channel
                    search_command = [
                        "yt-dlp",
                        f"ytsearch1:{channel_info['channel_name']}",
                        "--flat-playlist",
                        "--print", "%(channel_id)s",
                        "--print", "%(channel_url)s",
                        "--skip-download",
                        "--quiet"
                    ]

                    search_result = subprocess.run(search_command, capture_output=True, text=True, timeout=30)
                    if search_result.returncode == 0:
                        search_output = search_result.stdout.strip()
                        for line in search_output.split('\n'):
                            if line.startswith("UC") and len(line) == 24:  # YouTube channel ID format
                                channel_info["channel_id"] = line.strip()
                            elif "youtube.com" in line:
                                channel_info["url"] = line.strip()

                # If still no channel_id, try extracting from URL
                if not channel_info.get("channel_id"):
                    if "/channel/" in url:
                        channel_id = url.split("/channel/")[1].split("/")[0].split("?")[0]
                        if channel_id.startswith("UC") and len(channel_id) == 24:
                            channel_info["channel_id"] = channel_id

                if channel_info.get("channel_id") or channel_info.get("channel_name"):
                    if not channel_info.get("url"):
                        channel_info["url"] = url
                    logger.info(f"✅ Extracted channel info: {channel_info.get('channel_name', 'Unknown')}")
                    return channel_info
            else:
                logger.debug(f"yt-dlp output: {result.stderr}")

        except subprocess.TimeoutExpired:
            logger.warning(f"⚠️  Timeout extracting from URL: {url}")
        except Exception as e:
            logger.warning(f"⚠️  Error extracting from URL {url}: {e}")

        return None

    def process_channel(self, channel_key: str, channel_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a specific channel: find it, crawl it, and transform it

        Args:
            channel_key: Channel key (e.g., "star_wars_theory")
            channel_config: Channel configuration dictionary

        Returns:
            Holocron entry dictionary or None
        """
        channel_name = channel_config["name"]
        logger.info(f"\n{'='*80}")
        logger.info(f"🎯 Processing Channel: {channel_name}")
        logger.info(f"{'='*80}")

        # Step 1: Find channel
        channel_info = {}

        # Extract channel ID from URL
        primary_url = channel_config.get("channel_url") or channel_config.get("url")
        if primary_url:
            # If it's a channel ID URL, extract directly
            if "/channel/" in primary_url:
                channel_id = primary_url.split("/channel/")[1].split("/")[0].split("?")[0]
                if channel_id.startswith("UC") and len(channel_id) == 24:
                    channel_info["channel_id"] = channel_id
                    channel_info["channel_name"] = channel_name
                    channel_info["url"] = primary_url
                    logger.info(f"✅ Extracted channel ID from URL: {channel_id}")
            # If it's an @handle URL, extract channel ID directly from first video
            elif "/@" in primary_url:
                handle = primary_url.split("/@")[1].split("/")[0].split("?")[0]
                channel_info["channel_name"] = channel_name
                channel_info["url"] = primary_url
                logger.info(f"✅ Detected @handle URL: @{handle}, extracting channel ID...")

                # Extract channel ID from @handle URL by getting first video metadata (not flat-playlist)
                try:
                    import subprocess
                    test_url = primary_url.rstrip("/") + "/videos"
                    command = [
                        "yt-dlp",
                        test_url,
                        "--playlist-end", "1",  # Get first video (not flat-playlist to get metadata)
                        "--print", "%(channel_id)s",
                        "--skip-download",
                        "--quiet"
                    ]
                    result = subprocess.run(command, capture_output=True, text=True, timeout=60)
                    if result.returncode == 0:
                        for line in result.stdout.strip().split('\n'):
                            line = line.strip()
                            if line and line.startswith("UC") and len(line) == 24:
                                channel_info["channel_id"] = line
                                logger.info(f"✅ Extracted channel ID from @handle: {line}")
                                break
                except Exception as e:
                    logger.debug(f"Could not pre-extract channel ID from @handle: {e}, will extract during crawl")

        # If we don't have channel info yet, try finding it
        if not channel_info.get("channel_id"):
            # Try primary channel URL first
            if primary_url:
                found_info = self.find_channel_by_url(primary_url)
                if found_info:
                    channel_info.update(found_info)

            # Try alternative URLs
            if not channel_info.get("channel_id"):
                for url in channel_config.get("alternative_urls", []):
                    found_info = self.find_channel_by_url(url)
                    if found_info and found_info.get("channel_id"):
                        channel_info.update(found_info)
                        break

            # If not found, try search
            if not channel_info.get("channel_id"):
                found_info = self.find_channel_by_search(channel_name, channel_config.get("search_queries", []))
                if found_info:
                    channel_info.update(found_info)

        # Always use the provided channel name from config
        if channel_info:
            channel_info["channel_name"] = channel_name

        if not channel_info.get("channel_id"):
            logger.error(f"❌ Could not find channel ID for: {channel_name}")
            return None

        # Step 2: Crawl channel
        logger.info(f"🕷️  Crawling channel: {channel_info.get('channel_name')}")
        channel_id = channel_info.get("channel_id")
        if not channel_id:
            logger.error(f"❌ No channel ID found for: {channel_name}")
            return None

        videos = self.crawler.crawl_channel(channel_id, max_videos=None)  # Get ALL videos

        # If no videos found, try direct URL crawl as fallback
        if not videos:
            logger.info(f"🔄 Trying direct URL crawl fallback for: {channel_name}")
            channel_url = channel_config.get("channel_url") or channel_info.get("url")
            if channel_url:
                try:
                    import subprocess
                    crawl_url = channel_url.rstrip("/") + "/videos"

                    # First, extract channel_id from first video (full metadata, not flat-playlist)
                    if not channel_info.get("channel_id"):
                        try:
                            quick_cmd = [
                                "yt-dlp",
                                crawl_url,
                                "--playlist-end", "1",  # Just first video, full metadata
                                "--print", "%(channel_id)s",
                                "--skip-download",
                                "--quiet"
                            ]
                            quick_result = subprocess.run(quick_cmd, capture_output=True, text=True, timeout=60)
                            if quick_result.returncode == 0:
                                for line in quick_result.stdout.strip().split('\n'):
                                    line = line.strip()
                                    if line and line.startswith("UC") and len(line) == 24:
                                        channel_info["channel_id"] = line
                                        logger.info(f"✅ Extracted channel ID from first video: {line}")
                                        break
                        except Exception as e:
                            logger.debug(f"Could not extract channel_id from first video: {e}")

                    # Now crawl all videos using flat-playlist (faster, but no channel_id in output)
                    command = [
                        "yt-dlp",
                        crawl_url,
                        "--flat-playlist",
                        "--print", "%(id)s",
                        "--print", "%(title)s",
                        "--print", "%(duration)s",
                        "--print", "%(view_count)s",
                        "--print", "%(upload_date)s",
                        "--print", "%(url)s",
                        "--skip-download",
                        "--quiet"
                    ]

                    result = subprocess.run(command, capture_output=True, text=True, timeout=1800)

                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        current_video = {}

                        for line in lines:
                            if line.startswith("http"):
                                current_video["url"] = line.strip()
                                if current_video.get("video_id"):
                                    videos.append(current_video.copy())
                                current_video = {}
                            elif len(line) == 11 and not line.startswith("http"):
                                current_video["video_id"] = line.strip()
                            elif line and not line.startswith("http") and len(line) != 11:
                                if "title" not in current_video:
                                    current_video["title"] = line.strip()
                                elif "duration" not in current_video:
                                    current_video["duration"] = line.strip()
                                elif "view_count" not in current_video:
                                    current_video["view_count"] = line.strip()
                                elif "upload_date" not in current_video:
                                    current_video["upload_date"] = line.strip()

                        logger.info(f"✅ Found {len(videos)} videos via direct URL crawl")
                except Exception as e:
                    logger.warning(f"⚠️  Direct URL crawl fallback failed: {e}")

        if not videos:
            logger.warning(f"⚠️  No videos found for channel: {channel_name}")
            return None

        logger.info(f"✅ Crawled {len(videos)} videos from {channel_name}")

        # Step 3: Identify SME
        logger.info(f"🔍 Identifying SME profile for: {channel_name}")
        sme_profile = self.crawler.identify_sme(channel_info, videos)

        logger.info(f"✅ SME Profile:")
        logger.info(f"   Tier: {sme_profile.get('sme_tier', 'unknown').upper()}")
        logger.info(f"   Score: {sme_profile.get('sme_score', 0)}/3")
        logger.info(f"   Videos: {sme_profile.get('video_count', 0)}")
        logger.info(f"   Total Views: {sme_profile.get('total_views', 0):,}")

        # Step 4: Transform to Holocron
        logger.info(f"🔮 Transforming to Holocron (Inception Mode)...")
        try:
            holocron_entry = self.transformer.transform_sme_to_holocron(sme_profile)
            logger.info(f"✅ Holocron created: {holocron_entry['entry_id']}")
            return holocron_entry
        except Exception as e:
            logger.error(f"❌ Error transforming to Holocron: {e}")
            return None

    def process_all_target_channels(self) -> List[Dict[str, Any]]:
        """Process all target channels"""
        logger.info(f"\n{'='*80}")
        logger.info(f"🚀 STARTING SPECIFIC CHANNEL TRANSFORMATION")
        logger.info(f"{'='*80}")

        holocrons = []

        for channel_key, channel_config in self.target_channels.items():
            try:
                holocron = self.process_channel(channel_key, channel_config)
                if holocron:
                    holocrons.append(holocron)
            except Exception as e:
                logger.error(f"❌ Error processing {channel_config['name']}: {e}")

        # Save Holocron index
        self.transformer._save_holocron_index()

        logger.info(f"\n{'='*80}")
        logger.info(f"✅ TRANSFORMATION COMPLETE")
        logger.info(f"{'='*80}")
        logger.info(f"🔮 {len(holocrons)} channels transformed into Holocrons")
        logger.info(f"   Knowledge power granted! ⚡📚")

        return holocrons

    def generate_report(self, holocrons: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate transformation report"""
        report = {
            "transformation_timestamp": datetime.now().isoformat(),
            "channels_processed": len(self.target_channels),
            "holocrons_created": len(holocrons),
            "channels": []
        }

        for holocron in holocrons:
            channel_report = {
                "channel_name": holocron.get("source", {}).get("channel_name"),
                "holocron_id": holocron.get("entry_id"),
                "sme_tier": holocron.get("metadata", {}).get("sme_tier"),
                "sme_score": holocron.get("metadata", {}).get("sme_score"),
                "video_count": holocron.get("metadata", {}).get("video_count"),
                "total_views": holocron.get("metadata", {}).get("total_views"),
                "domain": holocron.get("domain"),
                "priority": holocron.get("priority"),
                "location": holocron.get("location")
            }
            report["channels"].append(channel_report)

        return report

def main():
    """Main execution"""
    transformer = SpecificChannelTransformer()

    import argparse
    parser = argparse.ArgumentParser(description="Transform Specific Channels to Holocrons")
    parser.add_argument("--report", action="store_true", help="Generate transformation report")
    parser.add_argument("--channel", choices=["star_wars_theory", "dashstar", "badger", "all"], 
                       default="all", help="Channel to process (default: all)")
    parser.add_argument("--url", type=str, help="Direct YouTube channel URL (overrides channel selection)")
    parser.add_argument("--name", type=str, help="Channel name (required when using --url)")

    args = parser.parse_args()

    holocrons = []

    # If URL provided, process that channel directly
    if args.url:
        if not args.name:
            logger.error("❌ --name is required when using --url")
            return

        logger.info(f"🎯 Processing custom channel from URL: {args.url}")
        channel_info = transformer.find_channel_by_url(args.url)

        if channel_info:
            # Create a temporary channel config
            channel_config = {
                "name": args.name,
                "channel_url": args.url
            }

            # Use the channel info we found
            channel_info["channel_name"] = args.name

            # Process the channel - try with URL directly if channel_id method fails
            channel_id = channel_info.get("channel_id")
            videos = []

            if channel_id:
                videos = transformer.crawler.crawl_channel(channel_id, max_videos=None)  # Get ALL videos

            # If no videos found, try crawling with the URL directly
            if not videos and args.url:
                logger.info(f"🔄 Trying direct URL crawl: {args.url}/videos")
                try:
                    import subprocess
                    channel_url = args.url.rstrip("/") + "/videos"
                    command = [
                        "yt-dlp",
                        channel_url,
                        "--flat-playlist",
                        "--print", "%(id)s",
                        "--print", "%(title)s",
                        "--print", "%(duration)s",
                        "--print", "%(view_count)s",
                        "--print", "%(upload_date)s",
                        "--print", "%(url)s",
                        "--skip-download",
                        "--quiet"
                    ]
                    # No --playlist-end limit - gets ALL videos

                    result = subprocess.run(command, capture_output=True, text=True, timeout=1800)  # 30 minutes for full crawl

                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        current_video = {}

                        for line in lines:
                            if line.startswith("http"):
                                current_video["url"] = line.strip()
                                if current_video.get("video_id"):
                                    videos.append(current_video.copy())
                                current_video = {}
                            elif len(line) == 11 and not line.startswith("http"):  # Video ID format
                                current_video["video_id"] = line.strip()
                            elif line and not line.startswith("http"):
                                if "title" not in current_video:
                                    current_video["title"] = line.strip()
                                elif "duration" not in current_video:
                                    current_video["duration"] = line.strip()
                                elif "view_count" not in current_video:
                                    current_video["view_count"] = line.strip()
                                elif "upload_date" not in current_video:
                                    current_video["upload_date"] = line.strip()

                        logger.info(f"✅ Found {len(videos)} videos via direct URL crawl")
                except Exception as e:
                    logger.warning(f"⚠️  Direct URL crawl failed: {e}")

            if videos:
                sme_profile = transformer.crawler.identify_sme(channel_info, videos)
                holocron = transformer.transformer.transform_sme_to_holocron(sme_profile)
                holocrons.append(holocron)
                transformer.transformer._save_holocron_index()
                logger.info(f"✅ Holocron created: {holocron['entry_id']}")
            else:
                logger.error("❌ Could not extract videos from channel")
        else:
            logger.error("❌ Could not extract channel information from URL")

    # Otherwise process predefined channels
    elif args.channel == "all":
        holocrons = transformer.process_all_target_channels()
    else:
        channel_config = transformer.target_channels.get(args.channel)
        if channel_config:
            holocron = transformer.process_channel(args.channel, channel_config)
            holocrons = [holocron] if holocron else []
        else:
            logger.error(f"❌ Unknown channel: {args.channel}")

    # Generate report if requested
    if args.report and holocrons:
        report = transformer.generate_report(holocrons)
        report_file = transformer.project_root / "data" / "youtube_intelligence" / f"specific_channels_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n📊 Transformation Report:")
        print(f"   Channels Processed: {report['channels_processed']}")
        print(f"   Holocrons Created: {report['holocrons_created']}")
        print(f"\n   Channels:")
        for channel in report["channels"]:
            print(f"   - {channel['channel_name']}")
            print(f"     Tier: {channel['sme_tier'].upper()}, Score: {channel['sme_score']}/3")
            print(f"     Videos: {channel['video_count']}, Views: {channel['total_views']:,}")
            print(f"     Holocron: {channel['holocron_id']}")
        print(f"\n✅ Report saved: {report_file.name}")

    print(f"\n🎯 Transformation complete: {len(holocrons)} Holocrons created")
    print("   Star Wars Theory, Dashstar, and Badger knowledge power granted! ⚡📚🔮")

if __name__ == "__main__":



    main()