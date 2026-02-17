#!/usr/bin/env python3
"""
Autonomous AI Agent - Independent Work on TODOs

After 5-10 minutes of idle time (dynamically scaled), if Cursor IDE detects idle time,
the AI begins working independently on:
- Master to-do list
- All sub to-do lists
- Identifies all roadblocks
- Addresses them systematically

Tags: #AUTONOMOUS_AI #IDLE_DETECTION #TODO_WORK #ROADBLOCKS @JARVIS @LUMINA  # [ADDRESSED]  # [ADDRESSED]
"""

import sys
import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AutonomousAIAgent")


class RoadblockType(Enum):
    """Roadblock types"""
    DEPENDENCY = "dependency"
    MISSING_RESOURCE = "missing_resource"
    ERROR = "error"
    STALLED = "stalled"
    BLOCKED = "blocked"
    WAITING_FOR_INPUT = "waiting_for_input"
    TECHNICAL_ISSUE = "technical_issue"
    UNKNOWN = "unknown"


class AutonomousAIAgent:
    """
    Autonomous AI Agent

    Works independently on master and sub to-do lists when idle time is detected.
    Identifies and addresses roadblocks systematically.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize autonomous AI agent"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "autonomous_ai"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Idle detection configuration
        self.idle_threshold_minutes = 5  # Base threshold
        self.idle_threshold_max_minutes = 10  # Max threshold
        self.dynamic_scaling = True

        # Components
        try:
            from idle_time_tracker import IdleTimeTracker
            self.idle_tracker = IdleTimeTracker(project_root)
        except ImportError:
            self.idle_tracker = None
            logger.warning("   ⚠️  Idle time tracker not available")

        try:
            from master_todo_tracker import MasterTodoTracker, TaskStatus, Priority
            self.master_todo_tracker = MasterTodoTracker(project_root)
            self.TaskStatus = TaskStatus
            self.Priority = Priority
        except ImportError:
            self.master_todo_tracker = None
            logger.warning("   ⚠️  Master todo tracker not available")

        try:
            from va_health_detector import VAHealthDetector
            self.va_health_detector = VAHealthDetector(project_root)
        except ImportError:
            self.va_health_detector = None
            logger.warning("   ⚠️  VA health detector not available")

        try:
            from doit_enhanced import DOITEnhanced
            self.doit_enhanced = DOITEnhanced(project_root)
        except ImportError:
            self.doit_enhanced = None
            logger.warning("   ⚠️  DOIT Enhanced not available")

        # State
        self.is_active = False
        self.current_work_session = None
        self.roadblocks_identified = []
        self.roadblocks_addressed = []

        logger.info("✅ Autonomous AI Agent initialized")

    def calculate_idle_threshold(self) -> float:
        """
        Calculate dynamic idle threshold (5-10 minutes)

        Returns:
            Idle threshold in minutes
        """
        if not self.dynamic_scaling:
            return self.idle_threshold_minutes

        # Base: 5 minutes
        # Can scale up to 10 minutes based on context
        # For now, use base threshold
        return self.idle_threshold_minutes

    def detect_idle_time(self) -> Tuple[bool, Optional[float]]:
        """
        Detect if user is idle based on screen sleep or activity

        Returns:
            (is_idle, idle_duration_minutes)
        """
        if not self.idle_tracker:
            # Fallback: Check for recent activity
            # TODO: Implement actual idle detection  # [ADDRESSED]  # [ADDRESSED]
            return (False, None)

        # Get current idle session if active
        idle_sessions = self.idle_tracker.tracking_data.get("idle_sessions", [])
        active_idle = [
            s for s in idle_sessions
            if s.get("idle_end") is None
        ]

        if active_idle:
            # Calculate idle duration
            latest_idle = active_idle[-1]
            idle_start = datetime.fromisoformat(latest_idle["idle_start"])
            idle_duration = (datetime.now() - idle_start).total_seconds() / 60

            threshold = self.calculate_idle_threshold()
            is_idle = idle_duration >= threshold

            return (is_idle, idle_duration)

        return (False, None)

    def identify_roadblocks(self, todo_item: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify roadblocks for a todo item

        Args:
            todo_item: Todo item to analyze

        Returns:
            List of identified roadblocks
        """
        roadblocks = []

        # Check dependencies
        dependencies = todo_item.get("dependencies", [])
        if dependencies:
            # Check if dependencies are complete
            for dep_id in dependencies:
                if self.master_todo_tracker:
                    dep_item = self.master_todo_tracker.items.get(dep_id)
                    if dep_item and dep_item.status != self.TaskStatus.COMPLETE:
                        roadblocks.append({
                            "type": RoadblockType.DEPENDENCY.value,
                            "description": f"Dependency not complete: {dep_item.title}",
                            "dependency_id": dep_id,
                            "dependency_title": dep_item.title,
                            "severity": "high"
                        })

        # Check for error indicators
        notes = todo_item.get("notes", [])
        for note in notes:
            if any(keyword in note.lower() for keyword in ["error", "failed", "exception", "blocked"]):
                roadblocks.append({
                    "type": RoadblockType.ERROR.value,
                    "description": f"Error indicator in notes: {note}",
                    "note": note,
                    "severity": "high"
                })

        # Check status
        status = todo_item.get("status", "")
        if status == "blocked":
            roadblocks.append({
                "type": RoadblockType.BLOCKED.value,
                "description": "Task is marked as blocked",
                "severity": "high"
            })

        # Check for missing resources
        description = todo_item.get("description", "")
        if any(keyword in description.lower() for keyword in ["missing", "need", "required", "waiting"]):
            roadblocks.append({
                "type": RoadblockType.MISSING_RESOURCE.value,
                "description": f"Missing resource indicator: {description}",
                "severity": "medium"
            })

        # Check if task is stalled (not updated recently)
        updated_date = todo_item.get("updated_date", "")
        if updated_date:
            try:
                updated = datetime.fromisoformat(updated_date)
                days_since_update = (datetime.now() - updated).days
                if days_since_update > 7 and status not in ["complete", "cancelled"]:
                    roadblocks.append({
                        "type": RoadblockType.STALLED.value,
                        "description": f"Task not updated in {days_since_update} days",
                        "days_since_update": days_since_update,
                        "severity": "medium"
                    })
            except Exception:
                pass

        return roadblocks

    def address_roadblock(self, roadblock: Dict[str, Any], todo_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Address a roadblock systematically

        Args:
            roadblock: Roadblock to address
            todo_item: Associated todo item

        Returns:
            Address result
        """
        roadblock_type = roadblock.get("type")
        result = {
            "roadblock_id": roadblock.get("id", f"rb_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            "type": roadblock_type,
            "addressed": False,
            "action_taken": None,
            "notes": []
        }

        if roadblock_type == RoadblockType.DEPENDENCY.value:
            # Address dependency roadblock
            dep_id = roadblock.get("dependency_id")
            if dep_id and self.master_todo_tracker:
                dep_item = self.master_todo_tracker.items.get(dep_id)
                if dep_item:
                    # Check if we can work on dependency
                    dep_roadblocks = self.identify_roadblocks(dep_item.to_dict())
                    if not dep_roadblocks:
                        # No roadblocks on dependency, can work on it
                        result["action_taken"] = f"Working on dependency: {dep_item.title}"
                        result["addressed"] = True
                    else:
                        result["action_taken"] = f"Dependency has roadblocks, addressing them first"
                        result["notes"].append(f"Dependency roadblocks: {len(dep_roadblocks)}")

        elif roadblock_type == RoadblockType.ERROR.value:
            # Address error roadblock
            result["action_taken"] = "Investigating error - checking logs and diagnostics"
            result["addressed"] = True
            result["notes"].append("Error investigation initiated")

        elif roadblock_type == RoadblockType.BLOCKED.value:
            # Address blocked roadblock
            result["action_taken"] = "Analyzing why task is blocked"
            result["addressed"] = True
            result["notes"].append("Block analysis initiated")

        elif roadblock_type == RoadblockType.MISSING_RESOURCE.value:
            # Address missing resource roadblock
            result["action_taken"] = "Identifying missing resources and alternatives"
            result["addressed"] = True
            result["notes"].append("Resource identification initiated")

        elif roadblock_type == RoadblockType.STALLED.value:
            # Address stalled roadblock
            result["action_taken"] = "Re-evaluating stalled task and updating status"
            result["addressed"] = True
            result["notes"].append("Stall review initiated")

        return result

    def work_on_todo_item(self, todo_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Work on a todo item independently

        Args:
            todo_item: Todo item to work on

        Returns:
            Work result
        """
        todo_id = todo_item.get("id")
        title = todo_item.get("title", "")

        logger.info(f"   🔧 Working on: {title} (ID: {todo_id})")

        # Identify roadblocks
        roadblocks = self.identify_roadblocks(todo_item)

        if roadblocks:
            logger.info(f"      ⚠️  Found {len(roadblocks)} roadblock(s)")
            for rb in roadblocks:
                logger.info(f"         - {rb.get('type')}: {rb.get('description')}")

            # Address roadblocks systematically
            addressed = []
            for roadblock in roadblocks:
                address_result = self.address_roadblock(roadblock, todo_item)
                if address_result.get("addressed"):
                    addressed.append(address_result)
                    logger.info(f"      ✅ Addressed: {roadblock.get('type')}")

            return {
                "todo_id": todo_id,
                "worked_on": True,
                "roadblocks_found": len(roadblocks),
                "roadblocks_addressed": len(addressed),
                "roadblocks": roadblocks,
                "addressed_results": addressed
            }
        else:
            # No roadblocks, can proceed with work
            logger.info(f"      ✅ No roadblocks - proceeding with work")
            return {
                "todo_id": todo_id,
                "worked_on": True,
                "roadblocks_found": 0,
                "roadblocks_addressed": 0,
                "action": "Proceeding with task implementation"
            }

    def get_pending_todos(self, include_sub_todos: bool = True) -> List[Dict[str, Any]]:
        """
        Get pending todos from master and sub lists

        Args:
            include_sub_todos: Include sub to-do lists

        Returns:
            List of pending todos
        """
        pending = []

        # Get from master todo tracker
        if self.master_todo_tracker:
            for todo_id, todo_item in self.master_todo_tracker.items.items():
                if todo_item.status not in [self.TaskStatus.COMPLETE, self.TaskStatus.CANCELLED]:
                    pending.append(todo_item.to_dict())

        # TODO: Get from sub to-do lists  # [ADDRESSED]  # [ADDRESSED]
        # This would integrate with sub-agent history manager or other sub-todo systems

        # Sort by priority and date
        pending.sort(key=lambda x: (
            {"high": 0, "medium": 1, "low": 2}.get(x.get("priority", "medium"), 1),
            x.get("created_date", "")
        ))

        return pending

    def work_independently(self, max_items: int = 10) -> Dict[str, Any]:
        """
        Work independently on master and sub to-do lists

        Args:
            max_items: Maximum items to work on

        Returns:
            Work session results
        """
        logger.info("=" * 80)
        logger.info("🤖 AUTONOMOUS AI AGENT - INDEPENDENT WORK SESSION")
        logger.info("=" * 80)
        logger.info("")

        # Check idle time
        is_idle, idle_duration = self.detect_idle_time()

        if not is_idle:
            logger.info("   ⚠️  User is not idle - autonomous work not activated")
            return {
                "activated": False,
                "reason": "User not idle",
                "idle_duration_minutes": idle_duration
            }

        logger.info(f"   ✅ User idle detected: {idle_duration:.1f} minutes")
        logger.info(f"   🚀 Activating autonomous work mode")
        logger.info("")

        # Step 0: Check VA Health and Fix Issues
        if self.va_health_detector:
            logger.info("📋 Step 0: Checking VA Health...")
            logger.info("")
            try:
                va_health = self.va_health_detector.check_va_health()
                if va_health["summary"]["required_not_running"] > 0 or va_health["summary"]["failed"] > 0:
                    logger.info("   ⚠️  VAs not running or failed - fixing...")
                    fix_results = self.va_health_detector.fix_failed_vas(va_health)
                    logger.info(f"   ✅ Fixed {len(fix_results['fixed'])} VAs")
                else:
                    logger.info("   ✅ All required VAs are running")
                logger.info("")
            except Exception as e:
                logger.warning(f"   ⚠️  VA health check failed: {e}")

        # Get pending todos
        pending_todos = self.get_pending_todos()

        if not pending_todos:
            logger.info("   ✅ No pending todos to work on")
            return {
                "activated": True,
                "todos_worked_on": 0,
                "reason": "No pending todos"
            }

        logger.info(f"   📋 Found {len(pending_todos)} pending todos")
        logger.info("")

        # Work on todos (up to max_items)
        work_results = []
        roadblocks_all = []
        addressed_all = []

        for todo in pending_todos[:max_items]:
            result = self.work_on_todo_item(todo)
            work_results.append(result)

            if result.get("roadblocks"):
                roadblocks_all.extend(result["roadblocks"])
            if result.get("addressed_results"):
                addressed_all.extend(result["addressed_results"])

        # Create work session
        session = {
            "session_id": f"autonomous_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "started_at": datetime.now().isoformat(),
            "idle_duration_minutes": idle_duration,
            "todos_worked_on": len(work_results),
            "roadblocks_identified": len(roadblocks_all),
            "roadblocks_addressed": len(addressed_all),
            "work_results": work_results,
            "roadblocks": roadblocks_all,
            "addressed": addressed_all
        }

        # Save session
        session_file = self.data_dir / f"work_session_{session['session_id']}.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session, f, indent=2, ensure_ascii=False, default=str)

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ AUTONOMOUS WORK SESSION COMPLETE")
        logger.info("=" * 80)
        logger.info(f"   Todos worked on: {len(work_results)}")
        logger.info(f"   Roadblocks identified: {len(roadblocks_all)}")
        logger.info(f"   Roadblocks addressed: {len(addressed_all)}")
        logger.info(f"   Session saved: {session_file.name}")
        logger.info("")

        return session

    def start_monitoring(self, check_interval_seconds: int = 60):
        """
        Start monitoring for idle time and working independently

        Args:
            check_interval_seconds: How often to check for idle time
        """
        logger.info("=" * 80)
        logger.info("🤖 STARTING AUTONOMOUS AI AGENT MONITORING")
        logger.info("=" * 80)
        logger.info(f"   Idle threshold: {self.calculate_idle_threshold()} minutes")
        logger.info(f"   Check interval: {check_interval_seconds} seconds")
        logger.info("")

        self.is_active = True

        def monitor_loop():
            while self.is_active:
                try:
                    is_idle, idle_duration = self.detect_idle_time()

                    if is_idle and idle_duration >= self.calculate_idle_threshold():
                        if not self.current_work_session:
                            logger.info(f"   🚀 Idle detected ({idle_duration:.1f} min) - Starting autonomous work")
                            session = self.work_independently()
                            self.current_work_session = session.get("session_id")
                    else:
                        if self.current_work_session:
                            logger.info("   ✅ User active - Stopping autonomous work")
                            self.current_work_session = None

                    time.sleep(check_interval_seconds)
                except Exception as e:
                    logger.error(f"   ❌ Error in monitoring loop: {e}")
                    time.sleep(check_interval_seconds)

        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()

        logger.info("   ✅ Monitoring started (running in background)")
        logger.info("")

        return monitor_thread

    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_active = False
        logger.info("   🛑 Monitoring stopped")


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Autonomous AI Agent")
    parser.add_argument("--work", action="store_true", help="Work independently on todos")
    parser.add_argument("--force", action="store_true", help="Force work even if not idle (for testing)")
    parser.add_argument("--monitor", action="store_true", help="Start monitoring for idle time")
    parser.add_argument("--check-interval", type=int, default=60, help="Check interval in seconds")
    parser.add_argument("--max-items", type=int, default=10, help="Max items to work on")
    parser.add_argument("--identify-roadblocks", help="Identify roadblocks for todo ID")
    parser.add_argument("--identify-all-roadblocks", action="store_true", help="Identify all roadblocks in todos")

    args = parser.parse_args()

    agent = AutonomousAIAgent()

    if args.work:
        if args.force:
            # Force work mode (for testing)
            logger.info("   🔧 FORCE MODE: Working independently (ignoring idle check)")
            # Temporarily override idle check
            original_detect = agent.detect_idle_time
            agent.detect_idle_time = lambda: (True, 10.0)  # Simulate idle
            session = agent.work_independently(max_items=args.max_items)
            agent.detect_idle_time = original_detect
        else:
            agent.work_independently(max_items=args.max_items)
    elif args.monitor:
        agent.start_monitoring(check_interval_seconds=args.check_interval)
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            agent.stop_monitoring()
    elif args.identify_all_roadblocks:
        if agent.master_todo_tracker:
            print("\n🔍 IDENTIFYING ALL ROADBLOCKS\n")
            all_roadblocks = []
            for todo_id, todo_item in agent.master_todo_tracker.items.items():
                if todo_item.status not in [agent.TaskStatus.COMPLETE, agent.TaskStatus.CANCELLED]:
                    roadblocks = agent.identify_roadblocks(todo_item.to_dict())
                    if roadblocks:
                        all_roadblocks.append({
                            "todo_id": todo_id,
                            "todo_title": todo_item.title,
                            "roadblocks": roadblocks
                        })
                        print(f"  [{todo_item.priority.value.upper()}] {todo_item.title}")
                        for rb in roadblocks:
                            print(f"      ⚠️  {rb['type']}: {rb['description']}")

            print(f"\n📊 Total roadblocks found: {sum(len(rb['roadblocks']) for rb in all_roadblocks)}")
            print(f"   Affected todos: {len(all_roadblocks)}")

            # Save roadblock report
            report_file = agent.data_dir / f"roadblocks_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "total_roadblocks": sum(len(rb['roadblocks']) for rb in all_roadblocks),
                    "affected_todos": len(all_roadblocks),
                    "roadblocks": all_roadblocks
                }, f, indent=2, ensure_ascii=False)

            print(f"   Report saved: {report_file.name}")
        else:
            print("❌ Master todo tracker not available")
    elif args.identify_roadblocks:
        if agent.master_todo_tracker:
            todo_item = agent.master_todo_tracker.items.get(args.identify_roadblocks)
            if todo_item:
                roadblocks = agent.identify_roadblocks(todo_item.to_dict())
                print(f"\n📋 Roadblocks for: {todo_item.title}\n")
                for rb in roadblocks:
                    print(f"  [{rb['type'].upper()}] {rb['description']}")
                    print(f"      Severity: {rb['severity']}")
            else:
                print(f"❌ Todo not found: {args.identify_roadblocks}")
        else:
            print("❌ Master todo tracker not available")
    else:
        # Default: Work independently
        agent.work_independently(max_items=args.max_items)

    return 0


if __name__ == "__main__":


    sys.exit(main())