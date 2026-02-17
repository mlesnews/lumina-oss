#!/usr/bin/env python3
"""
JARVIS-Mined Incomplete @ASKS from Inception - Triage & Resource-Aware Batch Processing

Mines all @ASKS from inception, identifies incomplete ones, triages them,
staggered for processing, and creates resource-aware parallel batches managed by JARVIS.

ORDER 66: @DOIT execution command

Tags: #JARVIS #@ASK #INCEPTION #MINING #TRIAGE #BATCH #RESOURCE_AWARE #PARALLEL @JARVIS @DOIT
"""

import sys
import json
import time
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISMineIncompleteAsksInception")

# Import required systems
try:
    from master_todo_from_ask_chain import MasterTodoFromAskChain, CompletionStatus
    ASK_CHAIN_AVAILABLE = True
except ImportError:
    ASK_CHAIN_AVAILABLE = False
    MasterTodoFromAskChain = None
    CompletionStatus = None
    logger.warning("⚠️  Master To-Do from Ask Chain not available")

try:
    from jarvis_ask_stack_triage_docuseries import JARVISAskStackTriageDocuseries, TriagePriority
    TRIAGE_AVAILABLE = True
except ImportError:
    TRIAGE_AVAILABLE = False
    JARVISAskStackTriageDocuseries = None
    TriagePriority = None
    logger.warning("⚠️  JARVIS Ask Stack Triage not available")

try:
    from workflow_chain_triage_batch_processor import BatchConfig
    BATCH_PROCESSOR_AVAILABLE = True
except ImportError:
    BATCH_PROCESSOR_AVAILABLE = False
    BatchConfig = None
    logger.warning("⚠️  Batch processor not available")

# Resource awareness
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("⚠️  psutil not available - resource awareness limited")


class AskStatus(Enum):
    """Ask completion status"""
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    PARTIAL = "partial"
    PENDING = "pending"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class ResourceLevel(Enum):
    """Resource availability level"""
    HIGH = "high"  # Plenty of resources
    MEDIUM = "medium"  # Normal resources
    LOW = "low"  # Limited resources
    CRITICAL = "critical"  # Very limited resources


@dataclass
class IncompleteAsk:
    """Incomplete @ASK from inception"""
    ask_id: str
    ask_text: str
    timestamp: str
    source: str
    category: str
    priority: str
    status: AskStatus
    triage_priority: Optional[TriagePriority] = None
    estimated_duration: int = 30  # minutes
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    batch_number: int = 0
    stagger_delay: int = 0  # seconds before processing
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceAwareBatch:
    """Resource-aware batch configuration"""
    batch_id: str
    batch_number: int
    asks: List[IncompleteAsk]
    resource_level: ResourceLevel
    max_concurrent: int
    stagger_delay: int  # seconds between batch start
    estimated_duration: int  # minutes
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"  # pending, running, completed, failed
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class ResourceMonitor:
    """Resource monitoring for batch processing"""
    cpu_threshold_high: float = 80.0  # %
    memory_threshold_high: float = 80.0  # %
    disk_threshold_high: float = 90.0  # %

    def get_resource_level(self) -> ResourceLevel:
        """Get current resource availability level"""
        if not PSUTIL_AVAILABLE:
            return ResourceLevel.MEDIUM

        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # Determine resource level
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

    def get_available_resources(self) -> Dict[str, Any]:
        """Get current resource availability"""
        if not PSUTIL_AVAILABLE:
            return {
                "cpu_percent": 50.0,
                "memory_percent": 50.0,
                "disk_percent": 50.0,
                "available": True
            }

        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_free_gb": disk.free / (1024**3),
                "available": cpu_percent < self.cpu_threshold_high and memory.percent < self.memory_threshold_high and disk.percent < self.disk_threshold_high
            }
        except Exception as e:
            logger.warning(f"⚠️  Error getting resources: {e}")
            return {"available": False}


class JARVISMineIncompleteAsksInception:
    """
    JARVIS-Mined Incomplete @ASKS from Inception System

    Mines all @ASKS from inception, identifies incomplete ones, triages them,
    creates staggered resource-aware batches, and manages processing via JARVIS.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize JARVIS mining system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "jarvis_incomplete_asks"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize subsystems
        self.ask_chain = None
        if ASK_CHAIN_AVAILABLE:
            try:
                self.ask_chain = MasterTodoFromAskChain(project_root=self.project_root)
                logger.info("✅ Master To-Do from Ask Chain initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize Ask Chain: {e}")

        self.triage_system = None
        if TRIAGE_AVAILABLE:
            try:
                self.triage_system = JARVISAskStackTriageDocuseries(project_root=self.project_root)
                logger.info("✅ JARVIS Ask Stack Triage initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize Triage: {e}")

        self.resource_monitor = ResourceMonitor()
        self.all_asks: List[Dict[str, Any]] = []
        self.incomplete_asks: List[IncompleteAsk] = []
        self.triaged_asks: List[IncompleteAsk] = []
        self.batches: List[ResourceAwareBatch] = []

        logger.info("✅ JARVIS Mine Incomplete Asks from Inception initialized")

    def mine_all_asks_from_inception(self) -> List[Dict[str, Any]]:
        """
        Mine all @ASKS from inception (zero ask to present)

        Searches all sources:
        - LUMINA_ALL_ASKS_ORDERED.json
        - ask_cache/discovered_asks.json
        - ask_stack_trace files
        - enhanced_memory.db
        - All workflow archives
        """
        logger.info("="*80)
        logger.info("⛏️  ORDER 66: Mining All @ASKS from Inception")
        logger.info("="*80)

        all_asks = []

        # Method 1: Master To-Do from Ask Chain
        if self.ask_chain:
            try:
                asks = self.ask_chain.load_all_asks()
                all_asks.extend(asks)
                logger.info(f"   ✅ Loaded {len(asks)} @asks from Ask Chain")
            except Exception as e:
                logger.warning(f"   ⚠️  Error loading from Ask Chain: {e}")

        # Method 2: ask_cache/discovered_asks.json
        ask_cache_file = self.project_root / "data" / "ask_cache" / "discovered_asks.json"
        if ask_cache_file.exists():
            try:
                with open(ask_cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    # Handle both dict and list formats
                    if isinstance(cache_data, dict):
                        cache_asks = cache_data.get("asks", []) or cache_data.get("discovered_asks", [])
                    else:
                        cache_asks = cache_data

                    # Deduplicate
                    seen_ids = {ask.get("ask_id", ask.get("id", "")) for ask in all_asks}
                    new_asks = [ask for ask in cache_asks if ask.get("ask_id", ask.get("id", "")) not in seen_ids]
                    all_asks.extend(new_asks)
                    logger.info(f"   ✅ Loaded {len(new_asks)} new @asks from cache")
            except Exception as e:
                logger.warning(f"   ⚠️  Error loading from cache: {e}")

        # Method 3: ask_stack_trace files
        trace_dir = self.project_root / "data" / "ask_stack_trace"
        if trace_dir.exists():
            try:
                trace_files = list(trace_dir.glob("ask_stack_trace_*.json"))
                for trace_file in trace_files:
                    try:
                        with open(trace_file, 'r', encoding='utf-8') as f:
                            trace_data = json.load(f)
                            trace_asks = trace_data.get("asks", []) or trace_data.get("ask_stack", [])
                            # Deduplicate
                            seen_ids = {ask.get("ask_id", ask.get("id", "")) for ask in all_asks}
                            new_asks = [ask for ask in trace_asks if ask.get("ask_id", ask.get("id", "")) not in seen_ids]
                            all_asks.extend(new_asks)
                    except Exception as e:
                        logger.debug(f"   ⚠️  Error loading {trace_file.name}: {e}")
                logger.info(f"   ✅ Loaded @asks from {len(trace_files)} trace files")
            except Exception as e:
                logger.warning(f"   ⚠️  Error loading trace files: {e}")

        # Sort by timestamp (oldest first - inception to present)
        all_asks.sort(key=lambda x: x.get("timestamp", x.get("created_at", "")))

        self.all_asks = all_asks
        logger.info(f"📊 Total @asks mined from inception: {len(all_asks)}")

        return all_asks

    def identify_incomplete_asks(self) -> List[IncompleteAsk]:
        """
        Identify all incomplete @ASKS

        Filters out completed asks and identifies:
        - pending
        - in_progress
        - partial
        - blocked
        """
        logger.info("="*80)
        logger.info("🔍 Identifying Incomplete @ASKS")
        logger.info("="*80)

        incomplete = []

        for ask in self.all_asks:
            # Determine status
            status_str = ask.get("status", "pending")
            if isinstance(status_str, str):
                try:
                    status = AskStatus(status_str)
                except ValueError:
                    # Try to infer from other fields
                    if any(word in str(ask.get("ask_text", "")).lower() for word in ["complete", "done", "finished"]):
                        status = AskStatus.COMPLETED
                    elif any(word in str(ask.get("ask_text", "")).lower() for word in ["in progress", "working"]):
                        status = AskStatus.IN_PROGRESS
                    elif any(word in str(ask.get("ask_text", "")).lower() for word in ["blocked", "waiting"]):
                        status = AskStatus.BLOCKED
                    else:
                        status = AskStatus.PENDING
            else:
                status = AskStatus.PENDING

            # Skip completed and cancelled
            if status in [AskStatus.COMPLETED, AskStatus.CANCELLED]:
                continue

            # Create IncompleteAsk
            incomplete_ask = IncompleteAsk(
                ask_id=ask.get("ask_id", ask.get("id", f"ask_{len(incomplete)}")),
                ask_text=ask.get("ask_text", ask.get("text", ask.get("content", ""))),
                timestamp=ask.get("timestamp", ask.get("created_at", datetime.now().isoformat())),
                source=ask.get("source", "unknown"),
                category=ask.get("category", "general"),
                priority=ask.get("priority", "normal"),
                status=status,
                dependencies=ask.get("dependencies", []),
                metadata=ask.get("metadata", {})
            )

            incomplete.append(incomplete_ask)

        self.incomplete_asks = incomplete
        logger.info(f"📊 Total incomplete @asks: {len(incomplete)}")
        logger.info(f"   - Pending: {sum(1 for a in incomplete if a.status == AskStatus.PENDING)}")
        logger.info(f"   - In Progress: {sum(1 for a in incomplete if a.status == AskStatus.IN_PROGRESS)}")
        logger.info(f"   - Partial: {sum(1 for a in incomplete if a.status == AskStatus.PARTIAL)}")
        logger.info(f"   - Blocked: {sum(1 for a in incomplete if a.status == AskStatus.BLOCKED)}")

        return incomplete

    def triage_asks(self) -> List[IncompleteAsk]:
        """
        Triage all incomplete @ASKS

        Uses JARVIS Ask Stack Triage system to:
        - Assign triage priorities
        - Categorize asks
        - Identify dependencies
        - Estimate processing duration
        """
        logger.info("="*80)
        logger.info("🎯 Triaging Incomplete @ASKS")
        logger.info("="*80)

        triaged = []

        for ask in self.incomplete_asks:
            # Use triage system if available
            if self.triage_system:
                try:
                    # Use _triage_single_ask method which expects a dict
                    ask_dict = {
                        "ask_text": ask.ask_text,
                        "category": ask.category,
                        "priority": ask.priority
                    }
                    triage_result = self.triage_system._triage_single_ask(ask_dict)

                    if triage_result:
                        ask.triage_priority = triage_result.priority if hasattr(triage_result, 'priority') and TRIAGE_AVAILABLE else None
                        ask.estimated_duration = triage_result.estimated_duration if hasattr(triage_result, 'estimated_duration') else 30
                        ask.dependencies = triage_result.dependencies if hasattr(triage_result, 'dependencies') else []
                except Exception as e:
                    logger.debug(f"   ⚠️  Error triaging {ask.ask_id}: {e}")

            # Assign default triage priority based on status and priority
            if not ask.triage_priority and TRIAGE_AVAILABLE:
                if ask.status == AskStatus.BLOCKED:
                    ask.triage_priority = TriagePriority.LOW
                elif ask.priority == "critical":
                    ask.triage_priority = TriagePriority.CRITICAL
                elif ask.priority == "high":
                    ask.triage_priority = TriagePriority.HIGH
                elif ask.priority == "low":
                    ask.triage_priority = TriagePriority.LOW
                else:
                    ask.triage_priority = TriagePriority.MEDIUM

            triaged.append(ask)

        # Sort by triage priority
        if TRIAGE_AVAILABLE:
            priority_order = {
                TriagePriority.CRITICAL: 0,
                TriagePriority.HIGH: 1,
                TriagePriority.MEDIUM: 2,
                TriagePriority.LOW: 3,
                TriagePriority.ARCHIVE: 4
            }
            triaged.sort(key=lambda x: priority_order.get(x.triage_priority, 99))

        self.triaged_asks = triaged
        logger.info(f"📊 Total triaged @asks: {len(triaged)}")

        if TRIAGE_AVAILABLE:
            logger.info(f"   - Critical: {sum(1 for a in triaged if a.triage_priority == TriagePriority.CRITICAL)}")
            logger.info(f"   - High: {sum(1 for a in triaged if a.triage_priority == TriagePriority.HIGH)}")
            logger.info(f"   - Medium: {sum(1 for a in triaged if a.triage_priority == TriagePriority.MEDIUM)}")
            logger.info(f"   - Low: {sum(1 for a in triaged if a.triage_priority == TriagePriority.LOW)}")

        return triaged

    def stagger_asks_for_triage(self, stagger_delay_base: int = 60) -> List[IncompleteAsk]:
        """
        Stagger @ASKS for triage and processing

        Calculates stagger delays based on:
        - Triage priority (critical first)
        - Resource availability
        - Batch assignment
        """
        logger.info("="*80)
        logger.info("⏱️  Staggering @ASKS for Triage and Processing")
        logger.info("="*80)

        staggered = []
        current_delay = 0

        for ask in self.triaged_asks:
            # Calculate stagger delay based on priority
            if TRIAGE_AVAILABLE and ask.triage_priority:
                if ask.triage_priority == TriagePriority.CRITICAL:
                    delay = 0  # Immediate
                elif ask.triage_priority == TriagePriority.HIGH:
                    delay = stagger_delay_base // 2
                elif ask.triage_priority == TriagePriority.MEDIUM:
                    delay = stagger_delay_base
                else:
                    delay = stagger_delay_base * 2
            else:
                delay = stagger_delay_base

            ask.stagger_delay = current_delay
            current_delay += delay

            staggered.append(ask)

        logger.info(f"📊 Total staggered @asks: {len(staggered)}")
        logger.info(f"   Total stagger time: {current_delay // 60} minutes")

        return staggered

    def create_resource_aware_batches(self, batch_size: int = 5, max_batches: int = 10) -> List[ResourceAwareBatch]:
        """
        Create resource-aware parallel batches

        Batches are created based on:
        - Resource availability (CPU, memory, disk)
        - Triage priority
        - Dependencies
        - Estimated duration
        """
        logger.info("="*80)
        logger.info("📦 Creating Resource-Aware Parallel Batches")
        logger.info("="*80)

        # Get current resource level
        resource_level = self.resource_monitor.get_resource_level()
        resources = self.resource_monitor.get_available_resources()

        logger.info(f"   Current Resource Level: {resource_level.value}")
        logger.info(f"   CPU: {resources.get('cpu_percent', 0):.1f}%, Memory: {resources.get('memory_percent', 0):.1f}%, Disk: {resources.get('disk_percent', 0):.1f}%")

        # Determine max concurrent based on resource level
        if resource_level == ResourceLevel.HIGH:
            max_concurrent = batch_size
        elif resource_level == ResourceLevel.MEDIUM:
            max_concurrent = max(2, batch_size // 2)
        elif resource_level == ResourceLevel.LOW:
            max_concurrent = max(1, batch_size // 3)
        else:  # CRITICAL
            max_concurrent = 1

        # Create batches
        batches = []
        batch_number = 1
        stagger_delay = 0

        # Group asks by priority first
        priority_groups = defaultdict(list)
        for ask in self.triaged_asks:
            if TRIAGE_AVAILABLE and ask.triage_priority:
                priority_key = ask.triage_priority.value
            else:
                priority_key = ask.priority
            priority_groups[priority_key].append(ask)

        # Process priority groups in order
        priority_order = ["critical", "high", "medium", "low", "archive"]

        for priority_key in priority_order:
            if priority_key not in priority_groups:
                continue

            asks = priority_groups[priority_key]

            # Split into batches
            for i in range(0, len(asks), batch_size):
                batch_asks = asks[i:i + batch_size]

                # Assign batch number and stagger delay
                for ask in batch_asks:
                    ask.batch_number = batch_number

                # Calculate batch resource requirements
                total_duration = sum(ask.estimated_duration for ask in batch_asks)

                batch = ResourceAwareBatch(
                    batch_id=f"batch_{batch_number:03d}_{priority_key}",
                    batch_number=batch_number,
                    asks=batch_asks,
                    resource_level=resource_level,
                    max_concurrent=max_concurrent,
                    stagger_delay=stagger_delay,
                    estimated_duration=total_duration,
                    resource_requirements={
                        "max_concurrent": max_concurrent,
                        "estimated_cpu": min(100, max_concurrent * 10),
                        "estimated_memory_mb": len(batch_asks) * 512
                    }
                )

                batches.append(batch)
                batch_number += 1
                stagger_delay += 120  # 2 minutes between batches

                if batch_number > max_batches:
                    break

            if batch_number > max_batches:
                break

        self.batches = batches
        logger.info(f"📊 Total batches created: {len(batches)}")
        logger.info(f"   Max concurrent per batch: {max_concurrent}")
        logger.info(f"   Total stagger time: {stagger_delay // 60} minutes")

        return batches

    def save_batch_plan(self) -> Path:
        try:
            """Save batch processing plan for JARVIS"""
            logger.info("💾 Saving batch processing plan...")

            plan = {
                "generated_at": datetime.now().isoformat(),
                "total_asks_mined": len(self.all_asks),
                "incomplete_asks": len(self.incomplete_asks),
                "triaged_asks": len(self.triaged_asks),
                "batches_created": len(self.batches),
                "resource_level": self.resource_monitor.get_resource_level().value,
                "resources": self.resource_monitor.get_available_resources(),
                "batches": [
                    {
                        "batch_id": batch.batch_id,
                        "batch_number": batch.batch_number,
                        "ask_count": len(batch.asks),
                        "resource_level": batch.resource_level.value,
                        "max_concurrent": batch.max_concurrent,
                        "stagger_delay": batch.stagger_delay,
                        "estimated_duration": batch.estimated_duration,
                        "asks": [
                            {
                                "ask_id": ask.ask_id,
                                "ask_text": ask.ask_text[:100],
                                "priority": ask.priority,
                                "status": ask.status.value,
                                "triage_priority": ask.triage_priority.value if ask.triage_priority else None,
                                "estimated_duration": ask.estimated_duration
                            }
                            for ask in batch.asks
                        ]
                    }
                    for batch in self.batches
                ]
            }

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plan_file = self.data_dir / f"batch_plan_{timestamp}.json"

            with open(plan_file, 'w', encoding='utf-8') as f:
                json.dump(plan, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"   ✅ Batch plan saved: {plan_file.name}")
            return plan_file

        except Exception as e:
            self.logger.error(f"Error in save_batch_plan: {e}", exc_info=True)
            raise
    def generate_jarvis_workflow_integration(self) -> Dict[str, Any]:
        """Generate JARVIS workflow integration data"""
        logger.info("🔗 Generating JARVIS Workflow Integration...")

        integration = {
            "generated_at": datetime.now().isoformat(),
            "managed_by": "JARVIS",
            "total_batches": len(self.batches),
            "batches": [
                {
                    "batch_id": batch.batch_id,
                    "batch_number": batch.batch_number,
                    "workflow_name": f"Process Batch {batch.batch_number}",
                    "asks": [ask.ask_id for ask in batch.asks],
                    "stagger_delay": batch.stagger_delay,
                    "max_concurrent": batch.max_concurrent,
                    "resource_requirements": batch.resource_requirements,
                    "workflow_config": {
                        "parallel": batch.max_concurrent > 1,
                        "resource_aware": True,
                        "staggered": batch.stagger_delay > 0
                    }
                }
                for batch in self.batches
            ]
        }

        return integration

    def execute_full_mining_and_triage(self) -> Dict[str, Any]:
        """
        Execute full mining, triage, and batch creation process

        ORDER 66: @DOIT execution command
        """
        logger.info("="*80)
        logger.info("🚀 ORDER 66: JARVIS Mine Incomplete @ASKS from Inception")
        logger.info("   - Mining all @asks from inception")
        logger.info("   - Identifying incomplete asks")
        logger.info("   - Triaging for priority")
        logger.info("   - Staggering for processing")
        logger.info("   - Creating resource-aware parallel batches")
        logger.info("   - Managed by JARVIS")
        logger.info("="*80)

        result = {
            "timestamp": datetime.now().isoformat(),
            "execution_type": "ORDER 66: @DOIT",
            "managed_by": "JARVIS",
            "success": False,
            "asks_mined": 0,
            "incomplete_asks": 0,
            "triaged_asks": 0,
            "batches_created": 0,
            "errors": []
        }

        try:
            # Step 1: Mine all asks from inception
            all_asks = self.mine_all_asks_from_inception()
            result["asks_mined"] = len(all_asks)

            # Step 2: Identify incomplete asks
            incomplete = self.identify_incomplete_asks()
            result["incomplete_asks"] = len(incomplete)

            # Step 3: Triage asks
            triaged = self.triage_asks()
            result["triaged_asks"] = len(triaged)

            # Step 4: Stagger asks for processing
            staggered = self.stagger_asks_for_triage()

            # Step 5: Create resource-aware batches
            batches = self.create_resource_aware_batches()
            result["batches_created"] = len(batches)

            # Step 6: Save batch plan
            plan_file = self.save_batch_plan()
            result["batch_plan_file"] = str(plan_file.relative_to(self.project_root))

            # Step 7: Generate JARVIS integration
            integration = self.generate_jarvis_workflow_integration()
            integration_file = self.data_dir / "jarvis_integration.json"
            with open(integration_file, 'w', encoding='utf-8') as f:
                json.dump(integration, f, indent=2, ensure_ascii=False, default=str)
            result["jarvis_integration_file"] = str(integration_file.relative_to(self.project_root))

            result["success"] = True

            logger.info("="*80)
            logger.info("✅ ORDER 66: JARVIS Mining and Triage Complete")
            logger.info(f"   Total @asks mined: {result['asks_mined']}")
            logger.info(f"   Incomplete @asks: {result['incomplete_asks']}")
            logger.info(f"   Triaged @asks: {result['triaged_asks']}")
            logger.info(f"   Batches created: {result['batches_created']}")
            logger.info("="*80)

        except Exception as e:
            error_msg = f"Error in mining and triage: {e}"
            logger.error(f"❌ {error_msg}", exc_info=True)
            result["errors"].append(error_msg)

        # Save execution result
        result_file = self.data_dir / f"mining_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)

        return result


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 ORDER 66: JARVIS Mine Incomplete @ASKS from Inception")
    print("   - Mining all @asks from inception")
    print("   - Triage & Staggered Processing")
    print("   - Resource-Aware Parallel Batches")
    print("   - Managed by JARVIS")
    print("="*80 + "\n")

    miner = JARVISMineIncompleteAsksInception()
    result = miner.execute_full_mining_and_triage()

    print("\n" + "="*80)
    print("📊 EXECUTION RESULT")
    print("="*80)
    print(f"Success: {result['success']}")
    print(f"@ASKS Mined: {result['asks_mined']}")
    print(f"Incomplete @ASKS: {result['incomplete_asks']}")
    print(f"Triaged @ASKS: {result['triaged_asks']}")
    print(f"Batches Created: {result['batches_created']}")

    if result.get('batch_plan_file'):
        print(f"\nBatch Plan: {result['batch_plan_file']}")
    if result.get('jarvis_integration_file'):
        print(f"JARVIS Integration: {result['jarvis_integration_file']}")

    if result.get('errors'):
        print(f"\n⚠️  Errors: {len(result['errors'])}")
        for error in result['errors']:
            print(f"   - {error}")

    print("\n✅ ORDER 66: Execution Complete")
    print("="*80 + "\n")
