#!/usr/bin/env python3
"""
YouTube Processed Video Tracker

Tracks which YouTube videos have been processed to avoid reprocessing.
Only processes videos if there's updated content.

Tags: #YOUTUBE #PROCESSING #TRACKING #NO_REPROCESS @JARVIS @LUMINA
"""

import sys
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
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

logger = get_logger("YouTubeProcessedTracker")


class YouTubeProcessedTracker:
    """
    YouTube Processed Video Tracker

    Tracks processed videos to avoid reprocessing unless content is updated.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize processed video tracker"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "youtube"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Processed videos database
        self.processed_db_file = self.data_dir / "processed_videos.json"
        self.processed_videos: Dict[str, Dict[str, Any]] = {}

        # Load existing processed videos
        self._load_processed_videos()

        logger.info("✅ YouTube Processed Tracker initialized")
        logger.info(f"   Processed videos tracked: {len(self.processed_videos)}")

    def _load_processed_videos(self):
        """Load processed videos database"""
        if self.processed_db_file.exists():
            try:
                with open(self.processed_db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.processed_videos = data.get("processed_videos", {})
                    logger.info(f"   ✅ Loaded {len(self.processed_videos)} processed videos")
            except Exception as e:
                logger.warning(f"   ⚠️  Could not load processed videos: {e}")
                self.processed_videos = {}
        else:
            self.processed_videos = {}

    def _save_processed_videos(self):
        """Save processed videos database"""
        try:
            with open(self.processed_db_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "last_updated": datetime.now().isoformat(),
                    "processed_videos": self.processed_videos
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"   ❌ Error saving processed videos: {e}")

    def _get_video_hash(self, video: Dict[str, Any]) -> str:
        """
        Generate hash for video content to detect updates

        Args:
            video: Video information

        Returns:
            Hash string representing video content
        """
        # Hash based on video ID, title, description, upload_date, duration
        content = f"{video.get('video_id', '')}|{video.get('title', '')}|{video.get('description', '')}|{video.get('upload_date', '')}|{video.get('duration', '')}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def is_video_processed(self, video_id: str) -> bool:
        """
        Check if video has been processed

        Args:
            video_id: YouTube video ID

        Returns:
            True if video has been processed
        """
        return video_id in self.processed_videos

    def has_video_updated(self, video: Dict[str, Any]) -> bool:
        """
        Check if video content has been updated since last processing

        Args:
            video: Video information

        Returns:
            True if video has updated content
        """
        video_id = video.get("video_id", "")
        if not video_id:
            return True  # New video, process it

        if video_id not in self.processed_videos:
            return True  # Not processed yet, process it

        # Compare content hash
        current_hash = self._get_video_hash(video)
        processed_hash = self.processed_videos[video_id].get("content_hash", "")

        return current_hash != processed_hash

    def should_process_video(self, video: Dict[str, Any]) -> bool:
        """
        Determine if video should be processed

        Args:
            video: Video information

        Returns:
            True if video should be processed (new or updated)
        """
        video_id = video.get("video_id", "")
        if not video_id:
            return True  # No ID, process it

        # If not processed, process it
        if not self.is_video_processed(video_id):
            logger.info(f"   📹 New video: {video.get('title', video_id)}")
            return True

        # If content updated, process it
        if self.has_video_updated(video):
            logger.info(f"   🔄 Updated video: {video.get('title', video_id)}")
            return True

        # Already processed and no updates
        logger.debug(f"   ⏭️  Skipping (already processed): {video.get('title', video_id)}")
        return False

    def mark_video_processed(self, video: Dict[str, Any], holocron_entry: Optional[Dict[str, Any]] = None):
        """
        Mark video as processed

        Args:
            video: Video information
            holocron_entry: Holocron entry if created
        """
        video_id = video.get("video_id", "")
        if not video_id:
            return

        content_hash = self._get_video_hash(video)

        self.processed_videos[video_id] = {
            "video_id": video_id,
            "title": video.get("title", ""),
            "processed_at": datetime.now().isoformat(),
            "content_hash": content_hash,
            "upload_date": video.get("upload_date", ""),
            "duration": video.get("duration", ""),
            "holocron_created": holocron_entry is not None
        }

        self._save_processed_videos()

    def filter_new_or_updated_videos(self, videos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter videos to only new or updated ones

        Args:
            videos: List of videos to filter

        Returns:
            List of videos that should be processed
        """
        new_or_updated = []
        skipped = []

        for video in videos:
            if self.should_process_video(video):
                new_or_updated.append(video)
            else:
                skipped.append(video.get("video_id", ""))

        if skipped:
            logger.info(f"   ⏭️  Skipping {len(skipped)} already-processed videos (no updates)")

        logger.info(f"   ✅ {len(new_or_updated)} videos to process (new or updated)")

        return new_or_updated

    def get_processed_count(self) -> int:
        """Get count of processed videos"""
        return len(self.processed_videos)

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            "total_processed": len(self.processed_videos),
            "last_updated": max(
                (v.get("processed_at", "") for v in self.processed_videos.values()),
                default=""
            )
        }


def main():
    try:
        """Test processed tracker"""
        import argparse

        parser = argparse.ArgumentParser(description="YouTube Processed Video Tracker")
        parser.add_argument("--stats", action="store_true", help="Show processing statistics")

        args = parser.parse_args()

        tracker = YouTubeProcessedTracker()

        if args.stats:
            stats = tracker.get_processing_stats()
            print(json.dumps(stats, indent=2, default=str))
        else:
            print(f"Processed videos tracked: {tracker.get_processed_count()}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()