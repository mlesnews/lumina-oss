#!/usr/bin/env python3
"""
JARVIS Team Leader

Lead teams of systems/VAs, delegate tasks, provide guidance.
Part of Phase 4 (Adolescent → ASI).

Tags: #JARVIS #LEADERSHIP #PHASE4 @JARVIS @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISTeamLeader")


@dataclass
class TeamTask:
    """A task delegated to a team member"""
    task_id: str
    team_member_id: str
    task: str
    status: str = "assigned"
    result: Optional[Any] = None


class JARVISTeamLeader:
    """
    Team leadership system

    Capabilities:
    - Lead teams of systems/VAs
    - Delegate tasks
    - Provide guidance
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize team leader"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "jarvis_team_leadership"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.tasks_file = self.data_dir / "team_tasks.json"
        self.team_tasks: List[TeamTask] = []
        self.team_members: Dict[str, Dict[str, Any]] = {}

        self._load_data()

        logger.info("=" * 80)
        logger.info("👔 JARVIS TEAM LEADER")
        logger.info("=" * 80)
        logger.info("   Lead teams, delegate tasks, provide guidance")
        logger.info("")

    def delegate_task(self, team_member_id: str, task: str) -> str:
        """Delegate a task to a team member"""
        task_id = f"task_{int(time.time() * 1000)}"

        team_task = TeamTask(
            task_id=task_id,
            team_member_id=team_member_id,
            task=task
        )

        self.team_tasks.append(team_task)
        self._save_data()

        logger.info(f"👔 Delegated task to {team_member_id}: {task}")
        return task_id

    def _load_data(self):
        """Load tasks from disk"""
        try:
            if self.tasks_file.exists():
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.team_tasks = [TeamTask(**t) for t in data.get("tasks", [])]
        except Exception as e:
            logger.debug(f"Could not load team data: {e}")

    def _save_data(self):
        """Save tasks to disk"""
        try:
            data = {
                "tasks": [asdict(t) for t in self.team_tasks],
                "last_updated": datetime.now().isoformat()
            }
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Could not save team data: {e}")


# Singleton
_team_leader_instance: Optional[JARVISTeamLeader] = None

def get_jarvis_team_leader(project_root: Optional[Path] = None) -> JARVISTeamLeader:
    global _team_leader_instance
    if _team_leader_instance is None:
        _team_leader_instance = JARVISTeamLeader(project_root)
    return _team_leader_instance
