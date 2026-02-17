#!/usr/bin/env python3
"""
VA Company Collaboration System

Complete inter-VA collaboration system for company-wide coordination with:
- Voice coordination
- VFX coordination
- Task distribution
- Status sharing
- Real-time collaboration
- Company-wide awareness

Features:
- Multi-VA task coordination
- Voice message routing
- VFX synchronization
- Status broadcasting
- Company-wide awareness
- Real-time collaboration

Tags: #COLLABORATION #COMPANY #COORDINATION #MULTI_VA @JARVIS @LUMINA
"""

import sys
import time
import threading
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger, setup_logging
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    setup_logging = lambda: None

logger = get_logger("VACompanyCollaboration")

# Import voice and VFX systems
try:
    from va_full_voice_mode_system import VAFullVoiceModeSystem, VoicePriority
    VOICE_SYSTEM_AVAILABLE = True
except ImportError:
    VOICE_SYSTEM_AVAILABLE = False
    VAFullVoiceModeSystem = None
    VoicePriority = None

try:
    from va_ai_vfx_system import VAAIVFXSystem, VFXType, VFXIntensity
    VFX_SYSTEM_AVAILABLE = True
except ImportError:
    VFX_SYSTEM_AVAILABLE = False
    VAAIVFXSystem = None
    VFXType = None
    VFXIntensity = None


class CollaborationType(Enum):
    """Collaboration types"""
    VOICE = "voice"
    VFX = "vfx"
    TASK = "task"
    STATUS = "status"
    NOTIFICATION = "notification"
    COORDINATION = "coordination"


class TaskPriority(Enum):
    """Task priority"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class CollaborationTask:
    """Collaboration task"""
    task_id: str
    task_type: str
    assigned_to: Optional[str]  # None = auto-assign
    priority: TaskPriority
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


@dataclass
class CollaborationMessage:
    """Message between VAs"""
    message_id: str
    from_va: str
    to_va: Optional[str]  # None = broadcast
    message_type: CollaborationType
    content: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


class VACompanyCollaborationSystem:
    """
    Company-wide VA Collaboration System

    Coordinates all VAs for company-wide operations:
    - Voice coordination
    - VFX coordination
    - Task distribution
    - Status sharing
    - Real-time collaboration
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.log_dir = project_root / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        setup_logging()

        # Registered VAs
        self.vas: Dict[str, Any] = {}
        self.va_lock = threading.Lock()

        # Voice system
        self.voice_system = None
        if VOICE_SYSTEM_AVAILABLE:
            try:
                self.voice_system = VAFullVoiceModeSystem(project_root)
                logger.info("✅ Voice system integrated")
            except Exception as e:
                logger.warning(f"⚠️  Voice system not available: {e}")

        # VFX system
        self.vfx_system = None
        if VFX_SYSTEM_AVAILABLE:
            try:
                self.vfx_system = VAAIVFXSystem(project_root)
                logger.info("✅ VFX system integrated")
            except Exception as e:
                logger.warning(f"⚠️  VFX system not available: {e}")

        # Collaboration state
        self.tasks: Dict[str, CollaborationTask] = {}
        self.messages: List[CollaborationMessage] = []
        self.collaboration_lock = threading.Lock()

        # Company-wide awareness
        self.company_status: Dict[str, Any] = {
            "all_vas_online": False,
            "active_tasks": 0,
            "voice_mode_active": False,
            "vfx_active": False,
            "last_update": datetime.now()
        }

        logger.info("✅ VA Company Collaboration System initialized")

    def register_va(self, va_name: str, va_instance: Any, capabilities: List[str] = None):
        """
        Register a VA with the collaboration system

        Args:
            va_name: Name of the VA
            va_instance: VA instance
            capabilities: List of capabilities (e.g., ["voice", "vfx", "tasks"])
        """
        with self.va_lock:
            self.vas[va_name] = {
                "instance": va_instance,
                "capabilities": capabilities or ["voice", "vfx", "tasks"],
                "status": "online",
                "position": (0, 0),
                "last_activity": datetime.now()
            }

            # Register with subsystems
            if self.voice_system:
                priority = VoicePriority.CRITICAL if va_name == "jarvis" else VoicePriority.MEDIUM
                self.voice_system.register_va(va_name, va_instance, priority)

            if self.vfx_system:
                self.vfx_system.register_va(va_name, va_instance)

        logger.info(f"✅ Registered VA: {va_name} (capabilities: {capabilities})")
        self._update_company_status()

    def start_full_collaboration_mode(self):
        """Start full collaboration mode (voice + VFX)"""
        if self.voice_system:
            self.voice_system.start_full_voice_mode()
            self.company_status["voice_mode_active"] = True

        self.company_status["all_vas_online"] = len(self.vas) > 0
        logger.info("🤝 Full collaboration mode activated")

    def stop_full_collaboration_mode(self):
        """Stop full collaboration mode"""
        if self.voice_system:
            self.voice_system.stop_full_voice_mode()
            self.company_status["voice_mode_active"] = False

        logger.info("🔇 Full collaboration mode deactivated")

    def send_collaboration_message(self, from_va: str, to_va: Optional[str],
                                  message_type: CollaborationType,
                                  content: Dict[str, Any]) -> str:
        """Send a collaboration message between VAs"""
        message_id = f"msg_{int(time.time() * 1000)}"
        message = CollaborationMessage(
            message_id=message_id,
            from_va=from_va,
            to_va=to_va,
            message_type=message_type,
            content=content
        )

        with self.collaboration_lock:
            self.messages.append(message)
            # Keep only last 1000 messages
            if len(self.messages) > 1000:
                self.messages.pop(0)

        # Route message
        if message_type == CollaborationType.VOICE:
            self._route_voice_message(message)
        elif message_type == CollaborationType.VFX:
            self._route_vfx_message(message)
        elif message_type == CollaborationType.TASK:
            self._route_task_message(message)
        elif message_type == CollaborationType.STATUS:
            self._route_status_message(message)
        elif message_type == CollaborationType.NOTIFICATION:
            self._route_notification_message(message)

        logger.info(f"📨 Collaboration message: {from_va} → {to_va or 'ALL'}: {message_type.value}")
        return message_id

    def _route_voice_message(self, message: CollaborationMessage):
        """Route voice message"""
        if not self.voice_system:
            return

        text = message.content.get("text", "")
        if message.to_va:
            # Direct message
            self.voice_system.send_voice_message(message.from_va, message.to_va, text)
        else:
            # Broadcast
            self.voice_system.send_voice_message(message.from_va, None, text)

    def _route_vfx_message(self, message: CollaborationMessage):
        """Route VFX message"""
        if not self.vfx_system:
            return

        vfx_type = message.content.get("vfx_type")
        va_name = message.content.get("va_name", message.from_va)
        intensity = message.content.get("intensity", "NORMAL")

        if vfx_type == "glow":
            self.vfx_system.create_glow_effect(
                va_name,
                VFXIntensity[intensity] if VFXIntensity else VFXIntensity.NORMAL
            )
        elif vfx_type == "particle":
            self.vfx_system.create_particle_effect(
                va_name,
                message.content.get("particle_count", 50),
                VFXIntensity[intensity] if VFXIntensity else VFXIntensity.NORMAL
            )
        elif vfx_type == "beam" and message.to_va:
            self.vfx_system.create_beam_effect(
                message.from_va,
                message.to_va,
                VFXIntensity[intensity] if VFXIntensity else VFXIntensity.NORMAL
            )

    def _route_task_message(self, message: CollaborationMessage):
        """Route task message"""
        task_data = message.content.get("task", {})
        task = CollaborationTask(
            task_id=f"task_{int(time.time() * 1000)}",
            task_type=task_data.get("type", "general"),
            assigned_to=task_data.get("assigned_to"),
            priority=TaskPriority[task_data.get("priority", "MEDIUM")],
            description=task_data.get("description", ""),
            metadata=task_data.get("metadata", {})
        )

        # Auto-assign if needed
        if not task.assigned_to:
            task.assigned_to = self._auto_assign_task(task)

        with self.collaboration_lock:
            self.tasks[task.task_id] = task

        # Notify assigned VA
        if task.assigned_to and task.assigned_to in self.vas:
            va_info = self.vas[task.assigned_to]
            va_instance = va_info["instance"]
            try:
                if hasattr(va_instance, "receive_task"):
                    va_instance.receive_task(task)
            except Exception as e:
                logger.warning(f"⚠️  Error delivering task to {task.assigned_to}: {e}")

        self._update_company_status()
        logger.info(f"📋 Task assigned: {task.task_id} → {task.assigned_to}")

    def _route_status_message(self, message: CollaborationMessage):
        """Route status message"""
        status_data = message.content.get("status", {})

        if message.from_va in self.vas:
            self.vas[message.from_va].update(status_data)
            self.vas[message.from_va]["last_activity"] = datetime.now()

        self._update_company_status()

    def _route_notification_message(self, message: CollaborationMessage):
        """Route notification message"""
        notification = message.content.get("notification", {})

        # Broadcast to all VAs
        for va_name, va_info in self.vas.items():
            if va_name != message.from_va:
                va_instance = va_info["instance"]
                try:
                    if hasattr(va_instance, "receive_notification"):
                        va_instance.receive_notification(notification)
                except Exception as e:
                    logger.warning(f"⚠️  Error delivering notification to {va_name}: {e}")

    def _auto_assign_task(self, task: CollaborationTask) -> Optional[str]:
        """Auto-assign task to best VA"""
        # Simple assignment logic (can be enhanced)
        if task.task_type == "voice":
            # Assign to JARVIS if available
            if "jarvis" in self.vas:
                return "jarvis"
        elif task.task_type == "combat":
            # Assign to Anakin or Iron Man
            for va_name in ["anakin", "ironman"]:
                if va_name in self.vas:
                    return va_name

        # Default: assign to first available VA
        if self.vas:
            return list(self.vas.keys())[0]

        return None

    def coordinate_voice_and_vfx(self, va_name: str, text: str, vfx_type: Optional[str] = None):
        """Coordinate voice and VFX together"""
        # Speak
        if self.voice_system:
            self.voice_system.speak(va_name, text)

        # VFX
        if self.vfx_system and vfx_type:
            if vfx_type == "glow":
                self.vfx_system.create_glow_effect(va_name)
            elif vfx_type == "particle":
                self.vfx_system.create_particle_effect(va_name)

    def _update_company_status(self):
        """Update company-wide status"""
        self.company_status["all_vas_online"] = len(self.vas) > 0
        self.company_status["active_tasks"] = sum(
            1 for task in self.tasks.values() 
            if task.status == "pending" or task.status == "in_progress"
        )
        self.company_status["voice_mode_active"] = (
            self.voice_system and self.voice_system.voice_mode_active
        )
        self.company_status["vfx_active"] = (
            self.vfx_system and len(self.vfx_system.active_effects) > 0
        )
        self.company_status["last_update"] = datetime.now()

    def get_company_status(self) -> Dict[str, Any]:
        """Get company-wide status"""
        self._update_company_status()
        return {
            **self.company_status,
            "registered_vas": list(self.vas.keys()),
            "active_tasks": self.company_status["active_tasks"],
            "voice_status": self.voice_system.get_status() if self.voice_system else None,
            "vfx_status": self.vfx_system.get_status() if self.vfx_system else None
        }


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="VA Company Collaboration System")
    parser.add_argument("--start", action="store_true", help="Start full collaboration mode")
    parser.add_argument("--stop", action="store_true", help="Stop full collaboration mode")
    parser.add_argument("--status", action="store_true", help="Show company status")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    system = VACompanyCollaborationSystem(project_root)

    if args.start:
        system.start_full_collaboration_mode()
        print("✅ Full collaboration mode started")
        print("   Press Ctrl+C to stop")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            system.stop_full_collaboration_mode()
            print("✅ Full collaboration mode stopped")
    elif args.stop:
        system.stop_full_collaboration_mode()
        print("✅ Full collaboration mode stopped")
    elif args.status:
        status = system.get_company_status()
        print(json.dumps(status, indent=2, default=str))
    else:
        parser.print_help()


if __name__ == "__main__":


    main()