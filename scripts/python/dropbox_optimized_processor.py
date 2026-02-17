#!/usr/bin/env python3
"""
Dropbox Optimized Processor
<COMPANY_NAME> LLC

Resource-aware, utilization-balanced parallel batch processing for Dropbox:
- Caching system integration
- Parallel batch processing with utilization balance
- Energy-efficient processing
- Conservative, timely processing

@JARVIS @MARVIN @SYPHON
"""

import sys
import os
import time
import psutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Iterator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from universal_logging_wrapper import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

# Import workflow_base for parallel processing
try:
    from workflow_base import WorkflowBase, PARALLEL_AVAILABLE
    if PARALLEL_AVAILABLE:
        from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
except ImportError:
    PARALLEL_AVAILABLE = False
    ThreadPoolExecutor = None

# Import caching systems
try:
    from cluster_aware_cache import ClusterAwareCache
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    ClusterAwareCache = None

try:
    from cluster_aware_cache import HostAwareCache
    HOST_CACHE_AVAILABLE = True
except ImportError:
    HOST_CACHE_AVAILABLE = False
    HostAwareCache = None

logger = get_logger("DropboxOptimizedProcessor")


class UtilizationLevel(Enum):
    """System utilization levels"""
    IDLE = "idle"  # < 20%
    LOW = "low"  # 20-40%
    MEDIUM = "medium"  # 40-60%
    HIGH = "high"  # 60-80%
    CRITICAL = "critical"  # > 80%


@dataclass
class UtilizationMetrics:
    """System utilization metrics"""
    cpu_percent: float
    memory_percent: float
    disk_io_percent: float
    network_io_percent: float
    level: UtilizationLevel
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ProcessingConfig:
    """Processing configuration"""
    batch_size: int = 100
    max_workers: int = 4
    utilization_threshold: float = 0.7  # 70% max utilization
    energy_save_mode: bool = True
    cache_enabled: bool = True
    parallel_enabled: bool = True
    adaptive_batching: bool = True


class DropboxOptimizedProcessor:
    """Resource-aware, utilization-balanced Dropbox processor"""

    def __init__(self, dropbox_path: Path, config: Optional[ProcessingConfig] = None):
        """Initialize processor"""

        self.dropbox_path = Path(dropbox_path)
        self.config = config or ProcessingConfig()
        self.logger = logger

        # Initialize workflow base for parallel processing (but don't inherit)
        self.workflow_base = None
        try:
            self.workflow_base = WorkflowBase("DropboxOptimizedProcessor", total_steps=5)
        except Exception as e:
            self.logger.debug(f"WorkflowBase not available: {e}")

        # Initialize cache if available (prefer host-aware cache for Dropbox)
        self.cache = None
        if HOST_CACHE_AVAILABLE and HostAwareCache:
            try:
                cache_root = self.dropbox_path.parent / ".dropbox_cache"
                self.cache = HostAwareCache(
                    cache_root=cache_root,
                    ide_name="cursor",
                    default_expiry_hours=24,
                    max_cache_size_mb=5000  # 5GB cache for Dropbox
                )
                self.logger.info("✅ Host-aware cache initialized for Dropbox")
            except Exception as e:
                self.logger.warning(f"Host cache not available: {e}")
                # Fallback to cluster cache
                if CACHE_AVAILABLE and ClusterAwareCache:
                    try:
                        self.cache = ClusterAwareCache()
                        self.logger.info("✅ Cluster-aware cache initialized (fallback)")
                    except Exception as e2:
                        self.logger.warning(f"Cluster cache also not available: {e2}")

        self.logger.info("✅ Dropbox Optimized Processor initialized")
        self.logger.info(f"   Dropbox path: {self.dropbox_path}")
        self.logger.info(f"   Cache enabled: {self.config.cache_enabled}")
        self.logger.info(f"   Parallel enabled: {self.config.parallel_enabled}")
        self.logger.info(f"   Energy save mode: {self.config.energy_save_mode}")

    def get_utilization_metrics(self) -> UtilizationMetrics:
        """Get current system utilization metrics"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent

        # Disk I/O (simplified)
        try:
            disk_io = psutil.disk_io_counters()
            disk_io_percent = 0.0  # Would need baseline for accurate calculation
        except Exception:
            disk_io_percent = 0.0

        # Network I/O (simplified)
        try:
            net_io = psutil.net_io_counters()
            network_io_percent = 0.0  # Would need baseline for accurate calculation
        except Exception:
            network_io_percent = 0.0

        # Determine utilization level
        avg_utilization = (cpu_percent + memory_percent) / 2

        if avg_utilization < 20:
            level = UtilizationLevel.IDLE
        elif avg_utilization < 40:
            level = UtilizationLevel.LOW
        elif avg_utilization < 60:
            level = UtilizationLevel.MEDIUM
        elif avg_utilization < 80:
            level = UtilizationLevel.HIGH
        else:
            level = UtilizationLevel.CRITICAL

        return UtilizationMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_io_percent=disk_io_percent,
            network_io_percent=network_io_percent,
            level=level
        )

    def calculate_optimal_workers(self, utilization: UtilizationMetrics, total_items: int) -> int:
        """Calculate optimal number of workers based on utilization"""
        if not self.config.adaptive_batching:
            return self.config.max_workers

        # Base workers on utilization level
        base_workers = {
            UtilizationLevel.IDLE: 8,
            UtilizationLevel.LOW: 6,
            UtilizationLevel.MEDIUM: 4,
            UtilizationLevel.HIGH: 2,
            UtilizationLevel.CRITICAL: 1
        }

        max_workers = base_workers.get(utilization.level, 2)

        # Energy save mode: reduce workers
        if self.config.energy_save_mode:
            max_workers = max(1, max_workers // 2)

        # Don't exceed configured max
        max_workers = min(max_workers, self.config.max_workers)

        # Don't exceed available CPUs
        cpu_count = os.cpu_count() or 4
        max_workers = min(max_workers, max(1, cpu_count - 1))

        # Don't exceed total items
        max_workers = min(max_workers, total_items)

        return max_workers

    def calculate_optimal_batch_size(self, utilization: UtilizationMetrics) -> int:
        """Calculate optimal batch size based on utilization"""
        if not self.config.adaptive_batching:
            return self.config.batch_size

        # Base batch size on utilization level
        base_batch_size = {
            UtilizationLevel.IDLE: 200,
            UtilizationLevel.LOW: 150,
            UtilizationLevel.MEDIUM: 100,
            UtilizationLevel.HIGH: 50,
            UtilizationLevel.CRITICAL: 25
        }

        batch_size = base_batch_size.get(utilization.level, 100)

        # Energy save mode: smaller batches
        if self.config.energy_save_mode:
            batch_size = max(10, batch_size // 2)

        return batch_size

    def should_pause_processing(self, utilization: UtilizationMetrics) -> bool:
        """Determine if processing should pause due to high utilization"""
        if utilization.level == UtilizationLevel.CRITICAL:
            return True

        if utilization.level == UtilizationLevel.HIGH and utilization.cpu_percent > 85:
            return True

        if utilization.memory_percent > 90:
            return True

        return False

    def process_file_with_cache(self, file_path: Path) -> Dict[str, Any]:
        """Process a single file with caching"""
        result = {
            "file_path": str(file_path),
            "cached": False,
            "processed": False,
            "error": None
        }

        # Check cache first
        if self.config.cache_enabled and self.cache:
            try:
                cache_key = f"dropbox_file:{file_path}"
                cached_data = self.cache.get(cache_key)
                if cached_data:
                    result["cached"] = True
                    result["data"] = cached_data
                    return result
            except Exception as e:
                self.logger.debug(f"Cache check failed: {e}")

        # Process file (simplified - just get metadata)
        try:
            stat = file_path.stat()
            file_data = {
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "exists": True
            }

            # Store in cache
            if self.config.cache_enabled and self.cache:
                try:
                    # HostAwareCache.set() expects key_parts (List[str]) and expiry_hours (not ttl)
                    cache_key_parts = ["dropbox_file", str(file_path)]
                    # Convert 1 hour TTL to expiry_hours
                    self.cache.set(cache_key_parts, file_data, namespace="dropbox", expiry_hours=1)
                except Exception as e:
                    self.logger.debug(f"Cache store failed: {e}")

            result["processed"] = True
            result["data"] = file_data
        except Exception as e:
            result["error"] = str(e)

        return result

    def get_dropbox_files(self, max_files: Optional[int] = None) -> List[Path]:
        """Get list of Dropbox files to process"""
        files = []

        try:
            for file_path in self.dropbox_path.rglob("*"):
                if file_path.is_file():
                    files.append(file_path)
                    if max_files and len(files) >= max_files:
                        break
        except Exception as e:
            self.logger.error(f"Error scanning Dropbox: {e}")

        return files

    def process_dropbox_optimized(self, max_files: Optional[int] = None) -> Iterator[Dict[str, Any]]:
        """
        Process Dropbox files with resource-aware, utilization-balanced parallel batch processing

        Features:
        - Caching to avoid re-processing
        - Parallel batch processing
        - Utilization balance (adapts to system load)
        - Energy-efficient (conservative processing)
        - Timely (processes efficiently without overwhelming system)
        """
        self.logger.info("🔄 Starting optimized Dropbox processing...")

        # Get files to process
        files = self.get_dropbox_files(max_files)
        total_files = len(files)

        if total_files == 0:
            self.logger.warning("No files found to process")
            return

        self.logger.info(f"📁 Found {total_files} files to process")

        # Get initial utilization
        utilization = self.get_utilization_metrics()
        self.logger.info(f"📊 System utilization: {utilization.level.value} (CPU: {utilization.cpu_percent:.1f}%, Memory: {utilization.memory_percent:.1f}%)")

        # Calculate optimal batch size and workers
        batch_size = self.calculate_optimal_batch_size(utilization)
        max_workers = self.calculate_optimal_workers(utilization, total_files)

        self.logger.info(f"⚙️  Configuration: batch_size={batch_size}, max_workers={max_workers}")

        # Process in batches
        processed = 0
        cached = 0
        errors = 0

        for batch_num, i in enumerate(range(0, total_files, batch_size), 1):
            batch = files[i:i + batch_size]
            total_batches = (total_files + batch_size - 1) // batch_size

            self.logger.info(f"📦 Processing batch {batch_num}/{total_batches} ({len(batch)} files)")

            # Check utilization before processing batch
            utilization = self.get_utilization_metrics()

            if self.should_pause_processing(utilization):
                self.logger.warning(f"⏸️  Pausing processing - high utilization: {utilization.level.value}")
                time.sleep(2)  # Wait for system to recover
                utilization = self.get_utilization_metrics()

            # Recalculate workers based on current utilization
            current_workers = self.calculate_optimal_workers(utilization, len(batch))

            # Process batch in parallel
            if self.config.parallel_enabled and PARALLEL_AVAILABLE and current_workers > 1:
                # Use parallel processing
                tasks = [lambda f=file: self.process_file_with_cache(f) for file in batch]

                with ThreadPoolExecutor(max_workers=current_workers) as executor:
                    futures = {executor.submit(task): file for task, file in zip(tasks, batch)}

                    for future in as_completed(futures):
                        try:
                            result = future.result()
                            yield result

                            if result.get("cached"):
                                cached += 1
                            elif result.get("processed"):
                                processed += 1
                            elif result.get("error"):
                                errors += 1
                        except Exception as e:
                            self.logger.error(f"Batch processing error: {e}")
                            errors += 1
            else:
                # Sequential processing
                for file in batch:
                    result = self.process_file_with_cache(file)
                    yield result

                    if result.get("cached"):
                        cached += 1
                    elif result.get("processed"):
                        processed += 1
                    elif result.get("error"):
                        errors += 1

            # Progress update
            completed = processed + cached + errors
            progress = (completed / total_files) * 100
            self.logger.info(f"   Progress: {completed}/{total_files} ({progress:.1f}%) - Cached: {cached}, Processed: {processed}, Errors: {errors}")

            # Small delay between batches for energy efficiency
            if self.config.energy_save_mode:
                time.sleep(0.1)

        # Final summary
        self.logger.info("=" * 60)
        self.logger.info("✅ Dropbox processing complete")
        self.logger.info(f"   Total files: {total_files}")
        self.logger.info(f"   Cached (skipped): {cached}")
        self.logger.info(f"   Processed: {processed}")
        self.logger.info(f"   Errors: {errors}")
        self.logger.info("=" * 60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Dropbox Optimized Processor")
    parser.add_argument("--path", type=str, default="C:\\Users\\mlesn\\Dropbox", help="Dropbox path")
    parser.add_argument("--max-files", type=int, help="Maximum files to process")
    parser.add_argument("--batch-size", type=int, default=100, help="Batch size")
    parser.add_argument("--max-workers", type=int, default=4, help="Max parallel workers")
    parser.add_argument("--no-cache", action="store_true", help="Disable caching")
    parser.add_argument("--no-parallel", action="store_true", help="Disable parallel processing")
    parser.add_argument("--no-energy-save", action="store_true", help="Disable energy save mode")

    args = parser.parse_args()

    config = ProcessingConfig(
        batch_size=args.batch_size,
        max_workers=args.max_workers,
        cache_enabled=not args.no_cache,
        parallel_enabled=not args.no_parallel,
        energy_save_mode=not args.no_energy_save
    )

    processor = DropboxOptimizedProcessor(Path(args.path), config)

    # Process files
    for result in processor.process_dropbox_optimized(max_files=args.max_files):
        if result.get("error"):
            print(f"Error: {result['file_path']} - {result['error']}")

