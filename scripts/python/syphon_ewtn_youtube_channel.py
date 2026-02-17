#!/usr/bin/env python3
"""
SYPHON: EWTN YouTube Channel

Comprehensive syphon for EWTN (Eternal Word Television Network) YouTube channel.
Extracts all videos, metadata, transcripts, and intelligence using SYPHON.

Usage:
    python syphon_ewtn_youtube_channel.py [--max-videos N] [--output-dir DIR] [--resume]
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
logger = get_logger("syphon_ewtn_youtube_channel")


script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier
    from syphon.models import DataSourceType
except ImportError:
    # Fallback if syphon not available
    SYPHONSystem = None
    SYPHONConfig = None
    SubscriptionTier = None
    DataSourceType = None

try:
    from r5_living_context_matrix import R5LivingContextMatrix
except ImportError:
    R5LivingContextMatrix = None


class EWTNYouTubeSyphon:
    """Comprehensive EWTN YouTube channel syphon using SYPHON"""

    EWTN_CHANNEL_URL = "https://www.youtube.com/@EWTN"

    def __init__(self, project_root: Path, max_videos: int = 1000, output_dir: Path = None):
        """
        Initialize EWTN YouTube syphon.

        Args:
            project_root: Project root directory
            max_videos: Maximum number of videos to process
            output_dir: Output directory for scraped data
        """
        self.project_root = Path(project_root)
        self.max_videos = max_videos
        self.output_dir = output_dir or (self.project_root / "data" / "syphon" / "ewtn_youtube")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.logger = get_logger("EWTNYouTubeSyphon")

        # Initialize SYPHON
        if SYPHONSystem is None:
            self.logger.warning("SYPHON not available - will only fetch video metadata")
            self.syphon = None
        else:
            config = SYPHONConfig(
                project_root=self.project_root,
                subscription_tier=SubscriptionTier.ENTERPRISE
            )
            self.syphon = SYPHONSystem(config)

        # Initialize R5 if available
        self.r5 = R5LivingContextMatrix(self.project_root) if R5LivingContextMatrix else None

        # Tracking
        self.processed_videos: List[Dict] = []
        self.failed_videos: List[Dict] = []
        self.processed_count = 0
        self.failed_count = 0

        # State file for resuming
        self.state_file = self.output_dir / "syphon_state.json"

    def check_yt_dlp(self) -> bool:
        """Check if yt-dlp is available"""
        try:
            result = subprocess.run(
                ["yt-dlp", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def get_channel_videos(self, resume_from: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all videos from EWTN YouTube channel using yt-dlp.

        Args:
            resume_from: Video ID to resume from (for pagination)

        Returns:
            List of video dictionaries with id, title, url, duration, etc.
        """
        if not self.check_yt_dlp():
            self.logger.error("❌ yt-dlp not installed: pip install yt-dlp")
            return []

        self.logger.info(f"📺 Fetching videos from EWTN YouTube channel...")
        self.logger.info(f"   Channel: {self.EWTN_CHANNEL_URL}")
        self.logger.info(f"   Max videos: {self.max_videos}")

        videos = []
        start_index = 1

        # If resuming, find the index of the resume video
        if resume_from:
            # Load state to find where we left off
            state = self.load_state()
            processed_ids = {v.get("video_id") for v in state.get("processed_videos", [])}
            # We'll skip already processed videos later, but need to fetch all
            pass

        # Use yt-dlp to get video list
        # Process in batches to avoid timeouts
        batch_size = 500
        total_fetched = 0

        while total_fetched < self.max_videos:
            end_index = min(start_index + batch_size - 1, self.max_videos)

            self.logger.info(f"   Fetching videos {start_index}-{end_index}...")

            command = [
                'yt-dlp',
                '--flat-playlist',
                '--print', '%(id)s|%(title)s|%(url)s|%(duration)s|%(upload_date)s|%(view_count)s|%(description)s',
                self.EWTN_CHANNEL_URL,
                '--no-download',
                '--playlist-items', f'{start_index}-{end_index}',
                '--ignore-errors'
            ]

            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=600  # 10 minute timeout per batch
                )

                if result.returncode != 0:
                    self.logger.warning(f"   ⚠️  yt-dlp returned non-zero exit code: {result.returncode}")
                    if result.stderr:
                        self.logger.warning(f"   Error: {result.stderr[:500]}")
                    # Continue with what we got

                # Parse output
                batch_videos = []
                for line in result.stdout.strip().split('\n'):
                    if '|' in line:
                        parts = line.split('|', 6)
                        if len(parts) >= 3:
                            video = {
                                'video_id': parts[0],
                                'title': parts[1] if len(parts) > 1 else '',
                                'url': parts[2] if len(parts) > 2 else f"https://www.youtube.com/watch?v={parts[0]}",
                                'duration': parts[3] if len(parts) > 3 else 'unknown',
                                'upload_date': parts[4] if len(parts) > 4 else '',
                                'view_count': parts[5] if len(parts) > 5 else '0',
                                'description': parts[6] if len(parts) > 6 else '',
                                'syphoned_at': datetime.now().isoformat()
                            }
                            batch_videos.append(video)

                videos.extend(batch_videos)
                total_fetched += len(batch_videos)

                self.logger.info(f"   ✅ Fetched {len(batch_videos)} videos (total: {total_fetched})")

                # If we got fewer videos than requested, we've reached the end
                if len(batch_videos) < (end_index - start_index + 1):
                    self.logger.info(f"   📊 Reached end of channel (fetched {total_fetched} total videos)")
                    break

                start_index = end_index + 1

                # Rate limiting between batches
                time.sleep(2)

            except subprocess.TimeoutExpired:
                self.logger.warning(f"   ⚠️  Timeout fetching batch {start_index}-{end_index}")
                break
            except Exception as e:
                self.logger.error(f"   ❌ Error fetching videos: {e}")
                break

        self.logger.info(f"✅ Total videos fetched: {len(videos)}")
        return videos

    def load_state(self) -> Dict[str, Any]:
        """Load previous state to resume processing"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.processed_videos = state.get('processed_videos', [])
                    self.failed_videos = state.get('failed_videos', [])
                    self.processed_count = len(self.processed_videos)
                    self.failed_count = len(self.failed_videos)
                    self.logger.info(f"Loaded state: {self.processed_count} processed, {self.failed_count} failed")
                    return state
            except Exception as e:
                self.logger.warning(f"Failed to load state: {e}")
        return {"processed_videos": [], "failed_videos": []}

    def save_state(self) -> None:
        """Save current state for resuming"""
        try:
            state = {
                'processed_videos': self.processed_videos,
                'failed_videos': self.failed_videos,
                'processed_count': self.processed_count,
                'failed_count': self.failed_count,
                'timestamp': datetime.now().isoformat()
            }
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.warning(f"Failed to save state: {e}")

    def process_video(self, video: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single video with SYPHON.

        Args:
            video: Video dictionary with id, title, url, etc.

        Returns:
            Result dictionary with success status and extracted data
        """
        video_id = video.get('video_id', '')
        video_url = video.get('url', '')
        video_title = video.get('title', 'Unknown')

        self.logger.info(f"📹 Processing: {video_title[:60]}...")
        self.logger.debug(f"   URL: {video_url}")

        try:
            # Extract with SYPHON if available
            if self.syphon is None:
                # Fallback: just save video metadata
                syphon_data_dict = {
                    "data_id": f"ewtn_video_{video_id}",
                    "content": video.get('description', ''),
                    "metadata": {
                        "title": video_title,
                        "source": "EWTN YouTube Channel",
                        "video_id": video_id,
                        "url": video_url,
                        "duration": video.get('duration', 'unknown'),
                        "upload_date": video.get('upload_date', ''),
                        "view_count": video.get('view_count', '0'),
                    },
                    "extracted_at": datetime.now(),
                    "actionable_items": [],
                    "tasks": [],
                    "intelligence": {}
                }

                # Create a simple object to mimic syphon data
                class SimpleSyphonData:
                    def __init__(self, data_dict):
                        self.data_id = data_dict["data_id"]
                        self.content = data_dict["content"]
                        self.metadata = data_dict["metadata"]
                        self.extracted_at = data_dict["extracted_at"]
                        self.actionable_items = data_dict["actionable_items"]
                        self.tasks = data_dict["tasks"]
                        self.intelligence = data_dict["intelligence"]

                    def to_dict(self):
                        return {
                            "data_id": self.data_id,
                            "content": self.content,
                            "metadata": self.metadata,
                            "extracted_at": self.extracted_at.isoformat(),
                            "actionable_items": self.actionable_items,
                            "tasks": self.tasks,
                            "intelligence": self.intelligence
                        }

                syphon_data = SimpleSyphonData(syphon_data_dict)
                result_success = True
            else:
                metadata = {
                    "title": video_title,
                    "source": "EWTN YouTube Channel",
                    "video_id": video_id,
                    "url": video_url,
                    "duration": video.get('duration', 'unknown'),
                    "upload_date": video.get('upload_date', ''),
                    "view_count": video.get('view_count', '0'),
                    "description": video.get('description', ''),
                    "accessibility_mode": True,
                    "extract_transcript": True,
                    "syphoned_at": datetime.now().isoformat()
                }

                result = self.syphon.extract(DataSourceType.SOCIAL, video_url, metadata)
                if result.success and result.data:
                    syphon_data = result.data
                    result_success = True
                else:
                    result_success = False
                    syphon_data = None

            if result_success and syphon_data:
                # Save extracted data
                output_file = self.output_dir / f"ewtn_video_{video_id}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "video": video,
                        "syphon_data": syphon_data.to_dict(),
                        "extracted_at": datetime.now().isoformat()
                    }, f, indent=2, ensure_ascii=False)

                # Ingest to R5 if available
                if self.r5:
                    try:
                        session_id = self.r5.ingest_session({
                            "session_id": f"ewtn_youtube_{video_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            "session_type": "youtube_video_syphon",
                            "timestamp": datetime.now().isoformat(),
                            "content": f"Title: {video_title}\nURL: {video_url}\nDuration: {video.get('duration', 'unknown')}\n\n{syphon_data.content}",
                            "metadata": {
                                **syphon_data.metadata,
                                "source": "EWTN YouTube Channel",
                                "video_id": video_id,
                                "url": video_url,
                                "accessibility_enabled": True,
                                "screen_reader_ready": True,
                                "transcript_available": syphon_data.metadata.get("transcript_available", False),
                                "actionable_items": syphon_data.actionable_items,
                                "tasks": syphon_data.tasks,
                                "intelligence": syphon_data.intelligence
                            }
                        })
                        self.logger.debug(f"      ✅ Ingested to R5: {session_id}")
                    except Exception as e:
                        self.logger.warning(f"      ⚠️  R5 ingestion failed: {e}")

                self.processed_count += 1

                return {
                    "video_id": video_id,
                    "success": True,
                    "data_id": syphon_data.data_id,
                    "title": video_title,
                    "extracted_at": syphon_data.extracted_at.isoformat(),
                    "output_file": str(output_file)
                }
            else:
                if self.syphon is None:
                    error_msg = "SYPHON not available"
                elif 'result' in locals():
                    error_msg = result.error if hasattr(result, 'error') else 'Unknown error'
                else:
                    error_msg = 'Unknown error'
                self.logger.warning(f"      ⚠️  SYPHON extraction failed: {error_msg}")
                self.failed_count += 1

                return {
                    "video_id": video_id,
                    "success": False,
                    "error": error_msg
                }

        except Exception as e:
            self.failed_count += 1
            self.logger.error(f"      ❌ Error processing video {video_id}: {e}")
            return {
                "video_id": video_id,
                "success": False,
                "error": str(e)
            }

    def run(self, resume: bool = False) -> None:
        """Run the EWTN YouTube syphon"""
        try:
            self.logger.info("=" * 80)
            self.logger.info("EWTN YouTube Channel Syphon Starting")
            self.logger.info("=" * 80)
            self.logger.info(f"Channel: {self.EWTN_CHANNEL_URL}")
            self.logger.info(f"Max videos: {self.max_videos}")
            self.logger.info("")

            # Load state if resuming
            if resume:
                self.load_state()
                processed_ids = {v.get("video_id") for v in self.processed_videos}
                self.logger.info(f"Resuming: {len(processed_ids)} videos already processed")
            else:
                processed_ids = set()

            # Get all videos from channel
            all_videos = self.get_channel_videos()

            if not all_videos:
                self.logger.error("❌ No videos found. Check yt-dlp installation and network connection.")
                return

            # Filter out already processed videos if resuming
            videos_to_process = [
                v for v in all_videos
                if v.get('video_id') not in processed_ids
            ]

            self.logger.info(f"📊 Total videos: {len(all_videos)}")
            self.logger.info(f"📊 Already processed: {len(processed_ids)}")
            self.logger.info(f"📊 To process: {len(videos_to_process)}")
            self.logger.info("")

            # Process each video
            for i, video in enumerate(videos_to_process, 1):
                self.logger.info(f"[{i}/{len(videos_to_process)}] Processing video...")

                result = self.process_video(video)

                if result.get("success"):
                    self.processed_videos.append(result)
                else:
                    self.failed_videos.append({
                        "video": video,
                        "error": result.get("error", "Unknown error")
                    })

                # Save state periodically
                if i % 10 == 0:
                    self.save_state()
                    self.logger.info(f"   Progress: {self.processed_count} processed, {self.failed_count} failed")

                # Rate limiting - be respectful to YouTube
                time.sleep(1)  # 1 second between videos

            # Final save
            self.save_state()

            # Save summary
            summary = {
                "channel_url": self.EWTN_CHANNEL_URL,
                "total_videos_fetched": len(all_videos),
                "total_processed": self.processed_count,
                "total_failed": self.failed_count,
                "processed_videos": self.processed_videos,
                "failed_videos": self.failed_videos,
                "completed_at": datetime.now().isoformat()
            }

            summary_file = self.output_dir / "syphon_summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)

            self.logger.info("")
            self.logger.info("=" * 80)
            self.logger.info("EWTN YouTube Channel Syphon Complete")
            self.logger.info("=" * 80)
            self.logger.info(f"✅ Processed: {self.processed_count}")
            self.logger.info(f"❌ Failed: {self.failed_count}")
            self.logger.info(f"📁 Results saved to: {self.output_dir}")
            self.logger.info(f"📊 Summary: {summary_file}")
            self.logger.info("=" * 80)

        except Exception as e:
            self.logger.error(f"Error in run: {e}", exc_info=True)
            raise


def main():
    try:
        """Main entry point"""
        parser = argparse.ArgumentParser(description="Syphon EWTN YouTube Channel")
        parser.add_argument(
            "--max-videos",
            type=int,
            default=1000,
            help="Maximum number of videos to process (default: 1000)"
        )
        parser.add_argument(
            "--output-dir",
            type=Path,
            help="Output directory for scraped data (default: data/syphon/ewtn_youtube)"
        )
        parser.add_argument(
            "--resume",
            action="store_true",
            help="Resume from previous state"
        )
        parser.add_argument(
            "--project-root",
            type=Path,
            default=Path(__file__).parent.parent.parent,
            help="Project root directory"
        )

        args = parser.parse_args()

        # Create syphon instance
        syphon = EWTNYouTubeSyphon(
            project_root=args.project_root,
            max_videos=args.max_videos,
            output_dir=args.output_dir
        )

        # Run
        syphon.run(resume=args.resume)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()