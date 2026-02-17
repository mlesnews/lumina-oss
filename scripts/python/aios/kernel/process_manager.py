#!/usr/bin/env python3
"""
AIOS Process Management Module

Handles process creation, termination, and status tracking.
"""

import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


# Process state enumeration
class ProcessState(Enum):
    CREATED = "created"
    READY = "ready"
    RUNNING = "running"
    BLOCKED = "blocked"
    TERMINATED = "terminated"


# Process descriptor
@dataclass
class Process:
    pid: int
    name: str
    state: ProcessState
    priority: int
    memory_base: int
    memory_size: int
    cpu_time: float
    created_at: str
    parent_pid: Optional[int] = None


class ProcessManager:
    """Manages processes within the AIOS kernel."""

    def __init__(self):
        self.processes: Dict[int, Process] = {}
        self.next_pid = 1
        self.process_lock = threading.Lock()

    def create_process(
        self,
        name: str,
        priority: int = 0,
        memory_size: int = 1024 * 1024,
        memory_base: int = 0,
        parent_pid: Optional[int] = None,
    ) -> Process:
        with self.process_lock:
            pid = self.next_pid
            self.next_pid += 1
            process = Process(
                pid=pid,
                name=name,
                state=ProcessState.CREATED,
                priority=priority,
                memory_base=memory_base,
                memory_size=memory_size,
                cpu_time=0.0,
                created_at=time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
                parent_pid=parent_pid,
            )
            self.processes[pid] = process
            return process

    def terminate_process(self, pid: int) -> bool:
        with self.process_lock:
            if pid not in self.processes:
                return False
            process = self.processes[pid]
            process.state = ProcessState.TERMINATED
            del self.processes[pid]
            return True

    def get_process_status(self, pid: int) -> Optional[Process]:
        return self.processes.get(pid)

    def get_all_processes(self) -> Dict[int, Process]:
        return dict(self.processes)
