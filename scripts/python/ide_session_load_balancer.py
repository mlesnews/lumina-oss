#!/usr/bin/env python3
"""
IDE Session Load Balancer

Ensures load balancing across all IDE sessions running on the same host.
Prevents any single session from stalling or hogging resources.

Tracks:
- Active IDE sessions per host
- Per-session resource usage
- Load distribution across sessions
- Session health monitoring
"""

import sys
import json
import os
import psutil
import threading
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class SessionStatus(Enum):
    """Session status"""
    ACTIVE = "active"
    IDLE = "idle"
    STALLED = "stalled"
    OVERLOADED = "overloaded"
    UNKNOWN = "unknown"


@dataclass
class IDESession:
    """IDE session information"""
    session_id: str
    process_id: int
    host: str
    ide_type: str  # cursor, vscode, etc.
    workspace_path: Optional[str] = None
    cpu_usage: float = 0.0
    memory_usage_mb: float = 0.0
    active_requests: int = 0
    queue_length: int = 0
    status: SessionStatus = SessionStatus.UNKNOWN
    last_activity: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['status'] = self.status.value
        if self.last_activity:
            data['last_activity'] = self.last_activity.isoformat()
        data['created_at'] = self.created_at.isoformat()
        return data

    def get_load_score(self) -> float:
        """Get load score (0-1, higher = more loaded)"""
        cpu_factor = self.cpu_usage / 100.0
        memory_factor = min(1.0, self.memory_usage_mb / 4096.0)  # Normalize to 4GB
        request_factor = min(1.0, self.active_requests / 10.0)  # Normalize to 10 requests
        queue_factor = min(1.0, self.queue_length / 20.0)  # Normalize to 20 queued

        # Weighted average
        load_score = (cpu_factor * 0.3 + memory_factor * 0.3 + request_factor * 0.2 + queue_factor * 0.2)
        return max(0.0, min(1.0, load_score))

    def is_stalled(self, timeout_seconds: int = 30) -> bool:
        """Check if session is stalled"""
        if not self.last_activity:
            return True

        time_since_activity = (datetime.now() - self.last_activity).total_seconds()
        return time_since_activity > timeout_seconds and self.active_requests > 0


@dataclass
class HostSessionState:
    """Host session state"""
    host_id: str
    total_sessions: int = 0
    active_sessions: int = 0
    stalled_sessions: int = 0
    total_cpu_usage: float = 0.0
    total_memory_usage_mb: float = 0.0
    total_active_requests: int = 0
    sessions: Dict[str, IDESession] = field(default_factory=dict)
    last_update: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['sessions'] = {k: v.to_dict() for k, v in self.sessions.items()}
        if self.last_update:
            data['last_update'] = self.last_update.isoformat()
        return data


class IDESessionLoadBalancer:
    """
    IDE Session Load Balancer

    Tracks and balances load across all IDE sessions on the same host.
    Prevents stalling and ensures fair resource distribution.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize session load balancer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("IDESessionLoadBalancer")

        # Data directories
        self.data_dir = self.project_root / "data" / "ide_sessions"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Session tracking
        self.host_sessions: Dict[str, HostSessionState] = {}
        self.current_session_id: Optional[str] = None

        # Monitoring
        self.monitoring_thread: Optional[threading.Thread] = None
        self.running = False

        # Load balancing settings (@PEAK optimization)
        self.max_cpu_per_session = 95.0  # Max 95% CPU per session (@PEAK)
        self.max_memory_per_session_mb = 4096.0  # Max 4GB per session (@PEAK)
        self.max_requests_per_session = 20  # Max 20 concurrent requests (@PEAK)
        self.stall_timeout_seconds = 600  # 600 seconds (10 minutes) = stalled (@PEAK - increased for better control retention)

        # Register current session
        self._register_current_session()

        # Start monitoring
        self.start_monitoring()

        self.logger.info("✅ IDE Session Load Balancer initialized")
        self.logger.info(f"   Current session: {self.current_session_id}")

    def _register_current_session(self) -> None:
        """Register current IDE session"""
        try:
            # Get current process info
            current_process = psutil.Process()
            process_id = current_process.pid

            # Try to detect IDE type
            parent = current_process.parent()
            ide_type = "unknown"
            if parent:
                parent_name = parent.name().lower()
                if "cursor" in parent_name:
                    ide_type = "cursor"
                elif "code" in parent_name or "vscode" in parent_name:
                    ide_type = "vscode"
                elif "abacus" in parent_name:
                    ide_type = "abacus"

            # Get hostname
            import socket
            host = socket.gethostname()

            # Create session ID
            session_id = f"{ide_type}_{host}_{process_id}_{int(time.time())}"
            self.current_session_id = session_id

            # Register session
            if host not in self.host_sessions:
                self.host_sessions[host] = HostSessionState(host_id=host)

            session = IDESession(
                session_id=session_id,
                process_id=process_id,
                host=host,
                ide_type=ide_type,
                workspace_path=str(self.project_root),
                last_activity=datetime.now()
            )

            self.host_sessions[host].sessions[session_id] = session
            self.host_sessions[host].total_sessions = len(self.host_sessions[host].sessions)

            self.logger.info(f"📝 Registered IDE session: {session_id}")

        except Exception as e:
            self.logger.error(f"Failed to register session: {e}")

    def discover_sessions(self) -> Dict[str, List[IDESession]]:
        """Discover all IDE sessions on this host"""
        discovered = {}

        try:
            # Find all processes that might be IDE sessions
            ide_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info']):
                try:
                    name = proc.info['name'].lower()
                    cmdline = ' '.join(proc.info['cmdline'] or [])

                    # Check if it's an IDE process
                    is_ide = False
                    ide_type = "unknown"

                    if "cursor" in name or "cursor" in cmdline.lower():
                        is_ide = True
                        ide_type = "cursor"
                    elif "code" in name or "vscode" in name or "code.exe" in name:
                        is_ide = True
                        ide_type = "vscode"
                    elif "abacus" in name or "abacus" in cmdline.lower():
                        is_ide = True
                        ide_type = "abacus"

                    if is_ide:
                        ide_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'ide_type': ide_type,
                            'cpu': proc.info['cpu_percent'] or 0.0,
                            'memory_mb': (proc.info['memory_info'].rss / 1024 / 1024) if proc.info['memory_info'] else 0.0
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Group by host
            import socket
            host = socket.gethostname()

            if host not in discovered:
                discovered[host] = []

            for proc_info in ide_processes:
                session_id = f"{proc_info['ide_type']}_{host}_{proc_info['pid']}"

                # Check if we already have this session
                if host in self.host_sessions and session_id in self.host_sessions[host].sessions:
                    session = self.host_sessions[host].sessions[session_id]
                    # Update metrics
                    session.cpu_usage = proc_info['cpu']
                    session.memory_usage_mb = proc_info['memory_mb']
                    session.last_activity = datetime.now()
                else:
                    # Create new session
                    session = IDESession(
                        session_id=session_id,
                        process_id=proc_info['pid'],
                        host=host,
                        ide_type=proc_info['ide_type'],
                        cpu_usage=proc_info['cpu'],
                        memory_usage_mb=proc_info['memory_mb'],
                        last_activity=datetime.now()
                    )

                    if host not in self.host_sessions:
                        self.host_sessions[host] = HostSessionState(host_id=host)

                    self.host_sessions[host].sessions[session_id] = session

                discovered[host].append(session)

            # Update host state
            if host in self.host_sessions:
                state = self.host_sessions[host]
                state.total_sessions = len(state.sessions)
                state.active_sessions = sum(1 for s in state.sessions.values() 
                                          if s.status == SessionStatus.ACTIVE)
                state.stalled_sessions = sum(1 for s in state.sessions.values() 
                                           if s.is_stalled(self.stall_timeout_seconds))
                state.total_cpu_usage = sum(s.cpu_usage for s in state.sessions.values())
                state.total_memory_usage_mb = sum(s.memory_usage_mb for s in state.sessions.values())
                state.total_active_requests = sum(s.active_requests for s in state.sessions.values())
                state.last_update = datetime.now()

        except Exception as e:
            self.logger.error(f"Session discovery error: {e}")

        return discovered

    def start_monitoring(self, interval: int = 5) -> None:
        """Start session monitoring"""
        if self.running:
            return

        self.running = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self.monitoring_thread.start()
        self.logger.info(f"✅ Session monitoring started (interval: {interval}s)")

    def _monitoring_loop(self, interval: int) -> None:
        """Monitoring loop"""
        while self.running:
            try:
                # Discover sessions
                self.discover_sessions()

                # Check for stalled sessions
                self._check_stalled_sessions()

                # Update session statuses
                self._update_session_statuses()

                # Save state
                self._save_state()

                time.sleep(interval)
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(interval)

    def _check_stalled_sessions(self) -> None:
        """Check for stalled sessions"""
        for host, state in self.host_sessions.items():
            for session_id, session in state.sessions.items():
                if session.is_stalled(self.stall_timeout_seconds):
                    if session.status != SessionStatus.STALLED:
                        session.status = SessionStatus.STALLED
                        self.logger.warning(f"⚠️  Session stalled: {session_id}")
                elif session.cpu_usage > self.max_cpu_per_session:
                    session.status = SessionStatus.OVERLOADED
                elif session.active_requests > 0:
                    session.status = SessionStatus.ACTIVE
                else:
                    session.status = SessionStatus.IDLE

    def _update_session_statuses(self) -> None:
        """Update session statuses based on metrics"""
        for host, state in self.host_sessions.items():
            for session in state.sessions.values():
                load_score = session.get_load_score()

                if session.is_stalled(self.stall_timeout_seconds):
                    session.status = SessionStatus.STALLED
                elif load_score > 0.8:
                    session.status = SessionStatus.OVERLOADED
                elif load_score > 0.0:
                    session.status = SessionStatus.ACTIVE
                else:
                    session.status = SessionStatus.IDLE

    def get_least_loaded_session(self, host: Optional[str] = None) -> Optional[IDESession]:
        """Get least loaded session on host"""
        if host is None:
            import socket
            host = socket.gethostname()

        if host not in self.host_sessions:
            return None

        state = self.host_sessions[host]
        active_sessions = [s for s in state.sessions.values() 
                          if s.status in [SessionStatus.ACTIVE, SessionStatus.IDLE]]

        if not active_sessions:
            return None

        # Return session with lowest load score
        return min(active_sessions, key=lambda s: s.get_load_score())

    def can_accept_request(self, session_id: Optional[str] = None) -> bool:
        """Check if session can accept new request"""
        if session_id is None:
            session_id = self.current_session_id

        if not session_id:
            return True  # Default allow if no session tracking

        for host, state in self.host_sessions.items():
            if session_id in state.sessions:
                session = state.sessions[session_id]

                # Check limits
                if session.cpu_usage >= self.max_cpu_per_session:
                    return False
                if session.memory_usage_mb >= self.max_memory_per_session_mb:
                    return False
                if session.active_requests >= self.max_requests_per_session:
                    return False
                if session.status == SessionStatus.STALLED:
                    return False

                return True

        return True  # Default allow if session not found

    def record_request(self, session_id: Optional[str] = None) -> None:
        """Record a request for session"""
        if session_id is None:
            session_id = self.current_session_id

        if not session_id:
            return

        for host, state in self.host_sessions.items():
            if session_id in state.sessions:
                session = state.sessions[session_id]
                session.active_requests += 1
                session.last_activity = datetime.now()
                if session.status == SessionStatus.IDLE:
                    session.status = SessionStatus.ACTIVE

    def complete_request(self, session_id: Optional[str] = None) -> None:
        """Complete a request for session"""
        if session_id is None:
            session_id = self.current_session_id

        if not session_id:
            return

        for host, state in self.host_sessions.items():
            if session_id in state.sessions:
                session = state.sessions[session_id]
                session.active_requests = max(0, session.active_requests - 1)

    def get_load_balance_status(self) -> Dict[str, Any]:
        """Get load balance status"""
        return {
            "timestamp": datetime.now().isoformat(),
            "hosts": {k: v.to_dict() for k, v in self.host_sessions.items()},
            "current_session": self.current_session_id,
            "total_sessions": sum(len(s.sessions) for s in self.host_sessions.values()),
            "stalled_sessions": sum(s.stalled_sessions for s in self.host_sessions.values()),
            "settings": {
                "max_cpu_per_session": self.max_cpu_per_session,
                "max_memory_per_session_mb": self.max_memory_per_session_mb,
                "max_requests_per_session": self.max_requests_per_session,
                "stall_timeout_seconds": self.stall_timeout_seconds
            }
        }

    def _save_state(self) -> None:
        """Save state to disk"""
        state_file = self.data_dir / "session_state.json"
        try:
            with open(state_file, 'w') as f:
                json.dump(self.get_load_balance_status(), f, indent=2)
        except Exception as e:
            self.logger.debug(f"Could not save state: {e}")

    def stop_monitoring(self) -> None:
        """Stop monitoring"""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="IDE Session Load Balancer")
    parser.add_argument("--discover", action="store_true", help="Discover IDE sessions")
    parser.add_argument("--status", action="store_true", help="Show load balance status")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    balancer = IDESessionLoadBalancer()

    if args.discover:
        print("\n🔍 Discovering IDE sessions...")
        sessions = balancer.discover_sessions()
        for host, host_sessions in sessions.items():
            print(f"\n📱 Host: {host}")
            print(f"   Sessions: {len(host_sessions)}")
            for session in host_sessions:
                status_icon = "🟢" if session.status == SessionStatus.ACTIVE else "🟡" if session.status == SessionStatus.IDLE else "🔴"
                print(f"   {status_icon} {session.session_id}")
                print(f"      Type: {session.ide_type}, CPU: {session.cpu_usage:.1f}%, Memory: {session.memory_usage_mb:.1f}MB")
                print(f"      Requests: {session.active_requests}, Status: {session.status.value}")

    elif args.status:
        status = balancer.get_load_balance_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print("\n⚖️  IDE Session Load Balance Status")
            print("=" * 60)
            print(f"Current Session: {status['current_session']}")
            print(f"Total Sessions: {status['total_sessions']}")
            print(f"Stalled Sessions: {status['stalled_sessions']}")
            print("\nHosts:")
            for host_id, host_data in status['hosts'].items():
                print(f"  📱 {host_id}")
                print(f"     Total: {host_data['total_sessions']}, Active: {host_data['active_sessions']}, Stalled: {host_data['stalled_sessions']}")
                print(f"     CPU: {host_data['total_cpu_usage']:.1f}%, Memory: {host_data['total_memory_usage_mb']:.1f}MB")

    else:
        parser.print_help()

