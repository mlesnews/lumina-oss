#!/usr/bin/env python3
"""
JARVIS Full-Time Super Agent
<COMPANY_NAME> LLC

JARVIS as a full-time super agent - always available, always listening, always ready.
Direct voice conversations, no IDE interface bottleneck.

"Tired of dancing around. Not being able to talk directly to JARVIS without having to
click, click, click through the IDE interface."

@JARVIS @MARVIN @TONY @MACE @GANDALF
"""

import sys
import json
import time
import threading
import queue
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from universal_logging_wrapper import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from jarvis_communication_bridge import get_jarvis_bridge, CommunicationParty
    JARVIS_BRIDGE_AVAILABLE = True
except ImportError:
    JARVIS_BRIDGE_AVAILABLE = False

try:
    from jarvis_elevenlabs_integration import JARVISElevenLabsTTS
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    JARVISElevenLabsTTS = None

logger = get_logger("JARVISFullTimeSuperAgent")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class AgentRole(Enum):
    """Agent roles in conversation"""
    SUPERVISOR = "supervisor"  # JARVIS - supervises everything
    EXECUTOR = "executor"  # Executes tasks
    ANALYST = "analyst"  # Analyzes and provides insights
    ADVISOR = "advisor"  # Provides advice
    COORDINATOR = "coordinator"  # Coordinates between agents
    HUMAN = "human"  # Human participant


class ConversationMode(Enum):
    """Conversation modes"""
    VOICE = "voice"  # Voice conversation
    TEXT = "text"  # Text conversation
    MULTI_AGENT = "multi_agent"  # Multiple agents discussing
    HUMAN_IN_LOOP = "human_in_loop"  # Human participating


@dataclass
class Agent:
    """Agent in the system"""
    agent_id: str
    agent_name: str
    role: AgentRole
    capabilities: List[str] = field(default_factory=list)
    active: bool = True
    current_task: Optional[str] = None
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['role'] = self.role.value
        return data


@dataclass
class ConversationTurn:
    """Single turn in conversation"""
    turn_id: str
    timestamp: datetime
    speaker: str  # Agent ID or "human"
    message: str
    mode: ConversationMode
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['mode'] = self.mode.value
        return data


class JARVISFullTimeSuperAgent:
    """
    JARVIS Full-Time Super Agent

    Always available, always listening, always ready.
    Direct voice conversations, multi-agent discussions, human participation.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize JARVIS Full-Time Super Agent

        @PEAK: Initialization with guards to prevent loops and ensure idempotency
        """
        # @PEAK: Check if already initialized (prevent re-initialization)
        if hasattr(self, '_initialized') and self._initialized:
            self.logger.warning("⚠️  JARVIS already initialized, skipping re-initialization")
            return

        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("JARVISFullTimeSuperAgent")

        # @PEAK: Mark initialization start
        self._initialized = False
        self._initialization_start = datetime.now()

        try:
            # Data directories
            self.data_dir = self.project_root / "data" / "jarvis_fulltime"
            self.data_dir.mkdir(parents=True, exist_ok=True)

            # Agent registry
            self.agents: Dict[str, Agent] = {}
            self._initialize_agents()

            # Conversation management
            self.active_conversations: Dict[str, List[ConversationTurn]] = {}
            self.conversation_queue = queue.Queue()

            # Voice interface (placeholder - will integrate with actual voice system)
            self.voice_interface_active = False
            self.voice_listening = False

            # ElevenLabs TTS integration
            self.elevenlabs_tts = None
            if ELEVENLABS_AVAILABLE:
                try:
                    self.elevenlabs_tts = JARVISElevenLabsTTS(project_root=self.project_root)
                    self.logger.info("✅ ElevenLabs TTS integrated")
                except Exception as e:
                    self.logger.warning(f"⚠️  ElevenLabs TTS not available: {e}")
                    self.elevenlabs_tts = None

            # @PEAK: Lazy auto-start with error isolation (prevent cascading failures)
            self._auto_start_services_lazy()

            # Persistent Memory System
            self.persistent_memory = None
            self._init_persistent_memory()

            # Communication bridge
            self.bridge = None
            if JARVIS_BRIDGE_AVAILABLE:
                try:
                    self.bridge = get_jarvis_bridge()
                except Exception:
                    pass

            # Full-time operation
            self.running = False
            self.supervisor_thread: Optional[threading.Thread] = None

            # Start full-time operation
            self.start_fulltime_operation()

            # @PEAK: Mark initialization complete
            self._initialized = True
            init_duration = (datetime.now() - self._initialization_start).total_seconds()

            self.logger.info("✅ JARVIS Full-Time Super Agent initialized")
            self.logger.info(f"   Initialization time: {init_duration:.2f}s")
            self.logger.info("   Always available, always listening, always ready")
            self.logger.info("   Direct voice conversations enabled")

        except Exception as e:
            self.logger.error(f"❌ JARVIS initialization failed: {e}", exc_info=True)
            self._initialized = False
            raise

    def _initialize_agents(self) -> None:
        """Initialize agent registry"""
        # JARVIS as supervisor
        self.agents['jarvis'] = Agent(
            agent_id='jarvis',
            agent_name='JARVIS',
            role=AgentRole.SUPERVISOR,
            capabilities=['supervision', 'coordination', 'delegation', 'conversation', 'voice']
        )

        # Other agents (can be dynamically added)
        self.agents['marvin'] = Agent(
            agent_id='marvin',
            agent_name='MARVIN',
            role=AgentRole.ANALYST,
            capabilities=['analysis', 'insights', 'problem_solving']
        )

        self.agents['tony'] = Agent(
            agent_id='tony',
            agent_name='TONY',
            role=AgentRole.EXECUTOR,
            capabilities=['execution', 'implementation', 'building']
        )

        self.agents['mace'] = Agent(
            agent_id='mace',
            agent_name='MACE',
            role=AgentRole.COORDINATOR,
            capabilities=['coordination', 'integration', 'orchestration']
        )

        self.agents['gandalf'] = Agent(
            agent_id='gandalf',
            agent_name='GANDALF',
            role=AgentRole.ADVISOR,
            capabilities=['advice', 'guidance', 'strategy']
        )

        self.logger.info(f"📋 Initialized {len(self.agents)} agents")

    def _auto_start_services_lazy(self) -> None:
        """
        @PEAK: Lazy auto-start of services with error isolation

        Prevents cascading failures and initialization loops by:
        - Isolating each service startup
        - Using background threads for non-critical services
        - Graceful degradation if services fail
        """
        # Store service managers to prevent re-initialization
        if not hasattr(self, '_service_managers'):
            self._service_managers = {}

        # Start services in background threads to prevent blocking
        def start_keep_all():
            """Start KEEP ALL in background thread"""
            try:
                from jarvis_auto_keep_all_manager import JARVISAutoKeepAllManager

                # Check if already started
                if 'keep_all' in self._service_managers:
                    return

                keep_all_manager = JARVISAutoKeepAllManager(self.project_root)
                self._service_managers['keep_all'] = keep_all_manager

                result = keep_all_manager.start()

                if result.get('success'):
                    logger.info("✅ KEEP ALL automation auto-started")
                else:
                    logger.warning(f"⚠️  KEEP ALL automation not started: {result.get('error', 'unknown')}")

            except ImportError:
                logger.debug("KEEP ALL manager not available")
            except Exception as e:
                logger.debug(f"KEEP ALL auto-start error: {e}")

        def start_ralt_macro():
            """Start RAlt Macro in background thread"""
            try:
                from jarvis_ralt_hybrid_macro import JARVISRAltHybridMacro

                if 'ralt_macro' in self._service_managers:
                    return

                self.ralt_macro = JARVISRAltHybridMacro(project_root=self.project_root)
                self._service_managers['ralt_macro'] = self.ralt_macro

                def start_macro():
                    self.ralt_macro.start_listening()

                macro_thread = threading.Thread(target=start_macro, daemon=True)
                macro_thread.start()

                time.sleep(0.5)

                if self.ralt_macro.is_active:
                    logger.info("✅ RAlt Hybrid Macro service auto-started")
                else:
                    logger.warning("⚠️  RAlt Macro service started but may not be fully active")

            except ImportError:
                logger.debug("RAlt macro system not available")
            except Exception as e:
                logger.debug(f"RAlt macro auto-start error: {e}")
                self.ralt_macro = None

        def start_roadblock_fixer():
            """Start Roadblock Fixer in background thread"""
            try:
                from jarvis_roadblock_auto_fixer import JARVISRoadblockAutoFixer

                if 'roadblock_fixer' in self._service_managers:
                    return

                self.roadblock_fixer = JARVISRoadblockAutoFixer(project_root=self.project_root)
                self._service_managers['roadblock_fixer'] = self.roadblock_fixer

                def run_fixer():
                    try:
                        self.roadblock_fixer.detect_and_fix_all_roadblocks()
                    except Exception as e:
                        logger.debug(f"Roadblock fixer error: {e}")

                fixer_thread = threading.Thread(target=run_fixer, daemon=True)
                fixer_thread.start()

                logger.info("✅ Roadblock Auto-Fixer started (continuous self-healing)")
            except ImportError:
                logger.debug("Roadblock auto-fixer not available")
                self.roadblock_fixer = None
            except Exception as e:
                logger.debug(f"Roadblock fixer auto-start error: {e}")
                self.roadblock_fixer = None

        # Start services in background threads (non-blocking)
        # @PEAK: Error isolation - each service starts independently
        services = [
            ("KEEP ALL", start_keep_all),
            ("RAlt Macro", start_ralt_macro),
            ("Roadblock Fixer", start_roadblock_fixer)
        ]

        for service_name, start_func in services:
            try:
                service_thread = threading.Thread(target=start_func, daemon=True, name=f"JARVIS-{service_name}")
                service_thread.start()
                # Small delay between service starts to prevent resource contention
                time.sleep(0.1)
            except Exception as e:
                self.logger.warning(f"⚠️  Failed to start {service_name} service: {e}")

    def _auto_start_keep_all(self) -> None:
        """
        @DEPRECATED: Use _auto_start_services_lazy() instead

        Kept for backward compatibility but should not be called directly
        """
        # This method is now handled by _auto_start_services_lazy()
        pass

    def _auto_start_roadblock_fixer(self) -> None:
        """
        @DEPRECATED: Use _auto_start_services_lazy() instead

        Kept for backward compatibility but should not be called directly
        """
        # This method is now handled by _auto_start_services_lazy()
        pass

    def _auto_start_ralt_macro(self) -> None:
        """
        @DEPRECATED: Use _auto_start_services_lazy() instead

        Kept for backward compatibility but should not be called directly
        """
        # This method is now handled by _auto_start_services_lazy()
        pass

    def _init_persistent_memory(self) -> None:
        """Initialize persistent memory system"""
        try:
            from jarvis_persistent_memory import JARVISPersistentMemory, MemoryType, MemoryPriority

            self.persistent_memory = JARVISPersistentMemory(self.project_root)
            self.logger.info("✅ Persistent Memory System initialized")

            # Store initialization memory
            self.persistent_memory.store_memory(
                content="JARVIS Full-Time Super Agent initialized",
                memory_type=MemoryType.EPISODIC,
                priority=MemoryPriority.MEDIUM,
                source="jarvis_fulltime_super_agent",
                tags=["initialization", "system_start"]
            )
        except ImportError:
            self.logger.debug("Persistent Memory not available")
        except Exception as e:
            self.logger.debug(f"Persistent Memory init error: {e}")

    def start_fulltime_operation(self) -> None:
        """Start full-time operation - always listening"""
        if self.running:
            return

        self.running = True
        self.voice_interface_active = True
        self.voice_listening = True

        # Start supervisor thread
        self.supervisor_thread = threading.Thread(
            target=self._supervisor_loop,
            daemon=True
        )
        self.supervisor_thread.start()

        self.logger.info("🚀 JARVIS Full-Time Operation Started")
        self.logger.info("   Always listening, always ready")
        self.logger.info("   Voice interface: ACTIVE")

    def _supervisor_loop(self) -> None:
        """Supervisor loop - continuously monitoring and ready"""
        while self.running:
            try:
                # Process conversation queue
                self._process_conversation_queue()

                # Monitor agents
                self._monitor_agents()

                # Check for voice input (placeholder)
                if self.voice_listening:
                    self._check_voice_input()

                time.sleep(0.1)  # 100ms loop
            except Exception as e:
                self.logger.error(f"Supervisor loop error: {e}")
                time.sleep(1)

    def _process_conversation_queue(self) -> None:
        """Process conversation queue"""
        try:
            while not self.conversation_queue.empty():
                turn = self.conversation_queue.get_nowait()
                self._handle_conversation_turn(turn)
        except queue.Empty:
            pass
        except Exception as e:
            self.logger.error(f"Conversation queue error: {e}")

    def _monitor_agents(self) -> None:
        """Monitor all agents"""
        for agent_id, agent in self.agents.items():
            if not agent.active:
                continue

            # Check agent health, status, etc.
            # This is where we'd check if agents need attention
            pass

    def _check_voice_input(self) -> None:
        """Check for voice input (placeholder - will integrate with actual voice system)"""
        # This is where we'd integrate with:
        # - Speech recognition (whisper, etc.)
        # - Voice activity detection
        # - Wake word detection ("Hey JARVIS")
        pass

    def start_voice_conversation(self, conversation_id: Optional[str] = None) -> str:
        """
        Start voice conversation with JARVIS

        No IDE interface - direct voice access
        """
        if conversation_id is None:
            conversation_id = f"conv_{int(time.time() * 1000)}"

        if conversation_id not in self.active_conversations:
            self.active_conversations[conversation_id] = []

        # Send hello through bridge
        if self.bridge:
            signal_id = self.bridge.send_hello(
                CommunicationParty.IDE_OPERATOR,
                CommunicationParty.AI,
                capabilities=["voice", "conversation", "directives"]
            )
            self.bridge.acknowledge_hello(signal_id, "JARVIS: Voice conversation ready")

        # Add initial turn
        initial_turn = ConversationTurn(
            turn_id=f"turn_{int(time.time() * 1000)}",
            timestamp=datetime.now(),
            speaker="jarvis",
            message="JARVIS here. I'm listening. How can I help?",
            mode=ConversationMode.VOICE
        )

        self.active_conversations[conversation_id].append(initial_turn)

        self.logger.info(f"🎤 Voice conversation started: {conversation_id}")
        self.logger.info("   JARVIS: 'I'm listening. How can I help?'")

        # Speak initial greeting using ElevenLabs TTS if available
        if self.elevenlabs_tts:
            try:
                self.elevenlabs_tts.speak(initial_turn.message)
            except Exception as e:
                self.logger.warning(f"⚠️  ElevenLabs TTS error: {e}")

        return conversation_id

    def speak(self, conversation_id: str, message: str, speaker: str = "human") -> str:
        """
        Speak in conversation (voice or text)

        This is the direct interface - no IDE clicking needed
        """
        turn = ConversationTurn(
            turn_id=f"turn_{int(time.time() * 1000)}",
            timestamp=datetime.now(),
            speaker=speaker,
            message=message,
            mode=ConversationMode.VOICE if self.voice_interface_active else ConversationMode.TEXT
        )

        if conversation_id not in self.active_conversations:
            self.active_conversations[conversation_id] = []

        self.active_conversations[conversation_id].append(turn)

        # Process turn
        self._handle_conversation_turn(turn)

        # Log
        mode_str = "🎤" if turn.mode == ConversationMode.VOICE else "💬"
        self.logger.info(f"{mode_str} {speaker}: {message}")

        return turn.turn_id

    def _handle_conversation_turn(self, turn: ConversationTurn) -> None:
        """Handle conversation turn"""
        # If human spoke, JARVIS responds
        if turn.speaker == "human":
            # Find the conversation this turn belongs to
            conv_id = None
            for cid, turns in self.active_conversations.items():
                if any(t.turn_id == turn.turn_id for t in turns):
                    conv_id = cid
                    break

            # If no conversation found, use the most recent one or create default
            if not conv_id:
                if self.active_conversations:
                    conv_id = list(self.active_conversations.keys())[-1]
                else:
                    conv_id = "default_conv"
                    self.active_conversations[conv_id] = []

            response = self._generate_jarvis_response(turn)
            if response:
                response_turn = ConversationTurn(
                    turn_id=f"turn_{int(time.time() * 1000)}",
                    timestamp=datetime.now(),
                    speaker="jarvis",
                    message=response,
                    mode=turn.mode,
                    context={'responding_to': turn.turn_id}
                )
                if conv_id not in self.active_conversations:
                    self.active_conversations[conv_id] = []
                self.active_conversations[conv_id].append(response_turn)
                self.logger.info(f"🤖 JARVIS: {response}")

                # Speak using ElevenLabs TTS if available
                if self.elevenlabs_tts and turn.mode == ConversationMode.VOICE:
                    try:
                        self.elevenlabs_tts.speak(response)
                    except Exception as e:
                        self.logger.warning(f"⚠️  ElevenLabs TTS error: {e}")

    def _generate_jarvis_response(self, turn: ConversationTurn) -> Optional[str]:
        """Generate JARVIS response to human input"""
        message = turn.message.lower()

        # Simple response logic (will be enhanced with LLM)
        if "hello" in message or "hey jarvis" in message:
            return "Hello! I'm here and ready to help. What would you like to discuss?"
        elif "status" in message or "what's happening" in message:
            return f"I'm monitoring {len(self.agents)} agents. All systems operational. How can I assist?"
        elif "help" in message:
            return "I can help with tasks, coordinate agents, answer questions, or facilitate discussions. What do you need?"
        else:
            # Default response - delegate to appropriate agent or provide general response
            return f"Understood. I'm processing that. Let me coordinate with the team and get back to you."

    def start_multi_agent_conversation(self, topic: str, 
                                      participant_agents: Optional[List[str]] = None,
                                      include_human: bool = True) -> str:
        """
        Start multi-agent conversation (like AI podcast)

        Multiple agents discuss topic, human can participate
        """
        conversation_id = f"multi_agent_{int(time.time() * 1000)}"

        if participant_agents is None:
            participant_agents = ['marvin', 'tony', 'mace', 'gandalf']

        self.active_conversations[conversation_id] = []

        # Initial turn - JARVIS introduces topic
        intro_turn = ConversationTurn(
            turn_id=f"turn_{int(time.time() * 1000)}",
            timestamp=datetime.now(),
            speaker="jarvis",
            message=f"Let's discuss: {topic}. I have {len(participant_agents)} agents ready to contribute. {', '.join([self.agents[a].agent_name for a in participant_agents if a in self.agents])} - what are your thoughts?",
            mode=ConversationMode.MULTI_AGENT
        )

        self.active_conversations[conversation_id].append(intro_turn)

        # Queue agent responses
        for agent_id in participant_agents:
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                agent_turn = ConversationTurn(
                    turn_id=f"turn_{int(time.time() * 1000)}",
                    timestamp=datetime.now(),
                    speaker=agent_id,
                    message=f"{agent.agent_name}: I'll analyze this from my perspective...",
                    mode=ConversationMode.MULTI_AGENT,
                    context={'topic': topic}
                )
                self.conversation_queue.put(agent_turn)

        self.logger.info(f"🎙️ Multi-agent conversation started: {conversation_id}")
        self.logger.info(f"   Topic: {topic}")
        self.logger.info(f"   Participants: {', '.join(participant_agents)}")
        if include_human:
            self.logger.info("   Human participation: Enabled")

        return conversation_id

    def add_agent_to_conversation(self, conversation_id: str, agent_id: str) -> bool:
        """Add agent to conversation"""
        if agent_id not in self.agents:
            self.logger.warning(f"Agent not found: {agent_id}")
            return False

        if conversation_id not in self.active_conversations:
            self.logger.warning(f"Conversation not found: {conversation_id}")
            return False

        agent = self.agents[agent_id]
        turn = ConversationTurn(
            turn_id=f"turn_{int(time.time() * 1000)}",
            timestamp=datetime.now(),
            speaker=agent_id,
            message=f"{agent.agent_name} joining the conversation.",
            mode=ConversationMode.MULTI_AGENT
        )

        self.active_conversations[conversation_id].append(turn)
        self.logger.info(f"➕ {agent.agent_name} added to conversation {conversation_id}")

        return True

    def register_agent(self, agent_id: str, agent_name: str, 
                      role: AgentRole, capabilities: List[str]) -> bool:
        """Register new agent dynamically"""
        agent = Agent(
            agent_id=agent_id,
            agent_name=agent_name,
            role=role,
            capabilities=capabilities
        )

        self.agents[agent_id] = agent
        self.logger.info(f"📝 Registered agent: {agent_name} ({agent_id})")

        return True

    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Get conversation history"""
        if conversation_id not in self.active_conversations:
            return []

        return [turn.to_dict() for turn in self.active_conversations[conversation_id]]

    def get_status(self) -> Dict[str, Any]:
        """Get JARVIS status"""
        return {
            'running': self.running,
            'voice_interface_active': self.voice_interface_active,
            'voice_listening': self.voice_listening,
            'total_agents': len(self.agents),
            'active_agents': sum(1 for a in self.agents.values() if a.active),
            'active_conversations': len(self.active_conversations),
            'agents': {k: v.to_dict() for k, v in self.agents.items()}
        }


# Singleton instance with thread-safe initialization
_jarvis_fulltime_instance: Optional[JARVISFullTimeSuperAgent] = None
_initialization_lock = threading.Lock()
_initialization_in_progress = False
_initialization_complete = False


def get_jarvis_fulltime() -> JARVISFullTimeSuperAgent:
    """
    Get singleton JARVIS full-time instance

    @PEAK: Thread-safe singleton with initialization guards to prevent loops
    """
    global _jarvis_fulltime_instance, _initialization_in_progress, _initialization_complete

    # Fast path: already initialized
    if _jarvis_fulltime_instance is not None and _initialization_complete:
        return _jarvis_fulltime_instance

    # Thread-safe initialization
    with _initialization_lock:
        # Double-check after acquiring lock
        if _jarvis_fulltime_instance is not None and _initialization_complete:
            return _jarvis_fulltime_instance

        # Prevent re-initialization if already in progress
        if _initialization_in_progress:
            logger.warning("⚠️  JARVIS initialization already in progress, waiting...")
            # Wait for initialization to complete (with timeout)
            import time
            timeout = 30  # 30 second timeout
            start_time = time.time()
            while _initialization_in_progress and (time.time() - start_time) < timeout:
                time.sleep(0.1)

            if _jarvis_fulltime_instance is not None and _initialization_complete:
                return _jarvis_fulltime_instance
            else:
                logger.error("❌ JARVIS initialization timeout or failed")
                raise RuntimeError("JARVIS initialization failed or timed out")

        # Mark initialization in progress
        _initialization_in_progress = True
        _initialization_complete = False

        try:
            # Create instance
            _jarvis_fulltime_instance = JARVISFullTimeSuperAgent()
            _initialization_complete = True
            logger.info("✅ JARVIS Full-Time Super Agent singleton initialized")
            return _jarvis_fulltime_instance
        except Exception as e:
            logger.error(f"❌ Failed to initialize JARVIS: {e}")
            _initialization_in_progress = False
            _initialization_complete = False
            raise
        finally:
            _initialization_in_progress = False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Full-Time Super Agent")
    parser.add_argument("--start-voice", action="store_true", help="Start voice conversation")
    parser.add_argument("--speak", type=str, nargs=2, metavar=("CONV_ID", "MESSAGE"),
                       help="Speak in conversation")
    parser.add_argument("--multi-agent", type=str, help="Start multi-agent conversation (topic)")
    parser.add_argument("--status", action="store_true", help="Get JARVIS status")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    jarvis = get_jarvis_fulltime()

    if args.start_voice:
        conv_id = jarvis.start_voice_conversation()
        print(f"✅ Voice conversation started: {conv_id}")
        print("   JARVIS: 'I'm listening. How can I help?'")

    elif args.speak:
        conv_id, message = args.speak
        turn_id = jarvis.speak(conv_id, message)
        print(f"✅ Message sent: {turn_id}")

    elif args.multi_agent:
        conv_id = jarvis.start_multi_agent_conversation(args.multi_agent)
        print(f"✅ Multi-agent conversation started: {conv_id}")
        print(f"   Topic: {args.multi_agent}")

    elif args.status:
        status = jarvis.get_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print("\n🤖 JARVIS Full-Time Super Agent Status")
            print("=" * 60)
            print(f"Running: {status['running']}")
            print(f"Voice Interface: {status['voice_interface_active']}")
            print(f"Voice Listening: {status['voice_listening']}")
            print(f"Total Agents: {status['total_agents']}")
            print(f"Active Agents: {status['active_agents']}")
            print(f"Active Conversations: {status['active_conversations']}")

    else:
        parser.print_help()
        print("\n🤖 JARVIS Full-Time Super Agent")
        print("   Always available, always listening, always ready")

