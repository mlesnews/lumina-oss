#!/usr/bin/env python3
"""
Resume All Agent Chat Sessions
Resumes interrupted/incomplete agent chat sessions after IDE restart with resource-aware staggering

Features:
- Finds all incomplete agent chat sessions (Cursor, VS Code, etc.)
- Triages by priority
- Staggers resumption to balance homelab resources
- Monitors system resources and adaptively adjusts
- Handles both Ciao sessions and general agent chat sessions
"""

import sys
import json
import time
import psutil
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ResumeAllAgentSessions")

@dataclass
class IncompleteSession:
    """Represents an incomplete agent chat session"""
    session_id: str
    file_path: Path
    timestamp: datetime
    source: str  # cursor, vscode, ciao, etc.
    priority: str = "Routine"  # Immediate, Urgent, Elevated, Routine
    estimated_load: float = 1.0  # Estimated resource load (0.0-10.0)
    messages: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ResourceState:
    """Current resource state"""
    cpu_percent: float
    memory_percent: float
    cpu_count: int
    available_memory_mb: float
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def load_factor(self) -> float:
        """Calculate overall load factor (0.0-1.0)"""
        cpu_load = self.cpu_percent / 100.0
        mem_load = self.memory_percent / 100.0
        return max(cpu_load, mem_load)

class AgentSessionResumer:
    """
    Resumes all incomplete agent chat sessions with resource-aware staggering
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = get_logger("AgentSessionResumer")

        # Data directories
        self.sessions_dir = self.project_root / "data" / "r5_living_matrix" / "sessions"
        self.cursor_chat_dir = Path.home() / ".cursor" / "User" / "globalStorage"
        self.output_dir = self.project_root / "data" / "resumed_sessions"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Resource limits
        self.max_cpu_percent = 75.0
        self.max_memory_percent = 80.0
        self.target_cpu_percent = 60.0
        self.target_memory_percent = 65.0

        # Stagger delays (seconds) - base delays by priority
        self.base_stagger_delays = {
            "Immediate": 1.0,
            "Urgent": 3.0,
            "Elevated": 5.0,
            "Routine": 10.0
        }

        # Incomplete sessions
        self.incomplete_sessions: List[IncompleteSession] = []

        self.logger.info("🔍 Agent Session Resumer initialized")
        self.logger.info(f"   Sessions directory: {self.sessions_dir}")
        self.logger.info(f"   Resource limits: CPU {self.max_cpu_percent}%, Memory {self.max_memory_percent}%")

    def get_resource_state(self) -> ResourceState:
        """Get current system resource state"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()

        return ResourceState(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            cpu_count=os.cpu_count() or 1,
            available_memory_mb=memory.available / (1024 * 1024)
        )

    def should_throttle(self, state: ResourceState) -> bool:
        """Check if should throttle based on resource state"""
        return (state.cpu_percent > self.max_cpu_percent or 
                state.memory_percent > self.max_memory_percent)

    def calculate_stagger_delay(self, session: IncompleteSession, current_state: ResourceState) -> float:
        """Calculate stagger delay based on priority and system load"""
        base_delay = self.base_stagger_delays.get(session.priority, 10.0)

        # Adjust based on current load
        load_factor = current_state.load_factor

        if load_factor > 0.8:
            # Very high load - significantly increase delay
            multiplier = 3.0
        elif load_factor > 0.7:
            # High load - increase delay
            multiplier = 2.0
        elif load_factor > 0.6:
            # Moderate load - slight increase
            multiplier = 1.5
        elif load_factor > 0.5:
            # Normal load - normal delay
            multiplier = 1.2
        else:
            # Low load - can proceed faster
            multiplier = 1.0

        # Adjust by session estimated load
        load_adjustment = 1.0 + (session.estimated_load * 0.1)

        final_delay = base_delay * multiplier * load_adjustment

        return final_delay

    def find_incomplete_sessions(self) -> List[IncompleteSession]:
        """Find all incomplete agent chat sessions"""
        self.logger.info("🔍 Finding incomplete agent chat sessions...")

        incomplete = []

        # Find R5 session files
        if self.sessions_dir.exists():
            for session_file in self.sessions_dir.glob("*.json"):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)

                    messages = session_data.get("messages", [])

                    # Determine if incomplete
                    is_incomplete = False
                    source = "unknown"
                    priority = "Routine"

                    # Check for interruption indicators
                    if len(messages) == 0:
                        is_incomplete = True
                    elif len(messages) < 3:
                        is_incomplete = True
                    else:
                        last_msg = messages[-1].get("content", "").lower()
                        if any(word in last_msg for word in ["interrupted", "error", "failed", "incomplete", "resume"]):
                            is_incomplete = True

                    # Check filename for source hints
                    filename_lower = session_file.name.lower()
                    if "ciao" in filename_lower:
                        source = "ciao"
                    elif "cursor" in filename_lower:
                        source = "cursor"
                    elif "vscode" in filename_lower or "code" in filename_lower:
                        source = "vscode"
                    else:
                        source = "r5_session"

                    if is_incomplete:
                        timestamp_str = session_data.get("timestamp", datetime.now().isoformat())
                        try:
                            timestamp = datetime.fromisoformat(timestamp_str)
                        except:
                            timestamp = datetime.fromtimestamp(session_file.stat().st_mtime)

                        # Estimate load based on message count
                        estimated_load = min(10.0, len(messages) * 0.5)

                        session = IncompleteSession(
                            session_id=session_data.get("session_id", session_file.stem),
                            file_path=session_file,
                            timestamp=timestamp,
                            source=source,
                            priority=priority,
                            estimated_load=estimated_load,
                            messages=messages
                        )

                        incomplete.append(session)
                        self.logger.info(f"   ✅ Found incomplete {source} session: {session.session_id}")

                except Exception as e:
                    self.logger.warning(f"   ⚠️  Error reading {session_file}: {e}")
                    continue

        # Sort by timestamp (oldest first) to prioritize older incomplete sessions
        incomplete.sort(key=lambda s: s.timestamp)

        self.incomplete_sessions = incomplete
        self.logger.info(f"📊 Found {len(incomplete)} incomplete sessions")

        return incomplete

    def triage_sessions(self) -> None:
        """Triage sessions to determine priority"""
        self.logger.info("🏥 Triaging sessions by priority...")

        # Simple triage logic - can be enhanced with AIQ triage router
        for session in self.incomplete_sessions:
            # Check session characteristics
            age_hours = (datetime.now() - session.timestamp).total_seconds() / 3600

            if age_hours < 1:
                session.priority = "Immediate"
            elif age_hours < 6:
                session.priority = "Urgent"
            elif age_hours < 24:
                session.priority = "Elevated"
            else:
                session.priority = "Routine"

            # Adjust based on message count (more messages = higher priority)
            if len(session.messages) > 20:
                if session.priority == "Routine":
                    session.priority = "Elevated"
                elif session.priority == "Elevated":
                    session.priority = "Urgent"

            self.logger.info(f"   {session.session_id}: {session.priority} (age: {age_hours:.1f}h, messages: {len(session.messages)})")

    def resume_session(self, session: IncompleteSession) -> bool:
        """Resume a single session"""
        try:
            self.logger.info(f"🔄 Resuming session: {session.session_id} ({session.source})")

            # Read session data
            with open(session.file_path, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            # Mark as resumed
            session_data["resumed"] = True
            session_data["resume_timestamp"] = datetime.now().isoformat()
            session_data["resume_priority"] = session.priority

            # Save resumed session
            output_file = self.output_dir / f"resumed_{session.session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"   ✅ Resumed: {output_file.name}")
            return True

        except Exception as e:
            self.logger.error(f"   ❌ Failed to resume {session.session_id}: {e}")
            return False

    def resume_all_sessions(self) -> Dict[str, Any]:
        try:
            """Resume all incomplete sessions with resource-aware staggering"""
            self.logger.info("=" * 80)
            self.logger.info("🚀 RESUMING ALL INCOMPLETE AGENT SESSIONS")
            self.logger.info("=" * 80)
            self.logger.info("")

            # Step 1: Find incomplete sessions
            self.logger.info("STEP 1: Finding incomplete sessions...")
            incomplete = self.find_incomplete_sessions()
            self.logger.info(f"   Found {len(incomplete)} incomplete sessions")
            self.logger.info("")

            if not incomplete:
                self.logger.warning("⚠️  No incomplete sessions found")
                return {"status": "no_sessions", "resumed": 0}

            # Step 2: Triage sessions
            self.logger.info("STEP 2: Triaging sessions...")
            self.triage_sessions()
            self.logger.info("")

            # Step 3: Sort by priority
            priority_order = {"Immediate": 0, "Urgent": 1, "Elevated": 2, "Routine": 3}
            sorted_sessions = sorted(self.incomplete_sessions, key=lambda s: priority_order.get(s.priority, 999))

            # Step 4: Resume with staggering
            self.logger.info("STEP 3: Resuming sessions with resource-aware staggering...")
            self.logger.info("")

            resumed_count = 0
            failed_count = 0
            skipped_count = 0

            for i, session in enumerate(sorted_sessions):
                # Check current resource state
                current_state = self.get_resource_state()

                # Throttle if needed
                if self.should_throttle(current_state):
                    self.logger.warning(f"   ⚠️  High resource usage (CPU: {current_state.cpu_percent:.1f}%, Memory: {current_state.memory_percent:.1f}%)")
                    self.logger.info(f"   ⏸️  Pausing for 5 seconds before resuming {session.session_id}...")
                    time.sleep(5.0)
                    current_state = self.get_resource_state()  # Re-check after pause

                # Calculate stagger delay
                stagger_delay = self.calculate_stagger_delay(session, current_state)

                if i > 0:  # Don't delay first session
                    self.logger.info(f"   ⏳ Staggering {stagger_delay:.1f}s before {session.priority} session: {session.session_id}")
                    time.sleep(stagger_delay)

                # Resume the session
                if self.resume_session(session):
                    resumed_count += 1
                else:
                    failed_count += 1

                # Log progress
                progress = ((i + 1) / len(sorted_sessions)) * 100
                self.logger.info(f"   📊 Progress: {i+1}/{len(sorted_sessions)} ({progress:.1f}%)")
                self.logger.info("")

            # Summary
            self.logger.info("=" * 80)
            self.logger.info("✅ RESUMPTION COMPLETE")
            self.logger.info("=" * 80)
            self.logger.info(f"   Total sessions: {len(sorted_sessions)}")
            self.logger.info(f"   Resumed: {resumed_count}")
            self.logger.info(f"   Failed: {failed_count}")
            self.logger.info(f"   Skipped: {skipped_count}")
            self.logger.info("")

            # Final resource state
            final_state = self.get_resource_state()
            self.logger.info(f"📊 Final resource state: CPU {final_state.cpu_percent:.1f}%, Memory {final_state.memory_percent:.1f}%")

            summary = {
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "total_sessions": len(sorted_sessions),
                "resumed": resumed_count,
                "failed": failed_count,
                "skipped": skipped_count,
                "by_priority": {},
                "by_source": {}
            }

            # Count by priority
            for session in sorted_sessions:
                priority = session.priority
                summary["by_priority"][priority] = summary["by_priority"].get(priority, 0) + 1
                source = session.source
                summary["by_source"][source] = summary["by_source"].get(source, 0) + 1

            # Save summary
            summary_file = self.output_dir / f"resume_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)

            self.logger.info(f"📄 Summary saved: {summary_file.name}")

            return summary

        except Exception as e:
            self.logger.error(f"Error in resume_all_sessions: {e}", exc_info=True)
            raise
def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Resume all incomplete agent chat sessions")
        parser.add_argument("--project-root", help="Project root directory")
        parser.add_argument("--max-cpu", type=float, default=75.0, help="Max CPU percent before throttling")
        parser.add_argument("--max-memory", type=float, default=80.0, help="Max memory percent before throttling")
        parser.add_argument("--target-cpu", type=float, default=60.0, help="Target CPU percent")
        parser.add_argument("--target-memory", type=float, default=65.0, help="Target memory percent")

        args = parser.parse_args()

        project_root = Path(args.project_root) if args.project_root else None

        resumer = AgentSessionResumer(project_root=project_root)

        # Configure resource limits
        resumer.max_cpu_percent = args.max_cpu
        resumer.max_memory_percent = args.max_memory
        resumer.target_cpu_percent = args.target_cpu
        resumer.target_memory_percent = args.target_memory

        # Get initial resource state
        initial_state = resumer.get_resource_state()
        resumer.logger.info(f"📊 Initial system state: CPU {initial_state.cpu_percent:.1f}%, Memory {initial_state.memory_percent:.1f}%")
        resumer.logger.info("")

        # Resume all sessions
        summary = resumer.resume_all_sessions()

        # Print summary
        print("\n" + "=" * 80)
        print("📊 SUMMARY")
        print("=" * 80)
        print(f"Total sessions: {summary.get('total_sessions', 0)}")
        print(f"Resumed: {summary.get('resumed', 0)}")
        print(f"Failed: {summary.get('failed', 0)}")
        print(f"Skipped: {summary.get('skipped', 0)}")
        print(f"\nBy priority:")
        for priority, count in summary.get('by_priority', {}).items():
            print(f"  {priority}: {count}")
        print(f"\nBy source:")
        for source, count in summary.get('by_source', {}).items():
            print(f"  {source}: {count}")
        print()

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":




    main()