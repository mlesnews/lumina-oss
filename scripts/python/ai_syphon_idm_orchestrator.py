#!/usr/bin/env python3
"""
AI-Powered SYPHON + IDM Orchestrator

Intelligent system that coordinates SYPHON (intelligence extraction) and
Internet Download Manager (IDM) for comprehensive content processing.

Features:
- AI-driven workflow routing
- Real-time progress monitoring
- Multi-stage processing pipeline
- Debug workflow visibility
- Live status updates
- Intelligent resource management

@AI @SYPHON @IDM @ORCHESTRATOR @REALTIME @DEBUG
"""

import sys
import json
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from queue import Queue
import logging

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from idm_cli_web_crawler import IDMCLIWebCrawler
except ImportError:
    IDMCLIWebCrawler = None

try:
    from syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier
    from syphon.models import DataSourceType
except ImportError:
    SYPHONSystem = None
    SYPHONConfig = None
    SubscriptionTier = None
    DataSourceType = None


class WorkflowStage(Enum):
    """Workflow processing stages"""
    DISCOVERY = "discovery"
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    DOWNLOADED = "downloaded"
    EXTRACTING = "extracting"
    EXTRACTED = "extracted"
    PROCESSING = "processing"
    PROCESSED = "processed"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowItem:
    """Represents an item in the workflow"""
    item_id: str
    url: str
    source_type: str
    stage: WorkflowStage
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str
    download_path: Optional[str] = None
    syphon_data_id: Optional[str] = None
    error: Optional[str] = None
    progress: float = 0.0
    stage_history: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.stage_history is None:
            self.stage_history = []

    def to_dict(self):
        return {
            **asdict(self),
            'stage': self.stage.value
        }


class AIOrchestrator:
    """
    AI-Powered Orchestrator for SYPHON + IDM Integration

    Intelligently routes content through download and extraction stages
    with real-time monitoring and debug capabilities.
    """

    def __init__(self, project_root: Optional[Path] = None, enable_ai_routing: bool = True):
        """
        Initialize AI Orchestrator

        Args:
            project_root: Project root directory
            enable_ai_routing: Enable AI-driven workflow routing decisions
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.enable_ai_routing = enable_ai_routing
        self.logger = get_logger("AIOrchestrator")

        # Initialize components
        self.idm_crawler = IDMCLIWebCrawler(self.project_root) if IDMCLIWebCrawler else None
        self.syphon = None

        if SYPHONSystem:
            try:
                config = SYPHONConfig(
                    project_root=self.project_root,
                    subscription_tier=SubscriptionTier.ENTERPRISE
                )
                self.syphon = SYPHONSystem(config)
                self.logger.info("✅ SYPHON initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  SYPHON initialization failed: {e}")

        # Workflow tracking
        self.workflow_items: Dict[str, WorkflowItem] = {}
        self.stage_queues: Dict[WorkflowStage, Queue] = {
            stage: Queue() for stage in WorkflowStage
        }

        # Real-time monitoring
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.status_callbacks: List[Callable] = []

        # Statistics
        self.stats = {
            "total_items": 0,
            "by_stage": {stage.value: 0 for stage in WorkflowStage},
            "completed": 0,
            "failed": 0,
            "started_at": datetime.now().isoformat()
        }

        # Progress tracking for transparency
        self.progress_metrics = {
            "current_item_index": 0,
            "total_items": 0,
            "items_per_second": 0.0,
            "items_per_minute": 0.0,
            "elapsed_time": 0.0,
            "estimated_time_remaining": 0.0,
            "completion_percentage": 0.0,
            "last_update": datetime.now().isoformat()
        }

        # Timing for speed calculation
        self.processing_times: List[float] = []  # Track processing times
        self.processing_start_time = None

        # Output directories
        self.output_dir = self.project_root / "data" / "ai_orchestrator"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.debug_dir = self.output_dir / "debug"
        self.debug_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("=" * 80)
        self.logger.info("🤖 AI SYPHON + IDM Orchestrator Initialized")
        self.logger.info("=" * 80)
        self.logger.info(f"   IDM Available: {self.idm_crawler.idm_available if self.idm_crawler else False}")
        self.logger.info(f"   SYPHON Available: {self.syphon is not None}")
        self.logger.info(f"   AI Routing: {enable_ai_routing}")
        self.logger.info(f"   Output: {self.output_dir}")
        self.logger.info("=" * 80)

    def add_status_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add callback for real-time status updates"""
        self.status_callbacks.append(callback)

    def _notify_status(self, status: Dict[str, Any]):
        """Notify all status callbacks"""
        for callback in self.status_callbacks:
            try:
                callback(status)
            except Exception as e:
                self.logger.warning(f"Status callback error: {e}")

    def _update_item_stage(self, item_id: str, new_stage: WorkflowStage,
                          metadata: Optional[Dict[str, Any]] = None,
                          error: Optional[str] = None):
        """Update item stage and notify"""
        if item_id not in self.workflow_items:
            return

        item = self.workflow_items[item_id]
        old_stage = item.stage

        # Update stage
        item.stage = new_stage
        item.updated_at = datetime.now().isoformat()

        if metadata:
            item.metadata.update(metadata)

        if error:
            item.error = error

        # Record stage transition
        item.stage_history.append({
            "from_stage": old_stage.value,
            "to_stage": new_stage.value,
            "timestamp": item.updated_at,
            "metadata": metadata or {}
        })

        # Update statistics
        self.stats["by_stage"][old_stage.value] = max(0, self.stats["by_stage"][old_stage.value] - 1)
        self.stats["by_stage"][new_stage.value] = self.stats["by_stage"].get(new_stage.value, 0) + 1

        if new_stage == WorkflowStage.COMPLETED:
            self.stats["completed"] += 1
            # Track processing time for speed calculation
            if item.created_at:
                try:
                    created = datetime.fromisoformat(item.created_at)
                    completed = datetime.now()
                    duration = (completed - created).total_seconds()
                    self.processing_times.append(duration)
                    # Keep only last 100 times for rolling average
                    if len(self.processing_times) > 100:
                        self.processing_times.pop(0)
                except:
                    pass
        elif new_stage == WorkflowStage.FAILED:
            self.stats["failed"] += 1

        # Update progress metrics
        self._update_progress_metrics()

        # Notify status
        self._notify_status({
            "type": "stage_update",
            "item_id": item_id,
            "old_stage": old_stage.value,
            "new_stage": new_stage.value,
            "item": item.to_dict(),
            "stats": self.stats.copy(),
            "progress": self.progress_metrics.copy()
        })

        # Debug logging
        self._debug_log(f"Stage transition: {item_id} {old_stage.value} → {new_stage.value}")

    def _update_progress_metrics(self):
        """Update progress metrics based on current stats and timing"""
        total_items = self.stats["total_items"]
        completed_items = self.stats["completed"]

        self.progress_metrics["total_items"] = total_items
        self.progress_metrics["current_item_index"] = completed_items

        if total_items > 0:
            self.progress_metrics["completion_percentage"] = (completed_items / total_items) * 100.0
        else:
            self.progress_metrics["completion_percentage"] = 0.0

        # Calculate processing speed
        if self.processing_start_time is not None and len(self.processing_times) > 0:
            elapsed_time = time.time() - self.processing_start_time
            self.progress_metrics["elapsed_time"] = elapsed_time

            if elapsed_time > 0:
                avg_time_per_item = sum(self.processing_times) / len(self.processing_times)
                self.progress_metrics["items_per_second"] = 1.0 / avg_time_per_item if avg_time_per_item > 0 else 0.0
                self.progress_metrics["items_per_minute"] = self.progress_metrics["items_per_second"] * 60.0

                # Estimate time remaining
                remaining_items = total_items - completed_items
                if self.progress_metrics["items_per_second"] > 0:
                    self.progress_metrics["estimated_time_remaining"] = remaining_items / self.progress_metrics["items_per_second"]
                else:
                    self.progress_metrics["estimated_time_remaining"] = 0.0
            else:
                self.progress_metrics["items_per_second"] = 0.0
                self.progress_metrics["items_per_minute"] = 0.0
                self.progress_metrics["estimated_time_remaining"] = 0.0
        else:
            self.progress_metrics["elapsed_time"] = 0.0
            self.progress_metrics["items_per_second"] = 0.0
            self.progress_metrics["items_per_minute"] = 0.0
            self.progress_metrics["estimated_time_remaining"] = 0.0

        self.progress_metrics["last_update"] = datetime.now().isoformat()

    def _debug_log(self, message: str, data: Optional[Dict] = None):
        try:
            """Log debug information"""
            debug_file = self.debug_dir / f"workflow_{datetime.now().strftime('%Y%m%d')}.log"
            with open(debug_file, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().isoformat()
                log_entry = {
                    "timestamp": timestamp,
                    "message": message,
                    "data": data or {}
                }
                f.write(json.dumps(log_entry) + "\n")

        except Exception as e:
            self.logger.error(f"Error in _debug_log: {e}", exc_info=True)
            raise
    def _ai_route_decision(self, item: WorkflowItem) -> Dict[str, Any]:
        """
        AI-driven routing decision for workflow item

        Determines:
        - Whether to download first or extract directly
        - Priority level
        - Resource allocation
        - Processing strategy
        """
        if not self.enable_ai_routing:
            return {
                "download_first": True,
                "priority": "normal",
                "strategy": "standard"
            }

        # AI decision logic based on content type and metadata
        url = item.url.lower()
        source_type = item.source_type.lower()

        # Decision rules
        decision = {
            "download_first": True,
            "priority": "normal",
            "strategy": "standard",
            "reasoning": []
        }

        # YouTube videos: download first for better processing
        if "youtube.com" in url or "youtu.be" in url:
            decision["download_first"] = True
            decision["priority"] = "high"
            decision["strategy"] = "video_extraction"
            decision["reasoning"].append("YouTube content benefits from download for transcript extraction")

        # Large files: download first
        if item.metadata.get("size_bytes", 0) > 100 * 1024 * 1024:  # > 100MB
            decision["download_first"] = True
            decision["priority"] = "normal"
            decision["reasoning"].append("Large file size requires download first")

        # Web pages: can extract directly
        if source_type == "web" and "youtube.com" not in url:
            decision["download_first"] = False
            decision["strategy"] = "direct_extraction"
            decision["reasoning"].append("Web page can be extracted directly without download")

        # Social media: extract directly
        if source_type == "social":
            decision["download_first"] = False
            decision["strategy"] = "direct_extraction"
            decision["reasoning"].append("Social media content can be extracted via API")

        return decision

    def add_item(self, url: str, source_type: str = "web",
                metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add item to workflow

        Args:
            url: URL to process
            source_type: Type of source (web, social, video, etc.)
            metadata: Additional metadata

        Returns:
            Item ID
        """
        item_id = f"{source_type}_{hash(url)}_{int(time.time())}"

        item = WorkflowItem(
            item_id=item_id,
            url=url,
            source_type=source_type,
            stage=WorkflowStage.DISCOVERY,
            metadata=metadata or {},
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )

        self.workflow_items[item_id] = item
        self.stats["total_items"] += 1
        self.stats["by_stage"][WorkflowStage.DISCOVERY.value] += 1

        # Update progress metrics
        self.progress_metrics["total_items"] = self.stats["total_items"]
        if self.processing_start_time is None:
            self.processing_start_time = time.time()

        # Get AI routing decision
        routing = self._ai_route_decision(item)
        item.metadata["routing"] = routing

        # Queue for processing
        self.stage_queues[WorkflowStage.DISCOVERY].put(item_id)

        self.logger.info(f"➕ Added item: {item_id} ({url[:60]}...)")
        self._notify_status({
            "type": "item_added",
            "item_id": item_id,
            "item": item.to_dict(),
            "stats": self.stats.copy()
        })

        return item_id

    def _process_discovery(self, item_id: str):
        """Process discovery stage"""
        item = self.workflow_items[item_id]
        self._update_item_stage(item_id, WorkflowStage.QUEUED)

        routing = item.metadata.get("routing", {})

        if routing.get("download_first", True):
            # Queue for download
            self.stage_queues[WorkflowStage.DOWNLOADING].put(item_id)
        else:
            # Skip to extraction
            self.stage_queues[WorkflowStage.EXTRACTING].put(item_id)

    def _process_download(self, item_id: str):
        """Process download stage using IDM"""
        item = self.workflow_items[item_id]
        self._update_item_stage(item_id, WorkflowStage.DOWNLOADING)

        if not self.idm_crawler or not self.idm_crawler.idm_available:
            self.logger.warning(f"⚠️  IDM not available for {item_id}, skipping download")
            self._update_item_stage(item_id, WorkflowStage.EXTRACTING,
                                  error="IDM not available")
            return

        try:
            # Determine download path
            url = item.url
            output_dir = self.output_dir / "downloads" / item.source_type
            output_dir.mkdir(parents=True, exist_ok=True)

            # Queue download in IDM
            self.idm_crawler._queue_download(url, output_dir)

            # Monitor IDM download completion
            expected_filename = self.idm_crawler._get_filename_from_url(url)
            download_path = output_dir / expected_filename

            # Poll for download completion (max 5 minutes)
            max_wait_time = 300  # 5 minutes
            poll_interval = 2  # Check every 2 seconds
            elapsed_time = 0

            while elapsed_time < max_wait_time:
                if download_path.exists() and download_path.stat().st_size > 0:
                    # Download complete - verify file is not still being written
                    initial_size = download_path.stat().st_size
                    time.sleep(1)  # Wait 1 second
                    if download_path.stat().st_size == initial_size:
                        # File size stable - download complete
                        self.logger.info(f"✅ Download completed: {download_path}")
                        break
                time.sleep(poll_interval)
                elapsed_time += poll_interval
                if elapsed_time % 10 == 0:  # Log every 10 seconds
                    self.logger.debug(f"   Waiting for download: {expected_filename} ({elapsed_time}s)")

            if not download_path.exists() or download_path.stat().st_size == 0:
                raise RuntimeError(f"Download timeout or failed: {url}")

            item.download_path = str(download_path)

            self._update_item_stage(item_id, WorkflowStage.DOWNLOADED, {
                "download_path": str(download_path)
            })

            # Queue for extraction
            self.stage_queues[WorkflowStage.EXTRACTING].put(item_id)

        except Exception as e:
            self.logger.error(f"❌ Download failed for {item_id}: {e}")
            self._update_item_stage(item_id, WorkflowStage.FAILED, error=str(e))

    def _process_extraction(self, item_id: str):
        """Process extraction stage using SYPHON"""
        item = self.workflow_items[item_id]
        self._update_item_stage(item_id, WorkflowStage.EXTRACTING)

        if not self.syphon:
            self.logger.warning(f"⚠️  SYPHON not available for {item_id}")
            self._update_item_stage(item_id, WorkflowStage.FAILED,
                                  error="SYPHON not available")
            return

        try:
            # Determine data source type
            if item.source_type == "social":
                ds_type = DataSourceType.SOCIAL
            elif item.source_type == "web":
                ds_type = DataSourceType.WEB
            else:
                ds_type = DataSourceType.WEB

            # Extract content
            content = item.url
            if item.download_path and Path(item.download_path).exists():
                # Use downloaded file
                with open(item.download_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

            metadata = {
                **item.metadata,
                "source_url": item.url,
                "extracted_at": datetime.now().isoformat()
            }

            result = self.syphon.extract(ds_type, content, metadata)

            if result.success and result.data:
                item.syphon_data_id = result.data.data_id
                self._update_item_stage(item_id, WorkflowStage.EXTRACTED, {
                    "syphon_data_id": result.data.data_id,
                    "content_length": len(result.data.content)
                })

                # Queue for processing
                self.stage_queues[WorkflowStage.PROCESSING].put(item_id)
            else:
                error_msg = result.error if hasattr(result, 'error') else "Extraction failed"
                self._update_item_stage(item_id, WorkflowStage.FAILED, error=error_msg)

        except Exception as e:
            self.logger.error(f"❌ Extraction failed for {item_id}: {e}")
            self._update_item_stage(item_id, WorkflowStage.FAILED, error=str(e))

    def _process_processing(self, item_id: str):
        """Process final processing stage"""
        item = self.workflow_items[item_id]
        self._update_item_stage(item_id, WorkflowStage.PROCESSING)

        try:
            # Final processing tasks
            # Save complete item data
            output_file = self.output_dir / f"items" / f"{item_id}.json"
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(item.to_dict(), f, indent=2, ensure_ascii=False)

            self._update_item_stage(item_id, WorkflowStage.COMPLETED, {
                "output_file": str(output_file)
            })

        except Exception as e:
            self.logger.error(f"❌ Processing failed for {item_id}: {e}")
            self._update_item_stage(item_id, WorkflowStage.FAILED, error=str(e))

    def _worker_thread(self, stage: WorkflowStage, processor: Callable):
        """Worker thread for processing a stage"""
        while self.monitoring_active:
            try:
                item_id = self.stage_queues[stage].get(timeout=1)
                processor(item_id)
            except:
                continue

    def start_monitoring(self):
        """Start real-time monitoring and processing"""
        if self.monitoring_active:
            return

        self.monitoring_active = True

        # Start worker threads for each stage
        workers = {
            WorkflowStage.DISCOVERY: self._process_discovery,
            WorkflowStage.DOWNLOADING: self._process_download,
            WorkflowStage.EXTRACTING: self._process_extraction,
            WorkflowStage.PROCESSING: self._process_processing
        }

        for stage, processor in workers.items():
            thread = threading.Thread(
                target=self._worker_thread,
                args=(stage, processor),
                daemon=True
            )
            thread.start()

        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()

        self.logger.info("🚀 Monitoring started - workflow processing active")

    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        self.logger.info("⏹️  Monitoring stopped")

    def _monitoring_loop(self):
        """Real-time monitoring loop"""
        while self.monitoring_active:
            try:
                # Generate status report
                status = {
                    "type": "status_update",
                    "timestamp": datetime.now().isoformat(),
                    "stats": self.stats.copy(),
                    "active_items": [
                        item.to_dict() for item in self.workflow_items.values()
                        if item.stage not in [WorkflowStage.COMPLETED, WorkflowStage.FAILED, WorkflowStage.SKIPPED]
                    ],
                    "stage_counts": {
                        stage.value: self.stage_queues[stage].qsize()
                        for stage in WorkflowStage
                    },
                    "progress": self.progress_metrics.copy()
                }

                self._notify_status(status)

                # Save status snapshot
                status_file = self.debug_dir / f"status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(status_file, 'w', encoding='utf-8') as f:
                    json.dump(status, f, indent=2)

                time.sleep(5)  # Update every 5 seconds

            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(5)

    def get_status(self) -> Dict[str, Any]:
        """Get current workflow status"""
        return {
            "stats": self.stats.copy(),
            "items": [item.to_dict() for item in self.workflow_items.values()],
            "stage_queues": {
                stage.value: self.stage_queues[stage].qsize()
                for stage in WorkflowStage
            }
        }

    def print_status(self):
        """Print human-readable status"""
        print("\n" + "=" * 80)
        print("🤖 AI SYPHON + IDM Orchestrator Status")
        print("=" * 80)
        print(f"Total Items: {self.stats['total_items']}")
        print(f"Completed: {self.stats['completed']}")
        print(f"Failed: {self.stats['failed']}")
        print(f"\nStage Distribution:")
        for stage, count in self.stats['by_stage'].items():
            if count > 0:
                print(f"  {stage}: {count}")
        print("=" * 80)


def console_status_callback(status: Dict[str, Any]):
    """Console status callback for real-time updates"""
    if status.get("type") == "stage_update":
        item = status.get("item", {})
        print(f"🔄 {item.get('item_id', 'unknown')}: {status.get('old_stage')} → {status.get('new_stage')}")
    elif status.get("type") == "status_update":
        stats = status.get("stats", {})
        print(f"\r📊 Active: {len(status.get('active_items', []))} | "
              f"Completed: {stats.get('completed', 0)} | "
              f"Failed: {stats.get('failed', 0)}", end="")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="AI SYPHON + IDM Orchestrator")
    parser.add_argument("--urls", nargs="+", help="URLs to process")
    parser.add_argument("--file", type=Path, help="File with URLs (one per line)")
    parser.add_argument("--no-ai", action="store_true", help="Disable AI routing")
    parser.add_argument("--console", action="store_true", help="Enable console status updates")

    args = parser.parse_args()

    # Initialize orchestrator
    orchestrator = AIOrchestrator(enable_ai_routing=not args.no_ai)

    # Add console callback if requested
    if args.console:
        orchestrator.add_status_callback(console_status_callback)

    # Start monitoring
    orchestrator.start_monitoring()

    # Add items
    urls = []
    if args.urls:
        urls.extend(args.urls)
    if args.file and args.file.exists():
        with open(args.file, 'r', encoding='utf-8') as f:
            urls.extend([line.strip() for line in f if line.strip()])

    if not urls:
        print("No URLs provided. Use --urls or --file")
        return

    print(f"\n➕ Adding {len(urls)} items to workflow...")
    for url in urls:
        orchestrator.add_item(url)

    # Keep running
    try:
        while True:
            time.sleep(10)
            orchestrator.print_status()
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping orchestrator...")
        orchestrator.stop_monitoring()
        orchestrator.print_status()


if __name__ == "__main__":


    main()