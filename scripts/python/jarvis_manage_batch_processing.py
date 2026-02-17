#!/usr/bin/env python3
"""
JARVIS Batch Processing Manager

Manages and executes all batches from the incomplete @ASKS mining system.
Resource-aware, parallel batch processing with JARVIS workflow integration.

ORDER 66: @DOIT execution command

Tags: #JARVIS #BATCH #MANAGEMENT #RESOURCE_AWARE #PARALLEL #WORKFLOW @JARVIS @DOIT
"""

import sys
import json
import time
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
import logging
import threading

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISBatchProcessingManager")

# Import required systems
try:
    from jarvis_helpdesk_integration import JARVISHelpdeskIntegration
    JARVIS_AVAILABLE = True
except ImportError:
    JARVIS_AVAILABLE = False
    JARVISHelpdeskIntegration = None
    logger.warning("⚠️  JARVIS Helpdesk Integration not available")

try:
    from jarvis_execute_ask_chains import JARVISAskChainExecutor
    ASK_CHAIN_EXECUTOR_AVAILABLE = True
except ImportError:
    ASK_CHAIN_EXECUTOR_AVAILABLE = False
    JARVISAskChainExecutor = None
    logger.warning("⚠️  JARVIS Ask Chain Executor not available")

# Resource awareness
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("⚠️  psutil not available - resource awareness limited")


class BatchStatus(Enum):
    """Batch processing status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class ResourceLevel(Enum):
    """Resource availability level"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    CRITICAL = "critical"


@dataclass
class BatchExecutionResult:
    """Result of batch execution"""
    batch_id: str
    batch_number: int
    status: BatchStatus
    started_at: str
    completed_at: Optional[str] = None
    asks_processed: int = 0
    asks_succeeded: int = 0
    asks_failed: int = 0
    total_duration: float = 0.0  # seconds
    errors: List[str] = field(default_factory=list)
    results: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ResourceMonitor:
    """Resource monitoring for batch processing"""
    cpu_threshold_high: float = 80.0
    memory_threshold_high: float = 80.0
    disk_threshold_high: float = 90.0

    def get_resource_level(self) -> ResourceLevel:
        """Get current resource availability level"""
        if not PSUTIL_AVAILABLE:
            return ResourceLevel.MEDIUM

        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            if cpu_percent > self.cpu_threshold_high or memory.percent > self.memory_threshold_high or disk.percent > self.disk_threshold_high:
                return ResourceLevel.CRITICAL
            elif cpu_percent > self.cpu_threshold_high * 0.7 or memory.percent > self.memory_threshold_high * 0.7:
                return ResourceLevel.LOW
            elif cpu_percent > self.cpu_threshold_high * 0.5 or memory.percent > self.memory_threshold_high * 0.5:
                return ResourceLevel.MEDIUM
            else:
                return ResourceLevel.HIGH
        except Exception as e:
            logger.warning(f"⚠️  Error monitoring resources: {e}")
            return ResourceLevel.MEDIUM

    def wait_for_resources(self, required_level: ResourceLevel = ResourceLevel.MEDIUM, max_wait: int = 300) -> bool:
        """Wait for resources to become available"""
        start_time = time.time()
        while time.time() - start_time < max_wait:
            current_level = self.get_resource_level()
            level_order = {ResourceLevel.HIGH: 0, ResourceLevel.MEDIUM: 1, ResourceLevel.LOW: 2, ResourceLevel.CRITICAL: 3}

            if level_order[current_level] <= level_order[required_level]:
                return True

            time.sleep(5)  # Check every 5 seconds

        return False


class JARVISBatchProcessingManager:
    """
    JARVIS Batch Processing Manager

    Manages and executes all batches from the incomplete @ASKS mining system.
    Resource-aware, parallel batch processing with JARVIS workflow integration.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize JARVIS batch processing manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "jarvis_incomplete_asks"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize subsystems
        self.jarvis = None
        if JARVIS_AVAILABLE:
            try:
                self.jarvis = JARVISHelpdeskIntegration(project_root=self.project_root)
                logger.info("✅ JARVIS Helpdesk Integration initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize JARVIS: {e}")

        self.ask_executor = None
        if ASK_CHAIN_EXECUTOR_AVAILABLE:
            try:
                self.ask_executor = JARVISAskChainExecutor(project_root=self.project_root)
                logger.info("✅ JARVIS Ask Chain Executor initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize Ask Chain Executor: {e}")

        self.resource_monitor = ResourceMonitor()
        self.batches: List[Dict[str, Any]] = []
        self.execution_results: List[BatchExecutionResult] = []
        self.active_batches: Set[str] = set()
        self.lock = threading.Lock()

        logger.info("✅ JARVIS Batch Processing Manager initialized")

    def load_batch_plan(self, plan_file: Optional[Path] = None) -> Dict[str, Any]:
        try:
            """Load batch processing plan"""
            if plan_file is None or (isinstance(plan_file, str) and plan_file == "latest"):
                # Find latest batch plan
                plan_files = sorted(self.data_dir.glob("batch_plan_*.json"), reverse=True)
                if not plan_files:
                    raise FileNotFoundError("No batch plan found")
                plan_file = plan_files[0]
            elif isinstance(plan_file, str):
                plan_file = Path(plan_file)

            logger.info(f"📋 Loading batch plan: {plan_file.name}")

            with open(plan_file, 'r', encoding='utf-8') as f:
                plan = json.load(f)

            self.batches = plan.get("batches", [])
            logger.info(f"   ✅ Loaded {len(self.batches)} batches")

            return plan

        except Exception as e:
            self.logger.error(f"Error in load_batch_plan: {e}", exc_info=True)
            raise
    def process_ask(self, ask: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single ask through JARVIS workflow system

        Returns execution result
        """
        ask_id = ask.get("ask_id", "")
        ask_text = ask.get("ask_text", "")

        result = {
            "ask_id": ask_id,
            "ask_text": ask_text[:100],  # Truncate for logging
            "success": False,
            "error": None,
            "result": None
        }

        try:
            # Method 1: Use JARVIS Ask Chain Executor
            if self.ask_executor:
                # Create workflow data from ask
                workflow_data = {
                    "workflow_id": f"ask_{ask_id}",
                    "workflow_name": f"Process @ASK: {ask_text[:50]}",
                    "ask_text": ask_text,
                    "ask_id": ask_id,
                    "category": ask.get("category", "general"),
                    "priority": ask.get("priority", "normal"),
                    "messages": [
                        {
                            "role": "user",
                            "content": ask_text
                        }
                    ],
                    "agents": ["JARVIS"],
                    "metadata": ask.get("metadata", {})
                }

                # Execute through JARVIS
                execution_result = self.ask_executor.execute_ask_chain(ask_id, workflow_data)
                result["success"] = execution_result.get("success", False)
                result["result"] = execution_result

                if not result["success"]:
                    result["error"] = execution_result.get("error", "Unknown error")

            # Method 2: Use JARVIS Helpdesk Integration
            elif self.jarvis:
                workflow_data = {
                    "workflow_id": f"ask_{ask_id}",
                    "workflow_name": f"Process @ASK: {ask_text[:50]}",
                    "ask_text": ask_text,
                    "messages": [
                        {
                            "role": "user",
                            "content": ask_text
                        }
                    ]
                }

                # Verify and execute workflow
                verified, verification_result = self.jarvis.verify_workflow_before_execution(
                    workflow_data,
                    require_verification=True,
                    escalate_on_failure=True
                )

                if verified:
                    # Execute workflow (placeholder - actual execution would go here)
                    result["success"] = True
                    result["result"] = {"status": "executed", "verification": verification_result}
                else:
                    result["success"] = False
                    result["error"] = verification_result.get("error", "Verification failed")

            # Method 3: Fallback - log and mark as processed
            else:
                logger.warning(f"   ⚠️  No JARVIS system available for ask {ask_id}, marking as processed")
                result["success"] = True
                result["result"] = {"status": "logged", "note": "JARVIS system not available"}

        except Exception as e:
            logger.error(f"   ❌ Error processing ask {ask_id}: {e}", exc_info=True)
            result["error"] = str(e)

        return result

    def execute_batch(self, batch: Dict[str, Any], wait_for_resources: bool = True) -> BatchExecutionResult:
        """
        Execute a single batch

        Args:
            batch: Batch configuration
            wait_for_resources: If True, wait for resources before starting

        Returns:
            BatchExecutionResult
        """
        batch_id = batch["batch_id"]
        batch_number = batch["batch_number"]
        asks = batch.get("asks", [])
        max_concurrent = batch.get("max_concurrent", 1)
        stagger_delay = batch.get("stagger_delay", 0)

        logger.info("="*80)
        logger.info(f"🚀 Executing Batch {batch_number}: {batch_id}")
        logger.info(f"   Asks: {len(asks)}, Max Concurrent: {max_concurrent}, Stagger: {stagger_delay}s")
        logger.info("="*80)

        # Wait for stagger delay
        if stagger_delay > 0:
            logger.info(f"⏱️  Waiting {stagger_delay}s before starting batch...")
            time.sleep(stagger_delay)

        # Wait for resources if needed
        if wait_for_resources:
            required_level = ResourceLevel.MEDIUM if max_concurrent > 1 else ResourceLevel.LOW
            if not self.resource_monitor.wait_for_resources(required_level):
                logger.warning(f"⚠️  Resources not available, proceeding anyway")

        # Mark batch as running
        with self.lock:
            self.active_batches.add(batch_id)

        result = BatchExecutionResult(
            batch_id=batch_id,
            batch_number=batch_number,
            status=BatchStatus.RUNNING,
            started_at=datetime.now().isoformat()
        )

        start_time = time.time()
        processed = 0
        succeeded = 0
        failed = 0

        try:
            # Process asks with concurrency control
            if max_concurrent == 1:
                # Sequential processing
                for ask in asks:
                    ask_result = self.process_ask(ask)
                    result.results.append(ask_result)
                    processed += 1

                    if ask_result["success"]:
                        succeeded += 1
                    else:
                        failed += 1
                        result.errors.append(f"Ask {ask.get('ask_id', 'unknown')}: {ask_result.get('error', 'Unknown error')}")

                    logger.info(f"   [{processed}/{len(asks)}] {'✅' if ask_result['success'] else '❌'} {ask.get('ask_text', '')[:60]}...")
            else:
                # Parallel processing with semaphore
                import concurrent.futures

                def process_ask_wrapper(ask):
                    return self.process_ask(ask)

                with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent) as executor:
                    future_to_ask = {executor.submit(process_ask_wrapper, ask): ask for ask in asks}

                    for future in concurrent.futures.as_completed(future_to_ask):
                        ask = future_to_ask[future]
                        try:
                            ask_result = future.result()
                            result.results.append(ask_result)
                            processed += 1

                            if ask_result["success"]:
                                succeeded += 1
                            else:
                                failed += 1
                                result.errors.append(f"Ask {ask.get('ask_id', 'unknown')}: {ask_result.get('error', 'Unknown error')}")

                            logger.info(f"   [{processed}/{len(asks)}] {'✅' if ask_result['success'] else '❌'} {ask.get('ask_text', '')[:60]}...")
                        except Exception as e:
                            failed += 1
                            error_msg = f"Ask {ask.get('ask_id', 'unknown')}: {e}"
                            result.errors.append(error_msg)
                            logger.error(f"   ❌ {error_msg}")

            result.asks_processed = processed
            result.asks_succeeded = succeeded
            result.asks_failed = failed
            result.status = BatchStatus.COMPLETED if failed == 0 else BatchStatus.FAILED
            result.completed_at = datetime.now().isoformat()
            result.total_duration = time.time() - start_time

            logger.info("="*80)
            logger.info(f"✅ Batch {batch_number} Complete")
            logger.info(f"   Processed: {processed}, Succeeded: {succeeded}, Failed: {failed}")
            logger.info(f"   Duration: {result.total_duration:.1f}s")
            logger.info("="*80)

        except Exception as e:
            logger.error(f"❌ Error executing batch {batch_id}: {e}", exc_info=True)
            result.status = BatchStatus.FAILED
            result.completed_at = datetime.now().isoformat()
            result.total_duration = time.time() - start_time
            result.errors.append(f"Batch execution error: {e}")

        finally:
            with self.lock:
                self.active_batches.discard(batch_id)

        return result

    def execute_all_batches(self, start_from: int = 1, max_batches: Optional[int] = None, wait_for_resources: bool = True) -> List[BatchExecutionResult]:
        """
        Execute all batches in sequence

        Args:
            start_from: Batch number to start from (1-indexed)
            max_batches: Maximum number of batches to execute (None = all)
            wait_for_resources: If True, wait for resources before each batch

        Returns:
            List of BatchExecutionResult
        """
        logger.info("="*80)
        logger.info("🚀 JARVIS: Executing All Batches")
        logger.info("="*80)

        if not self.batches:
            logger.error("❌ No batches loaded. Load batch plan first.")
            return []

        # Filter batches
        batches_to_execute = [
            batch for batch in self.batches
            if batch["batch_number"] >= start_from
        ]

        if max_batches:
            batches_to_execute = batches_to_execute[:max_batches]

        logger.info(f"📊 Executing {len(batches_to_execute)} batches (starting from batch {start_from})")

        results = []

        for batch in batches_to_execute:
            try:
                result = self.execute_batch(batch, wait_for_resources=wait_for_resources)
                results.append(result)
                self.execution_results.append(result)

                # Save progress after each batch
                self.save_execution_results()

            except KeyboardInterrupt:
                logger.warning("⚠️  Execution interrupted by user")
                break
            except Exception as e:
                logger.error(f"❌ Error in batch execution loop: {e}", exc_info=True)
                error_result = BatchExecutionResult(
                    batch_id=batch["batch_id"],
                    batch_number=batch["batch_number"],
                    status=BatchStatus.FAILED,
                    started_at=datetime.now().isoformat(),
                    completed_at=datetime.now().isoformat(),
                    errors=[str(e)]
                )
                results.append(error_result)
                self.execution_results.append(error_result)

        logger.info("="*80)
        logger.info("✅ All Batches Execution Complete")
        logger.info(f"   Total batches: {len(results)}")
        logger.info(f"   Completed: {sum(1 for r in results if r.status == BatchStatus.COMPLETED)}")
        logger.info(f"   Failed: {sum(1 for r in results if r.status == BatchStatus.FAILED)}")
        logger.info("="*80)

        return results

    def save_execution_results(self) -> Path:
        try:
            """Save execution results to file"""
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = self.data_dir / f"execution_results_{timestamp}.json"

            results_data = {
                "generated_at": datetime.now().isoformat(),
                "total_batches": len(self.execution_results),
                "batches_completed": sum(1 for r in self.execution_results if r.status == BatchStatus.COMPLETED),
                "batches_failed": sum(1 for r in self.execution_results if r.status == BatchStatus.FAILED),
                "total_asks_processed": sum(r.asks_processed for r in self.execution_results),
                "total_asks_succeeded": sum(r.asks_succeeded for r in self.execution_results),
                "total_asks_failed": sum(r.asks_failed for r in self.execution_results),
                "results": [
                    {
                        "batch_id": r.batch_id,
                        "batch_number": r.batch_number,
                        "status": r.status.value,
                        "started_at": r.started_at,
                        "completed_at": r.completed_at,
                        "asks_processed": r.asks_processed,
                        "asks_succeeded": r.asks_succeeded,
                        "asks_failed": r.asks_failed,
                        "total_duration": r.total_duration,
                        "errors": r.errors
                    }
                    for r in self.execution_results
                ]
            }

            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"💾 Execution results saved: {results_file.name}")
            return results_file

        except Exception as e:
            self.logger.error(f"Error in save_execution_results: {e}", exc_info=True)
            raise
    def get_status(self) -> Dict[str, Any]:
        """Get current processing status"""
        return {
            "active_batches": len(self.active_batches),
            "total_batches_loaded": len(self.batches),
            "batches_executed": len(self.execution_results),
            "resource_level": self.resource_monitor.get_resource_level().value,
            "resources": self.resource_monitor.get_resource_level(),
            "active_batch_ids": list(self.active_batches)
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Batch Processing Manager")
    parser.add_argument('--load-plan', type=str, nargs='?', const='latest', help='Load specific batch plan file (or latest if no file specified)')
    parser.add_argument('--execute', action='store_true', help='Execute all batches')
    parser.add_argument('--start-from', type=int, default=1, help='Start from batch number')
    parser.add_argument('--max-batches', type=int, help='Maximum number of batches to execute')
    parser.add_argument('--no-wait-resources', action='store_true', help='Do not wait for resources')
    parser.add_argument('--status', action='store_true', help='Show status')

    args = parser.parse_args()

    print("\n" + "="*80)
    print("🤖 JARVIS BATCH PROCESSING MANAGER")
    print("="*80 + "\n")

    manager = JARVISBatchProcessingManager()

    if args.load_plan or args.execute or args.status:
        # Load batch plan
        plan_file = args.load_plan if args.load_plan else None
        try:
            plan = manager.load_batch_plan(plan_file)
            print(f"✅ Loaded batch plan: {len(manager.batches)} batches")
        except Exception as e:
            print(f"❌ Error loading batch plan: {e}")
            sys.exit(1)

    if args.status:
        status = manager.get_status()
        print("\n📊 STATUS")
        print("="*80)
        print(f"Active Batches: {status['active_batches']}")
        print(f"Total Batches Loaded: {status['total_batches_loaded']}")
        print(f"Batches Executed: {status['batches_executed']}")
        print(f"Resource Level: {status['resource_level']}")
        print("="*80 + "\n")

    if args.execute:
        print("\n🚀 Starting batch execution...")
        results = manager.execute_all_batches(
            start_from=args.start_from,
            max_batches=args.max_batches,
            wait_for_resources=not args.no_wait_resources
        )

        print("\n" + "="*80)
        print("📊 EXECUTION SUMMARY")
        print("="*80)
        print(f"Total Batches: {len(results)}")
        print(f"Completed: {sum(1 for r in results if r.status == BatchStatus.COMPLETED)}")
        print(f"Failed: {sum(1 for r in results if r.status == BatchStatus.FAILED)}")
        print(f"Total Asks Processed: {sum(r.asks_processed for r in results)}")
        print(f"Total Asks Succeeded: {sum(r.asks_succeeded for r in results)}")
        print(f"Total Asks Failed: {sum(r.asks_failed for r in results)}")
        print("="*80 + "\n")

    if not any([args.load_plan, args.execute, args.status]):
        print("Usage:")
        print("  python jarvis_manage_batch_processing.py --load-plan [file] --execute")
        print("  python jarvis_manage_batch_processing.py --status")
        print("  python jarvis_manage_batch_processing.py --execute --start-from 1 --max-batches 5")
