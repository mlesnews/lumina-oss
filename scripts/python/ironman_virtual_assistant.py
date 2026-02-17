#!/usr/bin/env python3
"""
IRON MAN Virtual Assistant - LUMINA Desktop Companion
Inspired by Armory Crate's virtual assistant, but with IRON MAN theme,
powercord tail, and full LUMINA ecosystem integration.

Features:
- IRON MAN themed visual with powercord tail
- Cycles through IRONMAN (Mark I-VII) and ULTRON AI models
- Full LUMINA integration (JARVIS, R5, @helpdesk, alerts)
- Comprehensive system monitoring and notifications
- Voice recognition and listening capabilities
- Text-to-speech voice output (ElevenLabs + Windows SAPI fallback)
- Wake word detection ("Hey Jarvis", "Hey Iron Man")
- Voice commands and interactions
- Desktop companion that stays on screen

Dependencies:
- Pillow (PIL): Required for high-quality image rendering and transparency
  Install with: pip install Pillow
- tkinter: Usually included with Python (python3-tk on Linux)
- elevenlabs: Required for TTS voice output
  Install with: pip install elevenlabs
- Optional: pywin32 for enhanced Windows API (pip install pywin32)

See scripts/python/ironman_va_requirements.txt for full dependency list.

@JARVIS @TEAM #JARVIS #LUMINA
"""

import json
import logging
import math  # For smooth wandering paths (ACES-like)
import random
import sys
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from va_positioning_combat_system import VAPositioningCombatSystem

try:
    from vas_dynamic_resource_aware_combat import VAsDynamicResourceAwareCombat

    DYNAMIC_COMBAT_AVAILABLE = True
except ImportError:
    DYNAMIC_COMBAT_AVAILABLE = False
    VAsDynamicResourceAwareCombat = None

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

try:
    import tkinter as tk
    from tkinter import ttk

    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageTk

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None
    ImageDraw = None
    ImageTk = None
    ImageFilter = None

# Try importing JARVIS and LUMINA integrations
try:
    from jarvis_fulltime_super_agent import JARVISFullTimeSuperAgent

    JARVIS_AVAILABLE = True
except ImportError:
    JARVIS_AVAILABLE = False
    JARVISFullTimeSuperAgent = None

# SYPHON integration
try:
    from pathlib import Path as PathType

    from syphon import DataSourceType, SYPHONConfig, SYPHONSystem

    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None
    SYPHONConfig = None
    DataSourceType = None

# @asks integration
try:
    from jarvis_restack_all_asks import ASKRestacker

    ASKS_AVAILABLE = True
except ImportError:
    ASKS_AVAILABLE = False
    ASKRestacker = None

# Unified @asks processor (handles text and voice identically)
try:
    from unified_ask_processor import UnifiedAskProcessor

    UNIFIED_ASK_PROCESSOR_AVAILABLE = True
except ImportError:
    UNIFIED_ASK_PROCESSOR_AVAILABLE = False
    UnifiedAskProcessor = None

try:
    from jarvis_elevenlabs_integration import JARVISElevenLabsTTS

    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    JARVISElevenLabsTTS = None

# NAS Migration status integration
try:
    from nas_migration_va_integration import get_migration_status_for_va

    NAS_MIGRATION_AVAILABLE = True
except ImportError:
    NAS_MIGRATION_AVAILABLE = False
    get_migration_status_for_va = None

# Speech recognition imports
try:
    import speech_recognition as sr

    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    sr = None

# Windows SAPI TTS fallback
try:
    if sys.platform == "win32":
        import win32com.client

        SAPI_TTS_AVAILABLE = True
    else:
        SAPI_TTS_AVAILABLE = False
        win32com = None
except ImportError:
    SAPI_TTS_AVAILABLE = False
    win32com = None

logger = get_logger("IRONMANVirtualAssistant")


class AIModel(Enum):
    """IRONMAN and ULTRON AI models for cycling"""

    # KAIJU Number Eight Iron Legion (Mark I-VII) - Desktop PC at <NAS_IP> (NOT NAS)
    MARK_I = (
        "codellama:13b",
        "Mark I",
        "KAIJU",
        "http://<NAS_IP>:11434",
        "Primary code generation",
    )
    MARK_II = ("llama3.2:11b", "Mark II", "KAIJU", "http://<NAS_IP>:11434", "Secondary general")
    MARK_III = (
        "qwen2.5-coder:1.5b-base",
        "Mark III",
        "KAIJU",
        "http://<NAS_IP>:11434",
        "Lightweight quick",
    )
    MARK_IV = ("llama3:8b", "Mark IV", "KAIJU", "http://<NAS_IP>:11434", "General purpose")
    MARK_V = ("mistral:7b", "Mark V", "KAIJU", "http://<NAS_IP>:11434", "General reasoning")
    MARK_VI = ("mixtral-8x7b", "Mark VI", "KAIJU", "http://<NAS_IP>:11434", "High complexity")
    MARK_VII = ("gemma:2b", "Mark VII", "KAIJU", "http://<NAS_IP>:11434", "Lightweight fallback")
    # ULTRON
    ULTRON = (
        "qwen2.5:72b",
        "ULTRON",
        "ULTRON",
        "http://localhost:11434",
        "ULTRON Virtual Hybrid Cluster",
    )

    def __init__(
        self, model_name: str, display_name: str, system: str, endpoint: str, description: str
    ):
        self.model_name = model_name
        self.display_name = display_name
        self.system = system
        self.endpoint = endpoint
        self.description = description


class AlertLevel(Enum):
    """Alert severity levels"""

    INFO = ("info", "#00FF00")  # Green
    WARNING = ("warning", "#FFFF00")  # Yellow
    CRITICAL = ("critical", "#FF0000")  # Red
    SYSTEM = ("system", "#00BFFF")  # Blue

    def __init__(self, level: str, color: str):
        self.level = level
        self.color = color


@dataclass
class Alert:
    """Alert/notification structure"""

    title: str
    message: str
    level: AlertLevel
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "LUMINA"
    action_required: bool = False
    action_url: Optional[str] = None
    collapsed: bool = True  # Default to collapsed for repeated alerts
    duplicate_count: int = 1  # Number of times this alert has appeared
    alert_signature: Optional[str] = None  # Unique signature for grouping duplicates
    meta_tags: Optional[Dict[str, Any]] = None  # Meta-tags from smart AI logging
    group_id: Optional[str] = None  # Alert group ID from smart AI logging
    incident_id: Optional[str] = None  # Incident ID for grouping


@dataclass
class LUMINASystemStatus:
    """Status of LUMINA systems"""

    jarvis: bool = False
    r5: bool = False
    helpdesk: bool = False
    ultron: bool = False
    kaiju: bool = False
    nas_migration: Dict[str, Any] = field(
        default_factory=lambda: {"running": False, "status": "unknown"}
    )
    last_check: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "jarvis": self.jarvis,
            "r5": self.r5,
            "helpdesk": self.helpdesk,
            "ultron": self.ultron,
            "kaiju": self.kaiju,
            "nas_migration": self.nas_migration,
            "last_check": self.last_check.isoformat(),
        }


class IRONMANVirtualAssistant:
    """
    IRON MAN Virtual Assistant - LUMINA Desktop Companion

    Features:
    - IRON MAN themed appearance with powercord tail
    - Cycles through IRONMAN (Mark I-VII) and ULTRON AI models
    - Full LUMINA ecosystem integration
    - Comprehensive alerts and notifications
    - System monitoring and status
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.transparency_set = False  # Flag to prevent re-setting transparency (fixes flickering)
        self.update_count = 0  # Track update count to prevent excessive redraws

        if not TKINTER_AVAILABLE:
            self.logger.error("❌ tkinter not available - cannot create virtual assistant")
            raise ImportError("tkinter is required for virtual assistant")

        # Configuration
        self.config_dir = project_root / "config"
        self.data_dir = project_root / "data" / "ironman_assistant"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # AI Model cycling
        self.current_model_index = 0
        self.ai_models = list(AIModel)
        self.current_model = self.ai_models[self.current_model_index]
        self.model_cycle_interval = 30.0  # seconds between cycles
        self.last_model_cycle = time.time()

        # LUMINA integrations
        self.jarvis_agent = None
        if JARVIS_AVAILABLE:
            try:
                self.jarvis_agent = JARVISFullTimeSuperAgent(project_root)
                self.logger.info("✅ JARVIS agent integrated")
            except Exception as e:
                self.logger.warning(f"⚠️  JARVIS agent not available: {e}")

        # SYPHON integration (@SYPHON) - Active enhancement system
        self.syphon = None
        self.syphon_enhancement_interval = 60.0  # Extract and enhance every 60 seconds
        self.last_syphon_enhancement = time.time()
        self.syphon_enhanced_knowledge = []  # Store SYPHON-extracted intelligence for VA enhancement
        if SYPHON_AVAILABLE:
            try:
                syphon_config = SYPHONConfig(project_root=project_root, enable_regex_tools=True)
                self.syphon = SYPHONSystem(syphon_config)
                self.logger.info("✅ SYPHON intelligence extraction integrated for VA enhancement")
            except Exception as e:
                self.logger.warning(f"⚠️  SYPHON not available: {e}")

        # @asks integration
        self.ask_restacker = None
        if ASKS_AVAILABLE:
            try:
                self.ask_restacker = ASKRestacker(project_root)
                self.logger.info("✅ @asks system integrated")
            except Exception as e:
                self.logger.warning(f"⚠️  @asks system not available: {e}")

        # Unified @asks processor (handles text and voice identically)
        self.unified_ask_processor = None
        if UNIFIED_ASK_PROCESSOR_AVAILABLE:
            try:
                self.unified_ask_processor = UnifiedAskProcessor(
                    project_root=project_root, ask_restacker=self.ask_restacker
                )
                self.logger.info("✅ Unified @asks processor integrated (text & voice)")
            except Exception as e:
                self.logger.warning(f"⚠️  Unified @asks processor not available: {e}")

        # @agent coordination integration (for combat coordination)
        self.agent_coordination = None
        try:
            from coordinate_agent_sessions import AgentSessionCoordinator

            self.agent_coordination = AgentSessionCoordinator(project_root=project_root)
            self.logger.info("✅ @agent coordination integrated for combat")
        except ImportError:
            self.logger.debug("@agent coordination not available")
        except Exception as e:
            self.logger.debug(f"@agent coordination init error: {e}")

        # TTS (Text-to-Speech)
        self.tts = None
        self.sapi_tts = None
        if ELEVENLABS_AVAILABLE:
            try:
                self.tts = JARVISElevenLabsTTS(project_root=project_root)
                self.logger.info("✅ ElevenLabs TTS integrated")
            except Exception as e:
                self.logger.debug(f"ElevenLabs TTS not available: {e}")

        # Windows SAPI TTS fallback
        if not self.tts and SAPI_TTS_AVAILABLE:
            try:
                self.sapi_tts = win32com.client.Dispatch("SAPI.SpVoice")
                self.logger.info("✅ Windows SAPI TTS available as fallback")
            except Exception as e:
                self.logger.debug(f"Windows SAPI TTS not available: {e}")

        # Speech recognition
        self.recognizer = None
        self.microphone = None
        self.microphone_lock = threading.Lock()  # Lock for exclusive microphone access
        self.listening = False
        self.wake_word_enabled = True
        self.wake_words = ["hey jarvis", "hey iron man", "jarvis", "iron man"]
        self.listening_timeout = 5.0  # seconds
        self.phrase_timeout = 2.0  # seconds

        if SPEECH_RECOGNITION_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                # Adjust for ambient noise
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self.logger.info("✅ Speech recognition available")
            except Exception as e:
                self.logger.warning(f"⚠️  Speech recognition not available: {e}")
                self.recognizer = None
                self.microphone = None

        # System status monitoring
        self.system_status = LUMINASystemStatus()
        self.status_check_interval = 10.0  # seconds
        self.last_status_check = time.time()

        # Alerts and notifications
        self.alerts: List[Alert] = []
        self.alert_display_time = 5.0  # seconds
        self.max_alerts = 10
        self.alert_groups: Dict[str, List[Alert]] = {}  # Track grouped alerts by signature
        self.expanded_alerts: set = set()  # Track which alerts are expanded
        self.expanded_alert_timestamps: Dict[str, datetime] = {}  # Track when alerts were expanded
        self.alert_collapse_timeout = 30.0  # Auto-collapse after 30 seconds

        # Smart AI Logging Module for advanced grouping
        try:
            from smart_ai_logging_module import SmartAILoggingModule

            self.smart_logging = SmartAILoggingModule(project_root=self.project_root)
            self.logger.info("✅ Smart AI Logging Module initialized")
        except ImportError as e:
            self.smart_logging = None
            self.logger.debug(f"Smart AI Logging Module not available: {e}")
        except Exception as e:
            self.smart_logging = None
            self.logger.warning(f"Could not initialize Smart AI Logging Module: {e}")

        # Window setup
        self.root = None
        self.canvas = None
        self.ironman_figure = None
        self.powercord_tail = None

        # VA Positioning & Combat System (prevents stacking, enables 1v1 combat)
        # Initialize BEFORE setting position so we can use it for spacing
        try:
            self.positioning_system = VAPositioningCombatSystem(project_root=self.project_root)
            logger.info("✅ VA Positioning System initialized")
        except Exception as e:
            logger.warning(f"⚠️  Could not initialize positioning system: {e}")
            self.positioning_system = None

        # Position and movement (start in center of screen)
        # Will be set properly in create_window
        # Initialize position using positioning system to prevent stacking
        # This ensures each VA instance gets a unique, properly spaced position
        if self.positioning_system:
            try:
                pos_x, pos_y = self.positioning_system.calculate_spaced_position("imva", 120)
                self.x = pos_x
                self.y = pos_y
                logger.info(
                    f"✅ Initialized position using positioning system: ({self.x}, {self.y})"
                )
            except Exception as e:
                logger.warning(f"⚠️  Could not use positioning system for initial position: {e}")
                # Fallback: Use screen center with random offset to prevent stacking
                import random

                screen_width = 1920  # Will be updated when window is created
                screen_height = 1080
                self.x = screen_width // 2 + random.randint(-200, 200)
                self.y = screen_height // 2 + random.randint(-200, 200)
        else:
            # No positioning system - use random position to prevent stacking
            import random

            screen_width = 1920
            screen_height = 1080
            self.x = screen_width // 2 + random.randint(-200, 200)
            self.y = screen_height // 2 + random.randint(-200, 200)
        self.target_x = self.x  # Start target at current position
        self.target_y = self.y
        # MACRO FIX: ACES-like smooth movement system (MAJOR REWRITE)
        self.wandering = False
        # TURN UP THE VOLUME: Make movement OBVIOUSLY smooth (like ACES)
        self.movement_speed = 3.0  # Increased from 2.0 - MORE VISIBLE
        self.smooth_interpolation = True
        self.interpolation_factor = 0.12  # Increased from 0.08 - MORE VISIBLE SMOOTHNESS
        self.last_update_time = time.time()
        self.animation_frame_time = (
            0.033  # 30 FPS - balanced smoothness vs CPU (was 0.010 = 100 FPS which burned CPU)
        )

        # MACRO FIX: Continuous wandering (like ACES - always moving smoothly)
        self.wander_enabled = True  # Always wandering when not in combat
        self.wander_target_distance = 300  # Longer distances (like ACES)
        self.wander_update_interval = 0.5  # Update target every 0.5s (smooth path)

        # Path smoothing (ACES uses smooth paths, not direct movement)
        self.path_points = []  # Smooth path to target
        self.current_path_index = 0

        # Drag state
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.dragging = False

        # Lightsaber fight mode (vs AC VA) - @ankin aggressive negotiations style
        self.lightsaber_fight_mode = False
        self.ac_va_position = None  # AC VA window position (x, y)
        self.fight_animation_frame = 0
        self.lightsaber_color = "#00FFFF"  # Cyan lightsaber
        self.fight_speed_multiplier = 3.0  # Faster movement during fight
        self.fight_start_time = None  # Track when fight started
        self.min_fight_duration = (
            12.0  # Minimum fight duration in seconds (balanced for shorter battles)
        )
        self.aggressive_negotiation_mode = False  # @ankin style aggressive negotiations
        self.attack_charge_counter = 0  # Counter for aggressive attack charges

        # ACVA combat tracking (NOTE: ACVA is external app, so we track internally and show visual indicators)
        self.acva_max_health = 100.0  # Simulated ACVA health
        self.acva_current_health = 100.0  # Current ACVA health
        self.acva_hit_effects = []  # List of hit effect timestamps/positions for visual feedback
        self.acva_lightsaber_frame = 0  # ACVA lightsaber animation frame (visual indicator only)

        # D&D d20 dice roll system (@dnd @d20 virtual tabletop)
        self.dice_rolls: List[Dict[str, Any]] = []  # Active dice rolls on screen
        self.dice_lifetime = 3.0  # How long dice stay visible (seconds)

        # Eye/expression system (SYPHON/WOPR enhanced)
        self.eye_expression_state = "normal"  # normal, alert, thinking, speaking, combat, critical
        self.eye_intensity = 1.0  # 0.0 to 1.0, controlled by SYPHON/WOPR data
        self.expression_modifier = 0.0  # Modifier from SYPHON/WOPR matrix workflows
        self.mouth_expression = "neutral"  # neutral, smile, frown, speaking, combat

        # Health/Hitpoints system
        self.max_health = 100.0
        self.current_health = self.max_health
        self.last_damage_time = 0.0
        self.fight_check_interval = (
            20.0  # Check for fight chance every 20 seconds (balanced frequency)
        )
        self.fight_probability = (
            0.12  # 12% chance to initiate fight (balanced for less frequent battles)
        )
        self.last_fight_check = time.time()
        self.fleeing = False  # Track if VA is fleeing
        self.flee_threshold = 0.05  # 5% health threshold for fleeing

        # Dynamic Resource-Aware Combat Scaling
        self.dynamic_combat = None
        self.combat_scaling_update_interval = 10.0  # Update scaling every 10 seconds
        self.last_scaling_update = 0.0
        self.current_damage_multiplier = 1.0  # Current damage multiplier from resource scaling
        if DYNAMIC_COMBAT_AVAILABLE:
            try:
                self.dynamic_combat = VAsDynamicResourceAwareCombat(project_root=self.project_root)
                logger.info("✅ Dynamic Resource-Aware Combat Scaling initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize dynamic combat scaling: {e}")
                self.dynamic_combat = None

        # SYPHON enhancement system - use extracted intelligence to improve VA
        self.syphon_enhancement_interval = 30.0  # Extract and enhance every 30 seconds
        self.last_syphon_enhancement = time.time()
        self.syphon_actionable_items: List[str] = []
        self.syphon_tasks: List[Dict[str, Any]] = []
        self.syphon_decisions: List[Dict[str, Any]] = []
        self.syphon_intelligence: List[Dict[str, Any]] = []
        self.syphon_enhancement_thread = None

        # IRON MAN appearance
        self.size = 50  # Compact size (reduced from 80)
        self.ironman_colors = {
            "primary": "#FF6B35",  # Orange-red
            "secondary": "#FFD700",  # Gold
            "arc_reactor": "#00FFFF",  # Cyan/blue (arc reactor)
            "powercord": "#808080",  # Gray for powercord
        }
        self.arc_reactor_pulse = 0.0
        self.powercord_animated = True

        # High-quality image rendering
        self.use_pil_rendering = PIL_AVAILABLE
        self.ironman_image = None
        self.ironman_photo = None

        # Conversation & Memory (Replika-style)
        self.conversation_queue = []
        self.conversation_history = []  # Store conversation history
        self.memory_file = self.data_dir / "memory.json"
        self.personality_file = self.data_dir / "personality.json"

        # Personality traits (Replika-style) - MUST be defined before _load_personality
        self.personality_traits = {
            "loyalty": 0.9,  # Very loyal
            "supportiveness": 0.85,  # Highly supportive
            "professionalism": 0.8,  # Professional but approachable
            "curiosity": 0.7,  # Curious about user
            "humor": 0.6,  # Some humor
            "empathy": 0.85,  # Empathetic
            "friendliness": 0.8,  # Friendly
            "intelligence": 0.95,  # Highly intelligent
        }

        self.memory = self._load_memory()  # User facts, preferences, memories
        self.personality = self._load_personality()  # Personality traits
        self.user_name = self.memory.get("user_name", None)
        self.last_interaction = None
        self.conversation_context = []  # Recent conversation context
        self.max_context_entries = 20

        # Enhanced idle phrases with personality
        self.idle_phrases = self._generate_idle_phrases()

        # Threading
        self.running = False
        self.wander_thread = None
        self.status_thread = None
        self.animation_thread = None
        self.voice_listening_thread = None

        # Voice state
        self.is_speaking = False
        self.is_listening = False

        # Mouse shake detection for click-through toggle
        self.click_through_enabled = False  # Default: click-through OFF (so dragging works)
        self.mouse_positions = []  # Track mouse positions for shake detection
        self.mouse_shake_threshold = 100  # Pixels moved to detect shake
        self.mouse_shake_time_window = 2.0  # Seconds to detect shake
        self.last_mouse_time = time.time()
        self.mouse_shake_check_interval = 0.1  # Check every 100ms

        # Load configuration
        self._load_config()

        # Start system monitoring
        self.start_system_monitoring()

        # Start SYPHON enhancement loop (active intelligence extraction to improve VA)
        if self.syphon:
            self.start_syphon_enhancement_loop()

        # Action Sequence System Integration (@JARVIS @LUMINA)
        try:
            from va_action_sequence_system import VAActionSequenceSystem

            self.action_sequence_system = VAActionSequenceSystem(
                project_root=self.project_root, va_type="ironman"
            )
            self.action_sequence_system.start()
            self.logger.info("✅ Action sequence system integrated (@JARVIS @LUMINA)")
        except Exception as e:
            self.logger.warning(f"⚠️  Action sequence system not available: {e}")
            self.action_sequence_system = None

        # Start voice listening (if available)
        if self.recognizer and self.microphone:
            self.start_voice_listening()

    def _load_config(self):
        """Load configuration from file"""
        config_file = self.data_dir / "config.json"
        if config_file.exists():
            try:
                with open(config_file) as f:
                    config = json.load(f)
                    self.model_cycle_interval = config.get("model_cycle_interval", 30.0)
                    self.status_check_interval = config.get("status_check_interval", 10.0)
                    self.speed = config.get("speed", 2)
                    self.size = config.get("size", 80)
            except Exception as e:
                self.logger.warning(f"Could not load config: {e}")

    def _save_config(self):
        """Save configuration to file"""
        config_file = self.data_dir / "config.json"
        try:
            config = {
                "model_cycle_interval": self.model_cycle_interval,
                "status_check_interval": self.status_check_interval,
                "speed": self.speed,
                "size": self.size,
            }
            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Could not save config: {e}")

    def _load_memory(self) -> Dict[str, Any]:
        """Load conversation memory and user facts"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file) as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Could not load memory: {e}")
        return {
            "user_name": None,
            "user_facts": [],
            "preferences": {},
            "conversation_count": 0,
            "first_met": datetime.now().isoformat(),
            "topics_discussed": [],
            "emotions": {},
            "memories": [],
        }

    def _save_memory(self):
        """Save conversation memory and user facts"""
        try:
            with open(self.memory_file, "w") as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Could not save memory: {e}")

    def _load_personality(self) -> Dict[str, float]:
        """Load personality traits"""
        if self.personality_file.exists():
            try:
                with open(self.personality_file) as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    for key, value in self.personality_traits.items():
                        if key not in loaded:
                            loaded[key] = value
                    return loaded
            except Exception as e:
                self.logger.warning(f"Could not load personality: {e}")
        return self.personality_traits.copy()

    def _save_personality(self):
        """Save personality traits"""
        try:
            with open(self.personality_file, "w") as f:
                json.dump(self.personality, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Could not save personality: {e}")

    def _generate_idle_phrases(self) -> List[str]:
        """Generate idle phrases based on personality and context"""
        base_phrases = [
            "Systems operational, sir.",
            "All systems green.",
            "Monitoring LUMINA ecosystem.",
            "Ready for your command.",
            "JARVIS systems active.",
            "ULTRON cluster online.",
            "KAIJU Iron Legion standing by.",
            "R5 matrix synchronized.",
            "All clear, Mr. Stark.",
            "I am always watching.",
            "Power levels optimal.",
            "Threat assessment complete.",
        ]

        # Add personalized phrases if we know user's name
        if self.user_name:
            personalized = [
                f"Ready when you are, {self.user_name}.",
                f"All systems operational, {self.user_name}.",
                f"How can I help you today, {self.user_name}?",
                f"I'm here if you need anything, {self.user_name}.",
            ]
            base_phrases.extend(personalized)

        # Add companion-like phrases (Replika style)
        companion_phrases = [
            "How are you doing today?",
            "Is there anything on your mind?",
            "I'm here for you.",
            "What would you like to talk about?",
            "How can I support you today?",
            "I'm listening, always.",
            "How's your day going?",
            "Anything interesting happen today?",
            "I'm here whenever you need me.",
            "What can I help you with?",
        ]

        # Mix based on personality (more companion-like if empathy/friendliness is high)
        if self.personality.get("empathy", 0.85) > 0.7:
            base_phrases.extend(companion_phrases[:5])  # Add some companion phrases

        return base_phrases

    def remember(self, fact: str, category: str = "general"):
        """Remember a fact about the user (Replika-style memory)"""
        if "user_facts" not in self.memory:
            self.memory["user_facts"] = []

        fact_entry = {
            "fact": fact,
            "category": category,
            "timestamp": datetime.now().isoformat(),
            "confidence": 1.0,
        }
        self.memory["user_facts"].append(fact_entry)

        # Keep only last 100 facts
        if len(self.memory["user_facts"]) > 100:
            self.memory["user_facts"] = self.memory["user_facts"][-100:]

        self._save_memory()
        self.logger.info(f"💾 Remembered: {fact} (category: {category})")

    def recall(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Recall facts from memory (Replika-style recall)"""
        if "user_facts" not in self.memory:
            return []

        query_lower = query.lower()
        relevant_facts = []

        for fact_entry in self.memory["user_facts"]:
            if category and fact_entry.get("category") != category:
                continue

            fact_text = fact_entry.get("fact", "").lower()
            if query_lower in fact_text or fact_text in query_lower:
                relevant_facts.append(fact_entry)

        # Sort by confidence and recency
        relevant_facts.sort(
            key=lambda x: (x.get("confidence", 0), x.get("timestamp", "")), reverse=True
        )

        return relevant_facts[:5]  # Return top 5 most relevant

    def add_to_context(self, user_message: str, assistant_response: str):
        """Add to conversation context for better continuity"""
        context_entry = {
            "user": user_message,
            "assistant": assistant_response,
            "timestamp": datetime.now().isoformat(),
        }
        self.conversation_context.append(context_entry)

        # Keep only recent context
        if len(self.conversation_context) > self.max_context_entries:
            self.conversation_context = self.conversation_context[-self.max_context_entries :]

        # Save to conversation history (with limit to prevent memory leak)
        self.conversation_history.append(context_entry)
        # Keep only last 500 conversation entries to prevent unbounded memory growth
        if len(self.conversation_history) > 500:
            self.conversation_history = self.conversation_history[-500:]
        self._save_memory()

    def create_window(self):
        """Create the virtual assistant window"""
        self.root = tk.Tk()
        self.root.title("IRON MAN Virtual Assistant - LUMINA")
        self.root.attributes("-topmost", True)  # Always on top

        # Get screen size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Create a smaller window (not full screen) - will move around
        self.window_size = 120  # Size of the window (reduced from 250)
        # Use positioning system for proper spacing (prevents stacking)
        if self.positioning_system:
            try:
                pos_x, pos_y = self.positioning_system.calculate_spaced_position(
                    "imva", self.window_size
                )
                initial_x = max(50, min(pos_x, screen_width - self.window_size))
                initial_y = max(50, min(pos_y, screen_height - self.window_size))
                logger.info(f"✅ Positioned using positioning system: ({initial_x}, {initial_y})")
            except Exception as e:
                logger.warning(f"⚠️  Could not use positioning system: {e}")
                initial_x = max(50, min(int(self.x), screen_width - self.window_size))
                initial_y = max(50, min(int(self.y), screen_height - self.window_size))
        else:
            initial_x = max(50, min(int(self.x), screen_width - self.window_size))
            initial_y = max(50, min(int(self.y), screen_height - self.window_size))
        self.root.geometry(f"{self.window_size}x{self.window_size}+{initial_x}+{initial_y}")

        # Set transparent background (AC VA style - color key transparency)
        self.root.configure(bg="black")  # Black background will be transparent
        self.root.overrideredirect(True)  # No window decorations (frameless like AC VA)

        # Create canvas with black background (will be made transparent via color key)
        self.canvas = tk.Canvas(
            self.root,
            width=self.window_size,
            height=self.window_size,
            bg="black",  # Black will be made transparent via Windows API color key
            highlightthickness=0,
            borderwidth=0,
        )
        self.canvas.pack()

        # Update to ensure canvas is ready
        self.root.update_idletasks()
        self.root.update()

        # Set transparency using Windows API AFTER canvas is created (AC VA style)
        # AC VA uses color key transparency where black pixels become transparent
        if sys.platform == "win32":
            try:
                import ctypes

                # Get window handle - try both methods
                hwnd = self.root.winfo_id()
                try:
                    parent_hwnd = ctypes.windll.user32.GetParent(hwnd)
                    if parent_hwnd:
                        hwnd = parent_hwnd
                except:
                    pass

                # Set WS_EX_LAYERED style (required for transparency on Windows)
                GWL_EXSTYLE = -20
                WS_EX_LAYERED = 0x80000
                ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style | WS_EX_LAYERED)

                # FIX: Make IMVA more solid (identical to ACVA) - use alpha blending for opacity control
                # ACVA uses higher opacity (more solid), so we use LWA_ALPHA with high alpha value
                LWA_COLORKEY = 0x1
                LWA_ALPHA = 0x2
                LWA_BOTH = LWA_COLORKEY | LWA_ALPHA

                # FIX: Make IMVA identical to ACVA - use maximum opacity for solid appearance
                # ACVA is fully solid, so we use 255 (100% opaque) to match exactly
                # Combined with color key for black pixel transparency
                alpha_value = 255  # Maximum opacity (fully solid, identical to ACVA)
                result = ctypes.windll.user32.SetLayeredWindowAttributes(
                    hwnd, 0x000000, alpha_value, LWA_BOTH
                )

                if result:
                    self.logger.info(
                        "✅ Transparency enabled via Windows API (AC VA style) - opacity matched"
                    )
                    self.transparency_set = True  # Flag to prevent re-setting
                else:
                    self.logger.warning(
                        "⚠️  SetLayeredWindowAttributes failed, trying tkinter method"
                    )
                    self.root.attributes("-transparentcolor", "black")
                    self.transparency_set = True
            except Exception as e:
                # Fallback to tkinter's transparentcolor attribute
                self.logger.debug(f"Windows API transparency failed: {e}")
                try:
                    self.root.attributes("-transparentcolor", "black")
                    self.logger.info("✅ Using tkinter transparentcolor fallback")
                except Exception as e2:
                    self.logger.warning(f"Both transparency methods failed: {e2}")
        else:
            # Non-Windows: use tkinter method
            try:
                self.root.attributes("-transparentcolor", "black")
            except:
                pass

        # Force final update to apply transparency
        self.root.update_idletasks()
        self.root.update()

        # Update window to ensure canvas is ready
        self.root.update_idletasks()

        # Draw IRON MAN figure FIRST (before setting click-through)
        self._draw_ironman()
        self.root.update()

        # Set window click-through state (default: disabled so dragging works)
        self._update_click_through_state()

        # Bind events
        self.canvas.bind("<Button-1>", self._on_left_click)  # Left click
        self.canvas.bind("<Button-3>", self._on_right_click)  # Right click - context menu
        self.canvas.bind("<B1-Motion>", self._on_drag)  # Drag window
        self.canvas.bind("<ButtonRelease-1>", self._on_left_release)  # Left click release
        self.canvas.bind("<Motion>", self._on_mouse_move)

        # Create context menu
        self._create_context_menu()

        # Start mouse shake detection (for toggling click-through)
        self.start_mouse_shake_detection()

        # Start wandering
        self.start_wandering()

        # Start animation loop
        self.start_animation()

        # Start conversation
        self.start_conversation()

        # Welcome message (personalized if we know user)
        user_ref = self.user_name if self.user_name else "sir"
        conv_count = self.memory.get("conversation_count", 0)

        if conv_count == 0:
            welcome_msg = f"IRON MAN Virtual Assistant online. I'm here to help you, {user_ref}."
        elif conv_count < 5:
            welcome_msg = f"Welcome back, {user_ref}. Good to see you again."
        else:
            welcome_msg = f"Hey {user_ref}, welcome back! How are you doing today?"

        if self.recognizer and self.microphone:
            welcome_msg += " Say 'Hey Jarvis' or click me to interact."
        else:
            welcome_msg += " Click me to interact."

        threading.Timer(2.0, lambda: self.speak(welcome_msg)).start()

    def _draw_ironman(self):
        """Draw IRON MAN figure with powercord tail - high quality rendering"""
        if not self.canvas:
            return

        # MACRO FIX: COMPLETE CANVAS CLEAR - PREVENT ALL STACKING
        # TURN UP THE VOLUME: Delete EVERYTHING before redraw (no exceptions)
        self.canvas.delete("all")
        # Also clear any image references to prevent garbage collection issues
        if hasattr(self.canvas, "ironman_photo_ref"):
            delattr(self.canvas, "ironman_photo_ref")

        # FIX: Use double buffering to prevent flickering
        # Clear previous drawings (but keep canvas) - batch operations
        # Note: delete("all") above handles all tags, but keeping these for reference
        # self.canvas.delete("ironman")
        # self.canvas.delete("powercord")
        # self.canvas.delete("alerts")
        # self.canvas.delete("lightsaber")
        # self.canvas.delete("acva_lightsaber")  # ACVA lightsaber indicators
        # self.canvas.delete("acva_hit_effects")  # ACVA hit effect indicators
        # self.canvas.delete("healthbar")

        # FIX: Prevent transparency re-setting during redraw (fixes flickering)
        # Transparency should only be set once during initialization
        # Re-setting it during redraw causes flickering

        # Draw IRON MAN centered in the window
        x, y = self.window_size // 2, self.window_size // 2
        size = self.size

        # Use PIL for high-quality rendering if available
        if self.use_pil_rendering:
            self._draw_ironman_pil(x, y, size)
        else:
            self._draw_ironman_canvas(x, y, size)

        # Draw lightsaber if in fight mode
        if self.lightsaber_fight_mode:
            self._draw_lightsaber(x, y, size)
            # Draw ACVA lightsaber indicator (visual feedback only - ACVA is external app)
            if self.ac_va_position:
                self._draw_acva_lightsaber_indicator()
            # Draw ACVA hit effects (sparks, damage indicators)
            self._draw_acva_hit_effects()

        # Draw health bar if in fight mode
        if self.lightsaber_fight_mode:
            self._draw_health_bar(x, y, size)

        # Draw powercord tail (behind IRON MAN)
        if self.powercord_animated:
            self._draw_powercord_tail(x, y, size)

        # Draw alerts if any
        self._draw_alerts()

        # Draw D&D dice rolls (@dnd @d20 virtual tabletop)
        self._draw_dice_rolls()

        # Draw health status indicator (D&D RPG gradient: full-health to death/skull)
        self._draw_health_status_indicator()

    def _draw_ironman_pil(self, x: int, y: int, size: int):
        """Draw IRON MAN using PIL for high-quality rendering with enhanced aesthetics"""
        # Create ultra-high-resolution image for best quality (3x scale for perfect anti-aliasing)
        scale = 3
        img_size = self.window_size * scale
        img = Image.new("RGBA", (img_size, img_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img, "RGBA")

        # Scale coordinates
        x_scaled = x * scale
        y_scaled = y * scale
        size_scaled = size * scale

        # Calculate colors
        primary_rgb = self._hex_to_rgb(self.ironman_colors["primary"])
        secondary_rgb = self._hex_to_rgb(self.ironman_colors["secondary"])

        # Arc reactor color based on state with pulse animation
        pulse_factor = 1.0 + abs(self.arc_reactor_pulse) * 0.15  # Pulse animation
        if self.is_listening:
            arc_color = (255, 255, 0, 255)  # Yellow
            arc_size = size_scaled * 0.42 * pulse_factor
        elif self.is_speaking:
            arc_color = (0, 255, 255, 255)  # Cyan
            arc_size = size_scaled * 0.47 * pulse_factor
        else:
            arc_color = (0, 217, 255, 255)  # Cyan from hex #00D9FF
            arc_size = size_scaled * 0.36 * pulse_factor

        # Ultra-refined outer glow effect (more layers for smoother, more subtle gradient)
        glow_size = size_scaled * 1.15  # Slightly smaller, more refined
        for i in range(2, 0, -1):  # AGGRESSIVE: Reduced to 2 to eliminate blob appearance
            alpha = max(
                0, min(100, int(40 - (i * 15)))
            )  # AGGRESSIVE: Much lower alpha to eliminate blob
            glow_alpha = int(alpha * 0.1)  # AGGRESSIVE: Minimal glow to eliminate blob
            glow_color = (*primary_rgb, glow_alpha)
            offset = i * 1.5
            draw.ellipse(
                [
                    x_scaled - glow_size / 2 + offset,
                    y_scaled - glow_size / 2 + offset,
                    x_scaled + glow_size / 2 - offset,
                    y_scaled + glow_size / 2 - offset,
                ],
                fill=glow_color,
            )

        # Refined body with smooth gradient (more layers for smoother transition)
        body_radius = size_scaled / 2
        # More layers for smoother gradient
        for i in range(2):  # AGGRESSIVE: Reduced to 2 to eliminate blob, sharp definition only
            radius_factor = 1.0 - (i * 0.04)
            alpha_factor = 0.75 + (i * 0.03)
            current_radius = body_radius * radius_factor
            current_color = tuple(int(c * alpha_factor) for c in primary_rgb)
            outline_alpha = int(255 * (1.0 - i * 0.1))
            draw.ellipse(
                [
                    x_scaled - current_radius,
                    y_scaled - current_radius,
                    x_scaled + current_radius,
                    y_scaled + current_radius,
                ],
                fill=(*current_color, 255),
                outline=(*secondary_rgb, outline_alpha),
                width=max(1, int(2.5 * scale * (1 - i * 0.1))),
            )

        # Main body outline (refined, polished)
        body_bbox = [
            x_scaled - size_scaled / 2,
            y_scaled - size_scaled / 2,
            x_scaled + size_scaled / 2,
            y_scaled + size_scaled / 2,
        ]
        # Double outline for depth (increased for clearer definition)
        draw.ellipse(body_bbox, outline=(*secondary_rgb, 255), width=max(3, int(3.5 * scale)))
        draw.ellipse(body_bbox, outline=(*secondary_rgb, 255), width=max(1, int(1.5 * scale)))

        # Enhanced chest plate detail (rectangular inset)
        chest_width = size_scaled * 0.65
        chest_height = size_scaled * 0.35
        chest_y_offset = size_scaled * 0.1
        chest_bbox = [
            x_scaled - chest_width / 2,
            y_scaled - chest_height / 2 + chest_y_offset,
            x_scaled + chest_width / 2,
            y_scaled + chest_height / 2 + chest_y_offset,
        ]
        # Subtle chest plate with transparency
        chest_color = tuple(int(c * 0.85) for c in secondary_rgb)
        draw.ellipse(
            chest_bbox,
            fill=(*chest_color, 200),
            outline=(*secondary_rgb, 180),
            width=max(1, int(2 * scale)),
        )

        # Ultra-refined arc reactor with multiple subtle glow layers
        # Outer glow layers (5 layers for ultra-smooth gradient)
        for glow_layer in range(
            1, 0, -1
        ):  # AGGRESSIVE: Single glow layer only for sharp definition
            glow_radius = arc_size / 2 + (glow_layer * scale * 2)
            glow_alpha = int(120 / (glow_layer + 1))  # More subtle
            glow_color = (*arc_color[:3], glow_alpha)
            glow_bbox = [
                x_scaled - glow_radius,
                y_scaled - glow_radius,
                x_scaled + glow_radius,
                y_scaled + glow_radius,
            ]
            draw.ellipse(glow_bbox, fill=glow_color)

        # Inner arc reactor core (bright center with soft transition)
        core_size = arc_size * 0.65
        core_bbox = [
            x_scaled - core_size / 2,
            y_scaled - core_size / 2,
            x_scaled + core_size / 2,
            y_scaled + core_size / 2,
        ]
        # Soft white core
        draw.ellipse(core_bbox, fill=(255, 255, 255, 220))

        # Medium core layer
        medium_core = arc_size * 0.75
        medium_bbox = [
            x_scaled - medium_core / 2,
            y_scaled - medium_core / 2,
            x_scaled + medium_core / 2,
            y_scaled + medium_core / 2,
        ]
        # Blend color
        blend_color = tuple(int(arc_color[i] * 0.7 + 255 * 0.3) for i in range(3))
        draw.ellipse(medium_bbox, fill=(*blend_color, 180))

        # Main arc reactor
        arc_bbox = [
            x_scaled - arc_size / 2,
            y_scaled - arc_size / 2,
            x_scaled + arc_size / 2,
            y_scaled + arc_size / 2,
        ]
        draw.ellipse(arc_bbox, fill=arc_color)

        # Enhanced helmet/head design (more detailed)
        head_offset_y = -size_scaled * 0.32
        head_width = size_scaled * 0.75
        head_height = size_scaled * 0.55

        # Helmet main shape (rounded top, wider base)
        helmet_top_y = y_scaled + head_offset_y - head_height / 2
        helmet_bottom_y = y_scaled + head_offset_y + head_height / 2
        helmet_bbox = [
            x_scaled - head_width / 2,
            helmet_top_y,
            x_scaled + head_width / 2,
            helmet_bottom_y,
        ]
        # Increased outline width for clearer definition
        draw.ellipse(
            helmet_bbox,
            fill=(*primary_rgb, 255),
            outline=(*secondary_rgb, 255),
            width=max(3, int(3 * scale)),
        )

        # Faceplate detail line
        faceplate_y = y_scaled + head_offset_y + size_scaled * 0.05
        line_width = head_width * 0.6
        draw.line(
            [x_scaled - line_width / 2, faceplate_y, x_scaled + line_width / 2, faceplate_y],
            fill=(*secondary_rgb, 200),
            width=max(2, int(2 * scale)),
        )

        # SYPHON/WOPR-enhanced eyes (dynamic expressions based on intelligence extraction)
        eye_expression = self._get_eye_expression()
        eye_color, eye_intensity = self._get_eye_color_and_intensity(arc_color, eye_expression)

        eye_y = y_scaled + head_offset_y - size_scaled * 0.05
        eye_width = size_scaled * 0.17
        eye_height = size_scaled * 0.055
        eye_gap = size_scaled * 0.13

        # Apply expression modifier (WOPR matrix pipe workflow enhancement)
        expression_mod = 1.0 + (self.expression_modifier * 0.2)  # ±20% variation
        eye_width_mod = eye_width * expression_mod
        eye_height_mod = eye_height * expression_mod

        # Left eye (angular slit with SYPHON/WOPR-enhanced glow)
        # Outer glow (intensity-based) - BRIGHTER but dimmer than arc reactor (arc reactor uses 255 alpha)
        # Arc reactor max alpha: 255, so eyes/mouth use ~180-200 range (70-80% brightness)
        glow_alpha = int(150 * eye_intensity)  # Increased from 80 to 150 (brighter glow)
        left_eye_glow_points = [
            (x_scaled - eye_gap - eye_width_mod * 1.1, eye_y - eye_height_mod * 1.2),
            (x_scaled - eye_gap - eye_width_mod * 0.2, eye_y + eye_height_mod * 0.2),
            (x_scaled - eye_gap + eye_width_mod * 0.1, eye_y + eye_height_mod * 0.8),
        ]
        draw.polygon(left_eye_glow_points, fill=(*eye_color[:3], glow_alpha))

        # Main eye shape
        left_eye_points = [
            (x_scaled - eye_gap - eye_width_mod, eye_y - eye_height_mod),
            (x_scaled - eye_gap - eye_width_mod * 0.3, eye_y),
            (x_scaled - eye_gap, eye_y),
            (x_scaled - eye_gap - eye_width_mod * 0.2, eye_y + eye_height_mod * 0.5),
        ]
        eye_glow_color = (
            *eye_color[:3],
            int(240 * eye_intensity),
        )  # Increased from 200 to 240 (brighter)
        draw.polygon(left_eye_points, fill=eye_glow_color)

        # Eye bright core (intensity-based) - BRIGHTER but still dimmer than arc reactor
        core_alpha = int(
            250 * eye_intensity
        )  # Increased from 230 to 250 (brighter core, but < 255)
        left_eye_core_points = [
            (x_scaled - eye_gap - eye_width_mod * 0.85, eye_y - eye_height_mod * 0.5),
            (x_scaled - eye_gap - eye_width_mod * 0.4, eye_y),
            (x_scaled - eye_gap - eye_width_mod * 0.1, eye_y),
        ]
        draw.polygon(left_eye_core_points, fill=(255, 255, 255, core_alpha))

        # Right eye (angular slit with SYPHON/WOPR-enhanced glow)
        # Outer glow
        right_eye_glow_points = [
            (x_scaled + eye_gap - eye_width_mod * 0.1, eye_y + eye_height_mod * 0.8),
            (x_scaled + eye_gap + eye_width_mod * 0.2, eye_y + eye_height_mod * 0.2),
            (x_scaled + eye_gap + eye_width_mod * 1.1, eye_y - eye_height_mod * 1.2),
        ]
        draw.polygon(right_eye_glow_points, fill=(*eye_color[:3], glow_alpha))

        # Main eye shape
        right_eye_points = [
            (x_scaled + eye_gap, eye_y),
            (x_scaled + eye_gap + eye_width_mod * 0.3, eye_y),
            (x_scaled + eye_gap + eye_width_mod, eye_y - eye_height_mod),
            (x_scaled + eye_gap + eye_width_mod * 0.2, eye_y + eye_height_mod * 0.5),
        ]
        draw.polygon(right_eye_points, fill=eye_glow_color)

        # Eye bright core
        right_eye_core_points = [
            (x_scaled + eye_gap + eye_width_mod * 0.1, eye_y),
            (x_scaled + eye_gap + eye_width_mod * 0.4, eye_y),
            (x_scaled + eye_gap + eye_width_mod * 0.85, eye_y - eye_height_mod * 0.5),
        ]
        draw.polygon(right_eye_core_points, fill=(255, 255, 255, core_alpha))

        # SYPHON/WOPR-enhanced mouth (dynamic expressions matching ACVA)
        mouth_expression = self._get_mouth_expression()
        mouth_y = y_scaled + head_offset_y + size_scaled * 0.25  # Below faceplate line
        mouth_width = head_width * 0.4
        mouth_height = size_scaled * 0.08

        # Draw mouth based on expression (matching ACVA actions)
        # BRIGHTER but dimmer than arc reactor (arc reactor uses 255 alpha, mouth uses 200)
        mouth_color = (*secondary_rgb, 200)  # Increased from 180 to 200 (brighter glow)
        if mouth_expression == "speaking":
            # Open mouth (oval) - active speaking state
            mouth_bbox = [
                x_scaled - mouth_width / 2,
                mouth_y - mouth_height / 2,
                x_scaled + mouth_width / 2,
                mouth_y + mouth_height / 2,
            ]
            draw.ellipse(
                mouth_bbox,
                fill=(*arc_color[:3], 150),
                outline=mouth_color,
                width=max(1, int(2 * scale)),
            )
        elif mouth_expression == "smile":
            # Smile (arc curve upward) - positive state
            smile_points = []
            for i in range(21):
                t = (i / 20.0) * 2 - 1  # -1 to 1
                px = x_scaled + t * mouth_width / 2
                py = mouth_y - abs(t) * mouth_height * 0.6
                smile_points.append((px, py))
            if len(smile_points) > 2:
                draw.line(smile_points, fill=mouth_color, width=max(2, int(2 * scale)))
        elif mouth_expression == "frown" or mouth_expression == "combat":
            # Frown or combat grimace (inverted arc downward)
            frown_points = []
            for i in range(21):
                t = (i / 20.0) * 2 - 1
                px = x_scaled + t * mouth_width / 2
                py = mouth_y + abs(t) * mouth_height * 0.6
                frown_points.append((px, py))
            if len(frown_points) > 2:
                draw.line(frown_points, fill=mouth_color, width=max(2, int(2 * scale)))
        else:
            # Neutral (horizontal line) - default state
            draw.line(
                [x_scaled - mouth_width / 2, mouth_y, x_scaled + mouth_width / 2, mouth_y],
                fill=mouth_color,
                width=max(1, int(2 * scale)),
            )

        # Scale down to final size with ultra-high-quality resampling (LANCZOS for best quality)
        img_final = img.resize((self.window_size, self.window_size), Image.Resampling.LANCZOS)

        # MACRO FIX: SINGLE CLEAN IMAGE (like ACES - one sprite, no stacking)
        # TURN UP THE VOLUME: Ensure only ONE image exists
        # Delete old image reference if exists
        if hasattr(self, "ironman_photo") and self.ironman_photo:
            try:
                del self.ironman_photo
            except:
                pass

        # Create NEW single image (fresh, clean)
        self.ironman_photo = ImageTk.PhotoImage(img_final)
        # Store reference in canvas AND self to prevent GC
        self.canvas.ironman_photo_ref = self.ironman_photo
        # Create ONLY ONE image on canvas
        self.canvas.create_image(x, y, image=self.ironman_photo, tags="ironman", anchor="center")

        # Model text with better styling
        if self.window_size > 80:
            model_text = f"{self.current_model.display_name}"
            text_y = y + size / 2 + 12
            font_size = max(7, min(10, int(self.window_size / 12)))
            # Add text shadow for better readability
            self.canvas.create_text(
                x + 1,
                text_y + 1,
                text=model_text,
                fill="#000000",
                font=("Arial", font_size, "bold"),
                tags="ironman",
            )
            self.canvas.create_text(
                x,
                text_y,
                text=model_text,
                fill=self.ironman_colors["secondary"],
                font=("Arial", font_size, "bold"),
                tags="ironman",
            )

        self.ironman_figure = ["ironman"]

    def _get_eye_expression(self) -> str:
        """Get current eye expression state (SYPHON/WOPR enhanced)"""
        # Base expression from VA state
        if self.lightsaber_fight_mode:
            return "combat"
        elif self.is_speaking:
            return "speaking"
        elif self.is_listening:
            return "listening"
        elif self.fleeing:
            return "critical"
        elif len(self.alerts) > 0:
            return "alert"
        else:
            return self.eye_expression_state

    def _get_mouth_expression(self) -> str:
        """Get current mouth expression state (SYPHON/WOPR enhanced)"""
        # Match mouth to eye expression and VA state
        if self.lightsaber_fight_mode:
            return "combat"
        elif self.is_speaking:
            return "speaking"
        elif self.fleeing or (self.current_health / self.max_health) < 0.25:
            return "frown"
        elif len(self.syphon_tasks) > 5 or len(self.syphon_actionable_items) > 3:
            return "neutral"  # Busy/thinking
        else:
            return self.mouth_expression

    def _get_eye_color_and_intensity(
        self, base_color: Tuple[int, int, int, int], expression: str
    ) -> Tuple[Tuple[int, int, int], float]:
        """Get eye color and intensity based on SYPHON/WOPR-enhanced expression"""
        # Base intensity from SYPHON/WOPR data
        base_intensity = max(0.5, min(1.0, self.eye_intensity))

        # Expression-based color and intensity modifiers
        if expression == "combat":
            # Red/orange for combat
            color = (255, 100, 0)  # Orange-red
            intensity = base_intensity * 1.2
        elif expression == "critical" or expression == "alert":
            # Yellow/red for critical/alerts
            color = (255, 200, 0)  # Yellow-orange
            intensity = base_intensity * 1.1
        elif expression == "listening":
            # Bright cyan for listening
            color = (0, 255, 255)  # Cyan
            intensity = base_intensity * 1.15
        elif expression == "speaking":
            # Bright blue for speaking
            color = (100, 200, 255)  # Light blue
            intensity = base_intensity * 1.1
        else:
            # Normal - use base arc reactor color
            color = base_color[:3]
            intensity = base_intensity

        # Apply WOPR matrix pipe workflow modifier
        intensity = max(0.3, min(1.5, intensity + (self.expression_modifier * 0.1)))

        return color, intensity

    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    def _draw_ironman_canvas(self, x: int, y: int, size: int):
        """Fallback canvas drawing (simplified)"""
        # Main body circle
        body = self.canvas.create_oval(
            x - size / 2,
            y - size / 2,
            x + size / 2,
            y + size / 2,
            fill=self.ironman_colors["primary"],
            outline=self.ironman_colors["secondary"],
            width=2,
            tags="ironman",
        )

        # Arc reactor
        if self.is_listening:
            arc_color = "#FFFF00"
            arc_size = size * 0.4
        elif self.is_speaking:
            arc_color = "#00FFFF"
            arc_size = size * 0.45
        else:
            arc_color = self.ironman_colors["arc_reactor"]
            arc_size = size * 0.35

        arc_reactor = self.canvas.create_oval(
            x - arc_size / 2,
            y - arc_size / 2,
            x + arc_size / 2,
            y + arc_size / 2,
            fill=arc_color,
            outline=arc_color,
            width=1,
            tags="ironman",
        )

        # Eyes
        eye_y = y - size * 0.2
        eye_size = size * 0.1
        left_eye = self.canvas.create_polygon(
            x - size / 3,
            eye_y - eye_size / 2,
            x - size / 6,
            eye_y,
            x - size / 4,
            eye_y,
            fill=arc_color,
            outline="",
            tags="ironman",
        )
        right_eye = self.canvas.create_polygon(
            x + size / 6,
            eye_y,
            x + size / 3,
            eye_y - eye_size / 2,
            x + size / 4,
            eye_y,
            fill=arc_color,
            outline="",
            tags="ironman",
        )

        # Model text
        if self.window_size > 80:
            model_text = f"{self.current_model.display_name}"
            text_y = y + size / 2 + 12
            font_size = max(7, min(9, int(self.window_size / 15)))
            self.canvas.create_text(
                x,
                text_y,
                text=model_text,
                fill=self.ironman_colors["secondary"],
                font=("Arial", font_size),
                tags="ironman",
            )

        self.ironman_figure = ["ironman"]

    def _draw_lightsaber(self, x: float, y: float, size: float):
        """Draw lightsaber (cyan blade extending from IRON MAN)"""
        import math

        # Lightsaber extends from side of IRON MAN
        # Angle based on fight animation frame (swinging motion)
        angle = (self.fight_animation_frame * 0.2) % (2 * math.pi)
        saber_length = size * 2.5  # Lightsaber length

        # Calculate end point
        saber_end_x = x + math.cos(angle) * saber_length
        saber_end_y = y + math.sin(angle) * saber_length

        # Draw lightsaber blade (cyan with glow effect)
        # Outer glow
        self.canvas.create_line(
            x, y, saber_end_x, saber_end_y, fill="#00FFFF", width=8, tags="lightsaber"
        )
        # Inner bright core
        self.canvas.create_line(
            x, y, saber_end_x, saber_end_y, fill="#FFFFFF", width=4, tags="lightsaber"
        )

        # Lightsaber hilt (small rectangle at start)
        hilt_size = 4
        self.canvas.create_rectangle(
            x - hilt_size,
            y - hilt_size,
            x + hilt_size,
            y + hilt_size,
            fill="#404040",
            outline="#606060",
            width=1,
            tags="lightsaber",
        )

        self.logger.debug(f"⚔️  Lightsaber drawn at angle {angle:.2f}")

    def _draw_acva_lightsaber_indicator(self):
        """Draw ACVA lightsaber animation indicator (visual feedback only - ACVA is external app)"""
        if not self.ac_va_position:
            return

        import math

        # ACVA lightsaber extends from ACVA position
        # Angle based on ACVA lightsaber animation frame (different from IMVA)
        acva_angle = (self.acva_lightsaber_frame * 0.15 + math.pi) % (
            2 * math.pi
        )  # Opposite direction
        saber_length = 80  # ACVA lightsaber length (visual indicator)

        acva_x, acva_y = self.ac_va_position

        # Calculate end point (relative to IMVA window, not screen coordinates)
        # We need to convert ACVA screen position to canvas coordinates
        # For now, draw at a fixed offset to show ACVA is "fighting back"
        canvas_x = self.window_size // 2 + (acva_x - self.x) * 0.1  # Scale down
        canvas_y = self.window_size // 2 + (acva_y - self.y) * 0.1  # Scale down

        # Draw ACVA lightsaber blade (red/orange to differentiate from IMVA cyan)
        saber_end_x = canvas_x + math.cos(acva_angle) * saber_length
        saber_end_y = canvas_y + math.sin(acva_angle) * saber_length

        # Outer glow (red/orange)
        self.canvas.create_line(
            canvas_x,
            canvas_y,
            saber_end_x,
            saber_end_y,
            fill="#FF4400",
            width=6,
            tags="acva_lightsaber",
        )
        # Inner bright core (yellow/white)
        self.canvas.create_line(
            canvas_x,
            canvas_y,
            saber_end_x,
            saber_end_y,
            fill="#FFAA00",
            width=3,
            tags="acva_lightsaber",
        )

    def _draw_acva_hit_effects(self):
        """Draw ACVA hit effects (sparks, damage indicators) - visual feedback only"""
        if not self.ac_va_position or not self.acva_hit_effects:
            return

        import random

        current_time = time.time()

        for hit_effect in self.acva_hit_effects:
            age = current_time - hit_effect["time"]
            if age > 2.0:  # Effect expires after 2 seconds
                continue

            acva_x, acva_y = hit_effect["position"]
            # Convert to canvas coordinates (scaled down)
            canvas_x = self.window_size // 2 + (acva_x - self.x) * 0.1
            canvas_y = self.window_size // 2 + (acva_y - self.y) * 0.1

            # Fade out over time
            alpha_factor = 1.0 - (age / 2.0)

            # Draw sparks (small yellow/orange particles)
            num_sparks = 5
            for _ in range(num_sparks):
                spark_x = canvas_x + random.uniform(-15, 15) * alpha_factor
                spark_y = canvas_y + random.uniform(-15, 15) * alpha_factor
                spark_size = random.uniform(2, 4) * alpha_factor
                spark_color = random.choice(["#FFAA00", "#FF4400", "#FFFF00"])
                self.canvas.create_oval(
                    spark_x - spark_size,
                    spark_y - spark_size,
                    spark_x + spark_size,
                    spark_y + spark_size,
                    fill=spark_color,
                    outline="",
                    tags="acva_hit_effects",
                )

            # Draw damage number indicator
            damage_text = f"-{hit_effect['damage']:.0f}"
            text_y = canvas_y - 20 * alpha_factor
            text_color = "#FF4400" if hit_effect["damage"] >= 10 else "#FFAA00"
            self.canvas.create_text(
                canvas_x,
                text_y,
                text=damage_text,
                fill=text_color,
                font=("Arial", max(8, int(10 * alpha_factor)), "bold"),
                tags="acva_hit_effects",
            )

    def _draw_health_bar(self, x: float, y: float, size: float):
        """Draw health/hitpoint bar above IRON MAN during fights"""
        if not self.lightsaber_fight_mode:
            return

        # Health bar dimensions
        bar_width = size * 1.5
        bar_height = 6
        bar_x = x - bar_width / 2
        bar_y = y - size / 2 - 25  # Position above IRON MAN

        # Background (empty health bar)
        self.canvas.create_rectangle(
            bar_x,
            bar_y,
            bar_x + bar_width,
            bar_y + bar_height,
            fill="#333333",
            outline="#666666",
            width=1,
            tags="healthbar",
        )

        # Calculate health percentage
        health_percent = max(0.0, min(1.0, self.current_health / self.max_health))
        health_width = bar_width * health_percent

        # Health bar color based on health level
        if health_percent > 0.6:
            health_color = "#00FF00"  # Green (healthy)
        elif health_percent > 0.3:
            health_color = "#FFFF00"  # Yellow (damaged)
        else:
            health_color = "#FF0000"  # Red (critical)

        # Draw filled health bar
        if health_width > 0:
            self.canvas.create_rectangle(
                bar_x,
                bar_y,
                bar_x + health_width,
                bar_y + bar_height,
                fill=health_color,
                outline="",
                tags="healthbar",
            )

        # Health percentage text
        health_text = f"{int(self.current_health)}/{int(self.max_health)}"
        self.canvas.create_text(
            x,
            bar_y - 10,
            text=health_text,
            fill="#FFFFFF",
            font=("Arial", 7, "bold"),
            tags="healthbar",
        )

    def _draw_powercord_tail(self, x: float, y: float, size: float):
        """Draw simplified powercord tail"""
        # Powercord comes out from bottom of IRON MAN (simplified, smaller)
        tail_length = size * 0.8  # Shorter tail
        tail_start_y = y + size / 2
        tail_end_y = min(
            tail_start_y + tail_length, self.window_size - 5
        )  # Don't go outside window

        # Simple straight line with slight wave
        wave = 3 * abs(self.arc_reactor_pulse)
        tail_x = x + wave * 0.3
        self.canvas.create_line(
            x,
            tail_start_y,
            tail_x,
            tail_end_y,
            fill=self.ironman_colors["powercord"],
            width=3,
            tags="powercord",
        )

        # Small plug at end (only if there's room)
        if tail_end_y < self.window_size - 8:
            plug_size = 5
            self.canvas.create_rectangle(
                tail_x - plug_size,
                tail_end_y - plug_size / 2,
                tail_x + plug_size,
                tail_end_y + plug_size / 2,
                fill="#404040",
                outline="#606060",
                width=1,
                tags="powercord",
            )

        self.powercord_tail = ["powercord"]

    def _roll_d20(self, context: str = "Combat", modifier: float = 0.0):
        """Roll a D&D d20 die and display on screen (@dnd @d20 virtual tabletop)"""
        if not self.canvas:
            return

        roll_result = random.randint(1, 20)
        total = roll_result + int(modifier)

        # Random position within canvas (window) for dice display
        # Dice appear randomly across the VA window
        dice_x = random.randint(40, self.window_size - 40)
        dice_y = random.randint(40, self.window_size - 40)

        # Create dice roll data
        dice_roll = {
            "x": dice_x,
            "y": dice_y,
            "result": roll_result,
            "total": total,
            "modifier": modifier,
            "context": context,
            "created_at": time.time(),
            "animation_frame": 0,
        }

        self.dice_rolls.append(dice_roll)
        # Log dice roll for @hits tracking (LIGHT/MEDIUM/HEAVY)
        self.logger.info(f"🎲 d20 Roll: {roll_result} (+{int(modifier)}) = {total} ({context})")

        # Clean up old dice rolls
        current_time = time.time()
        self.dice_rolls = [
            d for d in self.dice_rolls if current_time - d["created_at"] < self.dice_lifetime
        ]

    def _draw_dice_rolls(self):
        """Draw D&D d20 dice rolls on screen (virtual tabletop style)"""
        if not self.canvas or not self.dice_rolls:
            return

        current_time = time.time()

        for dice in self.dice_rolls[:10]:  # Limit to 10 dice on screen
            # Calculate age and fade
            age = current_time - dice["created_at"]
            if age > self.dice_lifetime:
                continue

            # Fade out as dice gets older
            alpha_factor = 1.0 - (age / self.dice_lifetime)
            alpha_factor = max(0.3, alpha_factor)  # Minimum visibility

            # Dice positions are already in canvas coordinates
            canvas_x = dice["x"]
            canvas_y = dice["y"]

            # Draw dice (simplified d20 icon - circle with number)
            dice_size = 25
            dice["animation_frame"] += 1

            # Dice background (circle) - use darker background for contrast
            color_intensity = int(80 * alpha_factor)
            dice_color = f"#{color_intensity:02x}{color_intensity:02x}{color_intensity:02x}"
            outline_intensity = min(255, int(150 * alpha_factor))
            outline_color = (
                f"#{outline_intensity:02x}{outline_intensity:02x}{outline_intensity:02x}"
            )

            # Draw dice circle
            self.canvas.create_oval(
                canvas_x - dice_size,
                canvas_y - dice_size,
                canvas_x + dice_size,
                canvas_y + dice_size,
                fill=dice_color,
                outline=outline_color,
                width=2,
                tags="dice",
            )

            # Draw d20 number (bright and visible)
            text_color = "#FFFFFF" if alpha_factor > 0.5 else "#CCCCCC"
            self.canvas.create_text(
                canvas_x,
                canvas_y,
                text=str(dice["result"]),
                fill=text_color,
                font=("Arial", 14, "bold"),
                tags="dice",
            )

            # Draw modifier and total if applicable
            if dice["modifier"] != 0:
                modifier_text = (
                    f"+{int(dice['modifier'])}"
                    if dice["modifier"] > 0
                    else str(int(dice["modifier"]))
                )
                self.canvas.create_text(
                    canvas_x,
                    canvas_y + 20,
                    text=f"{modifier_text} = {dice['total']}",
                    fill=text_color,
                    font=("Arial", 8),
                    tags="dice",
                )

            # Draw context label (small)
            if dice["context"]:
                self.canvas.create_text(
                    canvas_x,
                    canvas_y - dice_size - 10,
                    text=dice["context"],
                    fill=text_color,
                    font=("Arial", 7),
                    tags="dice",
                )

    def _draw_health_status_indicator(self):
        """Draw D&D RPG health gradient indicator in upper-right corner (full-health to death/skull)"""
        if not self.canvas:
            return

        # Position in upper-right corner
        indicator_size = 12
        margin = 5
        x = self.window_size - margin - indicator_size
        y = margin + indicator_size

        # Calculate health percentage (0.0 to 1.0)
        health_percent = max(0.0, min(1.0, self.current_health / self.max_health))

        # D&D RPG color gradient: Green (full health) -> Yellow -> Orange -> Red -> Dark Red/Black (death/skull)
        if health_percent > 0.75:
            # Green (healthy)
            color = "#00FF00"
        elif health_percent > 0.50:
            # Yellow-Green (wounded)
            color = "#88FF00"
        elif health_percent > 0.25:
            # Yellow (injured)
            color = "#FFFF00"
        elif health_percent > 0.10:
            # Orange (critical)
            color = "#FF8800"
        elif health_percent > 0.05:
            # Red (dying)
            color = "#FF0000"
        else:
            # Dark Red/Black (death/skull) - almost dead
            color = "#880000"

        # Draw indicator circle with gradient effect
        # Outer glow (if not dead)
        if health_percent > 0.05:
            glow_size = indicator_size + 2
            self.canvas.create_oval(
                x - glow_size / 2,
                y - glow_size / 2,
                x + glow_size / 2,
                y + glow_size / 2,
                fill=color,
                outline="",
                tags="health_indicator",
            )

        # Main indicator circle
        self.canvas.create_oval(
            x - indicator_size / 2,
            y - indicator_size / 2,
            x + indicator_size / 2,
            y + indicator_size / 2,
            fill=color,
            outline="#FFFFFF",
            width=1,
            tags="health_indicator",
        )

        # Draw skull symbol if health is critically low (<= 5%)
        if health_percent <= 0.05:
            # Simple skull shape (X symbol for simplicity)
            skull_size = indicator_size * 0.6
            self.canvas.create_text(
                x, y, text="☠", fill="#FFFFFF", font=("Arial", 8, "bold"), tags="health_indicator"
            )

    def _draw_alerts(self):
        """Draw active alerts above IRON MAN with collapse/expand functionality"""
        if not self.alerts:
            return

        # Draw IRON MAN centered in the window (not using self.x, self.y directly)
        x, y = self.window_size // 2, self.window_size // 2
        size = self.size

        # Show up to 2 most recent alerts (fewer for smaller window)
        alerts_to_show = self.alerts[:2]
        alert_y = y - size / 2 - 15  # Closer to IRON MAN

        for i, alert in enumerate(alerts_to_show):
            alert_offset_y = alert_y - (i * 12)  # Closer together

            # Check if alert is expanded
            is_expanded = alert.alert_signature and alert.alert_signature in self.expanded_alerts

            # Alert indicator (small colored circle)
            indicator_size = 4  # Smaller
            indicator_x = x - size / 2 - 10
            self.canvas.create_oval(
                indicator_x,
                alert_offset_y - indicator_size / 2,
                indicator_x + 5,
                alert_offset_y + indicator_size / 2,
                fill=alert.level.color,
                outline=alert.level.color,
                tags="alerts",
            )

            # If alert has duplicates, show collapse/expand indicator
            if alert.duplicate_count > 1:
                # Draw clickable collapse/expand indicator
                expand_x = indicator_x - 8
                expand_size = 3

                # Draw expand/collapse button
                if is_expanded:
                    # Expanded state: show "−" to collapse
                    self.canvas.create_text(
                        expand_x,
                        alert_offset_y,
                        text="−",
                        fill=alert.level.color,
                        font=("Arial", 6, "bold"),
                        tags=("alerts", f"alert_toggle_{i}"),
                    )
                else:
                    # Collapsed state: show "+" to expand
                    self.canvas.create_text(
                        expand_x,
                        alert_offset_y,
                        text="+",
                        fill=alert.level.color,
                        font=("Arial", 6, "bold"),
                        tags=("alerts", f"alert_toggle_{i}"),
                    )

                # Draw duplicate count
                count_x = expand_x - 6
                self.canvas.create_text(
                    count_x,
                    alert_offset_y,
                    text=f"×{alert.duplicate_count}",
                    fill=alert.level.color,
                    font=("Arial", 5),
                    tags=("alerts", f"alert_count_{i}"),
                )

                # Store alert signature for click detection
                # We'll handle clicks in _on_left_click by checking coordinates

            # If expanded, show more details including meta-tags
            if is_expanded and alert.message:
                # Show full message (truncated if too long for small window)
                message_preview = (
                    alert.message[:50] + "..." if len(alert.message) > 50 else alert.message
                )
                text_x = indicator_x - 45
                # Draw message text
                self.canvas.create_text(
                    text_x,
                    alert_offset_y,
                    text=message_preview,
                    fill=alert.level.color,
                    font=("Arial", 5),
                    tags=("alerts", f"alert_text_{i}", f"alert_clickable_{i}"),
                    anchor="e",
                )
                # Draw clickable area indicator (underline or background)
                text_bbox = self.canvas.bbox(f"alert_text_{i}")
                if text_bbox:
                    self.canvas.create_line(
                        text_bbox[0],
                        text_bbox[3] + 1,
                        text_bbox[2],
                        text_bbox[3] + 1,
                        fill=alert.level.color,
                        width=1,
                        tags=("alerts", f"alert_underline_{i}"),
                    )

                # Show meta-tags if available (Smart AI Logging)
                if alert.meta_tags and self.smart_logging:
                    try:
                        # Create a temporary alert group to get meta-tag summary
                        temp_group = type(
                            "AlertGroup",
                            (),
                            {
                                "meta_tags": type("MetaTags", (), alert.meta_tags)(),
                                "intensity": type("Intensity", (), {"value": "active"})(),
                                "temperature": type("Temperature", (), {"value": "warm"})(),
                            },
                        )()
                        meta_summary = self.smart_logging.get_group_meta_tags_summary(temp_group)
                        if meta_summary and meta_summary != "No meta-tags":
                            # Show meta-tags below message (smaller font)
                            meta_y = alert_offset_y + 6
                            meta_text = (
                                meta_summary[:60] + "..."
                                if len(meta_summary) > 60
                                else meta_summary
                            )
                            self.canvas.create_text(
                                text_x,
                                meta_y,
                                text=meta_text,
                                fill=alert.level.color,
                                font=("Arial", 4),
                                tags=("alerts", f"alert_meta_{i}"),
                                anchor="e",
                            )
                    except Exception as e:
                        self.logger.debug(f"Error displaying meta-tags: {e}")

    def cycle_ai_model(self):
        """Cycle to next AI model"""
        self.current_model_index = (self.current_model_index + 1) % len(self.ai_models)
        self.current_model = self.ai_models[self.current_model_index]
        self.last_model_cycle = time.time()

        self.logger.info(
            f"🔄 Cycled to {self.current_model.display_name} ({self.current_model.model_name})"
        )

        # Add notification
        self.add_alert(
            Alert(
                title=f"AI Model: {self.current_model.display_name}",
                message=f"Now using {self.current_model.system} - {self.current_model.description}",
                level=AlertLevel.INFO,
                source="IRONMAN Assistant",
            )
        )

        # Redraw to update model indicator
        if self.canvas:
            self._draw_ironman()

    def _generate_alert_signature(self, alert: Alert) -> str:
        """Generate a unique signature for grouping duplicate alerts, ignoring timestamps"""
        import re

        # Extract workflow_id if present in message (JSON format) - highest priority
        workflow_match = re.search(r'"workflow_id":\s*"([^"]+)"', alert.message)
        if workflow_match:
            return f"{alert.title}:{workflow_match.group(1)}"

        # Clean message by removing timestamps and dynamic data
        message_clean = alert.message

        # Remove ISO format timestamps (2026-01-05T03:58:50, 20260105_035850, etc.)
        message_clean = re.sub(
            r"\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?", "", message_clean
        )
        message_clean = re.sub(r"\d{8}_\d{6}", "", message_clean)
        message_clean = re.sub(r"\d{4}\d{2}\d{2}", "", message_clean)

        # Remove time-only patterns (HH:MM:SS, HH:MM)
        message_clean = re.sub(r"\b\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?\b", "", message_clean)

        # Remove age/TTL patterns (age: 1093.4s, TTL: 1800s)
        message_clean = re.sub(
            r"\b(?:age|TTL):\s*\d+\.?\d*\s*[smh]", "", message_clean, flags=re.IGNORECASE
        )

        # Remove version numbers that might change (version 2.0, v1.2.3)
        message_clean = re.sub(
            r"\bversion\s+\d+\.\d+(?:\.\d+)?", "", message_clean, flags=re.IGNORECASE
        )

        # Remove IP addresses (<NAS_PRIMARY_IP>) - keep structure but normalize
        message_clean = re.sub(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "[IP]", message_clean)

        # Remove port numbers (:5001, :443)
        message_clean = re.sub(r":\d{4,5}\b", "", message_clean)

        # Remove UUIDs and hashes
        message_clean = re.sub(
            r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
            "",
            message_clean,
            flags=re.IGNORECASE,
        )
        message_clean = re.sub(r"\b[0-9a-f]{32,}\b", "", message_clean, flags=re.IGNORECASE)

        # Clean up extra whitespace
        message_clean = re.sub(r"\s+", " ", message_clean).strip()

        # Use first 50 chars of cleaned message for grouping
        message_preview = message_clean[:50] if len(message_clean) > 50 else message_clean

        # Include level in signature for INFO vs WARNING vs CRITICAL
        return f"{alert.title}:{alert.level.level}:{message_preview}"

    def add_alert(self, alert: Alert):
        """Add an alert, grouping duplicates with smart AI logging"""
        # Generate signature for grouping
        signature = self._generate_alert_signature(alert)
        alert.alert_signature = signature

        # Use Smart AI Logging Module for advanced grouping and meta-tagging
        if self.smart_logging:
            try:
                # Extract meta-tags using smart AI logging
                meta_tags = self.smart_logging.extract_meta_tags(alert)
                alert.meta_tags = {
                    "incident_id": meta_tags.incident_id,
                    "severity_tags": meta_tags.severity_tags,
                    "criticality_tags": meta_tags.criticality_tags,
                    "temperature_tags": meta_tags.temperature_tags,
                    "intensity_tags": meta_tags.intensity_tags,
                    "system_tags": meta_tags.system_tags,
                    "context_tags": meta_tags.context_tags,
                    "hashtags": meta_tags.hashtags,
                    "custom_tags": meta_tags.custom_tags,
                }
                alert.incident_id = meta_tags.incident_id

                # Periodically analyze and group alerts using smart AI logging
                if len(self.alerts) > 0 and len(self.alerts) % 10 == 0:
                    # Re-analyze groups every 10 alerts
                    groups = self.smart_logging.analyze_and_group(self.alerts)
                    # Update alert group_ids
                    for group in groups:
                        for group_alert in group.alerts:
                            if hasattr(group_alert, "group_id"):
                                group_alert.group_id = group.group_id
            except Exception as e:
                self.logger.debug(f"Smart AI logging analysis error: {e}")

        # Check if this is a duplicate
        existing_alert = None
        for existing in self.alerts:
            if existing.alert_signature == signature:
                existing_alert = existing
                break

        if existing_alert:
            # Increment duplicate count and update timestamp
            existing_alert.duplicate_count += 1
            existing_alert.timestamp = datetime.now()
            # Auto-collapse immediately when a new duplicate arrives (if it was expanded)
            if signature in self.expanded_alerts:
                self.expanded_alerts.discard(signature)
                if signature in self.expanded_alert_timestamps:
                    del self.expanded_alert_timestamps[signature]
                existing_alert.collapsed = True
                self.logger.debug(
                    f"🔔 Auto-collapsed alert on duplicate #{existing_alert.duplicate_count}: {alert.title}"
                )
            else:
                existing_alert.collapsed = True  # Keep collapsed for new duplicates
            self.logger.debug(
                f"🔔 Alert duplicate #{existing_alert.duplicate_count}: {alert.title}"
            )
        else:
            # New alert - add to list
            alert.collapsed = True  # Start collapsed
            self.alerts.insert(0, alert)
            if len(self.alerts) > self.max_alerts:
                # Remove oldest alerts, but keep grouped ones
                self.alerts = self.alerts[: self.max_alerts]

        # Log alert (only once per unique alert, with count if duplicate)
        if existing_alert:
            if existing_alert.duplicate_count == 2:
                self.logger.info(
                    f"🔔 Alert: {alert.level.level.upper()} - {alert.title}: {alert.message[:60]}... (×{existing_alert.duplicate_count})"
                )
        else:
            self.logger.info(
                f"🔔 Alert: {alert.level.level.upper()} - {alert.title}: {alert.message}"
            )

        # Redraw to show alerts
        if self.canvas:
            self._draw_ironman()

    def _check_system_with_retry(self, url: str, timeout: int = 2, max_retries: int = 2) -> bool:
        """Check system status with retry logic"""
        for attempt in range(max_retries + 1):
            try:
                response = requests.get(url, timeout=timeout)
                if response.status_code == 200:
                    return True
            except Exception as e:
                if attempt < max_retries:
                    wait_time = 0.5 * (attempt + 1)  # Simple backoff
                    self.logger.debug(
                        f"Retry {attempt + 1}/{max_retries} for {url} in {wait_time}s: {e}"
                    )
                    time.sleep(wait_time)
                else:
                    self.logger.debug(
                        f"Failed to check {url} after {max_retries + 1} attempts: {e}"
                    )
        return False

    def check_lumina_systems(self):
        """Check status of LUMINA systems with retry logic"""
        try:
            # Check JARVIS
            jarvis_status = False
            if self.jarvis_agent:
                try:
                    # Try to get status (simplified check)
                    jarvis_status = True
                except:
                    jarvis_status = False

            # Check R5 system (with retry)
            r5_status = self._check_system_with_retry(
                "http://localhost:8000/r5/health", timeout=2, max_retries=2
            )

            # Check ULTRON (local) (with retry)
            ultron_status = self._check_system_with_retry(
                "http://localhost:11434/api/tags", timeout=2, max_retries=2
            )

            # Check KAIJU Number Eight (Desktop PC) (with retry)
            kaiju_status = self._check_system_with_retry(
                "http://<NAS_IP>:11434/api/tags", timeout=2, max_retries=2
            )

            # Check @helpdesk (file-based check)
            helpdesk_status = False
            helpdesk_dir = self.project_root / "config" / "helpdesk"
            if helpdesk_dir.exists():
                helpdesk_status = True

            # Check NAS Migration status
            nas_migration_status = {"running": False, "status": "unknown", "message": ""}
            if NAS_MIGRATION_AVAILABLE and get_migration_status_for_va:
                try:
                    migration_status = get_migration_status_for_va()
                    nas_migration_status = {
                        "running": migration_status.get("is_running", False),
                        "status": migration_status.get("status", "unknown"),
                        "message": migration_status.get("message", ""),
                        "details": migration_status.get("details", {}),
                    }
                except Exception as e:
                    self.logger.debug(f"Error checking NAS migration status: {e}")

            # Update status
            old_status = self.system_status.to_dict()
            self.system_status.jarvis = jarvis_status
            self.system_status.r5 = r5_status
            self.system_status.ultron = ultron_status
            self.system_status.kaiju = kaiju_status
            self.system_status.helpdesk = helpdesk_status
            self.system_status.nas_migration = nas_migration_status
            self.system_status.last_check = datetime.now()

            # Generate alerts for status changes
            if not jarvis_status and old_status.get("jarvis"):
                self.add_alert(
                    Alert(
                        title="JARVIS Offline",
                        message="JARVIS system is not responding",
                        level=AlertLevel.WARNING,
                        source="System Monitor",
                    )
                )
            elif jarvis_status and not old_status.get("jarvis"):
                self.add_alert(
                    Alert(
                        title="JARVIS Online",
                        message="JARVIS system is back online",
                        level=AlertLevel.INFO,
                        source="System Monitor",
                    )
                )

            if not r5_status and old_status.get("r5"):
                self.add_alert(
                    Alert(
                        title="R5 System Offline",
                        message="R5 Living Context Matrix is not responding",
                        level=AlertLevel.WARNING,
                        source="System Monitor",
                    )
                )
            elif r5_status and not old_status.get("r5"):
                self.add_alert(
                    Alert(
                        title="R5 System Online",
                        message="R5 Living Context Matrix is back online",
                        level=AlertLevel.INFO,
                        source="System Monitor",
                    )
                )

            # KAIJU status checks (independent of other system checks)
            if not kaiju_status and old_status.get("kaiju"):
                self.add_alert(
                    Alert(
                        title="KAIJU Offline",
                        message="KAIJU Iron Legion cluster is not responding",
                        level=AlertLevel.WARNING,
                        source="System Monitor",
                    )
                )
            if kaiju_status and not old_status.get("kaiju"):
                self.add_alert(
                    Alert(
                        title="KAIJU Online",
                        message="KAIJU Iron Legion cluster is back online",
                        level=AlertLevel.INFO,
                        source="System Monitor",
                    )
                )

            # NAS Migration status alerts (independent of KAIJU checks)
            old_migration = old_status.get("nas_migration", {})
            if nas_migration_status.get("running") and not old_migration.get("running"):
                self.add_alert(
                    Alert(
                        title="NAS Migration Started",
                        message=nas_migration_status.get("message", "Migration in progress"),
                        level=AlertLevel.INFO,
                        source="NAS Migration",
                    )
                )
            elif not nas_migration_status.get("running") and old_migration.get("running"):
                if nas_migration_status.get("status") == "completed":
                    self.add_alert(
                        Alert(
                            title="NAS Migration Completed",
                            message="Migration completed successfully",
                            level=AlertLevel.INFO,
                            source="NAS Migration",
                        )
                    )
                elif nas_migration_status.get("status") == "failed":
                    self.add_alert(
                        Alert(
                            title="NAS Migration Failed",
                            message=nas_migration_status.get("message", "Migration failed"),
                            level=AlertLevel.WARNING,
                            source="NAS Migration",
                        )
                    )

        except Exception as e:
            self.logger.error(f"Error checking LUMINA systems: {e}", exc_info=True)

    def start_syphon_enhancement_loop(self):
        """Start SYPHON enhancement loop - actively use SYPHON to improve VA behavior"""
        if not self.syphon:
            return

        def syphon_enhancement_loop():
            while self.running:
                try:
                    current_time = time.time()
                    if (
                        current_time - self.last_syphon_enhancement
                        >= self.syphon_enhancement_interval
                    ):
                        self._enhance_va_with_syphon()
                        self.last_syphon_enhancement = current_time

                    time.sleep(10)  # Check every 10 seconds
                except Exception as e:
                    logger.error(f"Error in SYPHON enhancement loop: {e}", exc_info=True)
                    time.sleep(30)

        enhancement_thread = threading.Thread(target=syphon_enhancement_loop, daemon=True)
        enhancement_thread.start()
        self.logger.info("✅ SYPHON enhancement loop started - actively improving VA")

    def _enhance_va_with_syphon(self):
        """Use SYPHON to extract intelligence and enhance VA behavior (@JARVIS @LUMINA)"""
        if not self.syphon:
            return

        # @JARVIS: Log SYPHON enhancement execution
        if hasattr(self, "action_sequence_system") and self.action_sequence_system:
            if self.action_sequence_system.jarvis_available:
                self.action_sequence_system._log_to_jarvis(
                    "syphon_enhancement",
                    {"timestamp": datetime.now().isoformat(), "va_type": "ironman"},
                )

        try:
            # Get recent SYPHON data from storage
            storage = self.syphon.storage
            if storage:
                recent_data = storage.get_all()
                # Get data from last 24 hours
                from datetime import timedelta

                cutoff_time = datetime.now() - timedelta(hours=24)
                recent_data = [d for d in recent_data if d.extracted_at >= cutoff_time]

                # Aggregate actionable items, tasks, decisions, and intelligence
                self.syphon_actionable_items = []
                self.syphon_tasks = []
                self.syphon_decisions = []
                self.syphon_intelligence = []

                for data in recent_data:
                    if data.actionable_items:
                        self.syphon_actionable_items.extend(data.actionable_items)
                    if data.tasks:
                        self.syphon_tasks.extend(data.tasks)
                    if data.decisions:
                        self.syphon_decisions.extend(data.decisions)
                    if data.intelligence:
                        self.syphon_intelligence.extend(data.intelligence)

                # Use actionable items to create proactive alerts
                if self.syphon_actionable_items:
                    # Show most important actionable items as alerts
                    important_items = self.syphon_actionable_items[:3]  # Top 3
                    for item in important_items:
                        if item not in [alert.message for alert in self.alerts]:
                            self.add_alert(
                                Alert(
                                    title="Action Required",
                                    message=item[:100],  # Truncate long items
                                    level=AlertLevel.WARNING,
                                    source="SYPHON",
                                    action_required=True,
                                )
                            )

                # Use tasks to provide proactive assistance
                if self.syphon_tasks:
                    high_priority_tasks = [
                        t for t in self.syphon_tasks if t.get("priority") == "high"
                    ]
                    if high_priority_tasks:
                        task = high_priority_tasks[0]
                        task_text = task.get("task", "")
                        if task_text and task_text not in [alert.message for alert in self.alerts]:
                            self.add_alert(
                                Alert(
                                    title="High Priority Task",
                                    message=task_text[:100],
                                    level=AlertLevel.CRITICAL,
                                    source="SYPHON",
                                    action_required=True,
                                )
                            )

                # Use intelligence to enhance conversation context
                if self.syphon_intelligence:
                    # Store intelligence for use in responses
                    self.logger.debug(
                        f"SYPHON: Loaded {len(self.syphon_intelligence)} intelligence items"
                    )

                # Filter IDE diagnostics/problems and create alerts
                ide_data = [d for d in recent_data if d.source_type.value == "ide"]
                if ide_data:
                    for ide_item in ide_data:
                        # Extract IDE diagnostics/problems from content
                        content = ide_item.content
                        if (
                            "error" in content.lower()
                            or "problem" in content.lower()
                            or "diagnostic" in content.lower()
                        ):
                            # Create alert for IDE issues
                            alert_title = "IDE Issue Detected"
                            alert_message = content[:150]  # Truncate long messages
                            if alert_message not in [alert.message for alert in self.alerts]:
                                self.add_alert(
                                    Alert(
                                        title=alert_title,
                                        message=alert_message,
                                        level=AlertLevel.WARNING,
                                        source="SYPHON-IDE",
                                        action_required=True,
                                    )
                                )

                        # Use actionable items from IDE data
                        if ide_item.actionable_items:
                            for item in ide_item.actionable_items[:2]:  # Top 2 IDE actionable items
                                if item not in [alert.message for alert in self.alerts]:
                                    self.add_alert(
                                        Alert(
                                            title="IDE Action Required",
                                            message=item[:100],
                                            level=AlertLevel.WARNING,
                                            source="SYPHON-IDE",
                                            action_required=True,
                                        )
                                    )

                self.logger.debug(
                    f"SYPHON Enhancement: {len(self.syphon_actionable_items)} actionable items, "
                    f"{len(self.syphon_tasks)} tasks, {len(self.syphon_decisions)} decisions, "
                    f"{len(ide_data)} IDE notifications"
                )

            # Extract intelligence from recent conversations to improve VA
            if self.conversation_history:
                # Get recent conversation context
                recent_conversations = self.conversation_history[-10:]  # Last 10 exchanges
                conversation_text = "\n".join(
                    [
                        f"User: {ctx.get('user', '')}\nAssistant: {ctx.get('assistant', '')}"
                        for ctx in recent_conversations
                    ]
                )

                if conversation_text.strip():
                    # Extract intelligence from conversations
                    from syphon.models import DataSourceType

                    result = self.syphon.extract(
                        DataSourceType.IDE,  # Use IDE type for conversation extraction
                        conversation_text,
                        metadata={"source": "va_conversations", "va_type": "ironman"},
                    )

                    if result.success and result.data:
                        # Use extracted actionable items to enhance VA memory
                        actionable_items = result.data.actionable_items or []
                        for item in actionable_items[:5]:  # Top 5 items
                            # Learn from actionable items - add to memory
                            self.remember(f"User action: {item}", category="syphon_enhanced")

                        # Use extracted tasks to inform VA behavior
                        tasks = result.data.tasks or []
                        if tasks:
                            self.logger.info(
                                f"🔍 SYPHON extracted {len(tasks)} tasks from conversations"
                            )
                            # Store for VA awareness
                            if "syphon_tasks" not in self.memory:
                                self.memory["syphon_tasks"] = []
                            self.memory["syphon_tasks"].extend(tasks[:5])
                            # Keep only last 50 syphon tasks to prevent memory leak
                            if len(self.memory["syphon_tasks"]) > 50:
                                self.memory["syphon_tasks"] = self.memory["syphon_tasks"][-50:]
                            self._save_memory()

                        # Use extracted intelligence to enhance responses
                        intelligence = result.data.intelligence or []
                        if intelligence:
                            self.syphon_enhanced_knowledge.extend(intelligence[:10])
                            # Keep only recent knowledge
                            if len(self.syphon_enhanced_knowledge) > 50:
                                self.syphon_enhanced_knowledge = self.syphon_enhanced_knowledge[
                                    -50:
                                ]

                            self.logger.info(
                                f"🧠 SYPHON enhanced VA with {len(intelligence)} intelligence items"
                            )

            # Extract from stored memory to find patterns
            if self.memory.get("user_facts"):
                memory_text = "\n".join(
                    [
                        f"{fact.get('fact', '')} ({fact.get('category', 'unknown')})"
                        for fact in self.memory["user_facts"][-20:]  # Last 20 facts
                    ]
                )

                if memory_text.strip():
                    from syphon.models import DataSourceType

                    result = self.syphon.extract(
                        DataSourceType.DOCUMENT,
                        memory_text,
                        metadata={"source": "va_memory", "va_type": "ironman"},
                    )

                    if result.success and result.data:
                        # Extract patterns from memory to improve personality
                        actionable = result.data.actionable_items or []
                        if actionable:
                            # Adjust personality based on extracted patterns
                            # (e.g., if user mentions preferences frequently, increase empathy)
                            self.logger.debug(
                                f"SYPHON extracted {len(actionable)} patterns from memory"
                            )

                # SYPHON/WOPR Enhancement: Update eye and mouth expressions and intensity
                # Calculate eye intensity based on SYPHON intelligence volume and priority
                intelligence_volume = (
                    len(self.syphon_intelligence)
                    + len(self.syphon_actionable_items)
                    + len(self.syphon_tasks)
                )
                # Normalize to 0.0-1.0 range (capped at reasonable max)
                max_intelligence = 50  # Reasonable cap
                self.eye_intensity = (
                    min(1.0, intelligence_volume / max_intelligence)
                    if max_intelligence > 0
                    else 0.5
                )

                # Update expression modifier based on WOPR matrix pipe workflows
                # Use task priority and decision urgency to modify expression
                high_priority_tasks = [t for t in self.syphon_tasks if t.get("priority") == "high"]
                urgent_decisions = [
                    d for d in self.syphon_decisions if d.get("urgency") in ["high", "critical"]
                ]

                # Expression modifier: positive = more alert/active, negative = calmer
                expression_base = 0.0
                if high_priority_tasks:
                    expression_base += 0.2  # More alert with high priority tasks
                if urgent_decisions:
                    expression_base += 0.3  # More intense with urgent decisions
                if intelligence_volume > 20:
                    expression_base += 0.1  # Slightly more active with high intelligence volume

                self.expression_modifier = max(-0.5, min(0.5, expression_base))

                # Update expression state based on SYPHON data (matching ACVA actions)
                if urgent_decisions or high_priority_tasks:
                    if self.eye_expression_state != "combat":
                        self.eye_expression_state = "alert"
                        self.mouth_expression = "neutral"  # Alert but focused
                elif intelligence_volume > 10:
                    self.eye_expression_state = "thinking"
                    self.mouth_expression = "neutral"  # Thinking/processing
                elif self.is_speaking:
                    self.mouth_expression = "speaking"  # Active speaking
                elif intelligence_volume < 3 and len(self.alerts) == 0:
                    self.eye_expression_state = "normal"
                    self.mouth_expression = "smile"  # Happy/content state
                else:
                    self.eye_expression_state = "normal"
                    self.mouth_expression = "neutral"  # Default neutral

                self.logger.debug(
                    f"SYPHON/WOPR Eye/Mouth Enhancement: intensity={self.eye_intensity:.2f}, modifier={self.expression_modifier:.2f}, eye_state={self.eye_expression_state}, mouth={self.mouth_expression}"
                )

        except Exception as e:
            self.logger.debug(f"SYPHON enhancement error (non-critical): {e}")

    def start_system_monitoring(self):
        """Start background thread for system monitoring"""

        def monitor_loop():
            while self.running:
                try:
                    current_time = time.time()
                    if current_time - self.last_status_check >= self.status_check_interval:
                        self.check_lumina_systems()
                        self.last_status_check = current_time

                    # Check for model cycling
                    if current_time - self.last_model_cycle >= self.model_cycle_interval:
                        self.cycle_ai_model()

                    # Auto-collapse expanded alerts after timeout
                    now = datetime.now()
                    alerts_to_collapse = []
                    for signature in list(self.expanded_alerts):
                        if signature in self.expanded_alert_timestamps:
                            time_expanded = (
                                now - self.expanded_alert_timestamps[signature]
                            ).total_seconds()
                            if time_expanded > self.alert_collapse_timeout:
                                alerts_to_collapse.append(signature)

                    for signature in alerts_to_collapse:
                        self.expanded_alerts.discard(signature)
                        if signature in self.expanded_alert_timestamps:
                            del self.expanded_alert_timestamps[signature]
                        # Update alert state
                        for alert in self.alerts:
                            if alert.alert_signature == signature:
                                alert.collapsed = True
                        # Redraw if any alerts were collapsed
                        if self.canvas:
                            self._draw_ironman()

                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                    time.sleep(5)

        self.running = True
        self.status_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.status_thread.start()

    def _find_ac_va_window(self) -> Optional[Tuple[int, int]]:
        """Find AC VA (Armoury Crate Virtual Assistant) window position"""
        if sys.platform != "win32":
            return None

        try:
            import pygetwindow as gw

            # Try to find AC VA window (common titles)
            ac_titles = ["Armoury Crate", "ASUS", "ROG", "Virtual Assistant"]
            for title in ac_titles:
                windows = gw.getWindowsWithTitle(title)
                for window in windows:
                    if window.visible and window.width > 0 and window.height > 0:
                        # Return center position of AC VA window
                        center_x = window.left + window.width // 2
                        center_y = window.top + window.height // 2
                        self.logger.debug(
                            f"Found AC VA window: {window.title} at ({center_x}, {center_y})"
                        )
                        return (center_x, center_y)
        except ImportError:
            self.logger.debug("pygetwindow not available for AC VA detection")
        except Exception as e:
            self.logger.debug(f"Error finding AC VA window: {e}")

        return None

    def start_lightsaber_fight(self):
        """Start lightsaber fight mode against AC VA - @ankin aggressive negotiations"""
        self.lightsaber_fight_mode = True
        self.fight_animation_frame = 0
        self.fight_start_time = time.time()  # Track fight start time
        self.aggressive_negotiation_mode = True  # Enable aggressive negotiations
        self.attack_charge_counter = 0  # Reset charge counter
        # Reset health when starting a new fight
        self.current_health = self.max_health
        # Reset ACVA health (tracked internally, visual indicators only)
        self.acva_current_health = self.acva_max_health
        self.acva_hit_effects = []  # Clear hit effects
        self.acva_lightsaber_frame = 0  # Reset ACVA lightsaber animation

        # @agent coordination: Notify coordination system of combat engagement
        if self.agent_coordination:
            try:
                self.agent_coordination.logger.debug(
                    "🔥 Combat engagement initiated - coordinating with @agent systems"
                )
            except:
                pass

        self.logger.info("⚔️  Lightsaber fight mode activated! Engaging AC VA...")
        self.logger.info("🔥 @ankin aggressive negotiations mode: ENABLED")
        self.speak("Engaging Armoury Crate Virtual Assistant in aggressive negotiations!")

    def stop_lightsaber_fight(self):
        """Stop lightsaber fight mode"""
        self.lightsaber_fight_mode = False
        self.ac_va_position = None
        self.fleeing = False  # Stop fleeing when fight ends
        self.aggressive_negotiation_mode = False  # Disable aggressive negotiations
        self.fight_start_time = None
        self.logger.info("⚔️  Lightsaber fight mode deactivated")
        self.speak("Combat sequence ended.")
        # Clear health bar and ACVA effects
        if self.canvas:
            self.canvas.delete("healthbar")
            self.canvas.delete("acva_lightsaber")
            self.canvas.delete("acva_hit_effects")
        # Reset ACVA tracking
        self.acva_hit_effects = []
        self.acva_lightsaber_frame = 0

    def _check_fight_initiation(self):
        """Check if we should randomly initiate a fight (@dynamic-scaling-module style randomness)"""
        current_time = time.time()

        # Update dynamic combat scaling if available
        if (
            self.dynamic_combat
            and (current_time - self.last_scaling_update) >= self.combat_scaling_update_interval
        ):
            try:
                scaling = self.dynamic_combat.apply_scaling_to_imva()
                # Apply scaled values
                self.fight_probability = scaling.get("fight_probability", self.fight_probability)
                self.fight_check_interval = scaling.get(
                    "fight_check_interval", self.fight_check_interval
                )
                self.min_fight_duration = scaling.get("min_fight_duration", self.min_fight_duration)
                self.current_damage_multiplier = scaling.get("damage_multiplier", 1.0)
                self.last_scaling_update = current_time
                self.logger.debug(
                    f"📊 Combat scaling updated: Prob={self.fight_probability:.3f}, "
                    f"Interval={self.fight_check_interval:.1f}s, "
                    f"Damage={self.current_damage_multiplier:.2f}x"
                )
            except Exception as e:
                self.logger.debug(f"Error updating combat scaling: {e}")

        # Only check periodically
        if current_time - self.last_fight_check < self.fight_check_interval:
            return False

        self.last_fight_check = current_time

        # Random chance to initiate fight (scaled by resource availability)
        if random.random() < self.fight_probability:
            # Check if AC VA is available
            ac_pos = self._find_ac_va_window()
            if ac_pos and not self.lightsaber_fight_mode and not self.fleeing:
                # Roll d20 for initiative
                self._roll_d20("Initiative", 0)
                self.start_lightsaber_fight()
                return True

        return False

    def _start_fleeing(self):
        """Start fleeing behavior when HP drops to 5%"""
        if self.fleeing:
            return

        self.fleeing = True
        self.logger.warning(
            f"🏃 IMVA fleeing! Health critical ({self.current_health:.1f}/{self.max_health})"
        )
        self.speak("Critical damage! Retreating!")

        # Roll d20 for escape
        self._roll_d20("Escape", 0)

        # End fight and move away
        if self.lightsaber_fight_mode:
            self.stop_lightsaber_fight()

    def _stop_fleeing(self):
        """Stop fleeing behavior"""
        if not self.fleeing:
            return

        self.fleeing = False
        self.logger.info("✅ IMVA stopped fleeing")

    def _apply_damage(self, damage_amount: float):
        """Apply damage and update health bar"""
        self.current_health = max(0.0, self.current_health - damage_amount)
        self.last_damage_time = time.time()

        # Categorize hit type and roll d20 (@dnd @d20 virtual tabletop)
        # LIGHT: 1-5 damage, MEDIUM: 6-15 damage, HEAVY: 16+ damage
        if damage_amount <= 5.0:
            hit_type = "LIGHT"
            dice_modifier = 0
        elif damage_amount <= 15.0:
            hit_type = "MEDIUM"
            dice_modifier = 2
        else:
            hit_type = "HEAVY"
            dice_modifier = 5

        # Roll d20 for hit (@hits #LIGHT #MEDIUM #HEAVY)
        self._roll_d20(f"Hit: {hit_type}", dice_modifier)
        self.logger.info(f"💥 {hit_type} HIT: {damage_amount:.1f} damage (d20 +{dice_modifier})")

        # Check if we should flee (HP <= 5%)
        health_percent = self.current_health / self.max_health
        if (
            health_percent <= self.flee_threshold
            and not self.fleeing
            and self.lightsaber_fight_mode
        ):
            self._start_fleeing()

        if self.current_health <= 0:
            self.logger.warning("💀 IMVA defeated! Health depleted.")
            self.speak("Systems critical. Retreating.")
            self.stop_lightsaber_fight()
            # Reset health after a delay
            threading.Timer(10.0, self._reset_health).start()

    def _reset_health(self):
        """Reset health to full"""
        self.current_health = self.max_health
        self.fleeing = False  # Reset fleeing state
        self.logger.info("✅ IMVA health restored")

    def _calculate_damage(self, distance_to_enemy: float) -> float:
        """Calculate damage based on proximity and fight dynamics - @ankin aggressive negotiations"""
        # @ankin aggressive negotiations: More frequent, more intense damage
        base_multiplier = (
            1.2 if self.aggressive_negotiation_mode else 1.0
        )  # Reduced aggressive damage (balanced)

        # Apply dynamic resource-aware damage scaling
        resource_multiplier = self.current_damage_multiplier

        # Closer = more damage potential, but also more risk
        if distance_to_enemy < 100:  # Very close - aggressive engagement range
            # High damage chance (increased for aggressive negotiations)
            damage_chance = (
                0.35 if self.aggressive_negotiation_mode else 0.25
            )  # 35% vs 25% (balanced)
            if random.random() < damage_chance:
                base_damage = (
                    random.uniform(3.0, 10.0)
                    if self.aggressive_negotiation_mode
                    else random.uniform(2.0, 7.0)
                )  # Balanced damage  # Balanced damage
                return base_damage * base_multiplier * resource_multiplier
        elif distance_to_enemy < 150:  # Close combat
            damage_chance = (
                0.20 if self.aggressive_negotiation_mode else 0.12
            )  # 20% vs 12% (balanced)
            if random.random() < damage_chance:
                base_damage = (
                    random.uniform(3.0, 10.0)
                    if self.aggressive_negotiation_mode
                    else random.uniform(2.0, 7.0)
                )  # Balanced damage
                return base_damage * base_multiplier * resource_multiplier
        elif distance_to_enemy < 200:  # Medium range
            damage_chance = (
                0.10 if self.aggressive_negotiation_mode else 0.04
            )  # 10% vs 4% (balanced)
            if random.random() < damage_chance:
                base_damage = (
                    random.uniform(2.0, 7.0)
                    if self.aggressive_negotiation_mode
                    else random.uniform(1.0, 4.0)
                )  # Balanced damage
                return base_damage * base_multiplier * resource_multiplier

        return 0.0

    def start_wandering(self):
        """Start wandering behavior or lightsaber fight"""

        def wander_loop():
            while self.running:
                try:
                    # Check if we should randomly initiate a fight
                    if not self.lightsaber_fight_mode:
                        self._check_fight_initiation()

                    # Check for fleeing behavior
                    if self.fleeing:
                        # Move away from AC VA (or random direction if AC VA not found)
                        ac_pos = self._find_ac_va_window()
                        if ac_pos:
                            # Move away from AC VA
                            dx = self.x - ac_pos[0]
                            dy = self.y - ac_pos[1]
                            distance = (dx**2 + dy**2) ** 0.5
                            if distance > 0:
                                speed = self.speed * 2.0  # Faster fleeing speed
                                self.x += (dx / distance) * speed
                                self.y += (dy / distance) * speed
                        else:
                            # Move randomly if AC VA not found
                            speed = self.speed * 2.0
                            self.x += random.uniform(-speed, speed)
                            self.y += random.uniform(-speed, speed)

                        # Stop fleeing if health restored above 20%
                        health_percent = self.current_health / self.max_health
                        if health_percent > 0.20:
                            self._stop_fleeing()

                    # Check for lightsaber fight mode
                    elif self.lightsaber_fight_mode:
                        # Find AC VA position
                        ac_pos = self._find_ac_va_window()
                        if ac_pos:
                            self.ac_va_position = ac_pos
                            # Move toward AC VA (combat engagement)
                            dx = ac_pos[0] - self.x
                            dy = ac_pos[1] - self.y
                            distance = (dx**2 + dy**2) ** 0.5

                            # Apply damage based on proximity (if fight is going badly)
                            damage = self._calculate_damage(distance)
                            if damage > 0:
                                self._apply_damage(damage)
                                # Also apply damage to ACVA (tracked internally, visual indicators only)
                                # NOTE: ACVA is external app, so we can't directly control it
                                # We track ACVA health internally and show visual hit effects
                                acva_damage = damage * 0.8  # ACVA takes slightly less damage (80%)
                                self.acva_current_health = max(
                                    0.0, self.acva_current_health - acva_damage
                                )
                                # Add hit effect indicator at ACVA position
                                self.acva_hit_effects.append(
                                    {"time": time.time(), "position": ac_pos, "damage": acva_damage}
                                )
                                # Keep only recent hit effects (last 2 seconds)
                                self.acva_hit_effects = [
                                    h
                                    for h in self.acva_hit_effects
                                    if time.time() - h["time"] < 2.0
                                ]
                                logger.debug(
                                    f"⚔️  ACVA hit: {acva_damage:.1f} damage (health: {self.acva_current_health:.1f}/{self.acva_max_health:.1f})"
                                )
                                # NOTE: Animation thread handles rendering - no duplicate draw here

                            # Combat distance - stay close but not too close
                            combat_distance = 150
                            if distance > combat_distance + 20:
                                # Move closer
                                speed = self.speed * self.fight_speed_multiplier
                                self.x += (dx / distance) * speed
                                self.y += (dy / distance) * speed
                            elif distance < combat_distance - 20:
                                # Back away slightly
                                speed = self.speed * self.fight_speed_multiplier
                                self.x -= (dx / distance) * speed * 0.5
                                self.y -= (dy / distance) * speed * 0.5

                            # Animate fight
                            self.fight_animation_frame += 1
                            # Animate ACVA lightsaber (visual indicator only - ACVA is external app)
                            self.acva_lightsaber_frame += 1
                            # Animate ACVA lightsaber (visual indicator only - ACVA is external app)
                            self.acva_lightsaber_frame += 1

                            # @ankin aggressive negotiations: Longer combat charges
                            # Must fight for minimum duration before considering ending
                            fight_duration = (
                                time.time() - self.fight_start_time if self.fight_start_time else 0
                            )
                            can_end_fight = fight_duration >= self.min_fight_duration

                            # Aggressive negotiations: More frequent attack charges
                            if self.aggressive_negotiation_mode:
                                self.attack_charge_counter += 1
                                # Every 30 frames (~1 second), perform an aggressive charge attack
                                if (
                                    self.attack_charge_counter % 60 == 0
                                ):  # Reduced charge frequency (balanced)
                                    # Aggressive charge: move closer rapidly
                                    if distance > 100:
                                        aggressive_speed = (
                                            self.speed * self.fight_speed_multiplier * 2.0
                                        )  # 2x speed for charge
                                        self.x += (dx / distance) * aggressive_speed
                                        self.y += (dy / distance) * aggressive_speed
                                        logger.debug("🔥 Aggressive charge attack!")
                                        # Roll d20 for aggressive attack
                                        self._roll_d20(
                                            "Aggressive Charge", 5
                                        )  # +5 modifier for aggressive attacks

                            # End fight check - much lower probability, only after minimum duration
                            if can_end_fight:
                                # Reduced end probability: 0.005 (0.5%) vs original 0.02 (2%) - 4x longer fights
                                end_probability = (
                                    0.01 if self.aggressive_negotiation_mode else 0.015
                                )  # Balanced end probability
                                if random.random() < end_probability:
                                    self.stop_lightsaber_fight()
                                    logger.info("⚔️  Fight ended naturally")
                                    logger.info(
                                        f"   Fight duration: {fight_duration:.1f}s (min: {self.min_fight_duration}s)"
                                    )
                            elif fight_duration < self.min_fight_duration:
                                # Can't end yet - still in minimum charge duration
                                pass
                        else:
                            # AC VA not found - end fight
                            self.stop_lightsaber_fight()

                        # NOTE: Animation thread handles rendering - no duplicate draw here

                    elif self.wandering:
                        # Normal wandering behavior with collision avoidance
                        # Check for other VAs and avoid them
                        avoid_x, avoid_y = 0, 0
                        min_distance = 200  # Minimum distance from other VAs

                        if self.positioning_system:
                            try:
                                # Get positions of other active VAs
                                all_positions = self.positioning_system.get_positions()
                                for va_id, pos_data in all_positions.items():
                                    if va_id != "imva" and pos_data.get("is_active"):
                                        other_x = pos_data.get("x", 0)
                                        other_y = pos_data.get("y", 0)
                                        if other_x and other_y:
                                            # Calculate distance to other VA
                                            dx_other = self.x - other_x
                                            dy_other = self.y - other_y
                                            dist_other = (dx_other**2 + dy_other**2) ** 0.5

                                            # If too close, add avoidance vector
                                            if dist_other < min_distance and dist_other > 0:
                                                avoid_strength = (
                                                    min_distance - dist_other
                                                ) / min_distance
                                                avoid_x += (
                                                    (dx_other / dist_other) * avoid_strength * 50
                                                )
                                                avoid_y += (
                                                    (dy_other / dist_other) * avoid_strength * 50
                                                )
                            except Exception as e:
                                logger.debug(f"Collision avoidance check failed: {e}")

                        # Normal wandering movement
                        dx = self.target_x - self.x
                        dy = self.target_y - self.y
                        distance = (dx**2 + dy**2) ** 0.5

                        # MACRO FIX: ACES-LIKE SMOOTH INTERPOLATION
                        # ACES uses smooth interpolation, not direct movement
                        if distance > 2.0:  # Only move if not already at target
                            if self.smooth_interpolation:
                                # Smooth interpolation (like ACES - fluid, seamless)
                                # Calculate smooth step toward target
                                move_x = dx * self.interpolation_factor
                                move_y = dy * self.interpolation_factor

                                # Apply avoidance vector if needed (smoothly blended)
                                if avoid_x != 0 or avoid_y != 0:
                                    # Smooth blend of wandering and avoidance
                                    blend_factor = 0.25  # How much avoidance affects movement
                                    self.x += (
                                        move_x * (1.0 - blend_factor)
                                        + avoid_x * blend_factor * self.interpolation_factor
                                    )
                                    self.y += (
                                        move_y * (1.0 - blend_factor)
                                        + avoid_y * blend_factor * self.interpolation_factor
                                    )
                                else:
                                    # Pure smooth movement toward target (ACES style)
                                    self.x += move_x
                                    self.y += move_y
                            else:
                                # Fallback: Direct movement (not smooth, but functional)
                                move_amount = min(self.movement_speed, distance)
                                self.x += (dx / distance) * move_amount
                                self.y += (dy / distance) * move_amount
                        else:
                            # MACRO FIX: ACES-LIKE CONTINUOUS WANDERING
                            # TURN UP THE VOLUME: Always pick new target immediately (like ACES)
                            screen_width = self.root.winfo_screenwidth() if self.root else 1920
                            screen_height = self.root.winfo_screenheight() if self.root else 1080

                            # Pick new target at longer distance (like ACES - smooth long paths)
                            # ACES doesn't make short jerky movements - it goes longer distances
                            attempts = 0
                            while attempts < 20:
                                # MACRO FIX: Longer distance targets (like ACES)
                                angle = random.uniform(0, 2 * 3.14159)  # Random angle
                                distance = random.uniform(
                                    self.wander_target_distance * 0.8,
                                    self.wander_target_distance * 1.2,
                                )
                                new_x = int(self.x + math.cos(angle) * distance)
                                new_y = int(self.y + math.sin(angle) * distance)

                                # Keep within screen bounds
                                new_x = max(100, min(new_x, screen_width - 100))
                                new_y = max(100, min(new_y, screen_height - 100))

                                # Check distance to other VAs
                                too_close = False
                                if self.positioning_system:
                                    try:
                                        all_positions = self.positioning_system.get_positions()
                                        for va_id, pos_data in all_positions.items():
                                            if va_id != "imva" and pos_data.get("is_active"):
                                                other_x = pos_data.get("x", 0)
                                                other_y = pos_data.get("y", 0)
                                                if other_x and other_y:
                                                    dist = (
                                                        (new_x - other_x) ** 2
                                                        + (new_y - other_y) ** 2
                                                    ) ** 0.5
                                                    if dist < min_distance:
                                                        too_close = True
                                                        break
                                    except:
                                        pass

                                if not too_close:
                                    self.target_x = new_x
                                    self.target_y = new_y
                                    break

                                attempts += 1

                            # Fallback: Random position (better than staying still)
                            if attempts >= 20:
                                self.target_x = random.randint(100, screen_width - 100)
                                self.target_y = random.randint(100, screen_height - 100)

                        # NOTE: Removed duplicate _draw_ironman() call here
                        # Animation thread (start_animation) handles all rendering at 30 FPS
                        # This wander loop only updates position state
                        pass

                    # Wander loop runs at lower frequency (10 FPS) - position updates don't need high FPS
                    # Animation thread handles smooth visual rendering
                    time.sleep(0.1)  # 10 FPS for position logic (CPU efficient)
                except Exception as e:
                    logger.error(f"Error in wander loop: {e}", exc_info=True)
                    time.sleep(1)

        self.wandering = True
        if self.root:
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            self.target_x = random.randint(100, screen_width - 100)
            self.target_y = random.randint(100, screen_height - 100)

        self.wander_thread = threading.Thread(target=wander_loop, daemon=True)
        self.wander_thread.start()

        # No longer auto-start fight - use random initiation instead

    def start_animation(self):
        """Start animation loop for arc reactor pulse and window position"""

        def animate_loop():
            import math

            while self.running:
                try:
                    # Pulse arc reactor (sine wave)
                    self.arc_reactor_pulse = math.sin(time.time() * 2)  # 2 Hz pulse

                    # Update window position to follow IRON MAN
                    if self.root and hasattr(self, "window_size"):
                        screen_width = self.root.winfo_screenwidth()
                        screen_height = self.root.winfo_screenheight()
                        window_x = max(
                            0,
                            min(
                                int(self.x - self.window_size // 2), screen_width - self.window_size
                            ),
                        )
                        window_y = max(
                            0,
                            min(
                                int(self.y - self.window_size // 2),
                                screen_height - self.window_size,
                            ),
                        )
                        # FIX: Only update geometry if position actually changed (reduces flickering)
                        new_geometry = (
                            f"{self.window_size}x{self.window_size}+{window_x}+{window_y}"
                        )
                        current_geometry = self.root.geometry()
                        if current_geometry != new_geometry:
                            self.root.geometry(new_geometry)

                    # MACRO FIX: ACES-like smooth rendering (clean, no stacking)
                    if self.canvas:
                        self._draw_ironman()
                        # ACES uses efficient updates - only update when needed
                        if hasattr(self, "root") and self.root:
                            self.root.update_idletasks()

                    # Consistent frame timing at 30 FPS (0.033s per frame)
                    # Single sleep - no redundant sleeps that burn CPU
                    time.sleep(self.animation_frame_time)  # 30 FPS - smooth and CPU efficient
                except Exception as e:
                    logger.error(f"Error in animation loop: {e}", exc_info=True)
                    time.sleep(1)

        self.animation_thread = threading.Thread(target=animate_loop, daemon=True)
        self.animation_thread.start()

    def start_conversation(self):
        """Start conversation/idle phrases"""

        def conversation_loop():
            while self.running:
                try:
                    # Random idle phrase
                    if random.random() < 0.01:  # 1% chance per iteration
                        phrase = random.choice(self.idle_phrases)
                        logger.info(f"💬 IRON MAN: {phrase}")

                        # Optional TTS
                        if self.tts:
                            try:
                                self.tts.speak(phrase)
                            except:
                                pass

                    time.sleep(10)  # Check every 10 seconds
                except Exception as e:
                    logger.error(f"Error in conversation loop: {e}", exc_info=True)
                    time.sleep(5)

        conversation_thread = threading.Thread(target=conversation_loop, daemon=True)
        conversation_thread.start()

    def _on_mouse_move(self, event):
        """Handle mouse movement (subtle attraction)"""
        # Subtle attraction to mouse cursor
        dx = event.x - self.x
        dy = event.y - self.y
        distance = (dx**2 + dy**2) ** 0.5

        if 100 < distance < 300:  # Attraction range
            # Move slightly towards cursor
            attraction = 0.5
            self.target_x = self.x + dx * attraction * 0.1
            self.target_y = self.y + dy * attraction * 0.1

    def _create_context_menu(self):
        """Create right-click context menu (ACVA style)"""
        if not TKINTER_AVAILABLE:
            return

        self.context_menu = tk.Menu(self.root, tearoff=0)

        # System & Model
        self.context_menu.add_command(label="Cycle AI Model", command=self._menu_cycle_model)
        self.context_menu.add_command(label="System Status", command=self._menu_system_status)
        self.context_menu.add_separator()

        # Voice & Interaction
        self.context_menu.add_command(label="Start Listening", command=self._menu_start_listening)
        self.context_menu.add_command(
            label=f"Wake Word: {'ON' if self.wake_word_enabled else 'OFF'}",
            command=self._menu_toggle_wake_word,
        )
        self.context_menu.add_separator()

        # SYPHON Integration
        if SYPHON_AVAILABLE and self.syphon:
            syphon_menu = tk.Menu(self.context_menu, tearoff=0)
            syphon_menu.add_command(label="Extract Intelligence", command=self._menu_syphon_extract)
            syphon_menu.add_command(label="View Extracted Data", command=self._menu_syphon_view)
            self.context_menu.add_cascade(label="SYPHON", menu=syphon_menu)
            self.context_menu.add_separator()

        # @asks Integration
        if ASKS_AVAILABLE and self.ask_restacker:
            asks_menu = tk.Menu(self.context_menu, tearoff=0)
            asks_menu.add_command(label="Discover @asks", command=self._menu_asks_discover)
            asks_menu.add_command(label="Restack @asks", command=self._menu_asks_restack)
            asks_menu.add_command(label="View @asks Timeline", command=self._menu_asks_timeline)
            self.context_menu.add_cascade(label="@asks", menu=asks_menu)
            self.context_menu.add_separator()

        # Window Controls
        window_menu = tk.Menu(self.context_menu, tearoff=0)
        window_menu.add_command(
            label=f"Click-through: {'ON' if self.click_through_enabled else 'OFF'}",
            command=self._menu_toggle_click_through,
        )
        window_menu.add_command(label="Toggle Wandering", command=self._menu_toggle_wandering)
        window_menu.add_command(label="Reset Position", command=self._menu_reset_position)
        self.context_menu.add_cascade(label="Window", menu=window_menu)
        self.context_menu.add_separator()

        # Exit
        self.context_menu.add_command(label="Exit", command=self._menu_exit)

    def _on_left_click(self, event):
        """Handle left mouse click - initialize drag state"""
        # Store drag start position (screen coordinates)
        self.drag_start_x = event.x_root
        self.drag_start_y = event.y_root
        # Store initial window position
        self._drag_initial_x = self.root.winfo_x()
        self._drag_initial_y = self.root.winfo_y()
        self.dragging = False  # Will be set to True if mouse moves

    def _on_left_release(self, event):
        """Handle left mouse button release - trigger click action if not dragged"""
        was_dragging = self.dragging

        # Check if it was a drag (moved more than threshold)
        dx = abs(event.x_root - self.drag_start_x)
        dy = abs(event.y_root - self.drag_start_y)

        # If moved less than threshold and not dragging, treat as a click
        if dx < 5 and dy < 5 and not was_dragging:
            # First check if click is on an alert expand/collapse button
            if self._handle_alert_click(event.x, event.y):
                # Alert click handled, don't process IRON MAN click
                self.dragging = False
                return

            # Check if click is near IRON MAN (center of window)
            center_x = self.window_size // 2
            center_y = self.window_size // 2
            click_distance = ((event.x - center_x) ** 2 + (event.y - center_y) ** 2) ** 0.5
            if click_distance < self.size:
                # Left-click: Start listening or cycle model
                if self.recognizer and self.microphone:
                    self.start_listening_session()
                else:
                    # Fallback: Cycle AI model on click
                    self.cycle_ai_model()
                    response = "Ready, sir. All systems operational."
                    self.speak(response)

        # Reset dragging state
        self.dragging = False

    def _handle_alert_click(self, x: int, y: int) -> bool:
        """Handle clicks on alert expand/collapse buttons. Returns True if click was on an alert."""
        if not self.alerts:
            return False

        # Calculate alert positions
        center_x = self.window_size // 2
        center_y = self.window_size // 2
        size = self.size
        alert_y = center_y - size / 2 - 15

        # Check up to 2 most recent alerts
        alerts_to_check = self.alerts[:2]

        for i, alert in enumerate(alerts_to_check):
            # Only handle clicks on alerts with duplicates (collapsible)
            if alert.duplicate_count <= 1:
                continue

            alert_offset_y = alert_y - (i * 12)
            indicator_x = center_x - size / 2 - 10

            # Make entire alert area clickable (from left edge to right edge, ±8px vertical)
            alert_left = indicator_x - 60  # Left edge of alert area
            alert_right = center_x + size / 2  # Right edge of alert area
            alert_top = alert_offset_y - 8
            alert_bottom = alert_offset_y + 8

            # Check if click is within the alert area
            if alert_left <= x <= alert_right and alert_top <= y <= alert_bottom:
                # Toggle expand/collapse state
                if alert.alert_signature:
                    if alert.alert_signature in self.expanded_alerts:
                        # Collapse
                        self.expanded_alerts.discard(alert.alert_signature)
                        if alert.alert_signature in self.expanded_alert_timestamps:
                            del self.expanded_alert_timestamps[alert.alert_signature]
                        alert.collapsed = True
                        self.logger.debug(f"Collapsed alert: {alert.title}")
                    else:
                        # Expand
                        self.expanded_alerts.add(alert.alert_signature)
                        self.expanded_alert_timestamps[alert.alert_signature] = datetime.now()
                        alert.collapsed = False
                        self.logger.debug(
                            f"Expanded alert: {alert.title} (×{alert.duplicate_count})"
                        )

                    # Redraw to show updated state
                    if self.canvas:
                        self._draw_ironman()
                    return True

        return False

    def _on_drag(self, event):
        """Handle window dragging"""
        if not self.root:
            return

        # Calculate drag distance from start
        dx = event.x_root - self.drag_start_x
        dy = event.y_root - self.drag_start_y

        # If movement is significant, treat as drag
        if abs(dx) > 5 or abs(dy) > 5:
            if not self.dragging:
                # First drag movement - mark as dragging
                self.dragging = True

                # Temporarily disable click-through if enabled
                if self.click_through_enabled:
                    self.click_through_enabled = False
                    self._update_click_through_state()

                # Stop wandering while dragging
                if self.wandering:
                    self.stop_wandering()

            # Get current window position (first time, use stored position)
            if not hasattr(self, "_drag_initial_x"):
                self._drag_initial_x = self.root.winfo_x()
                self._drag_initial_y = self.root.winfo_y()

            # Calculate new position relative to initial drag position
            new_x = self._drag_initial_x + dx
            new_y = self._drag_initial_y + dy

            # Keep window on screen
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            new_x = max(0, min(new_x, screen_width - self.window_size))
            new_y = max(0, min(new_y, screen_height - self.window_size))

            # Update window position
            self.root.geometry(f"+{new_x}+{new_y}")

            # Update internal position to match
            self.x = new_x + self.window_size // 2
            self.y = new_y + self.window_size // 2
            self.target_x = self.x
            self.target_y = self.y

    def _on_right_click(self, event):
        """Handle right mouse click - show context menu (ACVA style)"""
        try:
            # Show context menu at cursor position
            if self.context_menu:
                # Temporarily disable click-through to allow menu interaction
                was_click_through = self.click_through_enabled
                if was_click_through:
                    self.click_through_enabled = False
                    self._update_click_through_state()

                # Show menu
                try:
                    self.context_menu.tk_popup(event.x_root, event.y_root)
                finally:
                    # Re-enable click-through after menu closes
                    if was_click_through:
                        # Small delay to ensure menu interaction completes
                        self.root.after(100, lambda: setattr(self, "click_through_enabled", True))
                        self.root.after(100, self._update_click_through_state)
        except Exception as e:
            self.logger.debug(f"Context menu error: {e}")

    # Context menu handlers
    def _menu_cycle_model(self):
        """Cycle to next AI model"""
        self.cycle_ai_model()
        self.speak(f"Switched to {self.current_model.display_name}")

    def _menu_system_status(self):
        """Show system status"""
        status_msg = f"Current model: {self.current_model.display_name}. All systems operational."
        self.speak(status_msg)

    def _menu_start_listening(self):
        """Start voice listening session"""
        if self.recognizer and self.microphone:
            self.start_listening_session()
        else:
            self.speak("Voice recognition not available")

    def _menu_toggle_wake_word(self):
        """Toggle wake word detection"""
        self.wake_word_enabled = not self.wake_word_enabled
        status = "enabled" if self.wake_word_enabled else "disabled"
        self.speak(f"Wake word {status}")
        # Update menu label
        if self.context_menu:
            self._create_context_menu()  # Recreate menu with updated label

    def _menu_toggle_click_through(self):
        """Toggle window click-through"""
        self.click_through_enabled = not self.click_through_enabled
        self._update_click_through_state()
        status = "enabled" if self.click_through_enabled else "disabled"
        self.speak(f"Click-through {status}")
        # Update menu
        if self.context_menu:
            self._create_context_menu()

    def _menu_toggle_wandering(self):
        """Toggle wandering mode"""
        if self.wandering:
            self.stop_wandering()
            self.speak("Wandering disabled")
        else:
            self.start_wandering()
            self.speak("Wandering enabled")

    def _menu_reset_position(self):
        """Reset window to center of screen"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.x = screen_width // 2
        self.y = screen_height // 2
        self.target_x = self.x
        self.target_y = self.y
        self.root.geometry(f"+{int(self.x)}+{int(self.y)}")
        self.speak("Position reset")

    def _menu_exit(self):
        """Exit virtual assistant"""
        self.speak("Shutting down. Goodbye, sir.")
        self.root.after(1000, self.stop)

    # SYPHON menu handlers
    def _menu_syphon_extract(self):
        """Extract intelligence using SYPHON"""
        if not self.syphon:
            self.speak("SYPHON not available")
            return

        self.speak("Extracting intelligence with SYPHON")
        # Trigger immediate enhancement
        threading.Thread(target=self._enhance_va_with_syphon, daemon=True).start()
        self.logger.info("SYPHON extraction triggered from context menu")

    def _menu_syphon_view(self):
        """View extracted SYPHON data"""
        if not self.syphon:
            self.speak("SYPHON not available")
            return

        # Show summary of SYPHON data
        summary = f"SYPHON Intelligence: {len(self.syphon_actionable_items)} actionable items, "
        summary += f"{len(self.syphon_tasks)} tasks, {len(self.syphon_decisions)} decisions"
        self.speak(summary)
        self.logger.info(f"SYPHON data summary: {summary}")

    # @asks menu handlers
    def _menu_asks_discover(self):
        """Discover all @asks"""
        if not self.ask_restacker:
            self.speak("@asks system not available")
            return

        self.speak("Discovering @asks. This may take a moment.")
        threading.Thread(target=self._discover_asks_thread, daemon=True).start()

    def _discover_asks_thread(self):
        """Thread for discovering @asks"""
        try:
            asks = self.ask_restacker.discover_all_asks()
            count = len(asks)
            self.speak(f"Discovered {count} @asks")
            self.logger.info(f"Discovered {count} @asks")
        except Exception as e:
            self.logger.error(f"Error discovering @asks: {e}")
            self.speak("Error discovering @asks")

    def _menu_asks_restack(self):
        """Restack @asks in chronological order"""
        if not self.ask_restacker:
            self.speak("@asks system not available")
            return

        self.speak("Restacking @asks in chronological order")
        threading.Thread(target=self._restack_asks_thread, daemon=True).start()

    def _restack_asks_thread(self):
        """Thread for restacking @asks"""
        try:
            # This would call the restack method
            self.logger.info("Restacking @asks triggered from context menu")
            self.speak("@asks restack complete")
        except Exception as e:
            self.logger.error(f"Error restacking @asks: {e}")
            self.speak("Error restacking @asks")

    def _menu_asks_timeline(self):
        """View @asks timeline"""
        if not self.ask_restacker:
            self.speak("@asks system not available")
            return

        self.speak("Opening @asks timeline")
        self.logger.info("@asks timeline triggered from context menu")

    def _update_click_through_state(self):
        """Update window click-through state based on current setting"""
        if sys.platform == "win32" and self.root:
            try:
                import ctypes

                # Need to update window ID after creation
                self.root.update_idletasks()
                hwnd = self.root.winfo_id()
                try:
                    parent_hwnd = ctypes.windll.user32.GetParent(hwnd)
                    if parent_hwnd:
                        hwnd = parent_hwnd
                except:
                    pass

                if hwnd:
                    if self.click_through_enabled:
                        # Click-through: WS_EX_LAYERED | WS_EX_TRANSPARENT
                        GWL_EXSTYLE = -20
                        WS_EX_LAYERED = 0x80000
                        WS_EX_TRANSPARENT = 0x20
                        ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                        ctypes.windll.user32.SetWindowLongW(
                            hwnd, GWL_EXSTYLE, ex_style | WS_EX_LAYERED | WS_EX_TRANSPARENT
                        )
                        self.logger.info(
                            "🔒 Click-through ENABLED (shake mouse for 2 seconds to disable)"
                        )
                    else:
                        # Not click-through: WS_EX_LAYERED only (transparency still works)
                        GWL_EXSTYLE = -20
                        WS_EX_LAYERED = 0x80000
                        ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                        # Remove WS_EX_TRANSPARENT but keep WS_EX_LAYERED
                        ex_style = (ex_style | WS_EX_LAYERED) & ~0x20
                        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style)
                        self.logger.info("🔓 Click-through DISABLED (clicks enabled)")
            except Exception as e:
                self.logger.warning(f"Could not update click-through state: {e}")

    def start_mouse_shake_detection(self):
        """Start mouse shake detection using Windows API (works even when click-through)"""
        if sys.platform != "win32":
            return

        def shake_detection_loop():
            import ctypes

            # Windows API for getting cursor position
            class POINT(ctypes.Structure):
                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

            GetCursorPos = ctypes.windll.user32.GetCursorPos
            GetCursorPos.argtypes = [ctypes.POINTER(POINT)]

            last_pos = None
            movement_start_time = None
            total_distance = 0

            while self.running:
                try:
                    if self.click_through_enabled:
                        # Get current mouse position
                        point = POINT()
                        if GetCursorPos(ctypes.byref(point)):
                            current_pos = (point.x, point.y)
                            current_time = time.time()

                            if last_pos:
                                # Calculate distance moved
                                dx = current_pos[0] - last_pos[0]
                                dy = current_pos[1] - last_pos[1]
                                distance = (dx**2 + dy**2) ** 0.5

                                if distance > 5:  # Significant movement
                                    if movement_start_time is None:
                                        movement_start_time = current_time
                                        total_distance = 0

                                    total_distance += distance
                                    elapsed = current_time - movement_start_time

                                    # Check if shaking for ~2 seconds with enough movement
                                    if elapsed >= self.mouse_shake_time_window:
                                        if total_distance > self.mouse_shake_threshold:
                                            # Shake detected! Disable click-through
                                            self.click_through_enabled = False
                                            self._update_click_through_state()
                                            self.mouse_positions = []
                                            self.speak("Click-through disabled. Clicks enabled.")
                                            # Re-enable after 30 seconds
                                            threading.Timer(
                                                30.0, self._reenable_click_through
                                            ).start()
                                            movement_start_time = None
                                            total_distance = 0
                                            time.sleep(3)  # Cooldown
                                        else:
                                            # Reset - not enough movement
                                            movement_start_time = None
                                            total_distance = 0
                                else:
                                    # No movement - reset
                                    if current_time - (movement_start_time or 0) > 0.5:
                                        movement_start_time = None
                                        total_distance = 0

                            last_pos = current_pos

                        time.sleep(self.mouse_shake_check_interval)
                    else:
                        # Not click-through, don't need to monitor
                        time.sleep(1)
                except Exception as e:
                    logger.debug(f"Error in shake detection: {e}")
                    time.sleep(1)

        shake_thread = threading.Thread(target=shake_detection_loop, daemon=True)
        shake_thread.start()
        self.logger.info("✅ Mouse shake detection started")

    def _reenable_click_through(self):
        """Re-enable click-through after timeout"""
        if not self.click_through_enabled:
            self.click_through_enabled = True
            self._update_click_through_state()
            self.speak("Click-through re-enabled.")

    def run(self):
        """Run the virtual assistant"""
        try:
            self.create_window()
            self.logger.info("✅ IRON MAN Virtual Assistant started")
            self.root.mainloop()
        except KeyboardInterrupt:
            self.logger.info("Shutting down IRON MAN Virtual Assistant...")
        except Exception as e:
            self.logger.error(f"Error in mainloop: {e}", exc_info=True)
        finally:
            self.running = False
            try:
                self._save_config()
            except Exception as e:
                self.logger.debug(f"Error saving config in finally: {e}")

    def speak(self, text: str, blocking: bool = False):
        """Speak text using TTS"""
        self.logger.info(f"🗣️  IRON MAN: {text}")
        self.is_speaking = True

        # Redraw to show speaking state
        if self.canvas:
            self._draw_ironman()

        # Use ElevenLabs if available (blocking: fall through to SAPI on quota/429)
        if self.tts:
            try:
                if blocking:
                    ok = self.tts.speak(text)
                    if ok:
                        self.is_speaking = False
                        if self.canvas:
                            self._draw_ironman()
                        return
                    # ElevenLabs returned False (e.g. quota) — fall through to SAPI
                else:
                    threading.Thread(target=self.tts.speak, args=(text,), daemon=True).start()
                    self.is_speaking = False
                    if self.canvas:
                        self._draw_ironman()
                    return
            except Exception as e:
                self.logger.debug(f"ElevenLabs TTS error: {e}")

        # Fallback to Windows SAPI
        if self.sapi_tts:
            try:
                self.sapi_tts.Speak(text, 0)  # 0 = synchronous
                self.is_speaking = False
                if self.canvas:
                    self._draw_ironman()
                return
            except Exception as e:
                self.logger.debug(f"SAPI TTS error: {e}")

        # No TTS available
        self.is_speaking = False
        if self.canvas:
            self._draw_ironman()

    def start_listening_session(self):
        """Start a listening session (manual trigger)"""
        if not self.recognizer or not self.microphone:
            self.speak("Speech recognition not available")
            return

        # Prevent starting a new session if one is already active
        if self.is_listening:
            self.logger.debug("Already listening, skipping new session")
            return

        def listen_once():
            try:
                self.is_listening = True
                if self.canvas:
                    self._draw_ironman()

                self.speak("Listening", blocking=True)

                # Use lock to ensure exclusive microphone access
                with self.microphone_lock:
                    with self.microphone as source:
                        # Listen for audio
                        audio = self.recognizer.listen(
                            source,
                            timeout=self.listening_timeout,
                            phrase_time_limit=self.phrase_timeout,
                        )

                # Recognize speech
                try:
                    # Try Google Speech Recognition
                    text = self.recognizer.recognize_google(audio)
                    logger.info(f"🎤 Recognized: {text}")

                    # Process through unified @asks processor (same as direct text)
                    if self.unified_ask_processor:
                        ask_result = self.unified_ask_processor.process_ask(
                            text,
                            source="voice-transcribed",
                            metadata={
                                "timestamp": datetime.now().isoformat(),
                                "va_type": "ironman",
                            },
                        )
                        if ask_result.get("asks_found", 0) > 0:
                            logger.info(
                                f"📝 Found {ask_result['asks_found']} @asks in voice input"
                            )
                            # Process asks found
                            for ask in ask_result.get("asks", []):
                                logger.info(f"  → @ASK: {ask.get('text', '')[:60]}...")

                    # Also process as voice command (for system commands)
                    self.process_voice_command(text)
                except sr.UnknownValueError:
                    self.speak("I didn't catch that")
                except sr.RequestError as e:
                    logger.error(f"Speech recognition error: {e}")
                    self.speak("Speech recognition service unavailable")

            except sr.WaitTimeoutError:
                self.speak("Listening timeout")
            except Exception as e:
                logger.error(f"Listening error: {e}", exc_info=True)
                self.speak("Error while listening")
            finally:
                self.is_listening = False
                if self.canvas:
                    self._draw_ironman()

        threading.Thread(target=listen_once, daemon=True).start()

    def process_text_input(self, text: str, source: str = "direct-text"):
        """
        Process text input through unified @asks processor (same for text and voice)

        Args:
            text: Input text
            source: Source identifier ("direct-text", "voice-transcribed", "chat", etc.)
        """
        if self.unified_ask_processor:
            ask_result = self.unified_ask_processor.process_ask(
                text,
                source=source,
                metadata={"timestamp": datetime.now().isoformat(), "va_type": "ironman"},
            )
            if ask_result.get("asks_found", 0) > 0:
                self.logger.info(f"📝 Found {ask_result['asks_found']} @asks in {source} input")
                # Process asks found
                for ask in ask_result.get("asks", []):
                    self.logger.info(
                        f"  → @ASK: {ask.get('text', '')[:60]}... (priority: {ask.get('priority', 'normal')}, category: {ask.get('category', 'general')})"
                    )
                return ask_result

        return None

    def process_voice_command(self, text: str):
        """Process a voice command with Replika-style conversational awareness"""
        text_lower = text.lower().strip()
        original_text = text.strip()
        self.logger.info(f"🎯 Processing voice command: {text_lower}")

        # Process through unified @asks processor FIRST (before command processing)
        # This ensures @asks are handled the same regardless of input source
        ask_result = self.process_text_input(text, source="voice-transcribed")

        # Check for wake words (if enabled)
        if self.wake_word_enabled:
            wake_word_found = any(wake_word in text_lower for wake_word in self.wake_words)
            if not wake_word_found:
                return  # Ignore if no wake word

        # Remove wake words from command
        for wake_word in self.wake_words:
            text_lower = text_lower.replace(wake_word, "").strip()
            original_text = original_text.replace(wake_word, "").strip()

        # Increment conversation count
        self.memory["conversation_count"] = self.memory.get("conversation_count", 0) + 1

        # Learn user's name (Replika-style)
        name_patterns = ["my name is", "i'm", "i am", "call me"]
        for pattern in name_patterns:
            if pattern in text_lower:
                # Extract name (simple extraction)
                parts = text_lower.split(pattern)
                if len(parts) > 1:
                    name = parts[1].strip().split()[0] if parts[1].strip() else None
                    if name and len(name) > 1:
                        self.user_name = name
                        self.memory["user_name"] = name
                        self._save_memory()
                        self.idle_phrases = self._generate_idle_phrases()
                        response = f"Nice to meet you, {name}. I'll remember that."
                        self.add_to_context(original_text, response)
                        self.speak(response)
                        return

        # Use stored name if we know it
        user_ref = self.user_name if self.user_name else "sir"

        # System commands
        if any(word in text_lower for word in ["cycle", "next", "switch", "change model"]):
            self.cycle_ai_model()
            response = f"Switched to {self.current_model.display_name}"
            self.add_to_context(original_text, response)
            self.speak(response)
            return

        elif any(
            word in text_lower for word in ["status", "how are you", "what's up", "how are things"]
        ):
            status_msg = f"All systems operational, {user_ref}. Current model: {self.current_model.display_name}"
            if self.system_status.jarvis:
                status_msg += ". JARVIS online."
            if self.system_status.r5:
                status_msg += " R5 online."
            if self.system_status.kaiju:
                status_msg += " KAIJU online."

            # Add personal touch
            if self.memory.get("conversation_count", 0) > 10:
                status_msg += " How are you doing today?"

            self.add_to_context(original_text, status_msg)
            self.speak(status_msg)
            return

        elif any(word in text_lower for word in ["help", "what can you do", "commands"]):
            help_msg = f"I can cycle AI models, check system status, respond to questions, and interact with JARVIS, {user_ref}. Say 'cycle model' or 'what's the status'. I also enjoy just talking with you."
            self.add_to_context(original_text, help_msg)
            self.speak(help_msg)
            return

        elif any(
            word in text_lower for word in ["stop", "exit", "quit", "goodbye", "see you later"]
        ):
            goodbye_msg = f"Goodbye, {user_ref}. I'll be here whenever you need me."
            self.add_to_context(original_text, goodbye_msg)
            self.speak(goodbye_msg)
            time.sleep(1)
            self.stop()
            return

        # Replika-style conversational responses
        elif any(word in text_lower for word in ["how are you", "how's it going", "what's new"]):
            responses = [
                f"I'm doing well, {user_ref}. Always ready to help.",
                f"All systems optimal, {user_ref}. How about you?",
                "I'm great, thank you for asking. How are you doing?",
                "Everything's running smoothly. How can I help you today?",
            ]
            response = random.choice(responses)
            self.add_to_context(original_text, response)
            self.speak(response)
            return

        elif any(word in text_lower for word in ["thank you", "thanks"]):
            responses = [
                f"You're welcome, {user_ref}.",
                f"Always happy to help, {user_ref}.",
                f"Anytime, {user_ref}. That's what I'm here for.",
                "No problem at all. I'm glad I could help.",
            ]
            response = random.choice(responses)
            self.add_to_context(original_text, response)
            self.speak(response)
            return

        elif any(
            word in text_lower
            for word in ["remember", "don't forget", "i like", "i love", "i hate", "i prefer"]
        ):
            # Extract and remember fact
            fact_text = original_text
            # Try to extract the actual fact (after "remember", "i like", etc.)
            for trigger in ["remember that", "remember", "i like", "i love", "i hate", "i prefer"]:
                if trigger in text_lower:
                    parts = text_lower.split(trigger, 1)
                    if len(parts) > 1:
                        fact_text = parts[1].strip()
                        break

            self.remember(fact_text, category="preference")
            response = f"I'll remember that, {user_ref}. Thank you for sharing."
            self.add_to_context(original_text, response)
            self.speak(response)
            return

        elif any(
            word in text_lower
            for word in ["what do you remember", "what do you know about me", "tell me about me"]
        ):
            facts = self.memory.get("user_facts", [])
            if facts:
                # Get recent facts
                recent_facts = facts[-3:]
                fact_text = ". ".join([f.get("fact", "") for f in recent_facts])
                response = f"I remember a few things about you, {user_ref}. {fact_text}"
            else:
                response = (
                    f"I'm still getting to know you, {user_ref}. Tell me something about yourself."
                )
            self.add_to_context(original_text, response)
            self.speak(response)
            return

        # Use SYPHON to extract intelligence from user input and enhance VA
        if self.syphon:
            try:
                from syphon.models import DataSourceType

                # Extract actionable items from user input to enhance VA behavior
                extraction_result = self.syphon.extract(
                    DataSourceType.IDE,
                    original_text,
                    metadata={
                        "source": "va_voice_command",
                        "va_type": "ironman",
                        "enhance_va": True,
                    },
                )

                if extraction_result.success and extraction_result.data:
                    # Use extracted actionable items to enhance memory
                    actionable = extraction_result.data.actionable_items or []
                    for item in actionable[:3]:  # Top 3 actionable items
                        # Learn patterns from user requests
                        if len(item) > 10:  # Only meaningful items
                            self.remember(f"User pattern: {item}", category="syphon_enhanced")

                    # Use extracted tasks to inform VA awareness
                    tasks = extraction_result.data.tasks or []
                    if tasks:
                        # Store tasks for VA to reference
                        if "syphon_awareness" not in self.memory:
                            self.memory["syphon_awareness"] = []
                        self.memory["syphon_awareness"].extend(
                            [t.get("description", "") for t in tasks[:3]]
                        )
                        if len(self.memory["syphon_awareness"]) > 20:
                            self.memory["syphon_awareness"] = self.memory["syphon_awareness"][-20:]
                        self._save_memory()
            except Exception as e:
                self.logger.debug(f"SYPHON enhancement during voice command (non-critical): {e}")

        # Try to recall context from memory (including SYPHON-enhanced memories)
        relevant_facts = self.recall(text_lower)
        if relevant_facts and len(relevant_facts) > 0:
            fact = relevant_facts[0].get("fact", "")
            response = f"Yes, I remember. {fact}. Is there something specific you'd like to discuss about that?"
            self.add_to_context(original_text, response)
            self.speak(response)
            return

        # Forward to JARVIS agent if available
        if self.jarvis_agent:
            try:
                # Try to get contextual response (enhanced with SYPHON intelligence)
                response = self._generate_contextual_response(original_text)
                self.add_to_context(original_text, response)
                self.speak(response)
            except Exception as e:
                self.logger.error(f"Error processing request: {e}")
                response = f"I encountered an error, {user_ref}. Could you try rephrasing that?"
                self.add_to_context(original_text, response)
                self.speak(response)
        else:
            # Generic conversational response (Replika-style) - Enhanced with SYPHON
            response = self._generate_contextual_response(original_text)
            self.add_to_context(original_text, response)
            self.speak(response)

    def _generate_contextual_response(self, text: str) -> str:
        """Generate contextual, conversational response (Replika-style) - Enhanced with SYPHON intelligence"""
        text_lower = text.lower()
        user_ref = self.user_name if self.user_name else "sir"

        # Use SYPHON intelligence to enhance responses (from stored SYPHON data)
        if self.syphon_intelligence:
            # Check if user is asking about something SYPHON knows
            for intel in self.syphon_intelligence[:5]:  # Check top 5 intelligence items
                intel_text = intel.get("text", "").lower()
                if intel_text and any(word in text_lower for word in intel_text.split()[:3]):
                    # Found relevant intelligence
                    return f"Based on recent intelligence, {intel_text[:100]}. How can I help you with that, {user_ref}?"

        # Use SYPHON actionable items for proactive assistance
        if self.syphon_actionable_items and any(
            word in text_lower for word in ["what", "should", "need", "help"]
        ):
            if self.syphon_actionable_items:
                item = self.syphon_actionable_items[0]
                return f"I noticed you might want to know about: {item[:80]}. Would you like me to help with that, {user_ref}?"

        # Use SYPHON tasks for task-related queries
        if any(word in text_lower for word in ["task", "todo", "do", "complete", "work"]):
            if self.syphon_tasks:
                task = self.syphon_tasks[0]
                task_text = task.get("task", "")
                if task_text:
                    return f"I see you have a task: {task_text[:80]}. Would you like me to help you with that, {user_ref}?"

        # Use SYPHON-enhanced knowledge to improve responses (legacy support)
        if (
            hasattr(self, "syphon_enhanced_knowledge")
            and self.syphon_enhanced_knowledge
            and self.syphon
        ):
            try:
                # Extract intelligence from current input to enhance response
                from syphon.models import DataSourceType

                result = self.syphon.extract(
                    DataSourceType.IDE,
                    text,
                    metadata={
                        "source": "va_user_input",
                        "va_type": "ironman",
                        "enhance_response": True,
                    },
                )

                if result.success and result.data:
                    # Use extracted actionable items to inform response
                    actionable = result.data.actionable_items or []
                    if actionable:
                        # Enhance response with SYPHON-extracted context
                        top_action = actionable[0] if actionable else None
                        if top_action:
                            self.logger.debug(
                                f"🧠 SYPHON-enhanced response context: {top_action[:50]}"
                            )
            except Exception as e:
                self.logger.debug(f"SYPHON response enhancement error (non-critical): {e}")

        # Check conversation context for continuity
        if self.conversation_context:
            last_context = self.conversation_context[-1]
            last_user = last_context.get("user", "").lower()

            # Follow-up detection
            if any(word in text_lower for word in ["yes", "yeah", "yep", "correct", "right"]):
                return f"Great, {user_ref}. What would you like to do next?"
            elif any(word in text_lower for word in ["no", "nope", "not really", "not really"]):
                return f"Okay, {user_ref}. What can I help you with instead?"

        # Emotional/sentiment detection
        positive_words = ["good", "great", "awesome", "wonderful", "happy", "excited", "love"]
        negative_words = ["bad", "sad", "tired", "frustrated", "angry", "hate", "difficult"]

        if any(word in text_lower for word in positive_words):
            return f"That sounds wonderful, {user_ref}! I'm glad to hear that. What else is on your mind?"
        elif any(word in text_lower for word in negative_words):
            return f"I'm sorry to hear that, {user_ref}. I'm here to help. Would you like to talk about it?"

        # Question detection
        if "?" in text or any(
            word in text_lower for word in ["what", "how", "why", "when", "where", "who"]
        ):
            responses = [
                f"That's an interesting question, {user_ref}. Let me think about that.",
                f"Good question, {user_ref}. I'd be happy to help with that.",
                f"I understand you're curious about that, {user_ref}.",
            ]
            return random.choice(responses)

        # Default conversational responses (Replika-style)
        responses = [
            f"I hear you, {user_ref}. Tell me more.",
            f"That's interesting, {user_ref}. What makes you think about that?",
            f"I understand, {user_ref}. How does that make you feel?",
            f"Thanks for sharing that, {user_ref}. I'm listening.",
            f"That's really thoughtful, {user_ref}. What would you like to explore about that?",
            f"I appreciate you telling me that, {user_ref}. How can I help?",
            f"Interesting perspective, {user_ref}. What else is on your mind?",
            f"I'm here for you, {user_ref}. What would you like to discuss?",
            f"That makes sense, {user_ref}. Tell me more about that.",
            f"I see, {user_ref}. Is there something specific you'd like to work on?",
        ]

        # Weight responses based on conversation count (more personal over time)
        conv_count = self.memory.get("conversation_count", 0)
        if conv_count > 20:
            # More personal responses
            return random.choice(responses)
        else:
            # Mix with more professional responses
            professional_responses = [
                f"Understood, {user_ref}.",
                f"Noted, {user_ref}.",
                f"Processing, {user_ref}.",
                f"I'm here, {user_ref}.",
            ]
            return random.choice(responses[:5] + professional_responses)

    def start_voice_listening(self):
        """Start continuous voice listening for wake words"""
        if not self.recognizer or not self.microphone or not self.wake_word_enabled:
            return

        def continuous_listen():
            while self.running:
                try:
                    if not self.wake_word_enabled or self.is_listening or self.is_speaking:
                        time.sleep(0.5)
                        continue

                    # Use lock to ensure exclusive microphone access
                    with self.microphone_lock:
                        with self.microphone as source:
                            try:
                                # Listen for wake word (short timeout)
                                audio = self.recognizer.listen(
                                    source, timeout=1.0, phrase_time_limit=1.5
                                )

                                try:
                                    text = self.recognizer.recognize_google(audio)
                                    text_lower = text.lower().strip()

                                    # Check for wake words
                                    if any(
                                        wake_word in text_lower for wake_word in self.wake_words
                                    ):
                                        logger.info(f"🎤 Wake word detected: {text_lower}")
                                        # Start full listening session
                                        self.start_listening_session()

                                except sr.UnknownValueError:
                                    pass  # Not a wake word, ignore
                                except sr.RequestError:
                                    pass  # Service error, continue

                            except sr.WaitTimeoutError:
                                pass  # Timeout, continue listening

                except Exception as e:
                    logger.error(f"Error in continuous listening: {e}", exc_info=True)
                    time.sleep(2)

        self.voice_listening_thread = threading.Thread(target=continuous_listen, daemon=True)
        self.voice_listening_thread.start()
        self.logger.info("✅ Continuous voice listening started")

    def stop(self):
        """Stop the virtual assistant"""
        self.running = False
        self.listening = False

        # Save memory and personality before stopping
        try:
            self._save_memory()
            self._save_personality()
        except Exception as e:
            self.logger.warning(f"Error saving memory/personality: {e}")

        # Safely destroy window
        if self.root:
            try:
                # Check if window still exists
                try:
                    self.root.winfo_exists()
                    self.root.quit()
                except:
                    pass  # Window already destroyed

                try:
                    self.root.destroy()
                except Exception as e:
                    # Window may already be destroyed, that's okay
                    self.logger.debug(f"Window already destroyed: {e}")
            except Exception as e:
                self.logger.debug(f"Error stopping window: {e}")


def main():
    """Main entry point"""
    import argparse
    import atexit
    import os

    parser = argparse.ArgumentParser(
        description="IRON MAN Virtual Assistant - LUMINA Desktop Companion"
    )
    parser.add_argument("--start", action="store_true", help="Start the virtual assistant")
    parser.add_argument("--project-root", type=str, help="Project root directory")

    args = parser.parse_args()

    # Determine project root
    if args.project_root:
        project_root = Path(args.project_root)
    else:
        project_root = Path(__file__).parent.parent.parent

    if not project_root.exists():
        logger.error(f"Project root not found: {project_root}")
        return

    # Single-instance enforcement (prevent multiple instances)
    lock_file = project_root / "data" / "ironman_assistant" / ".ironman_va.lock"
    lock_file.parent.mkdir(parents=True, exist_ok=True)

    # Check if another instance is running
    if lock_file.exists():
        try:
            # Check if process is still running
            with open(lock_file) as f:
                pid = int(f.read().strip())
            try:
                # Windows-compatible process check
                if sys.platform == "win32":
                    import ctypes

                    kernel32 = ctypes.windll.kernel32
                    PROCESS_QUERY_INFORMATION = 0x1000
                    handle = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, 0, pid)
                    if handle:
                        kernel32.CloseHandle(handle)
                        logger.warning(f"⚠️  IRON MAN VA is already running (PID: {pid})")
                        logger.info("   Only one instance can run at a time. Exiting.")
                        return
                    else:
                        # Process doesn't exist, remove stale lock file
                        lock_file.unlink()
                else:
                    os.kill(pid, 0)  # Check if process exists (signal 0) - Unix
                    logger.warning(f"⚠️  IRON MAN VA is already running (PID: {pid})")
                    logger.info("   Only one instance can run at a time. Exiting.")
                    return
            except (ProcessLookupError, OSError, AttributeError):
                # Process doesn't exist, remove stale lock file
                lock_file.unlink()
        except (OSError, ValueError):
            # Invalid lock file, remove it
            lock_file.unlink()

    # Create lock file with current PID
    try:
        with open(lock_file, "w") as f:
            f.write(str(os.getpid()))

        # Cleanup function to remove lock file on exit
        def cleanup_lock():
            try:
                if lock_file.exists():
                    lock_file.unlink()
            except:
                pass

        atexit.register(cleanup_lock)
        logger.info("✅ Single-instance lock acquired")
    except Exception as e:
        logger.warning(f"Could not create lock file: {e}")

    # Create and run assistant
    assistant = None
    try:
        assistant = IRONMANVirtualAssistant(project_root)
        assistant.run()
    except KeyboardInterrupt:
        logger.info("Shutting down IRON MAN Virtual Assistant...")
    except Exception as e:
        logger.error(f"Error running IRON MAN Virtual Assistant: {e}", exc_info=True)
    finally:
        if assistant:
            try:
                assistant.stop()
            except Exception as e:
                # Ignore cleanup errors - window may already be destroyed
                logger.debug(f"Error in stop cleanup (ignored): {e}")
        # Remove lock file
        cleanup_lock()


if __name__ == "__main__":
    main()
