#!/usr/bin/env python3
"""
LUMINA Data Consolidator - Unified Data Consolidation System
📚 Consolidates Documents, Holocrons, and YouTube Videos for Docuseries

Features:
- Document Consolidation: Aggregates all docs/ files
- Holocron Consolidation: Consolidates data/holocron/ entries
- YouTube Video Consolidation: Prepares videos for docuseries
- Parallel Processing: 4-5 concurrent workers with @bal/@measure integration
- @Sparks Generation: Discovers insights, enhancements, and improvements
- SYPHON Telemetry: Full workflow observability and continuous improvement

Tags: #CONSOLIDATION #HOLOCRON #DOCUSERIES #PARALLEL #SPARKS #TELEMETRY @JARVIS @SYPHON
"""

import sys
import json
import asyncio
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum
import logging
import time

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LuminaDataConsolidator")

# Import SYPHON telemetry
try:
    from syphon_workflow_telemetry_system import (
        SYPHONWorkflowTelemetrySystem,
        TelemetryEventType,
        get_telemetry_system
    )
    TELEMETRY_AVAILABLE = True
except ImportError:
    TELEMETRY_AVAILABLE = False
    logger.warning("SYPHON telemetry not available")

# Import measurement gatekeeper
try:
    from measurement_gatekeeper import MeasurementGatekeeper, MeasurementLevel
    MEASUREMENT_AVAILABLE = True
except ImportError:
    MEASUREMENT_AVAILABLE = False
    logger.warning("Measurement gatekeeper not available")


class ConsolidationType(Enum):
    """Types of data to consolidate"""
    DOCUMENTS = "documents"
    HOLOCRONS = "holocrons"
    YOUTUBE_VIDEOS = "youtube_videos"
    ALL = "all"


@dataclass
class ConsolidationSpark:
    """@Sparks: Insights, enhancements, and improvements discovered"""
    spark_id: str
    spark_type: str  # "insight", "enhancement", "improvement", "optimization"
    title: str
    description: str
    impact: str  # "high", "medium", "low"
    category: str  # "performance", "reliability", "efficiency", "scaling"
    discovered_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metrics: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ConsolidatedItem:
    """Single consolidated item"""
    item_id: str
    item_type: str  # "document", "holocron", "youtube_video"
    source_path: str
    title: str
    content_hash: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    consolidated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ConsolidationMetrics:
    """Performance metrics for consolidation"""
    total_items: int = 0
    processed_items: int = 0
    failed_items: int = 0
    total_duration: float = 0.0
    average_item_duration: float = 0.0
    parallel_workers: int = 0
    throughput_items_per_second: float = 0.0
    memory_usage_mb: float = 0.0
    sparks_generated: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LuminaDataConsolidator:
    """
    LUMINA Data Consolidator

    Consolidates documents, holocrons, and YouTube videos with:
    - Optimized parallel processing (4-5 workers)
    - @bal/@measure integration
    - @Sparks insights generation
    - SYPHON telemetry
    """

    def __init__(self, project_root: Optional[Path] = None, max_workers: int = 5, 
                 use_dynamic_workers: bool = True):
        """Initialize data consolidator"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger
        self.max_workers = max_workers  # 4-5 concurrent workers
        self.use_dynamic_workers = use_dynamic_workers  # @bal: Dynamic worker adjustment
        self.current_workers = max_workers

        # Initialize telemetry
        self.telemetry_system = None
        if TELEMETRY_AVAILABLE:
            try:
                self.telemetry_system = get_telemetry_system()
                logger.info("✅ SYPHON telemetry initialized")
            except Exception as e:
                logger.warning(f"⚠️  Telemetry initialization failed: {e}")

        # Initialize measurement gatekeeper
        self.measurement_gatekeeper = None
        if MEASUREMENT_AVAILABLE:
            try:
                self.measurement_gatekeeper = MeasurementGatekeeper()
                logger.info("✅ Measurement gatekeeper initialized")
            except Exception as e:
                logger.warning(f"⚠️  Measurement gatekeeper initialization failed: {e}")

        # Data directories
        self.docs_dir = self.project_root / "docs"
        self.holocron_dir = self.project_root / "data" / "holocron"
        self.youtube_dir = self.project_root / "data" / "youtube_intelligence"

        # Output directories
        self.consolidated_dir = self.project_root / "data" / "consolidated"
        self.consolidated_dir.mkdir(parents=True, exist_ok=True)

        self.sparks_dir = self.consolidated_dir / "sparks"
        self.sparks_dir.mkdir(parents=True, exist_ok=True)

        # Consolidated data storage
        self.consolidated_items: List[ConsolidatedItem] = []
        self.sparks: List[ConsolidationSpark] = []
        self.metrics = ConsolidationMetrics(parallel_workers=max_workers)

        logger.info("📚 LUMINA Data Consolidator initialized")
        logger.info(f"   Max workers: {max_workers}")
        logger.info(f"   Docs: {self.docs_dir}")
        logger.info(f"   Holocrons: {self.holocron_dir}")
        logger.info(f"   YouTube: {self.youtube_dir}")

    def _calculate_content_hash(self, content: str) -> str:
        """Calculate SHA256 hash of content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _process_document(self, doc_path: Path) -> Optional[ConsolidatedItem]:
        """Process a single document"""
        try:
            # Read document
            content = doc_path.read_text(encoding='utf-8', errors='ignore')
            content_hash = self._calculate_content_hash(content)

            # Extract metadata
            title = doc_path.stem
            metadata = {
                "file_size": len(content),
                "file_extension": doc_path.suffix,
                "lines": len(content.splitlines()),
                "words": len(content.split())
            }

            # Extract tags from content (look for #tags)
            tags = []
            for line in content.splitlines()[:50]:  # Check first 50 lines
                if '#' in line:
                    tags.extend([tag.strip('#') for tag in line.split() if tag.startswith('#')])

            item = ConsolidatedItem(
                item_id=f"doc_{content_hash[:16]}",
                item_type="document",
                source_path=str(doc_path.relative_to(self.project_root)),
                title=title,
                content_hash=content_hash,
                metadata=metadata,
                tags=list(set(tags))[:10]  # Limit to 10 unique tags
            )

            return item

        except Exception as e:
            self.logger.error(f"❌ Error processing document {doc_path}: {e}")
            return None

    def _process_holocron(self, holocron_path: Path) -> Optional[ConsolidatedItem]:
        """Process a single holocron entry"""
        try:
            # Read holocron
            if holocron_path.suffix == '.json':
                data = json.loads(holocron_path.read_text(encoding='utf-8'))
                content = json.dumps(data, indent=2)
            else:
                content = holocron_path.read_text(encoding='utf-8', errors='ignore')

            content_hash = self._calculate_content_hash(content)

            # Extract metadata
            title = holocron_path.stem
            metadata = {
                "file_size": len(content),
                "file_extension": holocron_path.suffix,
                "is_json": holocron_path.suffix == '.json'
            }

            # Extract tags from holocron content
            tags = []
            if isinstance(data, dict) if holocron_path.suffix == '.json' else False:
                tags = data.get("tags", [])

            item = ConsolidatedItem(
                item_id=f"holocron_{content_hash[:16]}",
                item_type="holocron",
                source_path=str(holocron_path.relative_to(self.project_root)),
                title=title,
                content_hash=content_hash,
                metadata=metadata,
                tags=tags[:10] if isinstance(tags, list) else []
            )

            return item

        except Exception as e:
            self.logger.error(f"❌ Error processing holocron {holocron_path}: {e}")
            return None

    def _process_youtube_video(self, video_data: Dict[str, Any]) -> Optional[ConsolidatedItem]:
        """Process a single YouTube video"""
        try:
            # Extract video information
            video_id = video_data.get("video_id") or video_data.get("id", "unknown")
            title = video_data.get("title", "Untitled")
            url = video_data.get("url", "")

            # Create content representation
            content = json.dumps(video_data, indent=2)
            content_hash = self._calculate_content_hash(content)

            metadata = {
                "video_id": video_id,
                "url": url,
                "view_count": video_data.get("view_count", 0),
                "duration": video_data.get("duration", "unknown"),
                "upload_date": video_data.get("upload_date", "unknown")
            }

            item = ConsolidatedItem(
                item_id=f"youtube_{content_hash[:16]}",
                item_type="youtube_video",
                source_path=url,
                title=title,
                content_hash=content_hash,
                metadata=metadata,
                tags=["youtube", "video", "docuseries"]
            )

            return item

        except Exception as e:
            self.logger.error(f"❌ Error processing YouTube video: {e}")
            return None

    def _generate_sparks(self, metrics: ConsolidationMetrics) -> List[ConsolidationSpark]:
        """Generate @Sparks: Insights, enhancements, and improvements"""
        sparks = []

        # Performance insights
        if metrics.throughput_items_per_second < 10:
            sparks.append(ConsolidationSpark(
                spark_id=f"spark_perf_{int(time.time())}",
                spark_type="optimization",
                title="Low Throughput Detected",
                description=f"Throughput is {metrics.throughput_items_per_second:.2f} items/sec. Consider increasing parallel workers or optimizing I/O.",
                impact="high",
                category="performance",
                metrics={"throughput": metrics.throughput_items_per_second},
                recommendations=[
                    "Increase max_workers if CPU/memory allows",
                    "Optimize file I/O operations",
                    "Consider async I/O for better concurrency"
                ]
            ))

        # Parallel processing insights
        if metrics.parallel_workers < 4:
            sparks.append(ConsolidationSpark(
                spark_id=f"spark_parallel_{int(time.time())}",
                spark_type="enhancement",
                title="Parallel Processing Opportunity",
                description=f"Only {metrics.parallel_workers} workers active. System may benefit from more concurrent processing.",
                impact="medium",
                category="scaling",
                metrics={"workers": metrics.parallel_workers},
                recommendations=[
                    "Increase max_workers to 4-5 for optimal throughput",
                    "Monitor CPU and memory usage",
                    "Use @bal/@measure to optimize worker count dynamically"
                ]
            ))

        # Memory optimization
        if metrics.memory_usage_mb > 1000:
            sparks.append(ConsolidationSpark(
                spark_id=f"spark_memory_{int(time.time())}",
                spark_type="improvement",
                title="Memory Usage Optimization",
                description=f"Memory usage is {metrics.memory_usage_mb:.2f} MB. Consider streaming or batch processing.",
                impact="medium",
                category="efficiency",
                metrics={"memory_mb": metrics.memory_usage_mb},
                recommendations=[
                    "Implement streaming for large files",
                    "Process in smaller batches",
                    "Clear processed items from memory"
                ]
            ))

        # Reliability insights
        if metrics.failed_items > 0:
            failure_rate = (metrics.failed_items / metrics.total_items) * 100
            if failure_rate > 5:
                sparks.append(ConsolidationSpark(
                    spark_id=f"spark_reliability_{int(time.time())}",
                    spark_type="improvement",
                    title="High Failure Rate Detected",
                    description=f"Failure rate is {failure_rate:.2f}%. Review error handling and retry logic.",
                    impact="high",
                    category="reliability",
                    metrics={"failure_rate": failure_rate, "failed_items": metrics.failed_items},
                    recommendations=[
                        "Improve error handling",
                        "Add retry logic with exponential backoff",
                        "Log detailed error information"
                    ]
                ))

        # @bal/@measure integration insights
        if metrics.parallel_workers > 0:
            efficiency = metrics.throughput_items_per_second / metrics.parallel_workers
            if efficiency < 2.0:
                sparks.append(ConsolidationSpark(
                    spark_id=f"spark_bal_{int(time.time())}",
                    spark_type="optimization",
                    title="@bal/@measure Performance Optimization",
                    description=f"Worker efficiency is {efficiency:.2f} items/sec/worker. Consider dynamic worker adjustment.",
                    impact="medium",
                    category="performance",
                    metrics={"efficiency": efficiency, "workers": metrics.parallel_workers},
                    recommendations=[
                        "Use @bal to dynamically adjust worker count based on load",
                        "Monitor @measure metrics for optimal worker count",
                        "Consider reducing workers if efficiency is low"
                    ]
                ))

        return sparks

    def consolidate_documents(self) -> List[ConsolidatedItem]:
        """Consolidate all documents"""
        self.logger.info("📄 Consolidating documents...")

        # Find all markdown files in docs/
        doc_files = list(self.docs_dir.rglob("*.md"))
        self.logger.info(f"   Found {len(doc_files)} documents")

        items = []
        start_time = time.time()

        # @bal: Dynamic worker adjustment
        effective_workers = self._calculate_optimal_workers(len(doc_files))

        # Process in parallel with ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=effective_workers) as executor:
            future_to_doc = {executor.submit(self._process_document, doc_path): doc_path 
                           for doc_path in doc_files}

            for future in as_completed(future_to_doc):
                doc_path = future_to_doc[future]
                try:
                    item = future.result()
                    if item:
                        items.append(item)
                        self.metrics.processed_items += 1
                except Exception as e:
                    self.logger.error(f"❌ Error processing {doc_path}: {e}")
                    self.metrics.failed_items += 1

        duration = time.time() - start_time
        self.metrics.total_duration += duration
        self.metrics.total_items += len(doc_files)

        self.logger.info(f"✅ Consolidated {len(items)} documents in {duration:.2f}s")
        return items

    def consolidate_holocrons(self) -> List[ConsolidatedItem]:
        """Consolidate all holocrons"""
        self.logger.info("📚 Consolidating holocrons...")

        # Find all holocron files
        holocron_files = list(self.holocron_dir.rglob("*.md")) + list(self.holocron_dir.rglob("*.json"))
        self.logger.info(f"   Found {len(holocron_files)} holocron files")

        items = []
        start_time = time.time()

        # @bal: Dynamic worker adjustment
        effective_workers = self._calculate_optimal_workers(len(holocron_files))

        # Process in parallel
        with ThreadPoolExecutor(max_workers=effective_workers) as executor:
            future_to_holocron = {executor.submit(self._process_holocron, holocron_path): holocron_path 
                                 for holocron_path in holocron_files}

            for future in as_completed(future_to_holocron):
                holocron_path = future_to_holocron[future]
                try:
                    item = future.result()
                    if item:
                        items.append(item)
                        self.metrics.processed_items += 1
                except Exception as e:
                    self.logger.error(f"❌ Error processing {holocron_path}: {e}")
                    self.metrics.failed_items += 1

        duration = time.time() - start_time
        self.metrics.total_duration += duration
        self.metrics.total_items += len(holocron_files)

        self.logger.info(f"✅ Consolidated {len(items)} holocrons in {duration:.2f}s")
        return items

    def consolidate_youtube_videos(self) -> List[ConsolidatedItem]:
        """Consolidate YouTube videos for docuseries"""
        self.logger.info("🎬 Consolidating YouTube videos...")

        # Load YouTube intelligence data
        sme_map_file = self.youtube_dir / "sme_map.json"
        intelligence_file = self.youtube_dir / "intelligence_aggregate.json"

        items = []
        start_time = time.time()

        # Process SME map
        if sme_map_file.exists():
            try:
                with open(sme_map_file, 'r', encoding='utf-8') as f:
                    sme_data = json.load(f)
                    smes = sme_data.get("smes", [])

                    for sme in smes:
                        videos = sme.get("videos", [])
                        for video in videos:
                            item = self._process_youtube_video(video)
                            if item:
                                items.append(item)
                                self.metrics.processed_items += 1
            except Exception as e:
                self.logger.error(f"❌ Error processing SME map: {e}")
                self.metrics.failed_items += 1

        # Process intelligence aggregate
        if intelligence_file.exists():
            try:
                with open(intelligence_file, 'r', encoding='utf-8') as f:
                    intel_data = json.load(f)
                    # Extract video intelligence
                    # (Add logic to extract video data from intelligence)
            except Exception as e:
                self.logger.error(f"❌ Error processing intelligence: {e}")

        duration = time.time() - start_time
        self.metrics.total_duration += duration
        self.metrics.total_items += len(items)

        self.logger.info(f"✅ Consolidated {len(items)} YouTube videos in {duration:.2f}s")
        return items

    def consolidate_all(self, consolidation_type: ConsolidationType = ConsolidationType.ALL) -> Dict[str, Any]:
        """Consolidate all data types"""
        self.logger.info("="*80)
        self.logger.info("📚 LUMINA DATA CONSOLIDATION STARTING")
        self.logger.info("="*80)

        execution_id = f"consolidation_{int(time.time())}"
        start_time = time.time()

        # Track with telemetry
        if self.telemetry_system:
            self.telemetry_system.capture_event(
                event_type=TelemetryEventType.WORKFLOW_START,
                workflow_id="lumina_data_consolidation",
                workflow_name="LUMINA Data Consolidation",
                execution_id=execution_id,
                data={"consolidation_type": consolidation_type.value},
                tags=["consolidation", "parallel"]
            )

        # Measure with gatekeeper
        if self.measurement_gatekeeper:
            measurement = self.measurement_gatekeeper.start_measurement(
                operation="lumina_data_consolidation",
                component="LuminaDataConsolidator",
                level=MeasurementLevel.HIGH
            )

        all_items = []

        try:
            # Consolidate based on type
            if consolidation_type in [ConsolidationType.DOCUMENTS, ConsolidationType.ALL]:
                doc_items = self.consolidate_documents()
                all_items.extend(doc_items)

            if consolidation_type in [ConsolidationType.HOLOCRONS, ConsolidationType.ALL]:
                holocron_items = self.consolidate_holocrons()
                all_items.extend(holocron_items)

            if consolidation_type in [ConsolidationType.YOUTUBE_VIDEOS, ConsolidationType.ALL]:
                youtube_items = self.consolidate_youtube_videos()
                all_items.extend(youtube_items)

            # Calculate final metrics
            total_duration = time.time() - start_time
            self.metrics.average_item_duration = total_duration / len(all_items) if all_items else 0
            self.metrics.throughput_items_per_second = len(all_items) / total_duration if total_duration > 0 else 0

            # Generate @Sparks
            self.sparks = self._generate_sparks(self.metrics)
            self.metrics.sparks_generated = len(self.sparks)

            # Save consolidated data
            self._save_consolidated_data(all_items)
            self._save_sparks()

            # Generate docuseries script
            docuseries_script = self.generate_docuseries_script(all_items)

            # Track completion with telemetry
            if self.telemetry_system:
                self.telemetry_system.track_workflow_execution(
                    workflow_id="lumina_data_consolidation",
                    workflow_name="LUMINA Data Consolidation",
                    execution_id=execution_id,
                    started_at=datetime.fromtimestamp(start_time),
                    ended_at=datetime.now(),
                    success=True,
                    outcome_text=f"Consolidated {len(all_items)} items",
                    metrics=self.metrics.to_dict()
                )

            # Complete measurement
            if self.measurement_gatekeeper and 'measurement' in locals():
                self.measurement_gatekeeper.complete_measurement(
                    measurement.measurement_id,
                    result={"items_consolidated": len(all_items), "sparks": len(self.sparks)},
                    duration_ms=total_duration * 1000
                )

            self.logger.info("="*80)
            self.logger.info("✅ LUMINA DATA CONSOLIDATION COMPLETE")
            self.logger.info("="*80)
            self.logger.info(f"📊 Results:")
            self.logger.info(f"   Total items: {len(all_items)}")
            self.logger.info(f"   Duration: {total_duration:.2f}s")
            self.logger.info(f"   Throughput: {self.metrics.throughput_items_per_second:.2f} items/sec")
            self.logger.info(f"   @Sparks generated: {len(self.sparks)}")
            self.logger.info("="*80)

            return {
                "success": True,
                "items": [item.to_dict() for item in all_items],
                "sparks": [spark.to_dict() for spark in self.sparks],
                "metrics": self.metrics.to_dict(),
                "docuseries_script": docuseries_script
            }

        except Exception as e:
            self.logger.error(f"❌ Consolidation failed: {e}", exc_info=True)

            # Track failure
            if self.telemetry_system:
                self.telemetry_system.capture_event(
                    event_type=TelemetryEventType.WORKFLOW_ERROR,
                    workflow_id="lumina_data_consolidation",
                    workflow_name="LUMINA Data Consolidation",
                    execution_id=execution_id,
                    data={"error": str(e)},
                    tags=["consolidation", "error"]
                )

            return {
                "success": False,
                "error": str(e),
                "items": [],
                "sparks": [],
                "metrics": self.metrics.to_dict(),
                "docuseries_script": None
            }

    def _save_consolidated_data(self, items: List[ConsolidatedItem]) -> None:
        try:
            """Save consolidated data to disk"""
            consolidated_file = self.consolidated_dir / f"consolidated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            data = {
                "consolidated_at": datetime.now().isoformat(),
                "total_items": len(items),
                "items": [item.to_dict() for item in items]
            }

            with open(consolidated_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"💾 Saved consolidated data: {consolidated_file.name}")

        except Exception as e:
            self.logger.error(f"Error in _save_consolidated_data: {e}", exc_info=True)
            raise
    def _calculate_optimal_workers(self, item_count: int) -> int:
        """@bal: Calculate optimal worker count based on load"""
        if not self.use_dynamic_workers:
            return self.max_workers

        # Dynamic calculation based on item count and system capacity
        # Optimal: 4-5 workers for most cases
        # Scale down for small batches, scale up for large batches (with limits)
        if item_count < 10:
            optimal = min(2, self.max_workers)
        elif item_count < 50:
            optimal = min(4, self.max_workers)
        elif item_count < 200:
            optimal = min(5, self.max_workers)
        else:
            optimal = self.max_workers

        self.current_workers = optimal
        return optimal

    def _save_sparks(self) -> None:
        try:
            """Save @Sparks to disk"""
            sparks_file = self.sparks_dir / f"sparks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            data = {
                "generated_at": datetime.now().isoformat(),
                "total_sparks": len(self.sparks),
                "sparks": [spark.to_dict() for spark in self.sparks]
            }

            with open(sparks_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"✨ Saved @Sparks: {sparks_file.name}")

        except Exception as e:
            self.logger.error(f"Error in _save_sparks: {e}", exc_info=True)
            raise
    def generate_docuseries_script(self, items: List[ConsolidatedItem]) -> Dict[str, Any]:
        try:
            """Generate docuseries script from consolidated data"""
            self.logger.info("🎬 Generating docuseries script...")

            # Group items by type
            documents = [item for item in items if item.item_type == "document"]
            holocrons = [item for item in items if item.item_type == "holocron"]
            videos = [item for item in items if item.item_type == "youtube_video"]

            # Create episode structure
            episodes = []

            # Episode 1: Documents Journey
            if documents:
                episodes.append({
                    "episode_number": 1,
                    "title": "The Documentation Journey",
                    "description": "Exploring our comprehensive documentation and knowledge base",
                    "items_count": len(documents),
                    "topics": list(set([tag for doc in documents[:20] for tag in doc.tags]))[:10]
                })

            # Episode 2: Holocron Archive
            if holocrons:
                episodes.append({
                    "episode_number": 2,
                    "title": "The Holocron Archive",
                    "description": "Deep dive into our knowledge repositories and intelligence systems",
                    "items_count": len(holocrons),
                    "topics": list(set([tag for holocron in holocrons[:20] for tag in holocron.tags]))[:10]
                })

            # Episode 3: YouTube Intelligence
            if videos:
                episodes.append({
                    "episode_number": 3,
                    "title": "YouTube Intelligence & Docuseries",
                    "description": "How we extract intelligence from YouTube and create docuseries",
                    "items_count": len(videos),
                    "topics": ["youtube", "intelligence", "docuseries", "sme_mapping"]
                })

            docuseries_script = {
                "generated_at": datetime.now().isoformat(),
                "total_episodes": len(episodes),
                "total_items": len(items),
                "episodes": episodes,
                "summary": {
                    "documents": len(documents),
                    "holocrons": len(holocrons),
                    "youtube_videos": len(videos),
                    "sparks": len(self.sparks)
                }
            }

            # Save docuseries script
            docuseries_file = self.consolidated_dir / "docuseries" / f"docuseries_script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            docuseries_file.parent.mkdir(parents=True, exist_ok=True)

            with open(docuseries_file, 'w', encoding='utf-8') as f:
                json.dump(docuseries_script, f, indent=2, ensure_ascii=False)

            self.logger.info(f"🎬 Saved docuseries script: {docuseries_file.name}")

            return docuseries_script


        except Exception as e:
            self.logger.error(f"Error in generate_docuseries_script: {e}", exc_info=True)
            raise
def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="LUMINA Data Consolidator")
        parser.add_argument("--type", choices=["documents", "holocrons", "youtube_videos", "all"],
                           default="all", help="Type of data to consolidate")
        parser.add_argument("--workers", type=int, default=5, help="Number of parallel workers (default: 5)")
        parser.add_argument("--no-dynamic-workers", action="store_true", 
                           help="Disable @bal dynamic worker adjustment")
        parser.add_argument("--json", action="store_true", help="JSON output")

        args = parser.parse_args()

        # Map type string to enum
        type_map = {
            "documents": ConsolidationType.DOCUMENTS,
            "holocrons": ConsolidationType.HOLOCRONS,
            "youtube_videos": ConsolidationType.YOUTUBE_VIDEOS,
            "all": ConsolidationType.ALL
        }

        consolidator = LuminaDataConsolidator(
            max_workers=args.workers,
            use_dynamic_workers=not args.no_dynamic_workers
        )
        result = consolidator.consolidate_all(consolidation_type=type_map[args.type])

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n✅ Consolidation complete!")
            print(f"   Items: {len(result.get('items', []))}")
            print(f"   @Sparks: {len(result.get('sparks', []))}")
            print(f"   Throughput: {result.get('metrics', {}).get('throughput_items_per_second', 0):.2f} items/sec")
            if result.get('docuseries_script'):
                print(f"   Docuseries Episodes: {result['docuseries_script'].get('total_episodes', 0)}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()