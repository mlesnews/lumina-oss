#!/usr/bin/env python3
"""
YouTube AI & DOIT Intelligence Scan

Scans YouTube channels, recommendations, and history for:
- AI-related intelligence
- DOIT (Execute/Action/Implementation) intelligence
- Actionable content that requires execution

Features:
- 30-day lookback period
- Time estimation before starting
- Performance benchmarking
- Framework integration
- Balance maintenance across ecosystem

Tags: #YOUTUBE #AI #DOIT #INTELLIGENCE #BENCHMARKING @JARVIS @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

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

logger = get_logger("YouTubeAIDOITScan")

# AI and DOIT keywords for intelligence filtering
AI_KEYWORDS = [
    "artificial intelligence", "AI", "machine learning", "ML", "deep learning",
    "neural network", "GPT", "LLM", "language model", "transformer",
    "automation", "autonomous", "agent", "assistant", "chatbot",
    "computer vision", "NLP", "natural language", "prompt engineering",
    "fine-tuning", "training", "model", "algorithm", "data science"
]

DOIT_KEYWORDS = [
    "do it", "execute", "action", "implementation", "complete", "finish",
    "build", "create", "make", "implement", "deploy", "run", "start",
    "tutorial", "how to", "step by step", "guide", "walkthrough",
    "setup", "install", "configure", "build", "deploy", "production",
    "real world", "practical", "hands on", "project", "code", "example"
]


@dataclass
class TimeEstimate:
    """Time estimation for scan operations"""
    total_estimated_seconds: float
    channels_seconds: float
    recommendations_seconds: float
    history_seconds: float
    processing_seconds: float
    breakdown: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """Performance tracking metrics"""
    scan_started: datetime
    scan_completed: Optional[datetime] = None
    estimated_duration: Optional[float] = None
    actual_duration: Optional[float] = None
    videos_scanned: int = 0
    intelligence_extracted: int = 0
    ai_intelligence: int = 0
    doit_intelligence: int = 0
    duplicates_skipped: int = 0
    errors: List[str] = field(default_factory=list)
    performance_notes: List[str] = field(default_factory=list)


class YouTubeAIDOITIntelligenceScanner:
    """Scan YouTube for AI and DOIT intelligence"""

    def __init__(self, project_root: Optional[Path] = None, days_back: int = 30):
        """Initialize scanner"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.days_back = days_back
        self.cutoff_date = datetime.now() - timedelta(days=days_back)

        # Data directories
        self.output_dir = self.project_root / "data" / "youtube_ai_doit_intelligence"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Performance tracking
        self.metrics = PerformanceMetrics(scan_started=datetime.now())

        logger.info("✅ YouTube AI & DOIT Intelligence Scanner initialized")
        logger.info(f"   Lookback period: {days_back} days (from {self.cutoff_date.date()})")

    def estimate_scan_time(self) -> TimeEstimate:
        """
        Estimate time required for scan BEFORE starting

        Returns:
            TimeEstimate with breakdown
        """
        logger.info("="*80)
        logger.info("⏱️  ESTIMATING SCAN TIME")
        logger.info("="*80)

        estimate = TimeEstimate(
            total_estimated_seconds=0.0,
            channels_seconds=0.0,
            recommendations_seconds=0.0,
            history_seconds=0.0,
            processing_seconds=0.0
        )

        # Estimate channels scan time
        try:
            from jarvis_syphon_youtube_financial_creators import SyphonYouTubeFinancialCreators
            youtube_syphon = SyphonYouTubeFinancialCreators(self.project_root)
            subscribed_channels = youtube_syphon._load_subscribed_channels()

            num_channels = min(len(subscribed_channels), 20)
            videos_per_channel = 10
            time_per_video = 2.0  # seconds per video (API call + processing)

            estimate.channels_seconds = num_channels * videos_per_channel * time_per_video
            estimate.breakdown["channels"] = {
                "num_channels": num_channels,
                "videos_per_channel": videos_per_channel,
                "time_per_video": time_per_video,
                "total_seconds": estimate.channels_seconds
            }

            logger.info(f"   📺 Channels: {num_channels} channels × {videos_per_channel} videos × {time_per_video}s = {estimate.channels_seconds:.1f}s ({estimate.channels_seconds/60:.1f} min)")
        except Exception as e:
            logger.warning(f"   ⚠️  Could not estimate channels time: {e}")
            estimate.channels_seconds = 300  # Default 5 minutes
            estimate.breakdown["channels"] = {"estimated": 300, "note": "Fallback estimate"}

        # Estimate recommendations scan time
        num_recommendations = 50
        time_per_recommendation = 1.5  # seconds per recommendation

        estimate.recommendations_seconds = num_recommendations * time_per_recommendation
        estimate.breakdown["recommendations"] = {
            "num_recommendations": num_recommendations,
            "time_per_recommendation": time_per_recommendation,
            "total_seconds": estimate.recommendations_seconds
        }

        logger.info(f"   📊 Recommendations: {num_recommendations} videos × {time_per_recommendation}s = {estimate.recommendations_seconds:.1f}s ({estimate.recommendations_seconds/60:.1f} min)")

        # Estimate history scan time
        num_history_videos = 100
        time_per_history_video = 3.0  # seconds per video (yt-dlp + processing)

        estimate.history_seconds = num_history_videos * time_per_history_video
        estimate.breakdown["history"] = {
            "num_videos": num_history_videos,
            "time_per_video": time_per_history_video,
            "total_seconds": estimate.history_seconds
        }

        logger.info(f"   📚 History: {num_history_videos} videos × {time_per_history_video}s = {estimate.history_seconds:.1f}s ({estimate.history_seconds/60:.1f} min)")

        # Estimate processing time (filtering, deduplication, assessment)
        videos_total = (estimate.breakdown.get("channels", {}).get("num_channels", 0) * 
                       estimate.breakdown.get("channels", {}).get("videos_per_channel", 0) +
                       num_recommendations + num_history_videos)

        time_per_processing = 0.1  # seconds per video for processing
        estimate.processing_seconds = videos_total * time_per_processing
        estimate.breakdown["processing"] = {
            "total_videos": videos_total,
            "time_per_video": time_per_processing,
            "total_seconds": estimate.processing_seconds
        }

        logger.info(f"   ⚙️  Processing: {videos_total} videos × {time_per_processing}s = {estimate.processing_seconds:.1f}s")

        # Total estimate
        estimate.total_estimated_seconds = (
            estimate.channels_seconds +
            estimate.recommendations_seconds +
            estimate.history_seconds +
            estimate.processing_seconds
        )

        # Add 20% buffer for network delays, API rate limits, etc.
        buffer = estimate.total_estimated_seconds * 0.2
        estimate.total_estimated_seconds += buffer

        logger.info("")
        logger.info("="*80)
        logger.info(f"⏱️  TOTAL ESTIMATED TIME: {estimate.total_estimated_seconds/60:.1f} minutes ({estimate.total_estimated_seconds:.0f} seconds)")
        logger.info(f"   (Includes 20% buffer for network/API delays)")
        logger.info("="*80)
        logger.info("")

        return estimate

    def is_ai_intelligence(self, text: str) -> bool:
        """Check if text contains AI-related intelligence"""
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in AI_KEYWORDS)

    def is_doit_intelligence(self, text: str) -> bool:
        """Check if text contains DOIT-related intelligence"""
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in DOIT_KEYWORDS)

    def filter_intelligence(self, intelligence_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Filter intelligence for AI and DOIT content"""
        ai_intelligence = []
        doit_intelligence = []
        combined_intelligence = []

        for intelligence in intelligence_list:
            title = intelligence.get("title", "")
            content = intelligence.get("content", "")
            summary = intelligence.get("summary", "")

            combined_text = f"{title} {summary} {content}".lower()

            is_ai = self.is_ai_intelligence(combined_text)
            is_doit = self.is_doit_intelligence(combined_text)

            if is_ai or is_doit:
                intelligence["ai_related"] = is_ai
                intelligence["doit_related"] = is_doit
                intelligence["intelligence_type"] = []

                if is_ai:
                    intelligence["intelligence_type"].append("AI")
                    ai_intelligence.append(intelligence)

                if is_doit:
                    intelligence["intelligence_type"].append("DOIT")
                    doit_intelligence.append(intelligence)

                combined_intelligence.append(intelligence)

        return {
            "ai_intelligence": ai_intelligence,
            "doit_intelligence": doit_intelligence,
            "combined_intelligence": combined_intelligence,
            "total_filtered": len(combined_intelligence),
            "ai_count": len(ai_intelligence),
            "doit_count": len(doit_intelligence)
        }

    def scan_channels(self) -> Dict[str, Any]:
        """Scan subscribed channels for AI/DOIT intelligence"""
        logger.info("="*80)
        logger.info("📺 SCANNING YOUTUBE CHANNELS (AI & DOIT Intelligence)")
        logger.info("="*80)

        all_intelligence = []

        try:
            from jarvis_syphon_youtube_financial_creators import SyphonYouTubeFinancialCreators
            import asyncio

            youtube_syphon = SyphonYouTubeFinancialCreators(self.project_root)
            subscribed_channels = youtube_syphon._load_subscribed_channels()

            logger.info(f"   Found {len(subscribed_channels)} subscribed channels")

            for channel in subscribed_channels[:20]:  # Limit to 20 channels
                try:
                    channel_name = channel.get("name", "Unknown")
                    logger.info(f"   📺 Scanning: {channel_name}")

                    # Extract channel content
                    channel_results = asyncio.run(youtube_syphon._extract_channel_content(channel))
                    videos = channel_results.get("videos", [])

                    # Filter videos by date (30 days back)
                    recent_videos = []
                    for video in videos:
                        try:
                            published_at = video.get("published_at", "")
                            if published_at:
                                video_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                                if video_date >= self.cutoff_date:
                                    recent_videos.append(video)
                        except:
                            # If date parsing fails, include video (better to include than exclude)
                            recent_videos.append(video)

                    # Convert to intelligence format
                    for video in recent_videos:
                        intelligence = {
                            "title": video.get("title", "Untitled Video"),
                            "content": video.get("description", video.get("transcript", "")),
                            "summary": video.get("summary", video.get("description", "")[:500]),
                            "url": f"https://www.youtube.com/watch?v={video.get('video_id', '')}",
                            "source": "youtube_channels",
                            "source_name": "YouTube Subscribed Channels",
                            "timestamp": video.get("published_at", datetime.now().isoformat()),
                            "scan_type": "ai_doit_intelligence",
                            "channel": channel_name,
                            "video_id": video.get("video_id", ""),
                            "days_back": self.days_back
                        }
                        all_intelligence.append(intelligence)

                    logger.info(f"      ✅ Found {len(recent_videos)} recent videos from {channel_name}")

                except Exception as e:
                    logger.error(f"   ❌ Error scanning channel {channel.get('name', 'unknown')}: {e}")
                    self.metrics.errors.append(f"Channel scan error: {e}")
                    continue

            self.metrics.videos_scanned += len(all_intelligence)

        except ImportError:
            logger.warning("⚠️  YouTube SYPHON not available")
            self.metrics.errors.append("YouTube SYPHON import failed")

        return {"intelligence": all_intelligence, "count": len(all_intelligence)}

    def scan_recommendations(self) -> Dict[str, Any]:
        """Scan recommendations for AI/DOIT intelligence"""
        logger.info("="*80)
        logger.info("📊 SCANNING YOUTUBE RECOMMENDATIONS (AI & DOIT Intelligence)")
        logger.info("="*80)

        all_intelligence = []

        try:
            from syphon_youtube_account_data import YouTubeAccountSyphon
            account_syphon = YouTubeAccountSyphon(self.project_root)
            account_data = account_syphon.extract_account_data()
            recommendations = account_data.get("recommendations", [])

            logger.info(f"   Found {len(recommendations)} recommendations")

            # Filter by date
            recent_recommendations = []
            for rec in recommendations:
                try:
                    published_at = rec.get("published_at", "")
                    if published_at:
                        video_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                        if video_date >= self.cutoff_date:
                            recent_recommendations.append(rec)
                except:
                    recent_recommendations.append(rec)

            for rec in recent_recommendations[:50]:
                intelligence = {
                    "title": rec.get("title", "Untitled Video"),
                    "content": rec.get("description", ""),
                    "summary": rec.get("description", "")[:500] if rec.get("description") else "",
                    "url": f"https://www.youtube.com/watch?v={rec.get('video_id', '')}",
                    "source": "youtube_recommendations",
                    "source_name": "YouTube Recommendations",
                    "timestamp": rec.get("published_at", datetime.now().isoformat()),
                    "scan_type": "ai_doit_intelligence",
                    "video_id": rec.get("video_id", ""),
                    "days_back": self.days_back
                }
                all_intelligence.append(intelligence)

            self.metrics.videos_scanned += len(all_intelligence)

        except ImportError:
            logger.warning("⚠️  YouTube Account SYPHON not available")
            self.metrics.errors.append("YouTube Account SYPHON import failed")

        return {"intelligence": all_intelligence, "count": len(all_intelligence)}

    def scan_history(self) -> Dict[str, Any]:
        """Scan watch history for AI/DOIT intelligence"""
        logger.info("="*80)
        logger.info("📚 SCANNING YOUTUBE HISTORY (AI & DOIT Intelligence)")
        logger.info("="*80)

        all_intelligence = []

        try:
            from syphon_youtube_watch_history_30_days import YouTubeWatchHistorySyphon
            history_syphon = YouTubeWatchHistorySyphon(self.project_root, days=self.days_back)

            methods = history_syphon.check_access_methods()
            logger.info(f"   Available methods: {methods}")

            videos = []
            if methods.get("cookies_file"):
                videos = history_syphon.syphon_via_cookies_file(max_videos=100)
            elif methods.get("browser_edge"):
                videos = history_syphon.syphon_via_browser("edge", max_videos=100)
            elif methods.get("browser_chrome"):
                videos = history_syphon.syphon_via_browser("chrome", max_videos=100)

            # Filter by date
            recent_videos = []
            for video in videos:
                try:
                    watched_at = video.get("watched_at", video.get("syphoned_at", ""))
                    if watched_at:
                        watch_date = datetime.fromisoformat(watched_at.replace('Z', '+00:00'))
                        if watch_date >= self.cutoff_date:
                            recent_videos.append(video)
                except:
                    recent_videos.append(video)

            for video in recent_videos:
                intelligence = {
                    "title": video.get("title", "Untitled Video"),
                    "content": "",
                    "summary": "",
                    "url": f"https://www.youtube.com/watch?v={video.get('video_id', '')}",
                    "source": "youtube_history",
                    "source_name": "YouTube Watch History",
                    "timestamp": video.get("watched_at", video.get("syphoned_at", datetime.now().isoformat())),
                    "scan_type": "ai_doit_intelligence",
                    "video_id": video.get("video_id", ""),
                    "days_back": self.days_back
                }

                # Get video details
                video_details = self._get_video_details(video.get("video_id", ""))
                if video_details:
                    intelligence["content"] = video_details.get("description", "")
                    intelligence["summary"] = video_details.get("description", "")[:500] if video_details.get("description") else ""

                all_intelligence.append(intelligence)

            self.metrics.videos_scanned += len(all_intelligence)

        except ImportError:
            logger.warning("⚠️  YouTube History SYPHON not available")
            self.metrics.errors.append("YouTube History SYPHON import failed")

        return {"intelligence": all_intelligence, "count": len(all_intelligence)}

    def _get_video_details(self, video_id: str) -> Dict[str, Any]:
        """Get video details using yt-dlp"""
        if not video_id:
            return {}

        try:
            import subprocess
            cmd = [
                "yt-dlp",
                f"https://www.youtube.com/watch?v={video_id}",
                "--skip-download",
                "--print", "%(title)s|%(description)s|%(channel)s"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0 and '|' in result.stdout:
                parts = result.stdout.strip().split('|')
                return {
                    "title": parts[0] if len(parts) > 0 else "",
                    "description": parts[1] if len(parts) > 1 else "",
                    "channel": parts[2] if len(parts) > 2 else ""
                }
        except Exception as e:
            logger.debug(f"Could not get video details for {video_id}: {e}")

        return {}

    def run_scan(self) -> Dict[str, Any]:
        """Run complete AI/DOIT intelligence scan"""
        logger.info("="*80)
        logger.info("🎬 YOUTUBE AI & DOIT INTELLIGENCE SCAN")
        logger.info("="*80)
        logger.info("")

        # Estimate time BEFORE starting
        time_estimate = self.estimate_scan_time()
        self.metrics.estimated_duration = time_estimate.total_estimated_seconds

        logger.info("⏳ Starting scan in 3 seconds...")
        time.sleep(3)

        # Start scan
        scan_start = time.time()
        all_intelligence = []

        # Scan channels
        try:
            channels_result = self.scan_channels()
            all_intelligence.extend(channels_result["intelligence"])
            logger.info("")
        except Exception as e:
            logger.error(f"Error scanning channels: {e}")
            self.metrics.errors.append(f"Channels scan: {e}")

        # Scan recommendations
        try:
            recommendations_result = self.scan_recommendations()
            all_intelligence.extend(recommendations_result["intelligence"])
            logger.info("")
        except Exception as e:
            logger.error(f"Error scanning recommendations: {e}")
            self.metrics.errors.append(f"Recommendations scan: {e}")

        # Scan history
        try:
            history_result = self.scan_history()
            all_intelligence.extend(history_result["intelligence"])
            logger.info("")
        except Exception as e:
            logger.error(f"Error scanning history: {e}")
            self.metrics.errors.append(f"History scan: {e}")

        # Filter for AI and DOIT intelligence
        logger.info("="*80)
        logger.info("🔍 FILTERING FOR AI & DOIT INTELLIGENCE")
        logger.info("="*80)

        filtered = self.filter_intelligence(all_intelligence)

        self.metrics.ai_intelligence = filtered["ai_count"]
        self.metrics.doit_intelligence = filtered["doit_count"]
        self.metrics.intelligence_extracted = filtered["total_filtered"]

        # Complete scan
        scan_end = time.time()
        actual_duration = scan_end - scan_start

        self.metrics.scan_completed = datetime.now()
        self.metrics.actual_duration = actual_duration

        # Performance analysis
        if self.metrics.estimated_duration:
            variance = ((actual_duration - self.metrics.estimated_duration) / self.metrics.estimated_duration) * 100
            self.metrics.performance_notes.append(
                f"Time variance: {variance:+.1f}% "
                f"(Estimated: {self.metrics.estimated_duration/60:.1f}min, "
                f"Actual: {actual_duration/60:.1f}min)"
            )

        # Prepare results
        results = {
            "scan_metadata": {
                "started": self.metrics.scan_started.isoformat(),
                "completed": self.metrics.scan_completed.isoformat(),
                "estimated_duration_seconds": self.metrics.estimated_duration,
                "actual_duration_seconds": self.metrics.actual_duration,
                "days_back": self.days_back,
                "cutoff_date": self.cutoff_date.isoformat()
            },
            "performance_metrics": {
                "videos_scanned": self.metrics.videos_scanned,
                "intelligence_extracted": self.metrics.intelligence_extracted,
                "ai_intelligence": self.metrics.ai_intelligence,
                "doit_intelligence": self.metrics.doit_intelligence,
                "errors": self.metrics.errors,
                "performance_notes": self.metrics.performance_notes
            },
            "intelligence": {
                "ai_intelligence": filtered["ai_intelligence"],
                "doit_intelligence": filtered["doit_intelligence"],
                "combined_intelligence": filtered["combined_intelligence"]
            },
            "time_estimate": {
                "total_estimated_seconds": time_estimate.total_estimated_seconds,
                "breakdown": time_estimate.breakdown
            }
        }

        # Save results
        output_file = self.output_dir / f"ai_doit_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)

        # Print summary
        logger.info("")
        logger.info("="*80)
        logger.info("✅ SCAN COMPLETE")
        logger.info("="*80)
        logger.info(f"   Videos Scanned: {self.metrics.videos_scanned}")
        logger.info(f"   AI Intelligence: {self.metrics.ai_intelligence}")
        logger.info(f"   DOIT Intelligence: {self.metrics.doit_intelligence}")
        logger.info(f"   Total Intelligence: {self.metrics.intelligence_extracted}")
        logger.info(f"   Estimated Time: {self.metrics.estimated_duration/60:.1f} minutes")
        logger.info(f"   Actual Time: {actual_duration/60:.1f} minutes")
        if self.metrics.estimated_duration:
            variance = ((actual_duration - self.metrics.estimated_duration) / self.metrics.estimated_duration) * 100
            logger.info(f"   Variance: {variance:+.1f}%")
        logger.info(f"   Results saved to: {output_file}")
        logger.info("="*80)

        return results


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="YouTube AI & DOIT Intelligence Scan")
    parser.add_argument("--days", type=int, default=30, help="Days to look back (default: 30)")
    parser.add_argument("--estimate-only", action="store_true", help="Only show time estimate, don't scan")

    args = parser.parse_args()

    scanner = YouTubeAIDOITIntelligenceScanner(days_back=args.days)

    if args.estimate_only:
        scanner.estimate_scan_time()
    else:
        scanner.run_scan()


if __name__ == "__main__":


    main()