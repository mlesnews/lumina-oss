#!/usr/bin/env python3
"""
Workflow Memory Persistence System
Stores workflows as core persistent memories broken into basic building blocks

All workflows are stored in AI's core persistent memories with:
- Short-term memory: Recent workflow executions
- Long-term memory: Core workflow patterns and building blocks
- Context memory: Workflow context and state
- Integration with R5 Living Context Matrix
"""

import json
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

try:
    from memory_manager import MemoryManager, MemoryEntry
    MEMORY_MANAGER_AVAILABLE = True
except ImportError:
    MEMORY_MANAGER_AVAILABLE = False
    MemoryManager = None
    MemoryEntry = None

try:
    from r5_living_context_matrix import R5LivingContextMatrix
    R5_AVAILABLE = True
except ImportError:
    R5_AVAILABLE = False
    R5LivingContextMatrix = None

try:
    from universal_logging_wrapper import get_logger
except ImportError:
    import logging
    get_logger = logging.getLogger

logger = get_logger("WorkflowMemoryPersistence")


class MemoryTier(Enum):
    """Memory tier classification"""
    SHORT_TERM = "short_term"  # Recent executions (48 hours)
    LONG_TERM = "long_term"  # Core patterns (365 days)
    CONTEXT = "context"  # Current workflow context (24 hours)
    EPISODIC = "episodic"  # Specific workflow executions
    SEMANTIC = "semantic"  # Workflow knowledge and patterns
    PROCEDURAL = "procedural"  # How to execute workflows


class BuildingBlockType(Enum):
    """Types of workflow building blocks"""
    STEP = "step"  # Individual workflow step
    PATTERN = "pattern"  # Reusable pattern
    DECISION = "decision"  # Decision point
    ACTION = "action"  # Action to execute
    CONDITION = "condition"  # Condition check
    TRANSITION = "transition"  # State transition
    INTEGRATION = "integration"  # External integration
    VALIDATION = "validation"  # Validation check


@dataclass
class WorkflowBuildingBlock:
    """Basic building block of a workflow"""
    block_id: str
    block_type: BuildingBlockType
    name: str
    description: str
    content: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "block_id": self.block_id,
            "block_type": self.block_type.value,
            "name": self.name,
            "description": self.description,
            "content": self.content,
            "dependencies": self.dependencies,
            "outputs": self.outputs,
            "metadata": self.metadata,
            "created": self.created.isoformat(),
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat()
        }


@dataclass
class WorkflowMemory:
    """Workflow stored as persistent memory"""
    workflow_id: str
    workflow_name: str
    workflow_type: str
    building_blocks: List[WorkflowBuildingBlock]
    execution_history: List[Dict[str, Any]] = field(default_factory=list)
    memory_tier: MemoryTier = MemoryTier.SHORT_TERM
    importance: float = 1.0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created: datetime = field(default_factory=datetime.now)
    last_executed: Optional[datetime] = None
    execution_count: int = 0
    success_rate: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "workflow_id": self.workflow_id,
            "workflow_name": self.workflow_name,
            "workflow_type": self.workflow_type,
            "building_blocks": [block.to_dict() for block in self.building_blocks],
            "execution_history": self.execution_history[-10:],  # Last 10 executions
            "memory_tier": self.memory_tier.value,
            "importance": self.importance,
            "tags": self.tags,
            "metadata": self.metadata,
            "created": self.created.isoformat(),
            "last_executed": self.last_executed.isoformat() if self.last_executed else None,
            "execution_count": self.execution_count,
            "success_rate": self.success_rate
        }


class WorkflowMemoryPersistence:
    """
    Workflow Memory Persistence System

    Stores workflows as core persistent memories, broken into basic building blocks.
    Integrates with memory manager and R5 Living Context Matrix.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize workflow memory persistence"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.memory_dir = project_root / "data" / "memory" / "workflows"
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # Initialize memory manager
        self.memory_manager = None
        if MEMORY_MANAGER_AVAILABLE and MemoryManager:
            try:
                self.memory_manager = MemoryManager(base_path=str(project_root / "data" / "memory"))
            except Exception as e:
                logger.warning(f"Memory manager not available: {e}")

        # Initialize R5
        self.r5_system = None
        if R5_AVAILABLE and R5LivingContextMatrix:
            try:
                self.r5_system = R5LivingContextMatrix(project_root)
            except Exception as e:
                logger.warning(f"R5 system not available: {e}")

        # In-memory cache
        self.workflow_cache: Dict[str, WorkflowMemory] = {}

        # Load existing workflows
        self._load_workflows()

        logger.info("Workflow Memory Persistence initialized")

    def _load_workflows(self):
        """Load workflows from disk"""
        workflow_file = self.memory_dir / "workflows.json"
        if workflow_file.exists():
            try:
                with open(workflow_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for workflow_data in data:
                        workflow = self._dict_to_workflow(workflow_data)
                        self.workflow_cache[workflow.workflow_id] = workflow
                logger.info(f"Loaded {len(self.workflow_cache)} workflows from memory")
            except Exception as e:
                logger.error(f"Error loading workflows: {e}")

    def _save_workflows(self):
        """Save workflows to disk"""
        workflow_file = self.memory_dir / "workflows.json"
        try:
            data = [workflow.to_dict() for workflow in self.workflow_cache.values()]
            with open(workflow_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving workflows: {e}")

    def _dict_to_workflow(self, data: Dict[str, Any]) -> WorkflowMemory:
        """Convert dictionary to WorkflowMemory"""
        building_blocks = [
            WorkflowBuildingBlock(
                block_id=block_data["block_id"],
                block_type=BuildingBlockType(block_data["block_type"]),
                name=block_data["name"],
                description=block_data["description"],
                content=block_data["content"],
                dependencies=block_data.get("dependencies", []),
                outputs=block_data.get("outputs", []),
                metadata=block_data.get("metadata", {}),
                created=datetime.fromisoformat(block_data["created"]),
                access_count=block_data.get("access_count", 0),
                last_accessed=datetime.fromisoformat(block_data.get("last_accessed", block_data["created"]))
            )
            for block_data in data.get("building_blocks", [])
        ]

        return WorkflowMemory(
            workflow_id=data["workflow_id"],
            workflow_name=data["workflow_name"],
            workflow_type=data["workflow_type"],
            building_blocks=building_blocks,
            execution_history=data.get("execution_history", []),
            memory_tier=MemoryTier(data.get("memory_tier", "short_term")),
            importance=data.get("importance", 1.0),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            created=datetime.fromisoformat(data["created"]),
            last_executed=datetime.fromisoformat(data["last_executed"]) if data.get("last_executed") else None,
            execution_count=data.get("execution_count", 0),
            success_rate=data.get("success_rate", 1.0)
        )

    def decompose_workflow(self, workflow_data: Dict[str, Any]) -> List[WorkflowBuildingBlock]:
        """
        Decompose workflow into basic building blocks

        Args:
            workflow_data: Workflow data (from WorkflowBase.to_dict() or similar)

        Returns:
            List of building blocks
        """
        blocks = []
        workflow_name = workflow_data.get("workflow_name", "unknown")
        execution_id = workflow_data.get("execution_id", "")

        # Extract steps
        step_tracker = workflow_data.get("step_tracker", {})
        if isinstance(step_tracker, dict):
            steps = step_tracker.get("steps", {})
            for step_num, step_data in steps.items():
                block = WorkflowBuildingBlock(
                    block_id=f"{execution_id}_step_{step_num}",
                    block_type=BuildingBlockType.STEP,
                    name=f"{workflow_name} - Step {step_num}",
                    description=step_data.get("step_name", ""),
                    content={
                        "step_number": step_num,
                        "step_name": step_data.get("step_name", ""),
                        "status": step_data.get("status", ""),
                        "details": step_data.get("details", {})
                    },
                    metadata={
                        "timestamp": step_data.get("timestamp", ""),
                        "workflow_name": workflow_name
                    }
                )
                blocks.append(block)

        # Extract patterns
        progress = workflow_data.get("progress", {})
        if progress:
            block = WorkflowBuildingBlock(
                block_id=f"{execution_id}_progress",
                block_type=BuildingBlockType.PATTERN,
                name=f"{workflow_name} - Progress Pattern",
                description="Workflow progress tracking pattern",
                content=progress,
                metadata={"workflow_name": workflow_name}
            )
            blocks.append(block)

        # Extract verification
        verification = workflow_data.get("verification", {})
        if verification:
            block = WorkflowBuildingBlock(
                block_id=f"{execution_id}_verification",
                block_type=BuildingBlockType.VALIDATION,
                name=f"{workflow_name} - Verification",
                description="Workflow completion verification",
                content=verification,
                metadata={"workflow_name": workflow_name}
            )
            blocks.append(block)

        return blocks

    def store_workflow(
        self,
        workflow_data: Dict[str, Any],
        workflow_type: str = "general",
        memory_tier: MemoryTier = MemoryTier.SHORT_TERM,
        importance: float = 1.0,
        tags: Optional[List[str]] = None,
        success: bool = True
    ) -> str:
        """
        Store workflow as persistent memory

        Args:
            workflow_data: Workflow data
            workflow_type: Type of workflow
            memory_tier: Memory tier (short-term, long-term, etc.)
            importance: Importance score (0.0-1.0)
            tags: Tags for categorization
            success: Whether workflow succeeded

        Returns:
            Workflow ID
        """
        workflow_name = workflow_data.get("workflow_name", "unknown")
        execution_id = workflow_data.get("execution_id", str(uuid4()))

        # Generate workflow ID
        workflow_id = hashlib.sha256(
            f"{workflow_name}_{execution_id}".encode()
        ).hexdigest()[:16]

        # Decompose into building blocks
        building_blocks = self.decompose_workflow(workflow_data)

        # Create workflow memory
        workflow_memory = WorkflowMemory(
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            workflow_type=workflow_type,
            building_blocks=building_blocks,
            execution_history=[{
                "execution_id": execution_id,
                "timestamp": datetime.now().isoformat(),
                "success": success,
                "data": workflow_data
            }],
            memory_tier=memory_tier,
            importance=importance,
            tags=tags or [workflow_type, workflow_name],
            metadata={
                "execution_id": execution_id,
                "total_steps": workflow_data.get("total_steps", 0)
            },
            last_executed=datetime.now(),
            execution_count=1,
            success_rate=1.0 if success else 0.0
        )

        # Store in cache
        if workflow_id in self.workflow_cache:
            # Update existing
            existing = self.workflow_cache[workflow_id]
            existing.execution_history.append(workflow_memory.execution_history[0])
            existing.execution_count += 1
            existing.last_executed = datetime.now()
            # Update success rate
            successful = sum(1 for h in existing.execution_history if h.get("success", False))
            existing.success_rate = successful / len(existing.execution_history) if existing.execution_history else 0.0
        else:
            self.workflow_cache[workflow_id] = workflow_memory

        # Save to disk
        self._save_workflows()

        # Store in memory manager
        if self.memory_manager:
            try:
                memory_content = json.dumps({
                    "workflow_id": workflow_id,
                    "workflow_name": workflow_name,
                    "workflow_type": workflow_type,
                    "building_blocks_count": len(building_blocks),
                    "success": success
                })

                self.memory_manager.store_memory(
                    content=memory_content,
                    session_id=execution_id,
                    memory_type=memory_tier.value,
                    tags=workflow_memory.tags,
                    priority=importance,
                    metadata=workflow_memory.metadata
                )
            except Exception as e:
                logger.warning(f"Failed to store in memory manager: {e}")

        # Store in R5
        if self.r5_system:
            try:
                r5_session = {
                    "session_id": f"workflow_{workflow_id}",
                    "timestamp": datetime.now().isoformat(),
                    "messages": [{
                        "role": "system",
                        "content": f"Workflow: {workflow_name} ({workflow_type}) - {len(building_blocks)} building blocks"
                    }],
                    "metadata": {
                        "workflow_id": workflow_id,
                        "workflow_type": workflow_type,
                        "building_blocks": len(building_blocks)
                    }
                }
                self.r5_system.ingest_session(r5_session)
            except Exception as e:
                logger.warning(f"Failed to store in R5: {e}")

        logger.info(f"Stored workflow {workflow_id} ({workflow_name}) in {memory_tier.value} memory")

        return workflow_id

    def retrieve_workflow(self, workflow_id: str) -> Optional[WorkflowMemory]:
        """Retrieve workflow from memory"""
        if workflow_id in self.workflow_cache:
            workflow = self.workflow_cache[workflow_id]
            workflow.building_blocks[0].access_count += 1  # Track access
            workflow.building_blocks[0].last_accessed = datetime.now()
            self._save_workflows()
            return workflow
        return None

    def search_workflows(
        self,
        query: str,
        workflow_type: Optional[str] = None,
        memory_tier: Optional[MemoryTier] = None,
        limit: int = 10
    ) -> List[WorkflowMemory]:
        """Search workflows by query"""
        results = []
        query_lower = query.lower()

        for workflow in self.workflow_cache.values():
            # Filter by type
            if workflow_type and workflow.workflow_type != workflow_type:
                continue

            # Filter by tier
            if memory_tier and workflow.memory_tier != memory_tier:
                continue

            # Search in name, description, tags
            score = 0
            if query_lower in workflow.workflow_name.lower():
                score += 2
            if any(query_lower in tag.lower() for tag in workflow.tags):
                score += 1
            if any(query_lower in block.description.lower() for block in workflow.building_blocks):
                score += 1

            if score > 0:
                results.append((workflow, score))

        # Sort by score and return
        results.sort(key=lambda x: x[1], reverse=True)
        return [workflow for workflow, score in results[:limit]]

    def promote_to_long_term(self, workflow_id: str) -> bool:
        """Promote workflow from short-term to long-term memory"""
        workflow = self.retrieve_workflow(workflow_id)
        if not workflow:
            return False

        workflow.memory_tier = MemoryTier.LONG_TERM
        workflow.importance = max(workflow.importance, 0.8)  # Increase importance

        self._save_workflows()

        # Update in memory manager
        if self.memory_manager:
            try:
                # Find and update memory entry
                memories = self.memory_manager.search_memories(
                    query=workflow.workflow_name,
                    memory_type="short_term"
                )
                for memory in memories:
                    if workflow_id in memory.content:
                        self.memory_manager.promote_to_long_term(memory.id)
                        break
            except Exception as e:
                logger.warning(f"Failed to promote in memory manager: {e}")

        logger.info(f"Promoted workflow {workflow_id} to long-term memory")
        return True

    def get_building_blocks(
        self,
        block_type: Optional[BuildingBlockType] = None,
        workflow_type: Optional[str] = None
    ) -> List[WorkflowBuildingBlock]:
        """Get all building blocks, optionally filtered"""
        blocks = []

        for workflow in self.workflow_cache.values():
            if workflow_type and workflow.workflow_type != workflow_type:
                continue

            for block in workflow.building_blocks:
                if block_type and block.block_type != block_type:
                    continue
                blocks.append(block)

        return blocks

    def get_workflow_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored workflows"""
        stats = {
            "total_workflows": len(self.workflow_cache),
            "by_tier": {},
            "by_type": {},
            "total_building_blocks": 0,
            "total_executions": 0,
            "average_success_rate": 0.0
        }

        total_success_rate = 0.0

        for workflow in self.workflow_cache.values():
            # By tier
            tier = workflow.memory_tier.value
            stats["by_tier"][tier] = stats["by_tier"].get(tier, 0) + 1

            # By type
            wf_type = workflow.workflow_type
            stats["by_type"][wf_type] = stats["by_type"].get(wf_type, 0) + 1

            # Building blocks
            stats["total_building_blocks"] += len(workflow.building_blocks)

            # Executions
            stats["total_executions"] += workflow.execution_count

            # Success rate
            total_success_rate += workflow.success_rate

        if len(self.workflow_cache) > 0:
            stats["average_success_rate"] = total_success_rate / len(self.workflow_cache)

        return stats


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Workflow Memory Persistence")
    parser.add_argument("--store", help="Store workflow from JSON file")
    parser.add_argument("--retrieve", help="Retrieve workflow by ID")
    parser.add_argument("--search", help="Search workflows")
    parser.add_argument("--promote", help="Promote workflow to long-term")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--blocks", help="Get building blocks (optional type filter)")

    args = parser.parse_args()

    persistence = WorkflowMemoryPersistence()

    if args.store:
        with open(args.store, 'r') as f:
            workflow_data = json.load(f)
        workflow_id = persistence.store_workflow(workflow_data)
        print(f"Stored workflow: {workflow_id}")

    elif args.retrieve:
        workflow = persistence.retrieve_workflow(args.retrieve)
        if workflow:
            print(json.dumps(workflow.to_dict(), indent=2))
        else:
            print("Workflow not found")

    elif args.search:
        workflows = persistence.search_workflows(args.search)
        print(f"Found {len(workflows)} workflows:")
        for wf in workflows:
            print(f"  - {wf.workflow_name} ({wf.workflow_id})")

    elif args.promote:
        success = persistence.promote_to_long_term(args.promote)
        print(f"Promotion: {'Success' if success else 'Failed'}")

    elif args.stats:
        stats = persistence.get_workflow_statistics()
        print(json.dumps(stats, indent=2))

    elif args.blocks:
        block_type = BuildingBlockType(args.blocks) if args.blocks else None
        blocks = persistence.get_building_blocks(block_type=block_type)
        print(f"Found {len(blocks)} building blocks")
        for block in blocks[:10]:  # Show first 10
            print(f"  - {block.name} ({block.block_type.value})")

    else:
        parser.print_help()

