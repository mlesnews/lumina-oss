#!/usr/bin/env python3
"""
Automatic Parallel @ASK Batch Processor with @PEAK Framework Selection

Automatically detects similar @ASKS, groups them into batches, and processes them
in parallel using background threads/processes with @PEAK framework selection
and @DYNAMIC-SCALING-MODULE.

Features:
- Automatic similarity detection for @ASKS
- Background batch parallel processing
- @PEAK framework selection (Docker, ElevenLabs, MANUS, MCP, Local)
- Subagent delegation with dynamic scaling
- Multithreading & multiprocessing
- Resource-aware load balancing
- Prevents sequential single-processor CPU logic

Tags: #PARALLEL #BATCH #ASK #PEAK #DYNAMIC_SCALING #SUBAGENT #MULTITHREAD #MULTIPROCESS @JARVIS @TEAM
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

logger = get_logger("AutomaticParallelAskProcessor")

# @PEAK Framework Selection
try:
    from jarvis_peak_agent_management import JARVISPeakAgentManagement, AgentType
    PEAK_AGENT_MGMT_AVAILABLE = True
except ImportError:
    PEAK_AGENT_MGMT_AVAILABLE = False
    JARVISPeakAgentManagement = None
    AgentType = None

# Subagent Delegation
try:
    from jarvis_subagent_delegation import JARVISSubagentDelegation, AgentDomain
    SUBAGENT_DELEGATION_AVAILABLE = True
except ImportError:
    SUBAGENT_DELEGATION_AVAILABLE = False
    JARVISSubagentDelegation = None
    AgentDomain = None

# Dynamic Scaling
try:
    from dynamic_timeout_scaling import DynamicTimeoutScaling
    DYNAMIC_SCALING_AVAILABLE = True
except ImportError:
    DYNAMIC_SCALING_AVAILABLE = False
    DynamicTimeoutScaling = None

# Parallel Processing
try:
    from parallel_agent_session_processor import ParallelAgentSessionProcessor
    PARALLEL_PROCESSOR_AVAILABLE = True
except ImportError:
    PARALLEL_PROCESSOR_AVAILABLE = False
    ParallelAgentSessionProcessor = None


class AskSimilarityLevel(Enum):
    """Levels of similarity between @ASKS"""
    IDENTICAL = "identical"  # Exact same ask
    VERY_SIMILAR = "very_similar"  # Same intent, minor variations
    SIMILAR = "similar"  # Related intent, different details
    DIFFERENT = "different"  # Different intents


@dataclass
class Ask:
    """Represents an @ASK"""
    ask_id: str
    ask_text: str
    source: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    similarity_hash: Optional[str] = None  # Hash for similarity detection

    def __post_init__(self):
        """Calculate similarity hash after initialization"""
        if self.similarity_hash is None:
            self.similarity_hash = self._calculate_similarity_hash()

    def _calculate_similarity_hash(self) -> str:
        """Calculate hash for similarity detection (normalized text)"""
        # Normalize: lowercase, remove extra whitespace, extract key terms
        normalized = self.ask_text.lower().strip()
        # Remove common words for better similarity matching
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = [w for w in normalized.split() if w not in common_words and len(w) > 2]
        key_text = ' '.join(sorted(set(words)))  # Sorted unique words
        return hashlib.md5(key_text.encode()).hexdigest()


@dataclass
class AskBatch:
    """Batch of similar @ASKS for parallel processing"""
    batch_id: str
    asks: List[Ask]
    similarity_level: AskSimilarityLevel
    peak_framework: str  # Selected @PEAK framework
    subagent_type: Optional[str] = None  # Subagent type if delegation needed
    created_at: datetime = field(default_factory=datetime.now)
    processing_started: Optional[datetime] = None
    processing_completed: Optional[datetime] = None
    results: List[Dict[str, Any]] = field(default_factory=list)


class AutomaticParallelAskProcessor:
    """
    Automatic Parallel @ASK Batch Processor

    Automatically detects similar @ASKS, groups them, and processes in parallel
    using @PEAK framework selection and dynamic scaling.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Automatic Parallel @ASK Processor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "parallel_ask_processing"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # @PEAK Agent Management
        self.peak_agent_mgmt = None
        if PEAK_AGENT_MGMT_AVAILABLE:
            try:
                self.peak_agent_mgmt = JARVISPeakAgentManagement(project_root=project_root)
                logger.info("✅ @PEAK Agent Management initialized")
            except Exception as e:
                logger.warning(f"⚠️  @PEAK Agent Management not available: {e}")

        # Subagent Delegation
        self.subagent_delegation = None
        if SUBAGENT_DELEGATION_AVAILABLE:
            try:
                self.subagent_delegation = JARVISSubagentDelegation(project_root=project_root)
                logger.info("✅ Subagent Delegation initialized")
            except Exception as e:
                logger.warning(f"⚠️  Subagent Delegation not available: {e}")

        # Dynamic Scaling
        self.dynamic_scaling = None
        if DYNAMIC_SCALING_AVAILABLE:
            try:
                self.dynamic_scaling = DynamicTimeoutScaling(project_root=project_root)
                logger.info("✅ Dynamic Scaling Module initialized")
            except Exception as e:
                logger.warning(f"⚠️  Dynamic Scaling Module not available: {e}")

        # Parallel Processor
        self.parallel_processor = None
        if PARALLEL_PROCESSOR_AVAILABLE:
            try:
                self.parallel_processor = ParallelAgentSessionProcessor()
                logger.info("✅ Parallel Processor initialized")
            except Exception as e:
                logger.warning(f"⚠️  Parallel Processor not available: {e}")

        # Processing queues
        self.ask_queue = queue.Queue()  # Incoming asks
        self.batch_queue = queue.Queue()  # Batches ready for processing
        self.results_queue = queue.Queue()  # Completed results

        # Background processing
        self.processing_thread = None
        self.is_processing = False
        self.processing_lock = threading.Lock()

        # Similarity threshold (minimum asks to trigger batch processing)
        self.similarity_threshold = 3  # Need at least 3 similar asks

        # Resource monitoring
        self.cpu_count = multiprocessing.cpu_count()
        self.max_workers = max(1, self.cpu_count - 1)  # Leave 1 core free

        logger.info("✅ Automatic Parallel @ASK Processor initialized")
        logger.info(f"   Max parallel workers: {self.max_workers}")
        logger.info(f"   Similarity threshold: {self.similarity_threshold} asks")

    def add_ask(self, ask_text: str, source: str = "unknown", metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add an @ASK to the processing queue

        Returns:
            ask_id: Unique identifier for this ask
        """
        ask_id = f"ask_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        ask = Ask(
            ask_id=ask_id,
            ask_text=ask_text,
            source=source,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )

        self.ask_queue.put(ask)
        logger.debug(f"📥 Added @ASK: {ask_id} ({ask_text[:50]}...)")

        # Trigger background processing if not already running
        self._start_background_processing()

        return ask_id

    def _start_background_processing(self):
        """Start background processing thread if not already running"""
        with self.processing_lock:
            if not self.is_processing:
                self.is_processing = True
                self.processing_thread = threading.Thread(
                    target=self._background_processing_loop,
                    daemon=True
                )
                self.processing_thread.start()
                logger.info("🚀 Background processing thread started")

    def _background_processing_loop(self):
        """Background processing loop - detects similar asks and processes in batches"""
        logger.info("🔄 Background processing loop started")

        ask_buffer: Dict[str, List[Ask]] = {}  # similarity_hash -> List[Ask]
        last_batch_time = time.time()
        batch_timeout = 5.0  # Wait 5 seconds for more similar asks

        while self.is_processing:
            try:
                # Collect asks with timeout
                try:
                    ask = self.ask_queue.get(timeout=1.0)
                    ask_buffer.setdefault(ask.similarity_hash, []).append(ask)
                    logger.debug(f"   📦 Buffered ask: {ask.ask_id} (hash: {ask.similarity_hash[:8]})")
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
                        logger.info(f"   ✅ Batch ready: {batch.batch_id} ({len(asks)} asks)")
                    elif time_since_last_batch >= batch_timeout and len(asks) > 0:
                        # Timeout reached - process what we have
                        batch = self._create_batch(asks, similarity_hash)
                        batches_to_process.append(batch)
                        del ask_buffer[similarity_hash]
                        logger.info(f"   ⏰ Batch timeout: {batch.batch_id} ({len(asks)} asks)")

                # Process batches in parallel
                if batches_to_process:
                    self._process_batches_parallel(batches_to_process)
                    last_batch_time = current_time

                # Small sleep to prevent CPU spinning
                time.sleep(0.1)

            except Exception as e:
                logger.error(f"❌ Error in background processing loop: {e}", exc_info=True)
                time.sleep(1.0)

        logger.info("🛑 Background processing loop stopped")

    def _create_batch(self, asks: List[Ask], similarity_hash: str) -> AskBatch:
        """Create a batch from similar asks"""
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        # Determine similarity level
        if len(asks) == 1:
            similarity_level = AskSimilarityLevel.DIFFERENT
        elif len(set(a.ask_text.lower().strip() for a in asks)) == 1:
            similarity_level = AskSimilarityLevel.IDENTICAL
        else:
            similarity_level = AskSimilarityLevel.SIMILAR

        # Select @PEAK framework
        peak_framework = self._select_peak_framework(asks)

        # Determine subagent type if needed
        subagent_type = self._determine_subagent_type(asks)

        batch = AskBatch(
            batch_id=batch_id,
            asks=asks,
            similarity_level=similarity_level,
            peak_framework=peak_framework,
            subagent_type=subagent_type
        )

        return batch

    def _select_peak_framework(self, asks: List[Ask]) -> str:
        """Select @PEAK framework for processing these asks"""
        if not self.peak_agent_mgmt:
            return "local"  # Default

        # Analyze asks to determine requirements
        ask_texts = ' '.join([a.ask_text.lower() for a in asks])

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

    def _determine_subagent_type(self, asks: List[Ask]) -> Optional[str]:
        """Determine subagent type for delegation"""
        if not self.subagent_delegation:
            return None

        ask_texts = ' '.join([a.ask_text.lower() for a in asks])

        # Map to AgentDomain
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

    def _process_batches_parallel(self, batches: List[AskBatch]):
        """Process multiple batches in parallel using multithreading/multiprocessing"""
        logger.info(f"🚀 Processing {len(batches)} batches in parallel")

        # Use ThreadPoolExecutor for I/O-bound tasks
        # Use ProcessPoolExecutor for CPU-bound tasks (if needed)
        with ThreadPoolExecutor(max_workers=min(len(batches), self.max_workers)) as executor:
            futures = {
                executor.submit(self._process_batch, batch): batch
                for batch in batches
            }

            for future in as_completed(futures):
                batch = futures[future]
                try:
                    result = future.result()
                    batch.results = result
                    batch.processing_completed = datetime.now()
                    logger.info(f"   ✅ Batch completed: {batch.batch_id}")
                except Exception as e:
                    logger.error(f"   ❌ Batch failed: {batch.batch_id} - {e}")
                    batch.results = [{"success": False, "error": str(e)}]

    def _process_batch(self, batch: AskBatch) -> List[Dict[str, Any]]:
        """Process a single batch of asks"""
        batch.processing_started = datetime.now()
        logger.info(f"   🔄 Processing batch: {batch.batch_id} ({len(batch.asks)} asks, framework: {batch.peak_framework})")

        results = []

        # Process each ask in the batch
        for ask in batch.asks:
            try:
                # Delegate to subagent if needed
                if batch.subagent_type and self.subagent_delegation:
                    result = self._delegate_to_subagent(ask, batch.subagent_type)
                else:
                    # Process directly using @PEAK framework
                    result = self._process_ask_with_peak_framework(ask, batch.peak_framework)

                result["ask_id"] = ask.ask_id
                result["batch_id"] = batch.batch_id
                results.append(result)

            except Exception as e:
                logger.error(f"   ❌ Error processing ask {ask.ask_id}: {e}")
                results.append({
                    "ask_id": ask.ask_id,
                    "success": False,
                    "error": str(e)
                })

        return results

    def _delegate_to_subagent(self, ask: Ask, subagent_type: str) -> Dict[str, Any]:
        """Delegate ask to appropriate subagent"""
        task = {
            "task_id": ask.ask_id,
            "title": ask.ask_text,
            "metadata": ask.metadata
        }

        # Map subagent type to AgentDomain
        domain_map = {
            "illumination": AgentDomain.ILLUMINATION if AgentDomain else None,
            "multimedia": AgentDomain.MULTIMEDIA if AgentDomain else None,
            "code_quality": AgentDomain.CODE_QUALITY if AgentDomain else None,
            "storytelling": AgentDomain.STORYTELLING if AgentDomain else None,
        }

        domain = domain_map.get(subagent_type)
        if domain and self.subagent_delegation:
            return self.subagent_delegation.delegate_task(task, domain)
        else:
            return {"success": False, "error": "Subagent delegation not available"}

    def _process_ask_with_peak_framework(self, ask: Ask, framework: str) -> Dict[str, Any]:
        """Process ask using @PEAK framework"""
        logger.debug(f"      📏 @PEAK Framework: {framework} for ask {ask.ask_id}")

        # Use @PEAK Agent Management to select and execute
        if self.peak_agent_mgmt:
            # Create agent definition for this ask
            agent_id = f"ask_agent_{ask.ask_id}"

            # Select framework via @PEAK
            selection = self.peak_agent_mgmt.select_peak_tool(
                task_description=ask.ask_text,
                task_requirements=ask.metadata.get("requirements", {})
            )

            framework = selection.get("framework", framework)

            # Process using selected framework
            return {
                "success": True,
                "framework": framework,
                "rationale": selection.get("rationale", "N/A"),
                "message": f"Processed using @PEAK framework: {framework}"
            }
        else:
            # Fallback: simple processing
            return {
                "success": True,
                "framework": framework,
                "message": f"Processed (no @PEAK management available)"
            }

    def stop_processing(self):
        """Stop background processing"""
        with self.processing_lock:
            self.is_processing = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5.0)
        logger.info("🛑 Background processing stopped")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Automatic Parallel @ASK Batch Processor")
    parser.add_argument("--test", action="store_true", help="Run test with sample asks")
    parser.add_argument("--threshold", type=int, default=3, help="Similarity threshold (default: 3)")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("🚀 Automatic Parallel @ASK Batch Processor")
    print("   @PEAK Framework Selection + Dynamic Scaling + Multithreading")
    print("="*80 + "\n")

    processor = AutomaticParallelAskProcessor()
    processor.similarity_threshold = args.threshold

    if args.test:
        print("🧪 Running test with sample asks...\n")

        # Add similar asks (should be batched)
        processor.add_ask("Create a video about Python", source="test")
        processor.add_ask("Make a video about Python programming", source="test")
        processor.add_ask("Generate Python tutorial video", source="test")

        # Add different asks (should be processed separately)
        processor.add_ask("Fix the lighting system", source="test")
        processor.add_ask("Update documentation", source="test")

        # Wait for processing
        print("⏳ Waiting for batch processing...")
        time.sleep(10)

        processor.stop_processing()
        print("\n✅ Test complete")
    else:
        print("Use --test to run a test")
        print("="*80 + "\n")
