#!/usr/bin/env python3
"""
JARVIS Teaching System

Knowledge transfer, mentoring framework, knowledge documentation.
Part of Phase 2 (Toddler → Child).

Tags: #JARVIS #TEACHING #PHASE2 @JARVIS @LUMINA
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

logger = get_logger("JARVISTeachingSystem")


@dataclass
class TeachingSession:
    """A teaching session"""
    session_id: str
    student_id: str
    topic: str
    knowledge_transferred: List[str]
    success: bool
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class JARVISTeachingSystem:
    """
    Teaching capabilities system

    Capabilities:
    - Transfer knowledge to other systems
    - Create teaching materials
    - Adapt to learner
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize teaching system"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "jarvis_teaching"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.sessions_file = self.data_dir / "teaching_sessions.json"
        self.sessions: List[TeachingSession] = []

        self._load_data()

        logger.info("=" * 80)
        logger.info("📚 JARVIS TEACHING SYSTEM")
        logger.info("=" * 80)
        logger.info("   Knowledge transfer, mentoring, knowledge documentation")
        logger.info("")

    def teach(self, student_id: str, topic: str, knowledge: List[str]) -> TeachingSession:
        """Teach knowledge to a student system"""
        session_id = f"teaching_{int(time.time() * 1000)}"

        session = TeachingSession(
            session_id=session_id,
            student_id=student_id,
            topic=topic,
            knowledge_transferred=knowledge,
            success=True
        )

        self.sessions.append(session)
        self._save_data()

        logger.info(f"📚 Teaching session: {topic} to {student_id}")
        return session

    def _load_data(self):
        """Load sessions from disk"""
        try:
            if self.sessions_file.exists():
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.sessions = [TeachingSession(**s) for s in data.get("sessions", [])]
        except Exception as e:
            logger.debug(f"Could not load teaching data: {e}")

    def _save_data(self):
        """Save sessions to disk"""
        try:
            data = {
                "sessions": [asdict(s) for s in self.sessions],
                "last_updated": datetime.now().isoformat()
            }
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.debug(f"Could not save teaching data: {e}")


# Singleton
_teaching_instance: Optional[JARVISTeachingSystem] = None

def get_jarvis_teaching_system(project_root: Optional[Path] = None) -> JARVISTeachingSystem:
    global _teaching_instance
    if _teaching_instance is None:
        _teaching_instance = JARVISTeachingSystem(project_root)
    return _teaching_instance
