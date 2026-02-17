#!/usr/bin/env python3
"""
Parallel Agent Session Batch Processor
@PEAK Optimized | @MAX Parallel Processing

Processes multiple agent sessions in parallel batches while maintaining system balance.
Implements intelligent load balancing, resource monitoring, and failure recovery.

Features:
- Parallel batch processing with configurable concurrency
- Resource monitoring and adaptive scaling
- Intelligent load balancing across CPU cores
- Memory pressure monitoring and throttling
- Failure recovery and retry mechanisms
- Progress tracking and status reporting
- System balance maintenance (CPU, memory, I/O)

Author: JARVIS Automation System
Date: 2025-01-27
"""

import sys
import json
import time
import psutil
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from dataclasses import dataclass, field
import threading
import queue
import os
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(project_root / "data" / "logs" / "parallel_agent_processor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class ProcessingStats:
    """Statistics for batch processing operations"""
    total_sessions: int = 0
    processed_sessions: int = 0
    failed_sessions: int = 0
    avg_processing_time: float = 0.0
    total_processing_time: float = 0.0
    peak_memory_usage: float = 0.0
    peak_cpu_usage: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

@dataclass
class ResourceLimits:
    """Resource limits for balanced processing"""
    max_concurrent_workers: int = 4
    max_memory_percent: float = 80.0
    max_cpu_percent: float = 75.0
    batch_size: int = 10
    throttle_delay: float = 0.1
    max_retries: int = 3
    retry_delay: float = 1.0

@dataclass(order=True)
class AgentSession:
    """Represents an agent session to be processed"""
    priority: int = field(default=1, compare=True)  # 1=low, 2=medium, 3=high (higher number = higher priority)
    session_id: str = field(default="", compare=False)
    file_path: Path = field(default=Path(), compare=False)
    session_type: str = field(default="", compare=False)
    metadata: Dict[str, Any] = field(default_factory=dict, compare=False)
    processing_attempts: int = field(default=0, compare=False)
    last_error: Optional[str] = field(default=None, compare=False)

class ParallelAgentSessionProcessor:
    """
    @PEAK Parallel Agent Session Processor

    Processes multiple agent sessions in parallel batches while maintaining
    system resource balance and providing intelligent load management.
    """

    def __init__(
        self,
        resource_limits: Optional[ResourceLimits] = None,
        session_processor: Optional[Callable] = None
    ):
        """
        Initialize the parallel processor.

        Args:
            resource_limits: Resource constraints for processing
            session_processor: Function to process individual sessions
        """
        self.resource_limits = resource_limits or ResourceLimits()
        self.session_processor = session_processor or self._default_session_processor
        self.stats = ProcessingStats()

        # Dynamic resource monitoring
        self.cpu_count = os.cpu_count() or 4
        self.memory_total = psutil.virtual_memory().total

        # Adaptive concurrency based on system resources
        self._adjust_concurrency_limits()

        # Processing queues and state
        self.session_queue = queue.PriorityQueue()
        self.results_queue = queue.Queue()
        self.active_workers = 0
        self.worker_lock = threading.Lock()

        # Progress tracking
        self.progress_callbacks: List[Callable] = []
        self.status_update_interval = 5.0  # seconds

        logger.info(f"Initialized parallel processor with {self.resource_limits.max_concurrent_workers} max workers")

    def _adjust_concurrency_limits(self) -> None:
        """Dynamically adjust concurrency based on system resources"""
        # Base on CPU cores
        cpu_based_workers = max(1, self.cpu_count // 2)

        # Adjust based on available memory (aim for ~1GB per worker)
        memory_based_workers = max(1, int(psutil.virtual_memory().available / (1024**3)))

        # Take the minimum of CPU and memory constraints
        recommended_workers = min(cpu_based_workers, memory_based_workers)

        # Don't exceed configured limits
        self.resource_limits.max_concurrent_workers = min(
            recommended_workers,
            self.resource_limits.max_concurrent_workers
        )

        logger.info(f"Adjusted concurrency: {self.resource_limits.max_concurrent_workers} workers "
                   f"(CPU: {cpu_based_workers}, Memory: {memory_based_workers})")

    def _monitor_system_resources(self) -> Tuple[float, float]:
        """Monitor current system resource usage"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_percent = psutil.virtual_memory().percent

        # Update peak stats
        self.stats.peak_cpu_usage = max(self.stats.peak_cpu_usage, cpu_percent)
        self.stats.peak_memory_usage = max(self.stats.peak_memory_usage, memory_percent)

        return cpu_percent, memory_percent

    def _should_throttle(self) -> bool:
        """Check if processing should be throttled due to resource constraints"""
        cpu_percent, memory_percent = self._monitor_system_resources()

        return (
            cpu_percent > self.resource_limits.max_cpu_percent or
            memory_percent > self.resource_limits.max_memory_percent
        )

    def _default_session_processor(self, session: AgentSession) -> Dict[str, Any]:
        """
        Default session processor - can be overridden by user

        This processes a single agent session and returns results.
        """
        try:
            # Simulate processing time based on session size
            file_size = session.file_path.stat().st_size if session.file_path.exists() else 0
            processing_time = min(max(file_size / 1000000, 0.1), 5.0)  # 0.1-5 seconds

            time.sleep(processing_time)

            # Mock processing result
            result = {
                "session_id": session.session_id,
                "status": "processed",
                "processing_time": processing_time,
                "file_size": file_size,
                "timestamp": datetime.now().isoformat(),
                "extracted_intelligence": {
                    "actionable_items": ["Sample action item"],
                    "decisions": ["Sample decision"],
                    "tasks": ["Sample task"]
                }
            }

            logger.debug(f"Processed session {session.session_id} in {processing_time:.2f}s")
            return result

        except Exception as e:
            logger.error(f"Error processing session {session.session_id}: {e}")
            raise

    def _process_session_batch(self, sessions: List[AgentSession]) -> List[Dict[str, Any]]:
        """Process a batch of sessions in parallel"""
        results = []

        with ThreadPoolExecutor(max_workers=self.resource_limits.max_concurrent_workers) as executor:
            # Submit all sessions in batch
            future_to_session = {
                executor.submit(self._process_single_session, session): session
                for session in sessions
            }

            # Collect results as they complete
            for future in as_completed(future_to_session):
                session = future_to_session[future]
                try:
                    result = future.result()
                    results.append(result)
                    self.stats.processed_sessions += 1

                except Exception as e:
                    logger.error(f"Failed to process session {session.session_id}: {e}")
                    self.stats.failed_sessions += 1

                    # Add retry logic for failed sessions
                    if session.processing_attempts < self.resource_limits.max_retries:
                        session.processing_attempts += 1
                        session.last_error = str(e)
                        logger.info(f"Retrying session {session.session_id} (attempt {session.processing_attempts})")
                        time.sleep(self.resource_limits.retry_delay)
                        # Re-queue for retry
                        self.session_queue.put((session.priority, session))

        return results

    def _process_single_session(self, session: AgentSession) -> Dict[str, Any]:
        """Process a single session with resource monitoring"""
        start_time = time.time()

        # Check resource limits before processing
        if self._should_throttle():
            logger.debug(f"Throttling due to resource constraints for session {session.session_id}")
            time.sleep(self.resource_limits.throttle_delay)

        try:
            result = self.session_processor(session)
            processing_time = time.time() - start_time

            # Update stats
            self.stats.total_processing_time += processing_time
            self.stats.avg_processing_time = (
                self.stats.total_processing_time / self.stats.processed_sessions
                if self.stats.processed_sessions > 0 else 0
            )

            return result

        except Exception as e:
            processing_time = time.time() - start_time
            raise Exception(f"Session processing failed after {processing_time:.2f}s: {e}")

    def add_session(self, session: AgentSession) -> None:
        """Add a session to the processing queue"""
        # PriorityQueue puts lowest priority first, so invert priority (higher number = higher priority)
        inverted_priority = -session.priority
        self.session_queue.put((inverted_priority, session))
        self.stats.total_sessions += 1

    def add_sessions_from_directory(
        self,
        directory: Path,
        file_pattern: str = "*.json",
        session_type: str = "agent_session"
    ) -> int:
        """
        Add all matching sessions from a directory

        Returns number of sessions added
        """
        added_count = 0

        if not directory.exists():
            logger.warning(f"Directory does not exist: {directory}")
            return 0

        for file_path in directory.rglob(file_pattern):
            if file_path.is_file():
                session_id = f"{session_type}_{file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

                # Determine priority based on file size and modification time
                file_size = file_path.stat().st_size
                modified_time = file_path.stat().st_mtime

                # Higher priority for larger, recently modified files
                priority = 1  # Base priority
                if file_size > 1000000:  # > 1MB
                    priority = 3  # High priority
                elif file_size > 100000:  # > 100KB
                    priority = 2  # Medium priority

                # Boost priority for recently modified files
                days_since_modified = (time.time() - modified_time) / (24 * 3600)
                if days_since_modified < 1:  # Modified today
                    priority = max(priority, 3)
                elif days_since_modified < 7:  # Modified this week
                    priority = max(priority, 2)

                session = AgentSession(
                    priority=priority,
                    session_id=session_id,
                    file_path=file_path,
                    session_type=session_type,
                    metadata={
                        "source_directory": str(directory),
                        "file_pattern": file_pattern,
                        "file_size": file_size,
                        "modified_time": datetime.fromtimestamp(modified_time).isoformat(),
                        "calculated_priority": priority
                    }
                )

                self.add_session(session)
                added_count += 1

        logger.info(f"Added {added_count} sessions from {directory}")
        return added_count

    def process_all_sessions(self) -> ProcessingStats:
        """
        Process all queued sessions in parallel batches while maintaining balance

        Returns final processing statistics
        """
        self.stats.start_time = datetime.now()

        logger.info(f"Starting parallel processing of {self.stats.total_sessions} sessions")
        logger.info(f"Using {self.resource_limits.max_concurrent_workers} concurrent workers")
        logger.info(f"Batch size: {self.resource_limits.batch_size}")

        batch_number = 1
        all_results = []

        while not self.session_queue.empty():
            # Collect batch of sessions
            batch_sessions = []
            for _ in range(self.resource_limits.batch_size):
                try:
                    inverted_priority, session = self.session_queue.get_nowait()
                    batch_sessions.append(session)
                except queue.Empty:
                    break

            if not batch_sessions:
                break

            logger.info(f"Processing batch {batch_number} with {len(batch_sessions)} sessions")

            # Process batch in parallel
            batch_results = self._process_session_batch(batch_sessions)
            all_results.extend(batch_results)

            # Progress callback
            for callback in self.progress_callbacks:
                try:
                    callback(self.stats, batch_results)
                except Exception as e:
                    logger.error(f"Progress callback error: {e}")

            # Throttle between batches if needed
            if self._should_throttle():
                logger.info("System under load, pausing between batches")
                time.sleep(self.resource_limits.throttle_delay * 2)

            batch_number += 1

        self.stats.end_time = datetime.now()

        # Save results
        self._save_processing_results(all_results)

        logger.info(f"Completed processing: {self.stats.processed_sessions}/{self.stats.total_sessions} successful")
        return self.stats

    def _save_processing_results(self, results: List[Dict[str, Any]]) -> None:
        try:
            """Save processing results to file"""
            results_dir = project_root / "data" / "parallel_processing"
            results_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = results_dir / f"parallel_processing_results_{timestamp}.json"

            output_data = {
                "processing_stats": {
                    "total_sessions": self.stats.total_sessions,
                    "processed_sessions": self.stats.processed_sessions,
                    "failed_sessions": self.stats.failed_sessions,
                    "avg_processing_time": self.stats.avg_processing_time,
                    "total_processing_time": self.stats.total_processing_time,
                    "peak_memory_usage": self.stats.peak_memory_usage,
                    "peak_cpu_usage": self.stats.peak_cpu_usage,
                    "start_time": self.stats.start_time.isoformat() if self.stats.start_time else None,
                    "end_time": self.stats.end_time.isoformat() if self.stats.end_time else None,
                    "duration_seconds": (
                        self.stats.end_time - self.stats.start_time
                    ).total_seconds() if self.stats.start_time and self.stats.end_time else None
                },
                "resource_limits": {
                    "max_concurrent_workers": self.resource_limits.max_concurrent_workers,
                    "max_memory_percent": self.resource_limits.max_memory_percent,
                    "max_cpu_percent": self.resource_limits.max_cpu_percent,
                    "batch_size": self.resource_limits.batch_size
                },
                "results": results
            }

            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved processing results to {results_file}")

        except Exception as e:
            self.logger.error(f"Error in _save_processing_results: {e}", exc_info=True)
            raise
    def add_progress_callback(self, callback: Callable) -> None:
        """Add a callback for progress updates"""
        self.progress_callbacks.append(callback)

def main():
    try:
        """CLI entry point for parallel processing"""
        import argparse

        parser = argparse.ArgumentParser(description="Parallel Agent Session Batch Processor")
        parser.add_argument("--input-dir", type=str, required=True, help="Directory containing sessions to process")
        parser.add_argument("--file-pattern", type=str, default="*.json", help="File pattern to match")
        parser.add_argument("--session-type", type=str, default="agent_session", help="Type of sessions being processed")
        parser.add_argument("--max-workers", type=int, default=None, help="Maximum concurrent workers")
        parser.add_argument("--batch-size", type=int, default=10, help="Batch size for processing")
        parser.add_argument("--max-memory", type=float, default=80.0, help="Max memory usage percentage")
        parser.add_argument("--max-cpu", type=float, default=75.0, help="Max CPU usage percentage")

        args = parser.parse_args()

        # Create resource limits
        limits = ResourceLimits(
            max_concurrent_workers=args.max_workers or 4,
            max_memory_percent=args.max_memory,
            max_cpu_percent=args.max_cpu,
            batch_size=args.batch_size
        )

        # Create processor
        processor = ParallelAgentSessionProcessor(resource_limits=limits)

        # Add progress callback
        def progress_callback(stats: ProcessingStats, batch_results: List[Dict[str, Any]]):
            print(f"Progress: {stats.processed_sessions}/{stats.total_sessions} sessions processed "
                  f"({stats.avg_processing_time:.2f}s avg)")

        processor.add_progress_callback(progress_callback)

        # Add sessions from directory
        input_dir = Path(args.input_dir)
        if not input_dir.exists():
            print(f"Error: Input directory does not exist: {input_dir}")
            return 1

        added_count = processor.add_sessions_from_directory(
            input_dir,
            args.file_pattern,
            args.session_type
        )

        if added_count == 0:
            print(f"No sessions found in {input_dir} matching pattern {args.file_pattern}")
            return 1

        print(f"Starting parallel processing of {added_count} sessions...")
        print(f"Configuration: {limits.max_concurrent_workers} workers, "
              f"batch size {limits.batch_size}")

        # Process all sessions
        stats = processor.process_all_sessions()

        # Print final summary
        duration = (
            stats.end_time - stats.start_time
        ).total_seconds() if stats.start_time and stats.end_time else 0

        print("\n=== PROCESSING COMPLETE ===")
        print(f"Total Sessions: {stats.total_sessions}")
        print(f"Successfully Processed: {stats.processed_sessions}")
        print(f"Failed: {stats.failed_sessions}")
        print(f"Average Processing Time: {stats.avg_processing_time:.2f}s")
        print(f"Peak Memory Usage: {stats.peak_memory_usage:.1f}%")
        print(f"Peak CPU Usage: {stats.peak_cpu_usage:.1f}%")
        print(f"Duration: {duration:.2f} seconds")

        return 0 if stats.failed_sessions == 0 else 1

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())