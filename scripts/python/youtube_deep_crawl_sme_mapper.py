#!/usr/bin/env python3
"""
YouTube Deep Crawl & SME Mapper

Crawls YouTube like old web crawlers, mapping out all domain life SMEs,
aggregating intelligence for Lumina's constant improvement feedback loop.

Features:
- Discovery: Find channels by domain/topic
- Crawling: Deep dive into channel content
- SME Mapping: Identify and catalog Subject Matter Experts
- Intelligence Extraction: SYPHON integration for actionable intelligence
- Aggregation: Feed into Lumina's feedback loops
- Scheduled: Hourly, daily, weekly execution
"""

import json
import sys
import subprocess
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

# Import SYPHON if available
try:
    from syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier, DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    logger.warning("SYPHON not available - intelligence extraction will be limited")

# Import transcription system
try:
    from automatic_video_audio_transcription import VideoAudioTranscriber
    TRANSCRIPTION_AVAILABLE = True
except ImportError:
    TRANSCRIPTION_AVAILABLE = False
    logger.warning("Video transcription not available")

class YouTubeDeepCrawler:
    """
    YouTube Deep Crawler - Old Internet Web Crawler Logic Applied to YouTube

    Crawls YouTube systematically, discovering SMEs and extracting intelligence
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize YouTube deep crawler"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.youtube_intel_dir = self.data_dir / "youtube_intelligence"
        self.youtube_intel_dir.mkdir(parents=True, exist_ok=True)

        self.sme_map_file = self.youtube_intel_dir / "sme_map.json"
        self.crawl_state_file = self.youtube_intel_dir / "crawl_state.json"
        self.intelligence_aggregate_file = self.youtube_intel_dir / "intelligence_aggregate.json"

        self.syphon_system = None
        if SYPHON_AVAILABLE:
            try:
                config = SYPHONConfig(
                    project_root=self.project_root,
                    subscription_tier=SubscriptionTier.ENTERPRISE,
                    enable_self_healing=True
                )
                self.syphon_system = SYPHONSystem(config)
                logger.info("✅ SYPHONSystem initialized")
            except Exception as e:
                logger.warning(f"⚠️  SYPHON initialization failed: {e}")

        self.transcriber = None
        if TRANSCRIPTION_AVAILABLE:
            try:
                self.transcriber = VideoAudioTranscriber(project_root=self.project_root)
                logger.info("✅ Video transcriber initialized")
            except Exception as e:
                logger.warning(f"⚠️  Transcriber initialization failed: {e}")

        # Domain focus areas
        self.domain_keywords = [
            # AI/ML
            "artificial intelligence", "machine learning", "deep learning", "neural networks",
            "AI agent", "LLM", "GPT", "Claude", "Anthropic", "OpenAI",
            # Software Engineering
            "software engineering", "coding", "programming", "software architecture",
            "system design", "distributed systems", "cloud computing",
            # Data Science
            "data science", "data engineering", "analytics", "big data",
            # Business/Product
            "product management", "startup", "entrepreneurship", "business strategy",
            # Technical Skills
            "python", "javascript", "typescript", "react", "kubernetes", "docker",
            # Emerging Tech
            "quantum computing", "blockchain", "web3", "crypto",
        ]

        logger.info("🕷️ YouTube Deep Crawler initialized")

    def discover_channels_by_domain(self, domain: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Discover YouTube channels by domain using yt-dlp

        Args:
            domain: Domain/topic to search for
            max_results: Maximum number of channels to discover

        Returns:
            List of channel information dictionaries
        """
        logger.info(f"🔍 Discovering channels for domain: {domain}")

        channels = []

        try:
            # Use yt-dlp to search for channels
            search_query = f"{domain} channel"
            command = [
                "yt-dlp",
                f"ytsearch{max_results}:{search_query}",
                "--flat-playlist",
                "--print", "channel",
                "--print", "channel_id",
                "--print", "uploader",
                "--print", "url",
                "--skip-download"
            ]

            result = subprocess.run(command, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                current_channel = {}

                for line in lines:
                    if line.startswith("channel="):
                        current_channel["channel_name"] = line.replace("channel=", "").strip()
                    elif line.startswith("channel_id="):
                        current_channel["channel_id"] = line.replace("channel_id=", "").strip()
                    elif line.startswith("uploader="):
                        current_channel["uploader"] = line.replace("uploader=", "").strip()
                    elif line.startswith("http"):
                        current_channel["url"] = line.strip()
                        if current_channel.get("channel_id"):
                            channels.append(current_channel.copy())
                        current_channel = {}

                logger.info(f"✅ Discovered {len(channels)} channels for domain: {domain}")
            else:
                logger.warning(f"⚠️  yt-dlp search failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            logger.error(f"❌ Channel discovery timed out for domain: {domain}")
        except Exception as e:
            logger.error(f"❌ Error discovering channels: {e}")

        return channels

    def crawl_channel(self, channel_id: str, max_videos: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Crawl a YouTube channel, extracting video information

        Args:
            channel_id: YouTube channel ID
            max_videos: Maximum number of videos to crawl

        Returns:
            List of video information dictionaries
        """
        logger.info(f"🕷️ Crawling channel: {channel_id}")

        videos = []

        try:
            channel_url = f"https://www.youtube.com/channel/{channel_id}/videos"

            command = [
                "yt-dlp",
                channel_url,
                "--flat-playlist",
                "--print", "id",
                "--print", "title",
                "--print", "duration",
                "--print", "view_count",
                "--print", "upload_date",
                "--print", "url",
                "--skip-download"
            ]

            # Only add max-downloads if limit is specified
            if max_videos is not None:
                command.extend(["--max-downloads", str(max_videos)])

            # Increased timeout for full channel crawls (no limit)
            timeout = 1800 if max_videos is None else 300  # 30 minutes for unlimited, 5 minutes for limited
            result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                current_video = {}

                for line in lines:
                    if line.startswith("id="):
                        current_video["video_id"] = line.replace("id=", "").strip()
                    elif line.startswith("title="):
                        current_video["title"] = line.replace("title=", "").strip()
                    elif line.startswith("duration="):
                        current_video["duration"] = line.replace("duration=", "").strip()
                    elif line.startswith("view_count="):
                        current_video["view_count"] = line.replace("view_count=", "").strip()
                    elif line.startswith("upload_date="):
                        current_video["upload_date"] = line.replace("upload_date=", "").strip()
                    elif line.startswith("http"):
                        current_video["url"] = line.strip()
                        if current_video.get("video_id"):
                            videos.append(current_video.copy())
                        current_video = {}

                logger.info(f"✅ Crawled {len(videos)} videos from channel: {channel_id}")
            else:
                logger.warning(f"⚠️  Channel crawl failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            logger.error(f"❌ Channel crawl timed out: {channel_id}")
        except Exception as e:
            logger.error(f"❌ Error crawling channel: {e}")

        return videos

    def identify_sme(self, channel_data: Dict[str, Any], videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Identify if a channel represents a Subject Matter Expert

        Args:
            channel_data: Channel information
            videos: List of videos from the channel

        Returns:
            SME profile dictionary
        """
        sme_score = 0
        sme_indicators = []

        # Calculate SME score based on indicators
        if len(videos) > 10:
            sme_score += 1
            sme_indicators.append("High video count")

        total_views = sum(
            int(v.get("view_count", 0)) if v.get("view_count") and str(v.get("view_count")).isdigit() else 0
            for v in videos
        )
        if total_views > 100000:
            sme_score += 1
            sme_indicators.append("High view count")

        # Check for domain keywords in video titles
        domain_match_count = 0
        for video in videos[:20]:  # Check first 20 videos
            title = video.get("title", "").lower()
            if any(keyword in title for keyword in self.domain_keywords):
                domain_match_count += 1

        if domain_match_count > 5:
            sme_score += 1
            sme_indicators.append("Domain-focused content")

        # Determine SME tier
        if sme_score >= 3:
            sme_tier = "expert"
        elif sme_score >= 2:
            sme_tier = "experienced"
        elif sme_score >= 1:
            sme_tier = "emerging"
        else:
            sme_tier = "casual"

        sme_profile = {
            "channel_id": channel_data.get("channel_id"),
            "channel_name": channel_data.get("channel_name"),
            "uploader": channel_data.get("uploader"),
            "url": channel_data.get("url"),
            "sme_score": sme_score,
            "sme_tier": sme_tier,
            "sme_indicators": sme_indicators,
            "video_count": len(videos),
            "total_views": total_views,
            "domain_matches": domain_match_count,
            "identified_at": datetime.now().isoformat(),
            "videos": videos[:10]  # Store first 10 videos for reference
        }

        return sme_profile

    def extract_video_intelligence(self, video_url: str) -> Optional[Dict[str, Any]]:
        """
        Extract intelligence from a video using SYPHON and transcription

        Args:
            video_url: YouTube video URL

        Returns:
            Intelligence dictionary
        """
        logger.info(f"🧠 Extracting intelligence from: {video_url}")

        intelligence = {
            "video_url": video_url,
            "extracted_at": datetime.now().isoformat(),
            "transcript": None,
            "syphon_data": None,
            "actionable_items": [],
            "key_insights": []
        }

        # Transcribe video if transcriber available
        if self.transcriber:
            try:
                result = self.transcriber.transcribe_youtube_video(video_url)
                if result.get("status") == "success":
                    intelligence["transcript"] = result.get("full_transcript_path")
                    logger.info("✅ Video transcribed")
            except Exception as e:
                logger.warning(f"⚠️  Transcription failed: {e}")

        # Extract with SYPHON if available
        if self.syphon_system and intelligence.get("transcript"):
            try:
                # Load transcript content
                transcript_file = Path(intelligence["transcript"])
                if transcript_file.exists():
                    transcript_content = transcript_file.read_text(encoding='utf-8')

                    # Use SYPHON to extract intelligence
                    syphon_data = self.syphon_system.syphon_email(
                        email_id=video_url,
                        subject=f"YouTube Video Intelligence: {video_url}",
                        body=transcript_content,
                        from_address="youtube_crawler@lumina.ai",
                        to_address="intelligence_hub@lumina.ai",
                        metadata={"source": "youtube", "video_url": video_url}
                    )

                    intelligence["syphon_data"] = {
                        "actionable_items": syphon_data.actionable_items if hasattr(syphon_data, 'actionable_items') else [],
                        "tasks": syphon_data.tasks if hasattr(syphon_data, 'tasks') else [],
                        "decisions": syphon_data.decisions if hasattr(syphon_data, 'decisions') else [],
                        "intelligence": syphon_data.intelligence if hasattr(syphon_data, 'intelligence') else []
                    }

                    logger.info("✅ SYPHON intelligence extracted")
            except Exception as e:
                logger.warning(f"⚠️  SYPHON extraction failed: {e}")

        return intelligence

    def aggregate_intelligence(self, sme_profiles: List[Dict[str, Any]], 
                               intelligence_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate all intelligence into Lumina feedback format

        Args:
            sme_profiles: List of SME profiles
            intelligence_data: List of intelligence dictionaries

        Returns:
            Aggregated intelligence dictionary
        """
        logger.info("📊 Aggregating intelligence...")

        aggregate = {
            "aggregated_at": datetime.now().isoformat(),
            "total_smes": len(sme_profiles),
            "total_videos_analyzed": len(intelligence_data),
            "sme_breakdown": defaultdict(int),
            "domain_coverage": defaultdict(int),
            "actionable_items": [],
            "key_insights": [],
            "intelligence_summary": {
                "top_smes": [],
                "top_domains": [],
                "recommendations": []
            }
        }

        # Process SME profiles
        for sme in sme_profiles:
            tier = sme.get("sme_tier", "unknown")
            aggregate["sme_breakdown"][tier] += 1

        # Process intelligence data
        all_actionable = []
        for intel in intelligence_data:
            if intel.get("syphon_data"):
                actionable = intel["syphon_data"].get("actionable_items", [])
                all_actionable.extend(actionable)

        aggregate["actionable_items"] = list(set(all_actionable))  # Deduplicate
        aggregate["total_actionable_items"] = len(aggregate["actionable_items"])

        # Top SMEs by score
        top_smes = sorted(sme_profiles, key=lambda x: x.get("sme_score", 0), reverse=True)[:10]
        aggregate["intelligence_summary"]["top_smes"] = [
            {
                "channel_name": sme.get("channel_name"),
                "sme_tier": sme.get("sme_tier"),
                "sme_score": sme.get("sme_score"),
                "video_count": sme.get("video_count")
            }
            for sme in top_smes
        ]

        logger.info(f"✅ Aggregated intelligence: {aggregate['total_actionable_items']} actionable items")

        return aggregate

    def save_sme_map(self, sme_profiles: List[Dict[str, Any]]) -> None:
        try:
            """Save SME map to disk"""
            sme_map = {
                "updated_at": datetime.now().isoformat(),
                "total_smes": len(sme_profiles),
                "smes": sme_profiles
            }

            with open(self.sme_map_file, 'w', encoding='utf-8') as f:
                json.dump(sme_map, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ SME map saved: {len(sme_profiles)} SMEs")

        except Exception as e:
            self.logger.error(f"Error in save_sme_map: {e}", exc_info=True)
            raise
    def load_sme_map(self) -> List[Dict[str, Any]]:
        try:
            """Load SME map from disk"""
            if self.sme_map_file.exists():
                with open(self.sme_map_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("smes", [])
            return []

        except Exception as e:
            self.logger.error(f"Error in load_sme_map: {e}", exc_info=True)
            raise
    def feed_to_lumina_feedback_loop(self, aggregate: Dict[str, Any]) -> None:
        try:
            """
            Feed aggregated intelligence into Lumina's feedback loops

            Args:
                aggregate: Aggregated intelligence dictionary
            """
            logger.info("🔄 Feeding intelligence to Lumina feedback loops...")

            # Feed to Master Feedback Loop
            feedback_loop_dir = self.data_dir / "master_feedback_loop"
            feedback_loop_dir.mkdir(parents=True, exist_ok=True)

            feedback_file = feedback_loop_dir / f"youtube_intelligence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            feedback_data = {
                "source": "youtube_deep_crawl",
                "type": "external_intelligence",
                "timestamp": datetime.now().isoformat(),
                "intelligence": aggregate,
                "actionable_items": aggregate.get("actionable_items", []),
                "priority": "high",
                "frequency": "continuous"
            }

            with open(feedback_file, 'w', encoding='utf-8') as f:
                json.dump(feedback_data, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Intelligence fed to feedback loop: {feedback_file.name}")

            # Also save aggregated intelligence
            with open(self.intelligence_aggregate_file, 'w', encoding='utf-8') as f:
                json.dump(aggregate, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Aggregated intelligence saved: {self.intelligence_aggregate_file.name}")

        except Exception as e:
            self.logger.error(f"Error in feed_to_lumina_feedback_loop: {e}", exc_info=True)
            raise
    def execute_crawl_cycle(self, domains: Optional[List[str]] = None, 
                           max_channels_per_domain: int = 20,
                           max_videos_per_channel: int = 50) -> Dict[str, Any]:
        """
        Execute a complete crawl cycle

        Args:
            domains: List of domains to crawl (defaults to domain_keywords)
            max_channels_per_domain: Maximum channels to discover per domain
            max_videos_per_channel: Maximum videos to crawl per channel

        Returns:
            Crawl cycle results
        """
        logger.info("="*80)
        logger.info("🕷️ STARTING YOUTUBE DEEP CRAWL CYCLE")
        logger.info("="*80)

        if domains is None:
            domains = list(set([kw.split()[0] for kw in self.domain_keywords[:10]]))  # Sample domains

        all_sme_profiles = []
        all_intelligence = []

        # Discover and crawl channels for each domain
        for domain in domains:
            logger.info(f"\n📚 Crawling domain: {domain}")

            # Discover channels
            channels = self.discover_channels_by_domain(domain, max_channels_per_domain)

            # Crawl each channel
            for channel in channels[:10]:  # Limit to top 10 channels per domain
                channel_id = channel.get("channel_id")
                if not channel_id:
                    continue

                # Crawl channel videos
                videos = self.crawl_channel(channel_id, max_videos_per_channel)

                # Identify SME
                sme_profile = self.identify_sme(channel, videos)
                if sme_profile["sme_tier"] in ["expert", "experienced"]:
                    all_sme_profiles.append(sme_profile)

                    # Extract intelligence from top videos
                    for video in videos[:5]:  # Top 5 videos per channel
                        video_url = video.get("url")
                        if video_url:
                            intel = self.extract_video_intelligence(video_url)
                            if intel:
                                all_intelligence.append(intel)

        # Aggregate intelligence
        aggregate = self.aggregate_intelligence(all_sme_profiles, all_intelligence)

        # Save SME map
        existing_smes = self.load_sme_map()
        all_sme_profiles.extend(existing_smes)
        self.save_sme_map(all_sme_profiles)

        # Feed to Lumina feedback loops
        self.feed_to_lumina_feedback_loop(aggregate)

        logger.info("\n" + "="*80)
        logger.info("✅ YOUTUBE DEEP CRAWL CYCLE COMPLETE")
        logger.info("="*80)
        logger.info(f"📊 Results: {len(all_sme_profiles)} SMEs, {len(all_intelligence)} videos analyzed")
        logger.info(f"🎯 Actionable items: {aggregate.get('total_actionable_items', 0)}")
        logger.info("="*80)

        return {
            "sme_profiles": all_sme_profiles,
            "intelligence": all_intelligence,
            "aggregate": aggregate
        }

def main():
    """Main execution"""
    crawler = YouTubeDeepCrawler()

    import argparse
    parser = argparse.ArgumentParser(description="YouTube Deep Crawl & SME Mapper")
    parser.add_argument("--domains", nargs="+", help="Domains to crawl")
    parser.add_argument("--max-channels", type=int, default=20, help="Max channels per domain")
    parser.add_argument("--max-videos", type=int, default=50, help="Max videos per channel")
    parser.add_argument("--schedule", choices=["hourly", "daily", "weekly"], help="Schedule frequency")

    args = parser.parse_args()

    # Execute crawl cycle
    results = crawler.execute_crawl_cycle(
        domains=args.domains,
        max_channels_per_domain=args.max_channels,
        max_videos_per_channel=args.max_videos
    )

    print(f"\n✅ Crawl complete: {len(results['sme_profiles'])} SMEs mapped")
    print(f"🎯 {results['aggregate'].get('total_actionable_items', 0)} actionable items extracted")

if __name__ == "__main__":



    main()