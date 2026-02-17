#!/usr/bin/env python3
"""
JARVIS Voice Request Queue

Enables queuing multiple voice requests while one is being processed.
Allows pausing/stopping current request and queuing new ones.

Tags: #JARVIS #VOICE #QUEUE #VCR_CONTROLS @JARVIS @LUMINA
"""

import sys
import json
import threading
import queue
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISVoiceQueue")


class RequestStatus(Enum):
    """Voice request status"""
    PENDING = "pending"
    PROCESSING = "processing"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


@dataclass
class VoiceRequest:
    """Voice request in queue"""
    request_id: str
    text: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    status: RequestStatus = RequestStatus.PENDING
    priority: int = 0  # Higher = more priority
    metadata: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


class JARVISVoiceRequestQueue:
    """
    Voice Request Queue System

    Allows queuing multiple voice requests while one is being processed.
    Supports pause/stop and queue management.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize voice request queue"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "voice_queue"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Queue
        self.request_queue = queue.PriorityQueue()  # Priority queue
        self.active_request: Optional[VoiceRequest] = None
        self.request_history: List[VoiceRequest] = []

        # Threading
        self.processing_thread: Optional[threading.Thread] = None
        self.is_processing = False
        self.pause_event = threading.Event()
        self.pause_event.set()  # Start unpaused
        self.stop_event = threading.Event()
        self.stop_event.clear()  # Start not stopped

        # Lock for thread safety
        self.lock = threading.Lock()

        # Load history
        self._load_history()

        logger.info("✅ JARVIS Voice Request Queue initialized")
        logger.info("   Queue ready for voice requests")
        logger.info("   Pause/Stop controls available")

    def _load_history(self):
        """Load request history"""
        history_file = self.data_dir / "request_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.request_history = [
                        VoiceRequest(**req_data)
                        for req_data in data.get("history", [])
                    ]
            except Exception as e:
                logger.warning(f"   ⚠️  Could not load history: {e}")

    def _save_history(self):
        """Save request history"""
        history_file = self.data_dir / "request_history.json"
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "last_updated": datetime.now().isoformat(),
                    "history": [req.to_dict() for req in self.request_history[-100:]]  # Last 100
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"   ⚠️  Could not save history: {e}")

    def add_request(self, text: str, priority: int = 0, metadata: Dict[str, Any] = None) -> str:
        """
        Add voice request to queue

        Args:
            text: Voice request text
            priority: Priority (higher = more priority)
            metadata: Additional metadata

        Returns:
            Request ID
        """
        import hashlib
        request_id = hashlib.md5(f"{text}{datetime.now().isoformat()}".encode()).hexdigest()[:16]

        request = VoiceRequest(
            request_id=request_id,
            text=text,
            priority=priority,
            metadata=metadata or {}
        )

        with self.lock:
            # Add to priority queue (negative priority for max-heap behavior)
            self.request_queue.put((-priority, datetime.now().isoformat(), request))

            # Start processing if not already
            if not self.is_processing:
                self._start_processing()

        logger.info(f"   ✅ Queued voice request: {request_id}")
        logger.info(f"      Text: {text[:50]}...")
        logger.info(f"      Priority: {priority}")
        logger.info(f"      Queue size: {self.request_queue.qsize()}")

        return request_id

    def pause_current_request(self) -> bool:
        """
        Pause current request

        Returns:
            True if paused, False if no active request
        """
        with self.lock:
            if self.active_request and self.active_request.status == RequestStatus.PROCESSING:
                self.active_request.status = RequestStatus.PAUSED
                self.pause_event.clear()  # Pause
                logger.info(f"   ⏸️  Paused request: {self.active_request.request_id}")
                return True
        return False

    def resume_current_request(self) -> bool:
        """
        Resume current request

        Returns:
            True if resumed, False if no paused request
        """
        with self.lock:
            if self.active_request and self.active_request.status == RequestStatus.PAUSED:
                self.active_request.status = RequestStatus.PROCESSING
                self.pause_event.set()  # Resume
                logger.info(f"   ▶️  Resumed request: {self.active_request.request_id}")
                return True
        return False

    def stop_current_request(self) -> bool:
        """
        Stop current request

        Returns:
            True if stopped, False if no active request
        """
        with self.lock:
            if self.active_request:
                self.active_request.status = RequestStatus.CANCELLED
                self.stop_event.set()  # Stop
                logger.info(f"   ⏹️  Stopped request: {self.active_request.request_id}")

                # Move to history
                self.request_history.append(self.active_request)
                self.active_request = None

                # Clear stop event for next request
                self.stop_event.clear()

                return True
        return False

    def _start_processing(self):
        """Start processing thread"""
        if self.processing_thread and self.processing_thread.is_alive():
            return

        self.is_processing = True
        self.processing_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.processing_thread.start()
        logger.info("   🔄 Processing thread started")

    def _process_queue(self):
        """Process queue in background thread"""
        while self.is_processing:
            try:
                # Get next request (with timeout to allow checking stop event)
                try:
                    priority, timestamp, request = self.request_queue.get(timeout=1)
                except queue.Empty:
                    # No requests, check if we should continue
                    if self.request_queue.empty() and not self.active_request:
                        # No more requests, stop processing
                        self.is_processing = False
                        break
                    continue

                # Set as active
                with self.lock:
                    self.active_request = request
                    self.active_request.status = RequestStatus.PROCESSING

                logger.info(f"   🔄 Processing request: {request.request_id}")
                logger.info(f"      Text: {request.text[:50]}...")

                # Process request (wait for pause/resume/stop)
                try:
                    result = self._execute_request(request)

                    # Check if stopped
                    if self.stop_event.is_set():
                        request.status = RequestStatus.CANCELLED
                        logger.info(f"   ⏹️  Request cancelled: {request.request_id}")
                    else:
                        request.status = RequestStatus.COMPLETED
                        request.result = result
                        logger.info(f"   ✅ Request completed: {request.request_id}")

                except Exception as e:
                    request.status = RequestStatus.ERROR
                    request.error = str(e)
                    logger.error(f"   ❌ Request error: {e}")

                # Move to history
                with self.lock:
                    self.request_history.append(request)
                    self.active_request = None
                    self._save_history()

                # Clear stop event for next request
                self.stop_event.clear()

            except Exception as e:
                logger.error(f"   ❌ Queue processing error: {e}")
                time.sleep(1)

    def _execute_request(self, request: VoiceRequest) -> Dict[str, Any]:
        """
        Execute voice request

        Args:
            request: Voice request to execute

        Returns:
            Result dictionary
        """
        # Wait for pause to be cleared (if paused)
        self.pause_event.wait()

        # Check if stopped
        if self.stop_event.is_set():
            return {"status": "cancelled"}

        # Execute request (integrate with JARVIS)
        try:
            from jarvis_hands_free_voice_control import JARVISHandsFreeVoiceControl
            voice_control = JARVISHandsFreeVoiceControl(self.project_root)

            # Process voice command
            result = voice_control.process_voice_input(request.text)

            return {
                "status": "completed",
                "result": result,
                "request_id": request.request_id
            }

        except Exception as e:
            logger.error(f"   ❌ Execution error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "request_id": request.request_id
            }

    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        with self.lock:
            return {
                "queue_size": self.request_queue.qsize(),
                "active_request": self.active_request.to_dict() if self.active_request else None,
                "is_processing": self.is_processing,
                "is_paused": not self.pause_event.is_set() if self.active_request else False,
                "history_count": len(self.request_history)
            }

    def get_queue_list(self) -> List[Dict[str, Any]]:
        """Get list of queued requests (without removing from queue)"""
        # Note: PriorityQueue doesn't support iteration, so we'd need to copy
        # For now, return active request info
        with self.lock:
            queue_list = []
            if self.active_request:
                queue_list.append(self.active_request.to_dict())
            return queue_list


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Voice Request Queue")
        parser.add_argument("--add", nargs=2, metavar=("TEXT", "PRIORITY"),
                           help="Add request to queue")
        parser.add_argument("--pause", action="store_true", help="Pause current request")
        parser.add_argument("--resume", action="store_true", help="Resume current request")
        parser.add_argument("--stop", action="store_true", help="Stop current request")
        parser.add_argument("--status", action="store_true", help="Get queue status")
        parser.add_argument("--json", action="store_true", help="JSON output")

        args = parser.parse_args()

        queue_system = JARVISVoiceRequestQueue()

        if args.add:
            text, priority = args.add
            request_id = queue_system.add_request(text, int(priority))
            if args.json:
                print(json.dumps({"request_id": request_id}, indent=2))
            else:
                print(f"✅ Queued: {request_id}")

        elif args.pause:
            paused = queue_system.pause_current_request()
            if args.json:
                print(json.dumps({"paused": paused}, indent=2))
            else:
                print(f"{'✅ Paused' if paused else '❌ No active request'}")

        elif args.resume:
            resumed = queue_system.resume_current_request()
            if args.json:
                print(json.dumps({"resumed": resumed}, indent=2))
            else:
                print(f"{'✅ Resumed' if resumed else '❌ No paused request'}")

        elif args.stop:
            stopped = queue_system.stop_current_request()
            if args.json:
                print(json.dumps({"stopped": stopped}, indent=2))
            else:
                print(f"{'✅ Stopped' if stopped else '❌ No active request'}")

        elif args.status or not any([args.add, args.pause, args.resume, args.stop]):
            status = queue_system.get_queue_status()
            if args.json:
                print(json.dumps(status, indent=2))
            else:
                print("=" * 80)
                print("📊 VOICE REQUEST QUEUE STATUS")
                print("=" * 80)
                print(f"Queue Size: {status['queue_size']}")
                print(f"Processing: {'✅ Yes' if status['is_processing'] else '❌ No'}")
                print(f"Paused: {'✅ Yes' if status['is_paused'] else '❌ No'}")
                if status['active_request']:
                    print(f"Active Request: {status['active_request']['request_id']}")
                    print(f"  Text: {status['active_request']['text'][:50]}...")
                    print(f"  Status: {status['active_request']['status']}")
                else:
                    print("Active Request: None")
                print(f"History Count: {status['history_count']}")
                print("=" * 80)

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    import time


    main()