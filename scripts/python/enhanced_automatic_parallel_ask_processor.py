#!/usr/bin/env python3
"""
Enhanced Automatic Parallel @ASK Batch Processor

AUTOMATIC BACKGROUND BATCH PARALLEL PROCESSING with:
- Automatic similarity detection for @ASKS
- Background batch parallel processing (multithreading & multiprocessing)
- @PEAK framework selection (Docker, ElevenLabs, MANUS, MCP, Local)
- Subagent delegation with dynamic scaling
- @DYNAMIC-SCALING-MODULE integration
- Resource-aware load balancing
- Prevents sequential single-processor CPU logic

Context Enhancements:
- @DYNO: Performance testing and tuning
- @BG[#BACKGROUND]: Background processing mode
- @BAL: Load balancing and resource balancing
- @REC: Recommendations and suggestions
- #TROUBLESHOOTING: Automatic troubleshooting integration
- #DECISIONING: Decision tree integration for routing
- @DOIT: Integration with autonomous execution system

Tags: #PARALLEL #BATCH #ASK #PEAK #DYNAMIC_SCALING #SUBAGENT #MULTITHREAD #MULTIPROCESS #TROUBLESHOOTING #DECISIONING @JARVIS @TEAM @DYNO @BG @BAL @REC @DOIT
"""

import sys
import json
import time
import threading
import multiprocessing
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import queue
import hashlib
import logging
import psutil

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("EnhancedAutomaticParallelAskProcessor")

# Import base processor
try:
    from automatic_parallel_ask_processor import (
        AutomaticParallelAskProcessor,
        Ask, AskBatch, AskSimilarityLevel
    )
    BASE_PROCESSOR_AVAILABLE = True
except ImportError:
    BASE_PROCESSOR_AVAILABLE = False
    AutomaticParallelAskProcessor = None
    Ask = None
    AskBatch = None
    AskSimilarityLevel = None

# @PEAK Framework Selection
try:
    from jarvis_peak_agent_management import JARVISPeakAgentManagement, AgentType
    PEAK_AGENT_MGMT_AVAILABLE = True
except ImportError:
    PEAK_AGENT_MGMT_AVAILABLE = False
    JARVISPeakAgentManagement = None
    AgentType = None

# Dynamic Scaling
try:
    from workflow_dynamic_scaler import WorkflowDynamicScaler
    DYNAMIC_SCALER_AVAILABLE = True
except ImportError:
    try:
        from dynamic_timeout_scaling import DynamicTimeoutScaling
        DYNAMIC_SCALER_AVAILABLE = True
        WorkflowDynamicScaler = DynamicTimeoutScaling
    except ImportError:
        DYNAMIC_SCALER_AVAILABLE = False
        WorkflowDynamicScaler = None

# Subagent Delegation
try:
    from jarvis_subagent_delegation import JARVISSubagentDelegation, AgentDomain
    SUBAGENT_DELEGATION_AVAILABLE = True
except ImportError:
    SUBAGENT_DELEGATION_AVAILABLE = False
    JARVISSubagentDelegation = None
    AgentDomain = None

# @DYNO Performance Testing
try:
    from jarvis_dyno_performance_tuner import JARVISDynoPerformanceTuner
    DYNO_AVAILABLE = True
except ImportError:
    DYNO_AVAILABLE = False
    JARVISDynoPerformanceTuner = None

# @DOIT Autonomous Execution
try:
    from jarvis_doit_executor import JARVISDOITExecutor
    DOIT_AVAILABLE = True
except ImportError:
    DOIT_AVAILABLE = False
    JARVISDOITExecutor = None

# #DECISIONING - Decision Tree System
try:
    from universal_decision_tree import decide, DecisionContext, DecisionOutcome
    DECISIONING_AVAILABLE = True
except ImportError:
    DECISIONING_AVAILABLE = False
    decide = None
    DecisionContext = None
    DecisionOutcome = None

# #TROUBLESHOOTING - Troubleshooting System
try:
    from universal_workflow_troubleshooting import UniversalWorkflowTroubleshooter
    TROUBLESHOOTING_AVAILABLE = True
except ImportError:
    try:
        from jarvis_syphon_enhanced_troubleshooting import JARVISSyphonEnhancedTroubleshooting
        TROUBLESHOOTING_AVAILABLE = True
        UniversalWorkflowTroubleshooter = JARVISSyphonEnhancedTroubleshooting
    except ImportError:
        TROUBLESHOOTING_AVAILABLE = False
        UniversalWorkflowTroubleshooter = None


class TaskType(Enum):
    """Task type for processing method selection"""
    CPU_BOUND = "cpu_bound"  # Use multiprocessing
    IO_BOUND = "io_bound"  # Use multithreading
    MIXED = "mixed"  # Use hybrid approach


class EnhancedAutomaticParallelAskProcessor:
    """
    Enhanced Automatic Parallel @ASK Batch Processor

    AUTOMATIC BACKGROUND BATCH PARALLEL PROCESSING:
    - Detects similar @ASKS automatically
    - Processes in parallel (multithreading & multiprocessing)
    - Uses @PEAK framework selection
    - Integrates with @DYNAMIC-SCALING-MODULE
    - Delegates to subagents
    - Resource-aware load balancing
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Enhanced Automatic Parallel @ASK Processor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "enhanced_parallel_ask_processing"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Base processor (if available)
        self.base_processor = None
        if BASE_PROCESSOR_AVAILABLE:
            try:
                self.base_processor = AutomaticParallelAskProcessor(project_root=project_root)
                logger.info("✅ Base Automatic Parallel Processor initialized")
            except Exception as e:
                logger.warning(f"⚠️  Base processor not available: {e}")

        # @PEAK Agent Management
        self.peak_agent_mgmt = None
        if PEAK_AGENT_MGMT_AVAILABLE:
            try:
                self.peak_agent_mgmt = JARVISPeakAgentManagement(project_root=project_root)
                logger.info("✅ @PEAK Agent Management initialized")
            except Exception as e:
                logger.warning(f"⚠️  @PEAK Agent Management not available: {e}")

        # Dynamic Scaling Module
        self.dynamic_scaler = None
        if DYNAMIC_SCALER_AVAILABLE:
            try:
                self.dynamic_scaler = WorkflowDynamicScaler(project_root=project_root)
                logger.info("✅ @DYNAMIC-SCALING-MODULE initialized")
            except Exception as e:
                logger.warning(f"⚠️  Dynamic Scaling Module not available: {e}")

        # Subagent Delegation
        self.subagent_delegation = None
        if SUBAGENT_DELEGATION_AVAILABLE:
            try:
                self.subagent_delegation = JARVISSubagentDelegation(project_root=project_root)
                logger.info("✅ Subagent Delegation initialized")
            except Exception as e:
                logger.warning(f"⚠️  Subagent Delegation not available: {e}")

        # @DYNO Performance Testing
        self.dyno_tuner = None
        if DYNO_AVAILABLE:
            try:
                self.dyno_tuner = JARVISDynoPerformanceTuner(project_root=project_root)
                logger.info("✅ @DYNO Performance Tuner initialized")
            except Exception as e:
                logger.warning(f"⚠️  @DYNO not available: {e}")

        # @DOIT Autonomous Execution
        self.doit_executor = None
        if DOIT_AVAILABLE:
            try:
                self.doit_executor = JARVISDOITExecutor(project_root=project_root)
                logger.info("✅ @DOIT Executor initialized")
            except Exception as e:
                logger.warning(f"⚠️  @DOIT not available: {e}")

        # #DECISIONING - Decision Tree System
        self.decisioning_available = DECISIONING_AVAILABLE
        if DECISIONING_AVAILABLE:
            logger.info("✅ #DECISIONING (Decision Tree) available")

        # #TROUBLESHOOTING - Troubleshooting System
        self.troubleshooter = None
        if TROUBLESHOOTING_AVAILABLE:
            try:
                self.troubleshooter = UniversalWorkflowTroubleshooter(project_root=project_root)
                logger.info("✅ #TROUBLESHOOTING system initialized")
            except Exception as e:
                logger.warning(f"⚠️  #TROUBLESHOOTING not available: {e}")

        # @BG[#BACKGROUND] - Background processing flag
        self.background_mode = True  # Always background for automatic processing

        # @BAL - Load balancing enabled
        self.load_balancing_enabled = True

        # @REC - Recommendations system
        self.recommendations_enabled = True

        # Resource monitoring
        self.cpu_count = multiprocessing.cpu_count()
        self.max_workers_threads = max(1, self.cpu_count * 2)  # I/O-bound: 2x CPU
        self.max_workers_processes = max(1, self.cpu_count - 1)  # CPU-bound: CPU-1

        # Dynamic worker adjustment
        self.current_workers_threads = self.max_workers_threads
        self.current_workers_processes = self.max_workers_processes

        # Processing queues
        self.ask_queue = queue.Queue()
        self.batch_queue = queue.Queue()
        self.results_queue = queue.Queue()

        # Background processing
        self.processing_thread = None
        self.resource_monitor_thread = None
        self.is_processing = False
        self.processing_lock = threading.Lock()

        # Similarity threshold
        self.similarity_threshold = 2  # Lower threshold for faster batching

        # Resource monitoring interval
        self.resource_check_interval = 5.0  # Check resources every 5 seconds

        logger.info("✅ Enhanced Automatic Parallel @ASK Processor initialized")
        logger.info(f"   CPU Cores: {self.cpu_count}")
        logger.info(f"   Max Thread Workers: {self.max_workers_threads}")
        logger.info(f"   Max Process Workers: {self.max_workers_processes}")
        logger.info(f"   Similarity Threshold: {self.similarity_threshold} asks")
        logger.info("   🚀 AUTOMATIC BACKGROUND BATCH PARALLEL PROCESSING ENABLED")
        logger.info("   Context Enhancements:")
        logger.info(f"      @DYNO: {'✅' if self.dyno_tuner else '❌'}")
        logger.info(f"      @BG[#BACKGROUND]: ✅ (Always enabled)")
        logger.info(f"      @BAL: {'✅' if self.load_balancing_enabled else '❌'}")
        logger.info(f"      @REC: {'✅' if self.recommendations_enabled else '❌'}")
        logger.info(f"      #TROUBLESHOOTING: {'✅' if self.troubleshooter else '❌'}")
        logger.info(f"      #DECISIONING: {'✅' if self.decisioning_available else '❌'}")
        logger.info(f"      @DOIT: {'✅' if self.doit_executor else '❌'}")

    def add_ask(self, ask_text: str, source: str = "unknown", metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add an @ASK to the processing queue (AUTOMATIC)

        Returns:
            ask_id: Unique identifier for this ask
        """
        ask_id = f"ask_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        # Create Ask object
        if BASE_PROCESSOR_AVAILABLE and Ask:
            ask = Ask(
                ask_id=ask_id,
                ask_text=ask_text,
                source=source,
                timestamp=datetime.now(),
                metadata=metadata or {}
            )
        else:
            # Fallback: simple dict
            ask = {
                "ask_id": ask_id,
                "ask_text": ask_text,
                "source": source,
                "timestamp": datetime.now(),
                "metadata": metadata or {}
            }

        self.ask_queue.put(ask)
        logger.debug(f"📥 Added @ASK: {ask_id} ({ask_text[:50]}...)")

        # AUTOMATIC: Start background processing
        self._start_background_processing()

        return ask_id

    def _start_background_processing(self):
        """Start background processing threads (AUTOMATIC)"""
        with self.processing_lock:
            if not self.is_processing:
                self.is_processing = True

                # Main processing thread
                self.processing_thread = threading.Thread(
                    target=self._background_processing_loop,
                    daemon=True,
                    name="AskProcessor"
                )
                self.processing_thread.start()

                # Resource monitoring thread
                self.resource_monitor_thread = threading.Thread(
                    target=self._resource_monitoring_loop,
                    daemon=True,
                    name="ResourceMonitor"
                )
                self.resource_monitor_thread.start()

                logger.info("🚀 Background processing threads started (AUTOMATIC)")

    def _resource_monitoring_loop(self):
        """Monitor system resources and adjust workers dynamically"""
        logger.info("📊 Resource monitoring loop started")

        while self.is_processing:
            try:
                # Get current resource usage
                cpu_percent = psutil.cpu_percent(interval=1.0)
                memory = psutil.virtual_memory()
                memory_percent = memory.percent

                # Adjust workers based on resources
                if cpu_percent > 80:
                    # High CPU - reduce workers
                    self.current_workers_threads = max(1, int(self.max_workers_threads * 0.7))
                    self.current_workers_processes = max(1, int(self.max_workers_processes * 0.7))
                    logger.debug(f"   ⚠️  High CPU ({cpu_percent:.1f}%) - reducing workers")
                elif cpu_percent < 50 and memory_percent < 70:
                    # Low usage - can increase workers
                    self.current_workers_threads = min(self.max_workers_threads, int(self.current_workers_threads * 1.2))
                    self.current_workers_processes = min(self.max_workers_processes, int(self.current_workers_processes * 1.2))
                    logger.debug(f"   ✅ Low usage - increasing workers")

                # Use dynamic scaler if available
                if self.dynamic_scaler:
                    # Get scaling recommendations
                    scaling_decision = self.dynamic_scaler.get_scaling_decision("ask_processor")
                    if scaling_decision:
                        recommended_scale = scaling_decision.recommended_scale
                        self.current_workers_threads = min(self.max_workers_threads, recommended_scale)
                        self.current_workers_processes = min(self.max_workers_processes, recommended_scale)
                        logger.debug(f"   📈 Dynamic scaling: {recommended_scale} workers")

                time.sleep(self.resource_check_interval)

            except Exception as e:
                logger.error(f"❌ Error in resource monitoring: {e}")
                time.sleep(self.resource_check_interval)

    def _background_processing_loop(self):
        """Background processing loop - AUTOMATIC batch detection and parallel processing"""
        logger.info("🔄 Background processing loop started (AUTOMATIC)")

        ask_buffer: Dict[str, List[Any]] = {}  # similarity_hash -> List[Ask]
        last_batch_time = time.time()
        batch_timeout = 3.0  # Wait 3 seconds for more similar asks

        while self.is_processing:
            try:
                # Collect asks with timeout
                try:
                    ask = self.ask_queue.get(timeout=1.0)

                    # Calculate similarity hash
                    similarity_hash = self._calculate_similarity_hash(ask)

                    ask_buffer.setdefault(similarity_hash, []).append(ask)
                    logger.debug(f"   📦 Buffered ask: {self._get_ask_id(ask)} (hash: {similarity_hash[:8]})")

                except queue.Empty:
                    # Timeout - check if we should process batches
                    pass

                # Check for batches ready to process
                current_time = time.time()
                time_since_last_batch = current_time - last_batch_time

                # Process batches if:
                # 1. We have enough similar asks (>= threshold)
                # 2. OR timeout reached (waiting too long)
                batches_to_process = []

                for similarity_hash, asks in list(ask_buffer.items()):
                    if len(asks) >= self.similarity_threshold:
                        # Enough similar asks - create batch
                        batch = self._create_batch(asks, similarity_hash)
                        batches_to_process.append(batch)
                        del ask_buffer[similarity_hash]
                        logger.info(f"   ✅ Batch ready: {len(asks)} similar asks")
                    elif time_since_last_batch >= batch_timeout and len(asks) > 0:
                        # Timeout reached - process what we have
                        batch = self._create_batch(asks, similarity_hash)
                        batches_to_process.append(batch)
                        del ask_buffer[similarity_hash]
                        logger.info(f"   ⏰ Batch timeout: {len(asks)} asks")

                # Process batches in parallel (MULTITHREAD & MULTIPROCESS)
                if batches_to_process:
                    self._process_batches_parallel_enhanced(batches_to_process)
                    last_batch_time = current_time

                # Small sleep to prevent CPU spinning
                time.sleep(0.1)

            except Exception as e:
                logger.error(f"❌ Error in background processing loop: {e}", exc_info=True)
                time.sleep(1.0)

        logger.info("🛑 Background processing loop stopped")

    def _calculate_similarity_hash(self, ask: Any) -> str:
        """Calculate similarity hash for ask"""
        if hasattr(ask, 'similarity_hash') and ask.similarity_hash:
            return ask.similarity_hash

        # Extract text
        if hasattr(ask, 'ask_text'):
            text = ask.ask_text
        elif isinstance(ask, dict):
            text = ask.get('ask_text', '')
        else:
            text = str(ask)

        # Normalize: lowercase, remove extra whitespace, extract key terms
        normalized = text.lower().strip()
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = [w for w in normalized.split() if w not in common_words and len(w) > 2]
        key_text = ' '.join(sorted(set(words)))  # Sorted unique words
        return hashlib.md5(key_text.encode()).hexdigest()

    def _get_ask_id(self, ask: Any) -> str:
        """Get ask ID from ask object"""
        if hasattr(ask, 'ask_id'):
            return ask.ask_id
        elif isinstance(ask, dict):
            return ask.get('ask_id', 'unknown')
        else:
            return 'unknown'

    def _create_batch(self, asks: List[Any], similarity_hash: str) -> Dict[str, Any]:
        """Create a batch from similar asks with context enhancements"""
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        # Determine task type (CPU-bound vs IO-bound)
        task_type = self._determine_task_type(asks)

        # Select @PEAK framework
        peak_framework = self._select_peak_framework(asks)

        # Determine subagent type if needed
        subagent_type = self._determine_subagent_type(asks)

        # #DECISIONING - Use decision tree for routing
        decision_context = None
        decision_outcome = None
        if self.decisioning_available and decide:
            try:
                decision_context = DecisionContext(
                    action="process_batch",
                    context={
                        "batch_id": batch_id,
                        "ask_count": len(asks),
                        "task_type": task_type.value if isinstance(task_type, Enum) else task_type,
                        "framework": peak_framework
                    }
                )
                decision_outcome = decide("ask_batch_processing", decision_context)
            except Exception as e:
                logger.debug(f"   Decisioning error: {e}")

        # #TROUBLESHOOTING - Pre-flight checks
        troubleshooting_checks = None
        if self.troubleshooter:
            try:
                troubleshooting_checks = self._run_troubleshooting_checks(asks)
            except Exception as e:
                logger.debug(f"   Troubleshooting check error: {e}")

        # @REC - Generate recommendations
        recommendations = None
        if self.recommendations_enabled:
            recommendations = self._generate_recommendations(asks, task_type, peak_framework)

        # @DYNO - Performance testing flag
        needs_dyno_test = self._should_run_dyno_test(asks)

        # @DOIT - Check if should delegate to @DOIT
        should_doit = self._should_delegate_to_doit(asks)

        batch = {
            "batch_id": batch_id,
            "asks": asks,
            "similarity_hash": similarity_hash,
            "task_type": task_type.value if isinstance(task_type, Enum) else task_type,
            "peak_framework": peak_framework,
            "subagent_type": subagent_type,
            "created_at": datetime.now().isoformat(),
            "processing_started": None,
            "processing_completed": None,
            "results": [],
            # Context Enhancements
            "context_enhancements": {
                "@DYNO": {
                    "enabled": needs_dyno_test,
                    "needs_test": needs_dyno_test
                },
                "@BG": {
                    "background_mode": True,
                    "description": "Background batch parallel processing"
                },
                "@BAL": {
                    "load_balancing": self.load_balancing_enabled,
                    "balanced": True
                },
                "@REC": {
                    "recommendations": recommendations,
                    "enabled": self.recommendations_enabled
                },
                "#TROUBLESHOOTING": {
                    "checks": troubleshooting_checks,
                    "enabled": self.troubleshooter is not None
                },
                "#DECISIONING": {
                    "decision_context": decision_context.__dict__ if decision_context else None,
                    "decision_outcome": decision_outcome.__dict__ if decision_outcome else None,
                    "enabled": self.decisioning_available
                },
                "@DOIT": {
                    "should_delegate": should_doit,
                    "enabled": self.doit_executor is not None
                }
            }
        }

        return batch

    def _determine_task_type(self, asks: List[Any]) -> TaskType:
        """Determine if task is CPU-bound or IO-bound"""
        ask_texts = ' '.join([self._get_ask_text(a) for a in asks]).lower()

        # CPU-bound indicators
        cpu_keywords = ['process', 'calculate', 'compute', 'analyze', 'transform', 'generate', 'render']
        # IO-bound indicators
        io_keywords = ['fetch', 'download', 'upload', 'read', 'write', 'network', 'api', 'request', 'http']

        cpu_score = sum(1 for kw in cpu_keywords if kw in ask_texts)
        io_score = sum(1 for kw in io_keywords if kw in ask_texts)

        if cpu_score > io_score:
            return TaskType.CPU_BOUND
        elif io_score > cpu_score:
            return TaskType.IO_BOUND
        else:
            return TaskType.MIXED

    def _get_ask_text(self, ask: Any) -> str:
        """Get ask text from ask object"""
        if hasattr(ask, 'ask_text'):
            return ask.ask_text
        elif isinstance(ask, dict):
            return ask.get('ask_text', '')
        else:
            return str(ask)

    def _select_peak_framework(self, asks: List[Any]) -> str:
        """Select @PEAK framework for processing these asks"""
        ask_texts = ' '.join([self._get_ask_text(a) for a in asks]).lower()

        # @PEAK Framework Selection Logic
        if 'docker' in ask_texts or 'container' in ask_texts:
            return "docker"
        elif 'voice' in ask_texts or 'tts' in ask_texts or 'elevenlabs' in ask_texts:
            return "elevenlabs"
        elif 'rdp' in ask_texts or 'remote' in ask_texts or 'manus' in ask_texts:
            return "manus"
        elif 'mcp' in ask_texts or 'model context' in ask_texts:
            return "mcp"
        else:
            return "local"  # Default

    def _determine_subagent_type(self, asks: List[Any]) -> Optional[str]:
        """Determine subagent type for delegation"""
        ask_texts = ' '.join([self._get_ask_text(a) for a in asks]).lower()

        # Map to subagent types
        if 'illumination' in ask_texts or 'lesson' in ask_texts:
            return "illumination"
        elif 'multimedia' in ask_texts or 'youtube' in ask_texts:
            return "multimedia"
        elif 'code' in ask_texts or 'quality' in ask_texts:
            return "code_quality"
        elif 'storytelling' in ask_texts:
            return "storytelling"
        else:
            return None

    def _process_batches_parallel_enhanced(self, batches: List[Dict[str, Any]]):
        """Process multiple batches in parallel using MULTITHREADING & MULTIPROCESSING"""
        logger.info(f"🚀 Processing {len(batches)} batches in parallel (MULTITHREAD & MULTIPROCESS)")

        # Separate batches by task type
        cpu_batches = [b for b in batches if b.get('task_type') == TaskType.CPU_BOUND.value]
        io_batches = [b for b in batches if b.get('task_type') == TaskType.IO_BOUND.value]
        mixed_batches = [b for b in batches if b.get('task_type') == TaskType.MIXED.value]

        # Process CPU-bound batches with multiprocessing
        if cpu_batches:
            logger.info(f"   🔧 Processing {len(cpu_batches)} CPU-bound batches (MULTIPROCESS)")
            with ProcessPoolExecutor(max_workers=min(len(cpu_batches), self.current_workers_processes)) as executor:
                futures = {
                    executor.submit(self._process_batch, batch): batch
                    for batch in cpu_batches
                }
                self._wait_for_futures(futures)

        # Process IO-bound batches with multithreading
        if io_batches:
            logger.info(f"   📡 Processing {len(io_batches)} IO-bound batches (MULTITHREAD)")
            with ThreadPoolExecutor(max_workers=min(len(io_batches), self.current_workers_threads)) as executor:
                futures = {
                    executor.submit(self._process_batch, batch): batch
                    for batch in io_batches
                }
                self._wait_for_futures(futures)

        # Process mixed batches with hybrid approach
        if mixed_batches:
            logger.info(f"   🔀 Processing {len(mixed_batches)} mixed batches (HYBRID)")
            # Use threading for mixed (can be optimized later)
            with ThreadPoolExecutor(max_workers=min(len(mixed_batches), self.current_workers_threads)) as executor:
                futures = {
                    executor.submit(self._process_batch, batch): batch
                    for batch in mixed_batches
                }
                self._wait_for_futures(futures)

    def _wait_for_futures(self, futures: Dict):
        """Wait for futures and handle results"""
        for future in as_completed(futures):
            batch = futures[future]
            try:
                result = future.result()
                batch["results"] = result
                batch["processing_completed"] = datetime.now().isoformat()
                logger.info(f"   ✅ Batch completed: {batch['batch_id']}")
            except Exception as e:
                logger.error(f"   ❌ Batch failed: {batch['batch_id']} - {e}")
                batch["results"] = [{"success": False, "error": str(e)}]

    def _process_batch(self, batch: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process a single batch of asks with context enhancements"""
        batch["processing_started"] = datetime.now().isoformat()
        logger.info(f"   🔄 Processing batch: {batch['batch_id']} ({len(batch['asks'])} asks, framework: {batch['peak_framework']})")

        # @DOIT - Delegate to @DOIT if needed
        context = batch.get("context_enhancements", {})
        if context.get("@DOIT", {}).get("should_delegate") and self.doit_executor:
            logger.info("   🚀 Delegating to @DOIT for autonomous execution")
            try:
                # Convert asks to @DOIT format
                doit_result = self._delegate_to_doit(batch)
                if doit_result.get("success"):
                    return doit_result.get("results", [])
            except Exception as e:
                logger.warning(f"   ⚠️  @DOIT delegation failed: {e}, falling back to normal processing")

        # @DYNO - Run performance test if needed
        if context.get("@DYNO", {}).get("needs_test") and self.dyno_tuner:
            logger.info("   📊 Running @DYNO performance test")
            try:
                dyno_result = self._run_dyno_test(batch)
                batch["dyno_results"] = dyno_result
            except Exception as e:
                logger.warning(f"   ⚠️  @DYNO test failed: {e}")

        results = []

        # Process each ask in the batch
        for ask in batch["asks"]:
            try:
                # #TROUBLESHOOTING - Pre-flight troubleshooting
                troubleshooting = context.get("#TROUBLESHOOTING", {})
                if troubleshooting.get("checks") and self.troubleshooter:
                    troubleshoot_result = self._apply_troubleshooting(ask, troubleshooting["checks"])
                    if troubleshoot_result.get("should_skip"):
                        logger.info(f"      ⚠️  Skipping ask {self._get_ask_id(ask)} due to troubleshooting")
                        results.append({
                            "ask_id": self._get_ask_id(ask),
                            "success": False,
                            "skipped": True,
                            "reason": troubleshoot_result.get("reason", "Troubleshooting check failed")
                        })
                        continue

                # #DECISIONING - Use decision tree for routing
                decisioning = context.get("#DECISIONING", {})
                if decisioning.get("decision_outcome") and self.decisioning_available:
                    routing = self._apply_decisioning_routing(ask, decisioning["decision_outcome"])
                    if routing.get("should_route"):
                        result = self._route_via_decisioning(ask, routing)
                    else:
                        # Normal processing
                        if batch.get("subagent_type") and self.subagent_delegation:
                            result = self._delegate_to_subagent(ask, batch["subagent_type"])
                        else:
                            result = self._process_ask_with_peak_framework(ask, batch["peak_framework"])
                else:
                    # Normal processing
                    if batch.get("subagent_type") and self.subagent_delegation:
                        result = self._delegate_to_subagent(ask, batch["subagent_type"])
                    else:
                        result = self._process_ask_with_peak_framework(ask, batch["peak_framework"])

                # @REC - Add recommendations to result
                if self.recommendations_enabled and context.get("@REC", {}).get("recommendations"):
                    result["recommendations"] = context["@REC"]["recommendations"]

                ask_id = self._get_ask_id(ask)
                result["ask_id"] = ask_id
                result["batch_id"] = batch["batch_id"]
                results.append(result)

            except Exception as e:
                logger.error(f"   ❌ Error processing ask {self._get_ask_id(ask)}: {e}")
                # #TROUBLESHOOTING - Troubleshoot the error
                if self.troubleshooter:
                    troubleshoot_error = self._troubleshoot_error(ask, e)
                    results.append({
                        "ask_id": self._get_ask_id(ask),
                        "success": False,
                        "error": str(e),
                        "troubleshooting": troubleshoot_error
                    })
                else:
                    results.append({
                        "ask_id": self._get_ask_id(ask),
                        "success": False,
                        "error": str(e)
                    })

        return results

    def _delegate_to_subagent(self, ask: Any, subagent_type: str) -> Dict[str, Any]:
        """Delegate ask to appropriate subagent"""
        if not self.subagent_delegation:
            return {"success": False, "error": "Subagent delegation not available"}

        task = {
            "task_id": self._get_ask_id(ask),
            "title": self._get_ask_text(ask),
            "metadata": self._get_ask_metadata(ask)
        }

        # Map subagent type to AgentDomain
        domain_map = {
            "illumination": AgentDomain.ILLUMINATION if AgentDomain else None,
            "multimedia": AgentDomain.MULTIMEDIA if AgentDomain else None,
            "code_quality": AgentDomain.CODE_QUALITY if AgentDomain else None,
            "storytelling": AgentDomain.STORYTELLING if AgentDomain else None,
        }

        domain = domain_map.get(subagent_type)
        if domain:
            return self.subagent_delegation.delegate_task(task, domain)
        else:
            return {"success": False, "error": f"Unknown subagent type: {subagent_type}"}

    def _get_ask_metadata(self, ask: Any) -> Dict[str, Any]:
        """Get metadata from ask object"""
        if hasattr(ask, 'metadata'):
            return ask.metadata
        elif isinstance(ask, dict):
            return ask.get('metadata', {})
        else:
            return {}

    def _process_ask_with_peak_framework(self, ask: Any, framework: str) -> Dict[str, Any]:
        """Process ask using @PEAK framework"""
        logger.debug(f"      📏 @PEAK Framework: {framework} for ask {self._get_ask_id(ask)}")

        # Use @PEAK Agent Management to select and execute
        if self.peak_agent_mgmt:
            try:
                # Create agent definition for this ask
                agent_id = f"ask_agent_{self._get_ask_id(ask)}"
                ask_text = self._get_ask_text(ask)

                # Map framework to AgentType
                agent_type_map = {
                    "docker": AgentType.DOCKER if AgentType else None,
                    "elevenlabs": AgentType.ELEVENLABS if AgentType else None,
                    "manus": AgentType.MANUS if AgentType else None,
                    "mcp": AgentType.MCP if AgentType else None,
                    "local": AgentType.LOCAL if AgentType else None,
                }

                agent_type = agent_type_map.get(framework, AgentType.LOCAL if AgentType else None)

                if agent_type:
                    # Deploy and execute agent
                    result = self.peak_agent_mgmt.deploy_agent(
                        agent_id=agent_id,
                        agent_type=agent_type,
                        command=ask_text
                    )
                    return {"success": True, "result": result, "framework": framework}
                else:
                    return {"success": False, "error": f"Unknown framework: {framework}"}

            except Exception as e:
                logger.error(f"      ❌ Error processing with @PEAK framework: {e}")
                return {"success": False, "error": str(e)}
        else:
            # Fallback: simple processing
            return {"success": True, "result": f"Processed: {self._get_ask_text(ask)}", "framework": framework}

    def _should_run_dyno_test(self, asks: List[Any]) -> bool:
        """Determine if @DYNO performance test should run"""
        if not self.dyno_tuner:
            return False

        ask_texts = ' '.join([self._get_ask_text(a) for a in asks]).lower()

        # Run @DYNO for performance-critical tasks
        dyno_keywords = ['performance', 'optimize', 'tune', 'speed', 'fast', 'slow', 'bottleneck', 'dyno']
        return any(kw in ask_texts for kw in dyno_keywords)

    def _should_delegate_to_doit(self, asks: List[Any]) -> bool:
        """Determine if should delegate to @DOIT"""
        if not self.doit_executor:
            return False

        ask_texts = ' '.join([self._get_ask_text(a) for a in asks]).lower()

        # Delegate to @DOIT for autonomous execution tasks
        doit_keywords = ['doit', 'autonomous', 'execute all', 'full autonomy', 'proceed', 'continue']
        return any(kw in ask_texts for kw in doit_keywords)

    def _run_dyno_test(self, batch: Dict[str, Any]) -> Dict[str, Any]:
        """Run @DYNO performance test on batch"""
        if not self.dyno_tuner:
            return {"success": False, "error": "@DYNO not available"}

        try:
            # Create test configuration
            test_config = {
                "test_name": f"batch_{batch['batch_id']}",
                "concurrent_sessions": len(batch['asks']),
                "asks": batch['asks']
            }

            # Run @DYNO test
            result = self.dyno_tuner.run_dyno_test(test_config)
            return {"success": True, "dyno_result": result}
        except Exception as e:
            logger.error(f"   ❌ @DYNO test error: {e}")
            return {"success": False, "error": str(e)}

    def _delegate_to_doit(self, batch: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate batch to @DOIT for autonomous execution"""
        if not self.doit_executor:
            return {"success": False, "error": "@DOIT not available"}

        try:
            # Convert batch to @DOIT format
            # @DOIT expects workflow/task format
            results = []
            for ask in batch['asks']:
                ask_text = self._get_ask_text(ask)
                # Execute via @DOIT
                doit_result = self.doit_executor.doit(use_triage=True)
                results.append({
                    "ask_id": self._get_ask_id(ask),
                    "doit_result": doit_result,
                    "success": doit_result.get("success", False)
                })

            return {"success": True, "results": results}
        except Exception as e:
            logger.error(f"   ❌ @DOIT delegation error: {e}")
            return {"success": False, "error": str(e), "results": []}

    def _run_troubleshooting_checks(self, asks: List[Any]) -> Dict[str, Any]:
        """Run #TROUBLESHOOTING pre-flight checks"""
        if not self.troubleshooter:
            return {"enabled": False}

        try:
            checks = {
                "enabled": True,
                "checks": []
            }

            for ask in asks:
                ask_text = self._get_ask_text(ask)
                # Run troubleshooting check
                check_result = self.troubleshooter.diagnose_workflow(ask_text)
                checks["checks"].append({
                    "ask_id": self._get_ask_id(ask),
                    "check_result": check_result
                })

            return checks
        except Exception as e:
            logger.debug(f"   Troubleshooting check error: {e}")
            return {"enabled": True, "error": str(e)}

    def _apply_troubleshooting(self, ask: Any, troubleshooting_checks: Dict[str, Any]) -> Dict[str, Any]:
        """Apply troubleshooting checks to ask"""
        if not troubleshooting_checks.get("enabled"):
            return {"should_skip": False}

        # Check if any checks indicate we should skip
        checks = troubleshooting_checks.get("checks", [])
        for check in checks:
            if check.get("ask_id") == self._get_ask_id(ask):
                check_result = check.get("check_result", {})
                if check_result.get("critical_issue"):
                    return {
                        "should_skip": True,
                        "reason": check_result.get("issue_description", "Critical issue detected")
                    }

        return {"should_skip": False}

    def _troubleshoot_error(self, ask: Any, error: Exception) -> Dict[str, Any]:
        """Troubleshoot an error that occurred"""
        if not self.troubleshooter:
            return {"enabled": False}

        try:
            ask_text = self._get_ask_text(ask)
            troubleshoot_result = self.troubleshooter.diagnose_error(ask_text, str(error))
            return {
                "enabled": True,
                "troubleshoot_result": troubleshoot_result
            }
        except Exception as e:
            return {"enabled": True, "error": str(e)}

    def _generate_recommendations(self, asks: List[Any], task_type: TaskType, framework: str) -> List[str]:
        """Generate @REC recommendations for batch"""
        recommendations = []

        # Framework recommendations
        if framework == "local" and len(asks) > 10:
            recommendations.append("Consider using Docker for better isolation with large batches")

        # Task type recommendations
        if task_type == TaskType.CPU_BOUND:
            recommendations.append("CPU-bound task detected - using multiprocessing for optimal performance")
        elif task_type == TaskType.IO_BOUND:
            recommendations.append("IO-bound task detected - using multithreading for optimal performance")

        # Batch size recommendations
        if len(asks) > 20:
            recommendations.append("Large batch detected - consider splitting for better resource management")

        # Resource recommendations
        cpu_percent = psutil.cpu_percent(interval=0.1)
        if cpu_percent > 80:
            recommendations.append("High CPU usage detected - consider reducing batch size or delaying processing")

        return recommendations

    def _apply_decisioning_routing(self, ask: Any, decision_outcome: Any) -> Dict[str, Any]:
        """Apply #DECISIONING routing decision"""
        if not decision_outcome:
            return {"should_route": False}

        # Check decision outcome
        if hasattr(decision_outcome, 'should_route'):
            return {"should_route": decision_outcome.should_route, "route": decision_outcome.route}
        elif isinstance(decision_outcome, dict):
            return {"should_route": decision_outcome.get("should_route", False), "route": decision_outcome.get("route")}
        else:
            return {"should_route": False}

    def _route_via_decisioning(self, ask: Any, routing: Dict[str, Any]) -> Dict[str, Any]:
        """Route ask via #DECISIONING decision tree"""
        route = routing.get("route")
        if route:
            # Route to appropriate handler based on decision
            logger.debug(f"      🧠 Routing via #DECISIONING: {route}")
            return {
                "success": True,
                "routed": True,
                "route": route,
                "result": f"Routed via decisioning to: {route}"
            }
        else:
            # Fallback to normal processing
            return self._process_ask_with_peak_framework(ask, "local")

    def stop_processing(self):
        """Stop background processing"""
        with self.processing_lock:
            self.is_processing = False
        logger.info("🛑 Background processing stopped")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Enhanced Automatic Parallel @ASK Processor")
    parser.add_argument("--test", action="store_true", help="Test with sample asks")
    parser.add_argument("--add", type=str, help="Add a single ask")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("🚀 Enhanced Automatic Parallel @ASK Batch Processor")
    print("   AUTOMATIC BACKGROUND BATCH PARALLEL PROCESSING")
    print("   MULTITHREAD & MULTIPROCESS")
    print("="*80 + "\n")

    processor = EnhancedAutomaticParallelAskProcessor()

    if args.test:
        # Test with multiple similar asks
        print("📥 Adding test asks...")
        processor.add_ask("Process video file", "test")
        processor.add_ask("Process video file", "test")
        processor.add_ask("Process video file", "test")
        processor.add_ask("Calculate statistics", "test")
        processor.add_ask("Calculate statistics", "test")

        print("✅ Test asks added - processing in background...")
        print("   (Wait a few seconds for batch processing)")
        time.sleep(10)

        processor.stop_processing()
        print("\n✅ Test complete")

    elif args.add:
        processor.add_ask(args.add, "cli")
        print(f"✅ Added ask: {args.add}")
        print("   Processing in background...")
        time.sleep(5)
        processor.stop_processing()

    else:
        print("Use --test for test mode or --add 'ask text' to add an ask")
        print("="*80 + "\n")
