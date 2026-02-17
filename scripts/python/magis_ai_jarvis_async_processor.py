#!/usr/bin/env python3
"""
MAGIS AI + JARVIS Async Processor

Asynchronously processes chat history items from the unified queue using
MAGIS AI for intelligence extraction, coordinated by JARVIS.

Features:
- Async processing of chat history queue items
- MAGIS AI intelligence extraction
- JARVIS coordination and orchestration
- Real-time queue status updates
- Background processing with progress tracking

@MAGISAI @JARVIS @ASYNC @CHAT_HISTORY @UNIFIED_QUEUE
"""

import sys
import json
import asyncio
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
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
    from unified_queue_adapter import UnifiedQueueAdapter, QueueItemType, QueueItemStatus
except ImportError:
    UnifiedQueueAdapter = None
    QueueItemType = None
    QueueItemStatus = None

try:
    from jarvis_syphon_chat_session import JARVISSyphonChatSession
except ImportError:
    JARVISSyphonChatSession = None


class MAGISAIProcessor:
    """
    MAGIS AI Processor for chat history intelligence extraction

    Uses MAGIS AI to extract intelligence from chat sessions
    """

    def __init__(self, project_root: Path):
        """Initialize MAGIS AI processor"""
        self.project_root = Path(project_root)
        self.logger = get_logger("MAGISAI")

        # Initialize JARVIS SYPHON if available
        self.jarvis_syphon = None
        if JARVISSyphonChatSession:
            try:
                self.jarvis_syphon = JARVISSyphonChatSession(self.project_root)
                self.logger.info("✅ JARVIS SYPHON initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  JARVIS SYPHON initialization failed: {e}")

        self.logger.info("🤖 MAGIS AI Processor initialized")

    async def process_chat_history(self, item: 'UnifiedQueueItem', 
                                  chat_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process chat history using MAGIS AI

        Args:
            item: Unified queue item
            chat_data: Chat session data

        Returns:
            Processing results with intelligence extraction
        """
        self.logger.info(f"🤖 MAGIS AI processing: {item.item_id}")

        try:
            # Simulate async processing with progress updates
            results = {
                "item_id": item.item_id,
                "session_id": item.chat_session_id,
                "agent_name": item.chat_agent_name,
                "processed_at": datetime.now().isoformat(),
                "intelligence": {},
                "extracted_data": {},
                "success": True
            }

            # Use JARVIS SYPHON if available
            if self.jarvis_syphon and chat_data:
                # Extract intelligence using JARVIS SYPHON
                extracted = self.jarvis_syphon.extract_chat_session(chat_data)
                results["intelligence"] = extracted.get("intelligence", {})
                results["extracted_data"] = extracted
                results["message_count"] = extracted.get("metadata", {}).get("message_count", 0)
            else:
                # Fallback: Basic extraction
                results["intelligence"] = {
                    "topics": self._extract_topics_basic(chat_data),
                    "message_count": len(chat_data.get("messages", []))
                }

            # Simulate async processing time
            await asyncio.sleep(0.5)  # Simulate processing

            self.logger.info(f"✅ MAGIS AI completed: {item.item_id}")
            return results

        except Exception as e:
            self.logger.error(f"❌ MAGIS AI processing failed: {e}")
            return {
                "item_id": item.item_id,
                "success": False,
                "error": str(e),
                "processed_at": datetime.now().isoformat()
            }

    def _extract_topics_basic(self, chat_data: Dict[str, Any]) -> List[str]:
        """Basic topic extraction fallback"""
        topics = []
        messages = chat_data.get("messages", [])

        # Simple keyword extraction
        keywords = ["code", "function", "error", "fix", "implement", "create", "update"]
        for message in messages:
            content = message.get("content", "").lower()
            for keyword in keywords:
                if keyword in content and keyword not in topics:
                    topics.append(keyword)

        return topics[:5]  # Top 5 topics


class JARVISCoordinator:
    """
    JARVIS Coordinator for async task orchestration

    Coordinates MAGIS AI processing with queue management
    """

    def __init__(self, project_root: Path):
        """Initialize JARVIS coordinator"""
        self.project_root = Path(project_root)
        self.logger = get_logger("JARVISCoordinator")
        self.magis_ai = MAGISAIProcessor(project_root)

        self.logger.info("🎯 JARVIS Coordinator initialized")

    async def coordinate_processing(self, item: 'UnifiedQueueItem',
                                   chat_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Coordinate async processing of chat history item

        Args:
            item: Unified queue item
            chat_data: Optional chat data (will be loaded if not provided)

        Returns:
            Coordination results
        """
        self.logger.info(f"🎯 JARVIS coordinating: {item.item_id}")

        try:
            # Load chat data if not provided
            if chat_data is None:
                chat_data = await self._load_chat_data(item)

            # Process with MAGIS AI
            results = await self.magis_ai.process_chat_history(item, chat_data)

            # Update queue status
            coordination_result = {
                "item_id": item.item_id,
                "coordinated_at": datetime.now().isoformat(),
                "magis_ai_results": results,
                "success": results.get("success", False)
            }

            self.logger.info(f"✅ JARVIS coordination complete: {item.item_id}")
            return coordination_result

        except Exception as e:
            self.logger.error(f"❌ JARVIS coordination failed: {e}")
            return {
                "item_id": item.item_id,
                "success": False,
                "error": str(e),
                "coordinated_at": datetime.now().isoformat()
            }

    async def _load_chat_data(self, item: 'UnifiedQueueItem') -> Dict[str, Any]:
        """Load chat data for processing"""
        # Try to load from session ID
        session_id = item.chat_session_id

        if not session_id:
            return {"messages": [], "metadata": {}}

        # Look for chat session files
        chat_paths = [
            self.project_root / "data" / "syphon" / "chat_sessions" / f"{session_id}.json",
            self.project_root / "data" / "cursor_agent_history" / f"{session_id}.json",
            self.project_root / "data" / "chat_history" / f"{session_id}.json"
        ]

        for chat_path in chat_paths:
            if chat_path.exists():
                try:
                    with open(chat_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    self.logger.warning(f"⚠️  Error loading {chat_path}: {e}")

        # Return empty structure if not found
        return {
            "messages": [],
            "metadata": {
                "session_id": session_id,
                "agent_name": item.chat_agent_name,
                "message_count": item.chat_message_count or 0
            }
        }


class MAGISAIJARVISAsyncProcessor:
    """
    Main async processor for MAGIS AI + JARVIS integration

    Monitors unified queue for chat history items and processes them asynchronously
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize async processor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("MAGISAIJARVISAsync")

        # Initialize components
        self.queue_adapter = UnifiedQueueAdapter(self.project_root) if UnifiedQueueAdapter else None
        self.jarvis = JARVISCoordinator(self.project_root)

        # Processing state
        self.processing_active = False
        self.processing_tasks: Dict[str, asyncio.Task] = {}
        self.processing_queue: Queue = Queue()

        # Statistics
        self.stats = {
            "processed": 0,
            "failed": 0,
            "active": 0,
            "started_at": datetime.now().isoformat()
        }

        # Output directory
        self.output_dir = self.project_root / "data" / "magis_ai_jarvis"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("=" * 80)
        self.logger.info("🤖 MAGIS AI + JARVIS Async Processor Initialized")
        self.logger.info("=" * 80)
        self.logger.info(f"   Queue Adapter: {'✅' if self.queue_adapter else '❌'}")
        self.logger.info(f"   JARVIS: ✅")
        self.logger.info(f"   MAGIS AI: ✅")
        self.logger.info(f"   Output: {self.output_dir}")
        self.logger.info("=" * 80)

    async def process_item(self, item: 'UnifiedQueueItem') -> Dict[str, Any]:
        """
        Process a single chat history item asynchronously

        Args:
            item: Unified queue item to process

        Returns:
            Processing results
        """
        item_id = item.item_id

        # Update status to processing
        if self.queue_adapter:
            self.queue_adapter.update_item_status(item_id, QueueItemStatus.PROCESSING)
            self.queue_adapter.queue_items[item_id].progress = 10.0

        self.logger.info(f"🔄 Processing: {item_id}")
        self.stats["active"] += 1

        try:
            # Coordinate with JARVIS
            results = await self.jarvis.coordinate_processing(item)

            # Update progress
            if self.queue_adapter:
                self.queue_adapter.queue_items[item_id].progress = 90.0

            # Save results
            results_file = self.output_dir / f"{item_id}_results.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            # Update queue status
            if self.queue_adapter:
                if results.get("success", False):
                    self.queue_adapter.update_item_status(item_id, QueueItemStatus.COMPLETED)
                    self.queue_adapter.queue_items[item_id].progress = 100.0
                    self.queue_adapter.queue_items[item_id].metadata["magis_ai_results"] = results
                    self.stats["processed"] += 1
                else:
                    error = results.get("error", "Processing failed")
                    self.queue_adapter.update_item_status(item_id, QueueItemStatus.FAILED, error=error)
                    self.stats["failed"] += 1

            self.logger.info(f"✅ Completed: {item_id}")
            return results

        except Exception as e:
            self.logger.error(f"❌ Processing failed: {item_id}: {e}")

            if self.queue_adapter:
                self.queue_adapter.update_item_status(item_id, QueueItemStatus.FAILED, error=str(e))

            self.stats["failed"] += 1
            return {
                "item_id": item_id,
                "success": False,
                "error": str(e)
            }
        finally:
            self.stats["active"] -= 1
            if item_id in self.processing_tasks:
                del self.processing_tasks[item_id]

    async def process_queue_async(self):
        """Main async processing loop"""
        self.logger.info("🚀 Starting async processing loop...")

        while self.processing_active:
            try:
                # Get pending chat history items
                if not self.queue_adapter:
                    await asyncio.sleep(5)
                    continue

                items = self.queue_adapter.get_all_items(
                    item_type=QueueItemType.CHAT_HISTORY,
                    status=QueueItemStatus.PENDING
                )

                # Process items (limit concurrent processing)
                max_concurrent = 3
                active_count = len(self.processing_tasks)

                for item in items:
                    if active_count >= max_concurrent:
                        break

                    if item.item_id not in self.processing_tasks:
                        # Start async task
                        task = asyncio.create_task(self.process_item(item))
                        self.processing_tasks[item.item_id] = task
                        active_count += 1

                # Clean up completed tasks
                completed = [
                    item_id for item_id, task in self.processing_tasks.items()
                    if task.done()
                ]
                for item_id in completed:
                    del self.processing_tasks[item_id]

                # Wait before next check
                await asyncio.sleep(2)

            except Exception as e:
                self.logger.error(f"Error in processing loop: {e}")
                await asyncio.sleep(5)

    def start_processing(self):
        """Start async processing"""
        if self.processing_active:
            self.logger.warning("⚠️  Processing already active")
            return

        self.processing_active = True

        # Run async loop in thread
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.process_queue_async())

        thread = threading.Thread(target=run_async, daemon=True)
        thread.start()

        self.logger.info("🚀 Async processing started")

    def stop_processing(self):
        """Stop async processing"""
        self.processing_active = False
        self.logger.info("⏹️  Async processing stopped")

    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            **self.stats,
            "active_tasks": len(self.processing_tasks),
            "queue_size": self.processing_queue.qsize()
        }


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="MAGIS AI + JARVIS Async Processor")
    parser.add_argument("--daemon", action="store_true",
                       help="Run as daemon (continuous processing)")
    parser.add_argument("--process-item", type=str,
                       help="Process specific item ID")
    parser.add_argument("--stats", action="store_true",
                       help="Show statistics")

    args = parser.parse_args()

    processor = MAGISAIJARVISAsyncProcessor()

    if args.process_item:
        # Process single item
        if not processor.queue_adapter:
            print("❌ Queue adapter not available")
            return

        item = processor.queue_adapter.get_item(args.process_item)
        if not item:
            print(f"❌ Item not found: {args.process_item}")
            return

        # Run async processing
        async def process_single():
            result = await processor.process_item(item)
            print(json.dumps(result, indent=2))

        asyncio.run(process_single())

    elif args.daemon:
        # Run as daemon
        print("🚀 Starting MAGIS AI + JARVIS async processor daemon...")
        print("   Press Ctrl+C to stop")
        print()

        processor.start_processing()

        try:
            while True:
                time.sleep(10)
                stats = processor.get_stats()
                print(f"📊 Stats: Processed: {stats['processed']}, "
                      f"Failed: {stats['failed']}, Active: {stats['active_tasks']}")
        except KeyboardInterrupt:
            print("\n⏹️  Stopping...")
            processor.stop_processing()

    elif args.stats:
        stats = processor.get_stats()
        print(json.dumps(stats, indent=2))

    else:
        # Default: start processing
        processor.start_processing()
        print("🚀 Processing started. Use --daemon for continuous mode.")
        print("   Press Ctrl+C to stop")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            processor.stop_processing()


if __name__ == "__main__":


    main()