#!/usr/bin/env python3
"""
JARVIS Optimized Startup Executor

Staggered parallel startup execution for fastest startup without severely taxing system resources.
Integrates with performance tracking for continuous optimization.

Tags: #OPTIMIZED_STARTUP #STAGGERED #PARALLEL #PERFORMANCE #RESOURCE_BALANCED @JARVIS @LUMINA
"""

import sys
import json
import time
import psutil
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("JARVISOptStartup")
except ImportError:
    try:
        from lumina_logger import get_logger
        logger = get_logger("JARVISOptStartup")
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("JARVISOptStartup")

# Import performance tracker
try:
    from jarvis_startup_performance_tracker import StartupPerformanceTracker, PhaseType
    PERF_TRACKER_AVAILABLE = True
except ImportError:
    try:
        from scripts.python.jarvis_startup_performance_tracker import StartupPerformanceTracker, PhaseType
        PERF_TRACKER_AVAILABLE = True
    except ImportError:
        PERF_TRACKER_AVAILABLE = False
        logger.warning("Performance tracker not available")


class OptimizedStartupExecutor:
    """Optimized staggered parallel startup executor"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "optimized_startup"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.config_file = project_root / "config" / "ai_post_startup_checklist.json"
        self.execution_log = self.data_dir / "execution_log.jsonl"

        # Performance tracker
        if PERF_TRACKER_AVAILABLE:
            try:
                self.perf_tracker = StartupPerformanceTracker(project_root)
                logger.info("✅ Performance tracker initialized")
            except Exception as e:
                logger.warning(f"Performance tracker initialization failed: {e}")
                self.perf_tracker = None
        else:
            self.perf_tracker = None

        # Resource monitoring
        self.max_cpu_percent = 75.0  # Start throttling at 75%
        self.max_memory_percent = 80.0  # Start throttling at 80%
        self.optimal_parallel_count = 4  # Start with 4 parallel items
        self.min_stagger_delay = 0.5  # Minimum delay between staggered starts (seconds)
        self.max_stagger_delay = 3.0  # Maximum delay if resources are constrained

        # Execution state
        self.execution_queue = Queue()
        self.active_items = {}
        self.completed_items = {}
        self.failed_items = {}

    def load_startup_checklist(self) -> Dict[str, Any]:
        """Load startup checklist configuration"""
        if not self.config_file.exists():
            logger.error(f"Startup checklist not found: {self.config_file}")
            return {}

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get("ai_post_startup_checklist", {})
        except Exception as e:
            logger.error(f"Error loading startup checklist: {e}")
            return {}

    def check_system_resources(self) -> Dict[str, Any]:
        """Check current system resource utilization"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()

            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_mb": memory.available / (1024 * 1024),
                "can_start_more": cpu_percent < self.max_cpu_percent and memory.percent < self.max_memory_percent,
                "throttle_level": self._calculate_throttle_level(cpu_percent, memory.percent)
            }
        except Exception as e:
            logger.warning(f"Error checking resources: {e}")
            return {
                "cpu_percent": 0,
                "memory_percent": 0,
                "can_start_more": True,
                "throttle_level": 0
            }

    def _calculate_throttle_level(self, cpu_percent: float, memory_percent: float) -> float:
        """Calculate throttle level (0.0 = no throttle, 1.0 = maximum throttle)"""
        cpu_throttle = max(0, (cpu_percent - self.max_cpu_percent) / (100 - self.max_cpu_percent))
        memory_throttle = max(0, (memory_percent - self.max_memory_percent) / (100 - self.max_memory_percent))
        return max(cpu_throttle, memory_throttle)

    def _calculate_stagger_delay(self, throttle_level: float) -> float:
        """Calculate delay before starting next item based on throttle level"""
        return self.min_stagger_delay + (throttle_level * (self.max_stagger_delay - self.min_stagger_delay))

    def _calculate_parallel_count(self, throttle_level: float) -> int:
        """Calculate optimal parallel execution count based on throttle level"""
        if throttle_level > 0.5:
            return 1  # Severe throttling - run sequentially
        elif throttle_level > 0.3:
            return 2  # Moderate throttling - run 2 in parallel
        elif throttle_level > 0.1:
            return 3  # Light throttling - run 3 in parallel
        else:
            return self.optimal_parallel_count  # No throttling - optimal parallel count

    def execute_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single startup item"""
        item_id = item.get("id", "unknown")
        item_name = item.get("name", "Unknown")
        script_path = self.project_root / item.get("script", "")
        args = item.get("args", [])

        # Start performance tracking
        if self.perf_tracker:
            self.perf_tracker.start_item(item_id, item_name)

        result = {
            "item_id": item_id,
            "item_name": item_name,
            "start_time": time.time(),
            "end_time": None,
            "duration_seconds": None,
            "success": False,
            "error": None,
            "exit_code": None
        }

        try:
            if not script_path.exists():
                raise FileNotFoundError(f"Script not found: {script_path}")

            # Execute script
            cmd = ["python", str(script_path)] + args
            process = subprocess.Popen(
                cmd,
                cwd=str(self.project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait for completion with timeout
            timeout = item.get("estimated_duration_seconds", 300) * 2  # 2x estimated duration
            stdout, stderr = process.communicate(timeout=timeout)

            result["end_time"] = time.time()
            result["duration_seconds"] = result["end_time"] - result["start_time"]
            result["exit_code"] = process.returncode
            result["success"] = process.returncode == 0
            result["error"] = stderr if not result["success"] else None

        except subprocess.TimeoutExpired:
            result["end_time"] = time.time()
            result["duration_seconds"] = result["end_time"] - result["start_time"]
            result["success"] = False
            result["error"] = f"Timeout after {timeout} seconds"
            process.kill()

        except Exception as e:
            result["end_time"] = time.time()
            result["duration_seconds"] = result["end_time"] - result["start_time"] if result["start_time"] else 0
            result["success"] = False
            result["error"] = str(e)

        finally:
            # End performance tracking
            if self.perf_tracker:
                self.perf_tracker.end_item(item_id, result["success"], result["error"])

        return result

    def execute_optimized_startup(self) -> Dict[str, Any]:
        """Execute optimized staggered parallel startup"""
        # Start performance tracking
        if self.perf_tracker:
            phase_id = self.perf_tracker.start_phase(PhaseType.STARTUP)
            logger.info(f"Performance tracking started: {phase_id}")

        checklist = self.load_startup_checklist()
        if not checklist:
            return {"error": "Failed to load startup checklist"}

        execution_order = checklist.get("execution_order", [])
        checklist_items = {item["id"]: item for item in checklist.get("checklist_items", [])}

        execution = {
            "execution_id": f"opt_startup_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "started_at": datetime.now().isoformat(),
            "total_items": len(execution_order),
            "items": [],
            "parallel_groups": [],
            "total_duration_seconds": None,
            "status": "IN_PROGRESS"
        }

        logger.info("=" * 80)
        logger.info("🚀 OPTIMIZED STAGGERED PARALLEL STARTUP")
        logger.info("=" * 80)
        logger.info(f"Total Items: {len(execution_order)}")
        logger.info(f"Optimal Parallel Count: {self.optimal_parallel_count}")
        logger.info("=" * 80)

        start_time = time.time()
        completed_count = 0
        failed_count = 0

        # Execute items with staggered parallel execution
        with ThreadPoolExecutor(max_workers=self.optimal_parallel_count) as executor:
            futures = {}
            pending_items = list(execution_order)

            while pending_items or futures:
                # Check system resources
                resources = self.check_system_resources()
                throttle_level = resources["throttle_level"]
                parallel_count = self._calculate_parallel_count(throttle_level)

                # Start new items if we have capacity
                while len(futures) < parallel_count and pending_items:
                    item_id = pending_items.pop(0)
                    if item_id not in checklist_items:
                        logger.warning(f"Item not found in checklist: {item_id}")
                        continue

                    item = checklist_items[item_id]
                    if not item.get("enabled", True):
                        logger.info(f"⏭️  Skipping disabled item: {item_id}")
                        continue

                    # Submit for execution
                    future = executor.submit(self.execute_item, item)
                    futures[future] = item_id

                    logger.info(f"▶️  Starting: {item.get('name', item_id)}")

                    # Stagger delay based on throttle level
                    if pending_items:
                        delay = self._calculate_stagger_delay(throttle_level)
                        time.sleep(delay)

                # Check for completed items
                for future in as_completed(futures, timeout=1.0):
                    item_id = futures.pop(future)
                    try:
                        result = future.result()
                        execution["items"].append(result)

                        if result["success"]:
                            completed_count += 1
                            logger.info(f"✅ Completed: {result['item_name']} ({result['duration_seconds']:.2f}s)")
                        else:
                            failed_count += 1
                            logger.warning(f"❌ Failed: {result['item_name']} - {result.get('error', 'Unknown error')}")

                    except Exception as e:
                        failed_count += 1
                        logger.error(f"❌ Exception executing {item_id}: {e}")
                        execution["items"].append({
                            "item_id": item_id,
                            "success": False,
                            "error": str(e)
                        })

        end_time = time.time()
        execution["total_duration_seconds"] = end_time - start_time
        execution["completed_count"] = completed_count
        execution["failed_count"] = failed_count
        execution["status"] = "COMPLETED"

        # Stop performance tracking
        if self.perf_tracker:
            report = self.perf_tracker.stop_phase()
            execution["performance_report"] = report

        # Log execution
        with open(self.execution_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(execution) + '\n')

        logger.info("=" * 80)
        logger.info("🚀 OPTIMIZED STARTUP COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Total Duration: {execution['total_duration_seconds']:.2f} seconds")
        logger.info(f"Completed: {completed_count}")
        logger.info(f"Failed: {failed_count}")
        logger.info("=" * 80)

        return execution


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Optimized Startup Executor")
        parser.add_argument("--execute", action="store_true", help="Execute optimized startup")
        parser.add_argument("--status", action="store_true", help="Show system resource status")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        executor = OptimizedStartupExecutor(project_root)

        if args.execute:
            result = executor.execute_optimized_startup()
            print("=" * 80)
            print("OPTIMIZED STARTUP RESULT")
            print("=" * 80)
            print(json.dumps(result, indent=2, default=str))

        elif args.status:
            resources = executor.check_system_resources()
            print("=" * 80)
            print("SYSTEM RESOURCE STATUS")
            print("=" * 80)
            print(f"CPU: {resources['cpu_percent']:.1f}%")
            print(f"Memory: {resources['memory_percent']:.1f}%")
            print(f"Memory Available: {resources['memory_available_mb']:.1f} MB")
            print(f"Can Start More: {resources['can_start_more']}")
            print(f"Throttle Level: {resources['throttle_level']:.2f}")
            print("=" * 80)

        else:
            print("JARVIS Optimized Startup Executor")
            print("Use --help for usage information")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()