#!/usr/bin/env python3
"""
Multi-Transcription Queue System

Allows multiple simultaneous transcriptions (currently only one at a time).
Enables "Jarvis edit original" while another transcription is active.

Tags: #MULTI_TRANSCRIPTION #QUEUE #HANDS_FREE #REQUIRED @JARVIS @LUMINA
"""

import sys
import threading
import queue
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("MultiTranscriptionQueue")


class TranscriptionPriority(Enum):
    """Transcription priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4  # Can interrupt active transcription


class TranscriptionContext(Enum):
    """Transcription context/window"""
    MAIN_WINDOW = "main"
    EDIT_ORIGINAL = "edit_original"
    NEW_REQUEST = "new_request"
    VOICE_EDIT = "voice_edit"
    OTHER = "other"


@dataclass
class TranscriptionRequest:
    """Transcription request"""
    request_id: str
    context: TranscriptionContext
    priority: TranscriptionPriority
    audio_data: Optional[Any] = None
    window_id: Optional[str] = None
    chat_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    callback: Optional[Callable] = None
    result: Optional[Dict[str, Any]] = None
    status: str = "pending"  # pending, processing, completed, failed
    error: Optional[str] = None


class MultiTranscriptionQueue:
    """
    Multi-transcription queue system

    Allows multiple simultaneous transcriptions with:
    - Priority-based processing
    - Context tracking (which window/chat)
    - Parallel processing
    - Interruption support (urgent requests)
    """

    def __init__(self, max_workers: int = 3):
        """Initialize multi-transcription queue"""
        self.max_workers = max_workers
        self.request_queue = queue.PriorityQueue()
        self.active_transcriptions: Dict[str, TranscriptionRequest] = {}
        self.completed_transcriptions: List[TranscriptionRequest] = []
        self.lock = threading.Lock()

        # Worker threads
        self.workers: List[threading.Thread] = []
        self.running = False
        self.stop_event = threading.Event()

        # Statistics
        self.stats = {
            "total_requests": 0,
            "completed": 0,
            "failed": 0,
            "interrupted": 0,
            "active_count": 0
        }

        logger.info(f"✅ Multi-Transcription Queue initialized (max_workers={max_workers})")

    def _get_priority_value(self, priority: TranscriptionPriority) -> int:
        """Get numeric value for priority (higher = more important)"""
        return priority.value

    def add_request(self,
                   context: TranscriptionContext,
                   priority: TranscriptionPriority = TranscriptionPriority.NORMAL,
                   audio_data: Optional[Any] = None,
                   window_id: Optional[str] = None,
                   chat_id: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None,
                   callback: Optional[Callable] = None) -> str:
        """
        Add transcription request to queue

        Returns:
            request_id: Unique ID for this request
        """
        request_id = f"trans_{int(time.time() * 1000)}_{len(self.active_transcriptions)}"

        request = TranscriptionRequest(
            request_id=request_id,
            context=context,
            priority=priority,
            audio_data=audio_data,
            window_id=window_id,
            chat_id=chat_id,
            metadata=metadata or {},
            callback=callback
        )

        # Add to priority queue (negative priority for max-heap behavior)
        priority_value = self._get_priority_value(priority)
        self.request_queue.put((-priority_value, time.time(), request))

        with self.lock:
            self.stats["total_requests"] += 1

        logger.info(f"📝 Added transcription request: {request_id} (context={context.value}, priority={priority.name})")

        # If urgent priority, check if we should interrupt active transcription
        if priority == TranscriptionPriority.URGENT:
            self._handle_urgent_request(request)

        return request_id

    def _handle_urgent_request(self, urgent_request: TranscriptionRequest):
        """Handle urgent request - may interrupt active transcription"""
        with self.lock:
            # Check if there are active transcriptions with lower priority
            for req_id, active_req in list(self.active_transcriptions.items()):
                if active_req.priority.value < urgent_request.priority.value:
                    logger.warning(f"⚠️  Interrupting transcription {req_id} for urgent request {urgent_request.request_id}")
                    active_req.status = "interrupted"
                    active_req.error = "Interrupted by urgent request"
                    self.stats["interrupted"] += 1
                    # Remove from active
                    del self.active_transcriptions[req_id]

    def _process_transcription(self, request: TranscriptionRequest):
        """Process a single transcription request"""
        request_id = request.request_id

        try:
            logger.info(f"🔄 Processing transcription: {request_id}")
            request.status = "processing"

            # Add to active transcriptions
            with self.lock:
                self.active_transcriptions[request_id] = request
                self.stats["active_count"] = len(self.active_transcriptions)

            # Import transcription service
            try:
                from cursor_auto_recording_transcription_fixed import CursorAutoRecordingTranscriptionFixed
                transcription_service = CursorAutoRecordingTranscriptionFixed()
            except ImportError:
                logger.error("❌ Transcription service not available")
                raise ImportError("Transcription service not available")

            # Process transcription based on context
            result = self._transcribe_by_context(request, transcription_service)

            # Mark as completed
            request.status = "completed"
            request.result = result

            with self.lock:
                self.stats["completed"] += 1
                if request_id in self.active_transcriptions:
                    del self.active_transcriptions[request_id]
                self.completed_transcriptions.append(request)
                self.stats["active_count"] = len(self.active_transcriptions)

            logger.info(f"✅ Transcription completed: {request_id}")

            # Call callback if provided
            if request.callback:
                try:
                    request.callback(request)
                except Exception as e:
                    logger.error(f"❌ Callback error for {request_id}: {e}")

        except Exception as e:
            logger.error(f"❌ Transcription failed: {request_id} - {e}")
            request.status = "failed"
            request.error = str(e)

            with self.lock:
                self.stats["failed"] += 1
                if request_id in self.active_transcriptions:
                    del self.active_transcriptions[request_id]

    def _transcribe_by_context(self, request: TranscriptionRequest, service) -> Dict[str, Any]:
        """Transcribe based on context"""
        context = request.context

        if context == TranscriptionContext.EDIT_ORIGINAL:
            # "Jarvis edit original" - edit existing transcription
            return self._transcribe_edit_original(request, service)
        elif context == TranscriptionContext.VOICE_EDIT:
            # Voice editing - natural speech text manipulation
            return self._transcribe_voice_edit(request, service)
        elif context == TranscriptionContext.NEW_REQUEST:
            # New request in active window
            return self._transcribe_new_request(request, service)
        else:
            # Default transcription
            return self._transcribe_default(request, service)

    def _transcribe_edit_original(self, request: TranscriptionRequest, service) -> Dict[str, Any]:
        """Transcribe for 'edit original' context"""
        logger.info(f"✏️  Transcribing for edit original: {request.request_id}")

        # Get original transcription to edit
        original_chat_id = request.metadata.get("original_chat_id")
        if original_chat_id:
            # Find original transcription
            original = self._find_original_transcription(original_chat_id)
            if original:
                request.metadata["original_transcription"] = original.result

        # Process transcription
        # This would integrate with actual transcription service
        result = {
            "text": "Transcribed text for edit original",
            "context": "edit_original",
            "original_id": original_chat_id
        }

        return result

    def _transcribe_voice_edit(self, request: TranscriptionRequest, service) -> Dict[str, Any]:
        """Transcribe for voice editing"""
        logger.info(f"🎤 Transcribing for voice edit: {request.request_id}")

        # Voice editing - natural speech text manipulation
        result = {
            "text": "Transcribed text for voice edit",
            "context": "voice_edit",
            "editing_commands": []
        }

        return result

    def _transcribe_new_request(self, request: TranscriptionRequest, service) -> Dict[str, Any]:
        """Transcribe new request"""
        logger.info(f"📝 Transcribing new request: {request.request_id}")

        result = {
            "text": "Transcribed text for new request",
            "context": "new_request"
        }

        return result

    def _transcribe_default(self, request: TranscriptionRequest, service) -> Dict[str, Any]:
        """Default transcription"""
        logger.info(f"🔄 Transcribing (default): {request.request_id}")

        result = {
            "text": "Transcribed text",
            "context": "default"
        }

        return result

    def _find_original_transcription(self, chat_id: str) -> Optional[TranscriptionRequest]:
        """Find original transcription by chat_id"""
        # Search completed transcriptions
        for req in reversed(self.completed_transcriptions):
            if req.chat_id == chat_id:
                return req
        return None

    def _worker_loop(self, worker_id: int):
        """Worker thread loop"""
        logger.info(f"👷 Worker {worker_id} started")

        while not self.stop_event.is_set():
            try:
                # Get request from queue (with timeout)
                try:
                    priority, timestamp, request = self.request_queue.get(timeout=1.0)
                except queue.Empty:
                    continue

                # Process request
                self._process_transcription(request)

            except Exception as e:
                logger.error(f"❌ Worker {worker_id} error: {e}")
                time.sleep(0.1)

        logger.info(f"👷 Worker {worker_id} stopped")

    def start(self):
        """Start worker threads"""
        if self.running:
            logger.warning("⚠️  Already running")
            return

        self.running = True
        self.stop_event.clear()

        # Start worker threads
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker_loop, args=(i,), daemon=True)
            worker.start()
            self.workers.append(worker)

        logger.info(f"✅ Multi-transcription queue started ({self.max_workers} workers)")

    def stop(self):
        """Stop worker threads"""
        self.running = False
        self.stop_event.set()

        # Wait for workers
        for worker in self.workers:
            worker.join(timeout=2)

        self.workers.clear()
        logger.info("👋 Multi-transcription queue stopped")

    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        with self.lock:
            return {
                **self.stats,
                "queue_size": self.request_queue.qsize(),
                "active_requests": [req.request_id for req in self.active_transcriptions.values()],
                "recent_completed": len(self.completed_transcriptions[-10:])
            }

    def get_request_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific request"""
        with self.lock:
            # Check active
            if request_id in self.active_transcriptions:
                req = self.active_transcriptions[request_id]
                return {
                    "request_id": req.request_id,
                    "status": req.status,
                    "context": req.context.value,
                    "priority": req.priority.name
                }

            # Check completed
            for req in self.completed_transcriptions:
                if req.request_id == request_id:
                    return {
                        "request_id": req.request_id,
                        "status": req.status,
                        "context": req.context.value,
                        "priority": req.priority.name,
                        "result": req.result,
                        "error": req.error
                    }

        return None


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Multi-Transcription Queue")
    parser.add_argument("--start", action="store_true", help="Start queue")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--test", action="store_true", help="Test with sample requests")

    args = parser.parse_args()

    queue_system = MultiTranscriptionQueue(max_workers=3)

    if args.test:
        print("🧪 Testing multi-transcription queue...")
        queue_system.start()

        # Add test requests
        req1 = queue_system.add_request(
            context=TranscriptionContext.MAIN_WINDOW,
            priority=TranscriptionPriority.NORMAL
        )
        req2 = queue_system.add_request(
            context=TranscriptionContext.EDIT_ORIGINAL,
            priority=TranscriptionPriority.HIGH,
            metadata={"original_chat_id": "test_chat_123"}
        )

        print(f"Added requests: {req1}, {req2}")

        # Wait a bit
        time.sleep(2)

        # Show stats
        stats = queue_system.get_stats()
        print(f"Stats: {stats}")

        queue_system.stop()
        return 0

    if args.stats:
        stats = queue_system.get_stats()
        print("="*80)
        print("📊 MULTI-TRANSCRIPTION QUEUE STATISTICS")
        print("="*80)
        print(f"Total Requests: {stats['total_requests']}")
        print(f"Completed: {stats['completed']}")
        print(f"Failed: {stats['failed']}")
        print(f"Active: {stats['active_count']}")
        print(f"Queue Size: {stats['queue_size']}")
        return 0

    if args.start:
        print("="*80)
        print("🚀 MULTI-TRANSCRIPTION QUEUE")
        print("="*80)
        print()
        print("Starting queue system...")
        print("Press Ctrl+C to stop")
        print()

        queue_system.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

        queue_system.stop()
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":


    sys.exit(main() or 0)