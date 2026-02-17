#!/usr/bin/env python3
"""
Kenny & Ace Collaboration System
Main collaboration orchestrator for Kenny (IMVA) and Ace (ACES/ACVA)

Enables:
- Shared state management
- Inter-assistant messaging
- Coordinated movement (avoid collisions)
- Collaborative task execution
- Master-Padawan relationship tracking

Tags: #KENNY #ACES #COLLABORATION #MASTER_PADAWAN @JARVIS @LUMINA
"""

import sys
import json
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field, asdict
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

logger = get_logger("KennyAcesCollaboration")


class RelationshipState(Enum):
    """Master-Padawan relationship states"""
    FIRST_MEETING = "first_meeting"
    PADAWAN_TRAINING = "padawan_training"
    KNIGHT_PARTNERSHIP = "knight_partnership"
    MASTER_COLLABORATION = "master_collaboration"


class MessageType(Enum):
    """Inter-assistant message types"""
    GREETING = "greeting"
    POSITION_UPDATE = "position_update"
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    COLLISION_WARNING = "collision_warning"
    LEARNING_REQUEST = "learning_request"
    LEARNING_RESPONSE = "learning_response"
    NOTIFICATION = "notification"
    STATUS_UPDATE = "status_update"


@dataclass
class AssistantPosition:
    """Assistant position on screen"""
    x: float
    y: float
    size: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AssistantMessage:
    """Message between assistants"""
    message_id: str
    from_assistant: str  # "kenny" or "ace"
    to_assistant: str  # "kenny" or "ace"
    message_type: MessageType
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    replied: bool = False


@dataclass
class SharedState:
    """Shared state between assistants"""
    kenny_position: Optional[AssistantPosition] = None
    ace_position: Optional[AssistantPosition] = None
    relationship_state: RelationshipState = RelationshipState.FIRST_MEETING
    messages: List[AssistantMessage] = field(default_factory=list)
    active_tasks: List[Dict[str, Any]] = field(default_factory=list)
    collision_warnings: List[Dict[str, Any]] = field(default_factory=list)
    last_update: datetime = field(default_factory=datetime.now)


class KennyAcesCollaboration:
    """
    Kenny & Ace Collaboration System

    Manages:
    - Shared state between Kenny and Ace
    - Inter-assistant messaging
    - Coordinated movement (collision avoidance)
    - Collaborative task execution
    - Master-Padawan relationship tracking
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize collaboration system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "kenny_aces_collaboration"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # State file
        self.state_file = self.data_dir / "shared_state.json"

        # Shared state
        self.shared_state = SharedState()
        self.state_lock = threading.Lock()

        # Message queue
        self.message_queue: List[AssistantMessage] = []
        self.message_lock = threading.Lock()

        # Collision detection
        self.collision_threshold = 100  # pixels - minimum distance before collision warning
        self.collision_check_interval = 0.5  # seconds

        # Update thread
        self.update_thread = None
        self.running = False

        # Load existing state
        self._load_state()

        logger.info("=" * 80)
        logger.info("🤝 KENNY & ACE COLLABORATION SYSTEM")
        logger.info("   Master-Padawan relationship tracking")
        logger.info("   Inter-assistant messaging")
        logger.info("   Coordinated movement & collision avoidance")
        logger.info("=" * 80)

        # SYPHON integration - Intelligence extraction for VA enhancement
        self.syphon = None
        self.syphon_enhancement_interval = 60.0  # Extract intelligence every 60 seconds
        self.last_syphon_enhancement = time.time()
        self.syphon_enhanced_knowledge = []
        if SYPHON_AVAILABLE:
            try:
                syphon_config = SYPHONConfig(project_root=project_root, enable_regex_tools=True)
                self.syphon = SYPHONSystem(syphon_config)
                self.logger.info("✅ SYPHON intelligence extraction integrated for VA enhancement")
            except Exception as e:
                self.logger.warning(f"⚠️  SYPHON integration failed: {e}")

        # R5 Living Context Matrix - Context aggregation
        self.r5 = None
        if R5_AVAILABLE:
            try:
                self.r5 = R5LivingContextMatrix(project_root)
                self.logger.info("✅ R5 context aggregation integrated")
            except Exception as e:
                self.logger.warning(f"⚠️  R5 integration failed: {e}")

    def _load_state(self):
        """Load shared state from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        logger.debug("State file is empty, starting fresh")
                        return
                    data = json.loads(content)

                # Restore state
                if 'kenny_position' in data and data['kenny_position']:
                    pos = data['kenny_position']
                    self.shared_state.kenny_position = AssistantPosition(
                        x=pos['x'],
                        y=pos['y'],
                        size=pos['size'],
                        timestamp=datetime.fromisoformat(pos['timestamp'])
                    )

                if 'ace_position' in data and data['ace_position']:
                    pos = data['ace_position']
                    self.shared_state.ace_position = AssistantPosition(
                        x=pos['x'],
                        y=pos['y'],
                        size=pos['size'],
                        timestamp=datetime.fromisoformat(pos['timestamp'])
                    )

                if 'relationship_state' in data:
                    self.shared_state.relationship_state = RelationshipState(data['relationship_state'])

                logger.info("✅ Loaded existing collaboration state")
            except Exception as e:
                logger.warning(f"⚠️  Could not load state: {e}")

    def _save_state(self):
        """Save shared state to file"""
        try:
            with self.state_lock:
                data = {
                    'kenny_position': None,
                    'ace_position': None,
                    'relationship_state': self.shared_state.relationship_state.value,
                    'last_update': self.shared_state.last_update.isoformat()
                }

                if self.shared_state.kenny_position:
                    data['kenny_position'] = {
                        'x': self.shared_state.kenny_position.x,
                        'y': self.shared_state.kenny_position.y,
                        'size': self.shared_state.kenny_position.size,
                        'timestamp': self.shared_state.kenny_position.timestamp.isoformat()
                    }

                if self.shared_state.ace_position:
                    data['ace_position'] = {
                        'x': self.shared_state.ace_position.x,
                        'y': self.shared_state.ace_position.y,
                        'size': self.shared_state.ace_position.size,
                        'timestamp': self.shared_state.ace_position.timestamp.isoformat()
                    }

            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            logger.error(f"❌ Error saving state: {e}")

    def update_kenny_position(self, x: float, y: float, size: int):
        """Update Kenny's position"""
        with self.state_lock:
            self.shared_state.kenny_position = AssistantPosition(x=x, y=y, size=size)
            self.shared_state.last_update = datetime.now()

        # Check for collisions
        self._check_collisions()

        # Save state
        self._save_state()

        # Send position update to Ace
        self.send_message(
            from_assistant="kenny",
            to_assistant="ace",
            message_type=MessageType.POSITION_UPDATE,
            payload={"x": x, "y": y, "size": size}
        )

    def update_ace_position(self, x: float, y: float, size: int):
        """Update Ace's position"""
        with self.state_lock:
            self.shared_state.ace_position = AssistantPosition(x=x, y=y, size=size)
            self.shared_state.last_update = datetime.now()

        # Check for collisions
        self._check_collisions()

        # Save state
        self._save_state()

        # Send position update to Kenny
        self.send_message(
            from_assistant="ace",
            to_assistant="kenny",
            message_type=MessageType.POSITION_UPDATE,
            payload={"x": x, "y": y, "size": size}
        )

    def _check_collisions(self):
        """Check for potential collisions between assistants"""
        with self.state_lock:
            if not self.shared_state.kenny_position or not self.shared_state.ace_position:
                return

            kenny_pos = self.shared_state.kenny_position
            ace_pos = self.shared_state.ace_position

            # VALIDATION: Check positions are not identical (prevent self-collision bug)
            if kenny_pos.x == ace_pos.x and kenny_pos.y == ace_pos.y:
                logger.warning(f"⚠️  IDENTICAL POSITIONS DETECTED: Kenny and Ace at same location ({kenny_pos.x:.1f}, {kenny_pos.y:.1f}) - skipping collision check")
                return  # Skip collision detection - positions are identical (prevent self-attack)

            # Calculate distance
            distance = ((kenny_pos.x - ace_pos.x) ** 2 + (kenny_pos.y - ace_pos.y) ** 2) ** 0.5

            # Debug logging
            logger.debug(f"🔍 Collision check: Kenny=({kenny_pos.x:.1f}, {kenny_pos.y:.1f}), Ace=({ace_pos.x:.1f}, {ace_pos.y:.1f}), distance={distance:.1f}px")

            # Check if too close
            min_distance = (kenny_pos.size + ace_pos.size) / 2 + self.collision_threshold

            if distance < min_distance:
                # Collision warning
                warning = {
                    "distance": distance,
                    "min_distance": min_distance,
                    "kenny_pos": {"x": kenny_pos.x, "y": kenny_pos.y},
                    "ace_pos": {"x": ace_pos.x, "y": ace_pos.y},
                    "timestamp": datetime.now().isoformat()
                }

                self.shared_state.collision_warnings.append(warning)

                # Keep only recent warnings
                if len(self.shared_state.collision_warnings) > 10:
                    self.shared_state.collision_warnings.pop(0)

                # Send collision warning to both
                self.send_message(
                    from_assistant="collaboration",
                    to_assistant="kenny",
                    message_type=MessageType.COLLISION_WARNING,
                    payload=warning
                )
                self.send_message(
                    from_assistant="collaboration",
                    to_assistant="ace",
                    message_type=MessageType.COLLISION_WARNING,
                    payload=warning
                )

                logger.debug(f"⚠️  Collision warning: distance={distance:.1f}px, min={min_distance:.1f}px")

    def send_message(self, from_assistant: str, to_assistant: str, message_type: MessageType, payload: Dict[str, Any]) -> str:
        """Send message between assistants"""
        message_id = f"{from_assistant}_{to_assistant}_{int(time.time() * 1000)}"

        message = AssistantMessage(
            message_id=message_id,
            from_assistant=from_assistant,
            to_assistant=to_assistant,
            message_type=message_type,
            payload=payload
        )

        with self.message_lock:
            self.message_queue.append(message)
            self.shared_state.messages.append(message)

            # Keep only recent messages
            if len(self.shared_state.messages) > 100:
                self.shared_state.messages.pop(0)

        logger.debug(f"📨 Message: {from_assistant} → {to_assistant} ({message_type.value})")
        return message_id

    def get_messages(self, assistant: str, message_type: Optional[MessageType] = None) -> List[AssistantMessage]:
        """Get messages for an assistant"""
        with self.message_lock:
            messages = [msg for msg in self.message_queue if msg.to_assistant == assistant]

            if message_type:
                messages = [msg for msg in messages if msg.message_type == message_type]

            return messages.copy()

    def clear_processed_messages(self, assistant: str):
        """Clear processed messages for an assistant"""
        with self.message_lock:
            self.message_queue = [msg for msg in self.message_queue if msg.to_assistant != assistant or not msg.replied]

    def get_other_assistant_position(self, assistant: str) -> Optional[AssistantPosition]:
        """Get the other assistant's position"""
        with self.state_lock:
            if assistant == "kenny":
                return self.shared_state.ace_position
            elif assistant == "ace":
                return self.shared_state.kenny_position
            return None

    def get_collision_warnings(self) -> List[Dict[str, Any]]:
        """Get recent collision warnings"""
        with self.state_lock:
            return self.shared_state.collision_warnings.copy()

    def update_relationship_state(self, new_state: RelationshipState):
        """Update relationship state"""
        with self.state_lock:
            old_state = self.shared_state.relationship_state
            self.shared_state.relationship_state = new_state
            self.shared_state.last_update = datetime.now()

        self._save_state()
        logger.info(f"📈 Relationship state: {old_state.value} → {new_state.value}")

    def get_relationship_state(self) -> RelationshipState:
        """Get current relationship state"""
        with self.state_lock:
            return self.shared_state.relationship_state

    def start(self):
        """Start collaboration system"""
        if self.running:
            return

        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        logger.info("✅ Collaboration system started")

    def stop(self):
        """Stop collaboration system"""
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=1.0)
        self._save_state()
        logger.info("🛑 Collaboration system stopped")

    def _update_loop(self):
        """Update loop for collision detection and state management"""
        while self.running:
            try:
                # Check collisions periodically
                self._check_collisions()

                # Save state periodically
                self._save_state()

                time.sleep(self.collision_check_interval)
            except Exception as e:
                logger.error(f"❌ Error in update loop: {e}")
                time.sleep(1.0)


# Global collaboration instance
_collaboration_instance: Optional[KennyAcesCollaboration] = None


def get_collaboration() -> KennyAcesCollaboration:
    """Get global collaboration instance"""
    global _collaboration_instance
    if _collaboration_instance is None:
        _collaboration_instance = KennyAcesCollaboration()
        _collaboration_instance.start()
    return _collaboration_instance


def main():
    """Main execution"""
    import argparse

# SYPHON integration (@SYPHON) - Intelligence extraction and VA enhancement
try:
    from syphon import SYPHONSystem, SYPHONConfig, DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None

# R5 Living Context Matrix integration
try:
    from r5_living_context_matrix import R5LivingContextMatrix
    R5_AVAILABLE = True
except ImportError:
    R5_AVAILABLE = False
    R5LivingContextMatrix = None
    SYPHONConfig = None
    DataSourceType = None

    parser = argparse.ArgumentParser(description="Kenny & Ace Collaboration System")
    parser.add_argument('--status', action='store_true', help='Show collaboration status')
    parser.add_argument('--messages', type=str, help='Show messages for assistant (kenny/ace)')
    parser.add_argument('--test', action='store_true', help='Test mode')

    args = parser.parse_args()

    print("=" * 80)
    print("🤝 KENNY & ACE COLLABORATION SYSTEM")
    print("=" * 80)
    print()

    collaboration = get_collaboration()

    if args.status:
        state = collaboration.get_relationship_state()
        print(f"📊 Relationship State: {state.value}")
        print()

        kenny_pos = collaboration.shared_state.kenny_position
        ace_pos = collaboration.shared_state.ace_position

        if kenny_pos:
            print(f"🐢 Kenny Position: ({kenny_pos.x:.1f}, {kenny_pos.y:.1f}) size={kenny_pos.size}px")
        else:
            print("🐢 Kenny: Not detected")

        if ace_pos:
            print(f"⚡ Ace Position: ({ace_pos.x:.1f}, {ace_pos.y:.1f}) size={ace_pos.size}px")
        else:
            print("⚡ Ace: Not detected")

        print()
        print(f"📨 Messages in queue: {len(collaboration.message_queue)}")
        print(f"⚠️  Collision warnings: {len(collaboration.shared_state.collision_warnings)}")

    elif args.messages:
        messages = collaboration.get_messages(args.messages)
        print(f"📨 Messages for {args.messages}:")
        for msg in messages[-10:]:  # Show last 10
            print(f"   [{msg.timestamp.strftime('%H:%M:%S')}] {msg.from_assistant} → {msg.to_assistant}: {msg.message_type.value}")

    elif args.test:
        print("🧪 Test mode - Collaboration system running")
        print("   Use Ctrl+C to stop")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            collaboration.stop()
            print("\n✅ Test complete")
    else:
        print("💡 Use --status, --messages <assistant>, or --test")
        print("=" * 80)


if __name__ == "__main__":


    main()