#!/usr/bin/env python3
"""
Ciao Session Resumer
Resumes interrupted Ciao sessions using triage and merge

Features:
- Finds all interrupted Ciao sessions
- Uses triage system to prioritize
- Merges related sessions
- Resumes all from this window with full visibility
"""

import sys
import json
import time
import psutil
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from aiq_triage_jedi import AIQTriageRouter, TriageResult, TriagePriority
except ImportError:
    AIQTriageRouter = None
    TriageResult = None
    TriagePriority = None

logger = get_logger("CiaoSessionResumer")

@dataclass
class InterruptedSession:
    """Represents an interrupted Ciao session"""
    session_id: str
    file_path: Path
    timestamp: datetime
    messages: List[Dict[str, Any]]
    last_message: Optional[str] = None
    completion_status: str = "interrupted"  # interrupted, incomplete, error
    metadata: Dict[str, Any] = field(default_factory=dict)
    triage_priority: Optional[str] = None
    triage_category: Optional[str] = None
    related_sessions: List[str] = field(default_factory=list)

@dataclass
class SessionGroup:
    """Group of related sessions to merge"""
    group_id: str
    sessions: List[InterruptedSession]
    merged_content: List[Dict[str, Any]] = field(default_factory=list)
    priority: str = "Routine"
    category: str = "general"

@dataclass
class ResourceStats:
    """System resource statistics"""
    cpu_percent: float
    memory_percent: float
    cpu_count: int
    available_memory_mb: float
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ProcessingStats:
    """Processing statistics for adaptive adjustment"""
    total_processed: int = 0
    successful: int = 0
    failed: int = 0
    avg_processing_time: float = 0.0
    cpu_usage_history: List[float] = field(default_factory=list)
    memory_usage_history: List[float] = field(default_factory=list)
    stagger_delays: Dict[str, float] = field(default_factory=dict)
    last_adjustment: Optional[datetime] = None

class CiaoSessionResumer:
    """
    Resumes interrupted Ciao sessions using triage and merge

    Workflow:
    1. Find all interrupted Ciao sessions
    2. Triage each session to determine priority
    3. Group related sessions for merging
    4. Merge sessions in each group
    5. Resume processing from this window
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = get_logger("CiaoSessionResumer")

        # Data directories
        self.sessions_dir = self.project_root / "data" / "r5_living_matrix" / "sessions"
        self.output_dir = self.project_root / "data" / "ciao_resumed"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Triage router
        self.triage_router = None
        if AIQTriageRouter:
            try:
                self.triage_router = AIQTriageRouter(mcp_server_url="http://localhost:8000")
                self.logger.info("✅ Triage router initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  Triage router unavailable: {e}")

        # Session tracking
        self.interrupted_sessions: List[InterruptedSession] = []
        self.session_groups: List[SessionGroup] = []

        # Resource monitoring
        self.stats = ProcessingStats()
        self.max_cpu_percent = 75.0  # Max CPU before throttling
        self.max_memory_percent = 80.0  # Max memory before throttling
        self.base_stagger_delays = {
            "Immediate": 0.5,  # 0.5 seconds
            "Urgent": 1.0,      # 1 second
            "Elevated": 2.0,    # 2 seconds
            "Routine": 5.0      # 5 seconds
        }
        self.stats.stagger_delays = self.base_stagger_delays.copy()

        # Auto-startup flag
        self.auto_startup_enabled = True
        self.startup_delay = 10.0  # Wait 10 seconds after IDE startup

        self.logger.info("🔍 Ciao Session Resumer initialized")
        self.logger.info(f"   Sessions directory: {self.sessions_dir}")
        self.logger.info(f"   Output directory: {self.output_dir}")
        self.logger.info(f"   Auto-startup: {self.auto_startup_enabled}")
        self.logger.info(f"   Resource limits: CPU {self.max_cpu_percent}%, Memory {self.max_memory_percent}%")

    def find_interrupted_sessions(self, pattern: str = "*ciao*", include_all: bool = True) -> List[InterruptedSession]:
        """
        Find all interrupted Ciao sessions

        Looks for:
        - Sessions with 'ciao' in filename or content (if include_all=False)
        - ALL sessions that appear incomplete/interrupted (if include_all=True)
        - Sessions with error indicators
        """
        self.logger.info("🔍 Finding interrupted Ciao sessions...")

        interrupted = []

        # Search for sessions
        if include_all:
            # Check ALL sessions for interruption indicators
            search_patterns = ["*.json"]
        else:
            # Only check Ciao sessions
            search_patterns = [
                "*ciao*",
                "*Ciao*",
                "*CIAO*",
                "*.json"  # Check all sessions for Ciao references
            ]

        session_files = []
        for pattern in search_patterns:
            session_files.extend(self.sessions_dir.glob(pattern))

        # Remove duplicates
        session_files = list(set(session_files))

        self.logger.info(f"   Found {len(session_files)} potential session files")

        for session_file in session_files:
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)

                # Get basic session data
                session_id = session_data.get("session_id", session_file.stem)
                messages = session_data.get("messages", [])
                metadata = session_data.get("metadata", {})

                # Check if this is a Ciao session (if not including all)
                is_ciao = include_all  # If including all, treat all as potential Ciao

                if not include_all:
                    # Check filename
                    if "ciao" in session_file.name.lower():
                        is_ciao = True

                    # Check content
                    for msg in messages:
                        content = msg.get("content", "").lower()
                        if "ciao" in content or "interrupted" in content or "resume" in content:
                            is_ciao = True
                            break

                    # Check metadata
                    if "ciao" in str(metadata).lower() or "interrupted" in str(metadata).lower():
                        is_ciao = True

                # Determine if interrupted
                is_interrupted = False
                completion_status = "complete"

                # Check for interruption indicators
                if len(messages) == 0:
                    is_interrupted = True
                    completion_status = "empty"
                elif len(messages) < 3:
                    is_interrupted = True
                    completion_status = "incomplete"
                else:
                    # Check last message for interruption
                    last_msg = messages[-1].get("content", "")
                    if any(word in last_msg.lower() for word in ["interrupted", "error", "failed", "incomplete", "resume", "ciao"]):
                        is_interrupted = True
                        completion_status = "error"

                    # Check if session seems incomplete (very short, no clear ending)
                    if len(messages) < 5 and not any(word in last_msg.lower() for word in ["complete", "done", "finished", "resolved"]):
                        is_interrupted = True
                        completion_status = "incomplete"

                # If it's a Ciao session (or we're including all) and interrupted, add it
                if is_ciao and is_interrupted:
                    timestamp_str = session_data.get("timestamp", datetime.now().isoformat())
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str)
                    except:
                        timestamp = datetime.fromtimestamp(session_file.stat().st_mtime)

                    interrupted_session = InterruptedSession(
                        session_id=session_id,
                        file_path=session_file,
                        timestamp=timestamp,
                        messages=messages,
                        last_message=messages[-1].get("content", "") if messages else None,
                        completion_status=completion_status,
                        metadata=metadata
                    )

                    interrupted.append(interrupted_session)
                    self.logger.info(f"   ✅ Found interrupted Ciao session: {session_id} ({completion_status})")

            except Exception as e:
                self.logger.warning(f"   ⚠️  Error reading {session_file}: {e}")
                continue

        self.interrupted_sessions = interrupted
        self.logger.info(f"📊 Found {len(interrupted)} interrupted Ciao sessions")

        return interrupted

    def triage_sessions(self) -> None:
        """Triage all interrupted sessions to determine priority"""
        self.logger.info("🏥 Triaging interrupted sessions...")

        if not self.triage_router:
            self.logger.warning("⚠️  Triage router unavailable, using default priorities")
            for session in self.interrupted_sessions:
                session.triage_priority = "Routine"
                session.triage_category = "general"
            return

        for session in self.interrupted_sessions:
            try:
                # Create issue text from session
                issue_text = f"Interrupted Ciao session: {session.session_id}\n"
                issue_text += f"Status: {session.completion_status}\n"
                if session.last_message:
                    issue_text += f"Last message: {session.last_message[:200]}"

                # Triage the session
                triage_result = self.triage_router.triage_issue(issue_text)

                session.triage_priority = triage_result.priority
                session.triage_category = triage_result.category

                self.logger.info(f"   ✅ {session.session_id}: {triage_result.priority} - {triage_result.category}")

            except Exception as e:
                self.logger.warning(f"   ⚠️  Triage failed for {session.session_id}: {e}")
                session.triage_priority = "Routine"
                session.triage_category = "general"

    def group_related_sessions(self) -> List[SessionGroup]:
        """Group related sessions for merging"""
        self.logger.info("🔗 Grouping related sessions for merging...")

        groups: Dict[str, List[InterruptedSession]] = defaultdict(list)

        # Group by category and similar content
        for session in self.interrupted_sessions:
            # Create group key from category and similar topics
            category = session.triage_category or "general"

            # Extract topic keywords from messages
            keywords = []
            for msg in session.messages[:5]:  # Check first 5 messages
                content = msg.get("content", "").lower()
                # Simple keyword extraction
                words = content.split()[:10]  # First 10 words
                keywords.extend([w for w in words if len(w) > 4])

            # Create group key
            group_key = f"{category}_{hash(tuple(keywords[:5]))}"
            groups[group_key].append(session)

        # Create SessionGroup objects
        session_groups = []
        for i, (group_key, sessions) in enumerate(groups.items()):
            # Determine group priority (highest priority in group)
            priorities = [s.triage_priority or "Routine" for s in sessions]
            priority_order = ["Immediate", "Urgent", "Elevated", "Routine"]
            group_priority = min(priorities, key=lambda p: priority_order.index(p) if p in priority_order else 999)

            group = SessionGroup(
                group_id=f"group_{i+1:03d}",
                sessions=sessions,
                priority=group_priority,
                category=sessions[0].triage_category or "general"
            )

            session_groups.append(group)
            self.logger.info(f"   ✅ Group {group.group_id}: {len(sessions)} sessions, priority: {group_priority}")

        self.session_groups = session_groups
        self.logger.info(f"📊 Created {len(session_groups)} session groups")

        return session_groups

    def get_resource_stats(self) -> ResourceStats:
        """Get current system resource statistics"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()

        return ResourceStats(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            cpu_count=os.cpu_count() or 1,
            available_memory_mb=memory.available / (1024 * 1024)
        )

    def should_throttle(self) -> bool:
        """Check if processing should be throttled due to resource constraints"""
        stats = self.get_resource_stats()

        # Update history
        self.stats.cpu_usage_history.append(stats.cpu_percent)
        self.stats.memory_usage_history.append(stats.memory_percent)

        # Keep only last 100 readings
        if len(self.stats.cpu_usage_history) > 100:
            self.stats.cpu_usage_history = self.stats.cpu_usage_history[-100:]
        if len(self.stats.memory_usage_history) > 100:
            self.stats.memory_usage_history = self.stats.memory_usage_history[-100:]

        return (stats.cpu_percent > self.max_cpu_percent or 
                stats.memory_percent > self.max_memory_percent)

    def calculate_stagger_delay(self, priority: str) -> float:
        """Calculate stagger delay based on priority and system load"""
        base_delay = self.stats.stagger_delays.get(priority, 5.0)

        # Adjust based on CPU load
        if self.stats.cpu_usage_history:
            avg_cpu = sum(self.stats.cpu_usage_history[-10:]) / min(10, len(self.stats.cpu_usage_history))

            if avg_cpu > 80:
                # High CPU - increase delays significantly
                multiplier = 2.0
            elif avg_cpu > 60:
                # Medium CPU - moderate increase
                multiplier = 1.5
            elif avg_cpu > 40:
                # Normal CPU - slight increase
                multiplier = 1.2
            else:
                # Low CPU - normal delays
                multiplier = 1.0

            adjusted_delay = base_delay * multiplier
        else:
            adjusted_delay = base_delay

        return adjusted_delay

    def adaptive_adjustment(self) -> None:
        """Adaptively adjust processing parameters based on statistics"""
        if not self.stats.cpu_usage_history or len(self.stats.cpu_usage_history) < 10:
            return

        # Only adjust every 30 seconds
        if self.stats.last_adjustment:
            if (datetime.now() - self.stats.last_adjustment).total_seconds() < 30:
                return

        avg_cpu = sum(self.stats.cpu_usage_history[-20:]) / min(20, len(self.stats.cpu_usage_history))
        avg_memory = sum(self.stats.memory_usage_history[-20:]) / min(20, len(self.stats.memory_usage_history))

        # Adjust stagger delays based on system load
        if avg_cpu > 70 or avg_memory > 75:
            # System under load - increase delays
            for priority in self.stats.stagger_delays:
                self.stats.stagger_delays[priority] = self.base_stagger_delays[priority] * 1.5
            self.logger.info(f"📊 System under load (CPU: {avg_cpu:.1f}%, Memory: {avg_memory:.1f}%) - Increased stagger delays")
        elif avg_cpu < 40 and avg_memory < 50:
            # System has capacity - decrease delays
            for priority in self.stats.stagger_delays:
                self.stats.stagger_delays[priority] = self.base_stagger_delays[priority] * 0.8
            self.logger.info(f"📊 System has capacity (CPU: {avg_cpu:.1f}%, Memory: {avg_memory:.1f}%) - Decreased stagger delays")
        else:
            # Reset to base delays
            self.stats.stagger_delays = self.base_stagger_delays.copy()

        self.stats.last_adjustment = datetime.now()

    def merge_session_group(self, group: SessionGroup) -> Dict[str, Any]:
        """Merge sessions in a group"""
        self.logger.info(f"🔀 Merging group {group.group_id} ({len(group.sessions)} sessions)...")

        merged_messages = []
        merged_metadata = {}
        all_patterns = []
        all_whatifs = []

        # Sort sessions by timestamp
        sorted_sessions = sorted(group.sessions, key=lambda s: s.timestamp)

        for session in sorted_sessions:
            # Add session messages
            merged_messages.extend(session.messages)

            # Merge metadata
            merged_metadata.update(session.metadata)

            # Collect patterns and whatifs
            if "patterns" in session.metadata:
                all_patterns.extend(session.metadata.get("patterns", []))
            if "whatif_scenarios" in session.metadata:
                all_whatifs.extend(session.metadata.get("whatif_scenarios", []))

        # Create merged session
        merged_session = {
            "session_id": f"merged_{group.group_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "messages": merged_messages,
            "metadata": {
                **merged_metadata,
                "merged_from": [s.session_id for s in sorted_sessions],
                "merge_timestamp": datetime.now().isoformat(),
                "original_count": len(sorted_sessions),
                "patterns": list(set(all_patterns)),
                "whatif_scenarios": list(set(all_whatifs))
            },
            "triage_priority": group.priority,
            "triage_category": group.category
        }

        group.merged_content = merged_messages

        self.logger.info(f"   ✅ Merged {len(sorted_sessions)} sessions into {len(merged_messages)} messages")

        return merged_session

    def resume_sessions(self) -> Dict[str, Any]:
        try:
            """
            Resume all interrupted sessions

            This is the main workflow that runs everything from this window
            """
            self.logger.info("=" * 80)
            self.logger.info("🚀 RESUMING CIAO SESSIONS")
            self.logger.info("=" * 80)
            self.logger.info("")

            # Step 1: Find interrupted sessions
            self.logger.info("STEP 1: Finding interrupted Ciao sessions...")
            # Try with include_all=True to find ALL interrupted sessions
            interrupted = self.find_interrupted_sessions(include_all=True)
            self.logger.info(f"   Found {len(interrupted)} interrupted sessions")
            self.logger.info("")

            if not interrupted:
                self.logger.warning("⚠️  No interrupted Ciao sessions found")
                return {"status": "no_sessions", "resumed": 0}

            # Step 2: Triage sessions
            self.logger.info("STEP 2: Triaging sessions...")
            self.triage_sessions()
            self.logger.info("   Triaging complete")
            self.logger.info("")

            # Step 3: Group related sessions
            self.logger.info("STEP 3: Grouping related sessions for merging...")
            groups = self.group_related_sessions()
            self.logger.info(f"   Created {len(groups)} groups")
            self.logger.info("")

            # Step 4: Merge sessions with staggered processing
            self.logger.info("STEP 4: Merging session groups (staggered by triage priority)...")

            # Sort groups by priority (Immediate > Urgent > Elevated > Routine)
            priority_order = {"Immediate": 0, "Urgent": 1, "Elevated": 2, "Routine": 3}
            sorted_groups = sorted(groups, key=lambda g: priority_order.get(g.priority, 999))

            merged_sessions = []
            for i, group in enumerate(sorted_groups):
                # Check resource constraints
                if self.should_throttle():
                    self.logger.warning(f"   ⚠️  System resources high, pausing before group {group.group_id}")
                    time.sleep(2.0)

                # Calculate stagger delay based on priority
                stagger_delay = self.calculate_stagger_delay(group.priority)

                if i > 0:  # Don't delay first group
                    self.logger.info(f"   ⏳ Staggering {stagger_delay:.1f}s for {group.priority} priority group {group.group_id}")
                    time.sleep(stagger_delay)

                # Merge the group
                merged = self.merge_session_group(group)
                merged_sessions.append(merged)

                # Update statistics
                self.stats.total_processed += 1
                self.stats.successful += 1

                # Adaptive adjustment
                if i % 5 == 0:  # Adjust every 5 groups
                    self.adaptive_adjustment()

            self.logger.info(f"   Merged {len(merged_sessions)} session groups")
            self.logger.info("")

            # Step 5: Save merged sessions
            self.logger.info("STEP 5: Saving resumed sessions...")
            resumed_count = 0
            for merged in merged_sessions:
                output_file = self.output_dir / f"{merged['session_id']}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(merged, f, indent=2, ensure_ascii=False)
                resumed_count += 1
                self.logger.info(f"   ✅ Saved: {output_file.name}")

            self.logger.info("")
            self.logger.info("=" * 80)
            self.logger.info(f"✅ RESUMED {resumed_count} CIAO SESSIONS")
            self.logger.info("=" * 80)

            # Create summary report
            summary = {
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "interrupted_sessions_found": len(interrupted),
                "groups_created": len(groups),
                "sessions_resumed": resumed_count,
                "sessions_by_priority": {},
                "merged_sessions": merged_sessions
            }

            # Count by priority
            for session in interrupted:
                priority = session.triage_priority or "Unknown"
                summary["sessions_by_priority"][priority] = summary["sessions_by_priority"].get(priority, 0) + 1

            # Save summary
            summary_file = self.output_dir / f"resume_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)

            self.logger.info(f"📄 Summary saved: {summary_file.name}")

            return summary

        except Exception as e:
            self.logger.error(f"Error in resume_sessions: {e}", exc_info=True)
            raise
    def check_auto_startup(self) -> bool:
        try:
            """Check if this should run automatically on IDE startup"""
            if not self.auto_startup_enabled:
                return False

            # Check for startup flag file
            startup_flag = self.project_root / "data" / "ciao_resumed" / ".auto_startup"

            # Check if IDE just started (within last 5 minutes)
            if startup_flag.exists():
                flag_time = datetime.fromtimestamp(startup_flag.stat().st_mtime)
                if (datetime.now() - flag_time).total_seconds() < 300:  # 5 minutes
                    return True

            return False

        except Exception as e:
            self.logger.error(f"Error in check_auto_startup: {e}", exc_info=True)
            raise
    def setup_auto_startup(self) -> None:
        """Setup auto-startup on IDE initialization"""
        startup_flag = self.project_root / "data" / "ciao_resumed" / ".auto_startup"
        startup_flag.parent.mkdir(parents=True, exist_ok=True)
        startup_flag.touch()
        self.logger.info("✅ Auto-startup flag created")

def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Resume interrupted Ciao sessions")
        parser.add_argument("--project-root", help="Project root directory")
        parser.add_argument("--pattern", default="*ciao*", help="Session file pattern")
        parser.add_argument("--auto-startup", action="store_true", help="Run automatically on IDE startup")
        parser.add_argument("--startup-delay", type=float, default=10.0, help="Delay after IDE startup (seconds)")
        parser.add_argument("--max-cpu", type=float, default=75.0, help="Max CPU percent before throttling")
        parser.add_argument("--max-memory", type=float, default=80.0, help="Max memory percent before throttling")

        args = parser.parse_args()

        project_root = Path(args.project_root) if args.project_root else None

        resumer = CiaoSessionResumer(project_root=project_root)

        # Configure resource limits
        resumer.max_cpu_percent = args.max_cpu
        resumer.max_memory_percent = args.max_memory
        resumer.startup_delay = args.startup_delay

        # Handle auto-startup
        if args.auto_startup:
            resumer.setup_auto_startup()
            resumer.logger.info(f"⏳ Waiting {resumer.startup_delay}s after IDE startup...")
            time.sleep(resumer.startup_delay)

        # Check if should run automatically
        if resumer.check_auto_startup():
            resumer.logger.info("🚀 Auto-startup detected - resuming sessions...")

        # Get initial resource stats
        initial_stats = resumer.get_resource_stats()
        resumer.logger.info(f"📊 Initial system state: CPU {initial_stats.cpu_percent:.1f}%, Memory {initial_stats.memory_percent:.1f}%")

        # Resume sessions
        summary = resumer.resume_sessions()

        # Final statistics
        final_stats = resumer.get_resource_stats()

        print("\n" + "=" * 80)
        print("📊 SUMMARY")
        print("=" * 80)
        print(f"Interrupted sessions found: {summary.get('interrupted_sessions_found', 0)}")
        print(f"Groups created: {summary.get('groups_created', 0)}")
        print(f"Sessions resumed: {summary.get('sessions_resumed', 0)}")
        print(f"\nBy priority:")
        for priority, count in summary.get('sessions_by_priority', {}).items():
            print(f"  {priority}: {count}")
        print(f"\nResource Usage:")
        print(f"  Initial: CPU {initial_stats.cpu_percent:.1f}%, Memory {initial_stats.memory_percent:.1f}%")
        print(f"  Final: CPU {final_stats.cpu_percent:.1f}%, Memory {final_stats.memory_percent:.1f}%")
        print(f"  Processed: {resumer.stats.total_processed}, Successful: {resumer.stats.successful}")
        print()

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()