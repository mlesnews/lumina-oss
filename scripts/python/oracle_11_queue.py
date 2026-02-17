#!/usr/bin/env python3
"""
ORACLE 11 - Queue System with Omniscience

Regular scheduled intervals. Pause/pivot capability.
Queue all transcriptions/translations. Use omniscience to peer ahead in time.
Operator requests stack up in queue as they form.
Unlike text messages - nothing gets lost.

Prime number: 11 (Oracle number - sees ahead)

Tags: #ORACLE #QUEUE #OMNISCIENCE #TRANSCRIPTION #TRANSLATION @JARVIS @TEAM
"""

import sys
import json
import queue
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from standardized_timestamp_logging import get_timestamp_logger
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

logger = get_logger("ORACLE11")
ts_logger = get_timestamp_logger()


class ItemType(Enum):
    """Queue item types"""
    TRANSCRIPTION = "transcription"
    TRANSLATION = "translation"
    OPERATOR_REQUEST = "operator_request"
    PAUSE = "pause"
    PIVOT = "pivot"
    TOPIC_CHANGE = "topic_change"


class ItemStatus(Enum):
    """Queue item status"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    PAUSED = "paused"
    DEFERRED = "deferred"


@dataclass
class QueueItem:
    """A queue item"""
    item_id: str
    item_type: ItemType
    content: str
    timestamp: str
    status: ItemStatus = ItemStatus.QUEUED
    priority: int = 0  # Higher = more priority
    metadata: Dict[str, Any] = field(default_factory=dict)
    oracle_preview: Optional[str] = None  # Omniscience preview


@dataclass
class OraclePreview:
    """Oracle preview - peering ahead in time"""
    preview_id: str
    timestamp: str
    previewed_items: List[str]  # Item IDs that will come
    predicted_content: List[str]
    confidence: float  # 0.0 to 1.0


class ORACLE11:
    """
    ORACLE 11 - Queue System with Omniscience

    Regular scheduled intervals. Pause/pivot capability.
    Queue all transcriptions/translations. Use omniscience to peer ahead.
    Operator requests stack up in queue as they form.
    Unlike text messages - nothing gets lost.

    Prime number: 11 (Oracle number - sees ahead)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize ORACLE 11"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "oracle_11_queue"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Queue system
        self.queue = queue.PriorityQueue()  # Priority queue (higher priority first)
        self.items: Dict[str, QueueItem] = {}
        self.processing = False
        self.paused = False

        # Oracle omniscience
        self.oracle_previews: List[OraclePreview] = []

        # Scheduled intervals
        self.scheduled_interval = 60  # 60 seconds default
        self.last_processing = datetime.now()

        # Threading
        self.processing_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()

        logger.info("🔮 ORACLE 11 initialized")
        logger.info("   Queue system with omniscience")
        logger.info("   Regular scheduled intervals")
        logger.info("   Pause/pivot capability")
        logger.info("   Nothing gets lost")

    def queue_item(self, item_type: ItemType, content: str, priority: int = 0, metadata: Dict[str, Any] = None) -> QueueItem:
        """Queue an item"""
        item = QueueItem(
            item_id=f"item_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            item_type=item_type,
            content=content,
            timestamp=datetime.now().isoformat(),
            priority=priority,
            metadata=metadata or {},
        )

        # Use omniscience to peer ahead
        item.oracle_preview = self._peer_ahead(item)

        # Add to queue (negative priority for max-heap behavior)
        self.queue.put((-priority, item.item_id, item))
        self.items[item.item_id] = item

        logger.info(f"📥 Queued: {item.item_id} ({item_type.value}, priority: {priority})")
        logger.info(f"   Content: {content[:50]}...")

        # Save to disk
        self._save_item(item)

        return item

    def _peer_ahead(self, item: QueueItem) -> Optional[str]:
        """Use omniscience to peer ahead in time"""
        # Oracle preview - predict what's coming
        preview = f"Oracle preview: {item.item_type.value} item queued. "

        if item.item_type == ItemType.OPERATOR_REQUEST:
            preview += "Operator request detected. Will process in scheduled interval."
        elif item.item_type == ItemType.PAUSE:
            preview += "Pause requested. Will pause processing."
        elif item.item_type == ItemType.PIVOT:
            preview += "Pivot requested. Will change direction."
        elif item.item_type == ItemType.TOPIC_CHANGE:
            preview += "Topic change requested. Will shift focus."
        else:
            preview += "Will process in queue order."

        return preview

    def queue_transcription(self, content: str, priority: int = 0) -> QueueItem:
        """Queue a transcription"""
        return self.queue_item(ItemType.TRANSCRIPTION, content, priority)

    def queue_translation(self, content: str, priority: int = 0) -> QueueItem:
        """Queue a translation"""
        return self.queue_item(ItemType.TRANSLATION, content, priority)

    def queue_operator_request(self, content: str, priority: int = 5) -> QueueItem:
        """Queue an operator request (higher priority)"""
        return self.queue_item(ItemType.OPERATOR_REQUEST, content, priority)

    def pause(self) -> QueueItem:
        """Pause processing"""
        self.paused = True
        item = self.queue_item(ItemType.PAUSE, "Pause requested", priority=10)
        logger.info("⏸️  Processing paused")
        return item

    def resume(self):
        """Resume processing"""
        self.paused = False
        logger.info("▶️  Processing resumed")

    def pivot(self, new_topic: str) -> QueueItem:
        """Pivot to new topic"""
        item = self.queue_item(ItemType.PIVOT, f"Pivot to: {new_topic}", priority=8)
        logger.info(f"🔄 Pivoted to: {new_topic}")
        return item

    def change_topic(self, new_topic: str) -> QueueItem:
        """Change topic"""
        item = self.queue_item(ItemType.TOPIC_CHANGE, f"Topic change to: {new_topic}", priority=7)
        logger.info(f"📝 Topic changed to: {new_topic}")
        return item

    def process_queue(self, callback: Optional[Callable[[QueueItem], None]] = None):
        """Process queue items"""
        if self.paused:
            logger.debug("⏸️  Processing paused - skipping")
            return

        processed = 0

        while not self.queue.empty():
            try:
                # Get next item (highest priority first)
                priority, item_id, item = self.queue.get_nowait()

                # Check for pause/pivot
                if item.item_type == ItemType.PAUSE:
                    self.paused = True
                    item.status = ItemStatus.COMPLETED
                    logger.info("⏸️  Pause processed")
                    break

                if item.item_type == ItemType.PIVOT:
                    item.status = ItemStatus.COMPLETED
                    logger.info(f"🔄 Pivot processed: {item.content}")
                    continue

                if item.item_type == ItemType.TOPIC_CHANGE:
                    item.status = ItemStatus.COMPLETED
                    logger.info(f"📝 Topic change processed: {item.content}")
                    continue

                # Process item
                item.status = ItemStatus.PROCESSING
                logger.info(f"🔄 Processing: {item.item_id} ({item.item_type.value})")

                if callback:
                    callback(item)

                item.status = ItemStatus.COMPLETED
                processed += 1

                # Update item
                self.items[item_id] = item
                self._save_item(item)

            except queue.Empty:
                break
            except Exception as e:
                logger.error(f"❌ Error processing item: {e}")
                if item_id in self.items:
                    self.items[item_id].status = ItemStatus.DEFERRED

        logger.info(f"✅ Processed {processed} items")
        self.last_processing = datetime.now()

    def start_scheduled_processing(self, interval: int = 60, callback: Optional[Callable[[QueueItem], None]] = None):
        """Start scheduled processing at regular intervals"""
        self.scheduled_interval = interval

        def processing_loop():
            while not self.stop_event.is_set():
                if not self.paused:
                    self.process_queue(callback)
                time.sleep(self.scheduled_interval)

        self.processing_thread = threading.Thread(target=processing_loop, daemon=True)
        self.processing_thread.start()

        logger.info(f"🔄 Scheduled processing started (interval: {interval}s)")

    def stop_processing(self):
        """Stop scheduled processing"""
        self.stop_event.set()
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        logger.info("⏹️  Processing stopped")

    def get_queue_status(self) -> Dict[str, Any]:
        """Get queue status"""
        return {
            "total_items": len(self.items),
            "queued": len([i for i in self.items.values() if i.status == ItemStatus.QUEUED]),
            "processing": len([i for i in self.items.values() if i.status == ItemStatus.PROCESSING]),
            "completed": len([i for i in self.items.values() if i.status == ItemStatus.COMPLETED]),
            "paused": len([i for i in self.items.values() if i.status == ItemStatus.PAUSED]),
            "queue_size": self.queue.qsize(),
            "paused": self.paused,
            "last_processing": self.last_processing.isoformat(),
            "scheduled_interval": self.scheduled_interval,
        }

    def _save_item(self, item: QueueItem):
        try:
            """Save item to disk"""
            file_path = self.data_dir / f"{item.item_id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(item), f, indent=2, ensure_ascii=False, default=str)

        except Exception as e:
            self.logger.error(f"Error in _save_item: {e}", exc_info=True)
            raise
    def get_all_items(self) -> List[QueueItem]:
        """Get all items"""
        return list(self.items.values())


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="ORACLE 11 - Queue System with Omniscience")
    parser.add_argument("--queue", type=str, help="Queue item (content)")
    parser.add_argument("--type", type=str, choices=["transcription", "translation", "operator_request"], help="Item type")
    parser.add_argument("--pause", action="store_true", help="Pause processing")
    parser.add_argument("--resume", action="store_true", help="Resume processing")
    parser.add_argument("--pivot", type=str, help="Pivot to new topic")
    parser.add_argument("--topic", type=str, help="Change topic")
    parser.add_argument("--process", action="store_true", help="Process queue")
    parser.add_argument("--status", action="store_true", help="Show queue status")
    parser.add_argument("--start", type=int, metavar="INTERVAL", help="Start scheduled processing (interval in seconds)")

    args = parser.parse_args()

    print("="*80)
    print("🔮 ORACLE 11 - QUEUE SYSTEM WITH OMNISCIENCE")
    print("="*80)
    print()
    print("Regular scheduled intervals")
    print("Pause/pivot capability")
    print("Queue all transcriptions/translations")
    print("Use omniscience to peer ahead in time")
    print("Operator requests stack up in queue")
    print("Unlike text messages - nothing gets lost")
    print("Prime number: 11 (Oracle number)")
    print()

    oracle = ORACLE11()

    if args.queue:
        item_type_map = {
            "transcription": ItemType.TRANSCRIPTION,
            "translation": ItemType.TRANSLATION,
            "operator_request": ItemType.OPERATOR_REQUEST,
        }
        item_type = item_type_map.get(args.type, ItemType.TRANSCRIPTION)
        item = oracle.queue_item(item_type, args.queue)
        print(f"📥 Queued: {item.item_id}")
        print(f"   Type: {item.item_type.value}")
        print(f"   Content: {item.content[:100]}...")
        if item.oracle_preview:
            print(f"   Oracle Preview: {item.oracle_preview}")
        print()

    if args.pause:
        oracle.pause()
        print("⏸️  Processing paused")
        print()

    if args.resume:
        oracle.resume()
        print("▶️  Processing resumed")
        print()

    if args.pivot:
        oracle.pivot(args.pivot)
        print(f"🔄 Pivoted to: {args.pivot}")
        print()

    if args.topic:
        oracle.change_topic(args.topic)
        print(f"📝 Topic changed to: {args.topic}")
        print()

    if args.process:
        oracle.process_queue()
        print("✅ Queue processed")
        print()

    if args.status:
        status = oracle.get_queue_status()
        print("📊 QUEUE STATUS:")
        print(f"   Total Items: {status['total_items']}")
        print(f"   Queued: {status['queued']}")
        print(f"   Processing: {status['processing']}")
        print(f"   Completed: {status['completed']}")
        print(f"   Queue Size: {status['queue_size']}")
        print(f"   Paused: {status['paused']}")
        print(f"   Last Processing: {status['last_processing']}")
        print(f"   Scheduled Interval: {status['scheduled_interval']}s")
        print()

    if args.start:
        oracle.start_scheduled_processing(args.start)
        print(f"🔄 Scheduled processing started (interval: {args.start}s)")
        print("   Press Ctrl+C to stop")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            oracle.stop_processing()
            print("\n⏹️  Processing stopped")
        print()

    if not any([args.queue, args.pause, args.resume, args.pivot, args.topic, args.process, args.status, args.start]):
        # Default: show status
        status = oracle.get_queue_status()
        print("📊 QUEUE STATUS:")
        print(f"   Total Items: {status['total_items']}")
        print(f"   Queued: {status['queued']}")
        print(f"   Completed: {status['completed']}")
        print()
        print("Use --queue CONTENT --type TYPE to queue item")
        print("Use --pause to pause")
        print("Use --resume to resume")
        print("Use --pivot TOPIC to pivot")
        print("Use --topic TOPIC to change topic")
        print("Use --process to process queue")
        print("Use --status to show status")
        print("Use --start INTERVAL to start scheduled processing")
        print()


if __name__ == "__main__":


    main()