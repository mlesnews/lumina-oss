#!/usr/bin/env python3
"""
Import All Major Star Wars YouTube Content Creators

Uses IDM-CLI and SYPHON to import complete YouTube channels from major Star Wars content creators.
Integrates with YouTube Deep Crawl & SME Mapper system.

@SYPHON @YOUTUBE @STARWARS @IDM-CLI @SOURCES #IMPORT #FUTURE-TODO
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("StarWarsYouTubeImport")

try:
    from scripts.python.idm_cli_web_crawler import IDMCLIWebCrawler
    from scripts.python.syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier
    from scripts.python.syphon.models import DataSourceType
    from scripts.python.r5_living_context_matrix import R5LivingContextMatrix
    from scripts.python.master_todo_tracker import MasterTodoTracker, TaskStatus
    from scripts.python.jarvis_progress_tracker import get_progress_tracker
    SYSTEMS_AVAILABLE = True
except ImportError as e:
    logger.error(f"⚠️  Import error: {e}")
    SYSTEMS_AVAILABLE = False


class StarWarsYouTubeImporter:
    """
    Import all major Star Wars YouTube content creators using IDM-CLI and SYPHON.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)

        if not SYSTEMS_AVAILABLE:
            raise RuntimeError("Required systems for Star Wars YouTube Import not available.")

        # Load channel configuration
        config_file = self.project_root / "config" / "star_wars_youtube_channels.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.channels = config.get("star_wars_youtube_channels", {}).get("channels", [])
                self.import_settings = config.get("star_wars_youtube_channels", {}).get("import_settings", {})
        else:
            logger.warning("⚠️  Star Wars channels config not found, using defaults")
            self.channels = []
            self.import_settings = {
                "max_videos_per_channel": 500,
                "use_idm_cli": True,
                "fallback_to_ytdlp": True,
                "extract_transcripts": True,
                "extract_intelligence": True,
                "ingest_to_r5": True,
                "map_smes": True,
                "accessibility_mode": True
            }

        self.idm_crawler = IDMCLIWebCrawler(project_root=self.project_root)
        self.syphon = SYPHONSystem(SYPHONConfig(
            project_root=self.project_root,
            subscription_tier=SubscriptionTier.ENTERPRISE
        ))
        self.r5 = R5LivingContextMatrix(project_root=self.project_root)
        self.todo_tracker = MasterTodoTracker(project_root=self.project_root)
        self.progress_tracker = get_progress_tracker(project_root=self.project_root, mode="bau")

        logger.info("✅ Star Wars YouTube Importer initialized")
        logger.info(f"   Channels configured: {len(self.channels)}")

    def import_all_channels(self, force_reimport: bool = False) -> Dict[str, Any]:
        """
        Import all configured Star Wars YouTube channels.

        Args:
            force_reimport: If True, reimport even if already imported

        Returns:
            Import results summary
        """
        logger.info("=" * 80)
        logger.info("🎬 STAR WARS YOUTUBE CHANNELS IMPORT")
        logger.info("=" * 80)
        logger.info(f"   Channels to import: {len(self.channels)}")
        logger.info(f"   Max videos per channel: {self.import_settings.get('max_videos_per_channel', 500)}")
        logger.info(f"   Use IDM-CLI: {self.import_settings.get('use_idm_cli', True)}")
        logger.info("")

        results = {
            "started_at": datetime.now().isoformat(),
            "channels_processed": 0,
            "channels_successful": 0,
            "channels_failed": 0,
            "total_videos_imported": 0,
            "total_transcripts_extracted": 0,
            "channel_results": []
        }

        # Find the Star Wars import TODO
        starwars_todo = next(
            (t for t in self.todo_tracker.get_todos() 
             if "Star Wars" in t.title and "YouTube" in t.title),
            None
        )

        if starwars_todo:
            self.todo_tracker.update_status(starwars_todo.id, TaskStatus.IN_PROGRESS)
            logger.info(f"✅ Updated TODO status to IN_PROGRESS: {starwars_todo.title}")

        # Process each channel
        for channel_info in self.channels:
            channel_name = channel_info.get("name", "Unknown")
            channel_url = channel_info.get("url", "")
            priority = channel_info.get("priority", "medium")

            logger.info("")
            logger.info("-" * 80)
            logger.info(f"📺 Processing: {channel_name}")
            logger.info(f"   URL: {channel_url}")
            logger.info(f"   Priority: {priority}")
            logger.info("-" * 80)

            # Register with progress tracker
            import uuid
            process_id = str(uuid.uuid4())
            max_videos = self.import_settings.get("max_videos_per_channel", 500)
            self.progress_tracker.register_process(
                process_id=process_id,
                process_name=f"Star Wars Import",
                source_name=channel_name,
                total_items=max_videos,
                agent_type="jarvis"
            )

            try:
                channel_result = self._import_channel(channel_info, force_reimport, process_id)
                results["channels_processed"] += 1

                if channel_result.get("success"):
                    results["channels_successful"] += 1
                    results["total_videos_imported"] += channel_result.get("items_imported", 0)
                    results["total_transcripts_extracted"] += channel_result.get("transcripts_extracted", 0)
                else:
                    results["channels_failed"] += 1

                results["channel_results"].append({
                    "channel": channel_name,
                    "result": channel_result
                })

            except Exception as e:
                logger.error(f"❌ Error processing {channel_name}: {e}", exc_info=True)
                results["channels_failed"] += 1
                results["channel_results"].append({
                    "channel": channel_name,
                    "result": {"success": False, "error": str(e)}
                })

        results["completed_at"] = datetime.now().isoformat()

        # Update TODO status
        if starwars_todo:
            if results["channels_successful"] > 0:
                self.todo_tracker.update_status(starwars_todo.id, TaskStatus.COMPLETE)
                logger.info(f"✅ Updated TODO status to COMPLETE: {starwars_todo.title}")
            else:
                self.todo_tracker.update_status(starwars_todo.id, TaskStatus.BLOCKED)
                logger.warning(f"⚠️  Updated TODO status to BLOCKED: {starwars_todo.title}")

        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 IMPORT SUMMARY")
        logger.info("=" * 80)
        logger.info(f"   Channels Processed: {results['channels_processed']}")
        logger.info(f"   Channels Successful: {results['channels_successful']}")
        logger.info(f"   Channels Failed: {results['channels_failed']}")
        logger.info(f"   Total Videos Imported: {results['total_videos_imported']}")
        logger.info(f"   Total Transcripts Extracted: {results['total_transcripts_extracted']}")
        logger.info("=" * 80)

        return results

    def _import_channel(self, channel_info: Dict[str, Any], force_reimport: bool = False, process_id: Optional[str] = None) -> Dict[str, Any]:
        """Import a single YouTube channel"""
        channel_url = channel_info.get("url", "")
        channel_name = channel_info.get("name", "Unknown")
        max_videos = self.import_settings.get("max_videos_per_channel", 500)

        # Try IDM-CLI first (Adapt, Improvise, Overcome)
        if self.import_settings.get("use_idm_cli", True):
            try:
                logger.info(f"   🚀 Using IDM-CLI method for channel crawling...")
                channel_result = self.idm_crawler.crawl_youtube_channel(channel_url, max_videos=max_videos)
                videos = channel_result.get("videos", [])

                if videos and len(videos) > 0:
                    logger.info(f"   ✅ IDM-CLI method discovered {len(videos)} videos")
                    result = self._process_videos_with_syphon(videos, channel_info, process_id)
                    if process_id:
                        self.progress_tracker.complete_process(process_id)
                    return result
                else:
                    logger.info(f"   ⚠️  IDM-CLI method found no videos, falling back to yt-dlp")
            except Exception as e:
                logger.warning(f"   ⚠️  IDM-CLI error: {e}, using yt-dlp fallback")

        # Fallback to yt-dlp
        if self.import_settings.get("fallback_to_ytdlp", True):
            logger.info(f"   🔍 Using yt-dlp to discover videos...")
            try:
                import subprocess

                command = [
                    'yt-dlp',
                    '--flat-playlist',
                    '--print', '%(id)s|%(title)s|%(url)s|%(duration)s',
                    channel_url,
                    '--no-download',
                    '--playlist-end', str(max_videos)
                ]

                result = subprocess.run(command, capture_output=True, text=True, timeout=600)
                videos = []

                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if '|' in line:
                            parts = line.split('|', 3)
                            if len(parts) >= 3:
                                video_id = parts[0]
                                title = parts[1]
                                url = parts[2]
                                duration = parts[3] if len(parts) > 3 else "unknown"
                                videos.append({
                                    'id': video_id,
                                    'title': title,
                                    'url': url,
                                    'duration': duration
                                })

                    logger.info(f"   ✅ yt-dlp discovered {len(videos)} videos")
                    result = self._process_videos_with_syphon(videos, channel_info, process_id)
                    if process_id:
                        self.progress_tracker.complete_process(process_id)
                    return result
                else:
                    logger.error(f"   ❌ yt-dlp failed: {result.stderr}")
                    return {"success": False, "error": f"yt-dlp failed: {result.stderr}"}

            except Exception as e:
                logger.error(f"   ❌ yt-dlp error: {e}")
                return {"success": False, "error": str(e)}

        return {"success": False, "error": "No import method available"}

    def _process_videos_with_syphon(self, videos: List[Dict[str, Any]], channel_info: Dict[str, Any], process_id: Optional[str] = None) -> Dict[str, Any]:
        """Process videos with SYPHON extraction"""
        processed = 0
        transcripts_extracted = 0

        channel_name = channel_info.get("name", "Unknown")
        channel_category = channel_info.get("category", "general")

        for i, video in enumerate(videos):
            logger.info(f"   📹 Processing: {video['title'][:60]}...")

            # Update progress
            if process_id:
                self.progress_tracker.update_progress(process_id, i + 1, len(videos))

            try:
                metadata = {
                    "title": video['title'],
                    "source": channel_name,
                    "video_id": video['id'],
                    "url": video['url'],
                    "duration": video.get('duration', 'unknown'),
                    "category": channel_category,
                    "domain": "star_wars",
                    "accessibility_mode": self.import_settings.get("accessibility_mode", True),
                    "extract_transcript": self.import_settings.get("extract_transcripts", True),
                    "sme_mapping": self.import_settings.get("map_smes", True)
                }

                extraction_result = self.syphon.extract(DataSourceType.SOCIAL, video['url'], metadata)

                if extraction_result.success and extraction_result.data:
                    syphon_data = extraction_result.data

                    # Ingest to R5
                    if self.import_settings.get("ingest_to_r5", True):
                        session_id = self.r5.ingest_session({
                            "session_id": f"starwars_{channel_name.lower().replace(' ', '_')}_{video['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            "session_type": "star_wars_youtube_import",
                            "timestamp": datetime.now().isoformat(),
                            "content": f"Title: {video['title']}\nURL: {video['url']}\nDuration: {video.get('duration', 'unknown')}\nChannel: {channel_name}\nCategory: {channel_category}\n\n{syphon_data.content}",
                            "metadata": {
                                **syphon_data.metadata,
                                "source": channel_name,
                                "channel_category": channel_category,
                                "domain": "star_wars",
                                "video_id": video['id'],
                                "accessibility_enabled": self.import_settings.get("accessibility_mode", True),
                                "screen_reader_ready": True,
                                "transcript_available": syphon_data.metadata.get("transcript_available", False),
                                "actionable_items": syphon_data.actionable_items,
                                "tasks": syphon_data.tasks,
                                "intelligence": syphon_data.intelligence
                            }
                        })

                        processed += 1
                        if syphon_data.metadata.get("transcript_available"):
                            transcripts_extracted += 1

            except Exception as e:
                logger.warning(f"      ⚠️  Error processing video: {e}")
                continue

        logger.info(f"   ✅ Imported {processed}/{len(videos)} videos")
        logger.info(f"   📝 Transcripts extracted: {transcripts_extracted}")

        return {
            "success": True,
            "items_imported": processed,
            "total_videos": len(videos),
            "transcripts_extracted": transcripts_extracted,
            "videos": videos[:10]  # Return first 10 for reference
        }


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Import Star Wars YouTube Channels")
        parser.add_argument("--force", action="store_true", help="Force reimport even if already imported")
        parser.add_argument("--channel", help="Import specific channel by name")
        args = parser.parse_args()

        if not SYSTEMS_AVAILABLE:
            logger.error("❌ Required systems not available")
            sys.exit(1)

        importer = StarWarsYouTubeImporter()

        if args.channel:
            # Import specific channel
            channel_info = next((c for c in importer.channels if c.get("name") == args.channel), None)
            if channel_info:
                result = importer._import_channel(channel_info, args.force)
                print(json.dumps(result, indent=2))
            else:
                logger.error(f"❌ Channel not found: {args.channel}")
                sys.exit(1)
        else:
            # Import all channels
            results = importer.import_all_channels(force_reimport=args.force)
            print(json.dumps(results, indent=2))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()