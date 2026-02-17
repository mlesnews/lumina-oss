#!/usr/bin/env python3
"""
JARVIS Progress Tracker with Airport Signboard Display

Tracks all active processes across @jarvis, @ai, @agents, @subagents
Displays live progress in Cursor IDE footer with airport signboard side-scrolling effect.

@JARVIS @AI @AGENTS @SUBAGENTS #FRAMEWORK @PEAK #WORKFLOW #OPTIMIZATION @DYNO
"""

import json
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import logging

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISProgressTracker")


@dataclass
class ProcessProgress:
    """Individual process progress tracking"""
    process_id: str
    process_name: str
    source_name: str
    total_items: int
    completed_items: int
    started_at: datetime
    estimated_duration: Optional[timedelta] = None
    agent_type: str = "jarvis"  # jarvis, ai, agent, subagent
    status: str = "running"  # running, paused, completed, failed
    # Migration-specific metrics
    success_count: int = 0  # Files/items successfully processed (green +)
    failure_count: int = 0  # Files/items failed/removed (red -)
    is_auto: bool = True  # Auto indicator for automated processes

    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage"""
        if self.total_items == 0:
            return 0.0
        return min(100.0, (self.completed_items / self.total_items) * 100.0)

    @property
    def elapsed_time(self) -> timedelta:
        """Calculate elapsed time"""
        return datetime.now() - self.started_at

    @property
    def elapsed_time_string(self) -> str:
        """Get elapsed time as compact string (e.g., '3m', '1h 23m')"""
        elapsed = self.elapsed_time
        total_seconds = int(elapsed.total_seconds())

        if total_seconds < 60:
            return f"{total_seconds}s"
        elif total_seconds < 3600:
            minutes = total_seconds // 60
            return f"{minutes}m"
        else:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            if minutes > 0:
                return f"{hours}h {minutes}m"
            return f"{hours}h"

    @property
    def estimated_completion(self) -> Optional[datetime]:
        """Estimate completion time"""
        if self.total_items == 0 or self.completed_items == 0:
            return None

        if self.estimated_duration:
            return self.started_at + self.estimated_duration

        # Calculate ETA based on current rate
        elapsed = self.elapsed_time.total_seconds()

        # Minimum elapsed time for accurate ETA (5 seconds)
        if elapsed < 5:
            return None

        if self.completed_items > 0:
            rate = self.completed_items / elapsed  # items per second
            remaining = self.total_items - self.completed_items

            # Avoid unrealistic ETAs from bursts
            if rate > 0:
                eta_seconds = remaining / rate
                # Cap ETA at 1 year just in case
                eta_seconds = min(eta_seconds, 365 * 24 * 3600)
                return datetime.now() + timedelta(seconds=eta_seconds)

        return None

    @property
    def eta_string(self) -> str:
        """Get ETA as formatted string"""
        eta = self.estimated_completion
        if eta:
            remaining = eta - datetime.now()
            if remaining.total_seconds() < 0:
                return "Overdue"
            elif remaining.total_seconds() < 60:
                return f"{int(remaining.total_seconds())}s"
            elif remaining.total_seconds() < 600:
                # Under 10 minutes: show minutes and seconds
                minutes = int(remaining.total_seconds() / 60)
                seconds = int(remaining.total_seconds() % 60)
                return f"{minutes}m {seconds}s"
            elif remaining.total_seconds() < 3600:
                # Under 1 hour: show minutes
                return f"{int(remaining.total_seconds() / 60)}m"
            else:
                hours = int(remaining.total_seconds() / 3600)
                minutes = int((remaining.total_seconds() % 3600) / 60)
                return f"{hours}h {minutes}m"
        return "Calculating..."


@dataclass
class AggregateProgress:
    """Aggregate progress across all processes"""
    total_processes: int
    active_processes: int
    total_sources: int
    max_sources_processing: int
    overall_percentage: float
    total_completed: int
    total_items: int
    earliest_eta: Optional[datetime] = None
    processes: List[ProcessProgress] = field(default_factory=list)

    @property
    def eta_string(self) -> str:
        """Get earliest ETA as formatted string"""
        if self.earliest_eta:
            remaining = self.earliest_eta - datetime.now()
            if remaining.total_seconds() < 0:
                return "Overdue"
            elif remaining.total_seconds() < 60:
                return f"{int(remaining.total_seconds())}s"
            elif remaining.total_seconds() < 600:
                # Under 10 minutes: show minutes and seconds
                minutes = int(remaining.total_seconds() / 60)
                seconds = int(remaining.total_seconds() % 60)
                return f"{minutes}m {seconds}s"
            elif remaining.total_seconds() < 3600:
                # Under 1 hour: show minutes
                return f"{int(remaining.total_seconds() / 60)}m"
            else:
                hours = int(remaining.total_seconds() / 3600)
                minutes = int((remaining.total_seconds() % 3600) / 60)
                return f"{hours}h {minutes}m"
        return "Calculating..."


class JARVISProgressTracker:
    """
    Tracks progress across all JARVIS, AI, agents, and subagents processes.
    Provides live updates for Cursor IDE footer display.

    Default: @LUMINA @CORE as @BAU (Business As Usual)
    """

    def __init__(self, project_root: Optional[Path] = None, mode: str = "bau"):
        """
        Initialize progress tracker

        Args:
            project_root: Project root directory
            mode: Operating mode - "bau" (Business As Usual) is default for @LUMINA @CORE
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)

        # Default: @LUMINA @CORE as @BAU
        self.mode = mode.lower()  # bau = Business As Usual
        self.is_lumina_core = True  # Default to LUMINA CORE
        self.is_bau = (self.mode == "bau")  # Default to BAU mode
        self._running = False

        self.data_dir = self.project_root / "data" / "progress_tracking"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.progress_file = self.data_dir / "active_progress.json"
        self.cursor_status_file = self.data_dir / "cursor_status.json"

        self.processes: Dict[str, ProcessProgress] = {}
        self.lock = threading.RLock()

        # Load existing progress
        self._load_progress()

        # Airport signboard scrolling state
        self.scroll_position = 0
        self.scroll_direction = 1  # 1 for right, -1 for left
        self.scroll_speed = 1

        logger.info("✅ JARVIS Progress Tracker initialized")
        logger.info(f"   Mode: @LUMINA @CORE as @BAU (Business As Usual)")

    def register_process(self, process_id: str, process_name: str, source_name: str,
                        total_items: int, agent_type: str = "jarvis",
                        is_auto: bool = True) -> None:
        """Register a new process for tracking"""
        with self.lock:
            self.processes[process_id] = ProcessProgress(
                process_id=process_id,
                process_name=process_name,
                source_name=source_name,
                total_items=total_items,
                completed_items=0,
                started_at=datetime.now(),
                agent_type=agent_type,
                status="running",
                is_auto=is_auto
            )
            logger.info(f"📊 Registered process: {process_name} ({source_name}) - {total_items} items")
            self._save_progress()

    def update_progress(self, process_id: str, completed_items: int,
                       total_items: Optional[int] = None,
                       success_count: Optional[int] = None,
                       failure_count: Optional[int] = None) -> None:
        """Update progress for a process"""
        with self.lock:
            if process_id in self.processes:
                process = self.processes[process_id]
                process.completed_items = completed_items
                if total_items is not None:
                    process.total_items = total_items
                if success_count is not None:
                    process.success_count = success_count
                if failure_count is not None:
                    process.failure_count = failure_count
                self._save_progress()
                self._update_cursor_status()

    def complete_process(self, process_id: str) -> None:
        """Mark a process as completed"""
        with self.lock:
            if process_id in self.processes:
                process = self.processes[process_id]
                process.status = "completed"
                process.completed_items = process.total_items
                logger.info(f"✅ Completed process: {process.process_name}")
                self._save_progress()
                self._update_cursor_status()

    def fail_process(self, process_id: str, error: str = "") -> None:
        """Mark a process as failed"""
        with self.lock:
            if process_id in self.processes:
                process = self.processes[process_id]
                process.status = "failed"
                logger.warning(f"❌ Failed process: {process.process_name} - {error}")
                self._save_progress()
                self._update_cursor_status()

    def get_aggregate_progress(self) -> AggregateProgress:
        """Get aggregate progress across all processes"""
        with self.lock:
            active = [p for p in self.processes.values() if p.status == "running"]
            completed = [p for p in self.processes.values() if p.status == "completed"]

            total_items = sum(p.total_items for p in active + completed)
            total_completed = sum(p.completed_items for p in active + completed)

            overall_percentage = (total_completed / total_items * 100) if total_items > 0 else 0.0

            # Get unique sources
            sources = set(p.source_name for p in active)
            max_sources = len(sources)

            # Get earliest ETA
            etas = [p.estimated_completion for p in active if p.estimated_completion]
            earliest_eta = min(etas) if etas else None

            return AggregateProgress(
                total_processes=len(self.processes),
                active_processes=len(active),
                total_sources=len(sources),
                max_sources_processing=max_sources,
                overall_percentage=overall_percentage,
                total_completed=total_completed,
                total_items=total_items,
                earliest_eta=earliest_eta,
                processes=active
            )

    def _calculate_per_source_percentages(self, aggregate: AggregateProgress) -> Dict[str, Dict[str, Any]]:
        """Calculate progressive percentages per source"""
        per_source: Dict[str, Dict[str, Any]] = {}

        for p in aggregate.processes:
            source = p.source_name
            if source not in per_source:
                per_source[source] = {
                    "total_items": 0,
                    "completed_items": 0,
                    "processes": []
                }
            per_source[source]["total_items"] += p.total_items
            per_source[source]["completed_items"] += p.completed_items
            per_source[source]["processes"].append(p.process_id)

        # Calculate percentages
        for source, data in per_source.items():
            if data["total_items"] > 0:
                data["percentage"] = (data["completed_items"] / data["total_items"]) * 100.0
            else:
                data["percentage"] = 0.0

        return per_source

    def _generate_airport_signboard_text(self, aggregate: AggregateProgress, max_width: int = 60) -> str:
        """
        Generate airport signboard style scrolling text

        Handles overflow when footer widgets are too many - uses compact format
        and scrolling to fit within available space.

        For migration processes, shows: "3m +5143 -117 Auto"
        """
        # Check if we have migration-style processes (with success/failure counts)
        migration_processes = [p for p in aggregate.processes 
                              if p.success_count > 0 or p.failure_count > 0]

        if migration_processes and len(migration_processes) == 1:
            # Migration-style format: "3m +5143 -117 Auto"
            proc = migration_processes[0]
            elapsed = proc.elapsed_time_string
            success = f"+{proc.success_count}" if proc.success_count > 0 else ""
            failure = f"-{proc.failure_count}" if proc.failure_count > 0 else ""
            auto = "Auto" if proc.is_auto else ""

            parts = [elapsed]
            if success:
                parts.append(success)
            if failure:
                parts.append(failure)
            if auto:
                parts.append(auto)

            migration_text = " ".join(parts)

            # Add process name if space allows
            process_name = proc.process_name[:15]
            full_text = f"{migration_text} | {process_name}"

            if len(full_text) <= max_width:
                return full_text.ljust(max_width)
            else:
                # Just show migration stats, truncate name if needed
                return migration_text.ljust(max_width)

        # Standard format for non-migration processes
        # Compact format for limited footer space
        # Priority: Progress % > Sources > ETA > Process names (scroll)

        # Core info (always visible if space allows)
        core_text = f"JARVIS {aggregate.overall_percentage:.0f}%"

        # Compact source info
        if aggregate.max_sources_processing > 0:
            core_text += f" | {aggregate.max_sources_processing}S"

        # Compact ETA
        if aggregate.eta_string and aggregate.eta_string != "Calculating...":
            eta_short = aggregate.eta_string.replace(" ", "").replace("h", "h").replace("m", "m")
            core_text += f" | ETA:{eta_short}"

        # Process names (scroll if too long)
        if aggregate.processes:
            if len(aggregate.processes) == 1:
                process_text = aggregate.processes[0].process_name[:15]
            else:
                process_names = [p.process_name[:10] for p in aggregate.processes[:2]]
                process_text = ",".join(process_names)
                if len(aggregate.processes) > 2:
                    process_text += f"+{len(aggregate.processes)-2}"

            # Calculate if we need scrolling
            full_text = f"{core_text} | {process_text}"

            if len(full_text) <= max_width:
                # Fits - no scrolling needed
                return full_text.ljust(max_width)
            else:
                # Too long - use scrolling for process names
                # Core stays visible, process names scroll
                scrollable_text = process_text
                padding = " " * 20
                scroll_content = padding + scrollable_text + padding

                # Update scroll position
                max_scroll = len(scroll_content) - (max_width - len(core_text) - 3)

                if self.scroll_position >= max_scroll:
                    self.scroll_direction = -1
                elif self.scroll_position <= 0:
                    self.scroll_direction = 1

                self.scroll_position += self.scroll_direction * self.scroll_speed
                self.scroll_position = max(0, min(self.scroll_position, max_scroll))

                # Extract scrolling portion
                scroll_start = self.scroll_position
                scroll_end = scroll_start + (max_width - len(core_text) - 3)
                scrolling_part = scroll_content[scroll_start:scroll_end]

                return f"{core_text} | {scrolling_part}".ljust(max_width)

        # No processes - just core info
        return core_text.ljust(max_width)

    def _update_cursor_status(self) -> None:
        """Update Cursor IDE status file"""
        aggregate = self.get_aggregate_progress()

        # Generate compact signboard text (adapts to available space)
        signboard_text = self._generate_airport_signboard_text(aggregate, max_width=60)

        # Also generate expanded version for tooltip/details
        expanded_text = f"JARVIS: {aggregate.overall_percentage:.1f}% | "
        expanded_text += f"Sources: {aggregate.max_sources_processing}/{aggregate.total_sources} | "
        expanded_text += f"Active: {aggregate.active_processes} | "
        expanded_text += f"ETA: {aggregate.eta_string}"

        status_data = {
            "timestamp": datetime.now().isoformat(),
            "aggregate": {
                "overall_percentage": aggregate.overall_percentage,
                "max_sources_processing": aggregate.max_sources_processing,
                "total_sources": aggregate.total_sources,
                "active_processes": aggregate.active_processes,
                "eta": aggregate.eta_string,
                "total_completed": aggregate.total_completed,
                "total_items": aggregate.total_items,
                "progressive_percentage": aggregate.overall_percentage  # Progressive tracking
            },
            "progressive": {
                "overall": aggregate.overall_percentage,
                "per_process": {
                    p.process_id: {
                        "name": p.process_name,
                        "percentage": p.progress_percentage,
                        "completed": p.completed_items,
                        "total": p.total_items
                    }
                    for p in aggregate.processes
                },
                "per_source": self._calculate_per_source_percentages(aggregate)
            },
            "signboard_text": signboard_text,  # Compact scrolling version
            "expanded_text": expanded_text,    # Full version for tooltip
            "compact": True,  # Flag indicating compact mode
            "mode": self.mode,  # Operating mode
            "is_lumina_core": self.is_lumina_core,  # @LUMINA @CORE flag
            "is_bau": self.is_bau,  # @BAU (Business As Usual) flag
            "processes": [
                {
                    "id": p.process_id,
                    "name": p.process_name,
                    "source": p.source_name,
                    "progress": p.progress_percentage,
                    "eta": p.eta_string,
                    "agent_type": p.agent_type
                }
                for p in aggregate.processes
            ]
        }

        try:
            with open(self.cursor_status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"⚠️  Error updating Cursor status: {e}")

    def _save_progress(self) -> None:
        """Save progress to file"""
        try:
            progress_data = {
                "timestamp": datetime.now().isoformat(),
                "processes": {
                    pid: {
                        "process_id": p.process_id,
                        "process_name": p.process_name,
                        "source_name": p.source_name,
                        "total_items": p.total_items,
                        "completed_items": p.completed_items,
                        "started_at": p.started_at.isoformat(),
                        "status": p.status,
                        "agent_type": p.agent_type
                    }
                    for pid, p in self.processes.items()
                }
            }

            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress_data, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"⚠️  Error saving progress: {e}")

    def _load_progress(self) -> None:
        """Load progress from file"""
        if not self.progress_file.exists():
            return

        try:
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for pid, p_data in data.get("processes", {}).items():
                self.processes[pid] = ProcessProgress(
                    process_id=p_data["process_id"],
                    process_name=p_data["process_name"],
                    source_name=p_data["source_name"],
                    total_items=p_data["total_items"],
                    completed_items=p_data["completed_items"],
                    started_at=datetime.fromisoformat(p_data["started_at"]),
                    agent_type=p_data.get("agent_type", "jarvis"),
                    status=p_data.get("status", "running")
                )
            logger.info(f"📂 Loaded {len(self.processes)} processes from history")
        except Exception as e:
            logger.warning(f"⚠️  Error loading progress: {e}")

    def start_status_updater(self, interval: float = 0.5) -> threading.Thread:
        """
        Start background thread to update status with progressive percentages

        Default interval: 0.5s for live monitoring
        """
        self._running = True
        def updater():
            while self._running:
                try:
                    # Update cursor status with progressive percentages
                    self._update_cursor_status()
                    time.sleep(interval)
                except Exception as e:
                    logger.error(f"❌ Status updater error: {e}")
                    time.sleep(interval)

        thread = threading.Thread(target=updater, daemon=True)
        thread.start()
        logger.info(f"✅ Status updater started (interval: {interval}s) - LIVE MONITORING")
        return thread

    def stop_status_updater(self):
        """Stop the status updater thread"""
        self._running = False


# Global tracker instance
_global_tracker: Optional[JARVISProgressTracker] = None


def get_progress_tracker(project_root: Optional[Path] = None, mode: str = "bau", auto_start: bool = False) -> JARVISProgressTracker:
    """
    Get or create global progress tracker

    Default: @LUMINA @CORE as @BAU (Business As Usual)

    Args:
        project_root: Project root directory
        mode: Operating mode - "bau" (Business As Usual) is default
        auto_start: If True, start background status updater
    """
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = JARVISProgressTracker(project_root, mode=mode)
        if auto_start:
            _global_tracker.start_status_updater()
    return _global_tracker


if __name__ == "__main__":
    # Test the progress tracker
    tracker = get_progress_tracker()

    # Register some test processes
    tracker.register_process("test1", "Star Wars Import", "Star Wars Explained", 100, "jarvis")
    tracker.register_process("test2", "EWTN Import", "EWTN Channel", 50, "agent")

    # Simulate progress
    for i in range(10):
        tracker.update_progress("test1", i * 10)
        tracker.update_progress("test2", i * 5)
        time.sleep(0.5)
        aggregate = tracker.get_aggregate_progress()
        print(f"Progress: {aggregate.overall_percentage:.1f}% | ETA: {aggregate.eta_string} | Sources: {aggregate.max_sources_processing}")

    tracker.complete_process("test1")
    tracker.complete_process("test2")
