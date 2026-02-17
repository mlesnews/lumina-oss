#!/usr/bin/env python3
"""
Cognitive Load-Aware Workflow System

Respects human cognitive limitations:
- 4 hours truly productive per day (sourced)
- <5 minutes average attention span (sourced)
- Multitasking degrades performance (sourced)
- Brain energy usage (fact-checked)

Features:
- Workflow chunking for <5min attention spans
- Daily productivity limits (4hr focus time)
- Single-tasking enforcement
- Cognitive load monitoring
- Break recommendations

Tags: #COGNITIVE #LOAD #WORKFLOW #HUMAN #PERFORMANCE #PRODUCTIVITY @JARVIS @TEAM
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CognitiveLoadAwareWorkflow")


class CognitiveLoadLevel(Enum):
    """Cognitive load levels"""
    LOW = "low"  # <2 hours focused work
    MEDIUM = "medium"  # 2-4 hours focused work
    HIGH = "high"  # >4 hours (needs break)
    CRITICAL = "critical"  # >6 hours (mandatory break)


@dataclass
class CognitiveMetrics:
    """Cognitive performance metrics"""
    # Sourced from research (see documentation)
    max_daily_productive_hours: float = 4.0  # Sourced: Research on daily productivity
    average_attention_span_minutes: float = 5.0  # Sourced: Modern attention span research
    multitasking_performance_degradation: float = 0.4  # Sourced: Multitasking research (40% degradation)
    brain_energy_percentage: float = 20.0  # Sourced: Brain energy usage (20%, not 10%)

    # Current session metrics
    current_focus_time_hours: float = 0.0
    current_attention_span_remaining: float = 5.0  # minutes
    tasks_in_progress: int = 0
    last_break_time: Optional[datetime] = None
    break_duration_minutes: float = 0.0

    # Performance tracking
    productivity_score: float = 1.0  # 1.0 = optimal, <1.0 = degraded
    cognitive_load_level: CognitiveLoadLevel = CognitiveLoadLevel.LOW


@dataclass
class WorkflowChunk:
    """A chunk of work optimized for attention span"""
    chunk_id: str
    workflow_id: str
    chunk_name: str
    estimated_duration_minutes: float
    max_duration_minutes: float = 5.0  # Default: attention span limit
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    completed: bool = False
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class CognitiveLoadAwareWorkflowSystem:
    """
    Cognitive Load-Aware Workflow System

    Manages workflows with respect to human cognitive limitations.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Cognitive Load-Aware Workflow System"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "cognitive_workflows"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Metrics storage
        self.metrics_file = self.data_dir / "cognitive_metrics.json"
        self.chunks_file = self.data_dir / "workflow_chunks.json"

        # Load metrics
        self.metrics = self._load_metrics()
        self.chunks: Dict[str, WorkflowChunk] = {}
        self._load_chunks()

        logger.info("✅ Cognitive Load-Aware Workflow System initialized")
        logger.info(f"   Max daily productive hours: {self.metrics.max_daily_productive_hours}")
        logger.info(f"   Average attention span: {self.metrics.average_attention_span_minutes} minutes")
        logger.info(f"   Multitasking degradation: {self.metrics.multitasking_performance_degradation * 100}%")

    def _load_metrics(self) -> CognitiveMetrics:
        """Load cognitive metrics"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert datetime strings
                    if data.get("last_break_time"):
                        data["last_break_time"] = datetime.fromisoformat(data["last_break_time"])
                    data["cognitive_load_level"] = CognitiveLoadLevel(data["cognitive_load_level"])
                    return CognitiveMetrics(**data)
            except Exception as e:
                logger.warning(f"⚠️  Error loading metrics: {e}")

        return CognitiveMetrics()

    def _save_metrics(self):
        """Save cognitive metrics"""
        try:
            data = {
                "max_daily_productive_hours": self.metrics.max_daily_productive_hours,
                "average_attention_span_minutes": self.metrics.average_attention_span_minutes,
                "multitasking_performance_degradation": self.metrics.multitasking_performance_degradation,
                "brain_energy_percentage": self.metrics.brain_energy_percentage,
                "current_focus_time_hours": self.metrics.current_focus_time_hours,
                "current_attention_span_remaining": self.metrics.current_attention_span_remaining,
                "tasks_in_progress": self.metrics.tasks_in_progress,
                "last_break_time": self.metrics.last_break_time.isoformat() if self.metrics.last_break_time else None,
                "break_duration_minutes": self.metrics.break_duration_minutes,
                "productivity_score": self.metrics.productivity_score,
                "cognitive_load_level": self.metrics.cognitive_load_level.value,
                "updated_at": datetime.now().isoformat()
            }

            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Error saving metrics: {e}")

    def _load_chunks(self):
        """Load workflow chunks"""
        if self.chunks_file.exists():
            try:
                with open(self.chunks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for chunk_id, chunk_data in data.get("chunks", {}).items():
                        if chunk_data.get("started_at"):
                            chunk_data["started_at"] = datetime.fromisoformat(chunk_data["started_at"])
                        if chunk_data.get("completed_at"):
                            chunk_data["completed_at"] = datetime.fromisoformat(chunk_data["completed_at"])
                        self.chunks[chunk_id] = WorkflowChunk(**chunk_data)
            except Exception as e:
                logger.warning(f"⚠️  Error loading chunks: {e}")

    def _save_chunks(self):
        """Save workflow chunks"""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "chunks": {}
            }
            for chunk_id, chunk in self.chunks.items():
                chunk_dict = {
                    "chunk_id": chunk.chunk_id,
                    "workflow_id": chunk.workflow_id,
                    "chunk_name": chunk.chunk_name,
                    "estimated_duration_minutes": chunk.estimated_duration_minutes,
                    "max_duration_minutes": chunk.max_duration_minutes,
                    "description": chunk.description,
                    "dependencies": chunk.dependencies,
                    "completed": chunk.completed,
                    "started_at": chunk.started_at.isoformat() if chunk.started_at else None,
                    "completed_at": chunk.completed_at.isoformat() if chunk.completed_at else None
                }
                data["chunks"][chunk_id] = chunk_dict

            with open(self.chunks_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"❌ Error saving chunks: {e}")

    def chunk_workflow(self, workflow_id: str, workflow_name: str, total_duration_minutes: float, steps: List[Dict[str, Any]]) -> List[WorkflowChunk]:
        """Chunk workflow into attention-span-sized pieces"""
        logger.info(f"📦 Chunking workflow: {workflow_name} ({total_duration_minutes} minutes)")

        chunks = []
        max_chunk_duration = self.metrics.average_attention_span_minutes

        # Calculate number of chunks needed
        num_chunks = max(1, int(total_duration_minutes / max_chunk_duration) + (1 if total_duration_minutes % max_chunk_duration > 0 else 0))

        # Distribute steps across chunks
        steps_per_chunk = max(1, len(steps) // num_chunks)

        for i in range(num_chunks):
            chunk_id = f"{workflow_id}_chunk_{i+1}"
            start_idx = i * steps_per_chunk
            end_idx = min((i + 1) * steps_per_chunk, len(steps))
            chunk_steps = steps[start_idx:end_idx]

            chunk_duration = min(max_chunk_duration, total_duration_minutes / num_chunks)

            chunk = WorkflowChunk(
                chunk_id=chunk_id,
                workflow_id=workflow_id,
                chunk_name=f"{workflow_name} - Part {i+1}/{num_chunks}",
                estimated_duration_minutes=chunk_duration,
                max_duration_minutes=max_chunk_duration,
                description=f"Chunk {i+1} of {num_chunks} for {workflow_name}",
                dependencies=[f"{workflow_id}_chunk_{j}" for j in range(i)] if i > 0 else []
            )

            chunks.append(chunk)
            self.chunks[chunk_id] = chunk

        self._save_chunks()
        logger.info(f"✅ Created {len(chunks)} chunks (max {max_chunk_duration} min each)")
        return chunks

    def check_cognitive_load(self) -> Dict[str, Any]:
        """Check current cognitive load and provide recommendations"""
        # Update metrics
        self._update_cognitive_metrics()

        recommendations = []
        warnings = []

        # Check daily productive hours
        if self.metrics.current_focus_time_hours >= self.metrics.max_daily_productive_hours:
            self.metrics.cognitive_load_level = CognitiveLoadLevel.HIGH
            recommendations.append("Take a break - reached daily productive hour limit")
            warnings.append("Productivity will degrade significantly beyond this point")

        # Check attention span
        if self.metrics.current_attention_span_remaining <= 0:
            recommendations.append("Take a short break (5-10 minutes) to reset attention")
            warnings.append("Attention span exhausted - focus will be degraded")

        # Check multitasking
        if self.metrics.tasks_in_progress > 1:
            degradation = self.metrics.multitasking_performance_degradation * self.metrics.tasks_in_progress
            self.metrics.productivity_score = max(0.1, 1.0 - degradation)
            recommendations.append(f"Reduce to single task - {self.metrics.tasks_in_progress} tasks active ({(degradation*100):.0f}% performance loss)")
            warnings.append("Multitasking significantly degrades performance")

        # Check break timing
        if self.metrics.last_break_time:
            time_since_break = datetime.now() - self.metrics.last_break_time
            if time_since_break.total_seconds() / 3600 > 2:  # 2 hours
                recommendations.append("Take a 15-minute break (2+ hours since last break)")

        return {
            "cognitive_load_level": self.metrics.cognitive_load_level.value,
            "productivity_score": self.metrics.productivity_score,
            "current_focus_time_hours": self.metrics.current_focus_time_hours,
            "attention_span_remaining_minutes": self.metrics.current_attention_span_remaining,
            "tasks_in_progress": self.metrics.tasks_in_progress,
            "recommendations": recommendations,
            "warnings": warnings,
            "can_continue": self.metrics.cognitive_load_level != CognitiveLoadLevel.CRITICAL
        }

    def _update_cognitive_metrics(self):
        """Update cognitive metrics based on current state"""
        # This would be called periodically or when tasks start/complete
        # For now, we'll update based on active chunks

        active_chunks = [c for c in self.chunks.values() if c.started_at and not c.completed]

        self.metrics.tasks_in_progress = len(active_chunks)

        # Calculate focus time (simplified - would track actual time)
        if active_chunks:
            oldest_start = min(c.started_at for c in active_chunks)
            focus_time = (datetime.now() - oldest_start).total_seconds() / 3600
            self.metrics.current_focus_time_hours = focus_time

        # Update attention span (decreases over time)
        if active_chunks:
            # Attention span decreases with time and multitasking
            base_attention = self.metrics.average_attention_span_minutes
            multitasking_penalty = (self.metrics.tasks_in_progress - 1) * 1.0  # 1 min per extra task
            self.metrics.current_attention_span_remaining = max(0, base_attention - multitasking_penalty)

        # Update cognitive load level
        if self.metrics.current_focus_time_hours >= 6:
            self.metrics.cognitive_load_level = CognitiveLoadLevel.CRITICAL
        elif self.metrics.current_focus_time_hours >= 4:
            self.metrics.cognitive_load_level = CognitiveLoadLevel.HIGH
        elif self.metrics.current_focus_time_hours >= 2:
            self.metrics.cognitive_load_level = CognitiveLoadLevel.MEDIUM
        else:
            self.metrics.cognitive_load_level = CognitiveLoadLevel.LOW

        self._save_metrics()

    def start_chunk(self, chunk_id: str) -> bool:
        """Start a workflow chunk"""
        if chunk_id not in self.chunks:
            logger.warning(f"⚠️  Chunk {chunk_id} not found")
            return False

        chunk = self.chunks[chunk_id]

        # Check cognitive load
        load_check = self.check_cognitive_load()
        if not load_check["can_continue"]:
            logger.warning(f"⚠️  Cannot start chunk - cognitive load too high: {load_check['cognitive_load_level']}")
            return False

        # Check dependencies
        for dep_id in chunk.dependencies:
            if dep_id not in self.chunks or not self.chunks[dep_id].completed:
                logger.warning(f"⚠️  Dependency {dep_id} not completed")
                return False

        chunk.started_at = datetime.now()
        self._save_chunks()
        self._update_cognitive_metrics()

        logger.info(f"✅ Started chunk: {chunk.chunk_name}")
        return True

    def complete_chunk(self, chunk_id: str) -> bool:
        """Complete a workflow chunk"""
        if chunk_id not in self.chunks:
            return False

        chunk = self.chunks[chunk_id]
        chunk.completed = True
        chunk.completed_at = datetime.now()

        # Reset attention span after completion
        self.metrics.current_attention_span_remaining = self.metrics.average_attention_span_minutes

        self._save_chunks()
        self._update_cognitive_metrics()

        logger.info(f"✅ Completed chunk: {chunk.chunk_name}")
        return True

    def recommend_break(self) -> Dict[str, Any]:
        """Recommend break based on cognitive load"""
        load_check = self.check_cognitive_load()

        if load_check["cognitive_load_level"] == CognitiveLoadLevel.CRITICAL:
            return {
                "break_needed": True,
                "break_duration_minutes": 30,
                "reason": "Critical cognitive load - mandatory break",
                "recommendations": [
                    "Step away from computer",
                    "Physical activity (walk, stretch)",
                    "Hydrate",
                    "Rest eyes"
                ]
            }
        elif load_check["cognitive_load_level"] == CognitiveLoadLevel.HIGH:
            return {
                "break_needed": True,
                "break_duration_minutes": 15,
                "reason": "High cognitive load - recommended break",
                "recommendations": [
                    "Short walk",
                    "Deep breathing",
                    "Hydrate"
                ]
            }
        elif self.metrics.current_attention_span_remaining <= 1:
            return {
                "break_needed": True,
                "break_duration_minutes": 5,
                "reason": "Attention span exhausted",
                "recommendations": [
                    "Quick stretch",
                    "Look away from screen",
                    "Deep breath"
                ]
            }
        else:
            return {
                "break_needed": False,
                "reason": "Cognitive load within acceptable limits"
            }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Cognitive Load-Aware Workflow System")
    parser.add_argument("--check", action="store_true", help="Check cognitive load")
    parser.add_argument("--chunk", type=str, nargs=3, metavar=("WORKFLOW_ID", "NAME", "DURATION"), help="Chunk a workflow")
    parser.add_argument("--start", type=str, help="Start a chunk")
    parser.add_argument("--complete", type=str, help="Complete a chunk")
    parser.add_argument("--break", action="store_true", dest="recommend_break", help="Recommend break")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("🧠 Cognitive Load-Aware Workflow System")
    print("="*80 + "\n")

    system = CognitiveLoadAwareWorkflowSystem()

    if args.check:
        load_check = system.check_cognitive_load()
        print(f"\n📊 COGNITIVE LOAD STATUS:")
        print(f"   Level: {load_check['cognitive_load_level']}")
        print(f"   Productivity Score: {load_check['productivity_score']:.2f}")
        print(f"   Focus Time: {load_check['current_focus_time_hours']:.2f} hours")
        print(f"   Attention Span Remaining: {load_check['attention_span_remaining_minutes']:.1f} minutes")
        print(f"   Tasks in Progress: {load_check['tasks_in_progress']}")
        if load_check.get('recommendations'):
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in load_check['recommendations']:
                print(f"   - {rec}")
        if load_check.get('warnings'):
            print(f"\n⚠️  WARNINGS:")
            for warn in load_check['warnings']:
                print(f"   - {warn}")
        print()

    elif args.chunk:
        workflow_id, name, duration = args.chunk
        chunks = system.chunk_workflow(workflow_id, name, float(duration), [])
        print(f"\n✅ Created {len(chunks)} chunks\n")

    elif args.start:
        success = system.start_chunk(args.start)
        print(f"\n{'✅ Started' if success else '❌ Failed to start'} chunk: {args.start}\n")

    elif args.complete:
        success = system.complete_chunk(args.complete)
        print(f"\n{'✅ Completed' if success else '❌ Failed to complete'} chunk: {args.complete}\n")

    elif args.recommend_break:
        break_rec = system.recommend_break()
        print(f"\n💤 BREAK RECOMMENDATION:")
        print(f"   Needed: {'Yes' if break_rec.get('break_needed') else 'No'}")
        if break_rec.get('break_needed'):
            print(f"   Duration: {break_rec.get('break_duration_minutes')} minutes")
            print(f"   Reason: {break_rec.get('reason')}")
            if break_rec.get('recommendations'):
                print(f"   Recommendations:")
                for rec in break_rec['recommendations']:
                    print(f"      - {rec}")
        print()

    else:
        print("Use --help for usage information\n")
