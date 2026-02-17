#!/usr/bin/env python3
"""
Channel Transformation Job Processor - Sliding Scale with Progress Tracking

Processes YouTube channel transformations with:
- Sliding scale approach (adapts to channel size)
- Real-time progress tracking
- Job queue management
- Progress updates and status reporting
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from transform_specific_channels_to_holocron import SpecificChannelTransformer
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('channel_transformation_progress.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ChannelJob:
    """Job definition for channel transformation"""
    channel_name: str
    channel_url: str
    priority: int = 5  # 1-10, higher = more important
    estimated_videos: Optional[int] = None
    status: str = "pending"  # pending, processing, completed, failed
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    videos_found: int = 0
    progress_percent: float = 0.0
    error_message: Optional[str] = None

class ChannelTransformationJobProcessor:
    """
    Job processor with sliding scale and progress tracking
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize job processor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.transformer = SpecificChannelTransformer(project_root=project_root)

        # Job queue
        self.jobs: List[ChannelJob] = []
        self.current_job: Optional[ChannelJob] = None

        # Progress tracking
        self.progress_file = self.project_root / "data" / "youtube_intelligence" / "transformation_progress.json"
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)

        logger.info("⚙️ Channel Transformation Job Processor initialized (Sliding Scale)")

    def add_job(self, channel_name: str, channel_url: str, priority: int = 5) -> ChannelJob:
        """Add a channel transformation job to the queue"""
        job = ChannelJob(
            channel_name=channel_name,
            channel_url=channel_url,
            priority=priority
        )
        self.jobs.append(job)
        logger.info(f"➕ Job added: {channel_name} (Priority: {priority})")
        return job

    def estimate_channel_size(self, channel_url: str) -> Optional[int]:
        """
        Quick estimate of channel size to determine processing strategy
        Returns approximate video count or None if unable to estimate
        """
        try:
            import subprocess
            # Quick check - get first page only
            command = [
                "yt-dlp",
                channel_url.rstrip("/") + "/videos",
                "--flat-playlist",
                "--playlist-end", "30",  # Just check first 30
                "--print", "%(id)s",
                "--skip-download",
                "--quiet"
            ]

            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                video_count = len([line for line in result.stdout.strip().split('\n') if line and len(line) == 11])
                # If we got 30 videos, channel is likely much larger
                if video_count == 30:
                    return 1000  # Estimate large channel
                return video_count
        except Exception as e:
            logger.debug(f"Could not estimate channel size: {e}")

        return None

    def determine_processing_strategy(self, estimated_videos: Optional[int]) -> Dict[str, Any]:
        """
        Determine processing strategy based on channel size (sliding scale)
        """
        if estimated_videos is None:
            # Unknown size - use conservative approach
            return {
                "batch_size": 100,
                "timeout": 1800,  # 30 minutes
                "show_progress_every": 50,
                "strategy": "conservative"
            }
        elif estimated_videos < 50:
            # Small channel - quick processing
            return {
                "batch_size": None,  # Get all at once
                "timeout": 300,  # 5 minutes
                "show_progress_every": 10,
                "strategy": "fast"
            }
        elif estimated_videos < 500:
            # Medium channel - standard processing
            return {
                "batch_size": None,  # Get all at once
                "timeout": 900,  # 15 minutes
                "show_progress_every": 50,
                "strategy": "standard"
            }
        else:
            # Large channel - patient processing with progress
            return {
                "batch_size": None,  # Still get all, but be patient
                "timeout": 3600,  # 60 minutes
                "show_progress_every": 100,
                "strategy": "patient"
            }

    def save_progress(self):
        try:
            """Save current progress to file"""
            progress_data = {
                "last_updated": datetime.now().isoformat(),
                "total_jobs": len(self.jobs),
                "completed_jobs": len([j for j in self.jobs if j.status == "completed"]),
                "failed_jobs": len([j for j in self.jobs if j.status == "failed"]),
                "current_job": asdict(self.current_job) if self.current_job else None,
                "jobs": [asdict(job) for job in self.jobs]
            }

            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in save_progress: {e}", exc_info=True)
            raise
    def print_progress(self, job: ChannelJob, message: str = ""):
        """Print progress update"""
        status_symbols = {
            "pending": "⏳",
            "processing": "🔄",
            "completed": "✅",
            "failed": "❌"
        }
        symbol = status_symbols.get(job.status, "⚙️")

        progress_bar = self._create_progress_bar(job.progress_percent)

        print(f"\n{symbol} [{job.channel_name}] {progress_bar} {job.progress_percent:.1f}%")
        if message:
            print(f"   {message}")
        if job.videos_found > 0:
            print(f"   📹 Videos found so far: {job.videos_found:,}")

        # Save progress
        self.save_progress()

    def _create_progress_bar(self, percent: float, width: int = 40) -> str:
        """Create a text progress bar"""
        filled = int(width * percent / 100)
        empty = width - filled
        return "█" * filled + "░" * empty

    def process_job(self, job: ChannelJob) -> bool:
        """
        Process a single job with progress tracking

        Returns True if successful, False otherwise
        """
        job.status = "processing"
        job.started_at = datetime.now().isoformat()
        job.progress_percent = 0.0
        self.current_job = job

        self.print_progress(job, "Starting transformation...")

        try:
            # Step 1: Estimate channel size (10%)
            self.print_progress(job, "Estimating channel size...")
            estimated_videos = self.estimate_channel_size(job.channel_url)
            job.estimated_videos = estimated_videos
            job.progress_percent = 10.0

            if estimated_videos:
                size_desc = f"~{estimated_videos:,} videos estimated"
            else:
                size_desc = "size unknown"

            self.print_progress(job, f"Channel size: {size_desc}")

            # Step 2: Determine processing strategy (20%)
            strategy = self.determine_processing_strategy(estimated_videos)
            job.progress_percent = 20.0
            self.print_progress(job, f"Strategy: {strategy['strategy']} (timeout: {strategy['timeout']//60}min)")

            # Step 3: Transform channel (20-90%)
            self.print_progress(job, "Transforming channel to Holocron...")

            # Use the transformer's process_channel method
            # We'll need to create a channel_config dict
            channel_config = {
                "name": job.channel_name,
                "channel_url": job.channel_url,
                "alternative_urls": [],
                "search_queries": []
            }

            # Call the transformer
            holocron = self.transformer.process_channel(job.channel_name.lower().replace(" ", "_"), channel_config)

            if holocron:
                job.progress_percent = 90.0
                videos_count = holocron.get("metadata", {}).get("video_count", 0)
                job.videos_found = videos_count
                self.print_progress(job, f"Holocron created: {holocron.get('entry_id', 'N/A')}")

                # Step 4: Complete (90-100%)
                job.progress_percent = 100.0
                job.status = "completed"
                job.completed_at = datetime.now().isoformat()
                self.print_progress(job, f"✅ Complete! {videos_count:,} videos processed")

                return True
            else:
                raise Exception("Transformation returned no Holocron")

        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.now().isoformat()
            self.print_progress(job, f"❌ Failed: {e}")
            logger.error(f"Job failed: {job.channel_name} - {e}")
            return False

    def process_all_jobs(self):
        """Process all jobs in the queue with progress tracking"""
        if not self.jobs:
            print("⚠️  No jobs in queue")
            return

        # Sort jobs by priority (higher priority first)
        self.jobs.sort(key=lambda j: j.priority, reverse=True)

        total_jobs = len(self.jobs)
        print(f"\n{'='*80}")
        print(f"🚀 Starting Job Processing - {total_jobs} job(s) in queue")
        print(f"{'='*80}\n")

        for idx, job in enumerate(self.jobs, 1):
            print(f"\n{'='*80}")
            print(f"Job {idx}/{total_jobs}: {job.channel_name}")
            print(f"{'='*80}")

            success = self.process_job(job)

            if success:
                print(f"✅ Job {idx}/{total_jobs} completed successfully")
            else:
                print(f"❌ Job {idx}/{total_jobs} failed")

            # Brief pause between jobs
            if idx < total_jobs:
                print("\n⏸️  Brief pause before next job...")
                time.sleep(2)

        # Final summary
        completed = len([j for j in self.jobs if j.status == "completed"])
        failed = len([j for j in self.jobs if j.status == "failed"])

        print(f"\n{'='*80}")
        print(f"📊 PROCESSING COMPLETE")
        print(f"{'='*80}")
        print(f"✅ Completed: {completed}/{total_jobs}")
        print(f"❌ Failed: {failed}/{total_jobs}")
        print(f"📁 Progress saved: {self.progress_file}")
        print(f"{'='*80}\n")

        self.current_job = None
        self.save_progress()

def main():
    """Main execution"""
    processor = ChannelTransformationJobProcessor()

    import argparse
    parser = argparse.ArgumentParser(description="Channel Transformation Job Processor (Sliding Scale)")
    parser.add_argument("--channel", action="append", nargs=2, metavar=("NAME", "URL"),
                       help="Add channel job (can be used multiple times)")
    parser.add_argument("--priority", type=int, default=5, help="Priority for jobs (1-10, default: 5)")

    args = parser.parse_args()

    # Add default jobs if no channels specified
    if not args.channel:
        # Default: the channels we've been working with
        processor.add_job("Star Wars Theory", "https://www.youtube.com/@StarWarsTheory", priority=10)
        processor.add_job("Badger", "https://www.youtube.com/@TheRussianBadger", priority=10)
        processor.add_job("Dashstar", "https://www.youtube.com/channel/UCfhYq8qIuADM_g5BypVywjA", priority=8)
        processor.add_job("The Stupendous Wave", "https://www.youtube.com/channel/UCdIt7cmllmxBK1-rQdu87Gg", priority=10)
    else:
        # Add custom jobs
        for name, url in args.channel:
            processor.add_job(name, url, priority=args.priority)

    # Process all jobs
    processor.process_all_jobs()

if __name__ == "__main__":



    main()