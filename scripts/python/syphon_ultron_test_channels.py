#!/usr/bin/env python3
"""
SYPHON: ULTRON Test Channels - Justin Jack Bear, Nate B Jones & Dave's Garage

Syphons data from YouTube channels to prove ULTRON cluster capabilities:
- https://www.youtube.com/@justinjackbear
- https://www.youtube.com/@NateBJones
- https://www.youtube.com/@DavesGarage

Extracts:
- Channel metadata (name, description, subscriber count, etc.)
- Video listings (titles, IDs, dates, views, etc.)
- Playlists
- Channel intelligence for ULTRON cluster analysis
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from syphon.core import SYPHONConfig, SYPHONSystem
    from syphon.models import DataSourceType
except ImportError:
    logger.warning("SYPHON system not available, using basic extraction")


class ULTRONChannelSyphon:
    """
    SYPHON YouTube channels for ULTRON cluster intelligence
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize channel syphon"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.output_dir = self.project_root / "data" / "syphon" / "ultron_channels"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize SYPHON system if available
        self.syphon_system = None
        try:
            config = SYPHONConfig(
                project_root=self.project_root,
                subscription_tier="premium",
                enable_cache=True
            )
            self.syphon_system = SYPHONSystem(config)
            logger.info("✅ SYPHON system initialized")
        except Exception as e:
            logger.warning(f"⚠️  SYPHON system not available: {e}")

        # Target channels
        self.channels = {
            "justinjackbear": {
                "name": "Justin Jack Bear",
                "url": "https://www.youtube.com/@justinjackbear",
                "handle": "@justinjackbear"
            },
            "natebjones": {
                "name": "Nate B Jones",
                "url": "https://www.youtube.com/@NateBJones",
                "handle": "@NateBJones"
            },
            "davesgarage": {
                "name": "Dave's Garage",
                "url": "https://www.youtube.com/@DavesGarage",
                "handle": "@DavesGarage"
            }
        }

        logger.info("🚀 ULTRON Channel Syphon initialized")

    def check_yt_dlp(self) -> bool:
        """Check if yt-dlp is available"""
        try:
            result = subprocess.run(
                ["yt-dlp", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"✅ yt-dlp available: {result.stdout.strip()}")
                return True
        except Exception as e:
            logger.error(f"❌ yt-dlp not available: {e}")
            logger.error("   Please install: pip install yt-dlp")
            return False
        return False

    def extract_channel_info(self, channel_url: str, channel_key: str) -> Dict[str, Any]:
        """
        Extract channel information using yt-dlp

        Args:
            channel_url: YouTube channel URL
            channel_key: Channel identifier key

        Returns:
            Dictionary with channel information
        """
        logger.info(f"📺 Extracting channel: {channel_url}")

        channel_data = {
            "channel_key": channel_key,
            "channel_url": channel_url,
            "extracted_at": datetime.now().isoformat(),
            "status": "success"
        }

        try:
            # Try lightweight channel info extraction
            logger.info(f"   Attempting lightweight channel info extraction...")

            # Method 1: Try channel about page (faster)
            about_url = f"{channel_url}/about"
            about_cmd = [
                "yt-dlp",
                "--dump-json",
                "--no-warnings",
                "--skip-download",
                "--no-download",
                "--extractor-args", "youtube:player_client=web",
                about_url
            ]

            about_result = subprocess.run(
                about_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if about_result.returncode == 0 and about_result.stdout.strip():
                try:
                    metadata = json.loads(about_result.stdout.strip().split('\n')[0])
                    channel_data.update({
                        "channel_name": metadata.get("channel", metadata.get("uploader", "")),
                        "channel_id": metadata.get("channel_id", ""),
                        "description": metadata.get("description", "")[:500],  # Limit description length
                        "subscriber_count": metadata.get("channel_follower_count", 0),
                        "video_count": metadata.get("channel_video_count", 0),
                        "playlist_count": metadata.get("channel_playlist_count", 0),
                        "channel_url_canonical": metadata.get("channel_url", channel_url),
                        "extraction_method": "channel_about_page"
                    })
                    logger.info(f"   ✅ Channel metadata extracted via about page: {channel_data.get('channel_name', 'Unknown')}")
                except (json.JSONDecodeError, IndexError) as e:
                    logger.warning(f"   ⚠️  Could not parse about page JSON: {e}")

            # If about page didn't work, try basic channel URL
            if not channel_data.get("channel_name"):
                basic_cmd = [
                    "yt-dlp",
                    "--dump-json",
                    "--no-warnings",
                    "--skip-download",
                    "--extractor-args", "youtube:player_client=web",
                    channel_url
                ]

                basic_result = subprocess.run(
                    basic_cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if basic_result.returncode == 0 and basic_result.stdout.strip():
                    try:
                        metadata = json.loads(basic_result.stdout.strip().split('\n')[0])
                        channel_data.update({
                            "channel_name": metadata.get("channel", metadata.get("uploader", "")),
                            "channel_id": metadata.get("channel_id", ""),
                            "description": metadata.get("description", "")[:500],
                            "subscriber_count": metadata.get("channel_follower_count", 0),
                            "video_count": metadata.get("channel_video_count", 0),
                            "playlist_count": metadata.get("channel_playlist_count", 0),
                            "channel_url_canonical": metadata.get("channel_url", channel_url),
                            "extraction_method": "basic_channel_url"
                        })
                        logger.info(f"   ✅ Channel metadata extracted: {channel_data.get('channel_name', 'Unknown')}")
                    except (json.JSONDecodeError, IndexError) as e:
                        logger.warning(f"   ⚠️  Could not parse basic metadata: {e}")

            # Extract video list (last 20 videos - faster)
            videos_cmd = [
                "yt-dlp",
                "--dump-json",
                "--flat-playlist",
                "--no-warnings",
                "--playlist-end", "20",
                "--extractor-args", "youtube:player_client=web",
                f"{channel_url}/videos"
            ]

            videos_result = subprocess.run(
                videos_cmd,
                capture_output=True,
                text=True,
                timeout=90
            )

            videos = []
            if videos_result.returncode == 0:
                for line in videos_result.stdout.strip().split('\n'):
                    if line.strip():
                        try:
                            video_data = json.loads(line)
                            videos.append({
                                "video_id": video_data.get("id", ""),
                                "title": video_data.get("title", ""),
                                "url": video_data.get("url", ""),
                                "duration": video_data.get("duration", 0),
                                "upload_date": video_data.get("upload_date", ""),
                                "view_count": video_data.get("view_count", 0)
                            })
                        except json.JSONDecodeError:
                            continue

                channel_data["videos"] = videos
                channel_data["video_count_extracted"] = len(videos)
                logger.info(f"   ✅ Extracted {len(videos)} videos")

            # Extract playlists (simplified)
            playlists_cmd = [
                "yt-dlp",
                "--dump-json",
                "--flat-playlist",
                "--no-warnings",
                "--extractor-args", "youtube:player_client=web",
                f"{channel_url}/playlists"
            ]

            playlists_result = subprocess.run(
                playlists_cmd,
                capture_output=True,
                text=True,
                timeout=45
            )

            playlists = []
            if playlists_result.returncode == 0:
                for line in playlists_result.stdout.strip().split('\n'):
                    if line.strip():
                        try:
                            playlist_data = json.loads(line)
                            playlists.append({
                                "playlist_id": playlist_data.get("id", ""),
                                "title": playlist_data.get("title", ""),
                                "url": playlist_data.get("url", ""),
                                "video_count": playlist_data.get("playlist_count", 0)
                            })
                        except json.JSONDecodeError:
                            continue

                channel_data["playlists"] = playlists
                channel_data["playlist_count_extracted"] = len(playlists)
                logger.info(f"   ✅ Extracted {len(playlists)} playlists")

        except subprocess.TimeoutExpired:
            logger.error(f"   ❌ Timeout extracting channel data")
            channel_data["status"] = "timeout"
        except Exception as e:
            logger.error(f"   ❌ Error extracting channel: {e}")
            channel_data["status"] = "error"
            channel_data["error"] = str(e)

        return channel_data

    def syphon_all_channels(self) -> Dict[str, Any]:
        try:
            """Syphon all target channels"""
            logger.info("🚀 Starting ULTRON channel syphon operation...")
            logger.info(f"   Target channels: {len(self.channels)}")

            if not self.check_yt_dlp():
                logger.error("❌ yt-dlp not available. Cannot proceed.")
                return {"status": "error", "message": "yt-dlp not available"}

            results = {
                "operation": "ULTRON Channel Syphon",
                "timestamp": datetime.now().isoformat(),
                "channels": {},
                "summary": {}
            }

            for channel_key, channel_info in self.channels.items():
                logger.info(f"\n📺 Processing channel: {channel_info['name']}")
                channel_data = self.extract_channel_info(channel_info["url"], channel_key)

                # Add channel metadata
                channel_data.update({
                    "name": channel_info["name"],
                    "handle": channel_info["handle"]
                })

                results["channels"][channel_key] = channel_data

                # Save individual channel file
                channel_file = self.output_dir / f"{channel_key}_syphon_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(channel_file, 'w', encoding='utf-8') as f:
                    json.dump(channel_data, f, indent=2, ensure_ascii=False)
                logger.info(f"   💾 Saved: {channel_file.name}")

            # Generate summary
            total_videos = sum(
                ch.get("video_count_extracted", 0) 
                for ch in results["channels"].values()
            )
            total_playlists = sum(
                ch.get("playlist_count_extracted", 0)
                for ch in results["channels"].values()
            )

            results["summary"] = {
                "channels_processed": len(results["channels"]),
                "total_videos_extracted": total_videos,
                "total_playlists_extracted": total_playlists,
                "successful_channels": sum(
                    1 for ch in results["channels"].values() 
                    if ch.get("status") == "success"
                ),
                "failed_channels": sum(
                    1 for ch in results["channels"].values() 
                    if ch.get("status") != "success"
                )
            }

            # Save combined results
            results_file = self.output_dir / f"ultron_syphon_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            logger.info(f"\n✅ ULTRON Channel Syphon Complete!")
            logger.info(f"   📊 Summary:")
            logger.info(f"      Channels: {results['summary']['channels_processed']}")
            logger.info(f"      Videos: {results['summary']['total_videos_extracted']}")
            logger.info(f"      Playlists: {results['summary']['total_playlists_extracted']}")
            logger.info(f"      Success: {results['summary']['successful_channels']}")
            logger.info(f"   💾 Results saved: {results_file.name}")

            return results


        except Exception as e:
            self.logger.error(f"Error in syphon_all_channels: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    syphon = ULTRONChannelSyphon()
    results = syphon.syphon_all_channels()

    if results.get("status") == "error":
        sys.exit(1)

    print("\n" + "="*60)
    print("ULTRON CLUSTER CHANNEL SYPHON - COMPLETE")
    print("="*60)
    print(f"Channels: {results['summary']['channels_processed']}")
    print(f"Videos: {results['summary']['total_videos_extracted']}")
    print(f"Playlists: {results['summary']['total_playlists_extracted']}")
    print("="*60)


if __name__ == "__main__":


    main()