#!/usr/bin/env python3
"""
Unified Queue Adapter

Integrates AI SYPHON + IDM Orchestrator sources queue with the unified
task queue system, treating sources the same way as VSCode problems and
other queue items.

This allows sources to be:
- Tracked in the same queue system
- Prioritized and managed consistently
- Viewed alongside other queue items
- Processed with the same workflow patterns

@UNIFIED @QUEUE @SOURCES @INTEGRATION
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass, asdict
logger = get_logger("unified_queue_adapter")


script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from ai_syphon_idm_orchestrator import AIOrchestrator, WorkflowItem, WorkflowStage
except ImportError:
    AIOrchestrator = None
    WorkflowItem = None
    WorkflowStage = None


class QueueItemType(Enum):
    """Types of items in the unified queue"""
    SOURCE = "source"  # Sources queue items (SYPHON + IDM)
    PROBLEM = "problem"  # VSCode problems
    TASK = "task"  # General tasks
    NOTIFICATION = "notification"  # System notifications
    ALERT = "alert"  # System alerts
    CHAT_HISTORY = "chat_history"  # Agent chat history sessions


class QueueItemStatus(Enum):
    """Unified status for all queue items"""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


@dataclass
class UnifiedQueueItem:
    """
    Unified queue item that can represent any type of queue item
    (sources, problems, tasks, etc.)
    """
    item_id: str
    item_type: QueueItemType
    status: QueueItemStatus
    title: str
    description: str
    priority: int = 5  # 1-10, 1 is highest
    created_at: str = None
    updated_at: str = None
    completed_at: Optional[str] = None
    assigned_to: Optional[str] = None
    metadata: Dict[str, Any] = None
    error: Optional[str] = None
    progress: float = 0.0

    # Source-specific fields (when item_type == SOURCE)
    source_url: Optional[str] = None
    source_type: Optional[str] = None
    workflow_stage: Optional[str] = None

    # Problem-specific fields (when item_type == PROBLEM)
    problem_category: Optional[str] = None
    problem_severity: Optional[str] = None

    # Chat history-specific fields (when item_type == CHAT_HISTORY)
    chat_session_id: Optional[str] = None
    chat_agent_name: Optional[str] = None
    chat_message_count: Optional[int] = None
    chat_timestamp: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self):
        """Convert to dictionary"""
        return {
            **asdict(self),
            'item_type': self.item_type.value,
            'status': self.status.value
        }

    @classmethod
    def from_workflow_item(cls, workflow_item: 'WorkflowItem') -> 'UnifiedQueueItem':
        """Create unified queue item from workflow item"""
        # Map workflow stages to unified status
        stage_to_status = {
            WorkflowStage.DISCOVERY: QueueItemStatus.PENDING,
            WorkflowStage.QUEUED: QueueItemStatus.QUEUED,
            WorkflowStage.DOWNLOADING: QueueItemStatus.PROCESSING,
            WorkflowStage.DOWNLOADED: QueueItemStatus.PROCESSING,
            WorkflowStage.EXTRACTING: QueueItemStatus.PROCESSING,
            WorkflowStage.EXTRACTED: QueueItemStatus.PROCESSING,
            WorkflowStage.PROCESSING: QueueItemStatus.PROCESSING,
            WorkflowStage.COMPLETED: QueueItemStatus.COMPLETED,
            WorkflowStage.FAILED: QueueItemStatus.FAILED,
            WorkflowStage.SKIPPED: QueueItemStatus.SKIPPED
        }

        status = stage_to_status.get(workflow_item.stage, QueueItemStatus.PENDING)

        # Determine priority from metadata
        priority = workflow_item.metadata.get("priority", 5)
        if isinstance(priority, str):
            priority_map = {"high": 3, "normal": 5, "low": 7}
            priority = priority_map.get(priority.lower(), 5)

        return cls(
            item_id=workflow_item.item_id,
            item_type=QueueItemType.SOURCE,
            status=status,
            title=f"Source: {workflow_item.url[:60]}...",
            description=f"Processing {workflow_item.source_type} source",
            priority=priority,
            created_at=workflow_item.created_at,
            updated_at=workflow_item.updated_at,
            source_url=workflow_item.url,
            source_type=workflow_item.source_type,
            workflow_stage=workflow_item.stage.value,
            progress=workflow_item.progress,
            error=workflow_item.error,
            metadata={
                **workflow_item.metadata,
                "workflow_item": workflow_item.to_dict()
            }
        )


class UnifiedQueueAdapter:
    """
    Adapter that integrates sources queue with unified queue system

    Treats sources queue items the same way as VSCode problems and other items
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize unified queue adapter"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("UnifiedQueueAdapter")

        # Initialize orchestrator if available
        self.orchestrator = None
        if AIOrchestrator:
            try:
                self.orchestrator = AIOrchestrator(project_root=project_root)
                self.orchestrator.start_monitoring()
                self.logger.info("✅ Orchestrator initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  Orchestrator initialization failed: {e}")

        # Unified queue storage
        self.queue_items: Dict[str, UnifiedQueueItem] = {}
        self.output_dir = self.project_root / "data" / "unified_queue"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Status callback to sync orchestrator items
        if self.orchestrator:
            self.orchestrator.add_status_callback(self._on_orchestrator_status)

        # Initialize MAGIS AI + JARVIS async processor
        self.magis_jarvis_processor = None
        try:
            from magis_ai_jarvis_async_processor import MAGISAIJARVISAsyncProcessor
            self.magis_jarvis_processor = MAGISAIJARVISAsyncProcessor(self.project_root)
            self.magis_jarvis_processor.start_processing()
            self.logger.info("✅ MAGIS AI + JARVIS async processor started")
        except ImportError:
            self.logger.debug("MAGIS AI + JARVIS processor not available")
        except Exception as e:
            self.logger.warning(f"⚠️  MAGIS AI + JARVIS processor initialization failed: {e}")

        # Initialize JARVIS instance recycler (after queue adapter is ready)
        self.instance_recycler = None
        try:
            from jarvis_warm_reboot_handler import JARVISWarmRebootHandler
            from jarvis_instance_recycler import JARVISInstanceRecycler

            # Create recycler directly (avoid circular dependency)
            self.instance_recycler = JARVISInstanceRecycler(self.project_root)
            # Set queue adapter reference (avoid circular init)
            self.instance_recycler.queue_adapter = self

            # Initialize warm reboot handler
            warm_reboot_handler = JARVISWarmRebootHandler(self.project_root)
            warm_reboot_handler.recycler = self.instance_recycler
            warm_reboot_handler.queue_adapter = self
            warm_reboot_handler.initialize()  # Check for warm reboot

            self.logger.info("✅ JARVIS instance recycler initialized (warm reboot ready)")
        except ImportError:
            self.logger.debug("JARVIS instance recycler not available")
        except Exception as e:
            self.logger.warning(f"⚠️  JARVIS instance recycler initialization failed: {e}")

        # Auto-save queue state for IDE extension
        self.start_auto_save(interval=5)

        # Initial save
        self.save_queue_state()

        self.logger.info("=" * 80)
        self.logger.info("🔗 Unified Queue Adapter Initialized")
        self.logger.info("=" * 80)
        self.logger.info(f"   Orchestrator: {'✅' if self.orchestrator else '❌'}")
        self.logger.info(f"   MAGIS AI + JARVIS: {'✅' if self.magis_jarvis_processor else '❌'}")
        self.logger.info(f"   Instance Recycler: {'✅' if self.instance_recycler else '❌'}")
        self.logger.info(f"   Output: {self.output_dir}")
        self.logger.info("=" * 80)

    def _on_orchestrator_status(self, status: Dict[str, Any]):
        """Handle status updates from orchestrator"""
        if status.get("type") == "stage_update":
            item_id = status.get("item_id")
            item = status.get("item", {})

            # Update unified queue item
            if item_id in self.queue_items:
                unified_item = self.queue_items[item_id]
                unified_item.updated_at = datetime.now().isoformat()
                unified_item.workflow_stage = status.get("new_stage")
                unified_item.progress = item.get("progress", 0.0)
                unified_item.error = item.get("error")

                # Update status
                stage_to_status = {
                    "discovery": QueueItemStatus.PENDING,
                    "queued": QueueItemStatus.QUEUED,
                    "downloading": QueueItemStatus.PROCESSING,
                    "downloaded": QueueItemStatus.PROCESSING,
                    "extracting": QueueItemStatus.PROCESSING,
                    "extracted": QueueItemStatus.PROCESSING,
                    "processing": QueueItemStatus.PROCESSING,
                    "completed": QueueItemStatus.COMPLETED,
                    "failed": QueueItemStatus.FAILED,
                    "skipped": QueueItemStatus.SKIPPED
                }
                unified_item.status = stage_to_status.get(status.get("new_stage"), QueueItemStatus.PENDING)

                if unified_item.status == QueueItemStatus.COMPLETED:
                    unified_item.completed_at = datetime.now().isoformat()

                # Auto-save on status change
                self.save_queue_state()

    def add_source(self, url: str, source_type: str = "web", 
                  metadata: Optional[Dict[str, Any]] = None,
                  priority: Union[int, str] = 5) -> str:
        """
        Add source to unified queue (same interface as other queue items)

        Args:
            url: Source URL
            source_type: Type of source
            metadata: Additional metadata
            priority: Priority (1-10 or "high"/"normal"/"low")

        Returns:
            Item ID
        """
        if not self.orchestrator:
            self.logger.error("❌ Orchestrator not available")
            return None

        # Add to orchestrator
        item_id = self.orchestrator.add_item(url, source_type, metadata)

        # Create unified queue item
        workflow_item = self.orchestrator.workflow_items.get(item_id)
        if workflow_item:
            unified_item = UnifiedQueueItem.from_workflow_item(workflow_item)
            if isinstance(priority, str):
                priority_map = {"high": 3, "normal": 5, "low": 7}
                priority = priority_map.get(priority.lower(), 5)
            unified_item.priority = priority
            self.queue_items[item_id] = unified_item
        self.save_queue_state()  # Save on add

        self.logger.info(f"➕ Added source to unified queue: {item_id}")
        return item_id

    def add_problem(self, title: str, description: str,
                   category: Optional[str] = None,
                   severity: Optional[str] = None,
                   priority: Union[int, str] = 5) -> str:
        """
        Add problem to unified queue (same interface as sources)

        Args:
            title: Problem title
            description: Problem description
            category: Problem category
            severity: Problem severity
            priority: Priority

        Returns:
            Item ID
        """
        item_id = f"problem_{hash(title)}_{int(datetime.now().timestamp())}"

        if isinstance(priority, str):
            priority_map = {"high": 3, "normal": 5, "low": 7}
            priority = priority_map.get(priority.lower(), 5)

        item = UnifiedQueueItem(
            item_id=item_id,
            item_type=QueueItemType.PROBLEM,
            status=QueueItemStatus.PENDING,
            title=title,
            description=description,
            priority=priority,
            problem_category=category,
            problem_severity=severity
        )

        self.queue_items[item_id] = item
        self.save_queue_state()  # Save on add

        self.logger.info(f"➕ Added problem to unified queue: {item_id}")
        return item_id

    def add_task(self, title: str, description: str,
                priority: Union[int, str] = 5,
                assigned_to: Optional[str] = None) -> str:
        """
        Add task to unified queue (same interface)

        Args:
            title: Task title
            description: Task description
            priority: Priority
            assigned_to: Assigned to

        Returns:
            Item ID
        """
        item_id = f"task_{hash(title)}_{int(datetime.now().timestamp())}"

        if isinstance(priority, str):
            priority_map = {"high": 3, "normal": 5, "low": 7}
            priority = priority_map.get(priority.lower(), 5)

        item = UnifiedQueueItem(
            item_id=item_id,
            item_type=QueueItemType.TASK,
            status=QueueItemStatus.PENDING,
            title=title,
            description=description,
            priority=priority,
            assigned_to=assigned_to
        )

        self.queue_items[item_id] = item
        self.save_queue_state()  # Save on add

        self.logger.info(f"➕ Added task to unified queue: {item_id}")
        return item_id

    def add_chat_history(self, session_id: str, agent_name: Optional[str] = None,
                        title: Optional[str] = None,
                        description: Optional[str] = None,
                        message_count: Optional[int] = None,
                        priority: Union[int, str] = 5) -> str:
        """
        Add chat history session to unified queue (same interface as problems)

        Args:
            session_id: Chat session identifier
            agent_name: Name of the agent for this chat session
            title: Optional title (defaults to session-based title)
            description: Optional description
            message_count: Number of messages in the session
            priority: Priority (1-10 or "high"/"normal"/"low")

        Returns:
            Item ID
        """
        item_id = f"chat_history_{session_id}_{int(datetime.now().timestamp())}"

        if isinstance(priority, str):
            priority_map = {"high": 3, "normal": 5, "low": 7}
            priority = priority_map.get(priority.lower(), 5)

        # Default title if not provided
        if title is None:
            title = f"Chat History: {agent_name or 'Agent'} Session"
            if session_id:
                title += f" ({session_id[:8]}...)"

        # Default description if not provided
        if description is None:
            description = f"Agent chat history session"
            if agent_name:
                description += f" with {agent_name}"
            if message_count is not None:
                description += f" ({message_count} messages)"

        item = UnifiedQueueItem(
            item_id=item_id,
            item_type=QueueItemType.CHAT_HISTORY,
            status=QueueItemStatus.PENDING,
            title=title,
            description=description,
            priority=priority,
            chat_session_id=session_id,
            chat_agent_name=agent_name,
            chat_message_count=message_count,
            chat_timestamp=datetime.now().isoformat()
        )

        self.queue_items[item_id] = item
        self.save_queue_state()  # Save on add

        self.logger.info(f"➕ Added chat history to unified queue: {item_id}")

        # Trigger MAGIS AI + JARVIS async processing
        if self.magis_jarvis_processor:
            # Item will be picked up by async processor automatically
            self.logger.debug(f"   🤖 MAGIS AI + JARVIS will process: {item_id}")

        return item_id

    def get_all_items(self, 
                     item_type: Optional[QueueItemType] = None,
                     status: Optional[QueueItemStatus] = None,
                     priority_min: Optional[int] = None,
                     filter_pinned: Optional[bool] = None,
                     filter_read: Optional[bool] = None,
                     filter_duplicates: Optional[bool] = None) -> List[UnifiedQueueItem]:
        """
        Get all queue items with optional filtering

        Args:
            item_type: Filter by item type
            status: Filter by status
            priority_min: Minimum priority (lower number = higher priority)
            filter_pinned: Filter by pinned status (True=pinned only, False=unpinned only, None=all)
            filter_read: Filter by read status (True=read only, False=unread only, None=all)
            filter_duplicates: Filter by duplicate status (True=duplicates only, False=non-duplicates only, None=all)

        Returns:
            List of unified queue items
        """
        items = list(self.queue_items.values())

        if item_type:
            items = [i for i in items if i.item_type == item_type]

        if status:
            items = [i for i in items if i.status == status]

        if priority_min is not None:
            items = [i for i in items if i.priority <= priority_min]

        # Filter by pinned status
        if filter_pinned is not None:
            items = [i for i in items if i.metadata.get("pinned", False) == filter_pinned]

        # Filter by read status
        if filter_read is not None:
            items = [i for i in items if i.metadata.get("read", False) == filter_read]

        # Filter by duplicate status
        if filter_duplicates is not None:
            items = [i for i in items if i.metadata.get("is_duplicate", False) == filter_duplicates]

        # Sort: pinned first, then priority, then created_at
        items.sort(key=lambda x: (
            not x.metadata.get("pinned", False),  # Pinned items first (False sorts before True)
            x.priority,
            x.created_at
        ))

        return items

    def get_item(self, item_id: str) -> Optional[UnifiedQueueItem]:
        """Get specific queue item"""
        return self.queue_items.get(item_id)

    def update_item_status(self, item_id: str, status: QueueItemStatus,
                        error: Optional[str] = None):
        """Update item status"""
        if item_id in self.queue_items:
            item = self.queue_items[item_id]
            item.status = status
            item.updated_at = datetime.now().isoformat()
            if error:
                item.error = error
            if status == QueueItemStatus.COMPLETED:
                item.completed_at = datetime.now().isoformat()
                item.progress = 100.0

            # Auto-save on status change
            self.save_queue_state()

    def pin_item(self, item_id: str) -> bool:
        """
        Pin a queue item (keeps it at top of queue)

        Args:
            item_id: Item ID to pin

        Returns:
            True if successful, False if item not found
        """
        if item_id not in self.queue_items:
            self.logger.warning(f"⚠️  Item not found: {item_id}")
            return False

        item = self.queue_items[item_id]
        item.metadata["pinned"] = True
        item.updated_at = datetime.now().isoformat()
        self.save_queue_state()

        self.logger.info(f"📌 Pinned item: {item_id}")
        return True

    def unpin_item(self, item_id: str) -> bool:
        """
        Unpin a queue item

        Args:
            item_id: Item ID to unpin

        Returns:
            True if successful, False if item not found
        """
        if item_id not in self.queue_items:
            self.logger.warning(f"⚠️  Item not found: {item_id}")
            return False

        item = self.queue_items[item_id]
        item.metadata["pinned"] = False
        item.updated_at = datetime.now().isoformat()
        self.save_queue_state()

        self.logger.info(f"📌 Unpinned item: {item_id}")
        return True

    def mark_read(self, item_id: str) -> bool:
        """
        Mark a queue item as read

        Args:
            item_id: Item ID to mark as read

        Returns:
            True if successful, False if item not found
        """
        if item_id not in self.queue_items:
            self.logger.warning(f"⚠️  Item not found: {item_id}")
            return False

        item = self.queue_items[item_id]
        item.metadata["read"] = True
        item.metadata["read_at"] = datetime.now().isoformat()
        item.updated_at = datetime.now().isoformat()
        self.save_queue_state()

        self.logger.info(f"👁️  Marked as read: {item_id}")
        return True

    def mark_unread(self, item_id: str) -> bool:
        """
        Mark a queue item as unread

        Args:
            item_id: Item ID to mark as unread

        Returns:
            True if successful, False if item not found
        """
        if item_id not in self.queue_items:
            self.logger.warning(f"⚠️  Item not found: {item_id}")
            return False

        item = self.queue_items[item_id]
        item.metadata["read"] = False
        if "read_at" in item.metadata:
            del item.metadata["read_at"]
        item.updated_at = datetime.now().isoformat()
        self.save_queue_state()

        self.logger.info(f"👁️  Marked as unread: {item_id}")
        return True

    def rename_item(self, item_id: str, new_title: str) -> bool:
        """
        Rename a queue item

        Args:
            item_id: Item ID to rename
            new_title: New title for the item

        Returns:
            True if successful, False if item not found
        """
        if item_id not in self.queue_items:
            self.logger.warning(f"⚠️  Item not found: {item_id}")
            return False

        item = self.queue_items[item_id]

        # Store original title on first rename
        if "original_title" not in item.metadata:
            item.metadata["original_title"] = item.title

        item.title = new_title
        item.updated_at = datetime.now().isoformat()
        self.save_queue_state()

        self.logger.info(f"✏️  Renamed item: {item_id} -> {new_title}")
        return True

    def duplicate_item(self, item_id: str, new_title: Optional[str] = None) -> Optional[str]:
        """
        Duplicate a queue item (creates a copy)

        Args:
            item_id: Item ID to duplicate
            new_title: Optional new title for duplicate (defaults to "Copy of {original_title}")

        Returns:
            New item ID if successful, None if item not found
        """
        if item_id not in self.queue_items:
            self.logger.warning(f"⚠️  Item not found: {item_id}")
            return None

        original = self.queue_items[item_id]

        # Create new item ID
        new_item_id = f"{item_id}_copy_{int(datetime.now().timestamp())}"

        # Create duplicate
        duplicate = UnifiedQueueItem(
            item_id=new_item_id,
            item_type=original.item_type,
            status=QueueItemStatus.PENDING,  # Fresh start
            title=new_title or f"Copy of {original.title}",
            description=original.description,
            priority=original.priority,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            assigned_to=original.assigned_to,
            metadata={
                **original.metadata.copy(),
                "is_duplicate": True,
                "duplicated_from": item_id,
                "pinned": False,  # Duplicates not pinned by default
                "read": False,  # New item, unread
            },
            error=None,
            progress=0.0,
            # Copy type-specific fields
            source_url=original.source_url,
            source_type=original.source_type,
            workflow_stage=original.workflow_stage,
            problem_category=original.problem_category,
            problem_severity=original.problem_severity,
            chat_session_id=original.chat_session_id,
            chat_agent_name=original.chat_agent_name,
            chat_message_count=original.chat_message_count,
            chat_timestamp=datetime.now().isoformat()
        )

        self.queue_items[new_item_id] = duplicate
        self.save_queue_state()

        self.logger.info(f"📋 Duplicated item: {item_id} -> {new_item_id}")
        return new_item_id

    def delete_item(self, item_id: str, force: bool = False) -> bool:
        """
        Delete a queue item (with safety checks)

        Safety rules:
        - By default, only deletes items marked as duplicates
        - Prevents deletion of pinned items unless force=True
        - Use force=True to delete any item (use with caution)

        Args:
            item_id: Item ID to delete
            force: If True, bypass safety checks

        Returns:
            True if successful, False if item not found or safety check failed
        """
        if item_id not in self.queue_items:
            self.logger.warning(f"⚠️  Item not found: {item_id}")
            return False

        item = self.queue_items[item_id]

        # Safety checks
        if not force:
            # Only allow deletion of duplicates by default
            if not item.metadata.get("is_duplicate", False):
                self.logger.warning(f"⚠️  Safety check: Only duplicates can be deleted by default. Use --force to override.")
                return False

            # Prevent deletion of pinned items
            if item.metadata.get("pinned", False):
                self.logger.warning(f"⚠️  Safety check: Cannot delete pinned item. Unpin first or use --force.")
                return False

        # Soft delete: mark as cancelled first
        item.status = QueueItemStatus.CANCELLED
        item.updated_at = datetime.now().isoformat()
        item.metadata["deleted_at"] = datetime.now().isoformat()
        self.save_queue_state()

        # Actually remove from queue
        del self.queue_items[item_id]
        self.save_queue_state()

        self.logger.info(f"🗑️  Deleted item: {item_id}")
        return True

    def get_queue_summary(self) -> Dict[str, Any]:
        """Get unified queue summary"""
        items = list(self.queue_items.values())

        summary = {
            "total_items": len(items),
            "by_type": {},
            "by_status": {},
            "by_priority": {},
            "pending_count": 0,
            "processing_count": 0,
            "completed_count": 0,
            "failed_count": 0
        }

        for item in items:
            # Count by type
            type_name = item.item_type.value
            summary["by_type"][type_name] = summary["by_type"].get(type_name, 0) + 1

            # Count by status
            status_name = item.status.value
            summary["by_status"][status_name] = summary["by_status"].get(status_name, 0) + 1

            # Count by priority range
            if item.priority <= 3:
                priority_range = "high"
            elif item.priority <= 6:
                priority_range = "normal"
            else:
                priority_range = "low"
            summary["by_priority"][priority_range] = summary["by_priority"].get(priority_range, 0) + 1

            # Count by status category
            if item.status == QueueItemStatus.PENDING:
                summary["pending_count"] += 1
            elif item.status == QueueItemStatus.PROCESSING:
                summary["processing_count"] += 1
            elif item.status == QueueItemStatus.COMPLETED:
                summary["completed_count"] += 1
            elif item.status == QueueItemStatus.FAILED:
                summary["failed_count"] += 1

        return summary

    def print_queue_summary(self):
        """Print human-readable queue summary"""
        summary = self.get_queue_summary()

        print("\n" + "=" * 80)
        print("📋 UNIFIED QUEUE SUMMARY")
        print("=" * 80)
        print(f"Total Items: {summary['total_items']}")
        print(f"Pending: {summary['pending_count']}")
        print(f"Processing: {summary['processing_count']}")
        print(f"Completed: {summary['completed_count']}")
        print(f"Failed: {summary['failed_count']}")
        print()

        print("By Type:")
        for type_name, count in summary['by_type'].items():
            print(f"  {type_name:15s} {count:>6}")
        print()

        print("By Status:")
        for status_name, count in summary['by_status'].items():
            print(f"  {status_name:15s} {count:>6}")
        print()

        print("By Priority:")
        for priority_range, count in summary['by_priority'].items():
            print(f"  {priority_range:15s} {count:>6}")
        print("=" * 80)

    def save_queue_state(self):
        """Save queue state to disk with progress metrics"""
        state_file = self.output_dir / "queue_state.json"

        # Get progress metrics from orchestrator if available
        progress_metrics = {}
        if self.orchestrator:
            try:
                status = self.orchestrator.get_status()
                progress_metrics = status.get("progress", {})
            except Exception as e:
                self.logger.debug(f"Could not get orchestrator progress: {e}")

        state = {
            "items": [item.to_dict() for item in self.queue_items.values()],
            "summary": self.get_queue_summary(),
            "progress": progress_metrics,  # Add progress metrics for transparency
            "saved_at": datetime.now().isoformat()
        }
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        self.logger.info(f"💾 Queue state saved: {state_file}")

    def start_auto_save(self, interval: int = 5):
        """Start auto-saving queue state periodically"""
        import threading

        def auto_save_loop():
            while True:
                time.sleep(interval)
                try:
                    self.save_queue_state()
                except Exception as e:
                    logger.warning(f"Auto-save error: {e}")

        thread = threading.Thread(target=auto_save_loop, daemon=True)
        thread.start()
        self.logger.info(f"💾 Auto-save started (every {interval}s)")


def main():
    """Main entry point - demo"""
    import argparse

    parser = argparse.ArgumentParser(description="Unified Queue Adapter")

    # Add items
    parser.add_argument("--add-source", nargs=2, metavar=("URL", "TYPE"),
                       help="Add source to queue")
    parser.add_argument("--add-problem", nargs=2, metavar=("TITLE", "DESCRIPTION"),
                       help="Add problem to queue")
    parser.add_argument("--add-chat-history", nargs=1, metavar="SESSION_ID",
                       help="Add chat history session to queue")
    parser.add_argument("--chat-agent", type=str,
                       help="Agent name for chat history (use with --add-chat-history)")
    parser.add_argument("--chat-messages", type=int,
                       help="Message count for chat history (use with --add-chat-history)")

    # Chat history operations
    parser.add_argument("--pin", type=str, metavar="ITEM_ID",
                       help="Pin a queue item")
    parser.add_argument("--unpin", type=str, metavar="ITEM_ID",
                       help="Unpin a queue item")
    parser.add_argument("--mark-read", type=str, metavar="ITEM_ID",
                       help="Mark item as read")
    parser.add_argument("--mark-unread", type=str, metavar="ITEM_ID",
                       help="Mark item as unread")
    parser.add_argument("--rename", nargs=2, metavar=("ITEM_ID", "NEW_TITLE"),
                       help="Rename a queue item")
    parser.add_argument("--duplicate", type=str, metavar="ITEM_ID",
                       help="Duplicate a queue item")
    parser.add_argument("--delete", type=str, metavar="ITEM_ID",
                       help="Delete a queue item (only duplicates by default)")
    parser.add_argument("--force", action="store_true",
                       help="Force operation (use with --delete to bypass safety checks)")

    # View operations
    parser.add_argument("--summary", action="store_true",
                       help="Show queue summary")
    parser.add_argument("--list", action="store_true",
                       help="List all items")
    parser.add_argument("--filter-pinned", action="store_true",
                       help="Filter to show only pinned items (use with --list)")
    parser.add_argument("--filter-unread", action="store_true",
                       help="Filter to show only unread items (use with --list)")
    parser.add_argument("--filter-duplicates", action="store_true",
                       help="Filter to show only duplicate items (use with --list)")

    args = parser.parse_args()

    adapter = UnifiedQueueAdapter()

    # Add items
    if args.add_source:
        url, source_type = args.add_source
        adapter.add_source(url, source_type, priority="normal")
        print(f"✅ Added source: {url}")

    if args.add_problem:
        title, description = args.add_problem
        adapter.add_problem(title, description, priority="normal")
        print(f"✅ Added problem: {title}")

    if args.add_chat_history:
        session_id = args.add_chat_history[0]
        adapter.add_chat_history(
            session_id=session_id,
            agent_name=args.chat_agent,
            message_count=args.chat_messages,
            priority="normal"
        )
        print(f"✅ Added chat history: {session_id}")

    # Chat history operations
    if args.pin:
        if adapter.pin_item(args.pin):
            print(f"📌 Pinned: {args.pin}")
        else:
            print(f"❌ Failed to pin: {args.pin}")

    if args.unpin:
        if adapter.unpin_item(args.unpin):
            print(f"📌 Unpinned: {args.unpin}")
        else:
            print(f"❌ Failed to unpin: {args.unpin}")

    if args.mark_read:
        if adapter.mark_read(args.mark_read):
            print(f"👁️  Marked as read: {args.mark_read}")
        else:
            print(f"❌ Failed to mark as read: {args.mark_read}")

    if args.mark_unread:
        if adapter.mark_unread(args.mark_unread):
            print(f"👁️  Marked as unread: {args.mark_unread}")
        else:
            print(f"❌ Failed to mark as unread: {args.mark_unread}")

    if args.rename:
        item_id, new_title = args.rename
        if adapter.rename_item(item_id, new_title):
            print(f"✏️  Renamed: {item_id} -> {new_title}")
        else:
            print(f"❌ Failed to rename: {item_id}")

    if args.duplicate:
        new_id = adapter.duplicate_item(args.duplicate)
        if new_id:
            print(f"📋 Duplicated: {args.duplicate} -> {new_id}")
        else:
            print(f"❌ Failed to duplicate: {args.duplicate}")

    if args.delete:
        if adapter.delete_item(args.delete, force=args.force):
            print(f"🗑️  Deleted: {args.delete}")
        else:
            print(f"❌ Failed to delete: {args.delete}")

    # View operations
    if args.summary:
        adapter.print_queue_summary()

    if args.list:
        # Build filter kwargs
        filter_kwargs = {}
        if args.filter_pinned:
            filter_kwargs["filter_pinned"] = True
        if args.filter_unread:
            filter_kwargs["filter_read"] = False
        if args.filter_duplicates:
            filter_kwargs["filter_duplicates"] = True

        items = adapter.get_all_items(**filter_kwargs)
        print(f"\n📋 Queue Items ({len(items)}):")
        for item in items:
            pinned = "📌" if item.metadata.get("pinned", False) else " "
            read = "✓" if item.metadata.get("read", False) else "🔴"
            dup = "📋" if item.metadata.get("is_duplicate", False) else " "
            print(f"  {pinned}{read}{dup} {item.item_type.value:12s} {item.status.value:12s} {item.title[:50]}")

    adapter.save_queue_state()


if __name__ == "__main__":


    main()