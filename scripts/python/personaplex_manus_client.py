#!/usr/bin/env python3
"""PERSONAPLEX Manus AI Agent Client"""
import json, logging, time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
import requests
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

@dataclass
class ManusTask:
    task_id: str
    name: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: Priority = Priority.MEDIUM
    input_data: Dict[str, Any] = field(default_factory=dict)
    result: Optional[str] = None

class ManusClient:
    DEFAULT_BASE_URL = "http://<NAS_PRIMARY_IP>:8085"
    def __init__(self, base_url: Optional[str] = None, timeout: int = 300):
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.timeout = timeout
        self._session = requests.Session()
        logger.info(f"ManusClient initialized: {self.base_url}")

    def health_check(self) -> bool:
        try:
            r = self._session.get(f"{self.base_url}/health", timeout=self.timeout)
            return r.status_code == 200
        except:
            return False

    def submit_task(self, task: ManusTask) -> ManusTask:
        try:
            data = {"name": task.name, "description": task.description, "priority": task.priority.value, "input_data": task.input_data}
            r = self._session.post(f"{self.base_url}/tasks", json=data, timeout=self.timeout)
            r.raise_for_status()
            resp = r.json()
            task.task_id = resp.get("task_id", task.task_id)
            task.status = TaskStatus(resp.get("status", "pending"))
            return task
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.result = str(e)
            return task

    def get_task_status(self, task_id: str) -> Optional[ManusTask]:
        try:
            r = self._session.get(f"{self.base_url}/tasks/{task_id}", timeout=self.timeout)
            r.raise_for_status()
            resp = r.json()
            return ManusTask(task_id=resp.get("task_id", task_id), name=resp.get("name", ""), description=resp.get("description", ""), status=TaskStatus(resp.get("status", "pending")), input_data=resp.get("input_data", {}), result=resp.get("result"))
        except:
            return None

def create_manus_client(base_url: Optional[str] = None) -> ManusClient:
    return ManusClient(base_url=base_url)

if __name__ == "__main__":
    c = create_manus_client()
    print(f"Health: {c.health_check()}")
    print("PERSONAPLEX Manus Client initialized!")
