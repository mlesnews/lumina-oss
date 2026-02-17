#!/usr/bin/env python3
"""
Daily Work Cycle - Complete System
Regularly scheduled sweeps and scans on all sources (internal and external)
Includes YouTube learning analysis and knowledge extraction

Tags: #DAILY #WORK_CYCLE #SWEEPS #SCANS #YOUTUBE #LEARNING @JARVIS @LUMINA
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

logger = get_logger("DailyWorkCycle")


@dataclass
class SourceScanResult:
    """Result from scanning a source"""
    source_name: str
    source_type: str  # internal, external, youtube, etc.
    scan_timestamp: str
    items_found: int = 0
    items_processed: int = 0
    items_new: int = 0
    items_updated: int = 0
    errors: List[str] = field(default_factory=list)
    learnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DailyWorkCycleReport:
    """Complete daily work cycle report"""
    cycle_date: str
    cycle_start: str
    cycle_end: str
    total_sources_scanned: int = 0
    total_items_found: int = 0
    total_items_processed: int = 0
    total_learnings: int = 0
    source_results: List[SourceScanResult] = field(default_factory=list)
    youtube_learnings: List[Dict[str, Any]] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DailyWorkCycle:
    """
    Complete Daily Work Cycle System

    Runs regularly scheduled sweeps and scans on all sources.
    Extracts learnings and stores in knowledge systems.
    """

    def __init__(self):
        """Initialize daily work cycle"""
        logger.info("=" * 80)
        logger.info("🔄 Daily Work Cycle System")
        logger.info("=" * 80)

        self.project_root = project_root
        self.data_dir = project_root / "data" / "daily_work_cycles"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Source configurations
        self.sources = {
            'internal': {
                'enabled': True,
                'scan_interval_minutes': 60,
                'last_scan': None,
                'estimated_duration_seconds': 5
            },
            'external': {
                'enabled': True,
                'scan_interval_minutes': 120,
                'last_scan': None,
                'estimated_duration_seconds': 2
            },
            'youtube': {
                'enabled': True,
                'scan_interval_minutes': 30,
                'last_scan': None,
                'estimated_duration_seconds': 3
            },
            'email': {
                'enabled': True,
                'scan_interval_minutes': 60,
                'last_scan': None,
                'estimated_duration_seconds': 30  # Depends on email volume
            },
            'holocron': {
                'enabled': True,
                'scan_interval_minutes': 15,
                'last_scan': None,
                'estimated_duration_seconds': 2
            },
            'r5': {
                'enabled': True,
                'scan_interval_minutes': 15,
                'last_scan': None,
                'estimated_duration_seconds': 2
            }
        }

        # Current cycle report
        self.current_report: Optional[DailyWorkCycleReport] = None

        logger.info("✅ Daily Work Cycle System initialized")

    def run_full_cycle(self) -> DailyWorkCycleReport:
        """
        Run complete daily work cycle.

        Returns:
            Complete cycle report
        """
        cycle_start = datetime.now()
        cycle_date = cycle_start.strftime('%Y-%m-%d')

        logger.info(f"\n🔄 Starting Daily Work Cycle: {cycle_date}")
        logger.info(f"   Start time: {cycle_start.isoformat()}")

        # Initialize report
        self.current_report = DailyWorkCycleReport(
            cycle_date=cycle_date,
            cycle_start=cycle_start.isoformat(),
            cycle_end=""
        )

        # Scan all sources with completion verification
        logger.info("\n📡 Scanning Sources...")

        expected_sources = [name for name, config in self.sources.items() if config.get('enabled', False)]
        scanned_sources = []

        # 1. Internal sources
        if self.sources['internal']['enabled']:
            logger.info("  🔍 Scanning internal sources...")
            try:
                result = self._scan_internal_sources()
                self.current_report.source_results.append(result)
                scanned_sources.append('internal')
                if result.errors:
                    logger.warning(f"     ⚠️  Errors: {len(result.errors)}")
            except Exception as e:
                logger.error(f"     ❌ Failed to scan internal sources: {e}")
                result = SourceScanResult(
                    source_name="internal",
                    source_type="internal",
                    scan_timestamp=datetime.now().isoformat(),
                    errors=[str(e)]
                )
                self.current_report.source_results.append(result)

        # 2. External sources
        if self.sources['external']['enabled']:
            logger.info("  🔍 Scanning external sources...")
            result = self._scan_external_sources()
            self.current_report.source_results.append(result)

        # 3. YouTube (special focus)
        if self.sources['youtube']['enabled']:
            logger.info("  🎥 Scanning YouTube for learnings...")
            result = self._scan_youtube_sources()
            self.current_report.source_results.append(result)
            self.current_report.youtube_learnings = result.metadata.get('learnings', [])

        # 4. Holocron
        if self.sources['holocron']['enabled']:
            logger.info("  📚 Scanning Holocron...")
            result = self._scan_holocron()
            self.current_report.source_results.append(result)

        # 5. Email (NAS Mail Hub)
        if self.sources['email']['enabled']:
            logger.info("  📧 Syphoning emails via NAS Company Mail Hub...")
            result = self._scan_email_sources()
            self.current_report.source_results.append(result)

        # 6. R5 Living Context Matrix
        if self.sources['r5']['enabled']:
            logger.info("  🤖 Scanning R5 Living Context Matrix...")
            result = self._scan_r5()
            self.current_report.source_results.append(result)

        # 7. Cursor IDE Development Monitoring (Keep finger on the pulse)
        logger.info("  🎯 Monitoring Cursor IDE developments...")
        result = self._scan_cursor_ide_developments()
        self.current_report.source_results.append(result)

        # Generate summary
        self._generate_summary()

        # Verify completion of all expected sources
        scanned_sources = {r.source_name for r in self.current_report.source_results}
        expected_sources = {name for name, config in self.sources.items() if config.get('enabled', False)}
        missing_sources = expected_sources - scanned_sources

        if missing_sources:
            logger.warning(f"\n⚠️  Completion Verification: {len(missing_sources)} sources not scanned")
            logger.warning(f"   Missing: {', '.join(missing_sources)}")
            for missing in missing_sources:
                # Create placeholder result for missing source
                result = SourceScanResult(
                    source_name=missing,
                    source_type=missing,
                    scan_timestamp=datetime.now().isoformat(),
                    errors=[f"Source not scanned - verification failed"]
                )
                self.current_report.source_results.append(result)
        else:
            logger.info(f"\n✅ Completion Verification: All {len(expected_sources)} expected sources scanned")

        # Complete cycle
        cycle_end = datetime.now()
        self.current_report.cycle_end = cycle_end.isoformat()
        duration = (cycle_end - cycle_start).total_seconds()

        # Save report
        self._save_report()

        # FINAL STEP: @DOIT @BDA (Build, Deploy, Activate)
        logger.info(f"\n🚀 FINAL STEP: @DOIT @BDA (Build, Deploy, Activate)")
        try:
            from doit_bda_final_step import DOITBDAFinalStep
            bda = DOITBDAFinalStep()
            bda_result = bda.execute_bda_for_workflow(
                workflow_id=f"daily_work_cycle_{cycle_date}",
                workflow_type="daily_work_cycle",
                workflow_metadata={
                    "sources_scanned": self.current_report.total_sources_scanned,
                    "items_found": self.current_report.total_items_found,
                    "learnings_extracted": self.current_report.total_learnings
                }
            )
            logger.info(f"   ✅ @DOIT @BDA Complete: {bda_result.overall_status.upper()}")
        except Exception as e:
            logger.warning(f"   ⚠️  @DOIT @BDA failed: {e}")

        logger.info(f"\n✅ Daily Work Cycle Complete")
        logger.info(f"   Duration: {duration:.1f} seconds")
        logger.info(f"   Sources scanned: {self.current_report.total_sources_scanned}")
        logger.info(f"   Items found: {self.current_report.total_items_found}")
        logger.info(f"   Learnings extracted: {self.current_report.total_learnings}")

        return self.current_report

    def _scan_internal_sources(self) -> SourceScanResult:
        """Scan internal sources"""
        result = SourceScanResult(
            source_name="internal",
            source_type="internal",
            scan_timestamp=datetime.now().isoformat()
        )

        try:
            # Scan internal data sources
            internal_dirs = [
                self.project_root / "data",
                self.project_root / "logs",
                self.project_root / "config"
            ]

            items_found = 0
            for dir_path in internal_dirs:
                if dir_path.exists():
                    # Count files modified today
                    today = datetime.now().date()
                    for file_path in dir_path.rglob("*"):
                        if file_path.is_file():
                            try:
                                mod_time = datetime.fromtimestamp(file_path.stat().st_mtime).date()
                                if mod_time == today:
                                    items_found += 1
                            except:
                                pass

            result.items_found = items_found
            result.items_processed = items_found
            result.items_new = items_found  # Assume new for today

            result.learnings.append(f"Found {items_found} internal files modified today")

        except Exception as e:
            result.errors.append(f"Error scanning internal sources: {e}")
            logger.error(f"Error scanning internal sources: {e}")

        return result

    def _scan_external_sources(self) -> SourceScanResult:
        """Scan external sources"""
        result = SourceScanResult(
            source_name="external",
            source_type="external",
            scan_timestamp=datetime.now().isoformat()
        )

        try:
            # Scan external APIs, feeds, etc.
            # Placeholder for external source scanning
            result.items_found = 0
            result.items_processed = 0

            result.learnings.append("External sources scanned (placeholder)")

        except Exception as e:
            result.errors.append(f"Error scanning external sources: {e}")
            logger.error(f"Error scanning external sources: {e}")

        return result

    def _scan_youtube_sources(self) -> SourceScanResult:
        """Scan YouTube for learnings"""
        result = SourceScanResult(
            source_name="youtube",
            source_type="youtube",
            scan_timestamp=datetime.now().isoformat()
        )

        learnings = []

        # Always read JSON files directly first (most reliable)
        youtube_data_dir = self.project_root / "data" / "lumina_youtube_learning"
        if youtube_data_dir.exists():
            today = datetime.now().date()
            recent_days = 90  # Include videos from last 90 days (expanded from 30 days)
            cutoff_date = today - timedelta(days=recent_days)

            logger.info("    Reading YouTube learning JSON files directly...")
            for file_path in youtube_data_dir.rglob("*.json"):
                try:
                    with open(file_path, 'r') as f:
                        video_data = json.load(f)
                        file_timestamp = video_data.get('timestamp', '')
                        include = False

                        if file_timestamp:
                            try:
                                file_date = datetime.fromisoformat(file_timestamp).date()
                                if file_date >= cutoff_date:
                                    include = True
                                    logger.debug(f"      Including video from {file_date}")
                            except Exception as e:
                                logger.debug(f"      Timestamp parse error: {e}")
                                mod_time = datetime.fromtimestamp(file_path.stat().st_mtime).date()
                                if mod_time >= cutoff_date:
                                    include = True
                                    logger.debug(f"      Including video from mod time {mod_time}")

                        if include:
                            # Extract directly from JSON
                            review = video_data.get('review', {})
                            video_learnings = review.get('learnings_for_lumina', []) or video_data.get('learnings', [])

                            learning = {
                                'video_id': video_data.get('video_id', ''),
                                'url': video_data.get('url', ''),
                                'title': video_data.get('title', 'Unknown'),
                                'learnings': video_learnings,
                                'rating': review.get('rating') if isinstance(review, dict) else None,
                                'timestamp': video_data.get('timestamp', datetime.now().isoformat())
                            }
                            learnings.append(learning)
                            result.learnings.append(f"Video: {learning['title']} - {len(video_learnings)} learnings")
                            logger.info(f"      ✅ Found: {learning['title']} ({len(video_learnings)} learnings)")
                except Exception as e:
                    logger.warning(f"      ⚠️  Error reading JSON {file_path.name}: {e}")

        logger.info(f"    Total learnings from JSON: {len(learnings)}")

        try:
            # Try to use YouTube learning analysis (for additional videos)
            try:
                from lumina_youtube_learning_analysis import (
                    LuminaYouTubeLearningAnalysis,
                    LearningVideo,
                    FiveStarReview
                )

                logger.info("    Using YouTube Learning Analysis...")
                analyzer = LuminaYouTubeLearningAnalysis()

                # Get today's learnings
                today = datetime.now().date()
                today_videos = []

                # Try different methods to get videos
                if hasattr(analyzer, 'get_videos_learned_today'):
                    today_videos = analyzer.get_videos_learned_today()
                elif hasattr(analyzer, 'learning_videos'):
                    # learning_videos is a dict, get values
                    all_videos = analyzer.learning_videos
                    if isinstance(all_videos, dict):
                        all_videos = list(all_videos.values())

                    # Include videos from recent days (last 7 days)
                    recent_days = 7
                    cutoff_date = today - timedelta(days=recent_days)

                    for video in all_videos:
                        try:
                            # Check if it's a LearningVideo object or dict
                            if hasattr(video, 'timestamp'):
                                video_date = datetime.fromisoformat(video.timestamp).date()
                            elif isinstance(video, dict) and 'timestamp' in video:
                                video_date = datetime.fromisoformat(video['timestamp']).date()
                            else:
                                continue

                            # Include if from today or recent days
                            if video_date >= cutoff_date:
                                today_videos.append(video)
                        except Exception as e:
                            logger.debug(f"Error processing video: {e}")
                            pass
                elif hasattr(analyzer, 'videos'):
                    all_videos = analyzer.videos
                    if isinstance(all_videos, dict):
                        all_videos = list(all_videos.values())

                    for video in all_videos:
                        try:
                            if hasattr(video, 'timestamp'):
                                video_date = datetime.fromisoformat(video.timestamp).date()
                                if video_date == today:
                                    today_videos.append(video)
                        except:
                            pass

                # Also check JSON files directly (fallback) - include recent videos (last 7 days)
                # This ensures we get learnings even if analyzer doesn't work
                youtube_data_dir = self.project_root / "data" / "lumina_youtube_learning"
                if youtube_data_dir.exists():
                    today = datetime.now().date()
                    recent_days = 7  # Include videos from last 7 days
                    cutoff_date = today - timedelta(days=recent_days)

                    json_videos = []
                    for file_path in youtube_data_dir.rglob("*.json"):
                        try:
                            with open(file_path, 'r') as f:
                                video_data = json.load(f)
                                file_timestamp = video_data.get('timestamp', '')
                                include_video = False

                                if file_timestamp:
                                    try:
                                        file_date = datetime.fromisoformat(file_timestamp).date()
                                        if file_date >= cutoff_date:
                                            include_video = True
                                    except:
                                        # If timestamp parsing fails, check file mod time
                                        mod_time = datetime.fromtimestamp(file_path.stat().st_mtime).date()
                                        if mod_time >= cutoff_date:
                                            include_video = True

                                if include_video:
                                    json_videos.append(video_data)
                        except Exception as e:
                            logger.debug(f"Error reading {file_path}: {e}")
                            pass

                    # Add JSON videos to today_videos if not already there
                    if json_videos:
                        # Convert to VideoObj format for consistency
                        for video_data in json_videos:
                            # Check if already in today_videos by video_id
                            video_id = video_data.get('video_id', '')
                            already_added = any(
                                (hasattr(v, 'video_id') and v.video_id == video_id) or
                                (isinstance(v, dict) and v.get('video_id') == video_id)
                                for v in today_videos
                            )

                            if not already_added:
                                class VideoObj:
                                    def __init__(self, data):
                                        for k, v in data.items():
                                            setattr(self, k, v)
                                today_videos.append(VideoObj(video_data))

                # Merge analyzer videos with JSON learnings (avoid duplicates)
                existing_ids = {l.get('video_id') for l in learnings}
                # Only process analyzer videos that aren't already in learnings
                analyzer_videos_to_process = []
                for video in today_videos:
                    try:
                        video_id = getattr(video, 'video_id', None) or (video.get('video_id') if isinstance(video, dict) else None)
                        if video_id and video_id not in existing_ids:
                            analyzer_videos_to_process.append(video)
                    except:
                        pass

                # Update today_videos to only include new ones
                today_videos = analyzer_videos_to_process

                result.items_found = len(today_videos) + len(learnings)
                result.items_processed = len(today_videos) + len(learnings)

                # Extract learnings from analyzer videos
                for video in today_videos:
                    try:
                        # Handle both object and dict formats
                        video_learnings = []
                        rating = None
                        video_id = ''
                        url = ''
                        title = 'Unknown'
                        timestamp = datetime.now().isoformat()

                        if hasattr(video, 'video_id'):
                            # LearningVideo object (or VideoObj created from dict)
                            video_id = video.video_id
                            url = video.url
                            title = video.title
                            timestamp = video.timestamp

                            # Check review (could be object or dict)
                            # First try direct attribute access
                            try:
                                review = getattr(video, 'review', None)
                                if review:
                                    if isinstance(review, dict):
                                        video_learnings = review.get('learnings_for_lumina', [])
                                        rating = review.get('rating')
                                    else:
                                        # It's an object
                                        video_learnings = getattr(review, 'learnings_for_lumina', [])
                                        rating = getattr(review, 'rating', None)
                                        if hasattr(rating, 'value'):
                                            rating = rating.value
                            except Exception as e:
                                logger.debug(f"Error accessing review attribute: {e}")

                            # Also check __dict__ if attribute access didn't work
                            if not video_learnings and hasattr(video, '__dict__'):
                                try:
                                    video_dict = video.__dict__
                                    if 'review' in video_dict:
                                        review = video_dict['review']
                                        if isinstance(review, dict):
                                            video_learnings = review.get('learnings_for_lumina', [])
                                            if not rating:
                                                rating = review.get('rating')
                                except Exception as e:
                                    logger.debug(f"Error accessing __dict__: {e}")

                            if not video_learnings:
                                video_learnings = getattr(video, 'learnings_for_lumina', []) or getattr(video, 'learnings', [])

                        elif isinstance(video, dict):
                            # Dict format - check review.learnings_for_lumina first
                            video_id = video.get('video_id', '')
                            url = video.get('url', '')
                            title = video.get('title', 'Unknown')
                            timestamp = video.get('timestamp', datetime.now().isoformat())

                            if 'review' in video and isinstance(video['review'], dict):
                                video_learnings = video['review'].get('learnings_for_lumina', [])
                                rating = video['review'].get('rating')
                            if not video_learnings:
                                video_learnings = video.get('learnings_for_lumina', []) or video.get('learnings', [])

                        # Create learning entry
                        if video_id or title != 'Unknown':
                            learning = {
                                'video_id': video_id,
                                'url': url,
                                'title': title,
                                'learnings': video_learnings,
                                'rating': rating,
                                'timestamp': timestamp
                            }
                            learnings.append(learning)
                            result.learnings.append(f"Video: {title} - {len(video_learnings)} learnings")
                    except Exception as e:
                        logger.debug(f"Error extracting learning from video: {e}")
                        pass

                result.metadata['learnings'] = learnings
                result.metadata['videos_analyzed'] = len(today_videos)

            except ImportError:
                logger.warning("    YouTube Learning Analysis not available")

            # Fallback: Check for YouTube learning data files
            youtube_data_dir = self.project_root / "data" / "lumina_youtube_learning"
            if youtube_data_dir.exists():
                today_files = []
                today = datetime.now().date()

                for file_path in youtube_data_dir.rglob("*.json"):
                    try:
                        mod_time = datetime.fromtimestamp(file_path.stat().st_mtime).date()
                        # Also check file content timestamp
                        with open(file_path, 'r') as f:
                            video_data = json.load(f)
                            file_timestamp = video_data.get('timestamp', '')
                            if file_timestamp:
                                try:
                                    file_date = datetime.fromisoformat(file_timestamp).date()
                                    if file_date == today or mod_time == today:
                                        today_files.append((file_path, video_data))
                                except:
                                    if mod_time == today:
                                        today_files.append((file_path, video_data))
                            elif mod_time == today:
                                today_files.append((file_path, video_data))
                    except Exception as e:
                        logger.debug(f"Error processing file {file_path}: {e}")
                        pass

                # Extract learnings from files
                for file_path, video_data in today_files:
                    try:
                        # Get learnings from review.learnings_for_lumina
                        review = video_data.get('review', {})
                        video_learnings = review.get('learnings_for_lumina', []) or video_data.get('learnings', [])

                        learning = {
                            'video_id': video_data.get('video_id', ''),
                            'url': video_data.get('url', ''),
                            'title': video_data.get('title', 'Unknown'),
                            'learnings': video_learnings,
                            'rating': review.get('rating') if isinstance(review, dict) else None,
                            'timestamp': video_data.get('timestamp', datetime.now().isoformat())
                        }
                        learnings.append(learning)
                        result.learnings.append(f"Video: {learning['title']} - {len(video_learnings)} learnings")
                    except Exception as e:
                        logger.debug(f"Error extracting from {file_path}: {e}")
                        pass

                result.items_found = len(today_files)
                result.items_processed = len(today_files)
                result.metadata['learnings'] = learnings
            else:
                # Also check old location
                youtube_data_dir = self.project_root / "data" / "youtube"
                if youtube_data_dir.exists():
                    today_files = []
                    today = datetime.now().date()

                    for file_path in youtube_data_dir.rglob("*.json"):
                        try:
                            mod_time = datetime.fromtimestamp(file_path.stat().st_mtime).date()
                            if mod_time == today:
                                today_files.append(file_path)

                                # Try to extract learnings from file
                                with open(file_path, 'r') as f:
                                    data = json.load(f)
                                    if 'learnings' in data:
                                        learnings.extend(data['learnings'])
                                    if 'title' in data:
                                        result.learnings.append(f"Video: {data.get('title', 'Unknown')}")
                        except:
                            pass

                    result.items_found = len(today_files)
                    result.items_processed = len(today_files)
                    result.metadata['learnings'] = learnings
                else:
                    result.learnings.append("No YouTube data directory found")

        except Exception as e:
            result.errors.append(f"Error scanning YouTube: {e}")
            logger.error(f"Error scanning YouTube: {e}", exc_info=True)

        return result

    def _scan_holocron(self) -> SourceScanResult:
        """Scan Holocron knowledge base"""
        result = SourceScanResult(
            source_name="holocron",
            source_type="holocron",
            scan_timestamp=datetime.now().isoformat()
        )

        try:
            holocron_dir = self.project_root / "data" / "holocron"
            if holocron_dir.exists():
                # Count entries modified today
                today = datetime.now().date()
                items_found = 0

                for file_path in holocron_dir.rglob("*.json"):
                    try:
                        mod_time = datetime.fromtimestamp(file_path.stat().st_mtime).date()
                        if mod_time == today:
                            items_found += 1
                    except:
                        pass

                result.items_found = items_found
                result.items_processed = items_found
                result.learnings.append(f"Found {items_found} Holocron entries modified today")
            else:
                result.learnings.append("Holocron directory not found")

        except Exception as e:
            result.errors.append(f"Error scanning Holocron: {e}")
            logger.error(f"Error scanning Holocron: {e}")

        return result

    def _scan_emails(self) -> SourceScanResult:
        """Syphon emails via NAS Mail Hub"""
        result = SourceScanResult(
            source_name="email",
            source_type="email",
            scan_timestamp=datetime.now().isoformat()
        )

        try:
            # Use JARVIS email syphon
            try:
                from jarvis_syphon_all_emails_nas_hub import JARVISEmailSyphonNASHub

                syphon = JARVISEmailSyphonNASHub()
                summary = syphon.syphon_all_accounts(days=30)

                result.items_found = summary.get('total_emails', 0)
                result.items_processed = summary.get('total_emails', 0)
                result.items_new = summary.get('total_emails', 0)  # Assume new for daily scan

                learnings = []
                for account_result in summary.get('results', []):
                    if account_result.get('learnings_extracted', 0) > 0:
                        learnings.append(f"{account_result['account_name']}: {account_result['learnings_extracted']} learnings")

                result.learnings = learnings
                result.metadata = {
                    'accounts_processed': summary.get('accounts_processed', 0),
                    'total_learnings': summary.get('total_learnings', 0),
                    'duration_seconds': summary.get('duration_seconds', 0)
                }

            except ImportError:
                logger.warning("    JARVIS email syphon not available")
                result.learnings.append("Email syphon system not available")

        except Exception as e:
            result.errors.append(f"Error syphoning emails: {e}")
            logger.error(f"Error syphoning emails: {e}", exc_info=True)

        return result

    def _scan_email_sources(self) -> SourceScanResult:
        """Scan emails via NAS Company Mail Hub"""
        result = SourceScanResult(
            source_name="email",
            source_type="email",
            scan_timestamp=datetime.now().isoformat()
        )

        try:
            # Use JARVIS Email Syphon via NAS Hub
            try:
                from jarvis_syphon_all_emails_nas_hub import JARVISEmailSyphonNASHub

                logger.info("    Using JARVIS Email Syphon via NAS Company Mail Hub...")
                email_syphon = JARVISEmailSyphonNASHub()

                # Syphon all email accounts (last 30 days)
                syphon_summary = email_syphon.syphon_all_accounts(days=30)

                # Extract from summary dict
                total_emails = syphon_summary.get('total_emails', 0)
                total_learnings = syphon_summary.get('total_learnings', 0)
                total_duration = syphon_summary.get('duration_seconds', 0)
                accounts_processed = syphon_summary.get('accounts_processed', 0)
                account_results = syphon_summary.get('results', [])

                # Calculate totals from results
                total_processed = sum(r.get('emails_processed', r.get('emails_found', 0)) for r in account_results)
                total_new = sum(r.get('emails_new', r.get('emails_found', 0)) for r in account_results)

                result.items_found = total_emails
                result.items_processed = total_processed
                result.items_new = total_new

                result.learnings.append(f"Syphoned {total_emails} emails from {accounts_processed} accounts")
                result.learnings.append(f"Extracted {total_learnings} learnings from emails")
                result.learnings.append(f"Duration: {total_duration:.1f} seconds")

                result.metadata = {
                    'accounts_processed': accounts_processed,
                    'total_learnings': total_learnings,
                    'duration_seconds': total_duration,
                    'accounts': [
                        {
                            'account': r.get('account_name', 'Unknown'),
                            'emails': r.get('emails_found', 0),
                            'learnings': r.get('learnings_extracted', 0)
                        }
                        for r in account_results
                    ]
                }

            except ImportError:
                logger.warning("    JARVIS Email Syphon not available")
                result.learnings.append("Email syphoning not available - install dependencies")
            except Exception as e:
                logger.error(f"    Error syphoning emails: {e}", exc_info=True)
                result.errors.append(f"Error syphoning emails: {e}")

        except Exception as e:
            result.errors.append(f"Error scanning email sources: {e}")
            logger.error(f"Error scanning email sources: {e}")

        return result

    def _scan_r5(self) -> SourceScanResult:
        """Scan R5 Living Context Matrix"""
        result = SourceScanResult(
            source_name="r5",
            source_type="r5",
            scan_timestamp=datetime.now().isoformat()
        )

        try:
            r5_dir = self.project_root / "data" / "r5_living_matrix"
            if r5_dir.exists():
                # Count sessions/entries modified today
                today = datetime.now().date()
                items_found = 0

                for file_path in r5_dir.rglob("*.json"):
                    try:
                        mod_time = datetime.fromtimestamp(file_path.stat().st_mtime).date()
                        if mod_time == today:
                            items_found += 1
                    except:
                        pass

                result.items_found = items_found
                result.items_processed = items_found
                result.learnings.append(f"Found {items_found} R5 entries modified today")
            else:
                result.learnings.append("R5 directory not found")

        except Exception as e:
            result.errors.append(f"Error scanning R5: {e}")
            logger.error(f"Error scanning R5: {e}")

        return result

    def _scan_cursor_ide_developments(self) -> SourceScanResult:
        """Scan Cursor IDE for new developments (keep finger on the pulse)"""
        result = SourceScanResult(
            source_name="cursor_ide_developments",
            source_type="cursor_ide",
            scan_timestamp=datetime.now().isoformat()
        )

        try:
            from jarvis_cursor_ide_development_monitor import JARVISCursorIDEDevelopmentMonitor
            from cursor_ide_auto_update_feature_tracker import CursorIDEAutoUpdateFeatureTracker

            # Monitor for new developments
            monitor = JARVISCursorIDEDevelopmentMonitor(self.project_root)
            new_devs = monitor.monitor_all_sources()

            result.items_found = len(new_devs)
            result.items_new = len(new_devs)

            if new_devs:
                result.items_processed = len(new_devs)
                result.learnings.append(f"Found {len(new_devs)} new Cursor IDE developments")

                # Get actionable developments
                actionable = monitor.get_actionable_developments()
                if actionable:
                    result.learnings.append(f"{len(actionable)} developments are actionable and verified")
                    result.metadata['actionable_count'] = len(actionable)
                    result.metadata['actionable_developments'] = [d.to_dict() for d in actionable]

                # Auto-sync to feature tracker
                updater = CursorIDEAutoUpdateFeatureTracker(self.project_root)
                updater.sync_new_features()

                # Get pulse status
                pulse = monitor.get_pulse_report()
                result.metadata['pulse_status'] = pulse['pulse_status']
                result.metadata['ready_to_pivot'] = pulse['ready_to_pivot']

                if pulse['ready_to_pivot']:
                    result.learnings.append("⚡ Ready to pivot on new features!")
            else:
                result.items_processed = 0
                result.learnings.append("No new Cursor IDE developments (pulse stable)")

                # Still get pulse status
                pulse = monitor.get_pulse_report()
                result.metadata['pulse_status'] = pulse['pulse_status']
                result.metadata['ready_to_pivot'] = pulse['ready_to_pivot']

        except ImportError as e:
            result.errors.append(f"Cursor IDE monitor not available: {e}")
            result.learnings.append("Cursor IDE monitoring not available")
        except Exception as e:
            result.errors.append(f"Error monitoring Cursor IDE: {e}")
            logger.error(f"Error monitoring Cursor IDE: {e}")

        return result

    def _generate_summary(self):
        """Generate cycle summary"""
        if not self.current_report:
            return

        # Calculate totals
        self.current_report.total_sources_scanned = len(self.current_report.source_results)
        self.current_report.total_items_found = sum(r.items_found for r in self.current_report.source_results)
        self.current_report.total_items_processed = sum(r.items_processed for r in self.current_report.source_results)

        # Calculate estimated duration
        cycle_start = datetime.fromisoformat(self.current_report.cycle_start)
        cycle_end = datetime.fromisoformat(self.current_report.cycle_end) if self.current_report.cycle_end else datetime.now()
        actual_duration = (cycle_end - cycle_start).total_seconds()

        # Estimate future duration (based on current + email if not run)
        estimated_duration = actual_duration
        if not any(r.source_name == 'email' for r in self.current_report.source_results):
            # Add email estimate if not run
            estimated_duration += self.sources['email']['estimated_duration_seconds']

        # Count learnings
        all_learnings = []
        for result in self.current_report.source_results:
            all_learnings.extend(result.learnings)

        self.current_report.total_learnings = len(all_learnings)

        # Add performance metrics
        self.current_report.summary['performance'] = {
            'actual_duration_seconds': actual_duration,
            'estimated_duration_seconds': estimated_duration,
            'estimated_duration_minutes': estimated_duration / 60,
            'sources_per_second': len(self.current_report.source_results) / actual_duration if actual_duration > 0 else 0
        }

        # YouTube-specific summary
        youtube_result = next((r for r in self.current_report.source_results if r.source_name == "youtube"), None)
        if youtube_result:
            self.current_report.summary['youtube'] = {
                'videos_found': youtube_result.items_found,
                'learnings_count': len(youtube_result.metadata.get('learnings', [])),
                'top_learnings': youtube_result.metadata.get('learnings', [])[:5]
            }

        # Overall summary
        self.current_report.summary['overall'] = {
            'sources_scanned': self.current_report.total_sources_scanned,
            'items_found': self.current_report.total_items_found,
            'items_processed': self.current_report.total_items_processed,
            'total_learnings': self.current_report.total_learnings,
            'errors': sum(len(r.errors) for r in self.current_report.source_results)
        }

    def _save_report(self):
        try:
            """Save cycle report"""
            if not self.current_report:
                return

            report_file = self.data_dir / f"cycle_report_{self.current_report.cycle_date}.json"

            with open(report_file, 'w') as f:
                json.dump(self.current_report.to_dict(), f, indent=2, default=str)

            logger.info(f"📄 Report saved: {report_file}")

        except Exception as e:
            self.logger.error(f"Error in _save_report: {e}", exc_info=True)
            raise
    def get_youtube_learnings_today(self) -> List[Dict[str, Any]]:
        """Get YouTube learnings from today"""
        if self.current_report:
            return self.current_report.youtube_learnings

        # Run YouTube scan if not done
        result = self._scan_youtube_sources()
        return result.metadata.get('learnings', [])

    def get_daily_summary(self) -> Dict[str, Any]:
        try:
            """Get summary of today's work cycle"""
            today = datetime.now().strftime('%Y-%m-%d')
            report_file = self.data_dir / f"cycle_report_{today}.json"

            if report_file.exists():
                with open(report_file, 'r') as f:
                    return json.load(f)

            # Run cycle if not done today
            report = self.run_full_cycle()
            return report.to_dict()


        except Exception as e:
            self.logger.error(f"Error in get_daily_summary: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description='Daily Work Cycle System')
        parser.add_argument('--run-cycle', action='store_true', help='Run full work cycle')
        parser.add_argument('--youtube-only', action='store_true', help='Get YouTube learnings only')
        parser.add_argument('--summary', action='store_true', help='Get today\'s summary')

        args = parser.parse_args()

        cycle = DailyWorkCycle()

        if args.youtube_only:
            learnings = cycle.get_youtube_learnings_today()
            print("\n🎥 YouTube Learnings Today:")
            print("=" * 80)
            for i, learning in enumerate(learnings, 1):
                print(f"\n{i}. {learning.get('title', 'Unknown Video')}")
                print(f"   URL: {learning.get('url', 'N/A')}")
                rating = learning.get('rating', 0) or 0
                if isinstance(rating, int):
                    print(f"   Rating: {'⭐' * rating}")
                else:
                    print(f"   Rating: {rating}")
                print(f"   Learnings: {len(learning.get('learnings', []))}")
                for learn in learning.get('learnings', [])[:3]:
                    print(f"     - {learn}")

        elif args.summary:
            summary = cycle.get_daily_summary()
            print("\n📊 Daily Work Cycle Summary:")
            print("=" * 80)
            print(json.dumps(summary.get('summary', {}), indent=2))

            if 'youtube' in summary.get('summary', {}):
                print("\n🎥 YouTube Summary:")
                print(json.dumps(summary['summary']['youtube'], indent=2))

        else:
            # Run full cycle
            report = cycle.run_full_cycle()

            print("\n" + "=" * 80)
            print("📊 Daily Work Cycle Report")
            print("=" * 80)
            print(f"Date: {report.cycle_date}")
            print(f"Duration: {(datetime.fromisoformat(report.cycle_end) - datetime.fromisoformat(report.cycle_start)).total_seconds():.1f}s")
            print(f"Sources Scanned: {report.total_sources_scanned}")
            print(f"Items Found: {report.total_items_found}")
            print(f"Items Processed: {report.total_items_processed}")
            print(f"Total Learnings: {report.total_learnings}")

            if report.youtube_learnings:
                print(f"\n🎥 YouTube Learnings: {len(report.youtube_learnings)}")
                for learning in report.youtube_learnings[:5]:
                    print(f"  - {learning.get('title', 'Unknown')}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()