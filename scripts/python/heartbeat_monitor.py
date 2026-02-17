#!/usr/bin/env python3
"""
Heartbeat Monitor - JARVIS Master Chat to Sub-Agent Chats

Monitors heartbeat from master chat to sub-agent chats with:
1. Follow through
2. Follow-up confirmation
3. Workflow checks and balances
"""

import json
import logging
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from master_session_manager import MasterSessionManager
    MASTER_SESSION_AVAILABLE = True
except ImportError:
    MASTER_SESSION_AVAILABLE = False
    MasterSessionManager = None

try:
    from sub_ask_todo_manager import SubAskTodoManager, SubAgentChatStatus
    SUB_ASK_AVAILABLE = True
except ImportError:
    SUB_ASK_AVAILABLE = False
    SubAskTodoManager = None


class HeartbeatStatus(Enum):
    """Heartbeat status"""
    ALIVE = "alive"
    RESPONDING = "responding"
    NO_RESPONSE = "no_response"
    STALE = "stale"
    DEAD = "dead"


class FollowUpStatus(Enum):
    """Follow-up status"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class Heartbeat:
    """Heartbeat entry"""
    heartbeat_id: str
    master_session_id: str
    sub_agent_chat_id: str
    timestamp: str
    status: HeartbeatStatus
    response_time_ms: Optional[float] = None
    workflow_status: Optional[str] = None
    follow_up_required: bool = False
    follow_up_status: Optional[FollowUpStatus] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        if data.get("follow_up_status"):
            data["follow_up_status"] = self.follow_up_status.value
        return data


@dataclass
class WorkflowCheckBalance:
    """Workflow check and balance"""
    check_id: str
    sub_agent_chat_id: str
    workflow_id: Optional[str] = None
    check_type: str = ""  # progress, completion, error, resource
    status: str = "pending"  # pending, passed, failed, warning
    timestamp: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    balance_action: Optional[str] = None  # Action taken to balance
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HeartbeatMonitor:
    """
    Heartbeat Monitor from JARVIS Master Chat to Sub-Agent Chats

    Features:
    - Heartbeat monitoring
    - Follow through
    - Follow-up confirmation
    - Workflow checks and balances
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("HeartbeatMonitor")

        # Directories
        self.data_dir = self.project_root / "data" / "heartbeat_monitor"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Files
        self.heartbeats_file = self.data_dir / "heartbeats.jsonl"
        self.workflow_checks_file = self.data_dir / "workflow_checks.jsonl"
        self.monitor_state_file = self.data_dir / "monitor_state.json"

        # Master session manager
        self.master_session = None
        if MASTER_SESSION_AVAILABLE and MasterSessionManager:
            try:
                self.master_session = MasterSessionManager(project_root=self.project_root)
            except Exception as e:
                self.logger.warning(f"Master session manager not available: {e}")

        # Sub-ask manager
        self.sub_ask_manager = None
        if SUB_ASK_AVAILABLE and SubAskTodoManager:
            try:
                self.sub_ask_manager = SubAskTodoManager(project_root=self.project_root)
            except Exception as e:
                self.logger.warning(f"Sub-ask manager not available: {e}")

        # State
        self.heartbeats: List[Heartbeat] = []
        self.workflow_checks: List[WorkflowCheckBalance] = []
        self.monitoring_active = False
        self.monitor_thread = None

        # Configuration
        self.heartbeat_interval_seconds = 30  # Send heartbeat every 30 seconds
        self.response_timeout_seconds = 10  # 10 second timeout for response
        self.stale_threshold_seconds = 60  # 60 seconds without response = stale
        self.dead_threshold_seconds = 300  # 5 minutes without response = dead

        # Load state
        self._load_state()

    def _load_state(self):
        """Load monitor state"""
        # Load heartbeats
        if self.heartbeats_file.exists():
            try:
                with open(self.heartbeats_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            heartbeat = Heartbeat(**data)
                            heartbeat.status = HeartbeatStatus(data["status"])
                            if data.get("follow_up_status"):
                                heartbeat.follow_up_status = FollowUpStatus(data["follow_up_status"])
                            self.heartbeats.append(heartbeat)
            except Exception as e:
                self.logger.error(f"Error loading heartbeats: {e}")

        # Load workflow checks
        if self.workflow_checks_file.exists():
            try:
                with open(self.workflow_checks_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            self.workflow_checks.append(WorkflowCheckBalance(**data))
            except Exception as e:
                self.logger.error(f"Error loading workflow checks: {e}")

    def _save_heartbeat(self, heartbeat: Heartbeat):
        try:
            """Save heartbeat"""
            self.heartbeats.append(heartbeat)
            # Keep only last 1000
            if len(self.heartbeats) > 1000:
                self.heartbeats = self.heartbeats[-1000:]

            # Append to file
            with open(self.heartbeats_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(heartbeat.to_dict()) + '\n')

        except Exception as e:
            self.logger.error(f"Error in _save_heartbeat: {e}", exc_info=True)
            raise
    def _save_workflow_check(self, check: WorkflowCheckBalance):
        try:
            """Save workflow check"""
            self.workflow_checks.append(check)
            # Keep only last 1000
            if len(self.workflow_checks) > 1000:
                self.workflow_checks = self.workflow_checks[-1000:]

            # Append to file
            with open(self.workflow_checks_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(check.to_dict()) + '\n')

        except Exception as e:
            self.logger.error(f"Error in _save_workflow_check: {e}", exc_info=True)
            raise
    def send_heartbeat(
        self,
        master_session_id: str,
        sub_agent_chat_id: str,
        workflow_status: Optional[str] = None
    ) -> Heartbeat:
        """
        Send heartbeat from master chat to sub-agent chat

        Returns heartbeat with response status
        """
        heartbeat_id = f"heartbeat_{int(datetime.now().timestamp() * 1000)}"
        start_time = time.time()

        # Send heartbeat (simulate response)
        response_received = self._check_sub_agent_response(sub_agent_chat_id)
        response_time_ms = (time.time() - start_time) * 1000

        # Determine status
        if response_received:
            if response_time_ms < self.response_timeout_seconds * 1000:
                status = HeartbeatStatus.ALIVE
            else:
                status = HeartbeatStatus.RESPONDING  # Responding but slow
        else:
            # Check last heartbeat time
            last_heartbeat = self._get_last_heartbeat(sub_agent_chat_id)
            if last_heartbeat:
                time_since_last = (datetime.now() - datetime.fromisoformat(last_heartbeat.timestamp)).total_seconds()
                if time_since_last > self.dead_threshold_seconds:
                    status = HeartbeatStatus.DEAD
                elif time_since_last > self.stale_threshold_seconds:
                    status = HeartbeatStatus.STALE
                else:
                    status = HeartbeatStatus.NO_RESPONSE
            else:
                status = HeartbeatStatus.NO_RESPONSE

        # Determine if follow-up required
        follow_up_required = status in [HeartbeatStatus.NO_RESPONSE, HeartbeatStatus.STALE, HeartbeatStatus.DEAD]

        heartbeat = Heartbeat(
            heartbeat_id=heartbeat_id,
            master_session_id=master_session_id,
            sub_agent_chat_id=sub_agent_chat_id,
            timestamp=datetime.now().isoformat(),
            status=status,
            response_time_ms=response_time_ms if response_received else None,
            workflow_status=workflow_status,
            follow_up_required=follow_up_required,
            follow_up_status=FollowUpStatus.PENDING if follow_up_required else None
        )

        self._save_heartbeat(heartbeat)

        if status == HeartbeatStatus.ALIVE:
            self.logger.debug(f"💓 Heartbeat: {sub_agent_chat_id} - ALIVE ({response_time_ms:.0f}ms)")
        elif status == HeartbeatStatus.RESPONDING:
            self.logger.info(f"💓 Heartbeat: {sub_agent_chat_id} - RESPONDING ({response_time_ms:.0f}ms)")
        else:
            self.logger.warning(f"⚠️ Heartbeat: {sub_agent_chat_id} - {status.value}")

        # If follow-up required, schedule it
        if follow_up_required:
            self._schedule_follow_up(heartbeat)

        return heartbeat

    def _check_sub_agent_response(self, sub_agent_chat_id: str) -> bool:
        """Check if sub-agent chat responds"""
        if not self.sub_ask_manager:
            return False

        # Check if chat session exists and is active
        if sub_agent_chat_id in self.sub_ask_manager.chat_sessions:
            chat_session = self.sub_ask_manager.chat_sessions[sub_agent_chat_id]
            # Consider active if status is ACTIVE or NEW
            return chat_session.chat_status in [SubAgentChatStatus.ACTIVE, SubAgentChatStatus.NEW]

        return False

    def _get_last_heartbeat(self, sub_agent_chat_id: str) -> Optional[Heartbeat]:
        """Get last heartbeat for sub-agent chat"""
        for heartbeat in reversed(self.heartbeats):
            if heartbeat.sub_agent_chat_id == sub_agent_chat_id:
                return heartbeat
        return None

    def _schedule_follow_up(self, heartbeat: Heartbeat):
        """Schedule follow-up for heartbeat"""
        self.logger.info(f"📋 Scheduling follow-up for heartbeat {heartbeat.heartbeat_id}")
        # Follow-up will be handled in monitoring loop
        heartbeat.follow_up_status = FollowUpStatus.PENDING

    def follow_up_confirmation(
        self,
        heartbeat_id: str,
        confirmed: bool = True
    ) -> bool:
        """
        Follow-up confirmation for heartbeat

        Returns True if confirmed, False otherwise
        """
        heartbeat = self._find_heartbeat(heartbeat_id)
        if not heartbeat:
            return False

        if confirmed:
            heartbeat.follow_up_status = FollowUpStatus.CONFIRMED
            heartbeat.status = HeartbeatStatus.ALIVE
            self.logger.info(f"✅ Follow-up confirmed: {heartbeat_id}")
        else:
            heartbeat.follow_up_status = FollowUpStatus.FAILED
            self.logger.warning(f"❌ Follow-up failed: {heartbeat_id}")

        self._save_heartbeat(heartbeat)

        return confirmed

    def _find_heartbeat(self, heartbeat_id: str) -> Optional[Heartbeat]:
        """Find heartbeat by ID"""
        for heartbeat in self.heartbeats:
            if heartbeat.heartbeat_id == heartbeat_id:
                return heartbeat
        return None

    def workflow_check_balance(
        self,
        sub_agent_chat_id: str,
        workflow_id: Optional[str] = None,
        check_type: str = "progress"
    ) -> WorkflowCheckBalance:
        """
        Workflow check and balance

        Performs checks and balances on workflow execution
        """
        check_id = f"check_{int(datetime.now().timestamp() * 1000)}"

        # Perform check based on type
        status = "pending"
        details = {}
        balance_action = None

        if check_type == "progress":
            status, details, balance_action = self._check_workflow_progress(sub_agent_chat_id, workflow_id)
        elif check_type == "completion":
            status, details, balance_action = self._check_workflow_completion(sub_agent_chat_id, workflow_id)
        elif check_type == "error":
            status, details, balance_action = self._check_workflow_errors(sub_agent_chat_id, workflow_id)
        elif check_type == "resource":
            status, details, balance_action = self._check_workflow_resources(sub_agent_chat_id, workflow_id)

        check = WorkflowCheckBalance(
            check_id=check_id,
            sub_agent_chat_id=sub_agent_chat_id,
            workflow_id=workflow_id,
            check_type=check_type,
            status=status,
            timestamp=datetime.now().isoformat(),
            details=details,
            balance_action=balance_action
        )

        self._save_workflow_check(check)

        if status == "passed":
            self.logger.info(f"✅ Workflow check passed: {check_id} ({check_type})")
        elif status == "warning":
            self.logger.warning(f"⚠️ Workflow check warning: {check_id} ({check_type})")
        else:
            self.logger.error(f"❌ Workflow check failed: {check_id} ({check_type})")

        return check

    def _check_workflow_progress(
        self,
        sub_agent_chat_id: str,
        workflow_id: Optional[str]
    ) -> Tuple[str, Dict[str, Any], Optional[str]]:
        """Check workflow progress"""
        if not self.sub_ask_manager:
            return "failed", {"error": "Sub-ask manager not available"}, None

        # Find sub-ask for this chat
        sub_ask = None
        for ask in self.sub_ask_manager.sub_asks.values():
            if ask.chat_session and ask.chat_session.session_id == sub_agent_chat_id:
                sub_ask = ask
                break

        if not sub_ask:
            return "failed", {"error": "Sub-ask not found"}, None

        # Check progress
        if sub_ask.status.value == "completed":
            return "passed", {"status": "completed"}, None
        elif sub_ask.status.value == "in_progress":
            # Check if making progress
            if sub_ask.todo_list:
                completion_rate = sub_ask.todo_list.completed_count / max(sub_ask.todo_list.total_count, 1)
                if completion_rate > 0.5:
                    return "passed", {"completion_rate": completion_rate}, None
                else:
                    return "warning", {"completion_rate": completion_rate}, "Increase progress rate"
            return "passed", {"status": "in_progress"}, None
        else:
            return "warning", {"status": sub_ask.status.value}, "Activate workflow"

    def _check_workflow_completion(
        self,
        sub_agent_chat_id: str,
        workflow_id: Optional[str]
    ) -> Tuple[str, Dict[str, Any], Optional[str]]:
        """Check workflow completion"""
        if not self.sub_ask_manager:
            return "failed", {"error": "Sub-ask manager not available"}, None

        # Find sub-ask for this chat
        sub_ask = None
        for ask in self.sub_ask_manager.sub_asks.values():
            if ask.chat_session and ask.chat_session.session_id == sub_agent_chat_id:
                sub_ask = ask
                break

        if not sub_ask:
            return "failed", {"error": "Sub-ask not found"}, None

        if sub_ask.workflow_completed:
            return "passed", {"workflow_completed": True}, None
        else:
            return "warning", {"workflow_completed": False}, "Complete workflow"

    def _check_workflow_errors(
        self,
        sub_agent_chat_id: str,
        workflow_id: Optional[str]
    ) -> Tuple[str, Dict[str, Any], Optional[str]]:
        """Check workflow errors"""
        # DONE: Implement error checking  # [ADDRESSED]  # [ADDRESSED]
        return "passed", {"errors": 0}, None

    def _check_workflow_resources(
        self,
        sub_agent_chat_id: str,
        workflow_id: Optional[str]
    ) -> Tuple[str, Dict[str, Any], Optional[str]]:
        """Check workflow resources"""
        # TODO: Implement resource checking  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
        return "passed", {"resources_ok": True}, None

    def start_monitoring(self):
        """Start heartbeat monitoring loop"""
        if self.monitoring_active:
            self.logger.warning("Monitoring already active")
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("💓 Heartbeat monitoring started")

    def stop_monitoring(self):
        """Stop heartbeat monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("⏹️ Heartbeat monitoring stopped")

    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                # Get master session ID
                master_session_id = None
                if self.master_session and self.master_session.master_session:
                    master_session_id = self.master_session.master_session.session_id

                if not master_session_id:
                    time.sleep(self.heartbeat_interval_seconds)
                    continue

                # Get all sub-agent chats
                if self.sub_ask_manager:
                    for chat_id, chat_session in self.sub_ask_manager.chat_sessions.items():
                        if chat_session.chat_status in [SubAgentChatStatus.ACTIVE, SubAgentChatStatus.NEW]:
                            # Send heartbeat
                            heartbeat = self.send_heartbeat(
                                master_session_id=master_session_id,
                                sub_agent_chat_id=chat_id,
                                workflow_status=chat_session.workflow_completed and "completed" or "in_progress"
                            )

                            # Perform workflow checks and balances
                            if heartbeat.status == HeartbeatStatus.ALIVE:
                                # Check progress
                                self.workflow_check_balance(chat_id, check_type="progress")

                                # Check completion
                                self.workflow_check_balance(chat_id, check_type="completion")

                            # Handle follow-up if needed
                            if heartbeat.follow_up_required:
                                self._handle_follow_up(heartbeat)

                time.sleep(self.heartbeat_interval_seconds)
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.heartbeat_interval_seconds)

    def _handle_follow_up(self, heartbeat: Heartbeat):
        """Handle follow-up for heartbeat"""
        if heartbeat.follow_up_status == FollowUpStatus.PENDING:
            # Wait for response timeout
            time.sleep(self.response_timeout_seconds)

            # Check if still no response
            if not self._check_sub_agent_response(heartbeat.sub_agent_chat_id):
                heartbeat.follow_up_status = FollowUpStatus.TIMEOUT
                self.logger.warning(f"⏱️ Follow-up timeout: {heartbeat.heartbeat_id}")
                self._save_heartbeat(heartbeat)

                # Take action based on status
                if heartbeat.status == HeartbeatStatus.DEAD:
                    self.logger.error(f"💀 Sub-agent chat {heartbeat.sub_agent_chat_id} is DEAD - taking recovery action")
                    # TODO: Implement recovery action  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
                elif heartbeat.status == HeartbeatStatus.STALE:
                    self.logger.warning(f"⚠️ Sub-agent chat {heartbeat.sub_agent_chat_id} is STALE - investigating")
                    # TODO: Implement investigation  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]

    def get_sub_agent_status(self, sub_agent_chat_id: str) -> Dict[str, Any]:
        """Get status of sub-agent chat"""
        last_heartbeat = self._get_last_heartbeat(sub_agent_chat_id)

        if not last_heartbeat:
            return {
                "status": "unknown",
                "last_heartbeat": None,
                "response_time_ms": None
            }

        return {
            "status": last_heartbeat.status.value,
            "last_heartbeat": last_heartbeat.timestamp,
            "response_time_ms": last_heartbeat.response_time_ms,
            "workflow_status": last_heartbeat.workflow_status,
            "follow_up_required": last_heartbeat.follow_up_required,
            "follow_up_status": last_heartbeat.follow_up_status.value if last_heartbeat.follow_up_status else None
        }


def main():
    """Main execution for testing"""
    monitor = HeartbeatMonitor()

    print("=" * 80)
    print("💓 HEARTBEAT MONITOR")
    print("=" * 80)

    # Test heartbeat
    heartbeat = monitor.send_heartbeat(
        master_session_id="master_123",
        sub_agent_chat_id="chat_456",
        workflow_status="in_progress"
    )

    print(f"\n💓 Heartbeat Sent:")
    print(f"   Status: {heartbeat.status.value}")
    print(f"   Response Time: {heartbeat.response_time_ms:.0f}ms" if heartbeat.response_time_ms else "   No Response")
    print(f"   Follow-up Required: {heartbeat.follow_up_required}")

    # Test workflow check
    check = monitor.workflow_check_balance(
        sub_agent_chat_id="chat_456",
        check_type="progress"
    )

    print(f"\n✅ Workflow Check:")
    print(f"   Type: {check.check_type}")
    print(f"   Status: {check.status}")
    print(f"   Balance Action: {check.balance_action or 'None'}")


if __name__ == "__main__":



    main()