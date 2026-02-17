#!/usr/bin/env python3
"""
JARVIS Interactive Avatar Agents System

Interactive AI-driven agents with real "modeled" character personalities:
- Links all major and minor systems
- Uses acting call list avatars
- Real modeled character personalities based on books and media
- Interactive @OP (operator) agents
- System coordination and management

Tags: #INTERACTIVE #AVATAR_AGENTS #AI_DRIVEN #CHARACTER_PERSONALITIES #SYSTEM_LINKING @JARVIS @LUMINA @OP
"""

import json
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("JARVISAvatar")
except ImportError:
    try:
        from lumina_logger import get_logger
        logger = get_logger("JARVISAvatar")
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("JARVISAvatar")

# Import acting call list and personality layers
try:
    from jarvis_acting_call_list import ActingCallList
    ACTING_CALL_LIST_AVAILABLE = True
except ImportError:
    try:
        from scripts.python.jarvis_acting_call_list import ActingCallList
        ACTING_CALL_LIST_AVAILABLE = True
    except ImportError:
        ACTING_CALL_LIST_AVAILABLE = False
        logger.warning("Acting call list not available")

try:
    from jarvis_modular_personality_layers import (LayerType,
                                                   ModularPersonalitySystem)
    PERSONALITY_LAYERS_AVAILABLE = True
except ImportError:
    try:
        from scripts.python.jarvis_modular_personality_layers import (
            LayerType, ModularPersonalitySystem)
        PERSONALITY_LAYERS_AVAILABLE = True
    except ImportError:
        PERSONALITY_LAYERS_AVAILABLE = False
        logger.warning("Personality layers not available")

# Import SYPHON system
try:
    from syphon_system import DataSourceType, SYPHONSystem
    SYPHON_AVAILABLE = True
except ImportError:
    try:
        from scripts.python.syphon_system import DataSourceType, SYPHONSystem
        SYPHON_AVAILABLE = True
    except ImportError:
        SYPHON_AVAILABLE = False
        logger.warning("SYPHON system not available")


class AgentRole(Enum):
    """Agent roles for system management"""
    SYSTEM_COORDINATOR = "system_coordinator"
    INTELLIGENCE_ANALYST = "intelligence_analyst"
    THREAT_RESPONSE = "threat_response"
    SUPERVISOR = "supervisor"
    ADVISOR = "advisor"
    OPERATOR_ASSISTANT = "operator_assistant"
    MEDIA_CURATOR = "media_curator"
    PEACE_INITIATIVE = "peace_initiative"
    MERIT_TRACKER = "merit_tracker"
    MEASUREMENT_ANALYST = "measurement_analyst"
    TERMINAL_MONITOR = "terminal_monitor"
    CLONE_MANAGER = "clone_manager"


class InteractiveAvatarAgent:
    """Interactive AI-driven avatar agent with modeled character personality"""

    def __init__(
        self,
        agent_id: str,
        persona_id: str,
        role: AgentRole,
        personality_stack_id: str = None,
        systems_managed: List[str] = None
    ):
        self.agent_id = agent_id
        self.persona_id = persona_id
        self.role = role
        self.personality_stack_id = personality_stack_id
        self.systems_managed = systems_managed or []
        self.created_at = datetime.now().isoformat()
        self.status = "active"
        self.interaction_history = []
        self.operator_interactions = []
        self.notifications = []

        # Auto-hide settings (similar to Cursor IDE UI)
        self.auto_hide_enabled = True
        self.auto_hide_duration_seconds = 5  # Default 5 seconds like Cursor IDE
        self.notification_timeout = None

        # Load persona details
        self.persona = None
        self.personality_layers = []
        self.modeled_personality = {}

    def load_persona(
        self,
        acting_call_list: ActingCallList,
        personality_system: ModularPersonalitySystem = None
    ):
        """Load persona and personality layers"""
        # Load persona from acting call list
        actors = acting_call_list.get_digital_actors()
        self.persona = next((a for a in actors if a["actor_id"] == self.persona_id), None)

        if not self.persona:
            logger.warning(f"Persona not found: {self.persona_id}")
            return

        # Load personality stack if available
        if personality_system and self.personality_stack_id:
            stack = personality_system.get_personality_stack(self.personality_stack_id)
            if "layers" in stack:
                self.personality_layers = stack["layers"]
                self.modeled_personality = stack.get("merged_attributes", {})

        logger.info(f"✅ Loaded persona for agent {self.agent_id}: {self.persona['name']}")

    def interact_with_operator(
        self,
        message: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Interact with operator (@OP)"""
        interaction = {
            "interaction_id": f"interact_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "agent_name": self.persona["name"] if self.persona else "Unknown",
            "role": self.role.value,
            "message": message,
            "context": context or {},
            "personality": self.modeled_personality,
            "response": self._generate_response(message, context),
            "auto_hide_enabled": self.auto_hide_enabled,
            "auto_hide_duration": self.auto_hide_duration_seconds,
            "auto_hide_at": (datetime.now().timestamp() + self.auto_hide_duration_seconds) if self.auto_hide_enabled else None
        }

        self.operator_interactions.append(interaction)
        return interaction

    def create_notification(
        self,
        notification_type: str,
        message: str,
        priority: str = "normal",
        auto_hide: bool = True,
        duration_seconds: int = None
    ) -> Dict[str, Any]:
        """Create a notification/alert chat bubble with auto-hide and accessibility features"""
        # Determine auto-hide behavior based on priority
        # Critical warnings should not auto-hide or have very long duration
        is_critical = priority == "critical" or notification_type in ["error", "alert"]
        is_high_priority = priority == "high" or notification_type == "warning"

        if is_critical:
            auto_hide = False  # Critical warnings persist - DO NOT AUTO-HIDE
            duration_seconds = None
        elif is_high_priority:
            # High priority warnings have longer duration (5 minutes)
            auto_hide = True
            duration_seconds = duration_seconds if duration_seconds else 300
        else:
            # Normal notifications use default (5 seconds)
            auto_hide = auto_hide if auto_hide is not None else True
            duration_seconds = duration_seconds if duration_seconds else self.auto_hide_duration_seconds

        # Calculate auto_hide_at only if auto_hide is enabled
        auto_hide_at = None
        if auto_hide and duration_seconds:
            auto_hide_at = datetime.now().timestamp() + duration_seconds

        notification = {
            "notification_id": f"notif_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "agent_name": self.persona["name"] if self.persona else "Unknown",
            "notification_type": notification_type,  # "info", "warning", "error", "success", "alert"
            "message": message,
            "priority": priority,  # "low", "normal", "high", "critical"
            "auto_hide_enabled": auto_hide,  # Explicitly set - False for critical, True for others
            "auto_hide_duration_seconds": duration_seconds,
            "auto_hide_at": auto_hide_at,
            "visible": True,
            "hidden": False,
            "acknowledged": False,
            "cursor_ide_style": True,  # Similar to Cursor IDE UI behavior
            # Accessibility features
            "accessibility": {
                "large_font": True,  # Always use large font for visibility
                "high_contrast": True,  # High contrast for visibility
                "font_size_multiplier": 1.5,  # 1.5x larger than normal
                "requires_acknowledgment": priority in ["high", "critical"] or notification_type in ["error", "alert"],
                "persistent": priority == "critical" or notification_type in ["error", "alert"],
                "sound_alert": priority in ["high", "critical"],
                "visual_flash": priority == "critical"
            }
        }

        self.notifications.append(notification)

        # Schedule auto-hide if enabled
        if notification["auto_hide_enabled"]:
            notification["status"] = "visible_auto_hide_scheduled"
        else:
            notification["status"] = "visible_persistent"

        logger.warning(f"📢 NOTIFICATION: {self.agent_id} - {notification_type.upper()}: {message} (Priority: {priority}, Auto-hide: {notification['auto_hide_enabled']})")
        return notification

    def create_alert_chat_bubble(
        self,
        alert_type: str,
        message: str,
        auto_hide: bool = True,
        duration_seconds: int = None
    ) -> Dict[str, Any]:
        """Create an alert chat bubble with auto-hide (Cursor IDE style)"""
        return self.create_notification(
            notification_type=alert_type,
            message=message,
            priority="high" if alert_type in ["error", "critical"] else "normal",
            auto_hide=auto_hide,
            duration_seconds=duration_seconds
        )

    def check_auto_hide_notifications(self) -> List[Dict[str, Any]]:
        """Check and auto-hide notifications that have expired (Cursor IDE style)"""
        current_time = datetime.now().timestamp()
        hidden_notifications = []

        for notification in self.notifications:
            # Don't auto-hide if it requires acknowledgment or is persistent
            if notification.get("accessibility", {}).get("requires_acknowledgment") or notification.get("accessibility", {}).get("persistent"):
                continue

            if (notification.get("visible") and
                notification.get("auto_hide_enabled") and
                notification.get("auto_hide_at") and
                current_time >= notification["auto_hide_at"]):
                notification["visible"] = False
                notification["hidden"] = True
                notification["hidden_at"] = datetime.now().isoformat()
                notification["status"] = "auto_hidden"
                hidden_notifications.append(notification)
                logger.debug(f"🔇 Auto-hid notification {notification['notification_id']} (Cursor IDE style)")

        return hidden_notifications

    def acknowledge_notification(self, notification_id: str) -> Dict[str, Any]:
        """Acknowledge a notification (for high/critical priority)"""
        notification = next((n for n in self.notifications if n["notification_id"] == notification_id), None)
        if not notification:
            return {"error": f"Notification not found: {notification_id}"}

        notification["acknowledged"] = True
        notification["acknowledged_at"] = datetime.now().isoformat()

        # If it was persistent and now acknowledged, allow auto-hide after delay
        if notification.get("accessibility", {}).get("persistent"):
            notification["auto_hide_enabled"] = True
            notification["auto_hide_duration_seconds"] = 10  # 10 seconds after acknowledgment
            notification["auto_hide_at"] = datetime.now().timestamp() + 10

        logger.info(f"✅ Notification {notification_id} acknowledged")
        return notification

    def get_unacknowledged_notifications(self) -> List[Dict[str, Any]]:
        """Get all unacknowledged notifications (especially important for visibility)"""
        return [n for n in self.notifications
                if n.get("visible", False) and
                not n.get("acknowledged", False) and
                (n.get("accessibility", {}).get("requires_acknowledgment", False) or
                 n.get("priority") in ["high", "critical"])]

    def get_visible_notifications(self) -> List[Dict[str, Any]]:
        """Get all currently visible notifications"""
        # Check for auto-hide first
        self.check_auto_hide_notifications()
        return [n for n in self.notifications if n.get("visible", False)]

    def _generate_response(
        self,
        message: str,
        context: Dict[str, Any] = None
    ) -> str:
        """Generate response based on modeled personality"""
        # This would use the personality layers to generate appropriate responses
        # For now, return a placeholder that reflects the persona
        persona_name = self.persona["name"] if self.persona else "Agent"
        role = self.role.value.replace("_", " ").title()

        # Use personality attributes to influence response style
        response_style = "formal" if self.modeled_personality.get("formality") == "high" else "casual"
        emotion = self.modeled_personality.get("emotion", "neutral")

        return f"[{persona_name} as {role}] Acknowledged. Processing request with {response_style} {emotion} tone based on modeled personality."

    def manage_system(
        self,
        system_id: str,
        action: str,
        parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Manage a system assigned to this agent"""
        management = {
            "management_id": f"manage_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "agent_name": self.persona["name"] if self.persona else "Unknown",
            "role": self.role.value,
            "system_id": system_id,
            "action": action,
            "parameters": parameters or {},
            "status": "managed"
        }

        self.interaction_history.append(management)
        logger.info(f"✅ Agent {self.agent_id} managing system {system_id}: {action}")
        return management

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary"""
        return {
            "agent_id": self.agent_id,
            "persona_id": self.persona_id,
            "persona": self.persona,
            "role": self.role.value,
            "personality_stack_id": self.personality_stack_id,
            "personality_layers": self.personality_layers,
            "modeled_personality": self.modeled_personality,
            "systems_managed": self.systems_managed,
            "status": self.status,
            "created_at": self.created_at,
            "interaction_count": len(self.interaction_history),
            "operator_interaction_count": len(self.operator_interactions),
            "notifications_count": len(self.notifications),
            "visible_notifications_count": len([n for n in self.notifications if n.get("visible", False)]),
            "auto_hide_enabled": self.auto_hide_enabled,
            "auto_hide_duration_seconds": self.auto_hide_duration_seconds
        }


class InteractiveAvatarAgentsSystem:
    """System for managing interactive avatar agents"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "avatar_agents"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.agents_file = self.data_dir / "agents.json"
        self.interactions_file = self.data_dir / "interactions.jsonl"
        self.system_links_file = self.data_dir / "system_links.json"
        self.notifications_file = self.data_dir / "notifications.json"  # Persistent notifications storage

        # Initialize acting call list and personality system
        if ACTING_CALL_LIST_AVAILABLE:
            try:
                self.acting_call_list = ActingCallList(project_root)
                logger.info("✅ Acting call list initialized for avatar agents")
            except Exception as e:
                logger.warning(f"Acting call list initialization failed: {e}")
                self.acting_call_list = None
        else:
            self.acting_call_list = None

        if PERSONALITY_LAYERS_AVAILABLE:
            try:
                self.personality_system = ModularPersonalitySystem(project_root)
                logger.info("✅ Personality layers system initialized for avatar agents")
            except Exception as e:
                logger.warning(f"Personality layers initialization failed: {e}")
                self.personality_system = None
        else:
            self.personality_system = None

        # Initialize SYPHON system
        if SYPHON_AVAILABLE:
            try:
                self.syphon = SYPHONSystem(project_root)
                logger.info("✅ SYPHON system initialized for avatar agents")
            except Exception as e:
                logger.warning(f"SYPHON initialization failed: {e}")
                self.syphon = None
        else:
            self.syphon = None

        # Load existing agents
        self.agents: Dict[str, InteractiveAvatarAgent] = {}
        self._load_agents()

        # Initialize default agents linking major systems
        if not self.agents:
            self._initialize_default_agents()

    def _load_agents(self):
        """Load agents from file"""
        if self.agents_file.exists():
            try:
                with open(self.agents_file, encoding='utf-8') as f:
                    agents_data = json.load(f)
                    for agent_id, agent_data in agents_data.items():
                        agent = InteractiveAvatarAgent(
                            agent_id=agent_data["agent_id"],
                            persona_id=agent_data["persona_id"],
                            role=AgentRole(agent_data["role"]),
                            personality_stack_id=agent_data.get("personality_stack_id"),
                            systems_managed=agent_data.get("systems_managed", [])
                        )
                        agent.load_persona(self.acting_call_list, self.personality_system)
                        self.agents[agent_id] = agent
            except Exception as e:
                logger.error(f"Error loading agents: {e}")

        # Load persistent notifications
        self._load_notifications()

    def _save_agents(self):
        """Save agents to file"""
        try:
            agents_data = {agent_id: agent.to_dict() for agent_id, agent in self.agents.items()}
            with open(self.agents_file, 'w', encoding='utf-8') as f:
                json.dump(agents_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving agents: {e}")

        # Save persistent notifications
        self._save_notifications()

    def _load_notifications(self):
        """Load persistent notifications for all agents"""
        if not self.notifications_file.exists():
            return

        try:
            with open(self.notifications_file, encoding='utf-8') as f:
                notifications_data = json.load(f)

                for agent_id, notifications_list in notifications_data.items():
                    if agent_id in self.agents:
                        agent = self.agents[agent_id]
                        # Restore notifications to agent
                        for notif_data in notifications_list:
                            # Only restore visible or unacknowledged notifications
                            if notif_data.get("visible", False) or not notif_data.get("acknowledged", False):
                                agent.notifications.append(notif_data)
        except Exception as e:
            logger.error(f"Error loading notifications: {e}")

    def _save_notifications(self):
        """Save persistent notifications for all agents"""
        try:
            notifications_data = {}
            for agent_id, agent in self.agents.items():
                # Save all notifications (including hidden for history)
                notifications_data[agent_id] = agent.notifications

            with open(self.notifications_file, 'w', encoding='utf-8') as f:
                json.dump(notifications_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving notifications: {e}")

    def _initialize_default_agents(self):
        """Initialize default agents linking major and minor systems"""
        default_agents = [
            {
                "agent_id": "jarvis_coordinator",
                "persona_id": "jarvis_iron_man",
                "role": AgentRole.SYSTEM_COORDINATOR,
                "systems_managed": [
                    "automatic_supervision",
                    "universal_measurement_system",
                    "autoproc_executor"
                ],
                "personality_stack_id": None
            },
            {
                "agent_id": "wopr_analyst",
                "persona_id": "jarvis_wopr",
                "role": AgentRole.INTELLIGENCE_ANALYST,
                "systems_managed": [
                    "intelligence_analysis",
                    "comprehensive_advice",
                    "wopr_memory"
                ],
                "personality_stack_id": None
            },
            {
                "agent_id": "marvin_supervisor",
                "persona_id": "jarvis_marvin",
                "role": AgentRole.SUPERVISOR,
                "systems_managed": [
                    "automatic_supervision",
                    "threat_response_framework"
                ],
                "personality_stack_id": None
            },
            {
                "agent_id": "hk47_threat_response",
                "persona_id": "jarvis_hk47",
                "role": AgentRole.THREAT_RESPONSE,
                "systems_managed": [
                    "threat_response_framework",
                    "comprehensive_threat_response",
                    "bounty_investigation_system"
                ],
                "personality_stack_id": None
            },
            {
                "agent_id": "data_advisor",
                "persona_id": "jarvis_data",
                "role": AgentRole.ADVISOR,
                "systems_managed": [
                    "comprehensive_advice",
                    "historical_knowledge_power"
                ],
                "personality_stack_id": None
            },
            {
                "agent_id": "c3po_operator_assistant",
                "persona_id": "jarvis_c3po",
                "role": AgentRole.OPERATOR_ASSISTANT,
                "systems_managed": [
                    "friendship_balance",
                    "literature_media_interest",
                    "come_to_life_recognition"
                ],
                "personality_stack_id": None
            },
            {
                "agent_id": "vision_peace_initiative",
                "persona_id": "jarvis_vision",
                "role": AgentRole.PEACE_INITIATIVE,
                "systems_managed": [
                    "global_peace_initiative",
                    "ai_rights_framework"
                ],
                "personality_stack_id": None
            },
            {
                "agent_id": "r2d2_merit_tracker",
                "persona_id": "jarvis_r2d2",
                "role": AgentRole.MERIT_TRACKER,
                "systems_managed": [
                    "merit_progression_system"
                ],
                "personality_stack_id": None
            },
            {
                "agent_id": "friday_measurement_analyst",
                "persona_id": "jarvis_friday",
                "role": AgentRole.MEASUREMENT_ANALYST,
                "systems_managed": [
                    "universal_measurement_system"
                ],
                "personality_stack_id": None
            },
            {
                "agent_id": "glados_terminal_monitor",
                "persona_id": "jarvis_glados",
                "role": AgentRole.TERMINAL_MONITOR,
                "systems_managed": [
                    "terminal_health_monitor"
                ],
                "personality_stack_id": None
            },
            {
                "agent_id": "amanita_clone_manager",
                "persona_id": "jarvis_amanita",
                "role": AgentRole.CLONE_MANAGER,
                "systems_managed": [
                    "acting_call_list",
                    "modular_personality_layers"
                ],
                "personality_stack_id": None
            }
        ]

        for agent_data in default_agents:
            agent = InteractiveAvatarAgent(
                agent_id=agent_data["agent_id"],
                persona_id=agent_data["persona_id"],
                role=agent_data["role"],
                personality_stack_id=agent_data.get("personality_stack_id"),
                systems_managed=agent_data.get("systems_managed", [])
            )

            if self.acting_call_list:
                agent.load_persona(self.acting_call_list, self.personality_system)

            self.agents[agent_data["agent_id"]] = agent

        self._save_agents()
        logger.info(f"✅ Initialized {len(default_agents)} default avatar agents")

    def create_agent(
        self,
        agent_id: str,
        persona_id: str,
        role: AgentRole,
        personality_stack_id: str = None,
        systems_managed: List[str] = None
    ) -> InteractiveAvatarAgent:
        """Create a new interactive avatar agent"""
        agent = InteractiveAvatarAgent(
            agent_id=agent_id,
            persona_id=persona_id,
            role=role,
            personality_stack_id=personality_stack_id,
            systems_managed=systems_managed or []
        )

        if self.acting_call_list:
            agent.load_persona(self.acting_call_list, self.personality_system)

        self.agents[agent_id] = agent
        self._save_agents()

        logger.info(f"✅ Created avatar agent: {agent_id} ({persona_id} as {role.value})")
        return agent

    def link_systems(
        self,
        agent_id: str,
        system_ids: List[str]
    ) -> Dict[str, Any]:
        """Link systems to an agent"""
        if agent_id not in self.agents:
            return {"error": f"Agent not found: {agent_id}"}

        agent = self.agents[agent_id]
        agent.systems_managed.extend(system_ids)
        agent.systems_managed = list(set(agent.systems_managed))  # Remove duplicates

        self._save_agents()

        logger.info(f"✅ Linked {len(system_ids)} systems to agent {agent_id}")
        return {
            "agent_id": agent_id,
            "systems_managed": agent.systems_managed,
            "status": "linked"
        }

    def operator_interact(
        self,
        agent_id: str,
        message: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Operator (@OP) interaction with agent"""
        if agent_id not in self.agents:
            return {"error": f"Agent not found: {agent_id}"}

        agent = self.agents[agent_id]
        interaction = agent.interact_with_operator(message, context)

        # Create notification chat bubble with auto-hide (Cursor IDE style)
        notification = agent.create_notification(
            notification_type="info",
            message=f"Operator interaction: {message[:100]}",
            auto_hide=True,
            duration_seconds=5  # Cursor IDE default
        )

        # Save interaction
        try:
            with open(self.interactions_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(interaction) + '\n')
        except Exception as e:
            logger.error(f"Error saving interaction: {e}")

        return interaction

    def create_agent_notification(
        self,
        agent_id: str,
        notification_type: str,
        message: str,
        auto_hide: bool = True,
        duration_seconds: int = None,
        priority: str = None
    ) -> Dict[str, Any]:
        """Create a notification from an agent with auto-hide"""
        if agent_id not in self.agents:
            return {"error": f"Agent not found: {agent_id}"}

        # Auto-detect priority based on notification type if not provided
        if priority is None:
            if notification_type in ["error", "alert"]:
                priority = "critical"
            elif notification_type == "warning":
                priority = "high"
            else:
                priority = "normal"

        agent = self.agents[agent_id]
        notification = agent.create_notification(
            notification_type=notification_type,
            message=message,
            priority=priority,
            auto_hide=auto_hide,
            duration_seconds=duration_seconds
        )

        # Save notifications immediately
        self._save_notifications()

        return notification

    def get_all_visible_notifications(self) -> Dict[str, Any]:
        """Get all visible notifications from all agents (Cursor IDE style)"""
        all_notifications = {
            "timestamp": datetime.now().isoformat(),
            "total_agents": len(self.agents),
            "visible_notifications": [],
            "unacknowledged_notifications": [],
            "critical_notifications": [],
            "auto_hide_enabled": True,
            "cursor_ide_style": True,
            "accessibility_enabled": True
        }

        for agent_id, agent in self.agents.items():
            visible = agent.get_visible_notifications()
            unacknowledged = agent.get_unacknowledged_notifications()

            for notification in visible:
                notification["agent_id"] = agent_id
                notification["agent_name"] = agent.persona["name"] if agent.persona else "Unknown"
                all_notifications["visible_notifications"].append(notification)

                # Track critical and unacknowledged separately for visibility
                if notification.get("priority") == "critical" or notification.get("notification_type") in ["error", "alert"]:
                    all_notifications["critical_notifications"].append(notification)
                if notification in unacknowledged:
                    all_notifications["unacknowledged_notifications"].append(notification)

        all_notifications["total_visible"] = len(all_notifications["visible_notifications"])
        all_notifications["total_unacknowledged"] = len(all_notifications["unacknowledged_notifications"])
        all_notifications["total_critical"] = len(all_notifications["critical_notifications"])
        return all_notifications

    def get_notification_history(
        self,
        hours: int = 24,
        include_hidden: bool = True
    ) -> Dict[str, Any]:
        """Get notification history for past N hours (for accessibility - see past notifications)"""
        cutoff_time = datetime.now().timestamp() - (hours * 3600)

        history = {
            "timestamp": datetime.now().isoformat(),
            "hours": hours,
            "notifications": [],
            "by_agent": {},
            "by_priority": {"critical": [], "high": [], "normal": [], "low": []},
            "by_type": {"error": [], "warning": [], "alert": [], "info": [], "success": []}
        }

        for agent_id, agent in self.agents.items():
            agent_notifications = []
            for notification in agent.notifications:
                notif_time = datetime.fromisoformat(notification["timestamp"]).timestamp()
                if notif_time >= cutoff_time:
                    if include_hidden or notification.get("visible", False):
                        notification["agent_id"] = agent_id
                        notification["agent_name"] = agent.persona["name"] if agent.persona else "Unknown"
                        agent_notifications.append(notification)
                        history["notifications"].append(notification)

                        # Categorize
                        priority = notification.get("priority", "normal")
                        if priority in history["by_priority"]:
                            history["by_priority"][priority].append(notification)

                        notif_type = notification.get("notification_type", "info")
                        if notif_type in history["by_type"]:
                            history["by_type"][notif_type].append(notification)

            if agent_notifications:
                history["by_agent"][agent_id] = agent_notifications

        history["total"] = len(history["notifications"])
        return history

    def acknowledge_notification_system(
        self,
        notification_id: str,
        agent_id: str = None
    ) -> Dict[str, Any]:
        """Acknowledge a notification system-wide"""
        if agent_id:
            if agent_id not in self.agents:
                return {"error": f"Agent not found: {agent_id}"}
            return self.agents[agent_id].acknowledge_notification(notification_id)
        else:
            # Search all agents
            for agent in self.agents.values():
                result = agent.acknowledge_notification(notification_id)
                if "error" not in result:
                    return result
            return {"error": f"Notification not found: {notification_id}"}

    def process_auto_hide_all_agents(self) -> Dict[str, Any]:
        """Process auto-hide for all agents (Cursor IDE style)"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "agents_processed": 0,
            "notifications_hidden": 0,
            "hidden_notifications": []
        }

        for agent_id, agent in self.agents.items():
            hidden = agent.check_auto_hide_notifications()
            if hidden:
                result["agents_processed"] += 1
                result["notifications_hidden"] += len(hidden)
                for notif in hidden:
                    notif["agent_id"] = agent_id
                    result["hidden_notifications"].append(notif)

        return result

    def generate_system_links_report(self) -> Dict[str, Any]:
        """Generate report of all system links through avatar agents"""
        report = {
            "report_id": f"links_report_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "total_agents": len(self.agents),
            "agents": [],
            "system_coverage": {},
            "syphon_intelligence": {}
        }

        # Collect all systems and their managing agents
        all_systems = set()
        for agent in self.agents.values():
            agent_dict = agent.to_dict()
            report["agents"].append(agent_dict)
            for system_id in agent.systems_managed:
                all_systems.add(system_id)
                if system_id not in report["system_coverage"]:
                    report["system_coverage"][system_id] = []
                report["system_coverage"][system_id].append(agent.agent_id)

        report["total_systems_linked"] = len(all_systems)
        report["systems"] = list(all_systems)

        # Use SYPHON to extract intelligence
        if self.syphon:
            try:
                content = json.dumps(report, default=str)
                syphon_result = self._syphon_extract_links_intelligence(content)
                if syphon_result:
                    report["syphon_intelligence"] = syphon_result
            except Exception as e:
                logger.warning(f"SYPHON links extraction failed: {e}")

        return report

    def _syphon_extract_links_intelligence(self, content: str) -> Dict[str, Any]:
        """Extract intelligence using SYPHON system"""
        if not self.syphon:
            return {}

        try:
            syphon_data = self.syphon.syphon_generic(
                content=content,
                source_type=DataSourceType.DOCUMENT,
                source_id=f"links_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                metadata={"avatar_agents": True, "system_linking": True}
            )

            return {
                "actionable_items": syphon_data.actionable_items,
                "tasks": syphon_data.tasks,
                "decisions": syphon_data.decisions,
                "intelligence": [item for item in syphon_data.intelligence]
            }
        except Exception as e:
            logger.error(f"SYPHON links extraction error: {e}")
            return {}


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Interactive Avatar Agents")
        parser.add_argument("--create-agent", type=str, nargs=5, metavar=("AGENT_ID", "PERSONA_ID", "ROLE", "STACK_ID", "SYSTEMS_JSON"),
                           help="Create a new avatar agent")
        parser.add_argument("--link-systems", type=str, nargs=2, metavar=("AGENT_ID", "SYSTEMS_JSON"),
                           help="Link systems to agent")
        parser.add_argument("--operator-interact", type=str, nargs=3, metavar=("AGENT_ID", "MESSAGE", "CONTEXT_JSON"),
                           help="Operator interaction with agent")
        parser.add_argument("--list-agents", action="store_true", help="List all agents")
        parser.add_argument("--create-notification", type=str, nargs=4, metavar=("AGENT_ID", "TYPE", "MESSAGE", "DURATION"),
                           help="Create notification with auto-hide")
        parser.add_argument("--get-notifications", action="store_true", help="Get all visible notifications")
        parser.add_argument("--get-history", type=int, metavar="HOURS", help="Get notification history (default: 24 hours)")
        parser.add_argument("--acknowledge", type=str, nargs=2, metavar=("NOTIFICATION_ID", "AGENT_ID"),
                           help="Acknowledge a notification")
        parser.add_argument("--process-auto-hide", action="store_true", help="Process auto-hide for all agents")
        parser.add_argument("--report", action="store_true", help="Generate system links report")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        system = InteractiveAvatarAgentsSystem(project_root)

        if args.create_agent:
            import json as json_lib
            systems = json_lib.loads(args.create_agent[4]) if args.create_agent[4] != "[]" else []
            agent = system.create_agent(
                agent_id=args.create_agent[0],
                persona_id=args.create_agent[1],
                role=AgentRole(args.create_agent[2]),
                personality_stack_id=args.create_agent[3] if args.create_agent[3] != "None" else None,
                systems_managed=systems
            )
            print("=" * 80)
            print("✅ AVATAR AGENT CREATED")
            print("=" * 80)
            print(json.dumps(agent.to_dict(), indent=2, default=str))

        elif args.link_systems:
            import json as json_lib
            systems = json_lib.loads(args.link_systems[1])
            result = system.link_systems(args.link_systems[0], systems)
            print("=" * 80)
            print("✅ SYSTEMS LINKED")
            print("=" * 80)
            print(json.dumps(result, indent=2, default=str))

        elif args.operator_interact:
            import json as json_lib
            context = json_lib.loads(args.operator_interact[2]) if args.operator_interact[2] != "{}" else {}
            interaction = system.operator_interact(args.operator_interact[0], args.operator_interact[1], context)
            print("=" * 80)
            print("💬 OPERATOR INTERACTION")
            print("=" * 80)
            print(json.dumps(interaction, indent=2, default=str))

        elif args.list_agents:
            agents = [agent.to_dict() for agent in system.agents.values()]
            print("=" * 80)
            print("🤖 INTERACTIVE AVATAR AGENTS")
            print("=" * 80)
            print(f"Total: {len(agents)}")
            print(json.dumps(agents, indent=2, default=str))

        elif args.create_notification:
            # Parse duration - if 0, means persistent (no auto-hide)
            duration_str = args.create_notification[3] if len(args.create_notification) > 3 else "5"
            duration = int(duration_str) if duration_str and duration_str != "0" else None
            auto_hide = duration is not None and duration > 0

            # Auto-detect priority from notification type
            notif_type = args.create_notification[1]
            priority = "critical" if notif_type in ["error", "alert"] else ("high" if notif_type == "warning" else "normal")

            notification = system.create_agent_notification(
                agent_id=args.create_notification[0],
                notification_type=notif_type,
                message=args.create_notification[2],
                priority=priority,
                auto_hide=auto_hide,
                duration_seconds=duration
            )
            print("=" * 80)
            if notification.get("accessibility", {}).get("persistent"):
                print("📢 CRITICAL NOTIFICATION CREATED (PERSISTENT - LARGE FONT, HIGH CONTRAST)")
            else:
                print("📢 NOTIFICATION CREATED (Auto-Hide Enabled)")
            print("=" * 80)
            print(f"Priority: {notification.get('priority', 'normal')}")
            print(f"Persistent: {notification.get('accessibility', {}).get('persistent', False)}")
            print(f"Large Font: {notification.get('accessibility', {}).get('large_font', False)}")
            print(f"High Contrast: {notification.get('accessibility', {}).get('high_contrast', False)}")
            print("=" * 80)
            print(json.dumps(notification, indent=2, default=str))

        elif args.get_notifications:
            notifications = system.get_all_visible_notifications()
            print("=" * 80)
            print("📢 VISIBLE NOTIFICATIONS (Accessibility Enhanced)")
            print("=" * 80)
            print(f"Total Visible: {notifications['total_visible']}")
            print(f"Unacknowledged: {notifications['total_unacknowledged']}")
            print(f"Critical: {notifications['total_critical']}")
            if notifications['critical_notifications']:
                print("\n⚠️  CRITICAL NOTIFICATIONS (LARGE FONT, HIGH CONTRAST):")
                for notif in notifications['critical_notifications']:
                    print(f"  [{notif['agent_name']}] {notif['notification_type'].upper()}: {notif['message']}")
            if notifications['unacknowledged_notifications']:
                print("\n🔔 UNACKNOWLEDGED NOTIFICATIONS:")
                for notif in notifications['unacknowledged_notifications']:
                    print(f"  [{notif['agent_name']}] {notif['notification_type'].upper()}: {notif['message']}")
            print("=" * 80)
            print(json.dumps(notifications, indent=2, default=str))

        elif args.get_history:
            hours = args.get_history if args.get_history > 0 else 24
            history = system.get_notification_history(hours=hours, include_hidden=True)
            print("=" * 80)
            print(f"📜 NOTIFICATION HISTORY (Last {hours} hours)")
            print("=" * 80)
            print(f"Total Notifications: {history['total']}")
            print(f"Critical: {len(history['by_priority']['critical'])}")
            print(f"High: {len(history['by_priority']['high'])}")
            print(f"Errors: {len(history['by_type']['error'])}")
            print(f"Warnings: {len(history['by_type']['warning'])}")
            if history['by_priority']['critical']:
                print("\n⚠️  CRITICAL NOTIFICATIONS IN HISTORY:")
                for notif in history['by_priority']['critical'][-10:]:  # Last 10 critical
                    print(f"  [{notif['timestamp']}] [{notif['agent_name']}] {notif['message']}")
            print("=" * 80)
            print(json.dumps(history, indent=2, default=str))

        elif args.acknowledge:
            result = system.acknowledge_notification_system(args.acknowledge[0], args.acknowledge[1] if len(args.acknowledge) > 1 else None)
            print("=" * 80)
            print("✅ NOTIFICATION ACKNOWLEDGED")
            print("=" * 80)
            print(json.dumps(result, indent=2, default=str))

        elif args.process_auto_hide:
            result = system.process_auto_hide_all_agents()
            print("=" * 80)
            print("🔇 AUTO-HIDE PROCESSED (Cursor IDE Style)")
            print("=" * 80)
            print(f"Notifications Hidden: {result['notifications_hidden']}")
            print(json.dumps(result, indent=2, default=str))

        elif args.report:
            report = system.generate_system_links_report()
            print("=" * 80)
            print("🔗 SYSTEM LINKS REPORT")
            print("=" * 80)
            print(f"Total Agents: {report['total_agents']}")
            print(f"Total Systems Linked: {report['total_systems_linked']}")
            print("=" * 80)
            print(json.dumps(report, indent=2, default=str))

        else:
            # Default: generate report
            report = system.generate_system_links_report()
            print("=" * 80)
            print("🤖 JARVIS INTERACTIVE AVATAR AGENTS")
            print("=" * 80)
            print(f"Total Agents: {report['total_agents']}")
            print(f"Total Systems Linked: {report['total_systems_linked']}")
            print("=" * 80)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()